from __future__ import annotations

import json
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated_two_child_rehearsal as rehearsal


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / rehearsal.PROOF_PATH
DOCUMENT = (
    ROOT
    / "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_TWO_CHILD_"
    "REHEARSAL_IMPLEMENTATION_PROOF.md"
)


def test_exact_green_implementation_proof_validates() -> None:
    value = json.loads(PROOF.read_text(encoding="utf-8"))

    assert rehearsal.validate_implementation_proof(value, root=ROOT) == value
    assert value["implementation_commit"] == (
        "e98330fbb72a4f89b81c154420a01b2ee42918c2"
    )
    assert value["implementation_CI_run_id"] == 33168320870
    assert value["implementation_base_python_job_id"] == 98838987492
    assert value["implementation_optional_neuro_readers_job_id"] == 98838987264


def test_proof_preserves_every_closed_authority_boundary() -> None:
    value = rehearsal.load_implementation_proof(ROOT)

    assert value["rehearsal_execution_authorized_under_Tier_B"] is True
    assert value["official_qualification_activated"] is False
    assert value["official_marker_operations_authorized"] is False
    assert value["real_private_network_device_or_release_authorized"] is False
    assert value["full_scale_rehearsal_attempts_before_proof"] == 0


def test_proof_document_separates_engineering_from_science() -> None:
    text = DOCUMENT.read_text(encoding="utf-8")

    assert "Engineering capability added:" in text
    assert "Scientific claim not established:" in text
    assert "performs no rehearsal" in text
