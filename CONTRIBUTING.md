# Contributing To NeuroDecodeKit

Thank you for helping make non-invasive neural language-decoding research more
accessible, reproducible, and honest. Contributions are welcome from software
engineers, neuroscientists, signal-processing researchers, dataset stewards,
EEG users, hardware builders, technical writers, designers, and people who are
new to the field.

You do not need access to a large MEG system or private dataset to contribute.
Many of the most useful improvements are pure-Python tests, synthetic fixtures,
format adapters, documentation, resource measurements, and better failure
messages.

## Read This First

NeuroDecodeKit is a research toolkit, not a medical device or a mind-reading
product. The current repository has **not** demonstrated:

- neural decoding that beats its no-signal prior on the real evaluations run;
- unseen-person generalization;
- useful open-vocabulary EEG sentence decoding;
- an end-to-end real-time text system;
- compatibility with a consumer or portable device;
- arbitrary-thought decoding or clinical utility.

Those are proof boundaries, not marketing caveats. Contributions must preserve
them in code, reports, documentation, issue titles, and screenshots.

Before opening a pull request, read:

1. `README.md` for the product and engineering map.
2. `docs/RISK_AND_ETHICS.md` for privacy, licensing, and claim language.
3. `docs/DECISIONS.md` for frozen experimental decisions.
4. `AGENTS.md` if an automated coding agent will touch the repository.
5. `THIRD_PARTY_NOTICES.md` before using Brain2Qwerty or SpanishBCBL material.
6. `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md` before proposing replay,
   streaming, or hardware work.
7. `docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md` plus its preregistration before
   proposing model precision, quantization, local-runtime, memory, or energy
   benchmarks.

## Ways To Contribute

Good contribution lanes include:

| Lane | Examples | Real neural data required? |
|---|---|---:|
| Base Python | schemas, hashes, manifests, metrics, reports, error messages | No |
| Synthetic fixtures | malformed files, timing cases, cap tests, deterministic replay | No |
| Neuro formats | BrainVision, EDF/EDF+, BDF, EEGLAB, FIF, BIDS reader validation | No; synthetic first |
| EEG compatibility | metadata reports, reference/geometry documentation, bounded local validation | Not for the first gate |
| EEG hardware | offline replay adapters, timestamp audits, packet-loss reports, device descriptors | Usually not at first |
| Evaluation | no-signal controls, leakage tests, split protocols, uncertainty | No for interfaces; approved data for results |
| Models | small CPU-bounded baselines, causal replay, frozen precision/runtime gates, explicit state and latency accounting | Synthetic first |
| Documentation | setup, diagrams, examples, terminology, accessibility, translations | No |
| Research registry | primary-source dataset/device facts with explicit unknowns | No |

Small, reviewable contributions are preferred. A precise test for one malformed
BrainVision companion path can be more valuable than a large unvalidated model.

## Non-Negotiable Safety Rules

Every contribution must follow these rules:

1. **Never commit neural recordings.** Do not add `.fif`, `.edf`, `.bdf`,
   `.eeg`, `.vhdr`, `.vmrk`, `.set`, `.fdt`, `.mat`, `.npz`, `.zarr`, XDF,
   DICOM, NIfTI, or vendor recording bundles containing participant data.
2. **Never paste participant data into an issue.** This includes demographics,
   acquisition timestamps, free-text annotations, target sentences, responses,
   electrode coordinates tied to a person, and persistent device identifiers.
3. **Never include credentials.** Remove API keys, Hugging Face tokens, cloud
   URLs with signed query parameters, device serial numbers, Wi-Fi credentials,
   and proprietary SDK keys.
4. **Do not upload a dataset because a maintainer asks a technical question.**
   Compatibility begins with redacted metadata and synthetic reproduction.
5. **Do not reopen consumed evaluation data for tuning.** A viewed holdout is no
   longer fresh. Preserve the split and label the result honestly.
6. **Keep modalities separate.** EEG, MEG, OPM-MEG, EOG, EMG, eye tracking,
   PPG, IMU, microphone, and hand tracking are different evidence channels.
7. **Keep tasks separate.** Prompted typing, imagined speech, natural reading,
   P300, SSVEP, and motor imagery do not share one decoding claim.
8. **Always include a no-signal comparator for predictive neural results.** A
   language prior can look impressive without using brain activity.
9. **Heavy dependencies stay optional.** The base package must remain usable
   without MNE, NumPy, SciPy, Torch, Zarr, Gradio, or Hugging Face.
10. **Downloads and writes must be bounded and explicit.** Large downloads are
    dry-run first; generated artifacts need declared file, byte, runtime, RSS,
    and thread caps.

If a contribution cannot meet these rules, open a design issue before writing
code. Do not quietly relax a cap or proof boundary to make a demo pass.

## I Have EEG Data

Excellent. The safest and most useful first contribution is usually a
**compatibility report**, not the recording itself.

The prospective open-cohort direction is local-first. A future contributor
runner would keep raw EEG and plaintext targets on the contributor's machine
and emit only a redacted, hash-bound aggregate receipt covering source identity,
modality, device, montage, sampling, trial/split identity, controls, resources,
warnings, unavailable fields, and claim ceiling. That design is documented in
`docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md`, but no real-data federation or
upload service exists yet. Do not send data in anticipation of that feature.

### What Not To Upload

Do not attach or link private raw EEG, event files, target text, participant
tables, consent forms, derived embeddings, subject-level predictions, or cloud
storage folders. A de-identified filename does not make a recording anonymous.

Public datasets should be referenced by their canonical landing page, exact
version/revision, and license. Do not mirror them into this repository.

### Step 1: Open The EEG Data Proposal

Use the **EEG data compatibility** issue form. It asks for non-sensitive facts:

- canonical dataset or local/private status;
- license and sharing boundary;
- task cohort and language;
- file format and companion-file layout;
- device or amplifier family;
- nominal channel count and sampling rate;
- reference scheme and geometry availability;
- event/annotation availability without event content;
- subject, session, and trial counts at an aggregate level;
- exact or capped byte counts;
- operating system and Python version;
- the engineering capability you want to validate.

Use `unknown` when a field is not verified. Unknown is better than a plausible
guess.

### Step 2: Run Metadata-Only Intake Locally

For supported formats, the base install can inspect file structure without
opening binary signal arrays or event/target content:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .

neurodecode inspect-recording \
  --path /absolute/path/to/local/recording-or-bids-root \
  --out-dir /absolute/path/to/private/intake-report

neurodecode inspect-intake-report \
  --report /absolute/path/to/private/intake-report/intake.json
```

Review the generated JSON, Markdown, and audit sidecar locally before sharing
anything from them. The scanner is designed to redact absolute paths and event
content, but metadata can still be sensitive in context. In an issue, prefer
the command's compact summary and warning names over attaching the whole file.

Current metadata-only format families are:

- BrainVision `.vhdr` with `.eeg` and `.vmrk` companions;
- EDF/EDF+;
- BDF;
- continuous EEGLAB `.set` plus external `.fdt`;
- FIF, including common split-file naming;
- BIDS roots with a recognized raw candidate.

Recognition is compatibility level 0. It does not prove readable samples,
correct units, valid events, usable signal, or decoding performance.

### Step 3: Reproduce With Synthetic Data

Before a reader touches a private or public participant recording, add or reuse
a deterministic synthetic fixture with the same format family and the smallest
metadata feature that matters. Synthetic fixtures should:

- contain no natural-language targets or participant attributes;
- use deterministic values and timestamps;
- fit under a declared artifact cap;
- include malformed/refusal cases;
- preserve exact channel, unit, reference, geometry, and event-status intent;
- pass replay, tamper, privacy, and no-mutation tests.

RW2 currently provides target-free fixtures for BrainVision, EDF/EDF+, BDF,
EEGLAB external-FDT, FIF, and BIDS direct-reader resolution.

Replay, streaming, and hardware contributions must also follow
`docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md` and
`registries/replay_equivalence_contract.v0.json`. The exact proposed Stage A
scope is in `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md`, with a hash-bound
machine request in `registries/rw3_stage_a_authorization_request.v0.json`.
Those files are a request, not permission: `authorized_now` is still `false`.
Do not attach or open a real recording, start an outlet/inlet, open a socket,
enumerate a board, or add BrainFlow/LSL/PyXDF code without a separately approved
stage. Start with target-free deterministic mechanics and state exactly which
registered schedule, anomaly, refusal, and cap you cover.

Opening an issue or pull request does not authorize Stage A. Maintainers must
record a separate authorization-only commit before any Stage A implementation,
and that decision cannot authorize Stages B-D, sockets, devices, or real data.

Precision, quantization, and local-runtime work follows the same decision
discipline through a separate gate. Loop 24 now has one measured target-free
closeout: float16 preserved behavior but was slower; QNNPACK qint8 was smaller
but incorrect and slower; no candidate qualified; the runtime cap failed;
float32 was retained. Selection seed 2401 is consumed and qualification seed
2402 remains unopened. Do not rerun, retune, or repurpose either under the same
claim. A new benchmark issue or pull request must define a separately frozen
question and is not execution authorization; RW3 authorization cannot reopen
Loop 24.

When that work is authorized, reports must distinguish tensor dtype, packed
weight dtype, input/output dtype, actual backend, serialized bytes, live state,
working memory, process RSS, producer time, fixed-decoder time, and full-pipeline
time. Smaller storage is not automatically faster execution; qint8 weights are
not automatically integer-only end to end; and a local synthetic speed result
is not neural accuracy, text latency, device qualification, or energy evidence
for another machine.

### Step 4: Request A Bounded Real-Read Protocol

Real signal access requires a separate, reviewable protocol. It must freeze:

- the exact recording revision and file list;
- the maximum source and generated bytes;
- the windows, channels, and sample-value cap;
- whether events or labels will be opened;
- privacy fields that will be omitted;
- train/validation/test identity and fit scope when applicable;
- access counters and one-time holdout rules;
- runtime, RSS, worker, and numerical-thread limits;
- proceed, park, and kill decisions;
- every claim the result cannot establish.

Do not post the recording while that protocol is reviewed. Maintainers may be
able to help using a synthetic twin or a local-only command.

### Compatibility Levels

NeuroDecodeKit treats EEG support as staged evidence:

| Level | Meaning | Does not establish |
|---:|---|---|
| 0 | File family and companions recognized from bounded metadata | Signal readability |
| 1 | Bounded samples can be read under a frozen adapter | Correct events or quality |
| 2 | Channels, timing, units, geometry status, and aggregate events validated | Good signal or task fitness |
| 3 | Deterministic preprocessing/replay is validated | Predictive information |
| 4 | Leakage-resistant classification beats registered controls | Sequence decoding |
| 5 | Sequence metrics beat no-signal controls on a fresh split | New-person or real-time use |
| 6 | Bounded live/replay timing and end-to-end behavior are measured | Clinical or arbitrary-thought use |

State the exact level your contribution reaches. Never inherit a higher level
from another dataset, device, subject, session, or file format.

## I Have An EEG Headset Or Board

Use the **EEG hardware qualification** issue form. A device name alone is not a
compatibility result. Please provide non-sensitive technical facts:

- manufacturer, model, hardware revision, and firmware version;
- whether each channel is EEG, generic ExG, EOG, EMG, reference, ground, or
  auxiliary;
- electrode positions or cap layout, without participant coordinates;
- reference and ground configuration;
- nominal and measured sampling rates;
- raw-data API, SDK, file export, or replay interface;
- transport: USB, serial, BLE, Wi-Fi, LSL, XDF, or vendor cloud;
- timestamp source, clock domain, correction method, packet counter, and known
  packet-loss behavior;
- operating system and driver/SDK versions;
- SDK, firmware, and sample-data license;
- whether capture can remain local and work offline;
- every peripheral stream such as IMU, PPG, audio, gaze, or EMG;
- the smallest synthetic or bench replay that can be shared legally.

The first hardware milestone should usually be **offline replay equivalence**:
feed the same deterministic samples through a file path and the proposed device
adapter, then compare channel order, timestamps, packet gaps, values, and hashes.

A connection success, live waveform plot, or vendor demo does not prove neural
language decoding. Low-channel consumer EEG should not be presented as a drop-in
replacement for 64-channel EEG or 306-channel MEG.

## Development Setup

### Base Environment

The base package intentionally has no runtime dependencies:

```bash
git clone https://github.com/CheickDiakite-yikes/neurodecodekit.git
cd neurodecodekit
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

On Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Optional Extras

Install only what your contribution uses:

| Extra | Purpose |
|---|---|
| `array` | NumPy-only synthetic shards, NPZ caches, and array-backed interfaces |
| `neuro` | MNE, NumPy, and SciPy readers and signal processing |
| `ml` | NumPy, scikit-learn, and optional Torch baselines |
| `cache` | Zarr/numcodecs experiments when a measured gate justifies them |
| `hf` | Hugging Face manifest listing and explicit selective download |
| `demo` | Local artifact-backed Gradio console |
| `dev` | Ruff and pytest development tools |
| `all` | Every optional group; large and rarely needed |

Example:

```bash
python -m pip install -e '.[neuro,dev]'
```

Do not add a heavy package to base `dependencies` to simplify one command.
Import optional dependencies inside the function or command that needs them,
and raise a helpful install message.

## Running Checks

Keep numerical work to one thread unless a protocol explicitly says otherwise:

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
```

Base test suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Neuro-enabled suite and focused reader gate:

```bash
python -m pip install -e '.[neuro,dev]'
PYTHONPATH=src python -m unittest discover -s tests -p 'test_signal_quality.py' -v
PYTHONPATH=src python -m unittest discover -s tests -v
```

Lint and repository hygiene:

```bash
ruff check .
python -m compileall -q src tests
git diff --check
```

Run CLI help for every command you add or change:

```bash
neurodecode --help
neurodecode YOUR-COMMAND --help
```

Tests that require an optional extra must skip cleanly when the extra is absent.
A skipped base test is not evidence that the optional path passed; report both
the base result and the environment in which the focused test actually ran.

## Engineering Conventions

- Use small, explicit functions and dataclasses for structured records.
- Prefer `pathlib.Path` over ad hoc string path handling.
- Use JSON/JSONL or typed NPZ schemas instead of parsing your own output text.
- Keep schemas versioned and strict; reject unknown incompatible versions.
- Hash source identity, configuration, splits, and numerical payloads when
  downstream claims depend on exact replay.
- Write atomically where partial artifacts would be misleading.
- Refuse output collisions by default. An overwrite flag may replace only
  registered artifacts; it must not delete unrelated files.
- Keep absolute paths, participant fields, free text, and exact acquisition
  timestamps out of shareable reports.
- Add comments only where a non-obvious invariant needs orientation.
- Preserve existing module boundaries and local patterns.
- Never silently download data, open a holdout, train a model, or widen a cap.

## Tests Expected By Change Type

| Change | Minimum test evidence |
|---|---|
| Parser/schema | valid, malformed, unknown-version, and roundtrip cases |
| File adapter | deterministic synthetic read, missing companion, unsafe path, cap, and no-preload cases |
| Cache | shape/dtype/length/mask/hash validation, malformed payload, collision, and output-cap cases |
| Split/evaluation | duplicate identity, fit-scope, strict binding, leakage, consumed-holdout, and no-signal control cases |
| Model | deterministic seed, parameter count, train-only fit, validation-before-test, prior control, runtime/RSS, and replay cases |
| CLI | root help, command help, success summary, refusal exit code, and bounded roundtrip |
| Docs-only | links/commands checked where practical, proof boundary unchanged, `git diff --check` |

Coverage should scale with blast radius. A shared schema or split contract needs
broader tests than a typo fix.

## Research And Evaluation Contributions

Every predictive result must identify:

- dataset and exact revision;
- modality, task, subject/session scope, and unit of prediction;
- train, validation, test, and calibration membership;
- every transformation and the rows used to fit it;
- whether the test has been viewed before;
- no-signal prior and any signal-shuffle/zero-signal controls;
- primary and secondary metrics with uncertainty when appropriate;
- runtime, peak RSS, input/output bytes, threads, and model/training runs;
- causal context, scheduling delay, compute time, and end-to-end latency as
  separate fields;
- failures, unavailable measurements, and claim boundaries.

Do not report only the best seed. Do not tune a threshold after opening test.
Do not compare event accuracy to sentence CER as one leaderboard. Do not call a
within-recording split unseen-person generalization.

Negative results are welcome. The existing real cross-session MEG and EEG
baseline results are negative, and preserving those outcomes is part of the
project's value.

## Documentation And Source Standards

Research claims should cite primary sources whenever possible: official papers,
dataset cards, specifications, source code, or vendor/developer documentation.
Record exact versions, revisions, and review dates for facts that can change.

Use these proof labels consistently:

- `production verified`
- `browser verified`
- `real-data validated`
- `fixture-backed`
- `synthetic mechanism only`
- `metadata only`
- `local shell only`
- `preregistered, not implemented`
- `parked after measured gate`
- `unavailable`

Do not use `ready`, `works`, or `supported` without saying what exact boundary
was tested.

Significant decisions belong in `docs/DECISIONS.md`. Measured implementation
closeouts belong in a focused document and `docs/BUILD_NOTES.md`. Update
`START_HERE.md`, the handoff, and the tracker when the current next gate changes.

## Independent Reproduction

Loop 43 planning research defines a future target-free NeuroToken causal-replay
artifact challenge. The experiment is `Not Started` and unauthorized: there is
no public packet, oracle, challenge issue, submission form, contributor run, or
independent result to attempt yet.

When separately authorized, the core challenge will accept only public,
target-free synthetic artifacts and a hash-frozen commit-reveal submission. It
will record clean-environment identity, public/private guidance, conflicts,
commands, resource use, semantic comparisons, warnings, discrepancies, privacy
scans, and negative or partial outcomes. Untrusted fork code must remain
unprivileged and receive no secrets, protected caches, or write authority.

Contributor-owned EEG is valuable, but it is outside the Loop 43 core challenge
and must remain local under a separate protocol. Even a successful future Loop
43 result would be independent artifact reproduction, not scientific
replication, neural advantage, decoding accuracy, participant generalization,
or device qualification. See `docs/LOOP_43_PRIMARY_SOURCE_RESEARCH.md` for the
complete boundary.

## Pull Request Process

1. Open an issue first for a new format, dataset, hardware adapter, dependency,
   schema version, model family, or real-data experiment.
2. Keep the pull request focused on one coherent capability or gate.
3. Add tests and documentation in the same pull request.
4. Run the relevant base and optional checks locally.
5. Complete every applicable item in the pull request template.
6. Call out generated files, local-only artifacts, and anything deliberately not
   committed.
7. State the engineering capability added in one sentence.
8. State the scientific or decoding claim **not** established in a separate
   sentence.
9. Respond to review with additional commits; do not force-push away useful
   review context unless a maintainer requests history cleanup.

Maintainers may ask a contribution to park if its protocol, privacy boundary,
resource cap, or test evidence is not yet strong enough. Parking is a measured
decision, not a rejection of the idea.

## Commit And License Terms

Write descriptive commits that explain one tested milestone. Do not commit
generated inspection debris, local caches, recordings, secrets, or unrelated
workspace changes.

Unless explicitly stated otherwise, a contribution intentionally submitted for
inclusion is accepted under the repository's Apache-2.0 license, as described in
Section 5 of that license. You must have the right to submit the work. Third-
party code, data, figures, and model assets keep their original terms and must
be identified before review.

No contributor license agreement is currently required. A future CLA or DCO
policy would require a documented governance decision and would not be applied
retroactively without review.

## Getting Help

Use the issue form that best matches your question. For sensitive security or
data-exposure concerns, follow `SECURITY.md` and do not open a public issue.
For conduct concerns, follow `CODE_OF_CONDUCT.md`.

The maintainers cannot accept private recordings through GitHub, certify a
device for medical use, or promise that a given EEG system can decode language.
They can help turn a well-scoped compatibility question into a safe synthetic
fixture, bounded local test, and honest result.
