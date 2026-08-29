"""Activation-locked range-only live wrapper for one Ofner 2017 GDF header."""

from __future__ import annotations

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
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, BinaryIO

from neurodecodekit.datasets import ofner_2017_motor_imagery_acquisition as source
from neurodecodekit.datasets import ofner_gdf_header as header

SCHEMA_VERSION = "0.1.0"
PACKET_ID = "OFNER-C6R-1-HL"
DECISION_RELATIVE_PATH = Path(
    "registries/ofner_2017_motor_imagery_range_header_decision.v0.json"
)
DECISION_SHA256 = "8b5578dd67e1e59a4480da908927a431c5bd80ec2191c7f79bb6fc97731b34dd"
GREEN_DECISION_COMMIT = "8ed4b7c93ad1a53c30bdacac63934a30d9f6a2f4"
GREEN_DECISION_CI_RUN_ID = 33_275_389_198
GREEN_DECISION_BASE_JOB_ID = 99_161_070_113
GREEN_DECISION_OPTIONAL_JOB_ID = 99_161_070_207
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/ofner_gdf_header_live_implementation.v0.json"
)
ACTIVATION_RELATIVE_PATH = Path("registries/ofner_gdf_header_live_activation.v0.json")
PUBLIC_RESULT_RELATIVE_PATH = Path("registries/ofner_gdf_header_live_result.v0.json")
PRIVATE_ROOT_RELATIVE_PATH = Path(".codex_work/ofner_gdf_header_live/v0")
CONSUMED_MARKER_NAME = "execution_consumed.v0.json"

MANIFEST_URL = "https://data.nemar.org/nm000173/v1.0.3/manifest.json"
MEMBER_PATH = "sourcedata/motorimagination_subject1_run1.gdf"
MEMBER_URL = f"https://data.nemar.org/nm000173/v1.0.3/{MEMBER_PATH}"
MEMBER_BYTES = 105_365_484
MEMBER_SHA256 = "ec334466272a936986a50c120c52c57634801f028acb0fee30705f8a2dee3087"
EXPECTED_HEADER_BYTES = 24_832
EXPECTED_CANONICAL_MANIFEST_BYTES = 748_162
EXPECTED_CANONICAL_MANIFEST_SHA256 = (
    "5e889976bf5f5c91970d35c968f5a7ee4b1075aeca0ede984414d4666845aa34"
)

MAX_RUNTIME_SECONDS = 120.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_MANIFEST_BODY_BYTES = 2 * 1024**2
MAX_GDF_BODY_BYTES = 65_536
MAX_TOTAL_BODY_BYTES = MAX_MANIFEST_BODY_BYTES + MAX_GDF_BODY_BYTES
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MINIMUM_FREE_DISK_BYTES = 2 * 1024**3
MAX_READ_CHUNK_BYTES = 64 * 1024
THREAD_ENV_KEYS = source.THREAD_ENV_KEYS

FROZEN_PREREQUISITES = (
    (
        Path("src/neurodecodekit/datasets/ofner_2017_motor_imagery_acquisition.py"),
        "9d2dc8d657860cefa5ec62500eaf23a8fcdbdba15eeec2ca5d2b19ed8ae58baa",
    ),
    (
        Path("src/neurodecodekit/datasets/ofner_gdf_header.py"),
        "a7d286a20c9a50c0a91003c19383eae4e2f9a846e5b44acb276bd724f69d5978",
    ),
    (
        Path("registries/ofner_2017_motor_imagery_fixed_header_contract.v0.json"),
        "c556049ddabdefe3f4de06d451954b8df99508c17ac950850bb8cf83e55fdae5",
    ),
    (
        Path("registries/ofner_2017_motor_imagery_range_header_authorization_request.v0.json"),
        "3ca9f7d873400be9f4ef833394a7373b8ec5fd0949c3a8cecbf8dc1bdca1547a",
    ),
)

REFUSAL_CODES = (
    "OHL-PROOF",
    "OHL-PATH",
    "OHL-MARKER",
    "OHL-TRANSPORT",
    "OHL-REPRESENTATION",
    "OHL-RESOURCE",
    "OHL-PUBLICATION",
)


class OfnerGDFHeaderLiveRefusal(RuntimeError):
    """Sanitized refusal raised by the proof-bound live wrapper."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code if code in REFUSAL_CODES else "OHL-PROOF"
        super().__init__(message)


@dataclass(frozen=True)
class LiveEvidence:
    """Externally observed identity of the separately green activation."""

    activation_sha256: str
    activation_commit: str
    activation_ci_run_id: int
    activation_base_job_id: int
    activation_optional_job_id: int
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class MachineSnapshot:
    """Bounded resource measurements captured before packet consumption."""

    free_disk_bytes: int
    peak_rss_bytes: int
    monotonic_started: float


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _GeneratedHeaders:
    def __init__(self, values: Sequence[tuple[str, str]]) -> None:
        self._values = tuple((str(name), str(value)) for name, value in values)

    def raw_items(self) -> list[tuple[str, str]]:
        return list(self._values)


class GeneratedResponse:
    """Closable in-memory response used only by generated qualification."""

    def __init__(
        self,
        body: bytes,
        *,
        url: str,
        status: int,
        headers: Sequence[tuple[str, str]],
        maximum_read_bytes: int | None = None,
        nonbytes_first_read: bool = False,
    ) -> None:
        self.status = status
        self.headers = _GeneratedHeaders(headers)
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
    """Three-response injected opener with observable request ordering."""

    def __init__(
        self,
        responses: Sequence[GeneratedResponse],
        events: list[str] | None = None,
    ) -> None:
        self.responses = list(responses)
        self.events = events if events is not None else []
        self.constructions = 0
        self.requests: list[urllib.request.Request] = []

    def __call__(self) -> Callable[[urllib.request.Request, float], BinaryIO]:
        self.constructions += 1
        self.events.append("opener_constructed")

        def open_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
            if timeout <= 0 or len(self.requests) >= len(self.responses):
                raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "request schedule differs")
            self.requests.append(request)
            self.events.append(f"request_{len(self.requests)}_opened")
            return self.responses[len(self.requests) - 1]  # type: ignore[return-value]

        return open_once


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError, RecursionError) as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "JSON serialization failed") from exc
    return (text + "\n").encode("ascii")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            while chunk := os.read(descriptor, MAX_READ_CHUNK_BYTES):
                digest.update(chunk)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "bound artifact read failed") from exc
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _strict_json(payload: bytes) -> Any:
    if not payload or payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ValueError("JSON encoding differs")
    return json.loads(
        payload.decode("utf-8", errors="strict"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite JSON")),
    )


def _read_bound_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "bound proof is unavailable") from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or not 0 < info.st_size <= MAX_PUBLIC_OUTPUT_BYTES
        or _sha256_file(path) != expected_sha256
    ):
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "bound proof identity differs")
    try:
        value = _strict_json(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "bound proof parse failed") from exc
    if not isinstance(value, dict):
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "bound proof root differs")
    return value


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact packet-bound decision after its remote-green barrier."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _read_bound_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    authority = decision.get("authorization_after_decision_green", {})
    frontier = decision.get("green_frontier_transition", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.ofner_2017_motor_imagery_range_header_decision"
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("packet_id") != PACKET_ID
        or decision.get("maintainer_words") != "continue"
        or decision.get("maintainer_words_sha256")
        != "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad"
        or decision.get("effective_only_after_decision_commit_pushed_and_both_CI_jobs_green")
        is not True
        or frontier.get("commit") != "845b39ef88cd747b329be49e56efa5cdf999a40d"
        or frontier.get("both_required_jobs_green") is not True
        or authority.get("implement_HL1_additive_standard_library_wrapper") is not True
        or authority.get("run_HL1_generated_mock_qualification_maximum") != 1
        or authority.get("HL2_registered_invocations_maximum") != 1
        or authority.get("HL2_success_manifest_GET_requests_exact") != 1
        or authority.get("HL2_success_GDF_range_GET_requests_exact") != 2
        or authority.get("HL2_combined_GDF_body_bytes_maximum") != MAX_GDF_BODY_BYTES
        or authority.get("whole_GDF_file_requests") != 0
        or authority.get("event_or_annotation_reads") != 0
        or authority.get("signal_sample_reads") != 0
        or authority.get("target_or_label_reads") != 0
        or authority.get("training_runs") != 0
        or authority.get("model_inference_runs") != 0
        or authority.get("scores") != 0
        or authority.get("reruns") != 0
    ):
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "green decision scope differs")
    for path, digest in FROZEN_PREREQUISITES:
        if _sha256_file(root / path) != digest:
            raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "qualified prerequisite changed")
    contract = header.load_registered_contract(root)
    policy = source.registered_policy(root)
    if (
        contract.get("exact_member", {}).get("path") != MEMBER_PATH
        or policy.expected_canonical_bytes != EXPECTED_CANONICAL_MANIFEST_BYTES
        or policy.expected_canonical_sha256 != EXPECTED_CANONICAL_MANIFEST_SHA256
    ):
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "source identity differs")
    return decision


def load_implementation_record(
    repo_root: str | Path,
    *,
    expected_sha256: str,
) -> dict[str, Any]:
    """Validate the exact generated-qualified implementation record."""

    if len(expected_sha256) != 64:
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "implementation digest is malformed")
    root = Path(repo_root)
    record = _read_bound_json(root / IMPLEMENTATION_RELATIVE_PATH, expected_sha256)
    if (
        record.get("schema_name") != "neurodecodekit.ofner_gdf_header_live_implementation"
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("packet_id") != PACKET_ID
        or record.get("status")
        != "generated_qualified_remote_green_required_before_activation"
        or record.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or record.get("green_decision", {}).get("CI_run_id") != GREEN_DECISION_CI_RUN_ID
        or record.get("generated_qualification", {}).get("all_gates_passed") is not True
        or record.get("execution_state", {}).get("real_invocation_consumed") is not False
        or any(record.get("real_operation_counters", {}).values())
    ):
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "implementation record differs")
    bindings = record.get("tracked_file_hashes")
    if not isinstance(bindings, list) or not bindings:
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "implementation bindings are absent")
    for binding in bindings:
        relative = str(binding.get("path", ""))
        digest = str(binding.get("sha256", ""))
        if (
            not relative
            or relative.startswith(("/", "~"))
            or ".." in Path(relative).parts
            or len(digest) != 64
            or _sha256_file(root / relative) != digest
        ):
            raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "implementation binding differs")
    return record


def load_activation(repo_root: str | Path, evidence: LiveEvidence) -> dict[str, Any]:
    """Load the separately green activation that exposes one real invocation."""

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
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "activation evidence is malformed")
    root = Path(repo_root)
    activation = _read_bound_json(root / ACTIVATION_RELATIVE_PATH, evidence.activation_sha256)
    implementation = activation.get("green_implementation", {})
    authority = activation.get("authority", {})
    if (
        activation.get("schema_name") != "neurodecodekit.ofner_gdf_header_live_activation"
        or activation.get("schema_version") != SCHEMA_VERSION
        or activation.get("packet_id") != PACKET_ID
        or activation.get("status") != "one_range_header_checkpoint_active_after_remote_green"
        or activation.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or activation.get("green_decision", {}).get("CI_run_id") != GREEN_DECISION_CI_RUN_ID
        or implementation.get("both_required_jobs_green") is not True
        or authority.get("registered_invocations") != 1
        or authority.get("success_manifest_GET_requests") != 1
        or authority.get("success_GDF_range_GET_requests") != 2
        or authority.get("combined_GDF_body_bytes_maximum") != MAX_GDF_BODY_BYTES
        or authority.get("whole_GDF_file_requests") != 0
        or authority.get("reruns") != 0
    ):
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "activation scope differs")
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
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "remote proof command failed") from exc
    if completed.returncode or not completed.stdout.strip():
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "remote proof command refused")
    return completed.stdout.strip()


def collect_remote_green_proof(
    repo_root: str | Path,
    activation: Mapping[str, Any],
    evidence: LiveEvidence,
) -> dict[str, Any]:
    """Collect fresh main-head and three-run GitHub proof before source access."""

    root = Path(repo_root)
    remote = _run_command(root, ("git", "ls-remote", "--heads", "origin", "refs/heads/main"))
    fields = remote.split()
    if len(fields) != 2 or fields[1] != "refs/heads/main":
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "remote main proof is ambiguous")
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
    observed: list[dict[str, Any]] = []
    for commit, run_id, base_job_id, optional_job_id in runs:
        output = _run_command(
            root,
            ("gh", "run", "view", str(run_id), "--json", "conclusion,headSha,jobs,status"),
        )
        try:
            value = json.loads(output)
        except json.JSONDecodeError as exc:
            raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "remote CI proof is malformed") from exc
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
            raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "remote CI proof differs")
        observed.append(
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
        "runs": observed,
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
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "remote green proof differs")
    for observed, wanted in zip(runs, expected, strict=True):
        commit, run_id, base_job_id, optional_job_id = wanted
        if (
            observed.get("commit") != commit
            or observed.get("CI_run_id") != run_id
            or observed.get("base_python_job_id") != base_job_id
            or observed.get("optional_neuro_readers_job_id") != optional_job_id
            or observed.get("both_required_jobs_green") is not True
        ):
            raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "remote run proof differs")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _ensure_single_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "thread environment differs")


def preconsumption_machine_gate(
    workspace: Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    clock: Callable[[], float] = time.monotonic,
) -> MachineSnapshot:
    """Check resource boundaries before creating the consumed marker."""

    _ensure_single_thread_environment(environ)
    try:
        free = int(disk_usage_reader(workspace).free)
        rss = int(rss_reader())
        started = float(clock())
    except Exception as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "machine metric unavailable") from exc
    if free < MINIMUM_FREE_DISK_BYTES or not 0 <= rss <= MAX_PEAK_RSS_BYTES:
        raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "preconsumption resource gate failed")
    if not math.isfinite(started):
        raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "monotonic clock differs")
    return MachineSnapshot(free, rss, started)


def _lstat_directory(path: Path, code: str = "OHL-PATH") -> os.stat_result:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise OfnerGDFHeaderLiveRefusal(code, "directory capability unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise OfnerGDFHeaderLiveRefusal(code, "directory capability type differs")
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
        raise OfnerGDFHeaderLiveRefusal("OHL-PATH", "directory durability failed") from exc


def _create_private_chain(workspace: Path) -> Path:
    if not workspace.is_absolute() or ".." in workspace.parts:
        raise OfnerGDFHeaderLiveRefusal("OHL-PATH", "workspace identity differs")
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
                raise OfnerGDFHeaderLiveRefusal(
                    "OHL-PATH", "private directory creation failed"
                ) from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise OfnerGDFHeaderLiveRefusal("OHL-PATH", "private path component differs")
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
        raise OfnerGDFHeaderLiveRefusal("OHL-MARKER", "exclusive file already exists") from exc
    except OSError as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "durable write failed") from exc


def _write_consumed_marker(
    private_root: Path,
    evidence: LiveEvidence,
    *,
    events: list[str] | None = None,
) -> tuple[Path, int]:
    marker = {
        "schema_name": "neurodecodekit.ofner_gdf_header_live_consumed",
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "activation_commit": evidence.activation_commit,
        "activation_sha256": evidence.activation_sha256,
        "registered_execution_ordinal": 1,
        "retry_allowed": False,
        "rerun_allowed": False,
        "fallback_or_substitution_allowed": False,
        "whole_file_signal_event_target_model_or_score_access_allowed": False,
    }
    payload = _canonical_json_bytes(marker)
    path = private_root / CONSUMED_MARKER_NAME
    _write_exclusive_durable(path, payload, mode=0o600)
    if events is not None:
        events.append("marker_durable")
    return path, len(payload)


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
        raise OfnerGDFHeaderLiveRefusal("OHL-PATH", "private allocation walk failed") from exc
    return total


def _enforce_resources(
    private_root: Path,
    snapshot: MachineSnapshot,
    *,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    disk_usage_reader: Callable[[Path], Any],
) -> dict[str, Any]:
    try:
        runtime = float(clock()) - snapshot.monotonic_started
        rss = int(rss_reader())
        free = int(disk_usage_reader(private_root).free)
        allocated = _allocated_tree_bytes(private_root)
    except OfnerGDFHeaderLiveRefusal:
        raise
    except Exception as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "resource metric failed") from exc
    if (
        not math.isfinite(runtime)
        or not 0 <= runtime <= MAX_RUNTIME_SECONDS
        or not 0 <= rss <= MAX_PEAK_RSS_BYTES
        or free < MINIMUM_FREE_DISK_BYTES
        or allocated > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "resource cap exceeded")
    return {
        "runtime_seconds": runtime,
        "peak_process_RSS_bytes": rss,
        "free_disk_bytes": free,
        "private_allocated_bytes": allocated,
    }


def _critical_headers(response: Any, *, range_response: bool) -> dict[str, str]:
    headers = getattr(response, "headers", None)
    if headers is None:
        raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "response headers unavailable")
    items = headers.raw_items() if hasattr(headers, "raw_items") else headers.items()
    critical = {
        "content-length",
        "content-encoding",
        "transfer-encoding",
        "location",
        "content-range",
        "content-type",
    }
    values: dict[str, str] = {}
    for raw_name, raw_value in items:
        name = str(raw_name).strip().casefold()
        value = str(raw_value).strip()
        if not name or "\r" in value or "\n" in value:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "response header malformed")
        if name not in critical:
            continue
        if name in values:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "critical header duplicated")
        values[name] = value
    if "transfer-encoding" in values or "location" in values:
        raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "response transport differs")
    if values.get("content-encoding", "identity").casefold() != "identity":
        raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "response is encoded")
    if range_response:
        content_type = values.get("content-type", "").casefold()
        if content_type.startswith("multipart/"):
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "range response is multipart")
    return values


def _response_url(response: Any, expected_url: str) -> None:
    getter = getattr(response, "geturl", None)
    if not callable(getter) or getter() != expected_url:
        raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "final response URL differs")


def _read_declared_body(response: BinaryIO, declared: int, cap: int) -> bytes:
    if not 0 < declared <= cap:
        raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "declared body exceeds cap")
    chunks: list[bytes] = []
    remaining = declared
    while remaining:
        try:
            chunk = response.read(min(remaining, MAX_READ_CHUNK_BYTES))
        except Exception as exc:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "response read failed") from exc
        if type(chunk) is not bytes:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "response body type differs")
        if not chunk:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "response body is truncated")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _request_headers(request: urllib.request.Request) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_name, raw_value in request.header_items():
        name = raw_name.strip().casefold()
        value = raw_value.strip()
        if not name or name in result or "\r" in value or "\n" in value:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "request header differs")
        result[name] = value
    return result


def _build_request(url: str, *, range_value: str | None = None) -> urllib.request.Request:
    headers = {
        "Accept-Encoding": "identity",
        "User-Agent": "NeuroDecodeKit-OFNER-C6R-1-HL/0.1",
    }
    if range_value is not None:
        headers["Range"] = range_value
    request = urllib.request.Request(url, headers=headers, method="GET")
    expected = {key.casefold(): value for key, value in headers.items()}
    if request.get_method() != "GET" or request.full_url != url:
        raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "request identity differs")
    if _request_headers(request) != expected:
        raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "request headers differ")
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
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "direct HTTPS request failed") from exc

    return open_once


def _close_response(response: BinaryIO) -> None:
    try:
        response.close()
    except (OSError, ValueError) as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "response close failed") from exc


def _fetch_manifest(
    opener: Callable[[urllib.request.Request, float], BinaryIO],
    policy: source.SelectionPolicy,
    *,
    timeout: float,
) -> tuple[tuple[source.ManifestMember, ...], int]:
    response = opener(_build_request(MANIFEST_URL), timeout)
    try:
        if getattr(response, "status", None) != 200:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "manifest status differs")
        _response_url(response, MANIFEST_URL)
        values = _critical_headers(response, range_response=False)
        raw_length = values.get("content-length", "")
        if not raw_length.isascii() or not raw_length.isdigit():
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "manifest length malformed")
        body = _read_declared_body(response, int(raw_length), MAX_MANIFEST_BODY_BYTES)
        try:
            members = source.select_manifest(body, policy)
        except source.OfnerAcquisitionRefusal as exc:
            raise OfnerGDFHeaderLiveRefusal(
                "OHL-TRANSPORT", "manifest identity firewall refused"
            ) from exc
        selected = tuple(
            member for member in members if member.participant == 1 and member.run == 1
        )
        if len(selected) != 1:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "exact member is absent")
        member = selected[0]
        if (
            member.path != MEMBER_PATH
            or member.size_bytes != MEMBER_BYTES
            or member.sha256 != MEMBER_SHA256
            or member.bytes_url != MEMBER_URL
        ):
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "exact member identity differs")
        return members, len(body)
    finally:
        _close_response(response)


def _fetch_range(
    opener: Callable[[urllib.request.Request, float], BinaryIO],
    *,
    start: int,
    end: int,
    timeout: float,
) -> bytes:
    request = _build_request(MEMBER_URL, range_value=f"bytes={start}-{end}")
    response = opener(request, timeout)
    try:
        if getattr(response, "status", None) != 206:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "range status differs")
        _response_url(response, MEMBER_URL)
        values = _critical_headers(response, range_response=True)
        raw_length = values.get("content-length", "")
        if not raw_length.isascii() or not raw_length.isdigit():
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "range length malformed")
        expected_length = end - start + 1
        if int(raw_length) != expected_length:
            raise OfnerGDFHeaderLiveRefusal("OHL-TRANSPORT", "range length differs")
        body = _read_declared_body(response, expected_length, MAX_GDF_BODY_BYTES)
        transcript = header.RangeResponse(
            status=206,
            headers=tuple(values.items()),
            body=body,
            redirects=0,
        )
        try:
            return header.validate_range_response(
                transcript,
                expected_start=start,
                expected_end=end,
                expected_total=MEMBER_BYTES,
            )
        except header.OfnerGDFHeaderRefusal as exc:
            raise OfnerGDFHeaderLiveRefusal(
                "OHL-TRANSPORT", "range transcript firewall refused"
            ) from exc
    finally:
        _close_response(response)


def _parse_representation(first: bytes, second: bytes, contract: Mapping[str, Any]):
    try:
        descriptor = header.parse_fixed_header(first)
        if descriptor.header_bytes != len(first) + len(second):
            raise header.OfnerGDFHeaderRefusal("assembled header length differs")
        parsed = header.parse_complete_header(first + second, contract)
    except header.OfnerGDFHeaderRefusal as exc:
        raise OfnerGDFHeaderLiveRefusal(
            "OHL-REPRESENTATION", "fixed representation differs"
        ) from exc
    if (
        parsed.header_bytes != EXPECTED_HEADER_BYTES
        or parsed.number_of_signals != 96
        or parsed.sampling_rate_hz != 512
        or (parsed.EEG_channels, parsed.EOG_channels, parsed.glove_channels, parsed.arm_channels)
        != (61, 3, 19, 13)
        or parsed.unique_normalized_labels != 96
    ):
        raise OfnerGDFHeaderLiveRefusal("OHL-REPRESENTATION", "H1 contract differs")
    return parsed


def _base_operation_counters() -> dict[str, int]:
    return {
        "manifest_GET_requests": 0,
        "GDF_range_GET_requests": 0,
        "response_opens": 0,
        "manifest_body_bytes": 0,
        "GDF_body_bytes": 0,
        "full_GDF_file_requests": 0,
        "full_payload_SHA256_passes": 0,
        "fixed_header_reads": 0,
        "fixed_header_semantic_parses": 0,
        "event_or_annotation_reads": 0,
        "signal_sample_reads": 0,
        "target_or_label_reads": 0,
        "model_or_checkpoint_opens": 0,
        "training_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scores": 0,
        "retries": 0,
        "reruns": 0,
        "fallbacks_or_substitutions": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _public_report(
    *,
    route: str,
    refusal_code: str | None,
    parsed: Any | None,
    resources: Mapping[str, Any],
    counters: Mapping[str, int],
    marker_bytes: int,
    remote_proof: Mapping[str, Any],
    generated_only: bool,
) -> dict[str, Any]:
    if route not in {"OFNER-H1", "OFNER-H0-REPRESENTATION", "OFNER-H0-TRANSPORT"}:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "terminal route differs")
    measurement = None
    if parsed is not None:
        measurement = {
            key: value
            for key, value in asdict(parsed).items()
            if key != "complete_header_sha256"
        }
    report = {
        "schema_name": "neurodecodekit.ofner_gdf_header_live_result",
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "status": "passed_fixed_header_contract" if route == "OFNER-H1" else "parked",
        "route": route,
        "refusal_code": refusal_code,
        "object": {
            "dataset": "NEMAR_nm000173",
            "revision": "v1.0.3",
            "participant": 1,
            "run": 1,
            "path": MEMBER_PATH,
            "declared_payload_bytes": MEMBER_BYTES,
            "manifest_declared_payload_sha256": MEMBER_SHA256,
            "full_payload_hash_recomputed": False,
        },
        "measurement_contract": measurement,
        "payload_retained_bytes": 0,
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
            "fresh_GitHub_Actions_calls": remote_proof.get("fresh_GitHub_Actions_calls", 0),
            "decision_implementation_and_activation_green": True,
        },
        "warnings": [
            "fixed_header_checkpoint_is_structural_not_a_neural_effect",
            "full_payload_hash_not_recomputed",
            "transport_header_and_TLS_byte_counts_unavailable",
            "patient_recording_date_events_annotations_signals_targets_models_and_scores_not_accessed",
            "end_to_end_latency_not_measured",
        ],
        "generated_only": generated_only,
        "claim_boundary": {
            "engineering_capability": "one_exact_range_only_GDF_fixed_header_checkpoint",
            "scientific_claim_not_established": "EEG_information_EEG_beyond_EOG_or_kinematics_unseen_person_generalization_movement_intention_motor_cortex_causation_thought_or_language_decoding_live_decoding_hardware_or_clinical_utility",
        },
    }
    previous = -1
    for _ in range(8):
        payload = _canonical_json_bytes(report)
        report["resources"]["public_output_bytes"] = len(payload)
        if len(payload) == previous:
            break
        previous = len(payload)
    _validate_public_report(report)
    if len(_canonical_json_bytes(report)) > MAX_PUBLIC_OUTPUT_BYTES:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "public output cap exceeded")
    return report


def _validate_public_report(report: Mapping[str, Any]) -> None:
    allowed = {
        "schema_name",
        "schema_version",
        "packet_id",
        "status",
        "route",
        "refusal_code",
        "object",
        "measurement_contract",
        "payload_retained_bytes",
        "resources",
        "operation_counters",
        "remote_proof",
        "warnings",
        "generated_only",
        "claim_boundary",
    }
    if set(report) != allowed:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "public report fields differ")
    forbidden_exact = {
        "patient",
        "recording",
        "date",
        "raw_header",
        "annotation",
        "signal_samples",
        "target",
        "label",
        "signed_url",
        "private_path",
        "exception",
        "traceback",
        "reference",
    }

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).casefold() in forbidden_exact:
                    raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "forbidden public field")
                walk(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                walk(child)
        elif isinstance(value, float) and not math.isfinite(value):
            raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "non-finite public number")

    walk(report)


def _publish_report(path: Path, report: Mapping[str, Any]) -> int:
    payload = _canonical_json_bytes(report)
    if len(payload) > MAX_PUBLIC_OUTPUT_BYTES:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "public output cap exceeded")
    _write_exclusive_durable(path, payload, mode=0o644)
    return len(payload)


def _execute_after_proof(
    workspace: Path,
    output_path: Path,
    evidence: LiveEvidence,
    remote_proof: Mapping[str, Any],
    opener_factory: Callable[[], Callable[[urllib.request.Request, float], BinaryIO]],
    *,
    policy: source.SelectionPolicy,
    contract: Mapping[str, Any],
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    clock: Callable[[], float] = time.monotonic,
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
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "public result already exists")
    marker_path, marker_bytes = _write_consumed_marker(private_root, evidence, events=events)
    if not marker_path.is_file() or marker_path.is_symlink():
        raise OfnerGDFHeaderLiveRefusal("OHL-MARKER", "consumed marker durability differs")

    counters = _base_operation_counters()
    opener = opener_factory()
    parsed = None
    route = "OFNER-H1"
    refusal_code = None
    try:
        if not generated_only:
            counters["manifest_GET_requests"] = 1
            counters["response_opens"] = 1
        _members, manifest_bytes = _fetch_manifest(
            opener,
            policy,
            timeout=MAX_RUNTIME_SECONDS,
        )
        if not generated_only:
            counters["manifest_body_bytes"] = manifest_bytes

        if not generated_only:
            counters["GDF_range_GET_requests"] = 1
            counters["response_opens"] += 1
        first = _fetch_range(opener, start=0, end=255, timeout=MAX_RUNTIME_SECONDS)
        if not generated_only:
            counters["GDF_body_bytes"] = len(first)
            counters["fixed_header_reads"] = 1
        try:
            descriptor = header.parse_fixed_header(first)
        except header.OfnerGDFHeaderRefusal as exc:
            raise OfnerGDFHeaderLiveRefusal(
                "OHL-REPRESENTATION", "fixed header representation differs"
            ) from exc
        if descriptor.header_bytes > MAX_GDF_BODY_BYTES:
            raise OfnerGDFHeaderLiveRefusal("OHL-REPRESENTATION", "declared header exceeds cap")

        if not generated_only:
            counters["GDF_range_GET_requests"] += 1
            counters["response_opens"] += 1
        second = _fetch_range(
            opener,
            start=256,
            end=descriptor.header_bytes - 1,
            timeout=MAX_RUNTIME_SECONDS,
        )
        if not generated_only:
            counters["GDF_body_bytes"] += len(second)
        parsed = _parse_representation(first, second, contract)
        if not generated_only:
            counters["fixed_header_semantic_parses"] = 1
        if manifest_bytes + len(first) + len(second) > MAX_TOTAL_BODY_BYTES:
            raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "total body cap exceeded")
    except OfnerGDFHeaderLiveRefusal as exc:
        refusal_code = exc.code
        route = (
            "OFNER-H0-REPRESENTATION"
            if exc.code == "OHL-REPRESENTATION"
            else "OFNER-H0-TRANSPORT"
        )
        parsed = None
    resources = _enforce_resources(
        private_root,
        snapshot,
        clock=clock,
        rss_reader=rss_reader,
        disk_usage_reader=disk_usage_reader,
    )
    report = _public_report(
        route=route,
        refusal_code=refusal_code,
        parsed=parsed,
        resources=resources,
        counters=counters,
        marker_bytes=marker_bytes,
        remote_proof=remote_proof,
        generated_only=generated_only,
    )
    _publish_report(output_path, report)
    return report


def execute_registered_checkpoint(
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
    """Execute the separately activated one-shot public range checkpoint."""

    root = (Path(repo_root) if repo_root is not None else _repo_root()).expanduser().absolute()
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
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "local Git proof failed") from exc
    if head != evidence.activation_commit or tracked.returncode or tracked.stdout.strip():
        raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "local activation checkout differs")
    remote_proof = remote_proof_collector(root, activation, evidence)
    validate_remote_green_proof(remote_proof, activation, evidence)
    return _execute_after_proof(
        root,
        root / PUBLIC_RESULT_RELATIVE_PATH,
        evidence,
        remote_proof,
        opener_factory,
        policy=source.registered_policy(root),
        contract=header.load_registered_contract(root),
        environ=os.environ if environ is None else environ,
        disk_usage_reader=disk_usage_reader,
        rss_reader=rss_reader,
        clock=clock,
        generated_only=False,
    )


def _generated_manifest() -> tuple[source.SelectionPolicy, bytes]:
    policy, raw, _payloads = source._generated_fixture()
    value = json.loads(raw)
    first = next(
        row for row in value["files"] if row["path"] == MEMBER_PATH
    )
    first["bytes"] = MEMBER_BYTES
    first["sha256"] = MEMBER_SHA256
    first["bytes_url"] = MEMBER_URL
    temporary = replace(
        policy,
        expected_payload_bytes=sum(int(row["bytes"]) for row in value["files"]),
        expected_canonical_bytes=None,
        expected_canonical_sha256=None,
    )
    first["url"] = source._generated_signed_url(
        temporary,
        MEMBER_BYTES,
        MEMBER_SHA256,
        signature_digit="2",
    )
    raw = source._canonical_json_bytes(value)
    canonical = source.canonicalize_manifest(raw)
    return (
        replace(
            temporary,
            expected_canonical_bytes=len(canonical),
            expected_canonical_sha256=_sha256_bytes(canonical),
        ),
        raw,
    )


def _generated_range_headers(start: int, end: int) -> tuple[tuple[str, str], ...]:
    return (
        ("Content-Range", f"bytes {start}-{end}/{MEMBER_BYTES}"),
        ("Content-Length", str(end - start + 1)),
        ("Content-Encoding", "identity"),
        ("Content-Type", "application/octet-stream"),
    )


def _generated_responses(
    manifest: bytes,
    fixture: bytes,
) -> list[GeneratedResponse]:
    return [
        GeneratedResponse(
            manifest,
            url=MANIFEST_URL,
            status=200,
            headers=(("Content-Length", str(len(manifest))),),
            maximum_read_bytes=97,
        ),
        GeneratedResponse(
            fixture[:256],
            url=MEMBER_URL,
            status=206,
            headers=_generated_range_headers(0, 255),
            maximum_read_bytes=71,
        ),
        GeneratedResponse(
            fixture[256:],
            url=MEMBER_URL,
            status=206,
            headers=_generated_range_headers(256, len(fixture) - 1),
            maximum_read_bytes=113,
        ),
    ]


def _generated_remote_proof() -> dict[str, Any]:
    return {
        "remote_main_commit": "a" * 40,
        "activation_is_remote_main": True,
        "runs": [],
        "fresh_git_remote_calls": 0,
        "fresh_GitHub_Actions_calls": 0,
    }


def _generated_evidence() -> LiveEvidence:
    return LiveEvidence("b" * 64, "a" * 40, 1, 2, 3)


def _generated_environment() -> dict[str, str]:
    return {key: "1" for key in THREAD_ENV_KEYS}


def _generated_disk_usage(_path: Path) -> Any:
    return type("Usage", (), {"free": MINIMUM_FREE_DISK_BYTES + 1024**3})()


def _run_generated_case(
    root: Path,
    name: str,
    *,
    response_mutator: Callable[[list[GeneratedResponse]], None] | None = None,
    fixture_mutator: Callable[[bytes], bytes] | None = None,
    manifest_mutator: Callable[[bytes], bytes] | None = None,
) -> tuple[dict[str, Any], GeneratedOpenerFactory, list[str]]:
    policy, manifest = _generated_manifest()
    if manifest_mutator is not None:
        manifest = manifest_mutator(manifest)
    contract = header.load_registered_contract(_repo_root())
    fixture = header.build_generated_header(contract)
    if fixture_mutator is not None:
        fixture = fixture_mutator(fixture)
    responses = _generated_responses(manifest, fixture)
    if response_mutator is not None:
        response_mutator(responses)
    events: list[str] = []
    opener = GeneratedOpenerFactory(responses, events)
    result = _execute_after_proof(
        root,
        root / f"{name}.json",
        _generated_evidence(),
        _generated_remote_proof(),
        opener,
        policy=policy,
        contract=contract,
        environ=_generated_environment(),
        disk_usage_reader=_generated_disk_usage,
        rss_reader=lambda: 16 * 1024**2,
        generated_only=True,
        events=events,
    )
    return result, opener, events


def _expect_refusal(name: str, operation: Callable[[], Any]) -> str:
    try:
        operation()
    except OfnerGDFHeaderLiveRefusal as exc:
        return exc.code
    raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", f"generated case passed: {name}")


def _new_generated_workspace(parent: Path, name: str) -> Path:
    root = parent / name
    root.mkdir(mode=0o700)
    (root / ".codex_work").mkdir(mode=0o700)
    return root


def run_generated_qualification(
    output_path: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Run the sole generated/mock qualification without source access."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_green_decision(root)
    _ensure_single_thread_environment(os.environ)
    started = time.monotonic()
    peak_before = _peak_rss_bytes()
    routes: dict[str, str] = {}
    generated_bytes = 0
    with tempfile.TemporaryDirectory(prefix="neurodecodekit-ofner-hl1-") as temporary:
        parent = Path(temporary).absolute()
        first_root = _new_generated_workspace(parent, "first")
        replay_root = _new_generated_workspace(parent, "replay")
        first, first_opener, first_events = _run_generated_case(first_root, "result")
        replay, replay_opener, replay_events = _run_generated_case(replay_root, "result")
        _policy, manifest = _generated_manifest()
        fixture = header.build_generated_header(header.load_registered_contract(root))
        generated_bytes += 2 * (len(manifest) + len(fixture))
        if (
            first["route"] != "OFNER-H1"
            or replay["route"] != "OFNER-H1"
            or first["measurement_contract"] != replay["measurement_contract"]
            or first_events[:2] != ["marker_durable", "opener_constructed"]
            or replay_events[:2] != ["marker_durable", "opener_constructed"]
            or first_opener.constructions != 1
            or replay_opener.constructions != 1
            or len(first_opener.requests) != 3
            or len(replay_opener.requests) != 3
            or not all(response.closed for response in first_opener.responses)
            or not all(response.closed for response in replay_opener.responses)
        ):
            raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "deterministic replay failed")
        expected_ranges = [None, "bytes=0-255", "bytes=256-24831"]
        for opener in (first_opener, replay_opener):
            observed = [_request_headers(request).get("range") for request in opener.requests]
            if observed != expected_ranges:
                raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "range schedule differs")

        rerun_root = _new_generated_workspace(parent, "rerun")
        _run_generated_case(rerun_root, "first")
        routes["consumed_rerun"] = _expect_refusal(
            "consumed_rerun", lambda: _run_generated_case(rerun_root, "second")
        )
        collision_root = _new_generated_workspace(parent, "collision")
        (collision_root / "result.json").write_text("preserve", encoding="ascii")
        routes["output_collision"] = _expect_refusal(
            "output_collision", lambda: _run_generated_case(collision_root, "result")
        )
        symlink_root = _new_generated_workspace(parent, "symlink")
        (symlink_root / ".codex_work").rmdir()
        os.symlink(parent, symlink_root / ".codex_work")
        routes["symlink_private_root"] = _expect_refusal(
            "symlink_private_root", lambda: _create_private_chain(symlink_root)
        )
        resource_cases = {
            "thread_cap": ({}, _generated_disk_usage, lambda: 1, lambda: 0.0),
            "disk_floor": (
                _generated_environment(),
                lambda _path: type("Usage", (), {"free": MINIMUM_FREE_DISK_BYTES - 1})(),
                lambda: 1,
                lambda: 0.0,
            ),
            "RSS_cap": (
                _generated_environment(),
                _generated_disk_usage,
                lambda: MAX_PEAK_RSS_BYTES + 1,
                lambda: 0.0,
            ),
            "clock_nonfinite": (
                _generated_environment(),
                _generated_disk_usage,
                lambda: 1,
                lambda: float("nan"),
            ),
        }
        for name, (environ, disk_reader, rss_reader, clock) in resource_cases.items():
            routes[name] = _expect_refusal(
                name,
                lambda environ=environ, disk_reader=disk_reader, rss_reader=rss_reader,
                clock=clock: preconsumption_machine_gate(
                    parent,
                    environ=environ,
                    disk_usage_reader=disk_reader,
                    rss_reader=rss_reader,
                    clock=clock,
                ),
            )

        evidence = _generated_evidence()
        activation = {
            "green_implementation": {
                "commit": "c" * 40,
                "CI_run_id": 4,
                "base_python_job_id": 5,
                "optional_neuro_readers_job_id": 6,
            }
        }
        proof = {
            "remote_main_commit": evidence.activation_commit,
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
                    "commit": evidence.activation_commit,
                    "CI_run_id": 1,
                    "base_python_job_id": 2,
                    "optional_neuro_readers_job_id": 3,
                    "both_required_jobs_green": True,
                },
            ],
        }
        validate_remote_green_proof(proof, activation, evidence)
        for name, key, value in (
            ("proof_remote_main", "remote_main_commit", "d" * 40),
            ("proof_activation_flag", "activation_is_remote_main", False),
            ("proof_git_calls", "fresh_git_remote_calls", 0),
            ("proof_CI_calls", "fresh_GitHub_Actions_calls", 2),
        ):
            candidate = json.loads(json.dumps(proof))
            candidate[key] = value
            routes[name] = _expect_refusal(
                name,
                lambda candidate=candidate: validate_remote_green_proof(
                    candidate, activation, evidence
                ),
            )
        for index, field in enumerate(
            ("commit", "CI_run_id", "base_python_job_id", "optional_neuro_readers_job_id")
        ):
            candidate = json.loads(json.dumps(proof))
            candidate["runs"][1][field] = "x" if field == "commit" else 999
            routes[f"proof_implementation_{field}_{index}"] = _expect_refusal(
                field,
                lambda candidate=candidate: validate_remote_green_proof(
                    candidate, activation, evidence
                ),
            )

        response_mutations: list[tuple[str, Callable[[list[GeneratedResponse]], None], str]] = [
            ("manifest_status", lambda values: setattr(values[0], "status", 206), "OFNER-H0-TRANSPORT"),
            ("manifest_URL", lambda values: setattr(values[0], "_url", "https://example.invalid"), "OFNER-H0-TRANSPORT"),
            ("manifest_encoding", lambda values: setattr(values[0], "headers", _GeneratedHeaders((("Content-Length", str(len(values[0]._body))), ("Content-Encoding", "gzip")))), "OFNER-H0-TRANSPORT"),
            ("manifest_duplicate_length", lambda values: setattr(values[0], "headers", _GeneratedHeaders((("Content-Length", str(len(values[0]._body))), ("Content-Length", str(len(values[0]._body)))))), "OFNER-H0-TRANSPORT"),
            ("manifest_transfer", lambda values: setattr(values[0], "headers", _GeneratedHeaders((("Content-Length", str(len(values[0]._body))), ("Transfer-Encoding", "chunked")))), "OFNER-H0-TRANSPORT"),
            ("manifest_short", lambda values: setattr(values[0], "_body", values[0]._body[:-1]), "OFNER-H0-TRANSPORT"),
            ("manifest_nonbytes", lambda values: setattr(values[0], "_nonbytes_first_read", True), "OFNER-H0-TRANSPORT"),
            ("first_status", lambda values: setattr(values[1], "status", 200), "OFNER-H0-TRANSPORT"),
            ("first_URL", lambda values: setattr(values[1], "_url", MANIFEST_URL), "OFNER-H0-TRANSPORT"),
            ("first_content_range", lambda values: setattr(values[1], "headers", _GeneratedHeaders(_generated_range_headers(1, 256))), "OFNER-H0-TRANSPORT"),
            ("first_encoding", lambda values: setattr(values[1], "headers", _GeneratedHeaders(_generated_range_headers(0, 255) + (("Content-Encoding", "gzip"),))), "OFNER-H0-TRANSPORT"),
            ("first_short", lambda values: setattr(values[1], "_body", values[1]._body[:-1]), "OFNER-H0-TRANSPORT"),
            ("second_status", lambda values: setattr(values[2], "status", 200), "OFNER-H0-TRANSPORT"),
            ("second_content_range", lambda values: setattr(values[2], "headers", _GeneratedHeaders(_generated_range_headers(257, EXPECTED_HEADER_BYTES))), "OFNER-H0-TRANSPORT"),
            ("second_multipart", lambda values: setattr(values[2], "headers", _GeneratedHeaders(_generated_range_headers(256, EXPECTED_HEADER_BYTES - 1) + (("Content-Type", "multipart/byteranges"),))), "OFNER-H0-TRANSPORT"),
            ("second_short", lambda values: setattr(values[2], "_body", values[2]._body[:-1]), "OFNER-H0-TRANSPORT"),
        ]
        for index, (name, mutator, expected_route) in enumerate(response_mutations):
            case_root = _new_generated_workspace(parent, f"transport-{index:02d}")
            report, _opener, _events = _run_generated_case(
                case_root, "result", response_mutator=mutator
            )
            if report["route"] != expected_route:
                raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", f"{name} route differs")
            routes[name] = str(report["refusal_code"])

        def manifest_target(payload: bytes) -> bytes:
            value = json.loads(payload)
            value["files"][0]["target"] = "forbidden"
            return source._canonical_json_bytes(value)

        manifest_root = _new_generated_workspace(parent, "manifest-target")
        report, _opener, _events = _run_generated_case(
            manifest_root, "result", manifest_mutator=manifest_target
        )
        if report["route"] != "OFNER-H0-TRANSPORT":
            raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "target firewall route differs")
        routes["manifest_target_field"] = str(report["refusal_code"])

        def wrong_version(payload: bytes) -> bytes:
            value = bytearray(payload)
            value[:8] = b"GDF 1.25"
            return bytes(value)

        def duplicate_roster(payload: bytes) -> bytes:
            value = bytearray(payload)
            value[272:288] = value[256:272]
            return bytes(value)

        def wrong_sampling(payload: bytes) -> bytes:
            value = bytearray(payload)
            offset = header.FIXED_HEADER_BYTES + 216 * header.EXPECTED_SIGNALS
            value[offset : offset + 4] = (256).to_bytes(4, "little")
            return bytes(value)

        representation_cases = (
            ("GDF_version", wrong_version),
            ("channel_roster", duplicate_roster),
            ("sampling_rate", wrong_sampling),
        )
        for index, (name, mutator) in enumerate(representation_cases):
            case_root = _new_generated_workspace(parent, f"representation-{index:02d}")
            report, _opener, _events = _run_generated_case(
                case_root, "result", fixture_mutator=mutator
            )
            if report["route"] != "OFNER-H0-REPRESENTATION":
                raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", f"{name} route differs")
            routes[name] = str(report["refusal_code"])

        retained_payload_bytes = sum(
            item.stat().st_size
            for item in parent.rglob("*")
            if item.is_file() and item.name != CONSUMED_MARKER_NAME and item.suffix != ".json"
        )
        if retained_payload_bytes != 0:
            raise OfnerGDFHeaderLiveRefusal("OHL-PROOF", "generated payload retained")

    runtime = time.monotonic() - started
    peak = max(peak_before, _peak_rss_bytes())
    if runtime > MAX_RUNTIME_SECONDS or peak > MAX_PEAK_RSS_BYTES:
        raise OfnerGDFHeaderLiveRefusal("OHL-RESOURCE", "qualification resource cap exceeded")
    result = {
        "schema_name": "neurodecodekit.ofner_gdf_header_live_generated_qualification",
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "status": "accepted_generated_only",
        "all_gates_passed": True,
        "measurements": {
            "generated_replays": 2,
            "mock_requests_per_replay": 3,
            "named_adversarial_refusals": len(routes),
            "generated_input_bytes": generated_bytes,
            "runtime_seconds": runtime,
            "peak_process_RSS_bytes": peak,
            "network_bytes": 0,
            "retained_generated_payload_bytes": 0,
        },
        "determinism": {
            "measurement_contracts_equal": True,
            "request_schedules_equal": True,
            "marker_precedes_opener": True,
        },
        "refusal_routes": routes,
        "real_operation_counters": _base_operation_counters(),
        "warnings": [
            "generated_mock_bytes_are_not_EEG",
            "qualification_made_no_network_request",
            "real_checkpoint_requires_exact_green_implementation_and_activation",
            "no_scientific_claim",
        ],
    }
    payload = _canonical_json_bytes(result)
    if len(payload) > MAX_PUBLIC_OUTPUT_BYTES:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "qualification output cap exceeded")
    output = Path(output_path).expanduser().absolute()
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_exclusive_durable(output, payload, mode=0o644)
    return result


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the activation-locked plan without opening live capability."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_green_decision(root)
    activation_present = (root / ACTIVATION_RELATIVE_PATH).is_file()
    return {
        "packet_id": PACKET_ID,
        "status": "activation_locked" if not activation_present else "activation_record_present",
        "member": {
            "path": MEMBER_PATH,
            "bytes": MEMBER_BYTES,
            "sha256": MEMBER_SHA256,
        },
        "manifest": {
            "URL": MANIFEST_URL,
            "canonical_bytes": EXPECTED_CANONICAL_MANIFEST_BYTES,
            "canonical_sha256": EXPECTED_CANONICAL_MANIFEST_SHA256,
        },
        "ranges": ["bytes=0-255", "bytes=256-(declared_header_length-1)"],
        "decision_commit": GREEN_DECISION_COMMIT,
        "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
        "implementation_record_present": (root / IMPLEMENTATION_RELATIVE_PATH).is_file(),
        "activation_record_present": activation_present,
        "real_invocation_available": False,
        "whole_file_requests": 0,
        "scientific_claim_established": False,
    }


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    candidate = Path(path).expanduser().absolute()
    try:
        info = os.lstat(candidate)
    except OSError as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "result unavailable") from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or not 0 < info.st_size <= MAX_PUBLIC_OUTPUT_BYTES
    ):
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "result type or cap differs")
    try:
        value = _strict_json(candidate.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "result parse failed") from exc
    if not isinstance(value, dict):
        raise OfnerGDFHeaderLiveRefusal("OHL-PUBLICATION", "result root differs")
    _validate_public_report(value)
    return value
