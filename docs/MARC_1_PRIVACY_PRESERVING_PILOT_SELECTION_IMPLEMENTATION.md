# MARC1-P1 Privacy-Preserving Pilot Selection Implementation

Date: 2026-08-12

Status: **generated-only implementation complete; development qualification
passed; one registered generated closeout not executed; real metadata and
payload access remain unauthorized**

Registry:
`registries/marc1_privacy_preserving_pilot_selection_implementation.v0.json`

## Same Research Path

MARC1-P1 is not a pivot away from thought-to-text. It is a confound-resolution
rung on the same path: before interpreting a language decoder, NeuroDecodeKit
must demonstrate that its acquisition, split, control, and scoring machinery
can recover a real sensor-level effect without mistaking cue timing, eye
activity, muscle activity, or movement for neural language information.

Movement evidence cannot itself establish thought-to-text. A later
language-specific experiment still requires neural input, linguistic targets,
held-out predictions, no-signal and language-model controls, and one frozen
score.

## Green Contract Boundary

Implementation began only after exact preregistration commit
`d1218066e64dea502d263acf0c096ed7eab55a11` passed both required jobs in CI
run `31569417204`:

```text
Base Python:             94028013357
Optional Neuro Readers: 94028013230
```

The implementation is bound to contract SHA-256
`2099849ad13c6c1a97488e81cef8b21dcd61e59914d00fd43b9e76e8ccd5c39c`.

## Implemented Surface

The dependency-free module is
`neurodecodekit.datasets.marc1_pilot_selection`. It exposes only:

```text
python -m neurodecodekit.datasets.marc1_pilot_selection plan
python -m neurodecodekit.datasets.marc1_pilot_selection qualify --output-dir PATH
python -m neurodecodekit.datasets.marc1_pilot_selection inspect REPORT
```

There is no `execute` command, URL, host, credential, real inventory path,
participant override, seed override, size override, split override, archive
reader, local-header reader, payload reader, event parser, neurophysiology
reader, target interface, model, scorer, retry, rerun, or fallback surface.
The module imports only the Python standard library and runs under `python -S`.

## Generated Inputs

The Freewill fixture has the exact registered inventory scale:

```text
rows:                    1,227
regular files:           1,025
directories:               202
eligible participants:       19
complete session-1/2 runs:   195
core bundle members:         780
auxiliary files:             245
```

Every generated central-directory row uses the exact live-manifest field
shape. Source identity and three transport digests are nested strict objects.
Names must be NFC, relative POSIX paths; member type, method, flags, sizes,
CRC declaration, ZIP64 flag, local-header offset, and BIDS path/filename
identity are validated without opening a local header or payload.

The Wrist fixture has exactly 55 generated Figshare-style rows: 45 unique
participant archives and ten supplementary rows. File IDs, names, subject
identities, generated URLs, sizes, and matching MD5 declarations are strict.
There is no network client or archive opener.

## Frozen Selection

The implementation recomputes both participant cohorts from:

```text
SHA256(UTF8(selection_seed) || 0x00 || UTF8(subject_id))
```

It requires the exact preregistered 12-person rank on each axis. Selection is
independent of row ordering, compressed size, CRC, file ID, signal quality,
event count, target, or outcome.

For Freewill, the selector validates the published session-1/session-2 run
count matrix for all 19 eligible participants, requires every run bundle to
contain exactly `.eeg`, `.vhdr`, `.vmrk`, and `_events.tsv`, and selects runs
1-3 from each session for each frozen participant. This yields 36 fit bundles,
36 held-out bundles, and 288 core members.

For Wrist, it binds runs 1-6 as fit and 7-8 as held out for each frozen
participant. This yields 72 fit runs, 24 held-out runs, 2,880 expected fit
trials, and 960 expected held-out trials. Trial counts are source-design
expectations only; no event or target row exists in the fixture.

## Target Firewall And Caps

The selector accepts only generated metadata. Unknown fields, including a
target or quality field, refuse before selection. It has no method capable of
reading event content, signal samples, movement onset, labels, local headers,
member payloads, or archives.

Generated reservation accounting includes the registered conservative
Freewill local-header reserve. The development fixture selected:

```text
Freewill reserved bytes:      623,853,450 / 6 GiB
Wrist reserved bytes:         604,285,952 / 2 GiB
joint reserved bytes:       1,228,139,402 / 8 GiB
fallbacks or substitutions:              0
```

Changing size or CRC within the caps changes provenance and private hashes but
does not change participant, run, or split identity. Crossing either source
cap or the joint cap refuses without cohort reduction or budget expansion.

## Privacy And Replay

The private manifest contains 300 exact rows: 288 Freewill members and 12
Wrist archives. It records source, subject, session, run, split, opaque member
or archive identity, available file ID/offset/CRC, sizes, and provenance
hashes. The private file is written mode `0600`.

The aggregate report may expose only preregistered participant IDs, counts,
split totals, byte totals, hashes, measurements, warnings, unavailable fields,
routes, and claim boundaries. A recursive firewall rejects member names,
archive names, offsets, CRCs, file IDs, URLs, raw paths, and private values.
`inspect` accepts the aggregate report and refuses the private manifest.

Canonical sorting makes the private manifest and aggregate selection hashes
byte-identical after complete reversal of both input row orders. Two fixed-
measurement qualifications also emit byte-identical reports and manifests.

## Adversarial Qualification

All 36 frozen mutations execute and refuse in their assigned classes:

```text
MARC1PSG-F00:  1
MARC1PSG-F01:  5
MARC1PSG-F02:  9
MARC1PSG-F03: 13
MARC1PSG-F04:  2
MARC1PSG-F05:  2
MARC1PSG-F06:  4
```

They cover contract drift, private-inventory identity/mode/schema, unsafe or
unsupported members, BIDS identity, incomplete or crossed bundles,
eligibility/rank drift, size-based cohort/run selection, run-count and split
drift, source/joint caps, Wrist metadata identity, forbidden content access,
privacy leakage, overwrite, symlink, output, and replay failures.

## Development Qualification

One disposable development qualification passed constructed route
`MARC1PSG-R1`:

```text
generated input bytes:                    873,348
generated output bytes:                   182,563
aggregate report bytes:                     6,945
private manifest bytes:                   175,618
selected private rows:                        300
Freewill run bundles / members:          72 / 288
Wrist selected archives:                       12
mutations / acceptance gates:             36 / 15
reported runtime seconds:     0.2268019998446107
reported peak RSS bytes:                32,833,536
external wall seconds:                         0.28
external maximum RSS bytes:              32,915,456
```

The aggregate report SHA-256 was
`c9613c308fc4ce3cbb2901297e3c3a6de39ba7ceebb41c58524369ca60bc9c39`.
The private manifest SHA-256 was
`e1b2db1506f94efcc7f85081d9df901349498a8b9a681156d5d37121a887e831`.
The report was inspected through the module CLI, both exact files were
removed, and the invocation-created directories were removed.

This was a development run, not the one registered generated closeout. The
registered closeout becomes eligible only after this exact implementation is
committed, pushed, and both required CI jobs are green.

## Verification And Access Accounting

Twenty-six focused implementation tests pass. They cover full-scale fixture
shape, both frozen ranks, exact split and private-row binding, source and joint
caps, row-order replay, size/CRC independence, strict provenance, target-field
refusal, all 36 mutations, private mode, public leakage, output/resource caps,
standard-library imports, CLI help, and an isolated `python -S` roundtrip.

All 37 implementation-plus-record tests and all 263 MARC tests pass. The
complete dependency-light suite passes 2,402 tests with 204 expected skips in
19.915 seconds and 225,837,056-byte external maximum RSS. The optional-neuro
suite passes 2,473 tests with 35 expected skips in 55.729 seconds and
724,615,168-byte external maximum RSS. Both are exactly 37 tests above the
green preregistration baseline with no new skip. Ruff over the repository,
compilation, all 171 registry JSON parses, module CLI help and plan, the
isolated roundtrip, and `git diff --check` pass.

The development run made zero private Freewill manifest reads, Wrist metadata
requests, network requests, real participant/member selections, local-header
or payload reads, signal/event/target/quality reads, derivative rows, training
fits, model calls, prediction sets, target deliveries, scores, provider calls,
hardware operations, retries/reruns, releases, or claim upgrades.

## Next Gate

1. Commit and push this exact implementation and require both CI jobs green.
2. Run one fresh registered generated closeout and remove its outputs.
3. Record, test, commit, push, and green that consumed generated result.
4. Only then prepare one all-false Tier C request for a single private
   Freewill manifest read and one bounded Wrist metadata response.

No current or earlier maintainer continuation authorizes step 4. The future
packet must first become the sole remotely green Tier C gate, followed by a
fresh packet-bound decision.

Engineering capability added: NeuroDecodeKit can deterministically select a
privacy-preserving, storage-capped two-axis pilot from full-scale generated
metadata without using target, signal, quality, or outcome information.

Scientific claim not established: no real participant metadata, payload,
human neural signal, target, model prediction, or score was accessed, so this
implementation establishes no neural effect or thought-to-text capability.
