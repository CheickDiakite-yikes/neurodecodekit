import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock

from neurodecodekit.cli import build_parser
from neurodecodekit.experiments.failure_localization import (
    FORBIDDEN_ACCESS_COUNTERS,
    PREFIX_SIZES,
    REPORT_SCHEMA_NAME,
    REPORT_SCHEMA_VERSION,
    SEEDS,
    Loop48Refusal,
    StageACaps,
    apply_ordered_failure_tree,
    inspect_failure_localization_report,
    recompute_aggregate_evidence,
    registered_stage_a_caps,
    run_failure_localization_stage_a,
    run_registered_failure_localization,
)


def _candidate_id(size, seed):
    return f"L33-N{size:02d}-S{seed}"


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    return {
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _ordered_classes():
    labels = {
        "F1": "identity_or_provenance_breach",
        "F2": "temporal_or_ctc_infeasibility",
        "F5": "model_fit_output_distribution_instability",
        "F3": "signal_quality_insufficiency",
        "F4": "preprocessing_or_temporal_resolution_mismatch",
        "F6": "stable_but_nonseparable_sensor_representation",
        "F7": "prior_dominated_task_regime",
        "U0": "unresolved",
    }
    order = ("F1", "F2", "F5", "F3", "F4", "F6", "F7", "U0")
    return [
        {
            "order": index,
            "class_id": class_id,
            "label": labels[class_id],
            "root_cause_claim_allowed": False,
        }
        for index, class_id in enumerate(order, start=1)
    ]


def _authorization():
    true_fields = (
        "loop48_artifact_only_implementation_authorized_now",
        "exact_four_committed_json_reads_authorized_now",
        "exact_input_sha256_verification_authorized_now",
        "frozen_aggregate_recomputation_authorized_now",
        "fixed_prefix_seed_dispersion_checks_authorized_now",
        "ordered_eight_class_tree_authorized_now",
        "one_aggregate_target_free_report_authorized_now",
        "one_stage_a_execution_authorized_now",
    )
    false_fields = (
        "git_ignored_loop26_output_read_authorized_now",
        "cache_or_member_read_authorized_now",
        "target_read_authorized_now",
        "model_inference_authorized_now",
        "rerun_authorized_now",
    )
    values = {name: True for name in true_fields}
    values.update({name: False for name in false_fields})
    return {"schema_name": "synthetic-loop48-authorization", "authorization": values}


def _synthetic_values():
    blank_rows = {
        8: (0.10, 0.40, 0.20),
        16: (0.20, 0.60, 0.30),
        24: (0.10, 0.50, 0.20),
        32: (0.20, 0.70, 0.30),
        44: (0.10, 0.40, 0.20),
        55: (0.99, 0.70, 0.50),
    }
    cer_rows = {size: (0.90, 0.91, 0.92) for size in PREFIX_SIZES}
    cer_rows[55] = (0.90, 0.95, 0.85)
    metrics = {}
    for size in PREFIX_SIZES:
        for index, seed in enumerate(SEEDS):
            metrics[_candidate_id(size, seed)] = {
                "blank_fraction": blank_rows[size][index],
                "macro_sentence_cer": cer_rows[size][index],
                "exact_sentence_count": 0,
            }
        metrics[f"L33-P{size:02d}"] = {
            "blank_fraction": None,
            "macro_sentence_cer": 0.70,
            "exact_sentence_count": 0,
        }
    for condition_id in (
        "L31-E02",
        "L31-E03",
        "L31-E04",
        "L31-E05",
        "L31-E06",
        "L31-E08",
        "L31-E09",
    ):
        metrics[condition_id] = {
            "blank_fraction": 0.5,
            "macro_sentence_cer": 0.8,
            "exact_sentence_count": 0,
        }
    all_blanks = [value for row in blank_rows.values() for value in row]
    prefix_ranges = {
        str(size): max(blank_rows[size]) - min(blank_rows[size]) for size in PREFIX_SIZES
    }
    snapshot = {
        "primary_candidate_id": "L33-N55-S2601",
        "primary_candidate_macro_sentence_cer": 0.90,
        "primary_candidate_blank_fraction": 0.99,
        "primary_candidate_exact_sentences": 0,
        "validation_sentence_count": 6,
        "train_only_prior_id": "L33-P55",
        "train_only_prior_macro_sentence_cer": 0.70,
        "primary_prior_minus_candidate_margin": -0.20,
        "primary_wins_ties_losses": [0, 1, 5],
        "primary_one_sided_exact_p": 1.0,
        "size55_seed_ids": [_candidate_id(55, seed) for seed in SEEDS],
        "size55_blank_fractions": list(blank_rows[55]),
        "size55_blank_fraction_min": min(blank_rows[55]),
        "size55_blank_fraction_max": max(blank_rows[55]),
        "size55_blank_fraction_range": max(blank_rows[55]) - min(blank_rows[55]),
        "size55_macro_sentence_cers": list(cer_rows[55]),
        "size55_every_seed_worse_than_prior": True,
        "trained_scaling_condition_count": 18,
        "trained_scaling_blank_fraction_min": min(all_blanks),
        "trained_scaling_blank_fraction_max": max(all_blanks),
        "trained_scaling_blank_fraction_range": max(all_blanks) - min(all_blanks),
        "trained_scaling_blank_fraction_ge_0_95_count": 1,
        "trained_scaling_blank_fraction_le_0_05_count": 0,
        "prefix_blank_ranges": prefix_ranges,
        "prefix_groups_with_blank_range_at_least_0_25": 6,
        "prefix_group_count": 6,
        "source_cache_preprocessing_is_causal": False,
        "loop25_mechanics_produced_source_cache": False,
    }
    return metrics, snapshot


def _make_bundle(root):
    metrics, snapshot = _synthetic_values()
    artifacts = {
        "loop26_consumed_result": {
            "schema_name": "neurodecodekit.loop26_shared_validation_score",
            "validation_items": 6,
            "condition_metrics": metrics,
            "exact_comparisons": {
                "L31-E01": {
                    "wins": 0,
                    "ties": 1,
                    "losses": 5,
                    "one_sided_greater_p": 1.0,
                }
            },
            "plaintext_targets_or_predictions_present": False,
        },
        "loop26_prediction_freeze": {
            "schema_name": "neurodecodekit.loop26_prediction_freeze",
            "prediction_sets": [{"condition_id": "L33-N55-S2601", "payload_sha256": "a" * 64}],
            "plaintext_predictions_committed": False,
            "validation_target_rows_delivered": 0,
        },
        "loop26_shared_contract": {
            "schema_name": "neurodecodekit.loop26_shared_validation_contract",
            "split_firewall": "synthetic",
        },
        "loop25_causal_mechanics_result": {
            "schema_name": "neurodecodekit.loop25_causal_preprocessing_result",
            "mechanics_only": True,
        },
    }
    specs = []
    for artifact_id, payload in artifacts.items():
        relative = Path("inputs") / f"{artifact_id}.json"
        identity = _write_json(root / relative, payload)
        specs.append(
            {
                "artifact_id": artifact_id,
                "path": str(relative),
                "bytes": identity["bytes"],
                "sha256": identity["sha256"],
                "contains_plaintext_targets_or_predictions": False,
            }
        )
    contract = {
        "committed_input_artifacts": specs,
        "ordered_failure_classes": _ordered_classes(),
        "observed_aggregate_snapshot": snapshot,
        "unavailable_root_cause_fields": ["training_dynamics", "signal_quality"],
        "future_artifact_only_stage_a": {
            "descriptive_thresholds": {
                "primary_blank_dominant_at_or_above": 0.95,
                "fixed_prefix_seed_blank_range_unstable_at_or_above": 0.25,
                "minimum_unstable_prefix_groups_for_F5": 1,
                "require_every_size55_seed_worse_than_prior_for_F5": True,
                "require_primary_exact_sentence_count_for_F5": 0,
            },
            "expected_primary_class_if_bound_artifacts_remain_exact": "F5",
        },
        "resource_caps": {
            "future_stage_a_cpu_threads": 1,
            "future_stage_a_workers": 1,
            "future_stage_a_runtime_sec": 30,
            "future_stage_a_peak_rss_bytes": 256 * 1024**2,
            "future_stage_a_generated_bytes": 1024**2,
            "future_stage_a_network_calls": 0,
            "future_stage_a_model_runs": 0,
            "future_stage_a_training_runs": 0,
            "future_stage_a_downloaded_bytes": 0,
        },
    }
    return {"artifacts": artifacts, "specs": specs, "contract": contract}


def _run(root, bundle, output, *, caps=None):
    synthetic_caps = caps or StageACaps(peak_rss_bytes=1024**3)
    return run_failure_localization_stage_a(
        artifact_root=root,
        artifact_specs=bundle["specs"],
        contract=bundle["contract"],
        authorization_decision=_authorization(),
        contract_sha256="a" * 64,
        authorization_decision_sha256="b" * 64,
        authorization_commit="c" * 40,
        implementation_commit="d" * 40,
        implementation_push_ci_run_id=101,
        implementation_pr_ci_run_id=102,
        output_path=output,
        caps=synthetic_caps,
    )


def _rewrite_artifact(root, bundle, artifact_id, payload):
    spec = next(row for row in bundle["specs"] if row["artifact_id"] == artifact_id)
    identity = _write_json(root / spec["path"], payload)
    spec.update(identity)


class Loop48FailureLocalizationTests(unittest.TestCase):
    def test_synthetic_roundtrip_is_aggregate_only_and_f5(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _make_bundle(root)
            output = root / "result.json"
            report = _run(root, bundle, output)
            summary = inspect_failure_localization_report(output)

            self.assertEqual(report["schema_name"], REPORT_SCHEMA_NAME)
            self.assertEqual(report["schema_version"], REPORT_SCHEMA_VERSION)
            self.assertEqual(summary["primary_failure_class"], "F5")
            self.assertFalse(summary["root_cause_established"])
            self.assertEqual(summary["input_artifact_count"], 4)
            self.assertEqual(report["aggregate_evidence"]["trained_scaling_condition_count"], 18)
            self.assertEqual(len(report["aggregate_evidence"]["prefix_blank_ranges"]), 6)
            self.assertEqual(report["access_counters"]["runtime_committed_json_reads"], 4)
            self.assertEqual(output.stat().st_size, report["generated_bytes"])

    def test_recomputed_summary_and_tree_replay_deterministically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _make_bundle(root)
            result = bundle["artifacts"]["loop26_consumed_result"]
            first = recompute_aggregate_evidence(result, bundle["contract"])
            second = recompute_aggregate_evidence(deepcopy(result), deepcopy(bundle["contract"]))
            self.assertEqual(first, second)
            first_class, first_trace = apply_ordered_failure_tree(
                ordered_classes=bundle["contract"]["ordered_failure_classes"],
                aggregate_evidence=first,
                thresholds=bundle["contract"]["future_artifact_only_stage_a"][
                    "descriptive_thresholds"
                ],
                identity_ok=True,
                temporal_ctc_infeasible=None,
            )
            second_class, second_trace = apply_ordered_failure_tree(
                ordered_classes=deepcopy(bundle["contract"]["ordered_failure_classes"]),
                aggregate_evidence=second,
                thresholds=deepcopy(
                    bundle["contract"]["future_artifact_only_stage_a"]["descriptive_thresholds"]
                ),
                identity_ok=True,
                temporal_ctc_infeasible=None,
            )
            self.assertEqual((first_class, first_trace), (second_class, second_trace))

    def test_pure_analysis_never_reads_a_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = _make_bundle(Path(tmp))
            result = bundle["artifacts"]["loop26_consumed_result"]
            with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("read")):
                aggregate = recompute_aggregate_evidence(result, bundle["contract"])
                selected, _ = apply_ordered_failure_tree(
                    ordered_classes=bundle["contract"]["ordered_failure_classes"],
                    aggregate_evidence=aggregate,
                    thresholds=bundle["contract"]["future_artifact_only_stage_a"][
                        "descriptive_thresholds"
                    ],
                    identity_ok=True,
                    temporal_ctc_infeasible=None,
                )
            self.assertEqual(selected["class_id"], "F5")

    def test_hash_mismatch_fails_before_report_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _make_bundle(root)
            path = root / bundle["specs"][0]["path"]
            path.write_bytes(path.read_bytes() + b" ")
            output = root / "result.json"
            with self.assertRaisesRegex(Loop48Refusal, "loop26_consumed_result"):
                _run(root, bundle, output)
            self.assertFalse(output.exists())

    def test_plaintext_target_or_prediction_field_is_refused(self):
        for forbidden_key in ("targets", "predictions"):
            with self.subTest(forbidden_key=forbidden_key), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                bundle = _make_bundle(root)
                payload = deepcopy(bundle["artifacts"]["loop25_causal_mechanics_result"])
                payload[forbidden_key] = ["synthetic-secret"]
                _rewrite_artifact(root, bundle, "loop25_causal_mechanics_result", payload)
                output = root / "result.json"
                with self.assertRaisesRegex(Loop48Refusal, "forbidden plaintext field"):
                    _run(root, bundle, output)
                self.assertFalse(output.exists())

    def test_missing_registered_condition_is_malformed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _make_bundle(root)
            payload = deepcopy(bundle["artifacts"]["loop26_consumed_result"])
            del payload["condition_metrics"]["L33-N24-S2602"]
            _rewrite_artifact(root, bundle, "loop26_consumed_result", payload)
            output = root / "result.json"
            with self.assertRaisesRegex(Loop48Refusal, "missing condition metric"):
                _run(root, bundle, output)
            self.assertFalse(output.exists())

    def test_output_cap_fails_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _make_bundle(root)
            output = root / "result.json"
            caps = StageACaps(peak_rss_bytes=1024**3, generated_output_bytes=512)
            with self.assertRaisesRegex(Loop48Refusal, "generated-output cap"):
                _run(root, bundle, output, caps=caps)
            self.assertFalse(output.exists())

    def test_existing_output_refuses_before_any_input_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _make_bundle(root)
            output = root / "result.json"
            output.write_text("occupied", encoding="utf-8")
            with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("read")):
                with self.assertRaisesRegex(Loop48Refusal, "rerun"):
                    _run(root, bundle, output)

    def test_f1_and_f2_precede_f5(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = _make_bundle(Path(tmp))
            aggregate = recompute_aggregate_evidence(
                bundle["artifacts"]["loop26_consumed_result"], bundle["contract"]
            )
            common = {
                "ordered_classes": bundle["contract"]["ordered_failure_classes"],
                "aggregate_evidence": aggregate,
                "thresholds": bundle["contract"]["future_artifact_only_stage_a"][
                    "descriptive_thresholds"
                ],
            }
            selected, _ = apply_ordered_failure_tree(
                **common, identity_ok=False, temporal_ctc_infeasible=True
            )
            self.assertEqual(selected["class_id"], "F1")
            selected, _ = apply_ordered_failure_tree(
                **common, identity_ok=True, temporal_ctc_infeasible=True
            )
            self.assertEqual(selected["class_id"], "F2")

    def test_every_forbidden_runtime_counter_is_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _make_bundle(root)
            report = _run(root, bundle, root / "result.json")
            self.assertTrue(
                all(report["access_counters"][name] == 0 for name in FORBIDDEN_ACCESS_COUNTERS)
            )
            self.assertFalse(report["producer"]["end_to_end_latency_measured"])

    def test_inspector_rejects_mutated_byte_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _make_bundle(root)
            output = root / "result.json"
            report = _run(root, bundle, output)
            report["generated_bytes"] += 1
            output.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "generated byte count"):
                inspect_failure_localization_report(output)

    def test_registered_wrapper_refuses_alternate_output_before_git_or_input_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("read")):
                with self.assertRaisesRegex(Loop48Refusal, "registered output"):
                    run_registered_failure_localization(
                        repo_root=tmp,
                        implementation_commit="a" * 40,
                        implementation_push_ci_run_id=1,
                        implementation_pr_ci_run_id=2,
                        output_path="elsewhere.json",
                    )

    def test_cli_exposes_run_and_inspect_commands(self):
        parser = build_parser()
        run_args = parser.parse_args(
            [
                "loop48-failure-localization",
                "--implementation-commit",
                "a" * 40,
                "--implementation-push-ci-run-id",
                "101",
                "--implementation-pr-ci-run-id",
                "102",
            ]
        )
        inspect_args = parser.parse_args(["loop48-inspect-failure-localization"])
        self.assertEqual(
            run_args.out,
            "registries/loop48_failure_localization_result.v0.json",
        )
        self.assertEqual(run_args.implementation_push_ci_run_id, 101)
        self.assertEqual(run_args.implementation_pr_ci_run_id, 102)
        self.assertEqual(
            inspect_args.report,
            "registries/loop48_failure_localization_result.v0.json",
        )

    def test_module_has_no_heavy_or_model_dependency(self):
        source_path = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "neurodecodekit"
            / "experiments"
            / "failure_localization.py"
        )
        source = source_path.read_text(encoding="utf-8")
        for forbidden in ("import numpy", "import torch", "import mne", "import scipy"):
            self.assertNotIn(forbidden, source)

    def test_registered_contract_keeps_the_256_mib_peak_rss_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            contract = _make_bundle(Path(tmp))["contract"]
            caps = registered_stage_a_caps(contract)
            self.assertEqual(caps.peak_rss_bytes, 256 * 1024**2)
            self.assertEqual(caps.runtime_sec, 30)
            self.assertEqual(caps.generated_output_bytes, 1024**2)


if __name__ == "__main__":
    unittest.main()
