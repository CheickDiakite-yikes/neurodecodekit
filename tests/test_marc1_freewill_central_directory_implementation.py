import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc1_central_directory_audit as audit


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT / "src" / "neurodecodekit" / "datasets" / "marc1_central_directory_audit.py"
)
IMPLEMENTATION_REGISTRY = (
    ROOT
    / "registries"
    / "marc1_freewill_central_directory_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1FreewillCentralDirectoryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(IMPLEMENTATION_REGISTRY.read_text(encoding="utf-8"))

    def setUp(self):
        self.fixture = audit.build_generated_fixture()
        self.thread_env = {key: "1" for key in audit.THREAD_ENV_KEYS}

    def test_implementation_registry_identity(self):
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc1_freewill_central_directory_implementation",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(
            self.registry["implementation_id"],
            "MARC1-CD1-generated-central-directory-implementation-v0",
        )
        self.assertEqual(
            self.registry["status"],
            "generated_mock_implementation_complete_registered_closeout_not_executed",
        )

    def test_implementation_artifact_bindings_are_current(self):
        for binding in self.registry["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_contract_proof_is_exact(self):
        proof = self.registry["green_contract_proof"]
        self.assertEqual(proof["commit"], audit.GREEN_CONTRACT_COMMIT)
        self.assertEqual(proof["CI_run_id"], audit.GREEN_CONTRACT_CI_RUN_ID)
        self.assertEqual(proof["base_job_id"], audit.GREEN_CONTRACT_BASE_JOB_ID)
        self.assertEqual(
            proof["optional_neuro_job_id"], audit.GREEN_CONTRACT_OPTIONAL_JOB_ID
        )
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["contract_sha256"], audit.CONTRACT_SHA256)

    def test_implementation_registry_preserves_zero_authority(self):
        self.assertTrue(
            all(
                value is False
                for value in self.registry["authorization_flags"].values()
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.registry["access_counters"].values())
        )
        self.assertFalse(self.registry["next_gate"]["public_access_eligible_now"])

    def test_registered_contract_loads(self):
        contract = audit.load_registered_contract()
        self.assertEqual(
            contract["contract_id"],
            "MARC-1-freewill-central-directory-generated-contract-v0",
        )
        self.assertEqual(contract["required_mutations"], list(audit.REQUIRED_MUTATIONS))

    def test_fixture_is_small_but_has_exact_virtual_identity(self):
        self.assertEqual(audit.VIRTUAL_ARCHIVE_BYTES, 13_591_548_048)
        self.assertEqual(len(self.fixture.tail_body), 128 * 1024)
        self.assertLess(self.fixture.materialized_bytes, 2 * 1024 * 1024)
        self.assertLess(self.fixture.central_directory_offset, audit.TAIL_START)
        self.assertEqual(len(self.fixture.entries), 18)

    def test_fixture_has_exact_member_kinds_and_zip64_count(self):
        kinds = [entry.kind for entry in self.fixture.entries]
        self.assertEqual(kinds.count("directory"), 4)
        self.assertEqual(kinds.count("regular_file"), 14)
        self.assertEqual(sum(entry.force_zip64 for entry in self.fixture.entries), 1)
        self.assertEqual(sum(bool(entry.flags & (1 << 11)) for entry in self.fixture.entries), 1)

    def test_tail_contains_structural_decoy_and_real_eocd(self):
        occurrences = []
        position = 0
        while True:
            position = self.fixture.tail_body.find(audit.EOCD_SIGNATURE, position)
            if position < 0:
                break
            occurrences.append(position)
            position += 1
        self.assertGreaterEqual(len(occurrences), 2)
        trailer = audit.parse_zip64_trailer(self.fixture.tail_body)
        self.assertEqual(trailer.entry_count, 18)

    def test_zip64_trailer_derives_exact_directory_range(self):
        trailer = audit.parse_zip64_trailer(self.fixture.tail_body)
        self.assertEqual(trailer.central_directory_size, len(self.fixture.central_directory_body))
        self.assertEqual(trailer.central_directory_offset, self.fixture.central_directory_offset)
        self.assertEqual(trailer.range_end + 1, self.fixture.zip64_eocd_offset)

    def test_central_directory_inventory_is_exact(self):
        trailer = audit.parse_zip64_trailer(self.fixture.tail_body)
        inventory = audit.parse_central_directory(
            self.fixture.central_directory_body,
            trailer,
        )
        summary = inventory.aggregate_summary
        self.assertEqual(summary["entry_count"], 18)
        self.assertEqual(summary["directory_entries"], 4)
        self.assertEqual(summary["regular_file_entries"], 14)
        self.assertEqual(summary["ZIP64_member_entries"], 1)
        self.assertEqual(summary["whole_archive_materialized_bytes"], 0)

    def test_private_manifest_has_exact_generated_names(self):
        trailer = audit.parse_zip64_trailer(self.fixture.tail_body)
        inventory = audit.parse_central_directory(self.fixture.central_directory_body, trailer)
        names = [row["member_name"] for row in inventory.private_manifest["entries"]]
        self.assertEqual(len(names), 18)
        self.assertEqual(len(set(names)), 18)
        self.assertIn("dataset/notes_\u00e9.txt", names)

    def test_aggregate_summary_has_no_names_or_offsets(self):
        trailer = audit.parse_zip64_trailer(self.fixture.tail_body)
        summary = audit.parse_central_directory(
            self.fixture.central_directory_body,
            trailer,
        ).aggregate_summary
        text = json.dumps(summary, sort_keys=True)
        self.assertNotIn("dataset/", text)
        self.assertNotIn("local_header_offset", text)
        self.assertNotIn("member_name", text)

    def test_direct_mock_path_passes(self):
        result = audit.run_generated_path(self.fixture, redirect_count=0)
        self.assertEqual(result.request_count, 3)
        self.assertEqual(result.redirect_count, 0)
        self.assertEqual(result.body_response_count, 3)
        self.assertLess(result.body_bytes, audit.MAX_MOCK_BODY_BYTES_PER_PATH)

    def test_two_redirect_mock_path_passes(self):
        result = audit.run_generated_path(self.fixture, redirect_count=2)
        self.assertEqual(result.request_count, 5)
        self.assertEqual(result.redirect_count, 2)
        self.assertEqual(result.body_response_count, 3)

    def test_direct_and_redirect_inventories_match(self):
        direct = audit.run_generated_path(self.fixture, redirect_count=0)
        redirected = audit.run_generated_path(self.fixture, redirect_count=2)
        self.assertEqual(
            direct.inventory.canonical_inventory_bytes,
            redirected.inventory.canonical_inventory_bytes,
        )
        self.assertEqual(
            direct.inventory.aggregate_summary,
            redirected.inventory.aggregate_summary,
        )

    def test_all_32_mutations_refuse_in_order(self):
        routes = audit.run_required_mutations(self.fixture)
        self.assertEqual(tuple(routes), audit.REQUIRED_MUTATIONS)
        self.assertEqual(len(routes), 32)
        self.assertTrue(all(route in audit.REFUSAL_IDS for route in routes.values()))

    def test_mutation_routes_cover_contract_archive_and_privacy(self):
        routes = set(audit.run_required_mutations(self.fixture).values())
        self.assertIn(audit.REFUSAL_IDS[0], routes)
        self.assertIn(audit.REFUSAL_IDS[2], routes)
        self.assertIn(audit.REFUSAL_IDS[3], routes)
        self.assertIn(audit.REFUSAL_IDS[4], routes)
        self.assertIn(audit.REFUSAL_IDS[5], routes)
        self.assertIn(audit.REFUSAL_IDS[6], routes)

    def test_http_200_range_refuses_without_body_read(self):
        response = audit.MockResponse(
            b"do-not-read",
            status=200,
            url=audit.DOWNLOAD_URL,
            headers={"Content-Length": "11"},
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
            audit._read_range_response(
                response,
                expected_start=audit.TAIL_START,
                expected_end=audit.TAIL_END,
            )
        self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[3])
        self.assertEqual(response.read_calls, 0)

    def test_wrong_content_range_refuses(self):
        headers = audit._range_headers(audit.TAIL_START, audit.TAIL_END)
        headers["Content-Range"] = (
            f"bytes {audit.TAIL_START + 1}-{audit.TAIL_END}/{audit.VIRTUAL_ARCHIVE_BYTES}"
        )
        response = audit.MockResponse(
            self.fixture.tail_body,
            status=206,
            url=audit.DOWNLOAD_URL,
            headers=headers,
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit._read_range_response(
                response,
                expected_start=audit.TAIL_START,
                expected_end=audit.TAIL_END,
            )

    def test_multipart_range_refuses_without_body_read(self):
        headers = audit._range_headers(audit.TAIL_START, audit.TAIL_END)
        headers["Content-Type"] = "multipart/byteranges; boundary=generated"
        response = audit.MockResponse(
            self.fixture.tail_body,
            status=206,
            url=audit.DOWNLOAD_URL,
            headers=headers,
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit._read_range_response(
                response,
                expected_start=audit.TAIL_START,
                expected_end=audit.TAIL_END,
            )
        self.assertEqual(response.read_calls, 0)

    def test_private_redirect_destination_refuses(self):
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
            audit._validate_redirect_destination(
                audit.DOWNLOAD_URL,
                "https://private.example.net/file",
                seen={audit.DOWNLOAD_URL},
                resolver=lambda _host: ("127.0.0.1",),
            )
        self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[3])

    def test_redirect_with_body_refuses_without_read(self):
        response = audit.MockResponse(
            b"x",
            status=302,
            url=audit.DOWNLOAD_URL,
            headers={"Content-Length": "1", "Location": "https://example.com/x"},
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit._validate_redirect_response(response)
        self.assertEqual(response.read_calls, 0)

    def test_missing_zip64_locator_refuses(self):
        tail = bytearray(self.fixture.tail_body)
        position = self.fixture.locator_position_in_tail
        tail[position : position + 4] = b"NOPE"
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
            audit.parse_zip64_trailer(bytes(tail))
        self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[4])

    def test_out_of_tail_zip64_refuses(self):
        tail = bytearray(self.fixture.tail_body)
        position = self.fixture.locator_position_in_tail + 8
        audit.struct.pack_into("<Q", tail, position, audit.TAIL_START - 1)
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit.parse_zip64_trailer(bytes(tail))

    def test_directory_trailing_bytes_refuse(self):
        trailer = audit.parse_zip64_trailer(self.fixture.tail_body)
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
            audit.parse_central_directory(
                self.fixture.central_directory_body + b"x",
                replace(trailer, central_directory_size=trailer.central_directory_size + 1),
            )
        self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[5])

    def test_duplicate_member_refuses(self):
        entries = list(self.fixture.entries)
        entries[1] = replace(entries[1], name=entries[0].name)
        body = audit._build_central_directory(entries)
        trailer = replace(
            audit.parse_zip64_trailer(self.fixture.tail_body),
            central_directory_size=len(body),
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit.parse_central_directory(body, trailer)

    def test_dot_path_component_refuses(self):
        entries = list(self.fixture.entries)
        entries[4] = replace(entries[4], name="dataset/./README")
        body = audit._build_central_directory(entries)
        trailer = replace(
            audit.parse_zip64_trailer(self.fixture.tail_body),
            central_directory_size=len(body),
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit.parse_central_directory(body, trailer)

    def test_control_character_in_path_refuses(self):
        entries = list(self.fixture.entries)
        entries[4] = replace(entries[4], name="dataset/bad\x7fname")
        body = audit._build_central_directory(entries)
        trailer = replace(
            audit.parse_zip64_trailer(self.fixture.tail_body),
            central_directory_size=len(body),
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit.parse_central_directory(body, trailer)

    def test_symlink_member_refuses(self):
        entries = list(self.fixture.entries)
        entries[4] = replace(entries[4], kind="symlink")
        body = audit._build_central_directory(entries)
        trailer = replace(
            audit.parse_zip64_trailer(self.fixture.tail_body),
            central_directory_size=len(body),
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit.parse_central_directory(body, trailer)

    def test_missing_zip64_extra_refuses(self):
        entries = list(self.fixture.entries)
        entries[13] = replace(entries[13], extra_override=b"")
        body = audit._build_central_directory(entries)
        trailer = replace(
            audit.parse_zip64_trailer(self.fixture.tail_body),
            central_directory_size=len(body),
        )
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
            audit.parse_central_directory(body, trailer)

    def test_qualification_writes_only_two_small_outputs(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ, self.thread_env
        ):
            output = Path(temporary) / "result"
            outcome = audit.qualify_generated_central_directory(
                output,
                rss_probe=lambda: 32 * 1024 * 1024,
            )
            self.assertEqual(outcome.report["route"], audit.EXPECTED_ROUTE)
            self.assertEqual(len(list(output.iterdir())), 2)
            self.assertLess(outcome.generated_output_bytes, 1024 * 1024)
            self.assertEqual(outcome.generated_input_bytes, self.fixture.materialized_bytes)

    def test_aggregate_report_inspects(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ, self.thread_env
        ):
            outcome = audit.qualify_generated_central_directory(
                Path(temporary) / "result",
                rss_probe=lambda: 32 * 1024 * 1024,
            )
            inspected = audit.inspect_generated_report(outcome.report_path)
            self.assertEqual(inspected["route"], audit.EXPECTED_ROUTE)
            self.assertTrue(all(inspected["acceptance_gates"].values()))

    def test_private_manifest_cannot_be_inspected_as_public(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ, self.thread_env
        ):
            outcome = audit.qualify_generated_central_directory(
                Path(temporary) / "result",
                rss_probe=lambda: 32 * 1024 * 1024,
            )
            with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
                audit.inspect_generated_report(outcome.private_manifest_path)
            self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[6])

    def test_output_collision_refuses_before_generation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result"
            output.mkdir()
            with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
                audit.qualify_generated_central_directory(output, rss_probe=lambda: 1)
            self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[1])

    def test_symlink_parent_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real_parent = root / "real"
            real_parent.mkdir()
            linked_parent = root / "linked"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaises(audit.Marc1CentralDirectoryRefusal):
                audit._assert_output_destination(linked_parent / "result")

    def test_peak_rss_cap_refuses(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ, self.thread_env
        ):
            with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
                audit.qualify_generated_central_directory(
                    Path(temporary) / "result",
                    rss_probe=lambda: audit.MAX_PEAK_RSS_BYTES + 1,
                )
            self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[1])

    def test_thread_cap_refuses(self):
        with mock.patch.dict(os.environ, {audit.THREAD_ENV_KEYS[0]: "2"}):
            with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
                audit._assert_resources(0.1, 1)
            self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[1])

    def test_public_report_rejects_member_name(self):
        with self.assertRaises(audit.Marc1CentralDirectoryRefusal) as caught:
            audit._walk_public({"member_name": "private"})
        self.assertEqual(caught.exception.refusal_id, audit.REFUSAL_IDS[6])

    def test_plan_summary_is_generated_only(self):
        plan = audit.build_plan_summary()
        self.assertEqual(plan["virtual_archive_bytes"], 13_591_548_048)
        self.assertEqual(plan["status"], audit.IMPLEMENTATION_STATUS)
        self.assertEqual(
            plan["contract_status"],
            "generated_mock_only_contract_frozen_implementation_not_started",
        )
        self.assertEqual(plan["network_requests"], 0)
        self.assertEqual(plan["member_payload_bytes"], 0)
        self.assertFalse(plan["scientific_claim"])

    def test_cli_help_exposes_no_execute_or_url(self):
        completed = subprocess.run(
            [sys.executable, "-S", "-m", "neurodecodekit.datasets.marc1_central_directory_audit", "--help"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("plan", completed.stdout)
        self.assertIn("qualify", completed.stdout)
        self.assertIn("inspect", completed.stdout)
        self.assertNotIn("execute", completed.stdout)
        self.assertNotIn("--url", completed.stdout.lower())

    def test_cli_plan_has_zero_live_counters(self):
        completed = subprocess.run(
            [sys.executable, "-S", "-m", "neurodecodekit.datasets.marc1_central_directory_audit", "plan"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            check=True,
            capture_output=True,
            text=True,
        )
        plan = json.loads(completed.stdout)
        self.assertEqual(plan["network_requests"], 0)
        self.assertEqual(plan["real_archive_bytes"], 0)

    def test_source_has_no_network_or_neuro_reader(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("import socket", source)
        self.assertNotIn("import requests", source)
        self.assertNotIn("import mne", source)
        self.assertNotIn("execute", audit._build_parser().format_help())


if __name__ == "__main__":
    unittest.main()
