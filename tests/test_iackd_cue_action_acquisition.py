import copy
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import iackd_cue_action_acquisition as acquisition


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fixture_contract_and_inventory():
    payloads = {
        "sub-01/eeg/run-01_eeg.vhdr": b"fixture-vhdr\n",
        "sub-01/eeg/run-01_eeg.eeg": b"fixture-signal-bytes",
        "sub-01/sourcedata/beh/run-01_ball.tsv": b"time\tx\n0\t0\n",
        "sub-01/sourcedata/beh/run-01_leap.tsv": b"time\tx\ty\tz\n0\t0\t0\t0\n",
    }
    roles = ("eeg_header", "eeg_signal", "ball_stream", "leap_stream")
    rows = []
    for index, (path, payload) in enumerate(payloads.items()):
        rows.append(
            {
                "path": path,
                "subject": "sub-01",
                "role": roles[index],
                "size_bytes": len(payload),
                "etag": hashlib.md5(payload).hexdigest(),  # noqa: S324 - generated fixture ID
                "last_modified": f"2025-11-17T02:50:{17 + index:02d}.000Z",
            }
        )
    rows.sort(key=lambda row: row["path"])
    identity_bytes, identity_sha256 = acquisition._canonical_identity(rows)
    description = json.dumps(
        {
            "Name": "IACKD fixture",
            "BIDSVersion": "1.7.0",
            "License": "CC0",
            "DatasetDOI": "doi:10.18112/openneuro.ds006840.v1.0.0",
        },
        sort_keys=True,
    ).encode()
    changes = b"1.0.0 generated fixture\n"
    contract = {
        "dataset_binding": {
            "accession": "ds006840",
            "version": "1.0.0",
            "dataset_doi": "10.18112/openneuro.ds006840.v1.0.0",
            "bids_version": "1.7.0",
            "license": "CC0",
            "participant_ids": ["sub-01"],
            "bids_run_count": 1,
            "selected_object_count": len(rows),
            "exact_selected_payload_bytes": sum(row["size_bytes"] for row in rows),
        },
        "metadata_reverification": {
            "list_objects_endpoint": "https://fixture.invalid/openneuro.org",
            "list_objects_query": "list-type=2&prefix=ds006840/&max-keys=1000",
            "expected_listed_object_count": len(rows),
            "expected_listed_total_bytes": sum(row["size_bytes"] for row in rows),
            "canonical_identity_sha256": identity_sha256,
        },
        "acquisition_contract": {
            "object_base_url": "https://fixture.invalid/openneuro.org/ds006840/",
            "payload_root": "data/iackd_fixture/raw",
            "temporary_root": ".codex_work/iackd_fixture/tmp",
            "receipt_root": ".codex_work/iackd_fixture/receipt",
        },
        "resource_caps": {
            "acquisition": {
                "payload_requests": len(rows),
                "payload_bytes": sum(row["size_bytes"] for row in rows),
                "metadata_body_bytes": 1024 * 1024,
                "wall_time_seconds": 30,
                "peak_rss_bytes": 256 * 1024 * 1024,
                "peak_incremental_disk_bytes": 4 * 1024 * 1024,
                "minimum_free_disk_bytes": 1,
                "private_receipt_bytes": 1024 * 1024,
            }
        },
    }
    inventory = {
        "source_documents": {
            "dataset_description": {
                "url": "https://fixture.invalid/dataset_description.json",
                "sha256": digest(description),
            },
            "changes": {
                "url": "https://fixture.invalid/CHANGES",
                "sha256": digest(changes),
            },
        },
        "selected_objects": rows,
    }
    first, second = acquisition.synthetic_listing_pages(rows, split_at=2)
    first_url = (
        f"{contract['metadata_reverification']['list_objects_endpoint']}?"
        f"{contract['metadata_reverification']['list_objects_query']}"
    )
    second_url = f"{first_url}&continuation-token=fixture-token"
    documents = {
        inventory["source_documents"]["dataset_description"]["url"]: description,
        inventory["source_documents"]["changes"]["url"]: changes,
        first_url: first,
        second_url: second,
    }
    base = contract["acquisition_contract"]["object_base_url"].rstrip("/")
    etags = {}
    for row in rows:
        url = f"{base}/{row['path']}"
        documents[url] = payloads[row["path"]]
        etags[url] = row["etag"]
    return contract, inventory, documents, etags, identity_bytes


class IACKDCueActionAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (
            self.contract,
            self.inventory,
            self.documents,
            self.etags,
            self.identity_bytes,
        ) = fixture_contract_and_inventory()

    def tearDown(self):
        self.temporary.cleanup()

    def run_fixture(self, **changes):
        return acquisition.run_acquisition(
            workspace_root=self.root,
            contract=changes.get("contract", self.contract),
            inventory=changes.get("inventory", self.inventory),
            opener=changes.get("opener", acquisition.bytes_opener(self.documents, self.etags)),
            environ=changes.get("environ", THREAD_ENV),
            enforce_registered_roots=False,
            minimum_free_disk_bytes=1,
            rss_reader=lambda: 16 * 1024 * 1024,
        )

    def test_registered_plan_is_exact_and_does_not_touch_local_payload(self):
        plan = acquisition.registered_plan(ROOT)
        self.assertEqual(plan["mode"], "dry_run_no_registered_path_stat_no_network")
        self.assertEqual(plan["dataset_id"], "ds006840")
        self.assertEqual(plan["object_count"], 1340)
        self.assertEqual(plan["payload_bytes"], 7_249_113_684)
        self.assertEqual(
            plan["inventory_sha256"],
            "c30b518f9dafe3d46128849725e1f2f8fdce33239fbf6ade8603d66a64f0ffa5",
        )

    def test_registered_inventory_canonical_identity_replays_exactly(self):
        inventory = acquisition.load_registered_inventory(ROOT)
        size, observed = acquisition._canonical_identity(inventory["selected_objects"])
        self.assertEqual(size, 231_424)
        self.assertEqual(
            observed,
            "c30b518f9dafe3d46128849725e1f2f8fdce33239fbf6ade8603d66a64f0ffa5",
        )

    def test_generated_four_object_roundtrip_hashes_while_streaming(self):
        outcome = self.run_fixture()
        self.assertTrue(outcome.passed)
        measurements = outcome.manifest["measurements"]
        self.assertEqual(measurements["metadata_requests"], 4)
        self.assertEqual(measurements["payload_requests"], 4)
        self.assertEqual(measurements["payload_bytes"], self.contract["resource_caps"]["acquisition"]["payload_bytes"])
        self.assertEqual(measurements["stream_hash_passes"], 4)
        self.assertEqual(measurements["post_write_content_opens"], 0)
        self.assertEqual(measurements["payload_content_parses"], 0)
        payload_root = self.root / self.contract["acquisition_contract"]["payload_root"]
        self.assertTrue(payload_root.is_dir())
        for record in outcome.manifest["file_records"]:
            expected = self.documents[
                f"https://fixture.invalid/openneuro.org/ds006840/{record['path']}"
            ]
            self.assertEqual(record["observed_local_sha256"], digest(expected))
            self.assertNotIn(str(self.root), json.dumps(record))

    def test_metadata_identity_drift_consumes_and_stops_before_payload(self):
        inventory = copy.deepcopy(self.inventory)
        inventory["selected_objects"][0]["etag"] = "0" * 32
        opener = acquisition.bytes_opener(self.documents, self.etags)
        with self.assertRaisesRegex(acquisition.IACKDAcquisitionFailure, "identity drift"):
            self.run_fixture(inventory=inventory, opener=opener)
        payload_base = self.contract["acquisition_contract"]["object_base_url"]
        self.assertFalse(any(url.startswith(payload_base) for url in opener.calls))
        receipt = self.root / self.contract["acquisition_contract"]["receipt_root"]
        self.assertTrue((receipt / "acquisition_consumed.v0.json").is_file())
        self.assertFalse((self.root / self.contract["acquisition_contract"]["payload_root"]).exists())

    def test_payload_etag_mismatch_fails_and_cleans_only_temporary_root(self):
        etags = dict(self.etags)
        first = next(iter(etags))
        etags[first] = "f" * 32
        with self.assertRaisesRegex(acquisition.IACKDAcquisitionFailure, "ETag mismatch"):
            self.run_fixture(opener=acquisition.bytes_opener(self.documents, etags))
        temporary = self.root / self.contract["acquisition_contract"]["temporary_root"]
        receipt = self.root / self.contract["acquisition_contract"]["receipt_root"]
        self.assertFalse(temporary.exists())
        self.assertTrue((receipt / "acquisition_consumed.v0.json").is_file())

    def test_payload_without_etag_fails_closed(self):
        with self.assertRaisesRegex(acquisition.IACKDAcquisitionFailure, "ETag mismatch"):
            self.run_fixture(opener=acquisition.bytes_opener(self.documents))
        receipt = self.root / self.contract["acquisition_contract"]["receipt_root"]
        self.assertTrue((receipt / "acquisition_consumed.v0.json").is_file())

    def test_truncated_payload_consumes_once_and_cannot_rerun(self):
        documents = dict(self.documents)
        row = self.inventory["selected_objects"][0]
        url = f"{self.contract['acquisition_contract']['object_base_url'].rstrip('/')}/{row['path']}"
        documents[url] = documents[url][:-1]
        with self.assertRaises(acquisition.IACKDAcquisitionFailure):
            self.run_fixture(opener=acquisition.bytes_opener(documents, self.etags))
        with self.assertRaisesRegex(acquisition.IACKDAcquisitionRefusal, "already exists"):
            self.run_fixture()

    def test_thread_mismatch_and_symlink_parent_fail_before_consumption(self):
        environ = dict(THREAD_ENV)
        environ["OMP_NUM_THREADS"] = "2"
        with self.assertRaisesRegex(acquisition.IACKDAcquisitionRefusal, "one-thread"):
            self.run_fixture(environ=environ)
        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(outside, self.root / "data")
        with self.assertRaisesRegex(acquisition.IACKDAcquisitionRefusal, "symlink"):
            self.run_fixture()

    def test_listing_parser_rejects_missing_identity_and_wrong_page_shape(self):
        malformed = b"<ListBucketResult><IsTruncated>true</IsTruncated></ListBucketResult>"
        with self.assertRaisesRegex(acquisition.IACKDAcquisitionFailure, "continuation"):
            acquisition._listing_objects(malformed)
        first, _ = acquisition.synthetic_listing_pages(
            self.inventory["selected_objects"], split_at=2
        )
        with self.assertRaisesRegex(acquisition.IACKDAcquisitionFailure, "truncation pattern"):
            acquisition.validate_metadata_documents(
                self.contract,
                self.inventory,
                self.documents[self.inventory["source_documents"]["dataset_description"]["url"]],
                self.documents[self.inventory["source_documents"]["changes"]["url"]],
                (first, first),
            )

    def test_response_url_change_is_rejected_as_redirect_equivalent(self):
        payloads = dict(self.documents)

        def opener(url, maximum_bytes):
            payload = payloads[url]
            if url.startswith(self.contract["acquisition_contract"]["object_base_url"]):
                return acquisition.FixtureResponse(payload, f"{url}?changed", "0" * 32)
            return io.BytesIO(payload)

        with self.assertRaisesRegex(acquisition.IACKDAcquisitionFailure, "URL mismatch"):
            self.run_fixture(opener=opener)

    def test_acquisition_module_has_no_neural_reader_import(self):
        source = Path(acquisition.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import mne", source)
        self.assertNotIn("read_raw_brainvision", source)
        self.assertNotIn("import numpy", source)


if __name__ == "__main__":
    unittest.main()
