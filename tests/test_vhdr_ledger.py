import copy
import hashlib
import io
import json
import os
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.cli import main
from neurodecodekit.preprocess import vhdr_ledger
from neurodecodekit.preprocess.vhdr_ledger import (
    CONTRACT_SHA256,
    DECISION_SHA256,
    ExecutionEvidence,
    REFUSAL_IDS,
    VHDRRefusal,
    _assert_forbidden_counters_zero,
    _base_access_counters,
    _validate_authorization_decision,
    _validate_safe_ledger,
    _verify_execution_evidence,
    git_blob_sha1,
    load_authorization_decision,
    load_registered_contract,
    load_vhdr_ledger,
    make_synthetic_vhdr,
    parse_vhdr_bytes,
    run_vhdr_ledger,
    summarize_vhdr_ledger,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}
EVIDENCE = ExecutionEvidence(
    implementation_commit="a" * 40,
    implementation_push_ci_run_id=101,
    implementation_base_python_job_id=102,
    implementation_optional_neuro_job_id=103,
)


def replace_bytes(payload, old, new):
    changed = payload.replace(old, new)
    if changed == payload:
        raise AssertionError(f"fixture mutation did not match {old!r}")
    return changed


class VHDRParserTests(unittest.TestCase):
    def parse(self, payload=None):
        return parse_vhdr_bytes(
            payload or make_synthetic_vhdr(),
            expected_data_basename="synthetic.eeg",
            expected_marker_basename="synthetic.vmrk",
        )

    def assert_refusal(self, refusal_id, payload):
        with self.assertRaises(VHDRRefusal) as raised:
            self.parse(payload)
        self.assertEqual(raised.exception.refusal_id, refusal_id)
        self.assertNotIn("ProtectedSyntheticValue", str(raised.exception))

    def test_utf8_fixture_parses_deterministically_and_decodes_documented_escape(self):
        first = self.parse()
        second = self.parse()
        self.assertEqual(first, second)
        self.assertEqual(first["strict_codepage"], "UTF-8")
        self.assertEqual(first["sampling_rate_hz"], "500")
        self.assertEqual(first["declared_channel_count"], 4)
        self.assertEqual(first["channels"][1]["source_name"], "C,mid")
        self.assertEqual(first["channels"][0]["declared_unit"], "\N{MICRO SIGN}V")
        self.assertTrue(first["impedance_section_available"])
        self.assertFalse(first["filter_declaration_available"])
        serialized = json.dumps(first, sort_keys=True)
        self.assertNotIn("ProtectedSyntheticValue", serialized)
        self.assertNotIn("synthetic comment", serialized)

    def test_windows_1252_and_utf8_bom_are_strictly_supported(self):
        cp1252 = self.parse(make_synthetic_vhdr(codepage="windows-1252"))
        bom = self.parse(make_synthetic_vhdr(include_bom=True))
        bom_without_field = self.parse(
            replace_bytes(
                make_synthetic_vhdr(include_bom=True),
                b"Codepage=UTF-8\r\n",
                b"",
            )
        )
        self.assertEqual(cp1252["strict_codepage"], "windows-1252")
        self.assertEqual(cp1252["channels"][0]["declared_unit"], "\N{MICRO SIGN}V")
        self.assertEqual(bom["strict_codepage"], "UTF-8")
        self.assertEqual(bom_without_field["strict_codepage"], "UTF-8")

    def test_F09_missing_unsupported_or_conflicting_codepage_refuses(self):
        missing = replace_bytes(make_synthetic_vhdr(), b"Codepage=UTF-8\r\n", b"")
        unsupported = replace_bytes(make_synthetic_vhdr(), b"UTF-8", b"UTF-16")
        conflicting = replace_bytes(
            make_synthetic_vhdr(include_bom=True), b"Codepage=UTF-8", b"Codepage=windows-1252"
        )
        misplaced = replace_bytes(
            replace_bytes(
                make_synthetic_vhdr(),
                b"Codepage=UTF-8\r\n",
                b"",
            ),
            b"[Comment]\r\n",
            b"[Comment]\r\nCodepage=UTF-8\r\n",
        )
        for payload in (missing, unsupported, conflicting, misplaced):
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[8], payload)

    def test_F10_invalid_utf8_replacement_and_control_characters_refuse(self):
        invalid = make_synthetic_vhdr() + b"\xff"
        control = replace_bytes(make_synthetic_vhdr(), b"DataFormat=BINARY", b"DataFormat=BIN\x00ARY")
        for payload in (invalid, control):
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[9], payload)

    def test_F11_missing_duplicate_or_malformed_required_declaration_refuses(self):
        missing = replace_bytes(make_synthetic_vhdr(), b"[Binary Infos]\r\n", b"")
        duplicate = replace_bytes(
            make_synthetic_vhdr(),
            b"[Binary Infos]\r\n",
            b"[Binary Infos]\r\n[Binary Infos]\r\n",
        )
        malformed = replace_bytes(
            make_synthetic_vhdr(), b"DataOrientation=MULTIPLEXED", b"DataOrientation"
        )
        for payload in (missing, duplicate, malformed):
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[10], payload)

    def test_F12_reference_must_be_exact_inert_basename(self):
        changed = replace_bytes(
            make_synthetic_vhdr(), b"DataFile=synthetic.eeg", b"DataFile=../synthetic.eeg"
        )
        self.assert_refusal(REFUSAL_IDS[11], changed)

    def test_F13_channel_count_indices_names_and_uniqueness_refuse(self):
        count = replace_bytes(make_synthetic_vhdr(), b"NumberOfChannels=4", b"NumberOfChannels=5")
        gap = replace_bytes(make_synthetic_vhdr(), b"Ch3=Pz", b"Ch5=Pz")
        duplicate = replace_bytes(make_synthetic_vhdr(), b"Ch3=Pz", b"Ch3=Fz")
        malformed = replace_bytes(make_synthetic_vhdr(), b"Ch4=Oz,,0.1", b"Ch4=Oz,0.1")
        for payload in (count, gap, duplicate, malformed):
            with self.subTest(payload=hashlib.sha256(payload).hexdigest()):
                self.assert_refusal(REFUSAL_IDS[12], payload)

    def test_F14_sampling_interval_must_be_explicit_finite_and_positive(self):
        for value in (b"0", b"-2", b"NaN", b"Infinity", b"not-a-number"):
            payload = replace_bytes(make_synthetic_vhdr(), b"SamplingInterval=2000", b"SamplingInterval=" + value)
            with self.subTest(value=value):
                self.assert_refusal(REFUSAL_IDS[13], payload)

    def test_F15_absolute_local_path_in_allowlisted_declaration_refuses(self):
        payload = replace_bytes(make_synthetic_vhdr(), b"Ch1=Fz", b"Ch1=/tmp/private")
        self.assert_refusal(REFUSAL_IDS[14], payload)


class VHDRLedgerExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.payload = make_synthetic_vhdr()
        self.contract = copy.deepcopy(load_registered_contract(REPO_ROOT))
        self.contract["registered_input"].update(
            {
                "payload_root_relative_path": "synthetic/source",
                "vhdr_relative_path": "fixture.vhdr",
                "expected_basename": "fixture.vhdr",
                "expected_data_basename": "synthetic.eeg",
                "expected_marker_basename": "synthetic.vmrk",
                "expected_size_bytes": len(self.payload),
                "maximum_read_bytes": len(self.payload) + 64,
                "source_identity": git_blob_sha1(self.payload),
                "modality": "synthetic_EEG",
                "subject_id": "synthetic",
                "session_id": "synthetic",
                "block_id": "synthetic",
                "task_id": "synthetic",
            }
        )
        self.contract["output_contract"]["output_root"] = "synthetic/output"
        self.source = self.root / "synthetic/source/fixture.vhdr"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(self.payload)

    def tearDown(self):
        self.temp.cleanup()

    def execute(self, *, contract=None, evidence=EVIDENCE):
        return run_vhdr_ledger(
            contract=contract or self.contract,
            contract_sha256=CONTRACT_SHA256,
            decision_sha256=DECISION_SHA256,
            implementation_record_sha256="b" * 64,
            evidence=evidence,
            workspace_root=self.root,
            environ=THREAD_ENV,
            clock=lambda: 100.0,
            rss_reader=lambda: 16 * 1024 * 1024,
            verify_evidence=lambda _root, _evidence: None,
        )

    def test_synthetic_filesystem_roundtrip_opens_only_vhdr_once_and_writes_bounded_outputs(self):
        real_open = os.open
        real_lstat = os.lstat
        opened = []
        statted = []

        def recording_open(path, flags, *args):
            opened.append(str(path))
            return real_open(path, flags, *args)

        def recording_lstat(path, *args):
            statted.append(str(path))
            return real_lstat(path, *args)

        with patch.object(vhdr_ledger.os, "open", side_effect=recording_open), patch.object(
            vhdr_ledger.os, "lstat", side_effect=recording_lstat
        ):
            outcome = self.execute()

        self.assertEqual(sum(path.endswith("fixture.vhdr") for path in opened), 1)
        self.assertFalse(any(path.endswith((".eeg", ".vmrk", ".mat")) for path in opened))
        self.assertFalse(any(path.endswith((".eeg", ".vmrk", ".mat")) for path in statted))
        self.assertTrue(outcome.ledger_path.is_file())
        self.assertTrue(outcome.summary_path.is_file())
        self.assertLess(outcome.generated_output_bytes, 1024 * 1024)
        self.assertEqual(outcome.ledger["access_counters"]["sibling_path_stats"], 0)
        self.assertEqual(outcome.ledger["access_counters"]["sibling_content_opens"], 0)
        loaded = load_vhdr_ledger(outcome.ledger_path, contract=self.contract)
        self.assertEqual(summarize_vhdr_ledger(loaded)["declared_channel_count"], 4)

    def test_F04_missing_nonregular_or_symlinked_input_refuses_before_open(self):
        self.source.unlink()
        self.source.symlink_to(self.root / "missing.vhdr")
        with self.assertRaises(VHDRRefusal) as raised:
            self.execute()
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[3])

    def test_F05_size_or_git_blob_identity_mismatch_refuses_without_output(self):
        contract = copy.deepcopy(self.contract)
        contract["registered_input"]["source_identity"] = "0" * 40
        with self.assertRaises(VHDRRefusal) as raised:
            self.execute(contract=contract)
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[4])
        self.assertFalse((self.root / "synthetic/output").exists())

    def test_F06_preexisting_output_refuses_before_vhdr_open(self):
        (self.root / "synthetic/output").mkdir()
        with patch.object(vhdr_ledger.os, "open", wraps=os.open) as mocked_open:
            with self.assertRaises(VHDRRefusal) as raised:
                self.execute()
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[5])
        self.assertFalse(any(str(call.args[0]).endswith("fixture.vhdr") for call in mocked_open.mock_calls))

    def test_F07_F16_F17_F18_forbidden_counter_groups_fail_closed(self):
        counters = _base_access_counters()
        probes = (
            (REFUSAL_IDS[6], "sibling_path_stats"),
            (REFUSAL_IDS[15], "eeg_stats_hashes_or_signal_reads"),
            (REFUSAL_IDS[16], "model_inference_runs"),
            (REFUSAL_IDS[17], "network_calls"),
        )
        for refusal_id, key in probes:
            mutated = dict(counters)
            mutated[key] = 1
            with self.subTest(key=key), self.assertRaises(VHDRRefusal) as raised:
                _assert_forbidden_counters_zero(mutated)
            self.assertEqual(raised.exception.refusal_id, refusal_id)

    def test_F08_new_heavy_dependency_import_refuses(self):
        original = vhdr_ledger.parse_vhdr_bytes

        def importing_parser(*args, **kwargs):
            sys.modules["numpy"] = types.ModuleType("numpy")
            return original(*args, **kwargs)

        old = sys.modules.pop("numpy", None)
        try:
            with patch.object(vhdr_ledger, "parse_vhdr_bytes", side_effect=importing_parser):
                with self.assertRaises(VHDRRefusal) as raised:
                    self.execute()
            self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[7])
        finally:
            sys.modules.pop("numpy", None)
            if old is not None:
                sys.modules["numpy"] = old

    def test_F15_raw_or_protected_ledger_field_refuses(self):
        outcome = self.execute()
        mutations = []
        raw = copy.deepcopy(outcome.ledger)
        raw["raw_header"] = "forbidden"
        mutations.append(raw)
        nested = copy.deepcopy(outcome.ledger)
        nested["declared_header"]["sentence"] = "forbidden"
        mutations.append(nested)
        for ledger in mutations:
            with self.subTest(keys=sorted(ledger)), self.assertRaises(VHDRRefusal) as raised:
                _validate_safe_ledger(ledger, self.contract)
            self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[14])
        duplicate_path = self.root / "duplicate-ledger.json"
        canonical = outcome.ledger_path.read_text(encoding="ascii")
        duplicate_path.write_text(
            canonical.replace(
                '  "status": "passed",',
                '  "status": "passed",\n  "status": "passed",',
                1,
            ),
            encoding="ascii",
        )
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            load_vhdr_ledger(duplicate_path, contract=self.contract)

    def test_F19_resource_and_output_caps_refuse(self):
        contract = copy.deepcopy(self.contract)
        contract["output_contract"]["maximum_combined_generated_output_bytes"] = 64
        with self.assertRaises(VHDRRefusal) as raised:
            self.execute(contract=contract)
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[18])

    def test_F20_output_path_symlink_refuses_without_following(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / "synthetic/output").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(VHDRRefusal) as raised:
            self.execute()
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[19])

    def test_F21_rerun_or_amendment_evidence_refuses(self):
        evidence = ExecutionEvidence(
            implementation_commit="a" * 40,
            implementation_push_ci_run_id=101,
            implementation_base_python_job_id=102,
            implementation_optional_neuro_job_id=103,
            registered_execution_ordinal=2,
        )
        with self.assertRaises(VHDRRefusal) as raised:
            self.execute(evidence=evidence)
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[20])

    def test_F22_claim_ceiling_or_gate_mutation_refuses(self):
        outcome = self.execute()
        ledger = copy.deepcopy(outcome.ledger)
        ledger["claim_boundary"]["claim_ceiling"] = "neural_advantage"
        with self.assertRaises(VHDRRefusal) as raised:
            _validate_safe_ledger(ledger, self.contract)
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[21])


class VHDRRegisteredBoundaryTests(unittest.TestCase):
    def test_F01_exact_authorization_and_F02_contract_identities_are_bound(self):
        decision = load_authorization_decision(REPO_ROOT)
        contract = load_registered_contract(REPO_ROOT)
        self.assertTrue(decision["conditional_registered_real_execution"]["authorized_by_this_exact_decision"])
        self.assertEqual(contract["refusal_ids"], list(REFUSAL_IDS))

        unauthorized = copy.deepcopy(decision)
        unauthorized["conditional_registered_real_execution"][
            "authorized_by_this_exact_decision"
        ] = False
        with self.assertRaises(VHDRRefusal) as missing:
            _validate_authorization_decision(unauthorized)
        self.assertEqual(missing.exception.refusal_id, REFUSAL_IDS[0])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / vhdr_ledger.CONTRACT_RELATIVE_PATH
            path.parent.mkdir(parents=True)
            path.write_bytes((REPO_ROOT / vhdr_ledger.CONTRACT_RELATIVE_PATH).read_bytes() + b" ")
            with self.assertRaises(VHDRRefusal) as raised:
                load_registered_contract(root)
            self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[1])

    def test_F03_malformed_green_evidence_refuses_before_git_or_path_access(self):
        malformed = ExecutionEvidence(
            implementation_commit="short",
            implementation_push_ci_run_id=0,
            implementation_base_python_job_id=0,
            implementation_optional_neuro_job_id=0,
        )
        with patch.object(vhdr_ledger.subprocess, "run") as git_run:
            with self.assertRaises(VHDRRefusal) as raised:
                _verify_execution_evidence(REPO_ROOT, malformed)
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[2])
        git_run.assert_not_called()

    def test_all_22_registered_refusal_ids_are_unique_and_covered(self):
        self.assertEqual(len(REFUSAL_IDS), 22)
        self.assertEqual(len(set(REFUSAL_IDS)), 22)
        self.assertEqual(
            [value.split("_", 1)[0] for value in REFUSAL_IDS],
            [f"L54A-F{index:02d}" for index in range(1, 23)],
        )

    def test_cli_dry_run_does_not_stat_registered_S20_path_and_help_is_available(self):
        stdout = io.StringIO()
        real_lstat = os.lstat

        def guarded_lstat(path, *args):
            if "loop53_s20_eeg" in str(path):
                raise AssertionError("dry-run touched the registered S20 path")
            return real_lstat(path, *args)

        old_cwd = Path.cwd()
        try:
            os.chdir(REPO_ROOT)
            with patch.object(vhdr_ledger.os, "lstat", side_effect=guarded_lstat), redirect_stdout(stdout):
                code = main(["loop54-vhdr-ledger", "--dry-run"])
            self.assertEqual(code, 0)
            self.assertIn("no registered s20 path stat", stdout.getvalue().lower())

            stdout = io.StringIO()
            with self.assertRaises(SystemExit) as raised, redirect_stdout(stdout):
                main(["loop54-vhdr-ledger", "--help"])
            self.assertEqual(raised.exception.code, 0)
            self.assertIn("--implementation-optional-neuro-job-id", stdout.getvalue())
        finally:
            os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
