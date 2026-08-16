import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import marc2_dynamic_live_selection as dynamic
from neurodecodekit.datasets import (
    marc2_source_validity_eligibility_repair as repair,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENVIRONMENT = {name: "1" for name in dynamic.THREAD_ENVIRONMENT}


class Marc2DynamicLiveSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(
            (
                ROOT / "registries/marc2_dynamic_live_selection_contract.v0.json"
            ).read_text(encoding="utf-8")
        )
        cls.vr2_contract = vr2.load_registered_contract(ROOT)
        cls.selector_contract = selector.load_registered_contract(ROOT)

    def _source(self, profile="minimum_exact_cap", row_order="canonical"):
        return dynamic.build_generated_profile(
            profile,
            row_order,
            vr2_contract=self.vr2_contract,
            selector_contract=self.selector_contract,
        )

    def _select(self, profile="minimum_exact_cap", row_order="canonical"):
        source = self._source(profile, row_order)
        return source, dynamic.adapt_dynamic_live_source(
            source,
            vr2_contract=self.vr2_contract,
            selector_contract=self.selector_contract,
        )

    def test_plan_has_no_private_or_execute_surface(self):
        plan = dynamic.build_plan_summary(repo_root=ROOT)
        self.assertEqual(plan["lane_id"], "MARC2-VR6")
        self.assertEqual(plan["generated_success_paths"], 10)
        self.assertFalse(plan["execute_command"])
        self.assertFalse(plan["real_cohort_freeze_authorized"])
        self.assertFalse(plan["MARC2_FW2_or_CIL1_authorized"])
        self.assertEqual(plan["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(plan["network_bytes"], 0)

    def test_five_profiles_select_dynamic_expected_counts(self):
        for profile, expected in dynamic.PROFILE_COUNTS.items():
            with self.subTest(profile=profile):
                _source, selected = self._select(profile)
                self.assertEqual(
                    selected.cohort_summary["selected_subjects"], expected
                )
                self.assertEqual(
                    selected.split_summary["selected_run_bundles"], expected * 6
                )
                self.assertEqual(
                    selected.split_summary["selected_core_members"], expected * 24
                )
                self.assertLessEqual(
                    selected.byte_summary["selected_reservation_bytes"],
                    selector.RESERVATION_CAP_BYTES,
                )
                if expected == selector.MAXIMUM_SUBJECTS:
                    self.assertIsNone(
                        selected.cohort_summary["first_nonfitting_subject_id"]
                    )
                else:
                    self.assertIsNotNone(
                        selected.cohort_summary["first_nonfitting_subject_id"]
                    )

    def test_row_order_replay_is_exact_for_every_profile(self):
        identities = set()
        for profile in dynamic.PROFILE_COUNTS:
            canonical_source, canonical = self._select(profile, "canonical")
            reversed_source, reversed_selection = self._select(profile, "reversed")
            self.assertNotEqual(
                canonical_source["entries"], reversed_source["entries"]
            )
            self.assertEqual(
                canonical.selection_hashes["selection_identity_sha256"],
                reversed_selection.selection_hashes["selection_identity_sha256"],
            )
            self.assertEqual(
                canonical.selection_hashes["live_source_canonical_sha256"],
                reversed_selection.selection_hashes[
                    "live_source_canonical_sha256"
                ],
            )
            identities.add(
                canonical.selection_hashes["selection_identity_sha256"]
            )
        self.assertEqual(len(identities), len(dynamic.PROFILE_COUNTS))

    def test_full_source_validation_precedes_selection(self):
        source = self._source()
        calls = []
        real_validate = vr2.validate_live_domain_source
        real_select = repair._select_from_filtered

        def validate(*args, **kwargs):
            calls.append("validate")
            return real_validate(*args, **kwargs)

        def select(*args, **kwargs):
            calls.append("select")
            return real_select(*args, **kwargs)

        with patch.object(vr2, "validate_live_domain_source", side_effect=validate), patch.object(
            repair, "_select_from_filtered", side_effect=select
        ):
            dynamic.adapt_dynamic_live_source(
                source,
                vr2_contract=self.vr2_contract,
                selector_contract=self.selector_contract,
            )
        self.assertEqual(calls, ["validate", "select"])

    def test_exact_generated_result_assertion_is_never_called(self):
        source = self._source("lower_middle")
        with patch.object(
            repair,
            "_assert_selection",
            side_effect=AssertionError("fixture identity assertion was called"),
        ):
            selected = dynamic.adapt_dynamic_live_source(
                source,
                vr2_contract=self.vr2_contract,
                selector_contract=self.selector_contract,
            )
        self.assertEqual(selected.cohort_summary["selected_subjects"], 14)

    def test_source_is_immutable_and_output_has_no_mutable_alias(self):
        source = self._source("reference_middle")
        before = vr2._canonical_source_bytes(source)
        selected = dynamic.adapt_dynamic_live_source(
            source,
            vr2_contract=self.vr2_contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(vr2._canonical_source_bytes(source), before)
        self.assertFalse(
            dynamic._mutable_ids(source)
            & dynamic._mutable_ids(selected.private_manifest)
        )

    def test_live_source_semantics_replace_generated_labels(self):
        _source, selected = self._select("upper_middle")
        manifest = selected.private_manifest
        self.assertEqual(manifest["schema_name"], dynamic.PRIVATE_SCHEMA_NAME)
        self.assertEqual(manifest["proof_posture"], dynamic.LIVE_PROOF_POSTURE)
        self.assertNotIn("generated_inventory_sha256", selected.selection_hashes)
        for row in manifest["rows"]:
            self.assertEqual(row["source_id"], dynamic.LIVE_ROW_SOURCE_ID)
            self.assertEqual(
                set(row["source_hashes"]),
                {
                    "live_source_canonical_sha256",
                    "selector_contract_sha256",
                    "dynamic_selection_contract_sha256",
                },
            )

    def test_row_reservation_sum_and_formula_are_revalidated(self):
        source = self._source()
        raw, eligible, _source_hash = dynamic._raw_selection_for_mutations(
            source,
            vr2_contract=self.vr2_contract,
            selector_contract=self.selector_contract,
        )
        changed = copy.deepcopy(raw)
        changed.private_manifest["rows"][0]["reservation_bytes"] += 1
        with self.assertRaises(dynamic.DynamicLiveSelectionRefusal) as raised:
            dynamic._validate_dynamic_selection(
                changed,
                eligible_keys=eligible,
                selector_contract=self.selector_contract,
            )
        self.assertEqual(raised.exception.route, "MARC2VR6-F04")

    def test_normalized_hashes_are_recomputed(self):
        _source, selected = self._select()
        changed = copy.deepcopy(selected)
        changed.private_manifest["selected_subject_ids"].reverse()
        source_hash = selected.selection_hashes["live_source_canonical_sha256"]
        with self.assertRaises(dynamic.DynamicLiveSelectionRefusal) as raised:
            dynamic._validate_live_semantics(changed, source_sha256=source_hash)
        self.assertEqual(raised.exception.route, "MARC2VR6-F05")

    def test_target_like_field_is_rejected(self):
        _source, selected = self._select()
        changed = copy.deepcopy(selected)
        changed.private_manifest["rows"][0]["target_text"] = "forbidden"
        source_hash = selected.selection_hashes["live_source_canonical_sha256"]
        with self.assertRaises(dynamic.DynamicLiveSelectionRefusal) as raised:
            dynamic._validate_live_semantics(changed, source_sha256=source_hash)
        self.assertEqual(raised.exception.route, "MARC2VR6-F06")

    def test_upstream_refusal_retains_only_allowlisted_route_code(self):
        source = self._source()
        source["unknown"] = "private detail must not survive"
        with self.assertRaises(dynamic.DynamicLiveSelectionRefusal) as raised:
            dynamic.adapt_dynamic_live_source(
                source,
                vr2_contract=self.vr2_contract,
                selector_contract=self.selector_contract,
            )
        refusal = raised.exception
        self.assertEqual(refusal.route, "MARC2VR6-F02")
        self.assertEqual(refusal.upstream_route, "MARC2VR2-F02")
        self.assertEqual(refusal.safe_reason, "upstream VR2 validation refused")
        self.assertNotIn("private detail", str(refusal))

    def test_unknown_upstream_route_fails_closed_without_echo(self):
        refusal = dynamic._preserve_upstream_route("UNKNOWN-private-detail")
        self.assertEqual(refusal.route, "MARC2VR6-F02")
        self.assertIsNone(refusal.upstream_route)
        self.assertNotIn("UNKNOWN", str(refusal))

    def test_measured_qualification_passes_all_registered_gates(self):
        with patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False):
            report = dynamic.qualify_generated(
                repo_root=ROOT,
                clock=iter((10.0, 11.0)).__next__,
                rss_reader=lambda: 64 * 1024**2,
            )
        self.assertEqual(report["route"], "MARC2VR6-G1")
        self.assertEqual(report["replay_summary"]["success_paths"], 10)
        self.assertEqual(
            [
                row["selected_subjects"]
                for row in report["generated_profiles"][::2]
            ],
            [12, 14, 16, 18, 19],
        )
        self.assertGreaterEqual(
            report["mutation_summary"]["direct_mutations_passed"], 24
        )
        self.assertEqual(
            set(report["mutation_summary"]["route_counts"]),
            set(dynamic.REFUSAL_ROUTES),
        )
        self.assertTrue(all(report["acceptance_gates"].values()))
        self.assertTrue(all(value == 0 for value in report["access_counters"].values()))
        self.assertEqual(report["measurements"]["retained_generated_output_bytes"], 0)

    def test_cli_help_exposes_only_plan_and_qualify(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.datasets.marc2_dynamic_live_selection",
                "--help",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("{plan,qualify}", completed.stdout)
        self.assertNotIn("execute", completed.stdout)
        self.assertNotIn("--path", completed.stdout)
        self.assertNotIn("--output", completed.stdout)


if __name__ == "__main__":
    unittest.main()
