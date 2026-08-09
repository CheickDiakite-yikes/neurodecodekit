import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/causal_motor_lattice_synthetic_contract.v0.json"


class CausalMotorLatticeSyntheticBaseTests(unittest.TestCase):
    def test_modules_import_without_optional_scientific_dependencies(self):
        code = """
import sys
blocked = ('numpy', 'scipy', 'torch', 'mne', 'sklearn', 'pyriemann')
assert all(name not in sys.modules for name in blocked)
import neurodecodekit.models.causal_motor_lattice
import neurodecodekit.experiments.causal_motor_lattice_synthetic
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

    def test_dry_run_plan_uses_no_optional_import_or_output(self):
        code = """
import json
import sys
from neurodecodekit.cli import main
blocked = ('numpy', 'scipy', 'torch', 'mne', 'sklearn', 'pyriemann')
assert main(['cml-v0-synthetic']) == 0
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
        plan = json.loads(result.stdout)
        self.assertFalse(plan["execution_requested"])
        self.assertEqual(plan["candidate"]["trainable_parameters"], 4535)
        self.assertEqual(plan["access_counters"]["parameter_update_runs"], 0)

    def test_contract_substitution_and_execution_without_proof_fail_closed(self):
        from neurodecodekit.experiments.causal_motor_lattice_synthetic import (
            execute_cml_synthetic_gate,
        )
        from neurodecodekit.models.causal_motor_lattice import (
            load_registered_cml_synthetic_contract,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            substitute = root / "contract.json"
            payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
            payload["training_recipe"]["optimizer_steps"] = 599
            substitute.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "byte count|SHA-256"):
                load_registered_cml_synthetic_contract(substitute)
            with self.assertRaisesRegex(ValueError, "40-character"):
                execute_cml_synthetic_gate(
                    root / "out",
                    implementation_commit="bad",
                    implementation_ci_run=1,
                    contract_path=CONTRACT_PATH,
                )

    def test_cli_help_exposes_dry_run_and_inspector(self):
        for command in ("cml-v0-synthetic", "inspect-cml-v0-synthetic"):
            result = subprocess.run(
                [sys.executable, "-m", "neurodecodekit.cli", command, "--help"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--execute", subprocess.run(
            [sys.executable, "-m", "neurodecodekit.cli", "cml-v0-synthetic", "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
@unittest.skipUnless(importlib.util.find_spec("torch"), "Torch not installed")
class CausalMotorLatticeSyntheticArrayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from neurodecodekit.experiments.causal_motor_lattice_synthetic import (
            prepare_cml_synthetic_inputs,
        )
        from neurodecodekit.models.causal_motor_lattice import load_registered_cml_synthetic_contract

        cls.np = np
        cls.contract = load_registered_cml_synthetic_contract(CONTRACT_PATH)
        cls.inputs = prepare_cml_synthetic_inputs(contract_path=CONTRACT_PATH)

    def _run_torch_qualification(self, body: str) -> None:
        code = f"""
import torch
from neurodecodekit.experiments.causal_motor_lattice_synthetic import prepare_cml_synthetic_inputs
from neurodecodekit.models.causal_motor_lattice import (
    build_causal_motor_lattice_model,
    count_trainable_parameters,
    load_registered_cml_synthetic_contract,
)
torch.set_num_threads(1)
torch.manual_seed(5513)
contract = load_registered_cml_synthetic_contract()
inputs = prepare_cml_synthetic_inputs()
model = build_causal_motor_lattice_model(contract=contract)
model.eval()
{body}
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env={
                **dict(__import__("os").environ),
                "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "VECLIB_MAXIMUM_THREADS": "1",
                "NUMEXPR_NUM_THREADS": "1",
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_projection_filters_lattice_and_parameter_ledger_are_exact(self):
        from neurodecodekit.models.causal_motor_lattice import (
            build_causal_filter_coefficients,
            build_lattice_incidence,
            build_synthetic_projection,
        )

        projection = build_synthetic_projection(contract=self.contract)
        filters = build_causal_filter_coefficients(contract=self.contract)
        incidence = build_lattice_incidence(contract=self.contract)
        self.assertEqual(projection.shape, (64, 8))
        self.assertEqual(int(self.np.linalg.matrix_rank(projection)), 8)
        self.assertEqual(incidence.shape, (29, 18))
        self.assertEqual(filters["mu"].shape, (33,))
        self.assertEqual(filters["beta"].shape, (33,))
        self._run_torch_qualification(
            """
assert count_trainable_parameters(model) == 4535
assert model.lattice_incidence.shape == (29, 18)
"""
        )

    def test_pair_anchored_adapter_blocks_length_and_noise_shortcuts(self):
        inputs = self.inputs
        self.assertEqual(inputs.normalized_signal.shape, (96, 64, 96))
        self.assertEqual(inputs.valid_mask.shape, (96, 96))
        self.assertTrue(inputs.valid_mask.all())
        self.assertEqual(int((inputs.partition_ids == "train").sum()), 48)
        self.assertEqual(int((inputs.partition_ids == "check").sum()), 32)
        self.assertEqual(int((inputs.partition_ids == "final").sum()), 16)
        for factor_id in (
            "timing_only_labels_without_signal_relation",
            "pure_noise",
        ):
            pair_values = inputs.pair_ids[inputs.factor_ids == factor_id]
            for pair_id in sorted(set(pair_values.tolist())):
                rows = self.np.flatnonzero(inputs.pair_ids == pair_id)
                self.assertTrue(
                    self.np.array_equal(inputs.source_crops[rows[0]], inputs.source_crops[rows[1]])
                )
                self.assertTrue(
                    self.np.array_equal(
                        inputs.normalized_signal[rows[0]],
                        inputs.normalized_signal[rows[1]],
                    )
                )

    def test_zero_update_forward_shapes_residual_and_hand_marginal(self):
        self._run_torch_qualification(
            """
signal = torch.as_tensor(inputs.normalized_signal[:4], dtype=torch.float32)
mask = torch.as_tensor(inputs.valid_mask[:4], dtype=torch.bool)
with torch.no_grad():
    output = model(signal, mask)
assert output['key_logits'].shape == (4, 29)
assert output['primitive_logits'].shape == (4, 18)
assert output['hand_probabilities'].shape == (4, 2)
assert output['fused_features'].shape == (4, 72)
assert float(output['bounded_residual'].abs().max().item()) <= 0.25 + 1e-7
key = output['key_probabilities']
left = key[:, :14].sum(dim=1)
right = key[:, 14:28].sum(dim=1)
expected = torch.stack((left, right), dim=1) / (left + right)[:, None]
assert torch.allclose(output['hand_probabilities'], expected, atol=1e-7, rtol=0.0)
"""
        )

    def test_common_mode_and_future_tail_are_causally_invisible(self):
        self._run_torch_qualification(
            """
signal = torch.as_tensor(inputs.normalized_signal[:4], dtype=torch.float32)
full_mask = torch.ones((4, 96), dtype=torch.bool)
time = torch.arange(96, dtype=torch.float32) / 128.0
common = 0.5 * torch.sin(2.0 * 3.141592653589793 * 3.0 * time)
with torch.no_grad():
    original = model(signal, full_mask)['key_logits']
    common_mode = model(signal + common[None, None, :], full_mask)['key_logits']
assert float((original - common_mode).abs().max().item()) <= 1e-6
mutated = signal.clone()
mutated[:, :, 64:] += torch.arange(1, 65, dtype=torch.float32)[None, :, None]
prefix_mask = torch.zeros((4, 96), dtype=torch.bool)
prefix_mask[:, :64] = True
with torch.no_grad():
    prefix = model(signal, prefix_mask)['key_logits']
    changed = model(mutated, prefix_mask)['key_logits']
assert torch.equal(prefix, changed)
"""
        )

    def test_malformed_model_inputs_and_unknown_view_fail_closed(self):
        self._run_torch_qualification(
            """
signal = torch.zeros((2, 64, 95), dtype=torch.float32)
mask = torch.ones((2, 95), dtype=torch.bool)
try:
    model(signal, mask)
except ValueError as exc:
    assert 'signal shape' in str(exc)
else:
    raise AssertionError('malformed shape was accepted')
valid_signal = torch.zeros((2, 64, 96), dtype=torch.float32)
valid_mask = torch.ones((2, 96), dtype=torch.bool)
try:
    model(valid_signal, valid_mask, muted_views=('unknown',))
except ValueError as exc:
    assert 'unknown CML-v0 muted' in str(exc)
else:
    raise AssertionError('unknown view was accepted')
"""
        )


if __name__ == "__main__":
    unittest.main()
