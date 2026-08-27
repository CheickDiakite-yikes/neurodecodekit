import copy
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import communication_eeg_source_identity as identity


class CommunicationEEGSourceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = identity.build_generated_fixture()
        self.payload = identity.generated_fixture_bytes(self.fixture)

    def mutate(self):
        return copy.deepcopy(self.fixture)

    def assert_refusal(self, payload, route):
        with self.assertRaises(identity.CommunicationSourceIdentityRefusal) as caught:
            identity.canonicalize_generated_response(payload)
        self.assertEqual(caught.exception.refusal_id, route)

    def test_success_is_deterministic_under_source_order(self):
        first = identity.canonicalize_generated_response(self.payload)
        replay = self.mutate()
        replay["data"]["snapshot"]["files"].reverse()
        second = identity.canonicalize_generated_response(
            identity.generated_fixture_bytes(replay)
        )
        self.assertEqual(first.report, second.report)
        self.assertEqual(first.report["route"], "COMM-L0-R1")
        self.assertEqual(first.report["selected_summary"]["participant_count"], 10)
        self.assertEqual(first.report["selected_summary"]["selected_raw_BDF_count"], 10)
        self.assertEqual(len(first.selected_rows), 40)

    def test_selection_is_first_common_session_for_all_people(self):
        result = identity.canonicalize_generated_response(self.payload)
        selected_paths = [row["filename"] for row in result.selected_rows]
        self.assertTrue(all("/ses-01/" in path for path in selected_paths))
        self.assertEqual({path.split("/")[0] for path in selected_paths}, set(identity.EXPECTED_PARTICIPANTS))

    def test_public_report_contains_no_private_row_identity(self):
        report = identity.canonicalize_generated_response(self.payload).report
        keys = identity._walk_keys(report)
        self.assertFalse(keys & identity.FORBIDDEN_PUBLIC_KEYS)
        serialized = json.dumps(report)
        self.assertNotIn("sub-01/", serialized)
        self.assertNotIn("versionId", serialized)

    def test_wrong_snapshot_refuses(self):
        fixture = self.mutate()
        fixture["data"]["snapshot"]["tag"] = "2.1.1"
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[3])

    def test_duplicate_key_invalid_utf8_and_graphql_errors_refuse(self):
        self.assert_refusal(b'{"data":{},"data":{}}', identity.REFUSAL_IDS[2])
        self.assert_refusal(b"\xff", identity.REFUSAL_IDS[2])
        fixture = self.mutate()
        fixture["errors"] = []
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[2])

    def test_unsafe_duplicate_and_bad_url_rows_refuse(self):
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"][1]["filename"] = "../bad.bdf"
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[4])
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"].append(
            copy.deepcopy(fixture["data"]["snapshot"]["files"][1])
        )
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[4])
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"][1]["urls"][0] = "https://example.com/x"
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[4])

    def test_missing_person_or_session_refuses(self):
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"] = [
            row
            for row in fixture["data"]["snapshot"]["files"]
            if not row["filename"].startswith("sub-10/")
        ]
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[5])
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"] = [
            row
            for row in fixture["data"]["snapshot"]["files"]
            if not row["filename"].startswith("sub-01/ses-03/")
        ]
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[5])

    def test_missing_multiple_or_processed_raw_unit_refuses(self):
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"] = [
            row
            for row in fixture["data"]["snapshot"]["files"]
            if not (
                row["filename"].startswith("sub-01/ses-01/")
                and not row["filename"].endswith(".bdf")
            )
        ]
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[6])
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"].append(
            identity._generated_file(
                "sub-01/ses-01/eeg/sub-01_ses-01_task-innerspeech_copy.bdf", 5
            )
        )
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[6])
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"].append(
            identity._generated_file(
                "sub-01/ses-01/eeg/sub-01_ses-01_task-innerspeech_eeg.fif", 5
            )
        )
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[7])

    def test_cap_and_derivatives_refuse(self):
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"][1]["size"] = identity.MAX_SELECTED_BYTES + 1
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[7])
        fixture = self.mutate()
        fixture["data"]["snapshot"]["files"].append(
            identity._generated_file("derivatives/result.json", 1)
        )
        self.assert_refusal(identity.generated_fixture_bytes(fixture), identity.REFUSAL_IDS[7])

    def test_output_refuses_existing_and_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = root / "existing.json"
            existing.write_text("{}", encoding="utf-8")
            with self.assertRaises(identity.CommunicationSourceIdentityRefusal):
                identity._assert_output_path(existing)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(identity.CommunicationSourceIdentityRefusal):
                identity._assert_output_path(link)

    def test_parser_has_no_execute_or_real_path_surface(self):
        parser = identity.build_parser()
        help_text = parser.format_help()
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertIn("inspect", help_text)
        self.assertNotIn("execute", help_text)
        self.assertFalse(hasattr(identity, "urllib_request"))

    def test_plan_is_explicitly_closed_to_real_access(self):
        self.assertEqual(identity.main(["plan"]), 0)


if __name__ == "__main__":
    unittest.main()
