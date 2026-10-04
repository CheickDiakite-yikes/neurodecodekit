"""Generated/mock successor checks only; never open participant files or outputs."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.test_inner_speech_reader import generated_events
from tests import test_inner_speech_temporal_runner as temporal_tests


SPEC = importlib.util.spec_from_file_location("attention_wrapper_tested",
    Path(__file__).resolve().parents[1] / "scripts/test_inner_speech_temporal_attention.py")
WRAPPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WRAPPER)
np = temporal_tests.np


class TemporalAttentionTests(unittest.TestCase):
    def setUp(self):
        self.runner = WRAPPER.configured_runner()

    # Reuse the existing entirely in-memory scorer fixture, not any real artifacts.
    roster = temporal_tests.TemporalRunnerTests.roster
    score_fixture = temporal_tests.TemporalRunnerTests.score_fixture

    def test_dry_run_and_successor_identity_require_no_source_or_numpy(self):
        r = self.runner
        with mock.patch.object(Path, "open", side_effect=AssertionError("No files")), \
                mock.patch.object(r, "git", side_effect=AssertionError("No Git")), \
                mock.patch.dict("sys.modules", {"numpy": None}), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(r.main([]), 0)
            with self.assertRaisesRegex(RuntimeError, "attempt_identity"):
                r.score("a" * 40, None, {"experiment_id": "INNER-SPEECH-TEMPORAL-DEV-S2"})
        self.assertEqual(json.loads(output.getvalue())["experiment_id"], "INNER-SPEECH-TEMPORAL-S2-A1")
        self.assertEqual(r.LOCAL.name, "inner_speech_temporal_s2_a1_20261002")
        for path, suffix in ((r.PLAN, "plan"), (r.FREEZE, "prediction_freeze"), (r.RESULT, "result")):
            self.assertEqual(path.name, f"inner_speech_temporal_attention_{suffix}.v0.json")
        self.assertEqual(r.PRIOR_EVIDENCE[WRAPPER.FAILED_ROOT], ("started.json", "execution_failed.json"))
        self.assertEqual(r.PRIOR_EVIDENCE[WRAPPER.AUDIT_ROOT], ("started.json", "result.json"))
        self.assertIn(WRAPPER.AUDIT, r.CODE_PATHS)

    def test_only_parser_opt_in_changes_science_and_legacy_default_stays_strict(self):
        r, original = self.runner, WRAPPER.load_temporal_runner()
        self.assertEqual(r.EVENT_PARSER_KWARGS, {"allow_attention_after_relax": True})
        self.assertEqual(original.EVENT_PARSER_KWARGS, {})
        for name in ("SOURCE", "SOURCE_SESSION", "MANIFEST", "ACQUISITION", "CONDITIONS",
                     "MODEL_MODULE", "EXPERIMENT_KWARGS", "MAX_EXCLUSIONS",
                     "MAX_SECONDS", "MAX_RSS", "MAX_OUTPUT"):
            self.assertEqual(getattr(r, name), getattr(original, name), name)
        self.assertEqual((r.MAX_SECONDS, r.MAX_RSS, r.MAX_OUTPUT), (1200, 1024**3, 32 * 1024**2))
        for name in ("predict", "qualify_all", "participant_features", "timing_features",
                     "expected_trials", "validate_pairs", "primary_decision", "score",
                     "canonical_local_paths", "main"):
            self.assertEqual(getattr(r, name).__code__, getattr(original, name).__code__, name)

    @contextlib.contextmanager
    def admission(self):
        original = WRAPPER.load_temporal_runner()
        inventory = mock.Mock(return_value="generated-inventory")
        original.source_inventory = inventory
        with mock.patch.object(WRAPPER, "load_temporal_runner", return_value=original):
            r = WRAPPER.configured_runner()
        r.BASE = Path("/generated-attention")
        audit = {
            "audit_id": "INNER-SPEECH-EVENT-AUDIT-S2", "status": "audit_completed",
            "dataset": "ds003626", "version": "2.1.2", "session": "ses-02",
            "participants_audited": 10, "decoder_agreement_participants": 10,
            "participants": [{"participant": person, "full_ordered_decoder_agreement": True,
                "source_hash_verified_before_and_after": True, "decoders": {
                    name: {"status": "decoded"} for name in ("frozen", "independent")}}
                for person in WRAPPER.PARTICIPANTS],
            "code_hashes": {path.relative_to(WRAPPER.REPO).as_posix(): "same"
                            for path in (r.MANIFEST, r.ACQUISITION)},
            "prior_evidence_hashes": {f"{WRAPPER.FAILED_ROOT}/{name}": "same"
                                     for name in r.PRIOR_EVIDENCE[WRAPPER.FAILED_ROOT]},
            **{key: 0 for key in ("physiological_windows_read", "training_calls", "scoring_calls",
                "trial_parser_calls", "events_changed", "labels_or_times_inferred",
                "direction_or_answer_identities_exported")},
        }
        pinned = {WRAPPER.REPO / WRAPPER.AUDIT, r.BASE / WRAPPER.AUDIT_ROOT / "result.json"}
        hashes = {path: WRAPPER.AUDIT_SHA256 for path in pinned}

        def read(path, *args, **kwargs):
            self.assertEqual(path, WRAPPER.REPO / WRAPPER.AUDIT)
            return json.dumps(audit)

        with mock.patch.object(Path, "open", side_effect=AssertionError("No real files")), \
                mock.patch.object(Path, "read_text", new=read), \
                mock.patch.object(r, "sha256", side_effect=lambda path: hashes.get(path, "same")):
            yield SimpleNamespace(runner=r, audit=audit, hashes=hashes, pinned=pinned,
                                  inventory=inventory, budget=SimpleNamespace(check=lambda: None))

    def test_pinned_complete_audit_is_checked_before_delegating_source_inventory(self):
        with self.admission() as f:
            self.assertEqual(f.runner.source_inventory(f.budget), "generated-inventory")
            f.inventory.assert_called_once_with(f.budget)

    def test_audit_hash_scope_roster_decoder_and_source_binding_fail_before_source(self):
        changes = (
            (lambda a: a.update(session="ses-01"), "attention_audit_identity"),
            (lambda a: a["participants"].reverse(), "attention_audit_complete_agreement"),
            (lambda a: a["participants"].pop(), "attention_audit_complete_agreement"),
            (lambda a: a["participants"][-1].update(full_ordered_decoder_agreement=False),
             "attention_audit_complete_agreement"),
            (lambda a: a["participants"][-1]["decoders"]["independent"].update(status="decoder_refused"),
             "attention_audit_complete_agreement"),
            (lambda a: a.update(training_calls=1), "attention_audit_scope"),
            (lambda a: a["code_hashes"].clear(), "attention_audit_source_binding"),
            (lambda a: a["prior_evidence_hashes"].clear(), "attention_prior_failure_changed"),
        )
        for change, code in changes:
            with self.subTest(code=code), self.admission() as f:
                change(f.audit)
                with self.assertRaisesRegex(RuntimeError, code):
                    f.runner.source_inventory(f.budget)
                f.inventory.assert_not_called()
        with self.admission() as f:
            for path in f.pinned:
                f.hashes[path] = "changed"
                with self.assertRaisesRegex(RuntimeError, "attention_audit_hash"):
                    f.runner.source_inventory(f.budget)
                f.hashes[path] = WRAPPER.AUDIT_SHA256
            f.inventory.assert_not_called()

    @contextlib.contextmanager
    def generated_gate(self, *, disagree=False):
        r, reports, calls = self.runner, {}, []
        events = generated_events()
        # One complete question/answer after intact core phases but absent rest.
        index = next(i for i, (_, code) in enumerate(events) if code == 46 and
                     [c for _, c in events[i + 1:i + 4]] == [17, 61, 42])
        events.pop(index)
        inventory = [(person, Path(f"generated-{person}.bdf"), "generated")
                     for person in WRAPPER.PARTICIPANTS]

        def status(check, *, participant, session):
            self.assertEqual(session, "ses-02")
            calls.append(("frozen", participant))
            return events

        def reference(reader, *, check, participant, session):
            self.assertEqual(session, "ses-02")
            calls.append(("independent", participant))
            return [(sample, 34 if code == 31 else code) for sample, code in events] if (
                disagree and participant == "sub-10") else events

        reader = SimpleNamespace(iter_status_events=status,
            read_window=mock.Mock(side_effect=AssertionError("No physiology")))
        budget = SimpleNamespace(check=lambda: None, storage=lambda: None, gate_active=False)
        with mock.patch.object(Path, "open", side_effect=AssertionError("No real files")), \
                mock.patch.object(r, "source_inventory", return_value=inventory), \
                mock.patch.object(r, "sha256", return_value="generated"), \
                mock.patch.object(r, "write_json", side_effect=lambda p, value: reports.update({p.name: value})), \
                mock.patch("neurodecodekit.datasets.inner_speech.BDFReader", return_value=reader), \
                mock.patch("neurodecodekit.datasets.inner_speech_reference_status.reference_status_events",
                           side_effect=reference), \
                mock.patch("neurodecodekit.experiments.inner_speech_temporal.preflight_condition", return_value={}), \
                mock.patch("neurodecodekit.experiments.inner_speech_temporal.run_condition",
                           side_effect=AssertionError("No fitting")), \
                mock.patch.object(r, "participant_features", side_effect=AssertionError("No physiology")):
            yield SimpleNamespace(inventory=inventory, budget=budget, reports=reports, calls=calls)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_amended_generated_gate_preserves_all_two_thousand_slots_and_no_physiology(self):
        with self.generated_gate() as f:
            qualified = self.runner.qualify_all(f.inventory, f.budget)
            self.assertEqual(len(qualified), 10)
            self.assertEqual(sum(len(item[2]) for item in qualified), 2000)
            gate = f.reports["decoder_gate.json"]
            self.assertEqual(gate["status"], "passed")
            self.assertEqual(len(gate["participants_checked"]), 10)
            self.assertTrue(all(row["full_event_agreement"] for row in gate["participants_checked"]))
            summaries = f.reports["qualification.json"]["participants"]
            self.assertTrue(all(row["attention_after_relax_pairs"] == 1 for row in summaries))
            self.assertEqual(f.reports["qualification.json"]["trials_excluded"], 0)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_last_person_disagreement_blocks_every_physiological_window_and_fit(self):
        with self.generated_gate(disagree=True) as f:
            with self.assertRaisesRegex(RuntimeError, "decoder_disagreement"):
                self.runner.predict(f.budget, {})
            self.assertEqual(f.calls[-1], ("independent", "sub-10"))
            self.assertEqual(len(f.calls), 20)
            self.assertEqual(f.reports["decoder_gate.json"]["status"], "refused")
            self.assertNotIn("qualification.json", f.reports)
            self.assertTrue(f.budget.gate_active)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_unchanged_thirteen_arm_scorer_remains_one_shot(self):
        temporal_tests.TemporalRunnerTests.test_complete_thirteen_arm_one_shot_score_consumes_before_load_and_integrates_primary(self)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_missing_arm_consumes_successor_without_result_or_retry(self):
        temporal_tests.TemporalRunnerTests.test_missing_arm_consumes_attempt_without_publication_or_second_load(self)


if __name__ == "__main__":
    unittest.main()
