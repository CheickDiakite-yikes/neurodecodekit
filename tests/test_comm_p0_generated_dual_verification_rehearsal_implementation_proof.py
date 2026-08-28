from __future__ import annotations

import json
from pathlib import Path

from neurodecodekit.experiments import (
    comm_p0_generated_dual_verification_rehearsal as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / rehearsal.PROOF_PATH


def test_full_wrapper_proof_binds_exact_green_implementation() -> None:
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    assert rehearsal.validate_implementation_proof(proof, root=ROOT) == proof
    assert proof["full_wrapper_implementation_commit"] == (
        "91743f584e5325ef946619869c7aaa477f83fe5a"
    )
    assert proof["full_wrapper_CI_run_id"] == 33188950787
    assert proof["full_wrapper_base_python_job_id"] == 98909173217
    assert proof["full_wrapper_optional_neuro_readers_job_id"] == 98909172856
    assert proof["full_scale_FS3_attempts_before_proof"] == 0
    assert proof["official_qualification_activated"] is False


def test_proof_does_not_activate_execution() -> None:
    plan = rehearsal.plan(ROOT)
    assert plan["full_wrapper_implementation_proof_present"] is False
    assert plan["official_qualification_activated"] is False
    assert plan["scientific_claim_established"] is False
