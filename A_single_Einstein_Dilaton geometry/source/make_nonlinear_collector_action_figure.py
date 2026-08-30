#!/usr/bin/env python3
"""Plot the nonlinear collector action and its mass-dependent scale map."""

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
ARTIFACT = (
    REPO
    / "first_principles_audit"
    / "prediction_factory"
    / "artifacts"
    / "nonlinear_collector_action.json"
)
OUT = PAPER / "figures" / "fig_nonlinear_collector_action.png"


def main() -> None:
    result = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rows = np.asarray(result["action_reconstruction"]["table"]["rows"])
    t, y, x, _, mu, _ = rows.T
    nu = 1.0 / mu
    exp_minus_t = np.exp(-t)
    denominator = -np.expm1(-t)
    dx_dt = 2.0 * t / denominator - t**2 * exp_minus_t / denominator**2
    longitudinal = mu + x * exp_minus_t / dx_dt
    ceiling = 1.106765079

    plt.rcParams.update(
        {
            "font.size": 8.0,
            "axes.titlesize": 9.0,
            "axes.labelsize": 8.0,
            "legend.fontsize": 7.0,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(10.7, 3.35), constrained_layout=True)

    ax = axes[0]
    ax.plot(y, nu, color="#0072B2", lw=2.2, label=r"collector $\nu(y)$")
    ax.axhline(ceiling, color="#7A3E9D", ls="-.", lw=1.8, label="stiff Yukawa ceiling")
    ax.axhline(1.0, color="#888888", ls="--", lw=1.0, label="Newtonian")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0e-5, 1.0e4)
    ax.set_ylim(0.95, 400.0)
    ax.set_xlabel(r"Newtonian acceleration $y=g_N/a_0$")
    ax.set_ylabel(r"acceleration multiplier $\nu=g/g_N$")
    ax.set_title("A  Required response", loc="left", fontweight="bold")
    ax.grid(alpha=0.18, which="both")
    ax.legend(frameon=False, loc="upper right")

    ax = axes[1]
    ax.plot(x, mu, color="#009E73", lw=2.1, label=r"transverse $\mu$")
    ax.plot(
        x,
        longitudinal,
        color="#D55E00",
        lw=1.8,
        ls="--",
        label=r"longitudinal $\mu+x\mu'$",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0e-6, 2.0e3)
    ax.set_ylim(5.0e-7, 2.0)
    ax.set_xlabel(r"physical acceleration $x=g/a_0$")
    ax.set_ylabel("elliptic eigenvalue")
    ax.set_title("B  Locally elliptic; degenerate at zero", loc="left", fontweight="bold")
    ax.grid(alpha=0.18, which="both")
    ax.legend(frameon=False, loc="lower right")

    ax = axes[2]
    mass_grid = np.geomspace(1.0e-6, 1.0e16, 500)
    sun = result["scale_map"]["transition_radii_by_source_mass"]["Sun"]
    radius_grid = sun["radius_kpc"] * np.sqrt(mass_grid)
    ax.plot(mass_grid, radius_grid, color="#CC79A7", lw=2.2)
    markers = {
        "Earth": "Earth",
        "Sun": "Sun",
        "dwarf_3e8_Msun": "dwarf",
        "Milky_Way_baryons_6e10_Msun": "MW baryons",
        "cluster_3e14_Msun": "cluster",
    }
    offsets = {
        "cluster_3e14_Msun": (-42, 5),
        "Milky_Way_baryons_6e10_Msun": (4, 6),
    }
    scales = result["scale_map"]["transition_radii_by_source_mass"]
    for key, label in markers.items():
        row = scales[key]
        ax.scatter(row["mass_msun"], row["radius_kpc"], s=28, zorder=3)
        ax.annotate(
            label,
            (row["mass_msun"], row["radius_kpc"]),
            xytext=offsets.get(key, (4, 4)),
            textcoords="offset points",
            fontsize=6.7,
        )
    ax.axhline(0.6, color="#0072B2", ls="--", lw=1.0)
    ax.axhline(600.0, color="#7A3E9D", ls="-.", lw=1.0)
    ax.text(1.5e-5, 0.68, r"0.6 kpc $\leftrightarrow2.96\times10^8 M_\odot$", fontsize=6.8)
    ax.text(1.5e-5, 680.0, r"600 kpc $\leftrightarrow2.96\times10^{14} M_\odot$", fontsize=6.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0e-6, 1.0e16)
    ax.set_ylim(1.0e-8, 3.0e3)
    ax.set_xlabel(r"isolated source mass $M/M_\odot$")
    ax.set_ylabel(r"transition radius $r_M$ [kpc]")
    ax.set_title("C  No universal 600-scale", loc="left", fontweight="bold")
    ax.grid(alpha=0.18, which="both")

    fig.suptitle(
        "Nonlinear collector action target: one acceleration scale, mass-dependent radii",
        fontsize=11.0,
        fontweight="bold",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
