from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.datasets import neural_payload_admission as npa1

ROOT = Path(__file__).resolve().parents[1]
ONE_THREAD_ENV = {key: "1" for key in npa1.THREAD_ENV_KEYS}


class NeuralPayloadAdmissionTests(unittest.TestCase):
    def test_plan_is_generated_only_and_exposes_no_live_surface(self) -> None:
        plan = npa1.registered_plan(ROOT)
        self.assertEqual(plan["protocol_id"], "NPA1-G-v0")
        self.assertEqual(plan["deterministic_replays"], 2)
        self.assertGreaterEqual(plan["implemented_named_adversarial_families"], 24)
        self.assertFalse(plan["network_client_present"])
        self.assertFalse(plan["real_execution_command_present"])
        self.assertFalse(plan["real_or_private_path_access_authorized"])
        self.assertFalse(plan["scientific_claim_upgrade_authorized"])

    def test_frontier_binding_is_exact_and_mutation_refuses(self) -> None:
        self.assertEqual(
            (ROOT / npa1.FRONTIER_RELATIVE_PATH).stat().st_size,
            npa1.FRONTIER_BYTES,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / npa1.FRONTIER_RELATIVE_PATH
            destination.parent.mkdir(parents=True)
            payload = (ROOT / npa1.FRONTIER_RELATIVE_PATH).read_bytes() + b" "
            destination.write_bytes(payload)
            with self.assertRaisesRegex(
                npa1.NeuralPayloadAdmissionRefusal, "frontier artifact identity"
            ):
                npa1.registered_plan(root)

    def test_two_replays_capability_refresh_and_refusals_are_exact(self) -> None:
        report = npa1.run_generated_qualification(
            ROOT,
            environ=ONE_THREAD_ENV,
            clock=iter((10.0, 10.125)).__next__,
            rss_reader=lambda: 23_822_336,
        )
        qualification = report["qualification"]
        self.assertEqual(qualification["deterministic_replays"], 2)
        self.assertEqual(qualification["accepted_profiles_per_replay"], 7)
        self.assertTrue(qualification["stable_transcript_digests_equal"])
        self.assertTrue(qualification["signed_capability_refresh_accepted"])
        self.assertEqual(
            tuple(row["mutation"] for row in qualification["refusals"]),
            npa1.REQUIRED_MUTATIONS,
        )
        self.assertEqual(qualification["named_adversarial_families"], 37)
        self.assertTrue(all(value == 0 for value in report["operation_counters"].values()))
        self.assertLess(
            report["measurements"]["generated_input_bytes"]
            + report["measurements"]["generated_output_bytes"],
            npa1.MAX_GENERATED_BYTES,
        )
        self.assertGreater(
            report["measurements"]["body_reads"],
            report["measurements"]["response_opens"],
        )

    def test_replay_digest_ignores_ephemeral_signature_only(self) -> None:
        first = npa1._run_acceptance_replay("0123456789abcdef", npa1.FixtureMetrics())
        second = npa1._run_acceptance_replay("fedcba9876543210", npa1.FixtureMetrics())
        self.assertEqual(first, second)

    def test_private_route_and_signed_shape_refuse_before_open(self) -> None:
        profile, body = npa1._acceptance_profiles()[1]
        url = npa1._signed_url(profile.source, "0123456789abcdef")
        metrics = npa1.FixtureMetrics()
        opener = npa1.FixtureOpener(
            (
                npa1.FixtureExchange(
                    url,
                    206,
                    npa1._headers_for(profile),
                    body,
                    npa1._request_headers(profile),
                ),
            ),
            metrics,
        )
        with self.assertRaisesRegex(
            npa1.NeuralPayloadAdmissionRefusal, npa1.REFUSAL_IDS["route"]
        ):
            npa1.admit_generated_transport(
                profile=profile,
                capability=npa1.TransportCapability(url, npa1.ALLOWED_HOSTS, 0),
                opener=opener,
                resolver=npa1.FixtureResolver(("127.0.0.1",)),
                metrics=metrics,
            )
        self.assertEqual(metrics.response_opens, 0)

        split = npa1.urlsplit(url)
        drifted = npa1.urlunsplit(
            (split.scheme, split.netloc, split.path, split.query + "&extra=1", "")
        )
        with self.assertRaisesRegex(
            npa1.NeuralPayloadAdmissionRefusal, npa1.REFUSAL_IDS["capability"]
        ):
            npa1.admit_generated_transport(
                profile=profile,
                capability=npa1.TransportCapability(
                    drifted, npa1.ALLOWED_HOSTS, 0
                ),
                opener=npa1.FixtureOpener((), npa1.FixtureMetrics()),
                resolver=npa1.FixtureResolver(),
                metrics=npa1.FixtureMetrics(),
            )

    def test_impossible_range_profile_refuses_before_open(self) -> None:
        profile, body = npa1._acceptance_profiles()[1]
        invalid = replace(profile, range_start=500, range_end=100, total_bytes=50)
        url = npa1._signed_url(profile.source, "0123456789abcdef")
        metrics = npa1.FixtureMetrics()
        exchange = npa1.FixtureExchange(
            url,
            206,
            npa1._headers_for(profile),
            body,
            npa1._request_headers(invalid),
        )
        with self.assertRaisesRegex(
            npa1.NeuralPayloadAdmissionRefusal, npa1.REFUSAL_IDS["range"]
        ):
            npa1.admit_generated_transport(
                profile=invalid,
                capability=npa1.TransportCapability(url, npa1.ALLOWED_HOSTS, 0),
                opener=npa1.FixtureOpener((exchange,), metrics),
                resolver=npa1.FixtureResolver(),
                metrics=metrics,
            )
        self.assertEqual(metrics.response_opens, 0)

    def test_expired_capability_refuses_before_open(self) -> None:
        profile, body = npa1._acceptance_profiles()[1]
        url = npa1._signed_url(
            profile.source,
            "0123456789abcdef",
            issued=npa1.FROZEN_NOW_EPOCH_SECONDS - 601,
        )
        metrics = npa1.FixtureMetrics()
        exchange = npa1.FixtureExchange(
            url,
            206,
            npa1._headers_for(profile),
            body,
            npa1._request_headers(profile),
        )
        with self.assertRaisesRegex(
            npa1.NeuralPayloadAdmissionRefusal, npa1.REFUSAL_IDS["capability"]
        ):
            npa1.admit_generated_transport(
                profile=profile,
                capability=npa1.TransportCapability(url, npa1.ALLOWED_HOSTS, 0),
                opener=npa1.FixtureOpener((exchange,), metrics),
                resolver=npa1.FixtureResolver(),
                metrics=metrics,
            )
        self.assertEqual(metrics.response_opens, 0)

    def test_report_validation_refuses_counter_and_output_drift(self) -> None:
        report = npa1.run_generated_qualification(
            ROOT,
            environ=ONE_THREAD_ENV,
            clock=iter((2.0, 2.1)).__next__,
            rss_reader=lambda: 24_000_000,
        )
        changed = copy.deepcopy(report)
        changed["operation_counters"]["network_requests"] = 1
        with self.assertRaisesRegex(
            npa1.NeuralPayloadAdmissionRefusal, "forbidden operation counter"
        ):
            npa1.validate_public_report(changed)

        mutations = []
        empty_counters = copy.deepcopy(report)
        empty_counters["operation_counters"] = {}
        mutations.append(empty_counters)
        over_rss = copy.deepcopy(report)
        over_rss["measurements"]["peak_RSS_bytes"] = npa1.MAX_PEAK_RSS_BYTES + 1
        mutations.append(over_rss)
        frontier_drift = copy.deepcopy(report)
        frontier_drift["green_frontier"]["commit"] = "0" * 40
        mutations.append(frontier_drift)
        claim_drift = copy.deepcopy(report)
        claim_drift["claim_boundary"]["scientific_claim_not_established"] = "changed"
        mutations.append(claim_drift)
        transcript_drift = copy.deepcopy(report)
        transcript_drift["qualification"]["stable_transcript_sha256"] = "0" * 64
        mutations.append(transcript_drift)
        route_drift = copy.deepcopy(report)
        first_route = route_drift["qualification"]["refusals"][0]["refusal_id"]
        sixth_route = route_drift["qualification"]["refusals"][5]["refusal_id"]
        route_drift["qualification"]["refusals"][0]["refusal_id"] = sixth_route
        route_drift["qualification"]["refusals"][5]["refusal_id"] = first_route
        mutations.append(route_drift)
        count_drift = copy.deepcopy(report)
        count_drift["measurements"]["body_reads"] += 1
        mutations.append(count_drift)
        oversized = copy.deepcopy(report)
        oversized["warnings"].append("x" * npa1.MAX_REPORT_BYTES)
        mutations.append(oversized)
        for mutation in mutations:
            with self.assertRaisesRegex(
                npa1.NeuralPayloadAdmissionRefusal,
                npa1.REFUSAL_IDS["output"],
            ):
                npa1.validate_public_report(mutation)

    def test_resource_and_thread_caps_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            npa1.NeuralPayloadAdmissionRefusal, "thread environment"
        ):
            npa1.run_generated_qualification(
                ROOT,
                environ={**ONE_THREAD_ENV, "OMP_NUM_THREADS": "2"},
            )
        with self.assertRaisesRegex(npa1.NeuralPayloadAdmissionRefusal, "runtime cap"):
            npa1.run_generated_qualification(
                ROOT,
                environ=ONE_THREAD_ENV,
                clock=iter((0.0, 31.0)).__next__,
                rss_reader=lambda: 24_000_000,
            )
        with self.assertRaisesRegex(npa1.NeuralPayloadAdmissionRefusal, "RSS cap"):
            npa1.run_generated_qualification(
                ROOT,
                environ=ONE_THREAD_ENV,
                clock=iter((0.0, 0.1)).__next__,
                rss_reader=lambda: npa1.MAX_PEAK_RSS_BYTES + 1,
            )

    def test_public_report_contains_no_ephemeral_transport_or_protected_fields(self) -> None:
        report = npa1.run_generated_qualification(
            ROOT,
            environ=ONE_THREAD_ENV,
            clock=iter((0.0, 0.1)).__next__,
            rss_reader=lambda: 24_000_000,
        )

        def walk(value: object) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(
                        key.casefold(),
                        {"url", "path", "query", "signature", "raw_headers"},
                    )
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
            elif isinstance(value, str):
                self.assertFalse(value.startswith("https://"))

        walk(report)
        text = json.dumps(report).casefold()
        for forbidden in ("participant", "target", "label", "reference_text"):
            self.assertNotIn(forbidden, text)

    def test_module_has_no_live_client_or_heavy_dependency(self) -> None:
        source = (ROOT / "src/neurodecodekit/datasets/neural_payload_admission.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "urllib.request",
            "urlopen",
            "requests.",
            "import mne",
            "import numpy",
            "import scipy",
        ):
            self.assertNotIn(forbidden, source)

    def test_socket_guard_is_never_reached(self) -> None:
        with patch("socket.socket", side_effect=AssertionError("network attempted")), patch(
            "socket.getaddrinfo", side_effect=AssertionError("DNS attempted")
        ):
            report = npa1.run_generated_qualification(
                ROOT,
                environ=ONE_THREAD_ENV,
                clock=iter((0.0, 0.1)).__next__,
                rss_reader=lambda: 24_000_000,
            )
        self.assertEqual(report["operation_counters"]["network_requests"], 0)

    def test_cli_help_has_no_execute_and_generated_roundtrip_passes(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        for key in npa1.THREAD_ENV_KEYS:
            environment[key] = "1"
        help_result = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.npa1_cli", "--help"],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("qualify-generated", help_result.stdout)
        self.assertNotIn("execute-real", help_result.stdout)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.npa1_cli",
                "qualify-generated",
                "--repo-root",
                str(ROOT),
            ],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "accepted_generated_only_zero_network")
        self.assertTrue(report["qualification"]["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
