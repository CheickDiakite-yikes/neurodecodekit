# MARC-1 Generated Qualification Implementation

Date: 2026-08-11

Status: **generated implementation complete; registered measured closeout not
executed; all public, real-data, neural, target, model, and score access remains
unauthorized**

Registry:
`registries/marc1_generated_qualification_implementation.v0.json`

## Green Contract Boundary

Implementation began only after contract commit
`4494d57bd3853ebb2e198747861c908cdb2a0bb1` passed both required jobs in CI
run `31502115918`:

```text
Base Python:             93814507482
Optional Neuro Readers: 93814507355
```

The implementation is bound to contract SHA-256
`17733537c6a5038eb0781098a4b2452d71526c47eb4314cebb19d1975f79a7ad`.

## Implemented Surface

The dependency-free module is
`neurodecodekit.datasets.marc1_generated_qualification`. It exposes only:

```text
python -m neurodecodekit.datasets.marc1_generated_qualification plan
python -m neurodecodekit.datasets.marc1_generated_qualification qualify --output-dir PATH
python -m neurodecodekit.datasets.marc1_generated_qualification inspect REPORT
```

There is no URL opener, network client, host, archive path, participant,
target, model, provider, or `execute` option. `inspect` validates only the
aggregate report and refuses the generated private manifest.

## Archive Mechanics

The implementation builds one deterministic in-memory ZIP with exactly 14
regular members, including one tiny `.eeg` member written with
`force_zip64=True`. A maximum-length deterministic ZIP comment keeps the
standard library's EOCD search inside archive metadata rather than generated
member payloads.

`zipfile.ZipFile` reads the archive through an instrumented, read-only,
seekable adapter. The adapter records every range and refuses before exceeding
the shared call or byte cap. The validator checks safe NFC POSIX-relative
paths, exact member identity, duplicates, file type, flags, compression,
compressed and uncompressed sizes, ratio, and forced ZIP64 observation. It
then proves that no read intersected a writer-observed compressed-payload
interval. No member is opened, read, or extracted.

The private generated manifest records the seven frozen member fields. The
aggregate report contains only counts, sizes, methods, hashes, measurements,
warnings, unavailable fields, refusal summaries, and claim boundaries.

## Multimodal Firewall

The generated plan implements Freewill-like EEG/EOG/acceleration/audio and
Wrist-like EEG/EMG/encoder/trigger profiles. Every channel keeps source type,
functional role, and model inclusion separate. Only EEG may be a candidate or
spatial proxy; every peripheral and trigger stream is nonpredictive.

The plan validates explicit geometry and clock states, same-amplifier
synchronization, a causal `[-1.5, -0.2)` interface window, zero future context,
fit-only normalization, and exact source-specific sample boundaries. The
window remains an interface fixture rather than a selected future real-data
window.

Fit rows, target-blind prediction rows, and isolated scorer rows have different
physical schemas. Fit and held-out identities are disjoint, prediction and
scorer identities match exactly, and prediction rows cannot contain a target.
All twelve comparator roles have explicit availability by source. Generated
features are fixed identity values and do not depend on generated labels or
targets. No model is implemented or run.

## Refusals And Outputs

All 24 frozen mutations are implemented and must route to their assigned
`MARC1G-F01` through `MARC1G-F06` class. Replay disagreement routes
`MARC1G-F07`. Outputs require a non-existent destination under a real
non-symlink parent, are written through a temporary sibling, and are renamed
atomically. Existing destinations, symlink parents, private fields in the
aggregate report, over-cap output, and non-one thread settings refuse.

The registered measured closeout has not run. Development and unit-test
fixtures have no scientific meaning. Commit and push this exact implementation
and require both CI jobs green before one measured generated CLI qualification.

The first implementation push `ff34a9e` passed Base Python but failed three
optional-job CLI subprocess tests. Each child returned the module's own
`MARC1G-F06` refusal; no report or closeout artifact was created. The focused
test-harness correction starts every CLI probe with Python `-S`, isolating the
standard-library module from optional site-package startup. It does not change
the implementation source, resource caps, route logic, or scientific boundary.
This corrected test hash must become remotely green before the closeout.

## Claim Boundary

Engineering capability added: a dependency-free implementation now enforces
bounded ZIP inventory, modality semantics, causal windows, split isolation,
target withholding, comparator availability, deterministic replay, output
privacy, and resource caps on generated fixtures.

Scientific claim not established: no public archive, human neural signal,
event, onset, target, model, prediction, or score was accessed, so this work
establishes no neural effect, movement decoding, or source attribution.
