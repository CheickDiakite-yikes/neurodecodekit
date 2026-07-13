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

## 2026-07-10 - Real-World Practice Track RW0 research gate

Added a parallel, non-renumbering practice track after a current primary-source
review. The machine-readable result covers eight dataset records across six
separate task cohorts and 13 device records with explicit EEG, EMG, EOG, eye,
PPG, IMU, microphone, and hand-tracking distinctions.

The local metadata inventory found only consumed S21 MEG and S7 EEG raw
signals. It did not open their arrays. The smallest fresh task-matched EEG
candidate is S20 session 2 block 2 at exactly 96,090,264 bytes. Its 204,940-byte
MAT log already exists locally but was not parsed. No acquisition is
authorized. The packet requires four exact files at revision
`88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`, a 128-MiB download cap, 16-MiB
generated cap, one worker/thread, and a target-free 44/10/10 trial split.

Research access counters: zero raw reads, consumed-cache reads, model runs,
training runs, target-log parses, and downloads. An isolated research
runtime/RSS measurement was unavailable and is recorded as such. The pre-edit
project baseline in `.venv` was 238 unittest tests with 3 skips in 12.27 seconds
and 479,182,848-byte peak RSS. A system-Python invocation first failed with
five missing-optional-dependency errors; it is retained as environment evidence
and is not a repository regression.

Decision: RW0 authorizes RW1 synthetic-fixture metadata intake only. S20 stays
blocked, Loop 24 keeps its independent preregistration path, and no live device
or scientific decoding claim was added.

## 2026-07-10 - RW1 metadata-only local intake

Added a dependency-free level-0 scanner in
`src/neurodecodekit/datasets/local_intake.py` plus create/inspect CLI commands.
The scanner recognizes BrainVision, EDF/EDF+, BDF, EEGLAB, FIF, and BIDS,
emits deterministic JSON/Markdown plus a measured audit sidecar, validates
source/config/registry/artifact hashes, and records every unavailable field,
warning, refusal, cap, and forbidden-access counter.

Safety coverage includes resolved root binding, symlink/traversal refusal,
BrainVision companion roles, EEGLAB sibling discovery, FIF filename
continuity, bounded BIDS traversal, archive/pickle/executable refusal reports,
unknown-input reports, text allowlists, NUL rejection, input/text/output caps,
collision refusal, and exact output tamper detection. No MNE, NumPy, SciPy,
Torch, BrainFlow, LSL, or Gradio import occurs in this path.

The ignored synthetic BrainVision roundtrip declares 532 source bytes and
reads 26,365 text bytes from one VHDR plus the tracked dataset registry. It
writes 7,795 bytes of deterministic JSON, 2,181 bytes of deterministic
Markdown, and a 1,569-byte measured audit, totaling 11,545 bytes. Internal
runtime is 0.001659 seconds and process peak RSS is 21,643,264 bytes. Binary,
raw, cache, target/label, model, training, and network counters are all zero;
end-to-end latency and producer causality are unavailable.

Verification: 11/11 focused tests; 249 unittest tests with 3 skips in 11.317
seconds and 496,943,104-byte maximum RSS; 246 pytest tests with 3 skips and 25
subtests in 11.13 seconds and 507,559,936-byte maximum RSS. Ruff, compileall,
root/create/inspect CLI help, strict roundtrip inspection, and
`git diff --check` pass. The pre-change baseline was 238 unittest and 235
pytest passes with the same skips/subtests.

Decision: close RW1. RW2 may be preregistered but no signal reader or quality
metric is authorized. S20 remains blocked and no scientific decoding claim is
added.

## 2026-07-10 - RW2 primary-source research and preregistration

Researched the active optional stack and upstream behavior before writing any
RW2 reader. The local environment has MNE 1.12.1, NumPy 2.5.0, and SciPy
1.18.0; MNE-BIDS and PyEDFlib are not installed, and the package base dependency
list remains empty. Primary MNE/MNE-BIDS/BIDS documentation, maintained reader
source, COBIDAS, PREP, Autoreject, and the public Brain2Qwerty v2 paper were
reviewed. The resulting source ledger is in
`docs/RW2_PRIMARY_SOURCE_RESEARCH.md`.

The review changed the protocol in four important ways. BIDS dispatch uses the
RW1 resolver and direct format readers because `read_raw_bids` can import
events and bad-channel sidecars. EEGLAB is restricted to continuous external
`.fdt` fixtures because an embedded `.set` matrix can be materialized despite
`preload=False`. EDF/BDF reaches level 2 only when one source sampling rate is
proven because mixed-rate lazy slices can involve upsampling. All readers use
explicit arguments so channel-role inference, exclusions, split handling, and
MaxShield behavior are not hidden defaults.

Commit `eacb231` freezes `registries/signal_quality_contract.v0.json` and
`docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md` before implementation. The
contract limits work to six generated format families, at most 512 channels,
three deterministic windows, 4,194,304 channel-sample values, 32 MiB of
materialized float64 signal, one thread, 30 seconds, 1 GiB peak RSS, 4 MiB per
run, and 16 MiB for the full fixture/report set. It requires deterministic
descriptive amplitude/structure/median-Welch summaries, privacy redaction,
source no-mutation checks, exact unavailable states, strict replay/tamper/cap
tests, and no automatic cleaning.

Access accounting for this preregistration: zero raw or signal-array reads,
zero real-cache reads, zero target/label reads, zero model or training runs,
zero downloads, zero network acquisition calls, and zero generated signal
artifacts. The machine-contract invariant check and `git diff --check` passed
before the registration commit was pushed. This is protocol evidence only; no
format has yet passed a synthetic RW2 read and no real signal-quality or
decoding claim was added.

Closeout verification retained the 249-test unittest baseline with 3 skips
(11.714 seconds; 491,683,840-byte maximum RSS) and the 246-test pytest baseline
with 3 skips plus 25 passing subtests (12.51 seconds; 489,914,368-byte maximum
RSS). Seven focused NeuroToken tests and all 11 RW1 tests passed. Ruff,
compileall, root/RW1 CLI help, the corrected machine-contract invariant query,
workbook formula inspection, all-eight-sheet visual inspection, exact
tracked/delivered workbook hashing, and `git diff --check` passed. The updated
workbook is 54,836 bytes with SHA-256
`c27d80d4831acc91795b2cbf10d7e00400ff393f58bfd029a7653e0e328dc669`.
Generated inspection output remains ignored, and the pre-existing untracked
tracker inspection NDJSON was not modified or staged.

## 2026-07-10 - RW2 synthetic signal-quality implementation and closeout

Implemented the exact `eacb231` preregistration in
`src/neurodecodekit/preprocess/signal_quality.py` and
`src/neurodecodekit/training/synthetic_signal_quality.py`, with four CLI
commands and nine focused tests. Optional `neuro` now pins MNE to `>=1.12,<1.13`
so the reader signature/behavior line matches the frozen evidence.

The deterministic fixture tree contains 40 rows across six format families:
38 readable sources and two exact refusals. Four unsupported export
combinations are documented rather than synthesized inaccurately. All readable
fixtures preserve lazy open, expected channel/timing/value/geometry/reference/
event identity, source no-mutation, privacy redaction, descriptive time/PSD
metrics, and exact payload replay.

The measured closeout reused the existing 3,937,717-byte fixture tree because
the local volume had only 3.4 GiB free. One clean FIF report selected nine
channels and windows of 384/512/384 samples, requested and returned 11,520
values in six bounded calls, and materialized 92,160 bytes. It wrote 76,592
bytes in 3.839168 seconds with 150,749,184-byte internal peak RSS. Raw-reader
opens were one; real/cache/target/model/training/network access was zero. The
producer is explicitly offline noncausal and end-to-end latency is unmeasured.

An initial CLI attempt supplied a broader root than the RW1 binding and refused
with `Selected source does not match the RW1 report.` before producing an
artifact. The exact-bound rerun passed. This refusal is retained as provenance
evidence.

Verification: nine focused RW2 tests; 258 unittest tests with 3 skips in 21.283
seconds and 492,044,288-byte external maximum RSS; 255 pytest passes with 3
skips and 25 subtests in 23.77 seconds and 523,501,568-byte maximum RSS. The
zero-dependency run passes 246 tests with 118 optional skips in 0.285 seconds
and 40,845,312-byte maximum RSS. Ruff, compileall, all RW2 CLI help,
deterministic replay, strict saved-report inspection, package metadata, and
`git diff --check` pass.

Decision: close RW2 at exact synthetic compatibility level 2. RW3
preregistration is next; no BrainFlow, LSL, live source, real recording, S20,
hardware, automatic cleaning, model, or training is authorized.

Evidence: implementation commit `2796dee` and
`docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md`.

The eight-sheet tracker was updated through the bundled artifact-tool workflow,
rendered before and after, checked for formula errors, and promoted only after
visual repair. The tracked/delivered workbook is 55,674 bytes with SHA-256
`f1c08a2e6f8e0e9889a525af5d3cb04977e7dca87b0fdb6d6810854cdcd32d2e`.

## 2026-07-10 - Open-source contribution and GitHub surface

Replaced the chronological starter README with a proof-first guide and added a
prominent results dashboard. Engineering wins, real-data scientific outcomes,
resource measurements, and proof labels are separate so synthetic accuracy
cannot conceal the negative real MEG/EEG comparisons.

Added Apache-2.0 `LICENSE`, `NOTICE`, third-party/data terms, citation,
contribution, code-of-conduct, governance, support, security, issue forms, PR
template, CODEOWNERS, and one-thread base/neuro CI. The contributor guide has
dedicated paths for EEG data owners and EEG headset/board owners, beginning
with metadata and deterministic replay rather than recording upload.

The base-CI rehearsal exposed five old optional-test guard failures. Collection
and missing-dependency tests now skip cleanly without NumPy/MNE/SciPy, while the
same paths run in the optional environment. A lightweight `array` extra allows
NumPy-only synthetic/NPZ work without installing MNE or Torch.

Tracked-history checks found no recording/cache files and no secret. Gitleaks
passes with the default rules and one exact reviewed fingerprint for a
documented NeuroToken SHA-256. TOML, YAML/CFF, local Markdown links, package
metadata, Ruff, compileall, and whitespace checks pass.

GitHub received a proof-accurate description, 16 topics, and eight issue
labels. The repository was private at the first check and reported public at
the later check although no visibility command was issued. PR #1 subsequently
merged this open-source surface through `e5d89ed` at main commit `18a705e`.
Draft PR #2 carries the latest evidence closeout; the maintainer must still
decide whether public visibility should remain before release signoff.

Evidence: open-source milestone commit `e5d89ed` and
`docs/OPEN_SOURCE_READINESS.md`.

## 2026-07-10 - Public CI float32 portability finding

The first public optional-neuro CI run passed the focused nine-test RW2 suite
but failed two Loop 21 causal-replay assertions. Commit `5c212c8` added
per-condition gate diagnostics without changing any threshold. The next Linux
run isolated the sole failure as
`all_schedules_offline_compatible`: NumPy 2.5.1/OpenBLAS produced a
`1.430511474609375e-6` maximum difference between Loop 20's historical batched
float32 matrix multiply and Loop 21's canonical one-frame multiply. Runtime was
0.060795 seconds and peak RSS was 59,772,928 bytes; schedule identity,
timestamps, frame grid, causality, state, and resources passed.

The same Python 3.12/NumPy 2.5.1 combination on macOS reproduced the historical
`9.5367431640625e-7` maximum. Decision 0044 therefore amends only this
cross-BLAS compatibility default to `2e-6`. Canonical stream payloads must
still be bitwise identical across all five schedules. No real/target/model/
training/holdout access occurred, and no scientific result changed.

The amended commit passed all four GitHub Actions checks: base and
optional-neuro on both push and pull-request events. A final default-branch
refresh showed PR #1 already merged. GitHub's license endpoint still returned
`spdx_id: null` because the Apache appendix in `LICENSE` contained a project
copyright instead of the canonical placeholder. PR #2 restores the exact
Apache 2.0 text; the project copyright remains in `NOTICE`.

## 2026-07-10 - RW3 replay/live-source equivalence preregistration

Researched BrainFlow 5.22.2, pylsl 1.18.2/liblsl 1.17.7, PyXDF 1.17.5, and
Python monotonic-clock behavior from maintained primary sources. The review
found that BrainFlow playback can regenerate timestamps unless configured to
preserve old values, BrainFlow exposes both draining and nondraining reads, LSL
is unsynchronized by default and separates source timestamps from clock
correction, LSL automatic postprocessing destroys the original timestamp view,
and PyXDF defaults to synchronized/dejittered timestamps. Device and transport
latency remain distinct from clock synchronization.

Commit `c3d1f01` freezes `neurodecodekit.replay_equivalence_contract` v0.1.0
and the future `neurodecodekit.source_chunk` v0.1.0 before implementation. The
contract separates source, corrected, and local monotonic arrival timestamps;
represents gaps, duplicates, reordering, packet-counter wraps, reconnects, and
clock resets explicitly; and forbids interpolation, silent sorting, and silent
deduplication. It registers five chunk schedules, 18 future target-free fixture
families, 30 exact refusal IDs, exact semantic and boundary-sensitive hashes,
and four sequential adapter stages.

Future resource caps are one thread/worker, 512 channels, 4,096 Hz, 4,194,304
channel-sample values, 32 MiB materialized payload, 16 MiB source/fixture bytes,
4 MiB output per run, 32 MiB total generated artifacts, 30 seconds, and 1 GiB
peak RSS. Real/consumed/cache/target/model/training/decoder/network access must
remain zero in Stage A.

Seven focused dependency-free contract tests passed. The registration itself
installed or imported no BrainFlow, pylsl, liblsl, or PyXDF; generated no
fixture or waveform; opened no socket, board, stream, XDF, real recording,
cache, target, or consumed evidence; and ran no model or training. Stage A is
not automatically authorized. No signal-quality, neural-advantage, decoding,
device-reliability, end-to-end-latency, portable-hardware, or clinical result
was established.

Evidence: `docs/RW3_PRIMARY_SOURCE_RESEARCH.md`,
`docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md`,
`registries/replay_equivalence_contract.v0.json`, and commit `c3d1f01`.

The synchronized public-documentation gate then passes 265 unittest tests with
3 skips and 262 pytest tests with 3 skips plus 25 subtests, exactly seven more
than the pre-RW3 baseline. The true zero-dependency run passes 253 tests with
118 expected optional skips. Focused contract runtime/peak RSS is 0.040 seconds
wall/18,022,400 bytes; full-run maxima are 13.920 seconds wall and 579,354,624
bytes. Ruff, compileall, root CLI help, JSON/TOML parsing, 39 local Markdown
links, workbook formula checks, eight-sheet render review, and diff checks pass.

The updated tracker is 56,304 bytes with SHA-256
`fdb6d38217682e29033eeb623ffe46f20debd12e82ade4866a6b58d06d80daa9`.
It records RW3 as review-stage protocol evidence, not a completed runtime gate.
Draft PR #2 then passed all four GitHub Actions checks on commit `ee5ce63`:
base and optional-neuro jobs for both push and pull-request events.
The final GitHub metadata audit now reports `Apache-2.0` for `LICENSE` on
default-branch commit `18a705e`; the earlier null result was a transient
detection state. PR #2 still restores the exact canonical appendix wording and
keeps project copyright in `NOTICE`.

## 2026-07-11 - RW3 Stage A decision packet and public results refresh

Prepared `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md` and
`registries/rw3_stage_a_authorization_request.v0.json` at commit `163ff2f`.
The request is bound to the exact frozen contract SHA-256 and Git blob, proposes
five schedules by 18 fixture families (90 future cases), carries all 30 refusal
IDs and exact resource/access caps, and requires an authorization-only commit
before implementation. `authorized_now` remains false. No source chunk,
fixture, replay runtime, CLI command, optional dependency, socket, board,
stream, XDF, device, real or consumed data, target, model, decoder, or training
operation was added or run.

Expanded the README into a public result ladder plus detailed engineering,
real-data scientific, and resource scorecards. The strongest engineering
results are visible beside the negative real MEG/EEG comparisons. A new EEG
contribution launch table gives separate first steps for recording owners,
headset/board owners, and contributors without hardware, while preserving local
privacy and staged compatibility boundaries.

Three new contract/request tests raise the measured suite from 265 to 268
unittests and from 262 to 265 pytest passes, with the same three optional skips
and 25 pytest subtests. The complete unittest run takes 15.390 seconds wall with
566,394,880-byte maximum RSS; pytest takes 13.320 seconds wall with
577,814,528-byte maximum RSS. The 10-test focused gate takes 0.040 seconds wall
with 20,529,152-byte maximum RSS. The true zero-dependency Python 3.12 run passes
256 tests with 118 expected optional skips in 0.320 seconds wall and
39,141,376-byte maximum RSS.

The tracker was updated through the bundled artifact-tool workflow, rendered
before and after across all eight sheets, reloaded, and checked with zero formula
errors. The tracked and delivered files are both 56,867 bytes with SHA-256
`2e47b86dd66769135278faeb218494d4719b61e705820f80b5afa961f2c57901`.
The dashboard, Practice Track, Decision Log, and Prompt Bank all record the
packet as a review-stage decision surface, not a runtime result.

The live GitHub About profile was refreshed without changing visibility or the
default branch. The description now identifies NeuroDecodeKit as an open-source,
local-first EEG/MEG research toolkit and names bounded access, honest baselines,
reproducible caches, and proof boundaries. Four discoverability topics were
added (`eeg-analysis`, `neuroinformatics`, `open-science`, and `open-source`),
bringing the exact topic set to 20. The repository remains public with issues
enabled, Discussions and Wiki disabled, `main` as default, and Apache-2.0
detected.

Final local checks pass: Ruff, compileall, every tracked JSON file, TOML,
all 43 local Markdown links, root and selected command help, `git diff --check`,
268 unittests, 265 pytest tests plus 25 subtests, the 256-test dependency-free
run, and the 10-test focused RW3 contract/request gate. Staged Gitleaks and all
four GitHub Actions jobs are checked around the final commit and push.

## 2026-07-11 - Loop 24 local precision/runtime preregistration

Researched the full Brain2Qwerty v2 architecture and PyTorch numerical,
threading, benchmark, inference-mode, automatic-mixed-precision, eager dynamic-
quantization, and torchao migration behavior from primary sources. The review
found that the full published architecture is too different from the local
1,130-parameter synthetic MLP to support transfer claims; PyTorch does not
promise bitwise floating-point identity across platforms or execution paths;
CPU autocast defaults to bfloat16 rather than float16; dynamic quantized Linear
uses qint8 packed weights with float inputs and outputs; and tiny timings require
warmup, replicated measurements, fixed threads, and balanced execution order.
Mac `powermetrics` is retained only as an optional within-device proxy because
its own manual warns against accurate or cross-device power interpretation.

Commit `186bb6f` freezes `neurodecodekit.local_precision_runtime_contract`
v0.1.0 before implementation. The exact candidates are float32 eager,
explicit float16 CPU, and dynamic qint8 under QNNPACK. Bfloat16, autocast,
static quantization, QAT, torchao, compile, TorchScript, ONNX, CoreML,
ExecuTorch, MPS, pruning, batching, and architecture changes are excluded from
this gate. The contract binds the existing producer, probe, checkpoint,
blank-intercept, and decoder hashes without opening any of them.

A future target-free fixture is physically split into seed-2401 selection and
seed-2402 qualification partitions, each with 48 items across six waveform
families. It contains signals, input lengths, item IDs, and metadata only; model
outputs, targets, labels, text, participants, and source paths may not create or
select rows. The selection schedule contains 12 exact candidate permutations,
placing each candidate in every order position four times. Qualification opens
only if a nonreference replacement passes selection, using six alternating
reference/candidate rounds.

Behavioral gates cover frame grids, timestamps, valid lengths, padding, greedy
paths and traces, width-8 prefix traces/finals, flush behavior, and causal
status. Measurements keep producer, fixed decoder, and complete pipeline time
separate. A replacement needs a producer median ratio at most 0.80, full-
pipeline median at most 0.90, p95 at most 0.95, upper paired 95% ratio at most
0.98, no payload growth, at most 32 MiB RSS increase, and both partitions.
Storage-only status instead requires at least 50% payload reduction and 2,048
bytes saved while pipeline median/p95 remain within 1.05; it cannot replace the
default or open qualification. Thirty refusal IDs and explicit proceed, park,
and kill rules freeze unsupported backends, leakage, nonfinite outputs,
behavior drift, fallback, collisions, caps, and unauthorized access.

Resource caps are one numerical thread, one concurrent worker, 48 workers,
512 KiB per fixture, 64 KiB per candidate payload, 32 MiB materialized arrays,
1 MiB report output, 4 MiB total generated artifacts, 60 seconds internal
runtime, and 1 GiB peak RSS per worker. All network, real/consumed/cache/target/
label/text/training and RW3 counters must remain zero. Energy measurement is
outside the primary cap, optional, and forbidden from prompting for sudo.

The contract SHA-256 is
`58e9d5407fef9419bc3bb0dc8cd3fa68d36dd238cb636d2f833dd9c5c6c3ae5d`.
Nine focused dependency-free invariants pass in 0.070 seconds wall with
20,791,296-byte peak RSS. The full unittest run reaches 277 passes with three
skips in 14.220 seconds wall and 569,884,672-byte peak RSS; pytest reaches 274
passes, three skips, and 25 subtests in 13.200 seconds wall and 576,421,888-byte
peak RSS. The true zero-dependency run reaches 265 tests with 118 expected
optional skips in 0.350 seconds wall and 40,861,696-byte peak RSS. The previous
268/265 unittest/pytest baseline therefore gains exactly nine invariants without
regression. Ruff, compileall, JSON/TOML parsing, local links, CLI help, diff
checks, and staged Gitleaks pass.

No fixture, candidate module, CLI command, checkpoint read or conversion,
inference, benchmark, profiler, energy, qualification, real/consumed data,
target, model-training, or RW3 operation was added or run. This milestone
registers a future local execution experiment; it does not establish a speedup,
integer-only execution, retained neural accuracy, end-to-end text latency,
portable hardware, or decoding.

Evidence: `docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`,
`registries/local_precision_runtime_contract.v0.json`, and commit `186bb6f`.

The tracker was imported and edited through the bundled artifact-tool runtime,
rendered before and after across all eight sheets, reloaded from the exported
XLSX, and scanned with zero formula errors. Dashboard, Practice Track, Decision
Log, and Prompt Bank now present Loop 24 and RW3 Stage A as separate explicit
decisions. The prompt-bank repair also wraps the final RW3/Loop 24 decision rows
instead of allowing long text to spill horizontally. The tracked and delivered
workbooks are both 57,413 bytes with SHA-256
`d0b1959fab1201eb8391733a1723ee803bf167441ecd48788f4f8179d16c78c4`.

The final documentation-inclusive verification preserves all counts: 277
unittest passes with three skips, 274 pytest passes with three skips and 25
subtests, 265 true zero-dependency tests with 118 expected optional skips, and
9/9 focused Loop 24 invariants. Final wall/RSS maxima are 15.460 seconds and
580,567,040 bytes. No Loop 24 or RW3 runtime, fixture, data, target, model, or
training operation was introduced by the documentation/workbook sync.

## 2026-07-11 - Clarify original-roadmap count versus current gate

The tracker dashboard previously displayed `Total loops: 20` while the current
post-roadmap position was Loop 24. The value was formula-correct because it
counts the original 20-row `Loop Tracker` table, but the label and title made
the two scopes too easy to confuse.

The dashboard now says `Original roadmap loops: 20`, `Original completed: 19`,
`Original parked: 1`, and `Current numbered gate: Loop 24 preregistered`. Its
scope note names Loops 21-22 as done, Loop 23 as parked, Loop 23.5 as done, Loop
24 as preregistered but unauthorized, and RW3 Stage A as separately
unauthorized. The phase table and chart now explicitly describe the original
20 loops. The Markdown tracker and README documentation map carry the same
distinction.

The artifact-tool edit preserves the original-loop count formula and all phase
formulas. All eight sheets render, the exported workbook reloads, and the
formula-error scan finds zero matches. The tracked workbook is 57,473 bytes
with SHA-256
`3bb5b2ab03b4327912024bac401fb76ae682151df96140a379514e36caa22f82`.

## 2026-07-12 - Research and freeze the next 20-loop planning tranche

Reviewed Brain2Qwerty v1/v2, MNE resampling, BIDS derivatives, the MOABB
benchmark, LSL clock synchronization, ExecuTorch, EEG identity privacy, the
NIST Privacy Framework, model cards, datasheets, and selective prediction from
primary or maintained sources. The review found that the highest-value next
steps are not 20 larger-model variants: causal preprocessing, fresh evidence,
neural-versus-language attribution, subject transfer, peripheral confounds,
geometry/reference identity, timestamp semantics, privacy, cross-machine
reproduction, and one-device qualification are the missing gates.

Commit `56a1c0a` adds `neurodecodekit.next_twenty_loops_roadmap` v0.1.0 plus
the human research and roadmap documents. The contract contains exactly Loops
25-44, five phases of four loops, backward-only loop dependencies, protected
S7/S21 and seed boundaries, one-thread and 32-MiB defaults, detailed controls,
metrics, acceptance and stop rules, authorization boundaries, 12 primary
sources, and row-level source mappings. Every loop is `Not Started` with
`execution_authorized: false`.

Nine dependency-free invariants pass in 0.070 seconds wall with 18,071,552-byte
peak RSS. The full optional unittest run reaches 286 passes with three skips in
20.180 seconds (21.320 seconds wall, 570,392,576-byte maximum RSS). Pytest
reaches 283 passes, three skips, and 105 subtests in 18.78 seconds (20.010
seconds wall, 579,158,016-byte maximum RSS). The true zero-dependency run
reaches 274 tests with 118 expected optional skips, exactly nine more than the
pre-roadmap 265-test baseline.

The tracker was imported and edited only through the bundled artifact-tool
runtime. Its ninth `Loops 25-44` sheet is generated from the JSON contract and
contains frozen panes, filters, status validation, detailed work orders,
proof/authorization fields, resource caps, and row-level source URLs. All nine
sheets were rendered; the workbook was exported, reloaded, inspected at the
first and last roadmap rows, and scanned with zero formula-error matches. The
tracked and delivered files are both 75,181 bytes with SHA-256
`775e907e63277fd42e536421715ce116adfb837b71bfdf270e70024dd39a13aa`.

No dataset download, raw/real/consumed-cache/target read, fixture generation,
checkpoint access, candidate conversion, model or decoder run, training,
BrainFlow/LSL/PyXDF operation, socket, stream, board, device, or hardware
session occurred. This milestone makes the next evidence queue detailed and
machine-checkable; it establishes no new decoding, neural, transfer, latency,
or device result.

## 2026-07-12 - Record narrow Loop 24 authorization before implementation

Recorded the user's explicit Loop 24 authorization in
`registries/loop24_authorization_decision.v0.json` and
`docs/LOOP_24_AUTHORIZATION_DECISION.md`. The decision is bound to parent
`4050b85`, preregistration commit `186bb6f`, the exact frozen contract SHA-256,
and its Git blob. The preregistration remains unchanged with false flags; the
separate current authority permits only target-free fixture generation, frozen
checkpoint validation, the three registered candidates, inference, selection,
conditional one-time qualification, reports, and CLI work after this
authorization-only commit is pushed and CI is confirmed.

Real or consumed data, targets, labels, text, training, parameter updates, new
architectures, energy, RW3, optional streaming stacks, sockets, devices,
hardware, and Loops 25-44 remain false. The user's real-data/training goal is
routed to separately frozen Loops 25-27. S21 source-test/session-2, S7, and
seeds 2203/2303/2353 remain closed. Authorization-only access counters are all
zero: no fixture, checkpoint read, candidate conversion, inference, benchmark,
model/training run, raw/cache/target read, network, stream, board, profiler,
energy, or qualification operation occurred.

Seven new dependency-free tests raise the full optional unittest count from 286
to 293 and pytest from 283 to 290, with three skips and 105 pytest subtests
unchanged. Unittest takes 18.882 seconds (19.880 seconds wall) with
565,280,768-byte maximum RSS; pytest takes 18.80 seconds (20.120 seconds wall)
with 578,502,656-byte maximum RSS. The true zero-dependency run passes 281 tests
with 118 expected skips in 0.359 seconds (0.650 seconds wall) and
41,435,136-byte maximum RSS. The combined 26-test authorization, Loop 24
contract, and RW3 boundary takes 0.210 seconds wall with 21,397,504-byte maximum
RSS.

The tracker was edited with the bundled artifact-tool runtime. Dashboard,
Practice Track, Decision Log, Prompt Bank, and the Loops 25-44 header now agree
on `Loop 24 authorized, no runtime`; all nine sheets render, the exported file
reloads, and the formula-error scan is empty. Tracked and delivered copies are
75,648 bytes with SHA-256
`4be4012eea926b2b417fca3da1665e1f192718a50d5243aebf5d38f02841afb9`.

This milestone authorizes one exact synthetic engineering experiment. It does
not establish a precision speedup, integer-only execution, neural information,
real-data accuracy, decoding improvement, end-to-end latency, useful EEG,
portable hardware, or any clinical result.

## 2026-07-12 - Implement and park Loop 24 after registered selection

Commit `3a5dc0b` implements the exact authorized Loop 24 surface before any
registered fixture or checkpoint read: deterministic physical target-free
selection/qualification fixtures, three explicit CPU candidates, strict
correctness and QNNPACK-profiler provenance, isolated balanced timing,
conditional qualification, converged byte accounting, audit-bound JSON/
Markdown/payload artifacts, strict inspection, and four deferred-import CLI
commands. It adds no base or optional dependency.

The implementation milestone passed 313 unittests with three skips, 310 pytest
tests with three skips and 105 subtests, 36 focused Loop 24 tests, Ruff,
compileall, CLI help, JSON/TOML parsing, diff checks, and staged Gitleaks. The
complete unittest run took 19.963 seconds internal and 20.860 seconds wall with
572,276,736-byte maximum RSS. The true dependency-free Python 3.12 discovery
remained green in 1.49 seconds wall with 51,724,288-byte maximum RSS and 121
optional skips. All four pushed GitHub checks passed before registered fixture
generation.

The registered fixture contains exact seeds 2401/2402, 48 items and six
balanced waveform families per physical partition, 4,536 valid samples per
partition, and no target, label, text, participant, prediction, model-output,
real, or consumed evidence. Selection/qualification files are 64,438/64,216
bytes; the 8,234-byte manifest brings the fixture to 136,888 bytes. Generation
took 0.17 seconds wall with 45,154,304-byte peak RSS. Metadata-only inspection
took 0.06 seconds and 22,183,936 bytes without hashing or opening either NPZ.

The gate opened selection once, extracted 990 complete causal frames, loaded
the exact 7,894-byte checkpoint once, built all three candidates, reproduced
the float32 payload bitwise across three runs, and completed all 12 balanced
rounds in 36 fresh sequential workers. Float16 passed every exact and numerical
correctness gate but was `1.169950x` the float32 producer latency and
`1.087904x` the full-pipeline latency. QNNPACK qint8 proved
`quantized::linear_dynamic` and reduced the deterministic payload from 5,210 to
2,454 bytes, but failed exact decoder behavior and numerical tolerances and was
`2.784595x`/`1.812123x` the producer/full latency. No replacement or
storage-only candidate passed, so qualification seed 2402 remained physically
unopened.

The timing protocol, 455,472-byte working-array cap, 222,248,960-byte maximum
worker RSS, 110,073 report bytes, and 262,822 total fixture-plus-output bytes
all passed. Internal orchestration took 65.154951 seconds against the frozen
60-second cap, so the final decision is `park_resource_cap_exceeded` and
float32 remains the default. External wall time was 65.62 seconds. Selection
seed 2401 is consumed; changing worker startup or rerunning after this result
would require a separately frozen amendment, not post-selection tuning.

Access counters are explicit: one manifest metadata read, one checkpoint read,
one selection open, zero qualification opens, three conversions, 15 reference
and 26 candidate protocol-level inference runs, one profiler run, and 36 timing
workers. Training, parameter updates, target/label/text, real/S7/S21, consumed
seed 2203/2303/2353, network, energy, and RW3 counters are all zero. Generated
fixture, payload, timing, and report artifacts remain ignored and untracked.

This closeout adds a local target-free precision/runtime execution and audit
capability. It establishes no speedup, integer-only execution, neural
advantage, real-data accuracy, CER/WER improvement, unseen-person transfer,
end-to-end latency, energy efficiency, useful EEG, portable hardware,
arbitrary-thought, assistive, diagnostic, or clinical result.

The tracker closeout was performed through the bundled artifact-tool runtime.
It brings the existing `24-AUTH` row inside the Decision Log table, appends the
measured `24-RUN` park, adds risk `R28`, marks the old execution prompt
consumed, and adds the Loop 25 preregistration-decision prompt. All nine sheets
were rendered and visually inspected; the exported workbook reloads with the
Decision Log, Risk Register, and Prompt Bank tables extended to rows 37, 29,
and 34; and the formula-error scan has zero matches. The tracked workbook is
76,476 bytes with SHA-256
`1f65236ac4cee76745f57f57aa137a3e4c0833f84a3c1719d8daffb17019372d`.
The unrelated untracked inspection sidecar remained byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Final closeout verification passes 36 focused Loop 24 tests in 4.07 seconds
wall with 308,510,720-byte maximum RSS; 313 unittests with three skips in
21.32 seconds wall and 570,753,024-byte maximum RSS; 310 pytest tests with
three skips and 105 subtests in 22.38 seconds wall and 583,499,776-byte maximum
RSS; and 281 true zero-dependency Python 3.12 tests with 121 expected optional
skips in 0.60 seconds wall and 42,450,944-byte maximum RSS. The optional suites
are 20 tests above the 293-unittest/290-pytest authorization-only baseline.
Ruff check, compileall, diff checks, all JSON/TOML parses, 54 local Markdown
links, five CLI help surfaces, strict fixture/report inspection, workbook
reload/formula inspection, and the 49-commit Gitleaks history scan all pass.

## 2026-07-12 - Preregister Loop 25 and prepare its decision packet

Loop 25 begins with a primary-source and local-source audit, not a transform.
The official Brain2Qwerty v2 path is documented as offline; local sentence
extraction defaults to zero-phase MNE filtering, whole-recording FFT resampling,
future-dependent scaling options, and endpoint/post-context extraction. Those
are legitimate offline mechanics but cannot inherit Loop 21's causal-producer
claim. The audit binds the current official commit plus five unchanged local
source blobs without reading any recording, cache, target, checkpoint, or model.

Commit `a36d97b` freezes `causal_preprocessing_contract.v0.json` before any
filter coefficient or fixture exists. The proposed five-channel path runs a
stateful 50 Hz Q30 notch SOS, a stateful fourth-order 0.5-45 Hz Butterworth SOS,
phase-locked integer decimation from 1000 to 100 Hz, contract-fixed scaling,
and an inclusive +/-5 clamp. Development seed 2501 and qualification seed 2502
each define 12 target-free items across six families. Seven chunk schedules,
ten resume cuts, three future-mutation cuts, exact source indices/timestamps,
40 refusal IDs, 21 access counters, 4 MiB fixtures, 16 MiB working arrays, 8
MiB total generated bytes, 45 seconds, 4 KiB state, and 1 GiB peak RSS are
frozen. Ten new dependency-free invariants pass, and the complete local suite
at that commit is 323 tests with three expected skips in 21.338 seconds. Both
the base Python and optional-neuro GitHub CI jobs pass.

The second milestone adds `docs/LOOP_25_AUTHORIZATION_PACKET.md` and
`registries/loop25_authorization_request.v0.json`, bound to the full green
registration commit, the contract SHA-256/Git blob, and the research,
preregistration, and invariant-test hashes. All 16 request-level
`authorized_now` fields remain false. Eight request invariants check the binding,
decision language, exact scope, caps, protected evidence, independent Loop 24/
RW3 boundaries, and absent runtime files. The combined contract, request, and
roadmap boundary passes 27 tests in 0.14 seconds wall with 22,216,704-byte
maximum RSS.

Public status surfaces now distinguish the original 20-loop KPI from the
current numbered gate. Loop 24 is historically authorized, consumed, and
parked; Loop 25 is preregistered and awaiting explicit authorization; Loops
26-44 remain `Not Started`; all 20 future execution flags are false. README,
Start Here, AGENTS, handoff, roadmap, tracker, prompt files, decision log, and
machine roadmap agree.

The tracker workbook was edited with the bundled artifact-tool runtime. The
Dashboard now says `Loop 25 preregistered; authorization pending`; Decision Log
adds `25-REG`; Risk Register adds `R29`; Prompt Bank asks for the exact Loop 25
decision; and the Loop 25 row carries the registered proof posture and lower
caps. All nine sheets render cleanly, the exported workbook reloads with table
ranges ending at Decision Log row 38 and Risk Register row 30, and the formula-
error scan has zero matches. The workbook is 77,394 bytes with SHA-256
`8baadcde95ab097a9944d402f1e92e5a8eb667821fc00ccf98f8ee7e5eaa04b6`.
The unrelated inspection sidecar remains unmodified at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

No Loop 25 fixture, filter design, preprocessing run, development or
qualification open, cache/data/target/model read, training run, network call,
RW3 operation, stream/device/hardware operation, or generated experiment
payload occurred. This milestone adds a falsifiable decision boundary, not a
causal-preprocessing result or a scientific decoding claim.

Final local verification passes 331 unittests with three expected skips in
22.01 seconds wall and 573,079,552-byte maximum RSS; 328 pytest tests with three
skips and 134 subtests in 22.35 seconds wall and 582,434,816-byte maximum RSS;
and 299 dependency-light tests with 121 optional skips in 0.59 seconds wall and
42,205,184-byte maximum RSS. The 27 focused contract/request/roadmap tests pass
in 0.14 seconds wall with 22,216,704-byte maximum RSS.

Repository-wide Ruff, compileall, TOML/JSON parsing, root CLI help, unauthorized-
command absence, `git diff --check`, 61 local Markdown links, workbook reload/
formula inspection, and the 51-commit Gitleaks scan all pass. The public GitHub
repository description and 20 research/EEG/MEG/open-source topics remain current;
no repository-setting churn was needed.

## 2026-07-12 - Supersede Loop 25 v0 with a full anti-alias amendment

An adversarial preauthorization review found one material gap in the original
Loop 25 packet. V0 used the fourth-order 0.5-45 Hz task bandpass as its
anti-alias filter for 10x decimation, checked only 60 Hz at -6 dB, and left
almost the complete 50-500 Hz source folding band unbounded. No seed,
coefficient, or runtime had opened, so the packet could be corrected without
contaminating either protected partition.

The source trace follows the actual public dependency chain. Brain2Qwerty's
commit `3bf5a40` pins NeuralSet 0.2.2, MNE 1.11.0, and SciPy 1.14.1. NeuralSet
tag `v0.2.2` applies notch, bandpass, a separate MNE `Raw.resample`, and then
scaling. MNE's default resampler is a complete-signal FFT anti-alias path,
which confirms that anti-aliasing is a separate responsibility but is not
eligible for a zero-lookahead runtime. Exact upstream commit, blob, and
SHA-256 identities are recorded in `docs/LOOP_25_ANTI_ALIAS_AUDIT.md` and the
v1 machine contract.

Commit `b6b92d8` preserves the v0 contract, request, preregistration, research,
and tests byte-for-byte while adding
`causal_preprocessing_contract.v1.json`. V1 freezes a dedicated elliptic SOS
designed by `scipy.signal.iirdesign`: 45 Hz passband edge, at most 1 dB loss,
50 Hz stopband edge, and at least 60 dB designed attenuation. It registers
65,537 inclusive response points from 0-500 Hz, 23 exact alias source probes,
a -59.5 dB dense folding-band gate on both the dedicated stage and complete
chain, at most 17 total SOS sections, and a 1,360-byte filter-state array.
Ripple, transition-band behavior, step ringing, pole margin, and frequency-
dependent delay remain mandatory disclosures.

The access order is tightened: after a future separate authorization-only
commit is tested, pushed, and green, coefficients may be generated exactly
once and hash-bound. Pole, dense response, alias-map, impulse, and step checks
run before fixture metadata or arrays. Any static failure parks with both seeds
2501 and 2502 unopened. The original six signal families, seven schedules, ten
resume cuts, three future-mutation cuts, one-thread execution, 8 MiB total
artifact cap, 45-second internal cap, and one-time qualification rule remain.
The refusal surface grows from 40 to 45 and the access ledger from 21 to 23.

The amendment commit passed 342 unittests with three expected skips in 22.02
seconds wall with 569,737,216-byte maximum RSS. Eleven new dependency-free
amendment invariants pass, and
the focused amendment plus immutable-v0 request boundary passed 29 tests in
0.12 seconds with 22,560,768-byte maximum RSS. Both GitHub CI jobs passed on
push run `29195938038` before the replacement request was prepared.

The second milestone adds `docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`,
`registries/loop25_authorization_request.v1.json`, and 11 request invariants.
The request binds the green amendment commit, v1 contract/amendment/audit/test
hashes, superseded v0 hashes, exact scope, resources, seeds, order, and claim
boundary. All 16 request-level `authorized_now` fields remain false. The v0
authorization sentence is explicitly non-actionable; the next decision is to
authorize only v1 exactly, amend again, or hold.

Public docs, AGENTS, Start Here, the handoff, both continuation prompts, the
human and machine roadmaps, and the tracker now name `Amended
Preregistration`. The tracker was edited with the bundled artifact-tool
runtime after a nine-sheet pre-edit render. It adds decision `25-AA`, risk
`R30`, updates the Loop 25 prompt and row, and preserves all other sheets. The
78,492-byte workbook has SHA-256
`483fde426c8212e7956814462b0aa11b0ca8426163b3dad95f6574eb7e10eb92`;
all nine sheets rendered, the exported workbook reloaded, table ranges end at
Decision Log row 39 and Risk Register row 31, and both in-memory and reloaded
formula scans have zero matches. The unrelated inspection sidecar remains
unmodified at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Final local verification passes 353 unittests with three expected skips in
20.28 seconds wall and 570,310,656-byte maximum RSS; 350 pytest tests with
three skips and 163 subtests in 21.03 seconds wall and 583,467,008-byte maximum
RSS; and 321 true dependency-light Python 3.12 tests with 121 expected optional
skips in 1.39 seconds wall and 45,465,600-byte maximum RSS. The 49 focused v0,
v1, request, and roadmap tests pass in 0.09 seconds wall with 23,216,128-byte
maximum RSS.

Repository-wide Ruff, compileall, tracked JSON and TOML parsing, seven CLI help
surfaces, unauthorized Loop 25 command absence, `git diff --check`, 62 local
Markdown links, workbook reload/formula inspection, and the 53-commit Gitleaks
scan pass. No filter design, coefficient, fixture, seed open, numerical
preprocessing, real/cache/consumed/target/model/training/network/RW3/stream/
device/hardware operation, or generated experiment payload occurred.

This milestone adds a stronger, cheaper-to-fail causal preprocessing protocol.
It does not add a filter result or establish official Brain2Qwerty equivalence,
acceptable phase/ringing for neural decoding, neural information, CER/WER
improvement, end-to-end latency, transfer, portable hardware, assistive
efficacy, diagnosis, or clinical utility.

## 2026-07-12 - Close Loop 26 planning research at the identifiability boundary

Commit `03605c5` completes a primary-source and committed-local-evidence audit
for the future real validation-only encoder gate. It does not preregister or
run the experiment. The machine boundary records the strict 55/6/5 source
protocol, one person/session, six reserved validation sentence instances, 64
exact paired sign assignments, minimum two-sided resolution 0.03125 with six
nonzero differences, and one biological replicate. All 14 authorization fields
are false and 12 protected-operation counters are zero.

The audit found that the existing 2,908-parameter `TinySentenceCTC` is
noncausal because its kernel-3 temporal layer uses symmetric padding. The
smallest future recommendation preserves all parameters and uses exactly two
left-context samples with zero right context and 128 bytes of float32 temporal
state. A 2,884-parameter one-layer linear signal CTC is the nearly matched
comparator. Six future controls separate a train-only no-signal prior, zero
signal, target derangement, channel derangement, nonwrapping zero-filled time
displacement, and the linear path. None is frozen, implemented, trained, or
evaluated by this pass.

The official Brain2Qwerty v2 source trace is kept as a scientific reference,
not copied as a local architecture. Its current whole-sentence path is
noncausal and GPU-scale. Loop 26 therefore remains a small, language-model-free
same-source question whose eventual result could apply only to six named
validation sentences. Source test and session 2 remain consumed and closed;
unseen-person, population, transfer, modality, device, real-time, assistive,
and clinical claims remain unavailable.

Public closeout updates AGENTS, README, Start Here, the handoff, both
continuation prompts, human roadmaps, decision log, and the tracker. A new
invariant requires seven public status surfaces to say both planning research
and `Not Started`, preventing documentation drift from silently authorizing an
experiment. The nine-sheet workbook adds decision `26-R1`, risk `R31`, prompt
`Loop26-Research`, and the refreshed Loop 26 row while retaining Loop 25 as the
active numbered decision. It is 79,856 bytes with SHA-256
`255b51b8d083db92030c389f8d40cf001b256dbe0345748c9120e35b993bdb15`;
all nine sheets render and reload, and the formula-error scan matches zero
cells. The unrelated inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Final local verification passes 41 focused Loop 25/26/roadmap tests in at most
0.14 seconds wall with 22,986,752-byte maximum RSS; 366 optional unittests with
three expected skips in 21.53 seconds wall and 575,389,696-byte maximum RSS;
363 pytest tests with three skips and 170 subtests in 21.44 seconds wall and
584,957,952-byte maximum RSS; and 334 true dependency-light Python 3.12 tests
with 121 optional skips in 0.75 seconds wall and 45,170,688-byte maximum RSS.
The three full counts are each 13 above the Loop 25 v1 baseline; the public
closeout adds one invariant above the 365-unittest `03605c5` milestone.

Repository-wide Ruff, compileall, 15 tracked JSON and two TOML parses, seven
CLI help surfaces, unauthorized Loop 25/26 command absence, `git diff --check`,
64 local Markdown links, workbook render/reload/formula inspection, and the
55-commit Gitleaks history scan pass. GitHub CI run `29197895836` is green for
the research milestone. No raw signal, real-cache content, target, source
validation prediction, consumed source-test/session-2 evidence, checkpoint,
model, training, numerical preprocessing, network, RW3, stream, board, device,
hardware, or generated experiment payload was opened or created.

This milestone adds a falsifiable, resource-bounded design for the next neural
question. It does not establish a causal model, neural information, decoding
advantage, validation performance, generalization, real-time text, or portable
hardware behavior.

## 2026-07-12 - Select an exact Loop 27 MEG holdout candidate without opening it

Commit `b3d61b6` completes a metadata-only primary-source search for the first
fresh same-modality transfer candidate. The one-thread selector used the pinned
SpanishBCBL revision and Hugging Face metadata APIs, examined 315 MEG entries,
found 23 clean single-FIF/log pairs and 16 eligible pairs, and ranked exact
bundle bytes after canonical identity and cohort exclusions. It took 3.10
seconds wall with 63,766,528-byte peak RSS and downloaded zero file payload
bytes.

The selected candidate is S25 session 2 block 2. Its raw FIF is
1,009,713,753 bytes and protected MAT log is 226,230 bytes, for an exact
1,009,939,983-byte bundle and 63,801,841-byte margin under a future 1 GiB cap.
The machine registry freezes each official Git blob, LFS SHA-256, Xet hash, and
last-file commit. The MAT path already exists locally at the expected size from
earlier metadata work, but this pass did not hash or open its payload. The raw
FIF is absent.

The selection is scientific, not merely small. S21 block 2 is observed source
evidence. S23 is smaller than S25 but the official dataset card excludes that
participant because of a metallic implant. S20 is prompted-typing EEG and stays
in the separate RW4 cohort. S25 has no published alias with the observed
S5/S10/S21 person and uses the same nominal 306-channel, 1 kHz Megin/Elekta
Neuromag task contract. Exact channels, geometry, performed trials, sentence
overlap, and external target-viewing history remain unavailable.

The future recommendation is final-only: zero S25 training, validation, or
calibration rows; every eligible performed row opens once after the source
model, controls, reports, target isolation, and Loop 28 decision rule are hash
frozen. At least 48 performed unique rows are required as a pragmatic 75%
retention floor from the nominal 64-row half-session, not a prospective power
claim. An unseen-person claim must disclose sentence overlap; unseen text
requires a future zero-overlap audit. Any S25 failure parks without automatic
backup substitution.

The research registry contains 18 false authorization fields. It explicitly
blocks preregistration, acquisition requests, download selections, local MAT
payload hashes, FIF headers/signals, MAT targets, models, training, final opens,
backup candidates, RW4, and Loop 28. Public docs and one new invariant preserve
the distinction between selecting S25 metadata and authorizing any content
operation.

The nine-sheet tracker adds decision `27-R1`, risk `R32`, prompt
`Loop27-Research`, and the refreshed Loop 27 row while Loop 25 remains the
active numbered decision. The 80,867-byte workbook has SHA-256
`186eda194695b92b1c18422e1a0ccbcbd9ed63249eb7ba1f6c8d500926f9c685`;
all nine sheets render, the exported workbook reloads with byte-identical key-
range inspection, and formula scans match zero cells. The unrelated inspection
sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Final local verification passes 55 focused Loop 25-27/roadmap tests in at most
0.10 seconds wall with 23,592,960-byte maximum RSS; 380 optional unittests with three
expected skips in 21.31 seconds wall and 577,060,864-byte maximum RSS; 377
pytest tests with three skips and 177 subtests in 21.21 seconds wall and
586,498,048-byte maximum RSS; and 348 true dependency-light Python 3.12 tests
with 121 optional skips in 0.73 seconds wall and 46,383,104-byte maximum RSS.
The three full counts are each 14 above the Loop 26 public closeout.

Repository-wide Ruff, compileall, 16 tracked/worktree JSON and two TOML parses,
seven CLI help surfaces, unauthorized Loop 25/26/27 command absence,
`git diff --check`, 66 local Markdown links, workbook render/reload/formula
inspection, and the full-history Gitleaks scan pass. GitHub CI run
`29199178320` is green for the research milestone. No candidate payload,
download, local MAT hash, header, signal, target, source consumed evidence,
model, training, final holdout, backup, RW3, stream, board, device, hardware, or
generated experiment payload was opened or created.

This milestone adds an exact, storage-bounded candidate for a future
unseen-person MEG transfer test. It does not establish an acquired or compatible
holdout, target freshness, transfer, neural advantage, unseen text, population
generalization, real-time behavior, or portable hardware.

## 2026-07-12 - Define the Loop 28 strict unseen-person transfer boundary

Loop 28 planning research converts the missing unseen-person claim into one
falsifiable future S25 test without opening the candidate. The primary-source
audit separates four noninterchangeable levels: T0 same-session heldout text,
T1 same-person cross-session, T2 unseen-person strict zero-shot, and T3 unseen-
person supervised calibrated transfer. It also records that Brain2Qwerty v2 is
continuous at inference but whole-sentence and noncausal, and that its joint and
leave-one-out transfer regimes use target-participant data rather than proving
strict zero-shot transfer.

The selected future S25 question is T2 only. It permits zero candidate training,
validation, calibration, target-wide fitting, subject embedding, adapter, or
unlabeled target-corpus adaptation rows. A future pass requires at least 48
eligible unique final rows, at least 0.05 absolute macro sentence-CER advantage
over the frozen source-train-only no-signal prior, a one-sided deterministic
paired label-swap result at `p <= 0.05` from 65,535 random assignments plus the
observed assignment, and strict wins over exact-zero signal, channel-name-hash
derangement, and nonwrapping zero-filled time-displacement controls. Ties,
missing fields, cap violations, fewer than 48 rows, and any failed gate park the
result without restart, threshold changes, calibration, or backup substitution.

The machine registry has 21 false `authorized_now` fields. It records zero S25
path checks, local MAT hashes, FIF header or signal reads, MAT content or target
reads, consumed source-evidence reads, model or checkpoint runs, training,
calibration, final evaluation, and RW3 or hardware operations. Public research
used ten high-level browser operations and one GitHub metadata API call, with
zero code or data payload bytes. External interactive runtime and RSS are
unavailable from the research tool contract and are reported as unavailable,
not estimated. The future generated-artifact cap remains 32 MiB, one worker,
one CPU thread, and no larger model or language model.

The nine-sheet tracker adds decision `28-R1`, risk `R33`, prompt
`Loop28-Research`, and the refreshed Loop 28 row while Loop 25 remains the
active numbered execution decision. The 82,284-byte workbook has SHA-256
`312a98d5d63d52ceb413383b7cd8a2424b0c1cb864665a485d3320f74d42ee7e`;
all nine sheets render, the exported workbook reloads with byte-identical key-
range inspection, and two formula scans match zero cells. The unrelated
inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Final local verification passes 69 focused Loop 25-28/roadmap tests in 0.08
seconds wall with 27,639,808-byte maximum RSS; 394 optional unittests with three
expected skips in 22.70 seconds wall and 566,378,496-byte maximum RSS; 391
pytest tests with three skips and 184 subtests in 23.75 seconds wall and
587,792,384-byte maximum RSS; and 362 true dependency-light Python 3.12 tests
with 121 optional skips in 0.79 seconds wall and 46,891,008-byte maximum RSS.
The three full counts are each 14 above the Loop 27 public closeout.

Repository-wide Ruff, compileall, 17 tracked/worktree JSON and two TOML parses,
seven CLI help surfaces, unauthorized Loop 25/26/27/28 command absence,
`git diff --check`, 68 local Markdown links, and staged Gitleaks pass. Research
commit `a55b7e6` passes both GitHub jobs in push run `29201270789` and draft PR
#7 run `29201323258`. No candidate payload, local MAT hash, header, signal,
target, source consumed evidence, model, training, calibration, final holdout,
backup, RW3, stream, board, device, hardware, or generated experiment payload
was opened or created.

This milestone adds a machine-checkable one-time strict zero-shot transfer
decision design. It does not establish S25 compatibility, unseen-person neural
advantage, decoding accuracy, unseen-text or population generalization,
causality, real-time decoding, or portable-hardware behavior.

## 2026-07-12 - Define the Loop 29 portable-sensing translation boundary

Loop 29 planning research now turns "portable" into two noninterchangeable
evidence lanes without selecting hardware. Scalp EEG is the immediate local-
first accessibility lane because practical acquisition, open formats, and
repeated self-administered home recordings exist. OPM-MEG is the same-modality
partner/lab lane because it preserves magnetic sensing but still depends on
specialist shielding, active field control, geometry, motion tracking, and
interference suppression. Cryogenic MEG remains the scientific reference;
peripheral wearables remain controls or separate accessibility inputs.

The primary-source research explicitly rejects two shortcuts. Brain2Qwerty
v2's 76/153/230-channel random subsets remain cryogenic MEGIN measurements and
do not qualify OPM-MEG or EEG. Evidence that dry EEG can be recorded repeatedly
at home supports acquisition mechanics, not at-home thought typing or text
decoding. The machine boundary freezes 15 cross-modality requirements, four
modality profiles, six qualification levels, 12 future device-packet gates, 18
source bindings, and 24 false `authorized_now` fields. The Loop 29 experiment
remains `Not Started`; no device is selected or recommended.

The user's additional 5-10 GB allowance is bound as 5,000,000,000 preferred
and 10,000,000,000 absolute incremental bytes, not as download permission. The
separately gated S20 EEG bundle is 96,090,264 bytes and S25 MEG pair is
1,009,939,983 bytes, totaling exactly 1,106,030,247 bytes and leaving
3,893,969,753 bytes below the preferred ceiling. Loop 29 downloaded zero
payload bytes and opened no real path, payload hash, header, signal, target,
consumed evidence, checkpoint, model, training, calibration, SDK, socket,
stream, device, partner, or hardware operation.

The nine-sheet tracker updates the dashboard and Loop 29 row, adds decision
`29-R1`, risk `R34`, and prompt `Loop29-Research`, and preserves Loop 25 as the
active numbered execution decision. The 83,821-byte workbook has SHA-256
`d80ce6940f65939c9ea8acca682cc416f988d56c0ceca42222e9e69eaa30ed6d`;
all nine sheets render, the exported workbook reloads with exact key ranges,
and two formula scans match zero cells. The unrelated inspection sidecar
remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Final local verification passes 107 focused Loop 25-29/roadmap tests in 0.19
seconds wall with 30,818,304-byte maximum RSS; 411 optional unittests with
three expected skips in 25.60 seconds wall and 554,991,616-byte maximum RSS;
408 pytest tests with three skips and 191 subtests in 24.31 seconds wall and
583,204,864-byte maximum RSS; and 379 dependency-light Python 3.12 tests with
121 optional skips in 1.97 seconds wall and 47,153,152-byte maximum RSS. Each
full count is 17 above the Loop 28 closeout.

Repository-wide Ruff, compileall, 18 tracked/worktree JSON and two TOML parses,
seven CLI help surfaces, 55 registered commands, unauthorized Loop 25-29
command absence, `git diff --check`, 70 local Markdown links, and workbook
render/reload/formula inspection pass. Research commit `f5fc740` passes both
jobs in push run `29204700023` and draft PR #8 run `29204804483`. Public
research used 14 high-level web operations and downloaded zero code/data
payload bytes; external interactive runtime and peak RSS remain unavailable
from the tool contract.

This milestone adds a machine-checkable path from cryogenic MEG toward local
EEG and partner OPM-MEG with a bounded data allocation. It does not establish
portable-device signal quality, OPM sentence production, useful EEG text
decoding, neural advantage, unseen-person generalization, at-home text input,
end-to-end real-time behavior, assistive efficacy, diagnosis, or clinical
utility.

## 2026-07-12 - Define the Loop 30 target-free local replay boundary

Loop 30 planning research now turns "local streaming" into an inspectable
interaction contract without creating a streaming runtime. The future product
is a loopback-only target-free replay inspector. Four source modes keep
artifact replay, synthetic replay, recorded replay, and live sources distinct.
The future trace has 30 required identity, timing, revision, finalization,
causality, hash, warning, and unavailable-field entries; target text, labels,
prompts, real sentence text, consumed predictions, quality metrics, logits,
checkpoints, real signal, and consumed caches are forbidden producer inputs.

The primary-source review preserves three lessons. Brain2Qwerty v2 is
continuous/asynchronous but still whole-sentence and noncausal, with a fully
real-time low-latency version left to future work. Loop 21 establishes a causal
producer but no decoder or capture-to-user latency. Loop 23's consumed test
recorded zero revisions yet reached only 5/8 exact against its 6/8 threshold,
so stability is not correctness or confidence. Finalization must therefore be
explicit and predictive confidence remains unavailable until a separately
authorized Loop 34 calibration result exists.

The machine registry freezes nine clock domains and six latency claim levels.
Source, backend monotonic, browser performance, and user-observed origins may
not be subtracted without a measured mapping. A future Loop 30 implementation
can qualify at most local replay presentation Level 3; device capture through
user-visible render is Level 5 and outside scope. Cold start, scheduling,
queueing, producer, decoder, serialization, browser receive, render, first
partial, first committed token, and finalization remain separate, with missing
stages reported as unavailable rather than zero.

Privacy and accessibility are fail-closed. The future launcher fixes
`127.0.0.1`, disables host override, share, analytics, monitoring, uploads,
allowed/static directories, service workers, popups, and external network
dependencies, and caps execution at one thread, one worker, and two sessions.
Browser QA records requests, responses, WebSockets, pages, console errors,
screenshots, blankness/overlap, W3C 50-ms long tasks, and Event Timing support.
Incremental changes require textual source/proof labels, status/log semantics,
polite announcements, keyboard access, stable focus, no forced autoscroll, and
reduced motion. Eighteen future pass requirements and 30 exact refusals bind
these behaviors before any code or fixture exists.

All 30 `authorized_now` fields are false. This research used ten high-level
public-web operations, one CPU thread and worker, and zero remote payload
bytes, real path/hash/header/signal/cache/target/consumed-artifact reads,
checkpoint/model/training/calibration runs, trace generations, server launches,
browser runs, SDK imports, sockets, streams, devices, or hardware sessions.
External research peak RSS and one end-to-end runtime are unavailable by tool
contract. The planning cap is 8 MiB; future separately authorized execution is
bounded to 32 MiB generated artifacts and 1 GiB peak RSS.

The nine-sheet tracker keeps Loop 25 as the active execution decision, updates
the Loop 30 row and dashboard, and adds decision `30-R1`, risk `R35`, and prompt
`Loop30-Research`. The 85,167-byte workbook has SHA-256
`c92c4fe378532c2d22b0be24b60c5f6c85192a14eac239dd954508f6f1e01d69`;
all nine sheets render, the export reloads with exact key ranges, and both
formula-error scans match zero cells. The unrelated 321,169-byte inspection
sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 122 focused Loop 25-30/roadmap tests in 0.11 seconds
wall with 29,097,984-byte maximum RSS; the strict Loop 30 plus roadmap slice
passes 24 tests in 0.15 seconds wall with 20,037,632-byte maximum RSS; 426
optional unittests pass with three expected skips in 22.27 seconds wall and
574,521,344-byte maximum RSS; 423 pytest tests pass with three skips and 198
subtests in 22.06 seconds wall and 591,413,248-byte maximum RSS; and 394
dependency-light tests pass with 121 optional skips in 0.75 seconds wall and
48,594,944-byte maximum RSS. Ruff, compileall, 23 source JSON and two TOML
parses, seven CLI help surfaces, 55 registered commands, unauthorized Loop
25-30 command absence, 72 local Markdown links, workbook render/reload/formula
inspection, and `git diff --check` pass.

Research commit `958ac4e` is published on
`codex/loop-30-local-streaming-research`. Both required jobs pass in push CI
run `29206964418` and draft PR #9 CI run `29206972221`.

This milestone adds a machine-checkable interaction, timing, privacy,
accessibility, and browser-QA design for a future local target-free replay. It
does not add a running UI or establish live neural input, causal end-to-end
text, confidence, neural advantage, decoding accuracy, unseen-person
generalization, capture-to-user latency, portable hardware, arbitrary-thought
typing, assistive efficacy, diagnosis, or clinical utility.

## 2026-07-12 - Define the Loop 31 neural-attribution firewall

Loop 31 planning research now separates predictive performance from scientific
attribution without opening protected evidence. The local evidence remains
negative: consumed S21 session-2 MEG reaches corpus CER `0.917949` versus
`0.775458` for its no-signal prior, and consumed S7 EEG reaches key-label
accuracy `0.009091` versus `0.122727` for its prior. Neither path was reopened.

The future encoder matrix has ten named conditions: full signal, train-only
no-signal prior, same-checkpoint zero signal, whole-item derangement, channel
derangement, time displacement, timing-only, conditional context-only,
train-pairing derangement, and a 2,884-parameter linear signal diagnostic. A
separately gated five-condition language-model matrix distinguishes
encoder-only output, full CTC-text-plus-Neuro-Token LLM output, Neuro Token
drop, item-deranged Neuro Tokens, and an LLM-only prior. No local LLM, v2
embedding, checkpoint, weight, or data is assumed.

Five estimands keep encoder signal dependence, language-prior gain, conditional
Neuro Token gain, total-system gain, and brain-specific increment separate.
The six-row source validation recommendation uses exact one-sided paired
sign-flip components under one intersection-union decision. Six nonzero pairs
provide 64 assignments and minimum one-sided p `0.015625`; five provide 32 and
`0.03125`; four provide 16 and `0.0625`. Two zero paired effects therefore make
a component unable to pass alpha `0.05`. The primary `0.05` macro-CER margin
remains a recommendation until preregistration.

Every future condition must use identical validation membership, target
normalization, and metric code. Item, channel, time, and train-pairing
transforms plus every configuration and prediction hash freeze before one
validation-target open. Timing-only inputs are restricted to candidate-visible
lengths, masks, sampling rate, and relative sample timestamps. Any exposed
prompt or sentence list makes the context-only control mandatory.

The claim ceiling is explicit. A clean future local encoder gate can support at
most sensor-signal dependence for the exact person, session, task, split,
candidate, and conditions. Brain-specific neural origin remains unavailable
until Loop 35 excludes EOG, EMG, motion, environmental, timing, prompt, and
action shortcuts. Language gain is not neural gain, and a Neuro Token drop is
conditional on identical CTC text and LLM rather than total neural
contribution.

The machine registry freezes six claim classes, 18 future requirements, 24
refusals, 14 source bindings, and 19 false authorization fields. This planning
pass used 16 high-level public network operations including eight GitHub API
requests, one CPU thread/worker, and zero protected cache/target/checkpoint/
model/training/validation/LLM/S20/S25/stream/device operations or downloaded
data/model bytes. Exact external research network bytes and interactive peak
RSS are unavailable from the tool contracts rather than estimated.

The nine-sheet tracker updates its scope note and Loop 31 row, adds decision
`31-R1`, risk `R36`, and prompt `Loop31-Research`, and preserves Loop 25 as the
active execution decision. The 86,166-byte workbook has SHA-256
`7e1da6c9e49ca5835adcb3b6216fe236e1521f38877c8ed3f508bd3b995ed60e`;
all nine sheets render, the export reloads with exact key ranges, and both
formula-error scans match zero cells. The unrelated 321,169-byte inspection
sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 125 focused Loop 24-31/roadmap tests in 0.12 seconds
wall with 29,179,904-byte maximum RSS; the strict Loop 31 plus roadmap slice
passes 26 tests in 0.07 seconds wall with 20,447,232-byte maximum RSS; 443
optional unittests pass with three expected skips in 23.12 seconds wall and
574,603,264-byte maximum RSS; 440 pytest tests pass with three skips and 205
subtests in 22.80 seconds wall and 591,003,648-byte maximum RSS; and 411
dependency-light tests pass with 121 optional skips in 1.61 seconds wall and
51,675,136-byte maximum RSS. Each full count is 17 above the Loop 30 closeout.

Ruff, touched-file format checks, compileall, 24 source JSON and two TOML
parses, seven CLI help surfaces, 55 registered commands, unauthorized Loop 31
runtime absence, 70 checked local Markdown links with zero missing, workbook
render/reload/formula inspection, and `git diff --check` pass. Remote CI is
green: research commit `5455340` passes both jobs in push run `29208510571`
and draft PR #10 run `29208529886`.

This milestone adds a machine-checkable attribution design that keeps signal,
language, context, timing, and conditional Neuro Token effects separate. It
does not establish sensor-signal dependence, brain-specific neural
contribution, decoding accuracy, unseen-person generalization, real-time or
portable-hardware behavior, assistive efficacy, diagnosis, or clinical utility.

## 2026-07-12 - Define the Loop 32 fresh-person calibration boundary

Loop 32 planning research now makes calibration information and human burden
explicit without opening a participant. The future recommendation is one
pointwise causal hidden affine adapter over the proposed 16-wide Loop 26 source
encoder: 16 scales plus 16 biases, exactly 32 target-trainable values, with all
2,908 base values frozen. Strict zero-shot, unlabeled transductive, label-light,
and supervised calibration remain four different modes and claims.

The nested recommendation is `0, 2, 4, 8, 16, 32` unique completed calibration
sentences. Label-light is capped at eight labeled calibration sentences and
supervised calibration at 32, while every labeled selection row remains part of
the reported supervision burden. Unlabeled mode cannot use target labels to
select its budget, stopping rule, or threshold. Synthetic Loop 16 seconds are
not translated into a human calibration-time claim.

A future candidate requires physically distinct, row-disjoint, and semantic-
text-disjoint recordings with at least 32 calibration, 16 selection, and 48
final unique completed sentences. S25 session 2 block 2 remains final-only for
Loop 28 and is ineligible. Strict zero-shot final predictions must hash-freeze
before any target-person calibration access; one mode, adapter, and budget must
then freeze before all adapted/control predictions and one final-target open.

The future final matrix has six conditions: frozen zero-shot, identity adapter,
selected adapter, source-train-only no-signal prior, robust normalization-only,
and label derangement for labeled modes. The current statistical recommendation
requires at least `0.05` macro-CER gain versus both zero-shot and prior, 65,535
random sign assignments plus observed, and strict wins over every applicable
control. The practical margins remain unfrozen until preregistration. Any tie,
final harm, split/hash/access/resource failure, or selection-to-final reversal
parks the claim without restart.

The machine registry freezes four modes, six budgets, six conditions, seven
claim classes, 20 future requirements, 26 refusals, nine source bindings, and
22 false authorization fields. This planning pass used six public network
operations including two pinned GitHub source reads, one CPU thread/worker, and
zero candidate selection, protected payload, signal, target, checkpoint, model,
adapter-fit, training, control-prediction, final-evaluation, stream, device, or
hardware operation. Public transport bytes, end-to-end interactive research
runtime, peak RSS, and candidate-specific calibration minutes remain
unavailable rather than estimated.

The nine-sheet tracker updates its dashboard and Loop 32 row, adds decision
`32-R1`, risk `R37`, and prompt `Loop32-Research`, and preserves Loop 25 as the
active execution decision. The 87,364-byte workbook has SHA-256
`32d51d0690940d7231df6b0c8db366ce0647332893e12bcf29cff1c3b573847f`;
all nine sheets render, the exported workbook reloads with exact key ranges,
and both formula-error scans match zero cells. The unrelated 321,169-byte
inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 171 focused Loop 24-32/roadmap tests in 0.19 seconds
wall with 32,391,168-byte maximum RSS; the strict Loop 32 plus roadmap slice
passes 25 tests in 0.16 seconds wall with 22,167,552-byte maximum RSS; 459
optional unittests pass with three expected skips in 22.80 seconds wall and
573,243,392-byte maximum RSS; 456 pytest tests pass with three skips and 212
subtests in 24.04 seconds wall and 586,711,040-byte maximum RSS; and 427
dependency-light tests pass with 121 optional skips in 0.74 seconds wall and
51,855,360-byte maximum RSS. Each full count is 16 above the Loop 31 closeout.

Repository-wide Ruff, touched-file formatting, compileall, 21 source JSON and
two TOML parses, seven CLI help surfaces, 55 registered commands, unauthorized
Loop 32 runtime absence, 74 local Markdown links, workbook render/reload/formula
inspection, and `git diff --check` pass. Research commit `8109b10` passes both
jobs in push CI run `29209987034` and draft PR #11 run `29209996914`.

This milestone adds a machine-checkable fresh-person calibration design with
an inspectable low-parameter adapter, physical split firewall, human-burden
ledger, and one-time final decision rule. It does not establish zero-shot or
calibrated-person improvement, sensor-signal dependence, neural advantage,
population generalization, real-time behavior, portable hardware, at-home
decoding, assistive efficacy, diagnosis, or clinical utility.

## 2026-07-12 - Define the Loop 33 bounded data-scaling boundary

Loop 33 planning research now protects the remaining prospective local
validation evidence before any scaling run exists. The future recommendation
uses strictly nested `8, 16, 24, 32, 44, 55` unique source-train sentence
instances, at most three fresh optimization seeds and 18 candidate fits, one
fixed 2,908-parameter Loop 26 architecture, and a train-size-matched no-signal
prior at every point. The experiment remains `Not Started`.

Access order is the central decision. Loop 26 and Loop 33 should freeze
together before the first source-validation target opens. Every architecture,
prefix, seed, control, model, config, prediction, ledger, and payload hash must
exist before all six shared targets open once and every Loop 26/31/33 condition
scores in one pass. If Loop 26 scores first, a later Loop 33 curve is
exploratory unless a new physical validation partition is separately approved.

The primary-source review keeps public scale results in their own evidence
cohorts. Brain2Qwerty v2's five-condition approximately 90-hour curve and
matched unique-versus-repeated sentence comparison, a 498-hour multi-dataset
image-decoding study, and a 175-hour overt-speech EEG study motivate the axes.
Their people, tasks, modalities, supervision, language coverage, models, and
compute do not supply a local exponent. Loop 33 refuses a formal power-law fit,
population inference, and extrapolation beyond 55 sentences.

Current committed metadata supports a unique-sentence prefix curve only.
Duplicating, resampling, reweighting, augmenting, or reslicing an array is not
a new physical neural recording. A future repetition-efficiency comparison
would require distinct performed recordings of the same normalized prompt,
matched physical trial counts, and its own metadata review, preregistration,
and exact authorization. No additional acquisition is recommended now.

The machine registry freezes four future conditions, seven outcomes, seven
claims, 20 requirements, 30 refusal IDs, and 23 false authorization fields. The
future resource envelope remains one thread/worker, 18 candidate fits, 1,200
total training seconds, 1 GiB RSS, 32 MiB outputs, and zero new downloads. CPU
time is not energy. This research used six public web operations and zero
protected cache/signal/target, model, training, scoring, S20/S25, stream,
device, or hardware operations. Complete public transport bytes, interactive
research runtime/RSS, and direct energy remain unavailable rather than
estimated.

The nine-sheet tracker updates its dashboard and Loop 33 row, adds decision
`33-R1`, risk `R38`, and prompt `Loop33-Research`, and preserves Loop 25 as the
active execution decision. The 88,615-byte workbook has SHA-256
`3ca4cff5ae1f744dd90d229934d8c831656411daaaa332a495ac2645bcb9ec08`;
all nine sheets render, the exported workbook reloads with exact key ranges,
and the formula-error scan matches zero cells. The unrelated 321,169-byte
inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 175 focused Loop 24-33/roadmap tests in 3.89 seconds
wall with 237,322,240-byte maximum RSS; the strict Loop 33 plus roadmap slice
passes 25 tests in 0.07 seconds wall with 20,463,616-byte maximum RSS; 475
optional unittests pass with three expected skips in 22.11 seconds wall and
575,733,760-byte maximum RSS; 472 pytest tests pass with three skips and 219
subtests in 22.71 seconds wall and 586,842,112-byte maximum RSS; and 443
dependency-light tests pass with 121 optional skips in 1.02 seconds wall and
52,871,168-byte maximum RSS. Each full count is 16 above the Loop 32 closeout.
A first dependency-light shell invocation omitted `PYTHONPATH=src` and failed
at import before exercising the suite; the corrected acceptance command above
is the measured passing gate.

Repository-wide Ruff, touched-file formatting, compileall, 21 source JSON and
two TOML parses, seven CLI help surfaces, 55 registered commands, unauthorized
Loop 33 runtime absence, 72 checked local Markdown links with zero missing,
workbook render/reload/formula inspection, and `git diff --check` pass. Research
commit `25724de` passes both jobs in push CI run `29211291337` and draft PR #12
run `29211306722`.

Engineering capability added: a machine-checkable bounded scaling design now
preserves one target-blind shared validation event, separates unique sentences
from physical repetitions, and gates any later acquisition packet.

Scientific claim not established: no protected payload, model, training run,
or target was accessed, so there is no learning curve, neural advantage,
scaling law, repetition-efficiency result, saturation finding, acquisition
value, unseen-person generalization, real-time behavior, or portable-hardware
result.

## 2026-07-12 - Loop 34 confidence research boundary

Closed Loop 34 planning research while leaving the confidence, abstention, and
revision experiment `Not Started`, confidence unavailable, and all 26
`authorized_now` fields false. The new machine contract separates seven
confidence semantics and eight score/control roles, recommends fresh target-
free synthetic calibration/selection/final counts of `128/64/256`, freezes 20
future gates and 30 refusal IDs, and permits no fixture, confidence feature,
probability mapping, threshold, target open, score, product confidence,
protected-data access, or download.

The critical scientific decision is that the six source-validation sentences
cannot fit a confidence mapping, select a score and policy, and independently
qualify that policy. Those rows remain reserved for the shared Loop 26/31/33
event. Even zero errors in six independent Bernoulli trials has an optimistic
one-sided 95% exact upper error bound of `0.39303776899708276`; the actual one-
person sequence rows are more dependent. Existing real confidence therefore
remains unavailable and would require fresh physically separate calibration,
selection, and final evidence.

The primary-source boundary distinguishes target-blind ranking from calibrated
correctness probability, fixed abstention policy, conformal bounded-risk
control, revision stability, and product-visible confidence. Exact-sequence
0/1 error is the primary bounded loss. Raw CER stays unclipped; optional
bounded CER must be separately named. A future report must show registered
working points, accepted and generalized error, abstention, legacy AURC with
limitations, and an AUGRC-equivalent area. ECE is secondary and unavailable
for raw scores. Revision delay preserves the Loop 30 clock-domain contract.

The nine-sheet tracker updates its dashboard and Loop 34 row, adds decision
`34-R1`, risk `R39`, and prompt `Loop34-Research`, and preserves Loop 25 as the
active execution decision. The 90,112-byte workbook has SHA-256
`88b4251b06b4ac1e5514b0cdd1dcaffcf0aaa80c57f7c4a37811cd841e31066d`;
all nine sheets rendered before and after the edit, the export reloads with
exact key ranges, and the formula-error scan matches zero cells. The unrelated
321,169-byte inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 224 focused Loop 24-34 tests in 5.34 seconds wall
with 314,818,560-byte maximum RSS; the strict Loop 34 plus roadmap slice passes
26 tests in 0.07 seconds wall with 20,496,384-byte maximum RSS; 492 optional
unittests pass with three expected skips in 22.64 seconds wall and
575,291,392-byte maximum RSS; 489 pytest tests pass with three skips and 226
subtests in 22.83 seconds wall and 588,234,752-byte maximum RSS; and 460
dependency-light tests pass with 121 optional skips in 0.71 seconds wall and
53,985,280-byte maximum RSS. Each full count is 17 above the Loop 33 closeout.

Repository-wide Ruff, touched-file formatting, compileall, 22 source JSON and
two TOML parses, seven CLI help surfaces, 55 registered commands, unauthorized
Loop 34 runtime absence, 74 checked local Markdown links with zero missing,
workbook render/reload/formula inspection, and `git diff --check` pass. Research
commit `ad9d647` passes push CI run `29213220777` and draft PR #13 CI
run `29213242970`.

Engineering capability added: a machine-checkable confidence semantics ladder,
three-way evidence firewall, selective-risk and revision-latency protocol,
target-leakage refusals, and explicit unavailable state now exist.

Scientific claim not established: no protected data, model, confidence fit,
target, score, or product surface was accessed, so there is no calibrated
confidence, abstention benefit, selective-risk guarantee, neural advantage,
decoding accuracy, unseen-person generalization, real-time behavior, or
portable-hardware result.

## 2026-07-12 - Loop 35 peripheral-confound research boundary

Closed Loop 35 planning research while leaving the peripheral-confound
experiment `Not Started`, all 31 `authorized_now` fields false, and every
fixture, synchronized peripheral acquisition, protected-data read, model,
training, residualization fit, scoring, no-keypress study, stream, device, and
hardware operation closed. The machine contract freezes ten confound classes,
nine future synchronized stream classes, 13 comparison conditions, three
independently authorized stages, 24 future gates, and 32 refusal IDs.

The primary-source task audit separates known-keypress v1 decoding from
continuous-input v2 inference while preserving the fact that both public
protocols use overt prompted typing. Eye movements, EMG, head/jaw/neck motion,
audio/environment, physiology/equipment, and task identity remain credible
predictive shortcuts. Calling a channel EEG/MEG or artifact-rejecting it does
not establish physical origin.

Current S21 has 102 magnetometers and timing but no synchronized EOG, EMG,
gaze, motion, or audio stream in the committed cache path. Consumed S7 source
metadata names three ocular channels, but its 61-channel cache contains none.
Current evidence therefore cannot close a peripheral firewall. A future local
pass can establish at most incremental brain-sensor information beyond every
recorded control for the exact people, task, device, streams, and split, not
absolute brain origin.

The future recommendation uses physically and semantically disjoint 32/16/48
calibration/selection/final floors. Select the strongest peripheral condition
and one brain candidate on selection only, freeze all predictions/configs/
access ledgers and hashes, then open final targets once. Recommend 0.05
practical margins for both the all-stream-over-peripheral and brain-sensor-over-
nonbrain estimands, 65,535 paired sign assignments plus observed, an
intersection-union decision, and failure on ties. These values remain planning
recommendations until a separate preregistration.

The nine-sheet tracker updates Dashboard `B10` and Loop 35 row 15, adds decision
`35-R1`, risk `R40`, and prompt `Loop35-Research`, and preserves Loop 25 as the
active execution decision. The 91,463-byte workbook has SHA-256
`90b59a0646837b1a83281c144edff688b967fd44deda06e2a7c09a0dccb9f61a`;
all nine sheets rendered before and after the edit, the export reloads with
exact key ranges, and the formula-error scan matches zero cells. The unrelated
321,169-byte inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 231 focused Loop 24-35 tests in 4.43 seconds wall
with 239,075,328-byte maximum RSS; the strict Loop 35 plus roadmap slice passes
27 tests in 0.09 seconds wall with 20,299,776-byte maximum RSS; 510 optional
unittests pass with three expected skips in 23.06 seconds wall and
561,594,368-byte maximum RSS; 507 pytest tests pass with three skips and 233
subtests in 23.41 seconds wall and 587,186,176-byte maximum RSS; and 478
dependency-light tests pass with 121 optional skips in 0.96 seconds wall and
55,902,208-byte maximum RSS. Each full count is 18 above the Loop 34 closeout.

Repository-wide Ruff lint, touched-file formatting, compileall, 23 source JSON
and two TOML parses, seven CLI help surfaces, 55 registered commands,
unauthorized Loop 35 runtime absence, 74 checked local Markdown links with zero
missing, workbook render/reload/formula inspection, and `git diff --check`
pass. Research commit `6f48363` passes push CI run `29214860306` and draft PR
#14 CI run `29214881916`.

Engineering capability added: a machine-checkable confound taxonomy,
synchronized-stream contract, 13-condition comparison design, staged evidence
program, missing-control refusals, and bounded incremental-attribution ceiling
now exist.

Scientific claim not established: no fixture, protected data, peripheral
recording, model, training run, residualization fit, target, or score was
accessed, so there is no peripheral-control result, incremental brain-sensor
result, absolute brain-origin result, neural advantage, decoding accuracy,
unseen-person generalization, no-keypress transfer, real-time behavior, or
portable-hardware result.

## 2026-07-12 - Loop 36 geometry/reference research boundary

Closed Loop 36 planning research while leaving the geometry/reference
experiment `Not Started`, all 29 `authorized_now` fields false, and every
fixture, real-header read, protected-data read, geometry transform, signal-unit
conversion, rereference, compensation, interpolation, model, training, stream,
device, and hardware operation closed. The machine contract freezes six
representation layers, five modality profiles, a 24-field future channel
record, 12 operation classes, 16 fixture families, 22 future gates, and 30
refusal IDs.

The primary-source audit binds BIDS channel, electrode, coordinate-system, and
unit semantics to MNE frame, montage, reference, transform, and interpolation
behavior. A matching label, standard montage name, integer coordinate-frame
code, channel count, or visually similar layout is not enough to establish
identity. Explicit unique reorder, versioned bijective aliases, declared unit
factors, and directional right-handed rigid transforms are the only candidate
identity-preserving operations. Signal scaling, EEG rereference, MEG
compensation/projectors, interpolation, zero-fill, and template mapping change
or synthesize data and require a separate signal authorization.

Current S21 aggregate/code evidence preserves names, types, positions in
metres, integer frame/unit codes, and coil types, but not a complete exchange-
frame, orientation, transform, reference, and compensation ledger. The
consumed S7 cache has no qualified measured electrode and acquisition-reference
contract. Neither dataset was reopened. A future separately authorized real-
header pass can establish at most declared metadata compatibility, not
numerical compatibility, model transfer, or device equivalence.

The nine-sheet tracker updates Dashboard `B10` and Loop 36 row 16, adds decision
`36-R1`, risk `R41`, and prompt `Loop36-Research`, and preserves Loop 25 as the
active execution decision. The 92,990-byte workbook has SHA-256
`12d49d56ab0bc2b316c3df0537a221282a220538b7ddc5544b7646d3dcba3dad`;
all nine sheets rendered before and after the edit, the export reloads with
exact key ranges, and the formula-error scan matches zero cells. The unrelated
321,169-byte inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 248 focused Loop 24-36 tests in 3.74 seconds wall
with 240,041,984-byte maximum RSS; the strict Loop 36 plus roadmap slice passes
26 tests in 0.07 seconds wall with 20,365,312-byte maximum RSS; 527 optional
unittests pass with three expected skips in 21.80 seconds wall and
564,117,504-byte maximum RSS; 524 pytest tests pass with three skips and 240
subtests in 22.73 seconds wall and 591,183,872-byte maximum RSS; and 495
dependency-light tests pass with 121 optional skips in 1.57 seconds wall and
57,638,912-byte maximum RSS. Each full count is 17 above the Loop 35 closeout.

Repository-wide Ruff lint, touched-file formatting, compileall, 25 source JSON
and two TOML parses, seven CLI help surfaces, 55 registered commands,
unauthorized Loop 36 runtime absence, 72 checked local Markdown links with zero
missing, workbook render/reload/formula inspection, and `git diff --check`
pass. Three high-level public web operations were used; public response bytes
and browser runtime/RSS are unavailable by tool contract. Protected download
bytes, real header/cache/signal/target reads, fixtures, generated payload,
transforms, models, training runs, streams, devices, and hardware operations
remain zero. Commit and CI identities are added only after the tested research
milestone is pushed. Research commit `4d5c7d2` passes push CI run
`29216381237` and draft PR #15 CI run `29216397245`.

Engineering capability added: a machine-checkable geometry/reference identity
firewall, operation taxonomy, staged header/signal protocol, strict refusal
surface, and bounded declared-metadata claim now exist.

Scientific claim not established: no fixture, protected data, real header,
signal, transform, model, training run, target, score, device, or hardware was
accessed, so there is no metadata-compatibility result, numerical compatibility,
model transfer, device equivalence, neural advantage, decoding accuracy,
unseen-person generalization, real-time behavior, or portable-hardware result.

## 2026-07-13 - Loop 37 BIDS derivative/provenance research boundary

Closed Loop 37 planning research while leaving the derivative export
experiment `Not Started`, all 29 `authorized_now` fields false, and every
fixture, exporter, derivative tree, validator install/run, protected payload,
raw copy, release/upload, model, training, stream, device, and hardware
operation closed. The machine contract freezes six export layers, five
artifact profiles, 15 stable BIDS field mappings, 16 explicit NeuroDecodeKit
extension fields, 20 fixture families, four independently authorized stages,
24 future gates, and 32 refusal IDs.

The primary-source audit pins the future envelope to BIDS 1.11.1 dataset,
derivative, URI, metadata-propagation, naming, and validator behavior.
NeuroToken NPZ caches, sentence/signal caches, split reports, report cards, and
manifests have no stable BIDS derivative suffix and remain explicitly
non-standard payloads. A future export must use BIDS URIs or opaque hashes,
allowlist every payload, redact local identity, copy zero raw files, refuse
target/prompt/response/free text, and retain every validator issue. Validator
success cannot establish privacy, license, source hashes, cross-machine
reproduction, or scientific validity.

The local audit found zero tracked neural/model binary candidate files and zero
candidate bytes; no payload was opened. Seven high-level public web operations,
including two official GitHub repository reads, informed the planning record.
Public response bytes and browser runtime/RSS are unavailable by tool contract.
Protected downloads, real header/cache/signal/target reads, fixtures, generated
derivative bytes, validator runs, raw copies, releases/uploads, models, training
runs, streams, devices, and hardware operations remain zero.

The nine-sheet tracker updates Dashboard `B10` and Loop 37 row 17, adds decision
`37-R1`, risk `R42`, and prompt `Loop37-Research`, and preserves Loop 25 as the
active execution decision. The 94,670-byte workbook has SHA-256
`9787dd51a5c0b7432a3e31316e56075a4495e0879dae8850a8def11c41900365`;
all nine sheets rendered before and after the edit, the export reloads with
exact key ranges, and the formula-error scan matches zero cells. The unrelated
321,169-byte inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 226 focused Loop 24-37 planning tests in 0.20 seconds
wall with 50,167,808-byte maximum RSS; the strict Loop 37 plus roadmap slice
passes 26 tests in 0.09 seconds wall with 34,865,152-byte maximum RSS; 544
optional unittests pass with three expected skips in 22.45 seconds wall and
587,300,864-byte maximum RSS; 541 pytest tests pass with three skips and 247
subtests in 23.08 seconds wall and 601,358,336-byte maximum RSS; and 512
dependency-light tests pass with 121 optional skips in 1.90 seconds wall and
73,728,000-byte maximum RSS. Each full count is 17 above the Loop 36 closeout.

Repository-wide Ruff lint, touched-file formatting, compileall, 25 source JSON
and two TOML parses, seven CLI help surfaces, 55 registered commands,
unauthorized Loop 37 runtime absence, 72 checked local Markdown links with zero
missing, workbook render/reload/formula inspection, and `git diff --check`
pass. Research commit `ef31efc` passes push CI run `29226436884` and draft PR
#16 CI run `29226853455`.

Engineering capability added: a machine-checkable BIDS envelope and provenance
firewall, explicit non-standard payload taxonomy, portable source-identity
rules, no-raw-copy/privacy refusals, validator ceiling, staged release program,
and bounded future export claim now exist.

Scientific claim not established: no fixture, protected payload, exporter,
derivative tree, validator run, raw copy, release, model, training run, target,
score, device, or hardware was accessed, so there is no BIDS-organized bundle,
privacy/license qualification, cross-machine reproduction, neural advantage,
decoding accuracy, unseen-person generalization, real-time behavior, or
portable-hardware result.

## 2026-07-13 - Loop 38 neural-data privacy/lifecycle research boundary

Closed Loop 38 planning research while leaving the privacy/lifecycle
experiment `Not Started`, all 32 `authorized_now` fields false, and every
fixture, scanner, deletion, protected-root scan, identity attack, consent/legal
determination, history rewrite, remote cleanup, release/upload, model,
training, stream, device, and hardware operation closed. The machine contract
freezes five sensitivity levels, eight artifact classes, ten lifecycle
surfaces, 12 sensitive-field classes, 12 threat scenarios, five deletion-
receipt levels, 24 fixture families, four independently authorized stages,
eight outcomes, six claims, 26 gates, and 36 refusal IDs.

The primary-source audit pins stable NIST Privacy Framework 1.0, NISTIR 8062,
PRAM, SP 800-88 Rev. 2, Git-history cleanup limits, Open Brain Consent, EEG
identity risk, and OECD neurotechnology stewardship. It separates technical
redaction, de-identification, path absence, repository coordination, media
sanitization, consent, license, and sharing authority. Neural derivatives,
stable hashes, pseudonyms, high-resolution timing, geometry, and small
individual rows remain potentially linkable. Unknown external copies remain
`unresolved`.

The metadata-only local audit found zero current tracked neural/model binary
candidate files and bytes and zero candidate paths across all-ref Git history;
no payload was opened. Six high-level public web operations and eight official
or primary page opens informed the planning record. Public response bytes and
web runtime/RSS are unavailable by tool contract. Protected downloads, real
header/cache/signal/target reads, fixtures, generated payloads, scanner runs,
deletions, identity attacks, history rewrites, releases/uploads, models,
training runs, streams, devices, and hardware operations remain zero.

The nine-sheet tracker updates Dashboard `B10` and Loop 38 row 18, adds
decision `38-R1`, risk `R43`, and prompt `Loop38-Research`, and preserves Loop
25 as the active execution decision. The 96,249-byte workbook has SHA-256
`8f03b7369362822c14f59ae438ffb09967ebd9cb4cb83f36cf852876b28e0b5c`;
all nine sheets rendered after the edit, the export reloads with exact key
ranges, and the formula-error scan matches zero cells. The unrelated
321,169-byte inspection sidecar remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 240 focused Loop 24-38 planning tests in 0.16 seconds
wall with 58,589,184-byte maximum RSS; the strict Loop 38 plus roadmap slice
passes 23 tests in 0.07 seconds wall with 34,390,016-byte maximum RSS; 558
optional unittests pass with three expected skips in 21.97 seconds wall and
605,208,576-byte maximum RSS; 555 pytest tests pass with three skips and 254
subtests in 22.13 seconds wall and 604,880,896-byte maximum RSS; and 526
dependency-light tests pass with 121 optional skips in 0.63 seconds wall and
77,545,472-byte maximum RSS. Each full count is 14 above the Loop 37 closeout.

Repository-wide Ruff lint, touched-file formatting, compileall, 26 source JSON
and two TOML parses, seven CLI help surfaces, 55 registered commands,
unauthorized Loop 38 runtime absence, 72 checked local Markdown links with zero
missing, workbook render/reload/formula inspection, and `git diff --check`
pass. Research commit `c82c3fa` passes push CI run `29228686142` and draft PR
#17 CI run `29228698759`.

Engineering capability added: a machine-checkable privacy risk map,
sensitivity taxonomy, artifact/copy inventory contract, redaction surface,
deletion-receipt ladder, consent/license firewall, staged evidence program,
and strict claim ceiling now exist.

Scientific claim not established: no fixture, protected payload, scanner,
deletion operation, identity attack, consent determination, model, training
run, target, score, release, device, or hardware was accessed, so there is no
privacy-safe dataset, anonymous neural representation, verified media
sanitization, shareable release, neural advantage, decoding accuracy,
unseen-person generalization, real-time behavior, or portable-hardware result.

## 2026-07-13 - Loop 39 cross-machine reproducibility research boundary

Closed Loop 39 planning research while leaving the reproducibility experiment
`Not Started`, all 36 `authorized_now` fields false, and every fixture,
environment manifest, matrix job, dependency lock/install, package build,
protected payload, model, training run, independent reproducer, edge runtime,
stream, device, and hardware operation closed. The machine contract freezes
seven qualification levels, 18 environment identity fields, eight output
classes, six comparison classes, six future matrix cells, 20 fixture families,
four independently authorized stages, eight outcomes, seven claims, 28 gates,
and 38 refusal IDs.

The primary-source audit uses ACM terminology to separate same-team
repeatability, different-team reproduction, and replication; uses Reproducible
Builds only for specified bit-identical build artifacts; and records Python,
PyPA, NumPy, PyTorch, GitHub Actions, MNE, and Scientific Python environment
boundaries. The future matrix contains Ubuntu 24.04 x64 Python 3.10/3.11/3.12
base, macOS 15 arm64 Python 3.12 base, and separate Ubuntu/macOS Python 3.12
optional-neuro cells. Semantic identity and floating compatibility use
different comparison classes and cannot be promoted into independent
reproduction or scientific replication.

The local support audit found two `ubuntu-latest` Python 3.12 CI profiles, zero
explicit cross-OS cells, zero tracked lockfiles, no reproducible package-build
job, and two direct `tomllib` test imports that leave complete Python 3.10 test
qualification unavailable. The diagnostics-only local host was Darwin 25.6.0
arm64 with CPython 3.13.5, NeuroDecodeKit 0.1.0, NumPy 2.5.0, SciPy 1.18.0, MNE
1.12.1, and Torch 2.13.0; it was not counted as a completed matrix cell. Six
high-level public web operations and eight official or primary page opens
informed the planning record. Public response bytes and web runtime/RSS are
unavailable by tool contract. Protected reads, fixtures, manifests, matrix
jobs, installs, lockfiles, package builds, models, training runs, edge runs,
streams, devices, and hardware operations remain zero.

The nine-sheet tracker updates Dashboard `B10` and Loop 39 row 19, adds
decision `39-R1`, risk `R44`, and prompt `Loop39-Research`, and preserves Loop
25 as the active execution decision. The 97,628-byte workbook has SHA-256
`d0f661b9718891237605873eff1124cea7df90fbb70f4affeb04740b497a327c`;
all nine sheets rendered before and after the edit, four untouched sheets were
pixel-identical, the export reloads with exact key ranges, and the formula-
error scan matches zero cells. The unrelated 321,169-byte inspection sidecar
remains byte-identical at SHA-256
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.

Local verification passes 256 focused Loop 24-39 planning tests in 0.25 seconds
wall with 66,093,056-byte maximum RSS; the strict Loop 39 plus roadmap slice
passes 25 tests in 0.09 seconds wall with 34,930,688-byte maximum RSS; 574
optional unittests pass with three expected skips in 21.80 seconds wall and
608,272,384-byte maximum RSS; 571 pytest tests pass with three skips and 261
subtests in 21.96 seconds wall and 615,596,032-byte maximum RSS; and 542
dependency-light tests pass with 121 optional skips in 0.64 seconds wall and
83,509,248-byte maximum RSS. Each full count is 16 above the Loop 38 closeout.
One initial full-suite invocation omitted `PYTHONPATH=src` and failed import
collection; the corrected source-layout command produced the green counts
above.

Repository-wide Ruff lint, seven touched Python file format checks, compileall,
27 source JSON and two TOML parses, seven CLI help surfaces, 55 registered
commands, unauthorized Loop 39 runtime absence, 72 checked local Markdown links
with zero missing, workbook render/reload/formula inspection, and `git diff
--check` pass. Research commit `efbf764` passes push CI run `29230660807` and
draft PR #18 CI run `29230681661`.

Engineering capability added: a machine-checkable cross-machine
reproducibility taxonomy, environment identity contract, six-cell future
matrix, output comparison firewall, numerical tolerance policy, resource
envelope, and strict claim ceiling now exist.

Scientific claim not established: no fixture, environment manifest, matrix
job, dependency lock, package build, protected payload, model, training run,
target, score, independent reproducer, edge runtime, device, or hardware was
accessed, so there is no cross-machine reproduction, independent replication,
neural advantage, decoding accuracy, unseen-person generalization, real-time
behavior, or portable-hardware result.

## 2026-07-13 - Loop 40 edge-runtime packaging research boundary

Closed Loop 40 planning research while leaving the packaging experiment `Not
Started`, all 40 `authorized_now` fields false, and every target/backend
selection, fixture, optional install, export, conversion, package, eager or
packaged inference, profiler, memory planner, delegate, simulator, app, device,
and hardware operation closed.

The primary-source audit compares ExecuTorch/XNNPACK, ONNX Runtime Mobile,
LiteRT, and Core ML without selecting a winner. ExecuTorch/XNNPACK is a research
lead only because the source is PyTorch and the official stack exposes the
needed delegate, memory-planning, profiling, and mobile-integration surfaces.
The relevant Loop 39 matrix has not run, and no target OS, architecture, ABI,
minimum deployment target, or application envelope exists.

The machine contract freezes seven qualification levels, six package layers,
four backend profiles, 20 identity fields, eight output classes, six comparison
classes, 24 fixture families, four separately authorized stages, eight
outcomes, seven claims, 30 gates, and 40 refusals. It pins the retained
1,130-parameter/5,210-byte float32 reference while keeping normalization,
causal state, timestamps, frame scheduling, decoder behavior, and app
integration outside the torch-graph claim.

Three high-level public web operations and 12 official or primary page opens
informed the record. Public response bytes and web runtime/RSS are unavailable
by tool contract. Generated experiment bytes, fixtures, installs, exports,
packages, inference runs, profiler/memory-planner/delegate runs, protected
reads, model/training runs, simulator/app runs, devices, and hardware remain
zero.

The nine-sheet tracker updates Dashboard `B10` and Loop 40 row 20, adds
decision `40-R1`, risk `R45`, and prompt `Loop40-Research`, and preserves Loop
25 as the active execution decision. The 98,147-byte workbook has SHA-256
`31675786de3d09be758f2001e7e681c3bdfa1b2ff75378162430e32ddf3d00e5`;
all nine sheets render, exact key ranges reload, and the formula-error scan
matches zero cells.

Artifact-tool export unintentionally rewrote the unrelated untracked workbook
inspection sidecar. No filesystem snapshot retained its exact original bytes.
The preserved Loop 16 workbook reproduces the sidecar's complete semantic
content and original 321,169-byte size, but artifact-tool-generated workbook
and sheet IDs differ, so the reconstructed SHA-256 is
`b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`
rather than the original
`5cd0ef08446c4e5feee5ce11f27eef41fae5eee8975cc77f6d401faca3b79f45`.
The sidecar remains untracked and unstaged; the accidental Loop 40 rewrite is
preserved outside the repository in `/tmp` for this local session.

Local verification passes 269 focused Loop 24-40 planning tests in 1.28
seconds wall with 74,825,728-byte maximum RSS; the strict Loop 40 plus roadmap
slice passes 22 tests in 1.10 seconds wall with 42,139,648-byte maximum RSS;
587 optional unittests pass with three expected skips in 23.91 seconds wall and
608,894,976-byte maximum RSS; 584 pytest tests pass with three skips and 269
subtests in 23.07 seconds wall and 614,612,992-byte maximum RSS; and 555
dependency-light tests pass with 121 optional skips in 2.63 seconds wall and
99,549,184-byte maximum RSS. Each full count is 13 above the Loop 39 closeout.

Repository-wide Ruff lint, seven touched Python file format checks, compileall,
28 source JSON and two TOML parses, seven CLI help surfaces, 55 registered
commands, unauthorized Loop 40 runtime absence, 72 checked local Markdown links
with zero missing, workbook render/reload/formula inspection, the 82-commit
Gitleaks scan, and `git diff --check` pass. Research commit `55a2191` passes
push CI run `29233258741` and draft PR #19 CI run `29233277952`.

Engineering capability added: a machine-checkable, named-target edge-package
decision boundary now separates graph export, host stream semantics, fallback,
complete deployment cost, simulator integration, and physical-device claims.

Scientific claim not established: no package or inference ran, so no neural
advantage, decoding accuracy, unseen-person generalization, real-time capture-
to-text latency, portable-hardware behavior, or scientific result exists.

## 2026-07-13 - Loop 41 Stream-To-NeuroToken Planning Research

- Audited the frozen RW3 source-chunk contract, the still-false RW3 Stage A
  request, NeuroTokenCache v0, the Loop 21 causal mock producer, and Loops 25,
  37, and 39 dependency states without opening any runtime or payload.
- Reviewed eight official primary pages covering LSL timestamps, clock offsets,
  buffering/recovery, postprocessing, monotonic duration clocks, Python timing,
  and BIDS derivative provenance. Four public search queries and two high-level
  web operations are recorded; public response bytes/runtime/RSS are
  unavailable from the tool contract.
- Added `registries/loop41_research_boundary.v0.json` with six integration
  layers, seven clock views, eight anomaly classes, five inherited schedules,
  five resume cuts, 18 hash bindings, 28 fixture families, four stages, 32
  gates, 42 refusals, and 42 false authorization fields.
- Added 14 dependency-light Loop 41 invariants and advanced the machine roadmap
  to schema v0.18.0 while keeping all 20 loop execution flags false.
- Generated experiment bytes, fixtures, source chunks, adapters,
  preprocessing/token runs, protected reads, target/model/training operations,
  streams, devices, hardware operations, and end-to-end latency measurements
  remain zero. Loop 41 remains `Not Started` and unauthorized.
- The user-owned workbook inspection sidecar remains untracked and must remain
  byte-exact at SHA-256
  `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.
- Local acceptance passed on one numerical thread: `unittest` ran 601 tests
  with three skips in 22.250 seconds (23.43 seconds wall, 616,284,160-byte peak
  RSS), `pytest` ran 598 tests with three skips and 277 subtests in 22.14
  seconds (23.37 seconds wall, 621,232,128-byte peak RSS), and dependency-light
  Python ran 569 tests with 121 skips in 1.474 seconds (2.73 seconds wall,
  92,831,744-byte peak RSS). These are increases of 14 tests, 14 tests plus
  eight subtests, and 14 tests respectively over the Loop 40 baselines.
- Focused verification passed 23 Loop 41/roadmap tests and 248 planning-boundary
  tests. Ruff check/format, compileall, all 29 source JSON files, both TOML
  files, and `git diff --check` passed.
- The CLI registers 55 commands; root help plus the existing
  `make-neurotoken-cache`, `inspect-neurotoken-cache`, and
  `causal-replay-gate` help surfaces passed. All 72 tracked local Markdown
  links resolve, and Gitleaks found no leaks across 84 commits and about 5.07
  MB of Git history.
- The visually inspected nine-sheet tracker workbook is 98,959 bytes at
  SHA-256
  `185cbc483321e3b1b53c7c6426092a31ed3ef4be0c7e0b1b4c9c5963b1a4c672`;
  its formula scan found zero errors. All 20 roadmap execution flags and all
  42 Loop 41 `*_authorized_now` fields remain false; the three authorization
  setup booleans are also false.
- Research commit `5e8308f` is pushed on
  `codex/loop-41-stream-neurotoken-research`. Push CI run `29235264294` and
  draft PR #20 CI run `29235281640` both pass Base Python and Optional Neuro
  Readers.

Engineering capability added: a machine-checkable future stream-to-NeuroToken
integration boundary now keeps clocks, anomaly propagation, resume state,
identity, provenance, resources, and unavailable latency claims explicit.

Scientific claim not established: no Loop 41 runtime or protected payload was
opened, so no neural advantage, decoding accuracy, unseen-person
generalization, real-time capture-to-text latency, or portable-hardware result
exists.

## 2026-07-13 - Loop 42 One-Device Qualification Planning Research

- Audited all 13 device-registry records, including seven EEG/ExG candidates,
  against the Loop 29 portability, Loop 38 privacy, Loop 41 stream, and RW3
  dependency boundaries without installing or importing an SDK.
- Selected OpenBCI Cyton base 8-channel over USB radio as the future mechanics
  candidate at Q0 official-specification level. Daisy, Wi-Fi Shield, GUI
  network streaming, cloud, targets, models, purchase, and ownership claims
  are excluded.
- Reviewed nine official OpenBCI/BrainFlow pages through 12 public search
  queries and four high-level web operations. Public response bytes, runtime,
  and RSS are unavailable from the tool contract.
- Added `registries/loop42_research_boundary.v0.json` with 28 identity fields,
  16 packet fields, seven timing observables, ten anomalies, ten privacy
  surfaces, ten safety requirements, six qualification levels, four stages, 30
  fixture families, 34 gates, 46 refusals, and 45 false authorization fields.
- Added 15 dependency-light invariants and advanced the machine roadmap to
  schema v0.19.0 while keeping all 20 execution flags false.
- Generated experiment files/bytes, device seconds, installs, SDK imports,
  serial reads, discovery, connections, hardware operations, participant
  contacts, recordings, network/cloud operations, raw/cache/target reads,
  models, training, decoders, NeuroTokens, and latency measurements remain
  zero. Loop 42 remains `Not Started` and unauthorized.
- The user-owned workbook inspection sidecar remains untracked and must remain
  byte-exact at SHA-256
  `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.
- Local acceptance passed on one numerical thread. The strict Loop 42 plus
  roadmap slice passes 24 tests in 0.043 seconds internal; all Loop 24-42
  planning boundaries pass 263 tests in 1.99 seconds wall with 88,997,888-byte
  maximum RSS. Full unittest discovery passes 616 tests with three expected
  skips in 24.31 seconds wall and 612,483,072-byte maximum RSS; pytest passes
  613 tests with three skips and 277 subtests in 23.34 seconds wall and
  625,065,984-byte maximum RSS; dependency-light Python passes 584 tests with
  121 optional skips in 2.57 seconds wall and 106,840,064-byte maximum RSS.
  Each full count is 15 above Loop 41 with no prior regression.
- Ruff lint, all ten touched Python format checks, compileall, all 31 source
  JSON files, both TOML files, four CLI help surfaces, 55 registered commands,
  72 local Markdown links, the 86-commit Gitleaks scan, authorization/runtime
  absence checks, and `git diff --check` pass. Repository-wide Ruff formatting
  still reports the pre-existing 96-file backlog and remains out of scope.
- The visually inspected nine-sheet tracker is 99,626 bytes at SHA-256
  `7ac856e73b7e4b985f3becbf3372e1b973074959eb4973213a53a1452249c2a8`.
  Exact key ranges reload, the formula-error scan matches zero cells, and the
  user-owned untracked sidecar remains byte-exact and unstaged.
- Research commit `9188157` is pushed on
  `codex/loop-42-device-qualification-research`. Push CI run `29237366884` and
  draft PR #21 CI run `29237382715` both pass Base Python and Optional Neuro
  Readers. GitHub reports only its platform-level Node 20 action deprecation
  annotation; no repository check failed.

Engineering capability added: a machine-checkable one-device qualification
boundary now makes future identity, packet, clock, anomaly, locality, safety,
resource, stage, and claim decisions exact for one named path.

Scientific claim not established: no SDK, device, participant, signal, target,
model, decoding, or latency operation ran, so there is no EEG-quality, neural-
advantage, unseen-person, real-time, portable-hardware, or text-decoding result.

## 2026-07-13 - Loop 43 Independent Reproduction Planning Research

- Reviewed ACM Artifact Review and Badging, CODECHECK principles/project,
  ReScience C guidance/FAQ, the NeurIPS reproducibility program, FAIR4RS v1,
  and GitHub Actions security guidance without creating a challenge or running
  an external experiment.
- Selected one future target-free NeuroToken causal-replay software-artifact
  reproduction lane, but marked it currently ineligible because compatible
  Loop 37, 38, and 39 execution dependencies remain unsatisfied.
- Added `registries/loop43_research_boundary.v0.json` with seven qualification
  levels, 16 independence fields, 28 packet fields, 34 submission fields,
  eight comparison classes, 12 discrepancy classes, four stages, 32 fixture
  families, 36 gates, 48 refusals, and 48 false authorization fields.
- Added 15 dependency-light invariants and advanced the machine roadmap to
  schema v0.20.0 while retaining all 20 false execution flags.
- Packet, oracle, fixture, workflow, outreach, contributor, submission,
  adjudication, archive, release, model, training, stream, device, runtime, and
  generated experiment byte counters remain zero. An overbroad local JSON
  validator nevertheless parsed 136 cache JSON files, including 11 known
  consumed S21 session-2 report/metadata files. No raw array, FIF/MAT, model,
  inference, scoring, tuning, training, or claim-selection operation occurred;
  the zero-consumed-read claim is withdrawn and the incident is retained.
- Local acceptance passed on one numerical thread after the incident was
  machine-recorded. The strict Loop 43 plus roadmap slice passes 24 tests in
  0.049 seconds internal; Loop 24-43 planning boundaries pass 308 tests in 1.33
  seconds wall with 91,504,640-byte peak RSS. Full unittest discovery passes
  631 tests with three expected skips in 22.99 seconds wall and 620,167,168-byte
  peak RSS; pytest passes 628 tests with three skips and 277 subtests in 22.06
  seconds wall and 624,771,072-byte peak RSS; dependency-light Python passes
  599 tests with 121 optional skips in 1.75 seconds wall and 108,773,376-byte
  peak RSS. Each full count is 15 above Loop 42 with no prior regression.
- Ruff lint/format, compileall, 32 Git-bound JSON source files, both TOML files,
  four CLI help surfaces, 55 registered commands, 76 local Markdown links,
  authorization/runtime absence checks, and `git diff --check` pass. Gitleaks
  scans 88 commits and about 5.23 MB with zero leaks after narrowly allowing the
  exact non-secret roadmap identifier it had misclassified.
- The visually inspected nine-sheet tracker is 100,461 bytes at SHA-256
  `7464dcc19b67740ff8f43fe0501e9c95be0f5dda1b62386c09eb4b5b537730f0`.
  Key ranges reload, the formula-error scan matches zero cells, and the
  user-owned inspection sidecar remains untracked and byte-exact at SHA-256
  `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.
- Research commit `81798e0` is pushed on
  `codex/loop-43-independent-reproduction-research`. Push CI run
  `29240649149` and draft PR #22 CI run `29240665109` both pass Base Python and
  Optional Neuro Readers. GitHub reports only its platform-level Node 20 action
  deprecation annotation; no repository check failed.

Engineering capability added: a machine-checkable independent artifact-
reproduction boundary now freezes identities, commitment order, comparisons,
discrepancies, privacy/security checks, resources, outcomes, and claim ceilings.

Scientific claim not established: no independent run or protected experiment
occurred, so there is no scientific replication, neural advantage, decoding,
unseen-person generalization, real-time, device, or home-use result.

## 2026-07-13 - Loop 44 Claim Promotion And Release Review

- Reviewed Model Cards, Datasheets for Datasets, NIST AI RMF, COBIDAS-MEEG,
  ACM artifact terminology, FAIR4RS, GitHub citation guidance, and Zenodo DOI
  versioning without creating a release or running a new experiment.
- Added `registries/loop44_claim_release_matrix.v0.json` with 16 claim cards,
  seven evidence levels, five model cards, four dataset cards, 14 release gates,
  eight risks, and explicit engineering/scientific decisions.
- Promoted three engineering claims, retained three negative or inconclusive
  real-data findings, kept two claims fixture-backed, parked two measured
  paths, marked five desired claims unavailable, and prohibited one overclaim.
- Held the engineering release because the current evidence stack is not on
  `main` and Loops 38, 39, and 43 have not executed. Parked scientific
  performance because no real neural model has convincingly beaten its
  no-signal comparator.
- Opened no raw data, real cache, consumed evaluation, target, model,
  checkpoint, stream, device, or hardware. One overbroad documentation search
  displayed the user-owned tracker inspection sidecar once. Artifact-tool later
  overwrote it during workbook export; the exact prior bytes were recovered,
  restored, and kept untracked and unstaged. It was not used as scientific
  evidence.
- Local acceptance passes 24 focused Loop 44 and Loops 45-64 invariants in
  0.06 seconds wall with 18,546,688-byte peak RSS; 655 unittests with three
  expected skips in 21.87 seconds wall and 616,251,392-byte peak RSS; 652
  pytest tests with three skips and 277 subtests in 22.52 seconds wall and
  622,362,624-byte peak RSS; and 623 dependency-light tests with 121 optional
  skips in 1.77 seconds wall and 92,422,144-byte peak RSS. Ruff lint,
  compileall, tracked plus new JSON, both TOML files, three CI CLI help
  surfaces, `git diff --check`, and a 90-commit/5.34-MB gitleaks scan pass.
  Exact-commit remote CI remains pending push.

Engineering capability added: a machine-checkable claim and release ledger now
binds public statements to evidence, limitations, access, privacy, and license.

Scientific claim not established: Loop 44 adds no positive neural advantage,
unseen-person generalization, real-time decoding, portable/home hardware,
independent reproduction, scientific replication, or clinical result.

## 2026-07-13 - Loops 45-64 Scientific Evidence Roadmap

- Added 20 contiguous planning work orders across Real Signal Truth,
  Unseen-Person Verdict, Accessible EEG Evidence, Causal Local Use, and
  Independent Evidence And Release.
- Bound the critical path to causal mechanics, one reserved S21 validation
  event, intact-signal controls, one nonfinal development person, and one frozen
  final-only S25 verdict.
- Kept all 20 execution flags and all nine global authorization fields false;
  S21 session 2 and S7 remain consumed and S25 remains unopened.
- Added ten primary-source bindings, ten cross-loop kill branches, and 11
  dependency-light invariants.
- Extended the tracker to ten sheets. The 114,652-byte workbook reloads at
  SHA-256 `83606898dc58201e016f1f44ca156c1817f3719a8a401b2619e20d7f349f91ae`;
  all sheets rendered and the formula-error scan found zero matches.
- Artifact-tool overwrote the adjacent user-owned inspection sidecar during
  export. The exact prior copy was recovered and restored to SHA-256
  `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`;
  it remains untracked and unstaged.

Engineering capability added: the tracker now routes directly from current
negative evidence to falsifiable real-effect, unseen-person, EEG, causal-use,
and independent-release gates.

Scientific claim not established: planning these gates creates no neural
advantage, transfer, EEG, real-time, home-use, or independent result.
