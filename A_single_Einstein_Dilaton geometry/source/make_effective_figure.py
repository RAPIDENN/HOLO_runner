#!/usr/bin/env python3
"""Render the geometry-preserving completion figure from its frozen artifact."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent.parent
ARTIFACT = ROOT / "first_principles_audit" / "artifacts" / "holo_effective_action.json"
OUTPUT = SOURCE.parent / "figures" / "fig_effective_reconstruction.png"


def main() -> int:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    u = np.asarray(data["u"], dtype=float)
    A = np.asarray(data["A"], dtype=float)
    phi = np.asarray(data["phi"], dtype=float)
    chi = np.asarray(data["canonical_chi"], dtype=float)
    kinetic = np.asarray(data["kinetic_K_of_phi"], dtype=float)
    potential = np.asarray(data["potential_V_of_phi"], dtype=float)
    delta_stored = np.asarray(data["delta_stored"], dtype=float)
    delta_effective = np.asarray(data["delta_effective"], dtype=float)

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 8,
            "figure.dpi": 160,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.1), constrained_layout=True)

    ax = axes[0]
    ax.plot(u, A, color="#26547c", lw=1.8, label=r"$A(u)$")
    ax.plot(u, phi, color="#ef476f", lw=1.5, label=r"$\phi(u)$")
    ax.set_xlabel(r"domain-wall coordinate $u$")
    ax.set_ylabel("field value")
    ax.set_title("A. Preserved profiles")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)

    ax = axes[1]
    ax.semilogy(chi, kinetic, color="#118ab2", lw=1.5, label=r"$K(\phi(\chi))$")
    ax.set_xlabel(r"canonical field $\chi$")
    ax.set_ylabel(r"positive kinetic function $K$")
    ax.set_title("B. Effective action")
    ax.grid(alpha=0.25)
    ax2 = ax.twinx()
    ax2.plot(chi, potential, color="#073b4c", lw=1.3, ls="--", label=r"$V(\chi)$")
    ax2.set_ylabel(r"potential $V$")
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [line.get_label() for line in lines], frameon=False, loc="best")

    ax = axes[2]
    ax.plot(u, delta_stored, color="#6a4c93", lw=2.0, label="stored")
    ax.plot(u, delta_effective, color="#ff9f1c", lw=1.2, ls="--", label="effective")
    ax.set_xlabel(r"domain-wall coordinate $u$")
    ax.set_ylabel(r"deformation $\delta$")
    ax.set_title("C. Operational recovery")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="upper left")
    inset = ax.inset_axes([0.53, 0.08, 0.42, 0.34])
    inset.plot(u, delta_effective - delta_stored, color="#d62828", lw=0.9)
    inset.axhline(0.0, color="black", lw=0.5)
    inset.set_title("residual", fontsize=7)
    inset.tick_params(labelsize=6)
    inset.grid(alpha=0.2)

    fig.savefig(OUTPUT, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
