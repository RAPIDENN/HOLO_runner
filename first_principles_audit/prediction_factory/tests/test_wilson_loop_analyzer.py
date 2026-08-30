from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from first_principles_audit.prediction_factory.wilson_loop_analyzer import (
    LINK_SCHEMA,
    analyze_sources,
    creutz_ratio,
    estimate_sigma_a2,
    load_link_ensemble,
    measure_wilson_loops,
    physical_scale_conversion,
    summarize_wilson_tables,
    validate_su3_links,
    wilson_rectangle,
)


def identity_links(n_configurations: int = 4, length: int = 4) -> np.ndarray:
    shape = (n_configurations, length, length, length, length, 4, 3, 3)
    links = np.zeros(shape, dtype=np.complex128)
    links[...] = np.eye(3, dtype=np.complex128)
    return links


def write_npz(path: Path, links: np.ndarray, **overrides: object) -> None:
    metadata: dict[str, object] = {
        "schema": LINK_SCHEMA,
        "axis_order": "config,x,y,z,t,mu,row,col",
        "gauge_group": "SU(3)",
        "boundary_conditions": "periodic",
        "time_direction": 3,
        "ensemble_id": "synthetic-identity",
        "gauge_action": "Wilson plaquette",
        "beta": 6.0,
        "thermalization_sweeps": 100,
        "saved_configuration_stride_sweeps": 10,
    }
    metadata.update(overrides)
    np.savez(path, links=links, **metadata)


class WilsonLoopAnalyzerTests(unittest.TestCase):
    def test_identity_rectangle_is_one(self) -> None:
        configuration = identity_links(1, 4)[0]
        for origin in ((0, 0, 0, 0), (3, 2, 1, 3)):
            for direction in range(3):
                self.assertAlmostEqual(
                    wilson_rectangle(
                        configuration, origin, direction, 2, 2
                    ),
                    1.0,
                    places=14,
                )

    def test_pure_gauge_configuration_has_unit_wilson_loops(self) -> None:
        length = 4
        gauge = np.zeros((length, length, length, length, 3, 3), dtype=np.complex128)
        for site in np.ndindex(length, length, length, length):
            phase = 0.13 * (site[0] + 2 * site[1] + 3 * site[2] + 5 * site[3])
            gauge[site] = np.diag(
                [np.exp(1j * phase), np.exp(-1j * phase), 1.0]
            )
        links = identity_links(1, length)
        for site in np.ndindex(length, length, length, length):
            for direction in range(4):
                neighbour = list(site)
                neighbour[direction] = (neighbour[direction] + 1) % length
                links[(0, *site, direction)] = (
                    gauge[site] @ gauge[tuple(neighbour)].conj().T
                )
        measured = measure_wilson_loops(links, r_max=2, t_max=2)
        np.testing.assert_allclose(measured, 1.0, atol=2e-14, rtol=0.0)

    def test_creutz_recovers_exact_area_coefficient(self) -> None:
        sigma_a2 = 0.17
        perimeter = 0.31
        table = np.zeros((4, 4), dtype=np.float64)
        for r in range(1, 5):
            for t in range(1, 5):
                table[r - 1, t - 1] = math.exp(
                    -sigma_a2 * r * t - perimeter * (r + t)
                )
        for r in range(2, 5):
            for t in range(2, 5):
                self.assertAlmostEqual(
                    creutz_ratio(table, r, t), sigma_a2, places=14
                )

    def test_canonical_npz_loads_and_checks_every_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "links.npz"
            write_npz(path, identity_links())
            loaded = load_link_ensemble(path)
            self.assertEqual(loaded.links.shape, (4, 4, 4, 4, 4, 4, 3, 3))
            self.assertTrue(loaded.validation["all_links_checked"])
            self.assertEqual(loaded.metadata["gauge_group"], "SU(3)")

    def test_non_su3_link_is_rejected(self) -> None:
        links = identity_links(1, 2)
        links[(0, 0, 0, 0, 0, 0)] *= 2.0
        with self.assertRaisesRegex(ValueError, r"fail SU\(3\) validation"):
            validate_su3_links(links)

    def test_summary_and_endpoint_proxy_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = root / "su3_summary.json"
            summary.write_text(
                json.dumps(
                    {"result": {"observables": {"plaquette_mean": 0.55}}}
                ),
                encoding="utf-8",
            )
            proxy = root / "wilson_endpoint_proxy.json"
            proxy.write_text(
                json.dumps(
                    {
                        "e2A_ir": 0.01,
                        "alpha_prime_GeV-2": 0.02,
                        "sigma_eff_GeV2": 0.2,
                    }
                ),
                encoding="utf-8",
            )
            result = analyze_sources([root])
            self.assertEqual(
                result["status"], "blocked_missing_link_configurations"
            )
            classifications = {
                row["classification"] for row in result["discovered_files"]
            }
            self.assertIn("observable_summary_without_links", classifications)
            self.assertIn("excluded_ed_endpoint_proxy", classifications)
            self.assertFalse(result["physical_scale"]["endpoint_proxy_used"])
            self.assertEqual(result["sigma_a2"]["value"], None)
            self.assertNotIn(directory, json.dumps(result))

    def test_identity_links_compute_w_but_do_not_fake_string_tension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "wilson_links.npz"
            write_npz(path, identity_links())
            result = analyze_sources(
                [path], r_max=2, t_max=2, block_size=1
            )
            self.assertEqual(
                result["status"], "wilson_loops_computed_sigma_not_established"
            )
            for record in result["measurements"]["wilson_loops"]:
                self.assertAlmostEqual(record["mean"], 1.0, places=14)
            self.assertEqual(result["sigma_a2"]["value"], None)
            self.assertFalse(result["evidence_boundary"]["endpoint_proxy_used"])

    def test_physical_conversion_requires_external_inverse_spacing(self) -> None:
        sigma = {"value": 0.04}
        missing = physical_scale_conversion(sigma, None)
        self.assertEqual(missing["status"], "not_available")
        converted = physical_scale_conversion(sigma, 2.0)
        self.assertEqual(
            converted["status"], "converted_using_external_lattice_scale"
        )
        self.assertAlmostEqual(converted["sigma_GeV2"], 0.16)
        self.assertAlmostEqual(converted["sqrt_sigma_GeV"], 0.4)
        self.assertFalse(converted["endpoint_proxy_used"])

    def test_explicit_stable_creutz_window_yields_only_sigma_a2(self) -> None:
        sigma_a2 = 0.17
        perimeter = 0.31
        per_configuration = np.zeros((4, 3, 3), dtype=np.float64)
        for config_index in range(4):
            for r in range(1, 4):
                for t in range(1, 4):
                    per_configuration[config_index, r - 1, t - 1] = math.exp(
                        -sigma_a2 * r * t - perimeter * (r + t)
                    )
        tables, mean, leave_one_out = summarize_wilson_tables(
            per_configuration, block_size=1
        )
        metadata = {
            "ensemble_id": "synthetic-area-law",
            "gauge_action": "synthetic test only",
            "beta": 6.0,
            "thermalization_sweeps": 100,
            "saved_configuration_stride_sweeps": 10,
        }
        estimate = estimate_sigma_a2(
            mean,
            leave_one_out,
            sigma_window=(2, 3, 2, 3),
            metadata=metadata,
            n_blocks=tables["blocking"]["n_blocks"],
        )
        self.assertEqual(
            estimate["status"], "diagnostic_lattice_plateau_estimate"
        )
        self.assertAlmostEqual(estimate["value"], sigma_a2, places=14)
        self.assertTrue(estimate["not_a_physical_GeV_scale"])


if __name__ == "__main__":
    unittest.main()
