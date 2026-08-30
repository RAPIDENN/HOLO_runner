#!/usr/bin/env python3
"""Render the four-panel prediction-factory audit figure."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


SOURCE = Path(__file__).resolve().parent
PAPER = SOURCE.parent
REPO = PAPER.parent
FACTORY = REPO / "first_principles_audit" / "prediction_factory"
OUT = PAPER / "figures" / "fig_prediction_factory.png"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    boundary = load(FACTORY / "artifacts" / "boundary_branch_catalogue.json")
    sparc = load(FACTORY / "sparc_crossval_report.json")
    desi = load(FACTORY / "desi_dr1_growth_diagnostic.json")
    kernel = load(PAPER / "artifacts" / "k_em_uv_projector.json")
    em = load(FACTORY / "em_kernel_completion.json")

    plt.rcParams.update(
        {
            "font.size": 8.2,
            "axes.titlesize": 9.2,
            "axes.labelsize": 8.2,
            "legend.fontsize": 7.2,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 6.7), constrained_layout=True)

    # A: all self-adjoint endpoint choices.  NN's exact zero is placed at a
    # labelled plotting sentinel because a logarithmic mass axis cannot show 0.
    ax = axes[0, 0]
    order = ["NN", "ND", "DN", "DD"]
    for y, name in enumerate(order):
        row = boundary["branches"][name]
        masses = np.asarray(row["masses_mu"], dtype=float)
        decoupled = bool(row["uv_point_probe_decouples"])
        if decoupled:
            ax.scatter(
                masses,
                np.full_like(masses, y),
                s=34,
                facecolors="none",
                edgecolors="#666666",
                marker="o",
                linewidths=1.0,
            )
        else:
            ax.scatter(masses, np.full_like(masses, y), s=30, color="#0072B2")
        if row["has_exact_massless_mode"]:
            ax.scatter([8e-5], [y], s=72, color="#D55E00", marker="*")
            ax.text(1.05e-4, y + 0.12, "exact zero", color="#A33E00", fontsize=7)
    ax.axvspan(5e-5, 1e-2, color="#D55E00", alpha=0.07)
    ax.set_xscale("log")
    ax.set_xlim(5e-5, 5.0)
    ax.set_yticks(range(4), order)
    ax.invert_yaxis()
    ax.set_xlabel(r"dimensionless mass $\mu=m\ell$")
    ax.set_title("A  Boundary branches (none selected)", loc="left", fontweight="bold")
    ax.grid(axis="x", which="both", alpha=0.2)
    ax.text(
        0.0027448,
        1.2,
        r"ND: $\mu_0=0.002745$",
        ha="center",
        va="bottom",
        fontsize=7,
        color="#0072B2",
    )
    ax.text(
        0.98,
        0.03,
        "open = UV point probe decouples",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7,
        color="#555555",
    )

    # B: held-out development split.  Absolute values are intentionally shown.
    ax = axes[0, 1]
    test = sparc["results"]["test"]
    labels = ["P5", "Newton", "RAR"]
    values = [test["models"][key]["chi2_per_point"] for key in ("p5", "newton", "rar")]
    colors = ["#0072B2", "#999999", "#009E73"]
    bars = ax.bar(labels, values, color=colors, width=0.62)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 6, f"{value:.1f}", ha="center")
    ax.set_ylim(0, max(values) * 1.18)
    ax.set_ylabel(r"test $\chi^2$/velocity point")
    ax.set_title("B  SPARC retrospective test split", loc="left", fontweight="bold")
    ax.text(
        0.03,
        0.96,
        "27 galaxies; P5 wins 22 vs Newton, 8 vs RAR\n"
        "P5 optimizer not converged; not a blind test",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7.2,
    )
    ax.spines[["top", "right"]].set_visible(False)

    # C: marginal published ShapeFit entries, explicitly not a full likelihood.
    ax = axes[1, 0]
    rows = desi["rows"]
    z = np.asarray([row["z_eff"] for row in rows])
    holo = np.asarray([row["holo_marginal_pull"] for row in rows])
    lcdm = np.asarray([row["lcdm_marginal_pull"] for row in rows])
    ax.axhspan(-1, 1, color="#999999", alpha=0.12)
    ax.axhline(0, color="black", lw=0.7)
    ax.plot(z, holo, "o-", color="#D55E00", label="frozen dictionary")
    ax.plot(z, lcdm, "s--", color="#0072B2", label=r"matched $\Lambda$CDM")
    ax.set_xlabel(r"effective redshift $z_{\rm eff}$")
    ax.set_ylabel("marginal pull")
    ax.set_title("C  DESI DR1 diagonal diagnostic", loc="left", fontweight="bold")
    ax.legend(loc="lower left", frameon=False)
    ax.text(
        0.98,
        0.95,
        r"$\chi^2_{\rm dict}=2.692$" "\n" r"$\chi^2_{\Lambda\rm CDM}=2.419$",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7.5,
    )
    ax.grid(alpha=0.2)

    # D: expose the historical radial-gauge mix instead of reproducing it by
    # defining a synthetic warp factor from the legacy kernel itself.
    ax = axes[1, 1]
    z_k = np.asarray(kernel["z_grid"], dtype=float)
    k = np.asarray(kernel["k_em"], dtype=float)
    audit = em["historical_artifact_audit"]
    uniform = audit["correct_Z1_domain_wall_uniform_value_on_legacy_support"]
    err = audit["max_abs_difference_from_uniform_domain_wall_kernel"]
    ax.plot(z_k, k, color="#CC79A7", lw=2.0, label="historical profile")
    ax.axhline(
        uniform,
        color="black",
        lw=1.1,
        ls="--",
        label=r"correct flat $K_u$",
    )
    ax.set_xlabel("raw trace coordinate (domain-wall u)")
    ax.set_ylabel(r"normalized radial density")
    ax.set_title("D  Historical EM gauge mix", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    ax.text(
        0.97,
        0.93,
        rf"max $|K_{{\rm old}}-K_u|={err:.6f}$" "\n"
        r"correct conformal density: $K_{z_c}=e^A/\Delta u$" "\n"
        "old numerical projection rejected",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7.2,
    )
    ax.grid(alpha=0.2)

    fig.suptitle(
        "Prediction factory: physical branch gates and present-data diagnostics",
        fontsize=11.5,
        fontweight="bold",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
