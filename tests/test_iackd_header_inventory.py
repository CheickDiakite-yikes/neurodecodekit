import copy
import hashlib
import io
import json
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.preprocess import iackd_header_inventory as inventory_audit
from neurodecodekit.preprocess.iackd_header_inventory import (
    CANONICAL_GATE_NAMES,
    CONTRACT_SHA256,
    FixtureResponse,
    HeaderAuditRefusal,
    PUBLIC_NAME_ALLOWLIST,
    REFUSAL_IDS,
    _assert_forbidden_counters_zero,
    _assert_rooted_output_path,
    _base_access_counters,
    build_channel_signature,
    fixture_opener,
    load_public_ledger,
    load_registered_contract,
    load_registered_inventory,
    main,
    make_synthetic_vhdr,
    parse_vhdr_bytes,
    registered_header_rows,
    registered_plan,
    route_signatures,
    run_header_audit,
    run_synthetic_qualification,
    summarize_public_ledger,
    validate_public_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}
CANONICAL_NAMES = [f"EEG{index:02d}" for index in range(1, 33)] + list(
    CANONICAL_GATE_NAMES
)


def replace_bytes(payload, old, new):
    changed = payload.replace(old, new)
    if changed == payload:
        raise AssertionError(f"fixture mutation did not match {old!r}")
    return changed


class IACKDHeaderParserTests(unittest.TestCase):
    def parse(self, payload=None):
        return parse_vhdr_bytes(payload or make_synthetic_vhdr(CANONICAL_NAMES))

    def assert_refusal(self, refusal_id, payload):
        with self.assertRaises(HeaderAuditRefusal) as raised:
            self.parse(payload)
        self.assertEqual(raised.exception.refusal_id, refusal_id)
        self.assertNotIn("must_not_escape", str(raised.exception))

    def test_exact_header_parses_without_sibling_resolution(self):
        parsed = self.parse()
        self.assertEqual(parsed["declared_channel_count"], 36)
        self.assertEqual(parsed["sampling_interval_microseconds"], "976.5625")
        self.assertEqual(parsed["sampling_rate_hz"], "1024")
        self.assertEqual(parsed["normalized_channel_names"][-4:], list(CANONICAL_GATE_NAMES))
        self.assertNotIn("DataFile", parsed)
        self.assertNotIn("MarkerFile", parsed)

    def test_utf8_bom_declared_cp1252_and_implicit_utf8_are_strict(self):
        bom = self.parse(
            make_synthetic_vhdr(CANONICAL_NAMES, codepage=None, include_bom=True)
        )
        cp1252_names = [*CANONICAL_NAMES[:-1], "V\N{LATIN SMALL LETTER E WITH ACUTE}OG"]
        cp1252 = self.parse(
            make_synthetic_vhdr(cp1252_names, codepage="windows-1252")
        )
        implicit = self.parse(make_synthetic_vhdr(CANONICAL_NAMES, codepage=None))
        comment_codepage = self.parse(
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES, codepage=None),
                b"[Comment]\r\n",
                b"[Comment]\r\nCodepage=windows-1252\r\n",
            )
        )
        self.assertEqual(bom["strict_codepage"], "UTF-8-BOM")
        self.assertEqual(cp1252["strict_codepage"], "windows-1252")
        self.assertEqual(implicit["strict_codepage"], "UTF-8")
        self.assertEqual(comment_codepage["strict_codepage"], "UTF-8")

    def test_F06_bad_preamble_codepage_decode_and_control_refuse(self):
        fixtures = (
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES),
                b"Brain Vision Data Exchange Header File Version 1.0",
                b"Brain Vision Data Exchange Header File Version 2.0",
            ),
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES), b"Codepage=UTF-8", b"Codepage=UTF-16"
            ),
            make_synthetic_vhdr(
                CANONICAL_NAMES, codepage="windows-1252", include_bom=True
            ),
            make_synthetic_vhdr(CANONICAL_NAMES) + b"\xff",
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES),
                b"DataFormat=BINARY",
                b"DataFormat=BIN\x00ARY",
            ),
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES),
                b"[Common Infos]",
                b"Unexpected=content\r\n[Common Infos]",
            ),
        )
        for payload in fixtures:
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[5], payload)

    def test_F06_missing_duplicate_or_malformed_required_declaration_refuses(self):
        fixtures = (
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES), b"DataFormat=BINARY\r\n", b""
            ),
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES),
                b"[Binary Infos]\r\n",
                b"[Binary Infos]\r\n[Binary Infos]\r\n",
            ),
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES),
                b"DataOrientation=MULTIPLEXED",
                b"DataOrientation",
            ),
        )
        for payload in fixtures:
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[5], payload)

    def test_F08_sibling_references_must_be_inert_basenames(self):
        fixtures = (
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES),
                b"DataFile=fixture.eeg",
                b"DataFile=../fixture.eeg",
            ),
            replace_bytes(
                make_synthetic_vhdr(CANONICAL_NAMES),
                b"MarkerFile=fixture.vmrk",
                b"MarkerFile=/tmp/fixture.vmrk",
            ),
        )
        for payload in fixtures:
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[7], payload)

    def test_F07_channel_count_gap_duplicate_name_and_unknown_key_refuse(self):
        fixture = make_synthetic_vhdr(CANONICAL_NAMES)
        fixtures = (
            replace_bytes(fixture, b"NumberOfChannels=36", b"NumberOfChannels=37"),
            replace_bytes(fixture, b"Ch20=EEG20", b"Ch40=EEG20"),
            replace_bytes(fixture, b"Ch20=EEG20", b"Ch20=EEG19"),
            replace_bytes(fixture, b"Ch20=EEG20", b"Sensor20=EEG20"),
        )
        for payload in fixtures:
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[6], payload)

    def test_sampling_interval_must_be_explicit_positive_and_finite(self):
        fixture = make_synthetic_vhdr(CANONICAL_NAMES)
        for value in (b"0", b"-1", b"NaN", b"Infinity", b"wrong"):
            payload = replace_bytes(
                fixture, b"SamplingInterval=976.5625", b"SamplingInterval=" + value
            )
            with self.subTest(value=value):
                self.assert_refusal(REFUSAL_IDS[5], payload)

    def test_signature_is_deterministic_and_contains_only_allowlisted_names(self):
        first = build_channel_signature(self.parse())
        second = build_channel_signature(self.parse())
        self.assertEqual(first, second)
        self.assertEqual(set(first["allowlisted_name_presence"]), set(PUBLIC_NAME_ALLOWLIST))
        encoded = json.dumps(first, sort_keys=True)
        self.assertNotIn("EEG01", encoded)
        self.assertEqual(len(first["ordered_normalized_channel_names_sha256"]), 64)

    def test_all_six_router_outcomes_are_fixed(self):
        r1 = build_channel_signature(self.parse())

        def changed(*, count=None, missing=None):
            value = copy.deepcopy(r1)
            if count is not None:
                value["declared_channel_count"] = count
            if missing is not None:
                value["allowlisted_name_presence"][missing] = False
            return value

        self.assertEqual(route_signatures([], failed=True), "IACKDH-R0")
        self.assertEqual(route_signatures([r1, changed(count=37)]), "IACKDH-R5")
        self.assertEqual(route_signatures([r1]), "IACKDH-R1")
        self.assertEqual(route_signatures([changed(count=37)]), "IACKDH-R2")
        self.assertEqual(route_signatures([changed(missing="HEOG")]), "IACKDH-R3")
        self.assertEqual(
            route_signatures([changed(count=37, missing="HEOG")]), "IACKDH-R4"
        )


class IACKDHeaderAuditExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.contract = copy.deepcopy(load_registered_contract(ROOT))
        self.contract["source"]["object_base_url"] = "fixture://mini"
        self.contract["resource_caps"].update(
            {
                "VHDR_requests": 1,
                "expected_VHDR_body_bytes": 0,
                "minimum_free_disk_bytes": 0,
            }
        )
        self.payload = make_synthetic_vhdr(["C3", "C4", "M1", "M2"])
        self.etag = hashlib.sha256(self.payload).hexdigest()[:32]
        self.row = {
            "path": "headers/one.vhdr",
            "size_bytes": len(self.payload),
            "etag": self.etag,
            "last_modified": "synthetic",
        }
        self.contract["resource_caps"]["expected_VHDR_body_bytes"] = len(self.payload)
        self.url = "fixture://mini/headers/one.vhdr"
        self.index = 0

    def tearDown(self):
        self.temp.cleanup()

    def next_output(self):
        self.index += 1
        return self.root / f"ledger-{self.index}.json"

    def execute(self, *, opener=None, contract=None, rows=None, output=None):
        opener = opener or fixture_opener({self.url: self.payload}, {self.url: self.etag})
        return run_header_audit(
            contract=contract or self.contract,
            rows=rows or [self.row],
            opener=opener,
            output_path=output or self.next_output(),
            environ=THREAD_ENV,
            synthetic=True,
            clock=time_counter(),
            rss_reader=lambda: 24 * 1024 * 1024,
        )

    def test_mocked_roundtrip_hashes_parses_and_writes_one_safe_ledger(self):
        opener = fixture_opener({self.url: self.payload}, {self.url: self.etag})
        outcome = self.execute(opener=opener)
        ledger = outcome.ledger
        self.assertEqual(opener.calls, [self.url])
        self.assertEqual(ledger["measurements"]["body_SHA256_passes"], 1)
        self.assertEqual(ledger["measurements"]["semantic_parse_passes"], 1)
        self.assertEqual(ledger["diagnostic_route"], "IACKDH-R4")
        self.assertFalse(
            ledger["acceptance_gate_results"][
                "separate_exact_Tier_C_decision_remote_green_before_real_access"
            ]
        )
        loaded = load_public_ledger(outcome.ledger_path, repo_root=ROOT)
        self.assertEqual(loaded, ledger)

    def test_response_status_url_etag_encoding_and_length_fail_closed(self):
        cases = (
            (FixtureResponse(self.payload, url=self.url, etag=self.etag, status=500), REFUSAL_IDS[4]),
            (
                FixtureResponse(self.payload, url=f"{self.url}?redirected", etag=self.etag),
                REFUSAL_IDS[3],
            ),
            (FixtureResponse(self.payload, url=self.url, etag="0" * 32), REFUSAL_IDS[4]),
            (
                FixtureResponse(
                    self.payload, url=self.url, etag=self.etag, content_encoding="gzip"
                ),
                REFUSAL_IDS[4],
            ),
            (FixtureResponse(self.payload[:-1], url=self.url, etag=self.etag), REFUSAL_IDS[4]),
        )
        for response, refusal_id in cases:
            with self.subTest(refusal=refusal_id):
                with self.assertRaises(HeaderAuditRefusal) as raised:
                    self.execute(opener=lambda _url, _maximum, value=response: value)
                self.assertEqual(raised.exception.refusal_id, refusal_id)

    def test_thread_output_and_row_caps_refuse_before_transport(self):
        calls = []

        def opener(*args):
            calls.append(args)
            raise AssertionError("transport must remain closed")

        with self.assertRaises(HeaderAuditRefusal) as thread:
            run_header_audit(
                contract=self.contract,
                rows=[self.row],
                opener=opener,
                output_path=self.next_output(),
                environ={**THREAD_ENV, "OMP_NUM_THREADS": "2"},
                synthetic=True,
            )
        self.assertEqual(thread.exception.refusal_id, REFUSAL_IDS[13])
        capped = copy.deepcopy(self.contract)
        capped["resource_caps"]["public_generated_output_bytes"] = 1
        with self.assertRaises(HeaderAuditRefusal) as output:
            self.execute(contract=capped)
        self.assertEqual(output.exception.refusal_id, REFUSAL_IDS[13])
        wrong_rows = [{**self.row, "size_bytes": len(self.payload) + 1}]
        with self.assertRaises(HeaderAuditRefusal) as rows:
            self.execute(rows=wrong_rows)
        self.assertEqual(rows.exception.refusal_id, REFUSAL_IDS[2])
        self.assertEqual(calls, [])

    def test_preexisting_output_refuses_before_transport(self):
        output = self.next_output()
        output.write_text("occupied", encoding="ascii")
        opener = fixture_opener({self.url: self.payload}, {self.url: self.etag})
        with self.assertRaises(HeaderAuditRefusal) as raised:
            self.execute(opener=opener, output=output)
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[14])
        self.assertEqual(opener.calls, [])
        outside = self.root / "outside"
        outside.mkdir()
        linked = self.root / "linked"
        linked.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(HeaderAuditRefusal) as symlinked:
            _assert_rooted_output_path(self.root, linked / "ledger.json")
        self.assertEqual(symlinked.exception.refusal_id, REFUSAL_IDS[14])

    def test_new_heavy_import_refuses(self):
        original = inventory_audit.parse_vhdr_bytes

        def importing_parser(*args, **kwargs):
            sys.modules["braindecode"] = types.ModuleType("braindecode")
            return original(*args, **kwargs)

        old = sys.modules.pop("braindecode", None)
        try:
            with patch.object(
                inventory_audit, "parse_vhdr_bytes", side_effect=importing_parser
            ):
                with self.assertRaises(HeaderAuditRefusal) as raised:
                    self.execute()
            self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[11])
        finally:
            sys.modules.pop("braindecode", None)
            if old is not None:
                sys.modules["braindecode"] = old

    def test_heterogeneous_signatures_route_R5_without_names_or_paths(self):
        second_payload = make_synthetic_vhdr(["C3", "C4", "M1", "TRIGGER"])
        second_etag = hashlib.sha256(second_payload).hexdigest()[:32]
        second_url = "fixture://mini/headers/two.vhdr"
        rows = [self.row, {**self.row, "path": "headers/two.vhdr", "size_bytes": len(second_payload), "etag": second_etag}]
        contract = copy.deepcopy(self.contract)
        contract["resource_caps"]["VHDR_requests"] = 2
        contract["resource_caps"]["expected_VHDR_body_bytes"] = len(self.payload) + len(second_payload)
        outcome = self.execute(
            contract=contract,
            rows=rows,
            opener=fixture_opener(
                {self.url: self.payload, second_url: second_payload},
                {self.url: self.etag, second_url: second_etag},
            ),
        )
        self.assertEqual(outcome.ledger["diagnostic_route"], "IACKDH-R5")
        self.assertEqual(len(outcome.ledger["signature_groups"]), 2)
        encoded = outcome.ledger_path.read_text(encoding="utf-8")
        self.assertNotIn("headers/", encoded)
        self.assertNotIn('"C3"', encoded)

    def test_public_validator_rejects_forbidden_fields_and_router_mutation(self):
        outcome = self.execute()
        forbidden = copy.deepcopy(outcome.ledger)
        forbidden["raw_header_text"] = "private"
        with self.assertRaises(HeaderAuditRefusal) as raw:
            validate_public_ledger(forbidden, contract=self.contract)
        self.assertEqual(raw.exception.refusal_id, REFUSAL_IDS[8])
        route = copy.deepcopy(outcome.ledger)
        route["diagnostic_route"] = "IACKDH-R1"
        with self.assertRaises(HeaderAuditRefusal) as changed:
            validate_public_ledger(route, contract=self.contract)
        self.assertEqual(changed.exception.refusal_id, REFUSAL_IDS[12])

    def test_forbidden_counter_groups_fail_closed(self):
        probes = (
            ("local_IACKD_path_stats_or_opens", REFUSAL_IDS[9]),
            ("sibling_resolutions_stats_hashes_or_opens", REFUSAL_IDS[7]),
            ("model_inference_runs", REFUSAL_IDS[10]),
            ("provider_or_language_model_calls", REFUSAL_IDS[11]),
        )
        for key, refusal_id in probes:
            counters = _base_access_counters(synthetic=True)
            counters[key] = 1
            with self.subTest(key=key), self.assertRaises(HeaderAuditRefusal) as raised:
                _assert_forbidden_counters_zero(counters, synthetic=True)
            self.assertEqual(raised.exception.refusal_id, refusal_id)


def time_counter():
    value = -0.001

    def clock():
        nonlocal value
        value += 0.001
        return value

    return clock


class IACKDHeaderInventoryIntegrationTests(unittest.TestCase):
    def test_registered_contract_inventory_and_plan_replay_without_payload_access(self):
        contract = load_registered_contract(ROOT)
        inventory = load_registered_inventory(ROOT)
        rows = registered_header_rows(contract, inventory)
        self.assertEqual(CONTRACT_SHA256, hashlib.sha256((ROOT / inventory_audit.CONTRACT_RELATIVE_PATH).read_bytes()).hexdigest())
        self.assertEqual(len(rows), 128)
        self.assertEqual(sum(row["size_bytes"] for row in rows), 161_792)
        plan = registered_plan(ROOT)
        self.assertEqual(plan["network_requests_made"], 0)
        self.assertEqual(plan["local_IACKD_path_stats_or_opens"], 0)
        self.assertFalse(plan["real_execution_authorized"])

    def test_full_128_fixture_roundtrip_is_bounded_and_replays_aggregate_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            first_path = Path(directory) / "first.json"
            second_path = Path(directory) / "second.json"
            first = run_synthetic_qualification(
                first_path,
                repo_root=ROOT,
                environ=THREAD_ENV,
                rss_reader=lambda: 32 * 1024 * 1024,
            )
            second = run_synthetic_qualification(
                second_path,
                repo_root=ROOT,
                environ=THREAD_ENV,
                rss_reader=lambda: 32 * 1024 * 1024,
            )
            for key in (
                "signature_groups",
                "first_header_diagnosis",
                "all_headers_identical",
                "diagnostic_route",
            ):
                self.assertEqual(first.ledger[key], second.ledger[key], key)
            self.assertEqual(
                first.ledger["provenance"]["body_hash_set_sha256"],
                second.ledger["provenance"]["body_hash_set_sha256"],
            )
            self.assertEqual(first.ledger["measurements"]["input_objects"], 128)
            self.assertEqual(first.ledger["measurements"]["input_bytes"], 161_792)
            self.assertLess(first.generated_output_bytes, 1024 * 1024)
            self.assertEqual(first.ledger["diagnostic_route"], "IACKDH-R1")
            self.assertEqual(first.ledger["access_counters"]["real_VHDR_requests"], 0)
            self.assertEqual(first.ledger["access_counters"]["real_header_parses"], 0)

    def test_fixture_and_inspection_cli_are_bounded_and_default_is_network_free(self):
        stdout = io.StringIO()
        with patch.object(
            inventory_audit.urllib.request, "build_opener", side_effect=AssertionError("network")
        ), redirect_stdout(stdout):
            self.assertEqual(main([]), 0)
        self.assertIn("zero network requests", stdout.getvalue().lower())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            original = run_synthetic_qualification

            def bounded_fixture(*args, **kwargs):
                return original(*args, **kwargs, rss_reader=lambda: 32 * 1024 * 1024)

            with patch.object(
                inventory_audit,
                "run_synthetic_qualification",
                side_effect=bounded_fixture,
            ), redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--fixture", "--out", str(path)]), 0)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(["--inspect", str(path)]), 0)
            summary = json.loads(stdout.getvalue())
            self.assertEqual(summary["input_objects"], 128)
            self.assertEqual(summary["diagnostic_route"], "IACKDH-R1")

    def test_execute_requires_complete_future_evidence_before_network(self):
        stderr = io.StringIO()
        with patch.object(
            inventory_audit.urllib.request, "build_opener", side_effect=AssertionError("network")
        ), redirect_stderr(stderr):
            self.assertEqual(main(["--execute"]), 2)
        self.assertIn("--execute requires", stderr.getvalue())

    def test_duplicate_json_keys_and_input_caps_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"status":"one","status":"two"}\n', encoding="ascii")
            with self.assertRaises(HeaderAuditRefusal):
                load_public_ledger(path, repo_root=ROOT)
            with self.assertRaises(ValueError):
                load_public_ledger(path, repo_root=ROOT, maximum_bytes=1024 * 1024 + 1)

    def test_module_source_has_no_neural_array_or_model_import(self):
        source = Path(inventory_audit.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "import mne",
            "import numpy",
            "import scipy",
            "import sklearn",
            "import torch",
            "read_raw_brainvision",
        ):
            self.assertNotIn(forbidden, source)

    def test_summary_preserves_every_warning_and_unavailable_field(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = run_synthetic_qualification(
                Path(directory) / "fixture.json",
                repo_root=ROOT,
                environ=THREAD_ENV,
                rss_reader=lambda: 32 * 1024 * 1024,
            )
            summary = summarize_public_ledger(outcome.ledger)
            contract = load_registered_contract(ROOT)
            self.assertEqual(summary["warnings"], contract["warnings"])
            self.assertEqual(summary["unavailable_fields"], contract["unavailable_by_design"])
            self.assertIsNone(summary["producer_is_causal"])
            self.assertFalse(summary["end_to_end_latency_measured"])


if __name__ == "__main__":
    unittest.main()
