#!/usr/bin/env python3
"""Rebuild all derived certificates, figures, paper, and validation bundle."""

from __future__ import annotations

import subprocess
import shutil
from pathlib import Path


SOURCE = Path(__file__).resolve().parent
PAPER_ROOT = SOURCE.parent
REPO_ROOT = PAPER_ROOT.parent
TECTONIC = Path("/home/debian/.local/bin/tectonic")


def run(*command: str, cwd: Path = SOURCE) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    (PAPER_ROOT / "build").mkdir(parents=True, exist_ok=True)
    run("python3", "first_principles_audit/derive_and_audit.py", cwd=REPO_ROOT)
    run(
        "python3",
        "first_principles_audit/reconstruct_holo_effective_action.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/derive_interface_action.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/derive_minimal_probe_completion.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/verify_minimal_probe_completion_shooting.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/audit_ricci_wilson_interface.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/derive_material_transducer.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/prediction_factory.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_boundary_branches.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/verify_nd_ultralight_shooting.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/material_prediction_factory.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_em_kernel_completion.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_robin_boundary_family.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_em_spectral_fingerprint.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/evaluate_desi_dr1_growth.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/build_master_prediction_registry.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "unittest",
        "first_principles_audit.test_derive_and_audit",
        "first_principles_audit.test_effective_reconstruction",
        "first_principles_audit.test_interface_action",
        "first_principles_audit.test_minimal_probe_completion",
        "first_principles_audit.test_minimal_probe_completion_shooting",
        "first_principles_audit.test_ricci_wilson_interface",
        "first_principles_audit.test_material_transducer",
        "first_principles_audit.prediction_factory.test_prediction_factory",
        "first_principles_audit.prediction_factory.test_boundary_branches",
        "first_principles_audit.prediction_factory.test_nd_ultralight_shooting",
        "first_principles_audit.prediction_factory.material_prediction_factory_test",
        "first_principles_audit.prediction_factory.test_em_kernel_completion",
        "first_principles_audit.prediction_factory.test_robin_boundary_family",
        "first_principles_audit.prediction_factory.test_em_spectral_fingerprint",
        "first_principles_audit.prediction_factory.test_desi_dr1_growth",
        "first_principles_audit.prediction_factory.test_master_prediction_registry",
        "first_principles_audit.prediction_factory.tests.test_wilson_loop_analyzer",
        "-v",
        cwd=REPO_ROOT,
    )
    run("python3", "make_effective_figure.py")
    run("python3", "make_probe_completion_figure.py")
    run("python3", "make_ricci_material_figure.py")
    run("python3", "make_prediction_factory_figure.py")
    run("python3", "make_em_double_comb_figure.py")
    run(
        str(TECTONIC),
        "main.tex",
        "--outdir",
        "../build",
        "--keep-logs",
        "--keep-intermediates",
    )
    shutil.copy2(
        PAPER_ROOT / "build" / "main.pdf",
        PAPER_ROOT / "build" / "A_single_Einstein-Dilaton_geometry.pdf",
    )
    run("python3", "compare_original_revision.py")
    run("python3", "validate_revision.py")
    shutil.copy2(
        PAPER_ROOT / "build" / "A_single_Einstein-Dilaton_geometry.pdf",
        PAPER_ROOT / "A_single_Einstein-Dilaton_geometry.pdf",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
