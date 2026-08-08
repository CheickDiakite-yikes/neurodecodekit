"""Deterministic synthetic contact-aware ear-channel adapter fixtures."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import math
import shutil
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


SCHEMA_NAME = "neurodecodekit.contact_aware_ear_channel_fixture"
SCHEMA_VERSION = "0.1.0"
SIDECAR_SCHEMA_NAME = "neurodecodekit.contact_aware_ear_channel_sidecar"
PROOF_POSTURE = "synthetic_post_acquisition_mask_and_weight_mechanics_only"
CONTRACT_RELATIVE_PATH = Path("registries/contact_aware_ear_channel_contract.v0.json")
REGISTERED_CONTRACT_SHA256 = "9a18c1ec1d7b234ffb302add9ea974d0cdf412ff722fc1fcc44445b0201882cc"
REGISTERED_CONTRACT_BYTES = 15_789
MAX_CONTRACT_BYTES = 1024 * 1024
MAX_SIDECAR_BYTES = 1024 * 1024
DEFAULT_MAX_OUTPUT_BYTES = 4 * 1024 * 1024
MINIMUM_FREE_DISK_BYTES = 1024 * 1024 * 1024
PAYLOAD_NAME = "ear_fixture.npz"
SIDECAR_NAME = "metadata.json"

ITEM_COUNT = 48
CHANNEL_COUNT = 16
SAMPLES = 256
SAMPLING_RATE_HZ = 128.0
CHANNEL_NAMES = tuple(
    [f"ear-L{index:02d}" for index in range(8)]
    + [f"ear-R{index:02d}" for index in range(8)]
)
EAR_SIDES = tuple(["L"] * 8 + ["R"] * 8)
RING_INDICES = tuple(range(8)) + tuple(range(8))
SCENARIO_IDS = (
    "all_contacts_observed",
    "left_partial_contact_loss",
    "right_partial_contact_loss",
    "bilateral_sparse_contact",
    "unknown_contact_quality",
    "line_noise_contamination",
    "common_mode_motion_contamination",
    "mixed_dropout_noise_contact",
)
REFUSAL_IDS = (
    "duplicate_or_missing_channel_identity",
    "unknown_or_mismatched_ear_side",
    "payload_sidecar_source_order_drift",
    "nonfinite_sample_marked_observed",
    "absent_channel_marked_selected",
    "invalid_or_unknown_contact_marked_selected",
    "over_noise_threshold_channel_marked_selected",
    "bilateral_minimum_not_met_but_selection_emitted",
    "selected_channel_count_above_side_cap",
    "nonzero_weight_outside_selected_mask",
    "left_or_right_weight_total_mismatch",
    "zero_filled_missing_value_marked_measured",
    "invented_impedance_or_contact_provenance",
    "measured_geometry_claim_from_synthetic_nominal_fields",
    "forbidden_target_identity_or_outcome_field",
    "post_event_or_right_context_dependency",
)
ARRAY_MEMBERS = (
    "adapted_observed_mask",
    "adapted_signal",
    "channel_names",
    "channel_present_mask",
    "contact_score",
    "contact_score_valid_mask",
    "ear_sides",
    "eligible_mask",
    "item_ids",
    "mask_reasons",
    "metadata",
    "noise_score",
    "observed_mask",
    "ring_indices",
    "scenario_ids",
    "selected_mask",
    "selection_status",
    "selection_weight",
    "signals",
    "time_sec",
)
HASHED_ARRAY_MEMBERS = tuple(name for name in ARRAY_MEMBERS if name != "metadata")
METADATA_FIELDS = {
    "schema",
    "proof_posture",
    "target_free",
    "identity",
    "array_shapes",
    "array_dtypes",
    "array_sha256",
    "scenario_counts",
    "selection_policy",
    "mask_semantics",
    "selection_diagnostics",
    "provenance_hashes",
    "refusal_ids",
    "causality",
    "access_counters",
    "warnings",
    "unavailable_fields",
    "claim_boundary",
}
FORBIDDEN_KEY_FRAGMENTS = (
    "target_text",
    "reference_text",
    "intended_text",
    "label_value",
    "prediction_value",
    "participant_id",
    "subject_id",
    "device_id",
    "protected_path",
)
ACCESS_COUNTERS = {
    "synthetic_payload_generations": 1,
    "target_blind_contact_policy_item_runs": ITEM_COUNT,
    "raw_data_reads": 0,
    "real_cache_reads": 0,
    "real_or_protected_data_reads": 0,
    "public_EEG_payload_reads": 0,
    "target_or_label_value_reads": 0,
    "adapter_backend_imports": 0,
    "feature_extraction_runs": 0,
    "parameter_update_runs": 0,
    "model_inference_runs": 0,
    "training_runs": 0,
    "scoring_or_selection_by_outcome_runs": 0,
    "network_calls": 0,
    "provider_calls": 0,
    "hardware_or_device_operations": 0,
    "scientific_claim_upgrades": 0,
}


@dataclass(frozen=True)
class LoadedContactAwareEarFixture:
    """One fully validated synthetic ear-channel fixture."""

    arrays: Mapping[str, Any]
    metadata: Mapping[str, Any]
    sidecar: Mapping[str, Any]
    opened_members: tuple[str, ...]


def load_registered_contact_aware_ear_contract(
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load the exact registered work-order-5 contract."""

    source = Path(path) if path is not None else _repo_root() / CONTRACT_RELATIVE_PATH
    with source.open("rb") as handle:
        payload = handle.read(MAX_CONTRACT_BYTES + 1)
    if len(payload) > MAX_CONTRACT_BYTES:
        raise ValueError("contact-aware ear-channel contract exceeds 1 MiB")
    if hashlib.sha256(payload).hexdigest() != REGISTERED_CONTRACT_SHA256:
        raise ValueError("contact-aware ear-channel contract SHA-256 mismatch")
    if len(payload) != REGISTERED_CONTRACT_BYTES:
        raise ValueError("contact-aware ear-channel contract byte count mismatch")
    contract = json.loads(payload.decode("utf-8"))
    if contract.get("schema_name") != "neurodecodekit.contact_aware_ear_channel_contract":
        raise ValueError("contact-aware ear-channel contract schema mismatch")
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("contact-aware ear-channel contract version mismatch")
    if contract.get("status") != (
        "preregistered_tier_B_synthetic_only_not_implemented_not_executed"
    ):
        raise ValueError("contact-aware ear-channel contract status mismatch")
    _validate_contract_identity(contract)
    return contract


def apply_fixed_contact_policy(
    *,
    channel_present_mask: Any,
    contact_score: Any,
    contact_score_valid_mask: Any,
    noise_score: Any,
    observed_mask: Any,
    ear_sides: Any,
    decision_sample: int = SAMPLES,
) -> tuple[Any, Any, Any, Any]:
    """Apply the fixed target-blind bilateral policy to pre-decision samples."""

    np = _require_numpy()
    present = np.asarray(channel_present_mask, dtype="bool")
    contact = np.asarray(contact_score, dtype="float32")
    contact_valid = np.asarray(contact_score_valid_mask, dtype="bool")
    noise = np.asarray(noise_score, dtype="float32")
    observed = np.asarray(observed_mask, dtype="bool")
    sides = np.asarray(ear_sides)
    if present.shape != (ITEM_COUNT, CHANNEL_COUNT):
        raise ValueError("contact policy channel-present shape mismatch")
    for value, name in (
        (contact, "contact-score"),
        (contact_valid, "contact-valid"),
        (noise, "noise-score"),
    ):
        if value.shape != present.shape:
            raise ValueError(f"contact policy {name} shape mismatch")
    if observed.ndim != 3 or observed.shape[:2] != present.shape:
        raise ValueError("contact policy observed-mask shape mismatch")
    if decision_sample <= 0 or decision_sample > observed.shape[2]:
        raise ValueError("contact policy decision sample is outside the observed window")
    if sides.shape != (CHANNEL_COUNT,) or tuple(sides.tolist()) != EAR_SIDES:
        raise ValueError("contact policy ear-side identity mismatch")

    observed_fraction = observed[:, :, :decision_sample].mean(axis=2, dtype="float64")
    eligible = (
        present
        & contact_valid
        & np.isfinite(contact)
        & (contact >= 0.6)
        & np.isfinite(noise)
        & (noise <= 0.4)
        & (observed_fraction >= 0.95)
    )
    selected = np.zeros_like(eligible)
    weights = np.zeros(present.shape, dtype="float32")
    statuses: list[str] = []
    rank_score = 0.6 * np.nan_to_num(contact, nan=-1.0) + 0.4 * (1.0 - noise)
    for item_index in range(ITEM_COUNT):
        ranked: dict[str, list[int]] = {}
        for side in ("L", "R"):
            candidates = [
                channel_index
                for channel_index in range(CHANNEL_COUNT)
                if sides[channel_index] == side and eligible[item_index, channel_index]
            ]
            candidates.sort(key=lambda index: (-float(rank_score[item_index, index]), index))
            ranked[side] = candidates[:4]
        if len(ranked["L"]) < 2 or len(ranked["R"]) < 2:
            statuses.append("insufficient_bilateral_contact")
            continue
        statuses.append("ok")
        for side in ("L", "R"):
            chosen = ranked[side]
            side_weight = np.float32(0.5 / len(chosen))
            selected[item_index, chosen] = True
            weights[item_index, chosen] = side_weight
    return eligible, selected, weights, np.asarray(statuses, dtype="U32")


def make_contact_aware_ear_arrays(
    *,
    contract_path: str | Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate the exact target-free synthetic fixture and adapter outputs."""

    contract = load_registered_contact_aware_ear_contract(contract_path)
    np = _require_numpy()
    rng = np.random.default_rng(5505)
    time_sec = (np.arange(SAMPLES, dtype="float64") - SAMPLES) / SAMPLING_RATE_HZ
    signals = rng.normal(0.0, 0.012, size=(ITEM_COUNT, CHANNEL_COUNT, SAMPLES)).astype(
        "float32"
    )
    phase = np.asarray([index * 0.17 for index in range(CHANNEL_COUNT)], dtype="float64")
    base_wave = 0.008 * np.sin(
        2.0 * math.pi * 10.0 * time_sec[None, None, :] + phase[None, :, None]
    )
    signals += base_wave.astype("float32")

    observed_mask = np.ones(signals.shape, dtype="bool")
    channel_present_mask = np.ones((ITEM_COUNT, CHANNEL_COUNT), dtype="bool")
    contact_score_valid_mask = np.ones((ITEM_COUNT, CHANNEL_COUNT), dtype="bool")
    base_contact = np.asarray(
        [0.92, 0.90, 0.88, 0.86, 0.84, 0.82, 0.80, 0.78] * 2,
        dtype="float32",
    )
    base_noise = np.asarray(
        [0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22, 0.24] * 2,
        dtype="float32",
    )
    contact_score = np.repeat(base_contact[None, :], ITEM_COUNT, axis=0)
    noise_score = np.repeat(base_noise[None, :], ITEM_COUNT, axis=0)
    item_ids: list[str] = []
    scenario_rows: list[str] = []

    for scenario_index, scenario_id in enumerate(SCENARIO_IDS):
        for replicate in range(6):
            row = scenario_index * 6 + replicate
            item_ids.append(f"ear-s{scenario_index:02d}-r{replicate:02d}")
            scenario_rows.append(scenario_id)
            if scenario_id == "left_partial_contact_loss":
                _mark_absent(signals, observed_mask, channel_present_mask, contact_score, contact_score_valid_mask, row, (0, 1))
                _mark_dropout(signals, observed_mask, row, 2)
            elif scenario_id == "right_partial_contact_loss":
                _mark_absent(signals, observed_mask, channel_present_mask, contact_score, contact_score_valid_mask, row, (8, 9))
                _mark_dropout(signals, observed_mask, row, 10)
            elif scenario_id == "bilateral_sparse_contact":
                absent = tuple(index for index in range(CHANNEL_COUNT) if index not in {2, 3, 10, 11})
                _mark_absent(signals, observed_mask, channel_present_mask, contact_score, contact_score_valid_mask, row, absent)
            elif scenario_id == "unknown_contact_quality":
                contact_score_valid_mask[row, :8] = False
                contact_score[row, :8] = np.nan
            elif scenario_id == "line_noise_contamination":
                contaminated = (1, 2, 9, 10)
                noise_score[row, list(contaminated)] = 0.8
                line = (0.07 * np.sin(2.0 * math.pi * 50.0 * time_sec)).astype("float32")
                signals[row, list(contaminated), :] += line[None, :]
            elif scenario_id == "common_mode_motion_contamination":
                contaminated = (0, 1, 8, 9)
                noise_score[row, list(contaminated)] = 0.75
                motion = (0.09 * np.sin(2.0 * math.pi * 1.25 * time_sec)).astype("float32")
                signals[row, list(contaminated), :] += motion[None, :]
            elif scenario_id == "mixed_dropout_noise_contact":
                _mark_absent(signals, observed_mask, channel_present_mask, contact_score, contact_score_valid_mask, row, (0, 8))
                contact_score_valid_mask[row, [1, 9]] = False
                contact_score[row, [1, 9]] = np.nan
                noise_score[row, [2, 10]] = 0.85
                _mark_dropout(signals, observed_mask, row, 3)
                _mark_dropout(signals, observed_mask, row, 11)
                contact_score[row, [4, 12]] = 0.4

    eligible_mask, selected_mask, selection_weight, selection_status = (
        apply_fixed_contact_policy(
            channel_present_mask=channel_present_mask,
            contact_score=contact_score,
            contact_score_valid_mask=contact_score_valid_mask,
            noise_score=noise_score,
            observed_mask=observed_mask,
            ear_sides=np.asarray(EAR_SIDES, dtype="U1"),
        )
    )
    adapted_observed_mask = observed_mask & selected_mask[:, :, None]
    adapted_signal = np.where(
        adapted_observed_mask,
        signals * selection_weight[:, :, None],
        0.0,
    ).astype("float32")
    mask_reasons = _mask_reasons(
        np,
        channel_present_mask=channel_present_mask,
        contact_score=contact_score,
        contact_score_valid_mask=contact_score_valid_mask,
        noise_score=noise_score,
        observed_mask=observed_mask,
        eligible_mask=eligible_mask,
        selected_mask=selected_mask,
    )
    arrays: dict[str, Any] = {
        "signals": signals,
        "observed_mask": observed_mask,
        "channel_present_mask": channel_present_mask,
        "contact_score": contact_score,
        "contact_score_valid_mask": contact_score_valid_mask,
        "noise_score": noise_score,
        "eligible_mask": eligible_mask,
        "selected_mask": selected_mask,
        "selection_weight": selection_weight,
        "adapted_signal": adapted_signal,
        "adapted_observed_mask": adapted_observed_mask,
        "time_sec": time_sec,
        "channel_names": np.asarray(CHANNEL_NAMES, dtype="U8"),
        "ear_sides": np.asarray(EAR_SIDES, dtype="U1"),
        "ring_indices": np.asarray(RING_INDICES, dtype="int8"),
        "item_ids": np.asarray(item_ids, dtype="U20"),
        "scenario_ids": np.asarray(scenario_rows, dtype="U40"),
        "selection_status": selection_status,
        "mask_reasons": mask_reasons,
    }
    metadata = _build_metadata(np, arrays=arrays, contract=contract)
    arrays["metadata"] = np.asarray(_canonical_json(metadata))
    validate_contact_aware_ear_arrays(arrays, expected_metadata=metadata)
    return arrays, metadata


def prepare_contact_aware_ear_fixture(
    out_dir: str | Path,
    *,
    contract_path: str | Path | None = None,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Create one bounded deterministic NPZ and one JSON sidecar."""

    if max_output_bytes <= 0 or max_output_bytes > DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("ear-channel fixture cap must be positive and at most 4 MiB")
    output = Path(out_dir)
    if output.exists():
        raise FileExistsError(f"refusing to replace ear-channel fixture directory: {output}")
    free_disk_bytes = shutil.disk_usage(_nearest_existing_parent(output)).free
    if free_disk_bytes < MINIMUM_FREE_DISK_BYTES:
        raise OSError(
            "ear-channel fixture requires at least 1 GiB free disk before generation"
        )
    contract_source = (
        Path(contract_path) if contract_path is not None else _repo_root() / CONTRACT_RELATIVE_PATH
    )
    contract = load_registered_contact_aware_ear_contract(contract_source)
    arrays, metadata = make_contact_aware_ear_arrays(contract_path=contract_source)
    payload = _deterministic_npz_bytes(arrays)
    sidecar = _build_sidecar(
        metadata=metadata,
        payload=payload,
        max_output_bytes=max_output_bytes,
        contract=contract,
    )
    sidecar_payload = _sidecar_payload_with_sizes(sidecar)
    total_bytes = len(payload) + len(sidecar_payload)
    if total_bytes > max_output_bytes:
        raise ValueError(
            f"ear-channel fixture would write {total_bytes} bytes, exceeding cap {max_output_bytes}"
        )
    output.mkdir(parents=True, exist_ok=False)
    payload_path = output / PAYLOAD_NAME
    sidecar_path = output / SIDECAR_NAME
    try:
        with payload_path.open("xb") as handle:
            handle.write(payload)
        with sidecar_path.open("xb") as handle:
            handle.write(sidecar_payload)
    except BaseException:
        for created_path in (sidecar_path, payload_path):
            created_path.unlink(missing_ok=True)
        output.rmdir()
        raise
    return load_contact_aware_ear_metadata(
        sidecar_path,
        contract_path=contract_source,
        max_output_bytes=max_output_bytes,
    )


def load_contact_aware_ear_metadata(
    path: str | Path,
    *,
    contract_path: str | Path | None = None,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Validate hashes and NPZ members without opening any array member."""

    if max_output_bytes <= 0 or max_output_bytes > DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("ear-channel fixture cap must be positive and at most 4 MiB")
    source = Path(path)
    with source.open("rb") as handle:
        sidecar_payload = handle.read(MAX_SIDECAR_BYTES + 1)
    if len(sidecar_payload) > MAX_SIDECAR_BYTES:
        raise ValueError("ear-channel fixture sidecar exceeds 1 MiB")
    sidecar = json.loads(sidecar_payload.decode("utf-8"))
    _validate_forbidden_keys(sidecar)
    contract = load_registered_contact_aware_ear_contract(contract_path)
    _validate_sidecar(sidecar, contract=contract)
    payload_binding = sidecar["payload"]
    relative = PurePosixPath(str(payload_binding["path"]))
    if relative.is_absolute() or len(relative.parts) != 1 or ".." in relative.parts:
        raise ValueError("ear-channel fixture payload path is unsafe")
    if relative.as_posix() != PAYLOAD_NAME:
        raise ValueError("ear-channel fixture payload filename mismatch")
    payload_path = source.parent / relative.as_posix()
    payload_bytes = payload_path.stat().st_size
    if payload_bytes != payload_binding["bytes"]:
        raise ValueError("ear-channel fixture payload byte count mismatch")
    if payload_bytes > max_output_bytes or payload_bytes > DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("ear-channel fixture payload exceeds cap before hashing")
    if payload_bytes > sidecar["artifacts"]["maximum_output_bytes"]:
        raise ValueError("ear-channel fixture payload exceeds its recorded cap")
    if _file_sha256(payload_path) != payload_binding["sha256"]:
        raise ValueError("ear-channel fixture payload SHA-256 mismatch")
    members, uncompressed_bytes = _npz_member_inventory(payload_path)
    if set(members) != set(ARRAY_MEMBERS) or len(members) != len(ARRAY_MEMBERS):
        raise ValueError("ear-channel fixture NPZ member set mismatch")
    if payload_binding["array_members"] != list(ARRAY_MEMBERS):
        raise ValueError("ear-channel fixture payload member binding mismatch")
    if uncompressed_bytes > DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("ear-channel fixture uncompressed arrays exceed cap")
    artifacts = sidecar["artifacts"]
    total_bytes = payload_bytes + len(sidecar_payload)
    if artifacts["payload_bytes"] != payload_bytes:
        raise ValueError("ear-channel fixture payload accounting mismatch")
    if artifacts["metadata_sidecar_bytes"] != len(sidecar_payload):
        raise ValueError("ear-channel fixture sidecar accounting mismatch")
    if artifacts["total_output_bytes"] != total_bytes:
        raise ValueError("ear-channel fixture total-byte accounting mismatch")
    if artifacts["output_files"] != 2:
        raise ValueError("ear-channel fixture output-file count mismatch")
    if total_bytes > max_output_bytes or total_bytes > artifacts["maximum_output_bytes"]:
        raise ValueError("ear-channel fixture output exceeds cap")
    return sidecar


def load_contact_aware_ear_fixture(
    sidecar_path: str | Path,
    *,
    contract_path: str | Path | None = None,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> LoadedContactAwareEarFixture:
    """Load and strictly validate every fixture array."""

    sidecar = load_contact_aware_ear_metadata(
        sidecar_path,
        contract_path=contract_path,
        max_output_bytes=max_output_bytes,
    )
    np = _require_numpy()
    payload_path = Path(sidecar_path).parent / sidecar["payload"]["path"]
    with np.load(payload_path, allow_pickle=False) as archive:
        arrays = {name: archive[name] for name in archive.files}
        opened_members = tuple(archive.files)
    metadata = json.loads(str(arrays["metadata"].item()))
    validate_contact_aware_ear_arrays(arrays, expected_metadata=sidecar["fixture_metadata"])
    if metadata != sidecar["fixture_metadata"]:
        raise ValueError("ear-channel embedded metadata does not match sidecar")
    return LoadedContactAwareEarFixture(
        arrays=arrays,
        metadata=metadata,
        sidecar=sidecar,
        opened_members=opened_members,
    )


def validate_contact_aware_ear_arrays(
    arrays: Mapping[str, Any],
    *,
    expected_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate every identity, mask, policy, hash, and causality invariant."""

    np = _require_numpy()
    if set(arrays) != set(ARRAY_MEMBERS):
        raise ValueError("ear-channel fixture array member set mismatch")
    expected_specs = {
        "signals": ((ITEM_COUNT, CHANNEL_COUNT, SAMPLES), "float32"),
        "observed_mask": ((ITEM_COUNT, CHANNEL_COUNT, SAMPLES), "bool"),
        "channel_present_mask": ((ITEM_COUNT, CHANNEL_COUNT), "bool"),
        "contact_score": ((ITEM_COUNT, CHANNEL_COUNT), "float32"),
        "contact_score_valid_mask": ((ITEM_COUNT, CHANNEL_COUNT), "bool"),
        "noise_score": ((ITEM_COUNT, CHANNEL_COUNT), "float32"),
        "eligible_mask": ((ITEM_COUNT, CHANNEL_COUNT), "bool"),
        "selected_mask": ((ITEM_COUNT, CHANNEL_COUNT), "bool"),
        "selection_weight": ((ITEM_COUNT, CHANNEL_COUNT), "float32"),
        "adapted_signal": ((ITEM_COUNT, CHANNEL_COUNT, SAMPLES), "float32"),
        "adapted_observed_mask": ((ITEM_COUNT, CHANNEL_COUNT, SAMPLES), "bool"),
        "time_sec": ((SAMPLES,), "float64"),
        "ring_indices": ((CHANNEL_COUNT,), "int8"),
    }
    for name, (shape, dtype) in expected_specs.items():
        if arrays[name].shape != shape or str(arrays[name].dtype) != dtype:
            raise ValueError(f"ear-channel fixture {name} shape or dtype mismatch")
    for name, shape in (
        ("channel_names", (CHANNEL_COUNT,)),
        ("ear_sides", (CHANNEL_COUNT,)),
        ("item_ids", (ITEM_COUNT,)),
        ("scenario_ids", (ITEM_COUNT,)),
        ("selection_status", (ITEM_COUNT,)),
        ("mask_reasons", (ITEM_COUNT, CHANNEL_COUNT)),
    ):
        if arrays[name].shape != shape or arrays[name].dtype.kind != "U":
            raise ValueError(f"ear-channel fixture {name} shape or string dtype mismatch")
    if arrays["metadata"].shape != () or arrays["metadata"].dtype.kind != "U":
        raise ValueError("ear-channel fixture metadata must be a Unicode scalar")
    if tuple(arrays["channel_names"].tolist()) != CHANNEL_NAMES:
        raise ValueError("ear-channel fixture channel identity mismatch")
    if tuple(arrays["ear_sides"].tolist()) != EAR_SIDES:
        raise ValueError("ear-channel fixture ear-side identity mismatch")
    if tuple(int(value) for value in arrays["ring_indices"].tolist()) != RING_INDICES:
        raise ValueError("ear-channel fixture ring-index identity mismatch")
    _validate_row_identities(arrays)

    signals = arrays["signals"]
    observed = arrays["observed_mask"]
    present = arrays["channel_present_mask"]
    if not np.isfinite(signals[observed]).all():
        raise ValueError("ear-channel observed source sample is nonfinite")
    if not np.isnan(signals[~observed]).all():
        raise ValueError("ear-channel missing source sample must remain NaN")
    if np.any(observed & ~present[:, :, None]):
        raise ValueError("ear-channel absent channel contains observed samples")
    contact = arrays["contact_score"]
    contact_valid = arrays["contact_score_valid_mask"]
    if not np.isfinite(contact[contact_valid]).all():
        raise ValueError("ear-channel valid contact score is nonfinite")
    if np.any((contact[contact_valid] < 0.0) | (contact[contact_valid] > 1.0)):
        raise ValueError("ear-channel valid contact score is outside [0,1]")
    if not np.isnan(contact[~contact_valid]).all():
        raise ValueError("ear-channel unavailable contact score must remain NaN")
    noise = arrays["noise_score"]
    if not np.isfinite(noise).all() or np.any((noise < 0.0) | (noise > 1.0)):
        raise ValueError("ear-channel noise score is invalid")

    expected_eligible, expected_selected, expected_weights, expected_status = (
        apply_fixed_contact_policy(
            channel_present_mask=present,
            contact_score=contact,
            contact_score_valid_mask=contact_valid,
            noise_score=noise,
            observed_mask=observed,
            ear_sides=arrays["ear_sides"],
        )
    )
    for name, expected in (
        ("eligible_mask", expected_eligible),
        ("selected_mask", expected_selected),
        ("selection_weight", expected_weights),
        ("selection_status", expected_status),
    ):
        if not np.array_equal(arrays[name], expected):
            raise ValueError(f"ear-channel fixture {name} violates fixed policy")
    expected_adapted_mask = observed & expected_selected[:, :, None]
    if not np.array_equal(arrays["adapted_observed_mask"], expected_adapted_mask):
        raise ValueError("ear-channel adapted observed mask mismatch")
    expected_adapted = np.where(
        expected_adapted_mask,
        signals * expected_weights[:, :, None],
        0.0,
    ).astype("float32")
    if not np.array_equal(arrays["adapted_signal"], expected_adapted):
        raise ValueError("ear-channel adapted signal or zero-fill semantics mismatch")
    if not np.isfinite(arrays["adapted_signal"]).all():
        raise ValueError("ear-channel adapted transport contains nonfinite values")
    expected_reasons = _mask_reasons(
        np,
        channel_present_mask=present,
        contact_score=contact,
        contact_score_valid_mask=contact_valid,
        noise_score=noise,
        observed_mask=observed,
        eligible_mask=expected_eligible,
        selected_mask=expected_selected,
    )
    if not np.array_equal(arrays["mask_reasons"], expected_reasons):
        raise ValueError("ear-channel mask reason mismatch")
    expected_time = (np.arange(SAMPLES, dtype="float64") - SAMPLES) / SAMPLING_RATE_HZ
    if not np.array_equal(arrays["time_sec"], expected_time) or not np.all(expected_time < 0.0):
        raise ValueError("ear-channel timestamps are not the exact pre-event grid")

    metadata = json.loads(str(arrays["metadata"].item()))
    _validate_forbidden_keys(metadata)
    if expected_metadata is not None and metadata != dict(expected_metadata):
        raise ValueError("ear-channel fixture metadata identity mismatch")
    _validate_metadata(np, metadata=metadata, arrays=arrays)
    return _selection_diagnostics(np, arrays)


def summarize_contact_aware_ear_metadata(sidecar: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact metadata-only summary."""

    fixture = sidecar["fixture_metadata"]
    return {
        "schema": sidecar["schema"],
        "proof_posture": sidecar["proof_posture"],
        "contract": sidecar["contract"],
        "payload": sidecar["payload"],
        "item_count": fixture["identity"]["item_count"],
        "signal_shape": fixture["array_shapes"]["signals"],
        "scenario_counts": fixture["scenario_counts"],
        "selection_diagnostics": fixture["selection_diagnostics"],
        "source_reference_state": fixture["identity"]["source_reference_state"],
        "geometry_provenance": fixture["identity"]["geometry_provenance"],
        "producer_is_causal": sidecar["causality"]["producer_is_causal_at_event_boundary"],
        "required_left_context_samples": sidecar["causality"]["required_left_context_samples"],
        "required_right_context_samples": sidecar["causality"]["required_right_context_samples"],
        "end_to_end_latency_measured": False,
        "array_members_opened": 0,
        "artifacts": sidecar["artifacts"],
        "access_counters": sidecar["access_counters"],
        "warnings": sidecar["warnings"],
        "unavailable_fields": sidecar["unavailable_fields"],
        "claim_boundary": sidecar["claim_boundary"],
    }


def make_contact_aware_ear_refusal_mutation(
    fixture: LoadedContactAwareEarFixture,
    refusal_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Construct one deterministic malformed fixture for a refusal test."""

    if refusal_id not in REFUSAL_IDS:
        raise ValueError(f"unknown ear-channel refusal: {refusal_id}")
    np = _require_numpy()
    arrays = {name: np.array(value, copy=True) for name, value in fixture.arrays.items()}
    metadata = copy.deepcopy(dict(fixture.metadata))
    if refusal_id == "duplicate_or_missing_channel_identity":
        arrays["channel_names"][1] = arrays["channel_names"][0]
    elif refusal_id == "unknown_or_mismatched_ear_side":
        arrays["ear_sides"][0] = "X"
    elif refusal_id == "payload_sidecar_source_order_drift":
        metadata["identity"]["source_channel_names"][0] = "ear-X00"
    elif refusal_id == "nonfinite_sample_marked_observed":
        arrays["signals"][0, 0, 0] = np.nan
    elif refusal_id == "absent_channel_marked_selected":
        arrays["selected_mask"][6, 0] = True
    elif refusal_id == "invalid_or_unknown_contact_marked_selected":
        arrays["selected_mask"][24, 0] = True
    elif refusal_id == "over_noise_threshold_channel_marked_selected":
        arrays["selected_mask"][30, 1] = True
    elif refusal_id == "bilateral_minimum_not_met_but_selection_emitted":
        arrays["selected_mask"][24, 0] = True
        arrays["selection_weight"][24, 0] = np.float32(0.5)
    elif refusal_id == "selected_channel_count_above_side_cap":
        arrays["selected_mask"][0, 4] = True
    elif refusal_id == "nonzero_weight_outside_selected_mask":
        arrays["selection_weight"][0, 4] = np.float32(0.1)
    elif refusal_id == "left_or_right_weight_total_mismatch":
        first = int(np.flatnonzero(arrays["selected_mask"][0, :8])[0])
        arrays["selection_weight"][0, first] += np.float32(0.1)
    elif refusal_id == "zero_filled_missing_value_marked_measured":
        arrays["adapted_observed_mask"][6, 0, 0] = True
    elif refusal_id == "invented_impedance_or_contact_provenance":
        metadata["identity"]["measured_impedance_ohm"] = 1234.0
    elif refusal_id == "measured_geometry_claim_from_synthetic_nominal_fields":
        metadata["identity"]["geometry_provenance"] = "measured_anatomical"
    elif refusal_id == "forbidden_target_identity_or_outcome_field":
        metadata["target_text"] = "forbidden"
    else:
        metadata["causality"]["required_right_context_samples"] = 1
    arrays["metadata"] = np.asarray(_canonical_json(metadata))
    return arrays, metadata


def _mark_absent(
    signals: Any,
    observed_mask: Any,
    channel_present_mask: Any,
    contact_score: Any,
    contact_score_valid_mask: Any,
    row: int,
    channels: tuple[int, ...],
) -> None:
    np = _require_numpy()
    channel_list = list(channels)
    signals[row, channel_list, :] = np.nan
    observed_mask[row, channel_list, :] = False
    channel_present_mask[row, channel_list] = False
    contact_score[row, channel_list] = np.nan
    contact_score_valid_mask[row, channel_list] = False


def _mark_dropout(signals: Any, observed_mask: Any, row: int, channel: int) -> None:
    signals[row, channel, -32:] = float("nan")
    observed_mask[row, channel, -32:] = False


def _mask_reasons(
    np: Any,
    *,
    channel_present_mask: Any,
    contact_score: Any,
    contact_score_valid_mask: Any,
    noise_score: Any,
    observed_mask: Any,
    eligible_mask: Any,
    selected_mask: Any,
) -> Any:
    reasons = np.empty((ITEM_COUNT, CHANNEL_COUNT), dtype="U32")
    fractions = observed_mask.mean(axis=2, dtype="float64")
    for row in range(ITEM_COUNT):
        for channel in range(CHANNEL_COUNT):
            if not channel_present_mask[row, channel]:
                reason = "absent_channel"
            elif not contact_score_valid_mask[row, channel]:
                reason = "unknown_contact"
            elif float(contact_score[row, channel]) < 0.6:
                reason = "low_contact"
            elif float(noise_score[row, channel]) > 0.4:
                reason = "high_noise"
            elif float(fractions[row, channel]) < 0.95:
                reason = "insufficient_observed"
            elif selected_mask[row, channel]:
                reason = "selected"
            elif eligible_mask[row, channel]:
                reason = "eligible_not_selected"
            else:  # pragma: no cover - exhaustive defensive branch
                reason = "ineligible_unspecified"
            reasons[row, channel] = reason
    return reasons


def _build_metadata(
    np: Any,
    *,
    arrays: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    array_sha256 = {name: _array_sha256(arrays[name]) for name in HASHED_ARRAY_MEMBERS}
    selection_policy = _selection_policy()
    mask_semantics = _mask_semantics_contract()
    causality = _causality_contract()
    provenance_hashes = _provenance_hashes(
        array_sha256=array_sha256,
        selection_policy=selection_policy,
        mask_semantics=mask_semantics,
        causality=causality,
    )
    metadata = {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "target_free": True,
        "identity": {
            "seed": 5505,
            "item_count": ITEM_COUNT,
            "channel_count": CHANNEL_COUNT,
            "samples_per_item": SAMPLES,
            "sampling_rate_hz": SAMPLING_RATE_HZ,
            "window_start_sec": -2.0,
            "window_stop_sec_exclusive": 0.0,
            "source_channel_names": list(CHANNEL_NAMES),
            "ear_sides": list(EAR_SIDES),
            "source_reference_state": "synthetic_differential_reference_preserved",
            "contact_score_provenance": "synthetic_normalized_proxy_not_impedance",
            "measured_impedance_available": False,
            "geometry_provenance": "synthetic_nominal_not_measured_not_anatomical",
            "physical_switching_or_reference_selection": False,
        },
        "array_shapes": {name: list(arrays[name].shape) for name in HASHED_ARRAY_MEMBERS},
        "array_dtypes": {name: str(arrays[name].dtype) for name in HASHED_ARRAY_MEMBERS},
        "array_sha256": array_sha256,
        "scenario_counts": {
            scenario: int(np.sum(arrays["scenario_ids"] == scenario))
            for scenario in SCENARIO_IDS
        },
        "selection_policy": selection_policy,
        "mask_semantics": mask_semantics,
        "selection_diagnostics": _selection_diagnostics(np, arrays),
        "provenance_hashes": provenance_hashes,
        "refusal_ids": list(REFUSAL_IDS),
        "causality": causality,
        "access_counters": dict(ACCESS_COUNTERS),
        "warnings": list(contract["warnings"]),
        "unavailable_fields": list(contract["unavailable_fields"]),
        "claim_boundary": dict(contract["claim_boundary"]),
    }
    _validate_forbidden_keys(metadata)
    return metadata


def _selection_policy() -> dict[str, Any]:
    return {
        "version": "fixed_quality_rank_v0",
        "minimum_contact_score": 0.6,
        "maximum_noise_score": 0.4,
        "minimum_observed_fraction": 0.95,
        "maximum_selected_channels_per_side": 4,
        "minimum_selected_channels_per_side": 2,
        "rank_score_formula": "0.6*contact_score+0.4*(1-noise_score)",
        "stable_tie_break": "ascending_source_channel_index",
        "selected_weight_formula": "equal_within_side_totaling_0.5",
        "insufficient_bilateral_action": "select_none_and_emit_explicit_status",
        "fit_or_learning": False,
    }


def _mask_semantics_contract() -> dict[str, str]:
    return {
        "observed_mask": "finite_generated_source_sample",
        "channel_present_mask": "source_channel_exists_for_item",
        "contact_score_valid_mask": "normalized_proxy_is_available",
        "eligible_mask": "fixed_target_blind_policy_candidate",
        "selected_mask": "candidate_receives_nonzero_weight",
        "adapted_observed_mask": "observed_and_selected_only",
        "zero_fill": "transport_encoding_only_never_measured_or_imputed_signal",
    }


def _causality_contract() -> dict[str, Any]:
    return {
        "producer_is_causal_at_event_boundary": True,
        "required_left_context_samples": SAMPLES,
        "required_right_context_samples": 0,
        "post_event_samples": 0,
        "decision_endpoint_exclusive": True,
        "future_tail_prefix_invariance_required": True,
        "end_to_end_latency_measured": False,
    }


def _provenance_hashes(
    *,
    array_sha256: Mapping[str, str],
    selection_policy: Mapping[str, Any],
    mask_semantics: Mapping[str, Any],
    causality: Mapping[str, Any],
) -> dict[str, str]:
    source_order = {
        "channel_names": list(CHANNEL_NAMES),
        "ear_sides": list(EAR_SIDES),
        "ring_indices": list(RING_INDICES),
    }
    selected_subset_and_weight = {
        "selected_mask_sha256": array_sha256["selected_mask"],
        "selection_weight_sha256": array_sha256["selection_weight"],
    }
    configuration = {
        "contract_sha256": REGISTERED_CONTRACT_SHA256,
        "schema_version": SCHEMA_VERSION,
        "seed": 5505,
        "shape": [ITEM_COUNT, CHANNEL_COUNT, SAMPLES],
        "sampling_rate_hz": SAMPLING_RATE_HZ,
        "window_start_sec": -2.0,
        "window_stop_sec_exclusive": 0.0,
        "scenario_ids": list(SCENARIO_IDS),
        "source_order_sha256": _json_sha256(source_order),
        "selection_policy": dict(selection_policy),
        "mask_semantics": dict(mask_semantics),
        "causality": dict(causality),
    }
    return {
        "configuration_sha256": _json_sha256(configuration),
        "source_order_sha256": _json_sha256(source_order),
        "selected_subset_and_weight_sha256": _json_sha256(selected_subset_and_weight),
    }


def _selection_diagnostics(np: Any, arrays: Mapping[str, Any]) -> dict[str, Any]:
    selected = arrays["selected_mask"]
    status = arrays["selection_status"]
    observed = arrays["observed_mask"]
    adapted_observed = arrays["adapted_observed_mask"]
    return {
        "status_counts": {
            key: int(value)
            for key, value in sorted(Counter(status.tolist()).items())
        },
        "eligible_channel_count": int(arrays["eligible_mask"].sum()),
        "selected_channel_count": int(selected.sum()),
        "selected_left_channel_count": int(selected[:, :8].sum()),
        "selected_right_channel_count": int(selected[:, 8:].sum()),
        "observed_sample_count": int(observed.sum()),
        "adapted_observed_sample_count": int(adapted_observed.sum()),
        "source_missing_fraction": round(1.0 - float(observed.mean()), 9),
        "adapted_masked_fraction": round(1.0 - float(adapted_observed.mean()), 9),
    }


def _expected_selection_diagnostics() -> dict[str, Any]:
    return {
        "status_counts": {"insufficient_bilateral_contact": 6, "ok": 42},
        "eligible_channel_count": 504,
        "selected_channel_count": 300,
        "selected_left_channel_count": 150,
        "selected_right_channel_count": 150,
        "observed_sample_count": 168_192,
        "adapted_observed_sample_count": 76_800,
        "source_missing_fraction": 0.14453125,
        "adapted_masked_fraction": 0.609375,
    }


def _build_sidecar(
    *,
    metadata: Mapping[str, Any],
    payload: bytes,
    max_output_bytes: int,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    payload_sha256 = hashlib.sha256(payload).hexdigest()
    metadata_sha256 = _json_sha256(metadata)
    return {
        "schema": {"name": SIDECAR_SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "target_free": True,
        "contract": {
            "path": CONTRACT_RELATIVE_PATH.as_posix(),
            "bytes": REGISTERED_CONTRACT_BYTES,
            "sha256": REGISTERED_CONTRACT_SHA256,
        },
        "payload": {
            "path": PAYLOAD_NAME,
            "bytes": len(payload),
            "sha256": payload_sha256,
            "array_members": list(ARRAY_MEMBERS),
        },
        "fixture_metadata": dict(metadata),
        "hashes": {
            "algorithm": "SHA-256",
            "payload_sha256": payload_sha256,
            "fixture_metadata_sha256": metadata_sha256,
            **dict(metadata["provenance_hashes"]),
        },
        "causality": dict(metadata["causality"]),
        "access_counters": dict(ACCESS_COUNTERS),
        "artifacts": {
            "input_contract_bytes": REGISTERED_CONTRACT_BYTES,
            "payload_bytes": len(payload),
            "metadata_sidecar_bytes": 0,
            "total_output_bytes": 0,
            "maximum_output_bytes": int(max_output_bytes),
            "output_files": 2,
        },
        "measurements": {
            "runtime_seconds": "unavailable_until_measured_closeout",
            "peak_RSS_bytes": "unavailable_until_measured_closeout",
            "configured_numerical_threads": 1,
            "worker_count": 1,
            "end_to_end_latency_measured": False,
        },
        "warnings": list(contract["warnings"]),
        "unavailable_fields": list(contract["unavailable_fields"]),
        "claim_boundary": dict(contract["claim_boundary"]),
    }


def _validate_contract_identity(contract: Mapping[str, Any]) -> None:
    fixture = contract["synthetic_fixture"]
    exact = {
        "seed": 5505,
        "items": ITEM_COUNT,
        "channels": CHANNEL_COUNT,
        "channels_per_side": 8,
        "samples_per_item": SAMPLES,
        "sampling_rate_hz": SAMPLING_RATE_HZ,
        "scenario_item_count": 6,
    }
    for key, value in exact.items():
        if fixture.get(key) != value:
            raise ValueError(f"contact-aware ear-channel contract drifted at {key}")
    if tuple(fixture["scenario_ids"]) != SCENARIO_IDS:
        raise ValueError("contact-aware ear-channel scenario contract drifted")
    if tuple(contract["required_refusal_matrix"]) != REFUSAL_IDS:
        raise ValueError("contact-aware ear-channel refusal contract drifted")
    if contract["resource_caps"]["maximum_generated_output_bytes"] != DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("contact-aware ear-channel output cap drifted")
    if contract["dependency_contract"]["implementation_optional_extra"] != "array":
        raise ValueError("contact-aware ear-channel dependency contract drifted")


def _validate_metadata(np: Any, *, metadata: Mapping[str, Any], arrays: Mapping[str, Any]) -> None:
    contract = load_registered_contact_aware_ear_contract()
    _validate_metadata_static(metadata, contract=contract)
    if metadata.get("selection_diagnostics") != _selection_diagnostics(np, arrays):
        raise ValueError("ear-channel fixture selection diagnostics mismatch")
    expected_hashes = _provenance_hashes(
        array_sha256=metadata["array_sha256"],
        selection_policy=metadata["selection_policy"],
        mask_semantics=metadata["mask_semantics"],
        causality=metadata["causality"],
    )
    if metadata.get("provenance_hashes") != expected_hashes:
        raise ValueError("ear-channel fixture provenance hash mismatch")
    for name in HASHED_ARRAY_MEMBERS:
        if metadata["array_shapes"].get(name) != list(arrays[name].shape):
            raise ValueError(f"ear-channel fixture {name} metadata shape mismatch")
        if metadata["array_dtypes"].get(name) != str(arrays[name].dtype):
            raise ValueError(f"ear-channel fixture {name} metadata dtype mismatch")
        if metadata["array_sha256"].get(name) != _array_sha256(arrays[name]):
            raise ValueError(f"ear-channel fixture {name} hash mismatch")


def _validate_metadata_static(
    metadata: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
) -> None:
    if set(metadata) != METADATA_FIELDS:
        raise ValueError("ear-channel fixture metadata fields mismatch")
    if metadata.get("schema") != {"name": SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("ear-channel fixture metadata schema mismatch")
    if metadata.get("proof_posture") != PROOF_POSTURE or not metadata.get("target_free"):
        raise ValueError("ear-channel fixture metadata proof posture mismatch")
    identity = metadata.get("identity", {})
    expected_identity = {
        "seed": 5505,
        "item_count": ITEM_COUNT,
        "channel_count": CHANNEL_COUNT,
        "samples_per_item": SAMPLES,
        "sampling_rate_hz": SAMPLING_RATE_HZ,
        "window_start_sec": -2.0,
        "window_stop_sec_exclusive": 0.0,
        "source_channel_names": list(CHANNEL_NAMES),
        "ear_sides": list(EAR_SIDES),
        "source_reference_state": "synthetic_differential_reference_preserved",
        "contact_score_provenance": "synthetic_normalized_proxy_not_impedance",
        "measured_impedance_available": False,
        "geometry_provenance": "synthetic_nominal_not_measured_not_anatomical",
        "physical_switching_or_reference_selection": False,
    }
    if identity != expected_identity:
        raise ValueError("ear-channel fixture identity or provenance mismatch")
    if metadata.get("scenario_counts") != {scenario: 6 for scenario in SCENARIO_IDS}:
        raise ValueError("ear-channel fixture scenario counts mismatch")
    if metadata.get("refusal_ids") != list(REFUSAL_IDS):
        raise ValueError("ear-channel fixture refusal inventory mismatch")
    if metadata.get("selection_diagnostics") != _expected_selection_diagnostics():
        raise ValueError("ear-channel fixture static diagnostics mismatch")
    for field in ("array_shapes", "array_dtypes", "array_sha256"):
        if set(metadata.get(field, {})) != set(HASHED_ARRAY_MEMBERS):
            raise ValueError(f"ear-channel fixture {field} inventory mismatch")
    if metadata.get("selection_policy") != _selection_policy():
        raise ValueError("ear-channel fixture selection policy mismatch")
    if metadata.get("mask_semantics") != _mask_semantics_contract():
        raise ValueError("ear-channel fixture mask semantics mismatch")
    if metadata.get("causality") != _causality_contract():
        raise ValueError("ear-channel fixture causality mismatch")
    if metadata.get("access_counters") != ACCESS_COUNTERS:
        raise ValueError("ear-channel fixture access counters mismatch")
    if metadata.get("warnings") != contract["warnings"]:
        raise ValueError("ear-channel fixture warnings mismatch")
    if metadata.get("unavailable_fields") != contract["unavailable_fields"]:
        raise ValueError("ear-channel fixture unavailable fields mismatch")
    if metadata.get("claim_boundary") != contract["claim_boundary"]:
        raise ValueError("ear-channel fixture claim boundary mismatch")
    provenance_hashes = metadata.get("provenance_hashes", {})
    if set(provenance_hashes) != {
        "configuration_sha256",
        "source_order_sha256",
        "selected_subset_and_weight_sha256",
    }:
        raise ValueError("ear-channel fixture provenance hash fields mismatch")
    for value in (*metadata["array_sha256"].values(), *provenance_hashes.values()):
        if not _is_sha256(value):
            raise ValueError("ear-channel fixture contains malformed SHA-256")


def _validate_sidecar(sidecar: Mapping[str, Any], *, contract: Mapping[str, Any]) -> None:
    expected_fields = {
        "schema",
        "proof_posture",
        "target_free",
        "contract",
        "payload",
        "fixture_metadata",
        "hashes",
        "causality",
        "access_counters",
        "artifacts",
        "measurements",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    if set(sidecar) != expected_fields:
        raise ValueError("ear-channel fixture sidecar fields mismatch")
    if sidecar["schema"] != {"name": SIDECAR_SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("ear-channel fixture sidecar schema mismatch")
    if sidecar["proof_posture"] != PROOF_POSTURE or not sidecar["target_free"]:
        raise ValueError("ear-channel fixture sidecar proof posture mismatch")
    if sidecar["contract"] != {
        "path": CONTRACT_RELATIVE_PATH.as_posix(),
        "bytes": REGISTERED_CONTRACT_BYTES,
        "sha256": REGISTERED_CONTRACT_SHA256,
    }:
        raise ValueError("ear-channel fixture contract binding mismatch")
    fixture = sidecar["fixture_metadata"]
    _validate_metadata_static(fixture, contract=contract)
    payload = sidecar["payload"]
    if set(payload) != {"path", "bytes", "sha256", "array_members"}:
        raise ValueError("ear-channel fixture payload fields mismatch")
    if not isinstance(payload["bytes"], int) or payload["bytes"] <= 0:
        raise ValueError("ear-channel fixture payload byte count is invalid")
    if not _is_sha256(payload["sha256"]):
        raise ValueError("ear-channel fixture payload SHA-256 is malformed")
    hashes = sidecar["hashes"]
    expected_hashes = {
        "algorithm": "SHA-256",
        "payload_sha256": payload["sha256"],
        "fixture_metadata_sha256": _json_sha256(fixture),
        **fixture["provenance_hashes"],
    }
    if hashes != expected_hashes:
        raise ValueError("ear-channel fixture provenance bindings mismatch")
    if fixture.get("access_counters") != ACCESS_COUNTERS:
        raise ValueError("ear-channel embedded access counters mismatch")
    if sidecar["access_counters"] != ACCESS_COUNTERS:
        raise ValueError("ear-channel sidecar access counters mismatch")
    if sidecar["causality"] != fixture.get("causality"):
        raise ValueError("ear-channel sidecar causality binding mismatch")
    if sidecar["warnings"] != contract["warnings"]:
        raise ValueError("ear-channel sidecar warnings mismatch")
    if sidecar["unavailable_fields"] != contract["unavailable_fields"]:
        raise ValueError("ear-channel sidecar unavailable fields mismatch")
    if sidecar["claim_boundary"] != contract["claim_boundary"]:
        raise ValueError("ear-channel sidecar claim boundary mismatch")
    artifacts = sidecar["artifacts"]
    if set(artifacts) != {
        "input_contract_bytes",
        "payload_bytes",
        "metadata_sidecar_bytes",
        "total_output_bytes",
        "maximum_output_bytes",
        "output_files",
    }:
        raise ValueError("ear-channel fixture artifact fields mismatch")
    if artifacts["input_contract_bytes"] != REGISTERED_CONTRACT_BYTES:
        raise ValueError("ear-channel fixture input-byte accounting mismatch")
    if artifacts["maximum_output_bytes"] <= 0 or (
        artifacts["maximum_output_bytes"] > DEFAULT_MAX_OUTPUT_BYTES
    ):
        raise ValueError("ear-channel fixture recorded output cap is invalid")
    measurements = sidecar["measurements"]
    if set(measurements) != {
        "runtime_seconds",
        "peak_RSS_bytes",
        "configured_numerical_threads",
        "worker_count",
        "end_to_end_latency_measured",
    }:
        raise ValueError("ear-channel fixture measurement fields mismatch")
    if measurements["runtime_seconds"] != "unavailable_until_measured_closeout":
        raise ValueError("ear-channel fixture runtime must remain unavailable in payload")
    if measurements["peak_RSS_bytes"] != "unavailable_until_measured_closeout":
        raise ValueError("ear-channel fixture RSS must remain unavailable in payload")
    if measurements["configured_numerical_threads"] != 1 or measurements["worker_count"] != 1:
        raise ValueError("ear-channel fixture execution resource identity mismatch")
    if measurements["end_to_end_latency_measured"] is not False:
        raise ValueError("ear-channel fixture latency status mismatch")


def _validate_row_identities(arrays: Mapping[str, Any]) -> None:
    items = arrays["item_ids"].tolist()
    scenarios = arrays["scenario_ids"].tolist()
    if len(set(items)) != ITEM_COUNT:
        raise ValueError("ear-channel fixture item IDs must be unique")
    row = 0
    for scenario_index, scenario in enumerate(SCENARIO_IDS):
        for replicate in range(6):
            if items[row] != f"ear-s{scenario_index:02d}-r{replicate:02d}":
                raise ValueError("ear-channel fixture item identity mismatch")
            if scenarios[row] != scenario:
                raise ValueError("ear-channel fixture scenario ordering mismatch")
            row += 1


def _deterministic_npz_bytes(arrays: Mapping[str, Any]) -> bytes:
    np = _require_numpy()
    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for name in sorted(arrays):
            member = io.BytesIO()
            np.save(member, np.asarray(arrays[name]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, member.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
    return output.getvalue()


def _npz_member_inventory(path: Path) -> tuple[tuple[str, ...], int]:
    try:
        with zipfile.ZipFile(path, mode="r") as archive:
            entries = archive.infolist()
    except zipfile.BadZipFile as exc:
        raise ValueError("ear-channel fixture payload is not a valid NPZ") from exc
    names: list[str] = []
    uncompressed_bytes = 0
    for entry in entries:
        member = PurePosixPath(entry.filename)
        if member.is_absolute() or len(member.parts) != 1 or member.suffix != ".npy":
            raise ValueError(f"ear-channel fixture contains unsafe member: {entry.filename}")
        names.append(member.stem)
        uncompressed_bytes += int(entry.file_size)
    if len(names) != len(set(names)):
        raise ValueError("ear-channel fixture contains duplicate members")
    return tuple(names), uncompressed_bytes


def _sidecar_payload_with_sizes(sidecar: dict[str, Any]) -> bytes:
    for _ in range(10):
        payload = (json.dumps(sidecar, indent=2, sort_keys=True) + "\n").encode("utf-8")
        sidecar["artifacts"]["metadata_sidecar_bytes"] = len(payload)
        sidecar["artifacts"]["total_output_bytes"] = sidecar["artifacts"]["payload_bytes"] + len(
            payload
        )
    return (json.dumps(sidecar, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _array_sha256(value: Any) -> str:
    np = _require_numpy()
    payload = io.BytesIO()
    np.save(payload, np.asarray(value), allow_pickle=False)
    return hashlib.sha256(payload.getvalue()).hexdigest()


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_forbidden_keys(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                if key not in ACCESS_COUNTERS or nested != 0:
                    raise ValueError(f"ear-channel fixture contains forbidden field: {key}")
            _validate_forbidden_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _validate_forbidden_keys(item)


def _nearest_existing_parent(path: Path) -> Path:
    parent = path.parent
    while not parent.exists():
        if parent == parent.parent:
            raise FileNotFoundError(f"no existing parent found for ear-channel output: {path}")
        parent = parent.parent
    return parent


def _require_numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError(
            "Contact-aware ear-channel fixtures require NumPy. "
            "Install neurodecodekit[array]."
        ) from exc
    if _major_minor(np.__version__) < (1, 26):
        raise RuntimeError("Contact-aware ear-channel fixtures require NumPy >=1.26.")
    return np


def _major_minor(version: str) -> tuple[int, int]:
    values: list[int] = []
    for part in version.split(".")[:2]:
        digits = "".join(character for character in part if character.isdigit())
        values.append(int(digits or 0))
    while len(values) < 2:
        values.append(0)
    return values[0], values[1]


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
