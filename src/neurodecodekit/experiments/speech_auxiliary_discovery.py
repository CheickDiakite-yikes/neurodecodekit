"""Fixed calibration-only modality discovery, never a confirmatory online score.

Call ``preflight_calibration`` on all six recordings before any model work.
``run_pair_discovery`` consumes arrays for one 100-trial recording and returns
JSON-safe aggregates separately from local-only out-of-fold probabilities.
No files, network, EEG features, checkpoints or online targets are accessed.
"""

from __future__ import annotations

import hashlib
import json

from neurodecodekit.evaluation.speech_reproduction import (
    _labels,
    _matrix,
    _metrics,
    _numpy,
    _probabilities,
    _standardized_block,
    ridge_probabilities,
)


SEED = 20260921
N_TRIALS = 100
N_FEATURES = 392
N_FOLDS = 5
SCHEMES = ("blocked_embargo1", "stratified_shuffled")
# fixed_channel_features is channel-major: 78 features per auxiliary channel.
MODALITY_COLUMNS = {
    "T": tuple(range(390, 392)),
    "D": tuple(range(0, 78)),
    "DT": (*range(0, 78), *range(390, 392)),
    "M": tuple(range(78, 156)),
    "E": tuple(range(156, 234)),
    "L": tuple(range(234, 390)),
    "P": tuple(range(78, 390)),
    "N": tuple(range(392)),
}
MODALITY_ARMS = tuple(MODALITY_COLUMNS)
ARMS = (*MODALITY_ARMS, *(name + "_shuffled" for name in MODALITY_ARMS),
        "uniform", "training_prior")


def _split_hash(train, validation):
    payload = json.dumps({"train": train.tolist(), "validation": validation.tolist()},
                         sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _split_plan(calibration_labels):
    np = _numpy()
    labels = _labels(calibration_labels)
    if len(labels) != N_TRIALS or set(labels.tolist()) != set(range(5)):
        raise ValueError("Discovery requires exactly 100 calibration trials and all five classes")
    try:
        from sklearn.model_selection import StratifiedKFold
    except ImportError as exc:
        raise RuntimeError("Auxiliary discovery requires neurodecodekit[ml].") from exc

    rows = np.arange(N_TRIALS)
    blocked = []
    for fold in range(N_FOLDS):
        start, stop = fold * 20, (fold + 1) * 20
        validation = rows[start:stop]
        excluded = rows[max(0, start - 1):min(N_TRIALS, stop + 1)]
        train = np.setdiff1d(rows, excluded, assume_unique=True)
        blocked.append((train, validation))
    stratifier = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    stratified = list(stratifier.split(np.zeros(N_TRIALS), labels))
    plans = dict(zip(SCHEMES, (blocked, stratified)))
    metadata = {"n_trials": N_TRIALS, "class_counts": np.bincount(labels, minlength=5).tolist(),
                "seed": SEED, "primary_scheme": SCHEMES[0], "schemes": {}}
    for scheme_index, (scheme, folds) in enumerate(plans.items()):
        coverage = np.zeros(N_TRIALS, dtype=int)
        records = []
        for fold, (train, validation) in enumerate(folds):
            train_counts = np.bincount(labels[train], minlength=5)
            if np.any(train_counts == 0):
                raise ValueError(f"{scheme} fold {fold}: a training class is absent; discovery incomplete")
            if np.intersect1d(train, validation).size:
                raise ValueError("Calibration training and validation trials overlap")
            coverage[validation] += 1
            records.append({
                "fold": fold,
                "training_trials": int(len(train)),
                "validation_trials": int(len(validation)),
                "embargoed_trials": int(N_TRIALS - len(train) - len(validation)),
                "training_class_counts": train_counts.tolist(),
                "validation_class_counts": np.bincount(labels[validation], minlength=5).tolist(),
                "split_indices_sha256": _split_hash(train, validation),
                "shuffle_seed": SEED + 100 * scheme_index + fold,
            })
        if not np.all(coverage == 1):
            raise ValueError("Every original calibration trial must be validated exactly once")
        metadata["schemes"][scheme] = {"folds": records}
    return labels, plans, metadata


def preflight_calibration(calibration_labels):
    """Validate both fixed split schemes before fitting; return no row labels.

    Missing classes in a validation block are permitted because metrics pool all
    100 out-of-fold rows. A missing training class refuses the complete pair;
    callers must not drop a fold, participant or condition to work around it.
    """
    return _split_plan(calibration_labels)[2]


def run_pair_discovery(features, calibration_labels, *, pair_id, progress=None):
    """Return ``(pair_report, {scheme: {arm: probabilities[100,5]}})``.

    The caller supplies unchanged 392-column auxiliary features. Each arm's
    selected columns are standardized on that fold's training rows only, then
    divided by sqrt(selected feature count). Identical training-label shuffles
    are shared by all modality arms within a fold; validation labels never
    enter any fit. No hyperparameters or feature variants are selected here.
    Optional ``progress`` receives target-free fold boundary dictionaries.
    """
    np = _numpy()
    matrix = _matrix(features, "calibration auxiliary features")
    if matrix.shape != (N_TRIALS, N_FEATURES):
        raise ValueError("Calibration features must have shape (100, 392)")
    if not isinstance(pair_id, str) or not pair_id:
        raise ValueError("A nonempty pair_id is required")
    labels, plans, report = _split_plan(calibration_labels)
    report.update({
        "pair_id": pair_id,
        "status": "calibration_only_discovery",
        "confirmatory_result": False,
        "n_features": N_FEATURES,
        "arms": list(ARMS),
        "feature_counts": {arm: len(columns) for arm, columns in MODALITY_COLUMNS.items()},
        "settings": {"ridge_penalty": 1.0, "intercept_penalized": False,
                     "standardization": "training rows only, per selected feature",
                     "dimension_normalization": "sqrt(selected feature count)",
                     "shuffle_scope": "training rows only, shared across modality arms",
                     "probabilities": "softmax of fixed one-hot ridge outputs, no calibration"},
    })
    out_of_fold = {}
    for scheme, folds in plans.items():
        predictions = {arm: np.full((N_TRIALS, 5), np.nan) for arm in ARMS}
        for fold, (train, validation) in enumerate(folds):
            if progress is not None:
                progress({"event": "fold_start", "pair_id": pair_id, "scheme": scheme, "fold": fold})
            shuffle_seed = report["schemes"][scheme]["folds"][fold]["shuffle_seed"]
            shuffled_labels = labels[train][np.random.default_rng(shuffle_seed).permutation(len(train))]
            for arm, columns in MODALITY_COLUMNS.items():
                standardized_train, standardized_test = _standardized_block(
                    matrix[np.ix_(train, columns)], matrix[np.ix_(validation, columns)])
                predictions[arm][validation] = ridge_probabilities(
                    standardized_train, labels[train], standardized_test)
                predictions[arm + "_shuffled"][validation] = ridge_probabilities(
                    standardized_train, shuffled_labels, standardized_test)
            predictions["uniform"][validation] = 0.2
            predictions["training_prior"][validation] = np.bincount(
                labels[train], minlength=5) / len(train)
            if progress is not None:
                progress({"event": "fold_complete", "pair_id": pair_id, "scheme": scheme,
                          "fold": fold})
        metrics = {arm: _metrics(_probabilities(values, N_TRIALS, arm), labels)
                   for arm, values in predictions.items()}
        report["schemes"][scheme]["metrics"] = metrics
        report["schemes"][scheme]["log_loss_gains"] = {
            arm: {"over_uniform": metrics["uniform"]["class_macro_log_loss"]
                  - metrics[arm]["class_macro_log_loss"],
                  "over_training_prior": metrics["training_prior"]["class_macro_log_loss"]
                  - metrics[arm]["class_macro_log_loss"],
                  "over_matched_shuffle": metrics[arm + "_shuffled"]["class_macro_log_loss"]
                  - metrics[arm]["class_macro_log_loss"]}
            for arm in MODALITY_ARMS
        }
        out_of_fold[scheme] = predictions
    return report, out_of_fold
