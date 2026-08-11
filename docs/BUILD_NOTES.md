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
- Research commit `90d8919` is pushed on
  `codex/loop-44-claim-release-research`. Push CI run `29243833014` and draft PR
  #23 CI run `29243844680` both pass Base Python and Optional Neuro Readers.
  GitHub reports only its platform-level Node 20 action deprecation annotation;
  no repository check failed.

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

## 2026-07-13 - Loop 25 Causal Preprocessing v1 Result

- Recorded separate green authorization commit `1e7296a` and implementation
  commit `439f151` before any registered execution. GitHub CI runs
  `29275552886` and `29277702513` passed both required jobs.
- Designed the registered filter exactly once. The 65,537-point static response
  and 23-probe alias gate passed before either fixture partition opened: four
  dedicated anti-alias and nine total SOS sections, 720 bytes of state,
  maximum pole magnitude 0.9988174290, dedicated stopband maximum -60.000000
  dB, and complete-chain folding-band maximum -67.503786 dB.
- Generated one target-free 728,596-byte fixture. Development seed 2501 opened
  once, passed, and froze before qualification seed 2502 opened once and passed
  unchanged. Metadata-only inspection opened zero signal arrays.
- Passed 24/24 items, 168/168 schedule checks, 240/240 resume checks, and 72/72
  future-mutation controls. The producer is causal with zero right context;
  sample-grid timestamps are exact, while frequency-dependent effective delay
  and end-to-end latency remain unavailable.
- Static plus complete-gate internal runtime was 5.542175 seconds. Maximum
  observed peak RSS was 136,806,400 bytes. Input/output bytes were
  1,971,744/212,328; total generated bytes were 788,967, or 9.41% of the 8 MiB
  cap. One CPU thread and one worker were used.
- All 23 access counters matched exactly. Real-data, real-cache, consumed-
  evidence, target/label/text/prediction, checkpoint, model, training,
  parameter-update, network, RW3, stream, device, and hardware counters were
  zero. No generated experiment artifact is committed.
- Added a machine-readable result, measured closeout, tracker transitions, and
  six dependency-light result invariants. Loop 25 and roadmap Loop 45 are
  complete; current execution authorization remains false because no rerun is
  open. Loop 26/46 still requires a new preregistration and authorization.
- Final local acceptance passes 89 focused Loop 25 and roadmap-boundary tests
  in 3.544 seconds,
  684 full unittests with three expected skips in 26.17 seconds wall and
  618,528,768-byte peak RSS, and 637 dependency-light tests with 124 expected
  optional skips in 1.80 seconds wall and 107,659,264-byte peak RSS. Ruff lint
  and format checks, compileall, JSON parsing, all five CLI help/inspection
  surfaces, `git diff --check`, workbook ZIP/render/formula checks, and the
  repository secret scan pass. The tracked workbook is 114,890 bytes at
  SHA-256 `1d014d7ff3e31773564062ed9430df70757a682e16ff09f4c124af5cf724b132`;
  the adjacent user-owned sidecar remains untracked and byte-identical at
  SHA-256 `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.

Engineering capability added: one strict stateful 1000-to-100 Hz causal
preprocessing interface now passes the registered anti-alias, schedule, resume,
mutation, timestamp, access, and resource gates.

Scientific claim not established: no neural recording, target, model, or
training operation occurred, so retained neural information, neural advantage,
decoding accuracy, unseen-person generalization, end-to-end latency, real-time
operation, and portable/home hardware remain unproven.

## 2026-07-13 - Loop 26/31/33 Shared Validation Authorization Packet

- Preserved the green shared preregistration at commit `881145d` and CI run
  `29282661766`, then prepared a separate hash-bound authorization request with
  all 19 `authorized_now` fields false and every protected/model/training/
  scoring counter at zero.
- Reconciled the machine and human roadmaps around one event: 21 bounded
  parameter-update runs, 24 target-blind model-inference runs, six train-only
  priors, 31 frozen six-row prediction sets, the ten-condition Loop 31 encoder
  matrix, the six-size Loop 33 curve, and one target delivery only after a
  separately committed, pushed, remotely green prediction freeze.
- Corrected the evidence boundary. The legacy deflated NPZ loader historically
  materialized the complete target array, so physical-never-opened wording is
  withdrawn. The supported boundary is narrower: the six validation targets
  were not used for fitting, restart/model/threshold selection, or predictive
  scoring.
- Kept source-test rows, session 2, S7, S20, S25, raw FIF/MAT, downloads,
  language models, RW3, streams, devices, and hardware closed. This milestone
  performed zero raw-data reads, real-cache value reads, target deliveries,
  model runs, training runs, parameter updates, prediction freezes, or scores.
- Updated the ten-sheet tracker in an ignored isolated work directory. The
  input workbook was 114,890 bytes and the verified output is 115,658 bytes at
  SHA-256 `651b9be4bab74c0258b340e6a3415f4ae1795a616a8b609d6b111d4d6e5cc237`;
  generation completed in 3.985 seconds wall, all changed sheets rendered, the
  formula scan found zero errors, and ZIP integrity passed. Peak builder RSS
  was unavailable. The adjacent user-owned sidecar remains untracked,
  unstaged, and byte-identical at SHA-256
  `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.
- A focused invariant caught an accidental Loop 29 flag mutation before the
  final pass; it was restored to planning-only. The first full pass then caught
  three stale Loop 31/33 living-roadmap expectations; those were reconciled
  without changing either immutable planning-research registry.
- Final local acceptance passes 90 focused shared-contract, request, planning-
  boundary, and roadmap tests; 708 full unittests with three expected skips in
  25.212 seconds and
  616,710,144-byte process maximum RSS; and 661 dependency-light tests with 124
  expected skips in 1.550 seconds and 107,626,496-byte process maximum RSS.
  The pre-change baselines were 684/3 and 637/124. Ruff lint, changed-file Ruff
  formatting, compileall, all registry JSON, TOML, CLI help, `git diff --check`,
  workbook render/formula/ZIP checks, and a 70,283-byte staged Gitleaks scan
  pass. A repository-wide Ruff format check still identifies 104
  pre-existing files outside this milestone and they remain untouched.

Engineering capability added: one green, machine-checked authorization packet
now binds a bounded causal model, signal-attribution controls, scaling curve,
prediction-freeze order, exact inference, access accounting, and resource caps
before any protected execution.

Scientific claim not established: no protected validation experiment ran, so
there is still no demonstrated neural advantage, sensor-signal dependence,
brain-specific origin, unseen-person transfer, decoding accuracy, real-time
operation, or portable/home hardware result.

## 2026-07-15 - Loop 26/31/33 Shared Validation Implementation

- Implemented bounded sequential NPY-member traversal inside deflated NPZ
  archives with explicit opaque-excluded-row accounting and no pickle support.
- Implemented the exact 2,908-parameter causal candidate and 2,884-parameter
  linear comparator with fixed 240-step deterministic CPU training and numeric
  checkpoints.
- Implemented the frozen prefix order, six priors, seven additional controls,
  31-set hash-only freeze, all 64 sign assignments, and the registered
  intersection-union and bounded-scaling decisions.
- Split protected execution into static, derivative, target-blind, freeze
  inspection, and one-shot score CLI stages. The scorer requires the freeze
  record to be tracked at the green `HEAD` and creates a consumed marker before
  opening validation targets.
- Added fail-closed validation for split and source binding, target leakage,
  malformed caches, exact access counters, parameter inventory, configuration,
  checkpoint and transform hashes, working arrays, generated bytes, runtime,
  RSS, and one-thread execution.
- Kept every implementation and test operation synthetic. No real S21 cache
  stat, hash, member, signal, or target value was read; no real model, training,
  prediction, freeze, or score exists at this milestone.
- Final local acceptance passes 45 focused Loop 26 implementation, contract,
  authorization, reader, model, control, freeze, and scorer tests in 0.977
  seconds. The complete suite passes 739 tests with three expected skips in
  26.10 seconds wall and 628,834,304-byte process maximum RSS, compared with
  the 716-test, three-skip pre-change baseline. Repository Ruff, compileall,
  all registry JSON, all five Loop 26 CLI help surfaces, and `git diff --check`
  pass.
- The first target-free static run on green implementation `91409bd` passed all
  frozen identities in 0.798270 seconds with 208,224,256-byte internal peak
  RSS. It made one cache stat read, 14 archive-header reads, two target-free
  metadata member streams, zero cache hash passes, and zero signal or target
  row deliveries. That measured ledger exposed a pre-model expectation bug:
  the 12-member archive plus two static header reads and six derivative member
  headers totals 20, not 16. Protected values remained closed while the exact
  invariant was corrected for a new implementation commit and remote CI pass.
- Corrected implementation `4015677` passed push CI `29425275808` and PR CI
  `29425280317`. Its static gate passed in 0.797510 seconds, then the source
  cache matched one 10,632,576-byte hash pass. Derivatives delivered 55 train
  signals/targets and six validation signals with zero validation-target,
  source-test, or session-2 rows; working arrays used 30,726,776 bytes.
- The target-blind run completed 18 candidate plus three control fits, 5,040
  optimizer steps, 24 model inferences, six train-only priors, 21 checkpoint
  writes, and 31 frozen prediction sets. Parameter updates took 182.152382
  seconds; end-to-end runtime was 184.046922 seconds; peak RSS was 522,797,056
  bytes; working arrays were bounded at 43,114,644 bytes. Checkpoints used
  278,753 bytes and private predictions used 50,810 bytes.
- The 31,271-byte hash-only freeze record is
  `10191558a68a8c646e32c4ab0516f84ee99d127b9e6a2ea277c432c6c28b2348`.
  Validation-target deliveries and scores remain zero. It must be committed,
  pushed, tested, and remotely green before the one-shot scorer can run.

Engineering capability added: a bounded and auditable implementation now
exists for the separately authorized shared S21 validation event.

Scientific claim not established: implementation and synthetic qualification
provide no neural advantage, signal-dependence, decoding, generalization,
real-time, EEG, hardware, assistive, or clinical result.

## 2026-07-15 - Close And Park The Consumed Loop 26/31/33 Event

- Hash-only prediction-freeze commit `54bdca9` passed push CI `29425811042`
  and PR CI `29425813894` before validation targets opened.
- The isolated scorer then delivered exactly the same six S21 session-1
  validation targets once. It delivered or scored zero source-test and
  session-2 rows, made zero post-target parameter/configuration changes, and
  wrote no plaintext targets or predictions to the public result.
- The 2,908-parameter candidate reached macro sentence CER `0.938177`, corpus
  CER `0.938547`, WER `0.966667`, 0/6 exact sentences, and blank fraction
  `0.993477`. The train-only no-signal prior reached macro CER `0.751235`,
  corpus CER `0.748603`, and WER `0.833333`.
- The registered candidate-minus-prior margin was `-0.186942`: zero wins, one
  tie, five losses, one-sided exact `p = 1.0`. The primary gate failed.
- Exact-zero and timing-only controls each yielded 6/6 candidate wins and
  one-sided exact `p = 0.015625`, but row, channel, displacement, target-
  derangement, and prior components did not all pass. The intersection-union
  attribution gate failed, so no sensor-signal-dependence claim exists.
- All three scaling slopes were negative and the 8-to-55 median macro-CER gain
  was `0.289202`, but the 55-row model remained `0.186942` worse than its
  matched prior. The scaling gate failed and no universal curve or acquisition
  claim is available.
- Engineering/resource gates passed: one cache hash, 55 train signals/targets,
  six validation signals/targets, 21 fits, 5,040 optimizer steps, 24 target-
  blind inferences, six priors, 31 frozen sets, one scoring run, 184.046922
  seconds target-blind end-to-end runtime, 0.017592 seconds scoring runtime,
  532,955,136-byte maximum measured RSS, and 10,148,673 generated bytes.
- The result registry SHA-256 is
  `7577c84eaea7579250b5c1fcdf53234a3d56fdab4640df2edebaee9ae8bd31b4`.
  Loops 26/31/33 and scientific Loops 46/47 are parked. No rerun, larger-model
  escalation, post-target tuning, source-test/session-2 access, or S25 action
  is authorized. Loop 48 is next but remains `Not Started`.

Engineering capability added: one bounded, remote-green-frozen S21 validation
event can be isolated, trained, frozen, target-delivered, scored, and audited
without crossing its split, resource, or post-target firewalls.

Scientific claim not established: the candidate lost to the no-signal prior,
so this event establishes no neural advantage, sensor-signal dependence,
brain-specific origin, transfer, real-time, portable-hardware, or clinical result.

- Closeout verification passes 70 focused result/roadmap tests; 748 fully
  provisioned unittests with three expected skips versus the 744/3 pre-change
  baseline; and 701 dependency-light tests with 142 expected optional skips.
  Final static, CLI, workbook, and secret-scan gates passed. Closeout commit
  `f407ffb` passed push CI `29428087084` and PR CI `29428091698`.

## 2026-07-15 - Loop 48 Artifact-Only Failure Localization Preregistration

- Audited only four committed aggregate JSON artifacts from the consumed
  Loop 26/31/33 result. No cache, derivative, checkpoint, private prediction,
  target bundle, raw FIF/MAT, source-test row, session 2, S7, S20, or S25
  payload was read.
- Reproduced the public failure signature: primary blank fraction `0.993477`,
  primary macro sentence CER `0.938177` versus prior `0.751235`, all-condition
  blank range `0.997146`, all six prefix groups above `0.25` three-seed blank
  dispersion, and all three size-55 seeds worse than the no-signal prior.
- Registered `F5` model-fit/output-distribution instability as the leading
  observable phenotype, not a proven root cause. The contract records the
  missing optimization, CTC-feasibility, train-only decoding, signal-quality,
  timing, and representation-comparison evidence instead of guessing.
- Frozen eight ordered failure classes, 17 unavailable evidence fields, 30
  refusals, four exact artifact identities, and one future artifact-only Stage
  A capped at one thread, 30 seconds, 256 MiB RSS, and 1 MiB output.
- Kept every authorization flag false. No Loop 48 implementation, generated
  diagnostic report, model run, training run, target read, protected data read,
  download, network call, stream, device, or hardware operation occurred.
- Updated and visually verified the ten-sheet tracker using the bundled
  spreadsheet runtime. The workbook grew from 115,442 to 116,124 bytes and is
  SHA-256 `3f5a2d70ff654b0eb56fc04cbed3153139816b4681b8d164a8f6292d6a427753`;
  all ten sheets rendered, the formula-error scan found zero matches, and ZIP
  integrity passed. The full render/export took 17.42 seconds and briefly
  reached 2,352,807,936-byte process RSS, so no further full render was used.
  The adjacent user-owned sidecar remained untracked and byte-identical at
  SHA-256 `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.
- Local acceptance passes 25 focused Loop 48/roadmap tests in 0.009 seconds;
  762 fully provisioned tests with three expected skips in 24.742 seconds and
  624,001,024-byte process maximum RSS, versus the 748/3 pre-change baseline;
  and 715 dependency-light tests with 142 expected optional skips in 1.240
  seconds and 118,374,400-byte process maximum RSS, versus the 701/142
  baseline. Ruff lint, changed-test formatting, compileall, every registry
  JSON, CLI help, `git diff --check`, workbook render/formula/ZIP checks, and
  the contract hash binding pass. An accidental Apple Python 3.9 invocation
  failed collection because it lacked `PYTHONPATH`, `tomllib`, and modern type
  syntax; the supported Python 3.13 dependency-light command passed unchanged.

Engineering capability proposed: one exact artifact-only discrepancy tree can
make the consumed negative result mechanically classifiable without reopening
protected data.

Scientific claim not established: the planning result does not prove why the
model failed or establish neural advantage, signal dependence, decoding,
generalization, real-time behavior, EEG performance, portable/home hardware,
or clinical utility.

## 2026-07-15 - Loop 48 Stage A Authorization Request

- Bound the request to green contract commit `83309bf`, push CI
  `29431318268`, PR CI `29431347801`, the exact contract/research/test hashes,
  and the four exact committed input identities totaling 155,545 bytes.
- Requested only a dependency-light analyzer plus one future aggregate Stage A
  under one thread, one worker, 30 seconds, 256 MiB RSS, and 1 MiB output.
- Kept all 18 `authorized_now` fields and 19 current runtime/access counters at
  zero or false. No implementation, runtime input read, report, model,
  training, target, protected payload, download, stream, device, or hardware
  operation occurred.
- Added ten request invariants; the combined Loop 48 request, contract, and
  roadmap suite passes 35 tests.

Engineering capability proposed: a separately reviewable permission gate now
binds the exact artifact-only runtime before any implementation or execution.

Scientific claim not established: preparing the request creates no new
evidence and does not establish a root cause, neural advantage, decoding,
generalization, real-time behavior, EEG result, portable/home hardware, or
clinical utility.

## 2026-07-15 - Loop 48 Multi-Hypothesis Stage B Design

- Replaced the implicit single-cause framing with five potentially coexisting
  hypotheses: CTC fit, sensor quality, timing/preprocessing, representation
  separability, and prior dominance.
- Designed one shared train-only evidence bundle spanning ten measurement
  families and explicit support-for, support-against, missing, conflicting,
  and next-falsifier fields for every hypothesis.
- Defined parallel scientific evaluation with sequential one-thread compute so
  evidence is reused without concurrent workloads or repeated prediction sets.
- Kept Stage B entirely outside the Stage A request. Exact train-only splits,
  thresholds, seeds, model inventory, and resource caps remain unfrozen; all 11
  authorization fields and 12 access counters remain false or zero.
- Added eight dependency-light portfolio invariants; the combined Loop 48
  request, portfolio, contract, and roadmap suite passes 43 tests.
- Updated the tracker to the exact Stage A decision and H1-H5 portfolio. The
  116,641-byte workbook is SHA-256
  `2d7d3c7b87aa58c9cb43d9b2ca39a360489b2b252944407a0fc3d602ffd81c7e`;
  focused dashboard/decision/scientific-roadmap renders are readable, the
  formula scan found zero errors, and ZIP integrity passed. The isolated
  renderer took 86.88 seconds and peaked at 840,777,728-byte RSS. The adjacent
  user-owned sidecar remains untracked and byte-identical at SHA-256
  `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.
- Local acceptance passes 43 focused request/portfolio/contract/roadmap tests
  and 733 dependency-light tests with 142 expected optional skips. Ruff,
  formatting, all registry JSON, workbook formula/render/ZIP checks, and
  `git diff --check` pass. The fully provisioned suite discovered 780 tests;
  779 reached expected outcomes, while the pre-existing Loop 24 isolated timing
  test exceeded its hard five-second worker timeout under heavy host CPU
  contention. An isolated rerun failed for the same measured timing reason.
  The previously committed 762-test suite was green before these 18 pure
  request/portfolio tests were added, and all 18 new tests pass focused. No
  timeout, threshold, or experiment code was changed; remote CI is the required
  clean-host full-suite gate for this milestone.
- Request/portfolio commit `0ffdf47` then passed push CI `29433294092` and PR
  CI `29433297546`. Each clean-host run passed 733 dependency-light tests with
  142 expected skips and 765 optional-neuro tests with 22 expected skips, plus
  Ruff. This closes the clean-host qualification gap without erasing the local
  780-test lane's measured Loop 24 timing timeout under host contention.

Engineering capability proposed: a future shared telemetry pass can test
several failure mechanisms efficiently without reusing consumed validation.

Scientific claim not established: the design confirms none of the five
hypotheses and adds no neural, decoding, generalization, real-time, EEG,
portable/home-device, or clinical evidence.

## 2026-07-15 - Loop 48 Hypothesis Discrimination Research

- Preserved the green H1-H5 portfolio and added an independent H1-H6
  discrimination map rather than rewriting historical evidence. `H1` now means
  failure of the exact 2,908-parameter, 240-step tiny CTC recipe, not failure of
  CTC generally; `H6` separately tests data quantity and unique-sentence
  diversity.
- Added orthogonal threat `T1` for peripheral/task-locked shortcut dependence.
  A future Stage B result can reach at most `E3` bounded sensor dependence and
  only if intact signal clears every registered prior/corruption by both a
  preregistered practical margin and paired uncertainty gate. Brain-specific
  origin remains behind the separate Loop 35 firewall.
- Bound six coexisting hypotheses to six shared sequential evidence stages,
  five evidence levels, five non-identifiability rules, seven deliberately
  unfrozen Stage B fields, five public primary-source bindings, 15 false
  authorization fields, one thread, one worker, and one numerical job.
- Read five public sources and produced a 12,215-byte research note plus a
  12,053-byte registry. Protected cache/array, signal, target, fixture, split,
  model, training, prediction, checkpoint, scoring, download, stream, device,
  and hardware counters all remained zero.
- Added ten dependency-light invariants. The combined Loop 48 and scientific
  roadmap surface passes 53 focused tests. The full dependency-light suite
  passes 743 tests with 142 expected skips, versus the 733/142 pre-change
  baseline; measured final-tree local runtime was 3.32 seconds with 112,672,768-byte
  maximum RSS.
- Commit `33a14d8` passed push CI `29436731383` and PR CI `29436735374`. Each
  clean host passed Ruff, 743 dependency-light tests with 142 expected skips,
  and 775 optional-neuro tests with 22 expected skips.
- Updated the ten-sheet tracker with dashboard scope, decision `48-R4`, the
  Loops 25-44 summary, and the scientific Loop 48 row. The workbook grew from
  116,641 to 117,184 bytes and is SHA-256
  `9a25c0eef4557618d3639c74549b30ace0c352cc559f45de9c73a0dbda3f33ec`.
  Changed ranges rendered cleanly after two targeted row-height repairs, the
  formula scan found zero errors, and ZIP integrity passed. The artifact-tool
  export took 11.53 seconds and peaked at 1,496,907,776-byte RSS, so the pass
  deliberately avoided a new full-workbook render. The adjacent user-owned
  sidecar remained untracked and byte-identical at SHA-256
  `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.
- Ruff lint, changed-test formatting, compileall, every registry JSON, CLI help,
  `git diff --check`, workbook value inspection, focused renders,
  formula-error scan, ZIP integrity, and staged secret scanning passed.

Engineering capability proposed: a future one-pass train-only diagnostic can
compare six plausible failure mechanisms while retaining conflicts, resource
limits, uncertainty, and claim ceilings.

Scientific claim not established: no hypothesis was tested or confirmed, no
new neural evidence was created, and neural advantage, useful decoding,
brain-specific origin, generalization, real-time behavior, EEG portability,
home use, and clinical utility remain unestablished.

## 2026-07-15 - Loop 48 Artifact-Only Stage A Result

- Recorded the user's exact bounded permission in a separate authorization-only
  milestone. Commit `5bae880` passed push CI `29442914090` and PR CI
  `29442916230` before implementation began.
- Added the dependency-light Loop 48 analyzer, strict path and hash checks,
  ordered eight-class decision tree, bounded JSON writer, two CLI commands, and
  15 synthetic-only tests. Implementation commit `ca21539` passed push CI
  `29444008688` and PR CI `29444012075` before registered inputs opened.
- Executed Stage A exactly once. Four committed aggregate JSON artifacts
  totaling 155,545 bytes passed SHA-256 verification. The run read no ignored
  Loop 26 output, arrays, targets, checkpoints, private predictions, source
  test, session 2, S7, S20, S25, FIF, or MAT payloads.
- Reproduced the primary blank fraction `0.9934773746432939`, all six
  fixed-prefix blank ranges, and all three size-55 seeds losing to the
  train-only prior. The ordered tree selected descriptive `F5`
  output-distribution instability; root cause remains unresolved.
- Internal runtime was `0.016568875` seconds, external wall time was 0.38
  seconds, internal/external peak RSS was 23,429,120/23,560,192 bytes, and the
  report was 10,643 bytes. Model inference, training, parameter updates,
  downloads, network, stream, device, hardware, and scientific claim upgrades
  were all zero.
- Bound the result to SHA-256
  `dbfb4c7cc6163ff31fa216c1b33e7510a87b0b843ef714754037d37275924659`
  and marked Stage A consumed with no rerun or post-result tuning authorized.
- Updated the ten-sheet tracker dashboard, roadmap summaries, scientific Loop
  48 row, and decision `48-R5`. The 117,187-byte workbook has SHA-256
  `7e6424cd5f69d29f78ea7335d1cf277d293eeac4071668991f66d37d7679d4c3`;
  all ten post-edit renders, focused crops, formula scan, and ZIP integrity
  passed. The final artifact-tool pass took 11.04 seconds and peaked at
  1,572,667,392 bytes RSS, so future updates should avoid unnecessary full
  workbook imports. The adjacent user-owned inspection sidecar was not read,
  modified, staged, or committed.
- Local acceptance passes 86 focused Loop 48/roadmap tests, 776
  dependency-light tests with 142 expected skips, and 823 optional-neuro tests
  with 3 expected skips. The full runs took 2.338/34.585 seconds and peaked at
  104,415,232/607,223,808 bytes RSS. Ruff lint and changed-file formatting pass.
  Repository-wide formatting still reports 106 historical files, which this
  closeout deliberately leaves untouched.
- Closeout commit `6322635` passed push CI `29446438743` and PR CI
  `29446440355`; both clean-host jobs were green.

Engineering capability added: one hash-bound aggregate analyzer can reproduce
the registered failure phenotype under strict resource and access limits.

Scientific claim not established: this result does not identify a causal root
cause or establish neural advantage, decoding utility, generalization,
real-time behavior, EEG portability, device performance, or clinical value.

## 2026-07-15 - Draft Tiered Research Autonomy

- Documented why the current gates exist: machine-safety controls protect
  storage, CPU, background processes, unrelated projects, and destructive
  operations; scientific controls protect sealed targets, consumed evaluations,
  frozen protocols, and honest claims.
- Proposed Tier A autonomous routine work and Tier B bounded development work
  under one thread, one worker, one numerical job, 1 GiB RSS, and 32 MiB output.
  An already-authorized development partition can move through later Tier B
  loops without another permission message when every split, metric, seed,
  threshold, stop rule, cap, and claim ceiling is frozen first.
- Retained one exact Tier C stop for new real payloads, final or unseen-person
  targets, consumed-evaluation reuse, post-outcome protocol changes, downloads,
  hardware or participant recording, destructive operations, releases, and
  claim promotion.
- Kept the charter explicitly inactive. Its exact standing approval is
  prospective and cannot reopen Loop 48 Stage B, RW3, S25, or another consumed
  or independently gated experiment.
- Added five dependency-light invariants. The final branch-level local suites
  pass 781 tests with 142 expected skips and 828 optional-neuro tests with 3
  expected skips. Runtime was 1.318/26.177 seconds and maximum RSS was
  110,821,376/611,926,016 bytes.

Engineering capability proposed: one standing decision can remove repeated
permission stops from reversible routine and bounded development work.

Scientific claim not established: the draft authorizes nothing and creates no
new neural, decoding, generalization, real-time, EEG, device, or clinical
evidence.

## 2026-07-15 - Loop 48 Stage B Train-Only Preregistration

- Advanced the additive six-hypothesis design into one exact, machine-readable
  protocol over the existing S21 session-1 source-train partition. No cache
  member, signal, target, checkpoint, private prediction, model, or ignored
  experiment artifact was read.
- Corrected the scientific ceiling after auditing historical use: every one of
  the 55 source-train rows contributed to prior Loop 26 fits, so a new 44/11
  split is prospective only within this execution and can reach at most E2
  pipeline-discriminative evidence.
- Froze target-independent row assignment; prefixes `8, 16, 24, 32, 44`;
  seeds `4801-4803`; the exact 2,908/2,884-parameter models; 20 fits; 35 model
  inferences; five priors; 41 prediction sets; 4,800 optimizer steps; and one
  post-green-freeze 11-target score using all 2,048 paired sign assignments.
- Separated the seven-comparator candidate corruption conjunction from a
  six-set candidate/linear prior rule. The latter cannot imply uncomputed
  linear corruption controls or a task-locked character probe.
- Retained one thread, one worker, one numerical job, 1 GiB RSS, 32 MiB output,
  a 20 GiB free-disk floor, and zero downloads. Current free disk was 39 GiB.
- Updated the Markdown tracker, machine roadmap, README, start-here guide,
  handoff, agent boundary, decision journal, and this build journal. The tracked
  workbook was deliberately not reopened: its last required artifact-tool pass
  measured 1,572,667,392-byte RSS, above this protocol's 1 GiB envelope. The
  adjacent user-owned inspection sidecar remained unread and untouched.
- Local acceptance passes 100 focused Loop 48/roadmap tests, 795 dependency-
  light tests with 142 expected skips, and 842 optional-neuro tests with 3
  expected skips. The complete runs took 1.64/27.55 seconds wall time and
  peaked at 90,767,360/609,239,040 bytes RSS. The 781/828 pre-change baselines
  therefore gain exactly 14 invariants without losing a prior test.
- A separate probe with macOS system Python 3.9 was rejected as outside the
  declared Python `>=3.10` range: it collected 777 tests but produced 22
  version-caused errors (`zip(strict=...)`, `tomllib`, and modern union syntax)
  with 141 skips. It is not counted as a project regression or qualification
  result, and no compatibility code was changed in response.

Engineering capability preregistered: one bounded, prediction-frozen protocol
can test six competing pipeline-failure explanations before a new acquisition.

Scientific claim not established: no Stage B execution or result exists, and
there is no new neural advantage, independent validation, brain-origin,
decoding, generalization, real-time, EEG, home-device, assistive, or clinical
evidence.

## 2026-07-15 - Loop 48 Stage B Authorization Request

- Verified preregistration commit
  `0ee0ab7cd3abae4ce654af9954854a6e236c8a0e` as green on push CI
  `29452286159` and PR CI `29452288520`; Base Python and Optional Neuro Readers
  passed in both workflows.
- Added one plain-language packet and one machine request bound to the immutable
  preregistration, contract, and invariant-test byte counts, SHA-256 hashes,
  Git blob identities, operation inventory, resource caps, access order, exact
  sentence, and E2 claim ceiling.
- Kept every authorization field false. Request preparation read no cache stat,
  hash, member, ignored file, signal, target, checkpoint, private prediction,
  or experiment artifact and ran no model, training, inference, or scoring
  operation.
- Added 12 dependency-light request invariants and updated the README,
  start-here guide, scientific roadmap, Markdown tracker, handoff, machine
  roadmap, agent boundary, decision journal, and this build journal. The
  tracked workbook and adjacent user-owned inspection sidecar remained
  unopened and unchanged.
- Local acceptance passes 112 focused Loop 48/roadmap tests, 807 dependency-
  light tests with 142 expected skips, and 854 optional-neuro tests with 3
  expected skips. The complete runs took 1.99/27.59 seconds wall time and
  peaked at 83,935,232/616,579,072 bytes RSS. The green preregistration
  baseline of 795/842 therefore gains exactly 12 request invariants without
  losing a prior test.

Engineering capability prepared: one exact decision surface can authorize the
smallest registered experiment that distinguishes six pipeline-failure
hypotheses without silently widening data, compute, or claims.

Scientific claim not established: an authorization request is not an
experiment, and no new neural, decoding, independent-validation,
generalization, real-time, EEG, device, assistive, or clinical evidence exists.

## 2026-07-15 - Loop 49 Development-Person Metadata Research

- Added `docs/LOOP_49_PRIMARY_SOURCE_RESEARCH.md`,
  `registries/loop49_research_boundary.v0.json`, and 17 dependency-light
  invariants. The machine boundary contains 25 false authorization fields and
  zero S24 path-stat, payload, header, signal, MAT, target, source-hash,
  derivative, model, training, prediction, or scoring operations.
- Selected S24 session 2 block 2 as the preferred future permanently
  development-only MEG participant from pinned public metadata. The exact FIF
  and MAT paths total 1,048,579,727 bytes, 293,597,553 bytes below the 1.25 GiB
  cap and 8,951,420,273 bytes below the user's remaining 10 GB cumulative
  envelope if both files are absent.
- Preferred S24 over the 29,701,559-byte-smaller S18 bundle because S18 carries
  the published S1/S18 alias. Preserved S25 as final-only, S23 as officially
  excluded, S21 as the observed source, S7 as consumed EEG, and S20 as a
  separate accessible-EEG lane. No backup substitution is automatic.
- Froze a research recommendation, not an executable contract: require at
  least 48 usable unique canonical sentence groups, reserve 16 salt-hash-ordered
  groups for development selection, assign the remainder to fit, and exclude
  every matching S21 source-train selection text from future fit. Emit no
  plaintext or raw sentence hashes. S24 can never become independent or final
  evidence after protected access.
- Bound the reasoning to the official Brain2Qwerty v2 paper, the official
  SpanishBCBL card and pinned revision, the official loader and Hub API, the v1
  primary paper, and primary model-selection/small-sample methodology papers.
  The key design consequences are cross-person development before final test,
  text-group splitting across people, a one-time final-person evaluation, and
  no power claim from a 48-row pragmatic floor.
- The metadata-only pass returned 396 rows in 3.51 seconds at 62,685,184-byte
  peak RSS under one thread and one worker. Exact wire bytes and transport-level
  request count are unavailable from the high-level Hub API. Payload download
  bytes were zero. Free disk before documentation was 42,255,929,344 bytes.
- Updated the scientific roadmap, machine roadmap, Markdown tracker, README,
  start-here guide, handoff, agent boundary, decision journal, and this build
  journal. The tracked workbook was deliberately not reopened because its last
  artifact-tool pass measured 1,572,667,392-byte peak RSS. The adjacent
  user-owned inspection sidecar remained unread and untouched.
- The three new core artifacts total 59,891 bytes, well below the 8 MiB
  planning-artifact cap. The isolated optional-reader setup left the shared
  `uv` cache at an apparent 1.0 GB and free disk at approximately 39.0 GiB; it
  created no project `.venv`, dataset payload, model, or experiment artifact.
- Focused Loop 49 plus scientific-roadmap acceptance passes 28 tests in 0.003
  seconds. The complete dependency-light suite passes 824 tests with 142
  expected skips in 1.91 seconds wall time at 115,032,064-byte maximum RSS,
  exactly 17 tests above the 807-test pre-change baseline with the same skip
  count. A Python 3.12 CI-shaped optional-neuro run passes 856 tests with 22
  expected skips in 36.12 seconds at 290,406,400-byte maximum RSS; its focused
  signal-quality cell passes 9 tests in 25.77 seconds at 210,026,496 bytes.
- One first optional command used `uv --extra neuro`, which unexpectedly tried
  to resolve the repository's `all` extra across Python 3.10 and stopped before
  tests at the known Zarr/Python compatibility boundary. The corrected
  `--no-project` command installed only MNE, SciPy, NumPy, pytest, and Ruff on
  Python 3.12. This was a harness-resolution failure, not a test failure or code
  change.
- Ruff lint and changed-test formatting pass. Compileall, all 49 registry JSON
  files, root and two CI CLI-help surfaces, and `git diff --check` pass. Remote
  qualification also passes: milestone commit
  `5afa61e3dad72e671f4c829187e593560a157f67` passed push CI `29454969710` and
  pull-request #27 CI `29455166081`, with Base Python and Optional Neuro Readers
  green in both workflows.

Engineering capability added: one exact, storage-bounded, identity-aware
metadata boundary now preserves separate development-person and final-person
roles before any S24 payload opens.

Scientific claim not established: no S24 payload, trial, target, signal, model,
training, decoding, unseen-person, real-time, EEG, device, assistive, or clinical
result exists from this planning pass.

## 2026-07-15 - Loop 50 Multi-Source Encoder Planning Research

- Added `docs/LOOP_50_PRIMARY_SOURCE_RESEARCH.md`,
  `registries/loop50_research_boundary.v0.json`, and 17 dependency-light
  invariants. The machine boundary contains 31 false authorization fields, 30
  refusal IDs, and zero protected data, model, training, inference, prediction,
  scoring, download, stream, device, or hardware operations.
- Bound the design to six primary sources: Brain2Qwerty v2 joint training and
  text-level hash splitting, the official SpanishBCBL identity/license record,
  participant-leakage evidence, worst-group methodology, small-sample
  uncertainty, and model-selection bias.
- Froze a research recommendation, not an executable protocol: one global
  canonical-text firewall, five historical S21 out-of-fold folds, 16 future
  S24 selection groups plus at least 32 fit groups, equal `0.5/0.5`
  participant loss, one shared causal candidate family, ten fixed conditions,
  primary seed 5001, stability seeds 5002/5003, an exact 20-parameter-update
  inventory, and a both-person/worst-person pass rule. The inventory uses five
  pooled out-of-fold fits, three pooled final fits, six linear fits, and six
  S21-only fits; its four-run cap margin is not rerun permission.
- Added a six-route Loop 48 Stage B outcome table. Mechanics, timing, plateau,
  and unresolved outcomes park S24; only a viable registered probe or stable
  non-saturation result can make a separately gated S24 intake eligible. A
  route is never acquisition authorization.
- Preserved strict future zero-shot compatibility: no participant-specific
  scaler, target-corpus normalization, participant embedding/affine/adapter,
  LLM, n-gram, semantic target, best-seed selection, pooled rescue, or S25 use.
- Updated the scientific roadmap, machine roadmap, Markdown tracker, README,
  start-here guide, handoff, agent boundary, decision journal, and this build
  journal. The tracked workbook and adjacent user-owned inspection sidecar were
  not opened or changed.
- The three new core artifacts total 66,845 bytes under the 8 MiB planning cap.
  No project `.venv`, protected payload, model, prediction, experiment output,
  or persistent process was created. Free disk remained approximately 39 GiB.
- Focused Loop 49/50 plus scientific-roadmap acceptance passes 45 tests in
  0.004 seconds. The complete dependency-light suite passes 841 tests with 142
  expected skips in 1.53 seconds wall time at 120,537,088-byte maximum RSS,
  exactly 17 tests above the 824-test pre-change baseline with the same skip
  count. The Python 3.12 optional-neuro suite passes 873 tests with 22 expected
  skips in 10.47 seconds at 240,304,128-byte maximum RSS, exactly 17 tests above
  the 856-test baseline; focused signal quality passes 9 tests in 4.12 seconds
  at 159,252,480 bytes.
- Ruff lint and changed-test formatting pass. Compileall, all 50 registry JSON
  files, root and two CI CLI-help surfaces, and `git diff --check` pass. A
  repository-wide formatter check would rewrite 104 pre-existing files under
  the current Ruff formatter, so it was deliberately scoped to the new test to
  avoid unrelated churn.
- Remote qualification passes for milestone commit
  `085f341941006383f859804caad4e2ffc50c1737`: push CI `29458102674` and PR #28
  CI `29458116994` both passed Base Python and Optional Neuro Readers. The only
  annotations were GitHub-hosted runner notices that Node.js 20 actions are
  being forced to Node.js 24; no repository test or lint warning occurred.

Engineering capability added: one machine-checkable design now specifies how a
future two-person tiny causal experiment must prevent text leakage, participant
shortcuts, row-count imbalance, pooled-average masking, seed selection, and
target-corpus normalization.

Scientific claim not established: no S24 payload or target was opened and no
model ran, so there is no new neural advantage, sensor-signal dependence,
brain-specific origin, decoding, unseen-person, real-time, EEG, home-device,
assistive, diagnostic, or clinical evidence.

## 2026-07-15 - Research Autonomy Charter Activation

- Recorded the maintainer's exact charter approval in
  `docs/RESEARCH_AUTONOMY_CHARTER_DECISION.md` and
  `registries/research_autonomy_charter_decision.v0.json`. The approved source
  remains byte-identical at commit `df9035a`, SHA-256
  `c9381bfc729dfca4aaab03929a6623f23c3cf06eb33fbae5379b0517981dcb64`.
- Activated Tier A routine work and Tier B fully frozen bounded development
  experiments, including autonomous commits, pushes, and CI checks, effective
  only after this decision commit is remotely green.
- Preserved every Tier C stop for irreversible evidence, real-data acquisition,
  sealed/final targets, consumed-evaluation reuse, hardware, destructive work,
  release, and claim promotion. The charter is prospective and does not itself
  authorize Loop 48 Stage B, RW3, S25, or any existing closed contract.
- Authorization-only access counters remain zero: no protected payload, target,
  model, training, inference, download, stream, device, hardware, destructive,
  release, or claim-promotion operation occurred.
- Added nine decision invariants. The three new core artifacts total 16,449
  bytes. Focused charter/Loop 50 acceptance passes 31 tests in 0.004 seconds;
  the complete dependency-light suite passes 850 tests with 142 expected skips
  in 1.92 seconds at 121,503,744-byte maximum RSS, and the optional-neuro suite
  passes 882 tests with 22 expected skips in 10.56 seconds at 227,950,592-byte
  maximum RSS. Both suites are exactly nine tests above the Loop 50 baseline.

Engineering capability authorized: routine research engineering and fully
frozen bounded development experiments may advance autonomously through local
verification, commits, pushes, and remote CI.

Scientific claim not established: this governance decision is not an
experiment and establishes no neural advantage, decoding accuracy,
sensor-signal dependence, brain-specific origin, generalization, real-time,
EEG, device, assistive, diagnostic, or clinical result.

## 2026-07-15 - Loop 48 Stage B Authorization Decision

- Recorded the maintainer's exact one-run sentence in
  `docs/LOOP_48_STAGE_B_AUTHORIZATION_DECISION.md` and
  `registries/loop48_stage_b_authorization_decision.v0.json`, binding the green
  preregistration, immutable request, exact hashes, operation counts, resources,
  access order, and E2 ceiling.
- Authorized the exact implementation and one registered execution only after
  this authorization-only commit is remotely green. Protected input remains
  closed during implementation and synthetic tests; the 11 check targets stay
  sealed until a later plaintext-free prediction-freeze commit is remotely
  green.
- Kept validation, source test, session 2, S7/S20/S25, raw FIF/MAT, downloads,
  larger or additional models, restarts, language models, NeuroTokens, RW3,
  streams, devices, hardware, post-check tuning, claim promotion beyond E2, and
  reruns closed.
- Authorization-only counters remain zero. No protected path, cache member,
  signal, target, derivative, model, training, inference, prediction, score,
  download, stream, device, or hardware operation occurred.
- Added nine decision invariants. The three new core artifacts total 27,098
  bytes. Focused Stage B contract/request/decision plus charter acceptance
  passes 44 tests in 0.007 seconds. The complete dependency-light suite passes
  859 tests with 142 expected skips in 1.88 seconds at 117,407,744-byte maximum
  RSS; the optional-neuro suite passes 891 tests with 22 expected skips in 10.36
  seconds at 241,254,400-byte maximum RSS. Both are exactly nine tests above
  the charter-decision baseline.

Engineering capability authorized for testing: one exact, hash-bound,
resource-bounded Stage B implementation and one registered train-only
failure-discrimination execution may proceed through three ordered green gates.

Scientific claim not established: this decision is not a result, and even a
later clean Stage B run cannot establish independent validation, neural
advantage, brain-specific origin, useful decoding, unseen-person
generalization, causal preprocessing, real-time behavior, EEG or device
performance, assistive value, diagnostic value, or clinical utility.

## 2026-07-15 - Loop 48 Stage B Train-Only Failure Discrimination

- Implemented the exact frozen Stage B boundary at commit `1d840e3`. The
  bounded archive reader, deterministic 44/11 source-train split, transforms,
  tiny causal and linear probes, five priors, registered controls, hash-only
  prediction freezer, isolated scorer, five CLI stages, and synthetic tests
  passed push CI `29461579009` and PR CI `29461580293` before protected access.
- The static gate passed at 41,714,499,584 free bytes in 0.956671 seconds with
  209,305,600-byte peak RSS. It delivered no signal or target rows and
  performed no source-cache hash pass.
- The isolated derivative stage performed the one authorized SHA-256 pass over
  the exact 10,632,576-byte S21 session-1 sentence cache. It delivered 44 fit
  signal/target rows and 11 check signal rows, while delivering zero check,
  validation, source-test, or session-2 targets. The 7,084,125-byte fit bundle
  and 1,750,971-byte target-free check bundle were created in 0.599360 seconds
  at 150,568,960-byte peak RSS.
- The one target-blind execution completed 15 causal fits, three linear fits,
  two control fits, 4,800 optimizer steps, 35 model-inference runs, five
  train-only prior fits, and 41 private prediction sets. It took 188.584455
  seconds for the target-blind stage and 190.140486 cumulative seconds through
  freeze, peaking at 483,540,992 bytes RSS. Check-target deliveries and scores
  remained zero.
- Hash-only freeze commit `00215b1` bound all 20 fit telemetry bundles and 41
  private prediction sets without plaintext predictions or targets. Push CI
  `29461934145` and PR CI `29461935560` were both green before the same 11
  train-check targets opened once for one 0.112110-second scoring event. No
  post-check parameter update, configuration change, or rerun occurred.
- The consumed machine result is
  `registries/loop48_train_only_discrimination_result.v0.json`, SHA-256
  `ef8290eb45e755bedb2deed781e6e472aa3621c25d91a01d01626c17c96ce891`,
  with readable closeout in `docs/LOOP_48_STAGE_B_RESULT.md`. The primary
  causal candidate reached macro CER `0.953566` versus `0.822045` for its
  matched train-only prior, a `-0.131522` improvement. It won 2 of 11 rows and
  lost 9 with one-sided p-value `0.980957` over all 2,048 assignments.
- All three full-size causal and all three full-size linear fits were finite and
  stable, but none cleared the registered prior rule. This supports `H4`,
  stable but nonseparable representation, for this transformed historical
  source-train slice and fixed probe family. No registered `-50/-25/+25/+50`
  shift improved all three seeds, providing evidence against fixed-offset
  `H3`. `H1`, `H2`, `H5`, and `H6` remain unresolved.
- The primary beat exact-zero and timing-only components on 11/11 rows at
  one-sided p-value `0.000488`, and beat the severe `+100` displacement on six
  rows with five ties at p-value `0.015625`. These isolated diagnostics cannot
  rescue the failed no-signal-prior and complete corrupted-signal conjunction;
  sensor-signal dependence remains unavailable.
- The frozen Loop 50 router selects `L50-R05`: park S24 acquisition for this
  model family. S24 remains metadata-only and unopened; S25 remains sealed and
  final-only. The next reversible work is Tier A representation-repair research
  and contract design. Any real post-outcome model operation, protected-data
  repair run, new participant acquisition, or sealed-target event remains Tier
  C and requires a separate exact maintainer decision.
- Total generated execution artifacts were 9,623,773 bytes under the 32 MiB
  cap, maximum RSS was 483,540,992 bytes under the 1 GiB cap, and the run used
  one thread and one worker. There were zero downloads, raw FIF/MAT reads,
  validation or test reads, language-model, NeuroToken, RW3, stream, device, or
  hardware operations. The model has two frames of left context and zero right
  context, but the upstream cache is offline/noncausal and end-to-end latency
  was not measured.
- Local closeout acceptance passes 63 focused Stage B tests in 6.758 seconds
  internal time and 7.39 seconds wall time at 316,719,104-byte maximum RSS. The
  complete dependency-light suite passes 887 tests with 149 expected skips in
  1.377 seconds internal time and 1.63 seconds wall time at 124,157,952-byte
  maximum RSS. The complete optional-neuro suite passes 934 tests with 3
  expected skips in 29.827 seconds internal time and 30.79 seconds wall time at
  609,648,640-byte maximum RSS. Both complete suites add exactly nine tests over
  their 878/925-test implementation baselines without losing a prior test.
- Ruff lint and scoped changed-test formatting pass. Compileall, all 54 registry
  JSON files, five Stage B CLI-help surfaces, strict prediction-freeze
  inspection, and `git diff --check` pass. Freeze inspection confirms 20 fit
  telemetry bundles, 41 prediction sets, zero check-target delivery, and zero
  score at the committed pre-target boundary. None of these closeout checks
  reran a scientific fit, inference, prediction, target delivery, or score.
- Result closeout commit `ad4410cfe41ba250c737c6345c83098906029479`
  passed push CI `29464527230` and PR CI `29464529524`. Base Python and Optional
  Neuro Readers were green in both workflows; the only annotations were
  GitHub-hosted runner notices that Node.js 20 actions are being forced to
  Node.js 24, not repository test or lint failures.
- Updated the README, start-here guide, Markdown tracker, scientific roadmap,
  machine roadmap, handoff, agent boundary, decision journal, start prompt, and
  this build journal. The tracked workbook remains the last reviewed Stage A
  visual snapshot because its prior import reached 1,572,667,392-byte peak RSS;
  its adjacent user-owned inspection sidecar was not opened, modified, staged,
  or committed.

Engineering capability added: NeuroDecodeKit now has a one-shot,
target-firewalled train-only failure-discrimination path with exact provenance,
resource accounting, hypothesis decisions, and a remotely green prediction
freeze.

Scientific claim not established: the run did not show neural advantage,
brain-specific decoding, independent generalization, real-time performance, or
portable/home EEG performance.

## 2026-07-15 - Loop 48 Stage C Temporal-Representation Repair Research

- Audited the failed `TinyCausalSentenceCTC-v0` architecture against the
  consumed Stage B aggregate result and the existing Loop 10 CTC geometry
  report without opening any protected cache, target, checkpoint, private
  prediction, S24 path, or S25 path. The failed candidate has only 20 ms of
  learned left context; raw quality and retained neural information remain
  unavailable.
- Added primary-source-informed Stage C research and a strict machine boundary.
  The selected `R1` hypothesis compares one 7,692-parameter causal candidate
  with 470 ms left context against one 7,568-parameter zero-context ablation on
  the same 25 Hz output grid. The 124-parameter gap is 1.612070% of the
  candidate. No model was implemented or run in this milestone.
- Froze a Tier A synthetic-only calibration path before implementation results:
  seed 4850, 40 rows, a 24/8/8 split, three candidate recipes, one ablation fit,
  four total parameter-update runs, at most 1,800 optimizer steps, 600 seconds,
  1 GiB peak RSS, 16 MiB generated output, one CPU thread, one worker, and zero
  real-data downloads. A protected diagnostic remains unpreregistered and
  unauthorized.
- Updated the README, start-here guide, agent boundary, Markdown tracker,
  machine roadmap, scientific roadmap, handoff, decision journal, and start
  prompt. The 117,187-byte workbook remains the last reviewed Stage A visual
  snapshot because its prior full import reached 1.57 GiB RSS; the adjacent
  user-owned inspection sidecar was not read, modified, staged, or committed.
- Focused Stage C/roadmap/legacy Loop 48 acceptance passes 52 tests in 0.018
  seconds. The complete dependency-light suite passes 897 tests with 149
  expected skips in 1.310 seconds internal time and 1.56 seconds wall time at
  126,533,632-byte external maximum RSS. The complete optional-neuro suite
  passes 944 tests with 3 expected skips in 29.221 seconds internal time; its
  observed in-suite peak RSS was 598,966,272 bytes. Both suites add exactly ten
  tests over the 887/934 Stage B baseline without losing a prior test.

Engineering capability added: NeuroDecodeKit now has an exact, parameter-
controlled causal temporal-representation hypothesis and a bounded synthetic
calibration decision surface ready for implementation.

Scientific claim not established: no model was implemented or run and no real
signal or target was opened, so neural advantage, sensor-signal dependence,
brain-specific origin, decoding improvement, generalization, real-time
performance, and portable or home EEG performance remain unestablished.

## 2026-07-15 - Loop 48 Stage C Synthetic Implementation

- Implemented the exact 7,692-parameter causal candidate and 7,568-parameter
  zero-context ablation with fixed 100-to-25 Hz geometry, numeric-only NPZ
  checkpoints, strict payload hashes, and optional NumPy/Torch imports.
- Added the exact seed-4850 synthetic fixture: 40 unique 102-channel rows in a
  24/8/8 split, 3,996 valid source samples, 999 valid output steps, 1,699,920
  array bytes, exact zero padding, and no file, cache, participant, or real-
  target input. Its SHA-256 is
  `0322b5d2a89c5b0bd95cd8829e0a5d463fb1c8a9da3a7aad82f6e00fd1e95537`.
- Added one refusal-first aggregate gate and two CLI surfaces. The gate freezes
  all three candidate recipes, one selected-recipe ablation, one final opening,
  bitwise checkpoint replay, eight future-mutation rows, eight prefix-resume
  rows, one thread, one worker, 1,800 steps, 600 seconds, 1 GiB RSS, 16 MiB
  generated output, and a 20 GiB free-disk floor.
- Thirteen focused tests pass in 1.331 seconds with zero parameter updates. The
  complete dependency-light suite passes 910 tests with 156 expected skips in
  1.745 seconds internal time and 1.97 seconds wall time at 121,733,120-byte
  peak RSS. The optional-neuro suite passes 957 tests with 3 expected skips in
  29.474 seconds internal time and 30.38 seconds wall time at 611,270,656-byte
  peak RSS. Both add exactly 13 tests over the 897/944 research baseline.
- Repository-wide Ruff, compileall, every registry JSON, both new CLI help
  surfaces, and `git diff --check` pass. The user-owned tracker inspection
  sidecar remains unread, unmodified, unstaged, and uncommitted.
- No synthetic training run, optimizer step, persistent generated artifact,
  real-data read, cache operation, download, S24/S25 operation, stream, device,
  hardware operation, or claim upgrade occurred. The four-fit calibration
  remains closed until this implementation commit is pushed and remotely green.

Engineering capability added: NeuroDecodeKit now implements the exact Stage C
causal temporal candidate, parameter-matched ablation, deterministic fixture,
bounded aggregate gate, safe checkpoints, and inspect CLI.

Scientific claim not established: implementation did not run the synthetic
calibration or open real signal or targets, so neural advantage, sensor-signal
dependence, brain-specific origin, decoding improvement, generalization,
real-time performance, and portable or home EEG performance remain
unestablished.

## 2026-07-15 - Loop 48 Stage C Preflight Correction

- After implementation commit `59b30a3` passed push CI `29467094688` and PR CI
  `29467095865`, the first command invocation refused during research-registry
  validation because it read `seed` instead of the frozen `fixture_seed` field.
- The refusal occurred in 0.12 seconds at 21,954,560-byte peak RSS before
  output-directory creation, fixture generation, model construction, inference,
  training, checkpoint writing, or result writing. Fixture rows, model runs,
  optimizer steps, outputs, protected reads, and downloads were all zero. The
  calibration did not start and remains unspent.
- Corrected the one field and added a regression test against the exact
  committed research registry. Fourteen focused tests pass. The corrected
  dependency-light suite passes 911 tests with 156 expected skips in 1.755
  seconds at 123,158,528-byte peak RSS; the optional-neuro suite passes 958
  tests with 3 expected skips in 29.511 seconds at 638,550,016-byte peak RSS.
- The correction must be committed, pushed, and pass fresh push and PR CI
  before the one synthetic calibration can begin. No immediate retry occurred.

## 2026-07-15 - Loop 48 Stage C Synthetic Result

- Correction commit `2836ecc` passed push CI `29467415680` and PR CI
  `29467416894` before the one synthetic calibration began. The prior preflight
  refusal remained a zero-row, zero-update event and did not consume the run.
- Executed the frozen seed-4850, 40-row, 24/8/8 gate once under one CPU thread
  and one worker. `L48C-SYN-OPT0` was selected by the unchanged selection rule.
- The 7,692-parameter temporal candidate reached final macro CER `0.433333`
  and `1/8` exact sequences. The 7,568-parameter zero-context ablation reached
  CER `1.000000` and `0/8` exact. The `0.566667` relative CER improvement
  passed, but the absolute CER `<=0.10` and exact-sequence `>=7/8` gates failed.
- Deterministic checkpoint replay, 8/8 future-mutation checks, 8/8 prefix-
  resume checks, causality, lengths, padding, output geometry, fixture identity,
  and every resource gate passed.
- The run performed four training runs, 1,680 optimizer steps, eight model-
  inference runs, two checkpoint writes, and one checkpoint read in 7.829308
  seconds internal time. Internal peak RSS was 310,509,568 bytes; external peak
  RSS was 320,405,504 bytes. Fixture arrays were 1,699,920 bytes and generated
  artifacts totaled 83,132 bytes.
- Raw-data reads, real-cache stat/hash/member reads, real signal and target
  rows, downloads, S24/S25 operations, stream/device/hardware/RW3 operations,
  and plaintext target/prediction emission were all zero. End-to-end latency
  was not measured.
- Added a 7,546-byte aggregate machine result and a human closeout. The ignored
  checkpoints and source reports remain uncommitted. Loop 48 Stage C is
  consumed and parked without tuning or rerun.
- The focused closeout set passes 64 tests. The dependency-light suite passes
  919 tests with 156 expected skips in 1.439 seconds internal time and 1.70
  seconds wall time at 123,912,192-byte external peak RSS. The optional-neuro
  suite passes 966 tests with 3 expected skips in 29.839 seconds internal time
  and 30.87 seconds wall time at 621,412,352-byte external peak RSS. Both add
  exactly eight result-contract tests over the corrected 911/958 baseline.
- Ruff, compileall, every registry JSON, three CLI help surfaces, source-result
  inspection, and `git diff --check` pass without rerunning the consumed gate.

Engineering capability added: NeuroDecodeKit executed the registered causal
temporal candidate, zero-context ablation, deterministic selection,
checkpoint-replay, causal-control, padding, resource, and no-leakage gates once
under a bounded synthetic interface.

Scientific claim not established: no real signal or target was opened, so
neural advantage, sensor-signal dependence, brain-specific origin, real
decoding improvement, generalization, real-time performance, and portable or
home EEG performance remain unestablished.

## 2026-07-15 - Loop 53 Fresh EEG Acquisition Registration

- Reverified only public metadata for the pinned SpanishBCBL revision and froze
  one exact S20 session 2 block 2 BrainVision triplet plus MAT log: four files
  totaling 96,090,264 bytes with Git/LFS/Xet source identities.
- Split acquisition from interpretation. Loop 53 permits only a future metadata
  recheck, one isolated transfer, opaque integrity hashes, and a bounded
  receipt; Loop 54 retains header, marker, geometry, signal, MAT, target, trial,
  and cache decisions.
- Froze one thread/worker, 600 seconds, 512 MiB RSS, 128 MiB network, 256 MiB
  incremental disk, 1 MiB receipt, and 2 GiB free-disk limits. Destination
  collisions and every mismatch park without overwrite, substitution, or rerun.
- Registration commit `bccd367` passed push CI `29469813041` and PR #31 CI
  `29469829357`. Base Python passed 929 tests with 156 expected skips; Optional
  Neuro Readers passed 961 with 29 expected skips. The local full environment
  passed 976 tests with 3 expected skips.
- Added the exact Tier C packet and hash-bound machine request. All 16 request
  execution flags remain false. No S20 payload, local path, header, marker,
  signal, MAT, target, cache, split, model, training, scoring, stream, device,
  or hardware operation occurred.

Engineering capability added: NeuroDecodeKit now has a source-bound,
resource-bounded, no-overwrite acquisition contract for one fresh EEG bundle.

Scientific claim not established: no EEG payload was acquired or interpreted,
so no signal quality, neural advantage, decoding accuracy, generalization,
real-time, portable/home, or clinical result was established.

## 2026-07-16 - Loop 54 EEG Qualification Research

- Audited six primary sources covering BrainVision file roles and marker
  semantics, MNE reader behavior, BIDS EEG/events identity, and the published
  Brain2Qwerty EEG cohort. No S20 path or payload was accessed.
- Audited the committed Loop 19 extractor at SHA-256
  `6aa8fcfff84a165cd88432bfd27ced3bab36af254261b28642ae12d9529ef7e9`.
  It co-loads marker annotations, MAT labels, and signal, excludes EOG-named
  channels, and writes plaintext labels. It remains valid at its historical
  engineering boundary but is not eligible for the future Loop 54/55 claim
  path.
- Added a four-stage prospective design: strict VHDR-only metadata with no MNE,
  target-blind VHDR+EEG quality with every channel retained, isolated VMRK+MAT
  reconciliation with protected outputs, and aggregate closeout.
- Froze five sensitivity classes, a 48-unique-trial floor, the trial as the
  future inference unit, 22 acceptance gates, 30 refusal IDs, one thread/worker,
  1 GiB maximum RSS, and 32 MiB combined public output. Loop 54 creates no
  split; exact Loop 55 counts remain a future prospective decision.
- Planning commit `aec440a` passes 22 focused contract/roadmap tests, the full
  996-test local suite with three expected skips in 30.312 seconds, Ruff, JSON
  validation, and `git diff --check`.
- Documentation-sync commit `b6785d7` passed push CI `29471589279` and PR #32
  CI `29471598364`; Base Python and Optional Neuro Readers passed in both.
- Loop 53 remains authorization-pending and is the next irreversible decision.
  All S20 stat/hash/header/marker/signal/MAT/target, split, model, training,
  inference, score, download, stream, device, and hardware counters remain zero.

Engineering capability added: NeuroDecodeKit now has a source-backed,
machine-checkable design for separating EEG metadata, target-blind signal
quality, and target-bearing trial reconciliation before any classifier claim.

Scientific claim not established: no S20 payload was accessed and no neural
advantage, decoding accuracy, brain-specific attribution, real-time operation,
portable hardware, home-use result, or clinical utility was demonstrated.

## 2026-07-16 - Loop 55 Fresh EEG Neural-Effect Research

- Audited the published Brain2Qwerty overt-typing windows and targets, EEGNet's
  compact spatial-temporal precedent, matched-control analysis, classifier
  permutations, small-sample uncertainty, and the inherited Loop 31/35/48
  boundaries. No S20 path or payload was accessed.
- Replaced one vague EEG score with two ordered endpoints from the same future
  final trials: causal pre-keypress performed-hand error and causal pre-
  keypress 29-class performed-key keypress-aligned CER.
- Made performed action primary and corrected intended sentence text secondary.
  The published `[-200,+300] ms` window is now explicitly diagnostic-only
  because it includes post-keypress execution and somatosensory feedback.
- Added seven competing hypotheses, a grouped trial-level split recommendation,
  twelve matched candidate/control/diagnostic conditions, exact paired final-
  trial decisions, a ten-stage target-access order, 30 acceptance gates, and 36
  exact refusal IDs.
- Froze prospective ceilings of one thread/worker, at most 10,000 trainable
  parameters per model, at most 12 fits, 45 CPU minutes, 1 GiB RSS, 64 MiB
  generated output, zero downloads, and no language model, stream, device, or
  hardware operation.
- Core planning commit `f3158c7` was followed by public-status synchronization.
  Current verification passes 24 focused Loop 55 and roadmap tests plus 9
  public-status subtests, Ruff, JSON validation, `git diff --check`, and the
  full local suite at 1007 passed, 3 expected skips, and 365 subtests in 31.88
  seconds.
- Documentation-sync commit `8efcb17` passed push CI `29473032843` and PR #33
  CI `29473045583`; Base Python and Optional Neuro Readers passed in both.
- Loop 53 remains the next irreversible Tier C decision. Loop 55 is Loop 54
  dependent, experimentally `Not Started`, and unauthorized; all S20, split,
  target, model, training, inference, scoring, and scientific-result counters
  remain zero.

Engineering capability added: NeuroDecodeKit now has a source-backed,
machine-checkable prospective design that distinguishes causal performed-hand
EEG evidence, causal performed-key evidence, and post-keypress task-aligned
diagnostics before any fresh target opens.

Scientific claim not established: no S20 payload, split, target, model,
prediction, training run, score, or latency measurement was accessed or
produced, so there is still no demonstrated EEG neural advantage or decoding
result.

## 2026-07-16 - Loop 56 Cross-Modality Accessibility Research

- Audited the local aggregate MEG and EEG evidence, Brain2Qwerty v1/v2,
  BIDS EEG/MEG channel semantics, OpenBCI Cyton packet mechanics, and the
  existing modality, geometry, and device boundaries without opening any raw,
  ignored, protected, target, prediction, checkpoint, model, or device payload.
- Froze five verdict classes: shared proven artifact, shared interface only,
  modality-specific requalification, unavailable, and prohibited inference.
  Signal values, scores, thresholds, channels, preprocessing, representations,
  weights, causal behavior, latency, and device capability cannot transfer by
  interface compatibility.
- Froze 12 non-skippable capability levels, 18 comparison dimensions, 16
  mandatory claim fields, 28 acceptance gates, 34 refusal IDs, eight outcome
  routes, and a 12-part at-home conjunction.
- Preserved the current evidence honestly: the registered tiny S21 MEG
  candidate reached macro CER `0.938177` versus prior `0.751235`; the historical
  S7 EEG nearest-centroid classifier reached accuracy `0.009091` versus prior
  `0.122727`. These are both negative but not a matched modality comparison.
  Fresh S20 qualification and neural-effect results remain unavailable.
- Separated continuous input, causal incremental output, and measured physical-
  source-to-visible-output latency. Published Brain2Qwerty v2 continuous MEG
  remains external, noncausal, whole-sentence evidence and establishes no local
  EEG, OPM, portable, device, or home result.
- The future final verdict is artifact-only under one thread/worker, 600 seconds,
  256 MiB RSS, and 16 MiB output. It waits for Loop 55 to close, exact aggregate
  hashes, and a separate exact Tier C claim decision. The provisional outcome
  is `L56-O2`, mechanics and interfaces only; execution remains `Not Started`.
- Planning commit `6583ca3` passed push CI `29586877054` and PR #34 CI
  `29586915269`; Base Python and Optional Neuro Readers passed in both.

Engineering capability added: NeuroDecodeKit now has a machine-checkable
cross-modality verdict vocabulary that separates shared artifacts and
interfaces from modality-specific evidence and prohibited inferences.

Scientific claim not established: no new EEG or MEG payload, target,
prediction, checkpoint, model, score, device, home session, or latency trace
was accessed or produced, so no cross-modality neural advantage, transfer,
real-time, portable, home, or clinical result was established.

## 2026-07-17 - Loop 53 Fresh S20 EEG Acquisition Closeout

- Recorded the user's exact acquisition-only decision at authorization commit
  `2a47bbc`; push CI `29589212626` and PR CI `29589225113` passed before
  implementation began.
- Added a standard-library, dry-run-by-default executor and CLI with immutable
  contract/decision hashes, current-clean-Git evidence, one-thread controls,
  metadata-first refusals, streaming byte/disk/time/RSS caps, opaque Git/LFS
  verification, complete-directory promotion, bounded receipts, and no payload
  parser. Implementation commit `8ec5b1b` passed push CI `29591387642` and PR
  CI `29591391286` before registered path or metadata network access.
- Qualified the implementation with 17 executor tests, 6 implementation-
  registry tests, 51 focused Loop 53 tests, Ruff, compile, all registry JSON,
  CLI help/dry-run, and `git diff --check`. The pre-execution full suite passed
  1,056 tests with 3 expected skips in 30.623 seconds.
- Ran the one registered invocation. The pinned public revision, CC BY-NC 4.0
  metadata, four paths, sizes, Git OIDs, LFS SHA-256 values, and Xet identities
  all matched. Exactly 96,090,264 network bytes became one exact four-file,
  96,090,264-byte isolated bundle; no partial or substitute was promoted.
- Measured 3.629499 seconds runtime, 63,225,856-byte peak RSS,
  102,035,529-byte peak incremental disk, 44,104,826,880 free bytes before,
  and 8,265 private receipt bytes. All ten frozen gates passed.
- Preserved zero header, marker, signal, MAT, target, cache, split, checkpoint,
  model, inference, training, scoring, language-model, RW3, stream, device,
  hardware, additional-file, additional-participant, and rerun counters. Four
  local reads were opaque integrity hashes only.
- Kept the payload and receipts Git-ignored. The public result repeats no per-
  file local content hashes and binds only the private manifest and receipt
  hashes plus aggregate measurements, counters, warnings, unavailable fields,
  and claim boundary.
- Marked Loop 53 `Consumed; Acquisition Passed; No Rerun` and stopped before
  Loop 54. No L54-A/B/C content stage is authorized by this closeout.
- Synchronized the current Markdown, JSON, and Excel trackers. The workbook
  now records consumed Loop 48 A/B/C, the exact Loop 53 result, the still-
  unauthorized Loop 54-56 boundaries, and the parked superseded RW4 route;
  its post-edit formula-error scan found zero matches and all ten sheets were
  rendered for visual review.
- Final closeout verification passed 68 focused tests and the complete 1,062-
  test suite with 3 expected skips in 44.090 seconds at 581,648,384-byte
  external peak RSS. Against the pre-execution 1,056-test baseline, this adds
  exactly 6 result tests; skips stayed at 3, measured runtime increased by
  13.467 seconds, and external peak RSS increased by 12,959,744 bytes. Ruff,
  compile, 65 registry JSON files, both CLI help surfaces, and
  `git diff --check` also passed.

Engineering capability added: NeuroDecodeKit can now acquire, opaque-verify,
atomically retain, and privately receipt one exact public EEG bundle under a
hash-bound one-shot resource and access-order contract.

Scientific claim not established: no BrainVision readability, channel,
geometry, signal-quality, event, trial, target, neural-advantage, decoding,
generalization, latency, portable-hardware, at-home, or clinical result was
measured or established.

## 2026-07-17 - Loop 55 Bounded AI Research Guard

- Audited Brain2Qwerty v2 Auto Research, its encoder/LLM failure discussion,
  LaBraM, BIOT, EEGNet, and the existing Loop 54/55 proof boundaries.
- Froze AI as a bounded recipe proposer and protocol critic, never a protected-
  data controller, endpoint selector, language-model decoder, or claim author.
- Preserved one compact causal family, the `[-500,0)` ms window, zero right
  context, `<=10,000` parameters, and the existing 12-fit total. At most four
  future train-inner proposal rounds may be preregistered; extra control needs
  reduce those rounds instead of expanding the total.
- Added a strict dependency-free proposal validator, canonical JSON/SHA-256
  identities, bounded JSON I/O, three CLI commands, and one 1,771-byte synthetic
  proposal. No AI service, NumPy, MNE, Torch, network, or model is required.
- Rejected target/text leakage, performed labels during self-supervised warm-
  up, pretrained weights, language models, final observation scope, noncausal
  windows, future context, unknown fields, unlisted hyperparameters, Boolean
  zero tricks, resource expansion, model/training runs, nonzero access
  counters, and untrusted warning text.
- Policy commit `8855fae` passed push CI `29620964755`. Implementation commit
  `bd52cce` was pushed separately before this documentation synchronization.
  Its first CI correctly exposed a brittle Loop 53 historical CLI hash test;
  repair `f50be96` preserved the consumed hash as a snapshot, retained semantic
  command checks, and passed push CI `29621564301`.
- One CLI validation read 11,949 policy bytes and 1,771 proposal bytes, ran in
  `0.000741542` seconds, reported 21,856,256-byte peak RSS, and recorded zero
  raw-data, real-cache, model, training, inference, scoring, network, language-
  model, stream, device, or hardware runs.
- The unrelated tracker inspection NDJSON remains untouched. The Excel
  workbook was not reopened because this additive policy does not change a
  loop's scientific status and its prior full import reached 1.57 GiB peak RSS.
- Final verification passed 49 focused policy/Loop 55/roadmap tests and the
  complete 1,087-test suite with 3 expected skips in 21.592 seconds. This adds
  exactly 25 tests to the 1,062-test pre-change baseline without changing the
  skip count. External peak RSS was 636,977,152 bytes. Ruff, compilation, both
  modified registry JSON files, three CLI help surfaces, the bounded synthetic
  roundtrip, and `git diff --check` passed.

Engineering capability added: NeuroDecodeKit can now constrain, hash, inspect,
and reject synthetic AI-generated representation proposals before they can
interact with protected evidence or executable model stages.

Scientific claim not established: no AI proposal accessed S20, trained or ran
a model, or measured an EEG effect, so no neural advantage, decoding,
brain-specific, generalization, real-time, portable, home, or clinical result
was established.

## 2026-08-06 - Loop 54-A Strict VHDR Preregistration

- Converted the first real EEG qualification step into one exact one-file
  contract instead of expanding the roadmap.
- Bound `EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr` at exactly 11,705 bytes and
  source Git ID `9ab325a0f8523b675ecab1c97e16169143f1f341`.
- Froze a base-Python-only parser with no-follow input handling, strict
  codepage decoding, exact required sections, ordered `Ch1..ChN` validation,
  deterministic sampling-rate derivation, inert sibling basenames, and no MNE
  or sibling resolution.
- Froze 18 acceptance gates, 22 refusal classes, one VHDR content open, one
  registered execution, one thread/worker, 30 seconds, 256 MiB peak RSS, 1 MiB
  generated output, and zero network or new payload bytes.
- Prepared an exact Tier C authorization request that permits synthetic-fixture
  implementation first and one real VHDR execution only after separate green
  decision and implementation commits. VMRK, EEG, MAT, target, split, model,
  training, inference, scoring, language-model, device, and rerun operations
  remain forbidden.
- Registration commit `c114623` is pushed. Local verification passed 20 focused
  Loop 54 tests and the complete 1,095-test suite with 3 expected skips in
  33.037 seconds at 650,264,576-byte external peak RSS, plus Ruff, compileall,
  JSON validation, and diff checks.
- GitHub registration CI `31127199848` was cancelled before any step started
  during the confirmed 2026-08-06 Actions major outage. The authorization
  request is preserved only as a non-actionable draft. A remote-green run over
  exact registration commit `c114623` remains required before it can freeze.
- The complete authorization-request tree passes 1,103 tests with 3 expected
  skips in 29.866 seconds at 643,842,048-byte external peak RSS; 39 focused
  contract/request/roadmap tests, Ruff, compileall, JSON validation, and diff
  checks also pass.

Engineering capability proposed: NeuroDecodeKit now has a machine-checkable
one-file path from opaque S20 acquisition toward declared-header qualification
without exposing marker, signal, MAT, or target siblings.

Scientific claim not established: no S20 path was statted and no header,
signal, marker, MAT, event, trial, target, or model content was accessed, so no
EEG quality, neural advantage, decoding, generalization, latency, hardware,
home-use, or clinical result was established.

## 2026-08-06 - Open EEG R&D Strategy Refresh

- Re-audited the current Loop 54/55 path against current primary papers,
  official tool repositories, public dataset metadata, and the project's
  frozen proof boundary.
- Confirmed that two current EEG foundation-model benchmarks support retaining
  a specialist-first path: specialist models remain competitive, linear probes
  are often insufficient, and larger models do not consistently generalize
  better. Full fine-tuning can help, but the strongest cited ST-EEGFormer
  variant exceeds 300 million parameters and belongs to a different resource
  regime.
- Added a prospective known-effect positive control using only public metadata:
  PhysioNet EEGMMIDB participants S001-S003, motor-execution runs 3/7/11, nine
  exact EDF paths totaling 23,248,224 bytes. No payload was downloaded. A
  future 32 MiB network/64 MiB disk contract and exact Tier C decision remain
  required.
- Recommended one public-data-selected CSP or Riemannian family, fixed
  low-frequency shrinkage LDA, a causal pre-keypress motor-physiology assay,
  and the existing compact EEGNet-style family. The existing 10,000-parameter,
  12-fit, target, language-model, and protected-access ceilings remain intact.
- Added an open-source adoption matrix for MNE 1.12.1, MOABB 1.5, Braindecode
  1.7.0, pyRiemann 0.12, MNE-BIDS 0.19.0, OpenEEGBench 0.6.0,
  EEG-FM-Compass, ST-EEGFormer, and ZUNA1.1. Every dependency remains optional
  or isolated. Automatic benchmark downloads and generative primary-input
  imputation remain forbidden.
- Defined a local-first contributor direction: raw EEG and plaintext targets
  remain on the contributor's machine by default, while future shareable
  receipts carry hashes, metadata, resources, controls, warnings, and aggregate
  claim boundaries.
- Added `docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md`,
  `registries/open_eeg_rd_strategy.v0.json`, and ten machine-checking tests.
  The three new strategy artifacts total 41,065 bytes.
- Focused verification passed 10/10 tests. The pre-change 1,103-test baseline
  advanced to 1,113 passing tests with the same 3 expected skips in 29.353
  seconds at 617,611,264-byte external peak RSS under one-thread environment
  limits. Ruff, compileall, JSON
  validation, source-link checks, and `git diff --check` passed.
- GitHub Actions remained in a major outage during preparation. No remote-green
  claim is made, and the separate L54-A registration recovery gate remains
  pending.

Engineering capability proposed: NeuroDecodeKit now has a machine-checkable
strategy for de-risking protected EEG work with a tiny public motor positive
control, interpretable specialist baselines, and local-first contributor
receipts.

Scientific claim not established: this refresh accessed public metadata and
committed local artifacts only; it downloaded no EEG payload, touched no S20
path, loaded no checkpoint, trained or scored no model, and established no EEG
effect, neural advantage, decoding, generalization, real-time, hardware,
home-use, or clinical result.

## 2026-08-06 - Causal Motor Lattice Architecture Research

- Reviewed nine primary sources spanning Brain2Qwerty keyboard geometry,
  compact filter-bank models, EEGNet, Riemannian decoding, movement-onset and
  signal-quality sensitivity, channel adaptation, responder/session effects,
  synchronized kinematics, and EEG+EMG movement-onset data.
- Selected `CML-v0` as a project-specific research synthesis, not a global
  novelty or superiority claim. It gives potential, causal mu, and causal beta
  separate rank-8 spatial branches and three temporal cells each, then uses a
  72-to-24 bottleneck. Every learned spatial row is zero-sum and unit-norm,
  adding no parameter while reducing common-reference and scale ambiguity.
- Replaced independent hand/key heads with a fixed physical keyboard lattice,
  one `rho * tanh(...)` bounded 29-key residual, and an exact hand probability
  marginal. This
  prevents internally contradictory hand and key predictions while preserving
  performed-action supervision and excluding intended text.
- Derived the exact trainable-parameter formula `24C + 2,549 + 25P`. At 64
  channels and the maximum 18 primitives, the reference has 4,535 parameters;
  it stays below 10,000 through 291 channels.
- Added eight same-checkpoint evidence-escrow probes for branch, channel, time,
  and optional hemisphere failure localization. They are explicitly
  diagnostic and cannot prove cortical physiology or replace trained controls.
- Split the public qualification strategy into two independent axes: the
  existing 23,248,224-byte PhysioNet prospect for left/right execution and a
  future exact EEG+EMG MRCP slice for pre-movement timing. No public payload was
  downloaded or opened.
- Defined the next eligible Tier B milestone as a separately contracted
  deterministic synthetic factor-isolation gate under one thread, 600 seconds,
  512 MiB RSS, and 4 MiB output. It was not implemented or executed here.
- Added the research document, machine-readable registry, and dependency-free
  invariants while preserving every frozen Loop 54/55 hash and zeroing every
  real/protected/model counter.
- The three new research artifacts total 64,022 bytes under the declared
  1 MiB cap. Focused verification passed 50 tests across the new architecture,
  existing Loop 55, open EEG strategy, and scientific-roadmap boundaries.
- The pre-change 1,113-test baseline advanced to 1,129 passing tests with the
  same 3 expected skips in 28.817 seconds of unittest runtime and 29.94 seconds
  wall time at 638,500,864-byte external peak RSS under one-thread limits.
  Ruff, compileall, all registry JSON parsing, and `git diff --check` passed.
- Push CI exposed a separate reproducibility defect already present in the
  preceding strategy commit: `pyproject.toml` allowed `ruff>=0.5`, so GitHub
  installed Ruff 0.16.1 while the locally qualified environment used 0.15.20.
  The newer release expanded lint behavior and surfaced 402 historical findings
  unrelated to this packet. Pin both `dev` and `all` extras to Ruff 0.15.20,
  matching the clean local gate, instead of mechanically rewriting unrelated
  source and test files. Repair commit `2232993` passed push CI
  `31132586790`: Base Python completed in 18 seconds and Optional Neuro Readers
  completed in 51 seconds.

Engineering capability proposed: NeuroDecodeKit now has a machine-checkable,
failure-addressable compact EEG architecture and a two-axis qualification
strategy that can localize potential, mu, beta, spatial, timing, peripheral,
and keyboard-structure failure before protected evidence is spent.

Scientific claim not established: no EEG payload, protected target, model, or
score was accessed, so this work establishes no EEG effect, neural advantage,
decoding accuracy, generalization, causal real-time output, portable hardware,
home use, or clinical utility.

## 2026-08-06 - Foundation-Model Decoder Strategy

- Recorded the product architecture as a compact causal sensor adapter followed
  by frozen `gpt-5.6-sol`, rather than treating the compact model as the final
  language decoder or attempting to train a GPT-scale model.
- Separated the hosted structured-evidence path from a future local continuous
  embedding-prefix path. Sol receives no raw EEG/MEG, dense NeuroToken vector,
  participant identity, target, intended sentence, label, or local path.
- Frozen four matched conditions: language-only `FM-A00`, CTC-only `FM-A01`,
  matched `FM-A02`, and fixed cyclically item-deranged `FM-A03`. A future
  incremental result requires `FM-A02` to beat both matched controls under the
  same model and prompt after a prediction freeze.
- Selected FM-0 as a deterministic synthetic no-call bridge under one thread,
  30 seconds, 256 MiB RSS, and 1 MiB input/output caps. External inference,
  credentials, spend, protected data, targets, scores, and fine-tuning remain
  closed.
- Added the strategy document, machine-readable registry, and invariants. No
  provider, model, network, real-data, target, training, inference, or scoring
  operation occurred.

Engineering capability proposed: NeuroDecodeKit now has an explicit and
testable boundary between neural evidence production and foundation-model
language decoding.

Scientific claim not established: no language model or neural model was run,
so this strategy establishes no neural advantage or decoding result.

## 2026-08-06 - Foundation-Model Bridge v0

- Implemented FM-0 as a dependency-free synthetic no-call compiler with three
  CLI commands for fixture creation, four-arm plan compilation, and inspection.
- Bound the source file, canonical evidence, per-item CTC and causal-key rows,
  fixed cyclic derangement, each blinded request, and the complete plan core by
  SHA-256.
- Added strict refusals for target/reference/label leakage, raw signal and
  dense-vector content, identity/path fields, noncausal timing, malformed
  probabilities, unknown fields, nonzero or Boolean counters, hash tampering,
  cap expansion, symlinks, and accidental overwrite.
- The committed 7,327-byte fixture contains 3 items, 6 CTC hypotheses, 12
  causal frames, and 24 top-key probabilities. It compiled into all 12
  conditions and 34,349 bytes in 0.002745583 seconds at 21,495,808-byte peak
  RSS. Inspection took 0.001411584 seconds at 21,037,056-byte peak RSS.
- Every provider, credential, model, network, real/protected read, annotation,
  training, and scoring counter remained integer zero. Provider responses,
  token usage, cost, latency, text accuracy, and end-to-end latency remain
  unavailable.
- Focused strategy/implementation verification passed 35 tests. The complete
  pre-change 1,129-test baseline advanced to 1,164 passing tests with the same
  3 expected skips in 31.172 seconds internal and 32.28 seconds wall time at
  629,456,896-byte external peak RSS. Ruff, compileall, every registry JSON,
  root and command help, the bounded roundtrip, and diff hygiene passed. The
  six implementation artifacts total 84,637 bytes.

Engineering capability added: NeuroDecodeKit can compile and audit the exact
four-condition foundation-model evidence experiment without a provider call.

Scientific claim not established: `FM-A02` has not run, no model output or
target exists, and FM-0 establishes no neural advantage or decoding result.

## 2026-08-08 - FM-1 Terra Contract, Authorization, And Provider Runner

- Preregistered one synthetic-only FM-1 Responses API qualification at commit
  `7db14d5`. The contract freezes the committed 7,327-byte fixture, rebuilt
  34,349-byte FM-0 plan, 12 independent requests, four blinded conditions,
  `gpt-5.6-terra`, low reasoning, strict structured output, standard service,
  no tools, no storage, no streaming, and no retries. Push CI `31267860543`
  passed both required jobs.
- Recorded the user's exact separate authorization at commit `04fc009` without
  reading the environment credential or contacting the provider. Push CI
  `31268358553` passed both required jobs.
- Implemented a standard-library provider transport with no new base
  dependency. It verifies every contract, decision, fixture, plan, and request
  hash; requires exact implementation `HEAD`, decision ancestry, origin
  presence, a clean tracked tree, one-thread settings, a new nonsymlink output,
  and at least 1 GiB free disk before credential access.
- Added a strict Responses request with fixed endpoint/model/reasoning/service,
  `store=false`, `stream=false`, no tools, and a four-field JSON Schema. The
  provider payload excludes condition/item identity, targets, references,
  labels, intended text, raw EEG/MEG, dense embeddings, NeuroTokens,
  participant identity, and local paths.
- Added sanitized consumed receipts with exact request/response hashes, parsed
  outputs, refusals, usage, estimated standard cost, byte totals, per-request
  latency, condition summaries, descriptive pairing, warnings, unavailable
  fields, and access counters. Raw response IDs, headers, provider error
  bodies, organization metadata, and credentials are not retained.
- Added fail-closed parking for transport, model, schema, usage, response-byte,
  total-byte, token, cost, runtime, and RSS failures. There is no retry. Failed
  response bodies are represented only by byte count and SHA-256.
- Added dry-run and offline inspection CLI commands. The current dry run rebuilt
  exactly 12 requests totaling 18,399 bytes, with a 1,047-byte minimum and
  1,958-byte maximum, in 0.004586541 seconds at 33,832,960-byte peak RSS.
- Focused implementation verification passes 13 tests covering exact replay,
  zero-network isolation, fake success, partial failure, malformed replies,
  cap parking, tamper rejection, offline inspection, CLI gates, and dependency
  boundaries. The post-decision 1,176-test baseline advanced to 1,193 passing
  tests with the same 3 expected skips in 28.274 seconds internal and 29.30
  seconds wall time at 618,086,400-byte external peak RSS. Ruff, compileall,
  every registry JSON, root and FM-1 CLI help, the zero-network dry run, and
  diff hygiene pass. Exact remote-green implementation evidence remains
  required before the one live invocation.
- No API credential was read. External network calls, provider calls, spend
  events, real/protected reads, target/reference reads, raw/dense neural
  uploads, training, fine-tuning, and scoring all remain zero.

Engineering capability added: NeuroDecodeKit now has a bounded, inspectable
provider boundary for the frozen synthetic FM-1 matrix, gated on an exact
remotely green implementation commit.

Scientific claim not established: no provider output, real neural evidence,
target, or score exists at this milestone, so no decoding or neural result was
established.

## 2026-08-08 - FM-1 Consumed Parked Result

- Implementation commit `a1d7ccc` passed push CI `31269398670`: Base Python in
  15 seconds and Optional Neuro Readers in 50 seconds.
- Consumed the one authorized invocation with one credential read, three
  sequential provider calls, and zero retries. Two responses completed and
  validated; request index 2 returned provider status other than `completed`.
- `FM-A00` abstained with empty text and no evidence. `FM-A01` returned
  `HELLO WURLD` from CTC evidence. No matched `FM-A02` or deranged `FM-A03`
  response pair exists, so descriptive evidence sensitivity is unavailable.
- The two completed responses reported 339 input, 143 output, and 62 reasoning
  tokens with no cached or cache-write tokens. Their local standard-price
  estimate is $0.002394. Usage and actual billing for the third attempt are
  unavailable; provider accounting remains authoritative.
- Runtime was 8.406004375 seconds, peak RSS was 39,337,984 bytes, wire request
  and response totals were 4,179 and 13,502 bytes, and the sanitized local
  result was 5,882 bytes with SHA-256
  `f1ff632c45bc0a6c60fcec865615bf7becf07589f5d3a3472f26492c2ee5756e`.
- Terminal response content was not retained. Its 5,720 bytes are represented
  only by SHA-256
  `c13d1e7c5ff6dd9440564c63b7f69e6ad877b89b00e0dcfe91b7043eb4b503cf`.
- Real/protected reads, target/reference reads, raw/dense neural uploads,
  training, fine-tuning, and scoring all remained zero. FM-1 is consumed and
  has no rerun.

Engineering capability added: the live provider boundary returned two strict
synthetic responses and produced an honest bounded receipt when the third did
not complete.

Scientific claim not established: the matrix is incomplete and contains no
real neural evidence or target, so FM-1 establishes no decoding or neural
result.

## 2026-08-08 - $50 AI Budget And Local-First Tool Strategy

- Recorded the user's $50 aggregate AI-provider ceiling. Conservatively held
  the entire $0.50 FM-1 cap because third-attempt billing is unavailable,
  leaving $49.50 in future lane ceilings rather than a spending target.
- Reserved $1.50 for independent transport recovery, $3 for synthetic
  Sol/Terra controls, $5 for public target-free integration, $10 for a future
  separately gated public target-bearing evaluation, $20 for a future
  separately gated protected evaluation, and $10 as unallocated contingency.
- Selected MNE, MOABB, pyRiemann, and compact Braindecode models as the local
  stack before further hosted inference. No dependency, dataset, checkpoint,
  model, or hardware was installed, downloaded, loaded, trained, or run.
- Verified Apple application `US20230225659A1`: it describes an earbud-form
  device with multiple active/reference electrodes, dynamic quality-aware
  selection or weighting, and EEG as a possible biosignal. It does not mention
  AirPods, prove a shipping product, or report thought-to-text.
- Added a generic future architecture for target-blind ear-channel contact,
  noise, missingness, and subset metadata ahead of classical and compact model
  comparisons. Hardware, SDKs, purchases, recording, protected data, targets,
  scoring, large downloads, commercial implementation, and claims remain
  separately gated.
- This documentation/research pass made zero new provider calls, credential
  reads, spend events, data/model downloads, protected reads, target reads,
  training runs, scoring runs, or hardware operations.
- Final closeout verification passed 1,201 tests with three expected skips in
  29.476 seconds, up from the 1,193-test pre-closeout baseline after adding the
  eight result and budget contract tests. Ruff, bytecode compilation, every
  JSON registry, CLI help, offline FM-1 result inspection, and
  `git diff --check` also passed. The complete-suite process used one configured
  compute thread and peaked at 629,555,200-byte resident set size.

Engineering direction added: NeuroDecodeKit now has a conservative provider
budget ledger and a mature local-tool path toward public EEG and future
contact-variable ear-worn sensing.

Scientific claim not established: no new signal, target, model, or hardware
evidence was produced, so no neural or decoding result follows.

## 2026-08-08 - Loop 54-A Registration CI Recovery

- Cancelled the two-day zero-job queue for run `31127199848` and retried it as
  attempt 2 against exact commit `c114623`. Optional Neuro Readers passed in 48
  seconds. Base Python installed Ruff `0.16.2` from the historical
  `ruff>=0.5` declaration and stopped at Ruff in 13 seconds with 400
  repository-wide findings; compile, tests, and CLI help did not run in that
  job. The exact-commit run remains failed evidence.
- Verified that the frozen preregistration, contract, and invariant test are
  byte-identical at `c114623`, pinned-toolchain descendant `2232993`, and the
  recovery parent. Push CI `31132586790` for `2232993` passed Base Python and
  Optional Neuro Readers under Ruff `0.15.20`.
- Replayed the exact `c114623` tree locally under pinned Ruff `0.15.20`: Ruff
  passed in 0.05 seconds at 49,659,904-byte peak RSS; 1,095 tests passed with
  three expected skips in 28.824 seconds internal and 30.26 seconds wall time
  at 626,622,464-byte external peak RSS. Compileall, every registry JSON, and
  CLI help passed.
- No S20 path, VHDR, sibling, signal, marker, MAT, target, model, network,
  provider, device, or hardware content was accessed. The old draft request
  remains non-actionable; a new recovery-bound exact request is required.
- Fresh recovery-tree verification passed 1,206 tests with three expected
  skips in 29.152 seconds internal and 30.25 seconds wall time at
  638,009,344-byte external peak RSS under one configured compute thread.
  Forty-four focused recovery, contract, request, roadmap, and tracker tests
  passed.

Engineering capability added: immutable registration evidence can survive
development-tool drift without rewriting the frozen scientific contract.

Scientific claim not established: this recovery accessed no S20 content and
produced no EEG, trial, neural, decoding, latency, device, or clinical result.

## 2026-08-08 - Zero-Network Local EEG Tooling Audit

- Added a dependency-light `inspect-local-eeg-tooling` command with a fixed
  seven-library matrix, isolated child imports, blocked socket operations,
  one-thread environment, disposable home/cache, sanitized output hashes,
  strict caps, no-overwrite writing, and malformed/timeout handling.
- Eight implementation tests raised the pre-change 1,206-test baseline to
  1,214 passing tests with three expected skips. The complete suite finished in
  28.129 seconds at 643,203,072-byte external peak RSS; Ruff, compileall, CLI
  help, and diff hygiene passed.
- Implementation commit `e1de855` passed exact-SHA push CI `31277731869`: Base
  Python in 16 seconds and Optional Neuro Readers in 49 seconds. A consumed
  FM-1 CLI digest remains preserved as historical evidence while current tests
  continue to assert that its command surface exists.
- One post-green audit found NumPy 2.5.0, SciPy 1.18.0, and MNE 1.12.1.
  NumPy/SciPy capabilities, the BrainVision reader, and ICA are available; MNE
  CSP is incomplete and scikit-learn, pyRiemann, MOABB, and Braindecode are
  absent. No dependency was installed.
- The audit finished in 14.52799025 seconds at 25,083,904-byte parent and
  173,211,648-byte maximum child RSS. It retained 9,416 bytes under a 1 MiB cap.
  One 290,596-byte MNE cache file existed only inside the disposable audit home
  and was removed. MNE's 63 captured terminal bytes survive only as count and
  SHA-256.
- All successful-network, download, real/protected, raw-signal, target, model,
  training, inference, scoring, provider, device, and hardware counters are
  zero. Stable import input bytes and all scientific fields remain unavailable.
- Added an active 20-work-order execution overlay. Work orders 1-2 are complete;
  work order 3 uses the existing NumPy/SciPy core for deterministic synthetic
  physiology/confound fixtures before any optional install or real-data gate.
- Seven result/receipt invariants bring the complete closeout to 1,221 passing
  tests with three expected skips, 15 tests above the 1,206-test starting
  baseline. The one-thread suite took 28.863 seconds internal and 29.94 seconds
  wall time at 653,066,240-byte external peak RSS.

Engineering capability added: the repository can inventory its local EEG stack
through bounded zero-network probes and route work from measured capability.

Scientific claim not established: installed library surfaces establish no EEG
quality, neural effect, decoding accuracy, generalization, latency, device, or
clinical result.

## 2026-08-08 - Synthetic Motor Fixture Contract

- Froze work order 3 as a fixture-only Tier B contract before implementation.
  Seed 5503 produces a prospective 96-item, eight-family array set with six
  paired synthetic design classes per family and exact 48/32/16
  train/check/final counts.
- The eight families match the additive CML research recommendation exactly:
  potential, mu, beta, mixed, spatial reversal, timing-only, peripheral common
  mode, and pure noise. Eight separate mutations cover 50/60 Hz line noise,
  channel dropout/derangement, time displacement, peripheral-only, zero-signal,
  and future-tail prefix checks.
- No real names, text targets, participant identity, protected paths, external
  weights, model, parameter update, inference, scoring, network, stream,
  device, or hardware action is allowed. NumPy/SciPy remain optional and lazy.
- Seven contract invariants pass. The registry, source hashes, factor list,
  pair/split inventory, array schema, mutation list, resource caps,
  authorization boundary, zero counters, and tracker state agree.

Engineering capability proposed: one deterministic fixture can exercise motor,
timing, peripheral, padding, and corruption interfaces before real evidence is
spent.

Scientific claim not established: preregistration and generated factors cannot
establish real EEG physiology, neural origin, decoding, generalization,
latency, device performance, home use, or clinical utility.

## 2026-08-08 - Synthetic Motor Fixture Implementation

- Added a lazy optional NumPy/SciPy generator for the exact seed-5503,
  96-item, eight-channel, eight-factor contract. Every row carries explicit
  length, mask, strictly pre-event timestamps, synthetic pair/class/factor
  identity, partition, channel name, and invented geometry.
- Added deterministic ZIP metadata, array hashes, a strict full loader, and a
  metadata-only inspector that hashes the payload and examines ZIP members
  without opening arrays. Output collision and 4 MiB cap failures occur before
  any fixture file is written.
- Added eight deterministic mutations. Tests verify byte replay, analytic
  factor isolation, pair-bound 48/32/16 splits, exact padding, malformed and
  hidden-target refusal, future-prefix invariance, lazy imports, cap behavior,
  and create/inspect CLI roundtrip.
- Twelve focused tests and 31 combined fixture/contract/receipt/prior-result
  tests pass. The complete suite currently passes 1,242 tests with three
  expected skips and 469 subtests. One historical local-tooling CLI digest
  remains preserved while its exact command surface is asserted after this
  additive CLI change.
- A disposable probe observed shape `[96, 8, 256]`, 20,448 valid samples,
  `0.16796875` padding fraction, and 584,133 total bytes. These are development
  observations, not the retained measured closeout. The exact implementation
  commit must be pushed and remotely green before that one measured replay.

Engineering capability added: the repository can generate, validate, inspect,
and mutate a deterministic synthetic motor-factor fixture with fail-closed
identity, leakage, causality, padding, hash, and resource checks.

Scientific claim not established: no real EEG physiology, neural origin,
decoding accuracy, generalization, end-to-end latency, device performance,
home use, or clinical utility was established.

## 2026-08-08 - Synthetic Motor Fixture Measured Closeout

- Implementation commit `ad361c8` passed exact-SHA push CI `31279302969`
  before the measured closeout: Base Python in 17 seconds and Optional Neuro
  Readers in 52 seconds.
- One CLI creation and one metadata-only inspection ran in an automatically
  removed temporary directory. Both returned zero and their summaries matched.
  The inspector opened zero arrays. There was no retry or post-result tuning.
- The fixture used 1.20 seconds, 118,177,792-byte peak RSS, and 584,308 output
  bytes: a 572,307-byte NPZ and 12,001-byte sidecar. Shape was `[96, 8, 256]`,
  valid samples were 20,448, and padding fraction was `0.16796875`.
- Every factor had 12 rows, partitions were 48/32/16 with pairs intact, the
  fixture producer was causal with zero right context, and end-to-end latency
  was not measured. The two generated files were removed after hashing.
- All 18 acceptance gates passed. Exactly one measured synthetic payload was
  generated. Raw-data, real-cache, real/protected, public-EEG, target, model,
  training, inference, scoring, network, provider, stream, device, hardware,
  and claim-upgrade counters were zero.
- Thirty-seven focused closeout checks and the complete suite passed at 1,248
  tests, three expected skips, and 469 subtests.
- Work order 3 is complete. Work order 4 now begins with optional classical EEG
  adapter contracts and leakage tests only; no package install or real adapter
  execution follows automatically.

Engineering capability added: NeuroDecodeKit now has a measured, bounded,
deterministic synthetic motor-factor fixture surface for pre-evidence adapter
and architecture testing.

Scientific claim not established: no real EEG physiology, neural origin,
decoding accuracy, generalization, end-to-end latency, device performance,
home use, or clinical result was established.

## 2026-08-08 - Classical EEG Adapter Contract

- Froze work order 4 before implementation as a standard-library symbolic-plan
  task. Registered low-frequency shrinkage LDA, causal 8-30 Hz CSP-LDA, and
  regularized Riemannian MDM without choosing, importing, fitting, or scoring a
  family.
- Bound availability to the completed zero-network audit: NumPy/SciPy substrate
  is available; MNE CSP is incomplete because scikit-learn is absent; pyRiemann
  and scikit-learn are absent. No install, new import probe, or silent fallback
  is allowed.
- Froze explicit item/group/pair/partition identities; zero cross-partition
  groups or pairs; train-only preprocessing, quality, standardization, spatial
  transform, classifier, and prior stages; target-blind check/final use; and
  zero post-event/right context.
- Added twelve required refusal classes covering group/pair leakage, duplicate
  or missing identity, row splits, evaluation targets, evaluation fitting,
  global normalization, future context, forbidden fields, unknown adapters,
  and dependency substitution.
- The eventual Tier B implementation may build only a deterministic 96-item,
  48-group symbolic plan from the synthetic identity formula. Every array,
  data, target, feature, fit, inference, score, network, provider, and hardware
  counter remains zero in this contract.
- Seven contract invariants and 20 combined contract/prior-result checks pass.
  The complete pre-implementation suite passes 1,255 tests with three expected
  skips and 469 subtests in 38.59 seconds wall time.

Engineering capability proposed: NeuroDecodeKit can validate leakage-resistant
optional classical EEG adapter plans before installing or fitting them.

Scientific claim not established: adapter specifications establish no real EEG
effect, neural origin, decoding, generalization, latency, device performance,
home use, or clinical result.

## 2026-08-08 - Classical EEG Adapter Plan Implementation

- Added a standard-library-only module that builds one deterministic 96-item,
  48-group symbolic plan for all three unselected classical families. It never
  imports NumPy, SciPy, MNE, scikit-learn, or pyRiemann.
- Added strict contract/source, adapter, item, pair/group, partition, fit-scope,
  target-firewall, causality, dependency-route, counter, warning, claim, and
  canonical-hash validation plus bounded save/load/summary APIs.
- All twelve registered malformed plans are deterministically constructed and
  refused. Unknown fields, hash changes, contract substitution, output cap,
  and collision paths also fail closed.
- Ten focused implementation tests and 33 combined adapter, contract,
  implementation-receipt, and prior-receipt checks pass. The complete suite
  passes 1,273 tests with three expected skips and 469 subtests in 35.18
  seconds wall time at 612,794,368-byte peak RSS.
- A disposable development probe serialized 27,335 bytes at canonical hash
  `66800348e76d03b9b994a460b2e78fbe569c450fdb289be5948cecbcea860bf1`.
  No plan file was retained. Measured closeout waits for exact-commit green CI.

Engineering capability added: the repository can construct, hash, validate,
save, inspect, and reject leakage in optional classical EEG adapter plans
without importing or fitting an adapter.

Scientific claim not established: no real EEG effect, neural origin, decoding,
generalization, latency, device performance, home use, or clinical result was
established.

## 2026-08-08 - Classical EEG Adapter Plan Measured Closeout

- Exact implementation `eefb7b066810c2a6b87417b105bdb746218e87dc` passed
  push CI `31280581308` before execution: Base Python in 16 seconds and
  Optional Neuro Readers in 57 seconds.
- Exactly one CLI creation and one CLI inspection ran in an automatically
  removed temporary directory. Both returned zero and their compact summaries
  matched. There was no retry or post-result tuning.
- Runtime was 0.12 seconds, peak RSS was 22,822,912 bytes, the input contract
  was 12,025 bytes, and the generated plan was 27,335 bytes under a 1 MiB cap.
  The plan was removed after hashing.
- The plan held 96 symbolic items in 48 pair-bound groups across exact
  48/32/16 item and 24/16/8 group partitions. All three adapter families
  remained unselected. Required right context and post-event samples were zero;
  no producer ran and end-to-end latency was not measured.
- All 18 gates passed. One symbolic build and one inspection occurred. Every
  adapter import, dependency install, array/data/target read, feature, fit,
  inference, training, scoring/selection, network/provider, hardware, and
  claim-upgrade counter was zero.
- Thirty-nine focused closeout checks and the complete suite pass at 1,279
  tests, three expected skips, and 469 subtests.
- Work order 4 is complete. Work order 5 is active only for a synthetic
  contact-mask, channel-noise, and missing-channel contract; no hardware or
  real-data action follows.

Engineering capability added: NeuroDecodeKit now has a measured,
leakage-resistant, bounded symbolic planning surface for three optional
classical EEG adapters.

Scientific claim not established: no EEG adapter was executed and no real
neural effect, decoding accuracy, generalization, latency, device performance,
home use, or clinical result was established.

## 2026-08-08 - Contact-Aware Ear-Channel Contract

- Used the Apple dynamic-electrode application, OpenBCI cEEGrid documentation,
  the original cEEGrid paper, and the open OpenBCI-cEEGrid adapter paper only to
  bound the engineering problem. The contract does not infer current AirPods
  capability, freedom to operate, brain-specific origin, or decoding.
- Froze a generic post-acquisition interface with seed 5505, 48 items, 16
  bilateral source channels, 256 strictly pre-event samples at 128 Hz, and
  eight six-item contact/noise/missingness scenarios.
- Kept observed, channel-present, contact-valid, eligible, selected, and
  adapted-observed masks separate. Zero fill is transport encoding only; it is
  never measured or imputed signal.
- Froze a target-blind rule: contact score at least 0.6, noise at most 0.4,
  observed fraction at least 0.95, maximum four and minimum two channels per
  side, equal side weight, stable source-index tie break, and select-none on
  insufficient bilateral contact.
- Registered 16 fail-closed mutations spanning identity, source order,
  nonfinite observations, invalid selection, side caps and weights, zero-fill
  semantics, invented impedance/geometry, target fields, and future context.
- Seven focused contract tests pass. The complete pre-implementation suite
  passes 1,286 tests with three expected skips and 469 subtests in 34.24
  seconds wall time at 621,395,968-byte peak RSS.
- Every payload, data, target, adapter, model, training, inference, scoring,
  network, provider, stream, device, hardware, and claim counter remains zero.

Engineering capability proposed: NeuroDecodeKit can preserve and validate
contact quality, missingness, bilateral selection, and mask semantics for a
bounded synthetic ear-channel interface.

Scientific claim not established: no real ear EEG hardware signal, brain
origin, decoding accuracy, generalization, latency, home-use, or clinical
result is established.

## 2026-08-08 - Contact-Aware Ear-Channel Implementation

- Implemented the exact post-green work-order-5 synthetic boundary with lazy
  NumPy, 48 items, 16 generic bilateral channels, eight scenarios, and six
  distinct mask meanings. The source signal, source order, synthetic geometry,
  and reference-state identity remain explicit and unchanged.
- Added the fixed target-blind contact/noise/observed-fraction rule, stable
  source-index ranking, bilateral count caps, equal side totals, and explicit
  select-none status. Missing source values remain NaN; adapted transport zeros
  remain unavailable under their mask and are never called measured or imputed.
- Added deterministic array, configuration, source-order, selected-subset,
  metadata, and compressed-payload hashes; strict save/load/validation/summary
  APIs; a zero-array-open metadata inspector; two CLI commands; and exclusive
  output creation with cap, free-disk, collision, and partial-write guards.
- All 16 registered malformed fixtures fail closed. Target and unknown fields,
  future-tail dependence, payload tampering, malformed NPZ, low disk, and cap
  failures are independently covered.
- Twelve focused implementation tests pass. The pre-receipt complete suite
  passes 1,298 tests with three expected skips and 469 subtests in 34.82 seconds
  wall time at 606,126,080-byte peak RSS. With five receipt invariants included,
  the final complete suite passes 1,303 tests with three expected skips and 469
  subtests in 35.35 seconds external wall time at 614,825,984-byte peak RSS.
- A disposable probe produced a 923,980-byte NPZ and 14,894-byte sidecar,
  totaling 938,874 bytes, then removed them. One measured closeout remains
  blocked until this exact implementation commit is pushed and remotely green.

Engineering capability added: the repository can generate, hash, validate,
inspect, and reject invalid contact, missingness, bilateral selection, and
transport-mask states in a bounded synthetic ear-channel interface.

Scientific claim not established: no real ear EEG hardware signal, brain
origin, decoding accuracy, generalization, latency, device performance,
home-use, or clinical result was established.

## 2026-08-08 - Contact-Aware Ear-Channel Measured Closeout

- Exact implementation `76ccc63bdb62b7695dd12ead6ae629c3ab73bb53`
  passed push CI `31282344300` before execution: Base Python in 16 seconds and
  Optional Neuro Readers in 56 seconds.
- Exactly one CLI creation and one metadata-only CLI inspection ran in an
  automatically removed temporary directory. Both returned zero, their compact
  summaries matched, and there was no retry or post-result change.
- Runtime was 0.40 seconds, peak RSS was 55,394,304 bytes, free disk before
  execution was 46,367,866,880 bytes, and the 15,789-byte contract produced a
  923,980-byte NPZ plus a 14,894-byte sidecar under the 4 MiB cap.
- The fixture held shape `[48,16,256]`, 168,192 observed source samples, 76,800
  adapted-observed samples, 504 eligible and 300 selected channel instances,
  and exact 150/150 left/right selected counts. Forty-two items passed; six
  insufficient-bilateral items selected none.
- All 18 gates passed. The explicit inspector opened zero arrays; both generated
  files were removed. Every raw, real/public/protected, target, model, fit,
  inference, training, score, network/provider, device/hardware, and claim
  counter was zero.
- Thirty-five focused closeout checks and the complete suite pass at 1,309
  tests, three expected skips, and 469 subtests in 35.01 seconds external wall
  time at 636,846,080-byte peak RSS.
- Work order 5 is complete and consumed with no rerun. Work order 6 opens only
  the recovery-bound Loop 54-A decision packet and synthetic parser route; real
  S20 access remains separately gated Tier C.

Engineering capability added: NeuroDecodeKit now has a measured, bounded,
source-preserving contact and missingness interface for synthetic ear channels.

Scientific claim not established: no real ear EEG hardware signal, brain
origin, decoding accuracy, generalization, latency, device performance,
home-use, or clinical result was established.

## 2026-08-08 - Loop 54-A Recovery-Bound Authorization Request

- Added a current v1 decision packet without modifying the immutable
  preregistration, contract, invariant test, recovery record, or historical v0
  request.
- Bound registration `c114623`, its three exact SHA-256 and Git-blob identities,
  green pinned anchor `2232993` / CI `31132586790`, and green recovery commit
  `5915bdf` / CI `31277277711`.
- Bound completed work order 5 only as queue state. It does not authorize S20 or
  parser work.
- Froze one exact authorization sentence and the evidence order: green request,
  green decision, generated-synthetic parser qualification, green
  implementation, then one real VHDR open.
- Retained one thread, one worker, 30 seconds, 256 MiB RSS, 16,384 maximum read
  bytes, 1 MiB output, one VHDR open, one real execution, zero network bytes,
  zero new payload bytes, and no rerun.
- Every authorization field and every S20, sibling, target, model, training,
  inference, scoring, provider, hardware, and claim counter remains false or
  zero. The local S20 path was not resolved, statted, hashed, or opened.
- Fifty focused route checks passed. The authoritative project environment
  advanced the complete suite from 1,309 to 1,317 passing tests with three
  expected skips in 34.89 seconds external wall time at 605,143,040-byte peak
  RSS. Ruff 0.15.20, compileall, 90 registry JSON files, 177 local Markdown
  links, root CLI help, staged Gitleaks, and diff hygiene passed.
- One preliminary system-interpreter discovery omitted the source-layout import
  path and failed imports before substantive execution. The corrected
  base-Python lane passed 1,245 tests with 158 expected optional skips before
  the authoritative `.venv` run above.

Engineering capability proposed: NeuroDecodeKit can qualify and then execute a
strict one-file BrainVision-header compatibility check under a recovery-bound,
no-sibling, one-shot evidence order.

Scientific claim not established: no S20 path or content was accessed, so this
request establishes no header readability, EEG signal quality, trial validity,
neural advantage, decoding accuracy, generalization, latency, device, home-use,
or clinical result.

## 2026-08-08 - Loop 54-A Recovery-Bound Authorization Decision

- Verified that the maintainer's sentence exactly equals the green v1 request.
  Request commit `19813a8` passed Base Python and Optional Neuro Readers in CI
  `31283297030` before the decision was recorded.
- Added separate human and machine decision records binding the current packet,
  request, preregistration, contract, and recovery hashes and Git blobs. The
  immutable request and contract remain unchanged and retain false permission
  fields.
- Authorized generated-synthetic parser implementation only after this
  decision commit becomes remotely green. Immediate S20 stat, resolution,
  hash, open, parse, and output permissions remain false.
- Recorded the already authorized conditional real stage without activating it:
  one exact 11,705-byte VHDR open only after the implementation commit becomes
  remotely green, with no sibling touch and no rerun.
- Preserved one thread, one worker, 30 seconds, 268,435,456-byte peak RSS,
  16,384 maximum read bytes, 1,048,576 generated bytes, zero network and new
  payload bytes, and every authorization-only access counter at zero.
- Fifty-seven focused authorization/route checks passed. The complete suite
  advanced from 1,317 to 1,324 passing tests with three expected skips in 33.53
  seconds external wall time at 651,296,768-byte peak RSS.

Engineering capability authorized for testing: NeuroDecodeKit may implement
and synthetically qualify one strict, dependency-free VHDR parser after the
decision's green CI gate.

Scientific claim not established: no parser ran and no S20 path or content was
accessed, so there is no header-readability, EEG-quality, neural, decoding,
generalization, latency, hardware, home-use, or clinical result.

## 2026-08-08 - Loop 54-A Strict VHDR Parser Implementation

- Confirmed exact decision commit `2177b36f56464361bc51b2656406da7575ff1a1f`
  passed CI `31286428489`: Base Python job `93176025548` and Optional Neuro
  Readers job `93176025560` both succeeded before implementation began.
- Added a standard-library-only parser for strict declared UTF-8, UTF-8 BOM,
  and explicit Windows-1252. It rejects replacement decoding, control
  characters, missing or duplicate required declarations, unsafe sibling
  references, channel-table drift, and invalid sampling intervals.
- Added exact no-follow source validation, one descriptor open, one bounded
  read, Git-blob verification, inert sibling basenames, deterministic decimal
  sampling, ordered allowlisted channels, and explicit unavailable fields.
- Added exclusive no-overwrite output: both payloads are finalized in memory,
  the summary is created and fsynced first, and the canonical JSON ledger is
  created and fsynced last as the commit marker. No rename or deletion path was
  added.
- Added `loop54-vhdr-ledger`, dry-run by default, and
  `inspect-loop54-vhdr-ledger`. Execution requires the exact implementation
  commit, push CI run, Base Python job, Optional Neuro Readers job, clean
  tracked tree, and decision ancestry.
- Twenty-four focused parser/filesystem tests and 24 mutation subchecks pass,
  covering all 22 frozen refusal classes. Generated fixtures were temporary;
  no fixture or inspection payload is retained or committed.
- Sixty-one combined Loop 54 route and implementation tests pass with 33
  subchecks. The complete one-thread suite passes 1,351 tests, three expected
  skips, and 493 subtests in 35.10 seconds external wall time at
  670,728,192-byte peak RSS.
  Ruff, compileall, 92 registry JSON files, both command-help surfaces, the
  guarded dry run, and diff hygiene pass. Complete-suite RSS is not the future
  one-VHDR execution measurement.
- Repaired Work Order 5's consumed shared-CLI test to preserve its historical
  CLI hash while asserting its two owned commands remain in the additive CLI.
- Every S20 path stat, VHDR open/hash/parse, sibling operation, signal/marker/
  target read, model/training/inference/scoring run, network/provider/hardware
  operation, real execution, rerun, and claim-upgrade counter remains zero.

Engineering capability added: a strict, bounded, sibling-blind VHDR parser and
one-shot compatibility-ledger interface are locally synthetic-qualified.

Scientific claim not established: no S20 content was opened and no EEG signal
quality, event or trial validity, neural advantage, decoding accuracy,
generalization, latency, portable hardware, home-use, or clinical result was
established.

## 2026-08-08 - Loop 54-A Strict VHDR Consumed Result

- Confirmed exact implementation `b486fdf13d8a2293432f9dca5f3fb8ba97527be0`
  passed CI `31287819503`: Base Python job `93179736029` and Optional Neuro
  Readers job `93179736035` were green before protected access.
- Ran the one registered one-thread, one-worker invocation. It returned code
  `2` after 0.20 seconds external wall time at 24,051,712-byte peak RSS.
- Opened the exact registered VHDR once and read exactly 11,705 bytes. The
  no-follow, regular-file, size, Git-blob, and strict-decode checks passed.
- Parked at
  `L54A-F11_missing_duplicate_or_malformed_required_section_or_key` with the
  safe diagnostic `VHDR format preamble is missing`. The raw first line and
  all header values remain unpublished and unavailable.
- Wrote zero registered output files and zero registered output bytes. The
  private output root remained absent.
- Every VMRK, EEG, MAT, sibling, signal, marker, event, trial, response, key,
  sentence, label, target, cache, split, feature, model, checkpoint, inference,
  training, scoring, selection, network, download, provider, language-model,
  RW3, stream, device, hardware, release, rerun, and claim-upgrade counter was
  zero.
- The 18-gate map records 12 passed or closeout-passed gates, one failed gate,
  and five not-reached gates. L54-Q2 was not established; L54-A is consumed
  with no rerun, and Loop 54-B/C remain blocked.
- Eighty-three focused Loop 54 tests and 40 mutation subchecks pass. The final
  CI-style unittest suite passes 1,359 tests with three expected skips in 33.11
  seconds external wall time at 650,461,184-byte peak RSS.
- The final pytest suite passes 1,356 tests with three expected skips and 493
  subtests in 33.99 seconds external wall time at 658,030,592-byte peak RSS.
  This is five passing tests above the exact implementation baseline with no
  lost skip or subtest. The first full closeout pass exposed three stale queue
  assertions; those documentation expectations were advanced before the final
  pass, with no real-data rerun.
- Repository-wide Ruff, compileall, all 93 registry JSON files, root and both
  Loop 54-A CLI help surfaces, and diff hygiene pass.

Engineering capability added: NeuroDecodeKit executed one exact, bounded,
sibling-blind VHDR compatibility gate and retained a fail-closed evidence
record.

Scientific claim not established: no EEG signal, event, trial, target, or model
was accessed, and no neural advantage, decoding accuracy, generalization,
real-time, portable-hardware, home-use, or clinical result was established.

## 2026-08-09 - CML-v0 Synthetic Gate Consumed At CML-R0

- Preserved the work-order-13 evidence order: contract
  `67709a3286a33f0947d57a97bf345a26d17dae45` passed CI `31294479865`, then
  exact implementation `90fa467e5acf24a8a47eb8c96b1cb485a6a9076b` passed CI
  `31295430105` before one seed-5513 execution.
- The exact 4,535-parameter, 64-channel, 18-primitive CML-v0 completed one
  600-step AdamW fit. All 16 constructed signal-bearing check rows reached
  hand accuracy `1.0` and key accuracy `1.0`; potential, mu, and beta matching
  ablations were each largest, the hand/key marginal error was
  `5.960464477539063e-08`, future-tail causal error was zero, and checkpoint
  replay hashes matched.
- Eighteen of 19 check gates passed. The uniform common-mode mutation produced
  maximum float32 key-logit error `1.9073486328125e-6`, exceeding the frozen
  `1e-6` tolerance by `9.073486328125e-7`. The conjunction therefore parked at
  `CML-R0`; the 16 synthetic final targets stayed closed, final scoring events
  remained zero, and no rerun or post-outcome tolerance change is open.
- Descriptive controls remain visible rather than optimized away:
  peripheral-proxy-only hand accuracy was `1.0`, channel-deranged accuracy was
  `0.0`, and nonwrapping time-displaced accuracy was `1.0`. These fixture
  behaviors sharpen future controls but establish neither a real peripheral
  shortcut nor timing robustness.
- Runtime was 6.5530732499901205 seconds at 398,737,408-byte peak RSS with one
  CPU thread and worker. The 22,952-byte checkpoint and 14,419-byte report
  totaled 37,371 bytes under the 4 MiB cap. Their exact SHA-256 bindings were
  recorded, then both generated files and their empty invocation directory
  were removed.
- Synthetic source generation, one parameter-update run, 600 optimizer steps,
  two inference stages, ten prediction sets, and one check score are explicit.
  Every real/public/protected read, S20 or PhysioNet operation, network/provider
  call, pretrained-weight read, stream/device/hardware action, release, and
  claim-upgrade counter is zero.
- Thirty focused CML tests passed. The complete one-thread suite advanced from
  the 1,380-test implementation baseline to 1,386 passed tests with three
  expected skips and 493 subtests in 38.99 seconds of pytest runtime and 40.37
  seconds external wall time at 705,822,720-byte maximum suite RSS.

Engineering capability added: the exact compact CML-v0 implementation can fit,
localize, causally probe, and deterministically replay the deliberately
constructed factor suite under a strict check-before-final protocol.

Scientific claim not established: no real or protected EEG was accessed, the
synthetic conjunction failed, and no neural advantage, decoding accuracy,
brain-specific origin, generalization, real-time, portable-hardware, home-use,
assistive, or clinical result was established.

## 2026-08-09 - Tiny PhysioNet Motor Acquisition Registration

- Added an acquisition-only work-order-8 preregistration and strict machine
  contract for PhysioNet EEGMMIDB v1.0.0. The selection is exactly nine EDF
  paths from S001-S003 and runs 03/07/11, totaling 23,248,224 bytes and bound
  to nine official SHA-256 values.
- Reverified the official dataset page, checksum manifest, and MNE task mapping.
  Ten HTTP HEAD requests were made across the nine selected paths, including
  one repeated first-file probe. Every request reported HTTP 200 and transferred
  zero EDF body bytes. Exact documentation and response-header transfer bytes
  are unavailable from the research-tool receipts and are disclosed as such.
- Froze dataset version, path, size, and SHA-256 as hard identities. ETag,
  Last-Modified, and Content-Type are informational observations only. Runs
  03/07 and 11 are prospective future fit and check roles, respectively; this
  registration creates no split.
- Froze one invocation, zero payload retries, one opaque local SHA-256 pass per
  EDF, one thread and worker, 300 seconds, 268,435,456-byte peak RSS, 1,048,576
  metadata-network bytes, 33,554,432 EDF-network bytes, 67,108,864 incremental
  disk bytes, 2,147,483,648 minimum free disk bytes, and 1,048,576 combined
  receipt bytes.
- No EDF payload, `.event` file, local PhysioNet path, header, annotation,
  signal, target, cache, split, model, checkpoint, training, inference, score,
  provider, stream, device, or hardware surface was opened. Every execution
  authorization remains false pending the separate exact Tier C sequence.
- Twelve focused contract tests pass. The complete pytest suite advances from
  the 1,386-test pre-change baseline to 1,398 passed tests with three expected
  skips and 493 subtests in 40.41 seconds of pytest runtime and 41.79 seconds
  external wall time at 677,920,768-byte maximum suite RSS.
- The CI-style unittest command passes 1,401 tests with three expected skips in
  37.594 seconds internal and 38.56 seconds external wall time at
  666,697,728-byte maximum suite RSS. These suite-wide RSS values include the
  complete historical test harness and are not acquisition-execution metrics.
- Repository-wide Ruff 0.15.20, compileall, all 97 registry JSON files, and diff
  hygiene pass. An initial file-targeted Ruff command mistakenly included the
  JSON contract and therefore reported JSON booleans as undefined Python names;
  the canonical repository-wide Ruff invocation passed without findings.
- The three new source artifacts total 45,351 bytes. No payload, cache,
  inspection output, fixture, or execution receipt was generated or retained.
  The unrelated untracked tracker inspection NDJSON was not touched.

Engineering capability proposed: NeuroDecodeKit can acquire and opaque-verify
one tiny exact public motor-EEG bundle under deterministic identity, storage,
network, access-order, and no-retry controls after the remaining green and
authorization gates.

Scientific claim not established: no EDF payload was opened, so this
registration establishes no EDF readability, event correctness, signal
quality, motor effect, neural advantage, model accuracy, generalization,
real-time behavior, portable hardware, home use, assistive value, or clinical
result.

## 2026-08-09 - PhysioNet Motor Acquisition Exact Tier C Request

- Confirmed registration `2a7b4188553e221133d788a081b838dbbb9f41bb`
  passed Base Python job `93215490492` and Optional Neuro Readers job
  `93215490501` in CI `31301730612` before preparing the request.
- Added a human authorization packet, all-false machine request, and
  self-hashing invariant test. They bind the registration commit and exact
  SHA-256 and Git blob identities of the preregistration, contract, contract
  test, packet, and request test without changing the registered contract.
- Froze one exact user sentence with two later green gates: the separate
  authorization-only decision must be remotely green before fixture-only
  implementation, and the exact implementation must be remotely green before
  one no-retry acquisition invocation.
- Preserved the exact nine files, 23,248,224 bytes, nine official SHA-256
  values, one opaque local hash pass per file, one thread and worker, 300
  seconds, 256 MiB RSS, 1 MiB metadata network, 32 MiB EDF network, 64 MiB
  incremental disk, 2 GiB minimum free disk, and 1 MiB receipt limits.
- Every implementation, fixture qualification, metadata recheck, EDF payload,
  local path, parse, sidecar, signal, target, cache, split, model, training,
  inference, score, provider, hardware, rerun, work-order-9, and claim
  authorization remains false in the request. Preparing it caused no new
  metadata or payload operation, so the registration counters remain exact.
- Twenty-two combined registration/request tests pass. The full one-thread
  pytest suite advances from the 1,398-test registration baseline to 1,408
  passed tests with three expected skips and 493 subtests in 40.27 seconds of
  pytest runtime and 41.44 seconds external wall time at 677,740,544-byte
  maximum suite RSS.
- The CI-style unittest command passes 1,411 tests with three expected skips in
  37.721 seconds internal and 38.63 seconds external wall time at
  673,005,568-byte maximum suite RSS. These complete-suite measurements are
  verification overhead, not future acquisition-execution measurements.
- Repository-wide Ruff 0.15.20 and compileall pass. The packet, machine request,
  and request test total 33,909 bytes. No payload, cache, fixture, inspection
  output, execution receipt, or experiment artifact was generated or retained.

Engineering capability proposed: NeuroDecodeKit now has a byte-bound,
self-checking Tier C decision surface for one tiny public motor-EEG acquisition.

Scientific claim not established: the request opened no EDF payload and
establishes no readability, event correctness, signal quality, motor effect,
neural advantage, model accuracy, generalization, real-time behavior,
portable-hardware performance, home use, assistive value, or clinical result.

## 2026-08-09 - PhysioNet Motor Acquisition Authorization Decision

- Verified request `f6eb577fdd8c168a4af229248dc56960e3ba75d8`
  is remotely green: Base Python job `93216583586` and Optional Neuro Readers
  job `93216583625` passed in CI `31302161647`.
- Recorded the maintainer's exact registered sentence in separate human and
  machine decision artifacts without modifying the immutable contract,
  preregistration, packet, or all-false request.
- Bound request SHA-256
  `77d2d1e7bd3560f2b60feb977c2826190b4ee7fd12144c7698beafb441626a76`
  and contract SHA-256
  `6c81dac6a818f13c49f5df25c540e9d3ef65f21b56ecb1a5b5d15d4a3dc819d3`.
- Authorized fixture/mock implementation only after this decision commit is
  remotely green, and the one real acquisition only after the exact
  implementation commit is remotely green.
- Preserved exactly nine files, 23,248,224 bytes, one no-retry invocation, one
  opaque local hash pass per EDF, and all resource limits. No source metadata,
  EDF, local PhysioNet path, parser, event, signal, target, split, model,
  provider, or experiment operation occurred.
- Ten focused decision checks pass. One GitHub Actions API read verified parent
  CI; every source-dataset and experiment counter remains zero.
- The maintainer's separate 10 GB future data ceiling was recorded as unused
  prospective headroom and does not amend this acquisition.
- Thirty-two combined registration, request, and decision checks pass. The
  complete one-thread suite advances from the 1,408-test request baseline to
  1,418 passed tests with three expected skips and 493 subtests in 68.42
  seconds under the unrestricted local test lane.
- The first complete-suite attempt reached 1,417 passing tests and one failure
  because the managed sandbox denied Python's forkserver permission to bind a
  temporary Unix socket. The same exact tree and command passed outside that
  sandbox restriction; no code or test was changed from the failure.
- Repository-wide Ruff 0.15.20 and all registry JSON validation pass before the
  decision commit.

Engineering capability authorized for testing: one dependency-light,
hash-bound implementation and one exact public-data invocation may proceed
through the ordered green gates.

Scientific claim not established: this decision is not an EDF or EEG result
and establishes no readability, event correctness, signal quality, motor
effect, neural advantage, model accuracy, generalization, real-time behavior,
portable hardware, home use, assistive value, or clinical result.

## 2026-08-09 - PhysioNet Motor Acquisition Fixture-Only Implementation

- Verified authorization decision `00b91ed` passed Base Python job
  `93322699209` and Optional Neuro Readers job `93322699259` in CI
  `31344104565` before implementation began.
- Added `src/neurodecodekit/datasets/physionet_motor_acquisition.py`, a
  standard-library-only, fail-closed executor with no EDF reader and no heavy
  dependency.
- Added `neurodecode physionet-motor-acquire`. Its default plan verifies the
  frozen contract and decision but performs no registered path stat and no
  network request. `--execute` requires the exact current implementation
  commit, CI run, and both successful job IDs.
- Implemented exact three-document metadata GETs, nine EDF HEADs, no redirects,
  no retries, strict version/DOI/license/task/path/size/checksum checks, bounded
  binary transfer, one no-follow opaque local SHA-256 pass per EDF, exact
  membership, atomic complete-bundle promotion, and bounded machine/human
  receipts.
- Added 23 dedicated adversarial executor tests. Fifty-five combined
  registration/request/decision/executor tests and 68 focused implementation
  plus compatibility checks pass. All payloads and responses are generated or
  mocked; invalid UTF-8 proves that the transfer path does not decode content.
- Repaired one historical CML test that treated the shared CLI as permanently
  immutable. Its consumed registry and result were not changed; their old CLI
  and registry-test hashes remain explicit historical evidence and the current
  CML command is still asserted.
- The first complete-suite run exposed that historical assertion and one
  transient five-second isolated-worker timeout. The unchanged worker test
  passed focused replay. The final full one-thread run passed 1,448 tests with
  three expected skips and 493 subtests in 44.21 seconds internal and 45.73
  seconds external wall time at 598,622,208-byte peak suite RSS.
- The suite RSS includes optional ML imports and is not an acquisition metric.
  The future standard-library executor independently enforces 300 seconds,
  268,435,456-byte RSS, 1 MiB metadata, 32 MiB EDF network, 64 MiB disk, and
  1 MiB receipt caps.
- No source metadata, registered PhysioNet path, EDF payload, sidecar, header,
  annotation, event, signal, task, target, label, channel, cache, split, model,
  training, inference, scoring, provider, stream, device, hardware, release,
  work-order-9, or rerun operation occurred. Retained generated experiment
  bytes remain zero.
- The user's 10 GB data allowance remains unused future headroom and does not
  alter the exact 23,248,224-byte contract. The unrelated tracker inspection
  NDJSON remains untouched.

Engineering capability added: one strict standard-library path can reverify,
acquire, opaque-hash, atomically promote, and privately receipt the exact
registered nine-EDF bundle after the ordered remote-green gates.

Scientific claim not established: fixture-only implementation establishes no
EDF readability, event correctness, signal quality, motor effect, neural
advantage, model accuracy, unseen-person generalization, real-time latency,
portable hardware, home use, assistive value, or clinical result.

## 2026-08-09 - One PhysioNet Motor Acquisition Consumed And Passed

- Verified exact implementation `92760ce7e3123058f15127b9afd8d5e4bae75321`
  passed Base Python job `93326279510` and Optional Neuro Readers job
  `93326279396` in CI `31345401581` before any registered local-path or source
  operation.
- Consumed the one no-retry invocation under one CPU thread, one worker, and
  one numerical job. No restart, retry, substitution, wildcard, alternate
  host, or additional file was used.
- All 12 acceptance gates passed. Three registered document GETs plus nine EDF
  HEADs consumed 442,178 response-body bytes and matched version, DOI, public
  availability, license, run mapping, exact paths, exact sizes, and all nine
  official SHA-256 values before payload transfer.
- Nine EDF GETs transferred exactly 23,248,224 bytes. Each local file received
  one and only one opaque sequential size/SHA-256 pass; all nine observed
  hashes matched. The complete nine-file bundle promoted atomically.
- Runtime was 50.682373 seconds, peak RSS 55,181,312 bytes, incremental disk
  peak 28,327,635 bytes, free disk 65,470,033,920 bytes before and
  65,443,667,968 after, and private receipt output 16,083 bytes. Every cap
  passed.
- Machine and human receipt hashes are recorded in the sanitized result
  registry. The 10,141-byte machine manifest, 5,942-byte human receipt, and
  23,248,224-byte EDF bundle remain Git-ignored and were not committed or
  uploaded.
- Every header, annotation, event, sidecar, signal, task, target, label,
  channel, montage, reference, geometry, sampling, quality, cache, split,
  model, checkpoint, training, inference, scoring, provider, stream, device,
  hardware, publication, retry, rerun, and work-order-9 counter stayed zero.
  End-to-end latency remains unmeasured.
- Work order 8 is complete and consumed with no rerun. Work order 9 remains
  gated. The user's 10 GB allowance remains future headroom and did not enlarge
  this invocation. The unrelated tracker inspection NDJSON remains untouched.
- Thirty-seven focused closeout tests pass. The complete post-result one-thread
  suite passes 1,455 tests with three expected skips and 493 subtests in 50.76
  seconds internal and 52.07 seconds external wall time at 665,387,008-byte
  peak suite RSS. That suite RSS is optional-ML verification overhead, not the
  measured acquisition RSS.

Engineering capability added: NeuroDecodeKit acquired and opaque-verified one
exact, isolated nine-file public EEGMMIDB bundle under the registered identity,
access-order, network, runtime, memory, storage, and no-retry controls.

Scientific claim not established: no EDF content was parsed and no event,
signal, target, model, or score was produced, so this result establishes no
motor-EEG effect, neural advantage, decoding accuracy, unseen-person
generalization, real-time latency, portable hardware, home use, assistive
value, or clinical result.

## 2026-08-09 - Work Order 9 Three-Axis Positive-Control Registration

- Re-audited the official PhysioNet EEGMMIDB task description, the MNE EEGBCI
  loader and CSP example, maintained pyRiemann 0.12 documentation, causal SciPy
  SOS filtering, motor ERD/ERS physiology, and primary ocular/muscle confound
  evidence.
- Replaced the vague classifier-only work-order boundary with a conjunctive
  prediction + physiology + confound protocol. The class-correlated left/right
  visual cue is now an explicit claim limiter rather than a buried caveat.
- Bound only the acquired S001-S003 runs 03/07/11 inventory: nine files,
  23,248,224 bytes, 90 fit/selection events expected from runs 03/07, and 45
  sealed final events expected from run 11. No additional data is requested.
- Froze two selection candidates, fixed four-component CSP-LDA and regularized
  Riemannian MDM, plus a nonselecting low-frequency shrinkage-LDA comparator.
  Selection is run-grouped in both 03-to-07 directions and never sees run 11.
- Froze 12 final prediction sets, causal 8-30 Hz filtering, explicit central
  and frontal/occipital channel sets, mu/beta physiology, a 30/45 correct gate,
  balanced-accuracy and permutation thresholds, and ordered `WO9-V0` through
  `WO9-V3` verdicts.
- Required a pushed remotely green hash-only prediction freeze before one
  isolated delivery and score of the 45 run-11 targets. Individual targets,
  predictions, probabilities, and participant outcomes remain private and
  uncommitted.
- Capped a future execution at one thread/worker/job, 1,800 seconds,
  805,306,368-byte peak RSS, 67,108,864 private generated bytes, 40 fits, 64
  prediction sets, zero network/new payload, one final score, and no rerun.
- Added nine invariant tests for all-false current authorization, exact source
  hashes and inventory, target firewall, causal view, model order, three-axis
  conjunction, remote-green freeze, resources, and claim ceiling.
- This planning pass performed zero local PhysioNet stats/opens, EDF reads,
  target/model operations, downloads, provider calls, or hardware operations.
  The unrelated tracker inspection NDJSON remains untouched.

Engineering capability added: a strict prospective route now exists from the
acquired public EEG inventory to one falsifiable, prediction-freeze-protected
motor positive control.

Scientific claim not established: no EDF content or outcome was observed, so
no motor-task EEG effect, physiology, neural advantage, generalization,
decoding accuracy, latency, device, or human-benefit result exists yet.

## 2026-08-09 - Work Order 9 Exact Tier C Request Prepared

- Verified registration `3c00557ecfb09c80e30843589ae295a09feec97c` passed
  Base Python job `93330354031` and Optional Neuro Readers job `93330354047` in
  CI `31346882592` before creating the request.
- Bound the primary-source research, preregistration, contract, invariant test,
  commit, Git blobs, SHA-256 values, CI run, and both required job IDs.
- Added one exact conditional sentence covering a fixture-only implementation,
  a narrow isolated optional classical environment, one nine-EDF real
  execution, one remotely green hash-only prediction freeze, and one final
  target delivery/score.
- Kept every authorization flag false and every local path, EDF, target,
  dependency, derivative, fit, prediction, freeze, score, network, provider,
  hardware, retry, and rerun counter at zero.
- Added eight request tests for exact all-false posture, green proof identity,
  artifact hashes and blobs, sentence identity, nonexpansion, ordered gates,
  resource caps, and the `WO9-V3` ceiling. Seventeen combined work-order-9
  registration/request tests pass.
- The request must itself be committed, pushed, and remotely green before the
  exact sentence can become a separate decision. No implementation or real
  access may begin from this packet.

Engineering capability added: NeuroDecodeKit now has an exact, reviewable
decision surface for one bounded public EEG positive-control execution.

Scientific claim not established: a permission request contains no EDF
observation or result and establishes no motor-task, neural, generalization,
decoding, latency, device, or human-benefit evidence.

## 2026-08-09 - Work Order 9 Exact Tier C Decision Recorded

- Verified request `c62b10a6e9dae8d92e5ff54d17403e1054a0ac76`
  passed Base Python job `93331241434` and Optional Neuro Readers job
  `93331241411` in CI `31347209691`.
- Accepted the maintainer's exact registered sentence, including the frozen
  limit of 64 target-blind prediction sets, into separate human and machine
  authorization records. The preregistration, contract, packet, and all-false
  request remain byte-identical historical snapshots.
- Bound the parent commit, CI run and jobs, contract/request/packet SHA-256 and
  Git-blob identities, exact nine-file inventory, four remote-green gates,
  installation and execution resources, one score, no retry/rerun, and the
  unchanged `WO9-V3` claim ceiling.
- Added ten decision invariants covering exact sentence identity, green proof,
  immutable prior snapshots, authorized and forbidden surfaces, dataset scope,
  access order, resource parity, zero current operations, and claim limits.
- This milestone made one GitHub CI verification call and performed zero
  dependency installs, implementation operations, local PhysioNet stats,
  opens, hashes, parses, EDF reads, derivative or split operations, fits,
  inferences, freezes, target deliveries, scores, provider calls, or hardware
  operations. The unrelated tracker inspection NDJSON remains untouched.

Next gate: commit and push this exact decision and require both CI jobs green.
Only then may generated-fixture-only implementation and the isolated optional
environment begin. The implementation must separately become remotely green
before any local PhysioNet operation.

Engineering capability authorized for testing: one leakage-resistant,
resource-bounded public EEG motor positive control may proceed through the
ordered decision, implementation, prediction-freeze, and scoring gates.

Scientific claim not established: this decision contains no EDF observation,
physiology, prediction, or score and establishes no motor-task EEG effect,
brain-specific origin, generalization, decoding, latency, device, or human-
benefit result.

## 2026-08-09 - Work Order 9 Fixture-Only Implementation Qualified

- Verified authorization-only commit
  `da9399c4290fc2be81834ed1036a6bede5f52154` passed Base Python job
  `93334251403` and Optional Neuro Readers job `93334251379` in CI
  `31348287824` before implementation began.
- Added a lazy-import sequential MNE EDF reader, exact 64-channel and 160 Hz
  validation, causal CAR/SOS preprocessing, strict 90-row runs-03/07 fit
  derivative, target-free 45-row run-11 prediction derivative, and separate
  sealed 45-target scorer input.
- Added fixed CSP-LDA and regularized Riemannian MDM family selection using
  runs 03/07 only, the non-selection low-frequency comparator, 12 mandatory
  prediction/control conditions, 33 exact fits, 45 target-blind model
  inferences, and three train-only prior fits.
- Added per-condition prediction hashes, private payload and derivative hashes,
  source-manifest, split, configuration, implementation-registry, and tracked-
  file bindings in the aggregate public freeze. The scorer verifies every hash
  before it may open the sealed target artifact.
- Added two dry-run-first CLI commands, fail-closed current-HEAD and CI proof
  checks, one-thread/resource monitors, exclusive outputs, one-shot consumed
  markers, exact path guards, and aggregate-only scoring.
- Added a narrow `classical` optional extra while leaving base dependencies
  empty. One isolated environment qualified NumPy `2.5.2`, SciPy `1.18.0`,
  MNE `1.12.1`, scikit-learn `1.9.0`, and pyRiemann `0.12` in 7.24 seconds,
  about 55.8 MiB of package transfer, 205,276 KiB retained disk, and
  55,279,616-byte peak RSS.
- The final generated seed-5509 roundtrip used nine runs and 135 events,
  selected CSP-LDA, made 33 fits and 45 target-blind inferences, froze 12 sets,
  and passed in 8.961233 seconds at 327,647,232-byte peak RSS with 20,825,424
  generated bytes. Real-data, real-target, and network reads were zero. The
  disposable output was inspected and removed.
- The focused matrix passed 17 checks with two expected optional skips in the
  broad environment and all 19 checks in the isolated environment. Final
  complete suites passed 1,499 of 1,504 tests with five expected skips and
  1,455 of 1,489 tests with 34 expected skips, respectively.
- The target firewall is described precisely as a function and artifact
  boundary: extraction parses run-11 annotations once to create the sealed
  file, while the model stage opens only fit and target-free prediction
  derivatives. It is not represented as an operating-system sandbox.
- No registered PhysioNet path, private acquisition manifest, EDF, real
  header, annotation, signal, target, derivative, model, prediction, freeze,
  score, provider, device, or hardware operation occurred. The unrelated
  tracker inspection NDJSON remains untouched.

Next gate: commit and push this exact implementation and require both CI jobs
green. Only then may the one no-network nine-EDF target-blind execution begin.
Even a successful execution cannot score until its aggregate prediction-freeze
ledger is separately committed, pushed, and remotely green.

Engineering capability added: NeuroDecodeKit now has the exact bounded reader,
target firewall, fixed classical protocol, controls, prediction freezer, and
aggregate scorer needed to run the preregistered public motor positive control.

Scientific claim not established: generated-fixture qualification establishes
no real EEG readability, motor-task prediction, motor physiology, neural
effect, brain-specific origin, unseen-person generalization, typing or language
decoding, latency, portable hardware, home use, assistive value, or clinical
utility.

## 2026-08-09 - Work Order 9 Target-Blind Prediction Freeze Created

- Verified exact implementation
  `52b9b15a64972a285efbe630f49600727e836983` passed Base Python job
  `93343718364` and Optional Neuro Readers job `93343718355` in CI
  `31351728650` before real access.
- Consumed the single authorized no-network target-blind execution. The private
  acquisition manifest opened once; all nine registered EDFs received one
  size/SHA-256 pass and one MNE semantic parse with exact 64-channel, 160 Hz,
  T0/T1/T2, geometry, finite-signal, and 15-task-event gates.
- Accepted all 135 task events with zero exclusion or substitution. Created 90
  runs-03/07 fit rows, 45 target-free run-11 signal rows, and one separately
  sealed 45-target scorer input.
- Selected CSP-LDA using only runs 03/07, made 33 classical fits, 45 target-
  blind model inferences, three train-only prior fits, and all 12 mandatory
  prediction/control sets.
- Bound every condition to a separate SHA-256, plus the private payload,
  derivatives, source manifest, split, configuration, implementation registry,
  tracked source hashes, dependencies, operation counts, and resources. The
  aggregate freeze contains no individual ID, prediction, probability, target,
  label, participant metric, or participant outcome.
- The execution finished in 3.054760 seconds at 460,734,464-byte peak RSS with
  20,852,059 private generated bytes. Network and new payload bytes, final-
  target deliveries, scores, additional files, sidecars, retries, and reruns
  were all zero.
- The public freeze file SHA-256 is
  `3c100daa8a6a2816ce4270c9e32cbdcc4cd30d70d1c255e37596c2ca6f665de4`;
  its internal canonical hash is
  `2b817b5273b6361d0636b7534f2744419b45a521e96fb94fdbe1ef4731f6292b`.
- Twenty-seven focused checks passed with two expected optional skips. The
  complete broad suite ran 1,512 tests with five expected skips, and the
  isolated classical suite ran 1,497 with 34 expected skips.
- The private execution root remains Git-ignored and was not inspected after
  execution. The unrelated tracker inspection NDJSON remains untouched.

Next gate: commit and push the aggregate freeze, tests, documentation, and
status updates, then require Base Python and Optional Neuro Readers to pass at
that exact commit. Do not open or score the sealed targets before that remote-
green gate. No rerun is authorized.

Engineering capability added: one real target-blind public EEG execution is
now fully hash-frozen without publishing individual protected output.

Scientific claim not established: no final target has opened or been scored,
so this milestone establishes no motor-task accuracy, neural effect,
motor-compatible physiology, brain-specific origin, generalization, decoding,
latency, device, assistive, or clinical result.

## 2026-08-09 - Work Order 9 Final Score Consumed

- Verified freeze `01eeff6e9a5ead1790e0f91aa52a443402eb397c` passed Base
  Python job `93345130576` and Optional Neuro Readers job `93345130569` in CI
  `31352250838` before target access.
- Opened the same sealed 45-target artifact once, verified every private
  payload and per-condition prediction hash, computed aggregate-only metrics,
  and applied the frozen router without changing a model, condition,
  threshold, exclusion, or claim rule.
- The selected 8-30 Hz CSP-LDA primary reached 27/45 correct, 0.603755 pooled
  balanced accuracy, 0.592262 macro-participant balanced accuracy, and
  `p=0.137390`. It beat the 0.500 no-signal prior but failed the 30-correct,
  0.65 pooled, 0.60 macro, and `p<=0.05` conjunction. The registered verdict
  is `WO9-V1`.
- The prespecified non-selection 0.5-4 Hz shrinkage-LDA comparator reached
  36/45, 0.800395 pooled balanced accuracy, 0.800595 macro-participant
  balanced accuracy, minimum-participant 0.732143, all three participants
  above chance, and `p=0.000183`.
- The low-frequency result is valid held-out task-information evidence, not a
  retrospectively promoted primary. The visually lateralized cue, unavailable
  EOG/EMG, and failed localization/physiology conjunction leave cue, ocular,
  movement, and distributed slow-potential explanations open.
- Motor physiology had the registered negative direction in two participants
  and pooled effect `-0.083918`, but failed at `p=0.108337`. Nine of ten
  confound components passed; central-minus-frontal/occipital failed because
  central BA was 0.534585 versus 0.624506 for the proxy.
- Total registered runtime was 9.661659 seconds, peak RSS was 460,734,464
  bytes, private output was 20,852,334 bytes, and public result output was
  10,443 bytes. One target delivery and one score occurred; network/new
  payload, retry, and rerun counts were zero. Every resource gate passed.
- No individual prediction, probability, target, participant metric, or
  participant outcome is public. The private execution root remains
  Git-ignored and must not be reopened, committed, or published.
- Forty-five focused checks passed with two expected optional skips. The final
  complete broad suite ran 1,521 tests with five expected skips, and the
  isolated classical suite ran 1,506 with 34 expected skips.

Next route: preserve `WO9-V1` and the strong secondary low-frequency lead.
Any new experiment must use untouched participants/runs, preregister the slow-
potential hypothesis prospectively, add cue/ocular/localization controls, and
obtain a separate real-data decision. Work order 9 itself has no rerun.

Engineering capability added: NeuroDecodeKit completed one end-to-end,
prediction-freeze-protected, aggregate-scored public EEG experiment under its
exact resource and leakage contract.

Scientific result established: the prespecified causal 0.5-4 Hz whole-head
comparator recovered held-out left/right task information at 0.800 balanced
accuracy and `p=0.000183` in this three-person dataset.

Scientific claim not established: the selected primary, motor-physiology, and
central-localization conjunctions failed, so brain-specific motor origin,
unseen-person generalization, typing, language or thought decoding, real-time
performance, portable hardware, home use, assistive benefit, and clinical
utility remain unestablished.

## 2026-08-09 - WO9R Low-Frequency Confirmation Research Frozen

- Converted the strong prespecified Work Order 9 `0.5-4 Hz` secondary result
  into a new prospective hypothesis without reopening or rerunning S001-S003.
- Selected the contiguous untouched S004-S015 cohort and six paired unilateral
  runs per participant: execution `03/07 -> 11` and imagery `04/08 -> 12`.
  The candidate inventory is 12 participants, 72 EDFs, 720 expected fit events,
  and 360 expected sealed-final events; exact paths/sizes/hashes are not yet
  frozen and no payload was requested.
- Carried forward one unchanged primary template: causal continuous-run
  `0.5-4 Hz` SOS, all-channel common-average reference, `+1` to `+3` second
  decision window, four temporal means plus one slope per channel, and fixed
  shrinkage-LDA `0.1`. No selection, larger model, foundation model, or LLM is
  part of the study.
- Added native execution, native imagery, bidirectional task transfer,
  participant-level exact tests, central low-frequency lateralization, and
  frontal/occipital/ocular-sensitive, early/pre-cue, timing, no-signal, label,
  displacement, channel, and hemisphere controls.
- Added a five-route `WO9R-R0` through `WO9R-R4` ceiling. Even the maximum route
  remains a motor-compatible within-dataset EEG task effect, not brain-specific
  origin or independent-team replication.
- Added one machine research registry and ten invariants covering all-false
  authorization/access counters, immutable inherited evidence, disjoint cohort
  identity, exact model template, four prediction questions, controls,
  participant-level gates, router, resources, and tracker synchronization.
- This pass opened no local PhysioNet bundle or private Work Order 9 artifact,
  downloaded no EDF, and performed zero header/event/signal/target reads,
  splits, fits, inferences, scores, provider calls, or hardware operations.
  Exact public web-research transfer bytes are unavailable; EDF payload bytes
  are zero. The unrelated tracker inspection NDJSON remains untouched.

Next gate: commit, push, and require both CI jobs green. Then prepare only the
exact public-metadata inventory, preregistration, and all-false Tier C request.
Real acquisition and execution remain unauthorized.

Engineering capability added: the project now has a falsifiable and bounded
cohort-confirmation/localization design for its strongest real EEG lead.

Scientific claim not established: no new participant payload, target, model,
prediction, or score was accessed, so no cohort replication or neural claim
was added.

## 2026-08-10 - WO9R Exact Preregistration Green And Request Prepared

- Retrieved exact public metadata without requesting an EDF URL: twelve
  official PhysioNet S3 `ListObjectsV2` bodies plus the official v1.0.0
  checksum manifest. The 13 retained bodies total 340,703 bytes. EDF HEAD/GET
  requests and EDF body bytes were zero.
- Froze exactly 72 S004-S015 EDF paths for runs 03/04/07/08/11/12, totaling
  184,252,032 bytes, with one official SHA-256 per file and canonical expanded
  inventory hash
  `41906e8c74cafdcaa99354baab8acd4927127a73e7454939429dbca2a8c03dad`.
- Froze execution `03/07 -> 11`, imagery `04/08 -> 12`, 720 expected fit rows,
  360 jointly sealed final rows, one exact `0.5-4 Hz` shrinkage-LDA primary,
  144 participant-specific fit ceilings, 18 conditions, 216 target-blind
  participant-condition prediction sets, literal controls, participant-level
  exact tests, and `WO9R-R0` through `WO9R-R4`.
- Documented the target firewall honestly: the reader will necessarily
  materialize annotations, while the firewall isolates final labels from all
  predictive, selection, threshold, channel, and normalization code. It is not
  represented as a physical-never-opened or operating-system boundary.
- Registration commit `716e5432498052b78cb799c9f4e3bfbae68e3ad2` passed
  Base Python job `93351737101` and Optional Neuro Readers job `93351737088`
  in CI `31354565966` before the all-false request was prepared.
- Added a human authorization packet and machine request binding that exact
  commit, CI proof, artifact hashes, 184,252,032-byte acquisition cap, existing
  dependency identities, fixture-first implementation, one-shot acquisition,
  one target-blind analysis, combined prediction freeze, and one combined
  360-target score. Every implementation, dependency, metadata-reverification,
  EDF, local path, model, target, cleanup, rerun, and claim flag remains false.
- Thirty-eight focused WO9R checks pass. The complete dependency-light suite
  passes 1,488 tests with 168 expected skips, and the retained classical
  environment passes 1,544 tests with 34 expected skips. These are exact
  12-test increases over the green registration baselines, with no prior test
  lost. Ruff 0.15.20, compileall, all registry JSON parsing, and diff checks
  pass.
- No local PhysioNet path, private Work Order 9 artifact, EDF, header,
  annotation, sample, target, channel, geometry, dependency installer,
  derivative, fit, inference, prediction, score, provider, stream, device, or
  hardware operation occurred. The unrelated tracker inspection NDJSON remains
  untouched.

Next gate: commit and push this all-false request and require both CI jobs green.
Only then may the exact sentence in the packet be accepted into a separate
authorization-only decision commit. Implementation and every Tier C operation
remain closed until that decision also becomes remotely green.

Engineering capability added: the project now has an exact, metadata-bound,
resource-bounded authorization surface for one twelve-person low-frequency
execution/imagery confirmation with a combined final-target firewall.

Scientific claim not established: no selected EDF or target was opened and no
model was run, so the request adds no cohort confirmation, brain-specific
effect, generalization, decoding, latency, hardware, or human-benefit evidence.

## 2026-08-10 - WO9R Short-Form Packet-Bound Decision Prepared

- Verified request commit `580708fa1f24772a2f9d7cfd572a421b860a1f14`
  remotely green in CI `31355270896`: Base Python job `93353672957` and
  Optional Neuro Readers job `93353672996` both passed.
- Recorded the maintainer's actual short-form instruction verbatim instead of
  pretending the long packet sentence was typed. The message immediately
  followed the named WO9R packet, commit, CI, and decision gate and therefore
  incorporates only that immutable packet by reference.
- Added a fail-closed short-form packet rule: exactly one active green packet,
  immediate named context, unambiguous approval, actual-word preservation,
  immutable hash binding, separate decision commit, and remote-green evidence
  are all mandatory. Short form cannot expand scope.
- Preserved every registered limit: 72 S004-S015 EDFs and 184,252,032 bytes,
  exact runs and targets, fixed `0.5-4 Hz` participant-specific LDA, 18
  conditions, at most 144 fits, exactly 216 target-blind inferences for a valid
  freeze, one combined target delivery/score, one thread/worker/job, and zero
  retry, rerun, or post-target update.
- Eleven new decision invariants pass, including actual-message hash,
  non-fabrication, immutable artifact hashes, green request proof, fail-closed
  short-form conditions, exact scope/resources, ordered gates, zero operation
  counters, and claim ceiling.
- The complete dependency-light suite passes 1,499 tests with 168 expected
  skips; the retained classical environment passes 1,555 tests with 34 expected
  skips; and the broad optional environment passes 1,570 tests with five
  expected skips when its registered forkserver test is run outside the macOS
  sandbox. Each total is exactly 11 tests above the green request baseline.
- This decision-only pass made no metadata or EDF request; statted or opened no
  local PhysioNet path; read no header, annotation, sample, target, channel, or
  geometry; and ran no installer, implementation, derivative, fit, inference,
  freeze, score, provider, stream, device, or hardware operation. The unrelated
  tracker inspection NDJSON remains untouched.

Next gate: commit and push this decision-only milestone and require both CI jobs
green. Only then may generated-fixture and mocked-transport implementation
begin. Real acquisition remains closed until that exact implementation is also
committed, pushed, and remotely green.

Engineering capability authorized for testing: one exact, resource-bounded,
target-firewalled twelve-person confirmation of the WO9 low-frequency lead may
proceed through the registered green gates.

Scientific claim not established: this decision contains no EEG observation,
prediction, or score and establishes no new task effect, brain-specific origin,
generalization, decoding, latency, hardware, or human-benefit result.

## 2026-08-10 - WO9R Exact Implementation Fixture Qualified

- Verified packet-bound decision commit
  `1efeac7f0b7b316bb94effb1a2eeeb1bbf99f50a` remotely green in CI
  `31355944651`: Base Python job `93355535398` and Optional Neuro Readers job
  `93355535361` passed before implementation began.
- Added a standard-library acquisition executor with exact 15-document metadata
  reverification, 72 allowlisted sequential payload requests, no redirects or
  retries, one local size/SHA-256 pass per EDF, symlink-parent refusal, bounded
  receipts, disk/RSS/time checks, atomic complete-bundle promotion, and cleanup
  limited to invocation-created temporary files. It imports no MNE or EDF
  reader.
- Added strict sequential EDF interpretation for S004-S015 runs
  03/04/07/08/11/12: exact 64-channel order, standard geometry, 160 Hz,
  T0/T1/T2 only, 15 task events per file, all-channel common-average reference,
  causal continuous-run 0.5-4 Hz SOS filtering, and explicit four-bin plus
  slope features for both one- and two-second windows.
- Added a function-and-artifact target firewall: 720 labeled fit rows, 360
  target-free prediction rows, and one separately sealed 360-target scorer
  input. Predictive code binds event, subject, run, split, source, configuration,
  derivative, private-payload, and all 216 participant-condition prediction
  hashes without reading the sealed target artifact.
- Added the exact twelve participant-specific templates per participant, 144
  total parameter-update fits, 18 condition families, 216 target-blind model
  inference runs/prediction sets, 3,240 private predictions, aggregate public
  freeze, participant-level exact tests, physiology/localization controls, and
  frozen `WO9R-R0` through `WO9R-R4` scorer.
- Corrected one-shot ordering before any real execution: the analysis consumed
  marker precedes the first bundle inspection, and the scoring consumed marker
  precedes the first private/target-free/sealed hash or open. Any later failure
  parks without retry.
- Added three dry-run-first CLI commands:
  `physionet-low-frequency-acquire`, `physionet-low-frequency-cohort`, and
  `score-physionet-low-frequency-cohort`. CI now exercises their help surfaces.
- One measured generated-only qualification completed 72 runs and 1,080 events,
  144 fits, 216 target-blind inferences, and 216 prediction sets in 12.083017
  seconds at 260,784,128-byte peak RSS with 4,215,687 generated bytes. Network,
  real-data, and real-target reads were zero. The generated router returned
  `WO9R-R3`, which is interface evidence only. Generated files were removed.
- Twenty-nine focused acquisition, analysis, and implementation tests pass in
  the exact NumPy 2.5.2, SciPy 1.18.0, MNE 1.12.1, scikit-learn 1.9.0, and
  pyRiemann 0.12 environment. They include malformed metadata, payload, cache,
  freeze, and private-prediction cases; deterministic replay; target leakage;
  exact counts; caps; symlinks; aggregate-only output; and access ordering.
- No real metadata reverification, EDF request, payload byte, local PhysioNet
  stat/open, EDF hash/parse, header, annotation, signal, target, real derivative,
  real fit, real inference, freeze, target delivery, score, retry, rerun,
  provider, stream, device, hardware, or claim operation occurred. The
  unrelated tracker inspection NDJSON remains untouched.

Next gate: commit and push this exact implementation and require Base Python
and Optional Neuro Readers green at the same commit. Only then may the single
registered acquisition and target-blind analysis run. The 360 final targets
remain closed until the combined prediction freeze commit is remotely green.

Engineering capability added: NeuroDecodeKit now has a fixture-qualified,
resource-bounded, target-firewalled twelve-person low-frequency EEG cohort
confirmation pipeline with aggregate-only one-shot scoring.

Scientific claim not established: no real S004-S015 EDF or target was opened,
so no cohort confirmation, neural effect, brain-specific origin,
generalization, decoding, latency, hardware, or human-benefit result was added.

## 2026-08-10 - WO9R Real Predictions Frozen Before Scoring

- Verified exact implementation `8242674e5821b2c923c0c79baa3a6ea20a27d838`
  remotely green in CI `31359548779`, including Base Python job `93365527795`
  and Optional Neuro Readers job `93365527849`, before any registered real
  operation.
- Consumed the one no-retry acquisition. All 72 registered S004-S015 EDFs
  matched their official SHA-256 values over exactly 184,252,032 payload bytes.
  Runtime was 518.051205 seconds, peak RSS was 73,089,024 bytes, metadata bodies
  totaled 522,962 bytes, and retained bundle plus receipts used 184,274,970
  bytes. Acquisition parsed zero EDF headers, annotations, signals, or targets.
- Consumed the one target-blind analysis. It accepted 1,080 task events,
  created 720 labeled fit rows and 360 target-free final rows, completed exactly
  144 participant-specific fits and 216 prediction sets across 18 conditions,
  and exposed zero final targets to the model stage.
- Analysis through freeze used 19.864386 seconds, 303,153,152-byte peak RSS,
  4,206,464 private bytes, one CPU thread, one worker, zero network bytes, and
  zero new payload bytes.
- Wrote the 23,174-byte aggregate public freeze with SHA-256
  `6a546ca32a92b35c9c3448cecb5831f926d02f519a563d2ad803944c8d1f487a`.
  It binds all 216 prediction hashes plus source, code, split, configuration,
  dependencies, derivatives, private payload, resources, and counters. It
  contains no individual prediction, probability, target, or participant
  outcome.
- Added a public freeze document and five invariant tests. No private
  prediction, derivative, sealed target, or individual outcome was committed.
  The unrelated tracker inspection NDJSON remains untouched.
- The complete dependency-free, exact-classical, and broad optional profiles
  pass 1,533/1,589/1,604 tests with 177/34/8 expected skips, exactly five tests
  above the implementation milestone in each profile.

Next gate: commit and push this exact combined freeze and require both CI jobs
green. Only then may the isolated scorer open the same sealed 360 targets once.
No retry, rerun, or post-target update is open.

Engineering capability added: the real cohort and every target-blind
prediction set are now bound to the exact source, implementation, split,
configuration, dependencies, and resources without publishing individual
output.

Scientific claim not established: no final target has been delivered or
scored, so no task accuracy, neural effect, physiology, localization,
brain-specific origin, generalization, decoding, latency, hardware, or
human-benefit result is established.

## 2026-08-10 - WO9R Cohort Confirmation Scored Once At R3

- Verified combined freeze
  `8cd45d74dfa3517ae53c1427a0eb06e27ad3c870` remotely green in CI
  `31360781199`, including Base Python job `93369101655` and Optional Neuro
  Readers job `93369101696`, before the isolated scorer opened any final
  target.
- Consumed exactly one delivery of the same 360 sealed targets and one scoring
  event. Every private prediction hash and event, participant, and run identity
  matched the frozen ledger. Post-target fits, selections, threshold changes,
  channel changes, retries, and reruns are zero.
- Execution passed every H1 gate at 123/180 correct, pooled balanced accuracy
  `0.680975`, macro-participant balanced accuracy `0.682292`, 9/12 participants
  above chance, and one-sided participant sign-flip `p=0.002930`. The no-signal
  pooled and macro scores were `0.490722` and `0.500000`.
- Imagery passed every H2 gate at 131/180 correct, pooled `0.728014`, macro
  `0.728423`, 12/12 above chance, and `p=0.000244`. Execution-to-imagery and
  imagery-to-execution transfer were also positive at pooled balanced
  accuracies `0.728261` and `0.695077`.
- H3 and the mandatory-control conjunction failed. Central sensorimotor pooled
  balanced accuracy was `0.647575`, below the frontal proxy's `0.671821`;
  central-minus-proxy margin was `-0.024245`; physiology followed the
  registered direction in only 5/12 participants; and early-cue balanced
  accuracy was `0.762865`, above its `0.600` ceiling.
- The frozen router returned `WO9R-R3`. The 8,208-byte public aggregate result
  has SHA-256
  `d6cda8b4ce5f6da7add4a78ac8b1e74587cd8ab8eacf0dce8b806c076e85699a`.
  No individual prediction, probability, target, participant metric, or
  participant outcome is committed.

Next gate: design a fresh cue-neutral or independently instrumented
EOG/EMG-plus-movement-onset replication. Do not rerun WO9R or scale its
classifier to answer the unresolved source question.

Engineering capability added: NeuroDecodeKit completed a leakage-resistant,
resource-bounded, multi-person public-EEG confirmation with a remotely green
prediction freeze and one aggregate score.

Scientific result established: the fixed low-frequency representation carries
held-out left/right task information across twelve fresh participants and both
execution and imagery. Brain-specific origin, motor-compatible localization,
unseen-person generalization, typing or thought decoding, real-time operation,
hardware, and human benefit were not established.

## 2026-08-10 - IACKD Cue-to-Action Reversal Frozen

- Completed a primary-source and public-metadata pass over OpenNeuro IACKD
  `ds006840` v1.0.0 and its 2026 data descriptor.
- Retained a 370,331-byte metadata inventory with 1,340 selected objects and
  exact path, size, ETag, and modification-time identities. The selected raw
  source totals 7,249,113,684 bytes; 717,671,039 bytes of published MATLAB
  derivatives are excluded.
- Froze a participant-hand split: 30 models, congruent earlier-run fitting,
  one final incongruent run per unit, and both final target views applied to the
  same prediction set.
- Froze a causal-in-samples 0.5-4 Hz model, 30 ms Leap motion guard, direct
  HEOG/VEOG and fit-only EOG projection controls, 300 maximum fits, exactly 420
  prediction sets, participant-level exact inference, and `IACKD-R0` through
  `IACKD-R4` routing.
- Research `d6f955e` passed both jobs in CI `31399402403`. Registration
  `e42b799` passed Base Python job `93493810963` and Optional Neuro Readers job
  `93493811025` in CI `31400450392`.
- Local registration verification passed 1,638 tests with eight expected
  skips, Ruff 0.15.20, compileall, 117 registry JSON files, and diff checks.
- The all-false authorization packet permits a future new short-form decision
  only after its own commit is remotely green. Earlier instructions are not
  retroactive.
- IACKD payload, local path, EEG/EOG, marker, event, ball, Leap, target, model,
  prediction, score, dependency, retry, rerun, and claim counters remain zero.

Next gate: commit and push the all-false packet, require both CI jobs green,
then identify that sole packet to the maintainer. No implementation or real
operation may begin before a separate decision-only commit is remotely green.

Engineering capability added: NeuroDecodeKit now has an exact, resource-
bounded prospective experiment that can distinguish cue-following from
action-following low-frequency EEG predictions under synchronized controls.

Scientific claim not established: no IACKD payload was opened and no
prediction was made, so no new EEG effect, action decoding, source,
generalization, real-time, hardware, assistive, or clinical evidence exists.

## 2026-08-10 - IACKD Reversal Implementation Qualified Locally

- Confirmed packet-bound decision
  `1f48b3011e19ba8da35a18c3d3395813f159adc2` green in CI `31403012709`,
  including Base Python job `93502398308` and Optional Neuro Readers job
  `93502398753`, before implementation.
- Added a standard-library, dry-run-first OpenNeuro acquisition executor with
  strict two-page inventory replay, no redirects or retries, mandatory length
  and ETag checks, streaming SHA-256, exclusive roots, atomic promotion, and
  bounded receipts. It imports no neural reader and parses no payload content.
- Added the exact sequential BrainVision, event, ball, and Leap reconciler;
  causal 0.5-4 Hz feature path; synchronized EOG/timing/kinematic controls;
  target-firewalled derivatives; 300 fixed fits; 420 target-blind prediction
  sets; strict aggregate freeze; and isolated dual-target scorer.
- Added `iackd-acquire`, `iackd-cue-action`, and
  `score-iackd-cue-action` CLI surfaces plus CI help checks.
- One measured generated-only qualification processed 128 runs and 2,048
  trials into 1,568 fit rows and 480 target-free final rows, completed 300 fits
  and 420 prediction sets, and used 8.674020 seconds, 263,618,560-byte peak RSS,
  and 5,683,285 generated bytes. The synthetic route was `IACKD-R2`, which has
  no scientific meaning. Generated files were removed.
- Focused exact-stack verification passes 77 tests, including deterministic
  replay, malformed artifacts, target leakage, strict unit handling, response
  identity, output caps, provenance, target-firewall ordering, and all five
  router outcomes.
- Real metadata requests, payload requests/bytes, local IACKD stats/opens,
  object hashes, semantic parses, EEG/EOG/event/signal/trajectory/target reads,
  derivatives, fits, inferences, freezes, target deliveries, scores, retries,
  reruns, installs, provider calls, hardware operations, and claim upgrades
  are all zero. The unrelated tracker inspection NDJSON remains untouched.

Next gate: commit and push the exact implementation and require both CI jobs
green. Only then may the single 7,249,113,684-byte acquisition and target-blind
analysis run. Final targets remain closed until the later prediction freeze is
committed, pushed, and remotely green.

Engineering capability added: NeuroDecodeKit now has a fixture-qualified,
resource-bounded, target-firewalled IACKD cue-to-action reversal pipeline that
can freeze the same held-out predictions for action-versus-cue scoring.

Scientific claim not established: no real IACKD payload or target was opened,
so this implementation establishes no EEG effect, action decoding,
brain-specific origin, generalization, typing, language or thought decoding,
real-time operation, hardware capability, assistive benefit, or clinical use.

## 2026-08-10 - IACKD Acquisition Passed; Analysis Parked At F10

- Exact implementation `f5c36baffefc3889c006a515d06bc42cd2b5cb78`
  passed Base Python job `93522699446` and Optional Neuro Readers job
  `93522699599` in CI `31409141349` before real access.
- The single no-retry acquisition passed every gate: four metadata requests,
  1,340 selected requests, 7,249,113,684 payload bytes, 1,340 streaming hashes,
  zero content parses, zero post-write opens, 679.749484 seconds,
  126,205,952-byte peak RSS, and 41,882,632,192 free bytes after promotion.
- The private acquisition manifest is 580,128 bytes with SHA-256
  `99dcdf587cba202422e25b92082ff90add8512a2769902f59aab67dee52334e2`.
  It and the complete bundle remain Git-ignored and uncommitted.
- The one analysis wrote its no-rerun marker, verified exact membership and all
  1,340 object hashes, then failed closed on the first lazy BrainVision reader
  with `BrainVision channel inventory is not 32+4`, registered as
  `IACKD-F10-channel_sampling_or_geometry_failure`.
- The combined gate does not reveal whether the count, one or more required
  names, or both differed. The actual count and names were not retained and are
  recorded as unavailable rather than guessed.
- The failure preceded signal materialization, channels TSV, geometry, event,
  ball, Leap, signed direction, target, derivative, fit, inference, prediction,
  freeze, and score operations. Every such counter is zero.
- IACKD-1 is consumed and parked. No retry, rerun, parser relaxation,
  post-failure local inspection, target delivery, post-target update, release,
  or scientific claim upgrade is open. The unrelated tracker-inspection NDJSON
  remains untouched.

Engineering capability added: NeuroDecodeKit acquired and opaque-verified the
exact 7.249 GB IACKD source under strict resource limits and demonstrated that
the target-blind analysis fails closed at a preregistered channel contract
instead of silently deleting, relabeling, or adapting channels.

Scientific claim not established: no signal sample, target, model prediction,
or score was produced, so this result establishes no EEG effect, action or cue
alignment, brain-specific origin, generalization, typing, language or thought
decoding, real-time operation, hardware capability, assistive benefit, or
clinical use.

## 2026-08-10 - IACKD-H1 Header Inventory Research And Registration

- Confirmed closeout `3a58fcc` passed Base Python job `93529518866` and
  Optional Neuro Readers job `93529518946` in CI `31411229793` before this
  follow-up was frozen.
- Read only the version-of-record article, the authors' public source at commit
  `c0b595d`, and committed aggregate metadata. No OpenNeuro VHDR payload or
  local IACKD path was requested, statted, or opened.
- Found that the article does not state an exact 36-channel BrainVision file
  invariant. The pinned premovement code deletes M1/M2/HEOG/VEOG/TRIGGER if
  present; the execution code instead deletes HEO/VEO/HEOG/VEOG/TRIGGER.
- Selected all 128 VHDR objects already present in the committed metadata
  inventory: 161,792 total bytes, four observed object sizes from 1,254 to
  1,292 bytes, and 15 participants.
- Froze an aggregate-only diagnostic router that can preserve source failure,
  contradiction, count-only mismatch, exact-name mismatch, combined mismatch,
  or run heterogeneity without selecting an answer after inspection.
- Froze one-thread caps of 120 seconds, 256 MiB RSS, 1 MiB network body, 2 MiB
  disk, and 1 MiB public output. Raw VHDR retention, redirects, retries,
  reruns, local-bundle access, siblings, samples, events, trajectories,
  targets, models, providers, devices, and claims remain closed.
- Eight invariant tests bind the prior failure, green closeout, exact header
  surface, source-code hypotheses, stage ordering, parser/output policy,
  diagnostic router, and resource caps.

Engineering capability proposed: a deterministic all-run header compatibility
audit that can replace a failed hard-coded channel assumption with a measured,
hash-bound parser contract.

Scientific claim not established: no real header content, EEG sample, event,
trajectory, target, model, prediction, or score was accessed, so this work
establishes no neural effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit, or
clinical use.

## 2026-08-10 - IACKD-H1 Synthetic Implementation

- Registration `0e52278aaa1d15e70f4baab7b21ab1c96eb37f67` passed Base
  Python job `93534203368` and Optional Neuro Readers job `93534203385` in CI
  `31412667060` before implementation.
- Added a standard-library strict VHDR parser, response validator, aggregate
  signature builder, six-route replay, leakage validator, bounded atomic
  writer, generated fixture transport, dry-run plan, loader, inspector, and
  future exact-decision execution gate.
- Preserved `src/neurodecodekit/cli.py` byte-for-byte because its current hash
  is bound by consumed IACKD-1 evidence. The new CLI is
  `python -m neurodecodekit.preprocess.iackd_header_inventory`.
- Twenty-four core tests cover strict decode, malformed declarations, inert
  siblings, channel tables, all routes, response identity, truncation,
  compression, thread/RSS/output limits, overwrite, heavy imports, duplicate
  JSON, deterministic replay, leakage, and network-free default behavior.
- One isolated 128-header generated qualification processed 161,792 bytes with
  128 hashes and 128 parses in 0.037818958 seconds at 36,634,624-byte peak RSS.
  Its 4,465-byte output was automatically removed. Network, real IACKD, target,
  model, score, dependency, provider, hardware, and claim counters stayed zero.
- The constructed fixture routed `IACKDH-R1`; that is not a real result. The
  exact implementation still needs remote-green CI before a separate Tier C
  real-header decision can be prepared.

Engineering capability added: NeuroDecodeKit now has a deterministic,
sibling-blind, aggregate-only audit that can identify which file-contract
assumption caused the consumed IACKD channel gate to fail without reopening
the downloaded dataset.

Scientific claim not established: no real IACKD header, EEG sample, event,
trajectory, target, model, prediction, or score was accessed, so this work
establishes no neural effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit,
or clinical use.

## 2026-08-10 - IACKD-H1 All-False Authorization Request Prepared

- Exact implementation `16621cc484f4bec4a9474b9ac20d5b7d9314152f`
  passed Base Python job `93542494819` and Optional Neuro Readers job
  `93542494839` in CI `31415213841` before this request was prepared.
- Added a human packet, machine request, and nine invariant tests binding the
  exact green registration and implementation evidence, artifact hashes,
  response contract, access order, resource caps, forbidden operations, future
  decision shape, and all-zero access counters.
- The sole requested execution would retrieve exactly 128 public VHDR bodies
  and 161,792 expected bytes sequentially, hash and parse each once in memory,
  discard raw content immediately, and retain one aggregate-only ledger.
- The retained 7.249 GB IACKD bundle, every sibling, signal sample, event,
  trajectory, target, model, prediction, score, provider, device, hardware,
  retry, rerun, release, and claim operation remains unauthorized.
- This packet authorizes nothing. It must be committed, pushed, and remotely
  green before a fresh packet-bound maintainer decision can be separately
  recorded using the maintainer's actual words.

Engineering capability requested: one tiny, reproducible public-header audit
can determine which frozen file-contract assumption failed while preserving
the consumed analysis and all scientific firewalls.

Scientific claim not established: an all-false request is not data or a result
and establishes no EEG effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit, or
clinical use.

## 2026-08-10 - IACKD-H1 Packet-Bound Decision Recorded

- Request `56531c64b6733f93c9def80ad57125e0ee998fd8` passed Base Python
  job `93546632359` and Optional Neuro Readers job `93546632280` in CI
  `31416489006`.
- After Codex identified IACKD-H1 as the sole active packet and named the exact
  commit, CI, scope, and decision gate, the maintainer supplied a fresh message
  containing `continue`. The separate decision quotes that complete message
  verbatim and never presents the packet recital as user-authored text.
- The record binds the contract, implementation, request, packet, their
  SHA-256 and Git-blob identities, green implementation evidence, and the exact
  executor schema. Ten focused invariants pass.
- Exactly one later 128-request, 161,792-byte public VHDR audit is conditionally
  authorized. The decision itself must be committed, pushed, and pass both CI
  jobs first.
- Decision-only counters record one CI verification and zero real-header,
  local-bundle, sibling, signal, event, trajectory, target, model, scoring,
  dependency, provider, hardware, retry, rerun, release, or claim operations.

Engineering capability authorized for testing: one exact, resource-bounded,
sibling-blind public-header audit may produce a measured aggregate file-
compatibility diagnosis.

Scientific claim not established: this decision is not data or a result and
establishes no EEG effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit, or
clinical use.

## 2026-08-10 - IACKD-H1 Public Header Audit Consumed

- Decision `04f2706b56315186fac0c9a82686e9a360dbaf1e` passed Base Python
  job `93572439094` and Optional Neuro Readers job `93572439047` in CI
  `31424361969` before execution.
- The clean-worktree preflight measured 43,131,187,200 free bytes. The executor
  wrote its consumed marker before the first request and ran exactly once.
- All eleven gates passed: 128 public VHDR bodies, 161,792 input/network bytes,
  128 SHA-256 passes, 128 strict parses, 23.576352333 seconds, 94,650,368-byte
  peak RSS, one thread/worker/job, and zero retries or reruns.
- The 5,515-byte aggregate ledger has SHA-256
  `f981597730a1cc813431cb83b3910d9f330fb54267d86911e9dea58ee9c620ed`;
  the 244-byte consumed marker has SHA-256
  `e84c68ebc0a862650b0241083684f4440ba8b99edf7ac3c55e95c84eb17c304a`.
  Both remain Git-ignored.
- Route `IACKDH-R5` measured two declaration signatures: 96 headers declare 29
  channels without M1/M2; 32 declare 31 channels with M1/M2; all include HEOG,
  VEOG, and TRIGGER at 1024 Hz. The old exact-36 global invariant was wrong.
- The declared totals do not establish EEG-channel counts, channel types,
  geometry, reference, bad-channel state, or signal quality.
- Retained local bundle, sibling, signal, marker, event, trajectory, target,
  feature, model, prediction, score, provider, hardware, release, and claim
  counters remained zero. Producer causality was not applicable and end-to-end
  decoding latency was not measured.

Engineering capability added: NeuroDecodeKit measured the complete public
IACKD header inventory and replaced the failed exact-36-channel assumption
with a reproducible two-signature compatibility contract.

Scientific claim not established: no EEG sample, event, trajectory, target,
model, prediction, or score was accessed, so this result establishes no neural
effect, action decoding, brain-specific origin, generalization, typing,
language or thought decoding, real-time operation, hardware capability,
assistive benefit, or clinical use.

## 2026-08-10 - IACKD Role-Aware Dual-Reversal Research

- Confirmed H1 result commit `a6704898cfb09f6321bac5f15e27424f02614317`
  passed Base Python job `93575925675` and Optional Neuro Readers job
  `93575925695` in CI `31425445891` before this pass.
- Audited the consumed reader without opening real content. Its source binds
  four coupled fixture/role assumptions: exact total 36, 32/34 BIDS EEG rows,
  TRIGGER falling through to EEG, and a 36-channel fixture without TRIGGER.
- Derived the exact next public surface from the committed inventory: 128
  channel tables, 128 EEG sidecars, 30 electrode tables, and 30 coordinate
  systems, totaling 316 objects and 457,602 bytes. The canonical identity is
  53,367 bytes with SHA-256
  `0a63b46395030cb967dbca05f37a1367cf2bb0bf1088befce378a3556eab2274`.
- Specified a role-first `SensorRoleMap` that selects EEG from frozen BIDS
  types, isolates HEOG/VEOG, excludes TRIGGER, treats M1/M2 as an optional run
  property, joins geometry by name, and binds every later artifact by hash.
- Strengthened the scientific design to symmetric `C2I` and `I2C` reversal
  arms. Both must prefer action over the exact-opposite cue surrogate; the
  weaker participant-level margin is primary.
- Thirteen invariants replay the green evidence, exact inventory surface,
  code findings, role contract, reversal algebra, caps, zero counters, and
  claim boundary. No H2 body, local bundle, signal, target, model, or score was
  accessed or authorized.

Engineering capability proposed: a role-first sensor contract and symmetric
dual-reversal design can replace a brittle channel count and distinguish
action alignment from transfer of a visual mapping in two opposing directions.

Scientific claim not established: no new public metadata body, retained EEG,
event, trajectory, target, model, prediction, or score was accessed, so this
research establishes no new neural effect, action decoding, brain-specific
origin, unseen-person generalization, typing, language or thought decoding,
real-time operation, hardware capability, assistive benefit, or clinical use.

## 2026-08-10 - IACKD-H2 Role And Geometry Registration Frozen

- Bound the exact next metadata surface from the committed OpenNeuro inventory:
  128 channel tables, 128 EEG sidecars, 30 electrode tables, and 30 coordinate
  systems, totaling 316 objects and 457,602 bytes.
- Froze strict standard-library UTF-8, TSV, and duplicate-key-free JSON
  contracts; one-pass sequential transport; source-declared channel roles;
  optional M1/M2 handling; explicit unavailable fields; geometry joins by
  normalized name; aggregate-only output; and routes `IACKDR-R0` through
  `IACKDR-R4`.
- The role policy excludes TRIGGER and recorded EOG controls from predictive
  EEG and does not infer a replacement channel count. Finite C3/C4/Cz geometry
  is required for the strongest compatibility route; occipital coverage is
  reported separately and cannot rescue it.
- Fourteen invariants replay the exact 316-object identity, H1 reconciliation,
  prior green anchors, parser policy, output firewall, resources, stage order,
  zero counters, and claim boundary.
- Local verification passed 1,718 dependency-free tests with 182 skips and
  1,789 optional-neuro tests with 13 skips. Ruff, JSON validation, compilation,
  and `git diff --check` also passed. The optional suite's first sandboxed
  attempt was blocked only when an existing test tried to create a local
  multiprocessing forkserver socket; the unchanged suite passed outside that
  sandbox with network disabled.
- No public H2 body or local IACKD path was requested, statted, resolved, or
  opened. Generated-fixture implementation remains blocked until this exact
  registration is committed, pushed, and both CI jobs pass; real execution
  requires a later all-false packet and fresh green decision.

Engineering capability proposed: a strict aggregate metadata audit can freeze
a reproducible `SensorRoleMap` before any corrected IACKD sample reader exists.

Scientific claim not established: no EEG sample, event, trajectory, target,
model, prediction, or score was accessed, so this registration establishes no
neural effect, action decoding, brain-specific origin, generalization,
real-time operation, hardware capability, assistive benefit, or clinical use.

## 2026-08-10 - IACKD-H2 Synthetic Implementation Qualified

- Registration `228ccd03f5e0b5d02ba104e13b77b04f2032df78` passed Base
  Python job `93583989913` and Optional Neuro Readers job `93583989996` in CI
  `31427931578` before implementation began.
- Added `neurodecodekit.preprocess.iackd_channel_roles` without changing the
  central CLI or consumed IACKD-1 reader. The standard-library module exposes
  dry-run, generated-fixture, bounded-inspect, and future exact-decision modes.
- Implemented strict UTF-8/BOM, duplicate-key-free JSON, exact TSV, declared
  BIDS type, sidecar count/sampling, electrode, coordinate-system, response,
  pairing, leakage, resource, output, and one-shot evidence boundaries.
- The aggregator uses private run and participant/hand keys but publishes no
  path, participant, coordinate, free text, or individual row. It emits two
  schema levels, status totals, sidecar groups, one role-map hash, geometry
  groups, H1 reconciliation, measurements, and one R0-R4 route.
- One final generated pass covered all 316 exact registered sizes and 457,602
  bytes, 316 hashes, and 316 parses. It produced constructed `IACKDR-R4`, one
  core schema after M1/M2 removal, 26 fixture predictive EEG roles, and 30
  complete fixture central/occipital geometry groups.
- Runtime was 0.054679625 seconds through return, peak RSS was 34,996,224
  bytes, and output was 8,282 bytes. Network and every real/protected counter
  were zero; the temporary output was removed.
- Forty-seven focused tests, all 1,751 dependency-free tests with 182 skips,
  and all 1,822 optional-neuro tests with 13 skips pass locally.

Engineering capability added: NeuroDecodeKit can derive and validate a
count-agnostic, source-declared, geometry-aware sensor-role contract through a
bounded aggregate interface without touching retained EEG data.

Scientific claim not established: the clean R4 is generated-fixture behavior;
no public H2 body, EEG sample, event, trajectory, target, model, prediction, or
score was accessed, so there is no new neural or decoding evidence.

## 2026-08-10 - IACKD-H2 All-False Authorization Request Prepared

- Exact implementation `9f6fef9540ae0a1fe52cbf24b17b0af89147beae`
  passed Base Python job `93591323731` and Optional Neuro Readers job
  `93591323646` in CI `31430151368` before packet preparation.
- The packet binds exactly 128 channel tables, 128 EEG sidecars, 30 electrode
  tables, and 30 coordinate systems: 316 public bodies and 457,602 bytes.
- It requests one future sequential pass, one SHA and one semantic parse per
  body, one private consumed marker, one aggregate ledger, one thread, 180
  seconds, 256 MiB RSS, 2 MiB network body, 4 MiB disk, 2 MiB output, and zero
  retry/rerun.
- All real request, parse, consumed-marker, output, local-bundle, VHDR/sibling,
  signal, event, trajectory, target, model, score, dependency, provider,
  hardware, release, IACKD-2, and claim authorization flags are false.
- Ten invariants verify both green parent commits, every bound artifact hash,
  exact scope/order/resources, future decision shape, zero counters, and claim
  boundary.

Engineering capability requested: one measured public metadata audit may
freeze whether a count-agnostic source role and geometry contract is compatible
with all registered IACKD files.

Scientific claim not established: this request is not data or a result and
adds no neural, decoding, localization, generalization, real-time, hardware,
assistive, or clinical evidence.

## 2026-08-10 - IACKD-H2 Packet-Bound Decision Recorded

- Request `86174bc86123bc010bac2f40a9d72147dc8aef05` passed Base Python job
  `93594327147` and Optional Neuro Readers job `93594327069` in CI
  `31431064259` before the decision.
- Codex identified IACKD-H2 as the sole active Tier C packet, including the
  exact commit, green CI, 316-object/457,602-byte scope, and fresh-decision
  boundary.
- The maintainer then said `continue :)`. The decision record preserves those
  exact words, incorporates the immutable packet by reference, and infers no
  wider authorization.
- Ten invariants verify the actual words and hash, green request evidence,
  bound artifact SHA-256 and Git-blob identities, exact executor schema,
  unchanged resource caps, ordered consumed marker, zero decision-only access
  counters, and scientific ceiling.
- The decision remains ineffective until its own exact commit is pushed and
  both remote CI jobs pass. Recording it made zero metadata requests, local
  bundle operations, signal/target reads, model runs, or scores.

Engineering capability authorized for testing: one exact public-metadata
audit may freeze a count-agnostic IACKD sensor-role and geometry contract.

Scientific claim not established: the decision is not data or a result and
adds no neural, decoding, localization, generalization, real-time, hardware,
assistive, or clinical evidence.

## 2026-08-10 - IACKD-H2 Role And Geometry Audit Consumed At R1

- Decision `f6eb5ab650a0232a17d2f8f56c582c90bf0cf420` passed Base Python
  job `93634720183` and Optional Neuro Readers job `93634720191` in CI
  `31444154297` before the sole execution.
- The executor wrote the 248-byte private consumed marker first, then made
  exactly 316 sequential requests, read 457,602 bytes, completed 316 SHA-256
  passes and 316 strict parses, and retained one 9,779-byte aggregate ledger.
- Runtime was 55.592999708 seconds, peak RSS was 86,769,664 bytes, retained
  generated bytes were 10,027, and every one-thread, network, disk, output,
  no-retry, and no-rerun cap passed.
- H1 totals, allowlisted presence, 1024 Hz sampling, one 26-channel predictive
  EEG core, average reference, and finite central/occipital geometry in all 30
  groups reconciled.
- `IACKDR-R1` applied because HEOG and VEOG are source-typed `MISC`, which the
  frozen EOG-control predicate rejected, and because the frozen reconciler
  separated the `MISC` Trigger from sidecars that consistently count all three
  controls as `MiscChannelCount=3`.
- This diagnoses our prospective taxonomy rather than malformed source files.
  The computed candidate hash is inadmissible, H2 is consumed, and no parser or
  router amendment, retry, or rerun is open.
- Local bundle, VHDR/sibling, signal, event, trajectory, target, model,
  prediction, score, provider, device, release, and claim counters stayed zero.

Engineering capability added: the complete public IACKD BIDS role and geometry
inventory isolates the remaining reader failure to a reproducible `MISC`
control-taxonomy mismatch.

Scientific claim not established: no EEG sample, event, trajectory, target,
model, prediction, or score was accessed, so there is no neural or decoding
evidence.

## 2026-08-10 - IACKD-H3 Source Semantics Policy Research

- Used only committed H2 result registry `e6f0665` after closeout `580f11f`
  passed both jobs in CI `31444931063`; no Git-ignored H2 artifact or source
  body was read.
- Rechecked dataset-pinned BIDS 1.7.0 against current BIDS 1.11.1. Both keep
  MISC, HEOG, VEOG, and TRIG distinct channel types, while the sidecar MISC
  count field spelling evolved. The adapter must bind dataset version rather
  than silently applying the latest schema.
- Candidate `IACKD-SourceSemanticsPolicy` hash
  `1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4`
  separates source type, functional role, and model inclusion.
- It preserves the observed 26/28 EEG plus three MISC source counts, fixes one
  26-name predictive core, treats M1/M2 as optional nonpredictive EEG, and
  assigns HEOG/VEOG/Trigger nonpredictive control roles without moving them out
  of their source MISC bucket.
- Ten invariants freeze canonical hash, role separation, count groups,
  geometry/reference requirements, zero access counters, and a one-thread,
  30-second, 256 MiB, 2 MiB generated-fixture-only next qualification.
- This does not amend H2, approve its inadmissible hash, implement a reader,
  access real data, or authorize IACKD-2.

Engineering capability proposed: version-aware source semantics can remove the
exact control-taxonomy bug while preserving BIDS truth and model isolation.

Scientific claim not established: this planning artifact accessed no signal,
event, target, model, prediction, or score and adds no neural evidence.

## 2026-08-10 - IACKD-H3 Generated-Fixture Implementation

- Research `ed5ce82` passed both required jobs in CI `31445790741` before
  implementation.
- Added a standard-library policy loader and validator bound to candidate hash
  `1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4`.
- Added deterministic 29-row and 31-row target-free fixtures that preserve
  26/28 EEG plus three MISC source counts while holding one 26-channel
  predictive output order.
- Added separate source-order, source-count, functional-role, model-mask, and
  geometry-mask hashes, plus strict source index, sampling, reference, and
  geometry validation.
- Added 13 generated mutations spanning 12 distinct refusal classes, including
  BIDS version and count spelling, role overlap, model-mask drift, binding
  drift, and target leakage.
- Added exclusive bounded output, load/validate/summary APIs, fixed-monitor
  byte replay, heavy-import and access-counter firewalls, and a module CLI with
  no real execute mode.
- Forty-three focused research and implementation invariants pass. Complete
  base, optional-neuro, lint, compile, registry, CLI, and diff verification are
  required before the implementation commit.
- No measured closeout has executed. It remains held until the exact
  implementation commit is pushed and both remote CI jobs pass.

Engineering capability added: the prospective H3 policy is now executable and
failure-addressable on generated metadata without conflating source type,
functional role, or model inclusion.

Scientific claim not established: no real or public body, local bundle,
signal, event, target, model, prediction, or score was accessed, so this adds
no neural or decoding evidence.

## 2026-08-10 - IACKD-H3 Measured Generated Closeout

- Exact implementation `8c5784a` passed both jobs in CI `31446902756` before
  the closeout.
- One output-parent preflight correctly refused a symbolic link at
  `IACKDS-F14` before the policy was read, a fixture was built, or output was
  created.
- One later semantic qualification completed with no retry or rerun after
  fixture access.
- The 29-row and 31-row fixtures preserved 26/28 EEG plus three MISC source
  counts while both kept exactly 26 predictive EEG channels.
- All five derivative hashes, deterministic replay, target firewall, 13
  mutations, 12 distinct refusal classes, resource caps, and output cap passed.
- Measured 6,093 input bytes, 6,834 output bytes, 60 generated rows, four
  semantic passes, 0.007473916979506612 seconds, and 20,250,624-byte peak RSS.
- Every real/public metadata, Git-ignored, local bundle, sibling, signal,
  event, trajectory, target, derivative, feature, model, training, inference,
  prediction, score, provider, hardware, release, and claim counter was zero.
- The temporary report was inspected, SHA-256 verified, cross-checked against
  the aggregate result registry, and removed.

Engineering capability added: H3 now has measured evidence that the
source-type-first policy, five derivative bindings, deterministic replay, and
fail-closed target firewall work on generated metadata.

Scientific claim not established: H3 accessed no real signal or scientific
outcome and therefore adds no neural or decoding evidence.

## 2026-08-10 - IACKD-2 Role-Aware Dual-Reversal Preregistration

- Bound green dual-reversal research, consumed IACKD-1 and H2 results, the H3
  policy result, and the exact 1,340-object OpenNeuro inventory without reading
  any private artifact or public body.
- Recomputed 128 canonical ten-object run groups from the committed inventory.
  The largest is 82,064,564 bytes, the largest object is 73,200,640 bytes, and
  the 60 separate geometry objects total 56,386 bytes.
- Froze a fresh one-run-at-a-time future path that forbids the old retained
  bundle, caps peak incremental disk at 1 GiB, and requires 10 GiB free before
  one exact 7,249,113,684-byte payload sequence.
- Froze symmetric `C2I` and `I2C` arms. Both must favor action over the exact
  cue-derived opposite; one arm cannot rescue the other and the participant's
  weaker arm margin is primary.
- Bound the fixed 26-channel H3 core, causal 0.5-4 Hz feature family, central,
  occipital, EOG, pre-window, timing, physiology, and five fixed controls.
- Registered exactly 660 fits, 900 target-blind prediction sets, one aggregate
  freeze that must become remotely green, one combined target delivery, one
  score, zero retries, zero reruns, and zero post-target updates.
- Added 16 invariants that replay hashes, inventory geometry, arm symmetry,
  target isolation, model dimensions, statistics, resources, router order,
  and the Tier B/Tier C boundary.
- This commit is registration only. Generated-fixture implementation is
  conditional on remote-green registration; real payload and scientific
  execution require a later separately green Tier C decision.

Engineering capability proposed: a storage-safe role-aware dual-reversal
experiment can distinguish symmetric action alignment from cue transfer under
strict participant-level and confound controls.

Scientific claim not established: no payload, retained bundle, signal, event,
trajectory, target, model prediction, or score was accessed, so this adds no
neural or decoding evidence.
