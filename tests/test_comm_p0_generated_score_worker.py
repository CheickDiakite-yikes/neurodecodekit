from __future__ import annotations

import ast
import hashlib
import hmac
import json
import os
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated_score_only as score_only
from neurodecodekit.experiments import comm_p0_generated_score_worker as worker

ROOT = Path(__file__).resolve().parents[1]
KEY = b"COMM-P0-G generated score-worker fixture HMAC key v0"


def _contract() -> dict[str, object]:
    conditions = [
        "equal_prior",
        "cue_only",
        "all_recorded_peripheral_P",
        "P_plus_residual_central_EEG",
        "P_plus_class_destroyed_residual_central_EEG",
    ]
    return {
        "schema_version": "0.1.0",
        "gate_id": "COMM-P0-G-v0",
        "conditions": conditions,
        "trial_grammar": {"commands": ["yes", "no", "help", "stop"]},
        "participant_first_scoring": {
            "primary_condition": "P_plus_residual_central_EEG",
            "primary_log_loss_comparators": [
                "all_recorded_peripheral_P",
                "P_plus_class_destroyed_residual_central_EEG",
            ],
            "balanced_accuracy_comparator_inventory": [
                "equal_prior",
                "cue_only",
                "all_recorded_peripheral_P",
            ],
            "mean_margin_nats_per_item_minimum": 0.03,
            "positive_participants_minimum": 2,
            "complete_participants_denominator": 2,
            "exact_one_sided_sign_flip_p_maximum": 0.25,
            "balanced_accuracy_margin_minimum": 0.05,
            "probability_floor": 0.000001,
            "maximum_frozen_log_loss": 13.815510557964274,
            "participant_metric_decimal_places": 12,
        },
        "live_metrics": {
            "stable_commit_coverage_fraction_minimum": 0.70,
            "per_command_coverage_fraction_minimum": 0.50,
            "false_commits_per_inactive_minute_maximum": 0.10,
            "dropped_or_invalid_chunk_fraction_maximum": 0.01,
            "frames_processed_before_next_deadline_fraction_minimum": 0.99,
            "stable_commit_latency_median_seconds_maximum": 2.5,
            "stable_commit_latency_p95_seconds_maximum": 5.0,
            "capture_to_presentation_processing_overhead_p95_seconds_maximum": 0.5,
        },
    }


def _fixture() -> tuple[
    dict[str, object],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, int],
]:
    contract = _contract()
    trials: list[dict[str, object]] = []
    targets: dict[str, int] = {}
    for cohort_index, cohort in enumerate(score_only.COHORTS):
        participants = [f"P-{cohort_index + 1}-{index + 1:02d}" for index in range(2)]
        phases = ["shadow", "live"] if cohort == "independent_replication" else ["shadow"]
        for participant in participants:
            for phase in phases:
                for endpoint in score_only.ENDPOINTS:
                    for command in range(4):
                        item_id = f"{participant}-{phase}-{endpoint}-{command}"
                        trials.append(
                            {
                                "item_id": item_id,
                                "cohort_id": cohort,
                                "participant_id": participant,
                                "phase": phase,
                                "endpoint": endpoint,
                                "role": endpoint,
                            }
                        )
                        targets[item_id] = command

    predictions: list[dict[str, object]] = []
    for trial in trials:
        truth = targets[str(trial["item_id"])]
        for condition in contract["conditions"]:
            probabilities = [0.05, 0.05, 0.05, 0.05]
            if condition == "P_plus_residual_central_EEG" or (
                condition == "cue_only" and trial["endpoint"] == "prompted_intend"
            ):
                probabilities[truth] = 0.85
            else:
                probabilities = [0.10, 0.10, 0.10, 0.10]
                probabilities[(truth + 1) % 4] = 0.70
            predictions.append(
                {
                    "item_id": trial["item_id"],
                    "cohort_id": trial["cohort_id"],
                    "participant_id": trial["participant_id"],
                    "endpoint": trial["endpoint"],
                    "phase": trial["phase"],
                    "condition": condition,
                    "probabilities": probabilities,
                }
            )

    observations: list[dict[str, object]] = []
    live_trials = [
        trial
        for trial in trials
        if trial["cohort_id"] == "independent_replication" and trial["phase"] == "live"
    ]
    for trial in live_trials:
        observations.append(
            {
                "interval_id": trial["item_id"],
                "cohort_id": trial["cohort_id"],
                "participant_id": trial["participant_id"],
                "endpoint": trial["endpoint"],
                "phase": trial["phase"],
                "active_intent": True,
                "inactive_surface": None,
                "duration_seconds": 3.0,
                "stable_commit": True,
                "predicted_command_index": targets[str(trial["item_id"])],
                "commit_count": 1,
                "invalid_chunk_count": 0,
                "total_chunk_count": 10,
                "processed_frame_count": 100,
                "total_frame_count": 100,
                "first_output_latency_seconds": 0.4,
                "stable_commit_latency_seconds": 1.5,
                "capture_to_presentation_overhead_seconds": 0.1,
                "clock_map_verified": True,
            }
        )
    participants = sorted({str(row["participant_id"]) for row in live_trials})
    for participant in participants:
        for surface in sorted(score_only.INACTIVE_SURFACES):
            observations.append(
                {
                    "interval_id": f"{participant}-inactive-{surface}",
                    "cohort_id": "independent_replication",
                    "participant_id": participant,
                    "endpoint": None,
                    "phase": "live",
                    "active_intent": False,
                    "inactive_surface": surface,
                    "duration_seconds": 120.0,
                    "stable_commit": False,
                    "predicted_command_index": None,
                    "commit_count": 0,
                    "invalid_chunk_count": 0,
                    "total_chunk_count": 10,
                    "processed_frame_count": 100,
                    "total_frame_count": 100,
                    "first_output_latency_seconds": None,
                    "stable_commit_latency_seconds": None,
                    "capture_to_presentation_overhead_seconds": None,
                    "clock_map_verified": True,
                }
            )
    return contract, trials, predictions, observations, targets


def _ndjson(records: list[dict[str, object]]) -> bytes:
    return b"".join(score_only.canonical_json_bytes(record) for record in records)


def _identity(path: Path) -> dict[str, object]:
    descriptor_stat = path.stat()
    payload = path.read_bytes()
    return {
        "device": descriptor_stat.st_dev,
        "inode": descriptor_stat.st_ino,
        "size_bytes": descriptor_stat.st_size,
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


class CommP0GeneratedScoreWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        worker._CONSUMED_TARGET_IDENTITIES.clear()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.contract, self.trials, self.predictions, self.observations, self.targets = _fixture()
        self.paths = {
            "contract": self.root / "contract.json",
            "trial_manifest": self.root / "trials.ndjson",
            "prediction_stream": self.root / "predictions.ndjson",
            "live_observations": self.root / "live.ndjson",
            "freeze_attestation": self.root / "freeze.json",
            "target_envelope": self.root / "targets.json",
            "aggregate_output": self.root / "aggregate.json",
        }
        self.paths["contract"].write_bytes(score_only.canonical_json_bytes(self.contract))
        self.paths["trial_manifest"].write_bytes(_ndjson(self.trials))
        self.paths["prediction_stream"].write_bytes(_ndjson(self.predictions))
        self.paths["live_observations"].write_bytes(_ndjson(self.observations))
        self.paths["target_envelope"].write_bytes(score_only.canonical_json_bytes(self.targets))
        self._write_attestation()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _attestation_body(self) -> dict[str, object]:
        return {
            "schema_name": worker.ATTESTATION_SCHEMA,
            "schema_version": worker.SCHEMA_VERSION,
            "gate_id": self.contract["gate_id"],
            "bound_inputs": {name: _identity(self.paths[name]) for name in worker._BOUND_SURFACES},
            "score_only_prediction_freeze": score_only.build_prediction_freeze_attestation(
                self.predictions, self.contract
            ),
            "authorization": {
                "prediction_freeze_green": True,
                "replication_artifact_freeze_green": True,
                "one_shot": True,
                "target_delivery_count": 1,
                "prior_score_count": 0,
            },
            "target_descriptor_open_count_at_freeze": 0,
            "target_delivery_count_at_freeze": 0,
            "score_count_at_freeze": 0,
        }

    def _write_attestation(self, body: dict[str, object] | None = None) -> None:
        value = body or self._attestation_body()
        value = dict(value)
        value["attestation_hmac_sha256"] = hmac.new(
            KEY,
            score_only.canonical_json_bytes(value),
            hashlib.sha256,
        ).hexdigest()
        self.paths["freeze_attestation"].write_bytes(score_only.canonical_json_bytes(value))

    def _open_descriptors(
        self,
        *,
        modes: dict[str, int] | None = None,
        output_name: str = "aggregate_output",
    ) -> dict[str, int]:
        modes = modes or {}
        descriptors = {
            name: os.open(self.paths[name], modes.get(name, os.O_RDONLY))
            for name in (
                "contract",
                "trial_manifest",
                "prediction_stream",
                "freeze_attestation",
                "target_envelope",
                "live_observations",
            )
        }
        output_path = self.paths[output_name]
        descriptors["aggregate_output"] = os.open(
            output_path,
            modes.get("aggregate_output", os.O_WRONLY | os.O_CREAT | os.O_EXCL),
            0o600,
        )
        return descriptors

    def _invoke(self, descriptors: dict[str, int], **caps: int) -> dict[str, object]:
        return worker.descriptor_main(
            contract_fd=descriptors["contract"],
            trial_manifest_fd=descriptors["trial_manifest"],
            prediction_stream_fd=descriptors["prediction_stream"],
            freeze_attestation_fd=descriptors["freeze_attestation"],
            target_envelope_fd=descriptors["target_envelope"],
            live_observations_fd=descriptors["live_observations"],
            aggregate_output_fd=descriptors["aggregate_output"],
            hmac_key=KEY,
            **caps,
        )

    def _close(self, descriptors: dict[str, int]) -> None:
        for descriptor in descriptors.values():
            try:
                os.close(descriptor)
            except OSError:
                pass

    def _run(self, descriptors: dict[str, int], **caps: int) -> dict[str, object]:
        try:
            return self._invoke(descriptors, **caps)
        finally:
            self._close(descriptors)

    def test_descriptor_only_score_emits_canonical_aggregate(self) -> None:
        result = self._run(self._open_descriptors())
        payload = self.paths["aggregate_output"].read_bytes()
        self.assertEqual(payload, score_only.canonical_json_bytes(result))
        self.assertEqual(result["target_delivery_count"], 1)
        self.assertEqual(result["score_count"], 1)
        self.assertFalse(result["scientific_claim_established"])
        encoded = payload.decode("ascii")
        for forbidden in (
            '"item_id"',
            '"participant_id"',
            '"probabilities"',
            '"predicted_command_index"',
            '"targets"',
        ):
            self.assertNotIn(forbidden, encoded)

    def test_wrong_fd_mode_and_nonregular_fd_are_refused(self) -> None:
        descriptors = self._open_descriptors(modes={"contract": os.O_RDWR})
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "descriptor_access_mode"):
            self._run(descriptors)

        self.paths["aggregate_output"].unlink(missing_ok=True)
        descriptors = self._open_descriptors()
        read_fd, write_fd = os.pipe()
        os.close(write_fd)
        os.close(descriptors["live_observations"])
        descriptors["live_observations"] = read_fd
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "descriptor_type_or_link"):
            self._run(descriptors)

        self.paths["aggregate_output"].unlink(missing_ok=True)
        os.link(self.paths["contract"], self.root / "contract-hard-link.json")
        descriptors = self._open_descriptors()
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "descriptor_type_or_link"):
            self._run(descriptors)

    def test_bad_hmac_never_reads_target_descriptor(self) -> None:
        attestation = json.loads(self.paths["freeze_attestation"].read_bytes())
        attestation["attestation_hmac_sha256"] = "0" * 64
        self.paths["freeze_attestation"].write_bytes(score_only.canonical_json_bytes(attestation))
        descriptors = self._open_descriptors()
        target_fd = descriptors["target_envelope"]
        try:
            with self.assertRaisesRegex(
                score_only.ScoreOnlyRefusal, "prediction_row_or_probability_tamper"
            ):
                self._invoke(descriptors)
            self.assertEqual(os.lseek(target_fd, 0, os.SEEK_CUR), 0)
        finally:
            self._close(descriptors)

    def test_tampered_prediction_identity_prevents_target_delivery(self) -> None:
        payload = bytearray(self.paths["prediction_stream"].read_bytes())
        payload[payload.index(b"0.85")] = ord("9")
        self.paths["prediction_stream"].write_bytes(payload)
        descriptors = self._open_descriptors()
        target_fd = descriptors["target_envelope"]
        try:
            with self.assertRaisesRegex(
                score_only.ScoreOnlyRefusal, "descriptor_identity_mismatch"
            ):
                self._invoke(descriptors)
            self.assertEqual(os.lseek(target_fd, 0, os.SEEK_CUR), 0)
        finally:
            self._close(descriptors)

    def test_target_fd_mode_is_checked_only_after_valid_freeze(self) -> None:
        descriptors = self._open_descriptors(modes={"target_envelope": os.O_RDWR})
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "descriptor_access_mode"):
            self._run(descriptors)

    def test_target_delivery_and_score_cannot_repeat(self) -> None:
        self._run(self._open_descriptors())
        self.paths["aggregate_output_2"] = self.root / "aggregate-2.json"
        descriptors = self._open_descriptors(output_name="aggregate_output_2")
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "repeated_score_or_target"):
            self._run(descriptors)

    def test_malformed_target_is_consumed_before_scoring(self) -> None:
        target_path = self.paths["target_envelope"]
        target_path.write_bytes(b'{"malformed":}\n')
        descriptors = self._open_descriptors()
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "noncanonical_input"):
            self._run(descriptors)

        self.paths["aggregate_output"].unlink(missing_ok=True)
        target_path.write_bytes(score_only.canonical_json_bytes(self.targets))
        descriptors = self._open_descriptors()
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "repeated_score_or_target"):
            self._run(descriptors)

    def test_noncanonical_and_oversized_inputs_are_refused(self) -> None:
        self.paths["contract"].write_text(json.dumps(self.contract), encoding="utf-8")
        descriptors = self._open_descriptors()
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "noncanonical_input"):
            self._run(descriptors)

        self.paths["aggregate_output"].unlink(missing_ok=True)
        self.paths["contract"].write_bytes(score_only.canonical_json_bytes(self.contract))
        self._write_attestation()
        descriptors = self._open_descriptors()
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "bounded_input_violation"):
            self._run(descriptors, input_byte_cap=64)

    def test_forbidden_import_and_capability_audit(self) -> None:
        path = ROOT / "src/neurodecodekit/experiments/comm_p0_generated_score_worker.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        called_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
        forbidden_roots = {
            "subprocess",
            "socket",
            "urllib",
            "http",
            "pathlib",
            "numpy",
            "sklearn",
            "scipy",
            "torch",
            "mne",
        }
        self.assertFalse({name.split(".", 1)[0] for name in imported} & forbidden_roots)
        self.assertFalse({"open", "exec", "eval", "compile", "__import__"} & called_names)
        source = path.read_text(encoding="utf-8")
        for forbidden_module in (
            "comm_p0_generated_qualification",
            "comm_p0_generated_runner",
            "comm_p0_generated_numerical",
            "comm_p0_generated_model_worker",
        ):
            self.assertNotIn(forbidden_module, source)
        audit = worker.capability_audit()
        self.assertFalse(audit["accepts_paths"])
        self.assertFalse(audit["fit_or_model_capability"])
        self.assertFalse(audit["subprocess_capability"])
        self.assertFalse(audit["network_capability"])
        self.assertFalse(audit["row_level_output_capability"])
        self.assertFalse(audit["official_qualification_executed"])


if __name__ == "__main__":
    unittest.main()
