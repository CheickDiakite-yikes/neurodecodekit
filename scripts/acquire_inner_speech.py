#!/usr/bin/env python3
"""One-shot, dry-run-first acquisition; never interpret BDF sample/status values.

Header offsets follow https://www.biosemi.com/faq/file_format.htm . Subject,
recording, date, transducer and prefilter text are never decoded or reported.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
import urllib.parse
import urllib.request


REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "registries/inner_speech_source_manifest.v0.json"
RESULT = REPO / "registries/inner_speech_acquisition_result.v0.json"
OUTPUT = Path(r"C:\Users\80714\AppData\Local\NeuroDecodeKit\ds003626_v2_1_2_ses01_20260922")
COMMIT = "d96743351ae4e5d0ee7a1384320ea8d52a2ce698"
GIB = 1024**3
CHUNK = 1024**2
PAYLOAD_BYTES = 6904627200
PAYLOAD_LIMIT = 10 * GIB
METADATA_LIMIT = 32 * CHUNK
DISK_FLOOR = 20 * GIB
WALL_SECONDS = 3600
MAX_CHANNELS = 512
FAILURE_METADATA_RESERVE = 4096
S3 = "https://s3.amazonaws.com/openneuro.org/ds003626/"
RAW = "https://raw.githubusercontent.com/OpenNeuroDatasets/ds003626/" + COMMIT + "/"
PATHS = tuple(f"sub-{i:02d}/ses-01/eeg/sub-{i:02d}_ses-01_task-innerspeech_eeg.bdf"
              for i in range(1, 11))


class Refusal(RuntimeError):
    """Only fixed, non-patient-bearing codes may enter failure metadata."""


def require(condition, code):
    if not condition:
        raise Refusal(code)


def blob_sha1(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def validate_manifest(manifest):
    require(isinstance(manifest, dict), "manifest_object")
    require((manifest.get("dataset"), manifest.get("version"), manifest.get("source_commit")) ==
            ("ds003626", "2.1.2", COMMIT), "manifest_identity")
    require(manifest.get("acquisition_id") == "INNER-SPEECH-ACQ-1", "acquisition_identity")
    require(manifest.get("license") == "CC0" and manifest.get("raw_companions") == [], "source_scope")
    require(manifest.get("resource_limits") == {
        "wall_seconds": WALL_SECONDS, "peak_rss_bytes": GIB,
        "generated_metadata_bytes": METADATA_LIMIT, "minimum_free_bytes": DISK_FLOOR,
        "workers": 1}, "resource_contract")
    files = manifest.get("files")
    require(isinstance(files, list) and len(files) == 10, "ten_files_required")
    require(all(isinstance(item, dict) for item in files), "file_record")
    require(sorted(item.get("path", "") for item in files) == list(PATHS), "exact_paths_required")
    for item in files:
        size, digest = item.get("size_bytes"), item.get("md5")
        require(type(size) is int and 0 < size <= PAYLOAD_LIMIT, "payload_size")
        require(isinstance(digest, str) and re.fullmatch("[0-9a-f]{32}", digest), "md5_pin")
        key = f"MD5E-s{size}--{digest}.bdf"
        pointer = item.get("annex_pointer")
        require(isinstance(pointer, str) and re.fullmatch(
            r"\.\./\.\./\.\./\.git/annex/objects/[A-Za-z0-9]{2}/[A-Za-z0-9]{2}/" +
            re.escape(key + "/" + key), pointer), "annex_pin")
        require(blob_sha1(pointer.encode("ascii")) == item.get("git_blob_sha1"), "annex_git_hash")
        url = item.get("url")
        require(isinstance(url, str), "payload_url")
        parsed = urllib.parse.urlsplit(url)
        base = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        require(base == S3 + item["path"] and not parsed.fragment, "payload_url")
        pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        require(len(pairs) == 1 and pairs[0][0] == "versionId" and
                0 < len(pairs[0][1]) <= 1024 and
                urllib.parse.urlencode(pairs) == parsed.query, "version_query")
        require(item.get("s3_version_id") == pairs[0][1], "version_pin")
    total = sum(item["size_bytes"] for item in files)
    require(total == PAYLOAD_BYTES == manifest.get("payload_bytes") and
            manifest.get("payload_limit_bytes") == PAYLOAD_LIMIT, "payload_total")
    metadata = manifest.get("metadata_files")
    require(isinstance(metadata, list) and len(metadata) == 2 and
            all(isinstance(item, dict) for item in metadata), "metadata_records")
    require(sorted(item.get("path", "") for item in metadata) == ["README", "dataset_description.json"],
            "metadata_paths")
    for item in metadata:
        require(type(item.get("size_bytes")) is int and 0 < item["size_bytes"] < METADATA_LIMIT,
                "metadata_size")
        require(isinstance(item.get("git_blob_sha1"), str) and
                re.fullmatch("[0-9a-f]{40}", item["git_blob_sha1"]), "metadata_hash")
        require(item.get("url") == RAW + item["path"], "metadata_url")
    require(sum(item["size_bytes"] for item in metadata) < METADATA_LIMIT, "metadata_total")
    return manifest


def load_manifest(path=MANIFEST):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result

    with Path(path).open("rb") as stream:
        content = stream.read(METADATA_LIMIT + 1)
    require(len(content) <= METADATA_LIMIT, "manifest_size")
    return validate_manifest(json.loads(content, object_pairs_hook=unique_object))


def _integer(field):
    require(re.fullmatch(rb" *[0-9]+ *", field) is not None, "header_integer")
    return int(field)


def _header_channels(fixed):
    require(len(fixed) == 256 and fixed[:8] == b"\xffBIOSEMI", "bdf_magic_or_truncated")
    count = _integer(fixed[252:256])
    require(137 <= count <= MAX_CHANNELS, "header_channel_count")
    require(_integer(fixed[184:192]) == 256 * (count + 1), "header_length")
    return count


def parse_bdf_header(header, file_size):
    """Pure header validation; no body, patient fields, dates or event decoding."""
    require(isinstance(header, bytes) and len(header) >= 256, "header_truncated")
    count = _header_channels(header[:256])
    require(len(header) == 256 * (count + 1), "header_truncated_or_body")
    require(header[192:236].strip() == b"24BIT", "bdf_24bit_marker")
    records = _integer(header[236:244])
    require(records > 0, "header_record_count")
    try:
        duration = Decimal(header[244:252].decode("ascii").strip())
    except (InvalidOperation, UnicodeDecodeError):
        raise Refusal("header_record_duration") from None
    require(duration.is_finite() and duration > 0, "header_record_duration")
    labels = []
    for index in range(count):
        field = header[256 + index * 16:256 + (index + 1) * 16]
        require(all(32 <= value < 127 for value in field), "header_channel_label")
        label = field.decode("ascii").strip()
        require(bool(label) and label not in labels, "header_channel_label")
        labels.append(label)
    eeg = {f"{bank}{i}" for bank in "ABCD" for i in range(1, 33)}
    require(eeg.issubset(labels), "missing_required_eeg")
    require({f"EXG{i}" for i in range(1, 9)}.issubset(labels), "missing_required_exg_or_lip")
    require(labels[-1] == "Status", "missing_final_status")
    offset = 256 + 216 * count
    samples = [_integer(header[offset + 8*i:offset + 8*(i+1)]) for i in range(count)]
    require(all(Decimal(value) == 1024 * duration for value in samples), "sampling_rate_not_1024")
    expected = len(header) + 3 * records * sum(samples)
    require(type(file_size) is int and file_size == expected, "bdf_file_geometry")
    return {"format": "BioSemi BDF", "sample_bits": 24, "header_bytes": len(header),
            "channel_count": count, "required_eeg_channels": 128, "required_exg_channels": 8,
            "additional_channels": count - 137, "status_channel_present": True,
            "sampling_hz_all_channels": 1024, "data_records": records,
            "record_duration_seconds": float(duration), "samples_per_record_sum": sum(samples),
            "file_geometry_verified": True, "all_channels_retained": True,
            "patient_recording_date_fields_reported": False, "sample_or_status_values_parsed": False}


def inspect_header(path, file_size):
    with Path(path).open("rb") as stream:
        fixed = stream.read(256)
        count = _header_channels(fixed)
        variable = stream.read(256 * count)
    return parse_bdf_header(fixed + variable, file_size)


class Budget:
    def __init__(self, storage_path):
        try:
            import psutil
        except ImportError:
            raise Refusal("execute_requires_psutil_rss_monitor") from None
        self.process = psutil.Process()
        self.storage_path = Path(storage_path)
        self.started = time.monotonic()
        self.deadline = self.started + WALL_SECONDS
        self.peak_rss = self.payload_bytes = self.metadata_bytes = self.generated_metadata_bytes = 0

    def check(self):
        self.peak_rss = max(self.peak_rss, self.process.memory_info().rss)
        require(time.monotonic() < self.deadline, "wall_budget")
        require(self.peak_rss <= GIB, "rss_budget")
        require(self.payload_bytes <= PAYLOAD_LIMIT, "payload_budget")
        require(self.metadata_bytes <= METADATA_LIMIT - FAILURE_METADATA_RESERVE, "metadata_budget")
        require(shutil.disk_usage(self.storage_path).free >= DISK_FLOOR, "disk_floor")

    def timeout(self):
        self.check()
        return min(60.0, max(0.001, self.deadline - time.monotonic()))

    def account(self, amount, *, payload):
        if payload:
            self.payload_bytes += amount
        else:
            self.metadata_bytes += amount
        self.check()


def write_json(path, payload, budget=None):
    encoded = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    require(len(encoded) <= METADATA_LIMIT, "metadata_budget")
    if budget is not None:
        budget.account(len(encoded), payload=False)
        budget.generated_metadata_bytes = getattr(budget, "generated_metadata_bytes", 0) + len(encoded)
    with Path(path).open("xb") as stream:
        stream.write(encoded)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Refusal("redirect_refused")


def download(item, destination, budget, *, metadata=False, opener=None):
    """Stream exactly one pinned object, retaining .partial on any refusal."""
    destination = Path(destination)
    partial = destination.with_name(destination.name + ".partial")
    require(not destination.exists() and not partial.exists(), "destination_exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected = item["size_bytes"]
    digest = hashlib.sha1(f"blob {expected}\0".encode("ascii")) if metadata else hashlib.md5()
    sha256 = hashlib.sha256()
    size = 0
    opener = opener or urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(item["url"], headers={
        "User-Agent": "NeuroDecodeKit-INNER-SPEECH-ACQ-1", "Accept-Encoding": "identity"})
    with partial.open("xb") as output:
        with opener.open(request, timeout=budget.timeout()) as source:
            require(source.status == 200 and source.geturl() == item["url"], "response_status_or_redirect")
            require(source.headers.get_all("Content-Length") == [str(expected)], "content_length")
            encoding = source.headers.get_all("Content-Encoding", [])
            require(not encoding or encoding == ["identity"], "content_encoding")
            require(not source.headers.get_all("Transfer-Encoding", []), "transfer_encoding")
            if not metadata:
                require(bool(item.get("s3_version_id")) and
                        source.headers.get_all("x-amz-version-id") == [item["s3_version_id"]], "response_version")
            while size < expected:
                try:
                    source.fp.raw._sock.settimeout(budget.timeout())
                except AttributeError:
                    raise Refusal("bounded_socket_required") from None
                chunk = source.read1(min(CHUNK, expected - size))
                require(bool(chunk) and len(chunk) <= min(CHUNK, expected - size), "truncated_or_oversized_body")
                budget.account(len(chunk), payload=not metadata)
                output.write(chunk)
                digest.update(chunk)
                sha256.update(chunk)
                size += len(chunk)
    require(digest.hexdigest() == item["git_blob_sha1" if metadata else "md5"], "content_hash")
    receipt = {"path": item["path"], "bytes": size, "sha256": sha256.hexdigest()}
    if metadata:
        receipt["git_blob_sha1"] = digest.hexdigest()
    else:
        receipt["md5"] = digest.hexdigest()
        receipt["header"] = inspect_header(partial, size)
    budget.check()
    # Hard-link publication is exclusive on Windows and POSIX; no rename overwrite race.
    os.link(partial, destination)
    partial.unlink()
    return receipt


def acquire(manifest, output, *, result_path=RESULT, budget=None, opener=None):
    validate_manifest(manifest)
    output, result_path = Path(output), Path(result_path)
    require(output.absolute() == OUTPUT.absolute() and output.resolve() == OUTPUT.absolute() and
            "onedrive" not in str(output).lower(), "fixed_local_output_required")
    require(not output.exists() and not result_path.exists(), "existing_run_or_result")
    with MANIFEST.open("rb") as stream:
        manifest_bytes = stream.read(METADATA_LIMIT + 1)
    require(len(manifest_bytes) <= METADATA_LIMIT and json.loads(manifest_bytes) == manifest,
            "manifest_changed")
    provenance = {"manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                  "acquisition_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    ancestor = output.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    require(shutil.disk_usage(ancestor).free >= DISK_FLOOR + PAYLOAD_BYTES + METADATA_LIMIT, "disk_reserve")
    budget = budget or Budget(ancestor)
    budget.check()
    output.mkdir(parents=True, exist_ok=False)
    files, metadata = [], []
    stage = "start"
    try:
        started_unix = time.time()
        write_json(output / "acquisition_started.json", {"acquisition_id": "INNER-SPEECH-ACQ-1",
                   "source_commit": COMMIT, "retry_or_resume_allowed": False, **provenance,
                   "started_unix": started_unix,
                   "started_utc": datetime.fromtimestamp(started_unix, timezone.utc).isoformat(),
                   "deadline_unix": started_unix + max(0, budget.deadline - time.monotonic()),
                   "wall_limit_seconds": WALL_SECONDS}, budget)
        opener = opener or urllib.request.build_opener(NoRedirect())
        stage = "metadata_transfer"
        for item in manifest["metadata_files"]:
            metadata.append(download(item, output / item["path"], budget, metadata=True, opener=opener))
        stage = "payload_transfer_and_header"
        for item in manifest["files"]:
            files.append(download(item, output / item["path"], budget, opener=opener))
            print(f"Verified BDF {len(files)}/10 (technical header only)", flush=True)
        require(len(files) == 10 and sum(item["bytes"] for item in files) == PAYLOAD_BYTES, "incomplete_acquisition")
        budget.check()
        report = {"schema_version": 1, "acquisition_id": "INNER-SPEECH-ACQ-1", "status": "complete",
                  "dataset": "ds003626", "version": "2.1.2", "source_commit": COMMIT,
                  **provenance,
                  "files_verified": len(files), "payload_bytes": sum(item["bytes"] for item in files),
                  "metadata_files": metadata, "files": files,
                  "elapsed_seconds": time.monotonic() - budget.started, "peak_rss_bytes": budget.peak_rss,
                  "transferred_body_bytes": budget.payload_bytes + sum(item["bytes"] for item in metadata),
                  "transferred_body_interpretation": "opaque copied bytes; embedded labels not interpreted",
                  "generated_metadata_bytes": 0,
                  "remaining_free_disk_bytes": shutil.disk_usage(output).free,
                  "sample_or_status_values_parsed": False, "targets_or_performance_outcomes_computed": False,
                  "all_original_channels_retained": True, "retries": 0, "resumed_files": 0}
        stage = "completion_publication"
        for _ in range(4):
            encoded_size = len((json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode())
            report["generated_metadata_bytes"] = budget.generated_metadata_bytes + encoded_size
        write_json(result_path, report, budget)
        return report
    except BaseException as error:
        failure = {"acquisition_id": "INNER-SPEECH-ACQ-1", "status": "failed", "stage": stage,
                   "failure_code": str(error) if isinstance(error, Refusal) else type(error).__name__,
                   "files_verified": len(files), "metadata_files_verified": len(metadata),
                   "copied_payload_bytes": budget.payload_bytes, "partial_files_preserved": True,
                   "retry_or_resume_allowed": False}
        # Failure reporting must remain possible after a wall/RSS budget refusal.
        require(len(json.dumps(failure).encode()) < FAILURE_METADATA_RESERVE // 2, "failure_metadata_size")
        write_json(output / "acquisition_failure.json", failure)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    manifest = load_manifest()
    if not args.execute:
        print(json.dumps({"mode": "dry_run", "dataset": "ds003626", "version": "2.1.2",
                          "files": list(PATHS), "payload_bytes": PAYLOAD_BYTES,
                          "required_output": str(OUTPUT), "network_requests": 0}, indent=2))
        return 0
    require(os.name == "nt" and args.output is not None, "explicit_windows_output_required")
    acquire(manifest, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
