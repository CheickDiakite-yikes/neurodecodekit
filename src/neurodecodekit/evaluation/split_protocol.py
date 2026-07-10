"""Deterministic, inspectable split membership and leakage audits."""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from neurodecodekit.cache.sentence_npz import SENTENCE_CACHE_SCHEMA_NAME
from neurodecodekit.cache.signal_representation import REPRESENTATION_CACHE_SCHEMA_NAME
from neurodecodekit.datasets.manifest import build_manifest_from_paths


SPLIT_PROTOCOL_SCHEMA_NAME = "b2q-split-protocol"
SPLIT_PROTOCOL_SCHEMA_VERSION = 1
DEFAULT_RATIOS = {"train": 0.8, "val": 0.1, "test": 0.1}
SPLIT_TYPES = ("event", "sentence-text", "session", "subject")
TEXT_SOURCES = ("reference", "target", "mat-response")
TEXT_NORMALIZATIONS = ("canonical-v1", "official-exact")
ALGORITHM_NAME = "brain2qwerty-v2-neuralset-deterministic-splitter"
ALGORITHM_VERSION = "neuralset-0.2.2-compatible"
OFFICIAL_V2_COMMIT = "3bf5a4099ca0d23bbe994b2287905760236e56e0"
OFFICIAL_V2_PAPER = (
    "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
)
OFFICIAL_V2_SPLITTER_SOURCE = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_V2_COMMIT}/brain2qwerty_v2/transforms.py"
)
OFFICIAL_V2_CONFIG_SOURCE = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_V2_COMMIT}/brain2qwerty_v2/config/xp_config.py"
)

# The public SpanishBCBL card documents repeated MEG subject IDs for one person.
SPANISHBCBL_PERSON_ALIASES = {
    "S1": "spanishbcbl-person-s1-s18",
    "S18": "spanishbcbl-person-s1-s18",
    "S4": "spanishbcbl-person-s4-s14",
    "S14": "spanishbcbl-person-s4-s14",
    "S5": "spanishbcbl-person-s5-s10-s21",
    "S10": "spanishbcbl-person-s5-s10-s21",
    "S21": "spanishbcbl-person-s5-s10-s21",
}


@dataclass(frozen=True)
class SplitSourceRow:
    """One sentence row with stable physical and semantic identities."""

    source_cache_path: str
    source_cache_sha256: str
    source_row_index: int
    trial_index: int
    row_uid_sha256: str
    semantic_row_uid_sha256: str
    target_text: str
    reference_text: str
    mat_response_text: str
    subject: str | None
    canonical_subject: str | None
    session: str | None
    block: str | None


@dataclass(frozen=True)
class SplitSource:
    """Signal-free source-cache summary used by the split audit."""

    path: str
    sha256: str
    bytes: int
    schema_name: str
    schema_version: int | None
    kind: str
    n_rows: int
    subject: str | None
    canonical_subject: str | None
    session: str | None
    block: str | None
    source_files: dict[str, str]
    signal_member_names: list[str]
    signal_members_loaded: bool
    metadata: dict[str, Any]

    def report_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("metadata")
        return payload


@dataclass(frozen=True)
class TrainingPartitions:
    """Validated train/validation/test indices bound to one physical cache."""

    report_path: str
    cache_path: str
    source_cache_sha256: str
    train_indices: list[int]
    validation_indices: list[int]
    test_indices: list[int]
    eval_partition: str
    eval_indices: list[int]
    protocol: dict[str, Any]
    protocol_config_sha256: str
    group_assignment_sha256: str
    semantic_membership_sha256: str
    signal_array_members_loaded: bool

    def metadata(self) -> dict[str, Any]:
        return asdict(self)


def canonicalize_sentence_text(value: str) -> str:
    """Normalize case, Unicode compatibility, and whitespace for leakage grouping."""

    normalized = unicodedata.normalize("NFKC", str(value)).casefold()
    return " ".join(normalized.split())


def official_v2_split_score(value: str, *, seed: float = 0.0) -> float:
    """Return the NeuralSet 0.2.2-compatible deterministic score in [0, 1)."""

    numeric_seed = float(seed)
    if not math.isfinite(numeric_seed):
        raise ValueError("split seed must be finite")
    hashed = int(hashlib.sha256(str(value).encode("utf-8")).hexdigest(), 16)
    # NeuralSet 0.2.2 declares seed as float and evaluates hashed + seed.
    return random.Random(hashed + numeric_seed).random()


def assign_deterministic_groups(
    values: Iterable[str],
    *,
    ratios: Mapping[str, float] | None = None,
    seed: float = 0.0,
) -> dict[str, dict[str, Any]]:
    """Assign every unique group value with the official-v2-compatible algorithm."""

    normalized_ratios = normalize_split_ratios(ratios)
    unique_values = sorted({str(value) for value in values})
    if not unique_values:
        raise ValueError("at least one split group is required")
    assignments: dict[str, dict[str, Any]] = {}
    for value in unique_values:
        score = official_v2_split_score(value, seed=seed)
        cumulative = 0.0
        selected = None
        for name, ratio in normalized_ratios.items():
            cumulative += ratio
            if score < cumulative:
                selected = name
                break
        if selected is None:  # protects against floating-point summation at 1.0
            selected = next(reversed(normalized_ratios))
        assignments[value] = {"split": selected, "score": score}
    return assignments


def normalize_split_ratios(
    ratios: Mapping[str, float] | None = None,
) -> dict[str, float]:
    """Validate ordered, positive split ratios that sum to one."""

    values = dict(DEFAULT_RATIOS if ratios is None else ratios)
    if len(values) < 2:
        raise ValueError("at least two split ratios are required")
    if any(not str(name).strip() for name in values):
        raise ValueError("split names must be non-empty")
    normalized = {str(name): float(value) for name, value in values.items()}
    if any(not math.isfinite(value) or value <= 0 for value in normalized.values()):
        raise ValueError("split ratios must be finite and positive")
    if not math.isclose(sum(normalized.values()), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("split ratios must sum to 1")
    return normalized


def split_protocol_config(
    *,
    split_type: str = "sentence-text",
    text_source: str = "reference",
    text_normalization: str = "official-exact",
    ratios: Mapping[str, float] | None = None,
    seed: float = 0.0,
) -> dict[str, Any]:
    """Return the complete, hashable deterministic split configuration."""

    if split_type not in SPLIT_TYPES:
        raise ValueError(f"split_type must be one of: {', '.join(SPLIT_TYPES)}")
    if text_source not in TEXT_SOURCES:
        raise ValueError(f"text_source must be one of: {', '.join(TEXT_SOURCES)}")
    if text_normalization not in TEXT_NORMALIZATIONS:
        raise ValueError(
            "text_normalization must be one of: " + ", ".join(TEXT_NORMALIZATIONS)
        )
    return {
        "algorithm_name": ALGORITHM_NAME,
        "algorithm_version": ALGORITHM_VERSION,
        "official_v2_commit": OFFICIAL_V2_COMMIT,
        "split_type": split_type,
        "text_source": text_source,
        "text_normalization": text_normalization,
        "ratios": normalize_split_ratios(ratios),
        "seed": float(seed),
    }


def build_sentence_text_membership(
    texts: Iterable[str],
    *,
    trial_indices: Iterable[int] | None = None,
    text_source: str = "reference",
    text_normalization: str = "official-exact",
    ratios: Mapping[str, float] | None = None,
    seed: float = 0.0,
) -> dict[str, Any]:
    """Build plaintext-free sentence membership before signal preprocessing."""

    text_rows = [str(value) for value in texts]
    if not text_rows:
        raise ValueError("at least one sentence text is required")
    if trial_indices is None:
        trials = list(range(len(text_rows)))
    else:
        trials = [int(value) for value in trial_indices]
    if len(trials) != len(text_rows):
        raise ValueError("trial_indices and texts must have the same row count")
    if len(set(trials)) != len(trials):
        raise ValueError("trial_indices must be unique")

    protocol = split_protocol_config(
        split_type="sentence-text",
        text_source=text_source,
        text_normalization=text_normalization,
        ratios=ratios,
        seed=seed,
    )
    group_values = [
        canonicalize_sentence_text(value)
        if text_normalization == "canonical-v1"
        else value
        for value in text_rows
    ]
    assignments = assign_deterministic_groups(
        group_values,
        ratios=protocol["ratios"],
        seed=seed,
    )
    group_counts = Counter(group_values)
    groups = sorted(
        (
            {
                "group_sha256": _sha256_text(value),
                "split": assignment["split"],
                "score": assignment["score"],
                "row_count": group_counts[value],
            }
            for value, assignment in assignments.items()
        ),
        key=lambda row: row["group_sha256"],
    )
    rows = [
        {
            "source_row_index": row_index,
            "trial_index": trial_index,
            "group_sha256": _sha256_text(group_value),
            "split": assignments[group_value]["split"],
        }
        for row_index, (trial_index, group_value) in enumerate(
            zip(trials, group_values, strict=True)
        )
    ]
    partition_rows = Counter(row["split"] for row in rows)
    partition_groups = Counter(row["split"] for row in groups)
    return {
        "protocol": protocol,
        "protocol_config_sha256": _sha256_json(protocol),
        "group_assignment_sha256": _sha256_json(groups),
        "semantic_membership_sha256": _sha256_json(rows),
        "partition_row_counts": {
            name: partition_rows[name] for name in protocol["ratios"]
        },
        "partition_group_counts": {
            name: partition_groups[name] for name in protocol["ratios"]
        },
        "unique_group_count": len(groups),
        "groups": groups,
        "rows": rows,
        "contains_plaintext": False,
    }


def run_split_protocol(
    *,
    cache_paths: Iterable[str | Path],
    out_dir: str | Path,
    split_type: str = "sentence-text",
    text_source: str = "reference",
    text_normalization: str = "canonical-v1",
    ratios: Mapping[str, float] | None = None,
    seed: float = 0.0,
    report_json_path: str | Path | None = None,
    report_markdown_path: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Audit deterministic membership without loading any signal array member."""

    started_at = time.perf_counter()
    if split_type not in SPLIT_TYPES:
        raise ValueError(f"split_type must be one of: {', '.join(SPLIT_TYPES)}")
    if text_source not in TEXT_SOURCES:
        raise ValueError(f"text_source must be one of: {', '.join(TEXT_SOURCES)}")
    if text_normalization not in TEXT_NORMALIZATIONS:
        raise ValueError(
            "text_normalization must be one of: " + ", ".join(TEXT_NORMALIZATIONS)
        )
    normalized_ratios = normalize_split_ratios(ratios)
    sources, rows, fit_findings, loader_warnings = load_split_sources(cache_paths)

    output_dir = Path(out_dir)
    report_json = Path(report_json_path) if report_json_path else output_dir / "split.json"
    report_markdown = (
        Path(report_markdown_path) if report_markdown_path else output_dir / "split.md"
    )
    _prepare_report_paths([report_json, report_markdown], overwrite=overwrite)

    capabilities = _build_capabilities(
        rows,
        ratios=normalized_ratios,
        text_source=text_source,
        text_normalization=text_normalization,
    )
    group_values = [
        _group_value(
            row,
            split_type=split_type,
            text_source=text_source,
            text_normalization=text_normalization,
        )
        for row in rows
    ]
    missing_group_rows = [index for index, value in enumerate(group_values) if value is None]
    assignments = (
        assign_deterministic_groups(
            (value for value in group_values if value is not None),
            ratios=normalized_ratios,
            seed=seed,
        )
        if len(missing_group_rows) < len(rows)
        else {}
    )

    membership_rows = []
    group_row_counts: Counter[str] = Counter()
    for row, group_value in zip(rows, group_values):
        group_hash = _sha256_text(group_value) if group_value is not None else None
        assignment = assignments.get(group_value) if group_value is not None else None
        split_name = assignment["split"] if assignment else None
        if group_value is not None:
            group_row_counts[group_value] += 1
        membership_rows.append(
            {
                "source_cache_sha256": row.source_cache_sha256,
                "source_row_index": row.source_row_index,
                "trial_index": row.trial_index,
                "row_uid_sha256": row.row_uid_sha256,
                "semantic_row_uid_sha256": row.semantic_row_uid_sha256,
                "group_sha256": group_hash,
                "split": split_name,
                "subject": row.subject,
                "canonical_subject": row.canonical_subject,
                "session": row.session,
                "block": row.block,
            }
        )

    partition_rows = Counter(
        row["split"] for row in membership_rows if row["split"] is not None
    )
    partition_groups: Counter[str] = Counter(
        assignment["split"] for assignment in assignments.values()
    )
    empty_partitions = [name for name in normalized_ratios if partition_rows[name] == 0]
    group_cross_split = _cross_split_count(
        (row["group_sha256"], row["split"]) for row in membership_rows
    )
    canonical_text_cross_split = _canonical_text_cross_split_count(rows, membership_rows)
    semantic_row_counts = Counter(row.semantic_row_uid_sha256 for row in rows)
    duplicate_semantic_uids = sorted(
        uid for uid, count in semantic_row_counts.items() if count > 1
    )

    group_assignment_rows = sorted(
        (
            {
                "group_sha256": _sha256_text(value),
                "split": assignment["split"],
                "score": assignment["score"],
                "row_count": group_row_counts[value],
            }
            for value, assignment in assignments.items()
        ),
        key=lambda row: row["group_sha256"],
    )
    sorted_membership = sorted(
        membership_rows,
        key=lambda row: (
            row["semantic_row_uid_sha256"],
            row["source_cache_sha256"],
            row["source_row_index"],
        ),
    )
    protocol_config = split_protocol_config(
        split_type=split_type,
        text_source=text_source,
        text_normalization=text_normalization,
        ratios=normalized_ratios,
        seed=seed,
    )
    protocol_config_sha256 = _sha256_json(protocol_config)
    group_assignment_sha256 = _sha256_json(group_assignment_rows)
    semantic_membership_sha256 = None
    if len(sources) == 1:
        semantic_membership_rows = sorted(
            (
                {
                    "source_row_index": row["source_row_index"],
                    "trial_index": row["trial_index"],
                    "group_sha256": row["group_sha256"],
                    "split": row["split"],
                }
                for row in membership_rows
            ),
            key=lambda row: row["source_row_index"],
        )
        semantic_membership_sha256 = _sha256_json(semantic_membership_rows)
    fit_findings = _finalize_fit_findings(
        fit_findings,
        protocol_config_sha256=protocol_config_sha256,
        semantic_membership_sha256=semantic_membership_sha256,
    )
    fit_scope_ready = all(finding["status"] == "pass" for finding in fit_findings)
    requested_usable = (
        not missing_group_rows
        and not empty_partitions
        and group_cross_split == 0
        and bool(assignments)
    )
    strict_training_ready = (
        requested_usable and fit_scope_ready and not duplicate_semantic_uids
    )
    decision = _split_decision(
        requested_usable=requested_usable,
        fit_scope_ready=fit_scope_ready,
        has_duplicate_semantic_rows=bool(duplicate_semantic_uids),
        missing_group_rows=len(missing_group_rows),
        empty_partitions=empty_partitions,
    )

    warnings = list(loader_warnings)
    if split_type == "event":
        warnings.append("event_split_is_not_a_sentence_text_generalization_claim")
    if canonical_text_cross_split:
        warnings.append("canonical_sentence_text_crosses_requested_partitions")
    if not fit_scope_ready:
        warnings.append("strict_train_only_fit_scope_not_ready")
    if duplicate_semantic_uids:
        warnings.append("duplicate_semantic_rows_across_input_caches")
    if len({row.canonical_subject for row in rows if row.canonical_subject}) < 2:
        warnings.append("subject_generalization_unavailable_single_person_group")
    if len(
        {
            (row.canonical_subject, row.session)
            for row in rows
            if row.canonical_subject and row.session
        }
    ) < 2:
        warnings.append("session_generalization_unavailable_single_session_group")
    warnings.extend(
        [
            "split_membership_audit_only_no_decoder_training_or_accuracy",
            "real_cache_records_physical_typing_not_arbitrary_thoughts",
            "whole_sentence_noncausal_v2_is_not_low_latency_streaming",
        ]
    )

    report: dict[str, Any] = {
        "schema": {
            "name": SPLIT_PROTOCOL_SCHEMA_NAME,
            "version": SPLIT_PROTOCOL_SCHEMA_VERSION,
        },
        "proof_posture": "split_membership_audit_no_decoder_training",
        "run": {
            "runtime_sec": round(time.perf_counter() - started_at, 6),
            "source_cache_count": len(sources),
            "row_count": len(rows),
            "signal_array_members_loaded": False,
            "numpy_version": _dependency_version("numpy"),
            "python_version": sys.version.split()[0],
            "peak_rss_bytes": _peak_rss_bytes(),
        },
        "protocol": protocol_config,
        "primary_sources": {
            "official_v2_paper": OFFICIAL_V2_PAPER,
            "official_v2_splitter": OFFICIAL_V2_SPLITTER_SOURCE,
            "official_v2_config": OFFICIAL_V2_CONFIG_SOURCE,
            "compatibility_note": (
                "Assignment matches NeuralSet 0.2.2 SHA-256 plus float-seeded "
                "Python Random behavior. canonical-v1 grouping is intentionally "
                "stricter than the official exact-string precondition."
            ),
        },
        "sources": [source.report_dict() for source in sources],
        "capabilities": capabilities,
        "membership": {
            "requested_split_usable": requested_usable,
            "strict_training_ready": strict_training_ready,
            "missing_group_row_count": len(missing_group_rows),
            "empty_partitions": empty_partitions,
            "partition_row_counts": {
                name: partition_rows[name] for name in normalized_ratios
            },
            "partition_group_counts": {
                name: partition_groups[name] for name in normalized_ratios
            },
            "group_cross_split_count": group_cross_split,
            "canonical_sentence_text_cross_split_count": canonical_text_cross_split,
            "duplicate_semantic_row_uid_count": len(duplicate_semantic_uids),
            "duplicate_semantic_row_uids": duplicate_semantic_uids,
            "protocol_config_sha256": protocol_config_sha256,
            "group_assignment_sha256": group_assignment_sha256,
            "semantic_membership_sha256": semantic_membership_sha256,
            "membership_sha256": _sha256_json(sorted_membership),
            "groups": group_assignment_rows,
            "rows": sorted_membership,
        },
        "fit_scope": {
            "strict_train_only_ready": fit_scope_ready,
            "finding_count": len(fit_findings),
            "unresolved_or_failed_count": sum(
                finding["status"] != "pass" for finding in fit_findings
            ),
            "findings": fit_findings,
            "official_v2_boundary": (
                "The official v2 paper reports per-recording RobustScaler statistics. "
                "This audit additionally tracks a stricter train-only fit posture."
            ),
        },
        "decision": decision,
        "warnings": sorted(set(warnings)),
        "artifact_paths": {
            "report_json": str(report_json),
            "report_markdown": str(report_markdown),
        },
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    report["resources"] = {
        "report_json_bytes": 0,
        "report_markdown_bytes": 0,
        "total_report_bytes": 0,
        "new_signal_cache_bytes": 0,
    }
    for _ in range(10):
        write_split_protocol_json(report, report_json)
        write_split_protocol_markdown(report, report_markdown)
        measured_resources = {
            "report_json_bytes": report_json.stat().st_size,
            "report_markdown_bytes": report_markdown.stat().st_size,
            "total_report_bytes": (
                report_json.stat().st_size + report_markdown.stat().st_size
            ),
            "new_signal_cache_bytes": 0,
        }
        if measured_resources == report["resources"]:
            break
        report["resources"] = measured_resources
    else:  # pragma: no cover - deterministic JSON sizes converge in two writes
        raise RuntimeError("Split report byte accounting did not converge.")
    return report


def load_split_sources(
    cache_paths: Iterable[str | Path],
) -> tuple[list[SplitSource], list[SplitSourceRow], list[dict[str, Any]], list[str]]:
    """Read only text/trial metadata from standard or packed sentence NPZ caches."""

    np = _require_numpy()
    paths = _normalize_cache_paths(cache_paths)
    sources: list[SplitSource] = []
    rows: list[SplitSourceRow] = []
    fit_findings: list[dict[str, Any]] = []
    warnings: list[str] = []
    for path in paths:
        cache_sha256 = _file_sha256(path)
        with np.load(path, allow_pickle=False) as data:
            required = {
                "target_texts",
                "reference_texts",
                "mat_response_texts",
                "trial_indices",
                "metadata",
            }
            missing = sorted(required - set(data.files))
            if missing:
                raise ValueError(f"Cache is missing split arrays {missing}: {path}")
            metadata = json.loads(str(data["metadata"].item()))
            schema_name = str((metadata.get("schema") or {}).get("name") or "")
            if schema_name not in {
                SENTENCE_CACHE_SCHEMA_NAME,
                REPRESENTATION_CACHE_SCHEMA_NAME,
            }:
                raise ValueError(f"Unsupported sentence cache schema {schema_name!r}: {path}")
            target_texts = [str(value) for value in data["target_texts"].tolist()]
            reference_texts = [str(value) for value in data["reference_texts"].tolist()]
            mat_response_texts = [
                str(value) for value in data["mat_response_texts"].tolist()
            ]
            trial_indices = [int(value) for value in data["trial_indices"].tolist()]
            signal_members = [
                name for name in ("signals", "signal_payload") if name in data.files
            ]
        lengths = {
            len(target_texts),
            len(reference_texts),
            len(mat_response_texts),
            len(trial_indices),
        }
        if len(lengths) != 1:
            raise ValueError(f"Split arrays have inconsistent row counts: {path}")

        semantic_metadata = _semantic_metadata(metadata)
        source_files = {
            str(name): str(value)
            for name, value in (semantic_metadata.get("source_files") or {}).items()
            if value not in (None, "")
        }
        identifiers, identifier_warnings = _source_identifiers(source_files)
        warnings.extend(f"{path.name}:{warning}" for warning in identifier_warnings)
        source = SplitSource(
            path=str(path),
            sha256=cache_sha256,
            bytes=path.stat().st_size,
            schema_name=schema_name,
            schema_version=_optional_int((metadata.get("schema") or {}).get("version")),
            kind=str(semantic_metadata.get("kind") or metadata.get("kind") or "unknown"),
            n_rows=len(target_texts),
            subject=identifiers["subject"],
            canonical_subject=_canonical_subject(identifiers["subject"]),
            session=identifiers["session"],
            block=identifiers["block"],
            source_files=source_files,
            signal_member_names=signal_members,
            signal_members_loaded=False,
            metadata=semantic_metadata,
        )
        sources.append(source)
        fit_findings.extend(_audit_fit_scope(source))
        source_identity = _sha256_json(source_files or {"cache_sha256": cache_sha256})
        for index, (target, reference, response, trial_index) in enumerate(
            zip(target_texts, reference_texts, mat_response_texts, trial_indices)
        ):
            semantic_uid = _sha256_json(
                {"source_identity": source_identity, "trial_index": trial_index}
            )
            row_uid = _sha256_json(
                {
                    "cache_sha256": cache_sha256,
                    "source_row_index": index,
                    "trial_index": trial_index,
                }
            )
            rows.append(
                SplitSourceRow(
                    source_cache_path=str(path),
                    source_cache_sha256=cache_sha256,
                    source_row_index=index,
                    trial_index=trial_index,
                    row_uid_sha256=row_uid,
                    semantic_row_uid_sha256=semantic_uid,
                    target_text=target,
                    reference_text=reference,
                    mat_response_text=response,
                    subject=source.subject,
                    canonical_subject=source.canonical_subject,
                    session=source.session,
                    block=source.block,
                )
            )
    return sources, rows, fit_findings, warnings


def load_training_partitions(
    report_path: str | Path,
    cache_path: str | Path,
    *,
    eval_partition: str = "test",
    require_strict: bool = True,
) -> TrainingPartitions:
    """Validate a split report and return indices for one exact cache artifact."""

    split_path = Path(report_path)
    cache_file = Path(cache_path)
    report = json.loads(split_path.read_text(encoding="utf-8"))
    schema = report.get("schema") or {}
    if schema.get("name") != SPLIT_PROTOCOL_SCHEMA_NAME:
        raise ValueError(f"Not a Split Protocol v1 report: {split_path}")
    protocol = report.get("protocol") or {}
    if protocol.get("split_type") != "sentence-text":
        raise ValueError("Training requires a sentence-text split report.")
    ratios = protocol.get("ratios") or {}
    if "train" not in ratios:
        raise ValueError("Split report does not contain a train partition.")
    if eval_partition == "train" or eval_partition not in ratios:
        raise ValueError(
            f"eval_partition must be a non-train partition in the report: {sorted(ratios)}"
        )
    membership = report.get("membership") or {}
    if require_strict and not membership.get("strict_training_ready"):
        raise ValueError(
            "Split report is not strict-training ready: "
            f"{(report.get('decision') or {}).get('status', 'unknown')}"
        )
    sources = report.get("sources") or []
    if len(sources) != 1:
        raise ValueError("Training partition loading currently requires exactly one cache.")
    source = sources[0]
    expected_sha256 = str(source.get("sha256") or "")
    actual_sha256 = _file_sha256(cache_file)
    if not expected_sha256 or actual_sha256 != expected_sha256:
        raise ValueError("Split report source SHA-256 does not match the requested cache.")

    n_rows = int(source.get("n_rows", -1))
    rows = membership.get("rows") or []
    by_index: dict[int, str] = {}
    for row in rows:
        if row.get("source_cache_sha256") != actual_sha256:
            raise ValueError("Split membership contains a different source cache hash.")
        row_index = int(row["source_row_index"])
        if row_index in by_index:
            raise ValueError(f"Split membership repeats source row {row_index}.")
        split_name = str(row.get("split") or "")
        if split_name not in ratios:
            raise ValueError(f"Split membership has an unknown partition: {split_name!r}")
        by_index[row_index] = split_name
    if set(by_index) != set(range(n_rows)):
        raise ValueError("Split membership does not cover every source cache row exactly once.")

    partition_indices = {
        name: sorted(index for index, value in by_index.items() if value == name)
        for name in ratios
    }
    if not partition_indices["train"] or not partition_indices[eval_partition]:
        raise ValueError("Requested train/evaluation partitions must both be non-empty.")
    semantic_membership_sha256 = membership.get("semantic_membership_sha256")
    if not semantic_membership_sha256:
        raise ValueError("Split report lacks a semantic membership hash.")
    return TrainingPartitions(
        report_path=str(split_path),
        cache_path=str(cache_file),
        source_cache_sha256=actual_sha256,
        train_indices=partition_indices["train"],
        validation_indices=partition_indices.get("val", []),
        test_indices=partition_indices.get("test", []),
        eval_partition=eval_partition,
        eval_indices=partition_indices[eval_partition],
        protocol=dict(protocol),
        protocol_config_sha256=str(membership["protocol_config_sha256"]),
        group_assignment_sha256=str(membership["group_assignment_sha256"]),
        semantic_membership_sha256=str(semantic_membership_sha256),
        signal_array_members_loaded=False,
    )


def load_sentence_text_columns(cache_path: str | Path) -> dict[str, Any]:
    """Read sentence text/trial columns without loading a signal array member."""

    np = _require_numpy()
    path = Path(cache_path)
    with np.load(path, allow_pickle=False) as data:
        required = {
            "target_texts",
            "reference_texts",
            "mat_response_texts",
            "trial_indices",
        }
        missing = sorted(required - set(data.files))
        if missing:
            raise ValueError(f"Cache is missing sentence text arrays {missing}: {path}")
        payload = {
            "target_texts": [str(value) for value in data["target_texts"].tolist()],
            "reference_texts": [
                str(value) for value in data["reference_texts"].tolist()
            ],
            "mat_response_texts": [
                str(value) for value in data["mat_response_texts"].tolist()
            ],
            "trial_indices": [int(value) for value in data["trial_indices"].tolist()],
            "signal_member_names": [
                name for name in ("signals", "signal_payload") if name in data.files
            ],
        }
    lengths = {len(payload[name]) for name in required}
    if len(lengths) != 1:
        raise ValueError(f"Sentence text arrays have inconsistent row counts: {path}")
    payload.update(
        {
            "path": str(path),
            "source_cache_sha256": _file_sha256(path),
            "signal_array_members_loaded": False,
        }
    )
    return payload


def write_split_protocol_json(report: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_split_protocol_markdown(report: dict[str, Any], path: str | Path) -> None:
    protocol = report["protocol"]
    membership = report["membership"]
    fit_scope = report["fit_scope"]
    decision = report["decision"]
    lines = [
        "# Split Protocol v1 Audit",
        "",
        f"**Proof posture:** `{report['proof_posture']}`",
        "",
        "This is a membership and preprocessing-fit audit. It does not train a "
        "decoder or produce a neural accuracy result.",
        "",
        "## Requested Protocol",
        "",
        f"- Split type: `{protocol['split_type']}`",
        f"- Text source: `{protocol['text_source']}`",
        f"- Text normalization: `{protocol['text_normalization']}`",
        f"- Algorithm: `{protocol['algorithm_name']}`",
        f"- Algorithm version: `{protocol['algorithm_version']}`",
        f"- Ratios: `{protocol['ratios']}`",
        f"- Seed: `{protocol['seed']}`",
        f"- Protocol config SHA-256: `{membership['protocol_config_sha256']}`",
        f"- Group assignment SHA-256: `{membership['group_assignment_sha256']}`",
        "- Semantic membership SHA-256: "
        f"`{membership['semantic_membership_sha256']}`",
        f"- Membership SHA-256: `{membership['membership_sha256']}`",
        "",
        "## Sources",
        "",
        "| Cache | Schema | Rows | Subject group | Session | Block | Signals loaded |",
        "|---|---|---:|---|---|---|---|",
    ]
    for source in report["sources"]:
        lines.append(
            f"| `{source['path']}` | `{source['schema_name']}` | {source['n_rows']} | "
            f"`{source['canonical_subject']}` | `{source['session']}` | "
            f"`{source['block']}` | `{source['signal_members_loaded']}` |"
        )
    lines.extend(
        [
            "",
            "## Partition Membership",
            "",
            "| Split | Rows | Groups |",
            "|---|---:|---:|",
        ]
    )
    for name in protocol["ratios"]:
        lines.append(
            f"| `{name}` | {membership['partition_row_counts'][name]} | "
            f"{membership['partition_group_counts'][name]} |"
        )
    lines.extend(
        [
            "",
            f"- Requested split usable: `{membership['requested_split_usable']}`",
            f"- Strict training ready: `{membership['strict_training_ready']}`",
            f"- Group cross-split count: `{membership['group_cross_split_count']}`",
            "- Canonical sentence-text cross-split count: "
            f"`{membership['canonical_sentence_text_cross_split_count']}`",
            "- Duplicate semantic row IDs across input caches: "
            f"`{membership['duplicate_semantic_row_uid_count']}`",
            "",
            "## Split Capabilities",
            "",
            "| Split type | Unique groups | Missing rows | Structural status |",
            "|---|---:|---:|---|",
        ]
    )
    for name, capability in report["capabilities"].items():
        lines.append(
            f"| `{name}` | {capability['unique_group_count']} | "
            f"{capability['missing_group_row_count']} | `{capability['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Fit-Scope Audit",
            "",
            f"- Strict train-only ready: `{fit_scope['strict_train_only_ready']}`",
            f"- Unresolved/failed findings: `{fit_scope['unresolved_or_failed_count']}`",
            "",
            "| Cache | Transform | Status | Declared fit split | Required action |",
            "|---|---|---|---|---|",
        ]
    )
    if fit_scope["findings"]:
        for finding in fit_scope["findings"]:
            lines.append(
                f"| `{finding['source_cache']}` | `{finding['transform']}` | "
                f"`{finding['status']}` | `{finding['declared_fit_split']}` | "
                f"{finding['required_action']} |"
            )
    else:
        lines.append("| - | no known data-dependent transform | `pass` | - | - |")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Status: `{decision['status']}`",
            f"- Next action: `{decision['next_action']}`",
            f"- Reason: {decision['reason']}",
            "",
            "## Primary Sources",
            "",
            f"- Official v2 paper: {report['primary_sources']['official_v2_paper']}",
            f"- Official splitter: {report['primary_sources']['official_v2_splitter']}",
            f"- Official config: {report['primary_sources']['official_v2_config']}",
            "",
            "## Warnings",
            "",
        ]
    )
    lines.extend(f"- `{warning}`" for warning in report["warnings"])
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _group_value(
    row: SplitSourceRow,
    *,
    split_type: str,
    text_source: str,
    text_normalization: str,
) -> str | None:
    if split_type == "event":
        return row.semantic_row_uid_sha256
    if split_type == "sentence-text":
        value = {
            "reference": row.reference_text,
            "target": row.target_text,
            "mat-response": row.mat_response_text,
        }[text_source]
        return (
            canonicalize_sentence_text(value)
            if text_normalization == "canonical-v1"
            else str(value)
        )
    if split_type == "session":
        if not row.canonical_subject or not row.session:
            return None
        return f"{row.canonical_subject}|session:{row.session}"
    if split_type == "subject":
        return row.canonical_subject
    raise ValueError(f"Unsupported split type: {split_type}")


def _build_capabilities(
    rows: list[SplitSourceRow],
    *,
    ratios: Mapping[str, float],
    text_source: str,
    text_normalization: str,
) -> dict[str, Any]:
    required_groups = len(ratios)
    capabilities = {}
    for split_type in SPLIT_TYPES:
        values = [
            _group_value(
                row,
                split_type=split_type,
                text_source=text_source,
                text_normalization=text_normalization,
            )
            for row in rows
        ]
        missing = sum(value is None for value in values)
        unique = len({value for value in values if value is not None})
        if missing:
            status = "unavailable_missing_group_metadata"
        elif unique < required_groups:
            status = "unavailable_insufficient_groups_for_requested_partitions"
        else:
            status = "structurally_available"
        capabilities[split_type] = {
            "status": status,
            "unique_group_count": unique,
            "missing_group_row_count": missing,
            "minimum_group_count_for_requested_partitions": required_groups,
            "claim_boundary": _capability_claim_boundary(split_type),
        }
    return capabilities


def _audit_fit_scope(source: SplitSource) -> list[dict[str, Any]]:
    findings = []
    seen = set()
    for transform in source.metadata.get("transformations") or []:
        if not isinstance(transform, dict):
            continue
        name = str(transform.get("name") or "")
        params = transform.get("params") if isinstance(transform.get("params"), dict) else {}
        if name == "per_channel_robust_scaler" and params.get("enabled", True):
            findings.append(_fit_finding(source, name, params))
            seen.add(name)
        if name == "channel_subset" and params.get("strategy") == "variance":
            findings.append(_fit_finding(source, "variance_channel_subset", params))
            seen.add("variance_channel_subset")
    subset = source.metadata.get("channel_subset") or {}
    if (
        isinstance(subset, dict)
        and subset.get("strategy") == "variance"
        and "variance_channel_subset" not in seen
    ):
        findings.append(_fit_finding(source, "variance_channel_subset", subset))
    return findings


def _fit_finding(
    source: SplitSource, transform: str, params: Mapping[str, Any]
) -> dict[str, Any]:
    declared = params.get("fit_split", params.get("fit_partition"))
    if transform == "per_channel_robust_scaler":
        action = "Refit scaler statistics on train rows or declare/justify transductive scope."
    else:
        action = "Fit variance ranking on train rows only, then freeze selected channels."
    return {
        "source_cache": source.path,
        "source_cache_sha256": source.sha256,
        "transform": transform,
        "status": "pending_protocol_validation",
        "declared_fit_split": declared,
        "declared_protocol_config_sha256": params.get(
            "split_protocol_config_sha256"
        ),
        "declared_semantic_membership_sha256": params.get(
            "semantic_membership_sha256"
        ),
        "required_action": action,
    }


def _finalize_fit_findings(
    findings: list[dict[str, Any]],
    *,
    protocol_config_sha256: str,
    semantic_membership_sha256: str | None,
) -> list[dict[str, Any]]:
    finalized = []
    for finding in findings:
        row = dict(finding)
        if row["declared_fit_split"] != "train":
            row["status"] = "unresolved"
        elif not row["declared_protocol_config_sha256"]:
            row["status"] = "unresolved"
            row["required_action"] = (
                "Bind train-fit provenance to the exact split protocol config hash."
            )
        elif not row["declared_semantic_membership_sha256"]:
            row["status"] = "unresolved"
            row["required_action"] = (
                "Bind train-fit provenance to the exact semantic membership hash."
            )
        elif semantic_membership_sha256 is None:
            row["status"] = "unresolved"
            row["required_action"] = (
                "Audit train-fit provenance one source cache at a time."
            )
        elif row["declared_protocol_config_sha256"] != protocol_config_sha256:
            row["status"] = "fail"
            row["required_action"] = (
                "Regenerate preprocessing with the requested split protocol config."
            )
        elif row["declared_semantic_membership_sha256"] != semantic_membership_sha256:
            row["status"] = "fail"
            row["required_action"] = (
                "Regenerate preprocessing with the requested row membership."
            )
        else:
            row["status"] = "pass"
            row["required_action"] = (
                "None; train-fit provenance matches the audited membership."
            )
        finalized.append(row)
    return finalized


def _split_decision(
    *,
    requested_usable: bool,
    fit_scope_ready: bool,
    has_duplicate_semantic_rows: bool,
    missing_group_rows: int,
    empty_partitions: list[str],
) -> dict[str, str]:
    if not requested_usable:
        return {
            "status": "requested_split_unavailable",
            "next_action": "fix_group_metadata_or_choose_a_supported_protocol",
            "reason": (
                f"The requested split has {missing_group_rows} missing group rows and "
                f"empty partitions {empty_partitions}. It cannot support evaluation."
            ),
        }
    if has_duplicate_semantic_rows:
        return {
            "status": "membership_valid_duplicate_semantic_rows_not_ready",
            "next_action": "deduplicate_underlying_trials_before_training",
            "reason": (
                "Group membership is valid, but multiple input caches contain the same "
                "underlying semantic trial rows."
            ),
        }
    if not fit_scope_ready:
        return {
            "status": "membership_valid_strict_fit_scope_not_ready",
            "next_action": "make_data_dependent_preprocessing_train_only_or_explicitly_transductive",
            "reason": (
                "Requested group membership is leakage-safe, but at least one data-dependent "
                "preprocessing step does not declare a train-only fit scope."
            ),
        }
    return {
        "status": "ready_for_training_protocol_integration",
        "next_action": "wire_exact_membership_into_training_and_reports",
        "reason": (
            "Requested groups are contained within partitions, all partitions are non-empty, "
            "semantic rows are unique, and known data-dependent transforms declare train-only fit."
        ),
    }


def _canonical_text_cross_split_count(
    rows: list[SplitSourceRow], membership_rows: list[dict[str, Any]]
) -> int:
    groups: dict[str, set[str]] = defaultdict(set)
    for row, membership in zip(rows, membership_rows):
        split_name = membership["split"]
        if split_name is not None:
            groups[canonicalize_sentence_text(row.reference_text)].add(split_name)
    return sum(len(splits) > 1 for splits in groups.values())


def _cross_split_count(values: Iterable[tuple[str | None, str | None]]) -> int:
    grouped: dict[str, set[str]] = defaultdict(set)
    for group, split_name in values:
        if group is not None and split_name is not None:
            grouped[group].add(split_name)
    return sum(len(splits) > 1 for splits in grouped.values())


def _source_identifiers(source_files: Mapping[str, str]) -> tuple[dict[str, str | None], list[str]]:
    records = build_manifest_from_paths(source_files.values()) if source_files else []
    warnings = []
    result = {}
    for field in ("subject", "session", "block"):
        values = sorted({getattr(record, field) for record in records if getattr(record, field)})
        if len(values) > 1:
            warnings.append(f"conflicting_source_{field}:{values}")
        result[field] = values[0] if len(values) == 1 else None
    return result, warnings


def _semantic_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    semantic = metadata.get("semantic_metadata")
    return semantic if isinstance(semantic, dict) else metadata


def _canonical_subject(subject: str | None) -> str | None:
    if subject is None:
        return None
    normalized = str(subject).upper()
    return SPANISHBCBL_PERSON_ALIASES.get(normalized, normalized)


def _capability_claim_boundary(split_type: str) -> str:
    return {
        "event": "plumbing_only_does_not_prevent_sentence_text_leakage",
        "sentence-text": "unseen_text_within_available_subject_session_groups",
        "session": "unseen_session_not_unseen_subject",
        "subject": "unseen_canonical_person_group",
    }[split_type]


def _normalize_cache_paths(values: Iterable[str | Path]) -> list[Path]:
    paths = [Path(value) for value in values]
    if not paths:
        raise ValueError("at least one sentence cache is required")
    if len({str(path.resolve()) for path in paths}) != len(paths):
        raise ValueError("cache paths must be unique")
    for path in paths:
        if path.suffix.lower() != ".npz" or not path.is_file():
            raise ValueError(f"Expected an existing NPZ cache: {path}")
    return paths


def _prepare_report_paths(paths: list[Path], *, overwrite: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Planned split reports already exist: "
            + ", ".join(str(path) for path in existing)
        )
    if overwrite:
        for path in existing:
            if path.is_dir():
                raise IsADirectoryError(f"Planned report path is a directory: {path}")
            path.unlink()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_text(value: str | None) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _optional_int(value: Any) -> int | None:
    return int(value) if value is not None else None


def _dependency_version(name: str) -> str | None:
    try:
        from importlib.metadata import version

        return version(name)
    except Exception:  # noqa: BLE001 - optional dependency metadata
        return None


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (ImportError, OSError, ValueError):  # pragma: no cover - platform-dependent
        return None
    return value if sys.platform == "darwin" else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Split protocol requires NumPy: `pip install numpy`.") from exc
    return np
