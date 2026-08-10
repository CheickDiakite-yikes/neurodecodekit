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

from neurodecodekit.preprocess import iackd_channel_roles as roles
from neurodecodekit.preprocess.iackd_channel_roles import (
    CONTRACT_SHA256,
    FixtureResponse,
    REFUSAL_IDS,
    RoleAuditRefusal,
    _assert_forbidden_counters_zero,
    _base_access_counters,
    _padded_tsv,
    _synthetic_contract_and_rows,
    fixture_opener,
    load_public_ledger,
    load_registered_contract,
    load_registered_inventory,
    main,
    make_synthetic_channels_tsv,
    make_synthetic_coordsystem,
    make_synthetic_eeg_sidecar,
    make_synthetic_electrodes_tsv,
    parse_channels_tsv,
    parse_coordsystem_json,
    parse_eeg_sidecar,
    parse_electrodes_tsv,
    registered_metadata_rows,
    registered_plan,
    route_role_audit,
    run_role_geometry_audit,
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


def deterministic_clock():
    state = [-0.001]

    def clock():
        state[0] += 0.001
        return state[0]

    return clock


def replace_bytes(payload, old, new):
    changed = payload.replace(old, new, 1)
    if changed == payload:
        raise AssertionError(f"fixture mutation did not match {old!r}")
    return changed


class IACKDRoleParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load_registered_contract(ROOT)

    def assert_refusal(self, refusal_id, function, payload):
        with self.assertRaises(RoleAuditRefusal) as raised:
            function(payload, self.contract)
        self.assertEqual(raised.exception.refusal_id, refusal_id)

    def test_registered_contract_is_hash_bound_and_remotely_green(self):
        payload = (ROOT / roles.CONTRACT_RELATIVE_PATH).read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), CONTRACT_SHA256)
        self.assertEqual(len(payload), roles.CONTRACT_BYTES)
        self.assertEqual(roles.REGISTRATION_COMMIT, "228ccd03f5e0b5d02ba104e13b77b04f2032df78")
        self.assertEqual(roles.REGISTRATION_CI_RUN_ID, 31427931578)
        self.assertEqual(roles.REGISTRATION_BASE_JOB_ID, 93583989913)
        self.assertEqual(roles.REGISTRATION_OPTIONAL_JOB_ID, 93583989996)

    def test_channel_tables_preserve_source_roles_and_optional_references(self):
        plain = parse_channels_tsv(
            make_synthetic_channels_tsv(include_references=False, total_bytes=1752),
            self.contract,
        )
        referenced = parse_channels_tsv(
            make_synthetic_channels_tsv(include_references=True, total_bytes=1866),
            self.contract,
        )
        self.assertEqual(len(plain["rows"]), 29)
        self.assertEqual(len(referenced["rows"]), 31)
        by_name = {row["name"]: row for row in referenced["rows"]}
        self.assertEqual(by_name["TRIGGER"]["type"], "TRIG")
        self.assertEqual(by_name["HEOG"]["type"], "HEOG")
        self.assertEqual(by_name["VEOG"]["type"], "VEOG")
        self.assertEqual(by_name["M1"]["type"], "REF")
        self.assertEqual(by_name["M2"]["type"], "REF")
        self.assertNotIn("fixture_padding", plain)

    def test_channel_utf8_bom_and_unknown_columns_are_safe(self):
        payload = make_synthetic_channels_tsv(
            include_references=False, total_bytes=1752
        )
        parsed = parse_channels_tsv(b"\xef\xbb\xbf" + payload, self.contract)
        self.assertEqual(len(parsed["rows"]), 29)
        self.assertEqual(len(parsed["unknown_column_names_sha256"]), 64)
        self.assertNotIn("generated", json.dumps(parsed, sort_keys=True))

    def test_channel_decode_schema_name_and_width_fail_closed(self):
        fixture = make_synthetic_channels_tsv(
            include_references=False, total_bytes=1752
        )
        cases = (
            (fixture + b"\xff", REFUSAL_IDS[8]),
            (replace_bytes(fixture, b"name\ttype\tunits", b"type\tname\tunits"), REFUSAL_IDS[8]),
            (replace_bytes(fixture, b"F3\tEEG", b"F7\tEEG"), REFUSAL_IDS[8]),
            (replace_bytes(fixture, b"Fp1\tEEG", b"Fp1\teeg"), REFUSAL_IDS[9]),
            (replace_bytes(fixture, b"good\t", b"okay\t"), REFUSAL_IDS[9]),
            (replace_bytes(fixture, b"\t1024\t", b"\tNaN \t"), REFUSAL_IDS[9]),
        )
        for payload, refusal_id in cases:
            with self.subTest(refusal_id=refusal_id):
                self.assert_refusal(refusal_id, parse_channels_tsv, payload)

    def test_sidecar_is_duplicate_key_free_and_allowlisted(self):
        payload = make_synthetic_eeg_sidecar(total_bytes=1354)
        parsed = parse_eeg_sidecar(payload, self.contract)
        self.assertEqual(parsed["SamplingFrequency"], 1024)
        self.assertEqual(parsed["EEGReference"], "Cz")
        self.assertEqual(parsed["EEGChannelCount"], 26)
        self.assertEqual(parsed["TriggerChannelCount"], 1)
        encoded = json.dumps(parsed, sort_keys=True)
        self.assertNotIn("TaskDescription", encoded)
        self.assertNotIn("generated-private", encoded)

    def test_sidecar_missing_duplicate_nonfinite_and_bad_count_refuse(self):
        valid = {
            "TaskName": "fixture",
            "EEGReference": "Cz",
            "SamplingFrequency": 1024,
            "PowerLineFrequency": 50,
            "SoftwareFilters": "n/a",
        }
        missing = {key: value for key, value in valid.items() if key != "EEGReference"}
        duplicate = (
            b'{"TaskName":"a","TaskName":"b","EEGReference":"Cz",'
            b'"SamplingFrequency":1024,"PowerLineFrequency":50,"SoftwareFilters":"n/a"}'
        )
        nonfinite = json.dumps({**valid, "SamplingFrequency": "NaN"}).encode()
        bad_count = json.dumps({**valid, "EEGChannelCount": True}).encode()
        for payload in (
            json.dumps(missing).encode(),
            duplicate,
            nonfinite,
            bad_count,
        ):
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[10], parse_eeg_sidecar, payload)

    def test_electrode_parser_hashes_but_never_returns_coordinates(self):
        payload = make_synthetic_electrodes_tsv(total_bytes=890)
        parsed = parse_electrodes_tsv(payload, self.contract)
        self.assertEqual(len(parsed["rows"]), 26)
        self.assertTrue(all(row["finite"] for row in parsed["rows"]))
        self.assertNotIn("x", json.dumps(parsed, sort_keys=True))
        self.assertEqual(len(parsed["ordered_name_sha256"]), 64)
        self.assertEqual(len(parsed["coordinate_bytes_sha256"]), 64)

    def test_electrode_na_is_explicit_and_bad_coordinate_refuses(self):
        payload = _padded_tsv(
            ("name", "x", "y", "z"),
            (("C3", "n/a", "0", "1"),),
            total_bytes=128,
        )
        parsed = parse_electrodes_tsv(payload, self.contract)
        self.assertFalse(parsed["rows"][0]["finite"])
        bad = replace_bytes(payload, b"n/a", b"NaN")
        self.assert_refusal(REFUSAL_IDS[11], parse_electrodes_tsv, bad)

    def test_coordsystem_parser_keeps_only_system_and_units(self):
        payload = make_synthetic_coordsystem(total_bytes=969)
        parsed = parse_coordsystem_json(payload, self.contract)
        self.assertEqual(parsed, {"coordinate_system": "CapTrak", "coordinate_units": "m"})
        self.assertNotIn("Anatomical", json.dumps(parsed))
        bad = replace_bytes(payload, b'"EEGCoordinateUnits":"m"', b'"EEGCoordinateUnits":"x"')
        self.assert_refusal(REFUSAL_IDS[11], parse_coordsystem_json, bad)

    def test_all_five_router_outcomes_are_ordered(self):
        reconciliation = {
            "channel_row_count_multiset_matches_H1": True,
            "allowlisted_presence_matches_H1": True,
            "required_control_BIDS_roles_valid": True,
            "present_sidecar_type_counts_reconcile": True,
            "present_channel_sampling_reconciles": True,
            "all_sidecar_sampling_matches_H1_1024_Hz": True,
        }
        role_map = {"core_schema_count": 1}
        geometry = [{"occurrence_count": 30, "finite_C3_C4_Cz_presence": True}]
        arguments = {
            "reconciliation": reconciliation,
            "role_map_candidate": role_map,
            "geometry_groups": geometry,
            "reference_values": ["Cz"],
        }
        self.assertEqual(route_role_audit(**arguments, failed=True), "IACKDR-R0")
        contradicted = {**reconciliation, "present_sidecar_type_counts_reconcile": False}
        self.assertEqual(
            route_role_audit(**{**arguments, "reconciliation": contradicted}),
            "IACKDR-R1",
        )
        self.assertEqual(
            route_role_audit(**{**arguments, "role_map_candidate": {"core_schema_count": 2}}),
            "IACKDR-R2",
        )
        self.assertEqual(
            route_role_audit(**{**arguments, "reference_values": ["n/a"]}),
            "IACKDR-R3",
        )
        incomplete = [{"occurrence_count": 30, "finite_C3_C4_Cz_presence": False}]
        self.assertEqual(
            route_role_audit(**{**arguments, "geometry_groups": incomplete}),
            "IACKDR-R3",
        )
        self.assertEqual(route_role_audit(**arguments), "IACKDR-R4")


class IACKDRoleAuditExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.contract = load_registered_contract(ROOT)
        self.inventory = load_registered_inventory(ROOT)
        (
            self.fixture_contract,
            self.rows,
            self.payloads,
            self.etags,
        ) = _synthetic_contract_and_rows(self.contract, self.inventory)

    def tearDown(self):
        self.temporary.cleanup()

    def output(self, name="ledger.json"):
        return self.root / name

    def execute(self, *, output=None, contract=None, rows=None, opener=None, clock=None):
        return run_role_geometry_audit(
            contract=contract or self.fixture_contract,
            rows=rows or self.rows,
            opener=opener or fixture_opener(self.payloads, self.etags),
            output_path=output or self.output(),
            environ=THREAD_ENV,
            synthetic=True,
            clock=clock or deterministic_clock(),
            rss_reader=lambda: 24 * 1024 * 1024,
        )

    def test_full_316_object_roundtrip_is_aggregate_and_constructed_R4(self):
        opener = fixture_opener(self.payloads, self.etags)
        outcome = self.execute(opener=opener)
        ledger = outcome.ledger
        self.assertEqual(len(opener.calls), 316)
        self.assertEqual(ledger["measurements"]["input_bytes"], 457602)
        self.assertEqual(ledger["diagnostic_route"], "IACKDR-R4")
        self.assertEqual(len(ledger["channel_schema_groups"]), 2)
        self.assertEqual(ledger["role_map_candidate"]["core_schema_count"], 1)
        self.assertEqual(len(ledger["role_map_candidate"]["predictive_EEG_names"]), 26)
        self.assertEqual(
            sum(row["occurrence_count"] for row in ledger["geometry_groups"]), 30
        )
        self.assertFalse(ledger["acceptance_gate_results"][self.contract["acceptance_gates"][0]])
        self.assertEqual(load_public_ledger(outcome.ledger_path, repo_root=ROOT), ledger)

    def test_full_surface_replay_is_deterministic(self):
        first = self.execute(output=self.output("first.json"))
        second = self.execute(output=self.output("second.json"))
        self.assertEqual(first.ledger, second.ledger)
        self.assertEqual(first.ledger_path.read_bytes(), second.ledger_path.read_bytes())
        self.assertEqual(
            first.ledger["body_hash_set_SHA256"], second.ledger["body_hash_set_SHA256"]
        )

    def test_fixture_sizes_roles_and_pair_membership_are_exact(self):
        registered = registered_metadata_rows(self.contract, self.inventory)
        self.assertEqual([row["path"] for row in registered], [row["path"] for row in self.rows])
        self.assertEqual(len(self.rows), 316)
        self.assertEqual(sum(row["size_bytes"] for row in self.rows), 457602)
        self.assertEqual(
            {role: sum(row["role"] == role for row in self.rows) for role in self.contract["source"]["selected_roles"]},
            {"channels": 128, "eeg_sidecar": 128, "electrodes": 30, "coordsystem": 30},
        )
        self.assertEqual(
            {len(payload) for payload in self.payloads.values()},
            {row["size_bytes"] for row in registered},
        )

    def test_response_status_url_etag_encoding_and_length_fail_closed(self):
        first = self.rows[0]
        url = f"fixture://iackd-role-geometry/{first['path']}"
        payload = self.payloads[url]
        cases = (
            FixtureResponse(payload, url=url, etag=first["etag"], status=500),
            FixtureResponse(payload, url=f"{url}?redirect", etag=first["etag"]),
            FixtureResponse(payload, url=url, etag="0" * 32),
            FixtureResponse(payload, url=url, etag=first["etag"], content_encoding="gzip"),
            FixtureResponse(payload[:-1], url=url, etag=first["etag"]),
        )
        for index, response in enumerate(cases):
            with self.subTest(index=index):
                with self.assertRaises(RoleAuditRefusal) as raised:
                    self.execute(
                        output=self.output(f"failure-{index}.json"),
                        opener=lambda _url, _maximum, value=response: value,
                    )
                self.assertIn(raised.exception.refusal_id, {REFUSAL_IDS[4], REFUSAL_IDS[5], REFUSAL_IDS[6]})

    def test_wrong_thread_count_output_cap_and_row_set_refuse_before_transport(self):
        calls = []

        def opener(*args):
            calls.append(args)
            raise AssertionError("transport must remain closed")

        with self.assertRaises(RoleAuditRefusal) as thread:
            run_role_geometry_audit(
                contract=self.fixture_contract,
                rows=self.rows,
                opener=opener,
                output_path=self.output("thread.json"),
                environ={**THREAD_ENV, "OMP_NUM_THREADS": "2"},
                synthetic=True,
            )
        self.assertEqual(thread.exception.refusal_id, REFUSAL_IDS[6])
        capped = copy.deepcopy(self.fixture_contract)
        capped["resource_caps"]["public_generated_output_bytes"] = 1
        with self.assertRaises(RoleAuditRefusal) as output:
            self.execute(contract=capped, output=self.output("cap.json"))
        self.assertEqual(output.exception.refusal_id, REFUSAL_IDS[6])
        with self.assertRaises(RoleAuditRefusal) as rows:
            self.execute(rows=self.rows[:-1], opener=opener, output=self.output("rows.json"))
        self.assertEqual(rows.exception.refusal_id, REFUSAL_IDS[3])
        self.assertEqual(calls, [])

    def test_preexisting_and_symlinked_output_refuse(self):
        output = self.output()
        output.write_text("occupied", encoding="ascii")
        opener = fixture_opener(self.payloads, self.etags)
        with self.assertRaises(RoleAuditRefusal) as occupied:
            self.execute(output=output, opener=opener)
        self.assertEqual(occupied.exception.refusal_id, REFUSAL_IDS[14])
        self.assertEqual(opener.calls, [])
        outside = self.root / "outside"
        outside.mkdir()
        linked = self.root / "linked"
        linked.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(RoleAuditRefusal) as linked_output:
            roles._assert_rooted_output_path(self.root, linked / "ledger.json")
        self.assertEqual(linked_output.exception.refusal_id, REFUSAL_IDS[14])

    def test_required_control_role_mutation_routes_R1(self):
        payloads = dict(self.payloads)
        target = next(row for row in self.rows if row["role"] == "channels")
        url = f"fixture://iackd-role-geometry/{target['path']}"
        payloads[url] = replace_bytes(payloads[url], b"TRIGGER\tTRIG", b"TRIGGER\tEEG ")
        rows = [dict(row) for row in self.rows]
        replacement_etag = hashlib.sha256(payloads[url]).hexdigest()[:32]
        next(row for row in rows if row["path"] == target["path"])["etag"] = replacement_etag
        etags = {**self.etags, url: replacement_etag}
        outcome = self.execute(
            rows=rows,
            opener=fixture_opener(payloads, etags),
            output=self.output("r1.json"),
        )
        self.assertEqual(outcome.ledger["diagnostic_route"], "IACKDR-R1")

    def test_core_schema_mutation_routes_R2(self):
        payloads = dict(self.payloads)
        target = next(row for row in self.rows if row["role"] == "channels")
        url = f"fixture://iackd-role-geometry/{target['path']}"
        payloads[url] = replace_bytes(payloads[url], b"Fp1\tEEG", b"AF1\tEEG")
        rows = [dict(row) for row in self.rows]
        replacement_etag = hashlib.sha256(payloads[url]).hexdigest()[:32]
        next(row for row in rows if row["path"] == target["path"])["etag"] = replacement_etag
        etags = {**self.etags, url: replacement_etag}
        outcome = self.execute(
            rows=rows,
            opener=fixture_opener(payloads, etags),
            output=self.output("r2.json"),
        )
        self.assertEqual(outcome.ledger["diagnostic_route"], "IACKDR-R2")

    def test_forbidden_field_hash_route_and_private_value_mutations_refuse(self):
        outcome = self.execute()
        for index, mutate in enumerate(
            (
                lambda value: value.update({"source_path": "hidden"}),
                lambda value: value["role_map_candidate"].update({"role_map_SHA256": "0" * 64}),
                lambda value: value.update({"status": "passed"}),
            )
        ):
            ledger = copy.deepcopy(outcome.ledger)
            mutate(ledger)
            with self.subTest(index=index), self.assertRaises(RoleAuditRefusal):
                validate_public_ledger(ledger, contract=self.contract)
        with self.assertRaises(RoleAuditRefusal) as private:
            validate_public_ledger(
                outcome.ledger,
                contract=self.contract,
                forbidden_private_values=[outcome.ledger["warnings"][0]],
            )
        self.assertEqual(private.exception.refusal_id, REFUSAL_IDS[13])

    def test_loader_refuses_duplicate_json_and_input_cap(self):
        duplicate = self.output("duplicate.json")
        duplicate.write_text('{"schema_name":"a","schema_name":"b"}', encoding="utf-8")
        with self.assertRaises(RoleAuditRefusal):
            load_public_ledger(duplicate, repo_root=ROOT)
        outcome = self.execute(output=self.output("bounded.json"))
        with self.assertRaises(RoleAuditRefusal):
            load_public_ledger(
                outcome.ledger_path,
                repo_root=ROOT,
                maximum_bytes=100,
            )

    def test_new_heavy_import_and_forbidden_counter_refuse(self):
        original = roles.parse_channels_tsv

        def importing_parser(*args, **kwargs):
            sys.modules["braindecode"] = types.ModuleType("braindecode")
            return original(*args, **kwargs)

        prior = sys.modules.pop("braindecode", None)
        try:
            with patch.object(roles, "parse_channels_tsv", side_effect=importing_parser):
                with self.assertRaises(RoleAuditRefusal) as raised:
                    self.execute(output=self.output("heavy.json"))
            self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[15])
        finally:
            sys.modules.pop("braindecode", None)
            if prior is not None:
                sys.modules["braindecode"] = prior
        counters = _base_access_counters(synthetic=True)
        counters["target_or_label_reads"] = 1
        with self.assertRaises(RoleAuditRefusal) as target:
            _assert_forbidden_counters_zero(counters, synthetic=True)
        self.assertEqual(target.exception.refusal_id, REFUSAL_IDS[15])


class IACKDRoleCLITests(unittest.TestCase):
    def test_default_plan_is_exact_and_network_free(self):
        with patch.object(roles, "_open_url_once", side_effect=AssertionError("network")):
            plan = registered_plan(ROOT)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main([])
        self.assertEqual(code, 0)
        self.assertEqual(plan["registered_objects"], 316)
        self.assertEqual(plan["registered_body_bytes"], 457602)
        self.assertFalse(plan["real_execution_authorized"])
        self.assertIn("zero network requests", stdout.getvalue())

    def test_fixture_and_inspect_cli_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "fixture.json"
            fixture_stdout = io.StringIO()
            with patch.object(roles, "_peak_rss_bytes", return_value=24 * 1024 * 1024):
                with redirect_stdout(fixture_stdout):
                    fixture_code = main(["--fixture", "--out", str(output)])
            inspect_stdout = io.StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_code = main(["--inspect", str(output)])
            summary = json.loads(inspect_stdout.getvalue())
        self.assertEqual((fixture_code, inspect_code), (0, 0))
        self.assertIn("IACKDR-R4", fixture_stdout.getvalue())
        self.assertEqual(summary["diagnostic_route"], "IACKDR-R4")
        self.assertEqual(summary["input_objects"], 316)

    def test_execute_without_exact_evidence_refuses_before_network(self):
        stderr = io.StringIO()
        with patch.object(roles, "_open_url_once", side_effect=AssertionError("network")):
            with redirect_stderr(stderr):
                code = main(["--execute"])
        self.assertEqual(code, 2)
        self.assertIn("--execute requires", stderr.getvalue())

    def test_synthetic_summary_reports_causality_and_latency_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = run_synthetic_qualification(
                Path(directory) / "fixture.json",
                environ=THREAD_ENV,
                rss_reader=lambda: 24 * 1024 * 1024,
            )
            summary = summarize_public_ledger(outcome.ledger)
        self.assertIsNone(summary["producer_is_causal"])
        self.assertFalse(summary["end_to_end_latency_measured"])
        self.assertEqual(summary["central_geometry_groups_complete"], 30)


if __name__ == "__main__":
    unittest.main()
