import copy
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import physionet_low_frequency_acquisition as acquisition


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


def tiny_contract_and_payloads():
    contract = copy.deepcopy(acquisition.load_registered_contract(ROOT))
    payloads = {}
    for index, row in enumerate(contract["selected_files"]):
        payload = (f"WO9R-generated-EDF-fixture-{index:02d}|".encode("ascii")) * 2
        row["size_bytes"] = len(payload)
        row["sha256"] = hashlib.sha256(payload).hexdigest()
        payloads[row["path"]] = payload
    total = sum(len(payload) for payload in payloads.values())
    caps = contract["resource_caps"]["acquisition"]
    caps["edf_payload_bytes"] = total
    caps["minimum_free_disk_bytes_before"] = 1
    caps["peak_incremental_disk_bytes"] = total + 2 * 1024 * 1024
    caps["wall_time_seconds"] = 60
    documents = acquisition.synthetic_metadata_documents(
        contract,
        contract["selected_files"],
    )
    file_root = contract["metadata_registration"]["official_file_root_url"].rstrip("/")
    documents.update(
        {f"{file_root}/{path}": payload for path, payload in payloads.items()}
    )
    return contract, payloads, documents


class RecordingOpener:
    def __init__(self, payloads):
        self.payloads = dict(payloads)
        self.calls = []

    def __call__(self, url, maximum_bytes):
        self.calls.append(url)
        return acquisition.bytes_opener(self.payloads)(url, maximum_bytes)


class PhysioNetLowFrequencyAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.contract, self.payloads, self.documents = tiny_contract_and_payloads()

    def tearDown(self):
        self.temporary.cleanup()

    def run_fixture(self, *, contract=None, documents=None, environ=None):
        selected_contract = contract or self.contract
        opener = RecordingOpener(documents or self.documents)
        outcome = acquisition.run_acquisition(
            workspace_root=self.root,
            contract=selected_contract,
            opener=opener,
            environ=environ or THREAD_ENV,
            enforce_registered_roots=False,
            minimum_free_disk_bytes=1,
            rss_reader=lambda: 16 * 1024 * 1024,
        )
        return outcome, opener

    def test_registered_plan_and_hash_locks_are_exact_and_dry(self):
        plan = acquisition.registered_plan(ROOT)
        decision = acquisition.load_registered_decision(ROOT)
        self.assertEqual(plan["mode"], "dry_run_no_registered_path_stat_no_network")
        self.assertEqual(plan["file_count"], 72)
        self.assertEqual(plan["payload_bytes"], 184_252_032)
        self.assertEqual(plan["payload_requests"], 72)
        self.assertEqual(decision["authorized_contract"]["sha256"], acquisition.CONTRACT_SHA256)

    def test_mocked_72_file_roundtrip_is_opaque_bounded_and_exact(self):
        outcome, opener = self.run_fixture()
        self.assertTrue(outcome.passed)
        manifest = outcome.manifest
        measurements = manifest["measurements"]
        self.assertEqual(measurements["metadata_requests"], 15)
        self.assertEqual(measurements["edf_payload_requests"], 72)
        self.assertEqual(measurements["opaque_local_hash_passes"], 72)
        self.assertEqual(measurements["edf_content_parses"], 0)
        self.assertEqual(len(opener.calls), 87)
        self.assertLessEqual(
            measurements["peak_incremental_disk_upper_bound_bytes"],
            self.contract["resource_caps"]["acquisition"]["peak_incremental_disk_bytes"],
        )
        payload_root = self.root / self.contract["acquisition_contract"]["payload_root"]
        for relative, payload in self.payloads.items():
            self.assertEqual((payload_root / relative).read_bytes(), payload)
        self.assertFalse(
            (self.root / self.contract["acquisition_contract"]["temporary_root"]).exists()
        )

    def test_metadata_mismatch_aborts_before_any_payload_request(self):
        documents = dict(self.documents)
        dataset_url = self.contract["metadata_registration"]["official_dataset_url"]
        documents[dataset_url] = b"wrong generated metadata"
        opener = RecordingOpener(documents)
        with self.assertRaisesRegex(acquisition.WO9RAcquisitionFailure, "dataset page"):
            acquisition.run_acquisition(
                workspace_root=self.root,
                contract=self.contract,
                opener=opener,
                environ=THREAD_ENV,
                enforce_registered_roots=False,
                minimum_free_disk_bytes=1,
                rss_reader=lambda: 16 * 1024 * 1024,
            )
        file_root = self.contract["metadata_registration"]["official_file_root_url"]
        self.assertFalse(any(url.startswith(file_root) and url.endswith(".edf") for url in opener.calls))

    def test_payload_hash_mismatch_consumes_once_and_cleans_only_temporary_files(self):
        documents = dict(self.documents)
        first = self.contract["selected_files"][0]
        file_root = self.contract["metadata_registration"]["official_file_root_url"].rstrip("/")
        url = f"{file_root}/{first['path']}"
        documents[url] = b"X" * first["size_bytes"]
        with self.assertRaisesRegex(acquisition.WO9RAcquisitionFailure, "hash mismatch"):
            self.run_fixture(documents=documents)
        receipt = self.root / self.contract["acquisition_contract"]["receipt_root"]
        temporary = self.root / self.contract["acquisition_contract"]["temporary_root"]
        payload = self.root / self.contract["acquisition_contract"]["payload_root"]
        self.assertTrue((receipt / "acquisition_consumed.v0.json").is_file())
        self.assertFalse(temporary.exists())
        self.assertFalse(payload.exists())
        with self.assertRaisesRegex(acquisition.WO9RAcquisitionRefusal, "already exists"):
            self.run_fixture(documents=documents)

    def test_incoherent_disk_cap_refuses_before_creating_any_output(self):
        contract = copy.deepcopy(self.contract)
        contract["resource_caps"]["acquisition"]["peak_incremental_disk_bytes"] = 1
        with self.assertRaisesRegex(acquisition.WO9RAcquisitionRefusal, "exceed disk cap"):
            self.run_fixture(contract=contract)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_thread_mismatch_and_symlink_parent_fail_closed(self):
        environ = dict(THREAD_ENV)
        environ["OMP_NUM_THREADS"] = "2"
        with self.assertRaisesRegex(acquisition.WO9RAcquisitionRefusal, "one-thread"):
            self.run_fixture(environ=environ)
        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(outside, self.root / "data")
        with self.assertRaisesRegex(acquisition.WO9RAcquisitionRefusal, "crosses a symlink"):
            self.run_fixture()

    def test_acquisition_module_has_no_neural_reader_import(self):
        source = Path(acquisition.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import mne", source)
        self.assertNotIn("read_raw_edf", source)


if __name__ == "__main__":
    unittest.main()
