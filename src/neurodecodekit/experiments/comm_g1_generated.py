"""Generated-only COMM-G1 shortcut-discrimination experiment."""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import stat
import tempfile
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

LANE_ID = "COMM-G1"
CONTRACT_PATH = Path("registries/comm_g1_generated_experiment_contract.v0.json")
CONTRACT_SHA256 = "cfdd4f8eeb42543b2d5a6226e0665740304517fd9a8b738c2b1e00a5613e5469"
AMENDMENT_PATH = Path("registries/comm_g1_generated_experiment_amendment_1.v0.json")
AMENDMENT_SHA256 = "a885b8317263bf0bdb5737be2e3bbfca227620d7ca50ef837685d2772d90ef3a"
CONDITIONS = (
    "equal_prior",
    "source_class_prior",
    "cue_plus_timing",
    "EOG_only",
    "oral_EMG_only",
    "peripheral_context_P",
    "selected_EEG_only",
    "posterior_EEG_only",
    "P_plus_residual_EEG",
    "P_plus_deranged_residual_EEG",
)
PARTICIPANTS = tuple(f"gsub-{index:02d}" for index in range(1, 7))
CHANNEL_NAMES = (
    "EEG-C1",
    "EEG-C2",
    "EEG-C3",
    "EEG-C4",
    "EEG-P1",
    "EEG-P2",
    "EEG-F1",
    "EEG-F2",
    "EOG-V1",
    "EOG-V2",
    "EOG-H1",
    "EOG-H2",
    "EMG-ORAL-L",
    "EMG-ORAL-R",
)
CHANNEL_ROLES = (
    "central_EEG",
    "central_EEG",
    "central_EEG",
    "central_EEG",
    "posterior_EEG",
    "posterior_EEG",
    "frontal_EEG",
    "frontal_EEG",
    "EOG",
    "EOG",
    "EOG",
    "EOG",
    "oral_EMG",
    "oral_EMG",
)
CHANNEL_GEOMETRY = (
    (-0.04, 0.00, 0.08),
    (-0.01, 0.00, 0.09),
    (0.01, 0.00, 0.09),
    (0.04, 0.00, 0.08),
    (-0.03, -0.06, 0.07),
    (0.03, -0.06, 0.07),
    (-0.03, 0.06, 0.07),
    (0.03, 0.06, 0.07),
    None,
    None,
    None,
    None,
    None,
    None,
)
BANDS_HZ = ((4.0, 8.0), (8.0, 13.0), (13.0, 20.0), (20.0, 30.0))
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
CAPS = {
    "wall_time_seconds": 180,
    "peak_process_tree_RSS_bytes": 536_870_912,
    "generated_input_bytes_maximum": 33_554_432,
    "private_generated_bytes_maximum": 33_554_432,
    "public_output_bytes_maximum": 1_048_576,
}
CASE_FAMILIES = (
    "residual_EEG_increment",
    "EOG_only",
    "oral_EMG_only",
    "posterior_only",
    "cue_only",
    "timing_only",
    "no_signal",
    "mixed_without_increment",
)


class CommG1Refusal(RuntimeError):
    """Fail-closed COMM-G1 generated experiment refusal."""


@dataclass(frozen=True)
class GeneratedRow:
    item_id: str
    participant_id: str
    session_id: str
    trial_id: str
    repeat_index: int
    outer_fold_id: str
    source_sample_start: int
    source_sample_stop: int
    source_time_start_seconds: float
    source_time_stop_seconds: float
    sampling_rate_hz: int
    channel_names: tuple[str, ...]
    channel_roles: tuple[str, ...]
    channel_geometry: tuple[tuple[float, float, float] | None, ...]
    true_length: int
    padding_mask: tuple[bool, ...]
    cue: tuple[float, ...]
    timing: tuple[float, ...]
    signal: Any


@dataclass(frozen=True)
class FoldCapability:
    held_out_participant: str
    source_rows: tuple[GeneratedRow, ...]
    source_targets: Mapping[str, int]
    held_out_rows: tuple[GeneratedRow, ...]


@dataclass
class OperationLedger:
    residualizer_fits: int = 0
    classifier_or_prior_fits: int = 0
    model_inference_runs: int = 0
    prediction_sets: int = 0
    synthetic_target_deliveries: int = 0
    synthetic_scores: int = 0
    post_target_updates: int = 0


class SealedTargetVault:
    def __init__(self, targets: Mapping[str, int]) -> None:
        self.__targets = dict(targets)
        self.deliveries = 0

    def deliver(self, *, freeze_green: bool) -> dict[str, int]:
        if not freeze_green:
            raise CommG1Refusal("G1-TARGET-PRE-FREEZE")
        if self.deliveries:
            raise CommG1Refusal("G1-TARGET-REPEATED-DELIVERY")
        self.deliveries = 1
        return dict(self.__targets)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _np() -> Any:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("COMM-G1 arrays require: pip install -e '.[classical]'") from exc
    return np


def _model_classes() -> tuple[Any, Any, Any]:
    try:
        from sklearn.linear_model import LogisticRegression, Ridge
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError("COMM-G1 models require: pip install -e '.[classical]'") from exc
    return LogisticRegression, Ridge, StandardScaler


def load_registration(root: str | Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    repository = Path(root) if root is not None else _repo_root()
    values = []
    for path, expected_hash in (
        (CONTRACT_PATH, CONTRACT_SHA256),
        (AMENDMENT_PATH, AMENDMENT_SHA256),
    ):
        payload = (repository / path).read_bytes()
        if _sha256(payload) != expected_hash:
            raise CommG1Refusal("G1-REGISTRATION-HASH")
        value = json.loads(payload)
        if not isinstance(value, dict):
            raise CommG1Refusal("G1-REGISTRATION-SCHEMA")
        values.append(value)
    contract, amendment = values
    if tuple(contract.get("conditions", ())) != CONDITIONS:
        raise CommG1Refusal("G1-CONDITION-INVENTORY")
    if amendment.get("corrected_derangement", {}).get("fixed_points") != 0:
        raise CommG1Refusal("G1-DERANGEMENT-AMENDMENT")
    return contract, amendment


def assert_single_thread_environment() -> None:
    changed = [name for name in THREAD_ENVIRONMENT if os.environ.get(name) != "1"]
    if changed:
        raise CommG1Refusal(f"G1-THREAD-ENV:{','.join(changed)}")


def peak_process_tree_rss_bytes() -> int:
    own = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    children = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    factor = 1 if os.uname().sysname == "Darwin" else 1024
    return int((own + children) * factor)


def _tone(np: Any, frequency: float, amplitude: float, phase: float = 0.0) -> Any:
    axis = np.arange(128, dtype="float64") / 128.0
    return amplitude * np.sin(2.0 * np.pi * frequency * axis + phase)


def generate_fixture(
    case_family: str = "residual_EEG_increment",
    *,
    participants: Sequence[str] = PARTICIPANTS,
) -> tuple[list[GeneratedRow], dict[str, int], int]:
    """Create deterministic fictional arrays; no real paths or labels enter features."""

    if case_family not in CASE_FAMILIES:
        raise CommG1Refusal("G1-FIXTURE-CASE")
    np = _np()
    rows: list[GeneratedRow] = []
    targets: dict[str, int] = {}
    frequencies = (6.0, 10.0, 16.0, 24.0)
    for participant_index, participant in enumerate(participants):
        for session in range(1, 4):
            for repeat in range(2):
                for target in range(4):
                    row_number = len(rows)
                    row_id = f"{participant}-s{session}-r{repeat}-c{target}"
                    rng = np.random.default_rng(10_000 + row_number)
                    signal = rng.normal(0.0, 0.08, (14, 128))
                    phase = 0.07 * participant_index + 0.03 * session + 0.01 * repeat
                    class_tone = _tone(np, frequencies[target], 1.0, phase)
                    nuisance_tone = _tone(np, frequencies[(target + 1) % 4], 1.0, phase)
                    cue = [0.0] * 4
                    timing = [session / 3.0, repeat]
                    if case_family == "residual_EEG_increment":
                        signal[0:4] += 3.0 * class_tone
                    elif case_family == "EOG_only":
                        signal[8:12] += 3.0 * class_tone
                    elif case_family == "oral_EMG_only":
                        signal[12:14] += 3.0 * class_tone
                    elif case_family == "posterior_only":
                        signal[4:6] += 3.0 * class_tone
                    elif case_family == "cue_only":
                        cue[target] = 1.0
                    elif case_family == "timing_only":
                        timing = [target / 3.0, (target * target) / 9.0]
                    elif case_family == "mixed_without_increment":
                        signal[8:12] += 2.5 * class_tone
                        signal[0:4] += 2.5 * class_tone + 0.5 * nuisance_tone
                    row = GeneratedRow(
                        item_id=row_id,
                        participant_id=participant,
                        session_id=f"ses-{session}",
                        trial_id=f"trial-{repeat}-{target}",
                        repeat_index=repeat,
                        outer_fold_id=participant,
                        source_sample_start=row_number * 192,
                        source_sample_stop=row_number * 192 + 128,
                        source_time_start_seconds=row_number * 1.5,
                        source_time_stop_seconds=row_number * 1.5 + 1.0,
                        sampling_rate_hz=128,
                        channel_names=CHANNEL_NAMES,
                        channel_roles=CHANNEL_ROLES,
                        channel_geometry=CHANNEL_GEOMETRY,
                        true_length=128,
                        padding_mask=(False,) * 128,
                        cue=tuple(cue),
                        timing=tuple(timing),
                        signal=signal,
                    )
                    rows.append(row)
                    targets[row_id] = target
    validate_rows(rows)
    expected = len(participants) * 24
    if len(rows) != expected or len(targets) != expected:
        raise CommG1Refusal("G1-FIXTURE-COMPLETENESS")
    return rows, targets, sum(int(row.signal.nbytes) for row in rows)


def validate_rows(rows: Sequence[GeneratedRow]) -> None:
    np = _np()
    if not rows:
        raise CommG1Refusal("G1-ROWS-EMPTY")
    identities: set[str] = set()
    for row in rows:
        if row.item_id in identities:
            raise CommG1Refusal("G1-ITEM-COLLISION")
        identities.add(row.item_id)
        if row.outer_fold_id != row.participant_id:
            raise CommG1Refusal("G1-SPLIT-IDENTITY")
        if row.sampling_rate_hz != 128:
            raise CommG1Refusal("G1-SAMPLING-RATE")
        if row.channel_names != CHANNEL_NAMES or row.channel_roles != CHANNEL_ROLES:
            raise CommG1Refusal("G1-CHANNEL-ROLE")
        if row.channel_geometry != CHANNEL_GEOMETRY:
            raise CommG1Refusal("G1-CHANNEL-GEOMETRY")
        if np.asarray(row.signal).shape != (14, 128):
            raise CommG1Refusal("G1-SIGNAL-SHAPE")
        if row.true_length != 128 or row.padding_mask != (False,) * 128:
            raise CommG1Refusal("G1-MASK-LENGTH")
        if row.source_sample_stop - row.source_sample_start != 128:
            raise CommG1Refusal("G1-SAMPLE-TIMESTAMP")
        if not math.isclose(row.source_time_stop_seconds - row.source_time_start_seconds, 1.0):
            raise CommG1Refusal("G1-TIME-TIMESTAMP")


def causal_log_relative_band_features(signal: Any, *, sampling_rate_hz: int = 128) -> Any:
    """Extract frozen causal features without accepting target or label inputs."""

    np = _np()
    values = np.asarray(signal, dtype="float64")
    if values.ndim != 2 or values.shape[1] != 128 or sampling_rate_hz != 128:
        raise CommG1Refusal("G1-FEATURE-INPUT")
    window = np.hanning(128)
    power = np.abs(np.fft.rfft(values * window, axis=1)) ** 2 / np.sum(window**2)
    frequencies = np.fft.rfftfreq(128, 1.0 / sampling_rate_hz)
    normalizer = power[:, (frequencies >= 2.0) & (frequencies <= 40.0)].sum(axis=1)
    features = []
    for low, high in BANDS_HZ:
        band = power[:, (frequencies >= low) & (frequencies < high)].sum(axis=1)
        features.append(np.log10(band + 1e-18) - np.log10(normalizer + 1e-18))
    return np.stack(features, axis=1)


def feature_views(row: GeneratedRow) -> dict[str, Any]:
    np = _np()
    validate_rows((row,))
    spectral = causal_log_relative_band_features(row.signal)
    central = spectral[0:4].reshape(-1)
    posterior = spectral[4:6].reshape(-1)
    eog = spectral[8:12].reshape(-1)
    oral = spectral[12:14].reshape(-1)
    context = np.concatenate((eog, oral, posterior, row.cue, row.timing))
    return {
        "central": central,
        "posterior": posterior,
        "eog": eog,
        "oral": oral,
        "cue_timing": np.asarray(row.cue + row.timing, dtype="float64"),
        "context": context,
    }


def build_fold_capability(
    rows: Sequence[GeneratedRow], targets: Mapping[str, int], held_out: str
) -> tuple[FoldCapability, dict[str, int]]:
    validate_rows(rows)
    participants = {row.participant_id for row in rows}
    if held_out not in participants:
        raise CommG1Refusal("G1-HELD-OUT-PARTICIPANT")
    if set(targets) != {row.item_id for row in rows}:
        raise CommG1Refusal("G1-TARGET-ROW-MISMATCH")
    source_rows = tuple(row for row in rows if row.participant_id != held_out)
    held_rows = tuple(row for row in rows if row.participant_id == held_out)
    source_targets = {row.item_id: targets[row.item_id] for row in source_rows}
    held_targets = {row.item_id: targets[row.item_id] for row in held_rows}
    capability = FoldCapability(held_out, source_rows, source_targets, held_rows)
    if set(source_targets) & set(held_targets):
        raise CommG1Refusal("G1-CAPABILITY-COLLISION")
    return capability, held_targets


def corrected_source_derangement(
    source_rows: Sequence[GeneratedRow],
    source_targets: Mapping[str, int],
    residuals: Any,
) -> Any:
    """Apply Amendment 1's source-only, no-fixed-point class rotation."""

    np = _np()
    values = np.asarray(residuals, dtype="float64")
    if values.ndim != 2 or values.shape[0] != len(source_rows):
        raise CommG1Refusal("G1-DERANGEMENT-SHAPE")
    by_group: dict[tuple[str, str, int], list[int]] = defaultdict(list)
    for index, row in enumerate(source_rows):
        if row.item_id not in source_targets:
            raise CommG1Refusal("G1-DERANGEMENT-MISSING-SOURCE-TARGET")
        by_group[(row.participant_id, row.session_id, row.repeat_index)].append(index)
    result = np.empty_like(values)
    for indices in by_group.values():
        classes = [source_targets[source_rows[index].item_id] for index in indices]
        if sorted(classes) != [0, 1, 2, 3]:
            raise CommG1Refusal("G1-DERANGEMENT-INCOMPLETE-GROUP")
        by_class = {source_targets[source_rows[index].item_id]: index for index in indices}
        for target_class, destination in by_class.items():
            source = by_class[(target_class + 1) % 4]
            result[destination] = values[source]
    if sorted(map(tuple, result.tolist())) != sorted(map(tuple, values.tolist())):
        raise CommG1Refusal("G1-DERANGEMENT-MARGINAL")
    return result


def _fit_residualizer(source_context: Any, source_central: Any) -> tuple[Any, Any, Any]:
    _, Ridge, StandardScaler = _model_classes()
    x_scaler = StandardScaler().fit(source_context)
    y_scaler = StandardScaler().fit(source_central)
    model = Ridge(alpha=10.0, fit_intercept=True).fit(
        x_scaler.transform(source_context), y_scaler.transform(source_central)
    )
    return x_scaler, y_scaler, model


def _residualize(bundle: tuple[Any, Any, Any], context: Any, central: Any) -> Any:
    x_scaler, y_scaler, model = bundle
    predicted = y_scaler.inverse_transform(model.predict(x_scaler.transform(context)))
    return central - predicted


def _fit_classifier(features: Any, targets: Any) -> tuple[Any, Any]:
    LogisticRegression, _, StandardScaler = _model_classes()
    scaler = StandardScaler().fit(features)
    model = LogisticRegression(
        C=0.1,
        solver="lbfgs",
        max_iter=1000,
        tol=1e-6,
        class_weight=None,
        random_state=0,
    ).fit(scaler.transform(features), targets)
    if getattr(model, "n_iter_", [1001]).max() >= 1000:
        raise CommG1Refusal("G1-MODEL-NONCONVERGENCE")
    return scaler, model


def _condition_features(
    condition: str,
    views: Sequence[dict[str, Any]],
    residuals: Any,
) -> Any:
    np = _np()
    arrays = {
        "cue_plus_timing": [view["cue_timing"] for view in views],
        "EOG_only": [view["eog"] for view in views],
        "oral_EMG_only": [view["oral"] for view in views],
        "peripheral_context_P": [view["context"] for view in views],
        "selected_EEG_only": [view["central"] for view in views],
        "posterior_EEG_only": [view["posterior"] for view in views],
    }
    if condition in arrays:
        return np.stack(arrays[condition])
    context = np.stack([view["context"] for view in views])
    if condition in {"P_plus_residual_EEG", "P_plus_deranged_residual_EEG"}:
        return np.concatenate((context, residuals), axis=1)
    raise CommG1Refusal("G1-CONDITION-FEATURES")


def run_target_blind_predictions(
    rows: Sequence[GeneratedRow], targets: Mapping[str, int]
) -> tuple[list[dict[str, Any]], SealedTargetVault, OperationLedger]:
    np = _np()
    validate_rows(rows)
    prepared_views = {row.item_id: feature_views(row) for row in rows}
    predictions: list[dict[str, Any]] = []
    all_held_targets: dict[str, int] = {}
    ledger = OperationLedger()
    for held_out in sorted({row.participant_id for row in rows}):
        capability, held_targets = build_fold_capability(rows, targets, held_out)
        all_held_targets.update(held_targets)
        source_views = [prepared_views[row.item_id] for row in capability.source_rows]
        held_views = [prepared_views[row.item_id] for row in capability.held_out_rows]
        source_context = np.stack([view["context"] for view in source_views])
        held_context = np.stack([view["context"] for view in held_views])
        source_central = np.stack([view["central"] for view in source_views])
        held_central = np.stack([view["central"] for view in held_views])
        source_y = np.asarray(
            [capability.source_targets[row.item_id] for row in capability.source_rows]
        )
        residualizer = _fit_residualizer(source_context, source_central)
        ledger.residualizer_fits += 1
        source_residual = _residualize(residualizer, source_context, source_central)
        held_residual = _residualize(residualizer, held_context, held_central)
        deranged_source = corrected_source_derangement(
            capability.source_rows, capability.source_targets, source_residual
        )
        counts = Counter(source_y.tolist())
        for condition in CONDITIONS:
            if condition == "equal_prior":
                probabilities = np.full((len(capability.held_out_rows), 4), 0.25)
            elif condition == "source_class_prior":
                ledger.classifier_or_prior_fits += 1
                prior = np.asarray([counts[index] for index in range(4)], dtype="float64")
                prior /= prior.sum()
                probabilities = np.tile(prior, (len(capability.held_out_rows), 1))
            else:
                source_condition_residual = (
                    deranged_source
                    if condition == "P_plus_deranged_residual_EEG"
                    else source_residual
                )
                source_x = _condition_features(
                    condition, source_views, source_condition_residual
                )
                held_x = _condition_features(condition, held_views, held_residual)
                model = _fit_classifier(source_x, source_y)
                ledger.classifier_or_prior_fits += 1
                probabilities = model[1].predict_proba(model[0].transform(held_x))
            probabilities = np.clip(probabilities, 1e-6, 0.999999)
            probabilities /= probabilities.sum(axis=1, keepdims=True)
            ledger.model_inference_runs += 1
            ledger.prediction_sets += 1
            for row, probability in zip(capability.held_out_rows, probabilities, strict=True):
                predictions.append(
                    {
                        "item_id": row.item_id,
                        "participant_id": row.participant_id,
                        "condition": condition,
                        "probabilities": probability.tolist(),
                    }
                )
    if len(predictions) != len(rows) * len(CONDITIONS):
        raise CommG1Refusal("G1-PREDICTION-COMPLETENESS")
    if ledger.residualizer_fits != 6 or ledger.classifier_or_prior_fits != 54:
        raise CommG1Refusal("G1-FIT-SCHEDULE")
    if ledger.model_inference_runs != 60 or ledger.prediction_sets != 60:
        raise CommG1Refusal("G1-INFERENCE-SCHEDULE")
    return predictions, SealedTargetVault(all_held_targets), ledger


def build_prediction_freeze(predictions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if len(predictions) != 1440:
        raise CommG1Refusal("G1-FREEZE-ROW-COUNT")
    payload = _canonical_bytes(list(predictions))
    return {
        "schema_name": "neurodecodekit.comm_g1_prediction_freeze",
        "schema_version": "0.1.0",
        "contract_sha256": CONTRACT_SHA256,
        "amendment_sha256": AMENDMENT_SHA256,
        "prediction_rows": len(predictions),
        "prediction_sets": 60,
        "participants": 6,
        "conditions": list(CONDITIONS),
        "private_prediction_payload_sha256": _sha256(payload),
        "contains_individual_prediction_probability_target_or_participant_outcome": False,
    }


def verify_prediction_freeze(
    predictions: Sequence[Mapping[str, Any]], freeze: Mapping[str, Any]
) -> None:
    expected = build_prediction_freeze(predictions)
    if dict(freeze) != expected:
        raise CommG1Refusal("G1-FREEZE-TAMPER")


def _expect_refusal(
    case_id: str, operation: Callable[[], Any], expected: str | None = None
) -> str:
    try:
        operation()
    except CommG1Refusal as exc:
        if expected is not None and expected not in str(exc):
            raise CommG1Refusal(f"G1-ADVERSARIAL-WRONG-REFUSAL:{case_id}") from exc
        return case_id
    raise CommG1Refusal(f"G1-ADVERSARIAL-ACCEPTED:{case_id}")


def validate_replay_hashes(first: str, second: str) -> None:
    if first != second:
        raise CommG1Refusal("G1-NONDETERMINISTIC-REPLAY")


def exercise_adversarial_refusals(
    rows: Sequence[GeneratedRow],
    targets: Mapping[str, int],
    predictions: Sequence[Mapping[str, Any]],
    freeze: Mapping[str, Any],
) -> list[str]:
    """Trigger the frozen malformed-input families with generated values only."""

    np = _np()
    row = rows[0]
    cases: list[tuple[str, Callable[[], Any], str | None]] = [
        ("A01_empty_rows", lambda: validate_rows(()), "ROWS-EMPTY"),
        ("A02_item_collision", lambda: validate_rows((row, row)), "ITEM-COLLISION"),
        (
            "A03_split_identity",
            lambda: validate_rows((replace(row, outer_fold_id="other"),)),
            "SPLIT-IDENTITY",
        ),
        (
            "A04_sampling_rate",
            lambda: validate_rows((replace(row, sampling_rate_hz=127),)),
            "SAMPLING-RATE",
        ),
        (
            "A05_channel_names",
            lambda: validate_rows((replace(row, channel_names=("bad",) * 14),)),
            "CHANNEL-ROLE",
        ),
        (
            "A06_channel_roles",
            lambda: validate_rows((replace(row, channel_roles=("bad",) * 14),)),
            "CHANNEL-ROLE",
        ),
        (
            "A07_channel_geometry",
            lambda: validate_rows((replace(row, channel_geometry=(None,) * 14),)),
            "CHANNEL-GEOMETRY",
        ),
        (
            "A08_signal_channels",
            lambda: validate_rows((replace(row, signal=np.zeros((13, 128))),)),
            "SIGNAL-SHAPE",
        ),
        (
            "A09_signal_samples",
            lambda: validate_rows((replace(row, signal=np.zeros((14, 127))),)),
            "SIGNAL-SHAPE",
        ),
        (
            "A10_true_length",
            lambda: validate_rows((replace(row, true_length=127),)),
            "MASK-LENGTH",
        ),
        (
            "A11_padding_mask_length",
            lambda: validate_rows((replace(row, padding_mask=(False,) * 127),)),
            "MASK-LENGTH",
        ),
        (
            "A12_padding_mask_value",
            lambda: validate_rows((replace(row, padding_mask=(True,) + (False,) * 127),)),
            "MASK-LENGTH",
        ),
        (
            "A13_sample_timestamp",
            lambda: validate_rows((replace(row, source_sample_stop=row.source_sample_stop + 1),)),
            "SAMPLE-TIMESTAMP",
        ),
        (
            "A14_time_timestamp",
            lambda: validate_rows(
                (replace(row, source_time_stop_seconds=row.source_time_stop_seconds + 0.1),)
            ),
            "TIME-TIMESTAMP",
        ),
        (
            "A15_feature_rank",
            lambda: causal_log_relative_band_features(np.zeros(128)),
            "FEATURE-INPUT",
        ),
        (
            "A16_feature_samples",
            lambda: causal_log_relative_band_features(np.zeros((14, 127))),
            "FEATURE-INPUT",
        ),
        (
            "A17_feature_rate",
            lambda: causal_log_relative_band_features(row.signal, sampling_rate_hz=127),
            "FEATURE-INPUT",
        ),
        (
            "A18_unknown_fixture",
            lambda: generate_fixture("unknown"),
            "FIXTURE-CASE",
        ),
        (
            "A19_unknown_held_out",
            lambda: build_fold_capability(rows, targets, "unknown"),
            "HELD-OUT-PARTICIPANT",
        ),
        (
            "A20_missing_target",
            lambda: build_fold_capability(rows, dict(list(targets.items())[1:]), row.participant_id),
            "TARGET-ROW-MISMATCH",
        ),
        (
            "A21_extra_target",
            lambda: build_fold_capability(
                rows, {**targets, "extra": 0}, row.participant_id
            ),
            "TARGET-ROW-MISMATCH",
        ),
        (
            "A22_derangement_rank",
            lambda: corrected_source_derangement(rows[:24], dict(list(targets.items())[:24]), np.zeros(24)),
            "DERANGEMENT-SHAPE",
        ),
        (
            "A23_derangement_rows",
            lambda: corrected_source_derangement(
                rows[:24], dict(list(targets.items())[:24]), np.zeros((23, 2))
            ),
            "DERANGEMENT-SHAPE",
        ),
        (
            "A24_derangement_missing_target",
            lambda: corrected_source_derangement(
                rows[:24], dict(list(targets.items())[1:24]), np.zeros((24, 2))
            ),
            "MISSING-SOURCE-TARGET",
        ),
        (
            "A25_derangement_incomplete_group",
            lambda: corrected_source_derangement(
                rows[:23], dict(list(targets.items())[:23]), np.zeros((23, 2))
            ),
            "INCOMPLETE-GROUP",
        ),
        (
            "A26_invalid_condition",
            lambda: _condition_features("unknown", [feature_views(row)], np.zeros((1, 16))),
            "CONDITION-FEATURES",
        ),
        (
            "A27_freeze_row_count",
            lambda: build_prediction_freeze(predictions[:-1]),
            "FREEZE-ROW-COUNT",
        ),
        (
            "A28_freeze_tamper",
            lambda: verify_prediction_freeze(
                [
                    {**predictions[0], "probabilities": [0.7, 0.1, 0.1, 0.1]},
                    *predictions[1:],
                ],
                freeze,
            ),
            "FREEZE-TAMPER",
        ),
        (
            "A29_replay_mismatch",
            lambda: validate_replay_hashes("a" * 64, "b" * 64),
            "NONDETERMINISTIC-REPLAY",
        ),
    ]
    refusals = [_expect_refusal(case_id, operation, expected) for case_id, operation, expected in cases]
    vault = SealedTargetVault(targets)
    refusals.append(
        _expect_refusal(
            "A30_pre_freeze_target_delivery",
            lambda: vault.deliver(freeze_green=False),
            "TARGET-PRE-FREEZE",
        )
    )
    delivered_vault = SealedTargetVault(targets)
    delivered_vault.deliver(freeze_green=True)
    refusals.append(
        _expect_refusal(
            "A31_repeated_target_delivery",
            lambda: delivered_vault.deliver(freeze_green=True),
            "TARGET-REPEATED-DELIVERY",
        )
    )
    missing_targets = dict(targets)
    missing_targets.pop(next(iter(missing_targets)))
    refusals.append(
        _expect_refusal(
            "A32_scorer_row_mismatch",
            lambda: score_predictions(predictions, missing_targets, freeze),
            "SCORER-ROW-MISMATCH",
        )
    )
    malformed_predictions = [dict(value) for value in predictions]
    malformed_predictions[0] = {**malformed_predictions[0], "probabilities": [0.5, 0.5]}
    malformed_freeze = build_prediction_freeze(malformed_predictions)
    refusals.append(
        _expect_refusal(
            "A33_scorer_dimension",
            lambda: score_predictions(malformed_predictions, targets, malformed_freeze),
            "SCORER-DIMENSION",
        )
    )
    with tempfile.TemporaryDirectory() as directory:
        existing = Path(directory) / "existing.json"
        existing.write_bytes(b"x")
        refusals.append(
            _expect_refusal(
                "A34_output_clobber",
                lambda: _write_no_clobber(existing, b"y"),
                "OUTPUT-CLOBBER",
            )
        )
        directory_path = Path(directory) / "directory"
        directory_path.mkdir()
        refusals.append(
            _expect_refusal(
                "A35_nonregular_inspection",
                lambda: _regular_no_follow(directory_path),
                "OUTPUT-FILE-TYPE",
            )
        )
    if len(refusals) < 30 or len(refusals) != len(set(refusals)):
        raise CommG1Refusal("G1-ADVERSARIAL-COMPLETENESS")
    return refusals


def score_predictions(
    predictions: Sequence[Mapping[str, Any]],
    targets: Mapping[str, int],
    freeze: Mapping[str, Any],
) -> dict[str, Any]:
    verify_prediction_freeze(predictions, freeze)
    by_condition: dict[str, list[float]] = defaultdict(list)
    by_participant_condition: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in predictions:
        item_id = row["item_id"]
        if item_id not in targets:
            raise CommG1Refusal("G1-SCORER-ROW-MISMATCH")
        target = targets[item_id]
        probabilities = row["probabilities"]
        if len(probabilities) != 4:
            raise CommG1Refusal("G1-SCORER-DIMENSION")
        loss = -math.log(max(float(probabilities[target]), 1e-6))
        condition = str(row["condition"])
        participant = str(row["participant_id"])
        by_condition[condition].append(loss)
        by_participant_condition[(participant, condition)].append(loss)
    means = {key: sum(values) / len(values) for key, values in by_condition.items()}
    candidate = "P_plus_residual_EEG"
    deranged = "P_plus_deranged_residual_EEG"
    delta_context = means["peripheral_context_P"] - means[candidate]
    delta_deranged = means[deranged] - means[candidate]
    participant_deltas = []
    for participant in PARTICIPANTS:
        candidate_loss = by_participant_condition[(participant, candidate)]
        deranged_loss = by_participant_condition[(participant, deranged)]
        participant_deltas.append(
            sum(deranged_loss) / len(deranged_loss)
            - sum(candidate_loss) / len(candidate_loss)
        )
    positive = sum(value > 0.0 for value in participant_deltas)
    if delta_context >= 0.1 and delta_deranged >= 0.1 and positive == 6:
        route = "COMM-G1-R1"
    elif delta_context > 0.0 or delta_deranged > 0.0:
        route = "COMM-G1-R2"
    else:
        route = "COMM-G1-R3"
    return {
        "route": route,
        "condition_log_loss": means,
        "candidate_delta_over_P": delta_context,
        "candidate_delta_over_deranged": delta_deranged,
        "positive_participants": positive,
        "scientific_value": "none_generated_engineering_only",
    }


def _fixture_fingerprint(rows: Sequence[GeneratedRow], targets: Mapping[str, int]) -> str:
    np = _np()
    digest = hashlib.sha256()
    for row in rows:
        metadata = {
            "item_id": row.item_id,
            "participant_id": row.participant_id,
            "session_id": row.session_id,
            "trial_id": row.trial_id,
            "repeat_index": row.repeat_index,
            "target": targets[row.item_id],
        }
        digest.update(_canonical_bytes(metadata))
        digest.update(np.asarray(row.signal, dtype="<f8").tobytes(order="C"))
    return digest.hexdigest()


def validate_shortcut_fixture(
    case_family: str, rows: Sequence[GeneratedRow], targets: Mapping[str, int]
) -> dict[str, Any]:
    """Verify shortcut placement without adding an unregistered model fit."""

    np = _np()
    if case_family not in CASE_FAMILIES[1:]:
        raise CommG1Refusal("G1-SHORTCUT-CASE")
    views = [feature_views(row) for row in rows]
    groups = {
        "central": np.stack([view["central"] for view in views]),
        "posterior": np.stack([view["posterior"] for view in views]),
        "eog": np.stack([view["eog"] for view in views]),
        "oral": np.stack([view["oral"] for view in views]),
        "cue_timing": np.stack([view["cue_timing"] for view in views]),
    }
    y = np.asarray([targets[row.item_id] for row in rows])

    def class_spread(values: Any) -> float:
        means = np.stack([values[y == target].mean(axis=0) for target in range(4)])
        return float(np.var(means, axis=0).sum())

    spreads = {name: class_spread(values) for name, values in groups.items()}
    expected = {
        "EOG_only": "eog",
        "oral_EMG_only": "oral",
        "posterior_only": "posterior",
        "cue_only": "cue_timing",
        "timing_only": "cue_timing",
    }
    if case_family in expected:
        winner = max(spreads, key=spreads.get)
        if winner != expected[case_family]:
            raise CommG1Refusal("G1-SHORTCUT-PLACEMENT")
    elif case_family == "no_signal":
        if max(spreads.values()) > 0.08:
            raise CommG1Refusal("G1-NO-SIGNAL-FIXTURE")
    elif case_family == "mixed_without_increment":
        if spreads["eog"] <= 0.1 or spreads["central"] <= 0.1:
            raise CommG1Refusal("G1-MIXED-FIXTURE")
    return {
        "status": "passed_targeted_shortcut_fixture_without_model_fit",
        "largest_class_spread_group": max(spreads, key=spreads.get),
        "class_spread_fingerprint": {
            name: round(value, 12) for name, value in sorted(spreads.items())
        },
    }


def _regular_no_follow(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise CommG1Refusal("G1-OUTPUT-FILE-TYPE")
    return info


def _write_no_clobber(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise CommG1Refusal("G1-OUTPUT-CLOBBER")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise CommG1Refusal("G1-OUTPUT-TEMP-CLOBBER")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise CommG1Refusal("G1-OUTPUT-RACE")
        os.rename(temporary, path)
        if _regular_no_follow(path).st_size != len(payload):
            raise CommG1Refusal("G1-OUTPUT-READBACK")
    finally:
        if temporary.exists() and not temporary.is_symlink():
            temporary.unlink()


def _result_payload(result: dict[str, Any]) -> bytes:
    previous = -1
    for _ in range(8):
        payload = _canonical_bytes(result)
        result["measurements"]["public_output_bytes"] = len(payload)
        if len(payload) == previous:
            return _canonical_bytes(result)
        previous = len(payload)
    raise CommG1Refusal("G1-PUBLIC-BYTE-ACCOUNTING")


def plan() -> dict[str, Any]:
    return {
        "lane_id": LANE_ID,
        "generated_only": True,
        "participants": 6,
        "rows": 144,
        "conditions": list(CONDITIONS),
        "parameter_update_fits": 60,
        "prediction_sets": 60,
        "prediction_rows": 1440,
        "real_or_private_operations": 0,
        "scientific_value": "none_generated_engineering_only",
    }


def run_generated_qualification(
    output_path: str | Path,
    *,
    root: str | Path | None = None,
    remote_proof_collector: Callable[[str | Path], Mapping[str, Any]] | None = None,
    peak_rss_reader: Callable[[], int] = peak_process_tree_rss_bytes,
) -> dict[str, Any]:
    """Run the bounded generated matrix; caller supplies a green-proof collector."""

    assert_single_thread_environment()
    repository = Path(root) if root is not None else _repo_root()
    load_registration(repository)
    output = Path(output_path).expanduser().absolute()
    if ".." in Path(output_path).parts or output.exists() or output.is_symlink():
        raise CommG1Refusal("G1-OUTPUT-CLOBBER")
    lowered = {part.lower() for part in output.parts}
    if lowered.intersection({"data", ".codex_work"}):
        raise CommG1Refusal("G1-PROTECTED-OUTPUT-ROOT")
    if output.parent.is_symlink():
        raise CommG1Refusal("G1-OUTPUT-SYMLINK-PARENT")
    from neurodecodekit.experiments import dreyer_c5r_1 as proof_tools

    collector = remote_proof_collector or proof_tools.collect_remote_green_proof
    try:
        proof = proof_tools.validate_remote_green_proof(dict(collector(repository)))
    except (proof_tools.DreyerExperimentRefusal, KeyError, TypeError) as exc:
        raise CommG1Refusal("G1-REMOTE-GREEN-PROOF-FAILED") from exc
    preflight_rss = peak_rss_reader()
    if type(preflight_rss) is not int or preflight_rss < 0:
        raise CommG1Refusal("G1-RSS-MEASUREMENT")
    if preflight_rss > CAPS["peak_process_tree_RSS_bytes"]:
        raise CommG1Refusal("G1-RSS-CAP")
    started = time.monotonic()
    case_results: dict[str, Any] = {}
    positive_predictions: list[dict[str, Any]] | None = None
    positive_rows: list[GeneratedRow] | None = None
    positive_targets: dict[str, int] | None = None
    positive_vault: SealedTargetVault | None = None
    positive_ledger: OperationLedger | None = None
    generated_input_bytes = 0
    private_prediction_bytes = 0
    replay_hashes: list[str] = []
    for case_family in CASE_FAMILIES:
        rows, targets, input_bytes = generate_fixture(case_family)
        replay_rows, replay_targets, replay_bytes = generate_fixture(case_family)
        first_hash = _fixture_fingerprint(rows, targets)
        second_hash = _fixture_fingerprint(replay_rows, replay_targets)
        if first_hash != second_hash or input_bytes != replay_bytes:
            raise CommG1Refusal("G1-NONDETERMINISTIC-REPLAY")
        replay_hashes.append(first_hash)
        generated_input_bytes += input_bytes + replay_bytes
        if case_family == "residual_EEG_increment":
            predictions, vault, ledger = run_target_blind_predictions(rows, targets)
            freeze = build_prediction_freeze(predictions)
            delivered = vault.deliver(freeze_green=True)
            ledger.synthetic_target_deliveries += 1
            score = score_predictions(predictions, delivered, freeze)
            ledger.synthetic_scores += 1
            case_results[case_family] = {
                "route": score["route"],
                "candidate_delta_over_P": score["candidate_delta_over_P"],
                "candidate_delta_over_deranged": score["candidate_delta_over_deranged"],
                "positive_participants": score["positive_participants"],
                "fixture_sha256": first_hash,
            }
            private_prediction_bytes = len(_canonical_bytes(predictions))
            positive_predictions = predictions
            positive_rows = rows
            positive_targets = targets
            positive_vault = vault
            positive_ledger = ledger
        else:
            case_results[case_family] = {
                **validate_shortcut_fixture(case_family, rows, targets),
                "fixture_sha256": first_hash,
            }
    if case_results["residual_EEG_increment"]["route"] != "COMM-G1-R1":
        raise CommG1Refusal("G1-POSITIVE-CONTROL")
    assert positive_predictions is not None
    assert positive_rows is not None
    assert positive_targets is not None
    assert positive_vault is not None
    assert positive_ledger is not None
    premature_refusals = 0
    fresh_vault = SealedTargetVault(positive_targets)
    try:
        fresh_vault.deliver(freeze_green=False)
    except CommG1Refusal:
        premature_refusals = 1
    repeated_refusals = 0
    try:
        positive_vault.deliver(freeze_green=True)
    except CommG1Refusal:
        repeated_refusals = 1
    freeze = build_prediction_freeze(positive_predictions)
    adversarial_refusal_ids = exercise_adversarial_refusals(
        positive_rows,
        positive_targets,
        positive_predictions,
        freeze,
    )
    tampered = [dict(row) for row in positive_predictions]
    tampered[0] = {**tampered[0], "probabilities": [0.7, 0.1, 0.1, 0.1]}
    tamper_refusals = 0
    try:
        verify_prediction_freeze(tampered, freeze)
    except CommG1Refusal:
        tamper_refusals = 1
    runtime = time.monotonic() - started
    peak_rss = peak_rss_reader()
    if type(peak_rss) is not int or peak_rss < 0:
        raise CommG1Refusal("G1-RSS-MEASUREMENT")
    if runtime > CAPS["wall_time_seconds"]:
        raise CommG1Refusal("G1-RUNTIME-CAP")
    if peak_rss > CAPS["peak_process_tree_RSS_bytes"]:
        raise CommG1Refusal("G1-RSS-CAP")
    if generated_input_bytes > CAPS["generated_input_bytes_maximum"]:
        raise CommG1Refusal("G1-INPUT-CAP")
    if private_prediction_bytes > CAPS["private_generated_bytes_maximum"]:
        raise CommG1Refusal("G1-PRIVATE-CAP")
    result = {
        "schema_name": "neurodecodekit.comm_g1_generated_qualification_result",
        "schema_version": "0.1.0",
        "lane_id": LANE_ID,
        "status": "passed_generated_only_no_scientific_value",
        "registration": {
            "contract_sha256": CONTRACT_SHA256,
            "amendment_sha256": AMENDMENT_SHA256,
        },
        "implementation_proof": proof,
        "cases": case_results,
        "replay_hashes": replay_hashes,
        "firewall_refusals": {
            "pre_freeze_target_delivery": premature_refusals,
            "repeated_target_delivery": repeated_refusals,
            "prediction_tamper": tamper_refusals,
        },
        "adversarial_qualification": {
            "refusal_count": len(adversarial_refusal_ids),
            "refusal_ids": adversarial_refusal_ids,
            "minimum_required": 30,
        },
        "positive_schedule": {
            "residualizer_fits": positive_ledger.residualizer_fits,
            "classifier_or_prior_fits": positive_ledger.classifier_or_prior_fits,
            "total_parameter_update_fits": 60,
            "model_inference_runs": positive_ledger.model_inference_runs,
            "prediction_sets": positive_ledger.prediction_sets,
            "prediction_rows": len(positive_predictions),
            "synthetic_target_deliveries": positive_ledger.synthetic_target_deliveries,
            "synthetic_scores": positive_ledger.synthetic_scores,
            "post_target_updates": positive_ledger.post_target_updates,
        },
        "measurements": {
            "runtime_seconds": runtime,
            "peak_process_tree_RSS_bytes": peak_rss,
            "generated_input_bytes": generated_input_bytes,
            "private_generated_prediction_bytes_maximum": private_prediction_bytes,
            "producer_causal": True,
            "required_context_seconds": 1.0,
            "right_context_seconds": 0.0,
            "end_to_end_latency_measured": False,
        },
        "access_counters": {
            "real_or_private_path_reads": 0,
            "network_bytes": 0,
            "real_signal_samples": 0,
            "real_targets_or_labels": 0,
            "real_training_runs": 0,
            "real_model_inference_runs": 0,
            "provider_calls": 0,
            "stream_or_device_operations": 0,
            "release_operations": 0,
            "scientific_claim_upgrades": 0,
        },
        "claim_boundary": {
            "scientific_value": "none_generated_engineering_only",
            "real_EEG_accessed": False,
            "communication_decoding_established": False,
            "EEG_beyond_peripheral_controls_established": False,
            "unseen_person_generalization_established": False,
            "live_neural_decoding_established": False,
        },
    }
    payload = _result_payload(result)
    if len(payload) > CAPS["public_output_bytes_maximum"]:
        raise CommG1Refusal("G1-PUBLIC-OUTPUT-CAP")
    _write_no_clobber(output, payload)
    return result


def inspect_result(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    _regular_no_follow(source)
    value = json.loads(source.read_bytes())
    if value.get("schema_name") != "neurodecodekit.comm_g1_generated_qualification_result":
        raise CommG1Refusal("G1-INSPECT-SCHEMA")
    return {
        "lane_id": value["lane_id"],
        "status": value["status"],
        "positive_route": value["cases"]["residual_EEG_increment"]["route"],
        "case_routes": {
            key: case["route"]
            for key, case in value["cases"].items()
            if "route" in case
        },
        "structural_case_statuses": {
            key: case["status"]
            for key, case in value["cases"].items()
            if "status" in case
        },
        "measurements": value["measurements"],
        "claim_boundary": value["claim_boundary"],
    }
