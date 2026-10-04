# Which cheap signals carry the words?

Prospective discovery plan, September 21, 2026. The maintainer asked to continue
the calibration-only ablation proposed after SPEECH-REPRO-1. This is bounded
Tier B exploration on the six already-authorized calibration recordings, not
another confirmation. The consumed online result remains closed and immutable.

The belief-changing question is whether the strong auxiliary comparator reflects
display/time structure or information in microphone, lip and eye recordings.
We can test this without another EEGNet fit: eight fixed channel subsets, eight
matched training-label shuffles, uniform and training-prior controls. The
[machine-readable plan](../registries/speech_auxiliary_discovery_plan.v0.json)
fixes all sources, hypotheses, splits, seeds, metrics, thresholds and limits.

Primary validation holds out five contiguous 20-trial blocks, with an adjacent
training trial embargoed on each boundary. The secondary check uses five fixed
stratified random folds. Blocked training may use both earlier and later blocks:
this is retrospective held-out-block prediction, not past-to-future validation.
Repetitions never cross folds; scaling is learned only
from training trials. All six recordings must have every class in every training
fold before fitting begins. We retain all 600 trials, both conditions, every arm
and both split schemes. Metrics pool each recording's 100 out-of-fold predictions
before class-macro log loss and five-class balanced accuracy are calculated.

A consistent carrier must beat uniform, training prior and its own shuffled-label
control in log loss in all three people under blocked validation. This is a
descriptive discovery threshold, not a p-value. If display/timing clears it,
the next confirmation needs an explicit cue/task-state control. If peripheral
channels clear it without display/timing, a small peripheral communication
baseline becomes a more credible direction. If neither clears it, preserve the
null and do not turn random-split performance into a success claim.

The two split schemes have slightly different training counts (78/79 versus 80),
so a gap is not uniquely attributable to temporal drift. Modality sets also have
different dimensions under fixed dimension-normalized regularization; their
performance differences do not estimate unique causal information. A single
shuffle per fold is a negative-control diagnostic, not a permutation test.
Calibration exploration cannot explain the previous online score by itself or
establish future online performance, cortical origin or utility.

## What DISPLAY does and does not mean

The [pinned converter](https://github.com/arayabrain/uhd-gmail-public/blob/0dca00584c528b288392684dcec0d496b6aa4951/bids/convert_to_bids.py#L59-L77)
records DISPLAY+/DISPLAY- separately from TRIGGER. Its labels come from a
separate word-list CSV, not DISPLAY. Separate provenance does not establish
statistical independence. The [primary manuscript](https://www.biorxiv.org/content/early/2024/05/09/2024.05.09.591996.source.xml)
describes online free choice among color-coded actions with repetition pacing,
not necessarily target-word flashes. It does not sufficiently specify the
calibration pixel sequence or identify the DISPLAY hardware. We therefore do
not assume a photodiode or direct target-color encoding. Task state, pacing,
content and acquisition effects remain competing explanations.

## Execution boundary

After generated tests and remote CI pass, invoke
`PYTHONPATH=src .venv/Scripts/python.exe -u scripts/discover_speech_auxiliary.py`
once (set the environment variable separately in PowerShell). Caps: ten minutes,
one numerical thread/worker, 1 GiB RSS, 32 MiB output, 20 GiB free-space floor.
No downloads or persistent background process. The extractor requests only
auxiliary and trigger samples; hashing the existing EDF necessarily reads its
opaque bytes. The auxiliary feature recipe matches the prior full pipeline
bit-for-bit on generated samples. Failures stay local without automatic retry.

Local out-of-fold probabilities stay under ignored
`data/speech_auxiliary_discovery_20260921`; only aggregate results and this
scientific interpretation may be committed. The previous confirmation aggregate
SHA256 is checked before and after execution. No old evaluation targets,
predictions or weights are opened.
