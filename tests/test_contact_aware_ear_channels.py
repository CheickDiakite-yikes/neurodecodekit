import contextlib
import copy
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/contact_aware_ear_channel_contract.v0.json"


class ContactAwareEarChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
        except ImportError:
            raise unittest.SkipTest("NumPy is optional") from None
        from neurodecodekit.preprocess.contact_aware_ear_channels import (
            load_contact_aware_ear_fixture,
            prepare_contact_aware_ear_fixture,
        )

        cls.np = np
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name) / "fixture"
        cls.sidecar_path = cls.output / "metadata.json"
        prepare_contact_aware_ear_fixture(cls.output, contract_path=CONTRACT_PATH)
        cls.fixture = load_contact_aware_ear_fixture(
            cls.sidecar_path,
            contract_path=CONTRACT_PATH,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    @staticmethod
    def _write_self_sized_sidecar(path: Path, sidecar: dict) -> None:
        for _ in range(10):
            payload = (json.dumps(sidecar, indent=2, sort_keys=True) + "\n").encode()
            sidecar["artifacts"]["metadata_sidecar_bytes"] = len(payload)
            sidecar["artifacts"]["total_output_bytes"] = (
                sidecar["artifacts"]["payload_bytes"] + len(payload)
            )
        path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_module_import_is_lazy_for_every_optional_scientific_dependency(self):
        code = """
import sys
blocked = ('numpy', 'scipy', 'mne', 'sklearn', 'pyriemann', 'torch')
assert all(name not in sys.modules for name in blocked)
import neurodecodekit.preprocess.contact_aware_ear_channels
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

    def test_replay_payload_metadata_and_provenance_hashes_are_exact(self):
        from neurodecodekit.preprocess.contact_aware_ear_channels import (
            _deterministic_npz_bytes,
            make_contact_aware_ear_arrays,
        )

        first_arrays, first_metadata = make_contact_aware_ear_arrays(
            contract_path=CONTRACT_PATH
        )
        second_arrays, second_metadata = make_contact_aware_ear_arrays(
            contract_path=CONTRACT_PATH
        )
        self.assertEqual(first_metadata, second_metadata)
        self.assertEqual(
            _deterministic_npz_bytes(first_arrays),
            _deterministic_npz_bytes(second_arrays),
        )
        self.assertEqual(
            self.fixture.sidecar["hashes"],
            {
                "algorithm": "SHA-256",
                "configuration_sha256": (
                    "d955fef2ea71cd0b13def1b32f2ef6b4b6e0c00ea0131d942baa47b2b89ba51f"
                ),
                "fixture_metadata_sha256": (
                    "ce3aa6bc6e3056ebcb66fad6ce19461a11b9e445cdd1cf064ae26dc02550d931"
                ),
                "payload_sha256": (
                    "caf1be67271a3753eb638e78e01fa8cae17154bc306eaff15ae1ed672a4c7051"
                ),
                "selected_subset_and_weight_sha256": (
                    "8eecf9f93dbb9b2f3c0cfb7b210361c470933621492eca1a7e1b104a50496c70"
                ),
                "source_order_sha256": (
                    "2ba9d54cd526f2664524c5386a34e8e7a2b2ab04596a0778f571849f9b94d383"
                ),
            },
        )
        self.assertEqual(
            hashlib.sha256(self.sidecar_path.read_bytes()).hexdigest(),
            "da9a2cc90662f5cbd1f29f85b14064998720a8556da6906a9f4c1bbecee15a1e",
        )

    def test_scenario_identity_geometry_and_artifact_inventory_are_exact(self):
        from neurodecodekit.preprocess.contact_aware_ear_channels import SCENARIO_IDS

        metadata = self.fixture.metadata
        self.assertEqual(metadata["scenario_counts"], {name: 6 for name in SCENARIO_IDS})
        self.assertEqual(metadata["identity"]["item_count"], 48)
        self.assertEqual(metadata["identity"]["channel_count"], 16)
        self.assertEqual(metadata["identity"]["source_channel_names"][0], "ear-L00")
        self.assertEqual(metadata["identity"]["source_channel_names"][-1], "ear-R07")
        self.assertEqual(
            metadata["identity"]["geometry_provenance"],
            "synthetic_nominal_not_measured_not_anatomical",
        )
        self.assertFalse(metadata["identity"]["measured_impedance_available"])
        artifacts = self.fixture.sidecar["artifacts"]
        self.assertEqual(artifacts["payload_bytes"], 923_980)
        self.assertEqual(artifacts["metadata_sidecar_bytes"], 14_894)
        self.assertEqual(artifacts["total_output_bytes"], 938_874)
        self.assertLessEqual(artifacts["total_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(artifacts["output_files"], 2)

    def test_source_missingness_and_adapted_zero_fill_remain_distinct(self):
        arrays = self.fixture.arrays
        observed = arrays["observed_mask"]
        selected = arrays["selected_mask"]
        adapted_observed = arrays["adapted_observed_mask"]
        self.assertTrue(self.np.isnan(arrays["signals"][~observed]).all())
        self.assertTrue(self.np.isfinite(arrays["signals"][observed]).all())
        self.assertTrue(self.np.equal(arrays["adapted_signal"][~adapted_observed], 0.0).all())
        self.assertTrue(
            self.np.array_equal(adapted_observed, observed & selected[:, :, None])
        )
        expected = self.np.where(
            adapted_observed,
            arrays["signals"] * arrays["selection_weight"][:, :, None],
            0.0,
        ).astype("float32")
        self.assertTrue(self.np.array_equal(arrays["adapted_signal"], expected))
        self.assertFalse(self.np.array_equal(arrays["eligible_mask"], selected))
        self.assertFalse(
            self.np.array_equal(arrays["channel_present_mask"], arrays["eligible_mask"])
        )

    def test_fixed_bilateral_policy_caps_weights_and_unknown_contact(self):
        arrays = self.fixture.arrays
        for row, status in enumerate(arrays["selection_status"].tolist()):
            left_count = int(arrays["selected_mask"][row, :8].sum())
            right_count = int(arrays["selected_mask"][row, 8:].sum())
            if status == "ok":
                self.assertGreaterEqual(left_count, 2)
                self.assertGreaterEqual(right_count, 2)
                self.assertLessEqual(left_count, 4)
                self.assertLessEqual(right_count, 4)
                self.assertAlmostEqual(float(arrays["selection_weight"][row, :8].sum()), 0.5)
                self.assertAlmostEqual(float(arrays["selection_weight"][row, 8:].sum()), 0.5)
            else:
                self.assertEqual(status, "insufficient_bilateral_contact")
                self.assertFalse(arrays["selected_mask"][row].any())
                self.assertEqual(float(arrays["selection_weight"][row].sum()), 0.0)
        unknown_rows = self.np.flatnonzero(
            arrays["scenario_ids"] == "unknown_contact_quality"
        )
        self.assertEqual(len(unknown_rows), 6)
        self.assertFalse(arrays["contact_score_valid_mask"][unknown_rows, :8].any())
        self.assertTrue(self.np.isnan(arrays["contact_score"][unknown_rows, :8]).all())

    def test_contact_policy_does_not_mutate_sources_or_consult_future_tail(self):
        from neurodecodekit.preprocess.contact_aware_ear_channels import (
            SAMPLES,
            apply_fixed_contact_policy,
        )

        arrays = self.fixture.arrays
        source_before = arrays["signals"].copy()
        common = {
            "channel_present_mask": arrays["channel_present_mask"],
            "contact_score": arrays["contact_score"],
            "contact_score_valid_mask": arrays["contact_score_valid_mask"],
            "noise_score": arrays["noise_score"],
            "ear_sides": arrays["ear_sides"],
            "decision_sample": SAMPLES,
        }
        original = apply_fixed_contact_policy(
            observed_mask=arrays["observed_mask"],
            **common,
        )
        future_tail = self.np.zeros((48, 16, 64), dtype="bool")
        extended = apply_fixed_contact_policy(
            observed_mask=self.np.concatenate(
                [arrays["observed_mask"], future_tail],
                axis=2,
            ),
            **common,
        )
        for first, second in zip(original, extended, strict=True):
            self.assertTrue(self.np.array_equal(first, second))
        self.assertTrue(self.np.array_equal(source_before, arrays["signals"], equal_nan=True))

    def test_all_sixteen_registered_refusal_mutations_fail_closed(self):
        from neurodecodekit.preprocess.contact_aware_ear_channels import (
            REFUSAL_IDS,
            make_contact_aware_ear_refusal_mutation,
            validate_contact_aware_ear_arrays,
        )

        self.assertEqual(len(REFUSAL_IDS), 16)
        for refusal_id in REFUSAL_IDS:
            arrays, metadata = make_contact_aware_ear_refusal_mutation(
                self.fixture,
                refusal_id,
            )
            with self.assertRaises(ValueError, msg=refusal_id):
                validate_contact_aware_ear_arrays(
                    arrays,
                    expected_metadata=metadata,
                )

    def test_unknown_and_target_bearing_metadata_fields_fail_closed(self):
        from neurodecodekit.preprocess.contact_aware_ear_channels import (
            _canonical_json,
            validate_contact_aware_ear_arrays,
        )

        for key, value, message in (
            ("unexpected", True, "fields mismatch"),
            ("target_text", "forbidden", "forbidden field"),
        ):
            arrays = {name: self.np.array(item, copy=True) for name, item in self.fixture.arrays.items()}
            metadata = copy.deepcopy(dict(self.fixture.metadata))
            metadata[key] = value
            arrays["metadata"] = self.np.asarray(_canonical_json(metadata))
            with self.assertRaisesRegex(ValueError, message):
                validate_contact_aware_ear_arrays(arrays, expected_metadata=metadata)

    def test_metadata_only_inspection_opens_no_numpy_array_members(self):
        from neurodecodekit.preprocess.contact_aware_ear_channels import (
            load_contact_aware_ear_metadata,
            summarize_contact_aware_ear_metadata,
        )

        with mock.patch("numpy.load", side_effect=AssertionError("array opened")) as loader:
            sidecar = load_contact_aware_ear_metadata(
                self.sidecar_path,
                contract_path=CONTRACT_PATH,
            )
        loader.assert_not_called()
        summary = summarize_contact_aware_ear_metadata(sidecar)
        self.assertEqual(summary["array_members_opened"], 0)
        self.assertFalse(summary["end_to_end_latency_measured"])
        self.assertTrue(summary["producer_is_causal"])

    def test_payload_tampering_malformed_npz_and_unknown_sidecar_fail_closed(self):
        from neurodecodekit.preprocess.contact_aware_ear_channels import (
            load_contact_aware_ear_metadata,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tampered = root / "tampered"
            shutil.copytree(self.output, tampered)
            payload_path = tampered / "ear_fixture.npz"
            payload = payload_path.read_bytes()
            payload_path.write_bytes(payload[:-1] + bytes([payload[-1] ^ 1]))
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                load_contact_aware_ear_metadata(
                    tampered / "metadata.json",
                    contract_path=CONTRACT_PATH,
                )

            malformed = root / "malformed"
            shutil.copytree(self.output, malformed)
            payload_path = malformed / "ear_fixture.npz"
            payload_path.write_bytes(b"not-an-npz")
            sidecar_path = malformed / "metadata.json"
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
            digest = hashlib.sha256(payload_path.read_bytes()).hexdigest()
            sidecar["payload"]["bytes"] = payload_path.stat().st_size
            sidecar["payload"]["sha256"] = digest
            sidecar["hashes"]["payload_sha256"] = digest
            sidecar["artifacts"]["payload_bytes"] = payload_path.stat().st_size
            self._write_self_sized_sidecar(sidecar_path, sidecar)
            with self.assertRaisesRegex(ValueError, "not a valid NPZ"):
                load_contact_aware_ear_metadata(
                    sidecar_path,
                    contract_path=CONTRACT_PATH,
                )

            unknown = root / "unknown"
            shutil.copytree(self.output, unknown)
            sidecar_path = unknown / "metadata.json"
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
            sidecar["unexpected"] = True
            sidecar_path.write_text(json.dumps(sidecar), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sidecar fields mismatch"):
                load_contact_aware_ear_metadata(
                    sidecar_path,
                    contract_path=CONTRACT_PATH,
                )

    def test_output_cap_collision_and_free_disk_preflight_fail_closed(self):
        from neurodecodekit.preprocess.contact_aware_ear_channels import (
            MINIMUM_FREE_DISK_BYTES,
            load_contact_aware_ear_metadata,
            prepare_contact_aware_ear_fixture,
        )

        with self.assertRaisesRegex(ValueError, "output exceeds cap"):
            load_contact_aware_ear_metadata(
                self.sidecar_path,
                contract_path=CONTRACT_PATH,
                max_output_bytes=self.fixture.sidecar["artifacts"]["total_output_bytes"] - 1,
            )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaises(FileExistsError):
                prepare_contact_aware_ear_fixture(existing, contract_path=CONTRACT_PATH)

            capped = root / "capped"
            with self.assertRaisesRegex(ValueError, "exceeding cap"):
                prepare_contact_aware_ear_fixture(
                    capped,
                    contract_path=CONTRACT_PATH,
                    max_output_bytes=1024,
                )
            self.assertFalse(capped.exists())

            low_disk = root / "low-disk"
            with mock.patch(
                "neurodecodekit.preprocess.contact_aware_ear_channels.shutil.disk_usage",
                return_value=SimpleNamespace(free=MINIMUM_FREE_DISK_BYTES - 1),
            ):
                with self.assertRaisesRegex(OSError, "at least 1 GiB"):
                    prepare_contact_aware_ear_fixture(
                        low_disk,
                        contract_path=CONTRACT_PATH,
                    )
            self.assertFalse(low_disk.exists())

    def test_cli_create_and_metadata_only_inspect_roundtrip(self):
        from neurodecodekit.cli import main

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            created_stdout = io.StringIO()
            with contextlib.redirect_stdout(created_stdout):
                created = main(
                    [
                        "make-contact-aware-ear-fixture",
                        "--out-dir",
                        str(output),
                        "--contract",
                        str(CONTRACT_PATH),
                    ]
                )
            inspected_stdout = io.StringIO()
            with contextlib.redirect_stdout(inspected_stdout):
                inspected = main(
                    [
                        "inspect-contact-aware-ear-fixture",
                        "--metadata",
                        str(output / "metadata.json"),
                        "--contract",
                        str(CONTRACT_PATH),
                    ]
                )
            created_summary = json.loads(created_stdout.getvalue())
            inspected_summary = json.loads(inspected_stdout.getvalue())
        self.assertEqual(created, 0)
        self.assertEqual(inspected, 0)
        self.assertEqual(created_summary, inspected_summary)
        self.assertEqual(inspected_summary["array_members_opened"], 0)
        self.assertEqual(inspected_summary["item_count"], 48)


if __name__ == "__main__":
    unittest.main()
