"""Dependency-free validation and summaries for the scientific knowledge ledger."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_NAME = "neurodecodekit.scientific_knowledge_ledger"
SCHEMA_VERSION = "0.1.0"

CLAIM_STATES = frozenset(
    {
        "UNKNOWN",
        "EXPLORATORY_SUPPORT",
        "SUPPORTED",
        "WEAKLY_SUPPORTED",
        "REFUTED",
        "CONFOUNDED",
        "INCONCLUSIVE",
        "UNDERPOWERED",
        "BLOCKED_BY_DATA",
        "BLOCKED_BY_MEASUREMENT",
        "BLOCKED_BY_METHOD",
        "BLOCKED_BY_ETHICS_OR_ACCESS",
    }
)
RELATION_TYPES = frozenset(
    {
        "supports",
        "contradicts",
        "depends_on",
        "confounded_by",
        "replicates",
        "fails_to_replicate",
        "narrows",
        "motivates",
        "supersedes",
    }
)
LANES = frozenset({"discovery", "confirmation", "translation", "engineering"})
COORDINATE_FIELDS = (
    "generalization",
    "attribution",
    "temporal_regime",
    "output_regime",
    "calibration_regime",
    "setting",
)
REQUIRED_TOP_LEVEL = frozenset(
    {
        "schema_name",
        "schema_version",
        "recorded_at",
        "constitution",
        "plan",
        "flagship",
        "claims",
        "evidence",
        "relationships",
        "experiments",
        "scoreboards",
        "portfolio",
        "operation_boundary",
    }
)


class KnowledgeLedgerError(ValueError):
    """Raised when a scientific ledger is malformed or internally inconsistent."""


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise KnowledgeLedgerError(f"{label} must be an object")
    return value


def _require_sequence(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise KnowledgeLedgerError(f"{label} must be an array")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeLedgerError(f"{label} must be nonempty text")
    return value


def _unique_ids(rows: Sequence[Any], label: str) -> set[str]:
    identities: list[str] = []
    for index, row in enumerate(rows):
        item = _require_mapping(row, f"{label}[{index}]")
        identities.append(_require_text(item.get("id"), f"{label}[{index}].id"))
    if len(set(identities)) != len(identities):
        raise KnowledgeLedgerError(f"{label} IDs must be unique")
    return set(identities)


def _validate_coordinates(value: Any, label: str) -> None:
    coordinates = _require_mapping(value, label)
    if set(coordinates) != set(COORDINATE_FIELDS):
        raise KnowledgeLedgerError(
            f"{label} must contain exactly {', '.join(COORDINATE_FIELDS)}"
        )
    for field in COORDINATE_FIELDS:
        _require_text(coordinates[field], f"{label}.{field}")


def _validate_relative_path(value: Any, label: str) -> str:
    text = _require_text(value, label)
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or text.startswith("~"):
        raise KnowledgeLedgerError(f"{label} must be a repository-relative safe path")
    return text


def validate_scientific_ledger(value: Any) -> dict[str, Any]:
    """Validate identities, claim coordinates, references, and active boundaries."""

    ledger = dict(_require_mapping(value, "ledger"))
    missing = REQUIRED_TOP_LEVEL - set(ledger)
    if missing:
        raise KnowledgeLedgerError(f"ledger is missing fields: {sorted(missing)}")
    unexpected = set(ledger) - REQUIRED_TOP_LEVEL
    if unexpected:
        raise KnowledgeLedgerError(f"ledger has unsupported fields: {sorted(unexpected)}")
    if ledger.get("schema_name") != SCHEMA_NAME:
        raise KnowledgeLedgerError("ledger schema name differs")
    if ledger.get("schema_version") != SCHEMA_VERSION:
        raise KnowledgeLedgerError("ledger schema version differs")
    _require_text(ledger.get("recorded_at"), "recorded_at")
    _validate_relative_path(ledger.get("constitution"), "constitution")
    _validate_relative_path(ledger.get("plan"), "plan")

    claims = _require_sequence(ledger.get("claims"), "claims")
    evidence = _require_sequence(ledger.get("evidence"), "evidence")
    experiments = _require_sequence(ledger.get("experiments"), "experiments")
    claim_ids = _unique_ids(claims, "claims")
    evidence_ids = _unique_ids(evidence, "evidence")
    experiment_ids = _unique_ids(experiments, "experiments")
    if not claim_ids or not evidence_ids or not experiment_ids:
        raise KnowledgeLedgerError("ledger requires claims, evidence, and experiments")

    for index, row in enumerate(claims):
        claim = _require_mapping(row, f"claims[{index}]")
        state = _require_text(claim.get("state"), f"claims[{index}].state")
        if state not in CLAIM_STATES:
            raise KnowledgeLedgerError(f"claims[{index}].state is unsupported: {state}")
        lane = _require_text(claim.get("lane"), f"claims[{index}].lane")
        if lane not in LANES:
            raise KnowledgeLedgerError(f"claims[{index}].lane is unsupported: {lane}")
        for field in (
            "question",
            "strongest_statement",
            "next_discriminator",
            "unsupported",
        ):
            _require_text(claim.get(field), f"claims[{index}].{field}")
        _validate_coordinates(claim.get("coordinates"), f"claims[{index}].coordinates")
        references = _require_sequence(claim.get("evidence_ids"), f"claims[{index}].evidence_ids")
        if any(reference not in evidence_ids for reference in references):
            raise KnowledgeLedgerError(f"claims[{index}] has a dangling evidence reference")
        blockers = _require_sequence(claim.get("blockers"), f"claims[{index}].blockers")
        if any(not isinstance(item, str) or not item for item in blockers):
            raise KnowledgeLedgerError(f"claims[{index}].blockers must contain text")

    for index, row in enumerate(evidence):
        item = _require_mapping(row, f"evidence[{index}]")
        lane = _require_text(item.get("lane"), f"evidence[{index}].lane")
        if lane not in LANES:
            raise KnowledgeLedgerError(f"evidence[{index}].lane is unsupported: {lane}")
        for field in ("kind", "summary", "limitations"):
            _require_text(item.get(field), f"evidence[{index}].{field}")
        for field in ("supports", "contradicts"):
            references = _require_sequence(item.get(field), f"evidence[{index}].{field}")
            if any(reference not in claim_ids for reference in references):
                raise KnowledgeLedgerError(f"evidence[{index}].{field} has a dangling claim")
        paths = _require_sequence(item.get("paths"), f"evidence[{index}].paths")
        if not paths:
            raise KnowledgeLedgerError(f"evidence[{index}] requires at least one path")
        for path_index, path in enumerate(paths):
            safe_path = _validate_relative_path(
                path,
                f"evidence[{index}].paths[{path_index}]",
            )
            if PurePosixPath(safe_path).parts[0] not in {"docs", "registries"}:
                raise KnowledgeLedgerError(
                    f"evidence[{index}].paths[{path_index}] must be public evidence"
                )

    relationships = _require_sequence(ledger.get("relationships"), "relationships")
    graph_ids = claim_ids | evidence_ids | experiment_ids
    for index, row in enumerate(relationships):
        relation = _require_mapping(row, f"relationships[{index}]")
        subject = _require_text(relation.get("subject"), f"relationships[{index}].subject")
        object_id = _require_text(relation.get("object"), f"relationships[{index}].object")
        kind = _require_text(relation.get("relation"), f"relationships[{index}].relation")
        if subject not in graph_ids or object_id not in graph_ids:
            raise KnowledgeLedgerError(f"relationships[{index}] has a dangling node")
        if kind not in RELATION_TYPES:
            raise KnowledgeLedgerError(f"relationships[{index}].relation is unsupported")
        _require_text(relation.get("rationale"), f"relationships[{index}].rationale")

    for index, row in enumerate(experiments):
        experiment = _require_mapping(row, f"experiments[{index}]")
        lane = _require_text(experiment.get("lane"), f"experiments[{index}].lane")
        if lane not in LANES:
            raise KnowledgeLedgerError(f"experiments[{index}].lane is unsupported: {lane}")
        for field in (
            "status",
            "scientific_question",
            "evidence_target",
            "earliest_checkpoint",
            "stop_rule",
            "deserves_resources_because",
            "authority",
            "expected_information_gain",
        ):
            _require_text(experiment.get(field), f"experiments[{index}].{field}")
        claim_references = _require_sequence(
            experiment.get("claim_ids"),
            f"experiments[{index}].claim_ids",
        )
        if not claim_references or any(item not in claim_ids for item in claim_references):
            raise KnowledgeLedgerError(f"experiments[{index}] has a dangling claim")
        evidence_references = _require_sequence(
            experiment.get("evidence_ids"),
            f"experiments[{index}].evidence_ids",
        )
        if any(item not in evidence_ids for item in evidence_references):
            raise KnowledgeLedgerError(f"experiments[{index}] has dangling evidence")

    flagship = _require_mapping(ledger.get("flagship"), "flagship")
    flagship_experiment = _require_text(flagship.get("experiment_id"), "flagship.experiment_id")
    if flagship_experiment not in experiment_ids:
        raise KnowledgeLedgerError("flagship experiment does not exist")
    flagship_claim = _require_text(flagship.get("claim_id"), "flagship.claim_id")
    if flagship_claim not in claim_ids:
        raise KnowledgeLedgerError("flagship claim does not exist")
    _require_text(flagship.get("first_empirical_checkpoint"), "flagship.first_empirical_checkpoint")

    portfolio = _require_mapping(ledger.get("portfolio"), "portfolio")
    if set(portfolio) != {"flagship", "adjacent_diagnostic", "moonshot"}:
        raise KnowledgeLedgerError("portfolio must contain flagship, adjacent_diagnostic, moonshot")
    for name, experiment_id in portfolio.items():
        if experiment_id not in experiment_ids:
            raise KnowledgeLedgerError(f"portfolio.{name} does not name an experiment")

    scoreboards = _require_mapping(ledger.get("scoreboards"), "scoreboards")
    if set(scoreboards) != {"scientific_attribution", "functional_utility"}:
        raise KnowledgeLedgerError("scoreboards must separate attribution and utility")
    for name, rows in scoreboards.items():
        values = _require_sequence(rows, f"scoreboards.{name}")
        if not values:
            raise KnowledgeLedgerError(f"scoreboards.{name} must not be empty")
        for index, row in enumerate(values):
            item = _require_mapping(row, f"scoreboards.{name}[{index}]")
            _require_text(item.get("measure"), f"scoreboards.{name}[{index}].measure")
            _require_text(item.get("status"), f"scoreboards.{name}[{index}].status")
            _require_text(item.get("value"), f"scoreboards.{name}[{index}].value")

    boundary = _require_mapping(ledger.get("operation_boundary"), "operation_boundary")
    if boundary.get("active_tier_c_packet") is not None:
        raise KnowledgeLedgerError("operation boundary must record no active Tier C packet")
    if boundary.get("all_authority_flags_false") is not True:
        raise KnowledgeLedgerError("operation boundary must remain all-false")
    for field in (
        "real_dreyer_payload_reads",
        "real_dreyer_header_reads",
        "real_dreyer_network_body_bytes",
        "new_data_downloads",
        "real_model_runs",
        "target_deliveries",
        "scientific_scores",
    ):
        if boundary.get(field) != 0:
            raise KnowledgeLedgerError(f"operation_boundary.{field} must remain zero")
    for field in (
        "real_dreyer_endpoint_requests",
        "real_dreyer_response_opens",
    ):
        if boundary.get(field) != 1:
            raise KnowledgeLedgerError(f"operation_boundary.{field} must equal one")
    return ledger


def load_scientific_ledger(
    path: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load a ledger and optionally verify that every public evidence path exists."""

    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KnowledgeLedgerError("ledger JSON is invalid") from exc
    ledger = validate_scientific_ledger(value)
    if repository_root is not None:
        root = Path(repository_root).resolve()
        paths = [ledger["constitution"], ledger["plan"]]
        for item in ledger["evidence"]:
            paths.extend(item["paths"])
        for relative in paths:
            candidate = (root / relative).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                raise KnowledgeLedgerError(f"ledger evidence path is unavailable: {relative}")
    return ledger


def summarize_scientific_ledger(value: Any) -> dict[str, Any]:
    """Return a compact belief and next-experiment summary."""

    ledger = validate_scientific_ledger(value)
    state_counts = Counter(claim["state"] for claim in ledger["claims"])
    flagship_id = ledger["flagship"]["experiment_id"]
    flagship = next(row for row in ledger["experiments"] if row["id"] == flagship_id)
    unresolved = sorted(
        claim["id"]
        for claim in ledger["claims"]
        if claim["state"]
        not in {"SUPPORTED", "REFUTED"}
    )
    return {
        "schema_name": ledger["schema_name"],
        "schema_version": ledger["schema_version"],
        "claim_count": len(ledger["claims"]),
        "evidence_count": len(ledger["evidence"]),
        "experiment_count": len(ledger["experiments"]),
        "claim_state_counts": dict(sorted(state_counts.items())),
        "unresolved_claim_ids": unresolved,
        "flagship_experiment_id": flagship_id,
        "flagship_status": flagship["status"],
        "first_empirical_checkpoint": ledger["flagship"]["first_empirical_checkpoint"],
        "active_tier_c_packet": ledger["operation_boundary"]["active_tier_c_packet"],
        "all_authority_flags_false": True,
    }


def build_research_update(value: Any) -> dict[str, str]:
    """Generate the constitution's six-field end-of-cycle update."""

    ledger = validate_scientific_ledger(value)
    experiment_id = ledger["flagship"]["experiment_id"]
    experiment = next(row for row in ledger["experiments"] if row["id"] == experiment_id)
    claim_id = ledger["flagship"]["claim_id"]
    claim = next(row for row in ledger["claims"] if row["id"] == claim_id)
    evidence_by_id = {item["id"]: item for item in ledger["evidence"]}
    latest_evidence = evidence_by_id[experiment["evidence_ids"][-1]]
    return {
        "scientific_question": experiment["scientific_question"],
        "evidence_produced": latest_evidence["summary"],
        "belief_changed": claim["strongest_statement"],
        "uncertainty_remaining": claim["next_discriminator"],
        "next_decisive_experiment": experiment["earliest_checkpoint"],
        "infrastructure_created_and_why": (
            "The source lock preserves immutable identity, nuisance measurements, storage "
            "limits, and the claim ceiling before any payload is opened."
        ),
    }
