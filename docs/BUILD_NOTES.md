# NeuroDecodeKit Build Notes

This file is the working journal for the build. It exists so later agents,
engineers, and case-study readers can reconstruct not only what changed, but
why the project moved in small loops.

## Note-taking convention

For each loop, record:

- the smallest useful question
- the code or artifact created
- the tests or smoke commands run
- what was deliberately not done
- any environment, data-access, or security blocker
- the next recommended action

When a loop is interrupted, mark it as pending instead of polishing the story.
An honest partial state is more useful than a false completion signal.

## Operating principles

- Keep the base install lightweight.
- Import heavy neuro/data dependencies only inside the command path that needs
  them.
- Prefer one tiny cache/report/demo over a large fragile pipeline.
- Never download large data silently.
- Keep `download-selection` dry-run by default.
- Require `--execute` plus explicit caps for any real download.
- Do not commit real dataset files, caches, credentials, or large binaries.
- Treat `--identity-smoke` as plumbing verification, not model performance.
- Do not proceed to a more complex loop until the previous loop has a clear
  artifact, decision, or pending handoff.

## Managed workstation observations

These observations are specific to the Bain-managed Windows environment used
for this build. They should guide future agents without being treated as
universal project constraints.

### GitHub push/export

On 2026-07-01, a push attempt after the local Loop 5 WIP commit was blocked by
the admin/reviewer layer because it would export the Bain workspace repo
externally and the privacy/trust status was not verified in that moment.

Implication:

- Do not retry `git push` from this workstation unless the user explicitly
  re-approves the export and the repository/privacy status is understood.
- Local commits are still useful for handoff.
- The next engineer can push from an approved environment or after explicit
  user approval.

### Workbook/tracker tooling

The attempt to close Loop 5 by updating the Excel tracker was interrupted by an
admin/tooling block during the earlier WIP handoff. On 2026-07-01, the tracker
workbook was successfully updated through the bundled spreadsheet runtime in an
ignored `.codex_work/loop5_tracker_closeout/` work area.

Implication:

- `docs/NEXT_20_LOOPS_TRACKER.md`, the root tracker copy, and both
  `NEURODECODEKIT_20_LOOP_TRACKER.xlsx` copies should show Loop 5 as done.
- Prefer the bundled spreadsheet runtime for future workbook edits when it is
  available and keep helper scripts inside `.codex_work/`.
- `.codex_work/` is ignored so transient local helper artifacts do not enter
  commits.

### Network and data access

Network access may be restricted. Real SpanishBCBL data is not present in the
repo, and the project should not fetch it implicitly.

Implication:

- Tests must keep working without Brain2Qwerty/SpanishBCBL files.
- Real extraction commands must only read explicit local `.fif` and `.mat`
  paths.
- Any download path must remain dry-run first and require explicit `--execute`.

### Git and OneDrive

This repo lives under OneDrive. Git commands may occasionally report an
`index.lock` unlink warning. Before any commit, verify no Git process is
running and remove only the exact stale lock path if needed.

Recommended safe lock cleanup:

```powershell
$repo = (Resolve-Path .).Path
$gitDir = Join-Path $repo '.git'
$lockPath = Join-Path $gitDir 'index.lock'
if (Test-Path $lockPath) {
  $resolvedLock = (Resolve-Path $lockPath).Path
  if (-not $resolvedLock.StartsWith($gitDir)) {
    throw "Refusing to remove unexpected path: $resolvedLock"
  }
  Remove-Item -LiteralPath $resolvedLock
}
```

## Loop timeline

| Loop | Status | Durable artifact | Notes |
|---:|---|---|---|
| 1 | Done | `docs/LOOP_01_PR1_CLOSEOUT_SMOKE.md` | Closed the first extraction scaffold with synthetic smoke coverage. Real data remains gated on one explicit `.fif`/`.mat` pair. |
| 2 | Done | `docs/LOOP_02_SPANISHBCBL_MANIFEST_V1.md` | Added manifest parsing and uncertainty reporting before any large download planning. |
| 3 | Done | `docs/LOOP_03_SAFE_TINY_SHARD_SELECTOR.md` | Added capped selection and dry-run download planning so the user sees exact files before execution. |
| 4 | Done | `docs/LOOP_04_B2Q_MINI_CACHE_V0.md` | Made `.npz` cache schema v0 the stable tiny-cache interface. |
| 5 | Done | `docs/LOOP_05_METRICS_ERROR_REPORT_V1.md` | Closed on 2026-07-01 with report command verification, synthetic JSON/Markdown smoke output, Markdown tracker updates, workbook tracker updates, and closeout docs. |
| 6 | Done | `docs/LOOP_06_LM_PRIOR_BASELINE.md` | Closed on 2026-07-01 with a no-brain prior baseline, report integration, tests, synthetic smoke output, and tracker updates. |
| 7 | Done | `docs/LOOP_07_TEMPLATE_BASELINE.md` | Closed on 2026-07-01 with nearest-centroid window baseline, deterministic holdout, reports, tests, synthetic smoke output, and tracker updates. |

## Loop 5 closeout state

Original WIP commit:

```text
fb3ec1a Add Loop 5 report WIP handoff
```

What exists:

- `neurodecode report`
- text target/prediction report flow
- synthetic cache `--identity-smoke` flow
- JSON and Markdown report writers
- CER, WER, exact-match, keyboard-distance, corpus edit counts, examples,
  worst examples, runtime, warnings, and optional cache metadata
- focused report tests and CLI report tests
- docs marking Loop 5 as done

Final closeout verification on 2026-07-01:

```text
python -m unittest tests.test_report tests.test_cli_report
Ran 8 tests
OK

python -m unittest discover -s tests
Ran 45 tests
OK
```

```text
neurodecode report --help
OK
```

Synthetic smoke output:

```text
cache/loop5_synthetic_tiny.npz
cache/loop5_synthetic_report.json
cache/loop5_synthetic_report.md
```

The cache/report files remain ignored local artifacts, not committed data.

Tracker closeout:

- `docs/NEXT_20_LOOPS_TRACKER.md` updated to Loop 5 done and Loop 6 next.
- Root `NEXT_20_LOOPS_TRACKER.md` updated to the same state.
- `docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx` updated:
  - Dashboard Done = 5.
  - Foundation Done = 5.
  - Loop 5 status = Done.
  - Decision Log includes the Loop 5 proceed row.
- Root `NEURODECODEKIT_20_LOOP_TRACKER.xlsx` updated with the same workbook.

## Case-study notes

The useful story is not "we built a decoder in one leap." The useful story is:

- Big neuro datasets become approachable when the first loop is manifest,
  selection, tiny cache, report, and demo.
- Optional dependencies make the tool usable on ordinary machines while still
  allowing real neuro extraction when the user opts in.
- Dry-run-by-default data access is a product feature, not just a safety guard.
- A report artifact is the bridge between research code and engineering
  repeatability.
- Identity smoke tests are valuable when they are named honestly.
- Prior-only baselines are valuable when they are visibly no-brain and fit on
  separate train labels for real experiments.
- Template baselines are valuable because they test window separability before
  hiding mistakes inside a neural network.
- Optional neural baselines need two smoke paths: a real training path when
  `.[ml]` is installed, and a clear install-hint failure path on lightweight or
  managed machines.
- Managed enterprise environments can block network, workbook, or export paths;
  the project should keep progressing through local commits and explicit
  handoffs rather than pretending those constraints do not exist.

## Loop 8 closeout - Tiny Conv / EEGNet-style Baseline

Loop 8 adds `neurodecode tiny-conv-baseline`, an optional PyTorch-backed tiny
ConvNet over cache windows.

What exists:

- `src/neurodecodekit/models/tiny_conv_baseline.py`
- `neurodecode tiny-conv-baseline`
- single-cache stratified holdout mode
- explicit `--train-cache` / `--eval-cache` mode
- CPU defaults: `--device cpu`, `--num-threads 1`
- training knobs: epochs, batch size, learning rate, hidden channels
- report metadata for model name, deep-learning usage, train/eval rows,
  classes, train/eval accuracy, loss history, and warnings
- tests for pure helpers, CLI validation, missing optional dependencies, report
  rendering, and Torch-enabled synthetic training smoke

Local closeout verification on 2026-07-01:

```text
python -m unittest tests.test_tiny_conv_baseline tests.test_cli_tiny_conv_baseline tests.test_report
Ran 15 tests
OK (skipped=2)

neurodecode --help
OK

neurodecode tiny-conv-baseline --help
OK
```

The two skipped tests are the actual Torch training smoke tests. Torch is not
installed in the current Bain-managed venv, and no heavy ML dependency download
was attempted during this loop. The local command failure was verified:

```text
neurodecode tiny-conv-baseline --cache cache/loop8_synthetic_tiny.npz --epochs 2
error: Tiny Conv baseline requires optional ML dependencies: `pip install -e '.[ml]'`.
```

In an ML-enabled environment, run:

```bash
pip install -e ".[ml]"
neurodecode tiny-conv-baseline --cache cache/loop8_synthetic_tiny.npz --train-fraction 0.75 --epochs 30
```

## Loop 9 closeout - Continuous Sentence Cache and Tiny CTC

Loop 9 adds a distinct `b2q-sentence-cache` schema, continuous S21 sentence
extraction, an optional 1,372-parameter CTC model, deterministic text-hash
holdout, training-only restart selection, and an automatic prior-only
comparator.

Verified locally on 2026-07-10:

```text
synthetic cache: 96 x 6 x 78, 136,734 bytes
synthetic CTC: 19/19 exact eval rows, corpus CER 0.0
prior-only comparator: corpus CER 0.70676692
CTC runtime: 0.969894 sec, one CPU thread
20-seed robustness: 20/20 at CER 0.0; one deterministic restart
real S21 cache: 66 x 16 x 617, 1,663,209 bytes
real extraction: 6.243 sec, about 515 MiB external peak RSS
real model score: intentionally not run or claimed
```

The optional Torch install used a 111.2 MB Apple Silicon wheel with
`--no-cache-dir`; `.venv` is about 942 MB after installation.

Full design, commands, sources, and proof boundary:
`docs/LOOP_09_CONTINUOUS_SENTENCE_CTC.md`.

## Loop 9 next action (completed by Loop 10)

The recommendation was to compare the same real S21 sentence cache at 100, 50,
and 25 Hz before acquiring more raw data or claiming a real decoder result.

## Loop 10 closeout - Sampling-Rate Resource Sweep

Loop 10 adds `neurodecode sampling-rate-sweep` and the reusable experiment
module `src/neurodecodekit/experiments/sampling_rate_sweep.py`.

The runner reuses the validated S21 block without any download, launches one
fresh process per rate, runs workers sequentially with common thread caps set
to one, refuses silent overwrite, and writes a complete audit bundle.

Verified locally on 2026-07-10:

```text
identity: exact 66 trials, targets, references, MAT responses, and 16 channels
100 Hz: 1,663,209 bytes, 4.121 sec, 66/66 CTC feasible
 50 Hz:   846,334 bytes, 3.586 sec, 66/66 CTC feasible
 25 Hz:   431,451 bytes, 3.539 sec, 66/66 CTC feasible
whole sweep: 11.778 sec, 2,940,994 cache bytes, 614,154,240 B peak worker RSS
```

The main result is a tradeoff boundary, not a winner. Storage and model
timepoints scale down, but fresh extraction runtime/memory do not because fixed
I/O, filtering, and process overhead dominate. Effective bandwidth falls from
45 Hz at the official-style 100 Hz rate to 25 Hz and 12.5 Hz. At 25 Hz the
current targets remain stride-one feasible, but the conservative uniform
temporal-stride ceiling falls to 2.

The pinned official v2 output-length formula adds an exact constraint: its
kernel-16, stride-4 temporal reducer is feasible for 66/66 rows at 100 and 50
Hz, but 0/66 at 25 Hz. This is structural compatibility evidence, not accuracy.

Full evidence: `docs/LOOP_10_SAMPLING_RATE_SWEEP.md`.

## Loop 10 next action (completed by Loop 11)

The recommendation was to replace the arbitrary first-channel smoke subset
with explicit geometry-aware, variance, random, and file-order controls on the
same validated source.

## Loop 11 closeout - Channel / Sensor Subset Sweep

Loop 11 adds channel geometry provenance to sentence extraction and the
cache-only `neurodecode channel-subset-sweep` command.

The real pass picks all 102 magnetometers before raw preload, records finite
device coordinates, and writes nested 76/51/25/16/8-channel caches for spatial
FPS, same-block variance, seed-17 random, and file-order controls. It downloads
no new data and refuses projected output above 128 MiB.

Verified locally on 2026-07-10:

```text
base: 66 x 102 x 617, 10,602,568 bytes
base extraction: 12.003939 sec, 1,679,278,080 B peak RSS, 0 swaps
geometry: 102/102 finite unique positions, 267.321 mm array diameter
subset sweep: 20 caches, 73,683,875 cache+sidecar bytes
subset runtime: 3.491672 sec, 270,499,840 B peak RSS
identity: all trial/text/timing arrays and exact signal slices match
```

At 16 channels, spatial FPS reduces mean/max whole-array coverage distance
from the file-order control's 102.2/219.3 mm to 34.9/69.8 mm. Variance ranking
retains 21.3% of post-scaling marginal variance versus 14.8% for FPS, but has
56.6/140.3 mm coverage. The two sets overlap on only 2 of 16 channels.

Decision: carry both `spatial-fps` and `variance` into a future held-out decoder
test. Keep `random` and `first` as controls. Select no count and claim no CER,
WER, anatomical ROI, OPM equivalence, or retained accuracy.

Full evidence: `docs/LOOP_11_CHANNEL_SENSOR_SUBSET_SWEEP.md`.

## Loop 11 next action (completed by Loop 12)

The recommendation was to compare float32, float16, and explicitly calibrated
integer or serialization variants on the fixed 102-mag base plus FPS-16 and
variance-16 caches, measuring bytes, encode/load time, reconstruction error,
clipping/saturation, and exact identity without a decoder claim.

## Loop 12 closeout - Precision and Storage Sweep

Loop 12 adds the versioned `b2q-signal-representation-cache` schema, packed
signal codecs, a standard/packed auto-loader, inspectable metadata sidecars,
and `neurodecode precision-storage-sweep`.

The real pass reused the fixed Loop 11 102-magnetometer base, FPS-16, and
variance-16 caches. It ran sequentially as one low-priority process with common
numeric thread pools capped at one. It downloaded no data, reprocessed no FIF,
and trained no model. A 96 MiB preflight cap bounded all planned artifacts.

Verified locally on 2026-07-10:

```text
inputs: 3 fixed real S21 caches, 66 rows each, 100 Hz
variants: float32, float16, packed bfloat16, fixed-range qint16, qint8
artifacts: 15 caches plus sidecars and JSON/Markdown reports
runtime: 3.788511 sec
peak RSS: 385,318,912 bytes
all artifacts: 36,212,760 bytes, below 100,663,296-byte cap
identity: all non-signal arrays, semantic metadata, shapes, and padding exact
integer source values outside [-5, 5]: 0
```

Aggregate compressed cache results:

```text
float32: 13,925,424 B, lossless reference
float16:  6,609,642 B, 52.54% smaller, worst relative RMSE 0.000179199
bfloat16: 5,400,633 B, 61.22% smaller, worst relative RMSE 0.001431703
qint16:   6,984,779 B, 49.84% smaller, worst relative RMSE 0.000036926
qint8:    2,679,951 B, 80.75% smaller, worst relative RMSE 0.009531163
```

Decision: keep float32 as the default. Carry qint16 as the fidelity candidate
and qint8 as the aggressive storage candidate into a future held-out decoder
test. Packed input storage currently decodes to float32 and is not integer-only
model inference. Low reconstruction error is not retained CER/WER.

Full evidence: `docs/LOOP_12_PRECISION_STORAGE_SWEEP.md`.

Final closeout verification:

```text
focused Loop 12 contracts: 13 tests, OK
full unittest discovery: 130 tests, OK (skipped=3)
full pytest: 127 passed, 3 skipped, 13 subtests passed
Ruff: clean
git diff --check: clean
real representation validation: 15/15 caches pass the public inspect command
workbook: 7/7 sheets rendered, key values reconcile, 0 formula-error matches
```

## Loop 13 - measured NPZ access / optional lazy-backend gate

Status: `Parked` on 2026-07-10 with a real report artifact and no Zarr install.

Implemented:

- `neurodecodekit.experiments.lazy_backend_gate`
- `neurodecode lazy-backend-gate`
- fresh subprocesses and one-thread caps per access pattern
- complete, 1-row, and 8-row access for standard and packed sentence caches
- exact decoded-signal SHA-256 checks
- declared time, peak-RSS, compressed-size, and identity gates
- JSON/Markdown decision reports with durable revisit triggers

The real gate reused nine S21 caches across the 102-magnetometer base, FPS-16,
variance-16, qint16, and qint8 representations. It read no raw FIF and wrote no
new signal cache.

Observed:

```text
9/9 caches pass all declared gates
largest compressed cache: 10,602,568 bytes
slowest full median: 60.386 ms (budget 250 ms)
slowest partial median: 53.634 ms (budget 100 ms)
highest worker peak RSS: 140.6 MiB (budget 512 MiB)
compressed-size threshold: 128 MiB per cache
decoded signal hashes: exact for every full and partial result
runtime: 5.358 sec
new cache/backend bytes: 0
report bytes: 40,101
zarr installed/benchmarked: no/no
```

Interpretation: a one-row NPZ request materializes the complete signal/payload
member, so its logical access amplification is 66x and its median takes
40.8%-82.1% of a full load. The inefficiency is real, but its current absolute
cost is below every declared local budget.

Decision: keep one bounded NPZ file per block and park the optional Zarr build.
Rerun the gate when one cache exceeds 128 MiB, full or partial time exceeds its
budget, worker RSS exceeds 512 MiB, or a real workflow repeatedly reads
subarrays. A future failure justifies a bounded Zarr comparison, not automatic
adoption.

Evidence: `docs/LOOP_13_LAZY_BACKEND_GATE.md` and
`cache/loop13_lazy_backend_gate/gate.json`.

## Next recommended action after Loop 13

Start Loop 14 Split Protocol v1. Match the official v2 sentence-text split
principle with deterministic train/validation/test assignment, preserve exact
membership hashes, make session/subject limits explicit, and prohibit fitting
data-dependent selectors or normalization on validation/test rows. Do not run a
real decoder comparison until that contract is machine-verified.

## Loop 14 - Split Protocol v1

Status: `Done` on 2026-07-10. Membership, train-only robust scaling, strict
report binding, signal-free prior evaluation, and explicit-membership tiny CTC
integration are validated on one real S21 block.

Implemented:

- `neurodecodekit.evaluation.split_protocol`
- `neurodecode split-protocol`
- NeuralSet 0.2.2-compatible SHA-256/float-seed assignment
- exact and canonical text grouping modes
- event, sentence-text, session, and canonical-subject capability audits
- duplicate semantic-row detection across cache representations
- deterministic protocol/group/membership hashes
- signal-free NPZ reads and exact report-byte accounting
- fit-scope checks for robust scaling and variance channel selection
- train-row-only scaler fit/apply with exact zero-padding preservation
- physical-cache, protocol-config, and semantic-membership hash binding
- `sentence-prior-baseline` with no signal-array load
- explicit split-report indices in the tiny CTC and no-brain comparator
- paired sentence-bootstrap comparison against the prior

Initial official-exact audit on the old 66-row S21 base:

```text
train/validation/test rows: 55/6/5
unique sentence groups: 66
group crossings: 0
canonical-text crossings: 0
duplicate semantic rows: 0
session groups: 1, unavailable for 3-way evaluation
canonical person groups: 1, unavailable for 3-way evaluation
runtime: 0.039339 sec
peak RSS: 46,825,472 bytes
report bytes: 63,438
new signal-cache bytes: 0
```

That artifact remains the expected failure proof. The replacement
`base_102mag_100hz_trainfit.npz` fits 102 channel statistics from 23,669 valid
timepoints in the 55 train rows, then freezes them for six validation and five
test rows. Its strict audit reports one fit finding passed and zero unresolved.

First strict test result:

```text
prior-only: 164 character edits, corpus CER 0.953488
tiny CTC: 163 character edits, corpus CER 0.947674
tiny train CER: 0.925469
tiny test blank fraction: 0.868132
tiny-minus-prior CER delta: -0.005814
paired bootstrap 95% interval: [-0.197279, 0.130653]
sentence wins/ties/losses: 2/0/3
```

Decision: close the protocol loop but treat the model result as near-null. Five
test rows, one character edit, poor train fit, and a wide interval do not show
that neural signal beats the no-brain baseline.

Evidence: `docs/LOOP_14_SPLIT_PROTOCOL_V1.md` and
`cache/loop14_s21_split_aware/split/split.json`.

Closeout verification snapshot: 147 unittest tests passed with 3 skipped;
pytest reported 144 passed, 3 skipped, and 21 subtests passed; Ruff, compileall,
five relevant CLI help paths, and `git diff --check` were clean; all seven
workbook sheets rendered and the formula-error scan returned zero matches.

## Next recommended action after Loop 14 - resolved by Loop 15 Stage A

The required second-session acquisition and fixed baseline are now complete.

## Loop 15 Stage A - same-subject cross-session gate

Status: `In progress; acquisition, normalization, and fixed baseline complete`
on 2026-07-10.

Implemented:

- explicit session filtering in `select-tiny`
- automatic inclusion and byte accounting for required split-FIFF continuations
- immutable Hub revision in selection/download provenance
- one-worker Hub download default and CLI override
- `MatTrialIndexMap` from nonempty MAT `keyTrig` slots
- gapped MAT trial IDs in sentence caches
- mapped raw/MAT key-trigger timing audit
- complete split-FIFF byte provenance in cache metadata
- `apply-frozen-scaler` with cache, split, statistic, preprocessing, and channel checks
- `cross-session-ctc` with source validation/test rows reserved and unused
- paired same-subject session holdout report plus signal-free prior

Acquisition:

```text
Hub revision: 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
files: primary FIFF + continuation FIFF + MAT log
known bytes: 2,516,384,765
cap: 2.5 GiB
download workers: 1
free disk before/after: about 18/16 GiB
```

FIFF/MAT identity:

```text
MNE parts: 2
duration: 977.05078125 sec
raw completed trials: 63
MAT target slots: 66
MAT nonempty keyTrig/response slots: 63
skipped MAT trial IDs: [54, 58, 60]
response indices equal nonempty keyTrig indices: true
timing pairs: 2,529
timing median/p95 absolute residual: 0.296/0.945 ms
```

Resource-bounded caches:

```text
unscaled: 63 x 102 x 1,636; 14,179,453 bytes
extraction: 14.228 sec; about 2.1 GB peak RSS
frozen source-train scaled: 13,543,399 bytes; 0.605 sec
all 102 channel names and preprocessing parameters match source: true
session-2 rows used for scaler fit: 0
Loop 15 cache/report artifacts: about 26 MiB
```

Fixed cross-session result:

```text
source train/validation/test: 55/6/5
source validation/test used by model: 0/0
independent session-2 eval rows: 63
typed-target/reference exact overlap: 0/0
prior: 2,117 edits; corpus CER 0.775458
tiny CTC: 2,506 edits; corpus CER 0.917949
tiny source-train CER: 0.925469
tiny eval blank fraction: 0.677081
tiny-minus-prior CER delta: +0.142491
paired bootstrap 95% interval: [+0.119386, +0.166069]
wins/ties/losses: 3/2/58
```

Decision: the acquisition, trial map, frozen-scaler, and cross-session protocol
pass. The unchanged tiny model fails transfer and is materially worse than the
no-signal comparator. Freeze session 2 as a consumed evaluation set. Continue
Loop 15 on synthetic domain shift and source train/validation only; pre-register
the next real held-out comparison.

Evidence: `docs/LOOP_15_SAME_SUBJECT_CROSS_SESSION.md` and
`cache/loop15_s21_cross_session/tiny_ctc/report.json`.

Final verification snapshot on 2026-07-10:

```text
unittest: 154 passed, 3 skipped, 3.954 sec
pytest: 151 passed, 3 skipped, 21 subtests passed, 3.70 sec
ruff check .: passed
compileall src tests: passed
git diff --check: passed
public CLI help: passed, including cross-session, frozen-scaler, selection, and download controls
real cache inspection: both Loop 15 caches passed schema/provenance validation
workbook: all 7 sheets visually checked; formula-error matches: 0
Loop 15 command/model/test formatter scope: 9 files clean
free disk: about 17 GiB
project data/cache/venv: about 4.6 GiB / 162 MiB / 942 MiB
```

Repository-wide `ruff format --check src tests` still identifies 33 files that
would be mechanically reformatted, including untouched legacy modules. This is
recorded as existing formatting debt; no broad formatter churn was mixed into
the Loop 15 scientific and data-contract changes.

## Loop 15 Stage B - synthetic adapter gate

Completed on 2026-07-10 without reading or writing a real cache.

Implemented:

- `preprocess/session_adapter.py` with deterministic synthetic channel shifts,
  unlabeled source/target median-IQR fitting, diagonal affine application,
  reconstruction metrics, statistic hashes, and exact padding checks
- `experiments/synthetic_adapter_gate.py` with a fixed 64/16/16 protocol,
  validation-only adapter selection, frozen synthetic holdout, no-brain prior,
  paired uncertainty, CPU/thread/output caps, and JSON/Markdown artifacts
- `neurodecode synthetic-adapter-gate`
- optional NumPy/Torch tests for the adapter and end-to-end gate

Observed:

```text
validation identity/adapted CER: 0.327273 / 0.000000
holdout identity/adapted/prior CER: 0.344828 / 0.000000 / 0.577586
adapted-minus-identity CI: [-0.408696, -0.286957]
runtime: 2.498 sec
peak RSS: 306,790,400 bytes
new cache bytes: 0
artifact bytes: 21,354
numeric threads: 1
decision: synthetic_gate_passed_select_robust_channel_affine
```

Interpretation: the gate proves exact recovery from the known diagonal affine
shift it was designed to invert. It does not establish real-session adaptation
or justify reopening the consumed S21 session-2 evaluation. Loop 16 should vary
calibration size and include unpaired/non-diagonal shifts.

Closeout verification:

- full unittest discovery: 160 tests passed, 3 skipped, 4.595 sec
- full pytest: 157 passed, 3 skipped, 21 subtests passed, 4.36 sec
- full Ruff check and `git diff --check`: passed
- test-suite peak RSS: 333,545,472 bytes or less under one-thread numeric caps
- workbook: all seven sheets rendered and inspected; formula-error scan found
  zero matches; the output copy is byte-identical to the tracked workbook
- final storage: 36 KiB experiment artifacts, 40 KiB workbook deliverable,
  zero new cache bytes, and 17 GiB free on the data volume

## Loop 16 - synthetic calibration curve and drift stress

Completed on 2026-07-10 without loading or writing a real cache.

Implemented:

- deterministic stationary channel-mixing and within-row time-varying synthetic
  shifts with exact zero-padding preservation
- one-fit multi-view tiny CTC evaluation so 63 validation views do not require
  63 source-model retrainings
- `experiments/synthetic_calibration_curve.py` with an independent unlabeled
  calibration pool, six nested row counts, three shift seeds, validation-only
  selection, one synthetic holdout pass, paired uncertainty, and resource caps
- `neurodecode synthetic-calibration-curve`
- focused adapter, multi-view CTC, and end-to-end experiment tests

Observed:

```text
source train/validation/holdout: 64/16/16
independent calibration pool: 48 rows; zero source-text overlap
sizes: 1, 2, 4, 8, 16, 32
shift seeds: 101, 211, 307
registered stationary selection: 1 row; 1.26 synthetic sec
stationary holdout median identity/adapted CER: 0.422414/0.232759
stationary outcomes: 2 seeds improve; 1 ties
channel-mixing median identity/adapted CER: 0.568966/0.862069; all 3 harmed
time-varying median identity/adapted CER: 0.439655/0.603448; all 3 harmed
validation/holdout model fits: 1/1 with exact training replay
runtime: 1.897 sec
reported peak RSS: 309,493,760 bytes
external maximum RSS: 318,963,712 bytes
new cache bytes: 0
artifact bytes: 158,256
numeric threads: 1
```

Interpretation: one synthetic row is enough for the registered median rule
because it supplies many valid samples from the same easy motif generator. It
is not a human calibration-time estimate. The stress failures are the more
important result: a static per-channel affine is not a general session adapter.
Any covariance-aware or causal rolling method stays synthetic-only until a new
validation gate is preregistered.

Closeout verification:

- full unittest discovery: 163 tests passed, 3 skipped, 4.806 sec
- full pytest: 160 passed, 3 skipped, 21 subtests passed, 4.57 sec
- full Ruff check, compileall, CLI help, and `git diff --check`: passed
- test-suite peak RSS: 335,953,920 bytes or less under one-thread numeric caps
- workbook: all seven sheets rendered and inspected; formula-error scan found
  zero matches; tracked and deliverable workbook hashes match
- final Loop 16 artifacts: about 156 KiB reports/CSVs and zero cache bytes

## Loop 17 - honest local evidence console

Completed on 2026-07-10 without loading raw neurodata, running a real model,
fetching data, or writing a new cache.

Implemented:

- `demo/evidence.py` with six-artifact loading, SHA-256 provenance, synthetic
  cache/prediction/report reconciliation, saved-summary reproduction, and
  explicit aggregate-only real evidence
- artifact-backed Gradio 6 console with 19 held-out synthetic examples, signal
  traces, target/prediction, editable CER/WER/keyboard-distance comparison,
  restore, calibration curves, real aggregate rows, and proof JSON
- `neurodecode demo` with loopback defaults and an `--audit-only` JSON gate
- optional `demo` dependency extra; the base package remains dependency-free
- focused evidence and UI audit tests
- desktop/mobile interaction and layout QA with zero browser-console errors

Observed:

```text
proof posture: synthetic_example_only_real_results_aggregate_only
Gradio: 6.20.0
held-out synthetic examples: 19
evidence/provenance rows: 6/6
evidence load / total build: 0.050 / 1.644 sec
peak RSS: 224,837,632 bytes
source cache: 136,734 bytes
components / callbacks: 27 / 4
startup checks: 8/8 passed
desktop: 1440 x 1000; no page overflow
mobile: 390 x 844; full page width 390; no horizontal overflow
console errors or warnings: 0
new cache / real model / raw read / network fetch: 0 / 0 / 0 / 0
optional environment increase: 178,756 KiB, about 174.6 MiB
free disk after closeout: about 17 GiB
```

Interpretation: the demo makes the current evidence inspectable but does not
improve the decoder. Synthetic example text remains synthetic; real metrics
remain aggregate-only; confidence is unavailable; and the tiny CTC remains
noncausal and typing-task-specific.

Workbook closeout:

- Done: 16; average progress: 80.5%; UX & Reproducibility: 1/2, 50%
- all seven actual sheets rendered and inspected
- formula-error scan found zero matches
- Loop 17 decision and demo-interpretation risk recorded
- Loop 18 prompt now requires a versioned artifact-only leaderboard contract

Closeout verification:

- full unittest discovery: 166 tests passed, 3 skipped, 6.307 sec
- full pytest: 163 passed, 3 skipped, 21 subtests passed, 6.14 sec
- full Ruff check, compileall, CLI help, demo help, and `git diff --check`: passed
- unittest/pytest maximum RSS: 484,524,032 / 495,206,400 bytes under
  one-thread numeric caps
- workbook: seven sheets rendered and inspected; formula-error scan found zero
  matches; tracked and deliverable workbook hashes match
- final Loop 17 compact output: about 268 KiB plus 8 KiB audit data; zero new
  cache bytes; about 17 GiB free

## Loop 18 - versioned report cards and cohort-local leaderboard

Completed on 2026-07-10 without opening raw neurodata, cache files, signal
arrays, or observed holdouts, and without running a model or fetching data.

Implemented:

- dependency-free `evaluation/report_card.py` with spec/card/leaderboard/audit
  schema v1, source/config hashing, completeness flags, and strict validation
- `neurodecode build-leaderboard` with 32-card and 2-MiB defaults, bounded
  source JSON, safe project-root paths, existing-output refusal, and explicit
  overwrite
- deterministic card JSON, metrics JSON, config JSON, cache metadata JSON,
  card Markdown, leaderboard JSON/CSV/Markdown, and sortable terminal table
- 11 saved runs normalized into six exact cohorts and four method families
- ranking limited to four explicitly comparable cohorts; no global winner
- tests for deterministic replay, malformed/mixed cards, duplicate IDs, caps,
  output collisions, CLI behavior, and forbidden-access counters

Observed:

```text
cards / cohorts / ranked cohorts: 11 / 6 / 4
source reports referenced / bytes read: 11 / 247,440
deterministic core files / bytes: 58 / 103,013
total output: 103,789 bytes
runtime: 0.012 sec
peak RSS: 21,643,264 bytes
raw reads / cache opens / signal loads: 0 / 0 / 0
model runs / network fetches / holdout reopenings: 0 / 0 / 0
cross-cohort ranking: false
free disk after build: about 17 GiB
```

Interpretation: the leaderboard is an evidence index, not a performance claim.
Synthetic and real, event and sentence, observed holdout and fit-on-eval rows
stay separate. The cross-session prior has lower CER while tiny CTC has lower
WER, so both metrics remain visible. SemER is unmeasured for every historical
run; cache hashes and other missing metadata are not backfilled by reopening
data.

Determinism check:

- a second build under `.codex_work/loop18_repeat` matches all 58 core files
  byte-for-byte
- `audit.json` is deliberately excluded because runtime and RSS vary

Workbook closeout:

- Done: 17; average progress: 85.5%; UX & Reproducibility: 2/2, 100%
- all seven actual sheets rendered and visually inspected
- formula-error scan found zero matches
- Loop 18 decision and leaderboard-comparability risk recorded
- Loop 19 prompt requires a read-only data/dependency/license gate before any
  EEG download or adapter implementation
- tracked and deliverable workbook SHA-256 are both
  `7b35c5abc788db3ff0b9ffe2121bf43ef7456eb70a2e8e4a8521a16bc1e159dd`

Closeout verification:

- full unittest discovery: 171 tests passed, 3 skipped, 6.624 sec; external
  maximum RSS 487,686,144 bytes
- full pytest: 168 passed, 3 skipped, 21 subtests passed, 6.28 sec; external
  maximum RSS 498,860,032 bytes
- full Ruff check, compileall, root CLI help, leaderboard help, artifact
  contract checks, and `git diff --check`: passed
- final Loop 18 output: 103,789 bytes; no new cache; about 17 GiB free

## Loop 19 - bounded SpanishBCBL EEG BrainVision bridge

Completed on 2026-07-10 with one explicitly approved 94,842,381-byte EEG
bundle, one 12,428,800-byte cache, no MOABB install, and no full EEG-subtree
download.

Implemented:

- corrected SpanishBCBL EEG subject/session/block parsing against the official
  loader convention
- complete `.vhdr/.eeg/.vmrk` plus exact MAT-log bundle selection, official
  known-bad stem exclusion, and pinned byte-aware Hugging Face metadata listing
- metadata-only `eeg-bridge-gate` with license, task, dependency, cap, and
  forbidden-access audit
- lazy `extract-eeg-windows` path using MNE BrainVision annotations and exact
  MAT trigger-code subsequence alignment
- streaming 1,000-to-50-Hz 500-ms key windows with raw global preload disabled
- same-split train-only prior comparator for the template baseline
- paired exact key-label accuracy comparison so token-string CER is not the
  primary classifier metric
- focused manifest, selection, Hub metadata, gate, alignment, extraction,
  report, and CLI tests

Observed:

```text
metadata gate: 13/13 checks passed; zero data/raw/model/cache access
gate runtime / peak RSS / bytes: 0.144 sec / 27,983,872 / 10,460
selected S7 session-2 block-1 bundle: 4 files / 94,842,381 bytes
raw: 64 channels / 1,000 Hz / 738.66 sec / preload false
MAT/raw trigger match: 2,534/2,534
alignment median/p99/max residual: 2.024/19.914/24.862 ms
output: 2,197 x 61 x 25 float32 / 12,428,800 bytes
extraction runtime / peak RSS: 6.402 sec / 300,548,096 bytes
template/prior exact label accuracy: 0.009091 / 0.122727
model-minus-prior accuracy interval: [-0.134545, -0.093636]
baseline runtime / peak RSS: 0.63 sec / 262,209,536 bytes
free disk after run: about 17 GiB
```

Interpretation: the native real EEG bridge works for this file; the first
transparent classifier does not. The event split is within one minimally
processed session, so it is a plumbing/negative-baseline result rather than a
sentence, session, subject, or hardware-generalization claim. EEG and MEG stay
in separate evidence cohorts.

Workbook closeout:

- Done: 18; average progress: 90.5%; Expansion: 1/2, 50%
- Loop 20 prompt requires a modality-aware cache/embedding interface using
  existing arrays and synthetic fixtures only

Closeout verification:

- full unittest discovery: 185 tests passed, 3 skipped, 5.920 sec; external
  maximum RSS 486,457,344 bytes under one-thread numeric caps
- full pytest: 182 passed, 3 skipped, 21 subtests passed, 6.17 sec; external
  maximum RSS 491,864,064 bytes under one-thread numeric caps
- full Ruff check, compileall, root CLI help, four Loop 19 command helps,
  artifact reconciliation, and `git diff --check`: passed
- artifact reconciliation: 13/13 metadata checks, exact `2197 x 61 x 25`
  cache shape, 12,428,800 cache bytes, train-only prior, and wholly negative
  label-accuracy interval all pass
- workbook: all seven sheets rendered and inspected; formula-error scan found
  zero matches; tracked and deliverable SHA-256 are both
  `fe07c8b2cdc8b944e57bd6b2b9518f1ee0aecc91778106b40664d315e41d47b8`
- final Loop 19 cache-directory artifacts: 12,774,604 bytes; local selected EEG
  tree including Hub metadata: 95,031,468 bytes; about 17 GiB free

## Loop 20 - NeuroTokenCache v0 synthetic interface

Completed on 2026-07-10 without opening a real neural cache, observed holdout,
or unreleased v2 data, and without running a model, training, downloading data,
or adding a dependency.

Implemented:

- optional-NumPy `NeuroTokenCache v0` with continuous
  `[items,time,embedding]` vectors, lengths, masks, frame timestamps, item and
  source identities, subject/session IDs, split labels, and source geometry
- normalized metadata for modality/device, timebase, geometry availability,
  official-v2 mapping, exact source/split hashes, transformations, resources,
  warnings, and claim boundaries
- separate asynchronous-input, producer-causality, decoder-causality,
  right-context, and measured end-to-end-latency fields
- deterministic target-free Gaussian frame projection with item/token/byte caps
- `make-neurotoken-cache` and `inspect-neurotoken-cache` CLI commands with
  collision refusal, metadata sidecar, and compact run summary
- tests for round trip, hash stability, mask/timestamp/vector padding failures,
  output caps, strict split binding, target-array absence, CLI behavior, and
  existing-output refusal

Observed:

```text
source: 48 x 5 x 77 / 59,357 bytes
strict split: 37 train / 4 validation / 7 test
tokens: 48 x 16 x 32 float32 / 553 valid frames
token cache / metadata: 76,646 / 11,369 bytes
primary Loop 20 directory: 204 KiB
runtime / maximum RSS: 0.09 sec / 44,564,480 bytes
payload SHA-256: 82b478948bdcfd5b2d12643f9f912c192a8977c8f0554b9f073171cf6dfe2709
independent payload replay: exact
model / training / real-data reads: 0 / 0 / 0
end-to-end latency measured: false
free disk after run: about 17 GiB
```

Interpretation: the interface is ready to receive a future learned encoder
output, but the current vectors are synthetic continuous mock embeddings. At
100 Hz the producer's kernel-16/stride-4 frames become available after 160 ms
and step every 40 ms; that is not a causal decoder or measured end-to-end
latency result.

Workbook closeout target:

- Done: 19; average progress: 95.5%; Expansion: 2/2, 100%
- next prompt requires a synthetic causal chunk/replay contract before a
  learned encoder or causal decoder

Closeout verification:

- full unittest discovery: 191 tests passed, 3 skipped, 6.794 sec; external
  maximum RSS 487,784,448 bytes under one-thread numeric caps
- full pytest: 188 passed, 3 skipped, 21 subtests passed, 6.45 sec; external
  maximum RSS 496,402,432 bytes under one-thread numeric caps
- full Ruff check, compileall, dependency-light module import, root CLI help,
  both Loop 20 command helps, and `git diff --check`: passed
- artifact reconciliation: exact source/split binding, `48 x 16 x 32` shape,
  553 valid frames, target-array absence, zero model/training/real reads, and
  independent token-payload replay all pass
- workbook: all seven sheets rendered and inspected; formula-error scan found
  zero matches; tracked and deliverable SHA-256 are both
  `dce9e92f02e5937d5e822f9facd6f659d2f840182c05be6e1dd912c79fa3bd59`
- final Loop 20 cache artifacts: 204 KiB; about 17 GiB free

### Loop 20 post-closeout selective-access hardening

Audited and pushed on 2026-07-10 as commit `389efe3`. The original projection
did not use target values, but its general sentence-cache loader still opened
target arrays. The producer now uses a projection-only reader that opens
exactly metadata, signals, lengths, row/trial timing, and channel names; it
verifies five target members are present without indexing them. An access-
tracking test covers two deterministic replays and fails on any target-member
read.

The independent ignored replay preserved the exact payload SHA-256 while
writing a 76,825-byte cache and 11,992-byte sidecar from the 59,357-byte source.
It produced `48 x 16 x 32` tokens, 553 valid frames, and 0.279948 padding in
0.069754 seconds at 43,401,216-byte internal peak RSS. Raw-data reads,
real-cache reads, model runs, and training runs remained zero; the producer is
causal at frame availability and end-to-end latency remains unmeasured. One
synthetic source cache was read. The primary historical artifact was not
overwritten.

Clean-commit verification preserved the existing baseline: 199 unittest tests
passed with 3 skipped; pytest reported 196 passed, 3 skipped, and 25 subtests
passed. Full Ruff, compileall, dependency-light import, CLI help, bounded
create/inspect, and `git diff --check` passed under one-thread numeric caps.

## Post-roadmap Loop 21 - causal NeuroToken chunk/replay gate

Completed on 2026-07-10 using the fixed 59,357-byte Loop 20 synthetic source,
without creating another signal cache or opening target arrays, real neural
data, observed holdouts, models, training, decoders, or network services.

Implemented:

- reusable fixed-weight causal mock producer plus one independent bounded
  stream state per item
- global frame sample/timestamp metadata, availability samples, and
  scheduler-delay accounting on every emitted token
- explicit zero-right-context and `drop-incomplete` flush contract
- fixed single-sample, stride-aligned, kernel-then-stride, jittered, and
  whole-item replay schedules
- canonical one-frame arithmetic for bitwise schedule identity, with declared
  `1e-6` compatibility against Loop 20's frozen batched arithmetic
- signal-only selective NPZ access and tests that track every opened member
- `neurodecode causal-replay-gate` with source/item/chunk/token/push/working/
  state/runtime/RSS/report caps and collision refusal
- JSON/Markdown reports with frame, state, latency, access, resource, source,
  research, warning, and claim-boundary records

Observed:

```text
source: 48 items / 5 channels / 2,870 valid samples / 28.7 sec
frames / schedules: 553 / 5 of 5 passed
right context / first frame: 0 samples / 160 ms
stream schedule bits: invariant
canonical hash: 78dc8b5298064216caa854c884a69834c0959566d9ede903d44ae1cd28562389
max Loop 20 difference: 9.5367431640625e-7 under 1e-6 tolerance
max scheduler delay: aligned 0 ms / jittered 140 ms / whole-item 610 ms
fixed weights / mutable state: 10,240 / 300 bytes
bounded working core: 195,520 bytes
total pushes / runtime / peak RSS: 4,652 / 0.135024 sec / 46,301,184 bytes
JSON / Markdown / total artifacts: 12,734 / 1,792 / 14,526 bytes
target/raw/real/model/training/decoder/network: all zero
independent stable-field replay: exact
free disk after run: about 15 GiB
```

Interpretation: causal frame production is now a tested local interface, but
there is still no learned neural representation, character decoder, partial
hypothesis, endpoint, or end-to-end latency measurement. A whole-item schedule
has the best compute RTF and worst transport latency, confirming that throughput
cannot stand in for responsiveness.

Next gate:

- Loop 22: one tiny optional-Torch causal encoder on synthetic train rows only
- validation-only configuration/stopping and one frozen synthetic test pass
- mandatory no-signal comparator plus parameter/state/RSS/RTF/artifact caps
- no CTC prefix decoder, language model, real cache, or observed holdout yet

Closeout verification:

- full unittest discovery: 199 tests passed, 3 skipped, 7.831 sec; external
  maximum RSS 475,774,976 bytes under one-thread numeric caps
- full pytest: 196 passed, 3 skipped, 25 subtests passed, 7.77 sec; external
  maximum RSS 501,366,784 bytes under one-thread numeric caps
- full Ruff check, compileall, root CLI help, Loop 21 command help, and
  `git diff --check`: passed
- focused Loop 20/21 producer, replay, and CLI tests: 12 passed
- independent stable-field artifact replay: exact; all five schedules passed
- all seven workbook sheets rendered; formula-error scan found zero matches;
  tracked and deliverable SHA-256 are both
  `bd7ba4895e3afaf54b279ff240cf3377d49693dfdaeb11527c7ef7600874836c`
- final Loop 21 gate artifacts: 14,526 bytes; about 15 GiB free

## Post-roadmap Loop 22 - tiny learned causal encoder gate

Completed on 2026-07-10 from the preregistered `9a40c7e` protocol. Alternate
seed mechanics, access-failure behavior, all tests, and resource caps passed
before implementation commit `57d3ad8`; only then was the registered
2201/2202/2203 fixture generated and its test opened once.

Implemented:

- strict versioned synthetic motif partitions and compact manifest with one
  physical train/validation/test NPZ each
- one-read partition loading, strict member rejection, complete content/hash/
  shape/label/frame rebinding, and path safety
- optional-Torch 80-12-8-6 causal window encoder/probe with 1,130 parameters
- train-only channel normalization and class weights, validation epoch
  selection, deterministic CPU training, and safe numeric NPZ checkpoint
- train-only prior and train-mean zero-signal controls, balanced accuracy,
  macro-F1, confusion, per-item accuracy, and paired item bootstrap
- producer-neutral Loop 21 stream interface and five-schedule learned replay
- ordered access audit that opens test only after validation and checkpoint
  freeze, plus tests proving one successful read and zero failed-gate reads
- fixture create, metadata-only inspect, and fixed gate CLI commands

Observed:

```text
fixture items / frames: 80 / 1,598
fixture bytes: 152,783 of 1 MiB
train / validation / test frames: 1,273 / 161 / 164
parameters / parameter bytes: 1,130 / 4,520
selected epoch / epochs run: 34 / 42
validation learned / prior balanced accuracy: 1.0 / 0.166667
test learned / prior / zero balanced accuracy: 1.0 / 0.166667 / 0.166667
test accuracy gain interval: [0.630906, 0.635766]
stream schedules / pushes: 5 of 5 / 1,194
right context / mutable state: 0 samples / 300 bytes
embedding schedule bits: identical
training / internal gate / external wall: 4.354204 / 5.105284 / 5.50 sec
internal / external peak RSS: 307,724,288 / 313,982,976 bytes
checkpoint / JSON / Markdown: 7,894 / 34,849 / 1,458 bytes
raw / real / text / network access: all zero
train / validation / test opens: 1 / 1 / 1
```

Interpretation: the project now has a working small learned causal producer and
frozen synthetic evaluation path. The task is intentionally obvious and its
perfect score is not neural or text decoding. The seed-2203 test is consumed.
The next gate was to preregister Loop 23 before writing a prefix decoder or
generating new targets; that preregistration is recorded below.

Closeout verification:

- focused Loop 22 fixture/model/gate tests: 10 passed
- full unittest discovery: 209 passed, 3 skipped; 14.61 sec external wall and
  475,725,824-byte maximum RSS under one-thread numeric caps
- full pytest: 206 passed, 3 skipped, 25 subtests passed; 15.02 sec external
  wall and 499,466,240-byte maximum RSS
- full Ruff, compileall, dependency-light import, root and three Loop 22 CLI
  helps, registered fixture create/inspect, and `git diff --check`: passed
- dependency-light import loaded no NumPy, Torch, or MNE
- registered gate was run once only; later verification uses alternate seeds
  and does not open the registered fixture

## Loop 23 preregistration - streaming CTC prefix decoder

Preregistered on 2026-07-10 before any Loop 23 fixture, target array, decoder
source, or test partition existed. Primary-source review covered the original
CTC blank/repeat and prefix-search formulation, incremental edit overhead and
correction time, streaming partial-hypothesis stability, emission latency, and
Brain2Qwerty v2's noncausal limitation.

Frozen design:

- exact Loop 22 checkpoint/hash, with no new parameter update or training run
- fresh physical 48/8/8 fixture using seeds 2301/2302/2303
- every six-to-eight-symbol target contains all five symbols and an adjacent
  repeated pair separated by a generated blank interval
- class 0 blank; synthetic `A-E` symbols; no natural text or word metric
- fixed greedy CTC comparator and width-8 float64 log-space prefix beam
- no language model, lexicon, insertion bonus, threshold, or decoder sweep
- exhaustive tiny-path probability oracle plus hand-built blank/repeat tests
- frame-indexed partial trace, edit overhead, revisions, first emission,
  first-correct, stable-correct, correction delay, and flush finalization
- model-frame timing separated from transport availability and endpointing
- train-target-only sequence prior plus zero-signal frozen-pipeline control
- validation schedule replay before one canonical test open
- 1 MiB fixture/report caps, 4 KiB decoder state, 20-second runtime, 768 MiB
  RSS, and one CPU thread

Implementation must begin with alternate seeds. The registered target/test
cannot be created until decoder semantics, access tests, full-suite checks, and
a full-size nonregistered rehearsal pass.

## Post-roadmap Loop 23 - streaming CTC decoder parked

Completed on 2026-07-10 from the preregistered `24ef1a9` protocol. Decoder,
fixture, metrics, access-gate, CLI, and tests were committed as `08b23d7` and
pushed before the registered seed-2303 partition existed.

Implemented:

- pure-Python greedy and width-8 log-space prefix CTC with separate
  blank/nonblank probabilities and deterministic ties
- exhaustive tiny-path oracle plus blank-separated repeat and chunk tests
- strict 48/8/8 physical synthetic symbol partitions with target-only train
  access, manifest/hash binding, collision refusal, and byte caps
- train-only complete-sequence prior and zero-signal frozen-pipeline controls
- final CER/exact/repeat metrics, paired bootstrap, partial timing, revision,
  edit-overhead, and finalization reports
- five-schedule frame-indexed replay with bounded encoder/decoder state
- create, metadata-only inspect, and strict one-time gate CLI commands

Observed registered result:

```text
fixture items / frames:                 64 / 1,472
fixture bytes:                          141,412 of 1 MiB
validation prefix CER / exact:          0.018182 / 0.875000 (pass)
frozen test prefix CER / exact:         0.054545 / 0.625000 (FAIL)
required frozen exact:                  0.750000
test repeated-pair recovery:            10/10
test prior / zero-signal CER:           0.800000 / 0.890909
test CER-reduction intervals:           [0.638374,0.870536] / [0.766369,0.897321]
prefix minus greedy CER:                0.0
wrong test rows:                        3, each target plus one tail symbol
stream schedules / pushes:              5/5 / 1,327 validation pushes
right context / encoder / prefix state: 0 samples / 300 / 290 bytes
internal / external runtime:            0.713611 / 0.91 sec
internal / external peak RSS:           214,319,104 / 226,410,496 bytes
JSON / Markdown / total report:         363,578 / 1,334 / 364,912 bytes
train / validation / test opens:        1 / 1 / 1
training / parameter updates:           0 / 0
raw / real / natural text / network:    0 / 0 / 0 / 0
```

Interpretation: CTC mechanics, repeated labels, access order, replay, controls,
and resources are validated, but the sequence gate fails. Stability metrics
show zero revisions even on stable wrong tails, demonstrating that stable output
is not necessarily correct output. Seed 2303 is consumed and must not be
reopened for tuning or treated as a fresh test.

Decision: park Loop 23 and block Loop 24 precision work. The next action is
preregistration only for a fresh Loop 23.5 target-independent blank/boundary
calibration gate; no target-length trim, language model, larger encoder, real
holdout, or seed-2303 reuse is authorized.

Closeout verification:

- focused Loop 23 decoder/fixture/metrics/gate tests: 16 passed
- full unittest discovery: 225 tests passed, 3 skipped; 13.18 sec external wall
  and 470,319,104-byte maximum RSS
- full pytest: 222 passed, 3 skipped, 25 subtests passed; 13.38 sec external
  wall and 481,918,976-byte maximum RSS
- full Ruff, compileall, dependency-light imports, root and three Loop 23 CLI
  helps, and `git diff --check`: passed
- pre-Loop-23 baseline was 209 unittest tests with 3 skipped; all 16 added
  Loop 23 tests pass and no prior test regressed
- registered seed 2303 was opened only by the single gate run; final suites use
  temporary alternate seeds and do not reopen registered artifacts

## Loop 23.5 preregistration - blank intercept calibration

Preregistered on 2026-07-10 before implementation, fresh targets, any fitted
intercept, or seed 2353 existed.

Frozen design:

- exact Loop 22 checkpoint and unchanged Loop 23 greedy/prefix decoders
- fresh physical 64/16/16 splits at seeds 2351/2352/2353; protocol hash
  `ac8b0dfa1ee512dd55645356546a068bc6b7e145f945a2e947d63dcf87185cc9`
- one float64 additive blank-logit intercept; symbol logits and slope unchanged
- one convex train-frame binary-log-loss fit by exactly 80 bisection iterations
  in `[-8,8]`; no candidate, restart, temperature, or regularization
- calibration train access opens signals/frame labels but not target arrays;
  prior access separately opens targets but not signals
- unmodified decoder, calibrated/unmodified greedy, train-only prior, and both
  zero-signal variants remain visible
- validation requires 14/16 exact, CER at most 0.03, at least two corrected
  items and tail tokens, zero new errors or per-item CER regressions, blank
  NLL/Brier improvement, repeated-label preservation, controls, and 5/5 replay
- one conditional canonical seed-2353 test open; no test replay or later fit
- one CPU thread; 1 MiB fixture/report, 2 MiB total generated artifacts,
  16 MiB working arrays, 20-second runtime, and 768 MiB RSS caps

Research basis: original CTC makes blank probability part of the alignment
distribution; post-hoc calibration and logit-adjustment literature support
testing low-parameter score corrections; blank-regularized CTC shows blank
occupancy is a real lever but changes training and is not this method. The
class-weighted Loop 22 logits motivate the hypothesis but do not prove it.

Implementation order: analytic fit/oracle tests, strict disjoint access, decoder
comparators, metrics, replay, and CLI; then a full-size alternate rehearsal at
9351/9352/9353; then full verification and an implementation commit/push. Only
after that may the registered fixture or seed 2353 exist.

Evidence: `docs/LOOP_23_5_PREREGISTRATION.md`.

## Post-roadmap Loop 23.5 - blank intercept calibration passed

Completed on 2026-07-10 from preregistration commit `f7f84db`. Alternate
implementation, access tests, CLI, and the full gate were committed as
`baeea77` and pushed before registered seed 2353 existed.

Implemented:

- dependency-free blank-vs-nonblank margin calibration with an exact
  80-iteration float64 bisection fit;
- analytic and independent dense-grid fit checks plus malformed-input tests;
- frame-only train access that does not index target arrays, separate
  target-only prior access, strict split/member/hash validation, and explicit
  open-order auditing;
- one additive blank-logit hook through unchanged greedy, prefix, zero-signal,
  and replay paths;
- paired corrections/regressions/tail metrics, frame NLL/Brier/ECE, and a
  deterministic 2,000-resample paired bootstrap;
- collision refusal, one-thread enforcement, report-byte convergence, and
  fixture/item/frame/state/runtime/RSS/output caps;
- registered fixture create, metadata-only inspect, and strict conditional gate
  CLI commands.

The full-size alternate 9351/9352/9353 rehearsal passed both mechanical gates:

```text
fixture / report / combined bytes:        204,720 / 756,215 / 960,935
validation calibrated CER / exact:        0.000000 / 16 of 16
alternate test calibrated CER / exact:    0.008929 / 15 of 16
alternate test unmodified CER / exact:    0.062500 / 9 of 16
corrections / new errors:                 6 / 0
runtime / peak RSS:                       1.276594 sec / 212,959,232 bytes
```

After `baeea77` matched upstream, the registered 2351/2352/2353 fixture was
created once. Metadata-only inspection passed without partition access.
Validation then passed the fixed rule and the gate opened seed 2353 once.

```text
fitted blank intercept:                   5.130175197684084
train NLL before / after:                 0.084489 / 0.007248
train Brier before / after:               0.025056 / 0.000898
validation calibrated CER / exact:        0.000000 / 16 of 16
validation unmodified CER / exact:        0.087719 / 6 of 16
validation corrections / regressions:     10 / 0
frozen test calibrated CER / exact:       0.000000 / 16 of 16
frozen test unmodified CER / exact:       0.081818 / 7 of 16
frozen test corrections / regressions:    9 / 0
frozen test removed tail tokens:          9
test exact-gain interval:                 [0.312500, 0.812500]
test CER-reduction interval:              [0.045387, 0.119420]
calibrated / unmodified replay:            5/5 / 5/5
train / validation / test opens:          2 / 1 / 1
test replays / post-open fits:             0 / 0
```

Resources:

```text
fixture items / frames / bytes:           96 / 2,190 / 203,700
report / combined generated bytes:        765,477 / 969,177
working core bytes:                       438,874
encoder / prefix / greedy state bytes:    300 / 294 / 24
internal runtime / peak RSS:              1.266573 sec / 213,958,656 bytes
training / updates / real reads:           0 / 0 / 0
```

Pre-registered-run verification passed: 26 focused tests; 238 unittest tests
with 3 skips; 235 pytest tests with 3 skips and 25 subtests; full Ruff;
`git diff --check`; all Loop 23.5 CLI help paths; exact upstream match. The
pre-change Loop 23 baseline was 225 unittest and 222 pytest tests, each with 3
skips, so 13 tests were added without regression. Final post-documentation
verification must use temporary alternate fixtures and must not reopen seed
2353.

Decision: Loop 23.5 passes as a supervised synthetic calibration mechanism.
Seed 2353 is consumed. Preregister Loop 24 before any precision candidate,
tolerance, or benchmark; do not infer real-neural, endpoint, or latency
performance from this result.

Evidence: `docs/LOOP_23_5_BLANK_INTERCEPT_CALIBRATION.md` and ignored local
artifacts under `cache/loop235_blank_intercept/`.
