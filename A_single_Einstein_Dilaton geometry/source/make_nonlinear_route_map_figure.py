#!/usr/bin/env python3
"""Render the nonlinear route graph, route matrix and current physical gates."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


SOURCE = Path(__file__).resolve().parent
REPO = SOURCE.parents[1]
FACTORY = REPO / "first_principles_audit" / "prediction_factory"
MATRIX = FACTORY / "artifacts" / "holo_nonlinear_route_matrix.json"
SHELL = FACTORY / "artifacts" / "collector_shell_residual.json"
AXISYMMETRIC = FACTORY / "artifacts" / "derive_axisymmetric_collector_solver.json"
OUTPUT = SOURCE.parent / "figures" / "fig_nonlinear_route_map.png"

NAVY = "#17324D"
BLUE = "#2F6B9A"
TEAL = "#1B887A"
AMBER = "#D99032"
RED = "#B64A4A"
GREY = "#6D7782"
PURPLE = "#76528B"
PALE = "#F5F7F9"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _node(ax, xy, width, height, text, color, *, text_color="white"):
    x, y = xy
    box = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.025",
        facecolor=color,
        edgecolor="white",
        linewidth=1.3,
        zorder=3,
    )
    ax.add_patch(box)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=7.2,
        color=text_color,
        weight="semibold",
        zorder=4,
    )


def _arrow(ax, start, end, label, color, rad=0.0, label_dy=0.025):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=9,
        linewidth=1.2,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=4,
        shrinkB=4,
        zorder=2,
    )
    ax.add_patch(arrow)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ax.text(
        midpoint[0],
        midpoint[1] + label_dy,
        label,
        fontsize=6.2,
        color=color,
        ha="center",
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.7, "alpha": 0.9},
        zorder=5,
    )


def route_graph(ax):
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")
    _node(ax, (0.11, 0.83), 0.20, 0.13, "Old: 7 fixed poles\n$g\\propto M$", RED)
    _node(ax, (0.36, 0.83), 0.21, 0.13, "Narrow crossover\n$0.210$ dex", AMBER)
    _node(ax, (0.11, 0.53), 0.20, 0.13, "Required target\n$P\\propto Y^{3/2}$", NAVY)
    _node(ax, (0.36, 0.53), 0.21, 0.13, "Exact envelope\n$s=\\sqrt{Y}$", BLUE)
    _node(ax, (0.61, 0.68), 0.24, 0.14, "Tricritical amplitude\n$q^2Y+q^6/3$", TEAL)
    _node(ax, (0.61, 0.39), 0.24, 0.14, "Gapless continuum\nconstant $\\rho_m$", PURPLE)
    _node(ax, (0.11, 0.20), 0.20, 0.13, "Existing interface\n$S_m[A_m^2g_E,\\Psi]$", NAVY)
    _node(ax, (0.37, 0.20), 0.20, 0.13, "Direct $sR_J$\nsingular", RED)
    _node(ax, (0.67, 0.14), 0.23, 0.14, "Fixed $R_E$ +\ncollective $P(Y)$", PURPLE)
    _node(ax, (0.89, 0.52), 0.18, 0.20, "Bulk vertex + $a_0$\ncausality + lensing", GREY)
    _arrow(ax, (0.21, 0.83), (0.25, 0.83), "shape only", AMBER, label_dy=0.04)
    _arrow(ax, (0.11, 0.76), (0.11, 0.60), "fails exponent", RED, label_dy=0.01)
    _arrow(ax, (0.21, 0.53), (0.25, 0.53), "Legendre", BLUE, label_dy=0.04)
    _arrow(ax, (0.47, 0.56), (0.50, 0.65), "classical", TEAL, -0.08)
    _arrow(ax, (0.47, 0.50), (0.50, 0.42), "spectral", PURPLE, 0.08)
    _arrow(ax, (0.21, 0.20), (0.27, 0.20), "frame test", RED, label_dy=0.04)
    _arrow(ax, (0.47, 0.18), (0.55, 0.16), "keep tensor", PURPLE, label_dy=0.04)
    _arrow(ax, (0.72, 0.67), (0.82, 0.58), "derive", GREY, 0.04)
    _arrow(ax, (0.72, 0.40), (0.82, 0.48), "derive", GREY, -0.04)
    _arrow(ax, (0.78, 0.18), (0.86, 0.42), "physical gate", GREY, -0.10)
    ax.text(
        0.5,
        0.01,
        "Exact exponent found; the frozen five-dimensional origin is still open.",
        color=GREY,
        fontsize=6.5,
        ha="center",
    )
    ax.set_title("A  Old response versus critical response", loc="left", fontsize=10, weight="bold", color=NAVY)


def score_matrix(ax, matrix):
    fields = ["derivability", "stability", "sqrt_mass_scaling", "lensing", "falsifier_strength"]
    field_labels = ["Action", "Stable", "$\\sqrt{M}$", "Lensing", "Falsifier"]
    routes = matrix["routes"]
    friendly = {
        "finite_stiff_yukawa": "finite Yukawa",
        "finite_mode_tree_elimination": "gapped elimination",
        "critical_ir_soft_mode": "critical soft mode",
        "breathing_legendre_condensate": "gapped occupation",
        "brane_px_exact_control": "brane $P(X)$ control",
        "jordan_frame_gravitational_selector": "Jordan $sR$ selector",
        "derivative_constitutive_scalar": "fixed $R$ + scalar $P(Y)$",
        "tricritical_collective_amplitude": "tricritical amplitude",
        "gapless_spectral_continuum": "gapless continuum",
        "collective_bulk_backreaction": "full backreaction",
    }
    values = np.asarray([[route["scores"][field] for field in fields] for route in routes])
    image = ax.imshow(values, vmin=0, vmax=4, cmap="YlGnBu", aspect="auto")
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, str(values[i, j]), ha="center", va="center",
                    color="white" if values[i, j] >= 3 else NAVY, fontsize=7, weight="bold")
    ax.set_xticks(range(len(fields)), field_labels, fontsize=7)
    ax.set_yticks(range(len(routes)), [friendly[r["id"]] for r in routes], fontsize=7)
    ax.tick_params(length=0)
    ax.set_title("B  Route readiness (0–4; not probabilities)", loc="left", fontsize=10, weight="bold", color=NAVY)
    cbar = plt.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    cbar.ax.tick_params(labelsize=6, length=2)


def shell_cost(ax, shell):
    anchors = shell["anchors"]
    s = np.asarray([row["s"] for row in anchors])
    required = np.asarray([row["epsilon_required"] for row in anchors])
    gap = np.asarray([row["epsilon_gap"] for row in anchors])
    missing = np.asarray([row["epsilon_interaction"] for row in anchors])
    ax.loglog(s, required, color=NAVY, lw=2.0, label="required shell cost")
    ax.loglog(s, gap, color=AMBER, lw=1.7, label="gapped mode")
    ax.loglog(s, missing, color=TEAL, lw=1.7, label="inverse-designed residual")
    ax.set_xlabel("selector $s$", fontsize=8)
    ax.set_ylabel("dimensionless shell cost", fontsize=8)
    ax.grid(True, which="both", alpha=0.18, lw=0.5)
    ax.tick_params(labelsize=7)
    ax.legend(frameon=False, fontsize=6.8, loc="upper left")
    ax.set_title("C  Differential target: what the carrier still lacks", loc="left", fontsize=10, weight="bold", color=NAVY)
    ax.text(0.03, 0.08, "$W_{int}=s^4/2+\\cdots$ only after target normalization",
            transform=ax.transAxes, fontsize=6.5, color=GREY)


def source_gate(ax, axisymmetric):
    names = ["DDO154", "NGC2403", "NGC3198", "NGC2841"]
    gas = [axisymmetric["galaxies"][name]["newtonian_source_closure"]["components"]["gas"]["relative_rms_v2_over_component_peak"] for name in names]
    passed = [axisymmetric["newtonian_source_gate"]["by_galaxy"][name] for name in names]
    colors = [TEAL if value else RED for value in passed]
    bars = ax.bar(range(len(names)), gas, color=colors, width=0.68, edgecolor="white")
    ax.axhline(0.15, color=NAVY, ls="--", lw=1.2, label="frozen 0.15 gate")
    for bar, value, gate in zip(bars, gas, passed):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.012,
                f"{value:.3f}\n{'eligible' if gate else 'blocked'}",
                ha="center", va="bottom", fontsize=6.5, color=TEAL if gate else RED)
    ax.set_xticks(range(len(names)), names, rotation=18, ha="right", fontsize=7)
    ax.set_ylabel("gas closure RMS$(v^2)$/peak", fontsize=8)
    ax.set_ylim(0, max(gas) * 1.25)
    ax.grid(axis="y", alpha=0.18, lw=0.5)
    ax.tick_params(axis="y", labelsize=7)
    ax.legend(frameon=False, fontsize=6.8, loc="upper left")
    ax.set_title("D  Axisymmetric source gate before force scoring", loc="left", fontsize=10, weight="bold", color=NAVY)


def main() -> None:
    matrix = _read(MATRIX)
    shell = _read(SHELL)
    axisymmetric = _read(AXISYMMETRIC)
    fig, axes = plt.subplots(2, 2, figsize=(12.4, 9.0), constrained_layout=True)
    fig.patch.set_facecolor("white")
    route_graph(axes[0, 0])
    score_matrix(axes[0, 1], matrix)
    shell_cost(axes[1, 0], shell)
    source_gate(axes[1, 1], axisymmetric)
    fig.suptitle(
        "Nonlinear HOLO collector: old fixed poles versus critical constitutive routes",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.text(
        0.5,
        -0.012,
        "Algebraic certificates do not constitute a force detection or a microscopic derivation.",
        ha="center",
        fontsize=7.5,
        color=GREY,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[figure] {OUTPUT}")


if __name__ == "__main__":
    main()
