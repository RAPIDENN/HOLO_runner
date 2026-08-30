#!/usr/bin/env python3
"""Render the conditional P7 space--time breathing response."""

from __future__ import annotations

import json
import math
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
    / "breathing_response.json"
)
OUT = PAPER / "figures" / "fig_breathing_response.png"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def first_mode_force(mu: float, drive_ratio: float, x: np.ndarray) -> np.ndarray:
    nu = drive_ratio * mu
    if drive_ratio < 1.0:
        kappa = np.sqrt(mu * mu - nu * nu)
        return (1.0 + kappa * x) * np.exp(-kappa * x)
    if drive_ratio == 1.0:
        return np.ones_like(x)
    wave_number = np.sqrt(nu * nu - mu * mu)
    return np.sqrt(1.0 + (wave_number * x) ** 2)


def main() -> None:
    data = load(ARTIFACT)
    modes = data["correlated_mode_clock"]["modes"]
    mu = float(modes[0]["mu_n"])

    plt.rcParams.update(
        {
            "font.size": 8.4,
            "axes.titlesize": 9.4,
            "axes.labelsize": 8.4,
            "legend.fontsize": 7.0,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(10.7, 7.0), constrained_layout=True)

    ax = axes[0, 0]
    below = np.linspace(0.0, 0.999, 500)
    above = np.linspace(1.001, 2.4, 500)
    ax.plot(
        below,
        np.sqrt(1.0 - below**2),
        color="#D55E00",
        lw=2.0,
        label=r"inverse range $\kappa_1/\mu_1$",
    )
    ax.plot(
        above,
        np.sqrt(1.0 - above ** -2),
        color="#0072B2",
        lw=2.0,
        label=r"group speed $v_g/c$",
    )
    ax.axvline(1.0, color="black", lw=1.0, ls="--")
    ax.text(1.02, 0.06, "threshold", rotation=90, va="bottom", fontsize=7.2)
    ax.set_xlim(0.0, 2.4)
    ax.set_ylim(0.0, 1.04)
    ax.set_xlabel(r"drive frequency $\Omega/\omega_1$")
    ax.set_ylabel("dimensionless response scale")
    ax.set_title("A  Breathing threshold", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="best")
    ax.grid(alpha=0.2)

    ax = axes[0, 1]
    x = np.logspace(-2.0, 1.15, 420)
    styles = (
        (0.0, "#6C757D", "-"),
        (0.9, "#009E73", "-"),
        (0.99, "#E69F00", "-"),
        (1.0, "#CC79A7", "--"),
        (1.1, "#0072B2", "-"),
    )
    for ratio, color, linestyle in styles:
        ax.loglog(
            x,
            first_mode_force(mu, ratio, x),
            color=color,
            ls=linestyle,
            lw=1.7,
            label=rf"$\Omega/\omega_1={ratio:g}$",
        )
    ax.set_xlabel(r"distance $x=r/\ell$")
    ax.set_ylabel(r"$|F_1(\Omega)|/(\alpha_1 F_N)$")
    ax.set_title("B  Stiff-candidate transfer law", loc="left", fontweight="bold")
    ax.legend(frameon=False, ncol=2)
    ax.grid(alpha=0.2, which="both")

    ax = axes[1, 0]
    stiff_modes = modes
    stiff_indices = np.arange(1, len(stiff_modes) + 1)
    stiff_ratios = np.asarray(
        [row["threshold_frequency_over_f1"] for row in stiff_modes]
    )
    alpha = np.asarray(
        [row["alpha_n_2_beta_squared"] for row in stiff_modes]
    )
    trace_modes = data["provisional_trace_benchmark"]["clock"]["modes"]
    indices = np.arange(1, len(trace_modes) + 1)
    ratios = np.asarray(
        [row["threshold_frequency_over_f1"] for row in trace_modes]
    )
    ax.plot(
        indices,
        ratios,
        "o-",
        color="#0072B2",
        lw=1.5,
        ms=4.5,
        label="trace NN benchmark",
    )
    ax.plot(
        stiff_indices,
        stiff_ratios,
        "s-",
        color="#5E3C99",
        lw=1.7,
        ms=4.4,
        label="microscopic stiff candidate",
    )
    ax.set_xticks(stiff_indices)
    ax.set_xlabel("scalar mode")
    ax.set_ylabel(r"threshold $f_n/f_1$")
    twin = ax.twinx()
    twin.plot(stiff_indices, alpha, "s--", color="#D55E00", lw=1.3, ms=4.5)
    twin.set_ylabel(r"stiff residue $\alpha_n$", color="#D55E00")
    twin.tick_params(axis="y", labelcolor="#D55E00")
    twin.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3))
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("C  Boundary physics changes the comb", loc="left", fontweight="bold")
    ax.grid(alpha=0.2)

    ax = axes[1, 1]
    ratio = np.linspace(1.005, 2.4, 600)
    group_delay_over_ell_c = 1.0 / np.sqrt(1.0 - ratio ** -2)
    ax.plot(
        ratio,
        group_delay_over_ell_c,
        color="#5E3C99",
        lw=2.0,
        label=r"packet delay at $r=\ell$",
    )
    ax.axhline(1.0, color="#009E73", ls="--", lw=1.5, label="causal front $r/c$")
    ax.set_xlim(1.0, 2.4)
    ax.set_ylim(0.9, 7.0)
    ax.set_xlabel(r"drive frequency $\Omega/\omega_1$")
    ax.set_ylabel(r"time in units $\ell/c$")
    ax.set_title("D  Interaction needs time", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    stiff_duration = data["correlated_mode_clock"]["adjacent_resolution"][
        "minimum_first_zero_duration_over_T1"
    ]
    duration = data["provisional_trace_benchmark"]["clock"][
        "adjacent_resolution"
    ]["minimum_first_zero_duration_over_T1"]
    ax.text(
        0.97,
        0.93,
        rf"first-zero only: NN ${duration:.2f}T_1$; stiff ${stiff_duration:.2f}T_1$"
        "\n" r"detection also needs coherence + SNR",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7.4,
    )
    ax.grid(alpha=0.2)

    fig.suptitle(
        "Boundary-audited breathing response: frequency, range, propagation and time",
        fontsize=11.7,
        fontweight="bold",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
