"""One approved acquisition: opaque ZIPs and README-only inspection; dry-run first."""

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import struct
import threading
import time
import urllib.parse
import urllib.request
import zipfile


REPO = Path(__file__).resolve().parents[1]
BASE = Path(r"C:\Users\80714\AppData\Local\NeuroDecodeKit")
OUTPUT_NAME = "kunz_reference_qualification_20261002"
RESULT = REPO / "registries/kunz_reference_qualification.v0.json"
FILES = (
    (4203849, "seqRecallSpeech.zip", 79443728,
     "077f44c2ffcd27a75472a01a34a044004832233d88895d768ba08a3f5af48173"),
    (4203853, "seqRecallVerbalMemory.zip", 175492315,
     "f5aca99cb74a4883a2b515ffcf5fa350c7810b4ddabc2254f4865673189ec3ef"),
    (4203851, "seqRecallVisualMemory.zip", 105176285,
     "1d5a9fddd830aabb309fec847f4ce277e7ddb3f6e8cdd0253b19096cfb8901d7"),
)
DOC_LIMIT = 64 * 1024
MIB = 1024**2


def load_helper(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition, code):
    if not condition:
        raise ValueError(code)


def safe_member(info):
    path = PurePosixPath(info.filename)
    require(info.filename and len(info.filename) <= 512 and not path.is_absolute()
            and ".." not in path.parts and "\\" not in info.filename
            and ":" not in info.filename and "\x00" not in info.filename,
            "unsafe_zip_name")
    require(not stat.S_ISLNK(info.external_attr >> 16) and not info.flag_bits & 1,
            "symlink_or_encrypted_member")
    return path


def bounded_directory(path):
    """Bound central-directory allocation before ZipFile constructs members."""
    # Only ZIP metadata is decoded; compressed scientific members stay opaque.
    with (contextlib.nullcontext(path) if hasattr(path, "read") else Path(path).open("rb")) as stream:
        stream.seek(0, 2)
        length = stream.tell()
        stream.seek(max(0, length - 65557))
        tail = stream.read(65557)
    end = tail.rfind(b"PK\x05\x06")
    require(end >= 0 and end + 22 <= len(tail), "zip_end_record")
    _, disk, central_disk, here, total, size, offset, comment = struct.unpack(
        "<4s4H2IH", tail[end:end + 22])
    require(end + 22 + comment == len(tail), "zip_end_geometry")
    require(disk == central_disk == 0 and here == total and total <= 4096
            and size <= MIB and offset + size <= length - 22 - comment,
            "zip_directory_budget_or_geometry")


def inspect_zip(path, remaining_docs):
    """Read central directory plus literal README text only; never load arrays."""
    inventory, documents, names = [], [], set()
    bounded_directory(path)
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        require(len(infos) <= 4096, "zip_member_count")
        for info in infos:
            name = safe_member(info)
            require(info.filename.casefold() not in names, "duplicate_zip_name")
            names.add(info.filename.casefold())
            inventory.append({"name": info.filename, "bytes": info.file_size,
                              "compressed_bytes": info.compress_size})
            # No broad *.txt / *.csv selector: those may contain trial records.
            if name.name.casefold() not in {"readme", "readme.txt", "readme.md"}:
                continue
            require(not info.is_dir() and info.file_size <= remaining_docs,
                    "documentation_budget")
            with archive.open(info) as stream:
                data = stream.read(info.file_size + 1)
            require(len(data) == info.file_size, "documentation_size")
            text = data.decode("utf-8-sig")
            require("\x00" not in text, "documentation_not_text")
            remaining_docs -= len(data)
            documents.append({"member": info.filename, "bytes": len(data),
                              "sha256": hashlib.sha256(data).hexdigest(), "text": text})
    return inventory, documents, remaining_docs


class HttpsRedirect(urllib.request.HTTPRedirectHandler):
    max_redirections = 4

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        require(parsed.scheme == "https" and parsed.hostname and
                parsed.username is None and parsed.password is None,
                "unsafe_download_redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(item, root, budget):
    file_id, name, expected, digest = item
    require(re.fullmatch(r"[0-9a-f]{64}", digest), "sha256_pin")
    path = root / name
    hasher, copied = hashlib.sha256(), 0
    request = urllib.request.Request(
        f"https://datadryad.org/downloads/file_stream/{file_id}",
        headers={"User-Agent": "NeuroDecodeKit-source-qualification", "Accept-Encoding": "identity"})
    opener = urllib.request.build_opener(HttpsRedirect())
    # No retries, range requests, automatic resume, extraction or extra files.
    with path.open("xb") as output, opener.open(request, timeout=budget.timeout()) as response:
        require(response.status == 200, "download_status")
        length = response.headers.get("Content-Length")
        require(length is None or length == str(expected), "download_length")
        require(response.headers.get("Content-Encoding", "identity") == "identity",
                "download_encoding")
        while copied < expected:
            response.fp.raw._sock.settimeout(budget.timeout())
            chunk = response.read1(min(MIB, expected - copied))
            require(bool(chunk), "truncated_download")
            budget.account(len(chunk), payload=True)
            output.write(chunk)
            hasher.update(chunk)
            copied += len(chunk)
        if not response.isclosed():
            response.fp.raw._sock.settimeout(budget.timeout())
        extra = response.read1(1)
        budget.account(len(extra), payload=True)
        require(not extra, "oversized_download")
    require(copied == expected and hasher.hexdigest() == digest, "download_hash")
    budget.check()
    return {"archive": name, "file_id": file_id, "bytes": copied, "sha256": digest}


def execute():
    require(os.name == "nt", "windows_only")
    helper = load_helper("acquire_inner_speech")
    canonical = load_helper("acquire_inner_speech_session2")
    canonical.OUTPUT_NAME = OUTPUT_NAME
    root = canonical.canonical_output(BASE / OUTPUT_NAME, require)
    require(not root.exists() and not RESULT.exists(), "attempt_already_exists")
    require(shutil.disk_usage(root.parent).free >= 1024 * MIB, "one_gib_free_required")
    helper.WALL_SECONDS = 600
    helper.GIB = 256 * MIB  # The reused monitor's RSS ceiling, not a unit conversion.
    helper.PAYLOAD_LIMIT = 500 * MIB
    helper.METADATA_LIMIT = 2 * MIB
    helper.DISK_FLOOR = 512 * MIB
    budget = helper.Budget(root.parent)
    budget.check()
    root.mkdir(exist_ok=False)
    stage, files, documents_left = "start", [], DOC_LIMIT

    def deadline_stop():
        failure = {"status": "failed", "stage": stage, "failure": "wall_budget",
                   "transferred_body_bytes": budget.payload_bytes,
                   "retry_or_resume_allowed": False, "partial_evidence_preserved": True}
        try:
            helper.write_json(root / "execution_failed.json", failure)
        finally:
            # Applies only to this explicitly launched one-shot process.
            os._exit(99)

    deadline_timer = threading.Timer(max(0.001, budget.deadline - time.monotonic()), deadline_stop)
    deadline_timer.daemon = True
    deadline_timer.start()
    try:
        helper.write_json(root / "started.json", {
            "approval": "continue approved, lets please get closer to thought to text",
            "source_version_id": 379376, "started_unix": time.time(),
            "wall_seconds": 600, "retry_or_resume_allowed": False,
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}, budget)
        for item in FILES:
            stage = "opaque_download"
            record = download(item, root, budget)
            stage = "zip_directory_and_readme"
            inventory, documents, documents_left = inspect_zip(root / item[1], documents_left)
            budget.check()
            helper.write_json(root / (item[1] + ".inventory.json"), inventory, budget)
            helper.write_json(root / (item[1] + ".documentation.json"), documents, budget)
            record.update({"members": len(inventory), "documentation_files": len(documents),
                           "documentation_bytes": sum(d["bytes"] for d in documents),
                           "advertised_uncompressed_bytes": sum(d["bytes"] for d in inventory)})
            files.append(record)
            print(json.dumps({"verified_archives": len(files), "copied_bytes": budget.payload_bytes,
                              "documentation_bytes": DOC_LIMIT - documents_left}), flush=True)
        require(budget.payload_bytes == sum(f[2] for f in FILES), "exact_three_archives")
        budget.check()
        report = {"status": "acquired_documentation_only", "source_version_id": 379376,
                  "license": "CC0-1.0", "files": files,
                  "elapsed_seconds": time.monotonic() - budget.started,
                  "peak_rss_bytes": budget.peak_rss, "transferred_body_bytes": budget.payload_bytes,
                  "documentation_bytes": DOC_LIMIT - documents_left,
                  "scientific_array_members_opened": 0, "trial_labels_or_events_parsed": 0,
                  "training_or_scoring_operations": 0, "retries": 0,
                  "source_fit": "Requires review of documentation; acquisition is not qualification."}
        helper.write_json(root / "completed.json", report, budget)
        helper.write_json(RESULT, report, budget)
        return report
    except BaseException as error:
        failure = {"status": "failed", "stage": stage, "verified_archives": len(files),
                   "transferred_body_bytes": budget.payload_bytes,
                   "elapsed_seconds": time.monotonic() - budget.started,
                   "peak_rss_bytes": budget.peak_rss,
                   "failure": str(error) if type(error) in (ValueError, helper.Refusal) else type(error).__name__,
                   "retry_or_resume_allowed": False, "partial_evidence_preserved": True}
        helper.write_json(root / "execution_failed.json", failure)
        print(json.dumps(failure), flush=True)
        return failure
    finally:
        deadline_timer.cancel()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"mode": "dry_run", "archive_bytes": sum(f[2] for f in FILES),
                          "source_requests": 0, "wall_seconds": 600,
                          "documentation_limit_bytes": DOC_LIMIT,
                          "scientific_array_members_opened": 0}))
        return 0
    result = execute()
    return int(result["status"] == "failed")


if __name__ == "__main__":
    raise SystemExit(main())
