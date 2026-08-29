"""Generated-qualified acquisition core for the Ofner 2017 motor-imagery source.

This module intentionally has no network client and no EEG parser. It separates
stable manifest identity from expiring transport URLs, validates the complete
15-by-10 source-GDF surface, and copies injected byte streams into an atomic,
bounded destination. A later Tier C wrapper may supply a real transport only
after a separate authorization decision.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import shutil
import sys
import tempfile
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable, Mapping, Sequence


SOURCE_RECORD_RELATIVE_PATH = Path(
    "registries/ofner_2017_motor_imagery_source_reselection.v0.json"
)
SOURCE_RECORD_SHA256 = "95f277a36122517653d336058dcfee507a2a4ca40076002d29120c21fa922b49"
DATASET_ID = "nm000173"
DATASET_VERSION = "v1.0.3"
STABLE_BYTES_HOST = "data.nemar.org"
SIGNED_OBJECT_HOST = "nemar.s3.us-east-2.amazonaws.com"
EXPECTED_PARTICIPANTS = tuple(range(1, 16))
EXPECTED_RUNS = tuple(range(1, 11))
EXPECTED_FILE_COUNT = 150
EXPECTED_PAYLOAD_BYTES = 13_748_417_608
MANIFEST_BODY_CAP_BYTES = 2 * 1024 * 1024
MANIFEST_ROW_CAP = 10_000
CHUNK_BYTES = 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
PATH_PATTERN = re.compile(
    r"sourcedata/motorimagination_subject(?P<subject>[1-9]|1[0-5])_"
    r"run(?P<run>10|[1-9])\.gdf\Z"
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
AMZ_DATE_PATTERN = re.compile(r"[0-9]{8}T[0-9]{6}Z\Z")
SIGNED_QUERY_REQUIRED = {
    "X-Amz-Algorithm",
    "X-Amz-Credential",
    "X-Amz-Date",
    "X-Amz-Expires",
    "X-Amz-SignedHeaders",
    "X-Amz-Signature",
}
SIGNED_QUERY_OPTIONAL = {"response-content-disposition"}
FORBIDDEN_ROW_FIELDS = {
    "annotation",
    "annotations",
    "event",
    "events",
    "label",
    "labels",
    "target",
    "targets",
    "trial_label",
}


class OfnerAcquisitionRefusal(RuntimeError):
    """A generated or future live acquisition input failed closed."""


@dataclass(frozen=True)
class SelectionPolicy:
    """Exact stable identity and resource constraints for one manifest surface."""

    dataset_id: str
    dataset_version: str
    participants: tuple[int, ...]
    runs: tuple[int, ...]
    expected_file_count: int
    expected_payload_bytes: int
    expected_canonical_bytes: int | None
    expected_canonical_sha256: str | None
    stable_bytes_host: str = STABLE_BYTES_HOST
    signed_object_host: str = SIGNED_OBJECT_HOST
    manifest_body_cap_bytes: int = MANIFEST_BODY_CAP_BYTES


@dataclass(frozen=True)
class ManifestMember:
    """One stable payload identity paired with a short-lived transport URL."""

    path: str
    size_bytes: int
    sha256: str
    bytes_url: str
    signed_url: str
    participant: int
    run: int


@dataclass(frozen=True)
class AcquisitionCaps:
    """Resource limits enforced by the transport-independent writer."""

    network_bytes: int
    incremental_disk_bytes: int
    output_bytes: int = 1024 * 1024


PayloadOpener = Callable[[str, int], BinaryIO]


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
        raise OfnerAcquisitionRefusal("artifact hash read failed") from exc
    return digest.hexdigest()


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
        raise OfnerAcquisitionRefusal("manifest cannot be canonicalized") from exc
    return (text + "\n").encode("ascii")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise OfnerAcquisitionRefusal("manifest JSON key is duplicated")
        value[key] = child
    return value


def _strict_json(payload: bytes, maximum_bytes: int) -> Any:
    if (
        not isinstance(payload, bytes)
        or not 0 < len(payload) <= maximum_bytes
        or payload.startswith(b"\xef\xbb\xbf")
        or b"\x00" in payload
    ):
        raise OfnerAcquisitionRefusal("manifest payload is absent, encoded differently, or too large")
    try:
        return json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=lambda _value: (_ for _ in ()).throw(
                OfnerAcquisitionRefusal("manifest JSON constant is non-finite")
            ),
        )
    except OfnerAcquisitionRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise OfnerAcquisitionRefusal("manifest JSON is invalid") from exc


def _manifest_rows(parsed: Any) -> list[Mapping[str, Any]]:
    if isinstance(parsed, list):
        rows = parsed
    elif isinstance(parsed, Mapping) and isinstance(parsed.get("files"), list):
        rows = parsed["files"]
    else:
        raise OfnerAcquisitionRefusal("manifest record container is invalid")
    if len(rows) > MANIFEST_ROW_CAP or any(not isinstance(row, Mapping) for row in rows):
        raise OfnerAcquisitionRefusal("manifest record table is invalid or exceeds its cap")
    return list(rows)


def canonicalize_manifest(payload: bytes, *, maximum_bytes: int = MANIFEST_BODY_CAP_BYTES) -> bytes:
    """Remove only direct row ``url`` values and canonicalize the full manifest."""

    parsed = _strict_json(payload, maximum_bytes)
    rows = _manifest_rows(parsed)
    canonical_rows = [{key: child for key, child in row.items() if key != "url"} for row in rows]
    if isinstance(parsed, list):
        canonical: Any = canonical_rows
    else:
        canonical = dict(parsed)
        canonical["files"] = canonical_rows
    return _canonical_json_bytes(canonical)


def _load_source_record(repo_root: Path) -> dict[str, Any]:
    path = repo_root / SOURCE_RECORD_RELATIVE_PATH
    payload = path.read_bytes()
    if _sha256_bytes(payload) != SOURCE_RECORD_SHA256:
        raise OfnerAcquisitionRefusal("Ofner source-selection record hash differs")
    value = _strict_json(payload, 1024 * 1024)
    if not isinstance(value, dict):
        raise OfnerAcquisitionRefusal("Ofner source-selection record is not an object")
    return value


def registered_policy(repo_root: str | Path) -> SelectionPolicy:
    """Load the frozen production policy without network or payload access."""

    record = _load_source_record(Path(repo_root))
    source = record["source_identity"]
    surface = record["selected_surface"]
    return SelectionPolicy(
        dataset_id=source["NEMAR_dataset"],
        dataset_version=source["NEMAR_version"],
        participants=tuple(surface["participant_ids"]),
        runs=tuple(surface["run_ids"]),
        expected_file_count=surface["files"],
        expected_payload_bytes=surface["payload_bytes"],
        expected_canonical_bytes=source["canonical_manifest_bytes"],
        expected_canonical_sha256=source["canonical_manifest_sha256"],
    )


def registered_plan(repo_root: str | Path) -> dict[str, Any]:
    """Return the frozen plan; this API has no live execution capability."""

    policy = registered_policy(repo_root)
    return {
        "schema_name": "neurodecodekit.ofner_2017_motor_imagery_acquisition_plan",
        "schema_version": "0.1.0",
        "mode": "generated_qualification_or_dry_run_only",
        "dataset_id": policy.dataset_id,
        "dataset_version": policy.dataset_version,
        "participants": list(policy.participants),
        "runs": list(policy.runs),
        "expected_file_count": policy.expected_file_count,
        "expected_payload_bytes": policy.expected_payload_bytes,
        "canonical_manifest_sha256": policy.expected_canonical_sha256,
        "stable_identity_fields": ["path", "bytes_or_size", "sha256", "bytes_url"],
        "volatile_transport_field": "url",
        "live_network_client_present": False,
        "real_payload_execution_present": False,
        "header_or_signal_parser_present": False,
        "warnings": [
            "generated_qualification_is_not_real_EEG_evidence",
            "real_GDF_access_requires_a_separate_Tier_C_wrapper_and_decision",
            "recorded_EMG_is_unavailable_in_this_source",
            "no_scientific_claim",
        ],
    }


def _row_size(row: Mapping[str, Any]) -> int:
    values = [row[key] for key in ("bytes", "size") if key in row]
    if (
        not values
        or any(type(value) is not int or value <= 0 for value in values)
        or len(set(values)) != 1
    ):
        raise OfnerAcquisitionRefusal("selected manifest size is missing or ambiguous")
    return values[0]


def _row_sha256(row: Mapping[str, Any]) -> str:
    values = [row[key] for key in ("sha256", "checksum") if key in row]
    if not values or any(not isinstance(value, str) for value in values):
        raise OfnerAcquisitionRefusal("selected manifest digest is missing or ambiguous")
    normalized = {
        value.removeprefix("sha256:").removeprefix("SHA256:").lower() for value in values
    }
    if len(normalized) != 1:
        raise OfnerAcquisitionRefusal("selected manifest digest fields disagree")
    digest = normalized.pop()
    if not SHA256_PATTERN.fullmatch(digest):
        raise OfnerAcquisitionRefusal("selected manifest digest is invalid")
    return digest


def _validate_bytes_url(value: Any, path: str, policy: SelectionPolicy) -> str:
    if not isinstance(value, str) or len(value) > 4096:
        raise OfnerAcquisitionRefusal("stable bytes URL is missing or malformed")
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise OfnerAcquisitionRefusal("stable bytes URL authority is invalid") from exc
    expected_path = f"/{policy.dataset_id}/{policy.dataset_version}/{path}"
    if (
        parsed.scheme != "https"
        or parsed.hostname != policy.stable_bytes_host
        or port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != expected_path
        or parsed.query
        or parsed.fragment
    ):
        raise OfnerAcquisitionRefusal("stable bytes URL differs from selected identity")
    return value


def _expected_signed_path(policy: SelectionPolicy, size_bytes: int, sha256: str) -> str:
    return f"/{policy.dataset_id}/objects/SHA256E-s{size_bytes}--{sha256}.gdf"


def _validate_signed_url(
    value: Any,
    *,
    policy: SelectionPolicy,
    size_bytes: int,
    sha256: str,
) -> str:
    if not isinstance(value, str) or len(value) > 8192:
        raise OfnerAcquisitionRefusal("signed object URL is missing or malformed")
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise OfnerAcquisitionRefusal("signed object URL authority is invalid") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname != policy.signed_object_host
        or port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or parsed.path != _expected_signed_path(policy, size_bytes, sha256)
    ):
        raise OfnerAcquisitionRefusal("signed object URL authority or path differs")
    pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    if len(pairs) != len({key for key, _value in pairs}):
        raise OfnerAcquisitionRefusal("signed object URL query key is duplicated")
    query = dict(pairs)
    if set(query) - (SIGNED_QUERY_REQUIRED | SIGNED_QUERY_OPTIONAL):
        raise OfnerAcquisitionRefusal("signed object URL query key is not allowlisted")
    if not SIGNED_QUERY_REQUIRED.issubset(query):
        raise OfnerAcquisitionRefusal("signed object URL query is incomplete")
    if (
        query["X-Amz-Algorithm"] != "AWS4-HMAC-SHA256"
        or not query["X-Amz-Credential"].endswith("/aws4_request")
        or not AMZ_DATE_PATTERN.fullmatch(query["X-Amz-Date"])
        or not query["X-Amz-Expires"].isdigit()
        or not 0 < int(query["X-Amz-Expires"]) <= 3600
        or query["X-Amz-SignedHeaders"] != "host"
        or not SHA256_PATTERN.fullmatch(query["X-Amz-Signature"])
    ):
        raise OfnerAcquisitionRefusal("signed object URL query value is invalid")
    disposition = query.get("response-content-disposition")
    if disposition is not None and (
        not disposition or "\r" in disposition or "\n" in disposition
    ):
        raise OfnerAcquisitionRefusal("signed object content disposition is invalid")
    return value


def select_manifest(payload: bytes, policy: SelectionPolicy) -> tuple[ManifestMember, ...]:
    """Validate and select the exact participant-by-run source-GDF matrix."""

    canonical = canonicalize_manifest(payload, maximum_bytes=policy.manifest_body_cap_bytes)
    if (
        policy.expected_canonical_bytes is not None
        and len(canonical) != policy.expected_canonical_bytes
    ):
        raise OfnerAcquisitionRefusal("canonical manifest byte count differs")
    if (
        policy.expected_canonical_sha256 is not None
        and _sha256_bytes(canonical) != policy.expected_canonical_sha256
    ):
        raise OfnerAcquisitionRefusal("canonical manifest SHA-256 differs")

    parsed = _strict_json(payload, policy.manifest_body_cap_bytes)
    selected: dict[tuple[int, int], ManifestMember] = {}
    for row in _manifest_rows(parsed):
        path = row.get("path")
        if not isinstance(path, str):
            continue
        match = PATH_PATTERN.fullmatch(path)
        if match is None:
            continue
        if FORBIDDEN_ROW_FIELDS.intersection(key.casefold() for key in row):
            raise OfnerAcquisitionRefusal("selected manifest row contains target-like content")
        participant = int(match.group("subject"))
        run = int(match.group("run"))
        key = (participant, run)
        if key in selected:
            raise OfnerAcquisitionRefusal("selected participant-run record is duplicated")
        size_bytes = _row_size(row)
        digest = _row_sha256(row)
        selected[key] = ManifestMember(
            path=path,
            size_bytes=size_bytes,
            sha256=digest,
            bytes_url=_validate_bytes_url(row.get("bytes_url"), path, policy),
            signed_url=_validate_signed_url(
                row.get("url"),
                policy=policy,
                size_bytes=size_bytes,
                sha256=digest,
            ),
            participant=participant,
            run=run,
        )

    expected_keys = {(subject, run) for subject in policy.participants for run in policy.runs}
    if set(selected) != expected_keys or len(selected) != policy.expected_file_count:
        raise OfnerAcquisitionRefusal("selected participant-run matrix is incomplete or expanded")
    members = tuple(selected[key] for key in sorted(selected))
    if sum(member.size_bytes for member in members) != policy.expected_payload_bytes:
        raise OfnerAcquisitionRefusal("selected payload byte total differs")
    if len({member.sha256 for member in members}) != len(members):
        raise OfnerAcquisitionRefusal("selected payload checksums are not unique")
    return members


def _safe_relative_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise OfnerAcquisitionRefusal("output path is unsafe")
    return path


def _assert_no_symlink_components(root: Path, path: Path) -> None:
    current = root
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise OfnerAcquisitionRefusal("output escaped workspace root") from exc
    for part in relative.parts:
        current = current / part
        try:
            if os.path.islink(current):
                raise OfnerAcquisitionRefusal("output path contains a symlink")
        except OSError as exc:
            raise OfnerAcquisitionRefusal("output path inspection failed") from exc
        if not current.exists():
            return


def _mkdir_no_symlinks(root: Path, path: Path) -> None:
    _assert_no_symlink_components(root, path)
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.exists():
            if current.is_symlink() or not current.is_dir():
                raise OfnerAcquisitionRefusal("output directory component is unsafe")
            continue
        current.mkdir()


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    wrong = {key: environ.get(key) for key in THREAD_ENV_KEYS if environ.get(key) != "1"}
    if wrong:
        raise OfnerAcquisitionRefusal("one-thread environment is required")


def _remove_created_tree(path: Path) -> None:
    if path.exists() and not path.is_symlink():
        shutil.rmtree(path)


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OfnerAcquisitionRefusal("payload write made no progress")
        view = view[written:]


def acquire_selected_members(
    members: Sequence[ManifestMember],
    *,
    workspace_root: str | Path,
    destination_relative: str | Path,
    payload_opener: PayloadOpener,
    caps: AcquisitionCaps,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Stream selected opaque bytes into one new atomic bundle.

    The caller owns transport policy. This function never constructs a network
    client, follows redirects, or interprets GDF bytes.
    """

    _check_thread_environment(environ)
    normalized = tuple(members)
    if not normalized or len({member.path for member in normalized}) != len(normalized):
        raise OfnerAcquisitionRefusal("acquisition member inventory is empty or duplicated")
    if not callable(payload_opener):
        raise OfnerAcquisitionRefusal("payload opener is not callable")
    if min(caps.network_bytes, caps.incremental_disk_bytes, caps.output_bytes) <= 0:
        raise OfnerAcquisitionRefusal("acquisition caps must be positive")

    root = Path(workspace_root).resolve()
    destination = root / _safe_relative_path(destination_relative)
    staging = destination.with_name(destination.name + ".partial-ofner")
    _assert_no_symlink_components(root, destination)
    _assert_no_symlink_components(root, staging)
    if destination.exists() or staging.exists():
        raise OfnerAcquisitionRefusal("destination or invocation staging already exists")
    _mkdir_no_symlinks(root, destination.parent)
    staging.mkdir()

    observed_rows: list[dict[str, Any]] = []
    network_bytes = 0
    disk_bytes = 0
    try:
        for member in normalized:
            relative = _safe_relative_path(member.path)
            output = staging / relative
            _mkdir_no_symlinks(root, output.parent)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(output, flags, 0o600)
            digest = hashlib.sha256()
            observed = 0
            try:
                stream = payload_opener(member.signed_url, member.size_bytes)
                try:
                    while True:
                        chunk = stream.read(min(CHUNK_BYTES, member.size_bytes - observed + 1))
                        if not chunk:
                            break
                        if not isinstance(chunk, bytes):
                            raise OfnerAcquisitionRefusal("payload stream yielded non-bytes")
                        observed += len(chunk)
                        network_bytes += len(chunk)
                        disk_bytes += len(chunk)
                        if (
                            observed > member.size_bytes
                            or network_bytes > caps.network_bytes
                            or disk_bytes > caps.incremental_disk_bytes
                        ):
                            raise OfnerAcquisitionRefusal("payload exceeded a frozen resource cap")
                        digest.update(chunk)
                        _write_all(descriptor, chunk)
                finally:
                    stream.close()
            finally:
                os.close(descriptor)
            if observed != member.size_bytes or digest.hexdigest() != member.sha256:
                raise OfnerAcquisitionRefusal("payload size or SHA-256 differs")
            observed_rows.append(
                {"path": member.path, "size_bytes": observed, "sha256": digest.hexdigest()}
            )
        os.rename(staging, destination)
    except Exception:
        _remove_created_tree(staging)
        raise

    receipt = {
        "schema_name": "neurodecodekit.ofner_2017_motor_imagery_opaque_acquisition",
        "schema_version": "0.1.0",
        "status": "passed",
        "files": observed_rows,
        "measurements": {
            "file_count": len(observed_rows),
            "network_bytes": network_bytes,
            "final_payload_bytes": disk_bytes,
            "opaque_content_hash_passes": len(observed_rows),
        },
        "operation_counters": {
            "manifest_reads": 0,
            "payload_streams": len(observed_rows),
            "GDF_header_reads": 0,
            "event_or_annotation_reads": 0,
            "target_or_label_reads": 0,
            "signal_sample_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scientific_scores": 0,
        },
        "warnings": [
            "opaque_bytes_only",
            "no_GDF_readability_or_measurement_contract_established",
            "no_scientific_claim",
        ],
    }
    if len(_canonical_json_bytes(receipt)) > caps.output_bytes:
        _remove_created_tree(destination)
        raise OfnerAcquisitionRefusal("acquisition receipt exceeded output cap")
    return receipt


def _generated_signed_url(
    policy: SelectionPolicy,
    size_bytes: int,
    sha256: str,
    *,
    signature_digit: str,
) -> str:
    query = urllib.parse.urlencode(
        {
            "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
            "X-Amz-Credential": "generated/20260829/us-east-2/s3/aws4_request",
            "X-Amz-Date": "20260829T120000Z",
            "X-Amz-Expires": "3600",
            "X-Amz-SignedHeaders": "host",
            "X-Amz-Signature": signature_digit * 64,
        }
    )
    return (
        f"https://{policy.signed_object_host}"
        f"{_expected_signed_path(policy, size_bytes, sha256)}?{query}"
    )


def _generated_fixture(
    *, signature_digit: str = "1"
) -> tuple[SelectionPolicy, bytes, dict[str, bytes]]:
    payloads: dict[str, bytes] = {}
    rows: list[dict[str, Any]] = []
    for participant in EXPECTED_PARTICIPANTS:
        for run in EXPECTED_RUNS:
            path = f"sourcedata/motorimagination_subject{participant}_run{run}.gdf"
            payload = (f"generated-ofner-{participant:02d}-{run:02d}|".encode("ascii")) * 3
            digest = _sha256_bytes(payload)
            payloads[path] = payload
            rows.append(
                {
                    "path": path,
                    "bytes": len(payload),
                    "sha256": digest,
                    "bytes_url": (
                        f"https://{STABLE_BYTES_HOST}/{DATASET_ID}/{DATASET_VERSION}/{path}"
                    ),
                    "url": "",
                }
            )
    total = sum(map(len, payloads.values()))
    temporary_policy = SelectionPolicy(
        dataset_id=DATASET_ID,
        dataset_version=DATASET_VERSION,
        participants=EXPECTED_PARTICIPANTS,
        runs=EXPECTED_RUNS,
        expected_file_count=EXPECTED_FILE_COUNT,
        expected_payload_bytes=total,
        expected_canonical_bytes=None,
        expected_canonical_sha256=None,
    )
    for row in rows:
        row["url"] = _generated_signed_url(
            temporary_policy,
            row["bytes"],
            row["sha256"],
            signature_digit=signature_digit,
        )
    raw = _canonical_json_bytes(
        {"dataset": "generated-nm000173", "files": rows, "targets_included": False}
    )
    canonical = canonicalize_manifest(raw)
    policy = SelectionPolicy(
        **{
            **temporary_policy.__dict__,
            "expected_canonical_bytes": len(canonical),
            "expected_canonical_sha256": _sha256_bytes(canonical),
        }
    )
    return policy, raw, payloads


def _directory_digest(path: Path, members: Sequence[ManifestMember]) -> str:
    rows = [
        {
            "path": member.path,
            "bytes": (path / member.path).stat().st_size,
            "sha256": _sha256_file(path / member.path),
        }
        for member in members
    ]
    return _sha256_bytes(_canonical_json_bytes(rows))


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def run_generated_qualification(repo_root: str | Path) -> dict[str, Any]:
    """Exercise two generated replays and a fixed refusal matrix."""

    started = time.perf_counter()
    registered = registered_plan(repo_root)
    policy, first_raw, payloads = _generated_fixture(signature_digit="1")
    _second_policy, second_raw, _second_payloads = _generated_fixture(signature_digit="2")
    first_members = select_manifest(first_raw, policy)
    second_members = select_manifest(second_raw, policy)
    if canonicalize_manifest(first_raw) != canonicalize_manifest(second_raw):
        raise OfnerAcquisitionRefusal("volatile-URL canonical replay differs")
    if [member.__dict__ | {"signed_url": None} for member in first_members] != [
        member.__dict__ | {"signed_url": None} for member in second_members
    ]:
        raise OfnerAcquisitionRefusal("stable selected identity differs across URL refresh")

    thread_env = {key: "1" for key in THREAD_ENV_KEYS}
    replay_digests: list[str] = []
    generated_bytes = 0
    for members, raw in ((first_members, first_raw), (second_members, second_raw)):
        payload_by_url = {
            member.signed_url: payloads[member.path]
            for member in members
        }

        def opener(url: str, expected_size: int) -> BinaryIO:
            payload = payload_by_url[url]
            if len(payload) != expected_size:
                raise AssertionError("generated fixture size binding differs")
            import io

            return io.BytesIO(payload)

        with tempfile.TemporaryDirectory(prefix="ndk-ofner-generated-") as temporary:
            root = Path(temporary)
            receipt = acquire_selected_members(
                members,
                workspace_root=root,
                destination_relative="bundle",
                payload_opener=opener,
                caps=AcquisitionCaps(
                    network_bytes=sum(map(len, payloads.values())),
                    incremental_disk_bytes=sum(map(len, payloads.values())),
                ),
                environ=thread_env,
            )
            generated_bytes = receipt["measurements"]["final_payload_bytes"]
            replay_digests.append(_directory_digest(root / "bundle", members))
    if len(set(replay_digests)) != 1:
        raise OfnerAcquisitionRefusal("generated acquisition replay digest differs")

    refusals = 0

    def expect_selector_refusal(mutator: Callable[[dict[str, Any]], None]) -> None:
        nonlocal refusals
        value = json.loads(first_raw)
        mutator(value)
        try:
            select_manifest(_canonical_json_bytes(value), policy)
        except OfnerAcquisitionRefusal:
            refusals += 1
        else:
            raise AssertionError("generated malformed manifest was accepted")

    expect_selector_refusal(lambda value: value["files"][0].update(target="forbidden"))
    expect_selector_refusal(lambda value: value["files"][0].update(label="forbidden"))
    expect_selector_refusal(lambda value: value["files"].pop())
    expect_selector_refusal(lambda value: value["files"].append(dict(value["files"][0])))
    expect_selector_refusal(lambda value: value["files"][0].update(bytes=999))
    expect_selector_refusal(lambda value: value["files"][0].update(sha256="0" * 64))
    expect_selector_refusal(
        lambda value: value["files"][0].update(
            bytes_url=value["files"][0]["bytes_url"].replace(STABLE_BYTES_HOST, "example.invalid")
        )
    )
    expect_selector_refusal(
        lambda value: value["files"][0].update(
            url=value["files"][0]["url"].replace(SIGNED_OBJECT_HOST, "example.invalid")
        )
    )
    expect_selector_refusal(
        lambda value: value["files"][0].update(
            url=value["files"][0]["url"].replace("SHA256E-s", "SHA256E-s1")
        )
    )
    expect_selector_refusal(
        lambda value: value["files"][0].update(url=value["files"][0]["url"] + "&extra=1")
    )
    expect_selector_refusal(
        lambda value: value["files"][0].update(
            url=value["files"][0]["url"].replace("X-Amz-Expires=3600", "X-Amz-Expires=3601")
        )
    )
    expect_selector_refusal(
        lambda value: value["files"][1].update(sha256=value["files"][0]["sha256"])
    )
    for malformed in (
        b'{"files":[],"files":[]}',
        b"not-json",
        b"\xef\xbb\xbf{}",
    ):
        try:
            select_manifest(malformed, policy)
        except OfnerAcquisitionRefusal:
            refusals += 1
        else:
            raise AssertionError("generated malformed JSON was accepted")

    first = first_members[0]

    def expect_acquisition_refusal(payload: bytes, *, network_cap: int | None = None) -> None:
        nonlocal refusals

        def opener(_url: str, _expected_size: int) -> BinaryIO:
            import io

            return io.BytesIO(payload)

        with tempfile.TemporaryDirectory(prefix="ndk-ofner-refusal-") as temporary:
            try:
                acquire_selected_members(
                    (first,),
                    workspace_root=temporary,
                    destination_relative="bundle",
                    payload_opener=opener,
                    caps=AcquisitionCaps(
                        network_bytes=network_cap if network_cap is not None else len(payload) + 1,
                        incremental_disk_bytes=len(payload) + 1,
                    ),
                    environ=thread_env,
                )
            except OfnerAcquisitionRefusal:
                refusals += 1
            else:
                raise AssertionError("generated malformed payload was accepted")

    expected_payload = payloads[first.path]
    expect_acquisition_refusal(expected_payload[:-1])
    expect_acquisition_refusal(expected_payload + b"x")
    expect_acquisition_refusal(b"x" * len(expected_payload))
    expect_acquisition_refusal(expected_payload, network_cap=len(expected_payload) - 1)
    with tempfile.TemporaryDirectory(prefix="ndk-ofner-existing-") as temporary:
        (Path(temporary) / "bundle").mkdir()
        try:
            acquire_selected_members(
                (first,),
                workspace_root=temporary,
                destination_relative="bundle",
                payload_opener=lambda _url, _size: (_ for _ in ()).throw(AssertionError()),
                caps=AcquisitionCaps(network_bytes=1, incremental_disk_bytes=1),
                environ=thread_env,
            )
        except OfnerAcquisitionRefusal:
            refusals += 1
        else:
            raise AssertionError("existing generated destination was accepted")
    if refusals != 20:
        raise OfnerAcquisitionRefusal("generated refusal accounting differs")

    repo = Path(repo_root)
    module_path = Path(__file__).resolve()
    result = {
        "schema_name": "neurodecodekit.ofner_2017_motor_imagery_acquisition_generated_qualification",
        "schema_version": "0.1.0",
        "status": "accepted_generated_only",
        "lane_id": "OFNER-C6R-1-G",
        "source_record": {
            "path": str(SOURCE_RECORD_RELATIVE_PATH),
            "sha256": SOURCE_RECORD_SHA256,
        },
        "implementation_artifact": {
            "path": str(module_path.relative_to(repo.resolve())),
            "sha256": _sha256_file(module_path),
        },
        "measurements": {
            "manifest_replays": 2,
            "acquisition_replays": 2,
            "selected_files_per_replay": len(first_members),
            "participant_run_cells_per_replay": len(first_members),
            "generated_payload_bytes_per_replay": generated_bytes,
            "adversarial_refusals": refusals,
            "runtime_seconds": time.perf_counter() - started,
            "peak_rss_bytes": _peak_rss_bytes(),
            "retained_generated_payload_bytes": 0,
            "network_bytes": 0,
        },
        "determinism": {
            "canonical_identity_equal_after_signed_URL_refresh": True,
            "acquisition_directory_digest_equal": True,
            "directory_digest_sha256": replay_digests[0],
        },
        "capabilities": {
            "strict_complete_matrix_selection": True,
            "stable_identity_separated_from_volatile_transport": True,
            "signed_transport_validation": True,
            "target_like_row_field_firewall": True,
            "atomic_bounded_opaque_writer": True,
            "live_network_client_present": False,
            "real_payload_execution_present": False,
            "GDF_parser_present": False,
        },
        "registered_plan_digest": _sha256_bytes(_canonical_json_bytes(registered)),
        "operation_counters": {
            "real_manifest_requests": 0,
            "real_payload_requests": 0,
            "real_payload_bytes": 0,
            "GDF_header_reads": 0,
            "event_or_annotation_reads": 0,
            "target_or_label_reads": 0,
            "signal_sample_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scientific_scores": 0,
        },
        "warnings": [
            "generated_fixture_only",
            "synthetic_binary_bytes_are_not_EEG",
            "real_GDF_transport_and_header_remain_separately_gated",
            "no_neural_advantage_or_unseen_person_result",
            "no_scientific_claim",
        ],
    }
    if len(_canonical_json_bytes(result)) > 1024 * 1024:
        raise OfnerAcquisitionRefusal("generated qualification result exceeded output cap")
    return result


def write_generated_qualification_result(
    repo_root: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    """Run the generated qualification and create one non-replacing result."""

    result = run_generated_qualification(repo_root)
    output = Path(output_path)
    if output.exists() or output.is_symlink():
        raise OfnerAcquisitionRefusal("generated qualification output already exists")
    payload = _canonical_json_bytes(result)
    if len(payload) > 1024 * 1024:
        raise OfnerAcquisitionRefusal("generated qualification output exceeded cap")
    output.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(output, flags, 0o600)
    try:
        _write_all(descriptor, payload)
    finally:
        os.close(descriptor)
    return result
