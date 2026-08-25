import importlib.util
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import bnci_2014_001_stage_q as q_core
from neurodecodekit.evaluation import bnci_2014_001_score as scorer
from neurodecodekit.evaluation import bnci_2014_001_stage_t_live as stage_t
from neurodecodekit.experiments import bnci_2014_001_cross_participant_eeg_gain as model_core
from neurodecodekit.experiments import bnci_2014_001_stage_p_live as stage_p

HAS_NUMPY = importlib.util.find_spec("numpy") is not None


def green_record(commit="1" * 40):
    return {
        "commit": commit,
        "CI_run_id": 1,
        "CI_head_sha": commit,
        "CI_conclusion": "success",
        "base_python_job_id": 2,
        "base_python_job_name": "Base Python",
        "base_python_job_conclusion": "success",
        "optional_neuro_readers_job_id": 3,
        "optional_neuro_readers_job_name": "Optional Neuro Readers",
        "optional_neuro_readers_job_conclusion": "success",
        "both_required_jobs_green": True,
    }


def implementation_artifacts():
    return [
        {"path": path, "bytes": 1, "sha256": "a" * 64}
        for path in stage_p.IMPLEMENTATION_ARTIFACTS
    ]


def stage_p_activation():
    return {
        "lane_id": stage_p.LANE_ID,
        "status": "remotely_green_stage_p_enabled",
        "green_stage_q_result": {
            "commit": stage_p.STAGE_Q_RESULT_COMMIT,
            "CI_run_id": stage_p.STAGE_Q_RESULT_CI_RUN_ID,
            "base_python_job_id": stage_p.STAGE_Q_RESULT_BASE_JOB_ID,
            "optional_neuro_readers_job_id": stage_p.STAGE_Q_RESULT_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "green_implementation": green_record(),
        "implementation_artifacts": implementation_artifacts(),
        "authority": {
            "one_real_Stage_P_execution": True,
            "parameter_update_fits_maximum": 540,
            "prediction_sets_maximum": 900,
            "held_out_E_target_delivery": False,
            "held_out_T_signal_or_target_delivery": False,
            "Stage_T": False,
            "reruns": 0,
            "post_target_updates": 0,
            "claim_upgrade": False,
        },
    }


def stage_t_activation():
    return {
        "lane_id": stage_t.LANE_ID,
        "status": "remotely_green_one_score_enabled",
        "green_implementation": green_record(),
        "green_prediction_freeze": green_record("2" * 40),
        "prediction_freeze_artifact": {
            "path": stage_p.PUBLIC_FREEZE_RELATIVE_PATH.as_posix(),
            "bytes": 1,
            "sha256": "b" * 64,
        },
        "implementation_artifacts": implementation_artifacts(),
        "authority": {
            "one_target_delivery_of_nine_sealed_fold_sets": True,
            "one_aggregate_score": True,
            "post_target_updates": 0,
            "reruns": 0,
            "held_out_T_delivery": False,
            "individual_prediction_probability_target_or_participant_outcome_public": False,
            "maximum_route": "BNCIC3C5-R5",
        },
    }


def identity_rows(participant="A01", session="E"):
    return [
        {
            "participant": participant,
            "session": session,
            "run_ordinal": run,
            "trial_ordinal": trial,
            "opaque_row_id": q_core._row_id(participant, session, run, trial),
        }
        for run in range(6)
        for trial in range(48)
    ]


def fold_prediction_rows(participant="A01"):
    rows = []
    for identity in identity_rows(participant):
        for condition in scorer.CONDITIONS:
            rows.append(
                {
                    **identity,
                    "condition": condition,
                    "probabilities": [0.25, 0.25, 0.25, 0.25],
                }
            )
    return sorted(rows, key=scorer._prediction_sort_key)


class TestStagePControlPlane(unittest.TestCase):
    def test_plan_is_exact_and_target_blind(self):
        plan = stage_p.plan_stage_p()
        self.assertEqual(plan["fits"], 468)
        self.assertEqual(plan["prediction_sets"], 495)
        self.assertEqual(plan["private_prediction_rows"], 41_472)
        self.assertEqual(plan["held_out_T_rows_used"], 0)
        self.assertEqual(plan["target_deliveries"], 0)
        self.assertEqual(plan["scores"], 0)

    def test_activation_is_strict(self):
        self.assertEqual(stage_p.validate_activation_document(stage_p_activation())["lane_id"], stage_p.LANE_ID)
        for mutation in (
            lambda value: value.update(status="enabled"),
            lambda value: value["authority"].update(Stage_T=True),
            lambda value: value["green_stage_q_result"].update(commit="0" * 40),
            lambda value: value["implementation_artifacts"].pop(),
        ):
            value = stage_p_activation()
            mutation(value)
            with self.assertRaises(stage_p.BNCIStagePRefusal):
                stage_p.validate_activation_document(value)

    def test_exact_grid_rejects_missing_duplicate_and_out_of_range_rows(self):
        rows = identity_rows()
        stage_p.validate_exact_identity_grid(rows, participant_sessions=[("A01", "E")])
        with self.assertRaises(stage_p.BNCIStagePRefusal):
            stage_p.validate_exact_identity_grid(rows[:-1], participant_sessions=[("A01", "E")])
        duplicate = [dict(row) for row in rows]
        duplicate[-1] = dict(duplicate[0])
        with self.assertRaises(stage_p.BNCIStagePRefusal):
            stage_p.validate_exact_identity_grid(duplicate, participant_sessions=[("A01", "E")])
        out_of_range = [dict(row) for row in rows]
        out_of_range[-1]["trial_ordinal"] = 48
        with self.assertRaises(stage_p.BNCIStagePRefusal):
            stage_p.validate_exact_identity_grid(out_of_range, participant_sessions=[("A01", "E")])

    def test_prediction_firewall_requires_exact_six_by_48_grid_and_conditions(self):
        rows = fold_prediction_rows()
        stage_p.validate_fold_predictions("A01", rows)
        malformed = [dict(row) for row in rows]
        malformed[-1] = dict(malformed[-1], trial_ordinal=48)
        with self.assertRaises(stage_p.BNCIStagePRefusal):
            stage_p.validate_fold_predictions("A01", malformed)
        with self.assertRaises(stage_p.BNCIStagePRefusal):
            stage_p.validate_fold_predictions("A01", rows[:-1])

    def test_source_commitment_is_keyed_and_deterministic(self):
        payload = b'{"private":"manifest"}\n'
        key = b"k" * 32
        first = stage_p.source_capability_commitment(payload, key)
        self.assertEqual(first, stage_p.source_capability_commitment(payload, key))
        self.assertNotEqual(first, stage_p.source_capability_commitment(payload, b"z" * 32))
        self.assertNotEqual(first, stage_p._sha256(payload))

    def test_target_transport_inventory_has_no_private_paths(self):
        artifacts = [
            {
                "role": "sealed_scoring_targets",
                "fold": participant,
                "file": f"scoring_target_vault/fold_{participant}.sealed.v0.bin",
                "bytes": 10,
                "sha256": str(index + 1) * 64,
            }
            for index, participant in enumerate(stage_p.PARTICIPANTS)
        ]
        artifacts.append(
            {
                "role": "scoring_key_vault_sealed_until_T",
                "file": "separate_fixed_private_path_not_in_fold_capability_tree",
                "bytes": 20,
                "sha256": "f" * 64,
            }
        )
        inventory = stage_p._target_transport_inventory({"artifacts": artifacts})
        self.assertEqual(len(inventory), 10)
        self.assertFalse(any("file" in row or "path" in row for row in inventory))


@unittest.skipUnless(HAS_NUMPY, "generated Stage P shards require NumPy")
class TestGeneratedFoldCapability(unittest.TestCase):
    def _write_fixture(self, root: Path, *, leak_held_target=False):
        import numpy as np

        shards = {}
        for participant_index, participant in enumerate(stage_p.PARTICIPANTS):
            for session_index, session in enumerate(q_core.SESSIONS):
                identities = identity_rows(participant, session)
                arrays = {
                    name: np.zeros((288, dimension), dtype="float32")
                    for name, dimension in q_core.FEATURE_DIMENSIONS.items()
                }
                arrays.update(
                    {
                        "participant_index": np.full(288, participant_index, dtype="uint8"),
                        "session_index": np.full(288, session_index, dtype="uint8"),
                        "run_ordinal": np.asarray([row["run_ordinal"] for row in identities], dtype="uint8"),
                        "trial_ordinal": np.asarray([row["trial_ordinal"] for row in identities], dtype="uint8"),
                        "trial_start_sample": np.arange(288, dtype="int32") * 100,
                        "opaque_row_id": np.asarray([row["opaque_row_id"].encode() for row in identities], dtype="S64"),
                    }
                )
                payload = q_core.deterministic_npz_bytes(arrays)
                relative = f"participant_signal_shards/{participant}{session}.target_free.private.v0.npz"
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                shards[(participant, session)] = {
                    "role": "target_free_participant_session_signal_shard",
                    "participant": participant,
                    "session": session,
                    "file": relative,
                    "rows": 288,
                    "bytes": len(payload),
                    "sha256": stage_p._sha256(payload),
                }
        held = "A01"
        delivered = []
        source_identities = []
        for participant in stage_p.PARTICIPANTS:
            if participant == held:
                continue
            for session in q_core.SESSIONS:
                delivered.append({**shards[(participant, session)], "delivery_role": "source_signal"})
                source_identities.extend(identity_rows(participant, session))
        delivered.append({**shards[(held, "E")], "delivery_role": "held_out_E_signal"})
        target_ids = [row["opaque_row_id"] for row in source_identities]
        if leak_held_target:
            target_ids[-1] = identity_rows(held, "E")[0]["opaque_row_id"]
        target_payload = q_core.deterministic_npz_bytes(
            {
                "opaque_row_id": np.asarray([value.encode() for value in target_ids], dtype="S64"),
                "target_index": np.asarray([index % 4 for index in range(len(target_ids))], dtype="uint8"),
            }
        )
        target_relative = "fold_capabilities/fold_A01.source_targets.private.v0.npz"
        (root / target_relative).parent.mkdir(parents=True, exist_ok=True)
        (root / target_relative).write_bytes(target_payload)
        delivery = {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_q_fold_delivery",
            "schema_version": "0.1.0",
            "fold": held,
            "signal_shards": delivered,
            "source_target_capability": {
                "file": target_relative,
                "rows": 4608,
                "bytes": len(target_payload),
                "sha256": stage_p._sha256(target_payload),
            },
            "held_out_E_rows": 288,
            "held_out_T_rows": 288,
            "held_out_T_rows_delivered": 0,
            "future_delivery": "exact_listed_bytes_only_no_repository_root_or_scoring_key_path",
        }
        (root / "fold_capabilities" / "fold_A01.delivery.private.v0.json").write_bytes(
            stage_p._canonical_bytes(delivery)
        )

    def test_generated_exact_shape_fold_loads_without_held_out_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_fixture(root)
            source, held, targets, capability = stage_p.load_fold_capability(root, "A01")
            self.assertEqual(len(source), 4608)
            self.assertEqual(len(held), 288)
            self.assertEqual(len(targets), 4608)
            self.assertFalse({row["opaque_row_id"] for row in held} & set(targets))
            self.assertEqual(capability["held_out_T_rows_delivered"], 0)

    def test_generated_target_leakage_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_fixture(root, leak_held_target=True)
            with self.assertRaises(stage_p.BNCIStagePRefusal):
                stage_p.load_fold_capability(root, "A01")

    def test_generated_exact_shape_fold_runs_the_frozen_schedule(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_fixture(root)
            source, held, targets, _capability = stage_p.load_fold_capability(root, "A01")
            result = model_core._run_single_fold("A01", source, held, targets)
            stage_p.validate_fold_predictions("A01", result["predictions"])
            self.assertEqual(result["fit_count"], 52)
            self.assertEqual(result["prediction_sets"], 55)
            self.assertEqual(result["model_inference_runs"], 55)


class TestStageTControlPlane(unittest.TestCase):
    def test_plan_is_one_score_only(self):
        plan = stage_t.plan_stage_t()
        self.assertEqual(plan["target_deliveries"], 1)
        self.assertEqual(plan["scores"], 1)
        self.assertEqual(plan["post_target_updates"], 0)
        self.assertEqual(plan["reruns"], 0)

    def test_activation_is_strict(self):
        self.assertEqual(stage_t.validate_activation_document(stage_t_activation())["lane_id"], stage_t.LANE_ID)
        value = stage_t_activation()
        value["authority"]["post_target_updates"] = 1
        with self.assertRaises(stage_t.BNCIStageTRefusal):
            stage_t.validate_activation_document(value)

    def test_public_freeze_rejects_target_delivery_or_wrong_inventory(self):
        value = {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_p_prediction_freeze",
            "lane_id": stage_p.LANE_ID,
            "status": "frozen_target_blind_predictions_targets_and_scoring_keys_still_sealed",
            "folds": 9,
            "held_out_E_rows_per_fold": 288,
            "held_out_T_rows_used": 0,
            "private_prediction_rows": 41_472,
            "prediction_set_sha256": "1" * 64,
            "condition_sha256": {condition: "2" * 64 for condition in scorer.CONDITIONS},
            "configuration_hash": "3" * 64,
            "code_hash": "4" * 64,
            "split_protocol_hash": "5" * 64,
            "source_capability_HMAC_commitment": "6" * 64,
            "sealed_target_transport_commitment_sha256": "7" * 64,
            "operation_counters": {
                "parameter_update_fits": 468,
                "prediction_sets": 495,
                "target_deliveries": 0,
                "scores": 0,
            },
            "scientific_claim_established": False,
        }
        stage_t.validate_public_freeze(value)
        value["operation_counters"]["target_deliveries"] = 1
        with self.assertRaises(stage_t.BNCIStageTRefusal):
            stage_t.validate_public_freeze(value)

    def test_claim_routes_remain_narrow(self):
        for route in ("BNCIC3C5-R2", "BNCIC3C5-R3", "BNCIC3C5-R4", "BNCIC3C5-R5"):
            boundary = stage_t._claim_boundary(route)
            self.assertIn("not_established", boundary)
            self.assertIn("thought or language", boundary["not_established"])


if __name__ == "__main__":
    unittest.main()
