#!/usr/bin/env python3
"""Render the repaired SPARC audit and current stiff-force test curves."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


SOURCE = Path(__file__).resolve().parent
PAPER = SOURCE.parent
REPO = PAPER.parent
FACTORY = REPO / "first_principles_audit" / "prediction_factory"
REPORT = FACTORY / "sparc_physical_audit.json"
COLLECTOR = FACTORY / "artifacts" / "universal_residual_collector.json"
OUT = PAPER / "figures" / "fig_sparc_physical_audit.png"

sys.path.insert(0, str(REPO))
from first_principles_audit.prediction_factory import sparc_crossval as legacy  # noqa: E402
from first_principles_audit.prediction_factory import sparc_physical_audit as audit  # noqa: E402
from first_principles_audit.prediction_factory import derive_sparc_finite_disk_yukawa as finite_disk  # noqa: E402


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    collector = json.loads(COLLECTOR.read_text(encoding="utf-8"))
    groups, split = audit.load_groups(
        legacy.default_sparc_dir(),
        FACTORY / "sparc_split_v1.json",
        legacy.default_trace_path(),
    )
    test_by_name = {galaxy.name: galaxy for galaxy in groups["test"]}
    selected = [test_by_name[name] for name in report["protocol"]["test_curve_ids"]]
    fits = report["frozen_train_fits"]
    g_dagger = collector["train_fit"]["g_dagger_m_s2"]
    stiff = fits["stiff_boundary_long_range_convolution_envelope"]
    stiff_alpha = stiff["sum_positive_alpha_n"]
    stiff_masses = np.asarray(stiff["positive_mode_masses_mu"])
    stiff_strengths = np.asarray(stiff["positive_mode_strengths_alpha"])
    selected_ell = report["finite_disk_followup"]["best_global_ell_kpc"]

    plt.rcParams.update(
        {
            "font.size": 7.8,
            "axes.titlesize": 8.8,
            "axes.labelsize": 7.8,
            "legend.fontsize": 6.8,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
        }
    )
    mosaic = [["acc", "acc"], ["g0", "g1"], ["g2", "g3"]]
    fig, axes = plt.subplot_mosaic(
        mosaic, figsize=(10.6, 8.1), constrained_layout=True
    )

    # Every point in the frozen test split is shown in acceleration space.
    ax = axes["acc"]
    gbar_values: list[float] = []
    gobs_values: list[float] = []
    for galaxy in groups["test"]:
        radius_m = galaxy.radius_kpc * legacy.KPC_METRES
        gbar_values.extend(np.square(galaxy.v_bary_kms) * 1.0e6 / radius_m)
        gobs_values.extend(np.square(galaxy.v_obs_kms) * 1.0e6 / radius_m)
    gbar = np.asarray(gbar_values)
    gobs = np.asarray(gobs_values)
    positive = (gbar > 0) & (gobs > 0)
    ax.scatter(
        gbar[positive],
        gobs[positive],
        s=8,
        color="#777777",
        alpha=0.38,
        linewidths=0,
        label="621 test points",
    )
    grid = np.logspace(-14.5, -8.5, 500)
    rar_grid = grid / (-np.expm1(-np.sqrt(grid / g_dagger)))
    ax.plot(grid, grid, color="#999999", ls="--", lw=1.2, label="baryons only")
    ax.plot(
        grid,
        grid * (1.0 + stiff_alpha),
        color="#7A3E9D",
        ls="-.",
        lw=2.0,
        label=r"stiff force (selected $\ell\to\infty$ limit)",
    )
    ax.plot(
        grid,
        rar_grid,
        color="#0072B2",
        lw=2.0,
        label="universal collector (empirical RAR)",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(10**-14.5, 10**-8.5)
    ax.set_ylim(10**-14.5, 10**-8.5)
    ax.set_xlabel(r"baryonic acceleration $g_{\rm bar}$ [m s$^{-2}$]")
    ax.set_ylabel(r"observed acceleration $g_{\rm obs}$ [m s$^{-2}$]")
    ax.set_title(
        "A  SPARC physical baryonic contract: every frozen test point",
        loc="left",
        fontweight="bold",
    )
    ax.legend(frameon=False, loc="upper left")
    ax.grid(alpha=0.16, which="both")
    ax.text(
        0.98,
        0.05,
        r"$\Upsilon_d=0.5$, $\Upsilon_b=0.7$; signed gas" "\n"
        r"RAR $a_\dagger=1.144\times10^{-10}$ m s$^{-2}$" "\n"
        r"stiff maximum $\Delta V/V=5.20\%$" "\n"
        r"finite-disk scan: best $\ell$ at $10^5$ kpc boundary" "\n"
        r"$R\geq0.6$ kpc: stiff "
        f"{collector['six_hundred_disambiguation']['observed_radius_thresholds_test'][1]['stiff_long_range']['chi2_per_point']:.2f}; "
        r"$\ell=600$ kpc: "
        f"{collector['six_hundred_disambiguation']['global_yukawa_range_test']['test'][1]['chi2_per_point']:.2f}" "\n"
        r"test $\chi^2/N$: stiff "
        f"{collector['metrics']['stiff_long_range']['test']['chi2_per_point']:.2f}; "
        f"collector {collector['metrics']['collector']['test']['chi2_per_point']:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.2,
    )

    for index, galaxy in enumerate(selected):
        ax = axes[f"g{index}"]
        stiff_curve = finite_disk.stiff_disk_velocity_curves(
            galaxy,
            np.asarray([selected_ell]),
            stiff_masses,
            stiff_strengths,
        )[0][0]
        rar_curve = legacy.predict_rar(galaxy, g_dagger)
        ax.errorbar(
            galaxy.radius_kpc,
            galaxy.v_obs_kms,
            yerr=galaxy.sigma_v_kms,
            fmt="o",
            ms=3.0,
            capsize=1.5,
            color="black",
            ecolor="#444444",
            label=r"$V_{\rm obs}$",
        )
        ax.plot(
            galaxy.radius_kpc,
            galaxy.v_bary_kms,
            color="#888888",
            ls="--",
            lw=1.3,
            label="repaired baryons",
        )
        ax.plot(
            galaxy.radius_kpc,
            rar_curve,
            color="#0072B2",
            lw=1.8,
            label="universal collector / RAR",
        )
        ax.plot(
            galaxy.radius_kpc,
            stiff_curve,
            color="#7A3E9D",
            ls="-.",
            lw=1.9,
            label=r"stiff finite-disk ($\ell=10^5$ kpc)",
        )
        ax.set_title(
            f"{chr(66 + index)}  {galaxy.name} (frozen test order)",
            loc="left",
            fontweight="bold",
        )
        ax.set_xlabel("radius [kpc]")
        ax.set_ylabel(r"circular speed [km s$^{-1}$]")
        ax.grid(alpha=0.18)
        ax.spines[["top", "right"]].set_visible(False)
        if index == 0:
            ax.legend(frameon=False, ncol=2, loc="best")

    fig.suptitle(
        "SPARC audit: action-derived stiff force versus empirical target",
        fontsize=11.2,
        fontweight="bold",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
