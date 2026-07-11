import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from neurodecodekit.cli import build_parser
from neurodecodekit.evaluation.split_protocol import (
    assign_deterministic_groups,
    build_sentence_text_membership,
    canonicalize_sentence_text,
    normalize_split_ratios,
    official_v2_split_score,
)


NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None


class SplitAssignmentTests(unittest.TestCase):
    def test_matches_neuralset_0_2_2_reference_cases(self):
        self.assertAlmostEqual(
            official_v2_split_score("0", seed=0.0),
            0.18144849969125265,
        )
        assignments = assign_deterministic_groups(
            ["0", "1", "10101001010101"],
            ratios={"train": 0.5, "test": 0.5},
        )
        self.assertEqual(
            {value: row["split"] for value, row in assignments.items()},
            {"0": "train", "1": "test", "10101001010101": "train"},
        )

    def test_canonical_text_groups_case_unicode_and_whitespace(self):
        self.assertEqual(canonicalize_sentence_text("  A\u00a0Ｂ  C  "), "a b c")

    def test_preprocessing_membership_is_plaintext_free_and_hash_stable(self):
        membership = build_sentence_text_membership(
            ["ALPHA", "BRAVO", "DELTA", "FOXTROT"],
            trial_indices=[10, 11, 12, 13],
            ratios={"train": 0.5, "test": 0.5},
        )

        self.assertFalse(membership["contains_plaintext"])
        self.assertEqual(membership["partition_row_counts"], {"train": 2, "test": 2})
        self.assertEqual([row["trial_index"] for row in membership["rows"]], [10, 11, 12, 13])
        self.assertNotIn("ALPHA", str(membership))

    def test_ratio_validation(self):
        self.assertEqual(
            normalize_split_ratios({"train": 0.8, "val": 0.1, "test": 0.1}),
            {"train": 0.8, "val": 0.1, "test": 0.1},
        )
        for invalid in (
            {"train": 1.0},
            {"train": 0.0, "test": 1.0},
            {"train": 0.8, "test": 0.3},
            {"train": float("nan"), "test": 0.5},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                normalize_split_ratios(invalid)

    def test_cli_defaults_are_explicit(self):
        args = build_parser().parse_args(
            [
                "split-protocol",
                "--cache",
                "base.npz",
                "base_qint8.npz",
                "--out-dir",
                "split",
            ]
        )
        self.assertEqual(args.split_type, "sentence-text")
        self.assertEqual(args.text_source, "reference")
        self.assertEqual(args.text_normalization, "canonical-v1")
        self.assertEqual(
            (args.train_ratio, args.val_ratio, args.test_ratio),
            (0.8, 0.1, 0.1),
        )
        self.assertEqual(args.seed, 0.0)

        extraction = build_parser().parse_args(
            [
                "extract-sentence-cache",
                "--raw",
                "block1.fif",
                "--events",
                "logs.mat",
                "--out",
                "sentences.npz",
            ]
        )
        self.assertEqual(extraction.scaler_fit_scope, "recording")
        self.assertEqual(extraction.split_text_normalization, "official-exact")


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class SplitProtocolCacheTests(unittest.TestCase):
    def test_membership_is_order_stable_private_and_fit_scope_explicit(self):
        from neurodecodekit.evaluation.split_protocol import run_split_protocol

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_a = root / "block1.npz"
            cache_b = root / "block2.npz"
            _write_sentence_cache(
                cache_a,
                texts=["ALPHA", "BRAVO", "CHARLIE", "DELTA"],
                trial_indices=[1, 2, 3, 4],
                events_path="/data/21_3660/231204/S21-session1_block1_list1.mat",
                robust_scaler=True,
            )
            _write_sentence_cache(
                cache_b,
                texts=["ALPHA", "ECHO", "FOXTROT", "GOLF"],
                trial_indices=[11, 12, 13, 14],
                events_path="/data/21_3660/231204/S21-session1_block2_list2.mat",
                robust_scaler=True,
            )

            first = run_split_protocol(
                cache_paths=[cache_a, cache_b],
                out_dir=root / "first",
                ratios={"train": 0.5, "test": 0.5},
            )
            second = run_split_protocol(
                cache_paths=[cache_b, cache_a],
                out_dir=root / "second",
                ratios={"train": 0.5, "test": 0.5},
            )

            first_membership = first["membership"]
            self.assertEqual(
                first_membership["group_assignment_sha256"],
                second["membership"]["group_assignment_sha256"],
            )
            self.assertEqual(
                first_membership["membership_sha256"],
                second["membership"]["membership_sha256"],
            )
            self.assertTrue(first_membership["requested_split_usable"])
            self.assertEqual(first_membership["group_cross_split_count"], 0)
            self.assertEqual(first_membership["duplicate_semantic_row_uid_count"], 0)
            self.assertIn(2, [row["row_count"] for row in first_membership["groups"]])
            self.assertFalse(first["fit_scope"]["strict_train_only_ready"])
            self.assertEqual(
                first["decision"]["status"],
                "membership_valid_strict_fit_scope_not_ready",
            )
            self.assertEqual(
                first["capabilities"]["session"]["status"],
                "unavailable_insufficient_groups_for_requested_partitions",
            )
            self.assertEqual(
                first["capabilities"]["subject"]["status"],
                "unavailable_insufficient_groups_for_requested_partitions",
            )
            self.assertTrue(
                all(not source["signal_members_loaded"] for source in first["sources"])
            )
            self.assertFalse(first["run"]["signal_array_members_loaded"])

            json_text = (root / "first" / "split.json").read_text(encoding="utf-8")
            markdown_text = (root / "first" / "split.md").read_text(encoding="utf-8")
            self.assertNotIn("ALPHA", json_text)
            self.assertNotIn("ALPHA", markdown_text)
            self.assertIn(hashlib.sha256(b"alpha").hexdigest(), json_text)
            self.assertEqual(
                first["resources"]["report_json_bytes"],
                (root / "first" / "split.json").stat().st_size,
            )
            self.assertEqual(
                first["resources"]["report_markdown_bytes"],
                (root / "first" / "split.md").stat().st_size,
            )

            with self.assertRaises(FileExistsError):
                run_split_protocol(
                    cache_paths=[cache_a],
                    out_dir=root / "first",
                    ratios={"train": 0.5, "test": 0.5},
                )

    def test_duplicate_physical_rows_across_representations_block_readiness(self):
        from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
        from neurodecodekit.cache.signal_representation import (
            save_signal_representation_cache,
        )
        from neurodecodekit.evaluation.split_protocol import run_split_protocol

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.npz"
            packed = root / "source_qint8.npz"
            _write_sentence_cache(
                source,
                texts=["ALPHA", "BRAVO", "DELTA", "FOXTROT"],
                trial_indices=[1, 2, 3, 4],
                events_path="/data/21_3660/231204/S21-session1_block1_list1.mat",
            )
            save_signal_representation_cache(
                packed,
                source_cache=load_sentence_npz_cache(source),
                encoding="qint8",
            )

            report = run_split_protocol(
                cache_paths=[source, packed],
                out_dir=root / "split",
                ratios={"train": 0.5, "test": 0.5},
            )

            self.assertEqual(report["membership"]["duplicate_semantic_row_uid_count"], 4)
            self.assertFalse(report["membership"]["strict_training_ready"])
            self.assertEqual(
                report["decision"]["status"],
                "membership_valid_duplicate_semantic_rows_not_ready",
            )
            self.assertEqual(
                {source["signal_member_names"][0] for source in report["sources"]},
                {"signals", "signal_payload"},
            )

    def test_variance_channel_selection_is_a_fit_scope_finding(self):
        from neurodecodekit.evaluation.split_protocol import run_split_protocol

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "variance.npz"
            _write_sentence_cache(
                source,
                texts=["ALPHA", "BRAVO", "DELTA", "FOXTROT"],
                trial_indices=[1, 2, 3, 4],
                events_path="/data/21_3660/231204/S21-session1_block1_list1.mat",
                variance_subset=True,
            )

            report = run_split_protocol(
                cache_paths=[source],
                out_dir=root / "split",
                ratios={"train": 0.5, "test": 0.5},
            )
            transforms = {
                finding["transform"] for finding in report["fit_scope"]["findings"]
            }
            self.assertEqual(transforms, {"variance_channel_subset"})
            self.assertFalse(report["fit_scope"]["strict_train_only_ready"])

    def test_train_fit_hashes_bind_preprocessing_and_training_partitions(self):
        from neurodecodekit.evaluation.split_protocol import (
            load_sentence_text_columns,
            load_training_partitions,
            run_split_protocol,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "strict.npz"
            _write_sentence_cache(
                source,
                texts=["ALPHA", "BRAVO", "DELTA", "FOXTROT"],
                trial_indices=[1, 2, 3, 4],
                events_path="/data/21_3660/231204/S21-session1_block1_list1.mat",
                robust_scaler=True,
                strict_membership=True,
            )
            report = run_split_protocol(
                cache_paths=[source],
                out_dir=root / "split",
                text_normalization="official-exact",
                ratios={"train": 0.5, "test": 0.5},
            )
            partitions = load_training_partitions(
                root / "split" / "split.json",
                source,
            )
            text_columns = load_sentence_text_columns(source)

            self.assertTrue(report["fit_scope"]["strict_train_only_ready"])
            self.assertTrue(report["membership"]["strict_training_ready"])
            self.assertEqual(
                report["decision"]["status"],
                "ready_for_training_protocol_integration",
            )
            self.assertEqual(len(partitions.train_indices), 2)
            self.assertEqual(len(partitions.eval_indices), 2)
            self.assertFalse(partitions.signal_array_members_loaded)
            self.assertFalse(text_columns["signal_array_members_loaded"])
            self.assertEqual(text_columns["target_texts"], ["ALPHA", "BRAVO", "DELTA", "FOXTROT"])

            mismatched = run_split_protocol(
                cache_paths=[source],
                out_dir=root / "mismatch",
                text_normalization="canonical-v1",
                ratios={"train": 0.5, "test": 0.5},
            )
            self.assertFalse(mismatched["fit_scope"]["strict_train_only_ready"])
            self.assertEqual(mismatched["fit_scope"]["findings"][0]["status"], "fail")

    def test_sentence_prior_uses_strict_membership_without_signal_arrays(self):
        from neurodecodekit.cli import main
        from neurodecodekit.evaluation.split_protocol import run_split_protocol

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "strict.npz"
            report_path = root / "prior.json"
            _write_sentence_cache(
                source,
                texts=["ALPHA", "BRAVO", "DELTA", "FOXTROT"],
                trial_indices=[1, 2, 3, 4],
                events_path="/data/21_3660/231204/S21-session1_block1_list1.mat",
                robust_scaler=True,
                strict_membership=True,
            )
            run_split_protocol(
                cache_paths=[source],
                out_dir=root / "split",
                text_normalization="official-exact",
                ratios={"train": 0.5, "test": 0.5},
            )
            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "sentence-prior-baseline",
                        "--cache",
                        str(source),
                        "--split-report",
                        str(root / "split" / "split.json"),
                        "--out-json",
                        str(report_path),
                    ]
                )
            prior_report = json.loads(report_path.read_text(encoding="utf-8"))

            self.assertEqual(code, 0)
            self.assertEqual(prior_report["summary"]["n_examples"], 2)
            self.assertEqual(prior_report["baseline"]["kind"], "prior-only")
            self.assertFalse(prior_report["baseline"]["uses_neural_windows"])
            self.assertFalse(
                prior_report["text_reader"]["signal_array_members_loaded"]
            )


def _write_sentence_cache(
    path: Path,
    *,
    texts: list[str],
    trial_indices: list[int],
    events_path: str,
    robust_scaler: bool = False,
    variance_subset: bool = False,
    strict_membership: bool = False,
) -> None:
    import numpy as np

    from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
    from neurodecodekit.preprocess.ctc_text import encode_ctc_text

    encoded = [encode_ctc_text(text) for text in texts]
    max_target_length = max(len(values) for values in encoded)
    target_ids = np.zeros((len(texts), max_target_length), dtype="int16")
    for index, values in enumerate(encoded):
        target_ids[index, : len(values)] = values
    transformations = []
    split_membership = None
    if robust_scaler:
        scaler_params = {"enabled": True}
        if strict_membership:
            split_membership = build_sentence_text_membership(
                texts,
                trial_indices=trial_indices,
                ratios={"train": 0.5, "test": 0.5},
            )
            scaler_params.update(
                {
                    "fit_split": "train",
                    "split_protocol_config_sha256": split_membership[
                        "protocol_config_sha256"
                    ],
                    "semantic_membership_sha256": split_membership[
                        "semantic_membership_sha256"
                    ],
                }
            )
        transformations.append(
            {"name": "per_channel_robust_scaler", "params": scaler_params}
        )
    if variance_subset:
        transformations.append(
            {"name": "channel_subset", "params": {"strategy": "variance"}}
        )
    save_sentence_npz_cache(
        path,
        signals=np.zeros((len(texts), 2, 8), dtype="float32"),
        input_lengths=np.full(len(texts), 8, dtype="int32"),
        target_token_ids=target_ids,
        target_lengths=np.asarray([len(values) for values in encoded], dtype="int32"),
        target_texts=np.asarray(texts, dtype="U"),
        reference_texts=np.asarray(texts, dtype="U"),
        mat_response_texts=np.asarray(texts, dtype="U"),
        trial_indices=np.asarray(trial_indices, dtype="int32"),
        sentence_start_sec=np.arange(len(texts), dtype="float64"),
        sentence_end_sec=np.arange(len(texts), dtype="float64") + 0.5,
        channel_names=np.asarray(["M1", "M2"], dtype="U"),
        metadata={
            "kind": "test_real_sentence_cache",
            "source_files": {"events": events_path},
            "transformations": transformations,
            "split_membership": split_membership,
            "warnings": ["test_only"],
        },
    )


if __name__ == "__main__":
    unittest.main()
