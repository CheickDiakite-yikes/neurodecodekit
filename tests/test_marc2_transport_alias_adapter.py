import contextlib
import copy
import hashlib
import io
import json
import os
import stat
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_transport_alias_adapter as adapter


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / adapter.CONTRACT_RELATIVE_PATH
ONE_THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


class Marc2TransportAliasAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = adapter.load_registered_contract(repo_root=ROOT)
        cls.selector_contract = selector.load_registered_contract(repo_root=ROOT)
        cls.source = adapter.build_generated_source_manifest(
            selector_contract=cls.selector_contract
        )

    def test_contract_hash_and_remote_green_registration_are_exact(self):
        self.assertEqual(
            hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
            adapter.CONTRACT_SHA256,
        )
        self.assertEqual(
            adapter.GREEN_REGISTRATION_COMMIT,
            "0c0e1c8a08ff7e68d0e4432a64dde8a85fb0274f",
        )
        self.assertEqual(adapter.GREEN_REGISTRATION_CI_RUN_ID, 31_932_701_989)
        self.assertEqual(adapter.GREEN_REGISTRATION_BASE_JOB_ID, 95_129_832_134)
        self.assertEqual(
            adapter.GREEN_REGISTRATION_OPTIONAL_JOB_ID, 95_129_832_169
        )

    def test_all_fixed_input_hashes_are_current(self):
        for binding in self.contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                self.assertEqual(
                    hashlib.sha256((ROOT / binding["path"]).read_bytes()).hexdigest(),
                    binding["sha256"],
                )

    def test_source_fixture_is_producer_native_and_full_scale(self):
        self.assertEqual(set(self.source), adapter.SOURCE_TOP_LEVEL_FIELDS)
        self.assertEqual(self.source["proof_posture"], adapter.SOURCE_PROOF_POSTURE)
        self.assertEqual(
            self.source["source_identity"]["provider"], adapter.SOURCE_PROVIDER
        )
        self.assertEqual(
            set(self.source["transport_body_sha256"]),
            adapter.SOURCE_TRANSPORT_KEYS,
        )
        self.assertEqual(len(self.source["entries"]), 1_227)
        self.assertEqual(
            Counter(row["entry_kind"] for row in self.source["entries"]),
            Counter({"regular_file": 1_025, "directory": 202}),
        )

    def test_source_validation_precedes_copy_or_mapping(self):
        events = []
        original_validate = adapter._validate_source_manifest
        original_adapt = adapter._adapt_validated_source

        def validate(*args, **kwargs):
            events.append("validate")
            return original_validate(*args, **kwargs)

        def adapt(*args, **kwargs):
            events.append("adapt")
            return original_adapt(*args, **kwargs)

        with (
            mock.patch.object(adapter, "_validate_source_manifest", side_effect=validate),
            mock.patch.object(adapter, "_adapt_validated_source", side_effect=adapt),
        ):
            adapter.adapt_generated_source(
                self.source,
                adapter_contract=self.contract,
                selector_contract=self.selector_contract,
            )
        self.assertEqual(events, ["validate", "adapt"])

    def test_invalid_source_refuses_before_copy(self):
        changed = copy.deepcopy(self.source)
        changed["transport_body_sha256"]["central_directory"] = changed[
            "transport_body_sha256"
        ]["directory"]
        with mock.patch.object(adapter, "_adapt_validated_source") as copier:
            with self.assertRaises(adapter.TransportAliasAdapterRefusal) as caught:
                adapter.adapt_generated_source(
                    changed,
                    adapter_contract=self.contract,
                    selector_contract=self.selector_contract,
                )
        self.assertEqual(caught.exception.route, adapter.REFUSAL_ROUTES[2])
        copier.assert_not_called()

    def test_adapter_preserves_source_and_maps_only_transport_alias(self):
        before = adapter._canonical_manifest_bytes(self.source)
        adapted = adapter.adapt_generated_source(
            self.source,
            adapter_contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(adapter._canonical_manifest_bytes(self.source), before)
        self.assertEqual(
            set(adapted["transport_body_sha256"]),
            adapter.SELECTOR_TRANSPORT_KEYS,
        )
        self.assertEqual(
            adapted["transport_body_sha256"]["central_directory"],
            self.source["transport_body_sha256"]["directory"],
        )
        self.assertEqual(
            Counter(adapted["transport_body_sha256"].values()),
            Counter(self.source["transport_body_sha256"].values()),
        )

    def test_source_and_adapted_mutable_objects_do_not_alias(self):
        adapted = adapter.adapt_generated_source(
            self.source,
            adapter_contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertFalse(adapter._mutable_ids(self.source) & adapter._mutable_ids(adapted))

    def test_adapted_source_replays_frozen_selector_identity(self):
        adapted = adapter.adapt_generated_source(
            self.source,
            adapter_contract=self.contract,
            selector_contract=self.selector_contract,
        )
        observed = selector.select_generated_prefix(
            adapted,
            contract=self.selector_contract,
        )
        baseline = selector.select_generated_prefix(
            selector.build_generated_manifest(contract=self.selector_contract),
            contract=self.selector_contract,
        )
        adapter._assert_selector_result(observed, self.contract)
        adapter._assert_selection_identity(observed, baseline)

    def test_reversed_source_order_replays_exactly(self):
        reversed_source = adapter.build_generated_source_manifest(
            row_order="reversed",
            selector_contract=self.selector_contract,
        )
        first = adapter.adapt_generated_source(
            self.source,
            adapter_contract=self.contract,
            selector_contract=self.selector_contract,
        )
        second = adapter.adapt_generated_source(
            reversed_source,
            adapter_contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(
            adapter._canonical_manifest_bytes(first),
            adapter._canonical_manifest_bytes(second),
        )

    def test_direct_unadapted_selector_call_refuses(self):
        with self.assertRaises(selector.FreewillPrefixSelectionRefusal):
            selector.select_generated_prefix(
                self.source,
                contract=self.selector_contract,
            )

    def test_all_26_mutations_refuse_in_registered_order(self):
        outcomes = adapter.run_required_mutations(
            self.source,
            adapter_contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(
            tuple(outcomes),
            tuple(self.contract["qualification"]["required_mutations"]),
        )
        self.assertEqual(len(outcomes), 26)
        self.assertEqual(
            Counter(outcomes.values()),
            Counter(
                {
                    adapter.REFUSAL_ROUTES[1]: 10,
                    adapter.REFUSAL_ROUTES[2]: 9,
                    adapter.REFUSAL_ROUTES[3]: 4,
                    adapter.REFUSAL_ROUTES[4]: 2,
                    adapter.REFUSAL_ROUTES[5]: 1,
                }
            ),
        )

    def test_target_or_label_entry_field_refuses_at_source_boundary(self):
        for field in ("target", "label"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.source)
                changed["entries"][0][field] = "forbidden"
                with self.assertRaises(adapter.TransportAliasAdapterRefusal) as caught:
                    adapter.adapt_generated_source(
                        changed,
                        adapter_contract=self.contract,
                        selector_contract=self.selector_contract,
                    )
                self.assertEqual(caught.exception.route, adapter.REFUSAL_ROUTES[1])

    def test_uppercase_short_and_nonstring_transport_digests_refuse(self):
        for value in ("A" * 64, "0" * 63, 1):
            with self.subTest(value=value):
                changed = copy.deepcopy(self.source)
                changed["transport_body_sha256"]["directory"] = value
                with self.assertRaises(adapter.TransportAliasAdapterRefusal) as caught:
                    adapter.adapt_generated_source(
                        changed,
                        adapter_contract=self.contract,
                        selector_contract=self.selector_contract,
                    )
                self.assertEqual(caught.exception.route, adapter.REFUSAL_ROUTES[2])

    def test_plan_builds_no_generated_fixture(self):
        with mock.patch.object(
            adapter,
            "build_generated_source_manifest",
            side_effect=AssertionError("fixture build forbidden"),
        ):
            plan = adapter.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-TA1")
        self.assertEqual(plan["required_mutations"], 26)
        self.assertFalse(plan["live_adapter_or_MARC2_FW2_authorized"])

    def test_qualification_writes_one_small_inspectable_aggregate(self):
        ticks = iter((10.0, 10.5))
        with tempfile.TemporaryDirectory() as temporary:
            report_path = Path(temporary) / "adapter-report.json"
            with mock.patch.dict(os.environ, ONE_THREAD_ENVIRONMENT, clear=False):
                outcome = adapter.qualify_generated_adapter(
                    report_path,
                    clock=lambda: next(ticks),
                    rss_probe=lambda: 32 * 1024 * 1024,
                )
            self.assertEqual(outcome.report["route"], adapter.SUCCESS_ROUTE)
            self.assertEqual(outcome.report["mutation_summary"]["passed"], 26)
            self.assertEqual(sum(outcome.report["access_counters"].values()), 0)
            self.assertLess(outcome.generated_output_bytes, 2 * 1024**2)
            self.assertEqual(stat.S_IMODE(report_path.stat().st_mode), 0o600)
            inspected = adapter.inspect_report(report_path)
            self.assertEqual(inspected["route"], adapter.SUCCESS_ROUTE)
            self.assertEqual(inspected["selected_subjects"], 16)
            self.assertEqual(inspected["mutations_passed"], 26)

    def test_output_overwrite_refuses_without_modification(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "existing.json"
            output.write_text("keep", encoding="utf-8")
            with mock.patch.dict(os.environ, ONE_THREAD_ENVIRONMENT, clear=False):
                with self.assertRaises(adapter.TransportAliasAdapterRefusal) as caught:
                    adapter.qualify_generated_adapter(output)
            self.assertEqual(caught.exception.route, adapter.REFUSAL_ROUTES[6])
            self.assertEqual(output.read_text(encoding="utf-8"), "keep")

    def test_symlinked_output_parent_refuses_before_fixture_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real = root / "real"
            real.mkdir()
            alias = root / "alias"
            alias.symlink_to(real, target_is_directory=True)
            with (
                mock.patch.dict(os.environ, ONE_THREAD_ENVIRONMENT, clear=False),
                mock.patch.object(
                    adapter,
                    "build_generated_source_manifest",
                    side_effect=AssertionError("fixture build forbidden"),
                ) as builder,
            ):
                with self.assertRaises(adapter.TransportAliasAdapterRefusal) as caught:
                    adapter.qualify_generated_adapter(alias / "report.json")
            self.assertEqual(caught.exception.route, adapter.REFUSAL_ROUTES[6])
            builder.assert_not_called()

    def test_missing_one_thread_environment_refuses_before_fixture_build(self):
        environment = dict(ONE_THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            with (
                mock.patch.dict(os.environ, environment, clear=True),
                mock.patch.object(
                    adapter,
                    "build_generated_source_manifest",
                    side_effect=AssertionError("fixture build forbidden"),
                ) as builder,
            ):
                with self.assertRaises(adapter.TransportAliasAdapterRefusal) as caught:
                    adapter.qualify_generated_adapter(output)
        self.assertEqual(caught.exception.route, adapter.REFUSAL_ROUTES[6])
        builder.assert_not_called()

    def test_runtime_and_RSS_caps_fail_closed(self):
        for runtime, rss in ((30.1, 1), (1.0, 256 * 1024**2 + 1)):
            with self.subTest(runtime=runtime, rss=rss):
                with self.assertRaises(adapter.TransportAliasAdapterRefusal) as caught:
                    adapter._assert_resources(runtime, rss, self.contract)
                self.assertEqual(caught.exception.route, adapter.REFUSAL_ROUTES[6])

    def test_report_validation_refuses_nonzero_forbidden_counter(self):
        counters = adapter._zero_access_counters()
        counters["scientific_claim_upgrades"] = 1
        with self.assertRaises(adapter.TransportAliasAdapterRefusal) as caught:
            adapter._validate_zero_access_counters(counters)
        self.assertEqual(caught.exception.route, adapter.REFUSAL_ROUTES[5])

    def test_strict_JSON_rejects_duplicate_keys(self):
        with self.assertRaises(ValueError):
            adapter._strict_json(b'{"a":1,"a":2}')

    def test_CLI_surface_has_only_plan_qualify_and_inspect(self):
        parser = adapter._build_parser()
        help_text = parser.format_help()
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertIn("inspect", help_text)
        self.assertNotIn("execute", help_text)

    def test_main_plan_emits_strict_JSON_without_live_authority(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(adapter.main(["plan"]), 0)
        value = json.loads(output.getvalue())
        self.assertEqual(value["lane_id"], "MARC2-TA1")
        self.assertEqual(value["private_or_Git_ignored_bytes_authorized"], 0)
        self.assertEqual(value["network_bytes_authorized"], 0)


if __name__ == "__main__":
    unittest.main()
