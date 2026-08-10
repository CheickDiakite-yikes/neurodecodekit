import copy
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from neurodecodekit.cli import main
from neurodecodekit.datasets import physionet_motor_acquisition as acquisition
from neurodecodekit.datasets.physionet_motor_acquisition import (
    AUTHORIZATION_COMMIT,
    CONTRACT_SHA256,
    DECISION_SHA256,
    EXPECTED_DATASET_ID,
    EXPECTED_DOI,
    EXPECTED_LICENSE_ID,
    EXPECTED_LICENSE_LABEL,
    EXPECTED_PATHS,
    EXPECTED_VERSION,
    AcquisitionFailure,
    AcquisitionRefusal,
    ExecutionEvidence,
    MetadataEvidence,
    _fetch_registered_metadata,
    _parse_checksum_manifest,
    _render_receipts,
    _validate_task_mapping_document,
    _verify_execution_evidence,
    run_acquisition,
)


THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}
EVIDENCE = ExecutionEvidence(
    implementation_commit="b" * 40,
    implementation_ci_run_id=201,
    base_python_job_id=202,
    optional_neuro_job_id=203,
)


def synthetic_fixture():
    payloads = {
        path: bytes([0xFF, index, 0x00, 0x80]) * (index + 1)
        for index, path in enumerate(EXPECTED_PATHS)
    }
    source = {
        "provider": "PhysioNet",
        "dataset_id": EXPECTED_DATASET_ID,
        "dataset_name": "EEG Motor Movement/Imagery Dataset",
        "version": EXPECTED_VERSION,
        "doi": EXPECTED_DOI,
        "dataset_url": "https://physionet.org/content/eegmmidb/1.0.0/",
        "file_root_url": "https://physionet.org/files/eegmmidb/1.0.0/",
        "official_checksum_manifest_url": (
            "https://physionet.org/files/eegmmidb/1.0.0/SHA256SUMS.txt"
        ),
        "task_mapping_source_url": (
            "https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html"
        ),
        "license_id": EXPECTED_LICENSE_ID,
        "license_label": EXPECTED_LICENSE_LABEL,
    }
    selected = []
    for path, payload in payloads.items():
        subject = path.split("/", 1)[0]
        run = path.removesuffix(".edf").rsplit("R", 1)[1]
        selected.append(
            {
                "repository_relative_path": path,
                "download_url": source["file_root_url"] + path,
                "destination_relative_path": path,
                "subject_id": subject,
                "run_id": run,
                "prospective_future_role": "fixture_only",
                "size_bytes": len(payload),
                "official_sha256": hashlib.sha256(payload).hexdigest(),
                "content_parse_allowed": False,
            }
        )
    total = sum(len(payload) for payload in payloads.values())
    contract = {
        "source_dataset": source,
        "prospective_cohort": {
            "subjects": ["S001", "S002", "S003"],
            "runs": ["03", "07", "11"],
        },
        "selected_files": selected,
        "storage_and_output": {
            "payload_root": "data/physionet_motor/eegmmidb-1.0.0",
            "temporary_root": ".codex_work/physionet_motor_acquisition/tmp",
            "receipt_root": ".codex_work/physionet_motor_acquisition/receipt",
            "expected_final_payload_bytes": total,
            "maximum_metadata_network_bytes": 1024 * 1024,
            "maximum_edf_payload_network_bytes": total + 1024,
            "maximum_incremental_disk_bytes_including_temporary_files": 4 * 1024 * 1024,
            "minimum_free_disk_bytes_before_execution": 1,
            "maximum_generated_receipt_bytes_combined": 1024 * 1024,
        },
        "resource_caps": {
            "cpu_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "wall_time_seconds": 300,
            "peak_rss_bytes": 256 * 1024 * 1024,
        },
        "receipt_contract": {
            "machine_manifest": "physionet_motor_acquisition_manifest.v0.json",
            "human_receipt": "physionet_motor_acquisition_receipt.md",
        },
    }
    return contract, payloads


class FakeTransport:
    def __init__(self, contract, payloads):
        self.contract = contract
        self.payloads = dict(payloads)
        self.payload_calls = []
        self.metadata_calls = 0
        self.metadata_evidence = MetadataEvidence(
            dataset_version=EXPECTED_VERSION,
            doi=EXPECTED_DOI,
            license_label=EXPECTED_LICENSE_LABEL,
            public_available=True,
            task_mapping_confirmed=True,
            source_surfaces=(
                contract["source_dataset"]["dataset_url"],
                contract["source_dataset"]["official_checksum_manifest_url"],
                contract["source_dataset"]["task_mapping_source_url"],
            ),
            file_records=tuple(
                {
                    "path": row["repository_relative_path"],
                    "size_bytes": row["size_bytes"],
                    "official_sha256": row["official_sha256"],
                    "content_type": "application/octet-stream",
                    "etag": "fixture",
                    "last_modified": "fixture",
                }
                for row in contract["selected_files"]
            ),
            request_count=12,
            network_bytes=503,
        )

    def fetch_metadata(self, source, selected_files, maximum_network_bytes):
        self.metadata_calls += 1
        if source != self.contract["source_dataset"]:
            raise AssertionError("runner changed the source metadata identity")
        if list(selected_files) != self.contract["selected_files"]:
            raise AssertionError("runner changed registered file order")
        if maximum_network_bytes != self.contract["storage_and_output"][
            "maximum_metadata_network_bytes"
        ]:
            raise AssertionError("runner changed metadata cap")
        return self.metadata_evidence

    def open_payload(self, url, expected_size):
        root = self.contract["source_dataset"]["file_root_url"]
        if not url.startswith(root):
            raise AssertionError("runner changed registered payload host")
        path = url.removeprefix(root)
        self.payload_calls.append(path)
        payload = self.payloads[path]
        if len(payload) != expected_size:
            raise AssertionError("fake expected-size binding drifted")
        return io.BytesIO(payload)


class FakeResponse(io.BytesIO):
    def __init__(self, payload, url, *, status=200, headers=None):
        super().__init__(payload)
        self.status = status
        self.headers = headers or {}
        self._url = url

    def geturl(self):
        return self._url

    def getcode(self):
        return self.status


class PhysioNetMotorAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.contract, self.payloads = synthetic_fixture()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def run_fixture(self, transport=None, contract=None, environ=None, **kwargs):
        selected_contract = contract or self.contract
        transport = transport or FakeTransport(selected_contract, self.payloads)
        outcome = run_acquisition(
            contract=selected_contract,
            evidence=EVIDENCE,
            workspace_root=self.root,
            metadata_fetcher=transport.fetch_metadata,
            payload_opener=transport.open_payload,
            environ=environ or THREAD_ENV,
            clock=kwargs.pop("clock", lambda: 100.0),
            utc_now=lambda: "2026-08-09T12:00:00Z",
            rss_reader=kwargs.pop("rss_reader", lambda: 16 * 1024 * 1024),
        )
        return outcome, transport

    def test_tiny_nine_file_roundtrip_passes_without_decoding_invalid_utf8(self):
        outcome, transport = self.run_fixture()
        self.assertTrue(outcome.passed)
        self.assertEqual(transport.payload_calls, list(EXPECTED_PATHS))
        final_root = self.root / "data/physionet_motor/eegmmidb-1.0.0"
        for path, payload in self.payloads.items():
            self.assertEqual((final_root / path).read_bytes(), payload)
        self.assertFalse((self.root / ".codex_work/physionet_motor_acquisition/tmp").exists())
        self.assertTrue(outcome.manifest_path.is_file())
        self.assertTrue(outcome.receipt_path.is_file())

    def test_manifest_preserves_metrics_hash_counts_warnings_and_claim_ceiling(self):
        outcome, _ = self.run_fixture()
        manifest = json.loads(outcome.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["file_paths_sizes_official_and_observed_sha256"]), 9)
        self.assertTrue(
            all(
                row["official_sha256"] == row["observed_local_sha256"]
                for row in manifest["file_paths_sizes_official_and_observed_sha256"]
            )
        )
        self.assertEqual(set(manifest["opaque_local_hash_pass_count_by_edf"].values()), {1})
        counters = manifest["access_and_operation_counters"]
        self.assertEqual(counters["metadata_request_count"], 12)
        self.assertEqual(counters["edf_payload_request_count"], 9)
        self.assertEqual(counters["opaque_local_hash_pass_count"], 9)
        for key in (
            "edf_header_reads",
            "edf_annotation_or_event_reads",
            "event_sidecar_requests_or_reads",
            "signal_sample_reads",
            "task_target_label_epoch_trial_reads",
            "split_operations",
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "scoring_or_selection_runs",
            "work_order_9_operations",
            "reruns",
        ):
            self.assertEqual(counters[key], 0, key)
        self.assertEqual(set(manifest["unavailable_fields"]), set(acquisition.REQUIRED_UNAVAILABLE_FIELDS))
        self.assertTrue(all(manifest["acceptance_gate_results"].values()))
        self.assertIn("establishes no EDF readability", manifest["claim_boundary"]["scientific_claim_not_established"])
        generated = outcome.manifest_path.stat().st_size + outcome.receipt_path.stat().st_size
        self.assertEqual(manifest["measurements"]["generated_receipt_bytes"], generated)
        self.assertLessEqual(generated, 1024 * 1024)
        human = outcome.receipt_path.read_text(encoding="utf-8")
        self.assertIn("## Unavailable Fields", human)
        for field in acquisition.REQUIRED_UNAVAILABLE_FIELDS:
            self.assertIn(f"`{field}`", human)

    def test_metadata_identity_drift_parks_before_any_payload_request(self):
        transport = FakeTransport(self.contract, self.payloads)
        transport.metadata_evidence = MetadataEvidence(
            **{**transport.metadata_evidence.__dict__, "doi": "drifted"}
        )
        outcome, _ = self.run_fixture(transport)
        self.assertEqual(outcome.status, "parked")
        self.assertEqual(outcome.manifest["failure_stage"], "metadata")
        self.assertEqual(transport.payload_calls, [])
        self.assertEqual(
            outcome.manifest["access_and_operation_counters"]["edf_payload_download_invocations"],
            0,
        )
        self.assertFalse((self.root / "data/physionet_motor").exists())

    def test_metadata_duplicate_or_cap_breach_parks_before_payload(self):
        transport = FakeTransport(self.contract, self.payloads)
        records = list(transport.metadata_evidence.file_records)
        records[1] = records[0]
        transport.metadata_evidence = MetadataEvidence(
            **{**transport.metadata_evidence.__dict__, "file_records": tuple(records)}
        )
        outcome, _ = self.run_fixture(transport)
        self.assertEqual(outcome.manifest["failure_stage"], "metadata")
        self.assertEqual(transport.payload_calls, [])

        self.tearDown()
        self.setUp()
        transport = FakeTransport(self.contract, self.payloads)
        transport.metadata_evidence = MetadataEvidence(
            **{
                **transport.metadata_evidence.__dict__,
                "network_bytes": 1024 * 1024 + 1,
            }
        )
        outcome, _ = self.run_fixture(transport)
        self.assertEqual(outcome.manifest["failure_stage"], "resource")
        self.assertEqual(transport.payload_calls, [])

    def test_hash_mismatch_cleans_temp_and_never_promotes_partial_bundle(self):
        changed = dict(self.payloads)
        changed[EXPECTED_PATHS[4]] = b"\x00" * len(changed[EXPECTED_PATHS[4]])
        transport = FakeTransport(self.contract, changed)
        outcome, _ = self.run_fixture(transport)
        self.assertEqual(outcome.status, "parked")
        self.assertEqual(outcome.manifest["failure_stage"], "integrity")
        self.assertFalse((self.root / "data/physionet_motor").exists())
        self.assertFalse((self.root / ".codex_work/physionet_motor_acquisition/tmp").exists())
        self.assertTrue(outcome.manifest_path.exists())

    def test_short_transfer_and_nonbyte_stream_park_without_promotion(self):
        transport = FakeTransport(self.contract, self.payloads)
        first_path = EXPECTED_PATHS[0]
        original_open = transport.open_payload

        def short_open(url, expected_size):
            if url.endswith(first_path):
                transport.payload_calls.append(first_path)
                return io.BytesIO(self.payloads[first_path][:-1])
            return original_open(url, expected_size)

        transport.open_payload = short_open
        outcome, _ = self.run_fixture(transport)
        self.assertEqual(outcome.manifest["failure_stage"], "transfer")
        self.assertFalse((self.root / "data/physionet_motor").exists())

    def test_payload_and_receipt_caps_are_strict(self):
        contract = copy.deepcopy(self.contract)
        contract["storage_and_output"]["maximum_edf_payload_network_bytes"] = 8
        outcome, _ = self.run_fixture(contract=contract)
        self.assertEqual(outcome.manifest["failure_stage"], "resource")
        self.assertIn("payload network cap", outcome.manifest["failure_reason"])

        manifest = {
            "status": "parked",
            "source_dataset": {
                "dataset_id": EXPECTED_DATASET_ID,
                "version": EXPECTED_VERSION,
                "doi": EXPECTED_DOI,
                "license_id": EXPECTED_LICENSE_ID,
            },
            "failure_stage": "test",
            "measurements": {
                "final_file_count": 0,
                "final_payload_bytes": 0,
                "metadata_network_bytes": 0,
                "edf_payload_network_bytes": 0,
                "runtime_seconds": 0,
                "peak_rss_bytes": 1,
                "incremental_disk_peak_bytes": 0,
                "generated_receipt_bytes": 0,
            },
            "file_paths_sizes_official_and_observed_sha256": [],
            "warnings": ["bounded"],
            "unavailable_fields": {"field": "unavailable"},
            "acceptance_gate_results": {"bounded": False},
            "claim_boundary": {
                "engineering_result": "parked",
                "scientific_claim_not_established": "none established",
            },
        }
        with self.assertRaisesRegex(AcquisitionFailure, "output cap"):
            _render_receipts(manifest, 64)

    def test_preexisting_and_symlink_paths_are_refused_without_network_or_mutation(self):
        marker_root = self.root / "data/physionet_motor"
        marker_root.mkdir()
        marker = marker_root / "user-owned.txt"
        marker.write_text("keep", encoding="utf-8")
        transport = FakeTransport(self.contract, self.payloads)
        with self.assertRaisesRegex(AcquisitionRefusal, "must not already exist"):
            self.run_fixture(transport)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
        self.assertEqual(transport.metadata_calls, 0)

        self.tearDown()
        self.setUp()
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / ".codex_work").symlink_to(outside, target_is_directory=True)
        transport = FakeTransport(self.contract, self.payloads)
        with self.assertRaisesRegex(AcquisitionRefusal, "symlink"):
            self.run_fixture(transport)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual(transport.metadata_calls, 0)

    def test_one_thread_low_disk_and_initial_rss_preflights_are_mandatory(self):
        environ = dict(THREAD_ENV)
        environ["OPENBLAS_NUM_THREADS"] = "4"
        transport = FakeTransport(self.contract, self.payloads)
        with self.assertRaisesRegex(AcquisitionRefusal, "one-thread"):
            self.run_fixture(transport, environ=environ)
        self.assertEqual(transport.metadata_calls, 0)

        with patch.object(acquisition.shutil, "disk_usage", return_value=SimpleNamespace(free=0)):
            with self.assertRaisesRegex(AcquisitionRefusal, "free disk"):
                self.run_fixture()
        with self.assertRaisesRegex(AcquisitionRefusal, "RSS already"):
            self.run_fixture(rss_reader=lambda: 300 * 1024 * 1024)

    def test_runtime_cap_parks_before_payload(self):
        ticks = iter([0.0, 301.0, 301.0, 301.0])
        transport = FakeTransport(self.contract, self.payloads)
        outcome, _ = self.run_fixture(transport, clock=lambda: next(ticks))
        self.assertEqual(outcome.manifest["failure_stage"], "resource")
        self.assertEqual(transport.payload_calls, [])

    def test_second_invocation_is_refused_by_existing_roots(self):
        first, _ = self.run_fixture()
        self.assertTrue(first.passed)
        second_transport = FakeTransport(self.contract, self.payloads)
        with self.assertRaises(AcquisitionRefusal):
            self.run_fixture(second_transport)
        self.assertEqual(second_transport.metadata_calls, 0)

    def test_contract_refuses_event_sidecars_substitutions_and_url_drift(self):
        for mutation in ("path", "url"):
            contract = copy.deepcopy(self.contract)
            if mutation == "path":
                contract["selected_files"][0]["repository_relative_path"] = (
                    "S001/S001R03.edf.event"
                )
            else:
                contract["selected_files"][0]["download_url"] = (
                    "https://example.com/S001R03.edf"
                )
            transport = FakeTransport(contract, self.payloads)
            with self.assertRaises(AcquisitionRefusal):
                self.run_fixture(transport, contract=contract)
            self.assertEqual(transport.metadata_calls, 0)

    def test_hash_helper_is_called_exactly_once_per_edf(self):
        with patch.object(
            acquisition,
            "_opaque_hash_file",
            wraps=acquisition._opaque_hash_file,
        ) as opaque_hash:
            outcome, _ = self.run_fixture()
        self.assertTrue(outcome.passed)
        self.assertEqual(opaque_hash.call_count, 9)

    def test_extra_staging_membership_parks_without_promotion(self):
        with patch.object(
            acquisition,
            "_enumerate_regular_files",
            side_effect=AcquisitionFailure("integrity", "synthetic extra file"),
        ):
            outcome, _ = self.run_fixture()
        self.assertEqual(outcome.manifest["failure_stage"], "integrity")
        self.assertFalse((self.root / "data/physionet_motor").exists())

    def test_registered_hash_and_authorization_bindings_are_fixed(self):
        self.assertEqual(
            CONTRACT_SHA256,
            "6c81dac6a818f13c49f5df25c540e9d3ef65f21b56ecb1a5b5d15d4a3dc819d3",
        )
        self.assertEqual(
            DECISION_SHA256,
            "5f232f174c67fae2f70f2cc26a779a82caee9176dc406ceccb182ad77d1bc304",
        )
        self.assertEqual(AUTHORIZATION_COMMIT, "00b91edd213112fd186711d06369ae4f836b2243")

    def test_execution_evidence_requires_current_clean_descendant_head(self):
        responses = [
            SimpleNamespace(returncode=0, stdout=f"{'b' * 40}\n"),
            SimpleNamespace(returncode=0, stdout=""),
            SimpleNamespace(returncode=0, stdout=""),
        ]
        with patch.object(acquisition.subprocess, "run", side_effect=responses) as run:
            _verify_execution_evidence(self.root, EVIDENCE)
        self.assertEqual(run.call_count, 3)

    def test_execution_evidence_refuses_head_mismatch_or_tracked_changes(self):
        with patch.object(
            acquisition.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=0, stdout=f"{'c' * 40}\n"),
        ):
            with self.assertRaisesRegex(AcquisitionRefusal, "current HEAD"):
                _verify_execution_evidence(self.root, EVIDENCE)
        responses = [
            SimpleNamespace(returncode=0, stdout=f"{'b' * 40}\n"),
            SimpleNamespace(returncode=0, stdout=" M tracked.py\n"),
        ]
        with patch.object(acquisition.subprocess, "run", side_effect=responses):
            with self.assertRaisesRegex(AcquisitionRefusal, "tracked worktree"):
                _verify_execution_evidence(self.root, EVIDENCE)

    def test_standard_library_executor_exposes_no_edf_reader_or_heavy_dependency(self):
        source_path = (
            Path(__file__).resolve().parents[1]
            / "src/neurodecodekit/datasets/physionet_motor_acquisition.py"
        )
        source = source_path.read_text(encoding="utf-8")
        for forbidden in (
            "import mne",
            "import numpy",
            "import scipy",
            "import torch",
            "read_raw_edf",
            "pyedflib",
        ):
            self.assertNotIn(forbidden, source)

    def test_cli_defaults_to_no_stat_no_network_plan(self):
        stdout = io.StringIO()
        with (
            patch.object(
                acquisition,
                "_lstat_optional",
                side_effect=AssertionError("dry-run must not stat registered paths"),
            ),
            patch.object(
                acquisition,
                "_open_request_once",
                side_effect=AssertionError("dry-run must not network"),
            ),
            redirect_stdout(stdout),
        ):
            code = main(["physionet-motor-acquire"])
        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn('"mode": "dry_run_no_registered_path_stat_no_network"', output)
        self.assertIn('"expected_payload_bytes": 23248224', output)
        self.assertIn("No registered path stat or network access occurred", output)

    def test_cli_execute_requires_all_remote_green_implementation_evidence(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["physionet-motor-acquire", "--execute"])
        self.assertEqual(code, 2)
        output = stderr.getvalue()
        self.assertIn("--implementation-commit", output)
        self.assertIn("--implementation-ci-run-id", output)
        self.assertIn("--base-python-job-id", output)
        self.assertIn("--optional-neuro-job-id", output)

    def test_checksum_and_task_mapping_parsers_are_strict(self):
        checksums = _parse_checksum_manifest(
            f"{'a' * 64}  ./S001/S001R03.edf\n".encode("ascii")
        )
        self.assertEqual(checksums, {"S001/S001R03.edf": "a" * 64})
        with self.assertRaisesRegex(AcquisitionFailure, "malformed"):
            _parse_checksum_manifest(b"not-a-checksum\n")
        with self.assertRaisesRegex(AcquisitionFailure, "duplicate"):
            _parse_checksum_manifest(
                (f"{'a' * 64}  x.edf\n{'b' * 64}  ./x.edf\n").encode("ascii")
            )
        _validate_task_mapping_document(
            "Valid runs include 3, 7, 11: Motor execution: left versus right hand."
        )
        with self.assertRaisesRegex(AcquisitionFailure, "run mapping"):
            _validate_task_mapping_document("3, 7, 11: motor imagery, hands versus feet")

    def test_registered_metadata_fetch_uses_only_three_gets_and_nine_heads(self):
        source = self.contract["source_dataset"]
        selected = self.contract["selected_files"]
        dataset = (
            "<html>EEG Motor Movement/Imagery Dataset 1.0.0 "
            "10.13026/C28G6P Open Data Commons Attribution License v1.0</html>"
        ).encode()
        checksums = "".join(
            f"{row['official_sha256']}  ./{row['repository_relative_path']}\n"
            for row in selected
        ).encode("ascii")
        mapping = b"<html>3, 7, 11 Motor execution: left vs right hand</html>"
        responses = [
            FakeResponse(dataset, source["dataset_url"], headers={"Content-Length": str(len(dataset))}),
            FakeResponse(
                checksums,
                source["official_checksum_manifest_url"],
                headers={"Content-Length": str(len(checksums))},
            ),
            FakeResponse(
                mapping,
                source["task_mapping_source_url"],
                headers={"Content-Length": str(len(mapping))},
            ),
        ]
        responses.extend(
            FakeResponse(
                b"",
                row["download_url"],
                headers={
                    "Content-Length": str(row["size_bytes"]),
                    "Content-Type": "application/octet-stream",
                },
            )
            for row in selected
        )
        requests = []

        def fake_open(request, *, stage):
            self.assertEqual(stage, "metadata")
            requests.append(request)
            return responses.pop(0)

        with patch.object(acquisition, "_open_request_once", side_effect=fake_open):
            evidence = _fetch_registered_metadata(source, selected, 1024 * 1024)
        self.assertEqual(evidence.request_count, 12)
        self.assertEqual(evidence.network_bytes, len(dataset) + len(checksums) + len(mapping))
        self.assertEqual([request.get_method() for request in requests[:3]], ["GET"] * 3)
        self.assertEqual([request.get_method() for request in requests[3:]], ["HEAD"] * 9)
        self.assertEqual(len(responses), 0)

    def test_redirect_or_unregistered_payload_host_is_refused(self):
        handler = acquisition._RejectRedirect("transfer")
        with self.assertRaisesRegex(AcquisitionFailure, "redirect refused"):
            handler.redirect_request(
                urllib_request("https://physionet.org/example.edf"),
                io.BytesIO(),
                302,
                "redirect",
                {},
                "https://example.com/example.edf",
            )
        with self.assertRaisesRegex(AcquisitionFailure, "registered PhysioNet host"):
            acquisition._open_payload("https://example.com/example.edf", 1)
        with self.assertRaisesRegex(AcquisitionFailure, "registered EDF"):
            acquisition._open_payload(
                "https://physionet.org/files/eegmmidb/1.0.0/S001/S001R03.edf.event",
                1,
            )


def urllib_request(url):
    import urllib.request

    return urllib.request.Request(url)


if __name__ == "__main__":
    unittest.main()
