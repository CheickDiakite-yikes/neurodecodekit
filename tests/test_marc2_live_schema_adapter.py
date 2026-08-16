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
from neurodecodekit.datasets import marc2_live_schema_adapter as live_adapter
from neurodecodekit.datasets import marc2_transport_alias_adapter as adapter


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / live_adapter.CONTRACT_RELATIVE_PATH
ONE_THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


class Marc2LiveSchemaAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = live_adapter.load_registered_contract(repo_root=ROOT)
        cls.adapter_contract = adapter.load_registered_contract(repo_root=ROOT)
        cls.selector_contract = selector.load_registered_contract(repo_root=ROOT)
        cls.source = live_adapter.build_generated_live_source(
            selector_contract=cls.selector_contract
        )

    def test_contract_hash_and_green_registration_are_exact(self):
        self.assertEqual(
            hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
            live_adapter.CONTRACT_SHA256,
        )
        self.assertEqual(
            live_adapter.GREEN_REGISTRATION_COMMIT,
            "62e465e0600622444b0868d5dcf19678504d20c4",
        )
        self.assertEqual(
            live_adapter.GREEN_REGISTRATION_CI_RUN_ID, 31_934_737_967
        )
        self.assertEqual(
            live_adapter.GREEN_REGISTRATION_BASE_JOB_ID, 95_134_785_476
        )
        self.assertEqual(
            live_adapter.GREEN_REGISTRATION_OPTIONAL_JOB_ID, 95_134_785_489
        )

    def test_all_fixed_input_hashes_are_current(self):
        for binding in self.contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                self.assertEqual(
                    hashlib.sha256((ROOT / binding["path"]).read_bytes()).hexdigest(),
                    binding["sha256"],
                )

    def test_source_fixture_has_exact_live_envelope_and_generated_rows(self):
        self.assertEqual(set(self.source), live_adapter.SOURCE_TOP_LEVEL_FIELDS)
        self.assertEqual(
            self.source["proof_posture"], live_adapter.LIVE_PROOF_POSTURE
        )
        self.assertEqual(
            self.source["source_identity"], live_adapter.LIVE_SOURCE_IDENTITY
        )
        self.assertEqual(
            set(self.source["transport_body_sha256"]),
            live_adapter.SOURCE_TRANSPORT_KEYS,
        )
        self.assertEqual(len(self.source["entries"]), 1_227)
        self.assertEqual(
            Counter(row["entry_kind"] for row in self.source["entries"]),
            Counter({"regular_file": 1_025, "directory": 202}),
        )

    def test_live_validation_precedes_bridge_and_green_adapter(self):
        events = []
        original_validate = live_adapter._validate_live_source_manifest
        original_bridge = live_adapter._bridge_live_identity
        original_adapt = adapter.adapt_generated_source

        def validate(*args, **kwargs):
            events.append("validate")
            return original_validate(*args, **kwargs)

        def bridge(*args, **kwargs):
            events.append("bridge")
            return original_bridge(*args, **kwargs)

        def adapt(*args, **kwargs):
            events.append("green_adapter")
            return original_adapt(*args, **kwargs)

        with (
            mock.patch.object(
                live_adapter, "_validate_live_source_manifest", side_effect=validate
            ),
            mock.patch.object(
                live_adapter, "_bridge_live_identity", side_effect=bridge
            ),
            mock.patch.object(adapter, "adapt_generated_source", side_effect=adapt),
        ):
            live_adapter.adapt_live_shaped_source(
                self.source,
                live_contract=self.contract,
                adapter_contract=self.adapter_contract,
                selector_contract=self.selector_contract,
            )
        self.assertEqual(events, ["validate", "bridge", "green_adapter"])

    def test_invalid_live_source_refuses_before_bridge_or_green_adapter(self):
        changed = copy.deepcopy(self.source)
        changed["source_identity"]["file_id"] = 0
        with (
            mock.patch.object(live_adapter, "_bridge_live_identity") as bridge,
            mock.patch.object(adapter, "adapt_generated_source") as green,
        ):
            with self.assertRaises(live_adapter.LiveSchemaAdapterRefusal) as caught:
                live_adapter.adapt_live_shaped_source(
                    changed,
                    live_contract=self.contract,
                    adapter_contract=self.adapter_contract,
                    selector_contract=self.selector_contract,
                )
        self.assertEqual(caught.exception.route, live_adapter.REFUSAL_ROUTES[1])
        bridge.assert_not_called()
        green.assert_not_called()

    def test_bridge_changes_only_four_values_and_never_aliases(self):
        validation = live_adapter._validate_live_source_manifest(
            self.source, self.selector_contract
        )
        before = live_adapter._canonical_manifest_bytes(self.source)
        bridged = live_adapter._bridge_live_identity(self.source, validation)
        self.assertEqual(live_adapter._canonical_manifest_bytes(self.source), before)
        self.assertFalse(
            live_adapter._mutable_ids(self.source)
            & live_adapter._mutable_ids(bridged)
        )
        self.assertEqual(bridged["schema_name"], self.source["schema_name"])
        self.assertEqual(bridged["entries"], self.source["entries"])
        self.assertEqual(
            bridged["transport_body_sha256"], self.source["transport_body_sha256"]
        )
        self.assertEqual(bridged["proof_posture"], adapter.SOURCE_PROOF_POSTURE)
        self.assertEqual(
            bridged["source_identity"]["provider"], adapter.SOURCE_PROVIDER
        )
        self.assertEqual(bridged["source_identity"]["file_id"], 0)
        self.assertEqual(bridged["source_identity"]["registered_MD5"], "0" * 32)

    def test_green_public_adapter_is_called_exactly_once_per_success(self):
        with mock.patch.object(
            adapter,
            "adapt_generated_source",
            wraps=adapter.adapt_generated_source,
        ) as green:
            adapted = live_adapter.adapt_live_shaped_source(
                self.source,
                live_contract=self.contract,
                adapter_contract=self.adapter_contract,
                selector_contract=self.selector_contract,
            )
        green.assert_called_once()
        self.assertEqual(
            set(adapted["transport_body_sha256"]),
            live_adapter.SELECTOR_TRANSPORT_KEYS,
        )
        self.assertEqual(
            Counter(adapted["transport_body_sha256"].values()),
            Counter(self.source["transport_body_sha256"].values()),
        )

    def test_adapted_source_replays_frozen_selector_identity(self):
        adapted = live_adapter.adapt_live_shaped_source(
            self.source,
            live_contract=self.contract,
            adapter_contract=self.adapter_contract,
            selector_contract=self.selector_contract,
        )
        result = selector.select_generated_prefix(
            adapted, contract=self.selector_contract
        )
        live_adapter._assert_selector_result(result, self.contract)
        self.assertEqual(
            result.selection_hashes["selection_identity_sha256"],
            self.contract["expected_selector_result"]["selection_identity_sha256"],
        )

    def test_reversed_source_order_replays_exactly(self):
        reversed_source = live_adapter.build_generated_live_source(
            row_order="reversed", selector_contract=self.selector_contract
        )
        first = live_adapter.adapt_live_shaped_source(
            self.source,
            live_contract=self.contract,
            adapter_contract=self.adapter_contract,
            selector_contract=self.selector_contract,
        )
        second = live_adapter.adapt_live_shaped_source(
            reversed_source,
            live_contract=self.contract,
            adapter_contract=self.adapter_contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(
            live_adapter._canonical_manifest_bytes(first),
            live_adapter._canonical_manifest_bytes(second),
        )

    def test_direct_live_shaped_selector_call_refuses(self):
        with self.assertRaises(selector.FreewillPrefixSelectionRefusal):
            selector.select_generated_prefix(
                self.source, contract=self.selector_contract
            )

    def test_all_30_mutations_refuse_in_registered_order(self):
        outcomes = live_adapter.run_required_mutations(
            self.source,
            live_contract=self.contract,
            adapter_contract=self.adapter_contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(
            tuple(outcomes), tuple(self.contract["qualification"]["required_mutations"])
        )
        self.assertEqual(
            Counter(outcomes.values()),
            Counter(
                {
                    live_adapter.REFUSAL_ROUTES[1]: 17,
                    live_adapter.REFUSAL_ROUTES[2]: 9,
                    live_adapter.REFUSAL_ROUTES[3]: 2,
                    live_adapter.REFUSAL_ROUTES[4]: 1,
                    live_adapter.REFUSAL_ROUTES[5]: 1,
                }
            ),
        )

    def test_target_or_label_entry_field_refuses_at_live_boundary(self):
        for field in ("target", "label"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.source)
                changed["entries"][0][field] = "forbidden"
                with self.assertRaises(
                    live_adapter.LiveSchemaAdapterRefusal
                ) as caught:
                    live_adapter.adapt_live_shaped_source(
                        changed,
                        live_contract=self.contract,
                        adapter_contract=self.adapter_contract,
                        selector_contract=self.selector_contract,
                    )
                self.assertEqual(
                    caught.exception.route, live_adapter.REFUSAL_ROUTES[1]
                )

    def test_green_adapter_refusal_is_mapped_without_fallback(self):
        refusal = adapter.TransportAliasAdapterRefusal(
            adapter.REFUSAL_ROUTES[4], "injected"
        )
        with mock.patch.object(
            adapter, "adapt_generated_source", side_effect=refusal
        ) as green:
            with self.assertRaises(live_adapter.LiveSchemaAdapterRefusal) as caught:
                live_adapter.adapt_live_shaped_source(
                    self.source,
                    live_contract=self.contract,
                    adapter_contract=self.adapter_contract,
                    selector_contract=self.selector_contract,
                )
        self.assertEqual(caught.exception.route, live_adapter.REFUSAL_ROUTES[4])
        green.assert_called_once()

    def test_contract_rejects_a_changed_green_adapter_identity(self):
        with mock.patch.object(
            live_adapter, "adapter_module_sha256", return_value="0" * 64
        ):
            with self.assertRaises(live_adapter.LiveSchemaAdapterRefusal) as caught:
                live_adapter._verify_contract_mapping(self.contract)
        self.assertEqual(caught.exception.route, live_adapter.REFUSAL_ROUTES[0])

    def test_plan_builds_no_fixture(self):
        with mock.patch.object(
            live_adapter,
            "build_generated_live_source",
            side_effect=AssertionError("fixture build forbidden"),
        ):
            plan = live_adapter.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-LA1")
        self.assertEqual(plan["required_mutations"], 30)
        self.assertFalse(plan["live_executor_or_private_read_authorized"])

    def test_qualification_writes_one_small_inspectable_aggregate(self):
        ticks = iter((10.0, 10.5))
        with tempfile.TemporaryDirectory() as temporary:
            report_path = Path(temporary) / "live-adapter-report.json"
            with mock.patch.dict(os.environ, ONE_THREAD_ENVIRONMENT, clear=False):
                outcome = live_adapter.qualify_generated_composition(
                    report_path,
                    clock=lambda: next(ticks),
                    rss_probe=lambda: 32 * 1024 * 1024,
                )
            self.assertEqual(outcome.report["route"], live_adapter.SUCCESS_ROUTE)
            self.assertEqual(outcome.report["mutation_summary"]["passed"], 30)
            self.assertEqual(sum(outcome.report["access_counters"].values()), 0)
            self.assertLess(outcome.generated_output_bytes, 2 * 1024**2)
            self.assertEqual(stat.S_IMODE(report_path.stat().st_mode), 0o600)
            inspected = live_adapter.inspect_report(report_path)
            self.assertEqual(inspected["selected_subjects"], 16)
            self.assertEqual(inspected["selected_core_members"], 384)
            self.assertEqual(inspected["mutations_passed"], 30)

    def test_output_overwrite_refuses_without_modification(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "existing.json"
            output.write_text("keep", encoding="utf-8")
            with mock.patch.dict(os.environ, ONE_THREAD_ENVIRONMENT, clear=False):
                with self.assertRaises(
                    live_adapter.LiveSchemaAdapterRefusal
                ) as caught:
                    live_adapter.qualify_generated_composition(output)
            self.assertEqual(caught.exception.route, live_adapter.REFUSAL_ROUTES[6])
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
                    live_adapter,
                    "build_generated_live_source",
                    side_effect=AssertionError("fixture build forbidden"),
                ) as builder,
            ):
                with self.assertRaises(
                    live_adapter.LiveSchemaAdapterRefusal
                ) as caught:
                    live_adapter.qualify_generated_composition(
                        alias / "report.json"
                    )
            self.assertEqual(caught.exception.route, live_adapter.REFUSAL_ROUTES[6])
            builder.assert_not_called()

    def test_missing_one_thread_environment_refuses_before_fixture_build(self):
        environment = dict(ONE_THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            with (
                mock.patch.dict(os.environ, environment, clear=True),
                mock.patch.object(
                    live_adapter,
                    "build_generated_live_source",
                    side_effect=AssertionError("fixture build forbidden"),
                ) as builder,
            ):
                with self.assertRaises(
                    live_adapter.LiveSchemaAdapterRefusal
                ) as caught:
                    live_adapter.qualify_generated_composition(output)
        self.assertEqual(caught.exception.route, live_adapter.REFUSAL_ROUTES[6])
        builder.assert_not_called()

    def test_runtime_and_RSS_caps_fail_closed(self):
        for runtime, rss in ((30.1, 1), (1.0, 256 * 1024**2 + 1)):
            with self.subTest(runtime=runtime, rss=rss):
                with self.assertRaises(
                    live_adapter.LiveSchemaAdapterRefusal
                ) as caught:
                    live_adapter._assert_resources(runtime, rss, self.contract)
                self.assertEqual(
                    caught.exception.route, live_adapter.REFUSAL_ROUTES[6]
                )

    def test_report_validation_refuses_nonzero_forbidden_counter(self):
        counters = live_adapter._zero_access_counters()
        counters["scientific_claim_upgrades"] = 1
        with self.assertRaises(live_adapter.LiveSchemaAdapterRefusal) as caught:
            live_adapter._validate_zero_access_counters(counters)
        self.assertEqual(caught.exception.route, live_adapter.REFUSAL_ROUTES[5])

    def test_strict_JSON_rejects_duplicate_keys(self):
        with self.assertRaises(ValueError):
            live_adapter._strict_json(b'{"a":1,"a":2}')

    def test_CLI_surface_has_only_plan_qualify_and_inspect(self):
        help_text = live_adapter._build_parser().format_help()
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertIn("inspect", help_text)
        self.assertNotIn("execute", help_text)

    def test_main_plan_emits_strict_JSON_without_live_authority(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(live_adapter.main(["plan"]), 0)
        value = json.loads(output.getvalue())
        self.assertEqual(value["lane_id"], "MARC2-LA1")
        self.assertEqual(value["private_or_Git_ignored_bytes_authorized"], 0)
        self.assertEqual(value["network_bytes_authorized"], 0)
        self.assertFalse(value["live_executor_or_private_read_authorized"])


if __name__ == "__main__":
    unittest.main()
