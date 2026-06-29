# Experiment Plan

## Experiment 0 — synthetic smoke loop

Purpose: prove the code path works before using real neural data.

Command:

```bash
neurodecode make-synthetic-shard --out cache/synthetic_tiny.npz --samples 128 --channels 8 --times 25
```

Acceptance:

- file is created
- shape is printed
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
neurodecode select-tiny --manifest data/spanishbcbl_manifest.jsonl --modality MEG --out data/tiny_selection.json
neurodecode download-selection --selection data/tiny_selection.json --local-dir data/spanishbcbl_tiny --dry-run
```

Acceptance:

- selection includes only one raw block and relevant logs
- total planned files are printed
- no data is downloaded unless the user passes an explicit execute flag

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

## Experiment 4 — first real baseline

Purpose: honest sanity check.

Baselines:

- majority/frequency character baseline
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

## Anti-goals

Do not do these until the earlier experiments pass:

- v2 reproduction
- large distributed training
- LLM fine-tuning
- claims about clinical use
- consumer headset claims
