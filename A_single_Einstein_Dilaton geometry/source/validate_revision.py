#!/usr/bin/env python3
"""Fail-closed validation for the rebuilt Einstein--dilaton paper."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


SOURCE = Path(__file__).resolve().parent
PAPER_ROOT = SOURCE.parent
REPO_ROOT = PAPER_ROOT.parent
PDF = PAPER_ROOT / "build" / "A_single_Einstein-Dilaton_geometry.pdf"
LOG = PAPER_ROOT / "build" / "main.log"
TEXT = PAPER_ROOT / "build" / "main.txt"
PRIMARY = PAPER_ROOT / "A_single_Einstein-Dilaton_geometry.pdf"
FROZEN_V1 = PAPER_ROOT / "A_single_Einstein-Dilaton_geometry_v1_frozen.pdf"
ORIGINAL = FROZEN_V1 if FROZEN_V1.is_file() else PRIMARY
SUMMARY = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "holo_effective_action_summary.json"
)
MINIMAL = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "minimal_probe_completion.json"
)
SHOOTING = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "minimal_probe_completion_shooting_verification.json"
)
RICCI_WILSON = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "ricci_wilson_interface_audit.json"
)
MATERIAL = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "material_transducer.json"
)
FACTORY_ROOT = REPO_ROOT / "first_principles_audit" / "prediction_factory"
BOUNDARY_BRANCHES = FACTORY_ROOT / "artifacts" / "boundary_branch_catalogue.json"
ND_SHOOTING = FACTORY_ROOT / "artifacts" / "nd_ultralight_shooting.json"
EM_KERNEL = FACTORY_ROOT / "em_kernel_completion.json"
EM_FINGERPRINT = FACTORY_ROOT / "em_spectral_fingerprint.json"
ROBIN_FAMILY = FACTORY_ROOT / "artifacts" / "robin_boundary_family.json"
DESI_DIAGNOSTIC = FACTORY_ROOT / "desi_dr1_growth_diagnostic.json"
SPARC_CROSSVAL = FACTORY_ROOT / "sparc_crossval_report.json"
MASTER_REGISTRY = FACTORY_ROOT / "MASTER_PREDICTION_REGISTRY.json"
COMPARISON = PAPER_ROOT / "build" / "original_revision_comparison.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(checks: list[dict[str, Any]], name: str, passed: bool, detail: Any) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def main() -> int:
    checks: list[dict[str, Any]] = []
    for path in (
        PDF,
        LOG,
        ORIGINAL,
        SUMMARY,
        MINIMAL,
        SHOOTING,
        RICCI_WILSON,
        MATERIAL,
        BOUNDARY_BRANCHES,
        ND_SHOOTING,
        EM_KERNEL,
        EM_FINGERPRINT,
        ROBIN_FAMILY,
        DESI_DIAGNOSTIC,
        SPARC_CROSSVAL,
        MASTER_REGISTRY,
        COMPARISON,
        SOURCE / "main.tex",
    ):
        record(checks, f"exists:{path.name}", path.is_file(), str(path))
    if not all(item["passed"] for item in checks):
        raise SystemExit("Required revision input is missing")

    subprocess.run(
        ["pdftotext", "-layout", str(PDF), str(TEXT)], check=True
    )
    info = subprocess.run(
        ["pdfinfo", str(PDF)], check=True, capture_output=True, text=True
    ).stdout
    text = TEXT.read_text(encoding="utf-8")
    text_lower = text.lower()
    log = LOG.read_text(encoding="utf-8", errors="replace")
    tex = (SOURCE / "main.tex").read_text(encoding="utf-8")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    minimal = json.loads(MINIMAL.read_text(encoding="utf-8"))
    shooting = json.loads(SHOOTING.read_text(encoding="utf-8"))
    ricci_wilson = json.loads(RICCI_WILSON.read_text(encoding="utf-8"))
    material = json.loads(MATERIAL.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY_BRANCHES.read_text(encoding="utf-8"))
    nd_shooting = json.loads(ND_SHOOTING.read_text(encoding="utf-8"))
    em_kernel = json.loads(EM_KERNEL.read_text(encoding="utf-8"))
    em_fingerprint = json.loads(EM_FINGERPRINT.read_text(encoding="utf-8"))
    robin_family = json.loads(ROBIN_FAMILY.read_text(encoding="utf-8"))
    desi = json.loads(DESI_DIAGNOSTIC.read_text(encoding="utf-8"))
    sparc_crossval = json.loads(SPARC_CROSSVAL.read_text(encoding="utf-8"))
    master_registry = json.loads(MASTER_REGISTRY.read_text(encoding="utf-8"))
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))

    pages_match = re.search(r"^Pages:\s+(\d+)$", info, flags=re.MULTILINE)
    pages = int(pages_match.group(1)) if pages_match else 0
    record(checks, "page_count", 6 <= pages <= 20, pages)
    record(checks, "metadata_title", "A single Einstein" in info, info.splitlines()[0])
    record(checks, "metadata_author", "Author:          Adrian Bohoyo" in info, "Adrian Bohoyo")

    required_text = {
        "effective_action": "geometry-preserving effective completion",
        "positive_kinetic": "strictly positive",
        "delta_correlation": "0.999999905",
        "spectrum_value": "1.5455",
        "ir_proxy": "0.203",
        "sparc_parameter_a": "0.13983",
        "sparc_parameter_n": "2.21605",
        "sparc_parameter_m": "1.20433",
        "sparc_parameter_gamma": "0.23356",
        "sparc_parameter_sigma": "0.60488",
        "planck_omega": "0.315",
        "planck_hubble": "67.4",
        "planck_sigma8": "0.811",
        "sparc_wins": "150/175",
        "sparc_sigma_wins": "149/175",
        "boss_ed": "2.266",
        "boss_lcdm": "2.443",
        "boss_delta": "0.177",
        "nist_null": "22.59",
        "doi": "10.5281/zenodo.18224589",
        "evidence_label": "global in-sample calibration",
        "forward_boundary": "forward predictive model",
        "comparison_scope": "not benchmarked",
        "conditional_interface": "compact-interval matter",
        "derived_beta_zero": "0.0542901",
        "derived_force_fraction": "5.89483",
        "first_positive_trace_mass": "0.913899",
        "blind_derivation": "No observational input enters",
        "independent_shooting": "separate shooting solve",
        "legacy_clock_boundary": "does not constitute a clock detection",
        "same_scalar_dof": "not an additional scalar tower",
        "cassini_exclusion": "massless unscreened Neumann branch is therefore",
        "positive_tower_strength": "7.20230",
        "corrected_ricci": "corrected value spans",
        "ricci_rms": "26.91",
        "wilson_boundary": "loop feeds the geometry",
        "material_transfer": "transfer law, not a predicted signal",
        "modern_lattice_ratio": "1.7195",
        "nd_ultralight_mass": "0.00274476",
        "nd_ultralight_beta": "0.0542910",
        "em_coordinate_span": "4.90458",
        "em_coordinate_error": "0.395739",
        "em_measure_invariance": "6.27",
        "photon_first_mass": "0.652597",
        "photon_second_mass": "1.301427",
        "scalar_photon_vertex": "3.94563",
        "double_comb": "double-comb",
        "robin_ir_no_go": "0.002744976",
        "robin_avoided_gap": "0.0119229",
        "robin_identity": "Hellmann",
        "sparc_crossval_split": "122 galaxies",
        "sparc_rar_score": "60.99",
        "sparc_rar_wins": "8/27",
        "desi_holo_diagonal": "2.6917",
        "desi_lcdm_diagonal": "2.4189",
        "wilson_fail_closed": "fails closed",
    }
    for name, needle in required_text.items():
        record(checks, f"text:{name}", needle.lower() in text_lower, needle)

    for number in range(1, 13):
        marker = f"Figure {number}:"
        record(checks, f"figure_caption:{number}", marker in text, marker)

    original_assets = [
        "glueball_ratio.png",
        "sparc_rotation_curves_forward.png",
        "fig_spectroscopy.pdf",
        "multiarm_svd_diagnostic.png",
        "fig_single_arm_modal_responses.pdf",
        "bulk_clock_5d.png",
        "nist_baseline_vs_uv.png",
    ]
    for asset in original_assets:
        record(checks, f"original_figure:{asset}", asset in tex, asset)
    record(
        checks,
        "new_effective_figure",
        "fig_effective_reconstruction.png" in tex,
        "fig_effective_reconstruction.png",
    )
    record(
        checks,
        "new_probe_figure",
        "fig_minimal_probe_completion.png" in tex,
        "fig_minimal_probe_completion.png",
    )
    record(
        checks,
        "new_ricci_material_figure",
        "fig_ricci_material_audit.png" in tex,
        "fig_ricci_material_audit.png",
    )
    record(
        checks,
        "new_prediction_factory_figure",
        "fig_prediction_factory.png" in tex,
        "fig_prediction_factory.png",
    )
    record(
        checks,
        "new_em_double_comb_figure",
        "fig_em_double_comb.png" in tex,
        "fig_em_double_comb.png",
    )

    forbidden_text = [
        "??",
        "qquad",
        "We present",
        "MNRAS 000",
        "Preprint 29 August",
        "Compiled using MNRAS",
        "sub-percent accuracy",
        "closes the X = 1 gap",
        "why NIST clocks see no signal",
        "nine global parameters",
    ]
    for needle in forbidden_text:
        record(checks, f"forbidden:{needle}", needle not in text, needle)

    fatal_log_patterns = [
        "Undefined control sequence",
        "Reference `",
        "Citation `",
        "Overfull \\hbox",
        "Fatal error",
        "Emergency stop",
    ]
    for pattern in fatal_log_patterns:
        record(checks, f"log_clean:{pattern}", pattern not in log, pattern)

    record(checks, "effective_certificate", summary["passes"]["all"], summary["passes"])
    record(checks, "minimal_probe_certificate", minimal["passes"]["all"], minimal["passes"])
    record(checks, "shooting_certificate", shooting["passes"]["all"], shooting["passes"])
    record(
        checks,
        "ricci_wilson_certificate",
        ricci_wilson["passes"]["all"],
        ricci_wilson["passes"],
    )
    record(
        checks,
        "material_transducer_certificate",
        material["passes"]["all"],
        material["passes"],
    )
    record(
        checks,
        "boundary_branch_certificate",
        boundary["passes"]["all"],
        boundary["passes"],
    )
    record(
        checks,
        "nd_ultralight_certificate",
        nd_shooting["passes"]["all"],
        nd_shooting["passes"],
    )
    record(
        checks,
        "em_kernel_certificate",
        all(em_kernel["passes"].values()),
        em_kernel["passes"],
    )
    record(
        checks,
        "em_fingerprint_certificate",
        em_fingerprint["passes"]["all"],
        em_fingerprint["passes"],
    )
    record(
        checks,
        "robin_family_certificate",
        robin_family["passes"]["all"],
        robin_family["passes"],
    )
    record(
        checks,
        "desi_diagnostic_certificate",
        desi["passes"]["all"],
        desi["passes"],
    )
    record(
        checks,
        "sparc_crossval_evidence_label",
        sparc_crossval["classification"]
        == "retrospective_cross_validation_not_blind_confirmation",
        sparc_crossval["classification"],
    )
    record(
        checks,
        "master_registry_evidence_label",
        "no new physical detection" in master_registry["global_classification"],
        master_registry["global_classification"],
    )
    record(
        checks,
        "minimal_probe_observational_blinding",
        minimal["observational_inputs_read"] == [],
        minimal["observational_inputs_read"],
    )
    record(
        checks,
        "shooting_observational_blinding",
        shooting["observational_inputs_read"] == [],
        shooting["observational_inputs_read"],
    )
    beta_zero = minimal["zero_mode_prediction"]["beta_0"]
    force_fraction = minimal["zero_mode_prediction"][
        "relative_force_strength_2_beta_squared"
    ]
    record(
        checks,
        "minimal_probe_beta_zero",
        abs(beta_zero - 0.05429009535288237) < 1e-14,
        beta_zero,
    )
    record(
        checks,
        "minimal_probe_force_fraction",
        abs(force_fraction - 0.0058948289068501206) < 1e-14,
        force_fraction,
    )
    record(
        checks,
        "shooting_independent_method",
        not shooting["method"]["primary_solver_reused"]
        and not shooting["method"]["fem_matrix_reused"],
        shooting["method"],
    )
    record(
        checks,
        "original_revision_comparison",
        comparison["passed"],
        comparison["interpretation_checks"],
    )
    metrics = summary["preservation_metrics"]
    record(
        checks,
        "delta_metric_consistent",
        abs(metrics["delta_correlation"] - 0.9999999047611539) < 1e-12,
        metrics["delta_correlation"],
    )
    record(
        checks,
        "source_has_no_placeholders",
        not re.search(r"\(\?\?\)|\(\?\)|TODO|FIXME|TBD", tex),
        "no unresolved citation placeholders",
    )

    passed = all(item["passed"] for item in checks)
    manifest = {
        "schema": "holo-paper-revision-validation.v1",
        "passed": passed,
        "paper": {
            "source": str(SOURCE / "main.tex"),
            "pdf": str(PDF),
            "pdf_sha256": sha256(PDF),
            "pages": pages,
        },
        "original": {
            "path": str(ORIGINAL),
            "sha256": sha256(ORIGINAL),
        },
        "effective_action_summary_sha256": sha256(SUMMARY),
        "minimal_probe_completion_sha256": sha256(MINIMAL),
        "shooting_verification_sha256": sha256(SHOOTING),
        "ricci_wilson_interface_sha256": sha256(RICCI_WILSON),
        "material_transducer_sha256": sha256(MATERIAL),
        "boundary_branch_catalogue_sha256": sha256(BOUNDARY_BRANCHES),
        "nd_ultralight_shooting_sha256": sha256(ND_SHOOTING),
        "em_kernel_completion_sha256": sha256(EM_KERNEL),
        "em_spectral_fingerprint_sha256": sha256(EM_FINGERPRINT),
        "robin_boundary_family_sha256": sha256(ROBIN_FAMILY),
        "desi_diagnostic_sha256": sha256(DESI_DIAGNOSTIC),
        "sparc_crossval_sha256": sha256(SPARC_CROSSVAL),
        "master_prediction_registry_sha256": sha256(MASTER_REGISTRY),
        "original_revision_comparison_sha256": sha256(COMPARISON),
        "checks": checks,
    }
    manifest_path = PAPER_ROOT / "build" / "revision_validation.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    failed = [item["name"] for item in checks if not item["passed"]]
    print(f"validation_passed={passed}")
    print(f"checks={len(checks)} failed={len(failed)}")
    if failed:
        print("failed_checks=" + ",".join(failed))
    print(manifest_path)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
