"""Generated events and entirely mocked lifecycle; never open a real recording."""

from contextlib import ExitStack, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tests.test_inner_speech_reader import generated_events

SPEC = importlib.util.spec_from_file_location(
    "event_census_tested", Path(__file__).resolve().parents[1] / "scripts/census_inner_speech_events.py")
CENSUS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CENSUS)


def events_for(codes):
    return [(1000000 + 1024 * i, code) for i, code in enumerate(codes)]


class CensusTests(unittest.TestCase):
    def assert_accounting(self, events, result):
        self.assertEqual(result["events"], len(events))
        self.assertEqual(sum(result["event_family_counts"].values()), len(events))
        self.assertEqual(sum(row["count"] for row in result["adjacent_family_transitions"]),
                         max(0, len(events) - 1))
        self.assertEqual(sum(sum(run.values()) for run in result["unambiguously_bounded_runs"]) +
                         sum(result["events_outside_unambiguous_runs"].values()), len(events))
        self.assertEqual(sum(row["blocks"] for row in result["trial_start_anchor_block_patterns"]),
                         result["event_family_counts"].get("trial_start", 0))
        self.assertFalse(result["alignment_or_scientific_qualification_established"])

    def test_complete_and_empty_stream_accounting_without_qualification(self):
        for events in ([], generated_events()):
            result = CENSUS.inventory(events)
            self.assert_accounting(events, result)
        self.assertEqual(len(result["unambiguously_bounded_runs"]), 5)
        self.assertTrue(all(run["trial_start"] == 40 for run in result["unambiguously_bounded_runs"]))
        self.assertEqual(result["cue_core_patterns"], {"contiguous_cue_action_relax": 200})

    def test_all_later_anomalies_remain_visible_and_input_is_unchanged(self):
        events = events_for([987654321, 15, 21, 42, 31, 44, 45,
                             42, 32, 44, 44, 45, 46, 42, 44, 45, 46, 16, 999999999])
        before = events.copy()
        result = CENSUS.inventory(events)
        self.assertEqual(events, before)
        self.assert_accounting(events, result)
        patterns = result["trial_start_anchor_block_patterns"]
        self.assertEqual(sum(p["blocks"] for p in patterns if p["rest_count"] == "zero"), 1)
        self.assertEqual(sum(p["blocks"] for p in patterns if p["action_count"] == "multiple"), 1)
        self.assertEqual(sum(p["blocks"] for p in patterns if p["cue_count"] == "zero"), 1)
        self.assertEqual(result["cue_core_patterns"],
                         {"contiguous_cue_action_relax": 1, "incomplete_or_interrupted": 1})
        self.assertEqual(result["event_family_counts"]["unrecognized_status_word"], 2)

    def test_unmatched_and_nested_boundaries_never_certify_nested_runs(self):
        for codes, unassigned in (([16, 15, 21, 16, 15], 2),
                                  ([15, 15, 16, 15, 16, 16, 15, 21, 16], 6)):
            events = events_for(codes)
            result = CENSUS.inventory(events)
            self.assert_accounting(events, result)
            self.assertEqual(result["unambiguously_bounded_runs"],
                             [{"condition_marker": 1, "run_end": 1, "run_start": 1}])
            self.assertEqual(result["unassigned_run_boundary_markers"], unassigned)

    def test_private_identities_and_sample_offsets_do_not_change_aggregates(self):
        events = events_for([987654321, 15, 21, 42, 31, 44, 45, 46, 17, 61, 16])
        changed = [(sample + 1234567890123, {987654321: 999999999, 21: 23, 31: 34, 61: 64}.get(code, code))
                   for sample, code in events]
        result = CENSUS.inventory(events)
        self.assertEqual(result, CENSUS.inventory(changed))
        encoded = json.dumps(result)
        self.assertNotIn("987654321", encoded)
        self.assertNotIn("1234567890123", encoded)

    def test_adjacent_interval_boundaries_and_nonincreasing_samples(self):
        events, origin = [], 1000000
        for a, b, lower, upper in ((42, 31, 1, 5120), (31, 44, 384, 3072),
                                    (44, 45, 2048, 4096), (45, 46, 1, 3072)):
            for delta in (lower - 1, lower, upper, upper + 1):
                events.extend(((origin, a), (origin + delta, b), (origin + upper + 10, 999)))
                origin += upper + 1000
        result = CENSUS.inventory(events)
        self.assert_accounting(events, result)
        self.assertEqual(result["nonincreasing_sample_pairs"], 2)
        self.assertTrue(all(value == {"within_range": 2, "outside_range": 2}
                            for value in result["adjacent_interval_checks"].values()))

    def test_default_dry_run_opens_nothing_and_never_executes(self):
        with patch.object(sys, "argv", ["census"]), \
                patch.object(Path, "open", side_effect=AssertionError("No files")), \
                patch.object(CENSUS, "execute", side_effect=AssertionError("No execution")), \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(CENSUS.main(), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "dry_run_no_data_access")

    def mocked_lifecycle(self, *, manifest_count=10, memory=1024, mutate_evidence=False):
        """All paths, hashes, headers, Status bytes, writes and workers are fakes."""
        stack = ExitStack()
        self.addCleanup(stack.close)
        root, repo = Path("/generated-census"), Path("/generated-repo")
        source, failed = root / "source", root / "failed"
        records, hashes, reads = {}, {}, []
        files = [{"path": f"{p}/ses-01/eeg/{p}_ses-01_task-innerspeech_eeg.bdf",
                  "size_bytes": 123, "sha256": "generated-source"} for p in CENSUS.PARTICIPANTS]
        manifest, acquisition = repo / "manifest.json", repo / "acquisition.json"

        def require(ok, code):
            if not ok:
                raise RuntimeError(code)

        def digest(path, check=None):
            if check:
                check()
            if path == acquisition:
                return "35caa3bea6e782a67ef982d185eb0781e7938cfe4bccc7b93c89fb86d57b54bb"
            if path.suffix == ".bdf":
                return "generated-source"
            hashes[path] = hashes.get(path, 0) + 1
            return "changed" if mutate_evidence and hashes[path] > 1 else "unchanged"

        def write(path, value):
            if path in records:
                raise FileExistsError(path)
            records[path] = value

        def forbidden(*args, **kwargs):
            raise AssertionError("No real reads, physiological windows, parsing, models or scoring")

        class Reader:
            def __init__(self, path):
                reads.append(path)
                self.status_summary = {"generated_only": True}

            def iter_status_events(self, check, *, participant):
                check()
                return events_for([15, 21, 42, 31, 44, 45, 46, 16])

            read_window = forbidden

        frozen = SimpleNamespace(BASE=root, SOURCE=source, LOCAL=failed,
            canonical_local_paths=lambda *args: (root, source, failed), CODE_PATHS=("code.py",),
            MANIFEST=manifest, ACQUISITION=acquisition, require=require, sha256=digest, write_json=write,
            git=lambda *args: "a" * 40 if args == ("rev-parse", "HEAD") else "",
            predict=forbidden, score=forbidden, qualify_all=forbidden, participant_features=forbidden)
        stack.enter_context(patch.multiple(CENSUS, REPO=repo, BDFReader=Reader,
            load_script=lambda name: SimpleNamespace(configured_runner=lambda: frozen)))
        stack.enter_context(patch.dict(sys.modules, {"psutil": SimpleNamespace(
            Process=lambda: SimpleNamespace(memory_info=lambda: SimpleNamespace(rss=memory)))}))
        stack.enter_context(patch.object(CENSUS.threading, "Thread", new=lambda **kwargs:
            SimpleNamespace(start=lambda: None, join=lambda **kwargs: None)))
        stack.enter_context(patch.object(CENSUS.shutil, "disk_usage", return_value=SimpleNamespace(free=30*1024**3)))
        stack.enter_context(patch.object(Path, "resolve", new=lambda path, **kwargs: path))
        stack.enter_context(patch.object(Path, "exists", new=lambda path: path in records))
        stack.enter_context(patch.object(Path, "mkdir", new=lambda path: write(path, "directory")))
        stack.enter_context(patch.object(Path, "stat", return_value=SimpleNamespace(st_size=123)))
        stack.enter_context(patch.object(Path, "read_text", new=lambda path: json.dumps({
            "files": files[:manifest_count] if path == manifest else files})))
        stack.enter_context(patch.object(Path, "open", new=forbidden))
        stack.enter_context(patch("neurodecodekit.datasets.inner_speech.parse_trials", new=forbidden))
        stack.enter_context(redirect_stdout(io.StringIO()))
        return root / CENSUS.CENSUS_NAME, records, reads

    def test_mocked_lifecycle_complete_roster_then_single_use_refusal(self):
        output, records, reads = self.mocked_lifecycle()
        self.assertEqual(CENSUS.execute(), 0)
        result = records[output / "result.json"]
        self.assertEqual(tuple(row["participant"] for row in result["participants"]), CENSUS.PARTICIPANTS)
        self.assertEqual(len(reads), 10)
        for key in ("physiological_windows_read", "training_calls", "scoring_calls", "parser_calls"):
            self.assertEqual(result[key], 0)
        with self.assertRaisesRegex(RuntimeError, "census_already_used_or_redirected"):
            CENSUS.execute()
        self.assertEqual(len(reads), 10)

    def test_mocked_incomplete_roster_refuses_before_reading_any_recording(self):
        output, records, reads = self.mocked_lifecycle(manifest_count=9)
        self.assertEqual(CENSUS.execute(), 1)
        self.assertEqual(reads, [])
        self.assertNotIn(output / "result.json", records)
        self.assertEqual(records[output / "census_failed.json"]["error_code"], "complete_source_required")

    def test_mocked_resource_refusal_does_not_publish_completion(self):
        output, records, reads = self.mocked_lifecycle(memory=CENSUS.MAX_RSS + 1)
        self.assertEqual(CENSUS.execute(), 1)
        self.assertEqual(reads, [])
        self.assertNotIn(output / "result.json", records)
        self.assertEqual(records[output / "census_failed.json"]["error_code"], "census_memory_cap")

    def test_mocked_immutable_evidence_refusal_retains_no_complete_result(self):
        output, records, reads = self.mocked_lifecycle(mutate_evidence=True)
        self.assertEqual(CENSUS.execute(), 1)
        self.assertEqual(len(reads), 10)
        self.assertNotIn(output / "result.json", records)
        self.assertEqual(records[output / "census_failed.json"]["error_code"], "immutable_evidence_changed")


if __name__ == "__main__":
    unittest.main()
