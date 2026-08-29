from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.datasets.ofner_gdf_header import (
    CONTRACT_SHA256,
    OfnerGDFHeaderRefusal,
    RangeResponse,
    assemble_two_range_header,
    build_generated_header,
    load_registered_contract,
    parse_complete_header,
    parse_fixed_header,
    registered_plan,
    run_generated_qualification,
    validate_range_response,
)

ROOT = Path(__file__).resolve().parents[1]


def response(body: bytes, *, start: int, total: int) -> RangeResponse:
    end = start + len(body) - 1
    return RangeResponse(
        status=206,
        headers=(
            ("Content-Range", f"bytes {start}-{end}/{total}"),
            ("Content-Length", str(len(body))),
            ("Content-Encoding", "identity"),
        ),
        body=body,
    )


class OfnerGDFHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_registered_contract(ROOT)
        cls.fixture = build_generated_header(cls.contract)
        cls.total = cls.contract["exact_member"]["declared_payload_bytes"]

    def test_registered_contract_and_plan_are_generated_only(self) -> None:
        self.assertEqual(
            CONTRACT_SHA256,
            "c556049ddabdefe3f4de06d451954b8df99508c17ac950850bb8cf83e55fdae5",
        )
        plan = registered_plan(ROOT)
        self.assertEqual(plan["protocol_id"], "OFNER-C6R-1-HG0")
        self.assertFalse(plan["network_client_present"])
        self.assertFalse(plan["real_execution_command_present"])
        self.assertFalse(plan["event_parser_present"])
        self.assertFalse(plan["signal_parser_present"])
        self.assertFalse(plan["model_or_scorer_present"])

    def test_generated_fixture_contains_exactly_one_complete_header(self) -> None:
        fixed = parse_fixed_header(self.fixture[:256])
        self.assertEqual(fixed.version, "GDF 2.20")
        self.assertEqual(fixed.header_length_blocks, 97)
        self.assertEqual(fixed.header_bytes, 24_832)
        self.assertEqual(fixed.number_of_signals, 96)
        self.assertEqual(len(self.fixture), fixed.header_bytes)

    def test_complete_header_recovers_frozen_measurement_contract(self) -> None:
        parsed = parse_complete_header(self.fixture, self.contract)
        self.assertEqual(parsed.number_of_signals, 96)
        self.assertEqual(parsed.sampling_rate_hz, 512)
        self.assertEqual(
            (parsed.EEG_channels, parsed.EOG_channels, parsed.glove_channels, parsed.arm_channels),
            (61, 3, 19, 13),
        )
        self.assertEqual(parsed.unique_normalized_labels, 96)
        self.assertEqual(parsed.finite_nonzero_EEG_geometry_channels, 61)

    def test_two_ranges_are_exact_gapless_and_signal_free(self) -> None:
        first = response(self.fixture[:256], start=0, total=self.total)
        second = response(self.fixture[256:], start=256, total=self.total)
        assembled = assemble_two_range_header(first, second, expected_total=self.total)
        self.assertEqual(assembled, self.fixture)
        self.assertEqual(len(first.body) + len(second.body), 24_832)
        self.assertLess(len(assembled), 65_536)

    def test_range_firewall_rejects_redirect_encoding_and_overread(self) -> None:
        first = response(self.fixture[:256], start=0, total=self.total)
        with self.assertRaises(OfnerGDFHeaderRefusal):
            validate_range_response(
                replace(first, redirects=1),
                expected_start=0,
                expected_end=255,
                expected_total=self.total,
            )
        with self.assertRaises(OfnerGDFHeaderRefusal):
            validate_range_response(
                replace(
                    first,
                    headers=first.headers + (("Transfer-Encoding", "chunked"),),
                ),
                expected_start=0,
                expected_end=255,
                expected_total=self.total,
            )
        with self.assertRaises(OfnerGDFHeaderRefusal):
            assemble_two_range_header(
                first,
                response(self.fixture[255:], start=255, total=self.total),
                expected_total=self.total,
            )

    def test_parser_rejects_trailing_signal_like_bytes(self) -> None:
        with self.assertRaises(OfnerGDFHeaderRefusal):
            parse_complete_header(self.fixture + b"\x00\x00", self.contract)

    def test_generated_qualification_is_deterministic_and_bounded(self) -> None:
        with patch(
            "neurodecodekit.datasets.ofner_gdf_header._peak_rss_bytes",
            return_value=26_214_400,
        ):
            result = run_generated_qualification(ROOT)
        self.assertEqual(result["status"], "accepted_generated_only")
        measurements = result["measurements"]
        self.assertEqual(measurements["generated_replays"], 2)
        self.assertEqual(measurements["combined_range_body_bytes_per_replay"], 24_832)
        self.assertGreaterEqual(measurements["named_adversarial_refusals"], 30)
        self.assertEqual(measurements["network_bytes"], 0)
        self.assertEqual(measurements["retained_generated_payload_bytes"], 0)
        self.assertTrue(result["determinism"]["replay_summaries_equal"])
        self.assertTrue(result["determinism"]["transcript_digests_equal"])
        self.assertTrue(all(value == 0 for value in result["operation_counters"].values()))

    def test_generated_qualification_refuses_over_rss_cap(self) -> None:
        with patch(
            "neurodecodekit.datasets.ofner_gdf_header._peak_rss_bytes",
            return_value=268_435_457,
        ), self.assertRaisesRegex(OfnerGDFHeaderRefusal, "RSS cap"):
            run_generated_qualification(ROOT)

    def test_nonunit_thread_environment_refuses(self) -> None:
        old = os.environ.get("OMP_NUM_THREADS")
        os.environ["OMP_NUM_THREADS"] = "2"
        try:
            with self.assertRaises(OfnerGDFHeaderRefusal):
                run_generated_qualification(ROOT)
        finally:
            if old is None:
                os.environ.pop("OMP_NUM_THREADS", None)
            else:
                os.environ["OMP_NUM_THREADS"] = old

    def test_cli_help_exposes_no_execute_command(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.ofner_gdf_header_cli", "--help"],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("qualify-generated", completed.stdout)
        self.assertNotIn("execute", completed.stdout)

    def test_cli_generated_plan_roundtrip_is_json_and_target_free(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.ofner_gdf_header_cli",
                "plan",
                "--repo-root",
                str(ROOT),
            ],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["mode"], "generated_only")
        self.assertFalse(result["network_client_present"])
        self.assertFalse(result["real_execution_command_present"])
        encoded = completed.stdout.encode("utf-8")
        self.assertNotIn(b"target_text", encoded)
        self.assertLess(len(encoded), 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
