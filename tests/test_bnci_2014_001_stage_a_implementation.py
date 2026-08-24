import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from email.message import Message
from pathlib import Path

from neurodecodekit.datasets.bnci_2014_001_acquisition import BNCIAcquisitionRefusal
from neurodecodekit.datasets import bnci_2014_001_stage_a as stage_a


ROOT = Path(__file__).resolve().parents[1]
G1_IMPLEMENTATION = (
    ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_implementation.v0.json"
)


class _Response:
    def __init__(
        self,
        payload: bytes,
        *,
        url: str = "https://example.invalid/member.mat",
        status: int = 200,
        content_range: str | None = None,
    ) -> None:
        self.payload = payload
        self.position = 0
        self.url = url
        self.status = status
        self.headers = Message()
        self.headers.add_header("Content-Length", str(len(payload)))
        if content_range is not None:
            self.headers.add_header("Content-Range", content_range)
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


class BNCIStageAImplementationTests(unittest.TestCase):
    def test_green_g1_proof_and_plan_are_exact(self):
        proof = stage_a.read_green_g1_proof(ROOT)
        self.assertEqual(proof["closed_result"]["case_classes_passed"], 11)
        plan = stage_a.registered_stage_a_plan(ROOT)
        self.assertEqual(plan["payload_files"], 18)
        self.assertEqual(plan["payload_bytes"], 779_873_919)
        self.assertEqual(plan["proof_commit"], stage_a.G1_PROOF_COMMIT)

    def test_original_g1_artifacts_remain_byte_identical(self):
        registry = json.loads(G1_IMPLEMENTATION.read_text(encoding="utf-8"))
        for row in registry["artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_transport_uses_identity_get_and_exact_range(self):
        calls = []
        response = _Response(
            b"payload",
            status=206,
            content_range="bytes 5-11/12",
        )

        def opener(request, timeout):
            calls.append((request, timeout))
            return response

        transport = stage_a.StandardLibraryRangeTransport(opener=opener)
        result = transport(response.url, 5)
        self.assertEqual(result.status, 206)
        self.assertEqual(result.range_start, 5)
        self.assertEqual(b"".join(result.body), b"payload")
        request, timeout = calls[0]
        headers = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(headers["range"], "bytes=5-")
        self.assertEqual(headers["accept-encoding"], "identity")
        self.assertEqual(timeout, stage_a.REQUEST_TIMEOUT_SECONDS)
        self.assertTrue(response.closed)

    def test_transport_refuses_redirect_and_short_body(self):
        redirected = _Response(b"x", url="https://example.invalid/other.mat")
        transport = stage_a.StandardLibraryRangeTransport(
            opener=lambda _request, _timeout: redirected
        )
        with self.assertRaises(BNCIAcquisitionRefusal):
            transport("https://example.invalid/member.mat", 0)
        short = _Response(b"x")
        short.headers.replace_header("Content-Length", "2")
        transport = stage_a.StandardLibraryRangeTransport(opener=lambda _r, _t: short)
        with self.assertRaises(ConnectionError):
            b"".join(transport(short.url, 0).body)

    def test_registered_execution_refuses_foreign_root_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(BNCIAcquisitionRefusal):
                stage_a.execute_registered_acquisition(
                    tmp,
                    environ={name: "1" for name in stage_a.THREAD_ENVIRONMENT},
                )

    def test_sidecar_help_does_not_execute(self):
        completed = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.bnci_c3c5_stage_a_cli", "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("{plan,execute}", completed.stdout)
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
