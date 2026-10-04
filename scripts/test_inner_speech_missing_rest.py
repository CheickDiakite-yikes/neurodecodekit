"""Approved missing-timing successor; reuse the original one-shot lifecycle.

No configurable source, output directory, model setting, or resource increase.
Default is dry-run; predict is one new attempt, never a resume of old evidence.
"""

import importlib.util
from pathlib import Path


def configured_runner():
    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("inner_speech_missing_rest_runner",
                                                repo / "scripts/test_inner_speech.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.EXPERIMENT_ID = "INNER-SPEECH-TEST-1-MR1"
    runner.ALLOW_MISSING_REST = True
    runner.LOCAL = runner.BASE / "inner_speech_test_1_mr1_20260929"
    runner.PLAN = repo / "registries/inner_speech_missing_rest_plan.v0.json"
    runner.FREEZE = repo / "registries/inner_speech_missing_rest_prediction_freeze.v0.json"
    runner.RESULT = repo / "registries/inner_speech_missing_rest_result.v0.json"
    runner.CODE_PATHS += ("scripts/test_inner_speech_missing_rest.py",
                          "scripts/audit_inner_speech_events.py",
                          "registries/inner_speech_missing_rest_plan.v0.json")
    return runner


if __name__ == "__main__":
    raise SystemExit(configured_runner().main())
