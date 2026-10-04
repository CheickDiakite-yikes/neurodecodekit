"""One fixed nested, calibration-only positive-temperature diagnosis.

Arrays only: no files, protected targets, feature selection or model search.
Call preflight_probability_calibration for every recording before any fitting.
"""

from __future__ import annotations

from neurodecodekit.evaluation.speech_reproduction import (
    _labels,
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
    _split_hash,
    _split_plan,
)


LEARNED_ARMS = (
    "N", "N_shuffled", "A", "A_shuffled", "full_all", "full_all_shuffled",
    "A_full_all", "A_full_all_deranged", "A_full_all_shuffled",
)
ARMS = (*LEARNED_ARMS, *(name + "_calibrated" for name in LEARNED_ARMS),
        "uniform", "training_prior")
PRIMARY_ARM = "A_full_all_calibrated"
PRIMARY_COMPARATORS = (
    "A_calibrated", "N_calibrated", "A_full_all_deranged_calibrated",
    "A_full_all_shuffled_calibrated", "uniform", "training_prior",
)
INNER_SEED = 20260922
BETA_BOUNDS = (0.05, 20.0)
BISECTION_STEPS = 60


def _log_probabilities(probabilities):
    np = _numpy()
    values = _matrix(probabilities, "temperature probabilities")
    values = _probabilities(values, len(values), "temperature probabilities")
    return np.log(np.maximum(values, np.finfo(float).tiny))


def _temperature_log_softmax(log_probabilities, beta):
    np = _numpy()
    scores = beta * (log_probabilities - log_probabilities.max(axis=1, keepdims=True))
    return scores - np.log(np.exp(scores).sum(axis=1, keepdims=True))


def temperature_probabilities(probabilities, beta):
    """Apply positive inverse temperature, refusing a numerical argmax change."""
    np = _numpy()
    if not np.isfinite(beta) or not BETA_BOUNDS[0] <= beta <= BETA_BOUNDS[1]:
        raise ValueError("Inverse temperature must be finite and within fixed bounds")
    logs = _log_probabilities(probabilities)
    result = np.exp(_temperature_log_softmax(logs, beta))
    if not np.array_equal(result.argmax(axis=1), np.asarray(probabilities).argmax(axis=1)):
        raise ValueError("Numerical temperature transformation changed an argmax")
    return _probabilities(result, len(result), "calibrated probabilities")


def fit_inverse_temperature(probabilities, calibration_labels):
    """Minimize class-macro NLL with one bounded scalar and 60 derivative steps.

    The objective uses stable, unclipped log-softmax, preserving convexity in
    beta. The downstream historical metric retains its own 1e-15 scoring floor.
    Labels supplied here must be inner-OOF calibration labels, never outer test
    labels. Null models must retain their fixed permuted labels here as well.
    """
    np = _numpy()
    logs = _log_probabilities(probabilities)
    labels = _labels(calibration_labels)
    if len(labels) != len(logs):
        raise ValueError("Temperature labels and prediction rows differ")
    counts = np.bincount(labels, minlength=5)
    if (counts == 0).any():
        raise ValueError("Temperature calibration requires all five classes")
    weights = 1.0 / (5 * counts[labels])
    target_scores = logs[np.arange(len(labels)), labels]

    def objective(beta):
        log_softmax = _temperature_log_softmax(logs, beta)
        return float(-np.sum(weights * log_softmax[np.arange(len(labels)), labels]))

    def derivative(beta):
        probabilities_at_beta = np.exp(_temperature_log_softmax(logs, beta))
        return float(np.sum(weights * ((probabilities_at_beta * logs).sum(axis=1) - target_scores)))

    lower, upper = BETA_BOUNDS
    steps = 0
    if np.all(np.ptp(logs, axis=1) == 0):
        beta, boundary = 1.0, "flat"
    elif derivative(lower) >= 0:
        beta, boundary = lower, "lower"
    elif derivative(upper) <= 0:
        beta, boundary = upper, "upper"
    else:
        for _ in range(BISECTION_STEPS):
            midpoint = (lower + upper) / 2
            if derivative(midpoint) > 0:
                upper = midpoint
            else:
                lower = midpoint
        beta, boundary = (lower + upper) / 2, "interior"
        steps = BISECTION_STEPS
    before, after = objective(1.0), objective(beta)
    if after > before + 1e-12:
        raise ValueError("Bounded temperature optimizer increased its calibration objective")
    return {
        "inverse_temperature": float(beta),
        "temperature": float(1.0 / beta),
        "boundary": boundary,
        "boundary_hit": boundary in ("lower", "upper"),
        "bisection_steps": steps,
        "calibration_trials": int(len(labels)),
        "class_macro_nll_before": before,
        "class_macro_nll_after": after,
        "derivative_at_solution": derivative(beta),
    }


def _nested_plan(calibration_labels):
    np = _numpy()
    from sklearn.model_selection import KFold

    labels, outer_plans, metadata = _split_plan(calibration_labels)
    nested, shuffled_targets = {}, {}
    for scheme_index, (scheme, outer_folds) in enumerate(outer_plans.items()):
        nested[scheme], shuffled_targets[scheme] = [], []
        for outer_fold, (outer_train, _) in enumerate(outer_folds):
            record = metadata["schemes"][scheme]["folds"][outer_fold]
            null_labels = np.full(N_TRIALS, -1, dtype=np.int64)
            permutation = np.random.default_rng(record["shuffle_seed"]).permutation(len(outer_train))
            null_labels[outer_train] = labels[outer_train][permutation]
            shuffled_targets[scheme].append(null_labels)
            inner_seed = INNER_SEED + 100 * scheme_index + outer_fold
            if scheme == "blocked_embargo1":
                inner_folds = []
                for block in range(5):
                    if block == outer_fold:
                        continue
                    start, stop = block * 20, (block + 1) * 20
                    validation = outer_train[(outer_train >= start) & (outer_train < stop)]
                    # Use original trial indices, including a one-trial embargo
                    # around the original block rather than compressed row ranks.
                    train = outer_train[(outer_train < start - 1) | (outer_train >= stop + 1)]
                    inner_folds.append((train, validation))
            else:
                splitter = KFold(n_splits=4, shuffle=True, random_state=inner_seed)
                inner_folds = [(outer_train[train], outer_train[validation])
                               for train, validation in splitter.split(outer_train)]
            coverage = np.zeros(N_TRIALS, dtype=int)
            inner_records = []
            for inner_fold, (train, validation) in enumerate(inner_folds):
                if (len(train) < 2 or len(validation) < 2 or np.intersect1d(train, validation).size
                        or not np.isin(train, outer_train).all()
                        or not np.isin(validation, outer_train).all()):
                    raise ValueError("Inner split is not an isolated subset of outer training trials")
                true_counts = np.bincount(labels[train], minlength=5)
                null_counts = np.bincount(null_labels[train], minlength=5)
                if (true_counts == 0).any() or (null_counts == 0).any():
                    raise ValueError(f"{scheme} outer {outer_fold} inner {inner_fold}: "
                                     "a true or shuffled inner-training class is absent")
                coverage[validation] += 1
                inner_records.append({
                    "fold": inner_fold,
                    "training_trials": int(len(train)),
                    "validation_trials": int(len(validation)),
                    "embargoed_outer_training_trials": int(len(outer_train) - len(train) - len(validation)),
                    "training_class_counts": true_counts.tolist(),
                    "shuffled_training_class_counts": null_counts.tolist(),
                    "validation_class_counts": np.bincount(labels[validation], minlength=5).tolist(),
                    "shuffled_validation_class_counts": np.bincount(null_labels[validation], minlength=5).tolist(),
                    "split_indices_sha256": _split_hash(train, validation),
                })
            if not np.all(coverage[outer_train] == 1) or coverage.sum() != len(outer_train):
                raise ValueError("Inner OOF must cover every outer-training trial exactly once")
            record["inner_folds"] = inner_records
            record["inner_split_seed"] = inner_seed if scheme == "stratified_shuffled" else None
            record["temperature_calibration_trials"] = int(len(outer_train))
            nested[scheme].append(inner_folds)
    return labels, outer_plans, nested, shuffled_targets, metadata


def preflight_probability_calibration(calibration_labels):
    """Validate every nested split and true/null training support, without fits."""
    return _nested_plan(calibration_labels)[4]


def _predict_arms(auxiliary, eeg, labels, null_labels, train, validation):
    np = _numpy()
    n_train, n_test = _standardized_block(auxiliary[train, :392], auxiliary[validation, :392])
    a_train, a_test = _standardized_block(auxiliary[train], auxiliary[validation])
    e_train, e_test = _standardized_block(eeg[train], eeg[validation])
    joint_train = np.concatenate((a_train, e_train), axis=1)
    joint_test = np.concatenate((a_test, e_test), axis=1)
    blocks = {
        "N": (n_train, n_test), "N_shuffled": (n_train, n_test),
        "A": (a_train, a_test), "A_shuffled": (a_train, a_test),
        "full_all": (e_train, e_test), "full_all_shuffled": (e_train, e_test),
        "A_full_all": (joint_train, joint_test),
        "A_full_all_deranged": (
            np.concatenate((a_train, np.roll(e_train, 1, axis=0)), axis=1),
            np.concatenate((a_test, np.roll(e_test, 1, axis=0)), axis=1)),
        "A_full_all_shuffled": (joint_train, joint_test),
    }
    return {arm: ridge_probabilities(blocks[arm][0],
                                     null_labels[train] if arm.endswith("_shuffled") else labels[train],
                                     blocks[arm][1]) for arm in LEARNED_ARMS}


def run_pair_probability_calibration(
    auxiliary, eeg_full_all, calibration_labels, *, pair_id, progress=None
):
    """Return pair aggregates and 20 local-only probability arrays per scheme.

    Each outer fold fits nine arms on four inner training sets, chooses one
    positive temperature per arm using pooled inner OOF, and refits the nine
    fixed ridge models on the full outer training set. Outer labels only score
    the final pooled OOF. Null labels stay permuted through both fitting stages.
    """
    np = _numpy()
    auxiliary = _matrix(auxiliary, "enriched auxiliary features")
    eeg = _matrix(eeg_full_all, "full_all EEG features")
    if auxiliary.shape != (N_TRIALS, 692) or eeg.shape != (N_TRIALS, 768):
        raise ValueError("Expected auxiliary (100, 692) and full_all EEG (100, 768)")
    if not isinstance(pair_id, str) or not pair_id:
        raise ValueError("A nonempty pair_id is required")
    labels, outer_plans, nested, null_targets, report = _nested_plan(calibration_labels)
    report.update({
        "pair_id": pair_id,
        "status": "calibration_only_discovery",
        "confirmatory_result": False,
        "arms": list(ARMS), "learned_arms": list(LEARNED_ARMS),
        "primary_arm": PRIMARY_ARM, "primary_comparators": list(PRIMARY_COMPARATORS),
        "feature_counts": {"N": 392, "A": 692, "full_all": 768},
        "ridge_models_fitted": 450, "temperatures_fitted": 90,
        "settings": {
            "ridge_penalty": 1.0, "intercept_penalized": False,
            "standardization": "current inner or outer training rows only, per block",
            "dimension_normalization": "sqrt(each auxiliary or EEG block feature count)",
            "beta_bounds": list(BETA_BOUNDS), "bisection_steps": BISECTION_STEPS,
            "temperature_objective": "pooled inner-OOF class-macro unclipped log-softmax NLL",
            "scoring_probability_floor": 1e-15,
            "null_labels": "one outer-training permutation retained for every inner fit, calibration and outer refit",
            "derangement": "one EEG row cyclic shift separately inside each actual train/validation partition",
            "claim_ceiling": "development probability-readout diagnosis, not independent confirmation",
        },
    })
    out_of_fold = {}
    for scheme, outer_folds in outer_plans.items():
        predictions = {arm: np.full((N_TRIALS, 5), np.nan) for arm in ARMS}
        for outer_fold, (outer_train, outer_validation) in enumerate(outer_folds):
            context = {"pair_id": pair_id, "scheme": scheme, "fold": outer_fold}
            if progress is not None:
                progress({**context, "event": "fold_start"})
            null_labels = null_targets[scheme][outer_fold]
            positions = np.full(N_TRIALS, -1, dtype=int)
            positions[outer_train] = np.arange(len(outer_train))
            inner_oof = {arm: np.full((len(outer_train), 5), np.nan) for arm in LEARNED_ARMS}
            for inner_fold, (train, validation) in enumerate(nested[scheme][outer_fold]):
                values = _predict_arms(auxiliary, eeg, labels, null_labels, train, validation)
                for arm in LEARNED_ARMS:
                    inner_oof[arm][positions[validation]] = values[arm]
                if progress is not None:
                    progress({**context, "event": "inner_fold_complete", "inner_fold": inner_fold})
            temperatures = {
                arm: fit_inverse_temperature(inner_oof[arm],
                    null_labels[outer_train] if arm.endswith("_shuffled") else labels[outer_train])
                for arm in LEARNED_ARMS
            }
            values = _predict_arms(auxiliary, eeg, labels, null_labels, outer_train, outer_validation)
            for arm in LEARNED_ARMS:
                predictions[arm][outer_validation] = values[arm]
                predictions[arm + "_calibrated"][outer_validation] = temperature_probabilities(
                    values[arm], temperatures[arm]["inverse_temperature"])
            predictions["uniform"][outer_validation] = 0.2
            predictions["training_prior"][outer_validation] = np.bincount(labels[outer_train], minlength=5) / len(outer_train)
            report["schemes"][scheme]["folds"][outer_fold]["temperature_fits"] = temperatures
            if progress is not None:
                progress({**context, "event": "fold_complete"})
        metrics = {arm: _metrics(_probabilities(values, N_TRIALS, arm), labels)
                   for arm, values in predictions.items()}
        scheme_report = report["schemes"][scheme]
        scheme_report["metrics"] = metrics
        scheme_report["true_class_probabilities_below_scoring_floor"] = {
            arm: int(np.count_nonzero(values[np.arange(N_TRIALS), labels] < 1e-15))
            for arm, values in predictions.items()
        }
        scheme_report["primary_log_loss_gains"] = {
            comparator: metrics[comparator]["class_macro_log_loss"] - metrics[PRIMARY_ARM]["class_macro_log_loss"]
            for comparator in PRIMARY_COMPARATORS
        }
        scheme_report["paired_calibration_log_loss_gains"] = {
            arm: metrics[arm]["class_macro_log_loss"] - metrics[arm + "_calibrated"]["class_macro_log_loss"]
            for arm in LEARNED_ARMS
        }
        scheme_report["all_argmax_predictions_preserved"] = all(
            np.array_equal(predictions[arm].argmax(axis=1), predictions[arm + "_calibrated"].argmax(axis=1))
            for arm in LEARNED_ARMS
        )
        out_of_fold[scheme] = predictions
    return report, out_of_fold


__all__ = ["ARMS", "LEARNED_ARMS", "PRIMARY_ARM", "PRIMARY_COMPARATORS", "SCHEMES",
           "BETA_BOUNDS", "BISECTION_STEPS", "temperature_probabilities", "fit_inverse_temperature",
           "preflight_probability_calibration", "run_pair_probability_calibration"]
