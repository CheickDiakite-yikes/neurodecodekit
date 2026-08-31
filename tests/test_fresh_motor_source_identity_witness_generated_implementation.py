from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import fresh_motor_source_identity_witness as witness

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/neurodecodekit/datasets/fresh_motor_source_identity_witness.py"
PACKET = (
    ROOT
    / "registries/fresh_motor_source_identity_witness_authorization_request.v0.json"
)
DECISION = (
    ROOT
    / "registries/fresh_motor_source_identity_witness_implementation_decision.v0.json"
)


class FreshMotorSourceIdentityWitnessGeneratedImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = witness.load_packet(ROOT)
        cls.decision = witness.load_green_decision(ROOT)
        cls.roots = witness.build_root_plan(ROOT)
        cls.fixture = witness.build_generated_fixture(ROOT)
        cls.ledger = witness.run_generated_replay(ROOT, fixture=cls.fixture)

    def assert_refusal(self, route: str, operation: object) -> None:
        with self.assertRaises(witness.WitnessRefusal) as raised:
            operation()  # type: ignore[operator]
        self.assertEqual(raised.exception.route, route)

    def test_exact_green_decision_and_packet_bytes_are_bound(self) -> None:
        packet_bytes = PACKET.read_bytes()
        decision_bytes = DECISION.read_bytes()
        self.assertEqual(len(packet_bytes), witness.PACKET_BYTES)
        self.assertEqual(hashlib.sha256(packet_bytes).hexdigest(), witness.PACKET_SHA256)
        self.assertEqual(len(decision_bytes), witness.DECISION_BYTES)
        self.assertEqual(
            hashlib.sha256(decision_bytes).hexdigest(), witness.DECISION_SHA256
        )
        self.assertEqual(self.packet["packet_id"], witness.PACKET_ID)
        self.assertEqual(self.decision["decision_id"], "FMSR1-R1-W-I0-D0")
        self.assertEqual(
            witness.GREEN_DECISION_COMMIT,
            "e158e8cef2bc0267e5161e947b35409081ea37d7",
        )

    def test_exact_five_profile_seventeen_root_plan_is_replayed(self) -> None:
        self.assertEqual(len(self.roots), 17)
        counts = {
            profile: sum(witness._profile_id(root.index_id) == profile for root in self.roots)
            for profile in witness.PROFILE_ORDER
        }
        self.assertEqual(list(counts), list(witness.PROFILE_ORDER))
        self.assertEqual(list(counts.values()), [4, 4, 4, 4, 1])
        frozen = self.packet["frozen_discovery_plan"]["root_request_identities"]
        for root, row in zip(self.roots, frozen, strict=True):
            self.assertEqual(root.root_ordinal, frozen.index(row))
            self.assertEqual(root.index_id, row["index_id"])
            self.assertEqual(root.query_or_category_id, row["query_or_category_id"])
            self.assertEqual(root.method, row["method"])
            self.assertEqual(root.url, row["url"])
            self.assertEqual(hashlib.sha256(root.body).hexdigest(), row["body_sha256"])

    def test_openneuro_root_and_continuation_bytes_are_distinct_and_exact(self) -> None:
        root = self.roots[0]
        self.assertTrue(root.body.endswith(b"\n"))
        media_type, payload = witness._generated_response(root, 0)
        next_url, next_body, control = witness._parse_control(
            self.packet,
            root,
            root.url,
            root.body,
            media_type,
            payload,
        )
        self.assertEqual(next_url, root.url)
        self.assertIsNotNone(next_body)
        self.assertFalse(next_body.endswith(b"\n"))  # type: ignore[union-attr]
        root_value = witness.strict_json_loads(root.body)
        next_value = witness.strict_json_loads(next_body)  # type: ignore[arg-type]
        self.assertIsNone(root_value["variables"]["after"])  # type: ignore[index]
        self.assertEqual(next_value["variables"]["after"], "cursor-0")  # type: ignore[index]
        root_value["variables"]["after"] = "cursor-0"  # type: ignore[index]
        self.assertEqual(root_value, next_value)
        self.assertEqual(control["variant"], "OPENNEURO_CONTINUE")

    def test_two_replays_are_byte_identical_and_structurally_complete(self) -> None:
        second = witness.run_generated_replay(ROOT, fixture=self.fixture)
        self.assertEqual(
            witness.canonical_json_bytes(self.ledger, newline=True),
            witness.canonical_json_bytes(second, newline=True),
        )
        self.assertEqual(self.ledger["total_root_count"], 17)
        self.assertEqual(self.ledger["total_page_count"], 34)
        self.assertEqual(len(self.ledger["global_root_sha256_values"]), 17)
        self.assertEqual(len(self.ledger["profile_sha256_values"]), 5)
        for profile in self.ledger["profiles"]:
            self.assertTrue(profile["complete"])
            for root in profile["roots"]:
                self.assertEqual(root["terminal_page_count"], 1)
                self.assertEqual(root["pages"][-1]["terminal_state"], "TERMINAL")
                self.assertIsNone(root["pages"][-1]["next_request_identity_sha256"])

    def test_candidate_poison_is_hashed_but_never_retained(self) -> None:
        fixture_bytes = b"".join(
            exchange.response_body for exchange in self.fixture["exchanges"]
        )
        self.assertIn(b"REFERENCE_TARGET_DO_NOT_RETAIN", fixture_bytes)
        public_bytes = witness.canonical_json_bytes(self.ledger, newline=True)
        self.assertNotIn(b"REFERENCE_TARGET_DO_NOT_RETAIN", public_bytes)
        self.assertNotIn(b"reference_text", public_bytes)
        self.assertNotIn(b'"target"', public_bytes)
        self.assertGreater(self.ledger["total_entity_body_bytes"], 0)

    def test_candidate_pagination_decoys_do_not_control_JSON_routing(self) -> None:
        terminal, control = witness.extract_generic_json_control(
            b'{"items":[{"next":"https://evil.invalid/"}],'
            b'"pagination":{"has_next":false}}'
        )
        self.assertIsNone(terminal)
        self.assertEqual(control["variant"], "PAGINATION_HAS_NEXT_FALSE")
        next_url, control = witness.extract_generic_json_control(
            b'{"items":[{"pagination":{"has_next":false}}],'
            b'"pagination":{"next":"/search?q=x&page=2"}}'
        )
        self.assertEqual(next_url, "/search?q=x&page=2")
        self.assertEqual(control["variant"], "PAGINATION_NEXT")

    def test_all_registered_JSON_and_HTML_control_variants_are_typed(self) -> None:
        cases = (
            (b'{"rows":[],"next":"/next"}', "/next", "TOP_LEVEL_NEXT"),
            (
                b'{"pagination":{"next":"/next"},"rows":[]}',
                "/next",
                "PAGINATION_NEXT",
            ),
            (
                b'{"pagination":{"has_next":false},"rows":[]}',
                None,
                "PAGINATION_HAS_NEXT_FALSE",
            ),
        )
        for payload, expected, variant in cases:
            value, control = witness.extract_generic_json_control(payload)
            self.assertEqual(value, expected)
            self.assertEqual(control["variant"], variant)
        value, control = witness.extract_generic_html_control(
            b'<div data-next="/fake"></div><nav aria-label="pagination">'
            b'<a rel="next" href="/next">next</a></nav>'
        )
        self.assertEqual(value, "/next")
        self.assertEqual(control["variant"], "HTML_NEXT")
        value, control = witness.extract_generic_html_control(
            b'<nav aria-label="pagination"><a rel="next" '
            b'aria-disabled="true">next</a></nav>'
        )
        self.assertIsNone(value)
        self.assertEqual(control["variant"], "HTML_TERMINAL")

    def test_ambiguous_pagination_and_noncanonical_URLs_refuse(self) -> None:
        self.assert_refusal(
            "PAGINATION_REFUSE",
            lambda: witness.extract_generic_json_control(
                b'{"next":null,"pagination":{"has_next":false}}'
            ),
        )
        self.assert_refusal(
            "PAGINATION_REFUSE",
            lambda: witness.extract_openneuro_control(
                b'{"data":{"datasets":{"pageInfo":'
                b'{"hasNextPage":true,"endCursor":null}}}}'
            ),
        )
        root = self.roots[4]
        valid = witness._next_url(root)
        self.assertEqual(
            witness.canonicalize_continuation_url(
                self.packet, root, root.url, valid
            ),
            valid,
        )
        invalid = (
            valid.replace("https://nemar.org", "https://n\u00e9mar.org"),
            valid.replace("https://nemar.org", "https://nemar.org:443"),
            valid + "#fragment",
            valid + "&page=3",
            valid + "&offset=1",
        )
        for value in invalid:
            self.assert_refusal(
                "URL_REFUSE",
                lambda value=value: witness.canonicalize_continuation_url(
                    self.packet, root, root.url, value
                ),
            )

    def test_hash_tree_rejects_omission_reordering_and_substitution(self) -> None:
        mutations = []
        missing = copy.deepcopy(self.ledger)
        missing["profiles"][0]["roots"].pop()
        mutations.append(missing)
        reordered = copy.deepcopy(self.ledger)
        reordered["profiles"].reverse()
        mutations.append(reordered)
        substituted = copy.deepcopy(self.ledger)
        substituted["global_root_sha256_values"][0] = "0" * 64
        mutations.append(substituted)
        incomplete = copy.deepcopy(self.ledger)
        incomplete["profiles"][0]["roots"][0]["complete"] = False
        mutations.append(incomplete)
        for value in mutations:
            self.assert_refusal(
                "HASH_TREE_REFUSE",
                lambda value=value: witness.validate_ledger(self.packet, value),
            )

    def test_CI_fixture_binds_exact_two_green_jobs_and_workflow_blob(self) -> None:
        fixture = witness.build_generated_CI_fixture(ROOT)
        receipt = witness.validate_generated_CI_fixture(self.packet, fixture)
        self.assertEqual(receipt["Base_Python_check_run_id"], 101)
        self.assertEqual(receipt["Optional_Neuro_Readers_check_run_id"], 102)
        bad = dict(fixture)
        checks = json.loads(bad["check_runs"])
        checks["total_count"] = 3
        checks["check_runs"].append(copy.deepcopy(checks["check_runs"][0]))
        bad["check_runs"] = witness.canonical_json_bytes(checks)
        self.assert_refusal(
            "CI_REFUSE",
            lambda: witness.validate_generated_CI_fixture(self.packet, bad),
        )

    def test_refusal_matrix_and_output_caps_are_fail_closed(self) -> None:
        refusals = witness.run_refusal_matrix(ROOT, baseline_ledger=self.ledger)
        self.assertEqual(len(refusals), 22)
        self.assertEqual(len({row["name"] for row in refusals}), 22)
        oversized = {
            "route": "GENERATED_WITNESS_QUALIFIED",
            "operation_counters": {
                name: 0
                for name in (
                    "network_requests",
                    "network_bytes",
                    "official_index_requests",
                    "candidate_semantic_operations",
                    "source_selections",
                    "payload_or_neural_reads",
                    "target_or_label_reads",
                    "model_runs",
                    "training_runs",
                    "prediction_sets",
                    "scoring_events",
                    "scientific_claim_upgrades",
                )
            },
            "claim_boundary": witness.CLAIM_BOUNDARY,
            "warnings": ["x" * witness.MAX_REPORT_BYTES],
        }
        self.assert_refusal(
            "OUTPUT_REFUSE", lambda: witness.validate_public_report(oversized)
        )

    def test_one_thread_requirement_and_resource_constants_are_exact(self) -> None:
        valid = {key: "1" for key in witness.THREAD_ENV_KEYS}
        witness._validate_thread_environment(valid)
        invalid = dict(valid)
        invalid[witness.THREAD_ENV_KEYS[0]] = "2"
        self.assert_refusal(
            "RESOURCE_REFUSE",
            lambda: witness._validate_thread_environment(invalid),
        )
        self.assertEqual(witness.MAX_PEAK_RSS_BYTES, 256 * 1024**2)
        self.assertEqual(witness.MAX_GENERATED_INPUT_BYTES, 4 * 1024**2)
        self.assertEqual(witness.MAX_REPORT_BYTES, 1024**2)

    def test_module_has_no_network_or_process_capability(self) -> None:
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        forbidden = {
            "socket",
            "ssl",
            "http.client",
            "urllib.request",
            "subprocess",
            "requests",
            "httpx",
        }
        self.assertTrue(imported.isdisjoint(forbidden), imported & forbidden)
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("fresh_motor_source_discovery import", source)
        self.assertNotIn("urlopen(", source)
        self.assertNotIn("create_connection(", source)

    def test_runtime_network_traps_remain_untouched(self) -> None:
        with (
            mock.patch("socket.socket", side_effect=AssertionError("network")) as socket_mock,
            mock.patch(
                "urllib.request.urlopen", side_effect=AssertionError("network")
            ) as urlopen_mock,
        ):
            replay = witness.run_generated_replay(ROOT, fixture=self.fixture)
        socket_mock.assert_not_called()
        urlopen_mock.assert_not_called()
        self.assertEqual(
            replay["canonical_global_ledger_sha256"],
            self.ledger["canonical_global_ledger_sha256"],
        )

    def test_public_plan_states_the_exact_nonclaim(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            plan = witness.registered_plan(ROOT)
        self.assertEqual(plan["official_index_profiles"], 5)
        self.assertEqual(plan["root_request_count"], 17)
        self.assertFalse(plan["network_authorized"])
        self.assertFalse(plan["scientific_claim_established"])
        self.assertFalse(plan["live_or_execute_command_present"])


if __name__ == "__main__":
    unittest.main()
