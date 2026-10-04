"""Generated/mock audit lifecycle only; no real participant file is opened."""

from contextlib import ExitStack, contextmanager, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("session2_audit_tested",
    Path(__file__).resolve().parents[1] / "scripts/audit_inner_speech_session2.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class SessionTwoAuditTests(unittest.TestCase):
    def test_default_dry_run_never_loads_runner_or_opens_source(self):
        with patch.object(Path, "open", side_effect=AssertionError("No files")), \
                patch.object(AUDIT, "load_script", side_effect=AssertionError("No runner")), \
                patch.object(AUDIT, "execute", side_effect=AssertionError("No execution")), \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(AUDIT.main([]), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["status"], "dry_run_no_data_access")
        self.assertEqual((result["participants"], result["max_seconds"]), (10, 120))
        self.assertFalse(result["physiology_training_scoring_allowed"])

    @contextmanager
    def lifecycle(self, **options):
        """All paths, recordings, metadata, writes, clocks and workers are fakes."""
        root, repo = Path("/generated-audit"), Path("/generated-repo")
        canonical = root / "canonical"
        source, output = canonical / "source", canonical / AUDIT.AUDIT_NAME
        state = SimpleNamespace(records={}, reads=[], decodes=[], analyzed=[], hashes={},
                                clock=0.0, armed=False, inventory_calls=0)

        def forbidden(*args, **kwargs):
            raise AssertionError("No real I/O, physiology, trial parsing, fitting or scoring")

        def require(ok, code):
            if not ok:
                raise RuntimeError(code)

        def write(path, value):
            if path in state.records:
                raise FileExistsError(path)
            state.records[path] = value

        def mkdir(path):
            write(path, "directory")
            state.armed = True

        def digest(path, check=None):
            if check:
                check()
            state.hashes[path] = state.hashes.get(path, 0) + 1
            if path.suffix == ".bdf":
                return ("changed" if options.get("changed_source") and
                        state.hashes[path] > 1 else "source-digest")
            return ("changed" if options.get("changed_evidence") and
                    state.hashes[path] > 1 else "unchanged")

        def read_text(path, *args, **kwargs):
            if path == repo / AUDIT.FAILURE:
                return json.dumps({"evidence_hashes": {
                    "started_json_sha256": "changed" if options.get("wrong_failure") else "unchanged",
                    "execution_failed_json_sha256": "unchanged"}})
            return forbidden()

        def canonicalize(base, original_source, local):
            self.assertEqual(local.name, AUDIT.AUDIT_NAME)
            return canonical, source, output

        def inventory(budget):
            state.inventory_calls += 1
            self.assertTrue(state.armed)
            self.assertIn(output / "started.json", state.records)
            self.assertEqual((frozen.BASE, frozen.SOURCE, frozen.LOCAL), (canonical, source, output))
            if options.get("deadline"):
                state.clock = AUDIT.MAX_SECONDS + 1
            budget.check()
            if options.get("identity_error"):
                raise RuntimeError(options["identity_error"])
            people = list(AUDIT.PARTICIPANTS)
            if options.get("roster") == "short":
                people.pop()
            elif options.get("roster") == "reversed":
                people.reverse()
            rows = []
            for person in people:
                path = source / person / "ses-02" / "eeg" / f"{person}_ses-02.bdf"
                rows.append((person, path, digest(path, budget.check)))
            return rows

        events = [(111111111111, 31), (111111112135, 44), (111111114695, 45)]

        def decode(name, reader, check, participant, session):
            self.assertEqual(session, "ses-02")
            self.assertEqual(participant, reader.path.parents[2].name)
            check()
            state.decodes.append((name, participant, session))
            if participant == "sub-01" and name == options.get("refused_decoder"):
                raise AUDIT.InnerSpeechRefusal(options.get("refusal", "reference_shortest_event"))
            if options.get("unexpected_io") and participant == "sub-02":
                raise OSError("private_path_123456789")
            return events + ([(111111115719, 46)] if options.get("disagree") and
                             name == "independent" and participant == "sub-01" else [])

        class Reader:
            def __init__(self, path):
                self.path = path
                state.reads.append(path)

            def iter_status_events(self, check, *, participant, session):
                return decode("frozen", self, check, participant, session)

            read_window = forbidden

        def reference(reader, *, check, participant, session):
            return decode("independent", reader, check, participant, session)

        def analyze(values, check):
            check()
            state.analyzed.append(tuple(values))
            return {"events": len(values), "generated_structure_only": True}

        frozen = SimpleNamespace(BASE=root, SOURCE=root / "source", LOCAL=root / "old",
            CODE_PATHS=("code.py",), PRIOR_EVIDENCE={"prior": ("started.json", "result.json")},
            canonical_local_paths=canonicalize, sha256=digest, write_json=write, require=require,
            source_inventory=inventory, git=lambda *args: "a" * 40 if args == ("rev-parse", "HEAD") else "",
            main=forbidden, predict=forbidden, score=forbidden, qualify_all=forbidden,
            participant_features=forbidden)

        def load(name):
            if name == "test_inner_speech_temporal":
                return SimpleNamespace(configured_runner=lambda: frozen)
            self.assertEqual(name, "inner_speech_session2_structure")
            return SimpleNamespace(analyze_structure=analyze)

        with ExitStack() as stack:
            stack.enter_context(patch.multiple(AUDIT, REPO=repo, load_script=load,
                BDFReader=Reader, reference_status_events=reference))
            stack.enter_context(patch.dict(sys.modules, {"numpy": None, "psutil": SimpleNamespace(Process=lambda:
                SimpleNamespace(memory_info=lambda: SimpleNamespace(rss=options.get("memory", 1024))))}))
            stack.enter_context(patch.object(AUDIT.threading, "Thread", new=lambda **kwargs:
                SimpleNamespace(start=lambda: None, join=lambda **kwargs: None)))
            stack.enter_context(patch.object(AUDIT.time, "monotonic", new=lambda: state.clock))
            stack.enter_context(patch.object(AUDIT.shutil, "disk_usage", new=lambda path:
                SimpleNamespace(free=0 if options.get("disk") and state.armed else 30 * 1024**3)))
            stack.enter_context(patch.object(Path, "open", new=forbidden))
            stack.enter_context(patch.object(Path, "read_text", new=read_text))
            stack.enter_context(patch.object(Path, "exists", new=lambda path: path in state.records))
            stack.enter_context(patch.object(Path, "mkdir", new=mkdir))
            stack.enter_context(patch.object(Path, "iterdir", new=lambda path:
                iter(p for p in state.records if p.parent == path)))
            stack.enter_context(patch.object(Path, "is_file", new=lambda path:
                path in state.records and isinstance(state.records[path], dict)))
            stack.enter_context(patch.object(Path, "stat", new=lambda path:
                SimpleNamespace(st_size=len(json.dumps(state.records[path]).encode()))))
            stack.enter_context(patch("neurodecodekit.datasets.inner_speech.parse_trials", new=forbidden))
            if options.get("output_cap"):
                stack.enter_context(patch.object(AUDIT, "MAX_OUTPUT", 1024))
            stack.enter_context(redirect_stdout(io.StringIO()))
            yield state, output

    def test_all_ten_ordered_two_decoders_hashes_and_exclusive_consumption(self):
        with self.lifecycle() as (state, output):
            self.assertEqual(AUDIT.execute(), 0)
            result = state.records[output / "result.json"]
            self.assertEqual(tuple(row["participant"] for row in result["participants"]), AUDIT.PARTICIPANTS)
            self.assertEqual(result["decoder_agreement_participants"], 10)
            self.assertEqual((len(state.reads), len(state.decodes), len(state.analyzed)), (10, 20, 10))
            self.assertTrue(all(state.hashes[path] == 2 for path in state.reads))
            for key in ("physiological_windows_read", "training_calls", "scoring_calls", "trial_parser_calls"):
                self.assertEqual(result[key], 0)
            self.assertFalse(result["alignment_or_scientific_qualification_established"])
            self.assertIn("scripts/audit_inner_speech_events.py", result["code_hashes"])
            self.assertNotIn("111111111111", json.dumps(state.records[output / "result.json"]))
            with self.assertRaisesRegex(RuntimeError, "audit_already_used"):
                AUDIT.execute()
            self.assertEqual((state.inventory_calls, len(state.reads)), (1, 10))

    def test_disagreement_retains_both_structures_and_does_not_choose_winner(self):
        with self.lifecycle(disagree=True) as (state, output):
            self.assertEqual(AUDIT.execute(), 0)
            result = state.records[output / "result.json"]
            row = result["participants"][0]
            self.assertFalse(row["full_ordered_decoder_agreement"])
            self.assertEqual(result["decoder_agreement_participants"], 9)
            self.assertEqual(row["decoders"]["frozen"]["structure"]["events"], 3)
            self.assertEqual(row["decoders"]["independent"]["structure"]["events"], 4)
            self.assertEqual(len(state.reads), 10)

    def test_semantic_decoder_refusal_is_reported_without_stopping_other_people(self):
        with self.lifecycle(refused_decoder="independent") as (state, output):
            self.assertEqual(AUDIT.execute(), 0)
            result = state.records[output / "result.json"]
            row = result["participants"][0]
            self.assertIsNone(row["full_ordered_decoder_agreement"])
            self.assertEqual(row["decoders"]["independent"], {
                "status": "decoder_refused", "refusal_code": "reference_shortest_event"})
            self.assertEqual(len(state.reads), 10)

    def test_resource_identity_and_immutability_failures_never_publish_success(self):
        cases = (({"memory": AUDIT.MAX_RSS + 1}, "audit_memory_cap"),
                 ({"deadline": True}, "audit_deadline"), ({"disk": True}, "free_disk_floor"),
                 ({"output_cap": True}, "audit_output_cap"),
                 ({"identity_error": "session_two_acquisition_identity"}, "session_two_acquisition_identity"),
                 ({"identity_error": "source_hash"}, "source_hash"),
                 ({"roster": "short"}, "complete_source_roster"),
                 ({"roster": "reversed"}, "complete_source_roster"),
                 ({"changed_source": True}, "source_changed_during_audit"),
                 ({"changed_evidence": True}, "immutable_evidence_changed"),
                 ({"unexpected_io": True}, "source_or_audit_error"))
        for options, expected in cases:
            with self.subTest(options=options), self.lifecycle(**options) as (state, output):
                self.assertEqual(AUDIT.execute(), 1)
                self.assertNotIn(output / "result.json", state.records)
                failure = state.records[output / "audit_failed.json"]
                self.assertEqual(failure["error_code"], expected)
                self.assertNotIn("private_path", json.dumps(failure))
                if options.get("identity_error") or options.get("roster"):
                    self.assertEqual(state.reads, [])
                with self.assertRaisesRegex(RuntimeError, "audit_already_used"):
                    AUDIT.execute()

    def test_decoder_integrity_failure_is_fatal_not_a_reportable_finding(self):
        with self.lifecycle(refused_decoder="frozen", refusal="file_changed") as (state, output):
            self.assertEqual(AUDIT.execute(), 1)
            self.assertNotIn(output / "result.json", state.records)
            self.assertEqual(len(state.reads), 1)
            self.assertEqual(state.records[output / "audit_failed.json"]["status"], "failed_no_retry")

    def test_prior_failure_binding_refuses_before_consumption_or_source_access(self):
        with self.lifecycle(wrong_failure=True) as (state, output):
            with self.assertRaisesRegex(RuntimeError, "prior_failure_changed"):
                AUDIT.execute()
            self.assertFalse(state.armed)
            self.assertEqual((state.inventory_calls, state.reads), (0, []))
            self.assertNotIn(output, state.records)


if __name__ == "__main__":
    unittest.main()
