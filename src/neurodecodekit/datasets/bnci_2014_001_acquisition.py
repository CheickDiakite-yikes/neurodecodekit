"""Bounded opaque acquisition mechanics for BNCI-C3C5-1."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


LANE_ID = "BNCI-C3C5-1"
SCHEMA_VERSION = "0.1.0"
BASE_URL = "https://data.nemar.org/nm000139/v1.0.2/"
RESEARCH_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_cross_participant_eeg_gain_research.v0.json"
)
RESEARCH_SHA256 = "5a333709dbbf8c2e30f33c9f47240d8830d34b78ac9eda5ae22ede68a751ded2"
REGISTERED_BYTES = 779_873_919
REGISTERED_FILES = 18
NETWORK_CAP_BYTES = 2_684_354_560
DISK_CAP_BYTES = 2_147_483_648
FREE_DISK_FLOOR_BYTES = 5_368_709_120
REQUEST_CAP = 54
ATTEMPT_CAP_PER_FILE = 3


class BNCIAcquisitionRefusal(RuntimeError):
    """Fail-closed acquisition refusal."""


@dataclass(frozen=True)
class PayloadMember:
    relative_path: str
    bytes: int
    sha256: str


@dataclass(frozen=True)
class TransportResponse:
    status: int
    content_length: int
    range_start: int | None
    body: Iterable[bytes]


Transport = Callable[[str, int], TransportResponse]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _load_research() -> dict[str, Any]:
    payload = (_repo_root() / RESEARCH_RELATIVE_PATH).read_bytes()
    if _sha256(payload) != RESEARCH_SHA256:
        raise BNCIAcquisitionRefusal("BNCI research registry hash changed")
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise BNCIAcquisitionRefusal("BNCI research registry is not an object")
    return parsed


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _validate_member(member: PayloadMember) -> None:
    path = Path(member.relative_path)
    if path.is_absolute() or ".." in path.parts or path.parts[:1] != ("sourcedata",):
        raise BNCIAcquisitionRefusal("payload member path escaped sourcedata")
    if len(path.parts) != 2 or not path.name.endswith(".mat"):
        raise BNCIAcquisitionRefusal("payload member is not one direct MAT file")
    if type(member.bytes) is not int or member.bytes <= 0:
        raise BNCIAcquisitionRefusal("payload member size is invalid")
    if not _is_sha256(member.sha256):
        raise BNCIAcquisitionRefusal("payload member SHA-256 is invalid")


def registered_members() -> tuple[PayloadMember, ...]:
    selected = _load_research().get("selected_original_payload")
    if not isinstance(selected, Mapping) or not isinstance(selected.get("members"), list):
        raise BNCIAcquisitionRefusal("registered payload member table is unavailable")
    members = tuple(
        PayloadMember(
            relative_path=str(row.get("path")),
            bytes=int(row.get("bytes")),
            sha256=str(row.get("sha256")),
        )
        for row in selected["members"]
        if isinstance(row, Mapping)
    )
    for member in members:
        _validate_member(member)
    if len(members) != REGISTERED_FILES:
        raise BNCIAcquisitionRefusal("registered payload file count changed")
    if sum(member.bytes for member in members) != REGISTERED_BYTES:
        raise BNCIAcquisitionRefusal("registered payload byte total changed")
    if len({member.relative_path for member in members}) != len(members):
        raise BNCIAcquisitionRefusal("registered payload path is duplicated")
    if len({member.sha256 for member in members}) != len(members):
        raise BNCIAcquisitionRefusal("registered payload digest is duplicated")
    expected_names = {
        f"sourcedata/A{participant:02d}{session}.mat"
        for participant in range(1, 10)
        for session in ("E", "T")
    }
    if {member.relative_path for member in members} != expected_names:
        raise BNCIAcquisitionRefusal("registered participant/session inventory changed")
    return tuple(sorted(members, key=lambda item: item.relative_path))


def registered_plan() -> dict[str, Any]:
    members = registered_members()
    return {
        "schema_name": "neurodecodekit.bnci_2014_001_acquisition_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "plan_only_no_path_stat_network_or_payload_operation",
        "base_url": BASE_URL,
        "members": [
            {
                "relative_path": member.relative_path,
                "bytes": member.bytes,
                "sha256": member.sha256,
            }
            for member in members
        ],
        "file_count": len(members),
        "accepted_payload_bytes_exact": sum(member.bytes for member in members),
        "payload_requests_maximum": REQUEST_CAP,
        "attempts_per_file_maximum": ATTEMPT_CAP_PER_FILE,
        "network_bytes_maximum": NETWORK_CAP_BYTES,
        "incremental_disk_bytes_maximum": DISK_CAP_BYTES,
        "free_disk_bytes_minimum": FREE_DISK_FLOOR_BYTES,
        "MAT_content_parse_allowed": False,
    }


def _assert_regular_no_follow(path: Path) -> os.stat_result:
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise BNCIAcquisitionRefusal("expected payload file is absent") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise BNCIAcquisitionRefusal("payload path is not a regular no-follow file")
    if info.st_nlink != 1:
        raise BNCIAcquisitionRefusal("payload hardlink alias is forbidden")
    return info


def _hash_file(path: Path) -> tuple[int, str]:
    info = _assert_regular_no_follow(path)
    digest = hashlib.sha256()
    observed = 0
    with path.open("rb", buffering=1024 * 1024) as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            observed += len(chunk)
            digest.update(chunk)
    if observed != info.st_size:
        raise BNCIAcquisitionRefusal("payload size changed during opaque hash pass")
    return observed, digest.hexdigest()


def _prepare_destination(destination: Path, *, minimum_free_bytes: int) -> Path:
    destination = destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise BNCIAcquisitionRefusal("acquisition destination already exists")
    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    if parent.is_symlink() or not parent.is_dir():
        raise BNCIAcquisitionRefusal("acquisition parent is not a direct directory")
    if shutil.disk_usage(parent).free < minimum_free_bytes:
        raise BNCIAcquisitionRefusal("free-disk floor is not satisfied")
    return destination


def acquire_members(
    members: Sequence[PayloadMember],
    destination: str | Path,
    *,
    transport: Transport,
    base_url: str = BASE_URL,
    attempts_per_file: int = ATTEMPT_CAP_PER_FILE,
    request_cap: int = REQUEST_CAP,
    network_cap_bytes: int = NETWORK_CAP_BYTES,
    disk_cap_bytes: int = DISK_CAP_BYTES,
    minimum_free_bytes: int = FREE_DISK_FLOOR_BYTES,
) -> dict[str, Any]:
    """Acquire an exact member table without interpreting any payload content."""

    if not members or not callable(transport):
        raise BNCIAcquisitionRefusal("member table or transport is invalid")
    normalized = tuple(members)
    for member in normalized:
        _validate_member(member)
    if len({member.relative_path for member in normalized}) != len(normalized):
        raise BNCIAcquisitionRefusal("acquisition member path is duplicated")
    expected_bytes = sum(member.bytes for member in normalized)
    if expected_bytes > disk_cap_bytes:
        raise BNCIAcquisitionRefusal("registered payload exceeds incremental-disk cap")
    if type(attempts_per_file) is not int or not 1 <= attempts_per_file <= 3:
        raise BNCIAcquisitionRefusal("attempt cap is outside the frozen envelope")
    destination_path = _prepare_destination(
        Path(destination), minimum_free_bytes=minimum_free_bytes
    )
    work_root: Path | None = Path(
        tempfile.mkdtemp(prefix=f".{destination_path.name}.partial-", dir=destination_path.parent)
    )
    request_count = 0
    network_bytes = 0
    manifest_rows: list[dict[str, Any]] = []
    try:
        for member in normalized:
            if work_root is None:
                raise BNCIAcquisitionRefusal("acquisition work root is unavailable")
            final_path = work_root / member.relative_path
            final_path.parent.mkdir(parents=True, exist_ok=True)
            partial_path = final_path.with_suffix(final_path.suffix + ".part")
            completed = False
            for attempt in range(1, attempts_per_file + 1):
                if final_path.exists() or final_path.is_symlink():
                    raise BNCIAcquisitionRefusal("completed payload was requested twice")
                if partial_path.exists() or partial_path.is_symlink():
                    offset = _assert_regular_no_follow(partial_path).st_size
                else:
                    offset = 0
                if offset < 0 or offset >= member.bytes:
                    raise BNCIAcquisitionRefusal("partial payload offset is invalid")
                request_count += 1
                if request_count > request_cap:
                    raise BNCIAcquisitionRefusal("payload request cap exceeded")
                response = transport(base_url + member.relative_path, offset)
                if not isinstance(response, TransportResponse):
                    raise BNCIAcquisitionRefusal("transport response type is invalid")
                expected_status = 200 if offset == 0 else 206
                if response.status != expected_status:
                    raise BNCIAcquisitionRefusal("transport status does not match resume state")
                if offset and response.range_start != offset:
                    raise BNCIAcquisitionRefusal("transport range does not match partial size")
                if not offset and response.range_start not in (None, 0):
                    raise BNCIAcquisitionRefusal("initial transport unexpectedly returned a range")
                expected_remaining = member.bytes - offset
                if response.content_length != expected_remaining:
                    raise BNCIAcquisitionRefusal("transport content length differs")
                mode = "ab" if offset else "xb"
                try:
                    with partial_path.open(mode) as handle:
                        for chunk in response.body:
                            if not isinstance(chunk, bytes) or not chunk:
                                raise BNCIAcquisitionRefusal("transport yielded a malformed chunk")
                            network_bytes += len(chunk)
                            if network_bytes > network_cap_bytes:
                                raise BNCIAcquisitionRefusal("network-byte cap exceeded")
                            handle.write(chunk)
                except (ConnectionError, TimeoutError):
                    if attempt == attempts_per_file:
                        raise BNCIAcquisitionRefusal("transport attempts exhausted")
                    continue
                observed_size, observed_hash = _hash_file(partial_path)
                if observed_size != member.bytes or observed_hash != member.sha256:
                    raise BNCIAcquisitionRefusal("payload size or SHA-256 differs")
                os.rename(partial_path, final_path)
                completed = True
                manifest_rows.append(
                    {
                        "relative_path": member.relative_path,
                        "bytes": observed_size,
                        "sha256": observed_hash,
                        "attempts": attempt,
                    }
                )
                break
            if not completed:
                raise BNCIAcquisitionRefusal("payload acquisition did not complete")
        if work_root is None:
            raise BNCIAcquisitionRefusal("acquisition work root is unavailable")
        if any(work_root.rglob("*.part")):
            raise BNCIAcquisitionRefusal("completed acquisition retained a partial file")
        manifest = {
            "schema_name": "neurodecodekit.bnci_2014_001_private_acquisition_manifest",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "complete_opaque_payload_bundle",
            "members": manifest_rows,
            "file_count": len(manifest_rows),
            "payload_bytes": sum(row["bytes"] for row in manifest_rows),
            "payload_requests": request_count,
            "network_bytes": network_bytes,
            "MAT_content_opens": 0,
            "MAT_semantic_parses": 0,
        }
        manifest_payload = _canonical_bytes(manifest)
        manifest_path = work_root / "manifest.private.v0.json"
        manifest_path.write_bytes(manifest_payload)
        os.chmod(manifest_path, 0o600)
        if destination_path.exists() or destination_path.is_symlink():
            raise BNCIAcquisitionRefusal("acquisition destination appeared during execution")
        os.rename(work_root, destination_path)
        work_root = None
        return manifest
    finally:
        if work_root is not None and work_root.exists():
            shutil.rmtree(work_root)


def run_generated_acquisition_cases(root: Path) -> dict[str, Any]:
    """Qualify resume, integrity, path, cap, and cleanup behavior with tiny bytes."""

    root.mkdir(parents=True, exist_ok=False)
    payloads = {
        "sourcedata/A01E.mat": b"generated-bnci-A01E",
        "sourcedata/A01T.mat": b"generated-bnci-A01T-longer",
        "sourcedata/A02E.mat": b"generated-bnci-A02E",
    }
    members = tuple(
        PayloadMember(path, len(payload), _sha256(payload))
        for path, payload in sorted(payloads.items())
    )
    calls: list[tuple[str, int]] = []
    interrupted = False

    def transport(url: str, offset: int) -> TransportResponse:
        nonlocal interrupted
        relative = url.removeprefix("mock://bnci/")
        payload = payloads[relative]
        calls.append((relative, offset))
        if relative == "sourcedata/A01T.mat" and offset == 0 and not interrupted:
            interrupted = True

            def broken() -> Iterable[bytes]:
                midpoint = len(payload) // 2
                yield payload[:midpoint]
                raise ConnectionError("generated interruption")

            return TransportResponse(200, len(payload), None, broken())
        return TransportResponse(
            200 if offset == 0 else 206,
            len(payload) - offset,
            None if offset == 0 else offset,
            (payload[offset:],),
        )

    destination = root / "bundle"
    manifest = acquire_members(
        members,
        destination,
        transport=transport,
        base_url="mock://bnci/",
        network_cap_bytes=4096,
        disk_cap_bytes=4096,
        minimum_free_bytes=0,
    )
    if manifest["file_count"] != 3 or manifest["payload_requests"] != 4:
        raise BNCIAcquisitionRefusal("generated resume accounting changed")
    if not any(offset > 0 for _path, offset in calls):
        raise BNCIAcquisitionRefusal("generated resume path was not exercised")
    for member in members:
        size, digest = _hash_file(destination / member.relative_path)
        if (size, digest) != (member.bytes, member.sha256):
            raise BNCIAcquisitionRefusal("generated accepted member changed")
    alias_source = root / "alias-source.mat"
    alias_source.write_bytes(b"generated-alias")
    symlink_path = root / "alias-symlink.mat"
    hardlink_path = root / "alias-hardlink.mat"
    symlink_path.symlink_to(alias_source)
    os.link(alias_source, hardlink_path)
    alias_refusals = 0
    for alias in (symlink_path, hardlink_path):
        try:
            _hash_file(alias)
        except BNCIAcquisitionRefusal:
            alias_refusals += 1
    if alias_refusals != 2:
        raise BNCIAcquisitionRefusal("generated alias refusal matrix changed")
    hardlink_path.unlink()
    symlink_path.unlink()
    alias_source.unlink()
    refusals = 0
    refusal_cases = (
        {"members": (PayloadMember("../escape.mat", 1, "0" * 64),)},
        {"members": members, "destination": destination},
        {"members": members, "network_cap_bytes": 1},
        {"members": members, "disk_cap_bytes": 1},
        {"members": members, "minimum_free_bytes": 1 << 80},
    )
    for index, case in enumerate(refusal_cases):
        try:
            acquire_members(
                case.get("members", members),
                case.get("destination", root / f"refusal-{index}"),
                transport=transport,
                base_url="mock://bnci/",
                network_cap_bytes=case.get("network_cap_bytes", 4096),
                disk_cap_bytes=case.get("disk_cap_bytes", 4096),
                minimum_free_bytes=case.get("minimum_free_bytes", 0),
            )
        except BNCIAcquisitionRefusal:
            refusals += 1
    if refusals != len(refusal_cases):
        raise BNCIAcquisitionRefusal("generated acquisition refusal matrix changed")
    if any(path.name.startswith(".refusal-") for path in root.iterdir()):
        raise BNCIAcquisitionRefusal("refused acquisition retained a partial work root")
    return {
        "case_classes": [
            "opaque_resume_and_integrity",
            "path_overwrite_symlink_hardlink_and_cap_refusal",
        ],
        "accepted_files": 3,
        "accepted_bytes": sum(map(len, payloads.values())),
        "accepted_payload_requests": manifest["payload_requests"],
        "mock_transport_calls_total": len(calls),
        "refusal_cases": refusals + alias_refusals,
        "temporary_generated_payload_bytes": manifest["payload_bytes"],
        "cleanup_owner": "caller_owned_generated_work_root",
    }
