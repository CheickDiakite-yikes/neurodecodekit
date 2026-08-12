# MARC-1 Privacy-Preserving Pilot Selection Result

Date: 2026-08-12

Status: **consumed at `MARC1PSG-R1`; generated engineering qualification
passed; no retry or rerun; real metadata and every scientific operation remain
closed**

Registry:
`registries/marc1_privacy_preserving_pilot_selection_result.v0.json`

## Green Implementation Gate

The one registered closeout ran only after exact implementation commit
`0c0a6982c6b9c65d6c51413d1baa8b577e00a194` passed both required jobs in CI
run `31571668853`:

```text
Base Python:             94034790262
Optional Neuro Readers: 94034790315
```

The execution bound implementation registry SHA-256
`09f3c559ba83b2eec47a36b8772a8904c4b2783e1e443f8999bf2c2371e6a4d1`.

## Registered Execution

Exactly one fresh Python `-S` process ran with every numerical thread variable
set to one and a new output directory. The process generated its complete
1,227-row Freewill fixture and 55-row Wrist fixture in memory. It had no
network client, real input path, archive opener, event or signal reader,
target interface, model, or scorer.

The command completed once with `MARC1PSG-R1`:

```text
generated input bytes:       873,348
aggregate report bytes:        6,946
private manifest bytes:       175,618
combined output bytes:        182,564
runtime:                        0.22733404207974672 seconds
reported peak RSS:             32,374,784 bytes
external wall time:             0.34 seconds
external maximum RSS:          32,423,936 bytes
joint payload reservation:  1,228,139,402 bytes
```

The aggregate report SHA-256 was
`e76b2ff0c8d74c3d298c0ff83e9ee093e08f3f02e02e1d264543fad749e3890d`.
The generated private manifest SHA-256 was
`e1b2db1506f94efcc7f85081d9df901349498a8b9a681156d5d37121a887e831`;
it was written mode `0600`. The aggregate report was inspected once through
the registered CLI. Both files and the invocation-created directory were then
removed. Only hashes and aggregate measurements are retained.

## Selection Result

The exact frozen selection mechanics replayed:

- 12 preregistered participants per source;
- 36 Freewill session-1 fit bundles and 36 session-2 held-out bundles;
- 288 opaque Freewill core-member rows across those 72 bundles;
- 12 Wrist participant archives;
- Wrist runs 1-6 reserved for fit and runs 7-8 reserved for held-out use;
- 300 exact rows confined to the generated private manifest; and
- a conservative joint payload reservation of 1,228,139,402 bytes, below the
  8-GiB cap.

The two DOI-bound participant ranks and all split identities were invariant to
complete input-row reversal. Within-cap fixture size and CRC changes changed
provenance only; they could not change participant, run, session, or split
selection.

## Adversarial Result

All 36 frozen mutations refused in their assigned class:

```text
MARC1PSG-F00:  1
MARC1PSG-F01:  5
MARC1PSG-F02:  9
MARC1PSG-F03: 13
MARC1PSG-F04:  2
MARC1PSG-F05:  2
MARC1PSG-F06:  4
```

All 15 acceptance gates passed. Every private-real-manifest, public-metadata,
payload, local-header, signal, event, target, quality, derivative, training,
inference, prediction, score, provider, hardware, retry, rerun, and claim
counter remained zero.

## Same Research Path

MARC-1 is not a pivot away from thought-to-text. It is a confound-resolution
and positive-control rung on the same path: before interpreting a future
language-decoding result, the stack must show that it can recover a real neural
effect and distinguish that effect from cue timing, eyes, muscle, and motion.
The two frozen axes make that later attribution test cheaper and harder to
fool. They do not replace the later language-specific held-out experiment,
language-model-only baseline, or no-signal controls.

## Warnings And Unavailable Fields

- All inventory and metadata rows were generated fixtures with no human
  content.
- The selected participant identifiers were preregistered, but no real
  participant row was read.
- Declared generated sizes and checksums do not verify a real payload.
- Real member/archive identities, payload totals, integrity, geometry, signal
  quality, events, targets, movement onset, models, predictions, scores, and
  neural latency remain unavailable.
- End-to-end neural decoding latency was not measured.
- No thought-to-text evidence was produced.

## Verification

- 11 result-record invariants pass.
- The four-file focused selector suite passes 65 tests plus 17 subtests.
- All MARC tests pass: 274 tests plus 170 subtests.
- The dependency-light suite passes 2,413 tests with 204 expected skips in
  19.685 seconds; external maximum RSS was 215,089,152 bytes.
- The locally comparable optional-neuro suite passes 2,484 tests with 35
  expected skips in 56.290 seconds; external maximum RSS was 719,716,352
  bytes.
- Relative to the remotely green implementation baseline, each comparable
  complete suite adds exactly 11 tests and zero skips.
- Ruff, compilation, registry parsing, CLI help/plan/roundtrip, and
  `git diff --check` pass.

## Disposition

The generated closeout is consumed with no retry or rerun. A future real
selection requires a separately committed, remotely green, all-false Tier C
request followed by a fresh packet-bound maintainer decision. Until then, the
418,755-byte sealed Freewill inventory must not be opened and no Wrist metadata
body may be requested.

Engineering capability added: NeuroDecodeKit can deterministically bind a
privacy-preserving, storage-capped two-axis pilot from full-scale generated
metadata without using targets, signals, quality values, or outcomes.

Scientific claim not established: no real participant metadata, payload,
human neural signal, target, model prediction, or score was accessed, so this
result establishes no neural effect, source attribution, movement decoding,
or thought-to-text capability.
