"""Proof-gated live Stage A acquisition for BNCI-C3C5-1.

This module is additive so the generated G1 implementation remains byte-identical.
It interprets only transport metadata, byte counts, and payload digests.
"""

from __future__ import annotations

import hashlib
import json
import os
import resource
import shutil
import ssl
import stat
import sys
import time
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterable, Mapping

from neurodecodekit.datasets.bnci_2014_001_acquisition import (
    ATTEMPT_CAP_PER_FILE,
    BASE_URL,
    DISK_CAP_BYTES,
    FREE_DISK_FLOOR_BYTES,
    LANE_ID,
    NETWORK_CAP_BYTES,
    REGISTERED_BYTES,
    REGISTERED_FILES,
    REQUEST_CAP,
    SCHEMA_VERSION,
    BNCIAcquisitionRefusal,
    TransportResponse,
    acquire_members,
    registered_members,
)


G1_PROOF_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_result_proof.v0.json"
)
G1_PROOF_SHA256 = "aad6cca7e3c14dbad2f4934f9d16d417effc7ef5db01a45c2918ee8ff253f434"
G1_PROOF_COMMIT = "cf476982d70cbd6c710b7d0a67352765155c6bc1"
G1_PROOF_CI_RUN_ID = 32_767_245_101
G1_PROOF_BASE_JOB_ID = 97_559_394_298
G1_PROOF_OPTIONAL_JOB_ID = 97_559_394_437
STAGE_A_BUNDLE_RELATIVE_PATH = Path(".codex_work/bnci_c3c5/stage_a_payload_v0")
STAGE_A_MARKER_RELATIVE_PATH = Path(
    ".codex_work/bnci_c3c5/stage_a_acquisition_v0.consumed.json"
)
STAGE_A_RECEIPT_RELATIVE_PATH = Path(
    ".codex_work/bnci_c3c5/stage_a_acquisition_receipt.private.v0.json"
)
CHUNK_BYTES = 1_048_576
REQUEST_TIMEOUT_SECONDS = 120.0
RUNTIME_CAP_SECONDS = 1_800.0
PEAK_RSS_CAP_BYTES = 1_073_741_824
PUBLIC_OUTPUT_CAP_BYTES = 4_194_304
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


OpenRequest = Callable[[urllib.request.Request, float], BinaryIO]


class StandardLibraryRangeTransport:
    """TLS-verified, proxy-free, no-redirect sequential GET transport."""

    def __init__(self, *, opener: OpenRequest | None = None) -> None:
        if opener is not None:
            self._open = opener
            return
        context = ssl.create_default_context()
        built = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            _NoRedirect(),
            urllib.request.HTTPSHandler(context=context),
        )
        self._open = lambda request, timeout: built.open(request, timeout=timeout)

    def __call__(self, url: str, offset: int) -> TransportResponse:
        headers = {
            "Accept-Encoding": "identity",
            "User-Agent": "NeuroDecodeKit-BNCI-C3C5-1/0.1",
        }
        if offset:
            headers["Range"] = f"bytes={offset}-"
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            response = self._open(request, REQUEST_TIMEOUT_SECONDS)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ConnectionError("registered payload request failed") from exc
        if response.geturl() != url:
            response.close()
            raise BNCIAcquisitionRefusal("payload response redirected")
        content_length = _single_decimal_header(response.headers, "Content-Length")
        content_encoding = response.headers.get("Content-Encoding")
        if content_encoding not in (None, "identity"):
            response.close()
            raise BNCIAcquisitionRefusal("payload response encoding is not identity")
        range_start = _content_range_start(response.headers)
        status_code = response.getcode()

        def body() -> Iterable[bytes]:
            observed = 0
            try:
                while True:
                    chunk = response.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    if not isinstance(chunk, bytes):
                        raise BNCIAcquisitionRefusal("payload transport yielded non-bytes")
                    observed += len(chunk)
                    yield chunk
                if observed != content_length:
                    raise ConnectionError("registered payload stream ended early")
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                raise ConnectionError("registered payload stream failed") from exc
            finally:
                response.close()

        return TransportResponse(
            status=status_code,
            content_length=content_length,
            range_start=range_start,
            body=body(),
        )


def _canonical_bytes(value: Any) -> bytes:
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


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _single_decimal_header(headers: Message, name: str) -> int:
    values = headers.get_all(name, [])
    if len(values) != 1 or not values[0].isdigit():
        raise BNCIAcquisitionRefusal(f"payload response {name} is invalid")
    return int(values[0])


def _content_range_start(headers: Message) -> int | None:
    values = headers.get_all("Content-Range", [])
    if not values:
        return None
    if len(values) != 1:
        raise BNCIAcquisitionRefusal("payload response Content-Range is duplicated")
    value = values[0]
    if not value.startswith("bytes ") or "-" not in value or "/" not in value:
        raise BNCIAcquisitionRefusal("payload response Content-Range is invalid")
    start = value.removeprefix("bytes ").split("-", 1)[0]
    if not start.isdigit():
        raise BNCIAcquisitionRefusal("payload response Content-Range start is invalid")
    return int(start)


def _peak_rss_bytes() -> int:
    observed = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(observed if sys.platform == "darwin" else observed * 1024)


def _read_regular_nofollow(path: Path, maximum_bytes: int) -> bytes:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise BNCIAcquisitionRefusal("proof path is not a regular no-follow file")
    if info.st_size > maximum_bytes:
        raise BNCIAcquisitionRefusal("proof path exceeds its byte cap")
    with path.open("rb") as handle:
        payload = handle.read(maximum_bytes + 1)
    if len(payload) != info.st_size:
        raise BNCIAcquisitionRefusal("proof path changed during read")
    return payload


def read_green_g1_proof(repo_root: str | Path) -> dict[str, Any]:
    proof_bytes = _read_regular_nofollow(
        Path(repo_root) / G1_PROOF_RELATIVE_PATH,
        PUBLIC_OUTPUT_CAP_BYTES,
    )
    if _sha256(proof_bytes) != G1_PROOF_SHA256:
        raise BNCIAcquisitionRefusal("G1 proof registry hash changed")
    try:
        proof = json.loads(proof_bytes)
    except json.JSONDecodeError as exc:
        raise BNCIAcquisitionRefusal("G1 proof registry JSON is invalid") from exc
    green = proof.get("green_result", {})
    closed = proof.get("closed_result", {})
    if (
        proof.get("status") != "proof_only_closeout_effective_after_own_remote_green"
        or green.get("commit") != "4ef12dd056358907ab6734c7a2a21e6776f6f6af"
        or green.get("CI_run_id") != 32_765_504_463
        or green.get("base_python_job_id") != 97_553_936_562
        or green.get("optional_neuro_readers_job_id") != 97_553_936_838
        or green.get("both_required_jobs_green") is not True
        or closed.get("status") != "passed_generated_mocked_qualification_only"
        or closed.get("qualification_may_be_repeated") is not False
        or closed.get("real_operations") != 0
    ):
        raise BNCIAcquisitionRefusal("G1 proof evidence changed")
    return proof


def _exclusive_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or not path.parent.is_dir():
        raise BNCIAcquisitionRefusal("Stage A output parent is unsafe")
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise BNCIAcquisitionRefusal("Stage A output already exists") from exc


def _freeze_threads(environ: Mapping[str, str]) -> None:
    if any(environ.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise BNCIAcquisitionRefusal("Stage A thread environment is not frozen")


def execute_registered_acquisition(
    repo_root: str | Path,
    *,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Run the one registered opaque Stage A acquisition after all proof barriers."""

    root = Path(repo_root).resolve()
    if root != Path(__file__).resolve().parents[3]:
        raise BNCIAcquisitionRefusal("Stage A repository root differs")
    _freeze_threads(environ)
    read_green_g1_proof(root)
    bundle = root / STAGE_A_BUNDLE_RELATIVE_PATH
    marker = root / STAGE_A_MARKER_RELATIVE_PATH
    receipt_path = root / STAGE_A_RECEIPT_RELATIVE_PATH
    for protected in (bundle, marker, receipt_path):
        if protected.exists() or protected.is_symlink():
            raise BNCIAcquisitionRefusal("Stage A is already consumed or has output")
    free_before = shutil.disk_usage(root).free
    if free_before < FREE_DISK_FLOOR_BYTES:
        raise BNCIAcquisitionRefusal("Stage A free-disk floor is not satisfied")
    marker_payload = _canonical_bytes(
        {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_a_consumed_marker",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "consumed_before_first_live_transport_construction",
            "G1_proof_commit": G1_PROOF_COMMIT,
            "G1_proof_CI_run_id": G1_PROOF_CI_RUN_ID,
            "rerun_allowed": False,
        }
    )
    _exclusive_write(marker, marker_payload)
    started = time.perf_counter()
    manifest = acquire_members(
        registered_members(),
        bundle,
        transport=StandardLibraryRangeTransport(),
    )
    runtime_seconds = time.perf_counter() - started
    peak_rss_bytes = _peak_rss_bytes()
    if runtime_seconds > RUNTIME_CAP_SECONDS:
        raise BNCIAcquisitionRefusal("Stage A runtime cap exceeded")
    if peak_rss_bytes > PEAK_RSS_CAP_BYTES:
        raise BNCIAcquisitionRefusal("Stage A peak RSS cap exceeded")
    private_manifest = bundle / "manifest.private.v0.json"
    private_manifest_bytes = private_manifest.lstat().st_size
    free_after = shutil.disk_usage(root).free
    receipt = {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_a_acquisition_receipt",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "complete_opaque_exact_payload_bundle",
        "proof_barrier": {
            "G1_proof_commit": G1_PROOF_COMMIT,
            "G1_proof_CI_run_id": G1_PROOF_CI_RUN_ID,
            "G1_proof_base_job_id": G1_PROOF_BASE_JOB_ID,
            "G1_proof_optional_job_id": G1_PROOF_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "measurements": {
            "input_network_bytes": manifest["network_bytes"],
            "accepted_payload_bytes": manifest["payload_bytes"],
            "private_manifest_bytes": private_manifest_bytes,
            "incremental_output_bytes": manifest["payload_bytes"] + private_manifest_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_process_RSS_bytes": peak_rss_bytes,
            "free_disk_bytes_before": free_before,
            "free_disk_bytes_after": free_after,
        },
        "operations": {
            "payload_files": manifest["file_count"],
            "payload_requests": manifest["payload_requests"],
            "opaque_post_write_hash_opens": manifest["file_count"],
            "MAT_semantic_content_opens": 0,
            "MAT_semantic_parses": 0,
            "signal_event_target_or_label_reads": 0,
            "cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "target_deliveries": 0,
            "scores": 0,
        },
        "resources": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "payload_files_exact": REGISTERED_FILES,
            "payload_bytes_exact": REGISTERED_BYTES,
            "payload_requests_maximum": REQUEST_CAP,
            "attempts_per_file_maximum": ATTEMPT_CAP_PER_FILE,
            "network_bytes_maximum": NETWORK_CAP_BYTES,
            "incremental_disk_bytes_maximum": DISK_CAP_BYTES,
            "runtime_seconds_maximum": RUNTIME_CAP_SECONDS,
            "peak_RSS_bytes_maximum": PEAK_RSS_CAP_BYTES,
        },
        "warnings": [
            "payload_is_private_and_Git_ignored",
            "payload_bytes_were_hashed_but_not_semantically_interpreted",
            "Stage_A_is_consumed_and_cannot_be_rerun",
            "no_scientific_or_decoding_claim_is_established",
        ],
        "next_gate": "commit_push_and_green_aggregate_Stage_A_result_before_Q",
        "claim_boundary": {
            "engineering_capability": "exact_private_BNCI_payload_bundle_acquired_and_verified",
            "scientific_claim_established": False,
        },
    }
    receipt_bytes = _canonical_bytes(receipt)
    if len(receipt_bytes) > PUBLIC_OUTPUT_CAP_BYTES:
        raise BNCIAcquisitionRefusal("Stage A receipt exceeds public output cap")
    _exclusive_write(receipt_path, receipt_bytes)
    return receipt


def registered_stage_a_plan(repo_root: str | Path) -> dict[str, Any]:
    """Return the proof-bound Stage A plan without touching ignored paths or network."""

    read_green_g1_proof(repo_root)
    return {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_a_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "plan_only_no_ignored_path_or_network_operation",
        "base_url": BASE_URL,
        "payload_files": REGISTERED_FILES,
        "payload_bytes": REGISTERED_BYTES,
        "proof_commit": G1_PROOF_COMMIT,
        "proof_CI_run_id": G1_PROOF_CI_RUN_ID,
        "next_operation": "one_proof_gated_opaque_acquisition",
    }
