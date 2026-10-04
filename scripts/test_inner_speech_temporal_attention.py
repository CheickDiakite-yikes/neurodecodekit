"""One approved attention-timing successor; unchanged session-two temporal study."""

import importlib.util
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
AUDIT = "registries/inner_speech_session2_audit_result.v0.json"
AUDIT_SHA256 = "c07767e099cb88185548245b5cfc64d89bcc75cbde93323b27fc9d3b59a200f5"
AUDIT_ROOT = "inner_speech_session2_event_audit_20261002"
FAILED_ROOT = "inner_speech_temporal_dev_s2_20261002"
PARTICIPANTS = tuple(f"sub-{i:02d}" for i in range(1, 11))


def load_temporal_runner():
    spec = importlib.util.spec_from_file_location("attention_temporal_lifecycle",
        REPO / "scripts/test_inner_speech_temporal.py")
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    return wrapper.configured_runner()


def configured_runner():
    runner = load_temporal_runner()
    runner.EXPERIMENT_ID = "INNER-SPEECH-TEMPORAL-S2-A1"
    runner.LOCAL = runner.BASE / "inner_speech_temporal_s2_a1_20261002"
    runner.PLAN = REPO / "registries/inner_speech_temporal_attention_plan.v0.json"
    runner.FREEZE = REPO / "registries/inner_speech_temporal_attention_prediction_freeze.v0.json"
    runner.RESULT = REPO / "registries/inner_speech_temporal_attention_result.v0.json"
    runner.EVENT_PARSER_KWARGS = {"allow_attention_after_relax": True}
    runner.PRIOR_EVIDENCE[FAILED_ROOT] = ("started.json", "execution_failed.json")
    runner.PRIOR_EVIDENCE[AUDIT_ROOT] = ("started.json", "result.json")
    runner.CODE_PATHS += ("scripts/test_inner_speech_temporal_attention.py",
        "registries/inner_speech_temporal_attention_plan.v0.json", AUDIT,
        "registries/inner_speech_temporal_failure.v0.json")
    original_inventory = runner.source_inventory

    def source_inventory(budget):
        # This is an admission check, not a substitute for the inherited all-ten
        # live decoder-agreement gate that must finish before physiology starts.
        budget.check()
        runner.require(runner.sha256(REPO / AUDIT) == AUDIT_SHA256 and
                       runner.sha256(runner.BASE / AUDIT_ROOT / "result.json") == AUDIT_SHA256,
                       "attention_audit_hash")
        audit = json.loads((REPO / AUDIT).read_text())
        runner.require(audit.get("audit_id") == "INNER-SPEECH-EVENT-AUDIT-S2" and
                       audit.get("status") == "audit_completed" and
                       audit.get("dataset") == "ds003626" and audit.get("version") == "2.1.2" and
                       audit.get("session") == "ses-02" and audit.get("participants_audited") == 10 and
                       audit.get("decoder_agreement_participants") == 10, "attention_audit_identity")
        rows = audit.get("participants", [])
        runner.require(tuple(row.get("participant") for row in rows) == PARTICIPANTS and
                       all(row.get("full_ordered_decoder_agreement") is True and
                           row.get("source_hash_verified_before_and_after") is True and
                           all(row.get("decoders", {}).get(name, {}).get("status") == "decoded"
                               for name in ("frozen", "independent")) for row in rows),
                       "attention_audit_complete_agreement")
        runner.require(all(audit.get(name) == 0 for name in (
            "physiological_windows_read", "training_calls", "scoring_calls", "trial_parser_calls",
            "events_changed", "labels_or_times_inferred", "direction_or_answer_identities_exported")),
            "attention_audit_scope")
        for path in (runner.MANIFEST, runner.ACQUISITION):
            runner.require(audit["code_hashes"].get(path.relative_to(REPO).as_posix()) ==
                           runner.sha256(path), "attention_audit_source_binding")
        for name in runner.PRIOR_EVIDENCE[FAILED_ROOT]:
            relative = f"{FAILED_ROOT}/{name}"
            runner.require(audit["prior_evidence_hashes"].get(relative) ==
                           runner.sha256(runner.BASE / relative), "attention_prior_failure_changed")
        budget.check()
        return original_inventory(budget)

    runner.source_inventory = source_inventory
    return runner


if __name__ == "__main__":
    raise SystemExit(configured_runner().main())
