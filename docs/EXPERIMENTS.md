# Experiment Plan

## Experiment 0 — synthetic smoke loop

Purpose: prove the code path works before using real neural data.

Command:

```bash
neurodecode make-synthetic-shard --out cache/synthetic_tiny.npz --samples 128 --channels 8 --times 25
neurodecode load-cache --cache cache/synthetic_tiny.npz --metadata-out cache/synthetic_tiny.metadata.json
neurodecode report --cache cache/synthetic_tiny.npz --identity-smoke --out-json cache/synthetic_report.json --out-md cache/synthetic_report.md
neurodecode prior-baseline --cache cache/synthetic_tiny.npz --out-predictions cache/prior_predictions.txt --out-json cache/prior_report.json --out-md cache/prior_report.md --run-name synthetic_prior_most_frequent --split synthetic-smoke
```

Acceptance:

- file is created
- shape is printed
- cache loads through the schema v0 loader
- metadata sidecar contains schema, dimensions, warnings, and transformations
- report command writes JSON and Markdown
- prior-only baseline writes predictions and a standard report
- metrics module works on sample text
- no heavy dependencies required except NumPy for shard creation

## Experiment 1 — path manifest

Purpose: verify data discovery and selection logic without downloading real data.

Command:

```bash
neurodecode list-hf-files --repo-id bcbl190626/SpanishBCBL --out data/spanishbcbl_files.txt
neurodecode manifest-from-paths --paths data/spanishbcbl_files.txt --out data/spanishbcbl_manifest.jsonl
neurodecode inspect-manifest --manifest data/spanishbcbl_manifest.jsonl
```

Acceptance:

- MEG raw `.fif` files are recognized
- EEG BrainVision files are recognized
- `.mat` logs are recognized
- subject IDs are inferred
- summary counts are sensible

## Experiment 2 — tiny selective download dry run

Purpose: create a safe tiny selection.

Command:

```bash
neurodecode select-tiny \
  --manifest data/spanishbcbl_manifest.jsonl \
  --modality MEG \
  --out data/tiny_selection.json \
  --max-files 4 \
  --max-total-gb 2
neurodecode download-selection --selection data/tiny_selection.json --local-dir data/spanishbcbl_tiny
```

Acceptance:

- selection includes only one raw block and relevant logs
- total planned files are printed
- exact planned paths and size metadata are printed
- no data is downloaded unless the user passes `--execute`
- real execution fails safely if selected sizes are unknown and `--allow-unknown-size` is not passed

## Experiment 3 — one real block to windows

Purpose: first real neural preprocessing.

Proposed command:

```bash
neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../logs.mat \
  --out cache/b2qmini_s1_block1.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3
```

Acceptance:

- MNE loads the block
- event parser finds keystrokes
- output shape is [events, channels, times]
- report includes bytes before/after preprocessing
- cache loads through `neurodecode load-cache`
- metadata records source files, extraction params, warnings, and transformations

## Experiment 4 — first real baseline

Purpose: honest sanity check.

Baselines:

- majority/frequency character baseline (implemented as `prior-baseline`)
- keyboard-neighbor baseline
- template classifier
- small ConvNet only after the first three are done

Required report:

```text
CER
WER
keyboard-distance error
example predictions
storage footprint
runtime
```

Before real baselines exist, use `neurodecode report` with explicit target and
prediction files:

```bash
neurodecode report \
  --targets outputs/run_001/targets.txt \
  --predictions outputs/run_001/predictions.txt \
  --cache cache/b2qmini_s1_block1.npz \
  --out-json outputs/run_001/metrics.json \
  --out-md outputs/run_001/report.md \
  --run-name run_001 \
  --split subject-or-session
```

`--identity-smoke` is allowed only as a plumbing check. It copies targets into
predictions and is not a decoder baseline.

The prior-only baseline is the first real comparator:

```bash
neurodecode prior-baseline \
  --targets outputs/run_001/targets.txt \
  --train-targets outputs/train_targets.txt \
  --out-predictions outputs/run_001/prior_predictions.txt \
  --out-json outputs/run_001/prior_report.json \
  --out-md outputs/run_001/prior_report.md \
  --run-name run_001_prior_only \
  --split subject-or-session
```

If `--train-targets` or `--train-cache` is omitted, the command emits
`prior_fit_on_eval_targets_for_smoke_only`. That is acceptable for plumbing
smoke tests, not for real baseline claims.

## Anti-goals

Do not do these until the earlier experiments pass:

- v2 reproduction
- large distributed training
- LLM fine-tuning
- claims about clinical use
- consumer headset claims
