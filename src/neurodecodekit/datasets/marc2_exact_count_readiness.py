"""Generated-only exact-count readiness primitive for future MARC2 lanes."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import resource
import sys
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR33A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_exact_count_readiness_repair_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_exact_count_readiness_repair_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_exact_count_readiness_repair_contract.v0.json"
)
CONTRACT_SHA256 = "db8e43a81d7f14b5c438bbd39c8dd7e87d8fbe12e9934f9df8598699d1b590b7"
GREEN_REGISTRATION_COMMIT = "23adf07a328824d3b671e8fd8edf3c9b8d1f15ba"
GREEN_REGISTRATION_CI_RUN_ID = 32_634_409_230
GREEN_REGISTRATION_BASE_JOB_ID = 97_181_894_886
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_181_895_045
SAMPLE_COUNT = 3
INTERVAL_SECONDS = 5.0
PATTERNS = ("PPP", "PPF", "PFP", "FPP", "PFF", "FPF", "FFP", "FFF")
REPLAYS = 2
SUCCESS_ROUTE = "MARC2VR33A-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR33A-F{index:02d}" for index in range(1, 7))
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
SAMPLE_KEYS = frozenset(
    {"sequence", "passing", "observed_at_seconds", "available_bytes"}
)


class ExactCountReadinessRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR33A refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR33A refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class ReadinessSample:
    sequence: int
    passing: bool
    observed_at_seconds: float
    available_bytes: int


@dataclass(frozen=True, slots=True)
class ReadinessResult:
    ready: bool
    samples: tuple[ReadinessSample, ReadinessSample, ReadinessSample]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[4], "value is not strict canonical JSON"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR33A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract schema differs"
        )
    return payload


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    registered = load_registered_contract()
    if (
        not isinstance(contract, dict)
        or contract != registered
        or contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "preregistered_artifact_only_generated_only_no_private_access"
    ):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "23adf07a328824d3b671e8fd8edf3c9b8d1f15ba"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_634_409_230
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_181_894_886
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_181_895_045
    ):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _verify_fixed_inputs(
    contract: Mapping[str, Any], root: Path | None = None
) -> int:
    base = root or _repo_root()
    inputs = contract.get("fixed_inputs")
    if not isinstance(inputs, list) or len(inputs) != contract.get(
        "fixed_input_count"
    ):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "fixed input registry differs"
        )
    total = 0
    for item in inputs:
        if not isinstance(item, dict) or set(item) != {
            "role",
            "path",
            "bytes",
            "sha256",
        }:
            raise ExactCountReadinessRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            payload = (base / item["path"]).read_bytes()
        except (OSError, TypeError) as exc:
            raise ExactCountReadinessRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != item["bytes"] or _sha256_bytes(payload) != item["sha256"]:
            raise ExactCountReadinessRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[0], "one-thread environment is not exact"
        )


def _validated_sample(value: Any, expected_sequence: int) -> ReadinessSample:
    if not isinstance(value, dict) or set(value) != SAMPLE_KEYS:
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[1], "readiness sample mapping differs"
        )
    _canonical_json_bytes(value)
    sequence = value["sequence"]
    passing = value["passing"]
    observed = value["observed_at_seconds"]
    available = value["available_bytes"]
    if (
        isinstance(sequence, bool)
        or not isinstance(sequence, int)
        or sequence != expected_sequence
    ):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[1], "readiness sequence differs"
        )
    if not isinstance(passing, bool):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[1], "readiness passing value is not Boolean"
        )
    if (
        isinstance(observed, bool)
        or not isinstance(observed, (int, float))
        or not math.isfinite(float(observed))
        or float(observed) < 0.0
    ):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[1], "readiness observation time differs"
        )
    if (
        isinstance(available, bool)
        or not isinstance(available, int)
        or available < 0
    ):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[1], "readiness available-byte value differs"
        )
    return ReadinessSample(
        sequence=sequence,
        passing=passing,
        observed_at_seconds=float(observed),
        available_bytes=available,
    )


def collect_exact_readiness(
    sample_provider: Callable[[int], Mapping[str, Any]],
    sleeper: Callable[[float], None],
) -> ReadinessResult:
    """Collect exactly three generated samples with two fixed sleeps."""

    if not callable(sample_provider) or not callable(sleeper):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[1], "readiness callbacks are not callable"
        )
    collected: list[ReadinessSample] = []
    for sequence in (1, 2, 3):
        try:
            raw_sample = sample_provider(sequence)
        except Exception as exc:
            raise ExactCountReadinessRefusal(
                REFUSAL_ROUTES[2], "readiness provider refused"
            ) from exc
        collected.append(_validated_sample(raw_sample, sequence))
        if sequence < SAMPLE_COUNT:
            try:
                sleeper(INTERVAL_SECONDS)
            except Exception as exc:
                raise ExactCountReadinessRefusal(
                    REFUSAL_ROUTES[2], "readiness sleeper refused"
                ) from exc
    samples = (collected[0], collected[1], collected[2])
    return ReadinessResult(
        ready=all(sample.passing for sample in samples),
        samples=samples,
    )


def _sample_payload(sequence: int, passing: bool) -> dict[str, Any]:
    return {
        "sequence": sequence,
        "passing": passing,
        "observed_at_seconds": float(sequence * 5),
        "available_bytes": 2_147_483_648 + sequence,
    }


def _build_pattern(pattern: str) -> list[dict[str, Any]]:
    if pattern not in PATTERNS:
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[3], "generated readiness pattern differs"
        )
    return [
        _sample_payload(index, marker == "P")
        for index, marker in enumerate(pattern, start=1)
    ]


def _collect_pattern(
    pattern: str,
) -> tuple[ReadinessResult, int, int, int, bool]:
    source = _build_pattern(pattern)
    before = _canonical_json_bytes(source)
    provider_calls = 0
    sleeper_calls = 0
    generated_input_bytes = 0

    def provider(sequence: int) -> Mapping[str, Any]:
        nonlocal provider_calls, generated_input_bytes
        provider_calls += 1
        payload = source[sequence - 1]
        generated_input_bytes += len(_canonical_json_bytes(payload))
        return payload

    def sleeper(interval: float) -> None:
        nonlocal sleeper_calls
        if interval != INTERVAL_SECONDS:
            raise ValueError("generated sleeper interval differs")
        sleeper_calls += 1

    result = collect_exact_readiness(provider, sleeper)
    unchanged = _canonical_json_bytes(source) == before
    return result, provider_calls, sleeper_calls, generated_input_bytes, unchanged


def _result_mapping(result: ReadinessResult) -> dict[str, Any]:
    return {
        "ready": result.ready,
        "samples": [asdict(sample) for sample in result.samples],
    }


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    payload = _canonical_json_bytes(report)
    forbidden = {
        "path",
        "source_path",
        "private_path",
        "participant",
        "subject",
        "target",
        "label",
        "prediction",
        "score",
        "neural_signal",
    }

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if key in forbidden:
                    raise ExactCountReadinessRefusal(
                        REFUSAL_ROUTES[4], "aggregate report contains private field"
                    )
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(report)
    if len(payload) > 1_048_576:
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[4], "aggregate report exceeds output cap"
        )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    aggregate_output_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_limits"]
    if (
        runtime_seconds < 0
        or runtime_seconds > caps["runtime_seconds"]
        or peak_rss_bytes < 0
        or peak_rss_bytes >= caps["peak_RSS_bytes_exclusive"]
        or generated_input_bytes > caps["generated_input_bytes"]
        or aggregate_output_bytes > caps["aggregate_output_bytes"]
    ):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(action: Callable[[], Any]) -> str:
    try:
        action()
    except ExactCountReadinessRefusal as exc:
        return exc.route
    raise ExactCountReadinessRefusal(
        REFUSAL_ROUTES[4], "direct refusal unexpectedly passed"
    )


def _run_direct_refusals(contract: Mapping[str, Any]) -> int:
    routes: list[str] = []
    for index, key in enumerate(contract):
        changed = copy.deepcopy(dict(contract))
        changed[key] = f"mutated-{index}"
        routes.append(_expect_refusal(lambda item=changed: _verify_contract_mapping(item)))
    for key in THREAD_ENVIRONMENT:
        changed = dict(THREAD_ENVIRONMENT)
        changed[key] = "2"
        routes.append(
            _expect_refusal(lambda item=changed: _validate_thread_environment(item))
        )
        changed = dict(THREAD_ENVIRONMENT)
        del changed[key]
        routes.append(
            _expect_refusal(lambda item=changed: _validate_thread_environment(item))
        )
    malformed = (
        None,
        [],
        {},
        {"sequence": 1},
        {**_sample_payload(1, True), "extra": "x"},
        {**_sample_payload(1, True), "sequence": 2},
        {**_sample_payload(1, True), "sequence": True},
        {**_sample_payload(1, True), "passing": 1},
        {**_sample_payload(1, True), "observed_at_seconds": float("nan")},
        {**_sample_payload(1, True), "observed_at_seconds": -1.0},
        {**_sample_payload(1, True), "available_bytes": -1},
        {**_sample_payload(1, True), "available_bytes": True},
        {**_sample_payload(1, True), "available_bytes": {"not": "an integer"}},
    )
    for value in malformed:
        routes.append(_expect_refusal(lambda item=value: _validated_sample(item, 1)))
    routes.append(_expect_refusal(lambda: collect_exact_readiness(None, lambda _: None)))
    routes.append(_expect_refusal(lambda: collect_exact_readiness(lambda _: {}, None)))

    def provider_error(_sequence: int) -> Mapping[str, Any]:
        raise RuntimeError("generated provider error")

    def sleeper_error(_interval: float) -> None:
        raise RuntimeError("generated sleeper error")

    routes.append(
        _expect_refusal(lambda: collect_exact_readiness(provider_error, lambda _: None))
    )
    routes.append(
        _expect_refusal(
            lambda: collect_exact_readiness(
                lambda sequence: _sample_payload(sequence, True), sleeper_error
            )
        )
    )
    for pattern in ("", "PP", "PPPP", "XYZ", "private", "execute"):
        routes.append(_expect_refusal(lambda value=pattern: _build_pattern(value)))
    for field in (
        "path",
        "source_path",
        "private_path",
        "participant",
        "subject",
        "target",
        "label",
        "prediction",
        "score",
        "neural_signal",
    ):
        routes.append(
            _expect_refusal(lambda key=field: _assert_public_report_safe({key: "x"}))
        )
    caps = contract["resource_limits"]
    for values in (
        (caps["runtime_seconds"] + 1.0, 1, 1, 1),
        (1.0, caps["peak_RSS_bytes_exclusive"], 1, 1),
        (1.0, 1, caps["generated_input_bytes"] + 1, 1),
        (1.0, 1, 1, caps["aggregate_output_bytes"] + 1),
    ):
        routes.append(
            _expect_refusal(
                lambda item=values: _assert_resources(
                    runtime_seconds=item[0],
                    peak_rss_bytes=item[1],
                    generated_input_bytes=item[2],
                    aggregate_output_bytes=item[3],
                    contract=contract,
                )
            )
        )
    if len(routes) < contract["generated_matrix"]["minimum_direct_refusals"]:
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[4], "direct refusal coverage is incomplete"
        )
    return len(routes)


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _zero_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "readiness_or_consumed_state_operations": 0,
        "archive_header_or_member_operations": 0,
        "signal_event_target_or_label_operations": 0,
        "model_training_inference_prediction_or_score_operations": 0,
        "network_download_provider_or_language_model_operations": 0,
        "stream_device_or_hardware_operations": 0,
        "FW2_or_CIL1_operations": 0,
        "other_project_operations": 0,
        "release_or_publication_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the exact 16-path generated-only VR33A qualification."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    _validate_thread_environment(environment)
    direct_refusals = _run_direct_refusals(registered)

    ready_counts: Counter[bool] = Counter()
    provider_calls = 0
    sleeper_calls = 0
    generated_input_bytes = 0
    source_mutations = 0
    replay_signatures: list[list[dict[str, Any]]] = []
    for _replay in range(REPLAYS):
        signature: list[dict[str, Any]] = []
        for pattern in PATTERNS:
            result, providers, sleepers, payload_bytes, unchanged = _collect_pattern(
                pattern
            )
            expected_ready = pattern == "PPP"
            if result.ready != expected_ready:
                raise ExactCountReadinessRefusal(
                    REFUSAL_ROUTES[3], "generated readiness result differs"
                )
            if tuple(sample.sequence for sample in result.samples) != (1, 2, 3):
                raise ExactCountReadinessRefusal(
                    REFUSAL_ROUTES[3], "generated readiness sequence differs"
                )
            provider_calls += providers
            sleeper_calls += sleepers
            generated_input_bytes += payload_bytes
            source_mutations += int(not unchanged)
            ready_counts[result.ready] += 1
            signature.append({"pattern": pattern, **_result_mapping(result)})
        replay_signatures.append(signature)

    matrix = registered["generated_matrix"]
    if (
        provider_calls != matrix["required_provider_calls"]
        or sleeper_calls != matrix["required_sleeper_calls"]
        or provider_calls != matrix["required_returned_samples"]
        or ready_counts != Counter({False: 14, True: 2})
        or replay_signatures[0] != replay_signatures[1]
        or source_mutations != 0
    ):
        raise ExactCountReadinessRefusal(
            REFUSAL_ROUTES[3], "generated matrix counts or replay differ"
        )

    runtime = clock() - started
    rss = peak_rss()
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTE,
        "status": "generated_exact_count_readiness_qualified",
        "proof": {
            "registration_commit": GREEN_REGISTRATION_COMMIT,
            "registration_CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "registration_base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "registration_optional_neuro_job_id": (
                GREEN_REGISTRATION_OPTIONAL_JOB_ID
            ),
            "contract_sha256": CONTRACT_SHA256,
        },
        "matrix": {
            "patterns": list(PATTERNS),
            "replays": REPLAYS,
            "paths": len(PATTERNS) * REPLAYS,
            "provider_calls": provider_calls,
            "sleeper_calls": sleeper_calls,
            "returned_samples": provider_calls,
            "ready_paths": ready_counts[True],
            "not_ready_paths": ready_counts[False],
            "ready_patterns": ["PPP"],
            "exact_replays_match": True,
            "source_mutations_after_call": source_mutations,
            "direct_refusals_passed": direct_refusals,
            "replay_digest": _sha256_bytes(
                _canonical_json_bytes(replay_signatures)
            ),
        },
        "measurements": {
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": generated_input_bytes,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "retained_output_bytes": 0,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": _zero_counters(),
        "warnings": [
            "artifact_only_and_generated_only",
            "no_private_executor",
            "does_not_repair_or_reinterpret_consumed_VR32P",
            "future_private_adoption_requires_a_new_Tier_C_packet",
            "no_real_cohort_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "private_readiness_state",
            "private_source_or_consumed_output",
            "real_target_free_cohort",
            "archive_member_neural_signal_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "exact finite readiness sampling for future proof-gated wrappers"
            ),
            "scientific_claim_not_established": (
                "No neural payload target model prediction or score was accessed."
            ),
        },
    }
    output_bytes = 0
    for _pass in range(3):
        report["measurements"]["aggregate_output_bytes"] = output_bytes
        output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    _assert_public_report_safe(report)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=rss,
        generated_input_bytes=generated_input_bytes,
        aggregate_output_bytes=output_bytes,
        contract=registered,
    )
    return report


def build_plan() -> dict[str, Any]:
    """Return the frozen generated-only plan with no private authority."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    return {
        "schema_name": "neurodecodekit.marc2_exact_count_readiness_repair_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_only_implementation_eligible",
        "fixed_input_bytes": _verify_fixed_inputs(contract),
        "sample_count": SAMPLE_COUNT,
        "interval_seconds": INTERVAL_SECONDS,
        "patterns": len(PATTERNS),
        "replays": REPLAYS,
        "paths": len(PATTERNS) * REPLAYS,
        "provider_calls": 48,
        "sleeper_calls": 32,
        "minimum_direct_refusals": 40,
        "private_executor_available": False,
        "FW2_or_CIL1_authorized": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 exact-count readiness repair."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = build_plan() if args.command == "plan" else qualify_generated()
    except ExactCountReadinessRefusal as exc:
        print(
            json.dumps(
                {"lane_id": LANE_ID, "route": exc.route, "status": "refused"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
