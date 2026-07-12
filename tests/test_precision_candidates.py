import hashlib
import types
import unittest


class PrecisionCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
            import torch
        except ImportError:
            raise unittest.SkipTest("NumPy and PyTorch are optional") from None
        cls.np = np
        cls.torch = torch

    def _source(self):
        from neurodecodekit.models.tiny_causal_encoder import _build_model

        torch = self.torch
        torch.manual_seed(9024)
        model = _build_model(
            torch,
            input_dim=5 * 16,
            hidden_dim=12,
            embedding_dim=8,
            n_classes=6,
        ).to("cpu")
        model.eval()
        parameter_count = sum(int(value.numel()) for value in model.parameters())
        self.assertEqual(parameter_count, 1130)
        return types.SimpleNamespace(
            model=model,
            normalization_mean=self.np.linspace(-0.2, 0.2, 5, dtype="float32"),
            normalization_std=self.np.linspace(0.8, 1.2, 5, dtype="float32"),
            n_channels=5,
            source_sampling_rate_hz=100.0,
            embedding_dim=8,
            kernel_size=16,
            stride=4,
            n_classes=6,
            trainable_parameter_count=parameter_count,
            parameter_payload_sha256="a" * 64,
        )

    def _source_frame_output(self, source, frame):
        normalized = (
            (
                frame.reshape(5, 16)
                - source.normalization_mean[:, None]
            )
            / source.normalization_std[:, None]
        ).reshape(1, -1)
        with self.torch.inference_mode():
            embedding = source.model.encode(self.torch.from_numpy(normalized))
            logits = source.model.probe(embedding)
        return (
            embedding.detach().cpu().numpy().astype("float32", copy=True)[0],
            logits.detach().cpu().numpy().astype("float32", copy=True)[0],
        )

    def test_float32_reference_is_bitwise_source_equivalent_and_nonmutating(self):
        from neurodecodekit.models.precision_candidates import (
            FLOAT32_REFERENCE,
            build_precision_candidate,
        )

        source = self._source()
        before = {
            name: hashlib.sha256(value.detach().cpu().numpy().tobytes()).hexdigest()
            for name, value in source.model.state_dict().items()
        }
        frame = self.np.linspace(-3.0, 3.0, 80, dtype="float32")
        expected_embedding, expected_logits = self._source_frame_output(source, frame)
        candidate = build_precision_candidate(source, FLOAT32_REFERENCE)
        embedding, logits = candidate.run_frame(frame)
        self.assertTrue(self.np.array_equal(embedding, expected_embedding))
        self.assertTrue(self.np.array_equal(logits, expected_logits))
        self.assertEqual(set(candidate.provenance.weight_dtypes.values()), {"float32"})
        self.assertFalse(candidate.provenance.fallback_used)
        after = {
            name: hashlib.sha256(value.detach().cpu().numpy().tobytes()).hexdigest()
            for name, value in source.model.state_dict().items()
        }
        self.assertEqual(before, after)

    def test_explicit_float16_stays_cpu_half_and_returns_finite_float32(self):
        from neurodecodekit.models.precision_candidates import (
            FLOAT16_EAGER_CPU,
            build_precision_candidate,
        )

        candidate = build_precision_candidate(self._source(), FLOAT16_EAGER_CPU)
        self.assertEqual(set(candidate.provenance.weight_dtypes.values()), {"float16"})
        self.assertEqual(candidate.provenance.unavailable_fields, ("hardware_accumulation_dtype",))
        self.assertTrue(
            all(
                value.device.type == "cpu" and value.dtype == self.torch.float16
                for value in candidate.model.parameters()
            )
        )
        embedding, logits = candidate.run_frame(
            self.np.linspace(-1.5, 2.0, 80, dtype="float32")
        )
        self.assertEqual(embedding.dtype, self.np.dtype("float32"))
        self.assertEqual(logits.dtype, self.np.dtype("float32"))
        self.assertTrue(self.np.isfinite(embedding).all())
        self.assertTrue(self.np.isfinite(logits).all())

    def test_dynamic_qint8_is_real_qnnpack_and_profiler_proven(self):
        from neurodecodekit.models.precision_candidates import (
            API_MIGRATION_WARNING,
            DYNAMIC_QINT8_QNNPACK,
            CandidateUnavailableError,
            build_precision_candidate,
            profile_candidate_operator,
        )

        if "qnnpack" not in self.torch.backends.quantized.supported_engines:
            with self.assertRaises(CandidateUnavailableError):
                build_precision_candidate(self._source(), DYNAMIC_QINT8_QNNPACK)
            return
        candidate = build_precision_candidate(self._source(), DYNAMIC_QINT8_QNNPACK)
        self.assertEqual(candidate.provenance.quantized_engine, "qnnpack")
        self.assertEqual(set(candidate.provenance.weight_dtypes.values()), {"qint8"})
        self.assertIn(API_MIGRATION_WARNING, candidate.provenance.warnings)
        self.assertTrue(
            all("/Users/" not in warning for warning in candidate.provenance.warnings)
        )
        self.assertFalse(candidate.provenance.fallback_used)
        trace = profile_candidate_operator(
            candidate,
            self.np.linspace(-2.0, 2.0, 80, dtype="float32"),
        )
        self.assertTrue(trace["passed"])
        self.assertTrue(
            any("quantized::linear_dynamic" in name for name in trace["operator_names"])
        )
        embedding, logits = candidate.run_frame(
            self.np.linspace(-2.0, 2.0, 80, dtype="float32")
        )
        self.assertTrue(self.np.isfinite(embedding).all())
        self.assertTrue(self.np.isfinite(logits).all())

    def test_numeric_payload_is_deterministic_bounded_and_dtype_explicit(self):
        from neurodecodekit.models.precision_candidates import (
            CANDIDATE_IDS,
            CandidateUnavailableError,
            build_precision_candidate,
            candidate_storage_summary,
            serialize_candidate_numeric_payload,
        )

        for candidate_id in CANDIDATE_IDS:
            try:
                first = build_precision_candidate(self._source(), candidate_id)
                second = build_precision_candidate(self._source(), candidate_id)
            except CandidateUnavailableError:
                self.assertEqual(candidate_id, "dynamic_qint8_qnnpack")
                continue
            first_payload = serialize_candidate_numeric_payload(first)
            second_payload = serialize_candidate_numeric_payload(second)
            self.assertEqual(first_payload, second_payload)
            self.assertLess(len(first_payload), 64 * 1024)
            summary = candidate_storage_summary(first)
            self.assertEqual(
                summary["deterministic_serialized_numeric_payload_bytes"],
                len(first_payload),
            )
            self.assertFalse(summary["serialized_numeric_payload_is_deployable_package"])
            self.assertEqual(summary["logical_parameter_count"], 1130)

    def test_worker_payload_rebuilds_reference_without_checkpoint_io(self):
        from neurodecodekit.models.precision_candidates import (
            FLOAT32_REFERENCE,
            build_precision_candidate,
            build_precision_candidate_from_payload,
            extract_frozen_producer_payload,
        )

        source = self._source()
        payload = extract_frozen_producer_payload(source)
        direct = build_precision_candidate(source, FLOAT32_REFERENCE)
        rebuilt = build_precision_candidate_from_payload(payload, FLOAT32_REFERENCE)
        frame = self.np.linspace(-3.5, 3.5, 80, dtype="float32")
        direct_embedding, direct_logits = direct.run_frame(frame)
        rebuilt_embedding, rebuilt_logits = rebuilt.run_frame(frame)
        self.assertTrue(self.np.array_equal(direct_embedding, rebuilt_embedding))
        self.assertTrue(self.np.array_equal(direct_logits, rebuilt_logits))

    def test_unknown_candidate_refuses_without_fallback(self):
        from neurodecodekit.models.precision_candidates import build_precision_candidate

        with self.assertRaisesRegex(ValueError, "unknown Loop 24 candidate"):
            build_precision_candidate(self._source(), "autocast_magic")


if __name__ == "__main__":
    unittest.main()
