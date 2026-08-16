import contextlib
import copy
import io
import os
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import (
    marc2_live_domain_eligibility_adapter as adapter,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENVIRONMENT = {name: "1" for name in adapter.THREAD_ENVIRONMENT}


class Marc2LiveDomainEligibilityAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = adapter.load_registered_contract(ROOT)
        cls.selector_contract = selector.load_registered_contract(ROOT)
        cls.source_a = adapter.build_generated_live_source(
            profile="A",
            contract=cls.contract,
            selector_contract=cls.selector_contract,
        )

    def test_registration_hash_and_green_remote_proof_are_compiled_in(self):
        self.assertEqual(
            adapter.CONTRACT_SHA256,
            "c7c94406c7b3f483bb2ecbbb42b131756d178f288eedc31ce48e9383180a0a33",
        )
        self.assertEqual(
            adapter.GREEN_REGISTRATION_COMMIT,
            "384373e0ffcfe999ae0ae188087f7e84f09720ca",
        )
        self.assertEqual(adapter.GREEN_REGISTRATION_CI_RUN_ID, 31_945_086_852)
        self.assertEqual(adapter.GREEN_REGISTRATION_BASE_JOB_ID, 95_159_734_989)
        self.assertEqual(
            adapter.GREEN_REGISTRATION_OPTIONAL_JOB_ID, 95_159_734_967
        )

    def test_generated_source_has_exact_live_shape_without_private_bytes(self):
        domain = self.contract["generated_live_source_domain"]
        self.assertEqual(set(self.source_a), adapter.SOURCE_TOP_LEVEL_FIELDS)
        self.assertEqual(self.source_a["proof_posture"], domain["proof_posture"])
        self.assertEqual(self.source_a["source_identity"], domain["source_identity"])
        self.assertEqual(
            self.source_a["transport_body_sha256"],
            domain["transport_body_sha256"],
        )
        self.assertEqual(len(self.source_a["entries"]), 1_227)
        self.assertEqual(
            Counter(row["entry_kind"] for row in self.source_a["entries"]),
            Counter({"regular_file": 1_025, "directory": 202}),
        )
        self.assertFalse(domain["contains_real_or_private_bytes"])

    def test_all_profiles_classify_variable_ineligible_counts(self):
        observed = {}
        for profile in ("A", "B", "C", "D"):
            with self.subTest(profile=profile):
                source = adapter.build_generated_live_source(
                    profile=profile,
                    contract=self.contract,
                    selector_contract=self.selector_contract,
                )
                filtered, counts, labels, source_hash = (
                    adapter.validate_live_domain_source(
                        source,
                        contract=self.contract,
                    )
                )
                expected = {
                    adapter.PREDICATE_CODES[0]: 195,
                    **self.contract["generated_success_profiles"][profile],
                }
                self.assertEqual(counts, expected)
                self.assertEqual(len(labels), 238)
                self.assertEqual(len(filtered), 195)
                self.assertEqual(len(source_hash), 64)
                observed[profile] = tuple(
                    counts[code] for code in adapter.PREDICATE_CODES[1:]
                )
        self.assertEqual(len(set(observed.values())), 4)

    def test_all_eight_profile_order_paths_replay_one_selection(self):
        identities = set()
        source_hashes = {profile: set() for profile in ("A", "B", "C", "D")}
        for profile in source_hashes:
            for row_order in ("canonical", "reversed"):
                source = adapter.build_generated_live_source(
                    profile=profile,
                    row_order=row_order,
                    contract=self.contract,
                    selector_contract=self.selector_contract,
                )
                result = adapter.adapt_live_domain_source(
                    source,
                    contract=self.contract,
                    selector_contract=self.selector_contract,
                )
                identities.add(
                    result.selection.selection_hashes[
                        "selection_identity_sha256"
                    ]
                )
                source_hashes[profile].add(result.source_sha256)
                self.assertEqual(
                    result.selection.byte_summary["selected_reservation_bytes"],
                    8_105_207_776,
                )
                self.assertEqual(
                    result.selection.split_summary["selected_core_members"], 384
                )
        self.assertEqual(
            identities,
            {
                "dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641"
            },
        )
        self.assertTrue(all(len(values) == 1 for values in source_hashes.values()))

    def test_generated_profile_identity_is_not_an_adapter_input(self):
        self.assertEqual(
            list(adapter.adapt_live_domain_source.__annotations__),
            ["source", "contract", "selector_contract", "return"],
        )
        source_b = adapter.build_generated_live_source(
            profile="B",
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        result = adapter.adapt_live_domain_source(
            source_b,
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(result.predicate_counts["MARC2VR2-P02"], 8)
        self.assertFalse(
            self.contract["live_acceptance"]["exact_ineligible_breakdown_frozen"]
        )

    def test_unknown_participant_and_taxonomy_overlap_fail_closed(self):
        changed = copy.deepcopy(self.source_a)
        old = adapter._first_ineligible_key(changed, self.contract)
        adapter._rename_key_once(changed, old, ("sub-99", "ses-01", 1))
        with self.assertRaises(adapter.LiveDomainEligibilityRefusal) as caught:
            adapter.validate_live_domain_source(changed, contract=self.contract)
        self.assertEqual(caught.exception.route, "MARC2VR2-F04")

        changed_contract = copy.deepcopy(self.contract)
        changed_contract["participant_taxonomy"]["eligible_subject_ids"].append(
            "sub-02"
        )
        with self.assertRaises(adapter.LiveDomainEligibilityRefusal) as caught:
            adapter._verify_contract_mapping(changed_contract)
        self.assertEqual(caught.exception.route, "MARC2VR2-F04")

    def test_every_registered_mutation_refuses_and_all_routes_are_exercised(self):
        routes = adapter.run_required_mutations(
            self.source_a,
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(
            list(routes), self.contract["qualification"]["required_mutations"]
        )
        self.assertEqual(len(routes), 58)
        self.assertEqual(set(routes.values()), set(adapter.REFUSAL_ROUTES))

    def test_development_preflight_is_bounded_and_aggregate(self):
        report = adapter.run_development_preflight(
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(len(report["success_paths"]), 8)
        self.assertEqual(len(report["mutation_routes"]), 58)
        self.assertLessEqual(
            report["generated_input_bytes"],
            self.contract["resource_caps"]["generated_input_bytes"],
        )
        self.assertTrue(
            all(
                set(row) == {
                    "profile",
                    "row_order",
                    "predicate_counts",
                    "source_sha256",
                    "selection_identity_sha256",
                }
                for row in report["success_paths"]
            )
        )

    def test_mocked_qualification_is_deterministic_public_and_zero_access(self):
        def run_once() -> dict:
            times = iter((100.0, 100.5))
            with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
                return adapter.qualify_generated(
                    repo_root=ROOT,
                    clock=lambda: next(times),
                    rss_reader=lambda: 50_000_000,
                )

        first = run_once()
        second = run_once()
        self.assertEqual(first, second)
        self.assertEqual(first["route"], "MARC2VR2-G1")
        self.assertEqual(first["replay_summary"]["success_paths"], 8)
        self.assertEqual(first["mutation_summary"]["refused_mutations"], 58)
        self.assertTrue(all(value == 0 for value in first["access_counters"].values()))
        adapter.validate_public_report(first)

    def test_public_report_tampering_and_resource_drift_refuse(self):
        times = iter((1.0, 1.1))
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
            report = adapter.qualify_generated(
                repo_root=ROOT,
                clock=lambda: next(times),
                rss_reader=lambda: 40_000_000,
            )
        changed = copy.deepcopy(report)
        changed["access_counters"]["MARC2_FW2_operations"] = 1
        with self.assertRaises(adapter.LiveDomainEligibilityRefusal):
            adapter.validate_public_report(changed)
        with self.assertRaises(adapter.LiveDomainEligibilityRefusal) as caught:
            adapter._assert_resources(
                runtime_seconds=31.0,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                retained_output_bytes=0,
                contract=self.contract,
            )
        self.assertEqual(caught.exception.route, "MARC2VR2-F08")

    def test_thread_environment_is_explicit_and_fail_closed(self):
        environment = dict(THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with self.assertRaises(adapter.LiveDomainEligibilityRefusal) as caught:
            adapter._validate_thread_environment(environment)
        self.assertEqual(caught.exception.route, "MARC2VR2-F08")

    def test_plan_inspect_and_help_expose_no_execute_or_path_argument(self):
        plan = adapter.build_plan_summary()
        inspect = adapter.build_inspection_summary()
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(plan["private_read_or_real_executor_allowed"])
        self.assertFalse(inspect["private_row_or_path_inspection_available"])
        parser = adapter._build_parser()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as caught:
                parser.parse_args(["--help"])
        self.assertEqual(caught.exception.code, 0)
        help_text = output.getvalue()
        self.assertIn("{plan,qualify,inspect}", help_text)
        self.assertNotIn("execute", help_text)
        self.assertNotIn("--path", help_text)
        self.assertNotIn("--url", help_text.lower())

    def test_module_has_no_private_executor_or_optional_dependency_import(self):
        text = Path(adapter.__file__).read_text(encoding="utf-8")
        self.assertNotIn("marc2_live_adapter_recovery", text)
        self.assertNotIn("live_alias_recovery_v2", text)
        self.assertNotIn("live_audit_v0", text)
        for dependency in ("numpy", "scipy", "mne", "torch", "sklearn"):
            self.assertNotIn(f"import {dependency}", text)
        parser = adapter._build_parser()
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices),
            {"plan", "qualify", "inspect"},
        )


if __name__ == "__main__":
    unittest.main()
