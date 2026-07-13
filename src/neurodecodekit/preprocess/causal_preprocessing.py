"""Stateful target-free causal preprocessing for the Loop 25 v1 gate."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


CONTRACT_RELATIVE_PATH = Path("registries/causal_preprocessing_contract.v1.json")
AUTHORIZATION_RELATIVE_PATH = Path("registries/loop25_authorization_decision.v1.json")
REGISTERED_CONTRACT_SHA256 = (
    "ecec99a7cc505ec0256c01c3c1e8aeaa05323ab54a71528323fa6d32bd289141"
)
STATE_SCHEMA_NAME = "neurodecodekit.causal_preprocessing_state"
STATE_SCHEMA_VERSION = "0.2.0"
FILTER_BUNDLE_SCHEMA_NAME = "b2q-causal-preprocessing-filter-bundle"
FILTER_BUNDLE_SCHEMA_VERSION = 0
CHANNELS = 5
SOURCE_RATE_HZ = 1000.0
OUTPUT_RATE_HZ = 100.0
DECIMATION_FACTOR = 10
MAX_SOURCE_SAMPLES_PER_CHUNK = 4096


class CausalPreprocessingRefusal(ValueError):
    """Fail-closed error carrying one registered refusal identifier."""

    def __init__(self, refusal_id: str, message: str) -> None:
        super().__init__(message)
        self.refusal_id = refusal_id


@dataclass(frozen=True)
class FilterBundle:
    """Exact SOS stages and their semantic identities."""

    notch_sos: Any
    bandpass_sos: Any
    antialias_sos: Any
    combined_sos: Any
    contract_sha256: str
    pipeline_config_sha256: str
    filter_sos_sha256: str

    @property
    def total_sections(self) -> int:
        return int(self.combined_sos.shape[0])

    @property
    def antialias_sections(self) -> int:
        return int(self.antialias_sos.shape[0])

    @property
    def filter_state_array_bytes(self) -> int:
        return CHANNELS * self.total_sections * 2 * 8

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_sha256": self.contract_sha256,
            "pipeline_config_sha256": self.pipeline_config_sha256,
            "filter_sos_sha256": self.filter_sos_sha256,
            "section_order": "notch_then_bandpass_then_dedicated_antialias",
            "notch_sos_float64": self.notch_sos.tolist(),
            "bandpass_sos_float64": self.bandpass_sos.tolist(),
            "antialias_sos_float64": self.antialias_sos.tolist(),
            "combined_sos_float64": self.combined_sos.tolist(),
            "notch_sections": int(self.notch_sos.shape[0]),
            "bandpass_sections": int(self.bandpass_sos.shape[0]),
            "antialias_sections": self.antialias_sections,
            "total_sections": self.total_sections,
            "filter_state_array_bytes": self.filter_state_array_bytes,
        }


@dataclass(frozen=True)
class PreprocessingOutput:
    """One emitted chunk on the registered 100 Hz sample grid."""

    values: Any
    source_indices: Any
    timestamps_sec: Any

    @property
    def array_bytes(self) -> int:
        return int(self.values.nbytes + self.source_indices.nbytes + self.timestamps_sec.nbytes)


def design_registered_filter_bundle() -> FilterBundle:
    """Design the exact registered SOS chain once in the authorized runner."""

    np = _require_numpy()
    signal = _require_scipy_signal()
    contract = load_registered_contract()
    validate_loop25_authorization()
    pipeline = contract["planned_pipeline"]

    notch = pipeline["notch"]
    b, a = signal.iirnotch(
        notch["frequency_hz"],
        notch["quality_factor"],
        fs=notch["sample_rate_hz"],
    )
    notch_sos = np.asarray(signal.tf2sos(b, a), dtype="float64")

    bandpass = pipeline["bandpass"]
    bandpass_sos = np.asarray(
        signal.butter(
            bandpass["order"],
            bandpass["critical_frequencies_hz"],
            btype=bandpass["btype"],
            fs=bandpass["sample_rate_hz"],
            output=bandpass["output"],
        ),
        dtype="float64",
    )

    antialias = pipeline["dedicated_antialias"]
    antialias_sos = np.asarray(
        signal.iirdesign(
            wp=antialias["passband_edge_hz"],
            ws=antialias["stopband_edge_hz"],
            gpass=antialias["maximum_passband_loss_db"],
            gstop=antialias["minimum_stopband_attenuation_db"],
            analog=antialias["analog"],
            ftype=antialias["filter_type"],
            output=antialias["output"],
            fs=antialias["sample_rate_hz"],
        ),
        dtype="float64",
    )
    combined = np.concatenate([notch_sos, bandpass_sos, antialias_sos], axis=0)
    pipeline_hash = _sha256_json(pipeline)
    bundle = FilterBundle(
        notch_sos=notch_sos,
        bandpass_sos=bandpass_sos,
        antialias_sos=antialias_sos,
        combined_sos=combined,
        contract_sha256=REGISTERED_CONTRACT_SHA256,
        pipeline_config_sha256=pipeline_hash,
        filter_sos_sha256=_sos_sha256(combined),
    )
    validate_filter_bundle(bundle, require_registered=True)
    return bundle


def make_test_filter_bundle(sos: Any) -> FilterBundle:
    """Build a nonregistered bundle for unit tests without designing coefficients."""

    np = _require_numpy()
    values = np.asarray(sos, dtype="float64")
    if values.ndim != 2 or values.shape[1] != 6 or values.shape[0] < 1:
        raise ValueError("test SOS must have shape [sections, 6]")
    empty = np.empty((0, 6), dtype="float64")
    return FilterBundle(
        notch_sos=empty,
        bandpass_sos=empty,
        antialias_sos=values.copy(),
        combined_sos=values.copy(),
        contract_sha256="test-contract",
        pipeline_config_sha256="test-pipeline",
        filter_sos_sha256=_sos_sha256(values),
    )


def validate_filter_bundle(bundle: FilterBundle, *, require_registered: bool) -> None:
    """Validate SOS identities, section caps, and finite coefficients."""

    np = _require_numpy()
    arrays = (
        bundle.notch_sos,
        bundle.bandpass_sos,
        bundle.antialias_sos,
        bundle.combined_sos,
    )
    for values in arrays:
        if values.dtype != np.dtype("float64"):
            raise CausalPreprocessingRefusal(
                "filter_configuration_or_coefficient_hash_mismatch",
                "all SOS coefficients must be float64",
            )
        if values.ndim != 2 or values.shape[1] != 6:
            raise CausalPreprocessingRefusal(
                "filter_configuration_or_coefficient_hash_mismatch",
                "SOS arrays must have shape [sections, 6]",
            )
        if not np.isfinite(values).all():
            raise CausalPreprocessingRefusal(
                "filter_configuration_or_coefficient_hash_mismatch",
                "SOS coefficients must be finite",
            )
    if bundle.antialias_sections > 12 or bundle.total_sections > 17:
        raise CausalPreprocessingRefusal(
            "dedicated_antialias_section_or_total_state_cap_exceeded",
            "registered SOS section cap exceeded",
        )
    if bundle.filter_state_array_bytes > 1360:
        raise CausalPreprocessingRefusal(
            "dedicated_antialias_section_or_total_state_cap_exceeded",
            "registered filter-state array cap exceeded",
        )
    if _sos_sha256(bundle.combined_sos) != bundle.filter_sos_sha256:
        raise CausalPreprocessingRefusal(
            "filter_configuration_or_coefficient_hash_mismatch",
            "combined SOS semantic hash mismatch",
        )
    if require_registered:
        contract = load_registered_contract()
        if bundle.contract_sha256 != REGISTERED_CONTRACT_SHA256:
            raise CausalPreprocessingRefusal(
                "contract_identity_mismatch",
                "filter bundle contract hash mismatch",
            )
        if bundle.pipeline_config_sha256 != _sha256_json(contract["planned_pipeline"]):
            raise CausalPreprocessingRefusal(
                "filter_configuration_or_coefficient_hash_mismatch",
                "pipeline configuration hash mismatch",
            )
        expected = np.concatenate(
            [bundle.notch_sos, bundle.bandpass_sos, bundle.antialias_sos], axis=0
        )
        if not np.array_equal(expected, bundle.combined_sos):
            raise CausalPreprocessingRefusal(
                "dedicated_antialias_stage_missing_reordered_or_spec_mismatch",
                "SOS stage order or content mismatch",
            )


def audit_static_filter_design(bundle: FilterBundle) -> dict[str, Any]:
    """Run the complete preregistered pole, response, alias, and transient gate."""

    np = _require_numpy()
    signal = _require_scipy_signal()
    validate_filter_bundle(bundle, require_registered=True)
    contract = load_registered_contract()
    gate = contract["acceptance_gates"]["frequency_response"]
    grid = np.linspace(
        gate["dense_grid_start_hz"],
        gate["dense_grid_stop_hz"],
        gate["dense_grid_points_inclusive"],
        dtype="float64",
    )
    dedicated_response = _sos_response(signal, bundle.antialias_sos, grid)
    combined_response = _sos_response(signal, bundle.combined_sos, grid)
    dedicated_db = _gain_db(np, dedicated_response)
    combined_db = _gain_db(np, combined_response)

    pass_mask = grid <= gate["dedicated_antialias_passband_hz"][1]
    stop_mask = grid >= gate["dedicated_antialias_stopband_hz"][0]
    folding_mask = grid >= gate["dedicated_antialias_stopband_hz"][0]
    dedicated_pass_min = float(dedicated_db[pass_mask].min())
    dedicated_pass_max = float(dedicated_db[pass_mask].max())
    dedicated_stop_max = float(dedicated_db[stop_mask].max())
    combined_folding_max = float(combined_db[folding_mask].max())

    _, poles, _ = signal.sos2zpk(bundle.combined_sos)
    pole_magnitudes = np.abs(poles)
    maximum_pole = float(pole_magnitudes.max(initial=0.0))
    passband_probes = {
        _format_frequency(value): _response_db_at(grid, combined_db, value)
        for value in gate["passband_probe_frequencies_hz"]
    }
    alias_rows = []
    for source_frequency in gate["registered_alias_source_probe_frequencies_hz"]:
        alias_rows.append(
            {
                "source_frequency_hz": float(source_frequency),
                "alias_destination_hz": float(
                    abs(((float(source_frequency) + 50.0) % 100.0) - 50.0)
                ),
                "combined_source_gain_db": _response_db_at(
                    grid, combined_db, float(source_frequency)
                ),
            }
        )

    transient_length = 8192
    impulse = np.zeros(transient_length, dtype="float64")
    impulse[0] = 1.0
    step = np.ones(transient_length, dtype="float64")
    impulse_output = signal.sosfilt(bundle.combined_sos, impulse)
    step_output = signal.sosfilt(bundle.combined_sos, step)
    impulse_finite = bool(np.isfinite(impulse_output).all())
    step_finite = bool(np.isfinite(step_output).all())
    step_final = float(step_output[-1])
    transient = {
        "response_samples": transient_length,
        "impulse_peak_abs": float(np.max(np.abs(impulse_output))),
        "impulse_tail_peak_abs_last_1024": float(
            np.max(np.abs(impulse_output[-1024:]))
        ),
        "step_peak": float(np.max(step_output)),
        "step_trough": float(np.min(step_output)),
        "step_final": step_final,
        "step_overshoot_above_final": float(np.max(step_output) - step_final),
        "step_ringing_peak_to_peak_last_1024": float(
            np.ptp(step_output[-1024:])
        ),
        "impulse_finite": impulse_finite,
        "step_finite": step_finite,
    }
    delay = _frequency_delay_report(np, grid, combined_response, [5.0, 10.0, 20.0, 35.0])

    tolerance = 1e-8
    checks = {
        "antialias_section_cap": bundle.antialias_sections <= 12,
        "total_section_cap": bundle.total_sections <= 17,
        "state_array_cap": bundle.filter_state_array_bytes <= 1360,
        "poles_strictly_inside_unit_circle": bool((pole_magnitudes < 1.0).all()),
        "maximum_pole_magnitude": maximum_pole <= gate["all_pole_magnitudes_maximum"],
        "dedicated_passband_min": dedicated_pass_min
        >= gate["dedicated_antialias_passband_gain_db_min"] - tolerance,
        "dedicated_passband_max": dedicated_pass_max
        <= gate["dedicated_antialias_passband_gain_db_max"] + tolerance,
        "dedicated_dense_stopband": dedicated_stop_max
        <= gate["dedicated_antialias_dense_stopband_gain_db_max"] + tolerance,
        "combined_dense_folding_band": combined_folding_max
        <= gate["combined_chain_dense_folding_band_gain_db_max"] + tolerance,
        "combined_dc_gain": _response_db_at(grid, combined_db, 0.0)
        <= gate["dc_gain_db_max"] + tolerance,
        "combined_notch_gain": _response_db_at(grid, combined_db, 50.0)
        <= gate["notch_gain_db_max"] + tolerance,
        "combined_passband_probes": all(
            gate["passband_gain_db_min"] - tolerance
            <= value
            <= gate["passband_gain_db_max"] + tolerance
            for value in passband_probes.values()
        ),
        "alias_fold_map": all(
            row["combined_source_gain_db"]
            <= gate["alias_map_source_gain_db_max"] + tolerance
            for row in alias_rows
        ),
        "impulse_finite": impulse_finite,
        "step_finite": step_finite,
    }
    return {
        "schema": {"name": "b2q-causal-preprocessing-static-audit", "version": 0},
        "proof_posture": "target_free_static_filter_mechanics_only",
        "passed": all(checks.values()),
        "checks": checks,
        "filter": bundle.to_dict(),
        "dense_grid": {
            "start_hz": float(grid[0]),
            "stop_hz": float(grid[-1]),
            "points": int(grid.size),
        },
        "poles": {
            "count": int(pole_magnitudes.size),
            "maximum_magnitude": maximum_pole,
            "registered_maximum": gate["all_pole_magnitudes_maximum"],
        },
        "response": {
            "dedicated_passband_min_db": dedicated_pass_min,
            "dedicated_passband_max_db": dedicated_pass_max,
            "dedicated_passband_ripple_db": dedicated_pass_max - dedicated_pass_min,
            "dedicated_stopband_max_db": dedicated_stop_max,
            "combined_folding_band_max_db": combined_folding_max,
            "combined_dc_gain_db": _response_db_at(grid, combined_db, 0.0),
            "combined_notch_gain_db": _response_db_at(grid, combined_db, 50.0),
            "combined_passband_probes_db": passband_probes,
            "transition_band_hz": gate["transition_band_hz"],
            "transition_band_has_no_passband_claim": True,
        },
        "alias_fold_map": alias_rows,
        "transient": transient,
        "frequency_dependent_delay": delay,
        "warnings": [
            "The causal SOS chain is not numerically equivalent to the official offline MNE FFT resampler.",
            "Elliptic ripple, step ringing, and nonlinear frequency-dependent delay are present and reported.",
            "Frequency delay is not capture-to-text or end-to-end latency.",
        ],
        "claim_boundaries": [
            "A static pass establishes filter mechanics only.",
            "It does not establish retained neural information or decoding performance.",
        ],
    }


class CausalPreprocessor:
    """Forward-only stateful SOS filter and phase-locked decimator."""

    def __init__(
        self,
        bundle: FilterBundle,
        *,
        source_start_sample: int,
        require_registered: bool = True,
        state: Mapping[str, Any] | None = None,
    ) -> None:
        np = _require_numpy()
        validate_filter_bundle(bundle, require_registered=require_registered)
        if not isinstance(source_start_sample, int):
            raise CausalPreprocessingRefusal(
                "source_start_changed_after_initialization",
                "source_start_sample must be an integer",
            )
        self.bundle = bundle
        self.source_start_sample = source_start_sample
        self.require_registered = require_registered
        self.center = np.asarray([-0.25, -0.125, 0.0, 0.125, 0.25], dtype="float64")
        self.scale = np.asarray([0.75, 0.875, 1.0, 1.125, 1.25], dtype="float64")
        self.source_samples_seen = 0
        self.output_samples_emitted = 0
        self.filter_state = np.zeros(
            (CHANNELS, bundle.total_sections, 2), dtype="float64"
        )
        self.initialized = False
        self.closed = False
        if state is not None:
            self._restore(state)

    def push(self, chunk: Any, *, chunk_start_sample: int) -> PreprocessingOutput:
        """Push one contiguous float32 chunk and emit retained 100 Hz samples."""

        np = _require_numpy()
        signal = _require_scipy_signal()
        if self.closed:
            raise CausalPreprocessingRefusal(
                "push_or_second_flush_after_close", "cannot push after flush"
            )
        values = np.asarray(chunk)
        if values.dtype != np.dtype("float32") or values.ndim != 2:
            raise CausalPreprocessingRefusal(
                "chunk_nonfinite_or_wrong_dtype",
                "chunk must be float32 [channels, time]",
            )
        if values.shape[0] != CHANNELS or not 1 <= values.shape[1] <= MAX_SOURCE_SAMPLES_PER_CHUNK:
            raise CausalPreprocessingRefusal(
                "chunk_empty_or_over_cap", "chunk shape exceeds the registered bounds"
            )
        if not np.isfinite(values).all():
            raise CausalPreprocessingRefusal(
                "chunk_nonfinite_or_wrong_dtype", "chunk contains nonfinite values"
            )
        expected_start = self.source_start_sample + self.source_samples_seen
        if chunk_start_sample != expected_start:
            raise CausalPreprocessingRefusal(
                "source_index_gap_overlap_duplicate_or_reorder",
                f"expected chunk start {expected_start}, got {chunk_start_sample}",
            )
        work = values.astype("float64", copy=True)
        if not self.initialized:
            base = signal.sosfilt_zi(self.bundle.combined_sos)
            self.filter_state = work[:, :1, None] * base[None, :, :]
            self.initialized = True
        scipy_state = self.filter_state.transpose(1, 0, 2)
        filtered, final_state = signal.sosfilt(
            self.bundle.combined_sos,
            work,
            axis=-1,
            zi=scipy_state,
        )
        self.filter_state = np.asarray(final_state.transpose(1, 0, 2), dtype="float64")
        relative = self.source_samples_seen + np.arange(values.shape[1], dtype="int64")
        keep = relative % DECIMATION_FACTOR == 0
        source_indices = relative[keep]
        retained = filtered[:, keep]
        normalized = (retained - self.center[:, None]) / self.scale[:, None]
        normalized = np.clip(normalized, -5.0, 5.0)
        output = normalized.astype("float32")
        timestamps = (self.source_start_sample + source_indices).astype("float64") / SOURCE_RATE_HZ
        if not np.isfinite(output).all() or float(output.min(initial=0.0)) < -5.0 or float(
            output.max(initial=0.0)
        ) > 5.0:
            raise CausalPreprocessingRefusal(
                "output_nonfinite_or_out_of_bounds", "output failed finite or clamp bounds"
            )
        self.source_samples_seen += int(values.shape[1])
        self.output_samples_emitted += int(source_indices.size)
        return PreprocessingOutput(output, source_indices, timestamps)

    def snapshot(self) -> dict[str, Any]:
        """Return an inspectable resumable state with a deterministic semantic hash."""

        state = {
            "schema_name": STATE_SCHEMA_NAME,
            "schema_version": STATE_SCHEMA_VERSION,
            "contract_sha256": self.bundle.contract_sha256,
            "pipeline_config_sha256": self.bundle.pipeline_config_sha256,
            "source_start_sample": self.source_start_sample,
            "source_samples_seen": self.source_samples_seen,
            "output_samples_emitted": self.output_samples_emitted,
            "filter_sos_sha256": self.bundle.filter_sos_sha256,
            "filter_state_float64": self.filter_state.tolist(),
            "initialized": self.initialized,
            "closed": self.closed,
        }
        state["semantic_sha256"] = _sha256_json(state)
        return state

    def flush(self) -> dict[str, Any]:
        """Close without padding or emitting invented samples."""

        if self.closed:
            raise CausalPreprocessingRefusal(
                "push_or_second_flush_after_close", "second flush is refused"
            )
        self.closed = True
        return {
            "source_samples_seen": self.source_samples_seen,
            "output_samples_emitted": self.output_samples_emitted,
            "invented_source_samples": 0,
            "invented_output_samples": 0,
            "closed": True,
            "state_semantic_sha256": self.snapshot()["semantic_sha256"],
        }

    def _restore(self, state: Mapping[str, Any]) -> None:
        np = _require_numpy()
        provided = dict(state)
        semantic_hash = provided.pop("semantic_sha256", None)
        if semantic_hash != _sha256_json(provided):
            raise CausalPreprocessingRefusal(
                "state_tampered_or_over_cap", "state semantic hash mismatch"
            )
        expected = {
            "schema_name": STATE_SCHEMA_NAME,
            "schema_version": STATE_SCHEMA_VERSION,
            "contract_sha256": self.bundle.contract_sha256,
            "pipeline_config_sha256": self.bundle.pipeline_config_sha256,
            "source_start_sample": self.source_start_sample,
            "filter_sos_sha256": self.bundle.filter_sos_sha256,
        }
        for key, value in expected.items():
            if provided.get(key) != value:
                raise CausalPreprocessingRefusal(
                    "state_contract_or_configuration_hash_mismatch",
                    f"state mismatch at {key}",
                )
        filter_state = np.asarray(provided["filter_state_float64"], dtype="float64")
        expected_shape = (CHANNELS, self.bundle.total_sections, 2)
        if (
            filter_state.shape != expected_shape
            or filter_state.nbytes > 1360
            or not np.isfinite(filter_state).all()
        ):
            raise CausalPreprocessingRefusal(
                "filter_state_shape_dtype_or_nonfinite_mismatch",
                "restored filter state is malformed",
            )
        self.filter_state = filter_state
        self.source_samples_seen = int(provided["source_samples_seen"])
        self.output_samples_emitted = int(provided["output_samples_emitted"])
        self.initialized = bool(provided["initialized"])
        self.closed = bool(provided["closed"])


def save_filter_bundle(path: str | Path, bundle: FilterBundle, audit: Mapping[str, Any]) -> int:
    """Persist the frozen coefficients and static audit as bounded JSON."""

    output = Path(path)
    if output.exists():
        raise FileExistsError(f"refusing to replace filter bundle: {output}")
    payload = {
        "schema": {"name": FILTER_BUNDLE_SCHEMA_NAME, "version": FILTER_BUNDLE_SCHEMA_VERSION},
        "bundle": bundle.to_dict(),
        "static_audit": dict(audit),
    }
    encoded = (_canonical_json(payload) + "\n").encode("utf-8")
    if len(encoded) > 1024 * 1024:
        raise CausalPreprocessingRefusal(
            "resource_or_output_cap_exceeded", "filter bundle exceeds 1 MiB"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encoded)
    return len(encoded)


def load_filter_bundle(path: str | Path, *, require_registered: bool = True) -> tuple[FilterBundle, dict[str, Any]]:
    """Load and strictly validate a saved filter bundle."""

    np = _require_numpy()
    source = Path(path)
    if source.stat().st_size > 1024 * 1024:
        raise CausalPreprocessingRefusal(
            "resource_or_output_cap_exceeded", "filter bundle exceeds 1 MiB"
        )
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema") != {
        "name": FILTER_BUNDLE_SCHEMA_NAME,
        "version": FILTER_BUNDLE_SCHEMA_VERSION,
    }:
        raise CausalPreprocessingRefusal(
            "filter_configuration_or_coefficient_hash_mismatch",
            "filter bundle schema mismatch",
        )
    row = payload["bundle"]
    bundle = FilterBundle(
        notch_sos=np.asarray(row["notch_sos_float64"], dtype="float64").reshape(-1, 6),
        bandpass_sos=np.asarray(row["bandpass_sos_float64"], dtype="float64").reshape(-1, 6),
        antialias_sos=np.asarray(row["antialias_sos_float64"], dtype="float64").reshape(-1, 6),
        combined_sos=np.asarray(row["combined_sos_float64"], dtype="float64").reshape(-1, 6),
        contract_sha256=row["contract_sha256"],
        pipeline_config_sha256=row["pipeline_config_sha256"],
        filter_sos_sha256=row["filter_sos_sha256"],
    )
    validate_filter_bundle(bundle, require_registered=require_registered)
    audit = payload["static_audit"]
    if require_registered and not audit.get("passed"):
        raise CausalPreprocessingRefusal(
            "full_folding_band_attenuation_failed", "saved static filter gate did not pass"
        )
    return bundle, audit


def load_registered_contract() -> dict[str, Any]:
    """Load and hash-check the immutable v1 contract."""

    path = _repo_root() / CONTRACT_RELATIVE_PATH
    if _file_sha256(path) != REGISTERED_CONTRACT_SHA256:
        raise CausalPreprocessingRefusal(
            "contract_identity_mismatch", "Loop 25 v1 contract SHA-256 mismatch"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("contract_id") != "loop25-causal-preprocessing-v1":
        raise CausalPreprocessingRefusal(
            "contract_identity_mismatch", "Loop 25 v1 contract identity mismatch"
        )
    return payload


def validate_loop25_authorization() -> dict[str, Any]:
    """Require the separate conservative authorization decision."""

    path = _repo_root() / AUTHORIZATION_RELATIVE_PATH
    if not path.exists():
        raise CausalPreprocessingRefusal("authorization_missing", "Loop 25 authorization missing")
    decision = json.loads(path.read_text(encoding="utf-8"))
    if decision.get("status") != "authorized_no_implementation_yet":
        raise CausalPreprocessingRefusal("authorization_missing", "Loop 25 authorization inactive")
    authorization = decision["authorization"]
    required_true = {
        "loop25_implementation_authorized_now",
        "target_free_fixture_generation_authorized_now",
        "registered_filter_design_authorized_now",
        "registered_numeric_preprocessing_authorized_now",
        "development_partition_open_authorized_now",
        "conditional_qualification_partition_open_authorized_now",
        "report_and_cli_implementation_authorized_now",
    }
    if not all(authorization.get(key) is True for key in required_true):
        raise CausalPreprocessingRefusal("authorization_missing", "Loop 25 scope is incomplete")
    if any(value is not False for key, value in authorization.items() if key not in required_true):
        raise CausalPreprocessingRefusal(
            "real_consumed_target_model_training_network_rw3_or_hardware_access",
            "Loop 25 authorization was widened beyond its frozen scope",
        )
    return decision


def _sos_response(signal: Any, sos: Any, frequencies_hz: Any) -> Any:
    function = getattr(signal, "freqz_sos", None) or getattr(signal, "sosfreqz", None)
    if function is None:
        raise CausalPreprocessingRefusal(
            "unsupported_scipy_version_or_api", "SciPy has no SOS frequency response API"
        )
    _, response = function(sos, worN=frequencies_hz, fs=SOURCE_RATE_HZ)
    return response


def _frequency_delay_report(np: Any, grid: Any, response: Any, probes: list[float]) -> dict[str, Any]:
    phase = np.unwrap(np.angle(response))
    omega = 2.0 * math.pi * grid / SOURCE_RATE_HZ
    group_delay_samples = -np.gradient(phase, omega)
    values = {
        _format_frequency(probe): {
            "samples": float(group_delay_samples[_nearest_index(grid, probe)]),
            "milliseconds": float(
                group_delay_samples[_nearest_index(grid, probe)] / SOURCE_RATE_HZ * 1000.0
            ),
        }
        for probe in probes
    }
    return {
        "method": "negative_unwrapped_phase_gradient",
        "probe_delays": values,
        "effective_signal_timestamp": "unavailable_because_group_delay_is_frequency_dependent",
        "end_to_end_latency_measured": False,
    }


def _response_db_at(grid: Any, values_db: Any, frequency_hz: float) -> float:
    return float(values_db[_nearest_index(grid, frequency_hz)])


def _nearest_index(grid: Any, value: float) -> int:
    np = _require_numpy()
    return int(np.argmin(np.abs(grid - value)))


def _gain_db(np: Any, response: Any) -> Any:
    return 20.0 * np.log10(np.maximum(np.abs(response), np.finfo("float64").tiny))


def _format_frequency(value: float) -> str:
    return f"{float(value):g}Hz"


def _sos_sha256(sos: Any) -> str:
    np = _require_numpy()
    values = np.asarray(sos, dtype="float64")
    payload = {
        "dtype": "float64",
        "shape": list(values.shape),
        "values": values.tolist(),
    }
    return _sha256_json(payload)


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("Loop 25 requires NumPy. Install neurodecodekit[neuro].") from exc
    return np


def _require_scipy_signal():
    try:
        from scipy import signal
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("Loop 25 requires SciPy. Install neurodecodekit[neuro].") from exc
    return signal
