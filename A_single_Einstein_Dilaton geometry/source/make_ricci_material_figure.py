#!/usr/bin/env python3
"""Plot the corrected Ricci audit and scale-free material response."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SOURCE = Path(__file__).resolve().parent
PAPER_ROOT = SOURCE.parent
REPO_ROOT = PAPER_ROOT.parent
EFFECTIVE = (
    REPO_ROOT / "first_principles_audit" / "artifacts" / "holo_effective_action.json"
)
INTERFACE = (
    REPO_ROOT
    / "first_principles_audit"
    / "artifacts"
    / "ricci_wilson_interface_audit.json"
)
MATERIAL = (
    REPO_ROOT / "first_principles_audit" / "artifacts" / "material_transducer.json"
)
LEGACY_CLOCK = PAPER_ROOT / "artifacts" / "ed_bulk_clock.json"
OUTPUT = PAPER_ROOT / "figures" / "fig_ricci_material_audit.png"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    effective = load(EFFECTIVE)
    interface = load(INTERFACE)
    material = load(MATERIAL)
    legacy = load(LEGACY_CLOCK)["series"]

    u = np.asarray(effective["u"], dtype=float)
    warp_u = np.asarray(effective["A_u"], dtype=float)
    phi_u = np.asarray(effective["phi_u"], dtype=float)
    kinetic = np.asarray(effective["kinetic_K_of_phi"], dtype=float)
    warp_uu = -kinetic * phi_u**2 / 6.0
    ricci = -8.0 * warp_uu - 20.0 * warp_u**2
    mask = u >= 1.0

    protocol = interface["ricci_5d"][
        "corrected_dimensionless_curvature_protocol"
    ]
    force = material["dimensionless_force_templates"]

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 8,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.35))

    axes[0].plot(u[mask], ricci[mask], color="#005f73", lw=2.0, label="corrected $R_5$")
    axes[0].plot(
        legacy["z"],
        legacy["R5"],
        color="#bb3e03",
        lw=1.5,
        ls="--",
        label="legacy artefact",
    )
    axes[0].set_xlabel("domain-wall coordinate $u$")
    axes[0].set_ylabel(r"dimensionless $\widehat R_5$")
    axes[0].set_title("A. Curvature audit")
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=0.22)

    protocol_u = np.asarray(protocol["u"])
    axes[1].plot(protocol_u, protocol["g_R"], color="#0a9396", lw=2, label="$g_R$")
    axes[1].plot(
        protocol_u,
        protocol["Theta_R"],
        color="#ee9b00",
        lw=2,
        label=r"$\Theta_R$",
    )
    axes[1].set_xlabel("domain-wall coordinate $u$")
    axes[1].set_ylabel("dimensionless protocol value")
    axes[1].set_title("B. Corrected Ricci protocol")
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.22)

    x = np.asarray(force["x"])
    positive_x = x[1:]
    axes[2].loglog(
        positive_x,
        np.asarray(force["positive_modes_acceleration_ratio"])[1:],
        "o-",
        color="#9b2226",
        lw=1.8,
        label="acceleration",
    )
    axes[2].loglog(
        positive_x,
        np.asarray(force["positive_modes_tidal_ratio"])[1:],
        "s--",
        color="#5a189a",
        lw=1.6,
        label="radial gradient",
    )
    axes[2].set_xlabel(r"distance $x=r/\ell$")
    axes[2].set_ylabel("scalar / Newtonian response")
    axes[2].set_title("C. Six-mode material template")
    axes[2].legend(frameon=False)
    axes[2].grid(which="both", alpha=0.22)

    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
