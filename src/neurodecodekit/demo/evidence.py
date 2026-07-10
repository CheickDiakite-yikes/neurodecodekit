"""Artifact-backed evidence model for the local NeuroDecodeKit demo."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from neurodecodekit.cache.sentence_npz import LoadedSentenceCache, load_sentence_npz_cache
from neurodecodekit.evaluation.report import (
    TextExampleScore,
    build_text_report,
    read_text_rows,
    score_text_example,
)


DEMO_SCHEMA_NAME = "neurodecodekit-demo-evidence"
DEMO_SCHEMA_VERSION = 1
PROOF_POSTURE = "synthetic_example_only_real_results_aggregate_only"


@dataclass(frozen=True)
class DemoExample:
    """One held-out synthetic sentence linked to its cache row and prediction."""

    display_index: int
    source_row_index: int
    trial_index: int
    target: str
    prediction: str
    input_length: int
    duration_sec: float

    @property
    def label(self) -> str:
        return f"Example {self.display_index + 1:02d} | row {self.source_row_index} | {self.target}"


@dataclass(frozen=True)
class DemoEvidence:
    """Validated compact artifacts and derived read-only demo views."""

    project_root: Path
    sentence_cache: LoadedSentenceCache
    examples: tuple[DemoExample, ...]
    synthetic_report: dict[str, Any]
    strict_real_report: dict[str, Any]
    cross_session_report: dict[str, Any]
    calibration_report: dict[str, Any]
    artifact_paths: dict[str, Path]
    artifact_sha256: dict[str, str]

    @property
    def channel_names(self) -> list[str]:
        return [str(value) for value in self.sentence_cache.channel_names.tolist()]

    @property
    def sampling_rate_hz(self) -> float:
        return float(self.sentence_cache.metadata.get("sampling_rate_hz") or 50.0)

    def example(self, display_index: int) -> DemoExample:
        index = int(display_index)
        if index < 0 or index >= len(self.examples):
            raise IndexError(f"demo example index {index} is outside 0..{len(self.examples) - 1}")
        return self.examples[index]

    def score(self, display_index: int, prediction: str | None = None) -> TextExampleScore:
        example = self.example(display_index)
        value = example.prediction if prediction is None else str(prediction)
        return score_text_example(display_index, example.target, value)

    def signal_rows(
        self,
        display_index: int,
        channel_names: list[str] | tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        """Return valid signal samples only for selected channels."""

        np = _require_numpy()
        example = self.example(display_index)
        available = self.channel_names
        selected = available if not channel_names else [str(value) for value in channel_names]
        unknown = sorted(set(selected) - set(available))
        if unknown:
            raise ValueError(f"unknown demo channels: {unknown}")
        channel_indices = [available.index(name) for name in selected]
        length = example.input_length
        signals = np.asarray(
            self.sentence_cache.signals[example.source_row_index, channel_indices, :length],
            dtype="float32",
        )
        return {
            "time_sec": np.arange(length, dtype="float32") / self.sampling_rate_hz,
            "signals": signals,
            "channel_names": selected,
            "source_row_index": example.source_row_index,
            "input_length": length,
            "duration_sec": example.duration_sec,
        }

    def aggregate_rows(self) -> list[list[Any]]:
        """Return aggregate-only evidence rows; real sentence text is never exposed."""

        synthetic_summary = self.synthetic_report["summary"]
        synthetic_prior = self.synthetic_report["comparators"]["prior_only"]["summary"]
        strict_summary = self.strict_real_report["summary"]
        strict_prior = self.strict_real_report["comparators"]["prior_only"]["summary"]
        strict_comparison = self.strict_real_report["comparisons"]["tiny_ctc_vs_prior_only"]
        cross_summary = self.cross_session_report["summary"]
        cross_prior = self.cross_session_report["comparators"]["prior_only"]["summary"]
        cross_comparison = self.cross_session_report["comparisons"]["tiny_ctc_vs_prior_only"]
        calibration = {
            row["shift_family"]: row for row in self.calibration_report["holdout"]["aggregate"]
        }
        rows = [
            [
                "Synthetic CTC smoke",
                "synthetic",
                synthetic_summary["n_examples"],
                _format_value(synthetic_summary["corpus_cer"]),
                _format_value(synthetic_prior["corpus_cer"]),
                _format_value(
                    synthetic_summary["corpus_cer"] - synthetic_prior["corpus_cer"],
                    signed=True,
                ),
                "not estimated",
                "plumbing only",
            ],
            [
                "S21 strict sentence-text test",
                "real MEG",
                strict_summary["n_examples"],
                _format_value(strict_summary["corpus_cer"]),
                _format_value(strict_prior["corpus_cer"]),
                _format_value(
                    strict_comparison["corpus_cer_delta_a_minus_b"],
                    signed=True,
                ),
                _format_interval(strict_comparison["paired_bootstrap_delta_ci95"]),
                "near-null; one character",
            ],
            [
                "S21 same-person session transfer",
                "real MEG",
                cross_summary["n_examples"],
                _format_value(cross_summary["corpus_cer"]),
                _format_value(cross_prior["corpus_cer"]),
                _format_value(
                    cross_comparison["corpus_cer_delta_a_minus_b"],
                    signed=True,
                ),
                _format_interval(cross_comparison["paired_bootstrap_delta_ci95"]),
                "fixed model worse than prior",
            ],
        ]
        for family, label in (
            ("stationary_diagonal", "Synthetic stationary calibration"),
            ("stationary_channel_mixing", "Synthetic channel-mixing stress"),
            ("within_row_time_varying", "Synthetic temporal-drift stress"),
        ):
            row = calibration[family]
            rows.append(
                [
                    label,
                    "synthetic",
                    row["seed_count"] * 16,
                    _format_value(row["median_adapted_cer"]),
                    _format_value(row["median_identity_cer"]),
                    _format_value(-row["median_cer_gain"], signed=True),
                    "3 shift seeds",
                    (
                        "narrow benefit"
                        if row["median_cer_gain"] > 0
                        else "adaptation harmful"
                    ),
                ]
            )
        return rows

    def calibration_rows(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.calibration_report["validation_aggregate"]]

    def proof_summary(self) -> dict[str, Any]:
        return {
            "schema": {"name": DEMO_SCHEMA_NAME, "version": DEMO_SCHEMA_VERSION},
            "proof_posture": PROOF_POSTURE,
            "example_domain": "synthetic token-motif sentence cache",
            "real_results_displayed": "aggregate metrics only",
            "predictive_confidence": "unavailable; no calibrated posterior in report",
            "decoder_causal": False,
            "decoder_real_time": False,
            "task": "typed-sentence production surrogate, not arbitrary thought",
            "real_session_adapter_authorized": False,
            "real_holdout_model_runs_triggered": 0,
            "network_data_fetches": 0,
            "source_cache_bytes": self.sentence_cache.summary.bytes,
            "source_cache_shape": list(self.sentence_cache.summary.signals_shape),
            "display_examples": len(self.examples),
        }

    def provenance_rows(self) -> list[list[str]]:
        return [
            [name, str(path), self.artifact_sha256[str(path)]]
            for name, path in self.artifact_paths.items()
        ]


def load_demo_evidence(
    project_root: str | Path,
    *,
    artifact_paths: Mapping[str, str | Path] | None = None,
) -> DemoEvidence:
    """Load and cross-check every compact artifact used by the demo."""

    root = Path(project_root).expanduser().resolve()
    paths = (
        _artifact_paths(root)
        if artifact_paths is None
        else {name: Path(path).expanduser().resolve() for name, path in artifact_paths.items()}
    )
    required_names = set(_artifact_paths(root))
    if set(paths) != required_names:
        raise ValueError(
            "Demo artifact path names must match exactly: "
            f"expected {sorted(required_names)}, got {sorted(paths)}"
        )
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Demo evidence artifacts are missing: " + ", ".join(missing))

    sentence_cache = load_sentence_npz_cache(paths["synthetic_sentence_cache"])
    synthetic_report = _read_json(paths["synthetic_ctc_report"])
    strict_real_report = _read_json(paths["strict_real_report"])
    cross_session_report = _read_json(paths["cross_session_report"])
    calibration_report = _read_json(paths["calibration_report"])
    predictions = read_text_rows(paths["synthetic_ctc_predictions"])
    eval_indices = [int(value) for value in synthetic_report["baseline"]["eval_indices"]]
    if len(predictions) != len(eval_indices):
        raise ValueError(
            "Synthetic demo predictions do not match report eval indices: "
            f"{len(predictions)} vs {len(eval_indices)}"
        )
    if synthetic_report["baseline"].get("causal") is not False:
        raise ValueError("Demo requires the synthetic report to declare causal=false")
    if calibration_report["decision"].get("real_session_adapter_authorized") is not False:
        raise ValueError("Demo refuses calibration reports that authorize a real adapter")

    examples = []
    for display_index, (source_row_index, prediction) in enumerate(
        zip(eval_indices, predictions)
    ):
        target = str(sentence_cache.target_texts[source_row_index])
        if display_index < len(synthetic_report["examples"]):
            report_example = synthetic_report["examples"][display_index]
            if target != str(report_example["target"]) or prediction != str(
                report_example["prediction"]
            ):
                raise ValueError(
                    "Synthetic cache, prediction rows, and report examples disagree at "
                    f"display index {display_index}"
                )
        input_length = int(sentence_cache.input_lengths[source_row_index])
        examples.append(
            DemoExample(
                display_index=display_index,
                source_row_index=source_row_index,
                trial_index=int(sentence_cache.trial_indices[source_row_index]),
                target=target,
                prediction=prediction,
                input_length=input_length,
                duration_sec=input_length
                / float(sentence_cache.metadata.get("sampling_rate_hz") or 50.0),
            )
        )

    rebuilt_summary = build_text_report(
        targets=[example.target for example in examples],
        predictions=[example.prediction for example in examples],
        max_examples=1,
    )["summary"]
    if rebuilt_summary != synthetic_report["summary"]:
        raise ValueError("Synthetic cache/prediction metrics do not reproduce the saved report")

    artifact_hashes = {str(path): _sha256(path) for path in paths.values()}
    return DemoEvidence(
        project_root=root,
        sentence_cache=sentence_cache,
        examples=tuple(examples),
        synthetic_report=synthetic_report,
        strict_real_report=strict_real_report,
        cross_session_report=cross_session_report,
        calibration_report=calibration_report,
        artifact_paths=paths,
        artifact_sha256=artifact_hashes,
    )


def _artifact_paths(root: Path) -> dict[str, Path]:
    return {
        "synthetic_sentence_cache": root / "cache/loop9_synthetic_sentences.npz",
        "synthetic_ctc_report": root / "cache/loop9_synthetic_ctc_report.json",
        "synthetic_ctc_predictions": root / "cache/loop9_synthetic_ctc_predictions.txt",
        "strict_real_report": root / "cache/loop14_s21_split_aware/tiny_ctc/report.json",
        "cross_session_report": root / "cache/loop15_s21_cross_session/tiny_ctc/report.json",
        "calibration_report": root / "cache/loop16_synthetic_calibration_curve/report.json",
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _format_interval(values: list[float]) -> str:
    return f"[{float(values[0]):+.4f}, {float(values[1]):+.4f}]"


def _format_value(value: float, *, signed: bool = False) -> str:
    return f"{float(value):{'+.4f' if signed else '.4f'}}"


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Demo evidence requires NumPy: `pip install numpy`.") from exc
    return np
