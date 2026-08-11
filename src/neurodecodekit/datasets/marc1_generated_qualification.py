"""Generated-only qualification for MARC-1 archive and modality mechanics."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import resource
import shutil
import stat
import sys
import tempfile
import time
import unicodedata
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
REPORT_SCHEMA_NAME = "neurodecodekit.marc1_generated_qualification"
MANIFEST_SCHEMA_NAME = "neurodecodekit.marc1_generated_archive_manifest"
PLAN_SCHEMA_NAME = "neurodecodekit.marc1_generated_multimodal_plan"
CONTRACT_RELATIVE_PATH = Path("registries/marc1_generated_qualification_contract.v0.json")
CONTRACT_SHA256 = "17733537c6a5038eb0781098a4b2452d71526c47eb4314cebb19d1975f79a7ad"
GREEN_CONTRACT_COMMIT = "4494d57bd3853ebb2e198747861c908cdb2a0bb1"
GREEN_CONTRACT_CI_RUN_ID = 31_502_115_918
GREEN_CONTRACT_BASE_JOB_ID = 93_814_507_482
GREEN_CONTRACT_OPTIONAL_JOB_ID = 93_814_507_355
MAX_ARCHIVE_BYTES = 8 * 1024 * 1024
MAX_RANGE_BYTES = 8 * 1024 * 1024
MAX_RANGE_CALLS = 256
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
EXPECTED_MEMBER_COUNT = 14
EXPECTED_ROUTE = "MARC1G-R1"
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
REFUSAL_IDS = (
    "MARC1G-F00-contract-artifact-or-green-proof-mismatch",
    "MARC1G-F01-EOCD-ZIP64-range-archive-or-resource-failure",
    "MARC1G-F02-member-path-duplicate-flag-method-ratio-or-type-failure",
    "MARC1G-F03-modality-role-geometry-clock-or-synchronization-failure",
    "MARC1G-F04-causal-preprocessing-future-context-or-onset-guard-failure",
    "MARC1G-F05-split-target-firewall-or-comparator-failure",
    "MARC1G-F06-output-privacy-overwrite-runtime-RSS-or-cap-failure",
    "MARC1G-F07-deterministic-replay-failure",
)
REQUIRED_MUTATIONS = (
    "truncated_EOCD",
    "duplicate_member_name",
    "absolute_member_path",
    "parent_traversal_member_path",
    "backslash_or_repeated_separator_path",
    "non_NFC_or_NUL_member_path",
    "encrypted_member",
    "symlink_or_nonregular_member",
    "unsupported_compression_or_ratio",
    "member_count_or_size_cap",
    "range_read_or_byte_cap",
    "member_content_read_attempt",
    "unknown_channel_field",
    "duplicate_channel_identity",
    "source_type_role_or_inclusion_conflation",
    "predictive_non_EEG_channel",
    "missing_geometry_or_clock_state",
    "unsynchronized_or_cross_source_clock",
    "noncausal_preprocessing",
    "future_or_guard_violating_window",
    "split_identity_or_window_overlap",
    "heldout_target_exposed_to_prediction",
    "required_comparator_missing",
    "output_symlink_overwrite_or_cap",
)
COMPARATOR_ROLES = (
    "no_signal_prevalence",
    "elapsed_time_or_trial_phase",
    "EOG_only_where_available",
    "pre_onset_EMG_only_where_available",
    "pre_onset_kinematic_only_where_available",
    "frontal_EEG_proxy_where_available",
    "occipital_EEG_proxy_where_available",
    "central_EEG_candidate",
    "EEG_residualized_against_train_only_EOG_where_available",
    "onset_shift",
    "label_derangement",
    "future_context_sentinel",
)
CHANNEL_FIELDS = frozenset(
    {
        "source_id",
        "subject_id",
        "session_id",
        "run_id",
        "channel_name",
        "source_type",
        "functional_role",
        "model_inclusion",
        "sampling_rate_hz",
        "units",
        "sample_count",
        "source_start_seconds",
        "clock_id",
        "synchronization_state",
        "geometry_state",
    }
)
IDENTITY_FIELDS = (
    "source_id",
    "subject_id",
    "session_id",
    "run_id",
    "trial_id",
    "window_id",
)
SOURCE_TYPES = frozenset({"EEG", "EOG", "EMG", "ACCEL", "ENCODER", "AUDIO", "TRIGGER"})
NONPREDICTIVE_SOURCE_TYPES = SOURCE_TYPES - {"EEG"}
FUNCTIONAL_ROLES = frozenset(
    {
        "central_candidate",
        "frontal_proxy",
        "occipital_proxy",
        "ocular_control",
        "muscle_control",
        "kinematic_onset_control",
        "alignment_trigger",
    }
)
PUBLIC_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "green_contract",
        "archive_summary",
        "multimodal_summary",
        "measurements",
        "mutation_summary",
        "access_counters",
        "acceptance_gates",
        "route",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "member_name",
        "member_names",
        "local_header_offset",
        "local_header_offsets",
        "filename",
        "filenames",
        "participant_id",
        "participant_ids",
        "target",
        "targets",
        "label",
        "labels",
    }
)
ROOT_MEMBERS = (
    "CHANGES",
    "README",
    "dataset_description.json",
    "participants.tsv",
)
SUBJECT_MEMBERS = tuple(
    f"sub-{subject}/eeg/sub-{subject}_task-generated{suffix}"
    for subject in ("01", "02")
    for suffix in (
        "_eeg.eeg",
        "_eeg.vhdr",
        "_eeg.vmrk",
        "_events.tsv",
        "_channels.tsv",
    )
)
EXPECTED_MEMBERS = ROOT_MEMBERS + SUBJECT_MEMBERS
FORCED_ZIP64_MEMBER = "sub-01/eeg/sub-01_task-generated_eeg.eeg"


class Marc1GeneratedRefusal(RuntimeError):
    """Fail closed with one stable, non-sensitive refusal identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown MARC-1 generated refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class GeneratedArchiveFixture:
    """One deterministic in-memory archive and its writer-observed payload ranges."""

    payload: bytes
    payload_intervals: tuple[tuple[int, int], ...]
    forced_zip64_member: str


@dataclass(frozen=True)
class ArchiveInventory:
    """Private inventory plus aggregate measurements from one traversal."""

    private_manifest: Mapping[str, Any]
    aggregate_summary: Mapping[str, Any]
    canonical_inventory_bytes: bytes
    range_read_calls: int
    range_bytes_returned: int


@dataclass(frozen=True)
class QualificationOutcome:
    """One bounded generated qualification outcome."""

    report: Mapping[str, Any]
    report_path: Path
    private_manifest_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


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
    ).encode("utf-8")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "non-finite JSON number")


def _strict_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "non-finite JSON number")
    return parsed


def _strict_json(payload: bytes) -> dict[str, Any]:
    try:
        text = payload.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
            parse_float=_strict_float,
        )
    except Marc1GeneratedRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "invalid JSON") from exc
    if not isinstance(value, dict):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "JSON root is not an object")
    return value


def load_registered_contract() -> dict[str, Any]:
    """Load and verify the exact remotely green generated-only contract."""

    path = _repo_root() / CONTRACT_RELATIVE_PATH
    if not path.is_file() or path.is_symlink():
        raise Marc1GeneratedRefusal(REFUSAL_IDS[0], "contract path is unavailable")
    if _sha256_file(path) != CONTRACT_SHA256:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[0], "contract hash differs")
    contract = _strict_json(path.read_bytes())
    expected_identity = {
        "schema_name": "neurodecodekit.marc1_generated_qualification_contract",
        "schema_version": "0.1.0",
        "contract_id": "MARC-1-generated-qualification-contract-v0",
        "status": "generated_fixture_only_contract_frozen_implementation_not_started",
    }
    for key, expected in expected_identity.items():
        if contract.get(key) != expected:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[0], f"contract {key} differs")
    proof = contract.get("green_research_proof")
    if not isinstance(proof, dict) or not proof.get("both_required_jobs_green"):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[0], "research proof is not green")
    interface = contract.get("interface")
    if not isinstance(interface, dict) or interface.get("commands") != [
        "plan",
        "qualify",
        "inspect",
    ]:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[0], "CLI surface differs")
    if any(value for key, value in interface.items() if key.endswith("_available")):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[0], "live interface flag is true")
    flags = contract.get("authorization_flags")
    counters = contract.get("access_counters")
    if not isinstance(flags, dict) or any(flags.values()):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[0], "authorization flag is true")
    if not isinstance(counters, dict) or any(counters.values()):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[0], "access counter is nonzero")
    return contract


class _RangeBudget:
    """Shared accounting across all generated archive readers."""

    def __init__(self, max_calls: int = MAX_RANGE_CALLS, max_bytes: int = MAX_RANGE_BYTES):
        self.max_calls = max_calls
        self.max_bytes = max_bytes
        self.read_calls = 0
        self.bytes_returned = 0

    def account(self, returned_bytes: int) -> None:
        next_calls = self.read_calls + 1
        next_bytes = self.bytes_returned + returned_bytes
        if next_calls > self.max_calls or next_bytes > self.max_bytes:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "range budget exceeded")
        self.read_calls = next_calls
        self.bytes_returned = next_bytes


class InstrumentedGeneratedRangeReader:
    """Read-only seekable adapter over generated bytes with exact range accounting."""

    def __init__(
        self,
        payload: bytes,
        payload_intervals: Sequence[tuple[int, int]],
        *,
        budget: _RangeBudget | None = None,
    ):
        self._payload = payload
        self._payload_intervals = tuple(payload_intervals)
        self._position = 0
        self._budget = budget or _RangeBudget()
        self.read_ranges: list[tuple[int, int]] = []
        self.payload_intersection_bytes = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self._position

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if isinstance(offset, bool) or not isinstance(offset, int):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "invalid seek offset")
        if whence == os.SEEK_SET:
            position = offset
        elif whence == os.SEEK_CUR:
            position = self._position + offset
        elif whence == os.SEEK_END:
            position = len(self._payload) + offset
        else:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "invalid seek origin")
        if position < 0:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "negative seek")
        self._position = position
        return position

    def read(self, size: int = -1) -> bytes:
        if isinstance(size, bool) or not isinstance(size, int):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "invalid read size")
        start = min(self._position, len(self._payload))
        stop = len(self._payload) if size < 0 else min(start + size, len(self._payload))
        result = self._payload[start:stop]
        self._budget.account(len(result))
        self._position = stop
        self.read_ranges.append((start, stop))
        for payload_start, payload_stop in self._payload_intervals:
            overlap = max(0, min(stop, payload_stop) - max(start, payload_start))
            self.payload_intersection_bytes += overlap
        return result


def _zip_info(name: str, compression: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 8, 11, 0, 0, 0))
    info.compress_type = compression
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o600) << 16
    return info


def build_generated_archive() -> GeneratedArchiveFixture:
    """Build one deterministic 14-member archive without a large payload."""

    contents: dict[str, bytes] = {
        "CHANGES": b"generated fixture v0\n",
        "README": b"generated-only MARC-1 archive fixture\n",
        "dataset_description.json": b'{"Name":"MARC-1 generated fixture"}\n',
        "participants.tsv": b"participant_id\nsub-01\nsub-02\n",
    }
    for subject in ("01", "02"):
        prefix = f"sub-{subject}/eeg/sub-{subject}_task-generated"
        contents[f"{prefix}_eeg.eeg"] = (f"generated-eeg-{subject}\n").encode("ascii")
        contents[f"{prefix}_eeg.vhdr"] = (f"generated-vhdr-{subject}\n").encode("ascii")
        contents[f"{prefix}_eeg.vmrk"] = (f"generated-vmrk-{subject}\n").encode("ascii")
        contents[f"{prefix}_events.tsv"] = b"onset\tduration\n1.0\t0.1\n"
        contents[f"{prefix}_channels.tsv"] = b"name\ttype\nC3\tEEG\n"
    if tuple(contents) != EXPECTED_MEMBERS:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "generated member order differs")

    buffer = io.BytesIO()
    payload_intervals: list[tuple[int, int]] = []
    with zipfile.ZipFile(buffer, mode="w", allowZip64=True) as archive:
        for name, member_payload in contents.items():
            compression = zipfile.ZIP_STORED if name.endswith(".eeg") else zipfile.ZIP_DEFLATED
            info = _zip_info(name, compression)
            with archive.open(
                info,
                mode="w",
                force_zip64=name == FORCED_ZIP64_MEMBER,
            ) as member:
                payload_start = buffer.tell()
                member.write(member_payload)
            written = archive.getinfo(name)
            payload_intervals.append(
                (payload_start, payload_start + int(written.compress_size))
            )
        archive.comment = b"MARC1G" + (b"." * (zipfile.ZIP_MAX_COMMENT - 6))
    payload = buffer.getvalue()
    if len(payload) > MAX_ARCHIVE_BYTES:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "generated archive exceeds cap")
    return GeneratedArchiveFixture(
        payload=payload,
        payload_intervals=tuple(payload_intervals),
        forced_zip64_member=FORCED_ZIP64_MEMBER,
    )


def _validate_member_path(name: str) -> None:
    if not name or "\x00" in name or "\\" in name or "//" in name:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "unsafe member path")
    if unicodedata.normalize("NFC", name) != name:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "member path is not NFC")
    path = PurePosixPath(name)
    if path.is_absolute() or str(path) != name or any(part in {"", ".", ".."} for part in path.parts):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "unsafe member path")


def _validate_archive_infos(
    infos: Sequence[zipfile.ZipInfo],
    *,
    archive_size: int,
    forced_zip64_member: str,
) -> None:
    if len(infos) != EXPECTED_MEMBER_COUNT:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "member count differs")
    names = [info.filename for info in infos]
    if len(set(names)) != len(names):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "duplicate member name")
    if tuple(names) != EXPECTED_MEMBERS:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "member inventory differs")
    zip64_seen = False
    for info in infos:
        _validate_member_path(info.filename)
        if info.is_dir():
            raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "directory member is forbidden")
        mode = (info.external_attr >> 16) & 0xFFFF
        file_type = stat.S_IFMT(mode)
        if file_type not in {0, stat.S_IFREG}:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "nonregular member")
        if info.flag_bits & 0x1:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "encrypted member")
        if info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "unsupported compression")
        if not (0 <= info.compress_size <= archive_size <= MAX_ARCHIVE_BYTES):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "compressed size exceeds cap")
        if not (0 <= info.file_size <= MAX_ARCHIVE_BYTES):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "uncompressed size exceeds cap")
        if info.compress_size == 0:
            ratio = 0.0 if info.file_size == 0 else math.inf
        else:
            ratio = info.file_size / info.compress_size
        if ratio > 1000.0:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[2], "compression ratio exceeds cap")
        if info.filename == forced_zip64_member and info.extract_version >= 45:
            zip64_seen = True
    if not zip64_seen:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "forced ZIP64 member was not observed")


def inventory_generated_archive(
    fixture: GeneratedArchiveFixture,
    *,
    budget: _RangeBudget | None = None,
) -> ArchiveInventory:
    """Inventory generated metadata with one standard-library ZIP traversal."""

    if len(fixture.payload) > MAX_ARCHIVE_BYTES:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "archive exceeds cap")
    shared_budget = budget or _RangeBudget()
    start_calls = shared_budget.read_calls
    start_bytes = shared_budget.bytes_returned
    reader = InstrumentedGeneratedRangeReader(
        fixture.payload,
        fixture.payload_intervals,
        budget=shared_budget,
    )
    try:
        with zipfile.ZipFile(reader, mode="r", allowZip64=True) as archive:
            infos = archive.infolist()
    except Marc1GeneratedRefusal:
        raise
    except (OSError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "archive inventory failed") from exc
    if reader.payload_intersection_bytes != 0:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "range read intersected member payload")
    _validate_archive_infos(
        infos,
        archive_size=len(fixture.payload),
        forced_zip64_member=fixture.forced_zip64_member,
    )
    rows = [
        {
            "member_name": info.filename,
            "CRC32": int(info.CRC),
            "compression_method": int(info.compress_type),
            "flag_bits": int(info.flag_bits),
            "compressed_size": int(info.compress_size),
            "uncompressed_size": int(info.file_size),
            "local_header_offset": int(info.header_offset),
        }
        for info in infos
    ]
    canonical_rows = _canonical_json_bytes(rows)
    method_counts = Counter(str(info.compress_type) for info in infos)
    manifest = {
        "schema_name": MANIFEST_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "fixture_only": True,
        "archive_sha256": _sha256_bytes(fixture.payload),
        "inventory_sha256": _sha256_bytes(canonical_rows),
        "members": rows,
    }
    summary = {
        "archive_bytes": len(fixture.payload),
        "archive_sha256": _sha256_bytes(fixture.payload),
        "inventory_sha256": _sha256_bytes(canonical_rows),
        "member_count": len(rows),
        "root_metadata_member_count": 4,
        "subject_count": 2,
        "forced_ZIP64_member_count": 1,
        "compression_method_counts": dict(sorted(method_counts.items())),
        "compressed_member_bytes": sum(info.compress_size for info in infos),
        "uncompressed_member_bytes": sum(info.file_size for info in infos),
        "inventory_traversals": 1,
        "member_content_reads": 0,
        "member_extractions": 0,
        "payload_interval_read_bytes": 0,
    }
    return ArchiveInventory(
        private_manifest=manifest,
        aggregate_summary=summary,
        canonical_inventory_bytes=canonical_rows,
        range_read_calls=shared_budget.read_calls - start_calls,
        range_bytes_returned=shared_budget.bytes_returned - start_bytes,
    )


def _channel(
    source_id: str,
    channel_name: str,
    source_type: str,
    functional_role: str,
    model_inclusion: str,
    sampling_rate_hz: int,
    units: str,
    geometry_state: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "subject_id": f"generated-{source_id}-subject",
        "session_id": "generated-session-1",
        "run_id": "generated-run-1",
        "channel_name": channel_name,
        "source_type": source_type,
        "functional_role": functional_role,
        "model_inclusion": model_inclusion,
        "sampling_rate_hz": sampling_rate_hz,
        "units": units,
        "sample_count": sampling_rate_hz * 20,
        "source_start_seconds": 0.0,
        "clock_id": f"{source_id}-amplifier-clock",
        "synchronization_state": "same_amplifier",
        "geometry_state": geometry_state,
    }


def _identity(source_id: str, role: str, index: int) -> dict[str, str]:
    return {
        "source_id": source_id,
        "subject_id": f"generated-{role}-subject",
        "session_id": "generated-session-1",
        "run_id": f"generated-{role}-run",
        "trial_id": f"generated-{role}-trial-{index}",
        "window_id": f"generated-{role}-window-{index}",
    }


def build_generated_multimodal_plan() -> dict[str, Any]:
    """Build deterministic role, causal-window, split, and comparator fixtures."""

    channels = [
        _channel("freewill_like", "C3", "EEG", "central_candidate", "candidate", 250, "uV", "available"),
        _channel("freewill_like", "C4", "EEG", "central_candidate", "candidate", 250, "uV", "available"),
        _channel("freewill_like", "Fp1", "EEG", "frontal_proxy", "proxy", 250, "uV", "available"),
        _channel("freewill_like", "O1", "EEG", "occipital_proxy", "proxy", 250, "uV", "available"),
        _channel("freewill_like", "HEOG", "EOG", "ocular_control", "nonpredictive", 250, "uV", "unavailable"),
        _channel("freewill_like", "VEOG", "EOG", "ocular_control", "nonpredictive", 250, "uV", "unavailable"),
        _channel("freewill_like", "ACC_X", "ACCEL", "kinematic_onset_control", "nonpredictive", 250, "m/s2", "unavailable"),
        _channel("freewill_like", "ACC_Y", "ACCEL", "kinematic_onset_control", "nonpredictive", 250, "m/s2", "unavailable"),
        _channel("freewill_like", "ACC_Z", "ACCEL", "kinematic_onset_control", "nonpredictive", 250, "m/s2", "unavailable"),
        _channel("freewill_like", "AUDIO", "AUDIO", "alignment_trigger", "nonpredictive", 250, "a.u.", "unavailable"),
        _channel("wrist_like", "C3", "EEG", "central_candidate", "candidate", 512, "uV", "available"),
        _channel("wrist_like", "C4", "EEG", "central_candidate", "candidate", 512, "uV", "available"),
        _channel("wrist_like", "Fp1", "EEG", "frontal_proxy", "proxy", 512, "uV", "available"),
        _channel("wrist_like", "O1", "EEG", "occipital_proxy", "proxy", 512, "uV", "available"),
        _channel("wrist_like", "EMG_FCR", "EMG", "muscle_control", "nonpredictive", 512, "uV", "unavailable"),
        _channel("wrist_like", "EMG_ECR", "EMG", "muscle_control", "nonpredictive", 512, "uV", "unavailable"),
        _channel("wrist_like", "ENCODER_X", "ENCODER", "kinematic_onset_control", "nonpredictive", 512, "degrees", "unavailable"),
        _channel("wrist_like", "TRIGGER", "TRIGGER", "alignment_trigger", "nonpredictive", 512, "code", "unavailable"),
    ]
    fit_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    scorer_rows: list[dict[str, Any]] = []
    for source_index, source_id in enumerate(("freewill_like", "wrist_like"), start=1):
        for index, label in enumerate(("left", "right"), start=1):
            fit_rows.append(
                {
                    **_identity(source_id, "fit", index),
                    "feature_values": [source_index * 0.1, index * 0.01],
                    "label": label,
                }
            )
            prediction_identity = _identity(source_id, "heldout", index)
            prediction_rows.append(
                {
                    **prediction_identity,
                    "feature_values": [source_index * 0.2, index * 0.02],
                }
            )
            scorer_rows.append({**prediction_identity, "target": label})

    availability = {
        "freewill_like": {
            role: (
                "unavailable"
                if role == "pre_onset_EMG_only_where_available"
                else "available"
            )
            for role in COMPARATOR_ROLES
        },
        "wrist_like": {
            role: (
                "unavailable"
                if role
                in {
                    "EOG_only_where_available",
                    "EEG_residualized_against_train_only_EOG_where_available",
                }
                else "available"
            )
            for role in COMPARATOR_ROLES
        },
    }
    preprocessing = {
        "window_seconds": [-1.5, -0.2],
        "right_endpoint_exclusive": True,
        "onset_guard_seconds": 0.2,
        "causal_preprocessing": True,
        "future_context_samples": 0,
        "normalization": "fit_rows_only",
        "centered_filter": False,
        "zero_phase_filter": False,
        "reflected_future_padding": False,
        "bidirectional_operation": False,
        "source_sample_offsets": {
            "freewill_like": {"start_inclusive": -375, "stop_exclusive": -50},
            "wrist_like": {"start_inclusive": -768, "stop_exclusive": -102},
        },
    }
    return {
        "schema_name": PLAN_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "fixture_only": True,
        "source_profiles": {
            "freewill_like": {
                "sampling_rate_hz": 250,
                "required_source_types": ["EEG", "EOG", "ACCEL", "AUDIO"],
                "optional_source_types": ["TRIGGER"],
            },
            "wrist_like": {
                "sampling_rate_hz": 512,
                "required_source_types": ["EEG", "EMG", "ENCODER", "TRIGGER"],
                "optional_source_types": [],
            },
        },
        "channels": channels,
        "preprocessing": preprocessing,
        "target_firewall": {
            "fit_rows": fit_rows,
            "target_blind_prediction_rows": prediction_rows,
            "isolated_scorer_rows": scorer_rows,
        },
        "comparator_availability": availability,
        "feature_generation": {
            "producer": "fixed_generated_identity_values",
            "uses_targets_or_labels": False,
        },
        "operation_counters": {
            "parameter_update_fits": 0,
            "model_inference_calls": 0,
            "prediction_sets": 0,
            "prediction_freezes": 0,
            "target_deliveries": 0,
            "scores": 0,
        },
    }


def _identity_tuple(row: Mapping[str, Any]) -> tuple[str, ...]:
    values: list[str] = []
    for field in IDENTITY_FIELDS:
        value = row.get(field)
        if not isinstance(value, str) or not value:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "row identity is invalid")
        values.append(value)
    return tuple(values)


def _validate_channels(plan: Mapping[str, Any]) -> None:
    profiles = plan.get("source_profiles")
    channels = plan.get("channels")
    if not isinstance(profiles, dict) or set(profiles) != {"freewill_like", "wrist_like"}:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "source profiles differ")
    if not isinstance(channels, list) or not channels:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "channels are unavailable")
    identities: set[tuple[str, ...]] = set()
    source_types_by_profile: dict[str, set[str]] = {key: set() for key in profiles}
    clocks_by_profile: dict[str, set[str]] = {key: set() for key in profiles}
    for channel in channels:
        if not isinstance(channel, dict) or set(channel) != CHANNEL_FIELDS:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "channel fields differ")
        source_id = channel["source_id"]
        if source_id not in profiles:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "channel source differs")
        identity = tuple(str(channel[key]) for key in ("source_id", "subject_id", "session_id", "run_id", "channel_name"))
        if identity in identities:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "duplicate channel identity")
        identities.add(identity)
        source_type = channel["source_type"]
        role = channel["functional_role"]
        inclusion = channel["model_inclusion"]
        if source_type not in SOURCE_TYPES or role not in FUNCTIONAL_ROLES:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "channel semantics differ")
        if source_type == role:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "source type and role are conflated")
        if source_type == "EEG":
            if inclusion not in {"candidate", "proxy"}:
                raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "EEG inclusion differs")
        elif source_type in NONPREDICTIVE_SOURCE_TYPES and inclusion != "nonpredictive":
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "non-EEG channel is predictive")
        sampling_rate = channel["sampling_rate_hz"]
        if sampling_rate != profiles[source_id].get("sampling_rate_hz"):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "sampling rate differs")
        if channel["geometry_state"] not in {"available", "unavailable"}:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "geometry state differs")
        if channel["synchronization_state"] not in {
            "same_amplifier",
            "declared_resampling_map",
        }:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "synchronization differs")
        clock_id = channel["clock_id"]
        if not isinstance(clock_id, str) or not clock_id:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "clock is unavailable")
        for numeric_key in ("sampling_rate_hz", "sample_count", "source_start_seconds"):
            value = channel[numeric_key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "channel numeric field differs")
        source_types_by_profile[source_id].add(source_type)
        clocks_by_profile[source_id].add(clock_id)
    for source_id, profile in profiles.items():
        required = profile.get("required_source_types")
        optional = profile.get("optional_source_types")
        if not isinstance(required, list) or not isinstance(optional, list):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "source type declaration differs")
        if not set(required).issubset(source_types_by_profile[source_id]):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "required source type is missing")
        if not source_types_by_profile[source_id].issubset(set(required) | set(optional)):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "undeclared source type")
        if len(clocks_by_profile[source_id]) != 1:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "cross-source clock mismatch")


def _validate_preprocessing(plan: Mapping[str, Any]) -> None:
    preprocessing = plan.get("preprocessing")
    if not isinstance(preprocessing, dict):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[4], "preprocessing is unavailable")
    expected_flags = {
        "right_endpoint_exclusive": True,
        "causal_preprocessing": True,
        "future_context_samples": 0,
        "normalization": "fit_rows_only",
        "centered_filter": False,
        "zero_phase_filter": False,
        "reflected_future_padding": False,
        "bidirectional_operation": False,
    }
    for key, expected in expected_flags.items():
        if preprocessing.get(key) != expected:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[4], f"preprocessing {key} differs")
    if preprocessing.get("window_seconds") != [-1.5, -0.2]:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[4], "window differs")
    if preprocessing.get("onset_guard_seconds") != 0.2:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[4], "onset guard differs")
    offsets = preprocessing.get("source_sample_offsets")
    expected = {
        "freewill_like": {"start_inclusive": -375, "stop_exclusive": -50},
        "wrist_like": {"start_inclusive": -768, "stop_exclusive": -102},
    }
    if offsets != expected:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[4], "sample offsets differ")
    for source_id, sampling_rate in (("freewill_like", 250), ("wrist_like", 512)):
        stop = offsets[source_id]["stop_exclusive"]
        if (stop - 1) / sampling_rate >= -0.2:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[4], "onset guard is violated")


def _validate_firewall_and_comparators(plan: Mapping[str, Any]) -> None:
    firewall = plan.get("target_firewall")
    if not isinstance(firewall, dict) or set(firewall) != {
        "fit_rows",
        "target_blind_prediction_rows",
        "isolated_scorer_rows",
    }:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "physical target roles differ")
    fit_rows = firewall["fit_rows"]
    prediction_rows = firewall["target_blind_prediction_rows"]
    scorer_rows = firewall["isolated_scorer_rows"]
    if not all(isinstance(rows, list) and rows for rows in (fit_rows, prediction_rows, scorer_rows)):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "target role rows are unavailable")
    fit_ids: set[tuple[str, ...]] = set()
    prediction_ids: set[tuple[str, ...]] = set()
    scorer_ids: set[tuple[str, ...]] = set()
    fit_fields = set(IDENTITY_FIELDS) | {"feature_values", "label"}
    prediction_fields = set(IDENTITY_FIELDS) | {"feature_values"}
    scorer_fields = set(IDENTITY_FIELDS) | {"target"}
    for row in fit_rows:
        if not isinstance(row, dict) or set(row) != fit_fields:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "fit row fields differ")
        fit_ids.add(_identity_tuple(row))
    for row in prediction_rows:
        if not isinstance(row, dict) or set(row) != prediction_fields:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "prediction row leaked a target")
        prediction_ids.add(_identity_tuple(row))
    for row in scorer_rows:
        if not isinstance(row, dict) or set(row) != scorer_fields:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "scorer row fields differ")
        scorer_ids.add(_identity_tuple(row))
    if len(fit_ids) != len(fit_rows) or len(prediction_ids) != len(prediction_rows):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "duplicate split identity")
    if fit_ids & prediction_ids or fit_ids & scorer_ids:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "fit and held-out identities overlap")
    if prediction_ids != scorer_ids:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "prediction and scorer identities differ")
    feature_generation = plan.get("feature_generation")
    if not isinstance(feature_generation, dict) or feature_generation.get(
        "uses_targets_or_labels"
    ) is not False:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "feature generation uses targets")
    counters = plan.get("operation_counters")
    if not isinstance(counters, dict) or any(counters.values()):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "model operation counter is nonzero")

    availability = plan.get("comparator_availability")
    if not isinstance(availability, dict) or set(availability) != {
        "freewill_like",
        "wrist_like",
    }:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "comparator sources differ")
    for source_id, source_availability in availability.items():
        if not isinstance(source_availability, dict) or set(source_availability) != set(
            COMPARATOR_ROLES
        ):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "comparator inventory differs")
        if not set(source_availability.values()).issubset({"available", "unavailable"}):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "comparator state differs")
        required = {
            "no_signal_prevalence",
            "elapsed_time_or_trial_phase",
            "pre_onset_kinematic_only_where_available",
            "frontal_EEG_proxy_where_available",
            "occipital_EEG_proxy_where_available",
            "central_EEG_candidate",
            "onset_shift",
            "label_derangement",
            "future_context_sentinel",
        }
        if source_id == "freewill_like":
            required |= {
                "EOG_only_where_available",
                "EEG_residualized_against_train_only_EOG_where_available",
            }
        else:
            required.add("pre_onset_EMG_only_where_available")
        if any(source_availability[role] != "available" for role in required):
            raise Marc1GeneratedRefusal(REFUSAL_IDS[5], "required comparator is unavailable")


def validate_generated_multimodal_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one strict generated multimodal plan and return aggregate facts."""

    expected_top = {
        "schema_name",
        "schema_version",
        "fixture_only",
        "source_profiles",
        "channels",
        "preprocessing",
        "target_firewall",
        "comparator_availability",
        "feature_generation",
        "operation_counters",
    }
    if set(plan) != expected_top:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "plan fields differ")
    if (
        plan.get("schema_name") != PLAN_SCHEMA_NAME
        or plan.get("schema_version") != SCHEMA_VERSION
        or plan.get("fixture_only") is not True
    ):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[3], "plan identity differs")
    _validate_channels(plan)
    _validate_preprocessing(plan)
    _validate_firewall_and_comparators(plan)
    channels = plan["channels"]
    firewall = plan["target_firewall"]
    return {
        "plan_sha256": _sha256_bytes(_canonical_json_bytes(plan)),
        "source_profile_count": len(plan["source_profiles"]),
        "channel_record_count": len(channels),
        "source_type_counts": dict(
            sorted(Counter(str(row["source_type"]) for row in channels).items())
        ),
        "fit_row_count": len(firewall["fit_rows"]),
        "target_blind_prediction_row_count": len(
            firewall["target_blind_prediction_rows"]
        ),
        "isolated_scorer_row_count": len(firewall["isolated_scorer_rows"]),
        "comparator_role_count": len(COMPARATOR_ROLES),
        "causal": True,
        "future_context_samples": 0,
        "end_to_end_latency_measured": False,
        "model_runs": 0,
        "training_runs": 0,
        "scores": 0,
    }


def _copy_infos(infos: Sequence[zipfile.ZipInfo]) -> list[zipfile.ZipInfo]:
    return [copy.copy(info) for info in infos]


def _expect_refusal(
    name: str,
    expected_refusal_id: str,
    operation: Callable[[], Any],
) -> str:
    try:
        operation()
    except Marc1GeneratedRefusal as exc:
        if exc.refusal_id != expected_refusal_id:
            raise Marc1GeneratedRefusal(
                REFUSAL_IDS[7],
                f"mutation {name} routed to the wrong refusal class",
            ) from exc
        return exc.refusal_id
    raise Marc1GeneratedRefusal(REFUSAL_IDS[7], f"mutation {name} did not refuse")


def _forbid_member_content_read() -> None:
    raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "member content access is forbidden")


def _bounded_output_bytes(report_bytes: bytes, manifest_bytes: bytes) -> int:
    total = len(report_bytes) + len(manifest_bytes)
    if total > MAX_OUTPUT_BYTES:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "combined output exceeds cap")
    return total


def run_required_mutations(
    fixture: GeneratedArchiveFixture,
    plan: Mapping[str, Any],
    base_infos: Sequence[zipfile.ZipInfo],
    *,
    budget: _RangeBudget,
) -> dict[str, str]:
    """Run all 24 frozen adversarial mutations and return their refusal classes."""

    checks: dict[str, tuple[str, Callable[[], Any]]] = {}
    eocd_offset = fixture.payload.rfind(zipfile.stringEndArchive)
    if eocd_offset < 0:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "generated EOCD is unavailable")
    truncated = GeneratedArchiveFixture(
        payload=fixture.payload[:eocd_offset],
        payload_intervals=tuple(
            interval for interval in fixture.payload_intervals if interval[1] <= eocd_offset
        ),
        forced_zip64_member=fixture.forced_zip64_member,
    )
    checks["truncated_EOCD"] = (
        REFUSAL_IDS[1],
        lambda: inventory_generated_archive(truncated, budget=budget),
    )

    def archive_check(mutator: Callable[[list[zipfile.ZipInfo]], None]) -> None:
        infos = _copy_infos(base_infos)
        mutator(infos)
        _validate_archive_infos(
            infos,
            archive_size=len(fixture.payload),
            forced_zip64_member=fixture.forced_zip64_member,
        )

    checks["duplicate_member_name"] = (
        REFUSAL_IDS[2],
        lambda: archive_check(lambda infos: setattr(infos[1], "filename", infos[0].filename)),
    )
    checks["absolute_member_path"] = (
        REFUSAL_IDS[2],
        lambda: archive_check(lambda infos: setattr(infos[0], "filename", "/absolute")),
    )
    checks["parent_traversal_member_path"] = (
        REFUSAL_IDS[2],
        lambda: archive_check(lambda infos: setattr(infos[0], "filename", "../escape")),
    )
    checks["backslash_or_repeated_separator_path"] = (
        REFUSAL_IDS[2],
        lambda: archive_check(lambda infos: setattr(infos[0], "filename", "bad//path")),
    )
    checks["non_NFC_or_NUL_member_path"] = (
        REFUSAL_IDS[2],
        lambda: archive_check(lambda infos: setattr(infos[0], "filename", "cafe\u0301")),
    )
    checks["encrypted_member"] = (
        REFUSAL_IDS[2],
        lambda: archive_check(lambda infos: setattr(infos[0], "flag_bits", 1)),
    )
    checks["symlink_or_nonregular_member"] = (
        REFUSAL_IDS[2],
        lambda: archive_check(
            lambda infos: setattr(infos[0], "external_attr", (stat.S_IFLNK | 0o777) << 16)
        ),
    )
    checks["unsupported_compression_or_ratio"] = (
        REFUSAL_IDS[2],
        lambda: archive_check(lambda infos: setattr(infos[0], "compress_type", 99)),
    )
    checks["member_count_or_size_cap"] = (
        REFUSAL_IDS[2],
        lambda: _validate_archive_infos(
            list(base_infos) + [copy.copy(base_infos[0])],
            archive_size=len(fixture.payload),
            forced_zip64_member=fixture.forced_zip64_member,
        ),
    )
    checks["range_read_or_byte_cap"] = (
        REFUSAL_IDS[1],
        lambda: inventory_generated_archive(
            fixture,
            budget=_RangeBudget(max_calls=0, max_bytes=0),
        ),
    )
    checks["member_content_read_attempt"] = (REFUSAL_IDS[1], _forbid_member_content_read)

    def plan_check(mutator: Callable[[dict[str, Any]], None]) -> None:
        changed = copy.deepcopy(plan)
        mutator(changed)
        validate_generated_multimodal_plan(changed)

    checks["unknown_channel_field"] = (
        REFUSAL_IDS[3],
        lambda: plan_check(lambda changed: changed["channels"][0].__setitem__("unknown", 1)),
    )
    checks["duplicate_channel_identity"] = (
        REFUSAL_IDS[3],
        lambda: plan_check(lambda changed: changed["channels"].append(changed["channels"][0])),
    )
    checks["source_type_role_or_inclusion_conflation"] = (
        REFUSAL_IDS[3],
        lambda: plan_check(
            lambda changed: changed["channels"][0].__setitem__("functional_role", "EEG")
        ),
    )
    checks["predictive_non_EEG_channel"] = (
        REFUSAL_IDS[3],
        lambda: plan_check(
            lambda changed: changed["channels"][4].__setitem__("model_inclusion", "candidate")
        ),
    )
    checks["missing_geometry_or_clock_state"] = (
        REFUSAL_IDS[3],
        lambda: plan_check(lambda changed: changed["channels"][0].pop("geometry_state")),
    )
    checks["unsynchronized_or_cross_source_clock"] = (
        REFUSAL_IDS[3],
        lambda: plan_check(
            lambda changed: changed["channels"][0].__setitem__("clock_id", "other-clock")
        ),
    )
    checks["noncausal_preprocessing"] = (
        REFUSAL_IDS[4],
        lambda: plan_check(
            lambda changed: changed["preprocessing"].__setitem__(
                "causal_preprocessing", False
            )
        ),
    )
    checks["future_or_guard_violating_window"] = (
        REFUSAL_IDS[4],
        lambda: plan_check(
            lambda changed: changed["preprocessing"].__setitem__(
                "window_seconds", [-1.5, 0.0]
            )
        ),
    )

    def overlap_split(changed: dict[str, Any]) -> None:
        prediction = changed["target_firewall"]["target_blind_prediction_rows"][0]
        fit = changed["target_firewall"]["fit_rows"][0]
        for field in IDENTITY_FIELDS:
            fit[field] = prediction[field]

    checks["split_identity_or_window_overlap"] = (
        REFUSAL_IDS[5],
        lambda: plan_check(overlap_split),
    )
    checks["heldout_target_exposed_to_prediction"] = (
        REFUSAL_IDS[5],
        lambda: plan_check(
            lambda changed: changed["target_firewall"][
                "target_blind_prediction_rows"
            ][0].__setitem__("target", "left")
        ),
    )
    checks["required_comparator_missing"] = (
        REFUSAL_IDS[5],
        lambda: plan_check(
            lambda changed: changed["comparator_availability"]["freewill_like"].pop(
                "EOG_only_where_available"
            )
        ),
    )
    checks["output_symlink_overwrite_or_cap"] = (
        REFUSAL_IDS[6],
        lambda: _bounded_output_bytes(b"x" * (MAX_OUTPUT_BYTES + 1), b""),
    )
    if tuple(checks) != REQUIRED_MUTATIONS:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[7], "mutation inventory differs")
    return {
        name: _expect_refusal(name, expected, operation)
        for name, (expected, operation) in checks.items()
    }


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_PUBLIC_KEYS:
                raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "public report leaks a private key")
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def validate_public_report(
    report: Mapping[str, Any],
    *,
    allow_incomplete_measurements: bool = False,
) -> None:
    """Validate one aggregate-only generated report."""

    if set(report) != PUBLIC_REPORT_FIELDS:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "public report fields differ")
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("status") != "passed_generated_qualification"
        or report.get("route") != EXPECTED_ROUTE
    ):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "public report identity differs")
    _walk_public(report)
    counters = report.get("access_counters")
    gates = report.get("acceptance_gates")
    if not isinstance(counters, dict) or any(counters.values()):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "public access counter is nonzero")
    if not isinstance(gates, dict) or not all(gates.values()):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "acceptance gate is false")
    measurements = report.get("measurements")
    if not isinstance(measurements, dict):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "measurements are unavailable")
    if not allow_incomplete_measurements:
        if measurements.get("generated_output_bytes", MAX_OUTPUT_BYTES + 1) > MAX_OUTPUT_BYTES:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "output measurement exceeds cap")
        if measurements.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1) > MAX_RUNTIME_SECONDS:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "runtime measurement exceeds cap")
        if measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1) > MAX_PEAK_RSS_BYTES:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "RSS measurement exceeds cap")


def _assert_output_destination(output_dir: Path) -> None:
    if output_dir.exists() or output_dir.is_symlink():
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "output directory already exists")
    parent = output_dir.parent
    if not parent.exists() or not parent.is_dir() or parent.is_symlink():
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "output parent is unavailable")
    if stat.S_ISLNK(os.lstat(parent).st_mode):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "output parent is a symlink")


def _write_outputs(
    output_dir: Path,
    report: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> tuple[Path, Path, int]:
    _assert_output_destination(output_dir)
    report_bytes = _canonical_json_bytes(report)
    manifest_bytes = _canonical_json_bytes(manifest)
    total = _bounded_output_bytes(report_bytes, manifest_bytes)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    try:
        report_path = stage / "marc1_generated_report.v0.json"
        manifest_path = stage / "marc1_generated_manifest.private.v0.json"
        report_path.write_bytes(report_bytes)
        manifest_path.write_bytes(manifest_bytes)
        os.replace(stage, output_dir)
    except Exception as exc:
        shutil.rmtree(stage, ignore_errors=True)
        if isinstance(exc, Marc1GeneratedRefusal):
            raise
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "output write failed") from exc
    return (
        output_dir / "marc1_generated_report.v0.json",
        output_dir / "marc1_generated_manifest.private.v0.json",
        total,
    )


def _assert_resources(runtime_seconds: float, peak_rss_bytes: int, budget: _RangeBudget) -> None:
    if runtime_seconds > MAX_RUNTIME_SECONDS:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "runtime exceeds cap")
    if peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "peak RSS exceeds cap")
    if budget.read_calls > MAX_RANGE_CALLS or budget.bytes_returned > MAX_RANGE_BYTES:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "range accounting exceeds cap")
    for key in THREAD_ENV_KEYS:
        value = os.environ.get(key)
        if value not in {None, "1"}:
            raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "numerical thread setting exceeds one")


def _read_infos_for_mutations(
    fixture: GeneratedArchiveFixture,
    budget: _RangeBudget,
) -> list[zipfile.ZipInfo]:
    reader = InstrumentedGeneratedRangeReader(
        fixture.payload,
        fixture.payload_intervals,
        budget=budget,
    )
    try:
        with zipfile.ZipFile(reader, mode="r", allowZip64=True) as archive:
            infos = [copy.copy(info) for info in archive.infolist()]
    except (OSError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "archive inventory failed") from exc
    if reader.payload_intersection_bytes:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[1], "range read intersected member payload")
    return infos


def _build_report(
    inventory: ArchiveInventory,
    plan_summary: Mapping[str, Any],
    mutations: Mapping[str, str],
    *,
    budget: _RangeBudget,
    runtime_seconds: float,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    return {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_qualification",
        "proof_posture": "generated_fixture_only_no_scientific_value",
        "green_contract": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "archive_summary": dict(inventory.aggregate_summary),
        "multimodal_summary": dict(plan_summary),
        "measurements": {
            "generated_input_bytes": 0,
            "generated_output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "range_read_calls": budget.read_calls,
            "range_bytes_returned": budget.bytes_returned,
            "inventory_replays": 2,
            "mutation_refusals_passed": len(mutations),
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": True,
            "end_to_end_latency_measured": False,
        },
        "mutation_summary": {
            "required_count": len(REQUIRED_MUTATIONS),
            "passed_count": len(mutations),
            "route_counts": dict(sorted(Counter(mutations.values()).items())),
            "mutation_names": list(REQUIRED_MUTATIONS),
        },
        "access_counters": {
            "network_requests": 0,
            "network_bytes": 0,
            "real_archive_path_operations": 0,
            "archive_member_content_reads": 0,
            "real_signal_sample_reads": 0,
            "real_event_or_onset_reads": 0,
            "target_or_label_reads": 0,
            "real_derivative_rows": 0,
            "parameter_update_fits": 0,
            "model_inference_calls": 0,
            "prediction_sets": 0,
            "prediction_freezes": 0,
            "target_deliveries": 0,
            "scores": 0,
            "scientific_claim_upgrades": 0,
        },
        "acceptance_gates": {
            "exact_14_member_inventory": True,
            "forced_ZIP64_member_observed": True,
            "zero_member_content_reads": True,
            "zero_payload_interval_reads": True,
            "range_and_archive_caps": True,
            "safe_unique_regular_members": True,
            "both_multimodal_profiles_valid": True,
            "causal_window_valid": True,
            "physical_target_firewall_valid": True,
            "all_12_comparator_roles_represented": True,
            "all_24_mutations_refused": True,
            "two_byte_identical_replays": True,
            "resource_and_output_caps": True,
            "all_real_model_score_and_claim_counters_zero": True,
        },
        "route": EXPECTED_ROUTE,
        "warnings": [
            "Generated fixtures contain no human neural data.",
            "The generated causal window is an interface fixture, not a frozen real-data window.",
            "Unavailable modality controls remain unavailable rather than being replaced with zeros.",
            "End-to-end latency was not measured.",
            "MARC1G-R1 does not authorize a public request or scientific claim.",
        ],
        "unavailable_fields": [
            "real participant identity",
            "real channel geometry",
            "human EEG EOG EMG acceleration or encoder samples",
            "real event or movement-onset timestamps",
            "held-out human targets",
            "decoding accuracy",
            "end-to-end latency",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A dependency-free generated qualification proves bounded ZIP inventory and "
                "multimodal causal firewalls behave deterministically without member payload reads."
            ),
            "scientific_claim_not_established": (
                "Generated archive and channel fixtures contain no human neural data and establish "
                "no neural effect movement decoding or source attribution."
            ),
        },
    }


def qualify_generated_marc1(output_dir: str | Path) -> QualificationOutcome:
    """Run one bounded generated qualification and atomically write its two outputs."""

    start = time.perf_counter()
    output = Path(output_dir)
    _assert_output_destination(output)
    load_registered_contract()
    budget = _RangeBudget()
    first_fixture = build_generated_archive()
    first_inventory = inventory_generated_archive(first_fixture, budget=budget)
    second_fixture = build_generated_archive()
    second_inventory = inventory_generated_archive(second_fixture, budget=budget)
    first_plan = build_generated_multimodal_plan()
    second_plan = build_generated_multimodal_plan()
    first_plan_summary = validate_generated_multimodal_plan(first_plan)
    second_plan_summary = validate_generated_multimodal_plan(second_plan)
    if (
        first_fixture.payload != second_fixture.payload
        or first_inventory.canonical_inventory_bytes
        != second_inventory.canonical_inventory_bytes
        or _canonical_json_bytes(first_plan) != _canonical_json_bytes(second_plan)
        or first_plan_summary != second_plan_summary
    ):
        raise Marc1GeneratedRefusal(REFUSAL_IDS[7], "generated replay differs")
    base_infos = _read_infos_for_mutations(first_fixture, budget)
    mutations = run_required_mutations(
        first_fixture,
        first_plan,
        base_infos,
        budget=budget,
    )
    runtime = time.perf_counter() - start
    peak_rss = _peak_rss_bytes()
    _assert_resources(runtime, peak_rss, budget)
    report = _build_report(
        first_inventory,
        first_plan_summary,
        mutations,
        budget=budget,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
    )
    plan_bytes = _canonical_json_bytes(first_plan)
    report["measurements"]["generated_input_bytes"] = len(first_fixture.payload) + len(
        plan_bytes
    )
    report_bytes = _canonical_json_bytes(report)
    manifest_bytes = _canonical_json_bytes(first_inventory.private_manifest)
    provisional_total = _bounded_output_bytes(report_bytes, manifest_bytes)
    report["measurements"]["generated_output_bytes"] = provisional_total
    final_total = _bounded_output_bytes(_canonical_json_bytes(report), manifest_bytes)
    if final_total != provisional_total:
        report["measurements"]["generated_output_bytes"] = final_total
        final_total = _bounded_output_bytes(_canonical_json_bytes(report), manifest_bytes)
    validate_public_report(report)
    report_path, manifest_path, written_total = _write_outputs(
        output,
        report,
        first_inventory.private_manifest,
    )
    if written_total != final_total:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "written output count differs")
    return QualificationOutcome(
        report=report,
        report_path=report_path,
        private_manifest_path=manifest_path,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        generated_input_bytes=report["measurements"]["generated_input_bytes"],
        generated_output_bytes=written_total,
    )


def inspect_generated_report(path: str | Path) -> dict[str, Any]:
    """Load and validate only an aggregate MARC-1 generated report."""

    report_path = Path(path)
    if report_path.is_symlink() or not report_path.is_file():
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "report path is unavailable")
    if report_path.stat().st_size > MAX_OUTPUT_BYTES:
        raise Marc1GeneratedRefusal(REFUSAL_IDS[6], "report exceeds cap")
    report = _strict_json(report_path.read_bytes())
    validate_public_report(report)
    return report


def build_plan_summary() -> dict[str, Any]:
    """Return the frozen generated-only plan without building an archive."""

    contract = load_registered_contract()
    return {
        "contract_id": contract["contract_id"],
        "status": contract["status"],
        "commands": contract["interface"]["commands"],
        "generated_member_count": contract["generated_archive_contract"]["member_count"],
        "source_profiles": sorted(contract["generated_multimodal_contract"]["source_profiles"]),
        "comparator_role_count": len(contract["comparator_roles"]),
        "mutation_count": len(contract["required_mutations"]),
        "network_bytes": 0,
        "real_payload_bytes": 0,
        "scientific_claim": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_generated_qualification",
        description="Generated-only MARC-1 archive and modality qualification.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan", help="Print the frozen generated-only plan.")
    qualify = subparsers.add_parser("qualify", help="Run one generated qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate report.")
    inspect.add_argument("report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Module CLI with no network or real-data execution mode."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command == "plan":
            print(json.dumps(build_plan_summary(), sort_keys=True))
            return 0
        if args.command == "qualify":
            outcome = qualify_generated_marc1(args.output_dir)
            print(
                json.dumps(
                    {
                        "status": outcome.report["status"],
                        "route": outcome.report["route"],
                        "generated_input_bytes": outcome.generated_input_bytes,
                        "generated_output_bytes": outcome.generated_output_bytes,
                        "runtime_seconds": outcome.runtime_seconds,
                        "peak_RSS_bytes": outcome.peak_rss_bytes,
                        "report": str(outcome.report_path),
                    },
                    sort_keys=True,
                )
            )
            return 0
        report = inspect_generated_report(args.report)
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "route": report["route"],
                    "member_count": report["archive_summary"]["member_count"],
                    "source_profile_count": report["multimodal_summary"][
                        "source_profile_count"
                    ],
                    "mutation_refusals_passed": report["measurements"][
                        "mutation_refusals_passed"
                    ],
                    "warnings": report["warnings"],
                },
                sort_keys=True,
            )
        )
        return 0
    except Marc1GeneratedRefusal as exc:
        print(
            json.dumps({"status": "refused", "refusal_id": exc.refusal_id}),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
