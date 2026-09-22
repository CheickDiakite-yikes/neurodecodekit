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


def run_pair_power_discovery(auxiliary, eeg_features, calibration_labels, *, pair_id, progress=None):
    """Return a JSON-safe pair report and local-only OOF arrays for all 24 arms.

    ``eeg_features`` contains exactly REPRESENTATIONS, each ``[100,768]``;
    auxiliary has the original ``[100,392]`` features. Both fixed split schemes
    and their label shuffles are reused unchanged. Each auxiliary/EEG block is
    independently standardized using original training rows only and divided
    by sqrt(its feature count). Derangement then rolls only standardized EEG,
    independently within training and validation, leaving auxiliaries aligned.
    """
    np = _numpy()
    auxiliary = _matrix(auxiliary, "calibration auxiliary features")
    if auxiliary.shape != (N_TRIALS, N_AUXILIARY_FEATURES):
        raise ValueError("Calibration auxiliary features must have shape (100, 392)")
    if set(eeg_features) != set(REPRESENTATIONS):
        raise ValueError("EEG features must contain exactly the four fixed representations")
    eeg = {name: _matrix(eeg_features[name], name) for name in REPRESENTATIONS}
    if any(matrix.shape != (N_TRIALS, N_EEG_FEATURES) for matrix in eeg.values()):
        raise ValueError("Every EEG representation must have shape (100, 768)")
    if not isinstance(pair_id, str) or not pair_id:
        raise ValueError("A nonempty pair_id is required")
    labels, plans, report = _split_plan(calibration_labels)
    report.update({
        "pair_id": pair_id,
        "status": "calibration_only_discovery",
        "confirmatory_result": False,
        "arms": list(ARMS),
        "representations": list(REPRESENTATIONS),
        "primary_arm": PRIMARY_ARM,
        "primary_comparators": list(PRIMARY_COMPARATORS),
        "n_auxiliary_features": N_AUXILIARY_FEATURES,
        "n_eeg_features_per_representation": N_EEG_FEATURES,
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
    out_of_fold = {}
    for scheme, folds in plans.items():
        predictions = {arm: np.full((N_TRIALS, 5), np.nan) for arm in ARMS}
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
            auxiliary_train, auxiliary_test = _standardized_block(auxiliary[train], auxiliary[validation])
            predictions["N"][validation] = ridge_probabilities(auxiliary_train, truth, auxiliary_test)
            predictions["N_shuffled"][validation] = ridge_probabilities(auxiliary_train, shuffled, auxiliary_test)
            for name, matrix in eeg.items():
                eeg_train, eeg_test = _standardized_block(matrix[train], matrix[validation])
                joint_train = np.concatenate((auxiliary_train, eeg_train), axis=1)
                joint_test = np.concatenate((auxiliary_test, eeg_test), axis=1)
                predictions[name][validation] = ridge_probabilities(eeg_train, truth, eeg_test)
                predictions[name + "_shuffled"][validation] = ridge_probabilities(eeg_train, shuffled, eeg_test)
                predictions["N_" + name][validation] = ridge_probabilities(joint_train, truth, joint_test)
                predictions["N_" + name + "_deranged"][validation] = ridge_probabilities(
                    np.concatenate((auxiliary_train, eeg_train[train_order]), axis=1), truth,
                    np.concatenate((auxiliary_test, eeg_test[validation_order]), axis=1))
                predictions["N_" + name + "_shuffled"][validation] = ridge_probabilities(
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
            - metrics[PRIMARY_ARM]["class_macro_log_loss"]
            for comparator in PRIMARY_COMPARATORS
        }
        out_of_fold[scheme] = predictions
    return report, out_of_fold


__all__ = [
    "ARMS", "BANDS", "PRIMARY_ARM", "PRIMARY_COMPARATORS", "REPRESENTATIONS",
    "SCHEMES", "SEED", "paired_power_features", "preflight_calibration",
    "fold_derangement_indices", "run_pair_power_discovery",
]
