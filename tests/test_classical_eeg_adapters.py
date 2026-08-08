import contextlib
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/classical_eeg_adapter_contract.v0.json"


class ClassicalEegAdapterPlanTests(unittest.TestCase):
    @staticmethod
    def _build():
        from neurodecodekit.models.classical_eeg_adapters import (
            build_synthetic_classical_adapter_plan,
        )

        return build_synthetic_classical_adapter_plan(contract_path=CONTRACT_PATH)

    def test_module_import_is_standard_library_only(self):
        code = """
import sys
blocked = ('numpy', 'scipy', 'mne', 'sklearn', 'pyriemann')
assert all(name not in sys.modules for name in blocked)
import neurodecodekit.models.classical_eeg_adapters
assert all(name not in sys.modules for name in blocked)
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_registered_plan_replays_with_exact_hash_and_no_winner(self):
        first = self._build()
        second = self._build()
        self.assertEqual(first, second)
        self.assertEqual(
            first["plan_sha256"],
            "66800348e76d03b9b994a460b2e78fbe569c450fdb289be5948cecbcea860bf1",
        )
        self.assertIsNone(first["selection"]["winner_adapter_id"])
        self.assertFalse(first["selection"]["winner_selected_now"])
        self.assertEqual(len(first["adapter_specs"]), 3)

    def test_items_are_unique_pair_group_bound_and_partition_exact(self):
        plan = self._build()
        items = plan["items"]
        self.assertEqual(len(items), 96)
        self.assertEqual(len({row["item_id"] for row in items}), 96)
        self.assertEqual(len({row["group_id"] for row in items}), 48)
        self.assertEqual(len({row["pair_id"] for row in items}), 48)
        for identity in ("group_id", "pair_id"):
            memberships = {}
            for row in items:
                memberships.setdefault(row[identity], set()).add(row["partition_id"])
            self.assertTrue(all(len(partitions) == 1 for partitions in memberships.values()))
        self.assertEqual(
            plan["partition_summary"]["item_counts"],
            {"train": 48, "check": 32, "final": 16},
        )
        self.assertEqual(
            plan["partition_summary"]["group_counts"],
            {"train": 24, "check": 16, "final": 8},
        )

    def test_fit_firewall_causality_and_dependency_routes_are_exact(self):
        plan = self._build()
        self.assertEqual(len(plan["fit_scope"]), 6)
        self.assertTrue(
            all(
                "train_groups_only" in row["fit_scope"] or "data_independent" in row["fit_scope"]
                for row in plan["fit_scope"]
            )
        )
        self.assertEqual(plan["causality"]["right_context_samples"], 0)
        self.assertEqual(plan["causality"]["post_event_samples"], 0)
        self.assertTrue(plan["causality"]["strictly_pre_event_timestamps_required"])
        for route in plan["dependency_routes"]:
            self.assertFalse(route["available_for_execution_now"])
            self.assertEqual(route["optional_backend_import_attempts"], 0)
            self.assertIsNone(route["fallback_adapter_id"])
            self.assertFalse(route["silent_fallback_allowed"])

    def test_plan_contains_no_class_values_or_protected_item_fields(self):
        from neurodecodekit.models.classical_eeg_adapters import FORBIDDEN_KEY_FRAGMENTS

        plan = self._build()
        self.assertEqual(plan["source"]["protected_class_values_created_or_read"], 0)
        for item in plan["items"]:
            for key in item:
                self.assertFalse(
                    any(fragment in key.lower() for fragment in FORBIDDEN_KEY_FRAGMENTS)
                )
        counters = plan["access_counters"]
        self.assertEqual(counters["synthetic_plan_builds"], 1)
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key != "synthetic_plan_builds")
        )

    def test_all_twelve_registered_leakage_mutations_fail_closed(self):
        from neurodecodekit.models.classical_eeg_adapters import (
            REFUSAL_IDS,
            make_classical_adapter_refusal_mutation,
            validate_classical_adapter_plan,
        )

        plan = self._build()
        self.assertEqual(len(REFUSAL_IDS), 12)
        for refusal_id in REFUSAL_IDS:
            mutated = make_classical_adapter_refusal_mutation(plan, refusal_id)
            with self.assertRaises(ValueError, msg=refusal_id):
                validate_classical_adapter_plan(mutated, contract_path=CONTRACT_PATH)

    def test_hash_tampering_unknown_fields_and_contract_substitution_fail(self):
        from neurodecodekit.models.classical_eeg_adapters import (
            build_synthetic_classical_adapter_plan,
            validate_classical_adapter_plan,
        )

        plan = self._build()
        tampered_hash = copy.deepcopy(plan)
        tampered_hash["plan_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "canonical plan SHA-256"):
            validate_classical_adapter_plan(tampered_hash, contract_path=CONTRACT_PATH)
        unknown = copy.deepcopy(plan)
        unknown["extra"] = True
        with self.assertRaisesRegex(ValueError, "fields mismatch"):
            validate_classical_adapter_plan(unknown, contract_path=CONTRACT_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            substituted = Path(temporary) / "contract.json"
            substituted.write_bytes(CONTRACT_PATH.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                build_synthetic_classical_adapter_plan(contract_path=substituted)

    def test_save_load_cap_and_collision_are_fail_closed(self):
        from neurodecodekit.models.classical_eeg_adapters import (
            load_classical_adapter_plan,
            save_classical_adapter_plan,
        )

        plan = self._build()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "plan.json"
            save_classical_adapter_plan(path, plan, contract_path=CONTRACT_PATH)
            loaded = load_classical_adapter_plan(path, contract_path=CONTRACT_PATH)
            self.assertEqual(loaded, plan)
            self.assertLess(path.stat().st_size, 1024 * 1024)
            retained_payload = path.read_bytes()
            with self.assertRaises(FileExistsError):
                save_classical_adapter_plan(path, plan, contract_path=CONTRACT_PATH)
            self.assertEqual(path.read_bytes(), retained_payload)
            capped = root / "capped.json"
            with self.assertRaisesRegex(ValueError, "exceeding cap"):
                save_classical_adapter_plan(
                    capped,
                    plan,
                    contract_path=CONTRACT_PATH,
                    max_plan_bytes=128,
                )
            self.assertFalse(capped.exists())
            oversized = root / "oversized.json"
            oversized.write_bytes(b" " * 129)
            with self.assertRaisesRegex(ValueError, "exceeds output cap"):
                load_classical_adapter_plan(
                    oversized,
                    contract_path=CONTRACT_PATH,
                    max_plan_bytes=128,
                )

    def test_summary_is_compact_and_excludes_item_rows(self):
        from neurodecodekit.models.classical_eeg_adapters import (
            summarize_classical_adapter_plan,
        )

        summary = summarize_classical_adapter_plan(self._build())
        self.assertNotIn("items", summary)
        self.assertEqual(summary["item_count"], 96)
        self.assertEqual(summary["group_count"], 48)
        self.assertEqual(summary["producer_requires_right_context_samples"], 0)
        self.assertEqual(summary["post_event_samples"], 0)

    def test_cli_create_and_inspect_roundtrip(self):
        from neurodecodekit.cli import main

        with tempfile.TemporaryDirectory() as temporary:
            plan_path = Path(temporary) / "plan.json"
            created_stdout = io.StringIO()
            with contextlib.redirect_stdout(created_stdout):
                created = main(
                    [
                        "make-classical-eeg-adapter-plan",
                        "--out",
                        str(plan_path),
                        "--contract",
                        str(CONTRACT_PATH),
                    ]
                )
            inspected_stdout = io.StringIO()
            with contextlib.redirect_stdout(inspected_stdout):
                inspected = main(
                    [
                        "inspect-classical-eeg-adapter-plan",
                        "--plan",
                        str(plan_path),
                        "--contract",
                        str(CONTRACT_PATH),
                    ]
                )
            created_summary = json.loads(created_stdout.getvalue())
            inspected_summary = json.loads(inspected_stdout.getvalue())
        self.assertEqual(created, 0)
        self.assertEqual(inspected, 0)
        self.assertEqual(created_summary, inspected_summary)
        self.assertIsNone(inspected_summary["winner_adapter_id"])


if __name__ == "__main__":
    unittest.main()
