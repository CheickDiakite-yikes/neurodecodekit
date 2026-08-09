import hashlib
import json
import math
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/causal_motor_lattice_synthetic_contract.v0.json"
DOC_PATH = ROOT / "docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_PREREGISTRATION.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CausalMotorLatticeSyntheticContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_is_synthetic_only_unimplemented_and_unexecuted(self):
        self.assertEqual(
            self.contract["status"],
            "preregistered_tier_B_synthetic_only_not_implemented_not_executed",
        )
        scope = self.contract["scope"]
        self.assertTrue(scope["exact_CML_v0_architecture_implementation"])
        self.assertTrue(scope["synthetic_fixture_replay"])
        self.assertFalse(scope["real_or_public_data_access"])
        self.assertFalse(scope["protected_target_access"])
        self.assertFalse(scope["scientific_scoring_or_claim_upgrade"])
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )

    def test_every_source_binding_matches_exactly(self):
        for source in self.contract["source_bindings"].values():
            self.assertEqual(source["sha256"], sha256(ROOT / source["path"]), source["path"])

    def test_pair_anchor_split_and_gradient_boundary_are_exact(self):
        adapter = self.contract["pair_anchored_adapter"]
        self.assertEqual(adapter["crop_samples"], 96)
        self.assertEqual(adapter["left_filter_context_samples"], 32)
        self.assertEqual(adapter["analysis_samples"], 64)
        self.assertEqual(adapter["right_context_samples"], 0)
        self.assertTrue(adapter["same_crop_bounds_required_for_both_pair_members"])
        protocol = self.contract["partition_and_target_protocol"]
        self.assertEqual(protocol["parameter_update_rows"], 24)
        self.assertEqual(protocol["check_rows"], 32)
        self.assertEqual(protocol["final_rows"], 16)
        self.assertTrue(protocol["final_target_delivery_requires_all_check_gates"])
        self.assertFalse(protocol["check_or_final_target_may_update_parameters"])
        self.assertFalse(protocol["selection_from_check_or_final"])

    def test_projection_formula_replays_registered_float32_hash(self):
        projection = self.contract["synthetic_projection"]
        payload = bytearray()
        for output_index in range(64):
            group = output_index // 8
            base = output_index % 8
            row = [0.0] * 8
            row[base] = 1.0
            row[(base + 1) % 8] = 0.05 * (1.0 if group % 2 == 0 else -1.0)
            row[(base + 4) % 8] = 0.01 * (group - 3.5)
            norm = math.sqrt(sum(value * value for value in row))
            for value in row:
                payload.extend(struct.pack("<f", value / norm))
        self.assertEqual(len(payload), projection["matrix_bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), projection["matrix_sha256"])
        self.assertEqual(projection["matrix_rank"], 8)
        self.assertEqual(projection["output_channel_names"], [f"CML_SYN{i:02d}" for i in range(64)])
        self.assertFalse(projection["geometry_available"])
        self.assertFalse(projection["target_or_label_dependent"])

    def test_filters_have_exact_lengths_hashes_and_causal_context(self):
        filters = self.contract["causal_filter_bank"]
        self.assertEqual(filters["tap_count"], 33)
        self.assertEqual(filters["valid_output_samples"], 64)
        self.assertEqual(filters["required_left_context_samples"], 32)
        self.assertFalse(filters["downsampling_applied"])
        self.assertEqual(filters["anti_alias_response"], "not_applicable_no_downsampling")
        for band in ("mu", "beta"):
            coefficients = filters[band]["coefficients_float64"]
            payload = b"".join(struct.pack("<d", value) for value in coefficients)
            self.assertEqual(len(coefficients), 33)
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                filters[band]["little_endian_float64_sha256"],
            )
        for field in (
            "centered_filter_allowed",
            "zero_phase_filter_allowed",
            "reflected_future_padding_allowed",
            "circular_padding_allowed",
            "sample_at_or_after_event_allowed",
        ):
            self.assertFalse(filters[field], field)

    def test_parameter_ledger_and_lattice_hash_are_exact(self):
        ledger = self.contract["architecture"]["parameter_ledger"]
        self.assertEqual(sum(value for key, value in ledger.items() if key != "total_trainable_parameters"), 4535)
        self.assertEqual(ledger["total_trainable_parameters"], 4535)
        lattice = self.contract["synthetic_lattice"]
        payload = bytearray()
        for key_index in range(29):
            row = [0] * 18
            if key_index < 28:
                local = key_index % 14
                hand = 0 if key_index < 14 else 1
                for primitive in (
                    hand,
                    2 + (local % 4),
                    6 + ((local // 4) % 4),
                    10 + (local % 7),
                ):
                    row[primitive] = 1
            else:
                row[17] = 1
            payload.extend(row)
        self.assertEqual(len(payload), lattice["incidence_bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), lattice["incidence_sha256"])
        self.assertEqual(lattice["incidence_shape"], [29, 18])
        self.assertFalse(self.contract["architecture"]["independent_hand_head"])

    def test_recipe_metrics_replay_and_stop_rules_are_frozen(self):
        recipe = self.contract["training_recipe"]
        self.assertEqual(recipe["parameter_update_runs"], 1)
        self.assertEqual(recipe["random_seed"], 5513)
        self.assertEqual(recipe["optimizer_steps"], 600)
        self.assertFalse(recipe["early_stopping"])
        self.assertFalse(recipe["checkpoint_selection"])
        self.assertFalse(recipe["rerun_allowed"])
        self.assertEqual(self.contract["check_acceptance_gates"]["signal_bearing_hand_accuracy_minimum"], 0.875)
        self.assertEqual(self.contract["conditional_final_acceptance_gates"]["signal_bearing_key_accuracy_minimum"], 0.75)
        replay = self.contract["replay_contract"]
        self.assertFalse(replay["second_training_run_allowed"])
        self.assertEqual(replay["checkpoint_loads"], 1)
        self.assertTrue(replay["byte_identical_prediction_hash_required"])
        order = self.contract["execution_order"]
        self.assertTrue(order["contract_commit_must_be_pushed_and_remotely_green_before_implementation"])
        self.assertTrue(order["exact_implementation_commit_must_be_pushed_and_remotely_green_before_execution"])
        self.assertTrue(order["failed_check_or_final_is_retained_without_rerun"])

    def test_resources_refusals_and_authorization_fail_closed(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["maximum_CPU_threads"], 1)
        self.assertEqual(caps["maximum_workers"], 1)
        self.assertEqual(caps["maximum_wall_seconds"], 600)
        self.assertEqual(caps["maximum_peak_RSS_bytes"], 512 * 1024 * 1024)
        self.assertEqual(caps["maximum_generated_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(caps["minimum_free_disk_bytes_before"], 20 * 1024 * 1024 * 1024)
        refusals = self.contract["required_refusal_matrix"]
        self.assertEqual(len(refusals), 24)
        self.assertEqual(len(refusals), len(set(refusals)))
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["tier_B_exact_synthetic_implementation_allowed_only_after_contract_remote_green"])
        self.assertTrue(authorization["tier_B_one_registered_execution_allowed_only_after_exact_implementation_remote_green"])
        for field in (
            "real_public_or_protected_data_access_allowed",
            "S20_or_PhysioNet_access_allowed",
            "download_network_or_provider_access_allowed",
            "pretrained_model_language_model_or_external_embedding_allowed",
            "stream_device_hardware_or_release_allowed",
            "scientific_claim_upgrade_allowed",
            "existing_loop54_or_loop55_artifact_amendment_allowed",
        ):
            self.assertFalse(authorization[field], field)

    def test_docs_and_tracker_preserve_phase_and_claim_ceiling(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability if all gates pass", document)
        self.assertIn("Scientific claim not established even if all gates pass", document)
        row = next(line for line in queue.splitlines() if line.startswith("| 13 |"))
        self.assertIn("Contract Frozen", row)
        self.assertIn("Implementation Qualified Locally", row)
        self.assertEqual(sum(line.startswith("| ") for line in queue.splitlines()), 21)


if __name__ == "__main__":
    unittest.main()
