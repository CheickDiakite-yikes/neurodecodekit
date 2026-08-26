"""Generated qualification primitives for the DREYER-C5R-1 Stage H preflight."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets.dreyer_c5r_1 import (
    DreyerDataRefusal,
    EDFHeaderSummary,
    build_generated_edf_header,
    parse_edf_fixed_header,
)
from neurodecodekit.experiments import dreyer_c5r_1 as parent

LANE_ID = "DREYER-C5R-1-H"
PARENT_LANE_ID = "DREYER-C5R-1"
CONTRACT_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_preflight_contract.v0.json"
)
CONTRACT_SHA256 = "5c2c795340bd90a5a361b4be47216d927fa918a474913d7d16af0310036252e9"
REGISTERED_RESULT_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_generated_qualification_result.v0.json"
)
PREFLIGHT_URL = (
    "https://data.nemar.org/nm000250/v1.0.4/sourcedata/sub-01/eeg/"
    "sub-01_task-R1acquisition_eeg.edf"
)
PREFLIGHT_PATH = "sourcedata/sub-01/eeg/sub-01_task-R1acquisition_eeg.edf"
PREFLIGHT_BYTES = 14_805_604
PREFLIGHT_SHA256 = "a678fe6d37e0496eb381dcac6b877b047d02dfffc659ae4cfc38226f4850e185"
EXPECTED_SAMPLING_RATE_HZ = 512.0
EXPECTED_EEG_LABELS = (
    "Fz",
    "FCz",
    "Cz",
    "CPz",
    "Pz",
    "C1",
    "C3",
    "C5",
    "C2",
    "C4",
    "C6",
    "F4",
    "FC2",
    "FC4",
    "FC6",
    "CP2",
    "CP4",
    "CP6",
    "P4",
    "F3",
    "FC1",
    "FC3",
    "FC5",
    "CP1",
    "CP3",
    "CP5",
    "P3",
)
EXPECTED_EOG_COUNT = 3
EXPECTED_EMG_COUNT = 2
MAX_ANNOTATION_CHANNELS = 1
MAX_FIXED_HEADER_BYTES = 65_536
STREAM_CHUNK_BYTES = 1_048_576
GENERATED_CAPS = {
    "runtime_seconds_maximum": 30,
    "peak_process_tree_RSS_bytes_maximum": 268_435_456,
    "generated_input_bytes_maximum": 33_554_432,
    "private_temporary_bytes_maximum": 33_554_432,
    "public_output_bytes_maximum": 1_048_576,
}


class StageHRefusal(RuntimeError):
    """Fail-closed refusal for Stage H preflight behavior."""


@dataclass(frozen=True)
class PreflightSpec:
    """Immutable identity for one preflight payload."""

    url: str
    relative_path: str
    bytes: int
    sha256: str


REGISTERED_SPEC = PreflightSpec(
    url=PREFLIGHT_URL,
    relative_path=PREFLIGHT_PATH,
    bytes=PREFLIGHT_BYTES,
    sha256=PREFLIGHT_SHA256,
)


class FixtureHeaders:
    """Small generated stand-in for an HTTP response header collection."""

    def __init__(self, values: Mapping[str, str | Sequence[str]]) -> None:
        self._values: dict[str, tuple[str, ...]] = {}
        for name, value in values.items():
            items = (value,) if isinstance(value, str) else tuple(value)
            self._values[name.casefold()] = tuple(str(item) for item in items)

    def get_all(self, name: str) -> list[str] | None:
        values = self._values.get(name.casefold())
        return list(values) if values is not None else None


class FixtureResponse:
    """Generated response object used only by the Stage H qualification."""

    def __init__(
        self,
        body: bytes,
        *,
        url: str,
        status: int = 200,
        headers: Mapping[str, str | Sequence[str]] | None = None,
        maximum_read_bytes: int | None = None,
        nonbytes_first_read: bool = False,
    ) -> None:
        self.status = status
        self.headers = FixtureHeaders(
            headers if headers is not None else {"Content-Length": str(len(body))}
        )
        self._url = url
        self._body = body
        self._offset = 0
        self._maximum_read_bytes = maximum_read_bytes
        self._nonbytes_first_read = nonbytes_first_read
        self._read_calls = 0

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


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8")
        + b"\n"
    )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_contract(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    payload = (repository / CONTRACT_RELATIVE_PATH).read_bytes()
    if _sha256(payload) != CONTRACT_SHA256:
        raise StageHRefusal("Stage H contract hash changed")
    value = json.loads(payload)
    if not isinstance(value, dict) or value.get("lane_id") != LANE_ID:
        raise StageHRefusal("Stage H contract identity changed")
    preflight = value.get("preflight")
    expected = {
        "url": REGISTERED_SPEC.url,
        "path": REGISTERED_SPEC.relative_path,
        "bytes": REGISTERED_SPEC.bytes,
        "sha256": REGISTERED_SPEC.sha256,
    }
    if not isinstance(preflight, dict) or any(
        preflight.get(name) != item for name, item in expected.items()
    ):
        raise StageHRefusal("Stage H registered member changed")
    return value


def _normalized_label(value: str) -> str:
    return value.strip().casefold()


def _compact_label(value: str) -> str:
    return "".join(character for character in _normalized_label(value) if character.isalnum())


def validate_sensor_contract(summary: EDFHeaderSummary) -> dict[str, Any]:
    """Validate the frozen roster and return only allowlisted structural facts."""

    normalized = tuple(_normalized_label(label) for label in summary.labels)
    if len(set(normalized)) != len(normalized):
        raise StageHRefusal("Stage H signal labels are duplicated")
    expected_lookup = {_normalized_label(label): label for label in EXPECTED_EEG_LABELS}
    observed_eeg: list[str] = []
    observed_eog: list[str] = []
    observed_emg: list[str] = []
    annotation_count = 0
    unknown: list[str] = []
    physiological_indices: list[int] = []
    for index, label in enumerate(summary.labels):
        normalized_label = _normalized_label(label)
        compact = _compact_label(label)
        if normalized_label in expected_lookup:
            observed_eeg.append(expected_lookup[normalized_label])
            physiological_indices.append(index)
        elif compact.startswith("eog"):
            observed_eog.append(label.strip())
            physiological_indices.append(index)
        elif compact.startswith("emg"):
            observed_emg.append(label.strip())
            physiological_indices.append(index)
        elif compact in {"edfannotation", "edfannotations"}:
            annotation_count += 1
        else:
            unknown.append(label.strip())
    if set(observed_eeg) != set(EXPECTED_EEG_LABELS) or len(observed_eeg) != len(
        EXPECTED_EEG_LABELS
    ):
        raise StageHRefusal("Stage H EEG roster differs from the frozen 27 channels")
    if len(observed_eog) != EXPECTED_EOG_COUNT:
        raise StageHRefusal("Stage H EOG roster does not contain exactly three channels")
    if len(observed_emg) != EXPECTED_EMG_COUNT:
        raise StageHRefusal("Stage H EMG roster does not contain exactly two channels")
    if annotation_count > MAX_ANNOTATION_CHANNELS:
        raise StageHRefusal("Stage H contains more than one annotation channel")
    if unknown:
        raise StageHRefusal("Stage H contains an unrecognized signal label")
    if any(
        summary.sampling_rates_hz[index] != EXPECTED_SAMPLING_RATE_HZ
        for index in physiological_indices
    ):
        raise StageHRefusal("Stage H physiological sampling rate differs from 512 Hz")
    return {
        "header_bytes": summary.header_bytes,
        "signal_count": summary.signal_count,
        "EEG_channel_count": len(observed_eeg),
        "EEG_roster_matches_frozen_27": True,
        "EOG_channel_count": len(observed_eog),
        "EOG_labels": observed_eog,
        "EMG_channel_count": len(observed_emg),
        "EMG_labels": observed_emg,
        "annotation_channel_count": annotation_count,
        "physiological_sampling_rate_hz": EXPECTED_SAMPLING_RATE_HZ,
        "all_physiological_channels_match_sampling_rate": True,
    }


def _header_values(headers: Any, name: str) -> tuple[str, ...]:
    getter = getattr(headers, "get_all", None)
    if not callable(getter):
        raise StageHRefusal("Stage H response headers do not preserve multiplicity")
    values = getter(name)
    if values is None:
        return ()
    if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
        raise StageHRefusal("Stage H response header values are malformed")
    return tuple(values)


def _prepare_private_destination(path: str | Path) -> Path:
    source = Path(path)
    if ".." in source.parts:
        raise StageHRefusal("Stage H output traversal is forbidden")
    candidate = source.expanduser().absolute()
    if candidate.exists() or candidate.is_symlink():
        raise StageHRefusal("Stage H destination already exists")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    parent_info = candidate.parent.lstat()
    if stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode):
        raise StageHRefusal("Stage H destination parent is not a real directory")
    return candidate


def _consume_exact(
    response: Any,
    byte_count: int,
    *,
    handle: Any,
    digest: Any,
) -> bytes:
    captured = bytearray()
    while len(captured) < byte_count:
        requested = min(STREAM_CHUNK_BYTES, byte_count - len(captured))
        chunk = response.read(requested)
        if type(chunk) is not bytes:
            raise StageHRefusal("Stage H response returned a non-bytes body chunk")
        if not chunk:
            raise StageHRefusal("Stage H response ended before the declared payload size")
        if len(chunk) > requested:
            raise StageHRefusal("Stage H response exceeded the requested chunk size")
        written = handle.write(chunk)
        if written != len(chunk):
            raise StageHRefusal("Stage H private payload write made incomplete progress")
        digest.update(chunk)
        captured.extend(chunk)
    return bytes(captured)


def stream_verified_preflight(
    response: Any,
    spec: PreflightSpec,
    destination: str | Path,
) -> dict[str, Any]:
    """Stream, verify, and fixed-header-parse exactly one already-open response."""

    if (
        not isinstance(spec, PreflightSpec)
        or not spec.url.startswith("https://")
        or not spec.relative_path
        or spec.bytes < 512
        or len(spec.sha256) != 64
        or any(character not in "0123456789abcdef" for character in spec.sha256)
    ):
        raise StageHRefusal("Stage H preflight specification is malformed")
    output = _prepare_private_destination(destination)
    status = getattr(response, "status", None)
    final_url_getter = getattr(response, "geturl", None)
    if status != 200 or not callable(final_url_getter) or final_url_getter() != spec.url:
        raise StageHRefusal("Stage H response status or final URL differs")
    content_lengths = _header_values(getattr(response, "headers", None), "Content-Length")
    if len(content_lengths) != 1 or content_lengths[0] != str(spec.bytes):
        raise StageHRefusal("Stage H Content-Length differs from the exact payload size")
    if _header_values(getattr(response, "headers", None), "Content-Encoding"):
        raise StageHRefusal("Stage H encoded transfer is forbidden")
    temporary = output.with_name(f".{output.name}.{os.getpid()}.stage-h.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise StageHRefusal("Stage H private temporary destination already exists")
    digest = hashlib.sha256()
    try:
        with temporary.open("xb") as handle:
            prefix = _consume_exact(response, 256, handle=handle, digest=digest)
            declared_text = prefix[184:192]
            try:
                declared_string = declared_text.decode("ascii").strip()
            except UnicodeDecodeError as exc:
                raise StageHRefusal("Stage H EDF header length is non-ASCII") from exc
            if not declared_string.isdigit():
                raise StageHRefusal("Stage H EDF header length is malformed")
            header_bytes = int(declared_string)
            if header_bytes < 512 or header_bytes > MAX_FIXED_HEADER_BYTES:
                raise StageHRefusal("Stage H EDF header length is outside the safety range")
            remainder = _consume_exact(
                response,
                header_bytes - len(prefix),
                handle=handle,
                digest=digest,
            )
            try:
                summary = parse_edf_fixed_header(prefix + remainder)
            except DreyerDataRefusal as exc:
                raise StageHRefusal("Stage H EDF fixed header is malformed") from exc
            sensor_contract = validate_sensor_contract(summary)
            consumed = header_bytes
            while consumed < spec.bytes:
                amount = min(STREAM_CHUNK_BYTES, spec.bytes - consumed)
                chunk = _consume_exact(response, amount, handle=handle, digest=digest)
                consumed += len(chunk)
            extra = response.read(1)
            if type(extra) is not bytes or extra:
                raise StageHRefusal("Stage H response continued past the exact payload size")
            handle.flush()
            os.fsync(handle.fileno())
        if digest.hexdigest() != spec.sha256:
            raise StageHRefusal("Stage H payload SHA-256 differs")
        info = temporary.lstat()
        if (
            stat.S_ISLNK(info.st_mode)
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_size != spec.bytes
        ):
            raise StageHRefusal("Stage H retained payload identity differs")
        if output.exists() or output.is_symlink():
            raise StageHRefusal("Stage H destination appeared before publication")
        os.rename(temporary, output)
        return {
            "payload_bytes": spec.bytes,
            "payload_sha256": spec.sha256,
            "payload_retained": True,
            "body_hash_passes": 1,
            "fixed_header_semantic_parses": 1,
            "annotation_semantic_reads": 0,
            "signal_sample_semantic_reads": 0,
            "sensor_contract": sensor_contract,
        }
    finally:
        if temporary.exists() and not temporary.is_symlink():
            temporary.unlink()


def _fixture_body(
    labels: Sequence[str],
    *,
    sampling_rate_hz: int = 512,
    suffix_bytes: int = 1024,
) -> bytes:
    header = build_generated_edf_header(labels, sampling_rate_hz=sampling_rate_hz)
    suffix = bytes((index * 17 + 29) % 256 for index in range(suffix_bytes))
    return header + suffix


def _fixture_spec(body: bytes) -> PreflightSpec:
    return PreflightSpec(
        url="https://generated.invalid/stage-h.edf",
        relative_path="generated/stage-h.edf",
        bytes=len(body),
        sha256=_sha256(body),
    )


def _valid_labels() -> tuple[str, ...]:
    return EXPECTED_EEG_LABELS + (
        "EOG-VU",
        "EOG-VD",
        "EOG-H",
        "EMG-LH",
        "EMG-RH",
        "EDF Annotations",
    )


def _expect_refusal(
    response: FixtureResponse,
    spec: PreflightSpec,
    destination: Path,
) -> None:
    try:
        stream_verified_preflight(response, spec, destination)
    except StageHRefusal:
        pass
    else:
        raise StageHRefusal("Stage H generated adversarial case did not refuse")
    if destination.exists() or destination.is_symlink():
        raise StageHRefusal("Stage H refused case retained an output")


def _run_generated_cases(root: Path) -> tuple[dict[str, Any], int, int]:
    labels = _valid_labels()
    body = _fixture_body(labels)
    spec = _fixture_spec(body)
    generated_bytes = 0
    retained_bytes = 0
    first_path = root / "valid-first.edf"
    first = stream_verified_preflight(
        FixtureResponse(body, url=spec.url), spec, first_path
    )
    generated_bytes += len(body)
    retained_bytes += first_path.stat().st_size
    second_path = root / "valid-replay.edf"
    second = stream_verified_preflight(
        FixtureResponse(body, url=spec.url, maximum_read_bytes=97), spec, second_path
    )
    generated_bytes += len(body)
    retained_bytes += second_path.stat().st_size
    if first != second or first_path.read_bytes() != second_path.read_bytes():
        raise StageHRefusal("Stage H generated replay differs")

    cases: list[tuple[str, FixtureResponse, PreflightSpec]] = []
    cases.append(("HTTP_status", FixtureResponse(body, url=spec.url, status=404), spec))
    cases.append(
        ("redirect", FixtureResponse(body, url="https://generated.invalid/other.edf"), spec)
    )
    cases.append(
        (
            "missing_Content_Length",
            FixtureResponse(body, url=spec.url, headers={}),
            spec,
        )
    )
    cases.append(
        (
            "duplicate_Content_Length",
            FixtureResponse(
                body,
                url=spec.url,
                headers={"Content-Length": (str(len(body)), str(len(body)))},
            ),
            spec,
        )
    )
    cases.append(
        (
            "wrong_Content_Length",
            FixtureResponse(
                body, url=spec.url, headers={"Content-Length": str(len(body) + 1)}
            ),
            spec,
        )
    )
    cases.append(
        (
            "content_encoding",
            FixtureResponse(
                body,
                url=spec.url,
                headers={"Content-Length": str(len(body)), "Content-Encoding": "gzip"},
            ),
            spec,
        )
    )
    cases.append(
        (
            "short_body",
            FixtureResponse(
                body[:-1], url=spec.url, headers={"Content-Length": str(len(body))}
            ),
            spec,
        )
    )
    cases.append(
        (
            "oversized_body",
            FixtureResponse(
                body + b"x", url=spec.url, headers={"Content-Length": str(len(body))}
            ),
            spec,
        )
    )
    cases.append(
        (
            "digest_mismatch",
            FixtureResponse(body, url=spec.url),
            PreflightSpec(spec.url, spec.relative_path, spec.bytes, "0" * 64),
        )
    )
    cases.append(
        (
            "nonbytes_body",
            FixtureResponse(body, url=spec.url, nonbytes_first_read=True),
            spec,
        )
    )
    malformed_header = b"1" + body[1:]
    cases.append(
        (
            "malformed_fixed_header",
            FixtureResponse(malformed_header, url=spec.url),
            _fixture_spec(malformed_header),
        )
    )
    roster_cases = {
        "missing_EEG": EXPECTED_EEG_LABELS[:-1] + labels[len(EXPECTED_EEG_LABELS) :],
        "wrong_EOG_count": EXPECTED_EEG_LABELS
        + ("EOG-VU", "EOG-VD", "EMG-LH", "EMG-RH", "EDF Annotations"),
        "wrong_EMG_count": EXPECTED_EEG_LABELS
        + ("EOG-VU", "EOG-VD", "EOG-H", "EMG-LH", "EDF Annotations"),
        "duplicate_label": EXPECTED_EEG_LABELS
        + ("EOG-VU", "EOG-VD", "EOG-H", "EMG-LH", "EMG-LH", "EDF Annotations"),
        "unknown_label": labels + ("MYSTERY",),
    }
    for name, candidate_labels in roster_cases.items():
        candidate = _fixture_body(candidate_labels)
        cases.append(
            (
                name,
                FixtureResponse(candidate, url=spec.url),
                PreflightSpec(spec.url, spec.relative_path, len(candidate), _sha256(candidate)),
            )
        )
    wrong_rate = _fixture_body(labels, sampling_rate_hz=511)
    cases.append(
        (
            "wrong_sampling_rate",
            FixtureResponse(wrong_rate, url=spec.url),
            PreflightSpec(spec.url, spec.relative_path, len(wrong_rate), _sha256(wrong_rate)),
        )
    )
    for index, (name, response, candidate_spec) in enumerate(cases):
        destination = root / f"refusal-{index}-{name}.edf"
        _expect_refusal(response, candidate_spec, destination)
        generated_bytes += len(response._body)

    occupied = root / "occupied.edf"
    occupied.write_bytes(b"preserve")
    proof_before = occupied.read_bytes()
    try:
        stream_verified_preflight(FixtureResponse(body, url=spec.url), spec, occupied)
    except StageHRefusal:
        pass
    else:
        raise StageHRefusal("Stage H no-clobber case did not refuse")
    if occupied.read_bytes() != proof_before:
        raise StageHRefusal("Stage H no-clobber case changed the existing file")
    generated_bytes += len(body)
    return (
        {
            "valid_cases_passed": 2,
            "adversarial_cases_refused": len(cases) + 1,
            "adversarial_case_names": [name for name, _response, _spec in cases]
            + ["no_clobber"],
            "deterministic_replay": True,
            "sensor_contract": first["sensor_contract"],
            "payload_sha256": spec.sha256,
        },
        generated_bytes,
        retained_bytes,
    )


def _result_payload(result: dict[str, Any]) -> bytes:
    previous = -1
    for _ in range(8):
        payload = _canonical_bytes(result)
        current = len(payload)
        result["measurements"]["public_output_bytes"] = current
        if current == previous:
            return _canonical_bytes(result)
        previous = current
    raise StageHRefusal("Stage H public byte accounting did not converge")


def run_generated_qualification(
    output_path: str | Path,
    *,
    root: str | Path | None = None,
    remote_proof_collector: Callable[[str | Path], dict[str, Any]] = (
        parent.collect_remote_green_proof
    ),
    peak_rss_reader: Callable[[], int] = parent.peak_process_tree_rss_bytes,
) -> dict[str, Any]:
    """Run the one registered generated/mock Stage H qualification."""

    parent.assert_single_thread_environment()
    repository = Path(root) if root is not None else _repo_root()
    contract = load_contract(repository)
    output = parent._prepare_output_path(output_path)
    proof = parent.validate_remote_green_proof(remote_proof_collector(repository))
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="neurodecodekit-stage-h-generated-") as name:
        cases, generated_bytes, retained_bytes = _run_generated_cases(Path(name))
    runtime = time.monotonic() - started
    peak_rss = peak_rss_reader()
    if type(peak_rss) is not int or peak_rss < 0:
        raise StageHRefusal("Stage H RSS measurement is invalid")
    caps = GENERATED_CAPS
    if runtime > caps["runtime_seconds_maximum"]:
        raise StageHRefusal("Stage H generated runtime cap exceeded")
    if peak_rss > caps["peak_process_tree_RSS_bytes_maximum"]:
        raise StageHRefusal("Stage H generated RSS cap exceeded")
    if generated_bytes > caps["generated_input_bytes_maximum"]:
        raise StageHRefusal("Stage H generated input cap exceeded")
    if retained_bytes > caps["private_temporary_bytes_maximum"]:
        raise StageHRefusal("Stage H generated temporary byte cap exceeded")
    result = {
        "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_generated_qualification_result",
        "schema_version": "0.1.0",
        "lane_id": LANE_ID,
        "status": "passed_generated_mock_only_no_real_data_or_network",
        "contract": {
            "path": str(CONTRACT_RELATIVE_PATH),
            "sha256": CONTRACT_SHA256,
            "verified": contract.get("status") == "generated_qualification_only",
        },
        "implementation_proof": {
            "fresh_remote_proof_collected_before_generated_fixture_work": True,
            "remote_green": proof,
        },
        "cases": cases,
        "measurements": {
            "runtime_seconds": runtime,
            "peak_process_tree_RSS_bytes": peak_rss,
            "generated_input_bytes": generated_bytes,
            "private_temporary_bytes": retained_bytes,
            "public_output_bytes": 0,
            "HTTP_requests": 0,
            "network_bytes": 0,
            "payload_hash_passes": 0,
            "fixed_header_semantic_parses": 0,
            "annotation_semantic_reads": 0,
            "signal_sample_semantic_reads": 0,
            "target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "target_deliveries": 0,
            "scores": 0,
            "producer_causal": False,
            "required_context_seconds": None,
            "end_to_end_latency_measured": False,
        },
        "planned_real_preflight": {
            "member": {
                "url": REGISTERED_SPEC.url,
                "path": REGISTERED_SPEC.relative_path,
                "bytes": REGISTERED_SPEC.bytes,
                "sha256": REGISTERED_SPEC.sha256,
            },
            "HTTP_GET_requests_maximum": 1,
            "payload_hash_passes_maximum": 1,
            "fixed_header_semantic_parses_maximum": 1,
            "remaining_cohort_payload_requests": 0,
            "real_authority": False,
        },
        "access_counters": {
            "pre_qualification_Git_remote_metadata_calls": 1,
            "pre_qualification_GitHub_Actions_metadata_calls": 2,
            "real_or_private_path_opens": 0,
            "real_HTTP_requests": 0,
            "real_network_bytes": 0,
            "real_EDF_payload_bytes": 0,
            "real_EDF_header_reads": 0,
            "real_annotation_reads": 0,
            "real_signal_sample_reads": 0,
            "real_target_or_label_reads": 0,
            "real_training_runs": 0,
            "real_prediction_sets": 0,
            "real_target_deliveries": 0,
            "real_scores": 0,
            "claim_upgrades": 0,
        },
        "warnings": [
            "generated_mock_preflight_has_no_scientific_claim_value",
            "real_source_EDF_sensor_roster_remains_unverified",
            "no_live_network_entry_point_exists",
            "causality_and_end_to_end_latency_are_not_applicable_to_header_preflight",
        ],
        "claim_boundary": {
            "engineering_capability": "bounded_stream_hash_fixed_EDF_header_sensor_contract_and_cleanup",
            "scientific_claim_not_established": "any_real_EEG_information_unseen_person_generalization_EEG_beyond_peripherals_movement_intention_language_live_hardware_or_clinical_result",
        },
    }
    payload = _result_payload(result)
    if len(payload) > caps["public_output_bytes_maximum"]:
        raise StageHRefusal("Stage H generated public output cap exceeded")
    parent._atomic_write(output, payload)
    return result


def inspect_generated_result(path: str | Path) -> dict[str, Any]:
    candidate = Path(path).expanduser().absolute()
    info = parent._regular_no_follow(candidate)
    if info.st_size > GENERATED_CAPS["public_output_bytes_maximum"]:
        raise StageHRefusal("Stage H result exceeds the inspect cap")
    value = json.loads(candidate.read_bytes())
    if not isinstance(value, dict) or value.get("lane_id") != LANE_ID:
        raise StageHRefusal("Stage H result identity differs")
    return {
        "status": value.get("status"),
        "cases": value.get("cases"),
        "measurements": value.get("measurements"),
        "access_counters": value.get("access_counters"),
        "warnings": value.get("warnings"),
        "claim_boundary": value.get("claim_boundary"),
    }
