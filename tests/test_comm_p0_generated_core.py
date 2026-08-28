from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as p0

ROOT = Path(__file__).resolve().parents[1]


class CommP0GeneratedCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = p0.load_contract(ROOT)

    def test_plan_is_bounded_generated_only_and_cli_matches(self) -> None:
        plan = p0.plan(ROOT)
        self.assertEqual(plan["gate_id"], "COMM-P0-G-v0")
        self.assertEqual(plan["complete_fictional_participants"], 42)
        self.assertEqual(plan["structural_rows_per_replay"], 10_752)
        self.assertEqual(plan["prediction_rows_per_replay"], 91_392)
        self.assertEqual(plan["refusal_families_per_replay"], 70)
        self.assertFalse(plan["official_qualification_authorized_now"])
        self.assertFalse(plan["real_or_private_data_allowed"])
        self.assertEqual(plan["network_bytes"], 0)
        completed = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.comm_p0_cli", "plan"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(completed.stdout), plan)

    def test_participants_are_disjoint_and_hardware_exclusions_are_target_free(self) -> None:
        plans = p0.participant_plans(self.contract)
        self.assertEqual(len(plans), 44)
        self.assertEqual(sum(plan.complete for plan in plans), 42)
        excluded = [plan for plan in plans if not plan.complete]
        self.assertEqual(len(excluded), 2)
        self.assertEqual({plan.cohort_id for plan in excluded}, set(p0.COHORTS))
        self.assertEqual(len({plan.participant_id for plan in plans}), 44)

    def test_full_trial_plan_is_deterministic_target_firewalled_and_segment_safe(self) -> None:
        first_vault = p0.GeneratedTargetVault(b"a" * 32)
        second_vault = p0.GeneratedTargetVault(b"a" * 32)
        first = p0.generate_trial_plan(self.contract, first_vault)
        second = p0.generate_trial_plan(self.contract, second_vault)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 10_752)
        self.assertEqual(first_vault.public_summary(), second_vault.public_summary())
        by_participant: dict[str, Counter[str]] = {}
        for row in first:
            by_participant.setdefault(row.participant_id, Counter())[row.role] += 1
            p0.assert_target_free(row.public_record())
            if row.endpoint is not None:
                self.assertEqual(
                    int(row.intention_window_start_seconds // 120),
                    int((row.intention_window_stop_seconds - 1e-12) // 120),
                )
        self.assertEqual(len(by_participant), 42)
        for counts in by_participant.values():
            self.assertEqual(counts, Counter(p0.TRIAL_ROLE_COUNTS))
        self.assertEqual(first_vault.public_summary()["commitment_count"], 42 * 96)

    def test_target_vault_delivers_once_and_only_after_freeze(self) -> None:
        vault = p0.GeneratedTargetVault(b"b" * 32)
        commitment = vault.precommit("discovery", "item-1", 2)
        self.assertEqual(len(commitment), 64)
        with self.assertRaisesRegex(p0.CommP0GeneratedRefusal, "pre_freeze_target_delivery"):
            vault.deliver_for_score(
                "discovery",
                prediction_freeze_green=False,
                replication_artifact_freeze_green=True,
            )
        self.assertEqual(
            vault.deliver_for_score(
                "discovery",
                prediction_freeze_green=True,
                replication_artifact_freeze_green=True,
            ),
            {"item-1": 2},
        )
        with self.assertRaisesRegex(p0.CommP0GeneratedRefusal, "repeated_score"):
            vault.deliver_for_score(
                "discovery",
                prediction_freeze_green=True,
                replication_artifact_freeze_green=True,
            )

    def test_target_scanner_is_recursive(self) -> None:
        with self.assertRaisesRegex(
            p0.CommP0GeneratedRefusal,
            "recursive_target_label_reference_key_leakage",
        ):
            p0.assert_target_free({"nested": [{"target": "stop"}]})

    def test_sensor_bundle_uses_three_sourcechunk_shards_and_shared_ledgers(self) -> None:
        participant = next(plan for plan in p0.participant_plans(self.contract) if plan.complete)
        first = p0.build_sensor_bundle(self.contract, participant, 0)
        second = p0.build_sensor_bundle(self.contract, participant, 0)
        self.assertEqual(first, second)
        self.assertEqual([len(row["channel_names"]) for row in first["shards"]], [32, 32, 9])
        self.assertEqual(sum(len(row["channel_names"]) for row in first["shards"]), 73)
        broken = copy.deepcopy(first)
        broken["shards"][1]["clock_ledger_sha256"] = "0" * 64
        with self.assertRaisesRegex(p0.CommP0GeneratedRefusal, "correction_ledger_tamper"):
            p0.validate_sensor_bundle(broken, self.contract)

    def test_prediction_freeze_checks_inventory_endpoints_and_probabilities(self) -> None:
        conditions = self.contract["conditions"][:2]
        rows = []
        for participant in ("P1", "P2"):
            for endpoint in p0.ENDPOINTS:
                for condition in conditions:
                    rows.append(
                        {
                            "item_id": f"{participant}-{endpoint}",
                            "participant_id": participant,
                            "endpoint": endpoint,
                            "condition": condition,
                            "probabilities": [0.25, 0.25, 0.25, 0.25],
                        }
                    )
        freeze = p0.build_prediction_freeze(rows, expected_rows=8, expected_sets=8)
        self.assertEqual(freeze["prediction_rows"], 8)
        self.assertFalse(
            freeze["contains_individual_prediction_probability_target_or_participant_outcome"]
        )
        malformed = copy.deepcopy(rows)
        malformed[0]["probabilities"] = [0.2, 0.2, 0.2, 0.2]
        with self.assertRaisesRegex(
            p0.CommP0GeneratedRefusal,
            "prediction_probability_nonfinite_or_sum_mismatch",
        ):
            p0.build_prediction_freeze(malformed, expected_rows=8, expected_sets=8)

    def test_participant_first_scoring_uses_all_21_and_exact_sign_flips(self) -> None:
        metrics = {
            f"P{index:02d}": {
                "LL_P": 1.2,
                "LL_P_plus_EEG": 1.0,
                "LL_P_plus_deranged_EEG": 1.15,
                "BA_P_plus_EEG": 0.65,
                "BA_best_control": 0.55,
            }
            for index in range(21)
        }
        summary = p0.participant_first_summary(metrics, self.contract)
        self.assertEqual(summary["participant_count"], 21)
        self.assertEqual(summary["positive_participants"], 21)
        self.assertEqual(summary["sign_flip_assignments_evaluated"], 2**21)
        self.assertTrue(summary["passes"])
        self.assertLessEqual(summary["exact_one_sided_sign_flip_p"], 0.05)

    def test_live_metrics_count_noncommits_and_inactive_time(self) -> None:
        records = []
        for participant in ("P1", "P2"):
            for index, command in enumerate(p0.COMMANDS * 2):
                records.append(
                    {
                        "participant_id": participant,
                        "command": command,
                        "active_intent": True,
                        "stable_commit": index != 7,
                        "invalid": False,
                        "processed_before_deadline": True,
                        "clock_map_verified": True,
                        "stable_commit_latency_seconds": 1.5,
                        "capture_to_presentation_overhead_seconds": 0.1,
                    }
                )
            records.append(
                {
                    "participant_id": participant,
                    "active_intent": False,
                    "duration_seconds": 600.0,
                    "commit_count": 0,
                }
            )
        summary = p0.summarize_live_records(records, self.contract)
        self.assertAlmostEqual(summary["participant_macro_coverage"], 0.875)
        self.assertEqual(summary["noncommits_retained"], 2)
        self.assertTrue(math.isfinite(summary["stable_commit_latency_p95_seconds"]))

    def test_all_70_refusals_have_exact_wrapper_and_unchanged_state(self) -> None:
        observations = p0.exercise_refusal_families(self.contract)
        self.assertEqual(len(observations), 70)
        self.assertEqual(len({row["family"] for row in observations}), 70)
        for row in observations:
            self.assertEqual(row["wrapper"], f"COMM-P0-G:{row['family']}")
            self.assertEqual(row["pre_state_sha256"], row["post_state_sha256"])
            self.assertTrue(row["state_unchanged"])

    def test_replay_digest_requires_every_frozen_field(self) -> None:
        fields = self.contract["adversarial_qualification"]["canonical_replay_equivalence"][
            "digest_fields"
        ]
        surface = {field: "a" * 64 for field in fields}
        self.assertEqual(len(p0.canonical_replay_digest(surface, self.contract)), 64)
        surface.pop(fields[0])
        with self.assertRaisesRegex(
            p0.CommP0GeneratedRefusal,
            "nondeterministic_fixture_prediction_or_freeze_replay",
        ):
            p0.canonical_replay_digest(surface, self.contract)

    def test_official_execution_is_activation_locked(self) -> None:
        with self.assertRaisesRegex(p0.CommP0GeneratedRefusal, "score_before_exact_green_freeze"):
            p0.run_generated_qualification(ROOT / "ignored.json", root=ROOT)


if __name__ == "__main__":
    unittest.main()
