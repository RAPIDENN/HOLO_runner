#!/usr/bin/env python3
"""Clean-process reproduction and mutant adjudication for Route C.

This gate launches a detached worktree at the frozen v5.6.6.6 checkpoint.  In
that clean checkout it regenerates the independent Route-C Euler--Green
artifact, the additive and geometric mutation campaigns, and the independent
v5.5.4 eight-face Stokes red-team.  Every regenerated artifact must be byte
identical to its frozen counterpart.

The Route-C replica reads only the primitive bundle and literal v5.2 action
contract.  The mutation jobs deliberately exercise the already independent
Torch/NumPy targets and are reported as a separate dependency branch; they are
not represented as additional clean-room action implementations.  This file
does not import any scientific helper from those routes.

The result closes the finite clean-process/mutant obligation only.  The
continuous restricted-class bridge and C1/N1 promotion remain fail-closed.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_clean_process_mutant_redteam_v5_6_6_7.json"
)
TEST = HERE / (
    "test_one_omega_topological_so3_clean_process_mutant_redteam_v5_6_6_7.py"
)

SCHEMA = (
    "holo.one-omega-topological-so3-clean-process-mutant-redteam-"
    "v5-6-6-7.v1"
)
FROZEN_COMMIT = "8dc58ada87f82c6151052e1ce6d2fb02080f99e3"
LITERAL_V5_2_ACTION_SHA256 = (
    "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
)

ROUTE_C_MODULE = (
    "first_principles_audit.prediction_factory."
    "derive_one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3"
)
COMPONENT_MUTANT_MODULE = (
    "first_principles_audit.prediction_factory."
    "derive_one_omega_topological_so3_component_action_mutants_v5_6_5_3"
)
SPECIAL_MUTANT_MODULE = (
    "first_principles_audit.prediction_factory."
    "derive_one_omega_topological_so3_special_configuration_mutants_v5_6_5_4"
)
STOKES_REDTEAM_MODULE = (
    "first_principles_audit.prediction_factory."
    "derive_one_omega_topological_so3_interface_diffeomorphism_khronon_"
    "v5_5_4_redteam"
)

ROUTE_C_SOURCE = HERE / (
    "derive_one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3.py"
)
ROUTE_C_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_multin_independent_euler_green_"
    "route_c_v5_6_6_3.json"
)
COMPONENT_MUTANT_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_component_action_mutants_v5_6_5_3.json"
)
SPECIAL_MUTANT_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_special_configuration_mutants_v5_6_5_4.json"
)
STOKES_REDTEAM_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_interface_diffeomorphism_khronon_"
    "v5_5_4_redteam.json"
)
UNDERRESOLVED_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_multidirection_convergence_"
    "route_c_v5_6_6_4.json"
)
PRECISION_ARTIFACT = ARTIFACTS / (
    "one_omega_topological_so3_precision_stabilized_route_c_v5_6_6_5.json"
)

EXPECTED_SHA256 = {
    "route_C_source": "87cd1e05184a9fb2703faa08eecf5aa8544f4cf24ba8c12dd830828888821d0b",
    "route_C_artifact": "4e343402192d539d7b5b8bf3e70dbbac139a779fea15273ce223143b0452bfd7",
    "component_mutant_artifact": "3d4fbea7e2dde254b9b1cc6add1eb48ea1e126df840912a38c0d86253777fc1a",
    "special_mutant_artifact": "5dff6fbb70534185cd56da3442685fb002bd017eb6b50102cf43af613dd4ec1d",
    "Stokes_redteam_artifact": "e1e70a013513ec154f3458891b28bb77a47739bcc264b571935cac1f06d1ade7",
    "underresolved_artifact": "23579f90fc535a71d088e992a4f6f49aea515a8ab9c7b04bb6b7cc89bff9ddb8",
    "precision_artifact": "06ad302a03d17e4ea718c9ab801113807a7f66c71102e69486f7869130f77654",
}

JOBS = (
    {
        "name": "Route_C_independent_Euler_Green",
        "module": ROUTE_C_MODULE,
        "artifact": ROUTE_C_ARTIFACT.relative_to(REPO),
        "expected_sha256": EXPECTED_SHA256["route_C_artifact"],
    },
    {
        "name": "forty_additive_component_mutants",
        "module": COMPONENT_MUTANT_MODULE,
        "artifact": COMPONENT_MUTANT_ARTIFACT.relative_to(REPO),
        "expected_sha256": EXPECTED_SHA256["component_mutant_artifact"],
    },
    {
        "name": "seven_nonadditive_geometric_mutants",
        "module": SPECIAL_MUTANT_MODULE,
        "artifact": SPECIAL_MUTANT_ARTIFACT.relative_to(REPO),
        "expected_sha256": EXPECTED_SHA256["special_mutant_artifact"],
    },
    {
        "name": "independent_eight_face_Stokes_redteam",
        "module": STOKES_REDTEAM_MODULE,
        "artifact": STOKES_REDTEAM_ARTIFACT.relative_to(REPO),
        "expected_sha256": EXPECTED_SHA256["Stokes_redteam_artifact"],
    },
)

REQUIRED_SPECIAL_MUTANTS = {
    "freeze_relative_R",
    "rotate_phi_only",
    "break_induced_pullback",
    "break_gluing",
    "V4_anisotropic",
    "remove_coordinate_T0i_matter_contractions",
    "impose_reflected_Z2",
}
REQUIRED_COMPONENTS = {
    "EH_bulk_plus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "GHY_minus",
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
}


class CleanProcessRedteamError(RuntimeError):
    """A frozen input, clean execution, or mutation witness failed."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_json(path: Path, expected_sha256: str) -> Mapping[str, Any]:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise CleanProcessRedteamError(
            f"byte pin drift for {path.name}: {observed} != {expected_sha256}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _route_c_static_independence(path: Path) -> Mapping[str, Any]:
    if _sha256(path) != EXPECTED_SHA256["route_C_source"]:
        raise CleanProcessRedteamError("Route C source pin drift")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = (
        "torch_c2_multin",
        "literal_torch_action",
        "numpy_c2_multin_fd5",
        "numpy_fd5_action",
        "ad_fd5_route_c_three_way",
    )
    if any(any(token in imported for token in forbidden) for imported in imports):
        raise CleanProcessRedteamError("Route C imports a primary action/comparator helper")
    forbidden_text = (
        "AD_ARTIFACT",
        "FD5_ARTIFACT",
        "AD_JVP_by_component",
        "FD5_Richardson_JVP",
    )
    if any(token in source for token in forbidden_text):
        raise CleanProcessRedteamError("Route C source reads a primary receipt symbol")
    return {
        "imported_modules": imports,
        "primary_action_or_comparator_helpers_imported": False,
        "primary_AD_or_FD5_receipt_symbols_read": False,
        "primitive_bundle_only_scientific_input": True,
    }


def _walk_false_refinement_witnesses(value: Any, path: str = "") -> list[dict[str, Any]]:
    witnesses: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if value.get("pass") is False:
            ratios = [
                float(value[key])
                for key in (
                    "maximum_difference_over_tolerance",
                    "maximum_residual_over_tolerance",
                )
                if key in value
            ]
            witnesses.append({"path": path, "ratios": ratios})
        for key, item in value.items():
            witnesses.extend(
                _walk_false_refinement_witnesses(item, f"{path}.{key}" if path else key)
            )
    elif isinstance(value, list):
        for index, item in enumerate(value):
            witnesses.extend(_walk_false_refinement_witnesses(item, f"{path}[{index}]"))
    return witnesses


def _validate_route_c(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    members = payload["scientific"]["members"]
    if [(row["N"], row["K"]) for row in members] != [(1, 1), (2, 2), (3, 3)]:
        raise CleanProcessRedteamError("Route C clean campaign member drift")
    if payload["decision"]["route_C_multin_independent_Euler_Green_pass"] is not True:
        raise CleanProcessRedteamError("Route C clean campaign is red")
    if not all(row["selected_member_Euler_Green_pass"] is True for row in members):
        raise CleanProcessRedteamError("a clean Route C member is red")
    return {
        "members": [
            {
                "N": row["N"],
                "K": row["K"],
                "maximum_absolute_component_Stokes_residual": row[
                    "maximum_absolute_component_Stokes_residual"
                ],
                "total_absolute_Stokes_residual": row[
                    "total_absolute_Stokes_residual"
                ],
                "maximum_absolute_local_chain_residual": row[
                    "maximum_absolute_local_chain_residual"
                ],
            }
            for row in members
        ],
        "literal_action_sha256": payload["source_pins"][
            "literal_v5_2_action_sha256"
        ],
    }


def _validate_component_mutants(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    records = payload["scientific"]["records"]
    identifiers = {row["id"] for row in records}
    expected = {
        f"{operation}_{component}"
        for operation in ("omit", "invert_sign")
        for component in REQUIRED_COMPONENTS
    }
    if identifiers != expected or len(records) != 40:
        raise CleanProcessRedteamError("additive mutant coverage drift")
    if not all(row["killed"] is True for row in records):
        raise CleanProcessRedteamError("an additive component mutant survived")
    minimum = min(float(row["target_component_relative_residual"]) for row in records)
    return {
        "mutant_count": len(records),
        "minimum_target_component_relative_residual": minimum,
        "covered_components": sorted(REQUIRED_COMPONENTS),
        "covered_operations": ["omit", "invert_sign"],
        "orientation_sign_equivalents": [
            "invert_sign_BF_bulk_plus",
            "invert_sign_BF_bulk_minus",
            "invert_sign_GHY_plus",
            "invert_sign_GHY_minus",
        ],
    }


def _validate_special_mutants(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    records = payload["scientific"]["records"]
    if {row["id"] for row in records} != REQUIRED_SPECIAL_MUTANTS:
        raise CleanProcessRedteamError("special mutant coverage drift")
    survived: list[str] = []
    for row in records:
        killed = row.get("killed_by_action_or_gluing")
        if killed is None:
            killed = row.get("killed_by_derivative_comparator")
        if killed is not True:
            survived.append(str(row["id"]))
    if survived:
        raise CleanProcessRedteamError(f"special mutants survived: {survived}")
    decision = payload["decision"]
    if decision["special_geometric_action_mutants_pass"] is not True:
        raise CleanProcessRedteamError("special mutant campaign is red")
    return {
        "mutant_count": len(records),
        "killed_mutants": sorted(REQUIRED_SPECIAL_MUTANTS),
        "T_ui_matter_independent_action_shift_JVP_match_pass": decision[
            "T_ui_matter_independent_action_shift_JVP_match_pass"
        ],
        "T_ui_matter_nonzero_same_family_witness_pass": decision[
            "T_ui_matter_nonzero_same_family_witness_pass"
        ],
    }


def _validate_stokes_redteam(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    decision = payload["decision"]
    required = (
        "independent_redteam_checks_pass",
        "independent_action_JVP_Stokes_density_assemblies_pass",
        "executed_mutation_re_evaluation_pass",
        "independent_R_groupoid_pullback_T_ui_V4_controls_pass",
    )
    if not all(decision[key] is True for key in required):
        raise CleanProcessRedteamError("independent v5.5.4 red-team drift")
    faces = list(payload["runtime"]["compact_Stokes_boundary_flux"].values())
    if len(faces) != 2 or not all(
        row["face_count"] == 8
        and row["boundary_zero_obtained_from_runtime_fields"] is True
        and float(row["total_oriented_boundary_flux_absolute"]) < 2.0e-14
        for row in faces
    ):
        raise CleanProcessRedteamError("eight-face Stokes certificate drift")
    return {
        "probe_count": len(faces),
        "face_count_per_probe": [row["face_count"] for row in faces],
        "total_oriented_boundary_flux_absolute": [
            row["total_oriented_boundary_flux_absolute"] for row in faces
        ],
        "minimum_mutant_witness": payload["runtime"]["minimum_mutant_witness"],
        "maximum_nominal_closure_error": payload["runtime"][
            "maximum_nominal_closure_error"
        ],
    }


def _validate_resolution_pair(
    underresolved: Mapping[str, Any], precision: Mapping[str, Any]
) -> Mapping[str, Any]:
    under_decision = underresolved["decision"]
    precision_decision = precision["decision"]
    if under_decision["route_C_h_and_quadrature_convergence_pass"] is not False:
        raise CleanProcessRedteamError("archived underresolved receipt lost its red state")
    if under_decision["restricted_spectral_family_Euler_Green_certificate_pass"] is not False:
        raise CleanProcessRedteamError("underresolved receipt was retrospectively promoted")
    if precision_decision["restricted_spectral_family_precision_correction_pass"] is not True:
        raise CleanProcessRedteamError("precision correction is not green")
    if precision["source_pins"]["v5_6_6_4_red_artifact_sha256"] != EXPECTED_SHA256[
        "underresolved_artifact"
    ]:
        raise CleanProcessRedteamError("precision correction does not pin the red receipt")
    witnesses = _walk_false_refinement_witnesses(underresolved["scientific"])
    if not witnesses:
        raise CleanProcessRedteamError("no raw underresolution witness remains")
    ratios = [ratio for row in witnesses for ratio in row["ratios"]]
    return {
        "archived_red_receipt_sha256": EXPECTED_SHA256["underresolved_artifact"],
        "false_refinement_witness_count": len(witnesses),
        "maximum_recorded_failure_ratio": max(ratios) if ratios else None,
        "precision_correction_sha256": EXPECTED_SHA256["precision_artifact"],
        "precision_correction_pass": True,
    }


def _minimal_environment() -> dict[str, str]:
    return {
        "HOME": str(Path.home()),
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "LANG": "C.UTF-8",
        "PYTHONHASHSEED": "0",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }


def _run_checked(
    command: Sequence[str], *, cwd: Path, environment: Mapping[str, str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        env=dict(environment),
        check=True,
        capture_output=True,
        text=True,
    )


def run_clean_campaign(repository: Path = REPO) -> Mapping[str, Any]:
    """Regenerate all finite evidence from a detached, clean checkpoint."""

    git = shutil.which("git")
    python = shutil.which("python3")
    if git is None or python is None:
        raise CleanProcessRedteamError("git and python3 are required")
    environment = _minimal_environment()
    temporary = Path(tempfile.mkdtemp(prefix="holo-v5667-clean-", dir="/tmp"))
    worktree_added = False
    try:
        _run_checked(
            (git, "worktree", "add", "--detach", str(temporary), FROZEN_COMMIT),
            cwd=repository,
            environment=environment,
        )
        worktree_added = True
        head = _run_checked(
            (git, "rev-parse", "HEAD"), cwd=temporary, environment=environment
        ).stdout.strip()
        if head != FROZEN_COMMIT:
            raise CleanProcessRedteamError(f"clean worktree HEAD drift: {head}")
        status_before = _run_checked(
            (git, "status", "--porcelain"), cwd=temporary, environment=environment
        ).stdout
        if status_before:
            raise CleanProcessRedteamError("detached worktree is dirty before execution")

        probe = _run_checked(
            (
                python,
                "-c",
                f"import {ROUTE_C_MODULE} as m; print(m.__file__)",
            ),
            cwd=temporary,
            environment=environment,
        ).stdout.strip()
        try:
            Path(probe).resolve().relative_to(temporary.resolve())
        except ValueError as exc:
            raise CleanProcessRedteamError(
                f"Route C loaded outside clean worktree: {probe}"
            ) from exc

        payloads: dict[str, Mapping[str, Any]] = {}
        job_records: list[dict[str, Any]] = []
        for job in JOBS:
            completed = _run_checked(
                (python, "-u", "-m", str(job["module"])),
                cwd=temporary,
                environment=environment,
            )
            artifact = temporary / Path(job["artifact"])
            observed = _sha256(artifact)
            if observed != job["expected_sha256"]:
                raise CleanProcessRedteamError(
                    f"clean {job['name']} artifact drift: {observed}"
                )
            payloads[str(job["name"])] = json.loads(
                artifact.read_text(encoding="utf-8")
            )
            job_records.append(
                {
                    "name": job["name"],
                    "module": job["module"],
                    "exit_code": completed.returncode,
                    "artifact": str(job["artifact"]),
                    "artifact_sha256": observed,
                    "byte_identical_to_frozen_checkpoint": True,
                }
            )

        underresolved = _load_json(
            temporary / UNDERRESOLVED_ARTIFACT.relative_to(REPO),
            EXPECTED_SHA256["underresolved_artifact"],
        )
        precision = _load_json(
            temporary / PRECISION_ARTIFACT.relative_to(REPO),
            EXPECTED_SHA256["precision_artifact"],
        )
        status_after = _run_checked(
            (git, "status", "--porcelain"), cwd=temporary, environment=environment
        ).stdout
        if status_after:
            raise CleanProcessRedteamError(
                "regenerated artifacts are not byte identical in git status"
            )

        route = _validate_route_c(payloads["Route_C_independent_Euler_Green"])
        components = _validate_component_mutants(
            payloads["forty_additive_component_mutants"]
        )
        special = _validate_special_mutants(
            payloads["seven_nonadditive_geometric_mutants"]
        )
        stokes = _validate_stokes_redteam(
            payloads["independent_eight_face_Stokes_redteam"]
        )
        resolution = _validate_resolution_pair(underresolved, precision)
        return {
            "target_commit": head,
            "module_loaded_under_clean_worktree": True,
            "clean_status_before": status_before,
            "clean_status_after": status_after,
            "minimal_environment_keys": sorted(environment),
            "jobs": job_records,
            "route_C": route,
            "additive_component_mutants": components,
            "special_geometric_mutants": special,
            "eight_face_Stokes": stokes,
            "resolution_adjudication": resolution,
        }
    finally:
        if worktree_added:
            subprocess.run(
                (git, "worktree", "remove", "--force", str(temporary)),
                cwd=repository,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
        if temporary.exists():
            temporary.rmdir()


def build_payload(execution: Mapping[str, Any]) -> Mapping[str, Any]:
    independence = _route_c_static_independence(ROUTE_C_SOURCE)
    jobs = execution["jobs"]
    clean_reproduction = bool(
        execution["target_commit"] == FROZEN_COMMIT
        and execution["module_loaded_under_clean_worktree"] is True
        and execution["clean_status_before"] == ""
        and execution["clean_status_after"] == ""
        and len(jobs) == len(JOBS)
        and all(
            row["exit_code"] == 0
            and row["byte_identical_to_frozen_checkpoint"] is True
            for row in jobs
        )
    )
    full_mutants = bool(
        execution["additive_component_mutants"]["mutant_count"] == 40
        and execution["special_geometric_mutants"]["mutant_count"] == 7
        and execution["special_geometric_mutants"][
            "T_ui_matter_independent_action_shift_JVP_match_pass"
        ]
        is True
        and execution["eight_face_Stokes"]["probe_count"] == 2
        and execution["resolution_adjudication"]["false_refinement_witness_count"]
        > 0
    )
    clean_redteam = bool(clean_reproduction and full_mutants)
    scientific = {
        "clean_execution": execution,
        "Route_C_static_independence": independence,
        "mutant_coverage": {
            "additive_omit_or_sign": 40,
            "nonadditive_geometric": 7,
            "underresolved_radial_receipt_preserved_red": True,
            "eight_oriented_faces_recomputed_per_probe": 8,
            "circular_expected_Euler_substitution_rejected_by_contract": True,
        },
    }
    return {
        "schema": SCHEMA,
        "classification": (
            "theory_only;clean_process;Route_C;full_finite_mutants;"
            "restricted_spectral_family;fail_closed_continuum"
        ),
        "decision": {
            "Route_C_clean_process_byte_reproduction_pass": clean_reproduction,
            "all_forty_additive_mutants_clean_regeneration_pass": full_mutants,
            "all_seven_special_mutants_clean_regeneration_pass": full_mutants,
            "eight_face_Stokes_clean_regeneration_pass": clean_redteam,
            "underresolved_radial_red_receipt_preserved_pass": clean_redteam,
            "full_mutant_campaign_pass": full_mutants,
            "independent_clean_process_redteam_pass": clean_redteam,
            "clean_room_and_mutants_pass": clean_redteam,
            "uniform_N_to_infinity_bridge_pass": False,
            "C1_ACTION_pass": False,
            "N1_ACTION_pass": False,
            "C1_N1_promotion_authorized": False,
            "B4_pass": False,
            "B5_pass": False,
        },
        "scientific": scientific,
        "source_pins": {
            "frozen_checkpoint_commit": FROZEN_COMMIT,
            "literal_v5_2_action_sha256": LITERAL_V5_2_ACTION_SHA256,
            **EXPECTED_SHA256,
        },
        "independence_boundary": {
            "Route_C_primary_action_helpers_imported": False,
            "Route_C_primary_AD_or_FD5_receipts_read": False,
            "Route_C_clean_replica_scientific_input": "primitive bundle only",
            "mutation_branch": (
                "the clean-regenerated mutant harnesses intentionally attack the "
                "frozen Torch/NumPy implementations; they are not counted as a "
                "fourth independent action route"
            ),
            "v5_5_4_redteam_lineage_reads": (
                "byte-pinned upstream artifacts for lineage only; no primary Python "
                "helper or runtime object is imported"
            ),
        },
        "open_obligation": {
            "uniform_continuous_bridge": (
                "prove the exact second-order Euler--Green identity and continuity "
                "bounds on the declared restricted C2 spectral class"
            ),
        },
        "evidence_boundary": (
            "The finite N=1,2,3 Route-C artifact and all required finite mutant "
            "campaigns reproduce byte-for-byte from a detached clean checkpoint. "
            "This does not prove the continuous restricted-class bridge and does "
            "not authorize C1/N1 or B4/B5."
        ),
        "provenance": {
            "generator": {
                "path": str(Path(__file__).resolve().relative_to(REPO)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "test": {
                "path": str(TEST.relative_to(REPO)),
                "sha256": _sha256(TEST) if TEST.exists() else None,
            },
        },
        "scientific_payload_sha256": _canonical_sha256(scientific),
    }


def write_payload(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args(argv)
    execution = run_clean_campaign()
    payload = build_payload(execution)
    if payload["decision"]["clean_room_and_mutants_pass"] is not True:
        raise CleanProcessRedteamError("clean-process mutant campaign failed")
    write_payload(arguments.output, payload)
    print(arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
