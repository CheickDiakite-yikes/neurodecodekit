from __future__ import annotations

import copy
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_domain_refusals as domain


ROOT = Path(__file__).resolve().parents[1]


class CommP0GeneratedDomainRefusalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = core.load_contract(ROOT)
        cls.expected = tuple(
            (category, family)
            for category, families in cls.contract["adversarial_qualification"][
                "refusal_families"
            ].items()
            for family in families
        )

    def test_exact_inventory_wrappers_and_transaction_immutability(self) -> None:
        observations = domain.exercise_domain_refusals(self.contract)
        self.assertEqual(len(observations), 70)
        self.assertEqual(
            tuple((row["category"], row["family"]) for row in observations),
            self.expected,
        )
        self.assertEqual(len({row["family"] for row in observations}), 70)
        for row in observations:
            self.assertEqual(row["wrapper"], f"COMM-P0-G:{row['family']}")
            self.assertEqual(row["pre_state_sha256"], row["post_state_sha256"])
            self.assertTrue(row["state_unchanged"])
            self.assertNotEqual(row["valid_fixture_sha256"], row["malformed_fixture_sha256"])

    def test_replay_is_deterministic(self) -> None:
        first = domain.exercise_domain_refusals()
        second = domain.exercise_domain_refusals(self.contract)
        self.assertEqual(first, second)
        self.assertEqual(core.sha256_json(first), core.sha256_json(second))

    def test_inventory_rejects_missing_extra_and_duplicate_families(self) -> None:
        cases = []
        missing = copy.deepcopy(self.contract)
        missing["adversarial_qualification"]["refusal_families"][
            "target_leakage_and_side_channels"
        ].pop()
        cases.append(missing)
        extra = copy.deepcopy(self.contract)
        extra["adversarial_qualification"]["refusal_families"][
            "target_leakage_and_side_channels"
        ].append("unregistered_family")
        cases.append(extra)
        duplicate = copy.deepcopy(self.contract)
        rows = duplicate["adversarial_qualification"]["refusal_families"][
            "target_leakage_and_side_channels"
        ]
        rows[-1] = rows[0]
        cases.append(duplicate)
        for malformed in cases:
            with (
                self.subTest(case=cases.index(malformed)),
                self.assertRaisesRegex(
                    core.CommP0GeneratedRefusal,
                    "required_control_condition_missing_duplicated_or_substituted",
                ),
            ):
                domain.family_inventory(malformed)

    def test_every_case_mutates_one_concrete_domain_field(self) -> None:
        observations = domain.exercise_domain_refusals(self.contract)
        for row in observations:
            self.assertIsInstance(row["mutated_field"], str)
            self.assertNotEqual(row["mutated_field"], "transaction")

    def test_wrong_internal_refusal_cannot_satisfy_family(self) -> None:
        def wrong_refusal(state: object, contract: object) -> None:
            raise core.CommP0GeneratedRefusal("pre_freeze_target_delivery")

        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "nondeterministic_fixture_prediction_or_freeze_replay",
        ):
            domain.qualify_refusal_case(
                "target_leakage_and_side_channels",
                "free_choice_target_before_precommit",
                self.contract,
                validator_override=wrong_refusal,
            )

    def test_malformed_acceptance_cannot_satisfy_family(self) -> None:
        def accepts_malformed(state: object, contract: object) -> None:
            return None

        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "required_control_condition_missing_duplicated_or_substituted",
        ):
            domain.qualify_refusal_case(
                "storage_filesystem_and_cleanup",
                "raw_payload_cap_breach",
                self.contract,
                validator_override=accepts_malformed,
            )

    def test_ledger_rejects_missing_extra_duplicate_and_wrong_wrapper(self) -> None:
        observations = list(domain.exercise_domain_refusals(self.contract))
        malformed_ledgers = (
            observations[:-1],
            observations + [observations[-1]],
            [observations[0], *observations],
        )
        for ledger in malformed_ledgers:
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "required_control_condition_missing_duplicated_or_substituted",
            ):
                domain.validate_observations(ledger, self.contract)

        wrong_wrapper = copy.deepcopy(observations)
        wrong_wrapper[0]["wrapper"] = "COMM-P0-G:pre_freeze_target_delivery"
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "nondeterministic_fixture_prediction_or_freeze_replay",
        ):
            domain.validate_observations(wrong_wrapper, self.contract)


if __name__ == "__main__":
    unittest.main()
