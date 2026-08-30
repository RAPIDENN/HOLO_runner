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
        "first_principles_audit/prediction_factory/derive_superpotential_boundary_completion.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/verify_superpotential_boundary_shooting.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_stiff_boundary_force.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_breathing_response.py",
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
        "first_principles_audit/prediction_factory/derive_sparc_finite_disk_yukawa.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/sparc_physical_audit.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_force_residual_bridge.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_universal_residual_collector.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_nonlinear_collector_action.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_collector_legendre_envelope.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_phase_space_collector_bridge.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_collector_shell_residual.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_holo_collector_embedding_gate.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_axisymmetric_collector_prototype.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_axisymmetric_collector_solver.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_soft_mode_cubic_bridge.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_soft_mode_cubic_scaling.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_jordan_selector_embedding.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_jordan_deep_limit_gate.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_scale_consistency.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_bulk_cubic_vertex_inventory.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_gauge_invariant_cubic_route",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_cubic_boundary_identifiability",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_radial_adm_quartic_seed",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_adm_quadratic_recovery",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_adm_bmp_tricritical_necessity",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_bps_radion_matter_coupling",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_bps_biscalar_matter_geometry",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_bps_volume_constraint_selector",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_compact_brane_S2_backward",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_bent_brane_geometry_S2",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_finite_gamma_brane_S2",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "-m",
        "first_principles_audit.prediction_factory.derive_nonlinear_swarm_adjudication",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_tricritical_constitutive_bridge.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_collective_spectral_bridge.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_bulk_constitutive_decision_gate.py",
        cwd=REPO_ROOT,
    )
    run(
        "python3",
        "first_principles_audit/prediction_factory/derive_holo_nonlinear_route_matrix.py",
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
        "first_principles_audit.prediction_factory.test_superpotential_boundary_completion",
        "first_principles_audit.prediction_factory.test_superpotential_boundary_shooting",
        "first_principles_audit.prediction_factory.test_stiff_boundary_force",
        "first_principles_audit.prediction_factory.test_breathing_response",
        "first_principles_audit.prediction_factory.test_em_spectral_fingerprint",
        "first_principles_audit.prediction_factory.test_desi_dr1_growth",
        "first_principles_audit.prediction_factory.test_sparc_physical_audit",
        "first_principles_audit.prediction_factory.test_sparc_finite_disk_yukawa",
        "first_principles_audit.prediction_factory.test_force_residual_bridge",
        "first_principles_audit.prediction_factory.test_universal_residual_collector",
        "first_principles_audit.prediction_factory.test_nonlinear_collector_action",
        "first_principles_audit.prediction_factory.test_collector_legendre_envelope",
        "first_principles_audit.prediction_factory.test_phase_space_collector_bridge",
        "first_principles_audit.prediction_factory.test_collector_shell_residual",
        "first_principles_audit.prediction_factory.test_holo_collector_embedding_gate",
        "first_principles_audit.prediction_factory.test_axisymmetric_collector_prototype",
        "first_principles_audit.prediction_factory.test_axisymmetric_collector_solver",
        "first_principles_audit.prediction_factory.test_soft_mode_cubic_bridge",
        "first_principles_audit.prediction_factory.test_soft_mode_cubic_scaling",
        "first_principles_audit.prediction_factory.test_jordan_selector_embedding",
        "first_principles_audit.prediction_factory.test_jordan_deep_limit_gate",
        "first_principles_audit.prediction_factory.test_scale_consistency",
        "first_principles_audit.prediction_factory.test_bulk_cubic_vertex_inventory",
        "first_principles_audit.prediction_factory.test_gauge_invariant_cubic_route",
        "first_principles_audit.prediction_factory.test_cubic_boundary_identifiability",
        "first_principles_audit.prediction_factory.test_radial_adm_quartic_seed",
        "first_principles_audit.prediction_factory.test_adm_quadratic_recovery",
        "first_principles_audit.prediction_factory.test_adm_bmp_tricritical_necessity",
        "first_principles_audit.prediction_factory.test_bps_radion_matter_coupling",
        "first_principles_audit.prediction_factory.test_bps_biscalar_matter_geometry",
        "first_principles_audit.prediction_factory.test_bps_volume_constraint_selector",
        "first_principles_audit.prediction_factory.test_compact_brane_S2_backward",
        "first_principles_audit.prediction_factory.test_bent_brane_geometry_S2",
        "first_principles_audit.prediction_factory.test_finite_gamma_brane_S2",
        "first_principles_audit.prediction_factory.test_nonlinear_swarm_adjudication",
        "first_principles_audit.prediction_factory.test_tricritical_constitutive_bridge",
        "first_principles_audit.prediction_factory.test_collective_spectral_bridge",
        "first_principles_audit.prediction_factory.test_bulk_constitutive_decision_gate",
        "first_principles_audit.prediction_factory.test_holo_nonlinear_route_matrix",
        "first_principles_audit.prediction_factory.test_master_prediction_registry",
        "first_principles_audit.prediction_factory.tests.test_wilson_loop_analyzer",
        "-v",
        cwd=REPO_ROOT,
    )
    run("python3", "make_effective_figure.py")
    run("python3", "make_probe_completion_figure.py")
    run("python3", "make_ricci_material_figure.py")
    run("python3", "make_breathing_response_figure.py")
    run("python3", "make_prediction_factory_figure.py")
    run("python3", "make_sparc_physical_figure.py")
    run("python3", "make_nonlinear_collector_action_figure.py")
    run("python3", "make_nonlinear_route_map_figure.py")
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
