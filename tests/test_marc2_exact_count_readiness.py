import ast
import copy
import io
import unittest
from contextlib import redirect_stderr

from neurodecodekit.datasets import marc2_exact_count_readiness as subject


class Marc2ExactCountReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = subject.load_registered_contract()

    def test_plan_is_generated_only_and_exact(self):
        plan = subject.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR33A")
        self.assertEqual(plan["sample_count"], 3)
        self.assertEqual(plan["interval_seconds"], 5.0)
        self.assertEqual(plan["paths"], 16)
        self.assertEqual(plan["provider_calls"], 48)
        self.assertEqual(plan["sleeper_calls"], 32)
        self.assertFalse(plan["private_executor_available"])
        self.assertFalse(plan["FW2_or_CIL1_authorized"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_all_patterns_use_three_provider_calls_and_two_sleeps(self):
        for pattern in subject.PATTERNS:
            result, providers, sleepers, _bytes, unchanged = (
                subject._collect_pattern(pattern)
            )
            self.assertEqual(providers, 3)
            self.assertEqual(sleepers, 2)
            self.assertEqual(result.ready, pattern == "PPP")
            self.assertEqual(tuple(item.sequence for item in result.samples), (1, 2, 3))
            self.assertTrue(unchanged)

    def test_result_uses_frozen_immutable_copies(self):
        source = [subject._sample_payload(index, True) for index in (1, 2, 3)]
        sleeps = []
        result = subject.collect_exact_readiness(
            lambda sequence: source[sequence - 1], sleeps.append
        )
        source[0]["passing"] = False
        self.assertTrue(result.ready)
        self.assertTrue(result.samples[0].passing)
        self.assertEqual(sleeps, [5.0, 5.0])
        with self.assertRaises((AttributeError, TypeError)):
            result.samples[0].passing = False

    def test_malformed_samples_fail_closed(self):
        bad_values = (
            None,
            {},
            {**subject._sample_payload(1, True), "extra": "x"},
            {**subject._sample_payload(1, True), "sequence": 2},
            {**subject._sample_payload(1, True), "passing": 1},
            {**subject._sample_payload(1, True), "observed_at_seconds": float("nan")},
            {**subject._sample_payload(1, True), "available_bytes": -1},
        )
        for value in bad_values:
            with self.assertRaises(subject.ExactCountReadinessRefusal):
                subject._validated_sample(value, 1)

    def test_provider_and_sleeper_exceptions_fail_closed(self):
        def provider_error(_sequence):
            raise RuntimeError("generated provider error")

        def sleeper_error(_interval):
            raise RuntimeError("generated sleeper error")

        with self.assertRaises(subject.ExactCountReadinessRefusal):
            subject.collect_exact_readiness(provider_error, lambda _: None)
        with self.assertRaises(subject.ExactCountReadinessRefusal):
            subject.collect_exact_readiness(
                lambda sequence: subject._sample_payload(sequence, True),
                sleeper_error,
            )

    def test_collection_has_no_while_loop_or_filesystem_name(self):
        source = ast.parse(
            __import__("inspect").getsource(subject.collect_exact_readiness)
        )
        self.assertFalse(any(isinstance(node, ast.While) for node in ast.walk(source)))
        names = {
            node.id for node in ast.walk(source) if isinstance(node, ast.Name)
        }
        self.assertTrue({"open", "Path", "read_text", "read_bytes"}.isdisjoint(names))

    def test_contract_and_environment_fail_closed(self):
        changed = copy.deepcopy(self.contract)
        changed["lane_id"] = "MARC2-VR33A-mutated"
        with self.assertRaises(subject.ExactCountReadinessRefusal):
            subject._verify_contract_mapping(changed)
        environment = dict(subject.THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with self.assertRaises(subject.ExactCountReadinessRefusal):
            subject._validate_thread_environment(environment)

    def test_direct_refusal_floor_passes(self):
        self.assertGreaterEqual(subject._run_direct_refusals(self.contract), 40)

    def test_resources_fail_closed(self):
        caps = self.contract["resource_limits"]
        with self.assertRaises(subject.ExactCountReadinessRefusal):
            subject._assert_resources(
                runtime_seconds=caps["runtime_seconds"] + 1,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                contract=self.contract,
            )

    def test_cli_has_no_execute_or_override_surface(self):
        for argv in (
            ["execute"],
            ["inspect"],
            ["plan", "--source", "/tmp/other"],
            ["qualify", "--count", "5"],
            ["qualify", "--interval", "0"],
        ):
            with redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    subject.main(argv)


if __name__ == "__main__":
    unittest.main()
