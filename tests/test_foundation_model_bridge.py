import copy
import hashlib
import io
import json
import math
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main
from neurodecodekit.evaluation.foundation_model_bridge import (
    ACCESS_COUNTER_FIELDS,
    CONDITION_IDS,
    MAX_INPUT_BYTES,
    MAX_OUTPUT_BYTES,
    FoundationModelBridgeError,
    build_ablation_plan,
    build_ablation_plan_file,
    build_synthetic_evidence_fixture,
    canonical_json_bytes,
    inspect_ablation_plan_file,
    load_json_object,
    make_synthetic_evidence_file,
    sha256_json,
    validate_ablation_plan,
    validate_synthetic_evidence,
    write_bounded_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "fixtures" / "foundation_model_bridge_synthetic_evidence.v0.json"


class FoundationModelBridgeTests(unittest.TestCase):
    def setUp(self):
        self.evidence = build_synthetic_evidence_fixture()

    def test_committed_fixture_is_small_valid_and_target_free(self):
        payload = load_json_object(FIXTURE_PATH)
        validate_synthetic_evidence(payload)
        self.assertLess(FIXTURE_PATH.stat().st_size, MAX_INPUT_BYTES)
        self.assertEqual(len(payload["items"]), 3)
        self.assertEqual(payload["task_context"], "synthetic_unprompted_typing_without_reference")
        self.assertTrue(all(value == 0 for value in payload["access_counters"].values()))

    def test_plan_is_deterministic_and_has_four_rows_per_item(self):
        first = build_ablation_plan(self.evidence)
        second = build_ablation_plan(copy.deepcopy(self.evidence))
        self.assertEqual(first, second)
        self.assertEqual(first["plan_core_sha256"], second["plan_core_sha256"])
        self.assertEqual(len(first["conditions"]), 12)
        self.assertEqual(first["condition_counts"], {name: 3 for name in CONDITION_IDS})
        self.assertLess(len(canonical_json_bytes(first)), MAX_OUTPUT_BYTES)

    def test_condition_payloads_are_blinded_and_matched(self):
        plan = build_ablation_plan(self.evidence)
        rows = [row for row in plan["conditions"] if row["item_id"] == "SYNTH-ITEM-00"]
        self.assertEqual([row["condition_id"] for row in rows], list(CONDITION_IDS))
        self.assertEqual(rows[0]["blinded_request_payload"]["ctc_nbest"], [])
        self.assertEqual(rows[0]["blinded_request_payload"]["neural_key_frames"], [])
        self.assertNotEqual(rows[1]["blinded_request_payload"]["ctc_nbest"], [])
        self.assertEqual(rows[1]["blinded_request_payload"]["neural_key_frames"], [])
        self.assertEqual(rows[2]["ctc_source_item_id"], "SYNTH-ITEM-00")
        self.assertEqual(rows[2]["neural_source_item_id"], "SYNTH-ITEM-00")
        self.assertEqual(rows[3]["neural_source_item_id"], "SYNTH-ITEM-01")
        for row in rows:
            payload = row["blinded_request_payload"]
            self.assertNotIn("condition_id", payload)
            self.assertNotIn("item_id", payload)
            self.assertEqual(row["request_sha256"], sha256_json(payload))

    def test_derangement_is_fixed_cyclic_and_has_no_self_pair(self):
        plan = build_ablation_plan(self.evidence)
        rows = plan["derangement"]["rows"]
        self.assertEqual(
            rows,
            [
                {"item_id": "SYNTH-ITEM-00", "neural_source_item_id": "SYNTH-ITEM-01"},
                {"item_id": "SYNTH-ITEM-01", "neural_source_item_id": "SYNTH-ITEM-02"},
                {"item_id": "SYNTH-ITEM-02", "neural_source_item_id": "SYNTH-ITEM-00"},
            ],
        )
        self.assertTrue(all(row["item_id"] != row["neural_source_item_id"] for row in rows))

    def test_model_plan_cannot_execute_or_inject_embeddings(self):
        plan = build_ablation_plan(self.evidence)
        self.assertEqual(plan["model"]["model_id"], "gpt-5.6-sol")
        self.assertEqual(plan["model"]["endpoint"], "responses")
        self.assertFalse(plan["model"]["external_call_enabled"])
        self.assertFalse(plan["model"]["fine_tuning_used"])
        self.assertFalse(plan["model"]["custom_embedding_injection"])
        self.assertEqual(plan["transport"]["status"], "not_implemented_no_call")
        self.assertTrue(all(value == 0 for value in plan["access_counters"].values()))

    def test_target_reference_and_label_fields_are_forbidden_recursively(self):
        for field in ("target_text", "reference_text", "performed_label", "intended_sentence"):
            payload = copy.deepcopy(self.evidence)
            payload["items"][0][field] = "FORBIDDEN"
            with self.subTest(field=field), self.assertRaisesRegex(
                FoundationModelBridgeError, "forbidden field fragment"
            ):
                validate_synthetic_evidence(payload)

    def test_raw_signal_dense_embedding_and_identity_fields_are_forbidden(self):
        for field in ("raw_eeg", "signal_samples", "neurotoken_embedding", "participant_name"):
            payload = copy.deepcopy(self.evidence)
            payload["items"][0][field] = [0.0]
            with self.subTest(field=field), self.assertRaisesRegex(
                FoundationModelBridgeError, "forbidden field fragment"
            ):
                validate_synthetic_evidence(payload)

    def test_unknown_fields_fail_closed(self):
        payload = copy.deepcopy(self.evidence)
        payload["items"][0]["mystery"] = 1
        with self.assertRaisesRegex(FoundationModelBridgeError, "unknown fields"):
            validate_synthetic_evidence(payload)

    def test_noncausal_and_nonmonotonic_frames_fail_closed(self):
        payload = copy.deepcopy(self.evidence)
        payload["items"][0]["neural_key_frames"][0]["available_at_ms"] = 99
        with self.assertRaisesRegex(FoundationModelBridgeError, "before it is available"):
            validate_synthetic_evidence(payload)

        payload = copy.deepcopy(self.evidence)
        payload["items"][0]["neural_key_frames"][1]["start_ms"] = 50
        with self.assertRaisesRegex(FoundationModelBridgeError, "timestamps must be ordered"):
            validate_synthetic_evidence(payload)

    def test_invalid_probabilities_and_nan_fail_closed(self):
        payload = copy.deepcopy(self.evidence)
        keys = payload["items"][0]["neural_key_frames"][0]["top_keys"]
        keys[0]["probability"] = 0.6
        keys[1]["probability"] = 0.7
        with self.assertRaisesRegex(FoundationModelBridgeError, "probabilities must be descending"):
            validate_synthetic_evidence(payload)

        payload = copy.deepcopy(self.evidence)
        payload["items"][0]["ctc_nbest"][0]["log_probability"] = math.nan
        with self.assertRaisesRegex(FoundationModelBridgeError, "finite number"):
            validate_synthetic_evidence(payload)

    def test_nonzero_and_boolean_access_counters_fail_closed(self):
        for value in (1, True):
            payload = copy.deepcopy(self.evidence)
            payload["access_counters"]["provider_model_calls"] = value
            with self.subTest(value=value), self.assertRaisesRegex(
                FoundationModelBridgeError, "must be integer zero"
            ):
                validate_synthetic_evidence(payload)

    def test_plan_hash_and_derangement_tampering_fail_closed(self):
        plan = build_ablation_plan(self.evidence)
        tampered = copy.deepcopy(plan)
        tampered["conditions"][0]["request_sha256"] = "0" * 64
        with self.assertRaisesRegex(FoundationModelBridgeError, "request_sha256 mismatch"):
            validate_ablation_plan(tampered)

        tampered = copy.deepcopy(plan)
        tampered["derangement"]["rows"][0]["neural_source_item_id"] = "SYNTH-ITEM-00"
        tampered["derangement"]["rows_sha256"] = sha256_json(tampered["derangement"]["rows"])
        with self.assertRaisesRegex(FoundationModelBridgeError, "exact cyclic"):
            validate_ablation_plan(tampered)

        tampered = copy.deepcopy(plan)
        row = tampered["conditions"][1]
        row["blinded_request_payload"]["ctc_nbest"][0]["text"] = "MADE UP"
        row["request_sha256"] = sha256_json(row["blinded_request_payload"])
        hash_payload = dict(tampered)
        del hash_payload["plan_core_sha256"]
        tampered["plan_core_sha256"] = sha256_json(hash_payload)
        with self.assertRaisesRegex(FoundationModelBridgeError, "source-hash bound"):
            validate_ablation_plan(tampered)

    def test_file_roundtrip_replays_exact_plan_identity_and_measures_caps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence_path = root / "evidence.json"
            first_plan = root / "first.json"
            second_plan = root / "second.json"
            evidence_summary = make_synthetic_evidence_file(evidence_path)
            first_summary = build_ablation_plan_file(evidence_path, first_plan)
            second_summary = build_ablation_plan_file(evidence_path, second_plan)
            inspection = inspect_ablation_plan_file(first_plan)

            self.assertEqual(first_plan.read_bytes(), second_plan.read_bytes())
            self.assertEqual(
                first_summary["plan_core_sha256"], second_summary["plan_core_sha256"]
            )
            self.assertEqual(first_summary["plan_core_sha256"], inspection["plan_core_sha256"])
            self.assertLessEqual(evidence_summary["output_bytes"], MAX_INPUT_BYTES)
            self.assertLessEqual(first_summary["output_bytes"], MAX_OUTPUT_BYTES)
            self.assertEqual(first_summary["condition_count"], 12)
            self.assertFalse(inspection["external_call_enabled"])
            self.assertFalse(inspection["fine_tuning_used"])
            self.assertFalse(inspection["end_to_end_latency_measured"])
            self.assertTrue(all(value == 0 for value in inspection["access_counters"].values()))

    def test_input_output_and_overwrite_limits_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            oversized = root / "oversized.json"
            oversized.write_bytes(b"{" + b" " * MAX_INPUT_BYTES + b"}")
            with self.assertRaisesRegex(FoundationModelBridgeError, "exceeds"):
                load_json_object(oversized)

            output = root / "bounded.json"
            write_bounded_json(output, {"small": True})
            with self.assertRaises(FileExistsError):
                write_bounded_json(output, {"small": True})
            with self.assertRaisesRegex(FoundationModelBridgeError, "exceeds"):
                write_bounded_json(root / "tiny.json", {"large": "x" * 20}, maximum_bytes=8)

    def test_symlinked_input_and_output_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "real.json"
            real.write_text("{}\n", encoding="utf-8")
            link = root / "link.json"
            try:
                link.symlink_to(real)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(FoundationModelBridgeError, "symlinked JSON input"):
                load_json_object(link)
            with self.assertRaisesRegex(FoundationModelBridgeError, "symlinked JSON output"):
                write_bounded_json(link, {"small": True}, overwrite=True)

    def test_cli_help_and_bounded_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "evidence.json"
            plan = root / "plan.json"
            help_stdout = io.StringIO()
            with redirect_stdout(help_stdout):
                with self.assertRaises(SystemExit) as caught:
                    main(["build-foundation-model-ablation", "--help"])
            self.assertEqual(caught.exception.code, 0)
            self.assertIn("without contacting a provider", help_stdout.getvalue())

            outputs = []
            with redirect_stdout(io.StringIO()) as made:
                self.assertEqual(
                    main(["make-foundation-model-bridge-fixture", "--out", str(evidence)]),
                    0,
                )
            outputs.append(json.loads(made.getvalue()))
            with redirect_stdout(io.StringIO()) as built:
                self.assertEqual(
                    main(
                        [
                            "build-foundation-model-ablation",
                            "--evidence",
                            str(evidence),
                            "--out",
                            str(plan),
                        ]
                    ),
                    0,
                )
            outputs.append(json.loads(built.getvalue()))
            with redirect_stdout(io.StringIO()) as inspected:
                self.assertEqual(
                    main(["inspect-foundation-model-ablation", "--plan", str(plan)]),
                    0,
                )
            outputs.append(json.loads(inspected.getvalue()))

        self.assertEqual(outputs[0]["operation"], "make_synthetic_evidence")
        self.assertEqual(outputs[1]["operation"], "build_ablation_plan")
        self.assertEqual(outputs[2]["transport_status"], "not_implemented_no_call")
        self.assertEqual(outputs[1]["condition_count"], 12)
        self.assertTrue(
            all(
                all(summary["access_counters"][name] == 0 for name in ACCESS_COUNTER_FIELDS)
                for summary in outputs
            )
        )

    def test_cli_refuses_target_leakage_and_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "evidence.json"
            plan = root / "plan.json"
            leaked = copy.deepcopy(self.evidence)
            leaked["items"][0]["target_text"] = "NO"
            evidence.write_text(json.dumps(leaked), encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                self.assertEqual(
                    main(
                        [
                            "build-foundation-model-ablation",
                            "--evidence",
                            str(evidence),
                            "--out",
                            str(plan),
                        ]
                    ),
                    2,
                )
            self.assertIn("forbidden field fragment", stderr.getvalue())

            make_synthetic_evidence_file(evidence, overwrite=True)
            build_ablation_plan_file(evidence, plan)
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                self.assertEqual(
                    main(
                        [
                            "build-foundation-model-ablation",
                            "--evidence",
                            str(evidence),
                            "--out",
                            str(plan),
                        ]
                    ),
                    2,
                )
            self.assertIn("refusing to overwrite", stderr.getvalue())

    def test_committed_fixture_file_identity_is_stable(self):
        self.assertEqual(
            hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest(),
            "12f1b68f3241c80e4ba54872a3c97769e666ad2342f84328b1a5df91f0089bdb",
        )


if __name__ == "__main__":
    unittest.main()
