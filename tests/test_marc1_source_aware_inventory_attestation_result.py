import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc1_source_aware_inventory_attestation_result.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_result() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_result_identity_route_and_consumed_status() -> None:
    result = load_result()
    assert result["schema_name"] == (
        "neurodecodekit.marc1_source_aware_inventory_attestation_result"
    )
    assert result["schema_version"] == "0.1.0"
    assert result["lane_id"] == "MARC1-SA1"
    assert result["route"] == "MARC1SA-G1"
    assert result["status"] == "passed_registered_generated_closeout_consumed"


def test_green_implementation_preceded_the_only_closeout() -> None:
    result = load_result()
    proof = result["green_implementation_proof"]
    assert proof["commit"] == "feb3b839e879d2a9edcdcfe664c68b3c4ba236d6"
    assert proof["CI_run_id"] == 31_619_037_335
    assert proof["base_python_job_id"] == 94_188_922_905
    assert proof["optional_neuro_job_id"] == 94_188_922_771
    assert proof["both_required_jobs_green"] is True
    assert result["registered_execution"]["runs"] == 1


def test_every_bound_artifact_is_current() -> None:
    result = load_result()
    for binding in result["artifact_bindings"].values():
        path = ROOT / binding["path"]
        assert path.stat().st_size == binding["bytes"]
        assert sha256_file(path) == binding["sha256"]


def test_all_families_predicates_hash_domains_refusals_and_gates_passed() -> None:
    result = load_result()
    execution = result["registered_execution"]
    assert execution["semantic_families_passed"] == execution["semantic_families"] == 6
    assert execution["predicate_fields"] == 21
    assert execution["identity_domains"] == 7
    assert execution["refusal_cases_passed"] == execution["refusal_cases"] == 52
    assert execution["acceptance_gates_passed"] == execution["acceptance_gates"] == 25
    assert len(result["family_routes"]) == 6
    assert len(result["acceptance_gate_names"]) == 25


def test_family_routes_preserve_optional_md5_and_drift_semantics() -> None:
    routes = load_result()["family_routes"]
    assert routes["documented_public_core_exact"] == "MARC1SA-R2"
    assert routes["observed_extension_exact"] == "MARC1SA-R1"
    assert routes["partial_optional_extension_exact"] == "MARC1SA-R2"
    assert routes["single_historical_drift"] == "MARC1SA-R3"
    assert routes["multiple_historical_drifts"] == "MARC1SA-R3"
    assert routes["unknown_non_target_extension"] == "MARC1SA-R4"


def test_output_receipt_is_bounded_private_and_removed() -> None:
    output = load_result()["output_receipt"]
    assert output["private_output_bytes"] == 95_392
    assert output["public_output_bytes"] == 14_197
    assert output["combined_output_bytes"] == 109_589
    assert output["private_mode"] == "0600"
    assert output["public_mode"] == "0600"
    assert output["public_report_inspections"] == 1
    assert output["temporary_outputs_removed"] is True
    assert output["caller_parent_cleanup_status"] == 0
    assert output["retained_output_files"] == 0
    assert output["public_report_sha256"] is None


def test_resource_measurements_pass_frozen_caps() -> None:
    result = load_result()
    measurements = result["measurements"]
    caps = result["resource_caps"]
    assert measurements["generated_input_bytes"] == 732_811
    assert measurements["generated_output_bytes"] == 109_589
    assert measurements["runtime_seconds"] == 0.053358083
    assert measurements["reported_peak_RSS_bytes"] == 27_885_568
    assert measurements["external_maximum_RSS_bytes"] == 27_983_872
    assert measurements["runtime_seconds"] < caps["runtime_seconds"]
    assert measurements["reported_peak_RSS_bytes"] < caps["peak_RSS_bytes"]
    assert measurements["generated_output_bytes"] < caps["combined_output_bytes"]
    assert (
        measurements["CPU_threads"],
        measurements["workers"],
        measurements["numerical_jobs"],
    ) == (1, 1, 1)


def test_every_real_neural_model_score_retry_and_claim_counter_is_zero() -> None:
    result = load_result()
    assert result["access_counters"]
    assert all(value == 0 for value in result["access_counters"].values())
    measurements = result["measurements"]
    assert measurements["raw_data_reads"] == 0
    assert measurements["real_cache_reads"] == 0
    assert measurements["model_runs"] == 0
    assert measurements["training_runs"] == 0


def test_result_is_aggregate_only_and_exposes_no_private_identity() -> None:
    serialized = json.dumps(load_result(), sort_keys=True)
    for forbidden in (
        "storage_location",
        "download_url",
        "sub-01.zip",
        ".codex_work",
        "/Users/",
        "target_text",
    ):
        assert forbidden not in serialized


def test_claim_boundary_and_same_path_are_explicit() -> None:
    result = load_result()
    boundary = result["claim_boundary"]
    path = result["research_path"]
    assert boundary["scientific_claim_established"] is False
    assert "no live metadata" in boundary["scientific_claim_not_established"].lower()
    assert path["same_thought_to_text_path"] is True
    assert path["is_pivot"] is False
    assert path["held_out_language_decoding_still_required"] is True


def test_closeout_is_consumed_and_future_real_work_remains_closed() -> None:
    result = load_result()
    disposition = result["consumption_and_next_gate"]
    assert disposition["registered_generated_closeout_consumed"] is True
    assert disposition["retries"] == 0
    assert disposition["reruns"] == 0
    assert disposition["live_wrapper_authorized_now"] is False
    assert disposition["public_metadata_request_authorized_now"] is False
    assert disposition["payload_authorized_now"] is False
    assert disposition["result_must_be_remotely_green_before_Tier_C_request"] is True
