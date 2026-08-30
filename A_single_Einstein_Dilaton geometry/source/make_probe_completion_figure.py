#!/usr/bin/env python3
"""Render the blind compact-interval interaction certificate."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent.parent
EFFECTIVE = ROOT / "first_principles_audit" / "artifacts" / "holo_effective_action.json"
COMPLETION = ROOT / "first_principles_audit" / "artifacts" / "minimal_probe_completion.json"
OUTPUT = SOURCE.parent / "figures" / "fig_minimal_probe_completion.png"


def main() -> int:
    effective = json.loads(EFFECTIVE.read_text(encoding="utf-8"))
    completion = json.loads(COMPLETION.read_text(encoding="utf-8"))

    u = np.asarray(completion["profiles"]["u"], dtype=float)
    modes = np.asarray(completion["profiles"]["f_n"], dtype=float)
    masses = np.asarray(
        completion["dimensionless_spectrum"]["masses_mu"], dtype=float
    )
    beta_uv = np.abs(
        np.asarray(completion["uv_probe_couplings_beta_n"], dtype=float)
    )

    A = np.asarray(effective["A"], dtype=float)
    A_u = np.asarray(effective["A_u"], dtype=float)
    phi_u = np.asarray(effective["phi_u"], dtype=float)
    kinetic = np.asarray(effective["kinetic_K_of_phi"], dtype=float)
    A_uu = -kinetic * np.square(phi_u) / 6.0
    epsilon = -A_uu / np.square(A_u)
    p_weight = np.exp(4.0 * A) * epsilon
    w_weight = np.exp(2.0 * A) * epsilon

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 7.5,
            "figure.dpi": 160,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.1), constrained_layout=True)

    ax = axes[0]
    ax.semilogy(u, p_weight, color="#26547c", lw=1.6, label=r"$p=e^{4A}\epsilon$")
    ax.semilogy(u, w_weight, color="#ef476f", lw=1.6, label=r"$w=e^{2A}\epsilon$")
    ax.set_xlabel(r"dimensionless interval coordinate $u$")
    ax.set_ylabel("positive carrier weight")
    ax.set_title("A. Geometry-fixed carrier")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)

    ax = axes[1]
    colours = ("#073b4c", "#118ab2", "#06d6a0", "#ff9f1c")
    for index, colour in enumerate(colours):
        ax.plot(u, modes[index], color=colour, lw=1.35, label=rf"$f_{index}$")
    ax.axhline(0.0, color="black", lw=0.5)
    ax.set_xlabel(r"dimensionless interval coordinate $u$")
    ax.set_ylabel(r"normalized mode $f_n(u)$")
    ax.set_title("B. Neumann benchmark modes")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, ncol=2)

    ax = axes[2]
    indices = np.arange(masses.size)
    ax.plot(indices, masses, "o-", color="#6a4c93", lw=1.4, ms=4, label=r"$\mu_n$")
    ax.set_xlabel("mode number $n$")
    ax.set_ylabel(r"dimensionless mass $\mu_n$", color="#6a4c93")
    ax.tick_params(axis="y", labelcolor="#6a4c93")
    ax.grid(alpha=0.25)
    beta_axis = ax.twinx()
    beta_axis.semilogy(
        indices,
        beta_uv,
        "s--",
        color="#d62828",
        lw=1.1,
        ms=3.5,
        label=r"$|\beta_n(u_{\rm UV})|$",
    )
    beta_axis.set_ylabel(r"UV matter coupling $|\beta_n|$", color="#d62828")
    beta_axis.tick_params(axis="y", labelcolor="#d62828")
    ax.set_title("C. Blind spectrum and coupling")
    lines = ax.get_lines() + beta_axis.get_lines()
    ax.legend(lines, [line.get_label() for line in lines], frameon=False, loc="center right")

    fig.savefig(OUTPUT, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
