#!/usr/bin/env python3
"""Retrospective galaxy-level cross-validation of the SPARC P5 readout.

The five P5 parameters and the one RAR acceleration scale are fitted only on
the already-frozen training galaxies.  Validation is reported once and is not
used for model selection.  Test galaxies are evaluated with frozen parameters.
This is retrospective cross-validation, not a blind confirmation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import scipy
from scipy.optimize import differential_evolution, minimize_scalar


SCHEMA = "sparc-p5-retrospective-crossval-v1"
CLASSIFICATION = "retrospective_cross_validation_not_blind_confirmation"
OPTIMIZER_SEED = 20260829
BOOTSTRAP_SEED = 5812387
DEFAULT_BOOTSTRAP_REPLICATES = 10_000
DEFAULT_MAXITER = 100
P5_BOUNDS: tuple[tuple[float, float], ...] = (
    (0.05, 0.8),  # A
    (0.5, 2.5),  # n
    (0.3, 2.0),  # m
    (0.2, 1.0),  # gamma
    (0.1, 0.8),  # Sigma0
)
RAR_LOG10_G_DAGGER_SI_BOUNDS = (-11.0, -9.0)
KPC_METRES = 3.085677581491367e19


@dataclass(frozen=True)
class Galaxy:
    name: str
    radius_kpc: np.ndarray
    v_obs_kms: np.ndarray
    sigma_v_kms: np.ndarray
    v_bary_kms: np.ndarray
    x_radius: np.ndarray
    sigma_b_norm: np.ndarray
    delta_ed: np.ndarray

    @property
    def points(self) -> int:
        return int(self.radius_kpc.size)


@dataclass(frozen=True)
class P5Params:
    A: float
    n: float
    m: float
    gamma: float
    Sigma0: float

    @classmethod
    def from_vector(cls, values: Sequence[float]) -> "P5Params":
        if len(values) != 5:
            raise ValueError("P5 requires exactly five parameters")
        return cls(*(float(value) for value in values))

    def as_dict(self) -> dict[str, float]:
        return {
            "A": self.A,
            "n": self.n,
            "m": self.m,
            "gamma": self.gamma,
            "Sigma0": self.Sigma0,
        }


def factory_dir() -> Path:
    return Path(__file__).resolve().parent


def default_repo_sibling(name: str) -> Path:
    return Path(__file__).resolve().parents[3] / name


def default_sparc_dir() -> Path:
    return default_repo_sibling("HOLO_TRANSDUCTOR_V2") / "data/external/SPARC/sparc_175"


def default_trace_path() -> Path:
    return default_repo_sibling("HOLO_TRANSDUCTOR_V2") / "data/internal/holo_physics_trace_ed_industrial.json"


def default_forward_artifact_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "A_single_Einstein_Dilaton geometry/artifacts/sparc_forward_eval.json"
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def aggregate_dataset_sha256(data_dir: Path) -> tuple[str, int]:
    files = sorted(data_dir.glob("*_rotmod.csv"), key=lambda path: path.name)
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_sha256(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest(), len(files)


def audit_dataset(data_dir: Path) -> dict[str, Any]:
    point_counts: list[int] = []
    velocity_errors: list[float] = []
    negative_gas_points = 0
    negative_gas_galaxies = 0
    zero_surface_brightness_points = 0
    zero_surface_brightness_galaxies = 0
    vbar_component_max_absdiff = 0.0
    files = sorted(data_dir.glob("*_rotmod.csv"), key=lambda path: path.name)
    for path in files:
        points = 0
        has_negative_gas = False
        has_zero_surface_brightness = False
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                points += 1
                error = _float_row(row, "eVobs_kms", path)
                vgas = _float_row(row, "Vgas_kms", path)
                vdisk = _float_row(row, "Vdisk_kms", path)
                vbul = _float_row(row, "Vbul_kms", path)
                vbar = _float_row(row, "Vbar_kms", path)
                sigma_b = _float_row(row, "SBdisk", path) + _float_row(
                    row, "SBbul", path
                )
                velocity_errors.append(error)
                if vgas < 0:
                    negative_gas_points += 1
                    has_negative_gas = True
                if sigma_b == 0:
                    zero_surface_brightness_points += 1
                    has_zero_surface_brightness = True
                unsigned_component_vbar = math.sqrt(
                    vgas * vgas + vdisk * vdisk + vbul * vbul
                )
                vbar_component_max_absdiff = max(
                    vbar_component_max_absdiff, abs(vbar - unsigned_component_vbar)
                )
        point_counts.append(points)
        negative_gas_galaxies += int(has_negative_gas)
        zero_surface_brightness_galaxies += int(has_zero_surface_brightness)
    return {
        "galaxies": len(files),
        "velocity_points": sum(point_counts),
        "points_per_galaxy_min": min(point_counts),
        "points_per_galaxy_median": float(np.median(point_counts)),
        "points_per_galaxy_max": max(point_counts),
        "reported_velocity_error_kms_min": min(velocity_errors),
        "reported_velocity_error_kms_median": float(np.median(velocity_errors)),
        "reported_velocity_error_kms_max": max(velocity_errors),
        "negative_vgas_points": negative_gas_points,
        "negative_vgas_galaxies": negative_gas_galaxies,
        "zero_disk_plus_bulge_surface_brightness_points": zero_surface_brightness_points,
        "zero_disk_plus_bulge_surface_brightness_galaxies": zero_surface_brightness_galaxies,
        "vbar_vs_unsigned_component_quadrature_max_absdiff_kms": vbar_component_max_absdiff,
        "vbar_warning": "The local Vbar column uses unsigned component quadrature. Negative Vgas signs therefore do not subtract from Vbar; this historical conversion is retained identically for P5 and every baseline in this report.",
    }


def load_split(path: Path) -> dict[str, list[str]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    groups = payload.get("groups")
    if not isinstance(groups, dict):
        raise ValueError("split document has no groups object")
    expected = {"train": 122, "validation": 26, "test": 27}
    parsed: dict[str, list[str]] = {}
    for group, expected_count in expected.items():
        names = groups.get(group)
        if not isinstance(names, list) or len(names) != expected_count:
            raise ValueError(f"split {group} must contain {expected_count} galaxy IDs")
        if any(not isinstance(name, str) or not name for name in names):
            raise ValueError(f"split {group} contains an invalid galaxy ID")
        parsed[group] = list(names)
    all_names = [name for names in parsed.values() for name in names]
    if len(set(all_names)) != 175:
        raise ValueError("split groups overlap or do not cover 175 unique galaxies")
    return parsed


def load_trace(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    trace = payload.get("trace", payload)
    z = np.asarray(trace["z"], dtype=float)
    delta = np.asarray(trace["delta"], dtype=float)
    if z.ndim != 1 or delta.shape != z.shape or z.size < 2:
        raise ValueError("trace z and delta must be equal one-dimensional arrays")
    if not np.all(np.isfinite(z)) or not np.all(np.isfinite(delta)):
        raise ValueError("trace contains non-finite values")
    order = np.argsort(z)
    z = z[order]
    delta = delta[order]
    if np.any(np.diff(z) <= 0):
        raise ValueError("trace coordinate must be strictly increasing")
    return z, delta


def _float_row(row: Mapping[str, str], field: str, source: Path) -> float:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"invalid {field} in {source.name}") from error
    if not math.isfinite(value):
        raise ValueError(f"non-finite {field} in {source.name}")
    return value


def load_galaxy(path: Path, trace_z: np.ndarray, trace_delta: np.ndarray) -> Galaxy:
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            rows.append(
                {
                    field: _float_row(raw, field, path)
                    for field in (
                        "R_kpc",
                        "Vobs_kms",
                        "eVobs_kms",
                        "Vbar_kms",
                        "SBdisk",
                        "SBbul",
                    )
                }
            )
    if not rows:
        raise ValueError(f"no usable rows in {path.name}")
    radius = np.asarray([row["R_kpc"] for row in rows], dtype=float)
    v_obs = np.asarray([row["Vobs_kms"] for row in rows], dtype=float)
    sigma_v = np.asarray([row["eVobs_kms"] for row in rows], dtype=float)
    v_bary = np.asarray([row["Vbar_kms"] for row in rows], dtype=float)
    sigma_b = np.asarray([row["SBdisk"] + row["SBbul"] for row in rows], dtype=float)
    if np.any(radius <= 0) or np.any(np.diff(radius) <= 0):
        raise ValueError(f"radii must be positive and increasing in {path.name}")
    if np.any(sigma_v <= 0):
        raise ValueError(f"velocity errors must be positive in {path.name}")
    if np.any(v_bary < 0) or np.any(sigma_b < 0):
        raise ValueError(f"baryonic inputs must be non-negative in {path.name}")
    x_radius = radius / radius[-1]
    sigma_max = float(np.max(sigma_b))
    sigma_b_norm = sigma_b / sigma_max if sigma_max > 0 else np.zeros_like(sigma_b)
    z_query = float(trace_z[0]) + (float(trace_z[-1]) - float(trace_z[0])) * x_radius
    delta_ed = np.interp(z_query, trace_z, trace_delta)
    return Galaxy(
        name=path.name.removesuffix("_rotmod.csv"),
        radius_kpc=radius,
        v_obs_kms=v_obs,
        sigma_v_kms=sigma_v,
        v_bary_kms=v_bary,
        x_radius=x_radius,
        sigma_b_norm=sigma_b_norm,
        delta_ed=delta_ed,
    )


def load_galaxies(
    data_dir: Path,
    names: Iterable[str],
    trace_z: np.ndarray,
    trace_delta: np.ndarray,
) -> list[Galaxy]:
    galaxies: list[Galaxy] = []
    for name in names:
        path = data_dir / f"{name}_rotmod.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing SPARC file for split ID {name}")
        galaxies.append(load_galaxy(path, trace_z, trace_delta))
    return galaxies


def predict_p5(galaxy: Galaxy, params: P5Params) -> np.ndarray:
    density_factor = np.power(
        1.0 / (1.0 + galaxy.sigma_b_norm / params.Sigma0), params.n
    )
    delta_missing = params.A * density_factor * np.power(galaxy.x_radius, params.m)
    weight = np.power(galaxy.x_radius, params.gamma)
    delta_total = np.clip(
        (1.0 - weight) * galaxy.delta_ed + weight * delta_missing,
        0.0,
        0.4,
    )
    return galaxy.v_bary_kms * np.sqrt(1.0 + delta_total)


def predict_newton(galaxy: Galaxy) -> np.ndarray:
    return galaxy.v_bary_kms.copy()


def predict_rar(galaxy: Galaxy, g_dagger_si: float) -> np.ndarray:
    if not math.isfinite(g_dagger_si) or g_dagger_si <= 0:
        raise ValueError("RAR acceleration scale must be positive and finite")
    radius_metres = galaxy.radius_kpc * KPC_METRES
    g_bar_si = np.square(galaxy.v_bary_kms) * 1.0e6 / radius_metres
    sqrt_ratio = np.sqrt(np.maximum(g_bar_si / g_dagger_si, 0.0))
    denominator = -np.expm1(-sqrt_ratio)
    g_obs_si = np.divide(
        g_bar_si,
        denominator,
        out=np.zeros_like(g_bar_si),
        where=denominator > 0,
    )
    return np.sqrt(np.maximum(g_obs_si * radius_metres, 0.0)) / 1000.0


def chi2_and_loglike(galaxy: Galaxy, prediction: np.ndarray) -> tuple[float, float]:
    if prediction.shape != galaxy.v_obs_kms.shape or not np.all(np.isfinite(prediction)):
        return math.inf, -math.inf
    residual_sigma = (prediction - galaxy.v_obs_kms) / galaxy.sigma_v_kms
    chi2 = float(np.dot(residual_sigma, residual_sigma))
    log_normalization = np.log(2.0 * math.pi * np.square(galaxy.sigma_v_kms))
    loglike = float(-0.5 * np.sum(np.square(residual_sigma) + log_normalization))
    return chi2, loglike


def historical_rank_loss(galaxy: Galaxy, prediction: np.ndarray) -> float:
    residual = prediction - galaxy.v_obs_kms
    return float(np.sum(np.square(residual) / (np.square(galaxy.v_obs_kms) + 1.0)))


def _total_chi2(galaxies: Sequence[Galaxy], predictor: Any) -> tuple[float, int]:
    total = 0.0
    points = 0
    for galaxy in galaxies:
        chi2, _ = chi2_and_loglike(galaxy, predictor(galaxy))
        if not math.isfinite(chi2):
            return math.inf, 0
        total += chi2
        points += galaxy.points
    return total, points


def fit_p5(
    train: Sequence[Galaxy],
    *,
    maxiter: int = DEFAULT_MAXITER,
    seed: int = OPTIMIZER_SEED,
) -> tuple[P5Params, dict[str, Any]]:
    if not train:
        raise ValueError("P5 training set is empty")

    def objective(values: np.ndarray) -> float:
        params = P5Params.from_vector(values)
        chi2, points = _total_chi2(train, lambda galaxy: predict_p5(galaxy, params))
        return chi2 / points if points else math.inf

    result = differential_evolution(
        objective,
        P5_BOUNDS,
        seed=seed,
        maxiter=maxiter,
        popsize=12,
        tol=1e-9,
        atol=1e-9,
        workers=1,
        updating="immediate",
        polish=True,
        disp=False,
    )
    params = P5Params.from_vector(result.x)
    receipt = {
        "algorithm": "scipy.optimize.differential_evolution",
        "seed": seed,
        "maxiter": maxiter,
        "popsize": 12,
        "bounds": [list(bound) for bound in P5_BOUNDS],
        "objective": "train total diagonal Gaussian chi2 divided by train velocity-point count",
        "fun": float(result.fun),
        "nfev": int(result.nfev),
        "nit": int(result.nit),
        "success": bool(result.success),
        "message": str(result.message),
    }
    return params, receipt


def fit_rar(train: Sequence[Galaxy]) -> tuple[float, dict[str, Any]]:
    if not train:
        raise ValueError("RAR training set is empty")

    def objective(log10_g: float) -> float:
        g_dagger = 10.0 ** float(log10_g)
        chi2, points = _total_chi2(train, lambda galaxy: predict_rar(galaxy, g_dagger))
        return chi2 / points if points else math.inf

    result = minimize_scalar(
        objective,
        bounds=RAR_LOG10_G_DAGGER_SI_BOUNDS,
        method="bounded",
        options={"xatol": 1e-12, "maxiter": 500},
    )
    g_dagger = 10.0 ** float(result.x)
    receipt = {
        "algorithm": "scipy.optimize.minimize_scalar_bounded",
        "bounds_log10_g_dagger_m_s2": list(RAR_LOG10_G_DAGGER_SI_BOUNDS),
        "objective": "train total diagonal Gaussian chi2 divided by train velocity-point count",
        "fun": float(result.fun),
        "nfev": int(result.nfev),
        "nit": int(result.nit),
        "success": bool(result.success),
        "message": str(result.message),
    }
    return g_dagger, receipt


def p5_bound_hits(params: P5Params, *, tolerance: float = 1e-8) -> list[dict[str, Any]]:
    values = params.as_dict()
    hits: list[dict[str, Any]] = []
    for name, bounds in zip(("A", "n", "m", "gamma", "Sigma0"), P5_BOUNDS):
        value = values[name]
        if math.isclose(value, bounds[0], rel_tol=0.0, abs_tol=tolerance):
            hits.append({"parameter": name, "side": "lower", "bound": bounds[0]})
        if math.isclose(value, bounds[1], rel_tol=0.0, abs_tol=tolerance):
            hits.append({"parameter": name, "side": "upper", "bound": bounds[1]})
    return hits


def evaluate_galaxies(
    galaxies: Sequence[Galaxy], params: P5Params, g_dagger_si: float
) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    for galaxy in galaxies:
        predictions = {
            "p5": predict_p5(galaxy, params),
            "newton": predict_newton(galaxy),
            "rar": predict_rar(galaxy, g_dagger_si),
        }
        row: dict[str, float | int | str] = {
            "name": galaxy.name,
            "points": galaxy.points,
        }
        for model, prediction in predictions.items():
            chi2, loglike = chi2_and_loglike(galaxy, prediction)
            row[f"chi2_{model}"] = chi2
            row[f"loglike_{model}"] = loglike
        rows.append(row)
    return rows


def summarize_rows(rows: Sequence[Mapping[str, float | int | str]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("cannot summarize an empty split")
    total_points = sum(int(row["points"]) for row in rows)
    models = ("p5", "newton", "rar")
    model_metrics: dict[str, dict[str, float]] = {}
    for model in models:
        total_chi2 = sum(float(row[f"chi2_{model}"]) for row in rows)
        total_loglike = sum(float(row[f"loglike_{model}"]) for row in rows)
        per_galaxy_chi2 = [
            float(row[f"chi2_{model}"]) / int(row["points"]) for row in rows
        ]
        per_galaxy_loglike = [
            float(row[f"loglike_{model}"]) / int(row["points"]) for row in rows
        ]
        model_metrics[model] = {
            "chi2": total_chi2,
            "chi2_per_point": total_chi2 / total_points,
            "loglike": total_loglike,
            "loglike_per_point": total_loglike / total_points,
            "median_galaxy_chi2_per_point": float(np.median(per_galaxy_chi2)),
            "median_galaxy_loglike_per_point": float(np.median(per_galaxy_loglike)),
        }

    def comparison(left: str, right: str) -> dict[str, float | int]:
        wins = sum(
            float(row[f"chi2_{left}"]) < float(row[f"chi2_{right}"])
            for row in rows
        )
        return {
            "delta_chi2_left_minus_right": model_metrics[left]["chi2"]
            - model_metrics[right]["chi2"],
            "delta_chi2_per_point_left_minus_right": model_metrics[left]["chi2_per_point"]
            - model_metrics[right]["chi2_per_point"],
            "delta_loglike_per_point_left_minus_right": model_metrics[left]["loglike_per_point"]
            - model_metrics[right]["loglike_per_point"],
            "left_wins_galaxies": wins,
            "left_win_fraction": wins / len(rows),
        }

    return {
        "galaxies": len(rows),
        "velocity_points": total_points,
        "models": model_metrics,
        "comparisons": {
            "p5_vs_newton": comparison("p5", "newton"),
            "p5_vs_rar": comparison("p5", "rar"),
            "rar_vs_newton": comparison("rar", "newton"),
        },
    }


def bootstrap_test_rows(
    rows: Sequence[Mapping[str, float | int | str]],
    *,
    replicates: int = DEFAULT_BOOTSTRAP_REPLICATES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    if not rows or replicates < 100:
        raise ValueError("bootstrap needs rows and at least 100 replicates")
    rng = np.random.default_rng(seed)
    n = len(rows)
    tracked = {
        "p5_chi2_per_point": [],
        "newton_chi2_per_point": [],
        "rar_chi2_per_point": [],
        "p5_median_galaxy_chi2_per_point": [],
        "newton_median_galaxy_chi2_per_point": [],
        "rar_median_galaxy_chi2_per_point": [],
        "p5_minus_newton_delta_loglike_per_point": [],
        "p5_minus_rar_delta_loglike_per_point": [],
        "p5_vs_newton_win_fraction": [],
        "p5_vs_rar_win_fraction": [],
    }
    for _ in range(replicates):
        indices = rng.integers(0, n, size=n)
        sampled = [rows[int(index)] for index in indices]
        summary = summarize_rows(sampled)
        for model in ("p5", "newton", "rar"):
            metrics = summary["models"][model]
            tracked[f"{model}_chi2_per_point"].append(metrics["chi2_per_point"])
            tracked[f"{model}_median_galaxy_chi2_per_point"].append(
                metrics["median_galaxy_chi2_per_point"]
            )
        tracked["p5_minus_newton_delta_loglike_per_point"].append(
            summary["comparisons"]["p5_vs_newton"][
                "delta_loglike_per_point_left_minus_right"
            ]
        )
        tracked["p5_minus_rar_delta_loglike_per_point"].append(
            summary["comparisons"]["p5_vs_rar"][
                "delta_loglike_per_point_left_minus_right"
            ]
        )
        tracked["p5_vs_newton_win_fraction"].append(
            summary["comparisons"]["p5_vs_newton"]["left_win_fraction"]
        )
        tracked["p5_vs_rar_win_fraction"].append(
            summary["comparisons"]["p5_vs_rar"]["left_win_fraction"]
        )
    intervals = {
        name: {
            "p2_5": float(np.quantile(values, 0.025, method="linear")),
            "p50": float(np.quantile(values, 0.5, method="linear")),
            "p97_5": float(np.quantile(values, 0.975, method="linear")),
        }
        for name, values in tracked.items()
    }
    return {
        "unit": "galaxy cluster bootstrap; each selected galaxy contributes all radial points",
        "seed": seed,
        "replicates": replicates,
        "interval": "deterministic percentile 95% interval",
        "intervals": intervals,
    }


def verify_current_forward_compatibility(
    galaxies: Sequence[Galaxy], artifact_path: Path
) -> dict[str, Any]:
    with artifact_path.open("r", encoding="utf-8") as handle:
        artifact = json.load(handle)
    params = P5Params.from_vector(
        [artifact["model"]["params"][name] for name in ("A", "n", "m", "gamma", "Sigma0")]
    )
    expected = {row["galaxy"]: row for row in artifact["results"]}
    if set(expected) != {galaxy.name for galaxy in galaxies}:
        raise ValueError("forward artefact and cross-validation dataset galaxy IDs differ")
    rank_differences: list[float] = []
    sigma_differences: list[float] = []
    newton_rank_differences: list[float] = []
    for galaxy in galaxies:
        row = expected[galaxy.name]
        p5_prediction = predict_p5(galaxy, params)
        p5_chi2, _ = chi2_and_loglike(galaxy, p5_prediction)
        rank_differences.append(
            abs(historical_rank_loss(galaxy, p5_prediction) - row["chi2_rank_ed"])
        )
        sigma_differences.append(abs(p5_chi2 - row["chi2_sigma_ed"]))
        newton_rank_differences.append(
            abs(
                historical_rank_loss(galaxy, predict_newton(galaxy))
                - row["chi2_rank_newton"]
            )
        )
    return {
        "target": "current manuscript trace-backed sparc_forward_eval artifact",
        "artifact_label": "HOLO_runner:A_single_Einstein_Dilaton geometry/artifacts/sparc_forward_eval.json",
        "artifact_sha256": file_sha256(artifact_path),
        "galaxies_checked": len(galaxies),
        "max_abs_rank_loss_difference_p5": max(rank_differences),
        "max_abs_diagonal_chi2_difference_p5": max(sigma_differences),
        "max_abs_rank_loss_difference_newton": max(newton_rank_differences),
        "exact_within_1e_8": max(rank_differences + sigma_differences + newton_rank_differences) < 1e-8,
        "legacy_divergence_warning": "The older ed_p5_industrial.py executable used an analytic smoothed delta profile and smoothed delta_missing. The current manuscript artifact instead uses the frozen trace.delta with linear interpolation and no smoothing; this cross-validation targets the current artifact.",
    }


def _group_id_sha256(names: Sequence[str]) -> str:
    return hashlib.sha256(canonical_json_bytes(sorted(names))).hexdigest()


def build_report(
    *,
    data_dir: Path,
    trace_path: Path,
    split_path: Path,
    forward_artifact_path: Path,
    maxiter: int = DEFAULT_MAXITER,
    bootstrap_replicates: int = DEFAULT_BOOTSTRAP_REPLICATES,
) -> dict[str, Any]:
    dataset_hash, file_count = aggregate_dataset_sha256(data_dir)
    if file_count != 175:
        raise ValueError(f"expected 175 SPARC files, found {file_count}")
    groups = load_split(split_path)
    trace_z, trace_delta = load_trace(trace_path)

    # Stage 1: only training outcomes enter either optimizer.
    train = load_galaxies(data_dir, groups["train"], trace_z, trace_delta)
    p5_params, p5_optimizer = fit_p5(train, maxiter=maxiter)
    g_dagger_si, rar_optimizer = fit_rar(train)
    train_rows = evaluate_galaxies(train, p5_params, g_dagger_si)

    # Stage 2: validation is opened once for reporting; no choice follows it.
    validation = load_galaxies(
        data_dir, groups["validation"], trace_z, trace_delta
    )
    validation_rows = evaluate_galaxies(validation, p5_params, g_dagger_si)

    # Stage 3: test is evaluated last with the same frozen parameters.
    test = load_galaxies(data_dir, groups["test"], trace_z, trace_delta)
    test_rows = evaluate_galaxies(test, p5_params, g_dagger_si)
    compatibility = verify_current_forward_compatibility(
        [*train, *validation, *test], forward_artifact_path
    )

    report = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "claim_boundary": "The split was frozen after the historical all-175 fit and all public outcomes existed. Test was excluded from this refit but was not historically blind; this is retrospective cross-validation, not independent confirmation.",
        "provenance": {
            "dataset_label": "HOLO_TRANSDUCTOR_V2:data/external/SPARC/sparc_175",
            "dataset_files": file_count,
            "dataset_aggregate_sha256": dataset_hash,
            "dataset_hash_algorithm": "SHA256 over sorted filename, NUL, per-file SHA256, newline",
            "trace_label": "HOLO_TRANSDUCTOR_V2:data/internal/holo_physics_trace_ed_industrial.json",
            "trace_sha256": file_sha256(trace_path),
            "split_label": "prediction_factory:sparc_split_v1.json",
            "split_sha256": file_sha256(split_path),
            "implementation_label": "prediction_factory:sparc_crossval.py",
            "implementation_sha256": file_sha256(Path(__file__).resolve()),
            "contains_absolute_paths": False,
            "raw_data_copied_into_report": False,
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "data_diagnostics": audit_dataset(data_dir),
        "implementation_compatibility": compatibility,
        "protocol": {
            "split_unit": "galaxy",
            "split_counts": {group: len(names) for group, names in groups.items()},
            "split_group_id_sha256": {
                group: _group_id_sha256(names) for group, names in groups.items()
            },
            "p5_formula": "v = Vbar*sqrt(1+clip((1-x^gamma)*delta_ED(z(x)) + x^gamma*A*(1/(1+Sigma_norm/Sigma0))^n*x^m, 0, 0.4))",
            "dictionary": "x=r/r_max; z=z_min+(z_max-z_min)*x; linear interpolation of frozen trace.delta",
            "p5_fitted_parameters": ["A", "n", "m", "gamma", "Sigma0"],
            "rar_formula": "g_obs=g_bar/(1-exp(-sqrt(g_bar/g_dagger))); v=sqrt(g_obs*r)",
            "rar_fitted_parameters": ["g_dagger_m_s2"],
            "fit_data": "train only",
            "validation_use": "opened once after fitting; reported only; no hyperparameter or model selection",
            "test_use": "evaluated last exactly once by the generation run; no refit",
            "per_galaxy_tuning": False,
            "uncertainty_model": "reported eVobs_kms as independent diagonal Gaussian sigma; no intrinsic-scatter or covariance fit",
            "primary_fit_score": "total train chi2 / train velocity-point count",
            "reported_scores": [
                "diagonal Gaussian log likelihood and chi2 per point",
                "median galaxy chi2 per point",
                "galaxy win fraction",
                "deterministic galaxy-cluster bootstrap intervals",
            ],
            "preregistered_model_list": ["P5 five-global-parameter readout", "Newton baryons-only", "one-global-parameter RAR"],
        },
        "frozen_fits": {
            "p5": {
                "parameters": p5_params.as_dict(),
                "optimizer": p5_optimizer,
                "parameters_at_preregistered_bounds": p5_bound_hits(p5_params),
                "optimizer_warning": "The differential-evolution budget ended before its convergence criterion and four parameters reached preregistered bounds; treat the returned fit as a bounded best-found estimate, not a certified optimum."
                if not p5_optimizer["success"] or p5_bound_hits(p5_params)
                else None,
            },
            "rar": {
                "g_dagger_m_s2": g_dagger_si,
                "optimizer": rar_optimizer,
            },
            "newton": {"fitted_parameters": 0},
        },
        "results": {
            "train": summarize_rows(train_rows),
            "validation": summarize_rows(validation_rows),
            "test": summarize_rows(test_rows),
            "test_bootstrap": bootstrap_test_rows(
                test_rows, replicates=bootstrap_replicates, seed=BOOTSTRAP_SEED
            ),
        },
        "interpretation_rules": [
            "Positive delta_loglike_per_point_left_minus_right favors the left model.",
            "Absolute chi2 may expose an inadequate diagonal error/model specification even when one model beats another.",
            "No result in this report is labelled blind, prospective, or confirmed.",
            "Four P5 boundary hits and optimizer non-convergence are model/fit diagnostics, not evidence for a physical parameter determination.",
            "All three models use the same historical Vbar column; the unsigned treatment of negative gas contributions and fixed stellar normalization limit the physical interpretation of absolute chi2.",
            "Changing formula, bounds, error model, split, optimizer objective, or baseline after reading validation/test requires a new version and cannot reuse this test as confirmation.",
        ],
    }
    return report


def _contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/") or value.startswith("file://")
    if isinstance(value, dict):
        return any(_contains_absolute_path(key) or _contains_absolute_path(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_absolute_path(item) for item in value)
    return False


def write_report(path: Path, report: dict[str, Any]) -> None:
    if _contains_absolute_path(report):
        raise ValueError("refusing to serialize an absolute path")
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=default_sparc_dir())
    parser.add_argument("--trace", type=Path, default=default_trace_path())
    parser.add_argument("--split", type=Path, default=factory_dir() / "sparc_split_v1.json")
    parser.add_argument("--forward-artifact", type=Path, default=default_forward_artifact_path())
    parser.add_argument("--output", type=Path, default=factory_dir() / "sparc_crossval_report.json")
    parser.add_argument("--maxiter", type=int, default=DEFAULT_MAXITER)
    parser.add_argument("--bootstrap", type=int, default=DEFAULT_BOOTSTRAP_REPLICATES)
    args = parser.parse_args()

    report = build_report(
        data_dir=args.data_dir.resolve(),
        trace_path=args.trace.resolve(),
        split_path=args.split.resolve(),
        forward_artifact_path=args.forward_artifact.resolve(),
        maxiter=args.maxiter,
        bootstrap_replicates=args.bootstrap,
    )
    write_report(args.output.resolve(), report)
    test = report["results"]["test"]
    print(f"wrote {args.output}")
    print(CLASSIFICATION)
    print(
        "test chi2/point: "
        f"P5={test['models']['p5']['chi2_per_point']:.6g}, "
        f"Newton={test['models']['newton']['chi2_per_point']:.6g}, "
        f"RAR={test['models']['rar']['chi2_per_point']:.6g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
