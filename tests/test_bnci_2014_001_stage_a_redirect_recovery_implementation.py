import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from email.message import Message
from pathlib import Path

from neurodecodekit.datasets.bnci_2014_001_acquisition import (
    BASE_URL,
    BNCIAcquisitionRefusal,
    PayloadMember,
    TransportResponse,
)
from neurodecodekit.datasets import (
    bnci_2014_001_stage_a_redirect_recovery as recovery,
)


ROOT = Path(__file__).resolve().parents[1]
STAGE_A_IMPLEMENTATION = (
    ROOT / "registries/bnci_2014_001_stage_a_implementation.v0.json"
)


class _Response:
    def __init__(
        self,
        payload: bytes,
        *,
        url: str = recovery.MANIFEST_URL,
        status: int = 200,
        content_length: int | None = None,
    ) -> None:
        self.payload = payload
        self.position = 0
        self.url = url
        self.status = status
        self.headers = Message()
        self.headers.add_header(
            "Content-Length",
            str(len(payload) if content_length is None else content_length),
        )
        self.closed = False

    def geturl(self):
        return self.url

    def getcode(self):
        return self.status

    def read(self, size=-1):
        if size < 0:
            size = len(self.payload) - self.position
        result = self.payload[self.position : self.position + size]
        self.position += len(result)
        return result

    def close(self):
        self.closed = True


def _fixture(members):
    return recovery._canonical_bytes(
        {
            "files": [
                {
                    "path": member.relative_path,
                    "bytes": member.bytes,
                    "sha256": member.sha256,
                    "url": recovery._signed_url(member),
                }
                for member in members
            ]
        }
    )


class BNCIStageARedirectRecoveryImplementationTests(unittest.TestCase):
    def setUp(self):
        payload = b"generated"
        self.member = PayloadMember(
            "sourcedata/A01E.mat",
            len(payload),
            hashlib.sha256(payload).hexdigest(),
        )

    def test_green_decision_and_plan_are_exact(self):
        decision = recovery.read_green_recovery_decision(ROOT)
        self.assertEqual(decision["maintainer_decision"]["message"], "continue, ")
        plan = recovery.registered_recovery_plan(ROOT)
        self.assertEqual(plan["payload_files"], 18)
        self.assertEqual(plan["payload_bytes"], 779_873_919)
        self.assertEqual(plan["decision_commit"], recovery.DECISION_COMMIT)

    def test_original_stage_a_artifacts_remain_byte_identical(self):
        registry = json.loads(STAGE_A_IMPLEMENTATION.read_text(encoding="utf-8"))
        for row in registry["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_manifest_client_is_direct_bounded_identity_get(self):
        payload = _fixture((self.member,))
        response = _Response(payload)
        calls = []

        def opener(request, timeout):
            calls.append((request, timeout))
            return response

        observed = recovery.StandardLibraryManifestClient(opener=opener).fetch()
        self.assertEqual(observed, payload)
        request, timeout = calls[0]
        headers = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(headers["accept-encoding"], "identity")
        self.assertEqual(timeout, recovery.REQUEST_TIMEOUT_SECONDS)
        self.assertTrue(response.closed)

    def test_manifest_client_refuses_redirect_short_body_and_oversize(self):
        payload = _fixture((self.member,))
        cases = (
            _Response(payload, url="https://example.invalid/manifest.json"),
            _Response(payload, content_length=len(payload) + 1),
            _Response(b"x", content_length=recovery.MANIFEST_BODY_CAP_BYTES + 1),
        )
        for response in cases:
            with self.subTest(response=response):
                client = recovery.StandardLibraryManifestClient(
                    opener=lambda _request, _timeout, item=response: item
                )
                with self.assertRaises(BNCIAcquisitionRefusal):
                    client.fetch()

    def test_resource_bound_transport_checks_each_payload_read(self):
        payload = b"payload"
        response = _Response(payload, url=recovery._signed_url(self.member))

        class Monitor:
            def __init__(self):
                self.checks = 0

            def check(self, *, required_free_bytes=0):
                self.assert_nonnegative = required_free_bytes >= 0
                self.checks += 1

            def request_timeout(self):
                return 7.0

        monitor = Monitor()
        transport = recovery.ResourceBoundRangeTransport(
            monitor,
            opener=lambda _request, timeout: response if timeout == 7.0 else None,
        )
        observed = transport(response.url, 0)
        self.assertEqual(b"".join(observed.body), payload)
        self.assertGreaterEqual(monitor.checks, 2)

    def test_manifest_validation_binds_identity_and_signed_query(self):
        urls = recovery.validate_manifest_signed_urls(
            _fixture((self.member,)),
            (self.member,),
        )
        self.assertEqual(list(urls), [self.member.relative_path])
        recovery.validate_signed_object_url(urls[self.member.relative_path], self.member)
        parsed = json.loads(_fixture((self.member,)))
        parsed["files"][0]["bytes"] += 1
        with self.assertRaises(BNCIAcquisitionRefusal):
            recovery.validate_manifest_signed_urls(
                recovery._canonical_bytes(parsed),
                (self.member,),
            )

    def test_manifest_validation_accepts_agreeing_duplicate_identity_fields(self):
        parsed = json.loads(_fixture((self.member,)))
        parsed["files"][0]["size"] = self.member.bytes
        parsed["files"][0]["checksum"] = f"sha256:{self.member.sha256}"
        observed = recovery.validate_manifest_signed_urls(
            recovery._canonical_bytes(parsed),
            (self.member,),
        )
        self.assertEqual(list(observed), [self.member.relative_path])

    def test_signed_url_refuses_invalid_port_and_disagreeing_identity_fields(self):
        malformed = recovery._signed_url(self.member).replace(
            recovery.SIGNED_OBJECT_HOST,
            f"{recovery.SIGNED_OBJECT_HOST}:not-a-port",
        )
        with self.assertRaises(BNCIAcquisitionRefusal):
            recovery.validate_signed_object_url(malformed, self.member)
        parsed = json.loads(_fixture((self.member,)))
        parsed["files"][0]["size"] = self.member.bytes + 1
        with self.assertRaises(BNCIAcquisitionRefusal):
            recovery.validate_manifest_signed_urls(
                recovery._canonical_bytes(parsed),
                (self.member,),
            )

    def test_manifest_validation_refuses_duplicate_and_ambiguous_url(self):
        parsed = json.loads(_fixture((self.member,)))
        parsed["files"].append(dict(parsed["files"][0]))
        with self.assertRaises(BNCIAcquisitionRefusal):
            recovery.validate_manifest_signed_urls(
                recovery._canonical_bytes(parsed),
                (self.member,),
            )
        parsed = json.loads(_fixture((self.member,)))
        parsed["files"][0]["signed_url"] = recovery._signed_url(self.member).replace(
            "1" * 64, "2" * 64
        )
        with self.assertRaises(BNCIAcquisitionRefusal):
            recovery.validate_manifest_signed_urls(
                recovery._canonical_bytes(parsed),
                (self.member,),
            )

    def test_manifest_validation_refuses_duplicate_json_keys_and_nonfinite_values(self):
        for payload in (
            b'{"files":[],"files":[]}',
            b'{"files":[],"not_finite":NaN}',
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(BNCIAcquisitionRefusal):
                    recovery.validate_manifest_signed_urls(payload, (self.member,))
    def test_adapter_exposes_only_registered_logical_member(self):
        signed = recovery._signed_url(self.member)
        calls = []

        def transport(url, offset):
            calls.append((url, offset))
            return TransportResponse(200, 1, None, (b"x",))

        adapter = recovery.SignedObjectTransportAdapter(
            {self.member.relative_path: signed},
            transport=transport,
        )
        adapter(BASE_URL + self.member.relative_path, 0)
        self.assertEqual(calls, [(signed, 0)])
        with self.assertRaises(BNCIAcquisitionRefusal):
            adapter(BASE_URL + "sourcedata/A02E.mat", 0)

    def test_registered_execution_refuses_foreign_root_before_ignored_access(self):
        with self.assertRaises(BNCIAcquisitionRefusal):
            recovery.execute_registered_recovery(
                "/tmp/foreign-bnci-root",
                environ={name: "1" for name in recovery.THREAD_ENVIRONMENT},
            )

    def test_safe_output_ancestry_refuses_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            (root / "linked").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(BNCIAcquisitionRefusal):
                recovery._assert_safe_directory_ancestry(
                    root,
                    root / "linked" / "child",
                    create=True,
                )

    def test_directory_descriptor_anchor_survives_path_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            direct = root / "direct"
            moved = root / "moved"
            outside = root / "outside"
            direct.mkdir()
            outside.mkdir()
            with recovery._anchored_directory(root, direct) as directory_fd:
                before_fd = os.open(
                    "before.txt",
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=directory_fd,
                )
                os.write(before_fd, b"anchored")
                os.close(before_fd)
                direct.rename(moved)
                direct.symlink_to(outside, target_is_directory=True)
                after_fd = os.open(
                    "after.txt",
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=directory_fd,
                )
                os.write(after_fd, b"still-anchored")
                os.close(after_fd)
            self.assertEqual((moved / "before.txt").read_bytes(), b"anchored")
            self.assertEqual((moved / "after.txt").read_bytes(), b"still-anchored")
            self.assertFalse((outside / "after.txt").exists())

    def test_live_gate_requires_post_green_implementation_activation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(BNCIAcquisitionRefusal):
                recovery.read_green_implementation_activation(tmp)

    def test_wall_clock_alarm_interrupts_blocking_operation(self):
        started = time.perf_counter()
        with self.assertRaises(BNCIAcquisitionRefusal):
            with recovery._runtime_alarm(0.02):
                time.sleep(0.1)
        self.assertLess(time.perf_counter() - started, 0.1)

    def test_sidecar_help_does_not_qualify_or_execute(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.bnci_c3c5_stage_a_redirect_recovery_cli",
                "--help",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("{plan,qualify,execute}", completed.stdout)
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
