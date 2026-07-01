# NeuroDecodeKit Starter

**Mission:** make non-invasive neural language decoding research easier to start, reproduce, compress, and explain.

This starter repo is intentionally not a state-of-the-art Brain2Qwerty replication. It is a clean first loop for turning a huge neuroimaging release into a small, inspectable, benchmark-ready developer experience.

The first principle is simple:

```text
list files → choose tiny slice → cache small windows → run honest baselines → report CER/WER → demo errors
```

The thesis: the fastest path to value is not a giant model first. It is the access layer that lets smart builders avoid downloading hundreds of gigabytes before they can think.

## What is included

```text
neurodecodekit_starter/
  AGENTS.md                         # instructions for Codex / coding agents
  README.md                         # repo overview and quickstart
  pyproject.toml                    # package metadata and optional dependency groups
  docs/
    CODEX_HANDOFF.md                # exact next loop for Codex
    RESEARCH_BRIEF.md               # current research map and source notes
    DATA_ACCESS_PLAN.md             # selective download + manifest strategy
    EXPERIMENTS.md                  # first experiments and acceptance criteria
    RISK_AND_ETHICS.md              # non-clinical scope, privacy, licensing guardrails
    DECISIONS.md                    # architectural decisions log
  prompts/
    CODEX_START_PROMPT.md           # copy/paste prompt to continue this repo in Codex
  src/neurodecodekit/
    cli.py                          # lightweight CLI, works without heavy neuro deps
    datasets/manifest.py            # SpanishBCBL path parser + manifest schema
    datasets/hf_access.py           # optional Hugging Face listing/download helpers
    preprocess/windowing.py         # event-aligned window extraction utility
    evaluation/metrics.py           # CER/WER and Levenshtein utilities
    evaluation/keyboard.py          # simple QWERTY keyboard-distance metric
    training/synthetic.py           # synthetic shard generator for CI/dev loop
    models/template_classifier.py   # tiny no-LLM baseline for sanity checks
    demo/app.py                     # Gradio demo scaffold
  tests/                            # pure-Python unit tests
  configs/                          # starter experiment configs
```

## Quickstart

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests
```

Run the tiny local smoke loop without downloading any brain data:

```bash
neurodecode eval-text --target "HOLA MUNDO" --prediction "HOLA MUNCO"
neurodecode make-synthetic-shard --out cache/synthetic_tiny.npz --samples 64 --channels 8 --times 25
neurodecode load-cache --cache cache/synthetic_tiny.npz --metadata-out cache/synthetic_tiny.metadata.json
neurodecode report \
  --cache cache/synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/synthetic_report.json \
  --out-md cache/synthetic_report.md
```

The synthetic shard is the current CI-friendly smoke loop. It verifies cache
writing, cache loading, report writing, and metric plumbing without requiring
MNE, SciPy, Hugging Face access, or any Brain2Qwerty/SpanishBCBL files.
`--identity-smoke` uses cache labels as predictions and is explicitly a
plumbing check, not a model result.

## Build notes and handoff trail

This project is being built as a sequence of small loops, with each loop leaving
behind a runnable artifact and a plain-English handoff. The current build
journal is `docs/BUILD_NOTES.md`.

That journal captures:

- loop status and local commits
- commands that were verified
- managed-workstation blockers, including blocked external push/workbook paths
- data-access guardrails
- case-study notes and next-agent closeout steps

If work is interrupted, prefer updating the journal and marking the loop
pending over implying that a loop is complete.

Inspect SpanishBCBL-style paths using a local file list:

```bash
cat > /tmp/spanishbcbl_files.txt <<'EOF'
pinet2024_public/MEG/FIF/S1/block1.fif
pinet2024_public/MEG/logs/S1_block1.mat
pinet2024_public/EEG/EEG/S2/eeg.vhdr
EOF

neurodecode manifest-from-paths --paths /tmp/spanishbcbl_files.txt --out /tmp/manifest.jsonl
neurodecode inspect-manifest --manifest /tmp/manifest.jsonl
neurodecode select-tiny --manifest /tmp/manifest.jsonl --out /tmp/tiny_selection.json --max-files 4 --max-total-gb 2
neurodecode download-selection --selection /tmp/tiny_selection.json --local-dir data/spanishbcbl_tiny
```

Manifest v1 accepts plain paths, JSONL rows with `path` and optional
`size_bytes`, or tab-separated `path<TAB>size_bytes` rows. `inspect-manifest`
prints file-family counts, explicit parser warnings for unknown rows, and
raw-to-log candidate pairing summaries before any download is attempted.
`select-tiny` is safety-capped by default and writes a planned download file
with exact paths, file-count limits, known-byte totals, and unknown-size
warnings.

Optional real Hugging Face listing, when online and authenticated if needed:

```bash
pip install -e '.[hf]'
neurodecode list-hf-files --repo-id bcbl190626/SpanishBCBL --out data/spanishbcbl_files.txt
neurodecode manifest-from-paths --paths data/spanishbcbl_files.txt --out data/spanishbcbl_manifest.jsonl
neurodecode select-tiny --manifest data/spanishbcbl_manifest.jsonl --out data/tiny_selection.json --max-files 4 --max-total-gb 2
neurodecode download-selection --selection data/tiny_selection.json --local-dir data/spanishbcbl_tiny  # dry-run by default
```

To actually download the selected files, first read the dry-run plan. Then run:

```bash
neurodecode download-selection --selection data/tiny_selection.json --local-dir data/spanishbcbl_tiny --execute
```

If the manifest did not contain file sizes, `--execute` fails safely until you
either rebuild the manifest with sizes or add `--allow-unknown-size` after
reviewing the exact file list and file-count cap.

## Real window extraction from one downloaded block

Once you have explicitly downloaded one `.fif` block and one matching `.mat`
behavior/log file, install the optional neuro dependencies and extract a tiny
event-aligned cache:

```bash
pip install -e '.[neuro]'

neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../S1_block1.mat \
  --out cache/b2qmini_s1_block1.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3 \
  --picks meg \
  --max-events 200
```

`extract-windows` does not download anything. It only reads the two paths you
provide. The command reports events found, events kept, edge/max-event drops,
output shape, sampling rate, channel count, raw file size, output cache size,
and parser warnings.

The `.npz` cache contains:

```text
windows            [events, channels, timepoints] float32
labels             per-event labels when parsed, blank otherwise
event_start_sec    event timestamps in seconds
event_source_index source row/index from the parsed log
channel_names      channel names after picking/resampling
metadata           JSON with source paths, extraction params, parser notes
```

All current caches are written as B2Q-mini cache schema v0. The stable loader:

```bash
neurodecode load-cache --cache cache/b2qmini_s1_block1.npz --metadata-out cache/b2qmini_s1_block1.metadata.json
```

prints shape, dtype, label coverage, source files, warnings, and the
transformation trail. The optional JSON sidecar is intended for quick review and
experiment reports; the `.npz` remains the source of truth.

## Metrics and reports

Loop 5 is closed. The `neurodecode report` implementation and tests are present,
and the closeout verification passed on 2026-07-01.

Write a report from one-target-per-line text files:

```bash
neurodecode report \
  --targets cache/targets.txt \
  --predictions cache/predictions.txt \
  --cache cache/b2qmini_s1_block1.npz \
  --out-json outputs/run_001/metrics.json \
  --out-md outputs/run_001/report.md \
  --run-name run_001 \
  --split synthetic-smoke
```

The report includes CER, WER, exact-match rate, keyboard-distance diagnostics,
example rows, cache/storage metadata when provided, runtime, and warnings. A
real neural result should always be compared against a no-brain baseline in a
later report.

Synthetic report smoke path:

```bash
neurodecode make-synthetic-shard --out cache/synthetic_tiny.npz --samples 32 --channels 4 --times 12
neurodecode report \
  --cache cache/synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/synthetic_report.json \
  --out-md cache/synthetic_report.md \
  --run-name synthetic_identity_smoke \
  --split synthetic-smoke
```

`--identity-smoke` copies cache labels into predictions and emits an explicit
warning. It is useful for proving report plumbing, but it is not a decoder or a
baseline result.

Run the no-brain prior-only baseline:

```bash
neurodecode prior-baseline \
  --cache cache/synthetic_tiny.npz \
  --out-predictions cache/prior_predictions.txt \
  --out-json cache/prior_report.json \
  --out-md cache/prior_report.md \
  --run-name synthetic_prior_most_frequent \
  --split synthetic-smoke
```

`prior-baseline` deliberately ignores neural windows. It predicts from target
priors only and writes the same report format, with explicit warnings that no
neural signal was used. For real experiments, pass `--train-targets` or
`--train-cache` so the prior is fit on training labels rather than eval labels.

Run the tiny neural-window template baseline:

```bash
neurodecode template-baseline \
  --cache cache/synthetic_tiny.npz \
  --train-fraction 0.5 \
  --out-predictions cache/template_predictions.txt \
  --out-json cache/template_report.json \
  --out-md cache/template_report.md \
  --run-name synthetic_template_nearest_centroid \
  --split synthetic-holdout
```

`template-baseline` uses cache windows, but no deep learning. With one cache it
creates a deterministic stratified holdout split; for cleaner real experiments,
use `--train-cache` and `--eval-cache`.

Run the optional tiny ConvNet neural-window baseline:

```bash
pip install -e ".[ml]"

neurodecode tiny-conv-baseline \
  --cache cache/synthetic_tiny.npz \
  --train-fraction 0.75 \
  --epochs 30 \
  --batch-size 16 \
  --learning-rate 0.02 \
  --out-predictions cache/tiny_conv_predictions.txt \
  --out-json cache/tiny_conv_report.json \
  --out-md cache/tiny_conv_report.md \
  --run-name synthetic_tiny_conv \
  --split synthetic-holdout
```

`tiny-conv-baseline` is behind the optional `ml` extra because it uses PyTorch.
It defaults to CPU and one Torch thread. The command is a smoke baseline for
tiny caches, not a production decoder. On a base install it should fail with a
clear `pip install -e '.[ml]'` message.

Loop 5 closeout checks:

```bash
python -m unittest tests.test_report tests.test_cli_report
python -m unittest discover -s tests
neurodecode report --help
```

Closeout smoke artifact:

```bash
neurodecode make-synthetic-shard --out cache/loop5_synthetic_tiny.npz --samples 32 --channels 4 --times 12
neurodecode report \
  --cache cache/loop5_synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/loop5_synthetic_report.json \
  --out-md cache/loop5_synthetic_report.md \
  --run-name loop5_synthetic_identity_smoke \
  --split synthetic-smoke
```

Current limitations:

- `.mat` event parsing is intentionally heuristic until the exact SpanishBCBL
  log schema is inspected from a real selected shard.
- Labels may be blank if the log file does not expose a clear per-event target
  field.
- No filtering, artifact rejection, or subject normalization is applied yet.
- The first neural-window classifier is a nearest-centroid template baseline;
  it is transparent and intentionally small.
- The tiny ConvNet baseline is optional and requires `pip install -e ".[ml]"`.
  It should be compared against the prior-only and template baselines before any
  performance claim.
- `.npz` is the first cache format; Zarr is still a later step for larger runs.

## Why this wedge matters

Brain2Qwerty v1/v2 are exciting, but the current practical barrier is large: the public v1 SpanishBCBL dataset is around 262GB, and the v2 dataset is not public yet. A developer-access layer can create real leverage by giving people tiny curated shards, event-aligned windows, reproducible baselines, and clear metrics before they ever touch the full data.

## Non-goals for v0

- No clinical claims.
- No consumer EEG hype.
- No attempt to identify people from neural data.
- No full Brain2Qwerty v2 reproduction until v2 data is public.
- No commercial use of CC BY-NC data unless rights are separately cleared.

## First useful milestone

**B2Q-mini v0:** one participant, one MEG block, downsampled/cacheable event windows, one tiny baseline, and one report with CER/WER + storage footprint.

Success looks like this:

```text
A new builder can run a real or synthetic end-to-end loop in minutes,
see where errors come from,
and know exactly what to try next.
```
