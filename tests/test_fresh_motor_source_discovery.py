from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import fresh_motor_source_discovery as discovery

ROOT = Path(__file__).resolve().parents[1]


class FreshMotorSourceDiscoveryTests(unittest.TestCase):
    def test_green_decision_and_exact_plan(self) -> None:
        decision = discovery.load_green_decision(ROOT)
        self.assertEqual(decision["decision_id"], "FMSR1-DISCOVERY-M0-D0")
        plan = discovery.build_plan()
        self.assertEqual(len(plan), 17)
        self.assertEqual([row.index_id for row in plan[:4]], ["OPENNEURO"] * 4)
        self.assertEqual([row.method for row in plan[:4]], ["POST"] * 4)
        self.assertTrue(all(row.body is not None for row in plan[:4]))
        self.assertEqual(plan[-1].index_id, "BNCI_HORIZON_2020")
        self.assertEqual(plan[-1].query_or_category_id, "complete_motor_EEG_category")
        self.assertEqual(plan[-1].method, "GET")
        self.assertIsNone(plan[-1].body)
        registered = discovery.registered_plan(ROOT)
        self.assertEqual(registered["root_request_count"], 17)
        self.assertFalse(registered["network_authorized_before_implementation_remote_green"])
        self.assertFalse(registered["payload_model_score_or_claim_authority"])

    def test_candidate_identity_is_nfkc_normalized_and_ascii_trimmed(self) -> None:
        observed = discovery.canonical_candidate_id(
            " OPENNEURO\t", "\uff24\uff33\uff10\uff10\uff11 ", " v1\r\n"
        )
        self.assertEqual(observed, "OPENNEURO::DS001::v1")
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery.canonical_candidate_id("OPENNEURO", " ", "v1")
        self.assertEqual(caught.exception.route, "MALFORMED_RESPONSE_REFUSE")

    def test_exact_candidate_predicate_is_noncompensatory(self) -> None:
        candidate = discovery._fixture_candidate()
        candidate.update(
            {
                "official_index_id": "OPENNEURO",
                "packet_bound_index_revision": discovery.INDEX_SPECS[0].profile_revision,
                "query_or_category_id": "query_1",
                "pagination_identity": "page-1",
                "ordered_redirect_transcript": [],
                "canonical_candidate_id": "OPENNEURO::FMSR1-GENERATED-001::generated-v1",
            }
        )
        route, reasons = discovery.evaluate_candidate(candidate)
        self.assertEqual(route, discovery.SUCCESS_ROUTE)
        self.assertEqual(reasons, [])
        candidate["declared_sensor_modalities_and_roles"] = [
            "raw_synchronized_EEG",
            "recorded_EOG",
        ]
        route, reasons = discovery.evaluate_candidate(candidate)
        self.assertEqual(route, "PARK")
        self.assertIn("task_relevant_EMG_for_every_named_effector_explicit", reasons)

    def test_complete_generated_surface_routes_exactly_one_candidate(self) -> None:
        report = discovery._run_success_fixture()
        self.assertEqual(report["route"], discovery.SUCCESS_ROUTE)
        self.assertEqual(report["traversal"]["official_indexes_complete"], 5)
        self.assertEqual(report["traversal"]["root_requests_complete"], 17)
        self.assertEqual(report["traversal"]["pages_complete"], 17)
        self.assertEqual(len(report["routing"]["selected_candidates"]), 1)
        self.assertEqual(report["operation_ledger"]["mock_HTTP_calls"], 17)
        self.assertEqual(report["operation_ledger"]["real_network_requests"], 0)
        self.assertLessEqual(
            report["measurements"]["retained_public_report_bytes"],
            discovery.MAX_RETAINED_BYTES,
        )
        self.assertFalse(any(report["claim_boundary"].values()))

    def test_generated_qualification_is_deterministic_and_target_free(self) -> None:
        with (
            mock.patch.object(
                discovery.socket,
                "getaddrinfo",
                side_effect=AssertionError("real DNS must not be reached"),
            ),
            mock.patch.object(
                discovery.urllib.request,
                "build_opener",
                side_effect=AssertionError("real HTTP must not be reached"),
            ),
        ):
            result = discovery.run_generated_qualification(ROOT)
        self.assertEqual(
            result["status"], "passed_generated_only_two_replay_qualification"
        )
        self.assertEqual(result["replay_count"], 2)
        self.assertEqual(result["mock_HTTP_calls_across_success_replays"], 34)
        self.assertTrue(result["refusal_matrix"]["all_passed"])
        self.assertGreaterEqual(result["refusal_matrix"]["case_count"], 21)
        self.assertEqual(result["operation_counters"]["real_network_requests"], 0)
        self.assertEqual(
            result["operation_counters"][
                "signal_event_annotation_target_or_label_reads"
            ],
            0,
        )
        self.assertFalse(any(result["claim_boundary"].values()))

    def test_valid_pagination_completes_but_ambiguity_parks(self) -> None:
        report = discovery._run_nemar_pagination_mutation(duplicate_identity=False)
        self.assertEqual(report["route"], discovery.NO_SOURCE_ROUTE)
        self.assertEqual(report["traversal"]["pages_complete"], 18)
        planned = discovery.build_plan()[0]
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery._run_first_page_mutation(b'{"results":[]}\n')
        self.assertEqual(caught.exception.route, discovery.CAP_PARK_ROUTE)
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery._run_first_page_mutation(
                discovery._fixture_page_bytes(
                    planned,
                    next_url="https://openneuro.org/download/payload",
                )
            )
        self.assertEqual(caught.exception.route, "OFF_ALLOWLIST_REDIRECT_REFUSE")

    def test_target_like_and_unknown_fields_refuse(self) -> None:
        planned = discovery.build_plan()[0]
        for field in (
            "target",
            "targets",
            "\uff34\uff21\uff32\uff27\uff25\uff34",
            "download_url",
            "convenience_metric",
        ):
            with self.subTest(field=field):
                candidate = discovery._fixture_candidate()
                candidate[field] = "forbidden"
                body = discovery._fixture_page_bytes(planned, candidates=(candidate,))
                with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
                    discovery._run_first_page_mutation(body)
                self.assertEqual(caught.exception.route, "RETAINED_FIELD_REFUSE")

    def test_all_consumed_source_aliases_are_excluded(self) -> None:
        aliases = (
            ("NEMAR", "nm000139", "historical BNCI source"),
            ("NEMAR", "nm000250", "historical Dreyer source"),
            ("NEMAR", "nm000173", "historical Ofner source"),
            ("OPENNEURO", "ds006840", "historical IACKD source"),
            ("BNCI_HORIZON_2020", "001-2014", "BNCI 2014-001"),
            ("PHYSIONET", "EEGMMIDB", "PhysioNet EEGMMIDB"),
            ("OPENNEURO", "SPANISHBCBL-S21", "SpanishBCBL S21"),
        )
        for index_id, source_id, title in aliases:
            with self.subTest(source_id=source_id):
                candidate = discovery._fixture_candidate(source_id=source_id)
                candidate.update(
                    {
                        "official_index_id": index_id,
                        "official_title": title,
                        "packet_bound_index_revision": "generated",
                        "query_or_category_id": "query_1",
                        "pagination_identity": "page-1",
                        "ordered_redirect_transcript": [],
                    }
                )
                routed = discovery.route_candidates(
                    [candidate], ledger=discovery.AccessLedger()
                )
                self.assertEqual(routed["route"], discovery.NO_SOURCE_ROUTE)
                self.assertIn(
                    "source_not_in_excluded_consumed_source_ids",
                    routed["routed_candidates"][0]["exclusion_reason"],
                )
        for source_id in discovery.EXCLUDED_SOURCE_IDS:
            with self.subTest(contract_source_id=source_id):
                candidate = discovery._fixture_candidate(source_id=source_id)
                candidate.update(
                    {
                        "official_index_id": "OPENNEURO",
                        "packet_bound_index_revision": "generated",
                        "query_or_category_id": "query_1",
                        "pagination_identity": "page-1",
                        "ordered_redirect_transcript": [],
                    }
                )
                routed = discovery.route_candidates(
                    [candidate], ledger=discovery.AccessLedger()
                )
                self.assertEqual(routed["route"], discovery.NO_SOURCE_ROUTE)

    def test_identity_normalization_merge_and_conflict_rules(self) -> None:
        context = {
            "official_index_id": "OPENNEURO",
            "packet_bound_index_revision": "generated",
            "query_or_category_id": "query_1",
            "pagination_identity": "page-1",
            "ordered_redirect_transcript": [],
        }
        first = {**discovery._fixture_candidate(source_id="\uff24\uff33\uff10\uff10\uff11"), **context}
        second = {**discovery._fixture_candidate(source_id="DS001"), **context}
        routed = discovery.route_candidates([first, second], ledger=discovery.AccessLedger())
        self.assertEqual(routed["canonical_candidates"], 1)
        conflicting = dict(second)
        conflicting["canonical_candidate_id"] = "OPENNEURO::OTHER::generated-v1"
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery.route_candidates([conflicting], ledger=discovery.AccessLedger())
        self.assertEqual(caught.exception.route, "MALFORMED_RESPONSE_REFUSE")
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal):
            discovery.canonical_candidate_id("OPENNEURO", "bad::id", "v1")

    def test_public_mapping_preserves_explicit_allowlisted_evidence(self) -> None:
        planned = discovery.build_plan()[0]
        raw = discovery._fixture_candidate(source_id="PUBLIC-001")
        transport = {
            "packet_bound_index_revision": discovery.INDEX_SPECS[0].profile_revision,
            "ordered_redirect_transcript": (),
        }
        candidate = discovery._candidate_from_public_mapping(
            raw,
            planned=planned,
            transport=transport,
            pagination_identity="public-page-1",
        )
        routed = discovery.route_candidates([candidate], ledger=discovery.AccessLedger())
        self.assertEqual(routed["route"], discovery.SUCCESS_ROUTE)
        self.assertEqual(len(routed["selected_candidates"]), 1)

    def test_nested_payload_surfaces_and_payload_landing_urls_refuse(self) -> None:
        context = {
            "official_index_id": "OPENNEURO",
            "packet_bound_index_revision": "generated",
            "query_or_category_id": "query_1",
            "pagination_identity": "page-1",
            "ordered_redirect_transcript": [],
        }
        nested = {**discovery._fixture_candidate(), **context}
        nested["source_field_provenance"] = dict(nested["source_field_provenance"])
        nested["source_field_provenance"]["download_url"] = "https://example.org/file.edf"
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery.route_candidates([nested], ledger=discovery.AccessLedger())
        self.assertEqual(caught.exception.route, "RETAINED_FIELD_REFUSE")
        landing = {**discovery._fixture_candidate(), **context}
        landing["official_landing_URL"] = "https://openneuro.org/download/file.edf"
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery.route_candidates([landing], ledger=discovery.AccessLedger())
        self.assertEqual(caught.exception.route, "RETAINED_FIELD_REFUSE")

    def test_generated_envelope_and_injected_transport_cannot_be_live(self) -> None:
        planned = discovery.build_plan()[0]
        body = discovery._fixture_page_bytes(planned)
        transport = {
            "content_type": "application/json",
            "packet_bound_index_revision": discovery.INDEX_SPECS[0].profile_revision,
            "ordered_redirect_transcript": (),
            "body_sha256": discovery._sha256(body),
        }
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery.parse_page(
                body,
                planned=planned,
                transport=transport,
                ledger=discovery.AccessLedger(),
                allow_fixture_envelope=False,
            )
        self.assertEqual(caught.exception.route, "MALFORMED_RESPONSE_REFUSE")
        opener = discovery.FixtureOpener(
            discovery.build_success_fixture_exchanges()
        )
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery._run_discovery(
                opener=opener,
                resolver=discovery._mock_resolver,
                execution_mode="real_public_metadata",
            )
        self.assertEqual(caught.exception.route, "AUTHORITY_REFUSE")

        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery.fetch_page(
                planned,
                opener=opener,
                resolver=discovery.socket.getaddrinfo,
                ledger=discovery.AccessLedger(),
            )
        self.assertEqual(caught.exception.route, "AUTHORITY_REFUSE")

    def test_exact_endpoint_and_deadline_firewalls(self) -> None:
        spec = discovery.INDEX_SPECS[0]
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery._canonical_url("https://openneuro.org/file.edf", spec=spec)
        self.assertEqual(caught.exception.route, "OFF_ALLOWLIST_REDIRECT_REFUSE")
        planned = discovery.build_plan()[0]
        response = discovery._fixture_response(
            planned, discovery._fixture_page_bytes(planned)
        )
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery._read_response_body(
                response,
                ledger=discovery.AccessLedger(),
                deadline=0.0,
            )
        self.assertEqual(caught.exception.route, "RESOURCE_CAP_REFUSE")

    def test_request_deadline_covers_the_complete_body_read(self) -> None:
        planned = discovery.build_plan()[0]
        body = discovery._fixture_page_bytes(planned)
        response = discovery._fixture_response(planned, body)
        opener = discovery.FixtureOpener(
            (
                discovery.FixtureExchange(
                    planned.method, planned.url, planned.body, response
                ),
            )
        )
        with (
            mock.patch.object(
                discovery.time,
                "monotonic",
                side_effect=(0.0, 0.0, 0.0, discovery.MAX_TIMEOUT_SECONDS + 1.0),
            ),
            self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught,
        ):
            discovery.fetch_page(
                planned,
                opener=opener,
                resolver=discovery._mock_resolver,
                ledger=discovery.AccessLedger(),
            )
        self.assertEqual(caught.exception.route, "RESOURCE_CAP_REFUSE")

    def test_generated_revision_must_match_the_registered_profile(self) -> None:
        planned = discovery.build_plan()[0]
        body = discovery._fixture_page_bytes(planned)
        response = discovery.FixtureResponse(
            body,
            url=planned.url,
            headers=(
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(body))),
                ("X-FMSR1-Index-Revision", "different-revision"),
            ),
        )
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery._fetch_first_fixture(response)
        self.assertEqual(caught.exception.route, "MALFORMED_RESPONSE_REFUSE")

    def test_stream_reader_stops_at_cap_plus_one(self) -> None:
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery._stream_cap_plus_one_observation()
        self.assertEqual(caught.exception.route, "RESPONSE_CAP_REFUSE")

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_values(self) -> None:
        for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b"\xef\xbb\xbf{}"):
            with (
                self.subTest(payload=payload),
                self.assertRaises((ValueError, json.JSONDecodeError)),
            ):
                discovery._strict_json(payload)

    def test_public_address_firewall_rejects_every_non_global_resolution(self) -> None:
        for address in ("127.0.0.1", "100.64.0.1", "192.0.2.1", "224.0.0.1"):
            with self.subTest(address=address):
                def non_global_resolver(
                    *_args: object,
                    selected_address: str = address,
                    **_kwargs: object,
                ) -> list[object]:
                    return [(2, 1, 6, "", (selected_address, 443))]

                with self.assertRaises(
                    discovery.FreshMotorDiscoveryRefusal
                ) as caught:
                    discovery._validate_public_resolution(
                        "openneuro.org", non_global_resolver
                    )
                self.assertEqual(
                    caught.exception.route, "OFF_ALLOWLIST_REDIRECT_REFUSE"
                )

    def test_unsupported_content_type_body_still_counts(self) -> None:
        planned = discovery.build_plan()[0]
        body = b"x" * 4096
        response = discovery.FixtureResponse(
            body,
            url=planned.url,
            headers=(
                ("Content-Type", "application/octet-stream"),
                ("Content-Length", str(len(body))),
                (
                    "X-FMSR1-Index-Revision",
                    discovery.INDEX_SPECS[0].profile_revision,
                ),
            ),
        )
        opener = discovery.FixtureOpener(
            (
                discovery.FixtureExchange(
                    planned.method, planned.url, planned.body, response
                ),
            )
        )
        ledger = discovery.AccessLedger()
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery.fetch_page(
                planned,
                opener=opener,
                resolver=discovery._mock_resolver,
                ledger=ledger,
            )
        self.assertEqual(caught.exception.route, "MALFORMED_RESPONSE_REFUSE")
        self.assertEqual(ledger.values["wire_body_bytes"], len(body))
        self.assertEqual(ledger.values["decoded_body_bytes"], len(body))

    def test_json_ld_without_explicit_result_and_terminal_surfaces_parks(self) -> None:
        planned = discovery.build_plan()[4]
        body = (
            b'<script type="application/ld+json">'
            b'{"@type":"Dataset","identifier":"fresh","name":"Fresh"}'
            b"</script>"
        )
        transport = {
            "packet_bound_index_revision": discovery.INDEX_SPECS[1].profile_revision,
            "ordered_redirect_transcript": (),
            "body_sha256": discovery._sha256(body),
        }
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery._parse_html_page(
                body, planned=planned, transport=transport
            )
        self.assertEqual(caught.exception.route, discovery.CAP_PARK_ROUTE)

    def test_output_cap_refuses_before_publication(self) -> None:
        report = {
            "measurements": {"retained_public_report_bytes": 0},
            "large": "x" * 256,
        }
        with (
            mock.patch.object(discovery, "MAX_RETAINED_BYTES", 64),
            self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught,
        ):
            discovery._bounded_report(report)
        self.assertEqual(caught.exception.route, "RESOURCE_CAP_REFUSE")

    def test_live_execution_is_not_armable_under_current_packet(self) -> None:
        evidence = discovery.GreenImplementationEvidence(
            implementation_commit="0" * 40,
            implementation_registry_sha256="0" * 64,
            implementation_proof_commit="0" * 40,
            implementation_proof_sha256="0" * 64,
            CI_run_id=1,
            base_python_job_id=1,
            optional_neuro_readers_job_id=1,
        )
        with self.assertRaises(discovery.FreshMotorDiscoveryRefusal) as caught:
            discovery.execute_registered_discovery(evidence, repo_root=ROOT)
        self.assertEqual(caught.exception.route, "AUTHORITY_REFUSE")
        self.assertIn("official index revisions", caught.exception.safe_reason)
        self.assertTrue(
            all(
                spec.packet_bound_official_revision is None
                for spec in discovery.INDEX_SPECS
            )
        )

    def test_cli_help_is_available_without_network(self) -> None:
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT / "src")
        result = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.fmsr1_discovery_cli", "--help"],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("qualify-generated", result.stdout)
        self.assertIn("execute", result.stdout)


if __name__ == "__main__":
    unittest.main()
