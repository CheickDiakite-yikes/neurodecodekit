"""Generated in-memory ZIPs and mocked transport; no source access."""

from contextlib import contextmanager, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import struct
from types import SimpleNamespace
import unittest
from unittest import mock
import urllib.request
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/qualify_kunz_reference.py"
SPEC = importlib.util.spec_from_file_location("kunz_qualification_tested", SCRIPT)
qualification = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qualification)


def generated_zip(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, body in entries:
            archive.writestr(name, body)
    stream.seek(0)
    return stream


class MemoryRoot:
    def __init__(self):
        self.files = {}

    def __truediv__(self, name):
        @contextmanager
        def open_file(mode):
            if mode != "xb":
                raise AssertionError("Downloads must use exclusive creation")
            if name in self.files:
                raise FileExistsError(name)
            self.files[name] = b""
            stream = io.BytesIO()
            try:
                yield stream
            finally:
                self.files[name] = stream.getvalue()
                stream.close()
        return SimpleNamespace(open=open_file)


class FakeBudget:
    def __init__(self):
        self.payload_bytes = 0
        self.checks = 0

    def check(self):
        self.checks += 1

    def timeout(self):
        self.check()
        return 2.0

    def account(self, amount, *, payload):
        if not payload:
            raise AssertionError("Only transport bytes expected")
        self.payload_bytes += amount
        self.check()


class FakeResponse:
    def __init__(self, body, *, headers=None, status=200, close_at_eof=False):
        self.body = io.BytesIO(body)
        self.headers = {"Content-Length": str(len(body))} if headers is None else headers
        self.status = status
        self.requests, self.timeouts = [], []
        self.fp = SimpleNamespace(raw=SimpleNamespace(
            _sock=SimpleNamespace(settimeout=self.timeouts.append)))
        self.close_at_eof = close_at_eof

    def read1(self, count):
        self.requests.append(count)
        data = self.body.read(count)
        if self.close_at_eof and self.body.tell() == len(self.body.getbuffer()):
            self.fp = None  # urllib HTTPResponse closes fp at Content-Length EOF.
        return data

    def __enter__(self):
        return self

    def isclosed(self):
        return self.fp is None

    def __exit__(self, *args):
        self.body.close()


class QualificationTests(unittest.TestCase):
    def test_only_literal_readme_members_are_opened(self):
        archive = generated_zip([
            ("folder/README.md", b"Documentation only.\n"),
            ("data.mat", b"ARRAY_DO_NOT_OPEN"),
            ("events.csv", b"EVENTS_DO_NOT_OPEN"),
            ("labels.txt", b"TARGETS_DO_NOT_OPEN"),
            ("README.npy", b"ARRAY_DO_NOT_OPEN"),
        ])
        opened = []
        original = zipfile.ZipFile.open

        def checked_open(instance, member, *args, **kwargs):
            name = member.filename if isinstance(member, zipfile.ZipInfo) else member
            opened.append(name)
            self.assertEqual(name, "folder/README.md")
            return original(instance, member, *args, **kwargs)

        with mock.patch.object(zipfile.ZipFile, "open", new=checked_open):
            inventory, documents, remaining = qualification.inspect_zip(archive, 100)
        self.assertEqual(opened, ["folder/README.md"])
        self.assertEqual(len(inventory), 5)
        self.assertEqual(documents[0]["text"], "Documentation only.\n")
        self.assertEqual(documents[0]["sha256"], hashlib.sha256(b"Documentation only.\n").hexdigest())
        self.assertEqual(remaining, 80)

    def test_documentation_budget_is_shared_across_archives_before_open(self):
        _, _, remaining = qualification.inspect_zip(generated_zip([("README", b"1234")]), 6)
        self.assertEqual(remaining, 2)
        # Build before the spy, because ZIP construction itself opens members.
        second = generated_zip([("README.txt", b"123")])
        with mock.patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("No body read")):
            with self.assertRaisesRegex(ValueError, "documentation_budget"):
                qualification.inspect_zip(second, remaining)

    def test_directory_size_is_refused_before_zipfile_allocation(self):
        payload = bytearray(generated_zip([("data.mat", b"opaque")]).getvalue())
        struct.pack_into("<I", payload, len(payload) - 10, qualification.MIB + 1)
        stream = io.BytesIO(payload)
        with mock.patch.object(zipfile, "ZipFile", side_effect=AssertionError("No directory allocation")):
            with self.assertRaisesRegex(ValueError, "zip_directory_budget_or_geometry"):
                qualification.inspect_zip(stream, 100)
        self.assertFalse(stream.closed)

    def test_duplicate_unsafe_symlink_names_fail_closed(self):
        for name in ("../data.mat", "/data.mat", "C:/data.mat"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "unsafe_zip_name"):
                qualification.inspect_zip(generated_zip([(name, b"opaque")]), 100)
        # ZipInfo's constructor normalizes the Windows separator; exercise the guard directly.
        backslash = zipfile.ZipInfo("data.mat")
        backslash.filename = "folder\\data.mat"
        with self.assertRaisesRegex(ValueError, "unsafe_zip_name"):
            qualification.safe_member(backslash)
        duplicate = generated_zip([("data.mat", b"x"), ("DATA.MAT", b"y")])
        with self.assertRaisesRegex(ValueError, "duplicate_zip_name"):
            qualification.inspect_zip(duplicate, 100)
        symlink = zipfile.ZipInfo("link")
        symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaisesRegex(ValueError, "symlink_or_encrypted_member"):
            qualification.inspect_zip(generated_zip([(symlink, b"../outside")]), 100)

    def test_nontext_readme_is_refused(self):
        for body in (b"not\x00text", b"\xff\xfe\xff"):
            with self.subTest(body=body), self.assertRaises(ValueError):
                qualification.inspect_zip(generated_zip([("README", body)]), 100)

    def test_streamed_hash_and_normal_closed_fp_eof(self):
        body = b"x" * (qualification.MIB + 13)
        root, budget = MemoryRoot(), FakeBudget()
        response = FakeResponse(body, close_at_eof=True)
        opener = SimpleNamespace(open=mock.Mock(return_value=response))
        digest = hashlib.sha256(body).hexdigest()
        with mock.patch.object(qualification.urllib.request, "build_opener", return_value=opener):
            result = qualification.download((1, "generated.zip", len(body), digest), root, budget)
        self.assertEqual(root.files["generated.zip"], body)
        self.assertEqual(result["sha256"], digest)
        self.assertEqual(budget.payload_bytes, len(body))
        self.assertTrue(all(0 < count <= qualification.MIB for count in response.requests))
        self.assertEqual(opener.open.call_count, 1)
        with mock.patch.object(qualification.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(FileExistsError):
                qualification.download((1, "generated.zip", len(body), digest), root, budget)
        self.assertEqual(opener.open.call_count, 1)

    def test_transport_failures_keep_partial_without_retry(self):
        digest = hashlib.sha256(b"abc").hexdigest()
        cases = [
            (b"abc", {}, 503, digest, "download_status"),
            (b"abc", {"Content-Length": "4"}, 200, digest, "download_length"),
            (b"abc", {"Content-Encoding": "gzip"}, 200, digest, "download_encoding"),
            (b"ab", {}, 200, digest, "truncated_download"),
            (b"abcd", {}, 200, digest, "oversized_download"),
            (b"abc", {}, 200, "0" * 64, "download_hash"),
        ]
        for body, headers, status, pin, error in cases:
            with self.subTest(error=error):
                root, budget = MemoryRoot(), FakeBudget()
                response = FakeResponse(body, headers=headers, status=status)
                opener = SimpleNamespace(open=mock.Mock(return_value=response))
                with mock.patch.object(qualification.urllib.request, "build_opener", return_value=opener):
                    with self.assertRaisesRegex(ValueError, error):
                        qualification.download((1, "generated.zip", 3, pin), root, budget)
                self.assertIn("generated.zip", root.files)
                self.assertEqual(opener.open.call_count, 1)

    def test_unsafe_redirects_are_refused(self):
        request = urllib.request.Request("https://datadryad.org/downloads/file_stream/1")
        for target in ("http://example.test/archive.zip", "https://user:secret@example.test/a"):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "unsafe_download_redirect"):
                qualification.HttpsRedirect().redirect_request(request, None, 302, "", {}, target)

    def test_default_dry_run_has_no_source_or_runtime_access(self):
        output = io.StringIO()
        with mock.patch("sys.argv", [str(SCRIPT)]), redirect_stdout(output), \
                mock.patch.object(qualification, "load_helper", side_effect=AssertionError("No helper")), \
                mock.patch.object(qualification.urllib.request, "build_opener", side_effect=AssertionError("No network")):
            self.assertEqual(qualification.main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["archive_bytes"], 360112328)
        self.assertEqual(result["source_requests"], 0)
        self.assertEqual(result["scientific_array_members_opened"], 0)


if __name__ == "__main__":
    unittest.main()
