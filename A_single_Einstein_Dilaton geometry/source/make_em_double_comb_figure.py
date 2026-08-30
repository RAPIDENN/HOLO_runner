#!/usr/bin/env python3
"""Render the coordinate correction and conditional double-comb fingerprint."""

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
OUT = PAPER / "figures" / "fig_em_double_comb.png"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    legacy = load(PAPER / "artifacts" / "k_em_uv_projector.json")
    kernel = load(FACTORY / "em_kernel_completion.json")
    fingerprint = load(FACTORY / "em_spectral_fingerprint.json")
    robin = load(FACTORY / "artifacts" / "robin_boundary_family.json")

    plt.rcParams.update(
        {
            "font.size": 8.2,
            "axes.titlesize": 9.2,
            "axes.labelsize": 8.2,
            "legend.fontsize": 7.0,
            "xtick.labelsize": 7.4,
            "ytick.labelsize": 7.4,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 6.9), constrained_layout=True)

    # A: expose the historical radial-gauge mix and show the true conformal
    # representation of the same corrected probability measure in an inset.
    ax = axes[0, 0]
    old_u = np.asarray(legacy["z_grid"], dtype=float)
    old_k = np.asarray(legacy["k_em"], dtype=float)
    uniform = np.full_like(old_u, 1.0 / np.ptp(old_u))
    ax.plot(old_u, old_k, color="#D55E00", lw=1.7, label="historical kernel")
    ax.plot(old_u, uniform, color="#0072B2", lw=1.7, ls="--", label=r"correct $K_u$")
    ax.set_xlabel(r"stored trace coordinate (domain-wall $u$)")
    ax.set_ylabel("normalized density")
    ax.set_title("A  Eq. 39 coordinate correction", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    mismatch = kernel["historical_artifact_audit"][
        "max_abs_difference_from_uniform_domain_wall_kernel"
    ]
    ax.text(
        0.97,
        0.08,
        rf"max $|K_{{old}}-K_u|={mismatch:.3f}$",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color="#8C2D04",
    )
    ax.grid(alpha=0.2)

    inset = ax.inset_axes([0.54, 0.35, 0.41, 0.31])
    profiles = kernel["bulk_maxwell_branch"]["eq39_special_case"]["profiles"]
    zc = np.asarray(profiles["z_conformal_from_u"])
    kzc = np.asarray(profiles["K_z_conformal"])
    inset.plot(zc, kzc, color="#009E73", lw=1.2)
    inset.set_title(r"true $K_{z_c}=e^A/\Delta u$", fontsize=6.8)
    inset.set_xlabel(r"$z_c$", fontsize=6.5)
    inset.tick_params(labelsize=6.2)
    inset.grid(alpha=0.15)

    # B: vector spectrum and charge residues.  These are independent of the
    # scalar endpoint branch but conditional on a bulk photon.
    ax = axes[0, 1]
    photon = fingerprint["bulk_photon_tower"]["modes"]
    mu_gamma = np.asarray([row["mu_gamma"] for row in photon])
    eta = np.asarray(
        [row["uv_charge_coupling_squared_relative_to_zero_mode"] for row in photon]
    )
    markerline, stemlines, baseline = ax.stem(mu_gamma, eta, basefmt=" ")
    plt.setp(stemlines, color="#0072B2", linewidth=1.4)
    plt.setp(markerline, color="#0072B2", marker="o", markersize=5)
    ax.set_xlabel(r"vector mass $\mu_{\gamma,n}=m_{\gamma,n}\ell$")
    ax.set_ylabel(r"UV residue $|g_n/g_0|^2$")
    ax.set_ylim(0, 1.08)
    ax.set_title("B  Bulk-photon KK comb", loc="left", fontweight="bold")
    ax.text(
        0.97,
        0.09,
        "same ell as scalar tower\nshooting + FEM agree",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.2,
    )
    ax.grid(alpha=0.2)

    # C: source-to-alpha coefficient; beta*d is invariant under a mode sign
    # flip even though d alone is not.
    ax = axes[1, 0]
    for code, color, marker in (
        ("NN", "#CC79A7", "o"),
        ("ND", "#009E73", "s"),
    ):
        rows = fingerprint["scalar_boundary_branches"][code]["modes"]
        masses = np.asarray([row["mu_scalar"] for row in rows])
        coeff = np.asarray(
            [row["source_to_delta_ln_alpha_per_U"] for row in rows]
        )
        ax.plot(masses, coeff, marker=marker, ls="none", color=color, label=code)
        for mass, value in zip(masses, coeff):
            ax.vlines(mass, 0.0, value, color=color, alpha=0.75, lw=1.2)
    ax.axhline(0.0, color="black", lw=0.7)
    ax.set_xlabel(r"scalar mass $\mu_n=m_n\ell$")
    ax.set_ylabel(r"$2\beta_n d_{\gamma n}$")
    ax.set_title("C  Matter-source to alpha fingerprint", loc="left", fontweight="bold")
    ax.legend(title="scalar BC", frameon=False)
    ax.text(
        0.98,
        0.06,
        r"$\delta\ln\alpha/U=\sum 2\beta_nd_{\gamma n}e^{-\mu_n r/\ell}$",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.0,
    )
    ax.grid(alpha=0.2)

    # D: show both sorted poles and attach each pole's own UV residue to its
    # marker size, so the residue exchange is visible rather than inferred.
    ax = axes[1, 1]
    uv_points = [
        row for row in robin["scan_paths"]["uv_only"] if row["rho_uv"] > 0.0
    ]
    rho = np.asarray([row["rho_uv"] for row in uv_points])
    mu0 = np.asarray([row["poles"][0]["mu"] for row in uv_points])
    mu1 = np.asarray([row["poles"][1]["mu"] for row in uv_points])
    res0 = np.asarray([row["poles"][0]["uv_profile_squared"] for row in uv_points])
    res1 = np.asarray([row["poles"][1]["uv_profile_squared"] for row in uv_points])
    ax.plot(rho, mu0, color="#D55E00", lw=1.2, alpha=0.8, label="sorted pole 0")
    ax.plot(rho, mu1, color="#0072B2", lw=1.2, alpha=0.8, label="sorted pole 1")
    residue_max = max(np.max(res0), np.max(res1))
    scale0 = 12.0 + 150.0 * res0 / residue_max
    scale1 = 12.0 + 150.0 * res1 / residue_max
    ax.scatter(rho, mu0, s=scale0, color="#D55E00", alpha=0.55, edgecolor="white", linewidth=0.3)
    ax.scatter(rho, mu1, s=scale1, color="#0072B2", alpha=0.55, edgecolor="white", linewidth=0.3)
    bracket = robin["uv_avoided_crossing"]["residue_exchange_brackets"][0]
    ax.axvspan(bracket[0], bracket[1], color="#F0E442", alpha=0.35)
    ax.set_xscale("log")
    ax.set_xlim(1.0e2, 1.0e7)
    ax.set_ylim(0.0, 1.35)
    ax.set_xlabel(r"UV boundary stiffness $\rho_{UV}$")
    ax.set_ylabel(r"first pole masses $\mu$")
    ax.set_title("D  Robin avoided crossing and residue exchange", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="lower right")
    ax.text(
        0.03,
        0.95,
        r"$b_{UV}=C_p\rho_{UV}$" "\n"
        r"$\partial_{b_{UV}}\mu_n^2=f_n(UV)^2$",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7.2,
    )
    ax.grid(alpha=0.2, which="both")

    fig.suptitle(
        "Action-derived electromagnetic double comb and boundary pole flow",
        fontsize=11.5,
        fontweight="bold",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
