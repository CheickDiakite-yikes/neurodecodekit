# PhysioNet Low-Frequency Cohort Confirmation Authorization Packet

Status: **Exact Tier C authorization requested; not yet granted**

Date: 2026-08-10

Registration commit:
`716e5432498052b78cb799c9f4e3bfbae68e3ad2`

Green registration CI:
`31354565966`

Machine request:
`registries/physionet_low_frequency_cohort_confirmation_authorization_request.v0.json`

## What This Decision Would Allow

The requested decision would allow one ordered WO9R sequence:

1. implement and fixture-qualify the exact acquisition, target firewall,
   low-frequency analysis, controls, prediction freezer, and scorer;
2. acquire and opaque-verify only the 72 frozen EEGMMIDB EDF files;
3. run one target-blind execution over S004-S015;
4. freeze all run-11 and run-12 predictions together; and
5. after the freeze is remotely green, deliver and score the same 360 final
   targets once and apply the frozen router.

This is not a broad data, model, or replication authorization. It permits no
other participant, run, file, dataset, model family, threshold, dependency
installation, retry, rerun, or post-target update.

## Immutable Proof Anchor

Registration `716e5432498052b78cb799c9f4e3bfbae68e3ad2` froze:

- exactly 72 EDF paths for S004-S015 and runs 03/04/07/08/11/12;
- exactly `184,252,032` payload bytes and one official SHA-256 per file;
- execution fit runs 03/07 and sealed-final run 11;
- imagery fit runs 04/08 and sealed-final run 12;
- expected 720 fit events and 360 combined sealed-final events;
- one exact `0.5-4 Hz` whole-head LDA primary template;
- exact central, frontal, occipital, asymmetry, cue, pre-cue, timing, no-signal,
  derangement, displacement, and hemisphere controls;
- 144 participant-specific parameter-update fits;
- 18 condition families, 216 participant-condition prediction sets, and 216
  target-blind inference runs;
- one combined hash-only prediction freeze before either final target set is
  delivered;
- the `WO9R-R0` through `WO9R-R4` router; and
- one-thread, one-worker, memory, runtime, storage, network, and no-rerun caps.

The registration used only 13 retained public metadata GETs totaling 340,703
body bytes. It sent zero requests to an EDF URL and transferred zero EDF body
bytes.

Push CI `31354565966` passed Base Python job `93351737101` and Optional Neuro
Readers job `93351737088` at the exact registration commit. Local verification
passed 26 focused tests, the 1,476-test dependency-light suite with 168 expected
skips, the 1,532-test retained-classical suite with 34 expected skips, Ruff
0.15.20, compileall, all registry JSON parsing, and `git diff --check`.

## Ordered Authorization

Authorization is conditional. Sending the exact sentence does not permit an
immediate download or model run.

### 1. Authorization-only decision

The exact maintainer sentence below must first be recorded in separate human
and machine decision artifacts. That decision-only commit must be pushed, and
both required CI jobs must be green.

The decision stage performs no metadata request, EDF operation, dependency
operation, fixture generation, fit, inference, target delivery, or score.

### 2. Generated-fixture implementation

Only after the decision commit is remotely green may Codex implement:

- an exact 72-file acquisition allowlist and mocked transport;
- no-follow path, hash, byte, disk, wall-time, RSS, and one-shot guards;
- the strict sequential MNE reader and 64-channel validator;
- the target firewall and isolated sealed scorer input;
- causal CAR and `0.5-4 Hz` SOS preprocessing;
- the fixed participant-specific LDA and all 18 conditions;
- deterministic label, row, channel, and hemisphere controls;
- low-frequency lateralization features;
- the aggregate hash-only freeze and isolated aggregate scorer;
- resource receipts and dry-run-first CLI commands; and
- malformed and generated synthetic fixture qualification.

Implementation may not stat or open any local PhysioNet path, request a public
EDF URL, or inspect a real header, annotation, sample, target, channel, or
geometry value.

The existing Git-ignored environment may be reused only if it reports exactly
NumPy `2.5.2`, SciPy `1.18.0`, MNE `1.12.1`, scikit-learn `1.9.0`, and
pyRiemann `0.12`. Missing or changed versions park the sequence. This request
authorizes no package installation, dependency resolution, or network access
for tooling.

The implementation must be committed, pushed, and remotely green in both CI
jobs before any real acquisition or local PhysioNet operation.

### 3. One exact acquisition

Only after the exact implementation is remotely green may one acquisition
invocation:

1. reverify the official dataset page, task mapping, checksum manifest, and
   twelve exact S3 subject-prefix listings using metadata only;
2. refuse before an EDF body request on any version, DOI, license, access,
   path, size, or checksum mismatch;
3. request only the 72 registered EDF payloads, sequentially and without
   retry;
4. write only to the new isolated WO9R temporary root;
5. make one opaque local size/SHA-256 pass per completed EDF without parsing;
6. refuse the entire bundle on any mismatch, cap breach, or unexpected path;
7. promote only the complete exact bundle into the absent final root; and
8. emit one machine manifest and one human receipt under 1 MiB combined.

The acquisition stage is capped at one thread, one worker, one numerical job,
900 seconds, 268,435,456-byte peak RSS, 2,097,152 metadata body bytes, exactly
184,252,032 EDF payload bytes, 402,653,184 incremental disk bytes, and at least
21,474,836,480 free disk bytes before start. It may clean up only temporary
files created by its own invocation.

Acquisition does not authorize MNE import, EDF parsing, annotation access,
signal access, split creation, fitting, inference, scoring, or a second
invocation.

### 4. One target-blind analysis

After the exact acquisition succeeds and only while no earlier gate has failed,
one no-network analysis execution may:

1. no-follow verify the private manifest and all 72 regular files;
2. make one new sequential size/SHA-256 pass and one semantic MNE parse per EDF;
3. read exact headers, the registered 64 EEG channels, available geometry,
   160 Hz signal samples, and only `T0`, `T1`, and `T2` annotations;
4. require exactly 15 `T1`/`T2` events per EDF and retain every registered
   participant, channel, run, and trial;
5. target-firewall 720 fit rows, 360 target-free final rows, and one isolated
   sealed 360-target scorer input;
6. run at most 144 participant-specific parameter-update fits and 216
   target-blind inference runs, with a valid freeze requiring all 18 condition
   families and all 216 participant-condition prediction sets;
7. freeze the registered low-frequency physiology inputs without applying a
   target-dependent statistic; and
8. emit one aggregate hash-only prediction ledger containing no individual
   prediction, probability, target, or participant outcome.

The reader necessarily materializes final annotations long enough for the
firewall to isolate them. The predictive and selection code receives only the
target-free derivative. This is a function-and-artifact boundary, not an
operating-system sandbox or a physical-never-opened claim.

All run-11 and run-12 predictions freeze together. The public ledger must be
committed and pushed, and both CI jobs must be remotely green, before either
final target set is delivered to the scorer.

The analysis is capped at one thread, one worker, one numerical job, 1,800
seconds through freeze, 1,073,741,824-byte peak RSS, 67,108,864 private
generated bytes, 2,097,152 public freeze/result bytes, zero network bytes, zero
new payload bytes, zero retry, zero rerun, and zero post-target update.

### 5. One combined final score

Only after the exact hash-only freeze is committed, pushed, and remotely green
may the isolated scorer receive both final target sets together once. It may:

- verify every frozen source, derivative, configuration, dependency,
  implementation, prediction, and firewall receipt hash;
- score the same 180 execution and 180 imagery final targets once;
- compute aggregate and participant-level registered metrics and exact
  participant sign-flip tests;
- apply H1, H2, H3, every mandatory control, and the ordered router; and
- emit only bounded aggregate public results and stop.

No individual target, prediction, probability, or participant outcome may be
committed, uploaded, or published.

## Maximum Result

`WO9R-R4` would establish only this:

> On twelve previously unused public EEGMMIDB participants, the frozen
> low-frequency model recovered held-out left/right task information across
> execution and imagery, and the registered motor-compatible localization and
> proxy-control conjunction passed.

Even that result would not establish brain-specific origin. The protocol uses
class-correlated visual cues, lacks dedicated EOG/EMG and measured movement
onset, remains within one public dataset, and is executed by the same research
team. It would not establish unseen-person decoding, typing, language or
thought decoding, end-to-end real-time performance, portable hardware, home
use, assistive benefit, or clinical utility.

## Exact Authorization Sentence

The request becomes active only if the maintainer sends this sentence exactly:

> Authorize the WO9R PhysioNet low-frequency cohort-confirmation implementation and one registered acquisition, target-blind analysis, prediction-freeze, and scoring sequence exactly as scoped in docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PREREGISTRATION.md and registries/physionet_low_frequency_cohort_confirmation_contract.v0.json. I bind registration commit 716e5432498052b78cb799c9f4e3bfbae68e3ad2 and green CI run 31354565966, including Base Python job 93351737101 and Optional Neuro Readers job 93351737088. I authorize, only after a separate authorization-only decision is committed, pushed, and remotely green, one generated-fixture-and-mocked-transport-only implementation of the exact acquisition allowlist, sequential EDF reader, target firewall, causal low-frequency preprocessing, fixed participant-specific LDA family, 18 registered prediction and control conditions, low-frequency physiology assay, aggregate hash-only prediction freezer, isolated scorer, resource monitors, receipts, and dry-run-first CLI; and reuse without modification of the existing Git-ignored environment only if it contains exactly NumPy 2.5.2, SciPy 1.18.0, MNE 1.12.1, scikit-learn 1.9.0, and pyRiemann 0.12, with no dependency installation or tooling network access. I authorize, only after that exact implementation is committed, pushed, and remotely green, metadata-only reverification of the 15 registered official source surfaces and one no-retry acquisition invocation for only the 72 named PhysioNet EEGMMIDB v1.0.0 S004-S015 runs 03/04/07/08/11/12 EDF files totaling exactly 184,252,032 bytes; exactly 72 sequential EDF payload requests; one opaque local size and SHA-256 pass per EDF without content parsing; creation of one new isolated complete bundle; and one machine manifest and human receipt under 1 MiB combined, using one CPU thread, one worker, one numerical job, 900 seconds, 268,435,456-byte peak RSS, 2,097,152 metadata body bytes, 402,653,184 incremental disk bytes, at least 21,474,836,480 free disk bytes, cleanup only of invocation-created temporary files, and zero retry or rerun. I authorize, after that exact acquisition succeeds and no earlier gate fails, one no-network target-blind analysis over only the same 72 EDFs: one no-follow private-manifest verification, one new sequential size and SHA-256 pass and one semantic MNE parse per EDF; reading their exact headers, all 64 registered EEG channels, available geometry, 160 Hz signal samples, and only T0, T1, and T2 EDF+ annotations; target-firewalled creation of exactly 720 fit rows, 360 target-free final rows, and one isolated sealed 360-target scorer input; at most 144 participant-specific parameter-update fits and 216 target-blind model-inference runs, with a valid freeze requiring all 18 condition families and all 216 participant-condition prediction sets; creation of the registered target-blind low-frequency physiology inputs; and one aggregate hash-only prediction-freeze ledger containing no individual prediction, probability, target, or participant outcome. I authorize, only after that freeze ledger is committed, pushed, and remotely green in both required CI jobs, one combined delivery and one scoring event for the same 180 run-11 execution targets and 180 run-12 imagery targets, application of the frozen H1, H2, H3, mandatory-control, and WO9R-R0 through WO9R-R4 router, and bounded aggregate result emission. The analysis and scoring sequence is limited to one CPU thread, one worker, one numerical job, 1,800 seconds through freeze, 1,073,741,824-byte peak RSS, 67,108,864 private generated bytes, 2,097,152 public freeze and result bytes, zero network bytes, zero new payload bytes, cleanup only of invocation-created temporary files, one final-target delivery, one scoring event, zero retry, zero rerun, and zero post-target update. I do not authorize any .event sidecar; any additional file, participant, run, dataset, download, substitution, or dependency installation; S20, S21, S24, S25, SpanishBCBL, raw FIF, or MAT access; cross-participant fitting or row-random splitting; final-target use by predictive, selection, threshold, channel, normalization, or update code before the remotely green freeze; target-derived exclusion; evaluation-time fit or test-time adaptation; filter, window, channel, classifier, threshold, or hyperparameter search; larger or additional models; deep network, CML-v0, pretrained checkpoint, foundation or language model, provider, RW3, stream, device, hardware, individual target, prediction, probability, or participant-outcome publication, release, independent-replication claim, or scientific claim beyond the registered WO9R-R4 within-EEGMMIDB motor-compatible task-effect ceiling.

## Current Counters

Preparing this packet performed no new metadata request. The inherited
registration evidence remains 13 public metadata GETs and 340,703 retained
body bytes, with zero EDF URL requests and zero EDF bytes.

All local PhysioNet stats, opens, hashes, parses, header reads, annotation
reads, signal reads, target reads, dependency installs, derivative or firewall
operations, fits, inferences, freezes, target deliveries, scores, provider
calls, hardware operations, retries, and reruns remain zero.

Engineering capability if the future registered sequence passes: one exact,
resource-bounded, target-firewalled twelve-person confirmation of the
low-frequency EEG lead can be executed with matched execution/imagery and
failure-addressable localization and confound controls.

Scientific claim not established by this request: authorization planning opens
no EDF content or target and runs no model, so it establishes no replicated
task effect, brain-specific neural origin, generalization, decoding, latency,
device, or human-benefit result.
