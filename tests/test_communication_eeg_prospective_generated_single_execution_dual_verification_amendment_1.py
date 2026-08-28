import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / (
    "communication_eeg_prospective_generated_single_execution_"
    "dual_verification_amendment_1.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_SINGLE_EXECUTION_"
    "DUAL_VERIFICATION_AMENDMENT_1.md"
)


def _record() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_amendment_binds_exact_green_parent_surface() -> None:
    record = _record()
    rows = record["bound_parent_artifacts"]
    observed_bytes = 0
    for row in rows:
        payload = (ROOT / row["path"]).read_bytes()
        observed_bytes += len(payload)
        assert row["bytes"] == len(payload)
        assert row["sha256"] == hashlib.sha256(payload).hexdigest()
    assert record["bound_parent_summary"]["count"] == 9
    assert record["bound_parent_summary"]["bytes"] == observed_bytes == 136817
    assert record["bound_parent_summary"]["prior_proof_closeout_commit"] == (
        "ccabfafb411e219292b103ce2327568112056286"
    )


def test_amendment_resolves_verifier_semantics_without_execution() -> None:
    record = _record()
    schedule = record["corrected_verifier_schedule"]
    transport = record["target_transport_semantics"]
    identity = record["identity_and_filesystem_corrections"]

    assert schedule["verifier_invocations"] == 1
    assert schedule["prediction_stream_traversals"] == 2
    assert schedule["prediction_rows"] == 91392
    assert schedule["prediction_sets"] == 1428
    assert schedule["logical_cohort_target_deliveries"] == 2
    assert transport["physical_no_follow_descriptors"] == 1
    assert transport["exact_logical_partitions"] == [
        "discovery",
        "independent_replication",
    ]
    assert identity["symlink_following_is_file_preflight_allowed"] is False
    assert identity["active_socket_guard_required"] is True
    assert all(value == 0 for value in record["operation_counters"].values())
    assert record["authority"]["FS3_execution_authorized_now"] is False
    assert not any(record["claim_boundary"].values())


def test_amendment_document_separates_engineering_from_science() -> None:
    text = DOCUMENT.read_text(encoding="utf-8")

    assert "Engineering capability added:" in text
    assert "Scientific claim not established:" in text
    assert "No full FS3 run may begin" in text
