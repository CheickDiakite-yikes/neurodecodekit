"""Independent, dependency-free scoring of frozen imagined-word predictions.

No model, signal reader, or fitting code belongs here. Prediction rows contain
only identity and probabilities; targets are joined separately at score time.
The file entry point checks a caller-supplied prediction digest before opening
the target file. It cannot itself prove how a caller produced that digest or
that a caller has never inspected targets.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
import random


DEFAULT_CONTROL_ARMS = ("prior", "metadata", "shuffled", "noise")
PROBABILITY_FLOOR = 1e-12
METRICS = ("macro_log_loss", "balanced_accuracy", "exact_accuracy")
CLAIM = (
    "Prediction of a prompted, fixed-vocabulary word condition in a held-out recording "
    "block of calibrated participants performing imagined speech. This does not "
    "establish self-chosen thought-to-text or unseen-person generalization. The cue "
    "remains present during the EEG window; sensory cue processing, eye movements, "
    "and muscle activity are not isolated from imagined speech."
)


def _identity(row: Mapping, keys: set[str]) -> tuple[str, str, str]:
    if not isinstance(row, Mapping) or set(row) != keys:
        raise ValueError(f"Record must contain exactly {sorted(keys)}")
    values = tuple(row[key] for key in ("participant", "session", "trial_id"))
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError("Participant, session, and trial_id must be nonempty strings")
    return values


def _names(values: Sequence[str], name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of unique names")
    result = tuple(values)
    if not result or any(not isinstance(value, str) or not value for value in result):
        raise ValueError(f"{name} must contain nonempty strings")
    if len(set(result)) != len(result):
        raise ValueError(f"{name} contains duplicates")
    return result


def _probabilities(values: Sequence[float], n_classes: int) -> tuple[float, ...]:
    if (
        not isinstance(values, Sequence) or isinstance(values, (str, bytes))
        or len(values) != n_classes
    ):
        raise ValueError("Probability vector has the wrong number of classes")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
        raise ValueError("Probabilities must be numbers, not booleans or strings")
    result = tuple(float(value) for value in values)
    if any(not math.isfinite(value) or not 0 <= value <= 1 for value in result):
        raise ValueError("Probabilities must be finite values between zero and one")
    if not math.isclose(math.fsum(result), 1.0, rel_tol=0, abs_tol=1e-6):
        raise ValueError("Probabilities must sum to one; scorer does not renormalize")
    return result


def _prepare_predictions(
    records: Sequence[Mapping], *, class_labels: Sequence[str], primary_arm: str,
    control_arms: Sequence[str], expected_participants: Sequence[str] | None,
    heldout_session: str, diagnostic_arms: Sequence[str] = (),
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], dict]:
    labels = _names(class_labels, "class_labels")
    if len(labels) < 2:
        raise ValueError("At least two classes are required")
    controls = _names(control_arms, "control_arms")
    if set(controls) != set(DEFAULT_CONTROL_ARMS):
        raise ValueError("All four null controls are required: prior, metadata, shuffled, noise")
    diagnostics = _names(diagnostic_arms, "diagnostic_arms") if diagnostic_arms else ()
    arms = _names((primary_arm, *controls, *diagnostics), "arms")
    if not isinstance(heldout_session, str) or not heldout_session:
        raise ValueError("heldout_session must be a nonempty string")
    predictions = {}
    for row in records:
        key = _identity(row, {"participant", "session", "trial_id", "probabilities"})
        if key in predictions:
            raise ValueError(f"Duplicate prediction identity: {key}")
        if key[1] != heldout_session:
            raise ValueError("Prediction outside the declared held-out session")
        if not isinstance(row["probabilities"], Mapping) or set(row["probabilities"]) != set(arms):
            raise ValueError("Every prediction must include exactly the declared arms")
        predictions[key] = {
            arm: _probabilities(row["probabilities"][arm], len(labels)) for arm in arms
        }
    if not predictions:
        raise ValueError("No prediction records supplied")
    observed = {key[0] for key in predictions}
    people = (
        tuple(sorted(observed)) if expected_participants is None
        else _names(expected_participants, "expected_participants")
    )
    if set(people) != observed:
        raise ValueError("Prediction participants do not match the expected participant set")
    return labels, arms, people, predictions


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values)


def _percentile(sorted_values: Sequence[float], quantile: float) -> float:
    position = (len(sorted_values) - 1) * quantile
    low = math.floor(position)
    high = math.ceil(position)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (position - low)


def _interval(values: Sequence[float], resamples: Sequence[Sequence[int]]) -> list[float] | None:
    if len(values) < 2:
        return None
    draws = sorted(_mean([values[index] for index in sample]) for sample in resamples)
    return [_percentile(draws, 0.025), _percentile(draws, 0.975)]


def _bootstrap_options(bootstrap_samples: int, seed: int) -> None:
    if isinstance(bootstrap_samples, bool) or not isinstance(bootstrap_samples, int):
        raise ValueError("bootstrap_samples must be an integer")
    if not 100 <= bootstrap_samples <= 100000:
        raise ValueError("bootstrap_samples must be between 100 and 100000")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")


def score_predictions(
    prediction_records: Sequence[Mapping], target_records: Sequence[Mapping], *,
    class_labels: Sequence[str], primary_arm: str = "eeg",
    control_arms: Sequence[str] = DEFAULT_CONTROL_ARMS,
    diagnostic_arms: Sequence[str] = (),
    expected_participants: Sequence[str] | None = None, heldout_session: str = "5",
    bootstrap_samples: int = 4000, seed: int = 20260905,
) -> dict:
    """Score an exact identity join; all classes must occur for every person.

    Log loss averages trials within class, then classes within person. Balanced
    accuracy averages class recalls; exact accuracy averages all trials within
    person. All cohort means and paired intervals weight people equally. The
    same participant bootstrap draws are used for every arm and comparison.
    Intervals are descriptive, not multiplicity-adjusted confirmation tests.
    Argmax ties use the first class in the declared class order. Only the true
    class probability in log loss is floored at 1e-12; other values stay intact.
    """
    labels, arms, people, predictions = _prepare_predictions(
        prediction_records, class_labels=class_labels, primary_arm=primary_arm,
        control_arms=control_arms, expected_participants=expected_participants,
        heldout_session=heldout_session, diagnostic_arms=diagnostic_arms,
    )
    _bootstrap_options(bootstrap_samples, seed)
    targets = {}
    for row in target_records:
        key = _identity(row, {"participant", "session", "trial_id", "target"})
        if key in targets:
            raise ValueError(f"Duplicate target identity: {key}")
        if row["target"] not in labels:
            raise ValueError("Target is outside the declared vocabulary")
        targets[key] = labels.index(row["target"])
    if set(targets) != set(predictions):
        raise ValueError("Predictions and targets must have identical record identities")

    participants = []
    scored_rows = []
    for person in people:
        keys = [key for key in predictions if key[0] == person]
        counts = Counter(targets[key] for key in keys)
        if set(counts) != set(range(len(labels))):
            raise ValueError(f"Every class is required for participant {person}; none are dropped")
        arm_results = {}
        for arm in arms:
            class_losses = [[] for _ in labels]
            class_correct = [[] for _ in labels]
            for key in keys:
                probability = predictions[key][arm]
                prediction = max(range(len(labels)), key=probability.__getitem__)
                target = targets[key]
                class_losses[target].append(-math.log(max(probability[target], PROBABILITY_FLOOR)))
                class_correct[target].append(int(prediction == target))
            arm_results[arm] = {
                "macro_log_loss": _mean([_mean(values) for values in class_losses]),
                "balanced_accuracy": _mean([_mean(values) for values in class_correct]),
                "exact_accuracy": sum(sum(values) for values in class_correct) / len(keys),
            }
        participants.append({
            "participant": person, "session": heldout_session, "n_trials": len(keys),
            "class_counts": {label: counts[index] for index, label in enumerate(labels)},
            "arms": arm_results,
        })
        for key in keys:
            outputs = {}
            for arm in arms:
                probability = predictions[key][arm]
                index = max(range(len(labels)), key=probability.__getitem__)
                outputs[arm] = {
                    "word": labels[index], "confidence": probability[index],
                    "correct": index == targets[key], "probabilities": list(probability),
                }
            scored_rows.append({
                "participant": key[0], "session": key[1], "trial_id": key[2],
                "reference": labels[targets[key]], "arms": outputs,
            })

    rng = random.Random(seed)
    resamples = [
        [rng.randrange(len(people)) for _ in people] for _ in range(bootstrap_samples)
    ]
    summary = {}
    for arm in arms:
        summary[arm] = {}
        for metric in METRICS:
            values = [person["arms"][arm][metric] for person in participants]
            summary[arm][metric] = {
                "participant_mean": _mean(values),
                "descriptive_ci95": _interval(values, resamples),
            }
    comparisons = {}
    for control in arms[1:]:
        comparison = {}
        for metric in METRICS:
            direction = -1 if metric == "macro_log_loss" else 1
            differences = [direction * (
                person["arms"][primary_arm][metric] - person["arms"][control][metric]
            ) for person in participants]
            comparison[metric] = {
                "mean_gain": _mean(differences),
                "descriptive_ci95": _interval(differences, resamples),
                "positive_people": sum(value > 0 for value in differences),
                "tied_people": sum(value == 0 for value in differences),
                "participant_gains": dict(zip(people, differences)),
            }
        comparisons[control] = comparison
    return {
        "schema": "imagined-word-score-v1", "claim_scope": CLAIM,
        "class_labels": list(labels), "primary_arm": primary_arm,
        "control_arms": list(control_arms), "diagnostic_arms": list(diagnostic_arms),
        "heldout_session": heldout_session,
        "n_participants": len(people), "n_trials": len(predictions),
        "probability_floor": PROBABILITY_FLOOR,
        "confidence_definition": "Maximum model probability; calibration is not established.",
        "bootstrap": {
            "unit": "participant", "samples": bootstrap_samples, "seed": seed,
            "method": "paired percentile bootstrap, equal participant weighting",
            "interpretation": "Descriptive 95% intervals; no confirmatory or multiplicity claim.",
        },
        "summary_by_arm": summary, "participants": participants,
        "comparisons": {arm: comparisons[arm] for arm in control_arms},
        "diagnostic_comparisons": {arm: comparisons[arm] for arm in diagnostic_arms},
        "prediction_rows": scored_rows,
    }


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json_bytes(value: bytes) -> object:
    def reject_constant(token: str) -> None:
        raise ValueError(f"Nonfinite JSON constant: {token}")

    return json.loads(value, object_pairs_hook=_unique_object, parse_constant=reject_constant)


def score_frozen_files(
    predictions_path: str | Path, targets_path: str | Path, *,
    expected_prediction_sha256: str, bootstrap_samples: int = 4000,
    seed: int = 20260905,
) -> dict:
    """Check frozen JSON prediction bytes and schema before reading targets.

    Prediction envelope keys: class_labels, primary_arm, control_arms,
    expected_participants, heldout_session, records; optional diagnostic_arms.
    Target envelope: records.
    Targets use vocabulary strings, not an implicit numeric class mapping.
    The caller must supply the digest from the prior prediction freeze.
    """
    if (
        not isinstance(expected_prediction_sha256, str)
        or len(expected_prediction_sha256) != 64
        or any(char not in "0123456789abcdef" for char in expected_prediction_sha256)
    ):
        raise ValueError("An externally supplied lowercase SHA-256 digest is required")
    prediction_bytes = Path(predictions_path).read_bytes()
    actual_digest = hashlib.sha256(prediction_bytes).hexdigest()
    if actual_digest != expected_prediction_sha256:
        raise ValueError("Frozen prediction digest mismatch; targets were not opened")
    envelope = _read_json_bytes(prediction_bytes)
    required = {
        "class_labels", "primary_arm", "control_arms", "expected_participants",
        "heldout_session", "records",
    }
    if (
        not isinstance(envelope, dict) or not required <= set(envelope)
        or set(envelope) - required - {"diagnostic_arms"}
    ):
        raise ValueError("Prediction envelope has unexpected or missing fields")
    _names(envelope["expected_participants"], "expected_participants")
    arguments = {key: value for key, value in envelope.items() if key != "records"}
    _prepare_predictions(envelope["records"], **arguments)
    _bootstrap_options(bootstrap_samples, seed)
    target_bytes = Path(targets_path).read_bytes()
    targets = _read_json_bytes(target_bytes)
    if not isinstance(targets, dict) or set(targets) != {"records"}:
        raise ValueError("Target envelope must contain exactly records")
    result = score_predictions(
        envelope["records"], targets["records"], **arguments,
        bootstrap_samples=bootstrap_samples, seed=seed,
    )
    result["provenance"] = {
        "prediction_sha256": actual_digest,
        "target_sha256_at_score": hashlib.sha256(target_bytes).hexdigest(),
        "prediction_bytes": len(prediction_bytes), "target_bytes": len(target_bytes),
    }
    return result


def render_html_report(result: Mapping) -> str:
    """Render all scored word outputs locally, with no network assets or LLM."""
    if result.get("schema") != "imagined-word-score-v1":
        raise ValueError("Expected an imagined-word-score-v1 result")
    def escape(value):
        return html.escape(str(value), quote=True)

    primary = result["primary_arm"]
    arms = [primary, *result["control_arms"], *result["diagnostic_arms"]]

    def interval(value):
        return "unavailable" if value is None else f"[{value[0]:.4f}, {value[1]:.4f}]"

    summary_rows = []
    for arm in arms:
        metrics = result["summary_by_arm"][arm]
        summary_rows.append(
            f"<tr><th>{escape(arm)}</th>"
            f"<td>{metrics['macro_log_loss']['participant_mean']:.4f}</td>"
            f"<td>{metrics['balanced_accuracy']['participant_mean']:.1%}</td>"
            f"<td>{metrics['exact_accuracy']['participant_mean']:.1%}</td></tr>"
        )
    comparison_rows = []
    for control, comparison in result["comparisons"].items():
        loss = comparison["macro_log_loss"]
        comparison_rows.append(
            f"<tr><th>{escape(control)}</th><td>{loss['mean_gain']:+.4f}</td>"
            f"<td>{interval(loss['descriptive_ci95'])}</td>"
            f"<td>{loss['positive_people']}/{result['n_participants']}</td></tr>"
        )
    diagnostic_rows = []
    for arm, comparison in result["diagnostic_comparisons"].items():
        loss = comparison["macro_log_loss"]
        diagnostic_rows.append(
            f"<tr><th>{escape(arm)}</th><td>{loss['mean_gain']:+.4f}</td>"
            f"<td>{interval(loss['descriptive_ci95'])}</td>"
            f"<td>{loss['positive_people']}/{result['n_participants']}</td></tr>"
        )
    diagnostics_html = ""
    if diagnostic_rows:
        diagnostics_html = (
            "<h2>Window diagnostic</h2><p>This is a comparison with a different EEG window, "
            "not a no-signal control. Both windows may contain cue, ocular, or muscle information. "
            "Positive gain favors the primary EEG window.</p><div class='scroll'><table><thead>"
            "<tr><th>Diagnostic arm</th><th>Mean gain (nats)</th><th>Descriptive 95% interval</th>"
            "<th>People with positive gain</th></tr></thead><tbody>"
            + "".join(diagnostic_rows) + "</tbody></table></div>"
        )
    person_rows = []
    for person in result["participants"]:
        for arm in arms:
            metrics = person["arms"][arm]
            person_rows.append(
                f"<tr><th>{escape(person['participant'])}</th><td>{escape(arm)}</td>"
                f"<td>{person['n_trials']}</td><td>{metrics['macro_log_loss']:.4f}</td>"
                f"<td>{metrics['balanced_accuracy']:.1%}</td>"
                f"<td>{metrics['exact_accuracy']:.1%}</td></tr>"
            )
    output_rows = []
    for row in result["prediction_rows"]:
        cells = [
            f"<th>{escape(row['participant'])}</th><td>{escape(row['session'])}</td>",
            f"<td>{escape(row['trial_id'])}</td>",
            f"<td dir='auto'>{escape(row['reference'])}</td>",
        ]
        for arm in arms:
            output = row["arms"][arm]
            status = "correct" if output["correct"] else "incorrect"
            cells.append(
                f"<td class='{status}'><span dir='auto'>{escape(output['word'])}</span>"
                f" <small>{output['confidence']:.1%} · {status}</small></td>"
            )
        output_rows.append(
            f"<tr data-person='{escape(row['participant'])}'>" + "".join(cells) + "</tr>"
        )
    options = "".join(
        f"<option value='{escape(person['participant'])}'>{escape(person['participant'])}</option>"
        for person in result["participants"]
    )
    digest = result.get("provenance", {}).get("prediction_sha256", "not supplied to this renderer")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Imagined-word decoding · held-block report</title>
<style>
body{{font:16px/1.55 system-ui,sans-serif;color:#172b35;background:#fafaf8;margin:0}}
main{{max-width:1200px;margin:auto;padding:32px 24px}}h1{{line-height:1.15;margin-bottom:12px}}
h2{{margin-top:36px}}p{{max-width:900px}}.scope{{border-left:4px solid #927640;padding-left:16px}}
table{{width:100%;border-collapse:collapse;background:white;text-align:left;font-size:14px}}
th,td{{padding:10px;border-bottom:1px solid #dce0df;vertical-align:top}}
thead th{{background:#edf1ee}}.scroll{{overflow:auto}}small{{display:block;color:#52636b}}
.correct span{{color:#136044}}.incorrect span{{color:#983833}}code{{overflow-wrap:anywhere}}
select{{font:inherit;padding:6px;margin:0 0 16px 8px}}details{{margin-top:28px}}
</style></head><body><main>
<p>NeuroDecodeKit · local evaluation</p><h1>Prompted imagined words, held-out block</h1>
<p>{result['n_participants']} calibrated participants · {result['n_trials']} held-out trials ·
{len(result['class_labels'])} predefined words · session {escape(result['heldout_session'])}</p>
<p class="scope">{escape(result['claim_scope'])}</p>
<h2>Word prediction performance</h2>
<p>Each participant contributes equally. Log loss averages classes equally and is measured in
nats; lower is better. Balanced accuracy averages class recalls. Exact accuracy counts all trials.
Predicted text is a direct vocabulary lookup, with no language-model rewrite.</p>
<div class="scroll"><table><thead><tr><th>Arm</th><th>Class-macro log loss</th>
<th>Balanced accuracy</th><th>Exact accuracy</th></tr></thead>
<tbody>{''.join(summary_rows)}</tbody></table></div>
<h2>Comparison with every null control</h2>
<p>Gain = control log loss minus {escape(primary)} log loss; positive favors EEG.
Intervals resample paired participants and are descriptive 95% intervals, not corrected
confirmation tests. The number of participants, not the number of trials, is the comparison unit.</p>
<div class="scroll"><table><thead><tr><th>Control</th><th>Mean gain (nats)</th>
<th>Descriptive 95% interval</th><th>People with positive gain</th></tr></thead>
<tbody>{''.join(comparison_rows)}</tbody></table></div>
{diagnostics_html}
<details><summary>Every participant and arm</summary><div class="scroll"><table><thead><tr>
<th>Participant</th><th>Arm</th><th>Trials</th><th>Class-macro log loss</th>
<th>Balanced accuracy</th><th>Exact accuracy</th></tr></thead>
<tbody>{''.join(person_rows)}</tbody></table></div></details>
<h2>Every held-out word prediction</h2>
<p>References below were joined only at scoring. Confidence is the model's maximum probability;
it has not been established as a calibrated probability of being correct. All predictions,
including errors, are shown.</p>
<label for="person-filter">Participant</label><select id="person-filter">
<option value="">All participants</option>{options}</select>
<div class="scroll"><table id="predictions"><thead><tr><th>Participant</th><th>Session</th>
<th>Trial</th><th>Reference</th>{''.join(f'<th>{escape(arm)}</th>' for arm in arms)}</tr></thead>
<tbody>{''.join(output_rows)}</tbody></table></div>
<details><summary>Scoring details</summary><p>Frozen prediction SHA-256:
<code>{escape(digest)}</code></p><p>Bootstrap: {result['bootstrap']['samples']} participant resamples,
seed {result['bootstrap']['seed']}. True-class probabilities are floored at
{result['probability_floor']} for log loss. Argmax ties select the first declared class.</p></details>
</main><script>
document.getElementById('person-filter').addEventListener('change', function () {{
  const person = this.value;
  document.querySelectorAll('#predictions tbody tr').forEach(function (row) {{
    row.hidden = Boolean(person) && row.dataset.person !== person;
  }});
}});
</script></body></html>"""


def write_html_report(result: Mapping, path: str | Path) -> Path:
    """Write a self-contained local HTML report and return its path."""
    destination = Path(path)
    destination.write_text(render_html_report(result), encoding="utf-8")
    return destination
