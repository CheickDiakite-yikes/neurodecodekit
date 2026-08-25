"""Live-only control plane for the qualified BNCI-C3C5-1 Stage Q core."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import shutil
import stat
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Mapping

from neurodecodekit.datasets import bnci_2014_001_stage_q as core


LIVE_ACTIVATION_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_stage_q_live_implementation_activation.v0.json"
)
SCORING_KEY_VAULT_RELATIVE_PATH = Path(
    ".codex_work/bnci_c3c5/stage_q_scoring_keys.sealed_until_T.private.v0.json"
)
QUALIFIED_RESULT_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_stage_q_generated_result.v0.json"
)
QUALIFIED_RESULT_SHA256 = "a240b4852b5e5a908ce929d5b07d32a4090d3371df576007bbe5020eac76620b"
LIVE_IMPLEMENTATION_ARTIFACTS = (
    "src/neurodecodekit/datasets/bnci_2014_001_stage_q.py",
    "src/neurodecodekit/datasets/bnci_2014_001_stage_q_live.py",
    "src/neurodecodekit/bnci_c3c5_stage_q_cli.py",
    "src/neurodecodekit/bnci_c3c5_stage_q_live_cli.py",
    "tests/test_zz_bnci_2014_001_stage_q_implementation.py",
    "tests/test_zz_bnci_2014_001_stage_q_live_control.py",
    "tests/test_zz_bnci_2014_001_stage_q_implementation_record.py",
    "tests/test_zz_bnci_2014_001_stage_q_generated_result.py",
    "docs/BNCI_2014_001_STAGE_Q_IMPLEMENTATION.md",
    "registries/bnci_2014_001_stage_q_implementation.v0.json",
    "registries/bnci_2014_001_stage_q_generated_result.v0.json",
)
HEX_DIGEST_LENGTH = 64
ENVELOPE_MAGIC = b"NDKQ1"
PRIVATE_LAYOUT_FIXED_MARGIN_BYTES = 64 * 1024 * 1024
MINIMUM_FREE_DISK_BYTES = 2 * 1024 * 1024 * 1024
REMOTE_PROOF_FIELDS = {
    "branch",
    "head_sha",
    "remote_head_sha",
    "CI_run_id",
    "CI_head_sha",
    "CI_conclusion",
    "base_python_job_id",
    "base_python_job_name",
    "base_python_job_conclusion",
    "optional_neuro_readers_job_id",
    "optional_neuro_readers_job_name",
    "optional_neuro_readers_job_conclusion",
}


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == HEX_DIGEST_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_commit(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )


def _artifact_identity(root: Path, relative_path: str) -> dict[str, Any]:
    payload = (root / relative_path).read_bytes()
    return {
        "path": relative_path,
        "bytes": len(payload),
        "sha256": core._sha256(payload),
    }


def validate_activation_document(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise core.BNCIStageQRefusal("Stage Q live activation is not an object")
    if set(value) != {
        "lane_id",
        "status",
        "green_stage_a_result",
        "green_implementation",
        "qualified_generated_core",
        "implementation_artifacts",
        "authority",
    }:
        raise core.BNCIStageQRefusal("Stage Q live activation fields differ")
    if value.get("lane_id") != core.LANE_ID or value.get("status") != "remotely_green_live_execution_enabled":
        raise core.BNCIStageQRefusal("Stage Q live activation status differs")
    stage_a = value.get("green_stage_a_result")
    expected_stage_a = {
        "commit": core.STAGE_A_RESULT_COMMIT,
        "CI_run_id": core.STAGE_A_RESULT_CI_RUN_ID,
        "base_python_job_id": core.STAGE_A_RESULT_BASE_JOB_ID,
        "optional_neuro_readers_job_id": core.STAGE_A_RESULT_OPTIONAL_JOB_ID,
        "both_required_jobs_green": True,
    }
    if stage_a != expected_stage_a:
        raise core.BNCIStageQRefusal("Stage Q Stage A green binding differs")
    green = value.get("green_implementation")
    if (
        not isinstance(green, dict)
        or set(green)
        != {
            "commit",
            "CI_head_sha",
            "CI_conclusion",
            "CI_run_id",
            "base_python_job_id",
            "base_python_job_name",
            "base_python_job_conclusion",
            "optional_neuro_readers_job_id",
            "optional_neuro_readers_job_name",
            "optional_neuro_readers_job_conclusion",
            "both_required_jobs_green",
        }
        or not _is_commit(green.get("commit"))
        or green.get("CI_head_sha") != green.get("commit")
        or green.get("CI_conclusion") != "success"
        or green.get("base_python_job_name") != "Base Python"
        or green.get("base_python_job_conclusion") != "success"
        or green.get("optional_neuro_readers_job_name") != "Optional Neuro Readers"
        or green.get("optional_neuro_readers_job_conclusion") != "success"
        or not all(
            isinstance(green.get(field), int) and green[field] > 0
            for field in ("CI_run_id", "base_python_job_id", "optional_neuro_readers_job_id")
        )
        or green.get("both_required_jobs_green") is not True
    ):
        raise core.BNCIStageQRefusal("Stage Q implementation green proof differs")
    qualified = value.get("qualified_generated_core")
    if qualified != {
        "path": QUALIFIED_RESULT_RELATIVE_PATH.as_posix(),
        "sha256": QUALIFIED_RESULT_SHA256,
        "consumed": True,
        "may_be_repeated": False,
    }:
        raise core.BNCIStageQRefusal("Stage Q generated-core binding differs")
    artifacts = value.get("implementation_artifacts")
    if not isinstance(artifacts, list):
        raise core.BNCIStageQRefusal("Stage Q implementation artifact table is absent")
    if [row.get("path") for row in artifacts if isinstance(row, dict)] != list(
        LIVE_IMPLEMENTATION_ARTIFACTS
    ):
        raise core.BNCIStageQRefusal("Stage Q implementation artifact path set differs")
    for row in artifacts:
        if (
            set(row) != {"path", "bytes", "sha256"}
            or not isinstance(row["bytes"], int)
            or row["bytes"] <= 0
            or not _is_sha256(row["sha256"])
        ):
            raise core.BNCIStageQRefusal("Stage Q implementation artifact identity differs")
    authority = value.get("authority")
    if authority != {
        "one_live_Stage_Q_execution": True,
        "network_bytes": 0,
        "model_runs": 0,
        "training_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scores": 0,
        "reruns": 0,
        "Stage_P": False,
        "Stage_T": False,
        "claim_upgrade": False,
    }:
        raise core.BNCIStageQRefusal("Stage Q live authority differs")
    return value


def read_green_live_activation(root: str | Path) -> dict[str, Any]:
    repo = Path(root).resolve()
    if (repo / core.ACTIVATION_RELATIVE_PATH).exists() or (
        repo / core.ACTIVATION_RELATIVE_PATH
    ).is_symlink():
        raise core.BNCIStageQRefusal("deprecated Stage Q core activation path must remain absent")
    activation_path = repo / LIVE_ACTIVATION_RELATIVE_PATH
    qualified_payload = (repo / QUALIFIED_RESULT_RELATIVE_PATH).read_bytes()
    if core._sha256(qualified_payload) != QUALIFIED_RESULT_SHA256:
        raise core.BNCIStageQRefusal("Stage Q qualified generated result changed")
    payload = activation_path.read_bytes()
    try:
        activation = validate_activation_document(json.loads(payload))
    except json.JSONDecodeError as exc:
        raise core.BNCIStageQRefusal("Stage Q live activation JSON is invalid") from exc
    green = activation["green_implementation"]
    for expected, row in zip(LIVE_IMPLEMENTATION_ARTIFACTS, activation["implementation_artifacts"], strict=True):
        if row != _artifact_identity(repo, expected):
            raise core.BNCIStageQRefusal("Stage Q live implementation artifact changed")
        if core._git_output(repo, "show", f"{green['commit']}:{expected}") != (repo / expected).read_bytes():
            raise core.BNCIStageQRefusal("Stage Q live artifact differs from green commit")
    if core._git_output(repo, "show", f"HEAD:{LIVE_ACTIVATION_RELATIVE_PATH.as_posix()}") != payload:
        raise core.BNCIStageQRefusal("Stage Q live activation differs from HEAD")
    core._git_output(repo, "merge-base", "--is-ancestor", core.STAGE_A_RESULT_COMMIT, "HEAD")
    core._git_output(repo, "merge-base", "--is-ancestor", green["commit"], "HEAD")
    branch = core._git_output(repo, "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
    if not branch or branch == "HEAD":
        raise core.BNCIStageQRefusal("Stage Q execution requires a pushed branch")
    local_head = core._git_output(repo, "rev-parse", "HEAD").strip()
    remote_head = core._git_output(repo, "rev-parse", f"refs/remotes/origin/{branch}").strip()
    if local_head != remote_head:
        raise core.BNCIStageQRefusal("Stage Q HEAD is not identical to its pushed remote branch")
    subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=repo, check=True, timeout=30)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--"], cwd=repo, check=True, timeout=30)
    return activation


def validate_remote_green_proof(root: str | Path, value: Any) -> dict[str, Any]:
    repo = Path(root).resolve()
    if not isinstance(value, dict) or set(value) != REMOTE_PROOF_FIELDS:
        raise core.BNCIStageQRefusal("Stage Q remote-green proof fields differ")
    branch = core._git_output(repo, "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
    head = core._git_output(repo, "rev-parse", "HEAD").decode().strip()
    if (
        not branch
        or branch == "HEAD"
        or value["branch"] != branch
        or value["head_sha"] != head
        or value["remote_head_sha"] != head
        or value["CI_head_sha"] != head
        or value["CI_conclusion"] != "success"
        or value["base_python_job_name"] != "Base Python"
        or value["base_python_job_conclusion"] != "success"
        or value["optional_neuro_readers_job_name"] != "Optional Neuro Readers"
        or value["optional_neuro_readers_job_conclusion"] != "success"
        or not all(
            isinstance(value[field], int) and value[field] > 0
            for field in (
                "CI_run_id",
                "base_python_job_id",
                "optional_neuro_readers_job_id",
            )
        )
    ):
        raise core.BNCIStageQRefusal("Stage Q remote-green proof differs")
    return value


def collect_remote_green_proof(
    root: str | Path,
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    """Collect fresh remote SHA and GitHub CI proof before analysis starts."""

    repo = Path(root).resolve()
    branch = core._git_output(repo, "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
    head = core._git_output(repo, "rev-parse", "HEAD").decode().strip()
    if not branch or branch == "HEAD" or not _is_commit(head):
        raise core.BNCIStageQRefusal("Stage Q remote preflight requires a branch commit")
    try:
        remote = runner(
            ["git", "ls-remote", "--heads", "origin", f"refs/heads/{branch}"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        remote_fields = remote.stdout.strip().split()
        if len(remote_fields) != 2 or remote_fields[0] != head:
            raise core.BNCIStageQRefusal("Stage Q fresh remote head differs")
        listed = runner(
            [
                "gh",
                "run",
                "list",
                "--workflow",
                "ci.yml",
                "--branch",
                branch,
                "--commit",
                head,
                "--limit",
                "20",
                "--json",
                "databaseId,headSha,status,conclusion",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        candidates = json.loads(listed.stdout)
        if not isinstance(candidates, list):
            raise core.BNCIStageQRefusal("Stage Q remote CI listing differs")
        successes = [
            row
            for row in candidates
            if isinstance(row, dict)
            and row.get("headSha") == head
            and row.get("status") == "completed"
            and row.get("conclusion") == "success"
            and isinstance(row.get("databaseId"), int)
        ]
        if not successes:
            raise core.BNCIStageQRefusal("Stage Q activation commit is not remotely green")
        run_id = max(int(row["databaseId"]) for row in successes)
        viewed = runner(
            [
                "gh",
                "run",
                "view",
                str(run_id),
                "--json",
                "headSha,status,conclusion,jobs",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        run = json.loads(viewed.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise core.BNCIStageQRefusal("Stage Q remote-green preflight failed") from exc
    if not isinstance(run, dict):
        raise core.BNCIStageQRefusal("Stage Q remote CI run differs")
    jobs = run.get("jobs")
    if (
        run.get("headSha") != head
        or run.get("status") != "completed"
        or run.get("conclusion") != "success"
        or not isinstance(jobs, list)
    ):
        raise core.BNCIStageQRefusal("Stage Q remote CI run differs")
    by_name = {job.get("name"): job for job in jobs if isinstance(job, dict)}
    base = by_name.get("Base Python")
    optional = by_name.get("Optional Neuro Readers")
    if (
        not isinstance(base, dict)
        or not isinstance(optional, dict)
        or base.get("status") != "completed"
        or optional.get("status") != "completed"
        or base.get("conclusion") != "success"
        or optional.get("conclusion") != "success"
        or not isinstance(base.get("databaseId"), int)
        or not isinstance(optional.get("databaseId"), int)
    ):
        raise core.BNCIStageQRefusal("Stage Q required remote CI jobs differ")
    proof = {
        "branch": branch,
        "head_sha": head,
        "remote_head_sha": remote_fields[0],
        "CI_run_id": run_id,
        "CI_head_sha": run["headSha"],
        "CI_conclusion": run["conclusion"],
        "base_python_job_id": int(base["databaseId"]),
        "base_python_job_name": base["name"],
        "base_python_job_conclusion": base["conclusion"],
        "optional_neuro_readers_job_id": int(optional["databaseId"]),
        "optional_neuro_readers_job_name": optional["name"],
        "optional_neuro_readers_job_conclusion": optional["conclusion"],
    }
    return validate_remote_green_proof(repo, proof)


def _ensure_direct_directory(root: Path, directory: Path) -> None:
    try:
        parts = directory.relative_to(root).parts
    except ValueError as exc:
        raise core.BNCIStageQRefusal("Stage Q output escaped the repository") from exc
    current = root
    root_info = root.lstat()
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise core.BNCIStageQRefusal("Stage Q repository root is not direct")
    for part in parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            current.mkdir(mode=0o700)
            info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise core.BNCIStageQRefusal("Stage Q output ancestry is not direct")


def _exclusive_directory(root: Path, directory: Path) -> None:
    _ensure_direct_directory(root, directory.parent)
    try:
        directory.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise core.BNCIStageQRefusal("Stage Q temporary output already exists") from exc
    info = directory.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise core.BNCIStageQRefusal("Stage Q temporary output is not direct")


def _exclusive_write(root: Path, path: Path, payload: bytes) -> None:
    _ensure_direct_directory(root, path.parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise core.BNCIStageQRefusal("Stage Q anchored write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _stream_bytes(key: bytes, length: int) -> bytes:
    output = bytearray()
    counter = 0
    while len(output) < length:
        output.extend(hashlib.sha256(key + counter.to_bytes(8, "big")).digest())
        counter += 1
    return bytes(output[:length])


def seal_payload(payload: bytes, key: bytes) -> bytes:
    if len(key) != 32:
        raise core.BNCIStageQRefusal("Stage Q sealing key length differs")
    stream = _stream_bytes(key, len(payload))
    ciphertext = bytes(left ^ right for left, right in zip(payload, stream, strict=True))
    tag = hmac.new(key, ENVELOPE_MAGIC + ciphertext, hashlib.sha256).digest()
    return ENVELOPE_MAGIC + tag + ciphertext


def unseal_payload(envelope: bytes, key: bytes) -> bytes:
    if len(key) != 32 or not envelope.startswith(ENVELOPE_MAGIC) or len(envelope) < 37:
        raise core.BNCIStageQRefusal("Stage Q sealed envelope is malformed")
    tag = envelope[5:37]
    ciphertext = envelope[37:]
    expected = hmac.new(key, ENVELOPE_MAGIC + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        raise core.BNCIStageQRefusal("Stage Q sealed envelope authentication failed")
    stream = _stream_bytes(key, len(ciphertext))
    return bytes(left ^ right for left, right in zip(ciphertext, stream, strict=True))


def fold_masks(participant_values: Any, session_values: Any, held_out_index: int) -> tuple[Any, Any, Any]:
    np = core._np()
    participants = np.asarray(participant_values)
    sessions = np.asarray(session_values)
    if participants.shape != (core.ROWS_TOTAL,) or sessions.shape != (core.ROWS_TOTAL,):
        raise core.BNCIStageQRefusal("Stage Q fold identity shape differs")
    source = participants != held_out_index
    held_out_e = (participants == held_out_index) & (sessions == 1)
    held_out_t = (participants == held_out_index) & (sessions == 0)
    if (
        int(source.sum()) != core.SOURCE_ROWS_PER_FOLD
        or int(held_out_e.sum()) != core.HELD_OUT_E_ROWS_PER_FOLD
        or int(held_out_t.sum()) != core.HELD_OUT_E_ROWS_PER_FOLD
    ):
        raise core.BNCIStageQRefusal("Stage Q fold capability count differs")
    return source, held_out_e, held_out_t


def _assert_resource_caps(*, started: float, private_bytes: int) -> tuple[float, int]:
    runtime = time.perf_counter() - started
    peak_rss = core.peak_process_rss_bytes()
    if runtime > core.RUNTIME_CAP_SECONDS:
        raise core.BNCIStageQRefusal("Stage Q runtime cap exceeded")
    if peak_rss > core.PEAK_RSS_CAP_BYTES:
        raise core.BNCIStageQRefusal("Stage Q peak RSS cap exceeded")
    if private_bytes > core.PRIVATE_OUTPUT_CAP_BYTES:
        raise core.BNCIStageQRefusal("Stage Q private derivative cap exceeded")
    return runtime, peak_rss


def private_layout_preflight_bound_bytes() -> int:
    """Return a conservative bound for one-copy shards plus all metadata."""

    feature_bytes = core.ROWS_TOTAL * sum(core.FEATURE_DIMENSIONS.values()) * 4
    identity_bytes = core.ROWS_TOTAL * (1 + 1 + 1 + 1 + 4 + 64)
    source_target_bytes = (
        len(core.PARTICIPANTS) * core.SOURCE_ROWS_PER_FOLD * (64 + 1)
    )
    scoring_bytes = core.ROWS_TOTAL * (64 + 1 + 1 + 1)
    raw_bytes = feature_bytes + identity_bytes + source_target_bytes + scoring_bytes
    return 2 * raw_bytes + PRIVATE_LAYOUT_FIXED_MARGIN_BYTES


def _bounded_private_total(current: int, added: int) -> int:
    total = current + added
    if total > core.PRIVATE_OUTPUT_CAP_BYTES:
        raise core.BNCIStageQRefusal("Stage Q private derivatives exceed cap")
    return total


def _write_live_derivatives(
    repo: Path,
    output: Path,
    feature_rows: Mapping[str, list[Any]],
    identity: Mapping[str, list[Any]],
    targets: Any,
    artifacts: Any,
    artifact_available: Any,
    *,
    key_factory: Callable[[int], bytes],
    scoring_key_path: Path,
) -> tuple[dict[str, Any], int]:
    np = core._np()
    arrays: dict[str, Any] = {
        name: np.asarray(rows, dtype="float32") for name, rows in feature_rows.items()
    }
    arrays.update(
        {
            "participant_index": np.asarray(identity["participant_index"], dtype="uint8"),
            "session_index": np.asarray(identity["session_index"], dtype="uint8"),
            "run_ordinal": np.asarray(identity["run_ordinal"], dtype="uint8"),
            "trial_ordinal": np.asarray(identity["trial_ordinal"], dtype="uint8"),
            "trial_start_sample": np.asarray(identity["trial_start_sample"], dtype="int32"),
            "opaque_row_id": np.asarray(identity["opaque_row_id"], dtype="S64"),
        }
    )
    for name, dimension in core.FEATURE_DIMENSIONS.items():
        if arrays[name].shape != (core.ROWS_TOTAL, dimension):
            raise core.BNCIStageQRefusal(f"Stage Q cohort feature shape differs: {name}")
    if private_layout_preflight_bound_bytes() > core.PRIVATE_OUTPUT_CAP_BYTES:
        raise core.BNCIStageQRefusal("Stage Q one-copy layout cannot fit its cap")
    total = 0
    target_values = np.asarray(targets, dtype="uint8")
    artifact_values = np.asarray(artifacts, dtype="uint8")
    artifact_availability = np.asarray(artifact_available, dtype="uint8")
    participant_values = arrays["participant_index"]
    session_values = arrays["session_index"]
    scoring_keys: dict[str, str] = {}
    derivative_rows: list[dict[str, Any]] = []
    signal_shards: dict[tuple[int, int], dict[str, Any]] = {}
    for participant_index, participant in enumerate(core.PARTICIPANTS):
        for session_index, session in enumerate(core.SESSIONS):
            shard_mask = (participant_values == participant_index) & (
                session_values == session_index
            )
            if int(shard_mask.sum()) != core.HELD_OUT_E_ROWS_PER_FOLD:
                raise core.BNCIStageQRefusal("Stage Q participant/session shard count differs")
            shard_payload = core.deterministic_npz_bytes(
                {name: values[shard_mask] for name, values in arrays.items()}
            )
            total = _bounded_private_total(total, len(shard_payload))
            shard_path = (
                output
                / "participant_signal_shards"
                / f"{participant}{session}.target_free.private.v0.npz"
            )
            _exclusive_write(repo, shard_path, shard_payload)
            shard_record = {
                "role": "target_free_participant_session_signal_shard",
                "participant": participant,
                "session": session,
                "file": str(shard_path.relative_to(output)),
                "rows": int(shard_mask.sum()),
                "bytes": len(shard_payload),
                "sha256": core._sha256(shard_payload),
            }
            signal_shards[(participant_index, session_index)] = shard_record
            derivative_rows.append(shard_record)
    for held_out_index, participant in enumerate(core.PARTICIPANTS):
        source_mask, held_out_e_mask, held_out_t_mask = fold_masks(
            participant_values, session_values, held_out_index
        )
        source_target_payload = core.deterministic_npz_bytes(
            {
                "opaque_row_id": arrays["opaque_row_id"][source_mask],
                "target_index": target_values[source_mask],
            }
        )
        total = _bounded_private_total(total, len(source_target_payload))
        source_target_path = (
            output
            / "fold_capabilities"
            / f"fold_{participant}.source_targets.private.v0.npz"
        )
        _exclusive_write(repo, source_target_path, source_target_payload)
        delivered_shards = []
        for source_index in range(len(core.PARTICIPANTS)):
            if source_index == held_out_index:
                continue
            for session_index in range(len(core.SESSIONS)):
                delivered_shards.append(
                    {
                        **signal_shards[(source_index, session_index)],
                        "delivery_role": "source_signal",
                    }
                )
        delivered_shards.append(
            {
                **signal_shards[(held_out_index, 1)],
                "delivery_role": "held_out_E_signal",
            }
        )
        delivery_manifest = {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_q_fold_delivery",
            "schema_version": core.SCHEMA_VERSION,
            "fold": participant,
            "signal_shards": delivered_shards,
            "source_target_capability": {
                "file": str(source_target_path.relative_to(output)),
                "rows": int(source_mask.sum()),
                "bytes": len(source_target_payload),
                "sha256": core._sha256(source_target_payload),
            },
            "held_out_E_rows": int(held_out_e_mask.sum()),
            "held_out_T_rows": int(held_out_t_mask.sum()),
            "held_out_T_rows_delivered": 0,
            "future_delivery": "exact_listed_bytes_only_no_repository_root_or_scoring_key_path",
        }
        delivery_payload = core._canonical_bytes(delivery_manifest)
        total = _bounded_private_total(total, len(delivery_payload))
        delivery_path = (
            output / "fold_capabilities" / f"fold_{participant}.delivery.private.v0.json"
        )
        _exclusive_write(repo, delivery_path, delivery_payload)
        held_out_plaintext = core.deterministic_npz_bytes(
            {
                "opaque_row_id": arrays["opaque_row_id"][held_out_e_mask],
                "target_index": target_values[held_out_e_mask],
            }
        )
        held_out_key = key_factory(32)
        held_out_envelope = seal_payload(held_out_plaintext, held_out_key)
        held_out_path = output / "scoring_target_vault" / f"fold_{participant}.sealed.v0.bin"
        total = _bounded_private_total(total, len(held_out_envelope))
        _exclusive_write(repo, held_out_path, held_out_envelope)
        scoring_keys[participant] = held_out_key.hex()
        derivative_rows.extend(
            [
                {"role": "fold_scoped_source_targets", "fold": participant, "file": str(source_target_path.relative_to(output)), "bytes": len(source_target_payload), "sha256": core._sha256(source_target_payload), "source_rows": int(source_mask.sum())},
                {"role": "fold_delivery_manifest", "fold": participant, "file": str(delivery_path.relative_to(output)), "bytes": len(delivery_payload), "sha256": core._sha256(delivery_payload), "signal_shards": len(delivered_shards), "held_out_T_rows_delivered": 0},
                {"role": "sealed_scoring_targets", "fold": participant, "file": str(held_out_path.relative_to(output)), "bytes": len(held_out_envelope), "sha256": core._sha256(held_out_envelope)},
            ]
        )
    artifact_plaintext = core.deterministic_npz_bytes(
        {
            "opaque_row_id": arrays["opaque_row_id"],
            "artifact_flag": artifact_values,
            "artifact_available": artifact_availability,
        }
    )
    artifact_key = key_factory(32)
    artifact_envelope = seal_payload(artifact_plaintext, artifact_key)
    artifact_path = output / "scoring_target_vault" / "artifacts.sealed.v0.bin"
    total = _bounded_private_total(total, len(artifact_envelope))
    _exclusive_write(repo, artifact_path, artifact_envelope)
    scoring_keys["artifacts"] = artifact_key.hex()
    scoring_key_payload = core._canonical_bytes(
        {"schema_name": "neurodecodekit.bnci_2014_001_stage_q_scoring_key_vault", "schema_version": core.SCHEMA_VERSION, "keys": scoring_keys}
    )
    total = _bounded_private_total(total, len(scoring_key_payload))
    _exclusive_write(repo, scoring_key_path, scoring_key_payload)
    derivative_rows.extend(
        [
            {"role": "sealed_artifact_flags_and_availability", "file": str(artifact_path.relative_to(output)), "bytes": len(artifact_envelope), "sha256": core._sha256(artifact_envelope)},
            {"role": "scoring_key_vault_sealed_until_T", "file": "separate_fixed_private_path_not_in_fold_capability_tree", "bytes": len(scoring_key_payload), "sha256": core._sha256(scoring_key_payload)},
        ]
    )
    manifest = {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_q_private_derivative_manifest",
        "schema_version": core.SCHEMA_VERSION,
        "lane_id": core.LANE_ID,
        "status": "complete_encrypted_target_firewalled_capabilities",
        "rows": core.ROWS_TOTAL,
        "task_runs": 108,
        "channels": list(core.ALL_CHANNELS),
        "sampling_rate_hz": core.SAMPLING_RATE_HZ,
        "features": core.FEATURE_DIMENSIONS,
        "folds": 9,
        "source_rows_per_fold": core.SOURCE_ROWS_PER_FOLD,
        "held_out_E_rows_per_fold": core.HELD_OUT_E_ROWS_PER_FOLD,
        "held_out_T_rows_exposed_per_fold": 0,
        "global_predictive_archive_exists": False,
        "one_copy_target_free_participant_session_signal_shards": True,
        "participant_session_signal_shards": len(signal_shards),
        "fold_delivery_manifests_reference_only_source_and_held_out_E_shards": True,
        "source_labels_exist_only_in_their_matching_fold_capability": True,
        "held_out_scoring_targets_stored_as_authenticated_envelopes": True,
        "scoring_keys_are_outside_the_fold_capability_tree": True,
        "first_trial_previous_interval_seconds_sentinel": 0.0,
        "geometry_available_from_payload": False,
        "artifacts": derivative_rows,
    }
    manifest_payload = core._canonical_bytes(manifest)
    manifest_path = output / "manifest.private.v0.json"
    total = _bounded_private_total(total, len(manifest_payload))
    _exclusive_write(repo, manifest_path, manifest_payload)
    return manifest, total


def _execute_registered_stage_q_live(
    root: str | Path,
    *,
    environ: Mapping[str, str],
    remote_green_proof: Mapping[str, Any],
    key_factory: Callable[[int], bytes],
) -> dict[str, Any]:
    repo = Path(root).resolve()
    if repo != core._repo_root():
        raise core.BNCIStageQRefusal("Stage Q repository root differs")
    core.assert_single_thread_environment(environ)
    versions = core.assert_exact_versions()
    core.load_public_bindings(repo)
    activation = read_green_live_activation(repo)
    remote_proof = validate_remote_green_proof(repo, remote_green_proof)
    members = core.registered_members(repo)
    output = repo / core.STAGE_Q_OUTPUT_RELATIVE_PATH
    marker = repo / core.STAGE_Q_MARKER_RELATIVE_PATH
    receipt_path = repo / core.STAGE_Q_RECEIPT_RELATIVE_PATH
    scoring_key_path = repo / SCORING_KEY_VAULT_RELATIVE_PATH
    if any(
        path.exists() or path.is_symlink()
        for path in (output, marker, receipt_path, scoring_key_path)
    ):
        raise core.BNCIStageQRefusal("Stage Q is already consumed or has output")
    layout_bound = private_layout_preflight_bound_bytes()
    if layout_bound > core.PRIVATE_OUTPUT_CAP_BYTES:
        raise core.BNCIStageQRefusal("Stage Q one-copy layout cannot fit its cap")
    free_before = shutil.disk_usage(repo).free
    if free_before < MINIMUM_FREE_DISK_BYTES + layout_bound:
        raise core.BNCIStageQRefusal("Stage Q free-disk preflight failed")
    temporary = output.with_name(output.name + f".tmp-{os.getpid()}")
    _exclusive_directory(repo, temporary)
    _ensure_direct_directory(repo, marker.parent)
    _ensure_direct_directory(repo, scoring_key_path.parent)
    marker_payload = core._canonical_bytes(
        {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_q_consumed_marker",
            "schema_version": core.SCHEMA_VERSION,
            "lane_id": core.LANE_ID,
            "status": "consumed_before_private_manifest_or_MAT_open",
            "implementation_commit": activation["green_implementation"]["commit"],
            "rerun_allowed": False,
        }
    )
    try:
        _exclusive_write(repo, marker, marker_payload)
    except Exception:
        shutil.rmtree(temporary)
        raise
    ledger = core.OperationLedger()
    started = time.perf_counter()
    try:
        core._private_manifest(repo, members)
        ledger.private_manifest_opens += 1
        feature_rows: dict[str, list[Any]] = {name: [] for name in core.FEATURE_DIMENSIONS}
        identity: dict[str, list[Any]] = {
            "participant_index": [],
            "session_index": [],
            "run_ordinal": [],
            "trial_ordinal": [],
            "trial_start_sample": [],
            "opaque_row_id": [],
        }
        targets: list[int] = []
        artifacts: list[int] = []
        artifact_available: list[int] = []
        calibration_structs = 0
        missing_artifact_runs = 0
        for member in members:
            participant = Path(member.relative_path).stem[:3]
            session = Path(member.relative_path).stem[3:]
            if participant not in core.PARTICIPANTS or session not in core.SESSIONS:
                raise core.BNCIStageQRefusal("Stage Q member participant or session differs")
            member_path = repo / core.STAGE_A_BUNDLE_RELATIVE_PATH / member.relative_path
            payload = core._read_exact_member(member_path, member, ancestry_root=repo)
            ledger.MAT_content_opens += 1
            runs, calibration_count = core.parse_verified_mat_payload(payload, member)
            ledger.MAT_semantic_parses += 1
            del payload
            calibration_structs += calibration_count
            for run_ordinal, run in enumerate(runs):
                run_features = core.extract_target_free_run_features(run.signal, run.starts)
                ledger.task_signal_runs_read += 1
                ledger.target_vectors_isolated += 1
                if not run.artifacts_available:
                    missing_artifact_runs += 1
                for name in core.FEATURE_DIMENSIONS:
                    values = run_features[name]
                    if name == "timing_only":
                        values = values.copy()
                        values[:, 0] = float(core.SESSIONS.index(session))
                        values[:, 1] = float(run_ordinal)
                    feature_rows[name].extend(values)
                for trial_ordinal, start in enumerate(run.starts):
                    identity["participant_index"].append(core.PARTICIPANTS.index(participant))
                    identity["session_index"].append(core.SESSIONS.index(session))
                    identity["run_ordinal"].append(run_ordinal)
                    identity["trial_ordinal"].append(trial_ordinal)
                    identity["trial_start_sample"].append(int(start))
                    identity["opaque_row_id"].append(
                        core._row_id(participant, session, run_ordinal, trial_ordinal).encode()
                    )
                targets.extend(int(value) - 1 for value in run.targets)
                artifacts.extend(int(value) for value in run.artifacts)
                artifact_available.extend(
                    [int(run.artifacts_available)] * core.TRIALS_PER_RUN
                )
            _assert_resource_caps(started=started, private_bytes=0)
        if (
            ledger.MAT_content_opens != core.MAT_FILE_COUNT
            or ledger.MAT_semantic_parses != core.MAT_FILE_COUNT
            or ledger.task_signal_runs_read
            != core.MAT_FILE_COUNT * core.TASK_RUNS_PER_FILE
            or len(targets) != core.ROWS_TOTAL
        ):
            raise core.BNCIStageQRefusal("Stage Q aggregate semantic inventory differs")
        derivative_manifest, derivative_bytes = _write_live_derivatives(
            repo,
            temporary,
            feature_rows,
            identity,
            targets,
            artifacts,
            artifact_available,
            key_factory=key_factory,
            scoring_key_path=scoring_key_path,
        )
        runtime, peak_rss = _assert_resource_caps(
            started=started, private_bytes=derivative_bytes
        )
        free_after = shutil.disk_usage(repo).free
        receipt = {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_q_private_receipt",
            "schema_version": core.SCHEMA_VERSION,
            "lane_id": core.LANE_ID,
            "status": "passed_consumed_encrypted_target_firewalled_semantic_qualification",
            "measurements": {
                "input_payload_bytes": sum(member.bytes for member in members),
                "private_derivative_bytes": derivative_bytes,
                "runtime_seconds": runtime,
                "peak_process_RSS_bytes": peak_rss,
                "free_disk_bytes_before": free_before,
                "free_disk_bytes_after": free_after,
                "receipt_bytes": 0,
            },
            "inventory": {
                "MAT_files": core.MAT_FILE_COUNT,
                "task_runs": ledger.task_signal_runs_read,
                "trials": core.ROWS_TOTAL,
                "calibration_structs_recognized": calibration_structs,
                "artifact_flag_unavailable_runs": missing_artifact_runs,
                "channels": len(core.ALL_CHANNELS),
                "EEG_channels": len(core.EEG_CHANNELS),
                "EOG_channels": len(core.EOG_CHANNELS),
                "sampling_rate_hz": core.SAMPLING_RATE_HZ,
                "geometry_available_from_payload": False,
                "folds": derivative_manifest["folds"],
                "source_rows_per_fold": core.SOURCE_ROWS_PER_FOLD,
                "sealed_held_out_E_rows_per_fold": core.HELD_OUT_E_ROWS_PER_FOLD,
                "held_out_T_rows_exposed_per_fold": 0,
            },
            "operations": ledger.__dict__,
            "remote_green_control_plane": remote_proof,
            "versions": versions,
            "resources": {
                "CPU_threads": 1,
                "workers": 1,
                "numerical_jobs": 1,
                "network_bytes": 0,
                "runtime_seconds_maximum": core.RUNTIME_CAP_SECONDS,
                "peak_RSS_bytes_maximum": core.PEAK_RSS_CAP_BYTES,
                "private_derivative_bytes_maximum": core.PRIVATE_OUTPUT_CAP_BYTES,
            },
            "warnings": [
                "payload_geometry_is_unavailable",
                "first_trial_previous_interval_uses_exact_zero_sentinel",
                "artifact_flags_and_availability_are_sealed_and_never_used_for_primary_exclusion",
                "held_out_scoring_keys_are_outside_every_fold_capability",
                "semantic_qualification_is_not_model_training_prediction_scoring_or_a_scientific_result",
            ],
            "rerun_allowed": False,
        }
        for _ in range(8):
            receipt_payload = core._canonical_bytes(receipt)
            if receipt["measurements"]["receipt_bytes"] == len(receipt_payload):
                break
            receipt["measurements"]["receipt_bytes"] = len(receipt_payload)
        else:
            raise core.BNCIStageQRefusal("Stage Q receipt byte count did not stabilize")
        if len(receipt_payload) > core.PUBLIC_OUTPUT_CAP_BYTES:
            raise core.BNCIStageQRefusal("Stage Q private receipt exceeds cap")
        temporary_receipt = temporary / receipt_path.relative_to(output)
        _exclusive_write(repo, temporary_receipt, receipt_payload)
        _assert_resource_caps(
            started=started,
            private_bytes=derivative_bytes + len(receipt_payload) + len(marker_payload),
        )
        temporary.rename(output)
        return receipt
    except Exception:
        if temporary.exists() and temporary.is_dir() and not temporary.is_symlink():
            shutil.rmtree(temporary)
        if scoring_key_path.exists() and not output.exists():
            os.unlink(scoring_key_path)
        raise


def execute_registered_stage_q_live(
    root: str | Path,
    *,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Run the public fixed live path with fresh proof and secure sealing keys."""

    remote_proof = collect_remote_green_proof(root)
    return _execute_registered_stage_q_live(
        root,
        environ=environ,
        remote_green_proof=remote_proof,
        key_factory=secrets.token_bytes,
    )
