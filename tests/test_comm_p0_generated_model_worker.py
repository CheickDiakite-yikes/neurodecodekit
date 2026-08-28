from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from dataclasses import asdict, replace
from io import StringIO
from pathlib import Path
from unittest import mock

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_model_worker as worker
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical


HAS_CLASSICAL = (
    importlib.util.find_spec("numpy") is not None
    and importlib.util.find_spec("sklearn") is not None
)


class CommP0GeneratedModelWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.contract = core.load_contract(cls.root)

    def _capability(self) -> tuple[list[dict], list[dict], str]:
        vault = core.GeneratedTargetVault(b"model-worker-test-vault-key-000000000")
        plans = core.generate_trial_plan(self.contract, vault)
        participants = sorted(
            {row.participant_id for row in plans if row.cohort_id == "discovery"}
        )[:3]
        selected = [
            row
            for row in plans
            if row.cohort_id == "discovery" and row.participant_id in participants
        ]
        active = [row for row in selected if row.endpoint in core.ENDPOINTS]
        original_by_item = {row.item_id: row for row in active}
        opaque = {
            item_id: hashlib.sha256(f"opaque:{item_id}".encode()).hexdigest()
            for item_id in original_by_item
        }
        features = [
            replace(row, item_id=opaque[row.item_id])
            for row in numerical.generate_feature_rows(selected)
        ]
        held_out = participants[-1]
        labels = [
            {
                "item_id": opaque[item_id],
                "participant_id": trial.participant_id,
                "source_command_index": numerical._fixture_command(trial),
            }
            for item_id, trial in original_by_item.items()
            if trial.participant_id != held_out
        ]
        return [asdict(row) for row in features], labels, held_out

    def test_feature_capability_rejects_trial_or_target_fields(self) -> None:
        features, _, _ = self._capability()
        features[0]["trial_index"] = 0
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "target_exposed_to_decoder_operator_freezer_or_language_context",
        ):
            worker._feature_rows(features)

    def test_source_label_capability_rejects_held_out_label(self) -> None:
        features, labels, held_out = self._capability()
        rows = worker._feature_rows(features)
        held_row = next(row for row in rows if row.participant_id == held_out)
        labels.append(
            {
                "item_id": held_row.item_id,
                "participant_id": held_out,
                "source_command_index": 0,
            }
        )
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "held_out_participant_fit_threshold_or_adaptation",
        ):
            worker._source_labels(
                labels, feature_rows=rows, held_out_participant=held_out
            )

    @unittest.skipUnless(HAS_CLASSICAL, "requires optional classical stack")
    def test_one_fold_runs_without_trial_plan_or_held_out_labels(self) -> None:
        features, labels, held_out = self._capability()
        output = StringIO()
        environment = {
            name: "1" for name in numerical.THREAD_ENVIRONMENT
        }
        with mock.patch.dict(os.environ, environment, clear=False):
            ledger = worker.run_fold(
                features,
                labels,
                self.contract,
                held_out_participant=held_out,
                output=output,
            )
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        header = records[0]
        trailer = records[-1]
        predictions = [row for row in records if row["record_type"] == "prediction"]
        self.assertEqual(header["held_out_labels_received"], 0)
        self.assertEqual(header["trial_plan_objects_received"], 0)
        self.assertEqual(header["target_vault_capabilities_received"], 0)
        self.assertEqual(ledger["classifier_fits"], 15)
        self.assertEqual(ledger["temperature_calibration_fits"], 15)
        self.assertEqual(ledger["residualizer_fits"], 2)
        self.assertEqual(ledger["prediction_sets"], 34)
        self.assertEqual(ledger["prediction_rows"], 2_176)
        self.assertEqual(len(predictions), 2_176)
        self.assertEqual(trailer["post_target_updates"], 0)
        core.assert_target_free(records)

    def test_descriptor_main_uses_only_preopened_descriptors(self) -> None:
        features, labels, held_out = self._capability()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [root / name for name in ("features", "labels", "contract", "output")]
            paths[0].write_text(
                "".join(core.canonical_json_bytes(row).decode() for row in features),
                encoding="utf-8",
            )
            paths[1].write_text(
                "".join(core.canonical_json_bytes(row).decode() for row in labels),
                encoding="utf-8",
            )
            paths[2].write_bytes(core.canonical_json_bytes(self.contract).rstrip(b"\n"))
            descriptors = [
                os.open(paths[0], os.O_RDONLY),
                os.open(paths[1], os.O_RDONLY),
                os.open(paths[2], os.O_RDONLY),
                os.open(paths[3], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
            ]
            if HAS_CLASSICAL:
                environment = {
                    name: "1" for name in numerical.THREAD_ENVIRONMENT
                }
                with mock.patch.dict(os.environ, environment, clear=False):
                    worker.descriptor_main(
                        feature_fd=descriptors[0],
                        label_fd=descriptors[1],
                        contract_fd=descriptors[2],
                        output_fd=descriptors[3],
                        held_out_participant=held_out,
                        byte_cap=8 * 1024 * 1024,
                    )
                self.assertGreater(paths[3].stat().st_size, 0)
            else:
                for descriptor in descriptors:
                    os.close(descriptor)

    def test_descriptor_main_rejects_read_write_substitution(self) -> None:
        features, labels, held_out = self._capability()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [root / name for name in ("features", "labels", "contract", "output")]
            paths[0].write_text(
                "".join(core.canonical_json_bytes(row).decode() for row in features),
                encoding="utf-8",
            )
            paths[1].write_text(
                "".join(core.canonical_json_bytes(row).decode() for row in labels),
                encoding="utf-8",
            )
            paths[2].write_bytes(core.canonical_json_bytes(self.contract).rstrip(b"\n"))
            paths[3].touch()
            descriptors = [
                os.open(paths[0], os.O_RDWR),
                os.open(paths[1], os.O_RDONLY),
                os.open(paths[2], os.O_RDONLY),
                os.open(paths[3], os.O_WRONLY),
            ]
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "filesystem_object_type_violation",
            ):
                worker.descriptor_main(
                    feature_fd=descriptors[0],
                    label_fd=descriptors[1],
                    contract_fd=descriptors[2],
                    output_fd=descriptors[3],
                    held_out_participant=held_out,
                    byte_cap=8 * 1024 * 1024,
                )
            for descriptor in descriptors:
                os.close(descriptor)


if __name__ == "__main__":
    unittest.main()
