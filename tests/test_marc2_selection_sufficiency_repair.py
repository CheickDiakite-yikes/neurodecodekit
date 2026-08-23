import copy
import hashlib
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
from unittest import mock

from neurodecodekit.datasets import (
    marc2_selection_sufficiency_repair as vr38a,
)


def _canonical_bytes(value):
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")


def _independent_semantic_identity(selection):
    identity = asdict(selection)
    manifest = identity["private_manifest"]
    for row in manifest["rows"]:
        row["source_hashes"].pop("generated_inventory_sha256")
    hashes = identity["selection_hashes"]
    hashes.pop("generated_inventory_sha256")
    hashes["private_selection_manifest_sha256"] = hashlib.sha256(
        _canonical_bytes(manifest)
    ).hexdigest()
    return hashlib.sha256(_canonical_bytes(identity)).hexdigest()


class Marc2SelectionSufficiencyRepairTests(unittest.TestCase):
    def test_registered_plan_is_generated_only(self):
        plan = vr38a.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR38A")
        self.assertEqual(plan["paths"], 40)
        self.assertGreaterEqual(plan["direct_refusal_minimum"], 80)
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["real_cohort_freeze_authorized"])
        self.assertFalse(plan["FW2_or_CIL1_authorized"])
        self.assertFalse(plan["execute_surface_available"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_exact_case_route_map_in_both_orders(self):
        expected_routes = {
            "public_map_exact_control": "MARC2VR38A-G1",
            "single_cell_contiguous_optional_surplus": "MARC2VR38A-G2",
            "single_cell_noncontiguous_optional_surplus": "MARC2VR38A-G2",
            "multi_cell_optional_surplus": "MARC2VR38A-G2",
            "mixed_optional_surplus_and_deficit": "MARC2VR38A-G2",
            "required_fit_run_missing": "MARC2VR38A-R1",
            "required_heldout_run_missing": "MARC2VR38A-R1",
            "unknown_participant": "MARC2VR38A-R2",
            "incomplete_companion_set": "MARC2VR38A-R2",
            "minimum_prefix_exceeds_cap": "MARC2VR38A-R3",
        }
        self.assertEqual(set(expected_routes), set(vr38a.CASES))
        for order in vr38a.ORDERS:
            for case, expected in expected_routes.items():
                with self.subTest(case=case, order=order):
                    source = vr38a.build_generated_case(case, order)
                    before = vr38a._source_bytes(source)
                    route, _outcome = vr38a._route_case(source)
                    self.assertEqual(route, expected)
                    self.assertEqual(vr38a._source_bytes(source), before)

    def test_all_accepted_paths_share_one_full_structural_identity(self):
        semantic_hashes = set()
        selected_name_hashes = set()
        for order in vr38a.ORDERS:
            for case in vr38a.CASES[:5]:
                with self.subTest(case=case, order=order):
                    outcome = vr38a.select_generated_source(vr38a.build_generated_case(case, order))
                    independent = _independent_semantic_identity(outcome.selection)
                    self.assertEqual(outcome.semantic_sha256, independent)
                    semantic_hashes.add(independent)
                    selected_name_hashes.add(outcome.source_exact_selected_names_sha256)
        self.assertEqual(len(semantic_hashes), 1)
        self.assertEqual(len(selected_name_hashes), 1)

    def test_selected_core_is_exact_task_runs_one_to_three_and_source_bound(self):
        vr2_contract = vr38a.vr2.load_registered_contract()
        eligible = set(vr2_contract["participant_taxonomy"]["eligible_subject_ids"])
        for case in vr38a.CASES[:5]:
            source = vr38a.build_generated_case(case, "canonical")
            source_names = {row["member_name"] for row in source["entries"]}
            outcome = vr38a.select_generated_source(source)
            rows = outcome.selection.private_manifest["rows"]
            bundles = {}
            for row in rows:
                name = row["member_name"]
                match = vr38a.vr20a._core_match(name)
                self.assertIsNotNone(match)
                key = (
                    match.group("subject"),
                    match.group("session"),
                    vr38a.vr20a._semantic_run(match.group("run")),
                )
                self.assertIn(name, source_names)
                self.assertIn(key[0], eligible)
                self.assertIn(key[1], {"ses-01", "ses-02"})
                self.assertIn(key[2], {1, 2, 3})
                self.assertEqual(match.group("task"), vr38a.vr35a.PUBLISHED_TASK)
                bundles.setdefault(key, set()).add(match.group("suffix"))
                self.assertEqual(
                    row["reservation_bytes"],
                    vr38a.selector._reservation_bytes(row),
                )
            count = outcome.selection.cohort_summary["selected_subjects"]
            self.assertEqual(len(rows), count * 24)
            self.assertEqual(len(bundles), count * 6)
            self.assertTrue(
                all(
                    suffixes == set(vr38a.selector.REQUIRED_SUFFIXES)
                    for suffixes in bundles.values()
                )
            )

    def test_missing_core_taxonomy_companion_and_floor_fail_separately(self):
        expected = {
            "required_fit_run_missing": "MARC2VR38A-R1",
            "required_heldout_run_missing": "MARC2VR38A-R1",
            "unknown_participant": "MARC2VR38A-R2",
            "incomplete_companion_set": "MARC2VR38A-R2",
            "minimum_prefix_exceeds_cap": "MARC2VR38A-R3",
        }
        for case, route in expected.items():
            with self.subTest(case=case):
                source = vr38a.build_generated_case(case, "canonical")
                with self.assertRaises(vr38a.SelectionSufficiencyRepairRefusal) as caught:
                    vr38a.select_generated_source(source)
                self.assertEqual(caught.exception.route, route)

    def test_floor_ceiling_and_exact_cap_boundaries_are_supported(self):
        frozen_selector = vr38a.selector.load_registered_contract(vr38a._repo_root())
        rank = vr38a.selector._validate_rank(frozen_selector)
        for count in (12, 19):
            with self.subTest(count=count):
                source = vr38a.build_generated_case("public_map_exact_control", "canonical")
                vr38a._adjust_required_prefix_reservation(
                    source,
                    rank[:count],
                    vr38a.selector.RESERVATION_CAP_BYTES,
                )
                outcome = vr38a.select_generated_source(source)
                self.assertEqual(outcome.selection.cohort_summary["selected_subjects"], count)
                self.assertEqual(
                    outcome.selection.byte_summary["selected_reservation_bytes"],
                    vr38a.selector.RESERVATION_CAP_BYTES,
                )

    def test_tampered_selection_fields_fail_closed(self):
        source = vr38a.build_generated_case("public_map_exact_control", "canonical")
        outcome = vr38a.select_generated_source(source)
        source_names = {row["member_name"] for row in source["entries"]}
        source_rows = {row["member_name"]: row for row in source["entries"]}
        filtered_keys = {
            (
                row["subject_id"],
                row["session_id"],
                int(row["run_id"].removeprefix("run-")),
            )
            for row in outcome.selection.private_manifest["rows"]
        }
        selector_contract = vr38a.selector.load_registered_contract(vr38a._repo_root())
        mutations = {
            "run": lambda value: value.private_manifest["rows"][0].__setitem__("run_id", "run-04"),
            "offset": lambda value: value.private_manifest["rows"][0].__setitem__(
                "local_header_offset",
                value.private_manifest["rows"][0]["local_header_offset"] + 1,
            ),
            "split": lambda value: value.split_summary.__setitem__("fit_heldout_overlap", 1),
            "cap": lambda value: value.byte_summary.__setitem__(
                "reservation_cap_bytes",
                vr38a.selector.RESERVATION_CAP_BYTES + 1,
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                changed = copy.deepcopy(outcome.selection)
                mutate(changed)
                with self.assertRaises(vr38a.SelectionSufficiencyRepairRefusal) as caught:
                    vr38a._validate_selection(
                        changed,
                        filtered_keys=filtered_keys,
                        source_names=source_names,
                        source_rows=source_rows,
                        source_sha256=outcome.source_sha256,
                        selector_contract=selector_contract,
                    )
                self.assertEqual(caught.exception.route, "MARC2VR38A-R1")

    def test_contract_drift_fails_before_source_validation(self):
        contract = vr38a.load_registered_contract()
        changed = copy.deepcopy(contract)
        changed["generated_matrix"]["required_paths"] = 41
        source = vr38a.build_generated_case("public_map_exact_control", "canonical")
        with mock.patch.object(vr38a.vr2, "_validate_live_envelope") as validate:
            with self.assertRaises(vr38a.SelectionSufficiencyRepairRefusal) as caught:
                vr38a.select_generated_source(source, contract=changed)
        self.assertEqual(caught.exception.route, "MARC2VR38A-F01")
        validate.assert_not_called()

    def test_direct_refusals_cover_all_registered_categories(self):
        counts = vr38a._run_direct_refusals(vr38a.load_registered_contract())
        self.assertGreaterEqual(sum(counts.values()), 80)
        for route in (
            "MARC2VR38A-F01",
            "MARC2VR38A-F03",
            "MARC2VR38A-F05",
            "MARC2VR38A-F06",
            "MARC2VR38A-R1",
            "MARC2VR38A-R2",
            "MARC2VR38A-R3",
        ):
            self.assertGreater(counts[route], 0, route)

    def test_refusal_witnesses_are_distinct_and_effective(self):
        contract = vr38a.load_registered_contract()
        baseline_hash = hashlib.sha256(_canonical_bytes(contract)).hexdigest()
        mutations = vr38a._contract_mutations(contract)
        mutation_hashes = {
            hashlib.sha256(_canonical_bytes(value)).hexdigest() for value in mutations
        }
        self.assertEqual(len(mutations), 64)
        self.assertEqual(len(mutation_hashes), 64)
        self.assertNotIn(baseline_hash, mutation_hashes)

        case_hashes = {
            hashlib.sha256(
                vr38a._source_bytes(vr38a.build_generated_case(case, "canonical"))
            ).hexdigest()
            for case in vr38a.CASES
        }
        self.assertEqual(len(case_hashes), len(vr38a.CASES))
        self.assertEqual(len(vr38a.FORBIDDEN_PUBLIC_KEYS), 20)

    def test_public_output_and_resource_caps_fail_closed(self):
        for key in ("member_name", "private_manifest", "subject_id"):
            with self.subTest(key=key):
                with self.assertRaises(vr38a.SelectionSufficiencyRepairRefusal) as caught:
                    vr38a._assert_public_report_safe({key: "forbidden"})
                self.assertEqual(caught.exception.route, "MARC2VR38A-F05")
        limits = vr38a.load_registered_contract()["resource_limits"]
        with self.assertRaises(vr38a.SelectionSufficiencyRepairRefusal) as caught:
            vr38a._assert_resources(
                runtime_seconds=limits["runtime_seconds_maximum"] + 1,
                peak_rss_bytes=1,
                aggregate_output_bytes=1,
                contract=vr38a.load_registered_contract(),
            )
        self.assertEqual(caught.exception.route, "MARC2VR38A-F06")

    def test_cli_has_only_plan_and_qualify(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit):
            vr38a.main(["execute"])
        self.assertIn("invalid choice", stderr.getvalue())
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            status = vr38a.main(["plan"])
        self.assertEqual(status, 0)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["private_access_authorized"])
        self.assertFalse(payload["execute_surface_available"])


if __name__ == "__main__":
    unittest.main()
