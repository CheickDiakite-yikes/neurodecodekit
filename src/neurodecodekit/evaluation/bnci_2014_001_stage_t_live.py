"""One-shot Stage T target delivery and aggregate scoring for BNCI-C3C5-1."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import bnci_2014_001_stage_q as q_core
from neurodecodekit.datasets import bnci_2014_001_stage_q_live as q_live
from neurodecodekit.evaluation import bnci_2014_001_score as scorer
from neurodecodekit.experiments import bnci_2014_001_cross_participant_eeg_gain as model_core
from neurodecodekit.experiments import bnci_2014_001_stage_p_live as stage_p

LANE_ID = "BNCI-C3C5-1-T"
SCHEMA_VERSION = "0.1.0"
ACTIVATION_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_stage_t_scoring_activation.v0.json"
)
RESULT_RELATIVE_PATH = Path("registries/bnci_2014_001_stage_t_result.v0.json")
MARKER_RELATIVE_PATH = Path(".codex_work/bnci_c3c5/stage_t_v0.consumed.json")


class BNCIStageTRefusal(RuntimeError):
    """Fail-closed Stage T refusal."""


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _validate_green_record(value: Any, *, label: str) -> dict[str, Any]:
    if (
        not isinstance(value, dict)
        or set(value)
        != {
            "commit",
            "CI_run_id",
            "CI_head_sha",
            "CI_conclusion",
            "base_python_job_id",
            "base_python_job_name",
            "base_python_job_conclusion",
            "optional_neuro_readers_job_id",
            "optional_neuro_readers_job_name",
            "optional_neuro_readers_job_conclusion",
            "both_required_jobs_green",
        }
        or not stage_p._is_commit(value.get("commit"))
        or value.get("CI_head_sha") != value.get("commit")
        or value.get("CI_conclusion") != "success"
        or value.get("base_python_job_name") != "Base Python"
        or value.get("base_python_job_conclusion") != "success"
        or value.get("optional_neuro_readers_job_name") != "Optional Neuro Readers"
        or value.get("optional_neuro_readers_job_conclusion") != "success"
        or value.get("both_required_jobs_green") is not True
        or not all(
            isinstance(value.get(field), int) and value[field] > 0
            for field in ("CI_run_id", "base_python_job_id", "optional_neuro_readers_job_id")
        )
    ):
        raise BNCIStageTRefusal(f"Stage T {label} green proof differs")
    return value


def validate_activation_document(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "lane_id",
        "status",
        "green_implementation",
        "green_prediction_freeze",
        "prediction_freeze_artifact",
        "implementation_artifacts",
        "authority",
    }:
        raise BNCIStageTRefusal("Stage T activation fields differ")
    if value.get("lane_id") != LANE_ID or value.get("status") != "remotely_green_one_score_enabled":
        raise BNCIStageTRefusal("Stage T activation status differs")
    _validate_green_record(value.get("green_implementation"), label="implementation")
    _validate_green_record(value.get("green_prediction_freeze"), label="prediction freeze")
    artifact = value.get("prediction_freeze_artifact")
    if (
        not isinstance(artifact, dict)
        or set(artifact) != {"path", "bytes", "sha256"}
        or artifact.get("path") != stage_p.PUBLIC_FREEZE_RELATIVE_PATH.as_posix()
        or not isinstance(artifact.get("bytes"), int)
        or artifact["bytes"] <= 0
        or not stage_p._is_sha256(artifact.get("sha256"))
    ):
        raise BNCIStageTRefusal("Stage T prediction-freeze identity differs")
    artifacts = value.get("implementation_artifacts")
    if not isinstance(artifacts, list) or [row.get("path") for row in artifacts if isinstance(row, dict)] != list(stage_p.IMPLEMENTATION_ARTIFACTS):
        raise BNCIStageTRefusal("Stage T implementation artifact inventory differs")
    if any(
        not isinstance(row, dict)
        or set(row) != {"path", "bytes", "sha256"}
        or not isinstance(row.get("bytes"), int)
        or row["bytes"] <= 0
        or not stage_p._is_sha256(row.get("sha256"))
        for row in artifacts
    ):
        raise BNCIStageTRefusal("Stage T implementation artifact identity differs")
    if value.get("authority") != {
        "one_target_delivery_of_nine_sealed_fold_sets": True,
        "one_aggregate_score": True,
        "post_target_updates": 0,
        "reruns": 0,
        "held_out_T_delivery": False,
        "individual_prediction_probability_target_or_participant_outcome_public": False,
        "maximum_route": "BNCIC3C5-R5",
    }:
        raise BNCIStageTRefusal("Stage T authority differs")
    return value


def read_green_activation(root: str | Path) -> dict[str, Any]:
    repo = Path(root).resolve()
    payload = (repo / ACTIVATION_RELATIVE_PATH).read_bytes()
    try:
        activation = validate_activation_document(json.loads(payload))
    except json.JSONDecodeError as exc:
        raise BNCIStageTRefusal("Stage T activation JSON is invalid") from exc
    implementation = activation["green_implementation"]
    freeze_green = activation["green_prediction_freeze"]
    for expected, row in zip(stage_p.IMPLEMENTATION_ARTIFACTS, activation["implementation_artifacts"], strict=True):
        if row != stage_p._artifact_identity(repo, expected):
            raise BNCIStageTRefusal("Stage T implementation artifact changed")
        if q_core._git_output(repo, "show", f"{implementation['commit']}:{expected}") != (repo / expected).read_bytes():
            raise BNCIStageTRefusal("Stage T implementation differs from its green commit")
    freeze_payload = (repo / stage_p.PUBLIC_FREEZE_RELATIVE_PATH).read_bytes()
    if activation["prediction_freeze_artifact"] != {
        "path": stage_p.PUBLIC_FREEZE_RELATIVE_PATH.as_posix(),
        "bytes": len(freeze_payload),
        "sha256": _sha256(freeze_payload),
    }:
        raise BNCIStageTRefusal("Stage T prediction-freeze artifact changed")
    if q_core._git_output(repo, "show", f"{freeze_green['commit']}:{stage_p.PUBLIC_FREEZE_RELATIVE_PATH.as_posix()}") != freeze_payload:
        raise BNCIStageTRefusal("Stage T freeze differs from its green commit")
    if q_core._git_output(repo, "show", f"HEAD:{ACTIVATION_RELATIVE_PATH.as_posix()}") != payload:
        raise BNCIStageTRefusal("Stage T activation differs from HEAD")
    q_core._git_output(repo, "merge-base", "--is-ancestor", implementation["commit"], "HEAD")
    q_core._git_output(repo, "merge-base", "--is-ancestor", freeze_green["commit"], "HEAD")
    branch = q_core._git_output(repo, "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
    head = q_core._git_output(repo, "rev-parse", "HEAD").strip()
    remote = q_core._git_output(repo, "rev-parse", f"refs/remotes/origin/{branch}").strip()
    if not branch or branch == "HEAD" or head != remote:
        raise BNCIStageTRefusal("Stage T activation is not the pushed branch HEAD")
    subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=repo, check=True, timeout=30)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--"], cwd=repo, check=True, timeout=30)
    return activation


def validate_public_freeze(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BNCIStageTRefusal("Stage T public freeze is not an object")
    if (
        value.get("schema_name") != "neurodecodekit.bnci_2014_001_stage_p_prediction_freeze"
        or value.get("lane_id") != stage_p.LANE_ID
        or value.get("status") != "frozen_target_blind_predictions_targets_and_scoring_keys_still_sealed"
        or value.get("folds") != 9
        or value.get("held_out_E_rows_per_fold") != 288
        or value.get("held_out_T_rows_used") != 0
        or value.get("private_prediction_rows") != stage_p.EXPECTED_TOTAL_PREDICTION_ROWS
        or value.get("operation_counters", {}).get("parameter_update_fits") != stage_p.EXPECTED_TOTAL_FITS
        or value.get("operation_counters", {}).get("prediction_sets") != stage_p.EXPECTED_TOTAL_PREDICTION_SETS
        or value.get("operation_counters", {}).get("target_deliveries") != 0
        or value.get("operation_counters", {}).get("scores") != 0
        or value.get("scientific_claim_established") is not False
    ):
        raise BNCIStageTRefusal("Stage T public freeze fields differ")
    for field in (
        "prediction_set_sha256",
        "configuration_hash",
        "code_hash",
        "split_protocol_hash",
        "source_capability_HMAC_commitment",
        "sealed_target_transport_commitment_sha256",
    ):
        if not stage_p._is_sha256(value.get(field)):
            raise BNCIStageTRefusal("Stage T public freeze hash differs")
    condition_hashes = value.get("condition_sha256")
    if not isinstance(condition_hashes, dict) or set(condition_hashes) != set(scorer.CONDITIONS) or any(
        not stage_p._is_sha256(digest) for digest in condition_hashes.values()
    ):
        raise BNCIStageTRefusal("Stage T condition hash inventory differs")
    return value


def _load_private_predictions(
    stage_p_output: Path,
    private_manifest: Mapping[str, Any],
    public_freeze: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], bytes]:
    folds = private_manifest.get("folds")
    if not isinstance(folds, list) or [row.get("fold") for row in folds if isinstance(row, dict)] != list(stage_p.PARTICIPANTS):
        raise BNCIStageTRefusal("Stage T private fold inventory differs")
    rows: list[dict[str, Any]] = []
    payloads: list[bytes] = []
    condition_digests = {condition: hashlib.sha256() for condition in scorer.CONDITIONS}
    for record in folds:
        path = stage_p._safe_child(stage_p_output, str(record.get("prediction_file")))
        payload = stage_p._read_direct(
            path,
            expected_bytes=int(record.get("prediction_bytes", -1)),
            expected_sha256=str(record.get("prediction_sha256")),
        )
        fold_rows = scorer._parse_jsonl(payload, kind="Stage T private predictions")
        stage_p.validate_fold_predictions(str(record["fold"]), fold_rows)
        rows.extend(fold_rows)
        payloads.append(payload)
        for row in fold_rows:
            condition_digests[str(row["condition"])].update(scorer._canonical_bytes(row))
    payload = b"".join(payloads)
    if (
        len(rows) != stage_p.EXPECTED_TOTAL_PREDICTION_ROWS
        or len(payload) != public_freeze.get("private_prediction_bytes")
        or _sha256(payload) != public_freeze.get("prediction_set_sha256")
        or {name: digest.hexdigest() for name, digest in condition_digests.items()}
        != public_freeze.get("condition_sha256")
    ):
        raise BNCIStageTRefusal("Stage T private prediction commitment differs")
    scorer._validate_prediction_rows(rows)
    return rows, payload


def _sealed_target_records(stage_q_manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = stage_q_manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise BNCIStageTRefusal("Stage T Stage Q artifact inventory is absent")
    records = {
        str(row.get("fold")): dict(row)
        for row in artifacts
        if isinstance(row, dict) and row.get("role") == "sealed_scoring_targets"
    }
    if set(records) != set(stage_p.PARTICIPANTS):
        raise BNCIStageTRefusal("Stage T sealed-target inventory differs")
    return records


def _scoring_key_record(stage_q_manifest: Mapping[str, Any]) -> dict[str, Any]:
    rows = [
        row
        for row in stage_q_manifest.get("artifacts", [])
        if isinstance(row, dict) and row.get("role") == "scoring_key_vault_sealed_until_T"
    ]
    if len(rows) != 1:
        raise BNCIStageTRefusal("Stage T scoring-key record differs")
    return dict(rows[0])


def _deliver_target_rows(
    *,
    repo: Path,
    stage_q_output: Path,
    stage_q_manifest: Mapping[str, Any],
    prediction_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    key_record = _scoring_key_record(stage_q_manifest)
    key_payload = stage_p._read_direct(
        repo / q_live.SCORING_KEY_VAULT_RELATIVE_PATH,
        expected_bytes=int(key_record.get("bytes", -1)),
        expected_sha256=str(key_record.get("sha256")),
    )
    try:
        key_vault = json.loads(key_payload)
    except json.JSONDecodeError as exc:
        raise BNCIStageTRefusal("Stage T scoring-key vault JSON is invalid") from exc
    if (
        not isinstance(key_vault, dict)
        or key_vault.get("schema_name") != "neurodecodekit.bnci_2014_001_stage_q_scoring_key_vault"
        or set(key_vault.get("keys", {})) != set(stage_p.PARTICIPANTS) | {"artifacts"}
    ):
        raise BNCIStageTRefusal("Stage T scoring-key vault differs")
    prediction_identity = {
        str(row["opaque_row_id"]): scorer._identity(row)
        for row in prediction_rows
    }
    if len(prediction_identity) != 9 * 288:
        raise BNCIStageTRefusal("Stage T prediction identity inventory differs")
    records = _sealed_target_records(stage_q_manifest)
    targets: list[dict[str, Any]] = []
    for participant in stage_p.PARTICIPANTS:
        record = records[participant]
        envelope = stage_p._read_direct(
            stage_p._safe_child(stage_q_output, str(record.get("file"))),
            expected_bytes=int(record.get("bytes", -1)),
            expected_sha256=str(record.get("sha256")),
        )
        try:
            key = bytes.fromhex(str(key_vault["keys"][participant]))
        except (TypeError, ValueError) as exc:
            raise BNCIStageTRefusal("Stage T scoring key is malformed") from exc
        plaintext = q_live.unseal_payload(envelope, key)
        arrays = stage_p._load_npz(plaintext)
        if set(arrays) != {"opaque_row_id", "target_index"} or arrays["opaque_row_id"].shape != (288,) or arrays["target_index"].shape != (288,):
            raise BNCIStageTRefusal("Stage T target payload shape differs")
        row_ids = [stage_p._decode_row_id(value) for value in arrays["opaque_row_id"]]
        target_indices = [int(value) for value in arrays["target_index"]]
        if len(set(row_ids)) != 288 or any(value not in range(4) for value in target_indices):
            raise BNCIStageTRefusal("Stage T target payload values differ")
        participant_prediction_ids = {
            row_id
            for row_id, identity in prediction_identity.items()
            if identity[0] == participant
        }
        if set(row_ids) != participant_prediction_ids:
            raise BNCIStageTRefusal("Stage T target and prediction identities differ")
        for row_id, target_index in zip(row_ids, target_indices, strict=True):
            identity = prediction_identity[row_id]
            targets.append(
                {
                    "participant": identity[0],
                    "session": identity[1],
                    "run_ordinal": identity[2],
                    "trial_ordinal": identity[3],
                    "opaque_row_id": identity[4],
                    "target": scorer.CLASSES[target_index],
                }
            )
    targets.sort(key=scorer._target_sort_key)
    scorer._validate_target_rows(targets)
    for participant in stage_p.PARTICIPANTS:
        participant_rows = [row for row in targets if row["participant"] == participant]
        stage_p.validate_exact_identity_grid(participant_rows, participant_sessions=[(participant, "E")])
    return targets


def _claim_boundary(route: str) -> dict[str, str]:
    meanings = {
        "BNCIC3C5-R2": "Neither registered C3 nor C5-partial gate passed.",
        "BNCIC3C5-R3": "The C3 unseen-participant protocol-condition gate passed; C5-partial did not.",
        "BNCIC3C5-R4": "The C5-partial incremental EEG-beyond-recorded-EOG gate passed; C3 did not.",
        "BNCIC3C5-R5": "Both the C3 unseen-participant protocol-condition gate and C5-partial incremental EEG-beyond-recorded-EOG gate passed.",
    }
    return {
        "registered_result": meanings[route],
        "maximum_scientific_meaning": "participant-independent four-class BNCI protocol-condition prediction and incremental scalp-EEG sensor information beyond three recorded EOG channels",
        "not_established": "thought or language decoding, executed movement intention, exclusive motor-cortex origin, freedom from every peripheral or visual confound, live decoding, portable hardware, home use, or clinical utility",
    }


def _execute_stage_t(
    root: str | Path,
    *,
    activation: Mapping[str, Any],
    remote_proof: Mapping[str, Any],
    environ: Mapping[str, str],
) -> dict[str, Any]:
    repo = Path(root).resolve()
    if repo != q_core._repo_root():
        raise BNCIStageTRefusal("Stage T repository root differs")
    q_core.assert_single_thread_environment(environ)
    result_path = repo / RESULT_RELATIVE_PATH
    marker = repo / MARKER_RELATIVE_PATH
    if any(path.exists() or path.is_symlink() for path in (result_path, marker)):
        raise BNCIStageTRefusal("Stage T is already consumed or has output")
    public_freeze_payload = stage_p._read_direct(repo / stage_p.PUBLIC_FREEZE_RELATIVE_PATH)
    try:
        public_freeze = validate_public_freeze(json.loads(public_freeze_payload))
    except json.JSONDecodeError as exc:
        raise BNCIStageTRefusal("Stage T public freeze JSON is invalid") from exc
    if activation["prediction_freeze_artifact"] != {
        "path": stage_p.PUBLIC_FREEZE_RELATIVE_PATH.as_posix(),
        "bytes": len(public_freeze_payload),
        "sha256": _sha256(public_freeze_payload),
    }:
        raise BNCIStageTRefusal("Stage T public freeze activation binding differs")
    marker_payload = _canonical_bytes({
        "schema_name": "neurodecodekit.bnci_2014_001_stage_t_consumed_marker",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_before_scoring_key_or_target_open",
        "prediction_freeze_commit": activation["green_prediction_freeze"]["commit"],
        "rerun_allowed": False,
        "post_target_updates_allowed": False,
    })
    q_live._exclusive_write(repo, marker, marker_payload)
    started = time.monotonic()
    stage_p_output = repo / stage_p.OUTPUT_RELATIVE_PATH
    stage_q_output = repo / q_core.STAGE_Q_OUTPUT_RELATIVE_PATH
    private_manifest_payload = stage_p._read_direct(stage_p_output / stage_p.PRIVATE_MANIFEST_NAME)
    stage_q_manifest_payload = stage_p._read_direct(stage_q_output / stage_p.PRIVATE_MANIFEST_NAME)
    binding_key = stage_p._read_direct(stage_p_output / stage_p.PRIVATE_BINDING_KEY_NAME, expected_bytes=32)
    try:
        private_manifest = json.loads(private_manifest_payload)
        stage_q_manifest = json.loads(stage_q_manifest_payload)
    except json.JSONDecodeError as exc:
        raise BNCIStageTRefusal("Stage T private manifest JSON is invalid") from exc
    if (
        private_manifest.get("schema_name") != "neurodecodekit.bnci_2014_001_stage_p_private_manifest"
        or private_manifest.get("status") != "complete_target_blind_predictions_targets_still_sealed"
        or private_manifest.get("target_deliveries") != 0
        or private_manifest.get("scores") != 0
    ):
        raise BNCIStageTRefusal("Stage T Stage P private manifest differs")
    if (
        stage_p.source_capability_commitment(stage_q_manifest_payload, binding_key)
        != public_freeze["source_capability_HMAC_commitment"]
        or private_manifest.get("source_capability_HMAC_commitment")
        != public_freeze["source_capability_HMAC_commitment"]
    ):
        raise BNCIStageTRefusal("Stage T source capability commitment differs")
    target_transport = stage_p._target_transport_inventory(stage_q_manifest)
    if (
        _sha256(_canonical_bytes(target_transport))
        != public_freeze["sealed_target_transport_commitment_sha256"]
        or private_manifest.get("sealed_target_transport_commitment_sha256")
        != public_freeze["sealed_target_transport_commitment_sha256"]
    ):
        raise BNCIStageTRefusal("Stage T sealed target transport commitment differs")
    prediction_rows, prediction_payload = _load_private_predictions(
        stage_p_output, private_manifest, public_freeze
    )
    target_rows = _deliver_target_rows(
        repo=repo,
        stage_q_output=stage_q_output,
        stage_q_manifest=stage_q_manifest,
        prediction_rows=prediction_rows,
    )
    if {scorer._identity(row) for row in prediction_rows} != {
        scorer._identity(row) for row in target_rows
    }:
        raise BNCIStageTRefusal("Stage T prediction and target inventories differ")
    metrics = scorer._score_rows(prediction_rows, target_rows)
    runtime = time.monotonic() - started
    peak_rss = model_core.peak_process_tree_rss_bytes()
    if runtime > 3600.0 or peak_rss > 1_073_741_824:
        raise BNCIStageTRefusal("Stage T resource cap exceeded")
    result: dict[str, Any] = {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_t_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "scored_once_frozen_router_applied_consumed",
        "route": metrics["route"],
        "C3_passed": metrics["C3_passed"],
        "C5_partial_passed": metrics["C5_partial_passed"],
        "aggregate_metrics": {
            key: value
            for key, value in metrics.items()
            if key not in {"route", "C3_passed", "C5_partial_passed", "participant_count", "held_out_session"}
        },
        "inventory": {
            "participants": 9,
            "held_out_session": "E",
            "held_out_rows": 2592,
            "held_out_rows_per_participant": 288,
            "prediction_conditions": 16,
            "prediction_rows": len(prediction_rows),
            "target_rows": len(target_rows),
            "held_out_T_rows_used": 0,
        },
        "operation_counters": {
            "private_prediction_payload_opens": 9,
            "scoring_key_vault_opens": 1,
            "sealed_target_envelope_opens": 9,
            "target_deliveries": 1,
            "scores": 1,
            "post_target_updates": 0,
            "reruns": 0,
        },
        "bindings": {
            "prediction_freeze_commit": activation["green_prediction_freeze"]["commit"],
            "prediction_freeze_sha256": _sha256(public_freeze_payload),
            "prediction_set_sha256": _sha256(prediction_payload),
            "source_capability_HMAC_commitment": public_freeze["source_capability_HMAC_commitment"],
            "sealed_target_transport_commitment_sha256": public_freeze["sealed_target_transport_commitment_sha256"],
        },
        "measurements": {
            "runtime_seconds": runtime,
            "peak_process_tree_RSS_bytes": peak_rss,
            "public_result_bytes": 0,
            "network_bytes": 0,
            "end_to_end_live_decoding_latency_measured": False,
        },
        "remote_green_scoring_control_plane": dict(remote_proof),
        "claim_boundary": _claim_boundary(metrics["route"]),
        "warnings": [
            "this_is_an_offline_four_class_protocol_condition_experiment_not_thought_or_language_decoding",
            "recorded_EOG_controls_do_not_exclude_every_unrecorded_peripheral_or_visual_confound",
            "no_individual_prediction_probability_target_or_participant_outcome_is_public",
            "the_one_scoring_event_is_consumed_and_cannot_be_retried_or_tuned",
        ],
        "rerun_allowed": False,
    }
    for _ in range(8):
        payload = _canonical_bytes(result)
        if result["measurements"]["public_result_bytes"] == len(payload):
            break
        result["measurements"]["public_result_bytes"] = len(payload)
    else:
        raise BNCIStageTRefusal("Stage T result byte count did not stabilize")
    if len(payload) > q_core.PUBLIC_OUTPUT_CAP_BYTES:
        raise BNCIStageTRefusal("Stage T result exceeds public output cap")
    q_live._exclusive_write(repo, result_path, payload)
    return result


def execute_registered_stage_t(root: str | Path, *, environ: Mapping[str, str]) -> dict[str, Any]:
    """Deliver the sealed targets and apply the frozen scorer exactly once."""

    activation = read_green_activation(root)
    remote_proof = q_live.collect_remote_green_proof(root)
    return _execute_stage_t(
        root,
        activation=activation,
        remote_proof=remote_proof,
        environ=environ,
    )


def plan_stage_t() -> dict[str, Any]:
    return {
        "lane_id": LANE_ID,
        "target_deliveries": 1,
        "scores": 1,
        "post_target_updates": 0,
        "reruns": 0,
        "held_out_T_rows_used": 0,
        "maximum_route": "BNCIC3C5-R5",
        "next_gate": "prediction_freeze_and_stage_t_activation_must_both_be_remotely_green",
    }
