"""Fail-closed live wrapper for the one-file DREYER-C5R-1 Stage H preflight."""

from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import math
import os
import resource
import shutil
import ssl
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

from neurodecodekit.datasets import dreyer_c5r_1_stage_h as stage_h
from neurodecodekit.datasets.dreyer_c5r_1 import EDFHeaderSummary, build_generated_edf_header
from neurodecodekit.experiments import dreyer_c5r_1 as parent

SCHEMA_VERSION = "0.1.0"
LANE_ID = "DREYER-C5R-1-HL"
DECISION_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_live_preflight_decision.v0.json"
)
DECISION_SHA256 = "b303af79271edff8dd3309a9546d8a66b7b08e21a4f6a4477439b0ff87f6aa55"
GREEN_DECISION_COMMIT = "de6cf80f4bd243e7e60a6933445d0a65291abb90"
GREEN_DECISION_CI_RUN_ID = 33_230_243_142
GREEN_DECISION_BASE_JOB_ID = 99_041_680_696
GREEN_DECISION_OPTIONAL_JOB_ID = 99_041_680_703
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_live_implementation.v0.json"
)
ACTIVATION_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_live_activation.v0.json"
)
PUBLIC_RESULT_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_live_preflight_result.v0.json"
)
PRIVATE_ROOT_RELATIVE_PATH = Path(".codex_work/dreyer_c5r_1_stage_h_live/v0")
CONSUMED_MARKER_NAME = "execution_consumed.v0.json"
STAGING_DIRECTORY_NAME = "staging-invocation-0001"
STAGING_PAYLOAD_NAME = "verified-payload.edf"
PRIVATE_PAYLOAD_NAME = "sub-01_task-R1acquisition_eeg.edf"
THREAD_ENV_KEYS = parent.THREAD_ENVIRONMENT
MAX_RUNTIME_SECONDS = 300.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_NETWORK_BODY_BYTES = 16 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 32 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MAX_STREAM_CHUNK_BYTES = 1024**2
MINIMUM_FREE_DISK_BYTES = 10 * 1024**3
FROZEN_STAGE_H_ARTIFACTS = (
    (
        Path("src/neurodecodekit/datasets/dreyer_c5r_1_stage_h.py"),
        "02c1726aaa1611ca4ca9de0db376881532123007e8fa4aa4e2c28ce6614ed20a",
    ),
    (
        Path("src/neurodecodekit/dreyer_c5r_1_stage_h_cli.py"),
        "0c1db3b4f449e14d2f7ca43fc75554027bc263a1c7e259746093fd588a2301a9",
    ),
    (
        Path("tests/test_dreyer_c5r_1_stage_h_preflight.py"),
        "fd562952520eaee2b9b35b86173f86169ec7d63fb70cb9c76c569b1e5cd120c7",
    ),
)
REFUSAL_CODES = (
    "HL1-PROOF",
    "HL1-PATH",
    "HL1-MARKER",
    "HL1-TRANSPORT",
    "HL1-PAYLOAD",
    "HL1-HEADER",
    "HL1-RESOURCE",
    "HL1-PUBLICATION",
)
_PARSER_CAPTURE_LOCK = threading.Lock()


class StageHLiveRefusal(RuntimeError):
    """Sanitized fail-closed refusal for the Stage H live shell."""

    def __init__(self, code: str, message: str) -> None:
        if code not in REFUSAL_CODES:
            code = "HL1-PROOF"
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class LiveEvidence:
    """Externally observed activation identity supplied to the one-shot executor."""

    activation_sha256: str
    activation_commit: str
    activation_ci_run_id: int
    activation_base_job_id: int
    activation_optional_job_id: int
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class MachineSnapshot:
    """Bounded computer measurements captured before consumption."""

    free_disk_bytes: int
    peak_rss_bytes: int
    monotonic_started: float


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _GeneratedHeaders:
    def __init__(self, values: Sequence[tuple[str, str]]) -> None:
        self._values = tuple((str(name), str(value)) for name, value in values)

    def get_all(self, name: str) -> list[str] | None:
        values = [value for key, value in self._values if key.casefold() == name.casefold()]
        return values or None

    def raw_items(self) -> list[tuple[str, str]]:
        return list(self._values)


class GeneratedResponse:
    """Closable generated response used by the registered H-L1 qualification."""

    def __init__(
        self,
        body: bytes,
        *,
        url: str,
        status: int = 200,
        headers: Sequence[tuple[str, str]] | None = None,
        maximum_read_bytes: int | None = None,
        nonbytes_first_read: bool = False,
    ) -> None:
        self.status = status
        self.headers = _GeneratedHeaders(
            headers if headers is not None else (("Content-Length", str(len(body))),)
        )
        self._body = body
        self._url = url
        self._offset = 0
        self._maximum_read_bytes = maximum_read_bytes
        self._nonbytes_first_read = nonbytes_first_read
        self._read_calls = 0
        self.closed = False

    def geturl(self) -> str:
        return self._url

    def read(self, size: int) -> bytes | str:
        self._read_calls += 1
        if self._nonbytes_first_read and self._read_calls == 1:
            return "not-bytes"
        amount = size
        if self._maximum_read_bytes is not None:
            amount = min(amount, self._maximum_read_bytes)
        chunk = self._body[self._offset : self._offset + amount]
        self._offset += len(chunk)
        return chunk

    def close(self) -> None:
        self.closed = True


class GeneratedOpenerFactory:
    """Single-response opener factory with observable construction ordering."""

    def __init__(self, response: GeneratedResponse, events: list[str] | None = None) -> None:
        self.response = response
        self.events = events if events is not None else []
        self.constructions = 0
        self.requests = 0

    def __call__(self) -> Callable[[urllib.request.Request, float], BinaryIO]:
        self.constructions += 1
        self.events.append("opener_constructed")

        def open_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
            if timeout <= 0:
                raise StageHLiveRefusal("HL1-TRANSPORT", "timeout differs")
            self.requests += 1
            self.events.append("request_opened")
            return self.response  # type: ignore[return-value]

        return open_once


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            while chunk := os.read(descriptor, 64 * 1024):
                digest.update(chunk)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PROOF", "tracked artifact read failed") from exc
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _strict_json(payload: bytes) -> Any:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ValueError("JSON encoding differs")
    text = payload.decode("utf-8", errors="strict")
    return json.loads(
        text,
        object_pairs_hook=_strict_object,
        parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite JSON")),
    )


def _read_bound_json(path: Path, expected_sha256: str, maximum_bytes: int = 1024**2) -> dict[str, Any]:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PROOF", "bound proof is unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise StageHLiveRefusal("HL1-PROOF", "bound proof type differs")
    if info.st_size > maximum_bytes or _sha256_file(path) != expected_sha256:
        raise StageHLiveRefusal("HL1-PROOF", "bound proof identity differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            payload = os.read(descriptor, maximum_bytes + 1)
        finally:
            os.close(descriptor)
        value = _strict_json(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise StageHLiveRefusal("HL1-PROOF", "bound proof parse failed") from exc
    if not isinstance(value, dict):
        raise StageHLiveRefusal("HL1-PROOF", "bound proof root differs")
    return value


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact packet-bound decision after its remote-green barrier."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _read_bound_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    authorization = decision.get("authorization", {})
    proof = decision.get("green_request_proof", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.dreyer_c5r_1_stage_h_live_preflight_decision"
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("packet_id") != LANE_ID
        or decision.get("maintainer_words") != "continue, make a deep push"
        or decision.get("effective_only_after_decision_commit_pushed_and_both_CI_jobs_green")
        is not True
        or proof.get("commit") != "821fad17e06914375c50a7d0dd7017458b2df838"
        or proof.get("CI_run_id") != 32_936_247_679
        or proof.get("both_required_jobs_green") is not True
        or authorization.get("implement_HL1_additive_standard_library_wrapper_after_decision_green")
        is not True
        or authorization.get("run_HL1_registered_generated_mock_qualification_maximum") != 1
        or authorization.get("HL2_registered_invocations_maximum") != 1
        or authorization.get("HL2_real_HTTP_GET_requests_exact") != 1
        or authorization.get("HL2_successful_payload_body_bytes_exact")
        != stage_h.PREFLIGHT_BYTES
        or authorization.get("remaining_119_payload_requests") != 0
        or authorization.get("annotation_record_reads") != 0
        or authorization.get("signal_sample_semantic_reads") != 0
        or authorization.get("target_or_label_reads") != 0
        or authorization.get("training_runs") != 0
        or authorization.get("model_inference_runs") != 0
        or authorization.get("scores") != 0
        or authorization.get("reruns") != 0
    ):
        raise StageHLiveRefusal("HL1-PROOF", "green decision scope differs")
    for path, digest in FROZEN_STAGE_H_ARTIFACTS:
        if _sha256_file(root / path) != digest:
            raise StageHLiveRefusal("HL1-PROOF", "qualified Stage H artifact changed")
    stage_h.load_contract(root)
    return decision


def load_implementation_record(
    repo_root: str | Path,
    *,
    expected_sha256: str,
) -> dict[str, Any]:
    """Validate the generated-qualified H-L1 implementation record."""

    if len(expected_sha256) != 64:
        raise StageHLiveRefusal("HL1-PROOF", "implementation digest is malformed")
    root = Path(repo_root)
    record = _read_bound_json(
        root / IMPLEMENTATION_RELATIVE_PATH,
        expected_sha256,
    )
    if (
        record.get("schema_name")
        != "neurodecodekit.dreyer_c5r_1_stage_h_live_implementation"
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("lane_id") != LANE_ID
        or record.get("status")
        != "generated_mock_wrapper_qualified_remote_green_required_before_activation"
        or record.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or record.get("green_decision", {}).get("CI_run_id")
        != GREEN_DECISION_CI_RUN_ID
        or record.get("generated_qualification", {}).get("all_gates_passed") is not True
        or record.get("execution_state", {}).get("real_invocation_consumed") is not False
        or any(record.get("implementation_access_counters", {}).values())
    ):
        raise StageHLiveRefusal("HL1-PROOF", "implementation record differs")
    for binding in record.get("tracked_file_hashes", ()):
        relative = str(binding.get("path", ""))
        digest = str(binding.get("sha256", ""))
        if (
            not relative
            or relative.startswith(("/", "~"))
            or ".." in Path(relative).parts
            or len(digest) != 64
            or _sha256_file(root / relative) != digest
        ):
            raise StageHLiveRefusal("HL1-PROOF", "implementation binding differs")
    return record


def load_activation(
    repo_root: str | Path,
    evidence: LiveEvidence,
) -> dict[str, Any]:
    """Load the separately green activation that exposes the one live invocation."""

    if (
        len(evidence.activation_sha256) != 64
        or len(evidence.activation_commit) != 40
        or min(
            evidence.activation_ci_run_id,
            evidence.activation_base_job_id,
            evidence.activation_optional_job_id,
        )
        <= 0
        or evidence.registered_execution_ordinal != 1
    ):
        raise StageHLiveRefusal("HL1-PROOF", "activation evidence is malformed")
    root = Path(repo_root)
    activation = _read_bound_json(
        root / ACTIVATION_RELATIVE_PATH,
        evidence.activation_sha256,
    )
    implementation = activation.get("green_implementation", {})
    if (
        activation.get("schema_name")
        != "neurodecodekit.dreyer_c5r_1_stage_h_live_activation"
        or activation.get("schema_version") != SCHEMA_VERSION
        or activation.get("lane_id") != LANE_ID
        or activation.get("status") != "one_live_preflight_active_after_activation_remote_green"
        or activation.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or activation.get("green_decision", {}).get("CI_run_id")
        != GREEN_DECISION_CI_RUN_ID
        or implementation.get("both_required_jobs_green") is not True
        or activation.get("authority", {}).get("registered_invocations") != 1
        or activation.get("authority", {}).get("real_HTTP_GET_requests") != 1
        or activation.get("authority", {}).get("successful_body_bytes")
        != stage_h.PREFLIGHT_BYTES
        or activation.get("authority", {}).get("remaining_119_requests") != 0
        or activation.get("authority", {}).get("reruns") != 0
    ):
        raise StageHLiveRefusal("HL1-PROOF", "activation scope differs")
    load_implementation_record(
        root,
        expected_sha256=str(implementation.get("registry_sha256", "")),
    )
    return activation


def _run_command(root: Path, args: Sequence[str], timeout: float = 30.0) -> str:
    try:
        completed = subprocess.run(
            tuple(args),
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StageHLiveRefusal("HL1-PROOF", "remote proof command failed") from exc
    if completed.returncode or not completed.stdout.strip():
        raise StageHLiveRefusal("HL1-PROOF", "remote proof command refused")
    return completed.stdout.strip()


def collect_remote_green_proof(
    repo_root: str | Path,
    activation: Mapping[str, Any],
    evidence: LiveEvidence,
) -> dict[str, Any]:
    """Collect fresh main-head and GitHub Actions proof before live capability."""

    root = Path(repo_root)
    remote = _run_command(root, ("git", "ls-remote", "--heads", "origin", "refs/heads/main"))
    fields = remote.split()
    if len(fields) != 2 or fields[1] != "refs/heads/main":
        raise StageHLiveRefusal("HL1-PROOF", "remote main proof is ambiguous")
    runs = (
        (
            GREEN_DECISION_COMMIT,
            GREEN_DECISION_CI_RUN_ID,
            GREEN_DECISION_BASE_JOB_ID,
            GREEN_DECISION_OPTIONAL_JOB_ID,
        ),
        (
            str(activation["green_implementation"]["commit"]),
            int(activation["green_implementation"]["CI_run_id"]),
            int(activation["green_implementation"]["base_python_job_id"]),
            int(activation["green_implementation"]["optional_neuro_readers_job_id"]),
        ),
        (
            evidence.activation_commit,
            evidence.activation_ci_run_id,
            evidence.activation_base_job_id,
            evidence.activation_optional_job_id,
        ),
    )
    observed_runs: list[dict[str, Any]] = []
    for commit, run_id, base_job_id, optional_job_id in runs:
        output = _run_command(
            root,
            (
                "gh",
                "run",
                "view",
                str(run_id),
                "--json",
                "conclusion,headSha,jobs,status",
            ),
        )
        try:
            value = json.loads(output)
        except json.JSONDecodeError as exc:
            raise StageHLiveRefusal("HL1-PROOF", "remote CI proof is malformed") from exc
        jobs = {int(job.get("databaseId", 0)): job for job in value.get("jobs", ())}
        if (
            value.get("status") != "completed"
            or value.get("conclusion") != "success"
            or value.get("headSha") != commit
            or jobs.get(base_job_id, {}).get("name") != "Base Python"
            or jobs.get(base_job_id, {}).get("conclusion") != "success"
            or jobs.get(optional_job_id, {}).get("name") != "Optional Neuro Readers"
            or jobs.get(optional_job_id, {}).get("conclusion") != "success"
        ):
            raise StageHLiveRefusal("HL1-PROOF", "remote CI proof differs")
        observed_runs.append(
            {
                "commit": commit,
                "CI_run_id": run_id,
                "base_python_job_id": base_job_id,
                "optional_neuro_readers_job_id": optional_job_id,
                "both_required_jobs_green": True,
            }
        )
    return {
        "remote_main_commit": fields[0],
        "activation_is_remote_main": fields[0] == evidence.activation_commit,
        "runs": observed_runs,
        "fresh_git_remote_calls": 1,
        "fresh_GitHub_Actions_calls": 3,
    }


def validate_remote_green_proof(
    proof: Mapping[str, Any],
    activation: Mapping[str, Any],
    evidence: LiveEvidence,
) -> None:
    """Validate exact decision, implementation, and activation remote proof."""

    implementation = activation.get("green_implementation", {})
    expected = (
        (
            GREEN_DECISION_COMMIT,
            GREEN_DECISION_CI_RUN_ID,
            GREEN_DECISION_BASE_JOB_ID,
            GREEN_DECISION_OPTIONAL_JOB_ID,
        ),
        (
            implementation.get("commit"),
            implementation.get("CI_run_id"),
            implementation.get("base_python_job_id"),
            implementation.get("optional_neuro_readers_job_id"),
        ),
        (
            evidence.activation_commit,
            evidence.activation_ci_run_id,
            evidence.activation_base_job_id,
            evidence.activation_optional_job_id,
        ),
    )
    runs = proof.get("runs")
    if (
        proof.get("remote_main_commit") != evidence.activation_commit
        or proof.get("activation_is_remote_main") is not True
        or proof.get("fresh_git_remote_calls") != 1
        or proof.get("fresh_GitHub_Actions_calls") != 3
        or not isinstance(runs, list)
        or len(runs) != 3
    ):
        raise StageHLiveRefusal("HL1-PROOF", "remote green proof differs")
    for observed, wanted in zip(runs, expected, strict=True):
        commit, run_id, base_job_id, optional_job_id = wanted
        if (
            observed.get("commit") != commit
            or observed.get("CI_run_id") != run_id
            or observed.get("base_python_job_id") != base_job_id
            or observed.get("optional_neuro_readers_job_id") != optional_job_id
            or observed.get("both_required_jobs_green") is not True
        ):
            raise StageHLiveRefusal("HL1-PROOF", "remote run proof differs")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _ensure_single_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise StageHLiveRefusal("HL1-RESOURCE", "thread environment differs")


def preconsumption_machine_gate(
    workspace: Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    clock: Callable[[], float] = time.monotonic,
) -> MachineSnapshot:
    """Check the bounded machine envelope before writing the consumed marker."""

    _ensure_single_thread_environment(environ)
    try:
        free = int(disk_usage_reader(workspace).free)
        rss = int(rss_reader())
        started = float(clock())
    except Exception as exc:
        raise StageHLiveRefusal("HL1-RESOURCE", "machine metric is unavailable") from exc
    if (
        free < MINIMUM_FREE_DISK_BYTES
        or rss < 0
        or rss > MAX_PEAK_RSS_BYTES
        or not math.isfinite(started)
    ):
        raise StageHLiveRefusal("HL1-RESOURCE", "preconsumption resource gate failed")
    return MachineSnapshot(free_disk_bytes=free, peak_rss_bytes=rss, monotonic_started=started)


def _lstat_directory(path: Path, code: str = "HL1-PATH") -> os.stat_result:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise StageHLiveRefusal(code, "directory capability is unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise StageHLiveRefusal(code, "directory capability type differs")
    return info


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PATH", "directory durability failed") from exc


def _create_private_chain(workspace: Path) -> Path:
    if not workspace.is_absolute() or ".." in workspace.parts:
        raise StageHLiveRefusal("HL1-PATH", "workspace identity differs")
    _lstat_directory(workspace)
    current = workspace
    for part in PRIVATE_ROOT_RELATIVE_PATH.parts:
        candidate = current / part
        try:
            info = os.lstat(candidate)
        except FileNotFoundError:
            try:
                os.mkdir(candidate, 0o700)
                _fsync_directory(current)
                info = os.lstat(candidate)
            except OSError as exc:
                raise StageHLiveRefusal("HL1-PATH", "private directory creation failed") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise StageHLiveRefusal("HL1-PATH", "private path component differs")
        current = candidate
    return current


def _write_exclusive_durable(path: Path, payload: bytes, *, mode: int) -> None:
    _lstat_directory(path.parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        try:
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise OSError("write made no progress")
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        _fsync_directory(path.parent)
    except FileExistsError as exc:
        raise StageHLiveRefusal("HL1-MARKER", "exclusive file already exists") from exc
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PUBLICATION", "exclusive durable write failed") from exc


def _write_consumed_marker(
    private_root: Path,
    evidence: LiveEvidence,
    *,
    events: list[str] | None = None,
) -> tuple[Path, int]:
    marker = {
        "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_live_consumed",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "activation_commit": evidence.activation_commit,
        "activation_sha256": evidence.activation_sha256,
        "registered_execution_ordinal": 1,
        "retry_allowed": False,
        "rerun_allowed": False,
        "remaining_119_payloads_allowed": False,
        "annotation_signal_target_model_or_score_access_allowed": False,
    }
    payload = _canonical_json_bytes(marker)
    path = private_root / CONSUMED_MARKER_NAME
    _write_exclusive_durable(path, payload, mode=0o600)
    if events is not None:
        events.append("marker_durable")
    return path, len(payload)


def _make_exclusive_directory(path: Path) -> None:
    _lstat_directory(path.parent)
    try:
        os.mkdir(path, 0o700)
        _fsync_directory(path.parent)
    except FileExistsError as exc:
        raise StageHLiveRefusal("HL1-PATH", "staging directory already exists") from exc
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PATH", "staging directory creation failed") from exc


def _allocated_tree_bytes(root: Path) -> int:
    total = 0
    try:
        root_info = os.lstat(root)
        if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
            raise OSError("root differs")
        for entry in os.scandir(root):
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise OSError("symlink differs")
            if stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1:
                    raise OSError("hard link differs")
                total += int(getattr(info, "st_blocks", 0)) * 512 or info.st_size
            elif stat.S_ISDIR(info.st_mode):
                total += _allocated_tree_bytes(Path(entry.path))
            else:
                raise OSError("path type differs")
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PATH", "private allocation walk failed") from exc
    return total


def _enforce_live_resources(
    private_root: Path,
    snapshot: MachineSnapshot,
    *,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    disk_usage_reader: Callable[[Path], Any],
) -> dict[str, Any]:
    try:
        runtime = float(clock()) - snapshot.monotonic_started
        peak_rss = int(rss_reader())
        free = int(disk_usage_reader(private_root).free)
        allocated = _allocated_tree_bytes(private_root)
    except StageHLiveRefusal:
        raise
    except Exception as exc:
        raise StageHLiveRefusal("HL1-RESOURCE", "live resource metric failed") from exc
    if (
        not math.isfinite(runtime)
        or runtime < 0
        or runtime > MAX_RUNTIME_SECONDS
        or peak_rss < 0
        or peak_rss > MAX_PEAK_RSS_BYTES
        or free < MINIMUM_FREE_DISK_BYTES
        or allocated > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise StageHLiveRefusal("HL1-RESOURCE", "live resource cap exceeded")
    return {
        "runtime_seconds": runtime,
        "peak_process_RSS_bytes": peak_rss,
        "free_disk_bytes": free,
        "private_allocated_bytes": allocated,
    }


def _critical_headers(response: Any) -> dict[str, str]:
    headers = getattr(response, "headers", None)
    if headers is None:
        raise StageHLiveRefusal("HL1-TRANSPORT", "response headers are unavailable")
    items = headers.raw_items() if hasattr(headers, "raw_items") else headers.items()
    critical = {"content-length", "content-encoding", "transfer-encoding", "location"}
    result: dict[str, str] = {}
    for raw_name, raw_value in items:
        name = str(raw_name).strip().casefold()
        value = str(raw_value).strip()
        if not name or "\r" in value or "\n" in value:
            raise StageHLiveRefusal("HL1-TRANSPORT", "response header differs")
        if name not in critical:
            continue
        if name in result:
            raise StageHLiveRefusal("HL1-TRANSPORT", "critical response header is duplicated")
        result[name] = value
    if set(result) != {"content-length"} or result["content-length"] != str(
        stage_h.PREFLIGHT_BYTES
    ):
        raise StageHLiveRefusal("HL1-TRANSPORT", "exact response headers differ")
    return result


class _MonitoredResponse:
    def __init__(
        self,
        response: BinaryIO,
        private_root: Path,
        snapshot: MachineSnapshot,
        *,
        clock: Callable[[], float],
        rss_reader: Callable[[], int],
        disk_usage_reader: Callable[[Path], Any],
    ) -> None:
        self._response = response
        self._private_root = private_root
        self._snapshot = snapshot
        self._clock = clock
        self._rss_reader = rss_reader
        self._disk_usage_reader = disk_usage_reader
        self.status = getattr(response, "status", None)
        self.headers = getattr(response, "headers", None)
        self.body_bytes = 0
        self.read_calls = 0

    def geturl(self) -> str:
        getter = getattr(self._response, "geturl", None)
        if not callable(getter):
            raise StageHLiveRefusal("HL1-TRANSPORT", "response URL is unavailable")
        value = getter()
        if not isinstance(value, str):
            raise StageHLiveRefusal("HL1-TRANSPORT", "response URL differs")
        return value

    def read(self, size: int) -> bytes:
        if type(size) is not int or size < 0 or size > MAX_STREAM_CHUNK_BYTES:
            raise StageHLiveRefusal("HL1-RESOURCE", "response chunk request exceeded cap")
        _enforce_live_resources(
            self._private_root,
            self._snapshot,
            clock=self._clock,
            rss_reader=self._rss_reader,
            disk_usage_reader=self._disk_usage_reader,
        )
        try:
            chunk = self._response.read(size)
        except Exception as exc:
            raise StageHLiveRefusal("HL1-TRANSPORT", "response body read failed") from exc
        if type(chunk) is not bytes:
            raise StageHLiveRefusal("HL1-PAYLOAD", "response body chunk type differs")
        self.read_calls += 1
        self.body_bytes += len(chunk)
        if self.body_bytes > MAX_NETWORK_BODY_BYTES:
            raise StageHLiveRefusal("HL1-RESOURCE", "network body cap exceeded")
        _enforce_live_resources(
            self._private_root,
            self._snapshot,
            clock=self._clock,
            rss_reader=self._rss_reader,
            disk_usage_reader=self._disk_usage_reader,
        )
        return chunk


def _request_headers(request: urllib.request.Request) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_name, raw_value in request.header_items():
        name = raw_name.strip().casefold()
        value = raw_value.strip()
        if not name or name in values or "\r" in value or "\n" in value:
            raise StageHLiveRefusal("HL1-TRANSPORT", "request header differs")
        values[name] = value
    return values


def _build_request() -> urllib.request.Request:
    request = urllib.request.Request(
        stage_h.PREFLIGHT_URL,
        headers={
            "Accept-Encoding": "identity",
            "User-Agent": "NeuroDecodeKit-DREYER-C5R-1-HL/0.1",
        },
        method="GET",
    )
    if (
        request.get_method() != "GET"
        or request.full_url != stage_h.PREFLIGHT_URL
        or _request_headers(request)
        != {
            "accept-encoding": "identity",
            "user-agent": "NeuroDecodeKit-DREYER-C5R-1-HL/0.1",
        }
    ):
        raise StageHLiveRefusal("HL1-TRANSPORT", "exact request differs")
    return request


def build_live_opener() -> Callable[[urllib.request.Request, float], BinaryIO]:
    """Construct the proxy-free verified-TLS no-redirect opener."""

    context = ssl.create_default_context()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        _NoRedirect,
        urllib.request.HTTPSHandler(context=context),
    )

    def open_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
        try:
            return opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            return exc
        except Exception as exc:
            raise StageHLiveRefusal("HL1-TRANSPORT", "direct HTTPS request failed") from exc

    return open_once


def _stream_with_single_summary(
    response: _MonitoredResponse,
    destination: Path,
) -> tuple[dict[str, Any], EDFHeaderSummary]:
    """Reuse Stage H unchanged while capturing its sole parser return value."""

    captured: list[EDFHeaderSummary] = []
    original = stage_h.parse_edf_fixed_header

    def capture(payload: bytes) -> EDFHeaderSummary:
        summary = original(payload)
        captured.append(summary)
        return summary

    with _PARSER_CAPTURE_LOCK:
        stage_h.parse_edf_fixed_header = capture
        try:
            result = stage_h.stream_verified_preflight(
                response,
                stage_h.REGISTERED_SPEC,
                destination,
            )
        except stage_h.StageHRefusal as exc:
            raise StageHLiveRefusal("HL1-PAYLOAD", "qualified verifier refused") from exc
        finally:
            stage_h.parse_edf_fixed_header = original
    if len(captured) != 1:
        raise StageHLiveRefusal("HL1-HEADER", "fixed-header parse count differs")
    return result, captured[0]


def _validate_payload_geometry(summary: EDFHeaderSummary) -> int:
    total = summary.header_bytes + summary.record_count * 2 * sum(
        summary.samples_per_record
    )
    if total != stage_h.PREFLIGHT_BYTES:
        raise StageHLiveRefusal("HL1-HEADER", "fixed-header payload geometry differs")
    return total


def _atomic_no_replace(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise StageHLiveRefusal("HL1-PUBLICATION", "private payload destination exists")
    libc = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    result: int
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        function = libc.renamex_np
        function.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        function.restype = ctypes.c_int
        result = int(function(source_bytes, destination_bytes, 0x00000004))
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        function = libc.renameat2
        function.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        function.restype = ctypes.c_int
        result = int(function(-100, source_bytes, -100, destination_bytes, 0x00000001))
    else:
        raise StageHLiveRefusal("HL1-PUBLICATION", "atomic no-replace rename unavailable")
    if result != 0:
        observed_errno = ctypes.get_errno()
        if observed_errno in {errno.EEXIST, errno.ENOTEMPTY}:
            raise StageHLiveRefusal("HL1-PUBLICATION", "private payload destination raced")
        raise StageHLiveRefusal("HL1-PUBLICATION", "atomic no-replace rename failed")
    _fsync_directory(destination.parent)


def _cleanup_owned_staging(staging: Path) -> None:
    try:
        info = os.lstat(staging)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PATH", "staging cleanup inspection failed") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise StageHLiveRefusal("HL1-PATH", "staging cleanup capability differs")
    entries = list(os.scandir(staging))
    for entry in entries:
        child = Path(entry.path)
        child_info = entry.stat(follow_symlinks=False)
        if (
            stat.S_ISLNK(child_info.st_mode)
            or not stat.S_ISREG(child_info.st_mode)
            or child_info.st_nlink != 1
        ):
            raise StageHLiveRefusal("HL1-PATH", "staging cleanup member differs")
        child.unlink()
    try:
        os.rmdir(staging)
        _fsync_directory(staging.parent)
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PATH", "staging cleanup failed") from exc


def _base_operation_counters() -> dict[str, int]:
    return {
        "real_HTTP_GET_requests": 0,
        "real_response_opens": 0,
        "real_network_body_bytes": 0,
        "real_payload_SHA256_passes": 0,
        "real_fixed_header_reads": 0,
        "real_fixed_header_semantic_parses": 0,
        "real_annotation_reads": 0,
        "real_signal_sample_reads": 0,
        "real_target_or_label_reads": 0,
        "remaining_119_payload_requests": 0,
        "model_or_checkpoint_opens": 0,
        "training_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scores": 0,
        "retries": 0,
        "reruns": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _public_report(
    *,
    route: str,
    refusal_code: str | None,
    sensor_contract: Mapping[str, Any] | None,
    resources: Mapping[str, Any],
    counters: Mapping[str, int],
    marker_bytes: int,
    payload_retained: bool,
    remote_proof: Mapping[str, Any],
    generated_only: bool,
) -> dict[str, Any]:
    if route not in {"DREYER-H1", "DREYER-H0"}:
        raise StageHLiveRefusal("HL1-PUBLICATION", "public route differs")
    report = {
        "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_live_preflight_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "passed_fixed_header_contract" if route == "DREYER-H1" else "parked",
        "route": route,
        "refusal_code": refusal_code,
        "object": {
            "dataset": "Dreyer_et_al_2023_Dataset_A",
            "NEMAR_dataset": "nm000250",
            "revision": "v1.0.4",
            "path": stage_h.PREFLIGHT_PATH,
            "bytes": stage_h.PREFLIGHT_BYTES,
            "sha256": stage_h.PREFLIGHT_SHA256,
        },
        "sensor_contract": dict(sensor_contract) if sensor_contract is not None else None,
        "payload_retained_private": payload_retained,
        "resources": {
            **dict(resources),
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 0,
            "marker_bytes": marker_bytes,
            "public_output_bytes": 0,
            "transport_header_bytes": None,
            "TLS_bytes": None,
            "producer_causal": None,
            "required_context_seconds": None,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": dict(counters),
        "remote_proof": {
            "fresh_git_remote_calls": remote_proof.get("fresh_git_remote_calls", 0),
            "fresh_GitHub_Actions_calls": remote_proof.get(
                "fresh_GitHub_Actions_calls", 0
            ),
            "decision_implementation_and_activation_green": True,
        },
        "warnings": [
            "fixed_header_preflight_is_structural_not_a_neural_effect",
            "transport_header_and_TLS_byte_counts_unavailable",
            "annotations_signals_targets_models_and_scores_not_accessed",
            "end_to_end_latency_not_measured",
        ],
        "generated_only": generated_only,
        "claim_boundary": {
            "engineering_capability": "one_exact_payload_identity_and_fixed_sensor_header_preflight",
            "scientific_claim_not_established": "any_EEG_information_EEG_beyond_peripherals_unseen_person_generalization_spontaneous_movement_intention_motor_cortex_causation_thought_or_language_decoding_live_decoding_hardware_or_clinical_result",
        },
    }
    previous = -1
    for _ in range(8):
        payload = _canonical_json_bytes(report)
        report["resources"]["public_output_bytes"] = len(payload)
        if len(payload) == previous:
            break
        previous = len(payload)
    if len(_canonical_json_bytes(report)) > MAX_PUBLIC_OUTPUT_BYTES:
        raise StageHLiveRefusal("HL1-PUBLICATION", "public output cap exceeded")
    _validate_public_report(report)
    return report


def _validate_public_report(report: Mapping[str, Any]) -> None:
    allowed = {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "refusal_code",
        "object",
        "sensor_contract",
        "payload_retained_private",
        "resources",
        "operation_counters",
        "remote_proof",
        "warnings",
        "generated_only",
        "claim_boundary",
    }
    if set(report) != allowed:
        raise StageHLiveRefusal("HL1-PUBLICATION", "public report fields differ")
    forbidden = {
        "patient",
        "recording",
        "date",
        "raw_header",
        "annotation",
        "sample",
        "target",
        "label",
        "private_path",
        "exception",
        "traceback",
        "geometry",
        "reference",
    }

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).casefold() in forbidden:
                    raise StageHLiveRefusal("HL1-PUBLICATION", "forbidden public field")
                walk(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                walk(child)
        elif isinstance(value, float) and not math.isfinite(value):
            raise StageHLiveRefusal("HL1-PUBLICATION", "non-finite public number")

    walk(report)


def _publish_report(path: Path, report: Mapping[str, Any]) -> int:
    payload = _canonical_json_bytes(report)
    if len(payload) > MAX_PUBLIC_OUTPUT_BYTES:
        raise StageHLiveRefusal("HL1-PUBLICATION", "public output cap exceeded")
    _write_exclusive_durable(path, payload, mode=0o644)
    return len(payload)


def _execute_after_proof(
    workspace: Path,
    output_path: Path,
    evidence: LiveEvidence,
    remote_proof: Mapping[str, Any],
    opener_factory: Callable[[], Callable[[urllib.request.Request, float], BinaryIO]],
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    clock: Callable[[], float] = time.monotonic,
    promoter: Callable[[Path, Path], None] = _atomic_no_replace,
    generated_only: bool = False,
    events: list[str] | None = None,
) -> dict[str, Any]:
    snapshot = preconsumption_machine_gate(
        workspace,
        environ=environ,
        disk_usage_reader=disk_usage_reader,
        rss_reader=rss_reader,
        clock=clock,
    )
    private_root = _create_private_chain(workspace)
    if output_path.exists() or output_path.is_symlink():
        raise StageHLiveRefusal("HL1-PUBLICATION", "public result already exists")
    marker_path, marker_bytes = _write_consumed_marker(
        private_root,
        evidence,
        events=events,
    )
    if not marker_path.is_file() or marker_path.is_symlink():
        raise StageHLiveRefusal("HL1-MARKER", "consumed marker durability differs")
    staging = private_root / STAGING_DIRECTORY_NAME
    _make_exclusive_directory(staging)
    final_payload = private_root / PRIVATE_PAYLOAD_NAME
    counters = _base_operation_counters()
    counters["real_HTTP_GET_requests"] = 1 if not generated_only else 0
    opener = opener_factory()
    request = _build_request()
    response: BinaryIO | None = None
    monitored: _MonitoredResponse | None = None
    try:
        try:
            response = opener(request, MAX_RUNTIME_SECONDS)
            counters["real_response_opens"] = 1 if not generated_only else 0
            _critical_headers(response)
            if getattr(response, "status", None) != 200:
                raise StageHLiveRefusal("HL1-TRANSPORT", "HTTP status differs")
            getter = getattr(response, "geturl", None)
            if not callable(getter) or getter() != stage_h.PREFLIGHT_URL:
                raise StageHLiveRefusal("HL1-TRANSPORT", "final URL differs")
            monitored = _MonitoredResponse(
                response,
                private_root,
                snapshot,
                clock=clock,
                rss_reader=rss_reader,
                disk_usage_reader=disk_usage_reader,
            )
            verifier_result, summary = _stream_with_single_summary(
                monitored,
                staging / STAGING_PAYLOAD_NAME,
            )
            _validate_payload_geometry(summary)
            resources = _enforce_live_resources(
                private_root,
                snapshot,
                clock=clock,
                rss_reader=rss_reader,
                disk_usage_reader=disk_usage_reader,
            )
            promoter(staging / STAGING_PAYLOAD_NAME, final_payload)
            _cleanup_owned_staging(staging)
            resources = _enforce_live_resources(
                private_root,
                snapshot,
                clock=clock,
                rss_reader=rss_reader,
                disk_usage_reader=disk_usage_reader,
            )
            if not generated_only:
                counters["real_network_body_bytes"] = monitored.body_bytes
                counters["real_payload_SHA256_passes"] = int(
                    verifier_result["body_hash_passes"]
                )
                counters["real_fixed_header_reads"] = 1
                counters["real_fixed_header_semantic_parses"] = 1
            report = _public_report(
                route="DREYER-H1",
                refusal_code=None,
                sensor_contract=verifier_result["sensor_contract"],
                resources=resources,
                counters=counters,
                marker_bytes=marker_bytes,
                payload_retained=True,
                remote_proof=remote_proof,
                generated_only=generated_only,
            )
        except StageHLiveRefusal as exc:
            resources = _enforce_live_resources(
                private_root,
                snapshot,
                clock=clock,
                rss_reader=rss_reader,
                disk_usage_reader=disk_usage_reader,
            )
            if monitored is not None and not generated_only:
                counters["real_network_body_bytes"] = monitored.body_bytes
            report = _public_report(
                route="DREYER-H0",
                refusal_code=exc.code,
                sensor_contract=None,
                resources=resources,
                counters=counters,
                marker_bytes=marker_bytes,
                payload_retained=False,
                remote_proof=remote_proof,
                generated_only=generated_only,
            )
        finally:
            if response is not None:
                try:
                    response.close()
                except (OSError, ValueError) as exc:
                    raise StageHLiveRefusal(
                        "HL1-TRANSPORT", "response close failed"
                    ) from exc
            _cleanup_owned_staging(staging)
        _publish_report(output_path, report)
        return report
    except Exception:
        _cleanup_owned_staging(staging)
        raise


def execute_registered_preflight(
    evidence: LiveEvidence,
    *,
    repo_root: str | Path | None = None,
    opener_factory: Callable[[], Callable[[urllib.request.Request, float], BinaryIO]] = (
        build_live_opener
    ),
    remote_proof_collector: Callable[
        [str | Path, Mapping[str, Any], LiveEvidence], Mapping[str, Any]
    ] = collect_remote_green_proof,
    environ: Mapping[str, str] | None = None,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    """Execute the separately activated one-shot real fixed-header preflight."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    root = root.expanduser().absolute()
    _lstat_directory(root)
    load_green_decision(root)
    activation = load_activation(root, evidence)
    try:
        head = _run_command(root, ("git", "rev-parse", "HEAD"))
        tracked = subprocess.run(
            ("git", "status", "--porcelain", "--untracked-files=no"),
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise StageHLiveRefusal("HL1-PROOF", "local Git proof failed") from exc
    if head != evidence.activation_commit or tracked.returncode or tracked.stdout.strip():
        raise StageHLiveRefusal("HL1-PROOF", "local activation checkout differs")
    remote_proof = remote_proof_collector(root, activation, evidence)
    validate_remote_green_proof(remote_proof, activation, evidence)
    return _execute_after_proof(
        root,
        root / PUBLIC_RESULT_RELATIVE_PATH,
        evidence,
        remote_proof,
        opener_factory,
        environ=os.environ if environ is None else environ,
        disk_usage_reader=disk_usage_reader,
        rss_reader=rss_reader,
        clock=clock,
        generated_only=False,
    )


def _generated_body(*, wrong_roster: bool = False, wrong_geometry: bool = False) -> bytes:
    labels: Sequence[str] = stage_h.EXPECTED_EEG_LABELS + (
        "EOG-VU",
        "EOG-VD",
        "EOG-H",
        "EMG-LH",
        "EMG-RH",
        "EDF Annotations",
    )
    if wrong_roster:
        labels = tuple(labels[:-2]) + ("MYSTERY", "EDF Annotations")
    header = build_generated_edf_header(labels, record_count=1)
    samples = len(labels) * 512
    suffix_bytes = samples * 2 + (2 if wrong_geometry else 0)
    suffix = bytes((index * 17 + 29) % 256 for index in range(suffix_bytes))
    return header + suffix


def _generated_remote_proof() -> dict[str, Any]:
    return {
        "remote_main_commit": "a" * 40,
        "activation_is_remote_main": True,
        "runs": [],
        "fresh_git_remote_calls": 0,
        "fresh_GitHub_Actions_calls": 0,
    }


def _generated_evidence() -> LiveEvidence:
    return LiveEvidence(
        activation_sha256="b" * 64,
        activation_commit="a" * 40,
        activation_ci_run_id=1,
        activation_base_job_id=2,
        activation_optional_job_id=3,
    )


def _generated_environment() -> dict[str, str]:
    return {key: "1" for key in THREAD_ENV_KEYS}


def _generated_disk_usage(_path: Path) -> Any:
    return type("Usage", (), {"free": MINIMUM_FREE_DISK_BYTES + 1024**3})()


def _run_generated_valid_case(root: Path, name: str) -> tuple[dict[str, Any], GeneratedOpenerFactory, list[str]]:
    body = _generated_body()
    response = GeneratedResponse(
        body,
        url=stage_h.PREFLIGHT_URL,
        maximum_read_bytes=97,
    )
    events: list[str] = []
    opener = GeneratedOpenerFactory(response, events)
    original_spec = stage_h.REGISTERED_SPEC
    stage_h.REGISTERED_SPEC = stage_h.PreflightSpec(
        stage_h.PREFLIGHT_URL,
        stage_h.PREFLIGHT_PATH,
        len(body),
        _sha256_bytes(body),
    )
    original_bytes = stage_h.PREFLIGHT_BYTES
    original_sha = stage_h.PREFLIGHT_SHA256
    stage_h.PREFLIGHT_BYTES = len(body)
    stage_h.PREFLIGHT_SHA256 = _sha256_bytes(body)
    try:
        report = _execute_after_proof(
            root,
            root / f"{name}.json",
            _generated_evidence(),
            _generated_remote_proof(),
            opener,
            environ=_generated_environment(),
            disk_usage_reader=_generated_disk_usage,
            rss_reader=lambda: 16 * 1024**2,
            generated_only=True,
            events=events,
        )
    finally:
        stage_h.REGISTERED_SPEC = original_spec
        stage_h.PREFLIGHT_BYTES = original_bytes
        stage_h.PREFLIGHT_SHA256 = original_sha
    return report, opener, events


def _expect_generated_refusal(name: str, operation: Callable[[], Any]) -> str:
    try:
        operation()
    except StageHLiveRefusal as exc:
        return exc.code
    raise StageHLiveRefusal("HL1-PROOF", f"generated mutation did not refuse: {name}")


def run_generated_qualification(output_path: str | Path) -> dict[str, Any]:
    """Run the sole generated/mock H-L1 wrapper qualification."""

    load_green_decision()
    _ensure_single_thread_environment(os.environ)
    started = time.monotonic()
    peak_before = _peak_rss_bytes()
    mutation_routes: dict[str, str] = {}
    generated_bytes = 0
    with tempfile.TemporaryDirectory(prefix="neurodecodekit-dreyer-hl1-") as name:
        root = Path(name).absolute()
        os.mkdir(root / ".codex_work", 0o700)
        first, first_opener, first_events = _run_generated_valid_case(root, "valid-first")
        generated_bytes += len(_generated_body())
        replay_root = root / "replay"
        os.mkdir(replay_root, 0o700)
        os.mkdir(replay_root / ".codex_work", 0o700)
        replay, replay_opener, replay_events = _run_generated_valid_case(
            replay_root, "valid-replay"
        )
        generated_bytes += len(_generated_body())
        if (
            first["route"] != "DREYER-H1"
            or replay["route"] != "DREYER-H1"
            or first["sensor_contract"] != replay["sensor_contract"]
            or first_events[:2] != ["marker_durable", "opener_constructed"]
            or replay_events[:2] != ["marker_durable", "opener_constructed"]
            or first_opener.constructions != 1
            or first_opener.requests != 1
            or replay_opener.constructions != 1
            or replay_opener.requests != 1
            or not first_opener.response.closed
            or not replay_opener.response.closed
        ):
            raise StageHLiveRefusal("HL1-PROOF", "generated deterministic replay failed")

        rerun_root = root / "rerun"
        os.mkdir(rerun_root, 0o700)
        os.mkdir(rerun_root / ".codex_work", 0o700)
        _run_generated_valid_case(rerun_root, "first")
        mutation_routes["consumed_rerun"] = _expect_generated_refusal(
            "consumed_rerun",
            lambda: _run_generated_valid_case(rerun_root, "second"),
        )

        symlink_root = root / "symlink-root"
        os.mkdir(symlink_root, 0o700)
        os.symlink(root / ".codex_work", symlink_root / ".codex_work")
        mutation_routes["symlinked_private_root"] = _expect_generated_refusal(
            "symlinked_private_root",
            lambda: _create_private_chain(symlink_root),
        )

        mutation_routes["low_free_disk"] = _expect_generated_refusal(
            "low_free_disk",
            lambda: preconsumption_machine_gate(
                root,
                environ=_generated_environment(),
                disk_usage_reader=lambda _path: type(
                    "Usage", (), {"free": MINIMUM_FREE_DISK_BYTES - 1}
                )(),
                rss_reader=lambda: 1,
            ),
        )
        mutation_routes["missing_thread_cap"] = _expect_generated_refusal(
            "missing_thread_cap",
            lambda: preconsumption_machine_gate(
                root,
                environ={},
                disk_usage_reader=_generated_disk_usage,
                rss_reader=lambda: 1,
            ),
        )
        mutation_routes["RSS_cap"] = _expect_generated_refusal(
            "RSS_cap",
            lambda: preconsumption_machine_gate(
                root,
                environ=_generated_environment(),
                disk_usage_reader=_generated_disk_usage,
                rss_reader=lambda: MAX_PEAK_RSS_BYTES + 1,
            ),
        )

        proof_activation = {
            "green_implementation": {
                "commit": "c" * 40,
                "CI_run_id": 4,
                "base_python_job_id": 5,
                "optional_neuro_readers_job_id": 6,
            }
        }
        proof_evidence = _generated_evidence()
        valid_proof = {
            "remote_main_commit": proof_evidence.activation_commit,
            "activation_is_remote_main": True,
            "fresh_git_remote_calls": 1,
            "fresh_GitHub_Actions_calls": 3,
            "runs": [
                {
                    "commit": GREEN_DECISION_COMMIT,
                    "CI_run_id": GREEN_DECISION_CI_RUN_ID,
                    "base_python_job_id": GREEN_DECISION_BASE_JOB_ID,
                    "optional_neuro_readers_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
                    "both_required_jobs_green": True,
                },
                {
                    "commit": "c" * 40,
                    "CI_run_id": 4,
                    "base_python_job_id": 5,
                    "optional_neuro_readers_job_id": 6,
                    "both_required_jobs_green": True,
                },
                {
                    "commit": proof_evidence.activation_commit,
                    "CI_run_id": proof_evidence.activation_ci_run_id,
                    "base_python_job_id": proof_evidence.activation_base_job_id,
                    "optional_neuro_readers_job_id": proof_evidence.activation_optional_job_id,
                    "both_required_jobs_green": True,
                },
            ],
        }
        validate_remote_green_proof(valid_proof, proof_activation, proof_evidence)
        proof_mutations = {
            "remote_main": ("remote_main_commit", "d" * 40),
            "activation_main_flag": ("activation_is_remote_main", False),
            "Git_remote_count": ("fresh_git_remote_calls", 0),
            "CI_call_count": ("fresh_GitHub_Actions_calls", 2),
        }
        for case, (key, value) in proof_mutations.items():
            candidate = dict(valid_proof)
            candidate[key] = value
            mutation_routes[case] = _expect_generated_refusal(
                case,
                lambda candidate=candidate: validate_remote_green_proof(
                    candidate, proof_activation, proof_evidence
                ),
            )
        for index, field in enumerate(
            ("commit", "CI_run_id", "base_python_job_id", "optional_neuro_readers_job_id")
        ):
            candidate = json.loads(json.dumps(valid_proof))
            candidate["runs"][index % 3][field] = "wrong" if field == "commit" else -1
            case = f"remote_run_{index}_{field}"
            mutation_routes[case] = _expect_generated_refusal(
                case,
                lambda candidate=candidate: validate_remote_green_proof(
                    candidate, proof_activation, proof_evidence
                ),
            )

        original_bytes = stage_h.PREFLIGHT_BYTES
        original_sha = stage_h.PREFLIGHT_SHA256
        original_spec = stage_h.REGISTERED_SPEC
        wrong_geometry = _generated_body(wrong_geometry=True)
        stage_h.PREFLIGHT_BYTES = len(wrong_geometry)
        stage_h.PREFLIGHT_SHA256 = _sha256_bytes(wrong_geometry)
        stage_h.REGISTERED_SPEC = stage_h.PreflightSpec(
            stage_h.PREFLIGHT_URL,
            stage_h.PREFLIGHT_PATH,
            len(wrong_geometry),
            _sha256_bytes(wrong_geometry),
        )
        h0_root = root / "h0"
        os.mkdir(h0_root, 0o700)
        os.mkdir(h0_root / ".codex_work", 0o700)
        h0_response = GeneratedResponse(wrong_geometry, url=stage_h.PREFLIGHT_URL)
        try:
            h0 = _execute_after_proof(
                h0_root,
                h0_root / "h0.json",
                _generated_evidence(),
                _generated_remote_proof(),
                GeneratedOpenerFactory(h0_response),
                environ=_generated_environment(),
                disk_usage_reader=_generated_disk_usage,
                rss_reader=lambda: 16 * 1024**2,
                generated_only=True,
            )
        finally:
            stage_h.PREFLIGHT_BYTES = original_bytes
            stage_h.PREFLIGHT_SHA256 = original_sha
            stage_h.REGISTERED_SPEC = original_spec
        generated_bytes += len(wrong_geometry)
        if h0["route"] != "DREYER-H0" or h0["refusal_code"] != "HL1-HEADER":
            raise StageHLiveRefusal("HL1-PROOF", "generated H0 routing failed")
        mutation_routes["header_payload_geometry"] = "HL1-HEADER"

        transfer_body = _generated_body()
        transfer_response = GeneratedResponse(
            transfer_body,
            url=stage_h.PREFLIGHT_URL,
            headers=(
                ("Content-Length", str(len(transfer_body))),
                ("Transfer-Encoding", "chunked"),
            ),
        )
        mutation_routes["transfer_encoding"] = _expect_generated_refusal(
            "transfer_encoding",
            lambda: _critical_headers(transfer_response),
        )
        duplicate_response = GeneratedResponse(
            transfer_body,
            url=stage_h.PREFLIGHT_URL,
            headers=(
                ("Content-Length", str(len(transfer_body))),
                ("Content-Length", str(len(transfer_body))),
            ),
        )
        mutation_routes["duplicate_content_length"] = _expect_generated_refusal(
            "duplicate_content_length",
            lambda: _critical_headers(duplicate_response),
        )
        encoded_response = GeneratedResponse(
            transfer_body,
            url=stage_h.PREFLIGHT_URL,
            headers=(
                ("Content-Length", str(len(transfer_body))),
                ("Content-Encoding", "identity"),
            ),
        )
        mutation_routes["content_encoding"] = _expect_generated_refusal(
            "content_encoding",
            lambda: _critical_headers(encoded_response),
        )

        existing_stage_h_root = root / "existing-stage-h"
        os.mkdir(existing_stage_h_root, 0o700)
        stage_h_cases, stage_h_generated_bytes, _retained = stage_h._run_generated_cases(
            existing_stage_h_root
        )
        generated_bytes += stage_h_generated_bytes

    runtime = time.monotonic() - started
    peak_rss = max(peak_before, _peak_rss_bytes())
    if runtime > 30 or peak_rss > MAX_PEAK_RSS_BYTES or generated_bytes > 64 * 1024**2:
        raise StageHLiveRefusal("HL1-RESOURCE", "generated qualification cap exceeded")
    result = {
        "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_live_generated_qualification_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "passed_generated_mock_only_consumed_no_real_or_network_operation",
        "green_decision": {
            "commit": GREEN_DECISION_COMMIT,
            "CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "base_python_job_id": GREEN_DECISION_BASE_JOB_ID,
            "optional_neuro_readers_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "cases": {
            "valid_wrapper_replays": 2,
            "deterministic_H1": True,
            "aggregate_H0": True,
            "marker_before_opener": True,
            "one_opener_and_request_per_replay": True,
            "responses_closed": True,
            "wrapper_mutation_refusals": len(mutation_routes),
            "wrapper_mutation_routes": mutation_routes,
            "replayed_stage_H_valid_cases": stage_h_cases["valid_cases_passed"],
            "replayed_stage_H_adversarial_refusals": stage_h_cases[
                "adversarial_cases_refused"
            ],
            "atomic_no_replace_implementation_present": True,
            "single_parser_capture_restored": stage_h.parse_edf_fixed_header.__module__
            == "neurodecodekit.datasets.dreyer_c5r_1",
        },
        "measurements": {
            "runtime_seconds": runtime,
            "peak_process_RSS_bytes": peak_rss,
            "generated_input_bytes": generated_bytes,
            "public_output_bytes": 0,
            "real_or_private_path_opens": 0,
            "real_HTTP_requests": 0,
            "real_network_bytes": 0,
            "real_EDF_payload_bytes": 0,
            "real_EDF_header_reads": 0,
            "annotation_signal_target_or_label_reads": 0,
            "model_training_inference_prediction_target_delivery_or_score_operations": 0,
            "producer_causal": None,
            "required_context_seconds": None,
            "end_to_end_latency_measured": False,
        },
        "warnings": [
            "generated_mock_qualification_has_no_scientific_value",
            "activation_is_absent_and_live_command_remains_locked",
            "real_source_EDF_sensor_roster_remains_unverified",
        ],
        "claim_boundary": {
            "engineering_capability": "generated_qualified_fail_closed_one_file_live_wrapper",
            "scientific_claim_not_established": "any_real_EEG_information_EEG_beyond_peripherals_unseen_person_generalization_movement_intention_motor_cortex_language_live_hardware_or_clinical_result",
        },
    }
    payload = _canonical_json_bytes(result)
    result["measurements"]["public_output_bytes"] = len(payload)
    payload = _canonical_json_bytes(result)
    result["measurements"]["public_output_bytes"] = len(payload)
    payload = _canonical_json_bytes(result)
    if len(payload) > MAX_PUBLIC_OUTPUT_BYTES:
        raise StageHLiveRefusal("HL1-PUBLICATION", "qualification output cap exceeded")
    output = Path(output_path).expanduser().absolute()
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_exclusive_durable(output, payload, mode=0o644)
    return result


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the activation-locked one-file plan without opening live capability."""

    load_green_decision(repo_root)
    root = Path(repo_root) if repo_root is not None else _repo_root()
    activation_present = (root / ACTIVATION_RELATIVE_PATH).is_file()
    return {
        "lane_id": LANE_ID,
        "status": "activation_locked" if not activation_present else "activation_record_present",
        "member": {
            "path": stage_h.PREFLIGHT_PATH,
            "bytes": stage_h.PREFLIGHT_BYTES,
            "sha256": stage_h.PREFLIGHT_SHA256,
        },
        "decision_commit": GREEN_DECISION_COMMIT,
        "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
        "implementation_record_present": (root / IMPLEMENTATION_RELATIVE_PATH).is_file(),
        "activation_record_present": activation_present,
        "real_invocation_available": False,
        "remaining_119_payload_requests": 0,
        "scientific_claim_established": False,
    }


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    candidate = Path(path).expanduser().absolute()
    info = os.lstat(candidate)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise StageHLiveRefusal("HL1-PUBLICATION", "result type differs")
    if info.st_size > MAX_PUBLIC_OUTPUT_BYTES:
        raise StageHLiveRefusal("HL1-PUBLICATION", "result cap exceeded")
    value = _strict_json(candidate.read_bytes())
    if not isinstance(value, dict):
        raise StageHLiveRefusal("HL1-PUBLICATION", "result root differs")
    _validate_public_report(value)
    return value
