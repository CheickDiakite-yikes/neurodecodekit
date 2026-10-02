"""Generated manifests/headers and mocked transport; no source or private reads."""

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.test_inner_speech_acquisition import FakeBudget, FakeOpener, FakeResponse, generated_header


SPEC = importlib.util.spec_from_file_location("session2_acquisition_wrapper",
    Path(__file__).resolve().parents[1] / "scripts/acquire_inner_speech_session2.py")
wrapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wrapper)


def generated_manifest(runner):
    files = []
    base, remainder = divmod(runner.PAYLOAD_BYTES, 10)
    for index, path in enumerate(runner.PATHS):
        size = base + (index < remainder)
        digest = hashlib.md5(f"generated-{index}".encode()).hexdigest()
        key = f"MD5E-s{size}--{digest}.bdf"
        pointer = f"../../../.git/annex/objects/ab/cd/{key}/{key}"
        files.append({"path": path, "size_bytes": size, "md5": digest,
            "annex_pointer": pointer, "git_blob_sha1": runner.blob_sha1(pointer.encode()),
            "url": runner.S3 + path + "?versionId=generated-v1", "s3_version_id": "generated-v1"})
    metadata = [{"path": name, "size_bytes": len(body), "url": runner.RAW + name,
                 "git_blob_sha1": runner.blob_sha1(body)}
                for name, body in (("README", b"generated"), ("dataset_description.json", b"{}"))]
    return {"dataset": "ds003626", "version": "2.1.2", "source_commit": runner.COMMIT,
        "acquisition_id": "INNER-SPEECH-ACQ-S2", "license": "CC0", "raw_companions": [],
        "payload_bytes": runner.PAYLOAD_BYTES, "payload_limit_bytes": runner.PAYLOAD_LIMIT,
        "resource_limits": {"wall_seconds": 3600, "peak_rss_bytes": runner.GIB,
            "generated_metadata_bytes": runner.METADATA_LIMIT,
            "minimum_free_bytes": runner.DISK_FLOOR, "workers": 1},
        "files": files, "metadata_files": metadata}


@contextlib.contextmanager
def generated_run():
    with tempfile.TemporaryDirectory() as directory:
        parent = Path(directory).resolve()
        base = parent / "Local" / "NeuroDecodeKit"
        base.mkdir(parents=True)
        with mock.patch.object(wrapper, "BASE", base):
            runner = wrapper.configured_runner()
            runner.MANIFEST, runner.RESULT = parent / "manifest.json", parent / "result.json"
            manifest = generated_manifest(runner)
            runner.MANIFEST.write_text(json.dumps(manifest), encoding="utf-8")
            with mock.patch.object(runner.shutil, "disk_usage",
                                   return_value=SimpleNamespace(free=100 * runner.GIB)):
                yield runner, manifest, base


class Session2AcquisitionTests(unittest.TestCase):
    def test_fixed_configuration_and_manifest_refusals(self):
        runner = wrapper.configured_runner()
        self.assertEqual(runner.ACQUISITION_ID, "INNER-SPEECH-ACQ-S2")
        self.assertEqual(runner.PAYLOAD_BYTES, 6870116352)
        self.assertEqual(runner.PAYLOAD_LIMIT, 10 * 1024**3)
        self.assertEqual(runner.WALL_SECONDS, 3600)
        self.assertEqual(runner.OUTPUT.name, "ds003626_v2_1_2_ses02_20261002")
        self.assertTrue(all("/ses-02/" in path and "_ses-02_" in path for path in runner.PATHS))
        manifest = generated_manifest(runner)
        runner.validate_manifest(manifest)
        mutations = (
            lambda m: m.update(acquisition_id="INNER-SPEECH-ACQ-1"),
            lambda m: m.update(payload_bytes=6904627200),
            lambda m: m["files"][0].update(path=m["files"][0]["path"].replace("ses-02", "ses-01")),
            lambda m: m["files"].pop(),
            lambda m: m["files"][0].update(path="../../escape.bdf"),
            lambda m: m["files"][0].update(md5="0"*32),
            lambda m: m["files"][0].update(git_blob_sha1="0"*40),
            lambda m: m["files"][0].update(url=m["files"][0]["url"].split("?")[0], s3_version_id=None),
            lambda m: m["files"][0].update(s3_version_id="different"),
            lambda m: m["files"][0].update(url="https://generated.invalid/other"),
            lambda m: m["resource_limits"].update(workers=2),
            lambda m: m["resource_limits"].update(wall_seconds=3601),
        )
        for mutation in mutations:
            changed = copy.deepcopy(manifest)
            mutation(changed)
            with self.subTest(mutation=mutation), self.assertRaises(runner.Refusal):
                runner.validate_manifest(changed)

    def test_dry_run_opens_no_manifest_source_or_network(self):
        with mock.patch.object(Path, "open", side_effect=AssertionError("No file reads")), \
                mock.patch("urllib.request.build_opener", side_effect=AssertionError("No network")), \
                mock.patch.dict("sys.modules", {"psutil": None}), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(wrapper.main([]), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["manifest_or_source_files_opened"], 0)
        self.assertEqual(result["network_requests"], 0)
        self.assertEqual(result["acquisition_id"], "INNER-SPEECH-ACQ-S2")

    def test_canonical_path_allows_only_direct_or_exact_codex_package_alias(self):
        with generated_run() as (runner, _, base):
            output = base / wrapper.OUTPUT_NAME
            self.assertEqual(wrapper.canonical_output(output, runner.require), output)
            target = base.parent / "Packages" / "OpenAI.Codex_123456789abcd" / "LocalCache" / "Local" / base.name
            target.mkdir(parents=True)
            original_resolve = Path.resolve

            def alias(path, *args, **kwargs):
                if path in (base, output):
                    return target / path.relative_to(base)
                return original_resolve(path, *args, **kwargs)

            with mock.patch.object(Path, "resolve", autospec=True, side_effect=alias):
                self.assertEqual(wrapper.canonical_output(output, runner.require), target / output.name)
                self.assertEqual(wrapper.canonical_output(target / output.name, runner.require), target / output.name)
            for name in ("ds003626_v2_1_2_ses01_20260922", "different", ".."):
                with self.subTest(name=name), self.assertRaises(runner.Refusal):
                    wrapper.canonical_output(base / name, runner.require)
            for bad in (base.parent / "OneDrive" / base.name,
                        base.parent / "Packages" / "OtherApp_123456789abcd" / "LocalCache" / "Local" / base.name,
                        base.parent.parent / "escape"):
                def redirect(path, *args, **kwargs):
                    return bad if path == base else original_resolve(path, *args, **kwargs)
                with mock.patch.object(Path, "resolve", autospec=True, side_effect=redirect), \
                        self.assertRaises(runner.Refusal):
                    wrapper.canonical_output(output, runner.require)
            def child_redirect(path, *args, **kwargs):
                return base.parent / "escape" if path == output else original_resolve(path, *args, **kwargs)
            with mock.patch.object(Path, "resolve", autospec=True, side_effect=child_redirect), \
                    self.assertRaisesRegex(runner.Refusal, "local_output_containment"):
                wrapper.canonical_output(output, runner.require)

    def test_complete_all_ten_preserves_ids_provenance_old_root_and_single_use(self):
        with generated_run() as (runner, manifest, base):
            old = base / "ds003626_v2_1_2_ses01_20260922"
            old.mkdir()
            sentinel = old / "generated_predecessor.txt"
            sentinel.write_text("preserve", encoding="utf-8")
            old_bytes = sentinel.read_bytes()
            calls = []

            def copied(item, destination, budget, *, metadata=False, opener=None):
                calls.append((item["path"], metadata))
                budget.account(item["size_bytes"], payload=not metadata)
                return {"path": item["path"], "bytes": item["size_bytes"], "sha256": "a"*64}

            with mock.patch.object(runner, "download", side_effect=copied), \
                    contextlib.redirect_stdout(io.StringIO()):
                result = runner.acquire(runner.load_manifest(), runner.OUTPUT, budget=FakeBudget(), opener=object())
                self.assertEqual(len(calls), 12)
                self.assertEqual(result["files_verified"], 10)
                self.assertEqual(result["payload_bytes"], 6870116352)
                self.assertEqual(result["acquisition_id"], "INNER-SPEECH-ACQ-S2")
                started = json.loads((runner.OUTPUT / "acquisition_started.json").read_text())
                self.assertEqual(started["acquisition_id"], result["acquisition_id"])
                self.assertEqual(started["wall_limit_seconds"], 3600)
                self.assertEqual(started["acquisition_wrapper_sha256"],
                                 hashlib.sha256(Path(wrapper.__file__).read_bytes()).hexdigest())
                self.assertEqual(started["manifest_sha256"], hashlib.sha256(runner.MANIFEST.read_bytes()).hexdigest())
                self.assertEqual(json.loads(runner.RESULT.read_text()), result)
                self.assertFalse(result["sample_or_status_values_parsed"])
                self.assertFalse(result["targets_or_performance_outcomes_computed"])
                self.assertEqual(sentinel.read_bytes(), old_bytes)
                with self.assertRaisesRegex(runner.Refusal, "existing_run_or_result"):
                    runner.acquire(manifest, runner.OUTPUT, budget=FakeBudget(), opener=object())
                self.assertEqual(len(calls), 12)

    def test_failure_preserves_partial_and_refuses_retry_or_alternate_result(self):
        with generated_run() as (runner, manifest, _):
            opener = FakeOpener(error=runner.Refusal("redirect_refused"))
            with self.assertRaisesRegex(runner.Refusal, "fixed_result_path_required"):
                runner.acquire(manifest, runner.OUTPUT, result_path=runner.RESULT.with_name("other.json"),
                               budget=FakeBudget(), opener=opener)
            self.assertEqual(opener.calls, 0)
            with self.assertRaisesRegex(runner.Refusal, "redirect_refused"):
                runner.acquire(manifest, runner.OUTPUT, budget=FakeBudget(), opener=opener)
            failure = json.loads((runner.OUTPUT / "acquisition_failure.json").read_text())
            self.assertEqual(failure["acquisition_id"], "INNER-SPEECH-ACQ-S2")
            self.assertTrue(failure["partial_files_preserved"])
            self.assertFalse(failure["retry_or_resume_allowed"])
            self.assertTrue((runner.OUTPUT / "README.partial").exists())
            self.assertFalse(runner.RESULT.exists())
            with self.assertRaisesRegex(runner.Refusal, "existing_run_or_result"):
                runner.acquire(manifest, runner.OUTPUT, budget=FakeBudget(), opener=opener)
            self.assertEqual(opener.calls, 1)

    def test_reused_transport_hash_header_and_session2_user_agent(self):
        runner = wrapper.configured_runner()
        header, size = generated_header()
        body = header + b"\0" * (size - len(header))
        item = {"path": "generated.bdf", "url": "https://generated.invalid/status-not-read",
                "size_bytes": size, "md5": hashlib.md5(body).hexdigest(), "s3_version_id": "generated"}
        response = FakeResponse(body, item["url"], version="generated")
        opener = FakeOpener(response)
        request_headers = []
        original_open = opener.open

        def record_request(request, *, timeout):
            request_headers.append(dict(request.header_items()))
            return original_open(request, timeout=timeout)

        opener.open = record_request
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "generated.bdf"
            result = runner.download(item, destination, FakeBudget(), opener=opener)
            self.assertEqual(result["md5"], item["md5"])
            self.assertEqual(result["sha256"], hashlib.sha256(body).hexdigest())
            self.assertEqual(result["header"]["required_eeg_channels"], 128)
            self.assertEqual(result["header"]["required_exg_channels"], 8)
            self.assertEqual(result["header"]["sampling_hz_all_channels"], 1024)
            self.assertFalse(result["header"]["sample_or_status_values_parsed"])
            self.assertNotIn("SECRET", json.dumps(result))
            self.assertEqual(request_headers[0]["User-agent"], "NeuroDecodeKit-INNER-SPEECH-ACQ-S2")


if __name__ == "__main__":
    unittest.main()
