"""Fixed, calibration-only comparison of evoked and repetition EEG power.

All functions consume arrays, never files or online targets. Power is computed
before logarithms: averaging repetition powers is not averaging log powers.
The caller preflights all six recordings before model work and preserves every
arm and condition; this module does not authorize a real-data invocation.
"""

from __future__ import annotations

from neurodecodekit.evaluation.speech_reproduction import (
    BANDS,
    _matrix,
    _metrics,
    _numpy,
    _probabilities,
    _standardized_block,
    ridge_probabilities,
)
from neurodecodekit.experiments.speech_auxiliary_discovery import (
    N_TRIALS,
    SCHEMES,
    SEED,
    _split_hash,
    _split_plan,
    preflight_calibration,
)


N_CHANNELS = 128
N_REPETITIONS = 5
N_SAMPLES = 320
SFREQ = 256.0
N_AUXILIARY_FEATURES = 392
N_EEG_FEATURES = N_CHANNELS * len(BANDS)
REPRESENTATIONS = ("raw_evoked", "raw_repetition", "filtered_evoked", "filtered_repetition")
ARMS = (
    "N", "N_shuffled", "uniform", "training_prior",
    *(arm for representation in REPRESENTATIONS for arm in (
        representation, representation + "_shuffled", "N_" + representation,
        "N_" + representation + "_deranged", "N_" + representation + "_shuffled")),
)
PRIMARY_ARM = "N_filtered_repetition"
PRIMARY_COMPARATORS = (
    "N", "N_filtered_evoked", "N_filtered_repetition_deranged",
    "N_filtered_repetition_shuffled", "uniform", "training_prior",
)
ADAPTIVE_REPRESENTATIONS = (
    "raw_repetition", "normalized_repetition", "filtered_repetition",
    "sham_normalized_repetition", "sham_filtered_repetition",
)
ADAPTIVE_ARMS = (
    "N", "N_shuffled", "uniform", "training_prior",
    *(arm for representation in ADAPTIVE_REPRESENTATIONS for arm in (
        representation, representation + "_shuffled", "N_" + representation,
        "N_" + representation + "_deranged", "N_" + representation + "_shuffled")),
)
ADAPTIVE_PRIMARY_ARM = "sham_filtered_repetition"
ADAPTIVE_PRIMARY_COMPARATORS = (
    "sham_normalized_repetition", "sham_filtered_repetition_shuffled", "uniform", "training_prior",
)
ADAPTIVE_SECONDARY_ARM = "N_filtered_repetition"
ADAPTIVE_SECONDARY_COMPARATORS = (
    "N", "N_normalized_repetition", "N_sham_filtered_repetition",
    "N_filtered_repetition_deranged", "N_filtered_repetition_shuffled", "uniform", "training_prior",
)
TIME_FREQUENCY_FEATURE_COUNTS = {
    "full_all": 768,
    "band_2_4": 128,
    "band_4_8": 128,
    "band_8_13": 128,
    "band_13_30": 128,
    "band_30_60": 128,
    "band_60_118": 128,
    "early_all": 768,
    "late_all": 768,
}
TIME_FREQUENCY_REPRESENTATIONS = tuple(TIME_FREQUENCY_FEATURE_COUNTS)
TIME_FREQUENCY_ARMS = (
    "N", "N_shuffled", "A", "A_shuffled", "uniform", "training_prior",
    *(arm for representation in TIME_FREQUENCY_REPRESENTATIONS for arm in (
        representation, representation + "_shuffled", "A_" + representation,
        "A_" + representation + "_deranged", "A_" + representation + "_shuffled")),
)
TIME_FREQUENCY_PRIMARY_ARM = "A_full_all"
TIME_FREQUENCY_PRIMARY_COMPARATORS = (
    "A", "N", "A_full_all_deranged", "A_full_all_shuffled", "uniform", "training_prior",
)


def _band_energies(values):
    """Unlogged, source-matched one-sided 320-point rectangular-window power."""
    np = _numpy()
    frequencies = np.fft.rfftfreq(N_SAMPLES, d=1.0 / SFREQ)
    energies = np.abs(np.fft.rfft(values, axis=-1)) ** 2 / N_SAMPLES**2
    energies[..., 1:-1] *= 2.0
    bands = []
    for lower, upper in BANDS:
        mask = (frequencies >= lower) & (frequencies < upper)
        if upper == BANDS[-1][1]:
            mask |= frequencies == upper
        bands.append(energies[..., mask].sum(axis=-1))
    return np.stack(bands, axis=-1)


def paired_power_features(full_trials):
    """Return matched 768-column evoked/repetition features and aggregate powers.

    Input is source-cropped ``[trials, 128, 1600]``, normally float32. Conversion
    to float64 precedes every averaging and Fourier operation. The last axis is
    five consecutive 320-sample repetitions. Output features are channel-major,
    with the same six BANDS, frequency bounds and power normalization as the
    original ``_log_band_energies``. No window taper or full-trial FFT is used.

    Diagnostic sums are additive across streaming calls. Recompute each pooled
    coherent/total ratio from pooled sums; do not average per-call ratios. A
    zero total power yields JSON null, not an invented ratio. No row labels or
    per-trial diagnostic values are retained.
    """
    np = _numpy()
    trials = np.asarray(full_trials, dtype=np.float64)
    if (trials.ndim != 3 or trials.shape[0] == 0
            or trials.shape[1:] != (N_CHANNELS, N_REPETITIONS * N_SAMPLES)):
        raise ValueError("Power inputs must have shape (trials, 128, 1600)")
    if not np.isfinite(trials).all():
        raise ValueError("Power inputs must contain only finite samples")
    repetitions = trials.reshape(len(trials), N_CHANNELS, N_REPETITIONS, N_SAMPLES)
    coherent = _band_energies(repetitions.mean(axis=2))
    total = _band_energies(repetitions).mean(axis=2)
    if not np.isfinite(coherent).all() or not np.isfinite(total).all():
        raise ValueError("Power computation produced nonfinite energies")
    coherent_sum = coherent.sum(axis=(0, 1))
    total_sum = total.sum(axis=(0, 1))
    if not np.isfinite(coherent_sum).all() or not np.isfinite(total_sum).all():
        raise ValueError("Power diagnostics produced nonfinite sums")
    floor = np.finfo(float).tiny
    return {
        "evoked": np.log(np.maximum(coherent, floor)).reshape(len(trials), N_EEG_FEATURES),
        "repetition": np.log(np.maximum(total, floor)).reshape(len(trials), N_EEG_FEATURES),
        "diagnostics": {
            "n_trials": int(len(trials)),
            "n_channels": N_CHANNELS,
            "repetitions": N_REPETITIONS,
            "samples_per_repetition": N_SAMPLES,
            "bands": [list(band) for band in BANDS],
            "coherent_band_power_sum": coherent_sum.tolist(),
            "total_band_power_sum": total_sum.tolist(),
            "coherent_to_total_band_power_ratio": [
                float(numerator / denominator) if denominator > 0 else None
                for numerator, denominator in zip(coherent_sum, total_sum)
            ],
        },
    }


def fold_derangement_indices(train, validation):
    """Original EEG donor rows: roll one position separately inside each split.

    This is a correspondence control, not an independent sample or a permutation
    significance test. In particular, held-out EEG is never a training donor.
    """
    np = _numpy()
    groups = (np.asarray(train), np.asarray(validation))
    for group in groups:
        if (group.ndim != 1 or len(group) < 2 or group.dtype.kind not in "iu"
                or len(np.unique(group)) != len(group) or (group < 0).any()):
            raise ValueError("Derangement requires distinct nonnegative integer rows per split")
    if np.intersect1d(*groups).size:
        raise ValueError("Derangement training and validation rows must be disjoint")
    return tuple(np.roll(group, 1) for group in groups)


def run_pair_power_discovery(
    auxiliary, eeg_features, calibration_labels, *, pair_id, progress=None, mode="repetition_power"
):
    """Return a JSON-safe pair report and local-only OOF arrays for fixed arms.

    ``eeg_features`` contains exactly REPRESENTATIONS, each ``[100,768]``;
    auxiliary has the original ``[100,392]`` features. Both fixed split schemes
    and their label shuffles are reused unchanged. Each auxiliary/EEG block is
    independently standardized using original training rows only and divided
    by sqrt(its feature count). Derangement then rolls only standardized EEG,
    independently within training and validation, leaving auxiliaries aligned.

    The default mode retains the original four views, 24 arms and endpoint.
    Explicit ``adaptive_attribution`` instead requires ADAPTIVE_REPRESENTATIONS,
    yielding 29 arms. Its primary comparison uses sham features alone; the real
    filtered-EEG joint comparison is reported separately as secondary. This
    function does not construct or verify the caller-owned fixed sham template.

    Explicit ``time_frequency`` requires nine fixed views and 692 auxiliary
    columns: original N first, then 150 raw and 150 normalized repetition-power
    features. N retains its original 392-column block; A standardizes all 692
    columns as one block. Joint arms use A. Each view's declared feature count
    determines its EEG-block normalization, without selecting a winning view.
    """
    if mode == "repetition_power":
        representations, arms = REPRESENTATIONS, ARMS
        primary_arm, primary_comparators = PRIMARY_ARM, PRIMARY_COMPARATORS
    elif mode == "adaptive_attribution":
        representations, arms = ADAPTIVE_REPRESENTATIONS, ADAPTIVE_ARMS
        primary_arm, primary_comparators = ADAPTIVE_PRIMARY_ARM, ADAPTIVE_PRIMARY_COMPARATORS
    elif mode == "time_frequency":
        representations, arms = TIME_FREQUENCY_REPRESENTATIONS, TIME_FREQUENCY_ARMS
        primary_arm, primary_comparators = TIME_FREQUENCY_PRIMARY_ARM, TIME_FREQUENCY_PRIMARY_COMPARATORS
    else:
        raise ValueError("Mode must be repetition_power, adaptive_attribution or time_frequency")
    time_frequency = mode == "time_frequency"
    auxiliary_count = 692 if time_frequency else N_AUXILIARY_FEATURES
    eeg_counts = TIME_FREQUENCY_FEATURE_COUNTS if time_frequency else {
        name: N_EEG_FEATURES for name in representations
    }
    joint_prefix = "A_" if time_frequency else "N_"
    np = _numpy()
    auxiliary = _matrix(auxiliary, "calibration auxiliary features")
    if auxiliary.shape != (N_TRIALS, auxiliary_count):
        raise ValueError(f"Calibration auxiliary features must have shape (100, {auxiliary_count})")
    if set(eeg_features) != set(representations):
        count = "nine" if time_frequency else ("four" if mode == "repetition_power" else "five")
        raise ValueError(f"EEG features must contain exactly the {count} fixed representations")
    eeg = {name: _matrix(eeg_features[name], name) for name in representations}
    if time_frequency and any(matrix.shape != (N_TRIALS, eeg_counts[name]) for name, matrix in eeg.items()):
        raise ValueError("Time-frequency EEG shapes must match each declared view feature count")
    if not time_frequency and any(matrix.shape != (N_TRIALS, N_EEG_FEATURES) for matrix in eeg.values()):
        raise ValueError("Every EEG representation must have shape (100, 768)")
    if not isinstance(pair_id, str) or not pair_id:
        raise ValueError("A nonempty pair_id is required")
    labels, plans, report = _split_plan(calibration_labels)
    report.update({
        "pair_id": pair_id,
        "status": "calibration_only_discovery",
        "confirmatory_result": False,
        "arms": list(arms),
        "representations": list(representations),
        "primary_arm": primary_arm,
        "primary_comparators": list(primary_comparators),
        "n_auxiliary_features": auxiliary_count,
        "n_eeg_features_per_representation": dict(eeg_counts) if time_frequency else N_EEG_FEATURES,
        "settings": {
            "ridge_penalty": 1.0,
            "intercept_penalized": False,
            "standardization": "original fold training rows only, per feature",
            "dimension_normalization": "separate auxiliary and EEG blocks, sqrt(block feature count)",
            "shuffle_scope": "training labels only, same permutation across all arms in each fold",
            "derangement_scope": "one-position EEG cyclic shift separately inside training and validation",
            "derangement_scaling": "scale on original training rows before permutation",
            "probabilities": "softmax of fixed one-hot ridge outputs, no calibration",
            "endpoint": "pooled original-trial out-of-fold class-macro log loss",
            "claim_ceiling": "exploratory within-recording prediction, not causal or confirmatory",
        },
    })
    if mode == "adaptive_attribution":
        report.update({
            "mode": mode,
            "secondary_arm": ADAPTIVE_SECONDARY_ARM,
            "secondary_comparators": list(ADAPTIVE_SECONDARY_COMPARATORS),
        })
    if time_frequency:
        report.update({"mode": mode, "auxiliary_feature_counts": {"N": 392, "A": 692}})
    out_of_fold = {}
    for scheme, folds in plans.items():
        predictions = {arm: np.full((N_TRIALS, 5), np.nan) for arm in arms}
        for fold, (train, validation) in enumerate(folds):
            if progress is not None:
                progress({"event": "fold_start", "pair_id": pair_id, "scheme": scheme, "fold": fold})
            fold_record = report["schemes"][scheme]["folds"][fold]
            donors = fold_derangement_indices(train, validation)
            fold_record["eeg_derangement_indices_sha256"] = _split_hash(*donors)
            train_order = np.roll(np.arange(len(train)), 1)
            validation_order = np.roll(np.arange(len(validation)), 1)
            truth = labels[train]
            shuffled = truth[np.random.default_rng(fold_record["shuffle_seed"]).permutation(len(train))]
            auxiliary_train, auxiliary_test = _standardized_block(
                auxiliary[train, :N_AUXILIARY_FEATURES], auxiliary[validation, :N_AUXILIARY_FEATURES])
            predictions["N"][validation] = ridge_probabilities(auxiliary_train, truth, auxiliary_test)
            predictions["N_shuffled"][validation] = ridge_probabilities(auxiliary_train, shuffled, auxiliary_test)
            if time_frequency:
                auxiliary_train, auxiliary_test = _standardized_block(auxiliary[train], auxiliary[validation])
                predictions["A"][validation] = ridge_probabilities(auxiliary_train, truth, auxiliary_test)
                predictions["A_shuffled"][validation] = ridge_probabilities(auxiliary_train, shuffled, auxiliary_test)
            for name, matrix in eeg.items():
                eeg_train, eeg_test = _standardized_block(matrix[train], matrix[validation])
                joint_train = np.concatenate((auxiliary_train, eeg_train), axis=1)
                joint_test = np.concatenate((auxiliary_test, eeg_test), axis=1)
                predictions[name][validation] = ridge_probabilities(eeg_train, truth, eeg_test)
                predictions[name + "_shuffled"][validation] = ridge_probabilities(eeg_train, shuffled, eeg_test)
                predictions[joint_prefix + name][validation] = ridge_probabilities(joint_train, truth, joint_test)
                predictions[joint_prefix + name + "_deranged"][validation] = ridge_probabilities(
                    np.concatenate((auxiliary_train, eeg_train[train_order]), axis=1), truth,
                    np.concatenate((auxiliary_test, eeg_test[validation_order]), axis=1))
                predictions[joint_prefix + name + "_shuffled"][validation] = ridge_probabilities(
                    joint_train, shuffled, joint_test)
            predictions["uniform"][validation] = 0.2
            predictions["training_prior"][validation] = np.bincount(labels[train], minlength=5) / len(train)
            if progress is not None:
                progress({"event": "fold_complete", "pair_id": pair_id, "scheme": scheme, "fold": fold})
        metrics = {arm: _metrics(_probabilities(values, N_TRIALS, arm), labels)
                   for arm, values in predictions.items()}
        report["schemes"][scheme]["metrics"] = metrics
        report["schemes"][scheme]["primary_log_loss_gains"] = {
            comparator: metrics[comparator]["class_macro_log_loss"]
            - metrics[primary_arm]["class_macro_log_loss"]
            for comparator in primary_comparators
        }
        if mode == "adaptive_attribution":
            report["schemes"][scheme]["secondary_conditional_log_loss_gains"] = {
                comparator: metrics[comparator]["class_macro_log_loss"]
                - metrics[ADAPTIVE_SECONDARY_ARM]["class_macro_log_loss"]
                for comparator in ADAPTIVE_SECONDARY_COMPARATORS
            }
        if time_frequency:
            report["schemes"][scheme]["view_log_loss_gains"] = {
                name: {
                    comparator: metrics[comparator]["class_macro_log_loss"]
                    - metrics["A_" + name]["class_macro_log_loss"]
                    for comparator in ("A", "N", "A_" + name + "_deranged",
                                       "A_" + name + "_shuffled", "uniform", "training_prior")
                }
                for name in representations
            }
            report["schemes"][scheme]["joint_vs_full_all_gain"] = {
                name: metrics[TIME_FREQUENCY_PRIMARY_ARM]["class_macro_log_loss"]
                - metrics["A_" + name]["class_macro_log_loss"]
                for name in representations
            }
        out_of_fold[scheme] = predictions
    return report, out_of_fold


__all__ = [
    "ARMS", "BANDS", "PRIMARY_ARM", "PRIMARY_COMPARATORS", "REPRESENTATIONS",
    "SCHEMES", "SEED", "paired_power_features", "preflight_calibration",
    "fold_derangement_indices", "run_pair_power_discovery",
    "ADAPTIVE_REPRESENTATIONS", "ADAPTIVE_ARMS", "ADAPTIVE_PRIMARY_ARM",
    "ADAPTIVE_PRIMARY_COMPARATORS", "ADAPTIVE_SECONDARY_ARM", "ADAPTIVE_SECONDARY_COMPARATORS",
    "TIME_FREQUENCY_REPRESENTATIONS", "TIME_FREQUENCY_FEATURE_COUNTS", "TIME_FREQUENCY_ARMS",
    "TIME_FREQUENCY_PRIMARY_ARM", "TIME_FREQUENCY_PRIMARY_COMPARATORS",
]
