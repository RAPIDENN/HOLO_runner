#!/usr/bin/env python3
"""Measure genuine rectangular Wilson loops from stored SU(3) links.

This module deliberately accepts only explicit link ensembles.  Plaquette
summaries, effective-mass correlators, and the historical Einstein--dilaton
endpoint scale are inspected for provenance but can never enter a Wilson-loop
measurement.

The native result is dimensionless: ``W(R,T)``, ``a V_eff(R,T)`` and, when a
large-loop window has been explicitly requested and passes conservative gates,
``sigma a^2``.  A value in GeV is emitted only when an independently supplied
inverse lattice spacing is provided.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
REPOS_ROOT = REPO_ROOT.parent
HK_ROOT = REPOS_ROOT / "HK-core"

ANALYSIS_SCHEMA = "holo.wilson-loop-analysis.v1"
LINK_SCHEMA = "holo.su3-link-ensemble.v1"
CANONICAL_AXIS_ORDER = "config,x,y,z,t,mu,row,col"
SINGLE_CONFIG_AXIS_ORDER = "x,y,z,t,mu,row,col"
DEFAULT_OUTPUT = HERE / "wilson_data_manifest.json"

SUPPORTED_SUFFIXES = {".npz", ".npy", ".json"}
DETECTED_UNSUPPORTED_SUFFIXES = {".h5", ".hdf5", ".lime", ".ildg"}
CANDIDATE_TOKENS = (
    "wilson",
    "gauge",
    "su3",
    "lattice",
    "link",
    "config",
    "hkcore",
)
PROXY_KEYS = {
    "e2A_ir",
    "alpha_prime_GeV-2",
    "sigma_eff_GeV2",
}
ENSEMBLE_METADATA_FOR_SIGMA = (
    "ensemble_id",
    "gauge_action",
    "beta",
    "thermalization_sweeps",
    "saved_configuration_stride_sweeps",
)


class LinkFormatError(ValueError):
    """The input cannot be interpreted as a certified link ensemble."""


@dataclass(frozen=True)
class LoadedLinks:
    path: Path
    links: np.ndarray
    metadata: dict[str, Any]
    validation: dict[str, Any]


def default_scan_roots() -> list[Path]:
    """Return the two locations that currently carry lattice-labelled data."""

    return [
        HK_ROOT / "results" / "4d_su3",
        REPO_ROOT / "instrument_closure" / "2026-01-04",
    ]


def portable_path(path: Path) -> str:
    """Render repository inputs without machine-specific home directories."""

    resolved = path.expanduser().resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        pass
    try:
        relative = resolved.relative_to(HK_ROOT).as_posix()
        return f"HK-core/{relative}"
    except ValueError:
        return f"external/{resolved.name}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_dump(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _python_scalar(value: Any) -> Any:
    array = np.asarray(value)
    if array.size != 1:
        return value
    item = array.reshape(()).item()
    if isinstance(item, bytes):
        return item.decode("utf-8")
    if isinstance(item, np.generic):
        return item.item()
    return item


def _normalise_axis_order(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ",".join(str(part).strip() for part in value)
    return str(value).replace(" ", "").strip()


def _normalise_boundary_conditions(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().lower()
    if isinstance(value, (list, tuple, np.ndarray)):
        values = [str(part).strip().lower() for part in value]
        if values and all(part == "periodic" for part in values):
            return "periodic"
        return ",".join(values)
    return str(value).strip().lower()


def _metadata_from_npz(data: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for key in data.files:
        if key in {"links", "links_real", "links_imag"}:
            continue
        value = data[key]
        scalar = _python_scalar(value)
        if isinstance(scalar, np.ndarray):
            scalar = scalar.tolist()
        metadata[key] = scalar
    return metadata


def _metadata_sidecar(path: Path) -> Path | None:
    candidates = [
        path.with_suffix(path.suffix + ".meta.json"),
        path.with_suffix(".meta.json"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _extract_json_links(payload: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    metadata = dict(payload.get("metadata", {}))
    for key in (
        "schema",
        "axis_order",
        "gauge_group",
        "boundary_conditions",
        "time_direction",
        *ENSEMBLE_METADATA_FOR_SIGMA,
    ):
        if key in payload and key not in metadata:
            metadata[key] = payload[key]

    if "links_real" in payload and "links_imag" in payload:
        real = np.asarray(payload["links_real"], dtype=np.float64)
        imag = np.asarray(payload["links_imag"], dtype=np.float64)
        if real.shape != imag.shape:
            raise LinkFormatError("links_real and links_imag have different shapes")
        return real + 1j * imag, metadata
    raise LinkFormatError(
        "JSON link ensembles require both links_real and links_imag"
    )


def _load_raw_links(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".npz":
        with np.load(path, allow_pickle=False) as data:
            metadata = _metadata_from_npz(data)
            if "links" in data.files:
                links = np.asarray(data["links"])
            elif {"links_real", "links_imag"}.issubset(data.files):
                real = np.asarray(data["links_real"], dtype=np.float64)
                imag = np.asarray(data["links_imag"], dtype=np.float64)
                if real.shape != imag.shape:
                    raise LinkFormatError(
                        "links_real and links_imag have different shapes"
                    )
                links = real + 1j * imag
            else:
                raise LinkFormatError(
                    "NPZ has no links or links_real/links_imag arrays"
                )
        return links, metadata

    if suffix == ".npy":
        sidecar = _metadata_sidecar(path)
        if sidecar is None:
            raise LinkFormatError(
                "NPY requires <file>.npy.meta.json or <file>.meta.json metadata"
            )
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        return np.asarray(np.load(path, allow_pickle=False)), metadata

    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise LinkFormatError("JSON top level must be an object")
        if PROXY_KEYS.issubset(payload):
            raise LinkFormatError(
                "Einstein--dilaton endpoint proxy is not a link ensemble"
            )
        return _extract_json_links(payload)

    raise LinkFormatError(f"unsupported link format: {suffix or '<none>'}")


def _validate_metadata(metadata: dict[str, Any], original_ndim: int) -> dict[str, Any]:
    missing = [
        key
        for key in (
            "schema",
            "axis_order",
            "gauge_group",
            "boundary_conditions",
            "time_direction",
        )
        if key not in metadata
    ]
    if missing:
        raise LinkFormatError(
            "missing structural metadata: " + ", ".join(missing)
        )

    if str(metadata["schema"]) != LINK_SCHEMA:
        raise LinkFormatError(
            f"schema must be {LINK_SCHEMA!r}, got {metadata['schema']!r}"
        )
    group = str(metadata["gauge_group"]).replace(" ", "").upper()
    if group not in {"SU(3)", "SU3"}:
        raise LinkFormatError(f"gauge_group must be SU(3), got {group!r}")
    if _normalise_boundary_conditions(metadata["boundary_conditions"]) != "periodic":
        raise LinkFormatError("all four lattice directions must be periodic")
    if int(metadata["time_direction"]) != 3:
        raise LinkFormatError(
            "canonical format requires time_direction=3 (the t axis)"
        )

    axis_order = _normalise_axis_order(metadata["axis_order"])
    expected = (
        SINGLE_CONFIG_AXIS_ORDER if original_ndim == 7 else CANONICAL_AXIS_ORDER
    )
    if axis_order != expected:
        raise LinkFormatError(
            f"axis_order must be {expected!r} for a {original_ndim}D array, "
            f"got {axis_order!r}"
        )
    return {
        "schema": LINK_SCHEMA,
        "axis_order": CANONICAL_AXIS_ORDER,
        "gauge_group": "SU(3)",
        "boundary_conditions": "periodic",
        "time_direction": 3,
    }


def validate_su3_links(
    links: np.ndarray, *, tolerance: float = 1e-6, chunk_size: int = 32768
) -> tuple[np.ndarray, dict[str, Any]]:
    """Validate shape, finiteness, unitarity and determinant of every link."""

    array = np.asarray(links)
    original_ndim = array.ndim
    if original_ndim == 7:
        array = array[np.newaxis, ...]
    if array.ndim != 8:
        raise LinkFormatError(
            "links must have shape [Ncfg,Lx,Ly,Lz,Lt,4,3,3] or "
            "[Lx,Ly,Lz,Lt,4,3,3]"
        )
    if array.shape[-3:] != (4, 3, 3):
        raise LinkFormatError(
            f"last axes must be [mu,row,col]=[4,3,3], got {array.shape[-3:]}"
        )
    if array.shape[0] < 1 or any(length < 2 for length in array.shape[1:5]):
        raise LinkFormatError(
            "need at least one configuration and lattice extents >=2"
        )
    if not np.issubdtype(array.dtype, np.complexfloating):
        if np.issubdtype(array.dtype, np.number):
            array = array.astype(np.complex128)
        else:
            raise LinkFormatError("link matrices must be numeric")
    else:
        array = array.astype(np.complex128, copy=False)
    if not np.all(np.isfinite(array.real)) or not np.all(np.isfinite(array.imag)):
        raise LinkFormatError("link matrices contain non-finite values")

    flat = array.reshape(-1, 3, 3)
    identity = np.eye(3, dtype=np.complex128)
    max_unitarity = 0.0
    max_det = 0.0
    for start in range(0, flat.shape[0], chunk_size):
        block = flat[start : start + chunk_size]
        gram = np.swapaxes(block.conj(), -1, -2) @ block
        unitary_error = np.linalg.norm(gram - identity, axis=(-2, -1))
        determinant_error = np.abs(np.linalg.det(block) - 1.0)
        max_unitarity = max(max_unitarity, float(np.max(unitary_error)))
        max_det = max(max_det, float(np.max(determinant_error)))

    if max_unitarity > tolerance or max_det > tolerance:
        raise LinkFormatError(
            "links fail SU(3) validation: "
            f"max ||U^dagger U-I||_F={max_unitarity:.6g}, "
            f"max |det(U)-1|={max_det:.6g}, tolerance={tolerance:.6g}"
        )
    return array, {
        "all_links_checked": True,
        "n_link_matrices": int(flat.shape[0]),
        "max_unitarity_frobenius_error": max_unitarity,
        "max_determinant_error": max_det,
        "tolerance": tolerance,
    }


def load_link_ensemble(path: Path, *, tolerance: float = 1e-6) -> LoadedLinks:
    raw, metadata = _load_raw_links(path)
    structural = _validate_metadata(metadata, np.asarray(raw).ndim)
    links, validation = validate_su3_links(raw, tolerance=tolerance)
    clean_metadata = dict(metadata)
    clean_metadata.update(structural)
    return LoadedLinks(
        path=path.resolve(),
        links=links,
        metadata=clean_metadata,
        validation=validation,
    )


def _is_candidate(path: Path, *, explicit: bool) -> bool:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES | DETECTED_UNSUPPORTED_SUFFIXES:
        return False
    if explicit or suffix != ".json":
        return True
    lower = path.name.lower()
    if any(token in lower for token in CANDIDATE_TOKENS):
        return True
    # HK-core's tracked SU(3) regression file has no lattice-related token in
    # its filename.  A bounded content sniff finds summary/link payloads while
    # avoiding a full parse of unrelated large JSON artifacts.
    try:
        head = path.read_bytes()[:65536].lower()
    except OSError:
        return False
    return any(
        marker in head
        for marker in (
            b'"links"',
            b'"links_real"',
            b'"plaquette_mean"',
            b'"correlator"',
            b'"sigma_eff_gev2"',
        )
    )


def discover_files(sources: Sequence[Path]) -> list[Path]:
    found: set[Path] = set()
    ignored_dirs = {".git", "target", "build", "__pycache__"}
    for source in sources:
        source = source.expanduser().resolve()
        if source.is_file():
            if _is_candidate(source, explicit=True):
                found.add(source)
            continue
        if not source.is_dir():
            continue
        for candidate in source.rglob("*"):
            if not candidate.is_file():
                continue
            if any(part in ignored_dirs for part in candidate.parts):
                continue
            if _is_candidate(candidate, explicit=False):
                found.add(candidate.resolve())
    return sorted(found, key=lambda item: str(item))


def inspect_file(path: Path, *, tolerance: float = 1e-6) -> tuple[dict[str, Any], LoadedLinks | None]:
    record: dict[str, Any] = {
        "path": portable_path(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "usable_link_ensemble": False,
    }
    suffix = path.suffix.lower()
    if suffix in DETECTED_UNSUPPORTED_SUFFIXES:
        record.update(
            {
                "classification": "detected_format_without_loader",
                "reason": (
                    f"{suffix} detected but no schema-safe loader is implemented; "
                    "convert explicitly to the canonical NPZ/JSON contract"
                ),
            }
        )
        return record, None

    json_payload: dict[str, Any] | None = None
    if suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            record.update(
                {"classification": "invalid_json", "reason": str(exc)}
            )
            return record, None
        if isinstance(payload, dict):
            json_payload = payload
        if json_payload is not None and PROXY_KEYS.issubset(json_payload):
            record.update(
                {
                    "classification": "excluded_ed_endpoint_proxy",
                    "reason": (
                        "contains e2A_ir, alpha_prime_GeV-2 and "
                        "sigma_eff_GeV2 but no gauge links; it is not a "
                        "Wilson-loop observable"
                    ),
                }
            )
            return record, None

    try:
        loaded = load_link_ensemble(path, tolerance=tolerance)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        reason = str(exc)
        classification = "observable_summary_without_links"
        if "unsupported link format" in reason:
            classification = "unsupported_format"
        elif suffix in {".npz", ".npy"}:
            classification = "invalid_or_incomplete_link_container"
        elif json_payload is not None:
            result = json_payload.get("result")
            if isinstance(result, dict) and isinstance(result.get("trace_id"), str):
                record["summary_trace_id"] = result["trace_id"]
                record["available_result_fields"] = sorted(result)
                reason = (
                    "serialized plaquette/correlator analysis has no links, "
                    "links_real or links_imag field"
                )
            elif "files" in json_payload and "summary" in json_payload:
                classification = "manifest_without_link_matrices"
                record["available_top_level_fields"] = sorted(json_payload)
                reason = "bundle manifest references outputs but stores no gauge links"
        record.update({"classification": classification, "reason": reason})
        return record, None

    record.update(
        {
            "classification": "genuine_su3_link_ensemble",
            "usable_link_ensemble": True,
            "shape": list(loaded.links.shape),
            "metadata": loaded.metadata,
            "validation": loaded.validation,
        }
    )
    return record, loaded


def _metadata_equal(a: Any, b: Any) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        try:
            return bool(math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1e-14))
        except (TypeError, ValueError):
            return False
    return a == b


def combine_link_ensembles(items: Sequence[LoadedLinks]) -> tuple[np.ndarray, dict[str, Any]]:
    if not items:
        raise LinkFormatError("no usable link ensemble")
    shape = items[0].links.shape[1:]
    reference = items[0].metadata
    required_consistent = (
        "axis_order",
        "gauge_group",
        "boundary_conditions",
        "time_direction",
        *ENSEMBLE_METADATA_FOR_SIGMA,
    )
    for item in items[1:]:
        if item.links.shape[1:] != shape:
            raise LinkFormatError(
                "link sources have incompatible lattice shapes: "
                f"{shape} versus {item.links.shape[1:]}"
            )
        for key in required_consistent:
            if key in reference or key in item.metadata:
                if key not in reference or key not in item.metadata:
                    raise LinkFormatError(
                        f"metadata {key!r} is missing from one source"
                    )
                if not _metadata_equal(reference[key], item.metadata[key]):
                    raise LinkFormatError(
                        f"metadata {key!r} differs across link sources"
                    )
    return np.concatenate([item.links for item in items], axis=0), dict(reference)


def wilson_rectangle(
    configuration: np.ndarray,
    origin: Sequence[int],
    spatial_direction: int,
    r: int,
    t: int,
    *,
    time_direction: int = 3,
) -> float:
    """Return Re Tr(U_loop)/3 for one oriented R by T rectangle."""

    if configuration.ndim != 7 or configuration.shape[-3:] != (4, 3, 3):
        raise ValueError("configuration must have shape [Lx,Ly,Lz,Lt,4,3,3]")
    if len(origin) != 4:
        raise ValueError("origin must have four coordinates")
    if spatial_direction == time_direction or spatial_direction not in range(4):
        raise ValueError("spatial and time directions must be distinct")
    if time_direction not in range(4) or r < 1 or t < 1:
        raise ValueError("directions and positive R,T are required")

    extents = configuration.shape[:4]
    position = [int(value) % extents[i] for i, value in enumerate(origin)]
    product = np.eye(3, dtype=np.complex128)

    def forward(direction: int) -> None:
        nonlocal product
        product = product @ configuration[(*position, direction)]
        position[direction] = (position[direction] + 1) % extents[direction]

    def backward(direction: int) -> None:
        nonlocal product
        position[direction] = (position[direction] - 1) % extents[direction]
        product = product @ configuration[(*position, direction)].conj().T

    for _ in range(r):
        forward(spatial_direction)
    for _ in range(t):
        forward(time_direction)
    for _ in range(r):
        backward(spatial_direction)
    for _ in range(t):
        backward(time_direction)
    return float(np.trace(product).real / 3.0)


def measure_wilson_loops(
    links: np.ndarray,
    *,
    r_max: int,
    t_max: int,
    time_direction: int = 3,
    tolerance: float = 1e-6,
) -> np.ndarray:
    """Average rectangles over origins and the three spatial orientations.

    The returned array has shape ``[Ncfg, r_max, t_max]`` and keeps the
    per-configuration means needed for blocking and jackknife analysis.
    """

    array, _ = validate_su3_links(links, tolerance=tolerance)
    extents = array.shape[1:5]
    spatial_directions = [direction for direction in range(4) if direction != time_direction]
    max_r_allowed = min(extents[direction] // 2 for direction in spatial_directions)
    max_t_allowed = extents[time_direction] // 2
    if r_max < 1 or r_max > max_r_allowed:
        raise ValueError(
            f"r_max must lie in [1,{max_r_allowed}] to avoid wrapped rectangles"
        )
    if t_max < 1 or t_max > max_t_allowed:
        raise ValueError(
            f"t_max must lie in [1,{max_t_allowed}] to avoid wrapped rectangles"
        )

    output = np.zeros((array.shape[0], r_max, t_max), dtype=np.float64)
    origins = tuple(np.ndindex(*extents))
    denominator = float(len(origins) * len(spatial_directions))
    for config_index, configuration in enumerate(array):
        for r in range(1, r_max + 1):
            for t in range(1, t_max + 1):
                total = 0.0
                for origin in origins:
                    for direction in spatial_directions:
                        total += wilson_rectangle(
                            configuration,
                            origin,
                            direction,
                            r,
                            t,
                            time_direction=time_direction,
                        )
                output[config_index, r - 1, t - 1] = total / denominator
    return output


def _blocked_leave_one_out(
    values: np.ndarray, block_size: int
) -> tuple[np.ndarray, np.ndarray | None, dict[str, int]]:
    if block_size < 1:
        raise ValueError("block_size must be >=1")
    n_configurations = values.shape[0]
    n_blocks = n_configurations // block_size
    n_used = n_blocks * block_size
    discarded = n_configurations - n_used
    if n_blocks == 0:
        raise ValueError("block_size is larger than the number of configurations")
    block_means = values[:n_used].reshape(
        n_blocks, block_size, *values.shape[1:]
    ).mean(axis=1)
    mean = block_means.mean(axis=0)
    leave_one_out = None
    if n_blocks >= 2:
        leave_one_out = (
            block_means.sum(axis=0)[None, ...] - block_means
        ) / float(n_blocks - 1)
    return mean, leave_one_out, {
        "block_size_configurations": block_size,
        "n_blocks": n_blocks,
        "n_configurations_used": n_used,
        "n_configurations_discarded_tail": discarded,
    }


def _jackknife_standard_error(values: np.ndarray) -> float:
    n = values.shape[0]
    if n < 2:
        raise ValueError("at least two leave-one-out values are required")
    centre = values.mean(axis=0)
    variance = (n - 1.0) / n * np.sum(np.square(values - centre), axis=0)
    return float(np.sqrt(max(float(variance), 0.0)))


def _positive_log_ratio(numerator: float, denominator: float) -> float | None:
    if not (math.isfinite(numerator) and math.isfinite(denominator)):
        return None
    if numerator <= 0.0 or denominator <= 0.0:
        return None
    return math.log(numerator / denominator)


def creutz_ratio(loop_means: np.ndarray, r: int, t: int) -> float | None:
    """Return chi(R,T), with R,T one-based and both at least two."""

    if r < 2 or t < 2 or r > loop_means.shape[0] or t > loop_means.shape[1]:
        return None
    w_rt = float(loop_means[r - 1, t - 1])
    w_prev = float(loop_means[r - 2, t - 2])
    w_r_tm1 = float(loop_means[r - 1, t - 2])
    w_rm1_t = float(loop_means[r - 2, t - 1])
    if min(w_rt, w_prev, w_r_tm1, w_rm1_t) <= 0.0:
        return None
    ratio = w_rt * w_prev / (w_r_tm1 * w_rm1_t)
    if not math.isfinite(ratio) or ratio <= 0.0:
        return None
    return -math.log(ratio)


def _jackknife_transform(
    leave_one_out: np.ndarray | None, transform: Any
) -> tuple[float | None, list[float] | None]:
    if leave_one_out is None:
        return None, None
    transformed: list[float] = []
    for sample in leave_one_out:
        value = transform(sample)
        if value is None or not math.isfinite(value):
            return None, None
        transformed.append(float(value))
    array = np.asarray(transformed, dtype=np.float64)
    return _jackknife_standard_error(array), transformed


def summarize_wilson_tables(
    per_configuration: np.ndarray, *, block_size: int
) -> tuple[dict[str, Any], np.ndarray, np.ndarray | None]:
    mean, leave_one_out, blocking = _blocked_leave_one_out(
        per_configuration, block_size
    )
    wilson_records: list[dict[str, Any]] = []
    potential_records: list[dict[str, Any]] = []
    creutz_records: list[dict[str, Any]] = []

    for r in range(1, mean.shape[0] + 1):
        for t in range(1, mean.shape[1] + 1):
            error = None
            if leave_one_out is not None:
                error = _jackknife_standard_error(leave_one_out[:, r - 1, t - 1])
            wilson_records.append(
                {"R": r, "T": t, "mean": float(mean[r - 1, t - 1]), "standard_error": error}
            )

    for r in range(1, mean.shape[0] + 1):
        for t in range(1, mean.shape[1]):
            value = _positive_log_ratio(
                float(mean[r - 1, t - 1]), float(mean[r - 1, t])
            )
            error, _ = _jackknife_transform(
                leave_one_out,
                lambda sample, rr=r, tt=t: _positive_log_ratio(
                    float(sample[rr - 1, tt - 1]),
                    float(sample[rr - 1, tt]),
                ),
            )
            potential_records.append(
                {
                    "R": r,
                    "T_mid": t + 0.5,
                    "aV_eff": value,
                    "standard_error": error,
                    "valid": value is not None,
                }
            )

    for r in range(2, mean.shape[0] + 1):
        for t in range(2, mean.shape[1] + 1):
            value = creutz_ratio(mean, r, t)
            error, samples = _jackknife_transform(
                leave_one_out,
                lambda sample, rr=r, tt=t: creutz_ratio(sample, rr, tt),
            )
            creutz_records.append(
                {
                    "R": r,
                    "T": t,
                    "chi": value,
                    "standard_error": error,
                    "valid": value is not None and samples is not None,
                    "invalid_reason": (
                        None
                        if value is not None and samples is not None
                        else "non-positive/noisy loop mean or fewer than two blocks"
                    ),
                }
            )

    return (
        {
            "blocking": blocking,
            "wilson_loops": wilson_records,
            "effective_static_potential_lattice_units": potential_records,
            "creutz_ratios": creutz_records,
            "definitions": {
                "wilson": "W(R,T)=<Re Tr product_C U/3>",
                "effective_potential": (
                    "aV_eff(R,T+1/2)=ln[W(R,T)/W(R,T+1)]"
                ),
                "creutz": (
                    "chi(R,T)=-ln[W(R,T)W(R-1,T-1)/"
                    "(W(R,T-1)W(R-1,T))]"
                ),
            },
        },
        mean,
        leave_one_out,
    )


def _parse_sigma_window(value: str | None) -> tuple[int, int, int, int] | None:
    if value is None:
        return None
    try:
        r_text, t_text = value.split(",", maxsplit=1)
        r_min, r_max = (int(item) for item in r_text.split(":"))
        t_min, t_max = (int(item) for item in t_text.split(":"))
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            "sigma window must be RMIN:RMAX,TMIN:TMAX"
        ) from exc
    if r_min < 2 or t_min < 2 or r_max < r_min or t_max < t_min:
        raise argparse.ArgumentTypeError(
            "sigma window requires RMIN,TMIN>=2 and ordered bounds"
        )
    return r_min, r_max, t_min, t_max


def estimate_sigma_a2(
    loop_mean: np.ndarray,
    leave_one_out: np.ndarray | None,
    *,
    sigma_window: tuple[int, int, int, int] | None,
    metadata: dict[str, Any],
    n_blocks: int,
    max_relative_spread: float = 0.25,
) -> dict[str, Any]:
    """Gate a constant large-loop Creutz estimate in lattice units."""

    base: dict[str, Any] = {
        "quantity": "sigma_a2",
        "units": "dimensionless_lattice_units",
        "value": None,
        "standard_error": None,
        "not_continuum_extrapolated": True,
        "not_a_physical_GeV_scale": True,
    }
    if sigma_window is None:
        base.update(
            {
                "status": "not_estimated_no_preregistered_large_loop_window",
                "reason": (
                    "Creutz values are reported individually; pass an explicit "
                    "RMIN:RMAX,TMIN:TMAX window to test a plateau"
                ),
            }
        )
        return base

    r_min, r_max, t_min, t_max = sigma_window
    base["window"] = {
        "R_min": r_min,
        "R_max": r_max,
        "T_min": t_min,
        "T_max": t_max,
    }
    if r_max > loop_mean.shape[0] or t_max > loop_mean.shape[1]:
        base.update(
            {"status": "blocked_window_outside_measured_loop_table", "reason": "increase r_max/t_max or reduce the requested window"}
        )
        return base

    coordinates = [
        (r, t)
        for r in range(r_min, r_max + 1)
        for t in range(t_min, t_max + 1)
    ]
    values = [creutz_ratio(loop_mean, r, t) for r, t in coordinates]
    if len(values) < 3:
        base.update(
            {"status": "blocked_too_few_large_loop_points", "reason": "at least three Creutz cells are required"}
        )
        return base
    if any(value is None or value <= 0.0 for value in values):
        base.update(
            {"status": "blocked_nonpositive_or_noisy_creutz_values", "reason": "every loop and Creutz value in the window must be positive"}
        )
        return base
    numeric_values = np.asarray(values, dtype=np.float64)
    diagnostic_mean = float(np.mean(numeric_values))
    relative_spread = float(np.ptp(numeric_values) / abs(diagnostic_mean))
    base.update(
        {
            "diagnostic_unweighted_mean": diagnostic_mean,
            "relative_range_across_window": relative_spread,
            "max_allowed_relative_range": max_relative_spread,
            "n_cells": len(coordinates),
        }
    )
    missing_metadata = [
        key for key in ENSEMBLE_METADATA_FOR_SIGMA if key not in metadata
    ]
    if missing_metadata:
        base.update(
            {
                "status": "blocked_missing_ensemble_metadata",
                "missing_metadata": missing_metadata,
                "reason": "the configurations cannot be certified as one equilibrated ensemble",
            }
        )
        return base
    if n_blocks < 4 or leave_one_out is None:
        base.update(
            {
                "status": "blocked_insufficient_jackknife_blocks",
                "reason": "at least four blocked samples are required",
            }
        )
        return base
    if relative_spread > max_relative_spread:
        base.update(
            {
                "status": "blocked_no_large_loop_plateau",
                "reason": "Creutz ratios are not stable across the requested window",
            }
        )
        return base

    jackknife_estimates: list[float] = []
    for sample in leave_one_out:
        sample_values = [creutz_ratio(sample, r, t) for r, t in coordinates]
        if any(value is None or value <= 0.0 for value in sample_values):
            base.update(
                {
                    "status": "blocked_unstable_jackknife_creutz_values",
                    "reason": "at least one leave-one-block sample is non-positive",
                }
            )
            return base
        jackknife_estimates.append(float(np.mean(sample_values)))

    base.update(
        {
            "status": "diagnostic_lattice_plateau_estimate",
            "value": diagnostic_mean,
            "standard_error": _jackknife_standard_error(
                np.asarray(jackknife_estimates, dtype=np.float64)
            ),
            "evidence_boundary": (
                "This is sigma*a^2 at one bare coupling and finite volume. "
                "Several beta values, volumes and a continuum extrapolation "
                "are still required for a continuum Yang--Mills result."
            ),
        }
    )
    return base


def physical_scale_conversion(
    sigma_a2: dict[str, Any], inverse_lattice_spacing_gev: float | None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "not_available",
        "inverse_lattice_spacing_GeV": inverse_lattice_spacing_gev,
        "sigma_GeV2": None,
        "sqrt_sigma_GeV": None,
        "endpoint_proxy_used": False,
        "required_external_input": (
            "an independently scale-set a^{-1} in GeV, e.g. from r0/a plus "
            "an external r0 convention; it cannot come from the ED endpoint proxy"
        ),
    }
    value = sigma_a2.get("value")
    if value is None:
        result["reason"] = "sigma*a^2 has not passed the lattice plateau gate"
        return result
    if inverse_lattice_spacing_gev is None:
        result["reason"] = "no independent inverse lattice spacing supplied"
        return result
    if not math.isfinite(inverse_lattice_spacing_gev) or inverse_lattice_spacing_gev <= 0.0:
        raise ValueError("inverse_lattice_spacing_gev must be finite and positive")
    sigma_gev2 = float(value) * inverse_lattice_spacing_gev**2
    result.update(
        {
            "status": "converted_using_external_lattice_scale",
            "sigma_GeV2": sigma_gev2,
            "sqrt_sigma_GeV": math.sqrt(sigma_gev2),
            "evidence_boundary": (
                "The GeV normalization is inherited from the supplied scale; "
                "it is not an additional lattice prediction."
            ),
        }
    )
    return result


def _missing_manifest(
    inspections: list[dict[str, Any]], sources: Sequence[Path]
) -> dict[str, Any]:
    return {
        "schema": ANALYSIS_SCHEMA,
        "status": "blocked_missing_link_configurations",
        "fail_closed": True,
        "sources_scanned": [portable_path(path) for path in sources],
        "discovered_files": inspections,
        "measurements": None,
        "sigma_a2": {
            "status": "not_computable_without_link_configurations",
            "value": None,
            "units": "dimensionless_lattice_units",
        },
        "physical_scale": {
            "status": "not_available",
            "sigma_GeV2": None,
            "endpoint_proxy_used": False,
        },
        "missing_data": [
            {
                "id": "su3_link_matrices",
                "required": True,
                "contract": (
                    "One or more thermalized configurations with shape "
                    "[Ncfg,Lx,Ly,Lz,Lt,4,3,3], complex SU(3) matrices, "
                    "canonical axis metadata and periodic boundaries"
                ),
                "producer_gap": (
                    "HK-core currently serializes plaquette/correlator summaries "
                    "rather than the Su3Gauge4D link field"
                ),
            },
            {
                "id": "ensemble_provenance",
                "required_for": "sigma_a2_interpretation",
                "fields": list(ENSEMBLE_METADATA_FOR_SIGMA),
            },
            {
                "id": "independent_lattice_scale",
                "required_for": "GeV_conversion_only",
                "acceptable_example": "r0/a together with an external r0_phys",
                "explicitly_rejected": (
                    "instrument_closure/2026-01-04/"
                    "wilson_loop_sigma_from_ed_trace.json"
                ),
            },
        ],
        "evidence_boundary": {
            "plaquette_is_only_W_1_1": True,
            "plaquette_correlator_is_not_static_potential": True,
            "ed_endpoint_proxy_is_not_wilson_data": True,
            "lattice_spacing_a_is_not_a_physical_compactification_length": True,
        },
    }


def analyze_sources(
    sources: Sequence[Path],
    *,
    r_max: int = 3,
    t_max: int = 3,
    block_size: int = 1,
    sigma_window: tuple[int, int, int, int] | None = None,
    inverse_lattice_spacing_gev: float | None = None,
    tolerance: float = 1e-6,
) -> dict[str, Any]:
    files = discover_files(sources)
    inspections: list[dict[str, Any]] = []
    loaded_items: list[LoadedLinks] = []
    for path in files:
        inspection, loaded = inspect_file(path, tolerance=tolerance)
        inspections.append(inspection)
        if loaded is not None:
            loaded_items.append(loaded)

    if not loaded_items:
        return _missing_manifest(inspections, sources)

    try:
        links, metadata = combine_link_ensembles(loaded_items)
    except LinkFormatError as exc:
        result = _missing_manifest(inspections, sources)
        result["status"] = "blocked_incompatible_link_ensembles"
        result["combination_error"] = str(exc)
        return result

    per_configuration = measure_wilson_loops(
        links,
        r_max=r_max,
        t_max=t_max,
        time_direction=int(metadata["time_direction"]),
        tolerance=tolerance,
    )
    tables, loop_mean, leave_one_out = summarize_wilson_tables(
        per_configuration, block_size=block_size
    )
    sigma = estimate_sigma_a2(
        loop_mean,
        leave_one_out,
        sigma_window=sigma_window,
        metadata=metadata,
        n_blocks=tables["blocking"]["n_blocks"],
    )
    physical = physical_scale_conversion(sigma, inverse_lattice_spacing_gev)
    valid_creutz = sum(
        bool(record["valid"]) for record in tables["creutz_ratios"]
    )
    return {
        "schema": ANALYSIS_SCHEMA,
        "status": (
            "sigma_a2_estimated_lattice_units"
            if sigma["value"] is not None
            else "wilson_loops_computed_sigma_not_established"
        ),
        "fail_closed": True,
        "sources_scanned": [portable_path(path) for path in sources],
        "discovered_files": inspections,
        "ensemble": {
            "n_configurations": int(links.shape[0]),
            "lattice_extents": list(links.shape[1:5]),
            "metadata": metadata,
            "all_sources_are_genuine_links": True,
        },
        "measurements": tables,
        "sigma_a2": sigma,
        "physical_scale": physical,
        "passes": {
            "genuine_links_loaded": True,
            "wilson_loops_computed": True,
            "at_least_one_creutz_ratio_with_jackknife": valid_creutz > 0,
            "sigma_a2_plateau_gate": sigma["value"] is not None,
            "physical_scale_independently_supplied": physical["status"]
            == "converted_using_external_lattice_scale",
        },
        "evidence_boundary": {
            "native_observables": ["W(R,T)", "aV_eff(R,T)", "sigma*a^2 estimator"],
            "requires_continuum_campaign": True,
            "endpoint_proxy_used": False,
            "physical_compactification_length_identified": False,
            "compactification_requirement": (
                "A separate theory prediction for ell*sqrt(sigma), or a/ell, "
                "is required; setting ell=a would be an extra matching assumption."
            ),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Measure genuine rectangular Wilson loops from canonical SU(3) "
            "link ensembles, or write a fail-closed missing-data manifest."
        )
    )
    parser.add_argument(
        "--source",
        action="append",
        type=Path,
        help=(
            "Input file/directory; repeat as needed. Defaults to HK-core 4D "
            "SU(3) results and HOLO instrument_closure."
        ),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--r-max", type=int, default=3)
    parser.add_argument("--t-max", type=int, default=3)
    parser.add_argument("--block-size", type=int, default=1)
    parser.add_argument(
        "--sigma-window",
        type=_parse_sigma_window,
        help="Explicit Creutz plateau window RMIN:RMAX,TMIN:TMAX",
    )
    parser.add_argument(
        "--inverse-lattice-spacing-gev",
        type=float,
        help="Independent external a^{-1} in GeV; never inferred from ED",
    )
    parser.add_argument("--su3-tolerance", type=float, default=1e-6)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sources = args.source if args.source else default_scan_roots()
    result = analyze_sources(
        sources,
        r_max=args.r_max,
        t_max=args.t_max,
        block_size=args.block_size,
        sigma_window=args.sigma_window,
        inverse_lattice_spacing_gev=args.inverse_lattice_spacing_gev,
        tolerance=args.su3_tolerance,
    )
    _json_dump(args.output, result)
    print(f"[{result['status']}] {args.output}")
    return 2 if result["status"].startswith("blocked_") else 0


if __name__ == "__main__":
    raise SystemExit(main())
