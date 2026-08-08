import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/synthetic_motor_fixture_contract.v0.json"


class SyntheticMotorFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
            import scipy  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("NumPy and SciPy are optional") from None
        cls.np = np

    @staticmethod
    def _make(root: Path, name: str = "fixture") -> Path:
        from neurodecodekit.training.synthetic_motor_fixture import (
            prepare_synthetic_motor_fixture,
        )

        output = root / name
        prepare_synthetic_motor_fixture(output, contract_path=CONTRACT_PATH)
        return output / "metadata.json"

    @staticmethod
    def _write_self_sized_sidecar(path: Path, sidecar: dict) -> None:
        for _ in range(10):
            payload = (json.dumps(sidecar, indent=2, sort_keys=True) + "\n").encode()
            sidecar["artifacts"]["metadata_sidecar_bytes"] = len(payload)
            sidecar["artifacts"]["total_output_bytes"] = sidecar["artifacts"][
                "payload_bytes"
            ] + len(payload)
        path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_module_import_is_lazy_for_numpy_and_scipy(self):
        code = """
import sys
assert 'numpy' not in sys.modules
assert 'scipy' not in sys.modules
import neurodecodekit.training.synthetic_motor_fixture
assert 'numpy' not in sys.modules
assert 'scipy' not in sys.modules
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_replay_is_byte_identical_bounded_and_loadable(self):
        from neurodecodekit.training.synthetic_motor_fixture import (
            load_synthetic_motor_fixture,
            load_synthetic_motor_metadata,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = self._make(root, "first")
            second = self._make(root, "second")
            for name in ("fixture.npz", "metadata.json"):
                self.assertEqual(
                    (first.parent / name).read_bytes(), (second.parent / name).read_bytes()
                )
            sidecar = load_synthetic_motor_metadata(first, contract_path=CONTRACT_PATH)
            fixture = load_synthetic_motor_fixture(first, contract_path=CONTRACT_PATH)

        self.assertLessEqual(sidecar["artifacts"]["total_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(sidecar["artifacts"]["output_files"], 2)
        self.assertEqual(fixture.signals.shape, (96, 8, 256))
        self.assertEqual(fixture.signals.dtype, self.np.dtype("float32"))
        self.assertEqual(
            set(fixture.opened_members), set(fixture.sidecar["payload"]["array_members"])
        )

    def test_factor_inventory_pair_partitions_and_analytic_gates_are_exact(self):
        from neurodecodekit.training.synthetic_motor_fixture import (
            FACTOR_IDS,
            load_synthetic_motor_fixture,
        )

        with tempfile.TemporaryDirectory() as temporary:
            fixture = load_synthetic_motor_fixture(
                self._make(Path(temporary)),
                contract_path=CONTRACT_PATH,
            )
        metadata = fixture.metadata
        self.assertEqual(metadata["factor_counts"], {name: 12 for name in FACTOR_IDS})
        self.assertEqual(metadata["partition_counts"], {"train": 48, "check": 32, "final": 16})
        self.assertEqual(metadata["pair_count"], 48)
        self.assertTrue(all(row["passed"] for row in metadata["factor_diagnostics"].values()))
        self.assertLess(
            metadata["factor_diagnostics"]["left_right_spatial_reversal"][
                "mean_potential_lateralization"
            ],
            0.0,
        )

    def test_masks_timestamps_padding_geometry_and_array_hashes_are_strict(self):
        from neurodecodekit.training.synthetic_motor_fixture import (
            load_synthetic_motor_fixture,
            validate_synthetic_motor_arrays,
        )

        with tempfile.TemporaryDirectory() as temporary:
            fixture = load_synthetic_motor_fixture(
                self._make(Path(temporary)),
                contract_path=CONTRACT_PATH,
            )
        validate_synthetic_motor_arrays(fixture.arrays, expected_metadata=fixture.metadata)
        for row, length_value in enumerate(fixture.valid_lengths.tolist()):
            length = int(length_value)
            self.assertTrue(fixture.valid_mask[row, :length].all())
            self.assertFalse(fixture.valid_mask[row, length:].any())
            self.assertTrue((fixture.timestamps_sec[row, :length] < 0.0).all())
            self.assertTrue(self.np.equal(fixture.signals[row, :, length:], 0.0).all())
        self.assertEqual(
            fixture.arrays["channel_names"].tolist(), [f"SYN{i:02d}" for i in range(8)]
        )
        self.assertEqual(fixture.metadata["identity"]["geometry_units"], "synthetic_arbitrary_unit")

    def test_timing_only_and_pure_noise_pairs_have_frozen_relations(self):
        from neurodecodekit.training.synthetic_motor_fixture import load_synthetic_motor_fixture

        with tempfile.TemporaryDirectory() as temporary:
            fixture = load_synthetic_motor_fixture(
                self._make(Path(temporary)),
                contract_path=CONTRACT_PATH,
            )
        for factor, expected_difference, timing_equal in (
            ("timing_only_labels_without_signal_relation", 16, False),
            ("pure_noise", 0, True),
        ):
            indices = self.np.flatnonzero(fixture.arrays["factor_ids"] == factor).tolist()
            for offset in range(0, len(indices), 2):
                first, second = indices[offset : offset + 2]
                first_length = int(fixture.valid_lengths[first])
                second_length = int(fixture.valid_lengths[second])
                shared = min(first_length, second_length)
                self.assertTrue(
                    self.np.array_equal(
                        fixture.signals[first, :, :shared],
                        fixture.signals[second, :, :shared],
                    )
                )
                self.assertEqual(abs(first_length - second_length), expected_difference)
                self.assertEqual(
                    self.np.array_equal(
                        fixture.timestamps_sec[first, :first_length],
                        fixture.timestamps_sec[second, :second_length],
                    ),
                    timing_equal,
                )

    def test_every_mutation_is_deterministic_shape_preserving_and_zero_padded(self):
        from neurodecodekit.training.synthetic_motor_fixture import (
            MUTATION_IDS,
            apply_synthetic_motor_mutation,
            load_synthetic_motor_fixture,
        )

        with tempfile.TemporaryDirectory() as temporary:
            fixture = load_synthetic_motor_fixture(
                self._make(Path(temporary)),
                contract_path=CONTRACT_PATH,
            )
        for mutation_id in MUTATION_IDS:
            first = apply_synthetic_motor_mutation(fixture, mutation_id)
            second = apply_synthetic_motor_mutation(fixture, mutation_id)
            self.assertTrue(self.np.array_equal(first, second), mutation_id)
            self.assertEqual(first.shape, fixture.signals.shape)
            self.assertEqual(first.dtype, fixture.signals.dtype)
            for row, length_value in enumerate(fixture.valid_lengths.tolist()):
                self.assertTrue(self.np.equal(first[row, :, int(length_value) :], 0.0).all())

    def test_future_tail_mutation_preserves_every_prefix_value(self):
        from neurodecodekit.training.synthetic_motor_fixture import (
            apply_synthetic_motor_mutation,
            load_synthetic_motor_fixture,
        )

        with tempfile.TemporaryDirectory() as temporary:
            fixture = load_synthetic_motor_fixture(
                self._make(Path(temporary)),
                contract_path=CONTRACT_PATH,
            )
        mutated = apply_synthetic_motor_mutation(
            fixture,
            "future_tail_mutation",
            cutoff_sample=128,
        )
        self.assertTrue(self.np.array_equal(mutated[:, :, :129], fixture.signals[:, :, :129]))
        self.assertFalse(self.np.array_equal(mutated[:, :, 129:], fixture.signals[:, :, 129:]))

    def test_metadata_only_inspection_never_opens_numpy_arrays(self):
        from neurodecodekit.training.synthetic_motor_fixture import load_synthetic_motor_metadata

        with tempfile.TemporaryDirectory() as temporary:
            metadata = self._make(Path(temporary))
            with mock.patch("numpy.load", side_effect=AssertionError("array opened")) as loader:
                sidecar = load_synthetic_motor_metadata(metadata, contract_path=CONTRACT_PATH)
        loader.assert_not_called()
        self.assertEqual(sidecar["payload"]["array_members"].count("signals"), 1)

    def test_payload_tampering_and_hidden_target_member_fail_closed(self):
        from neurodecodekit.training.synthetic_motor_fixture import (
            _deterministic_npz_bytes,
            load_synthetic_motor_fixture,
            load_synthetic_motor_metadata,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            metadata_path = self._make(root)
            payload_path = metadata_path.parent / "fixture.npz"
            original = payload_path.read_bytes()
            payload_path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                load_synthetic_motor_metadata(metadata_path, contract_path=CONTRACT_PATH)

            payload_path.write_bytes(original)
            fixture = load_synthetic_motor_fixture(metadata_path, contract_path=CONTRACT_PATH)
            arrays = dict(fixture.arrays)
            arrays["target_text"] = self.np.asarray(["forbidden"])
            hidden_payload = _deterministic_npz_bytes(arrays)
            payload_path.write_bytes(hidden_payload)
            sidecar = json.loads(metadata_path.read_text(encoding="utf-8"))
            sidecar["payload"]["bytes"] = len(hidden_payload)
            sidecar["payload"]["sha256"] = hashlib.sha256(hidden_payload).hexdigest()
            sidecar["artifacts"]["payload_bytes"] = len(hidden_payload)
            self._write_self_sized_sidecar(metadata_path, sidecar)
            with self.assertRaisesRegex(ValueError, "member set mismatch"):
                load_synthetic_motor_metadata(metadata_path, contract_path=CONTRACT_PATH)

    def test_forbidden_metadata_padding_and_split_mutations_fail_closed(self):
        from neurodecodekit.training.synthetic_motor_fixture import (
            load_synthetic_motor_fixture,
            validate_synthetic_motor_arrays,
        )

        with tempfile.TemporaryDirectory() as temporary:
            fixture = load_synthetic_motor_fixture(
                self._make(Path(temporary)),
                contract_path=CONTRACT_PATH,
            )
        forbidden = {name: value.copy() for name, value in fixture.arrays.items()}
        metadata = dict(fixture.metadata)
        metadata["target_text"] = "forbidden"
        forbidden["metadata"] = self.np.asarray(json.dumps(metadata, sort_keys=True))
        with self.assertRaisesRegex(ValueError, "forbidden field"):
            validate_synthetic_motor_arrays(forbidden)

        padding = {name: value.copy() for name, value in fixture.arrays.items()}
        length = int(padding["valid_lengths"][0])
        padding["signals"][0, 0, length] = 1.0
        with self.assertRaisesRegex(ValueError, "padding"):
            validate_synthetic_motor_arrays(padding)

        split = {name: value.copy() for name, value in fixture.arrays.items()}
        split["partition_ids"][1] = "check"
        with self.assertRaisesRegex(ValueError, "partition identity"):
            validate_synthetic_motor_arrays(split)

    def test_output_cap_collision_and_contract_substitution_are_refused(self):
        from neurodecodekit.training.synthetic_motor_fixture import (
            prepare_synthetic_motor_fixture,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            capped = root / "capped"
            with self.assertRaisesRegex(ValueError, "exceeding cap"):
                prepare_synthetic_motor_fixture(
                    capped,
                    contract_path=CONTRACT_PATH,
                    max_output_bytes=1024,
                )
            self.assertFalse(capped.exists())

            existing = root / "existing"
            existing.mkdir()
            marker = existing / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                prepare_synthetic_motor_fixture(existing, contract_path=CONTRACT_PATH)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

            substituted = root / "contract.json"
            substituted.write_bytes(CONTRACT_PATH.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                prepare_synthetic_motor_fixture(root / "substituted", contract_path=substituted)

    def test_cli_create_and_metadata_only_inspect_roundtrip(self):
        from neurodecodekit.cli import main

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            created_stdout = io.StringIO()
            with contextlib.redirect_stdout(created_stdout):
                created = main(
                    [
                        "make-synthetic-motor-fixture",
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
                        "inspect-synthetic-motor-fixture",
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
        self.assertEqual(inspected_summary["access_counters"]["model_inference_runs"], 0)
        self.assertFalse(inspected_summary["end_to_end_latency_measured"])


if __name__ == "__main__":
    unittest.main()
