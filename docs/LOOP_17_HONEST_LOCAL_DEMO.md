# Loop 17 - Honest Local Evidence Console

Status: `Done` on 2026-07-10.

Proof posture: `synthetic example only; real results aggregate only; predictive
confidence unavailable; noncausal typed-sentence surrogate; no real-time,
arbitrary-thought, unseen-person, clinical, or at-home hardware claim`.

## Decision summary

Loop 17 replaces the text-only demo scaffold with a local artifact-backed
Gradio console. It does not train or run a model. It validates six compact
saved artifacts, reconstructs the saved synthetic score, and refuses to start
when cache rows, predictions, report examples, summary metrics, or calibration
authorization disagree.

The Example view exposes 19 held-out synthetic token-motif sentences, four of
six selectable signal channels, target, recorded prediction, CER, WER,
keyboard distance, exact match, character diff, and row-level provenance.
Prediction text can be edited for metric inspection and restored to the saved
artifact. This edit never changes the source artifact or creates confidence.

The Evidence view shows six aggregate rows: synthetic smoke, the five-row
strict real test, the 63-row same-person session transfer, and three synthetic
calibration stress families. No real sentence text is shown. The Provenance
view exposes all local paths, SHA-256 hashes, and the machine-readable proof
contract.

## Evidence boundary

| Evidence | Rows | Method CER | Comparator CER | Delta | Interpretation |
|---|---:|---:|---:|---:|---|
| Synthetic CTC smoke | 19 | 0.0000 | 0.7068 | -0.7068 | Plumbing/mechanism example only |
| S21 strict sentence-text test | 5 | 0.9477 | 0.9535 | -0.0058 | Near-null; interval crosses zero |
| S21 same-person session transfer | 63 | 0.9179 | 0.7755 | +0.1425 | Fixed CTC is worse than prior |
| Synthetic stationary calibration | 48 | 0.2328 | 0.4224 | -0.1897 | Narrow stationary-diagonal benefit |
| Synthetic channel-mixing stress | 48 | 0.8621 | 0.5690 | +0.2586 | Static adaptation harmful |
| Synthetic temporal-drift stress | 48 | 0.6034 | 0.4397 | +0.1638 | Static adaptation harmful |

The console labels predictive confidence `unavailable`. The stored report has
a greedy CTC string, not a calibrated posterior or uncertainty model. The real
rows retain their paired intervals where available, but intervals are not
rebranded as per-example confidence.

## Artifact contract

The loader reads only:

```text
cache/loop9_synthetic_sentences.npz
cache/loop9_synthetic_ctc_report.json
cache/loop9_synthetic_ctc_predictions.txt
cache/loop14_s21_split_aware/tiny_ctc/report.json
cache/loop15_s21_cross_session/tiny_ctc/report.json
cache/loop16_synthetic_calibration_curve/report.json
```

It hashes every file and cross-checks the 19 synthetic evaluation indices,
target strings, prediction strings, report examples, input lengths, noncausal
flag, summary metrics, and the Loop 16 prohibition on real-session adapter use.
The console triggers zero raw-neurodata reads, network fetches, real model runs,
or new cache writes.

## Commands

Install the optional demo dependency and launch locally:

```bash
pip install -e '.[demo]'
neurodecode demo --host 127.0.0.1 --port 7860
```

Run the same evidence/build gate without a server:

```bash
neurodecode demo \
  --audit-only \
  --out-json cache/loop17_demo/audit.json
```

Remote sharing is disabled and the default bind address is loopback only.

## Resource result

Final isolated startup audit under one-thread numeric limits:

```text
Gradio: 6.20.0
evidence load: 0.050 sec
total build: 1.644 sec
peak RSS: 224,837,632 bytes
components / callbacks: 27 / 4
display examples: 19
source cache: 136,734 bytes
audit checks: 8/8 passed
new cache bytes: 0
raw data reads / real model runs / network fetches: 0 / 0 / 0
```

Adding Gradio to the existing environment increased `.venv` by 178,756 KiB,
about 174.6 MiB. The two audit JSON files total about 8 KiB. The cleaned Loop
17 output folder, containing three screenshots and the tracker workbook, is
about 268 KiB. Free disk after closeout is about 17 GiB.

## Browser validation

The live local server was exercised, not only configuration-inspected:

- desktop `1440 x 1000`: no page overflow; all five proof cells visible
- mobile `390 x 844`: full page width remains 390 px; no horizontal overflow
- example switch: source row 0 to row 4 updates target and signal provenance
- edited prediction `BAD`: CER 0.7500, WER 1.0000, exact match `no`
- restore: returns `DAAB DBA`, zero CER/WER, exact match `yes`
- Evidence and Provenance tabs: aggregate rows, calibration plot, six hashes,
  and proof contract visible
- browser console: zero errors or warnings

Evidence:

```text
cache/loop17_demo/audit.json
cache/loop17_demo/browser_qa.json
outputs/loop17-demo/desktop.png
outputs/loop17-demo/mobile.png
outputs/loop17-demo/evidence.png
```

## Tests

Focused tests cover artifact/report agreement, aggregate-only real rows,
unknown channel rejection, edited scoring, required UI surfaces, and startup
audit checks. Final repository-wide verification passes 166 unittest tests
with 3 skipped and 163 pytest tests with 3 skipped plus 21 subtests. Ruff,
compileall, public CLI help, demo CLI help, and `git diff --check` pass.

## Research sources

- Brain2Qwerty project and task boundary:
  https://facebookresearch.github.io/brain2qwerty/
- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Gradio Blocks documentation:
  https://www.gradio.app/docs/gradio/blocks
- Gradio Plot documentation:
  https://www.gradio.app/docs/gradio/plot

## Decision and next gate

Loop 17 is complete as a local evidence and reproducibility surface. It is not
a real-MEG live-decoding demo. Loop 18 should define one versioned report-card
contract and ingest at least three existing baselines into a local leaderboard
without retraining, reopening observed real holdouts, or hiding missing proof,
split, comparator, resource, config, or cache-provenance fields.
