# MARC2-VR16A Variable-Width Run-Index Repair Implementation

Date: 2026-08-21

Lane: `MARC2-VR16A`

Status: **Generated implementation and measured qualification complete; remote
implementation proof pending**

Registration:
`registries/marc2_variable_width_run_index_repair_contract.v0.json`

Implementation record:
`registries/marc2_variable_width_run_index_repair_implementation.v0.json`

## Registration Barrier

Registration commit `7dba59355ca45c8ab5eafb9d8b7757edfc9755c5`
passed Base Python job `96699811237` and Optional Neuro Readers job
`96699811051` in CI `32458280634` before implementation began. The module
binds that exact proof and contract SHA-256
`308b80864553fd12a7bda7e4691aea35c63eebfbd651c7ed86ebc15e2fd41dec`.

## Added Surface

`src/neurodecodekit/datasets/marc2_variable_width_run_index_repair.py` is a
standard-library, generated-only adapter over the unchanged structural
producer and selector. It:

- accepts ASCII numeric run tokens matching `[0-9]+` under the existing
  1,024-byte member-name ceiling;
- canonicalizes a run token by removing leading zeroes before integer
  conversion;
- groups companions by semantic run identity while requiring source-exact
  lexical spelling within each companion set;
- refuses normalized companion collisions and incomplete bundles;
- preserves source-exact selected names and derives reservation bytes from
  those exact UTF-8 names;
- preserves participant taxonomy, eligibility, rank, session split, selected
  runs 1/2/3, and the 8 GiB reservation cap;
- recursively firewalls aggregate output; and
- exposes only `plan` and `qualify`, with no path, output, or `execute` surface.

The module has no private executor, network client, archive reader, signal
reader, model, scorer, or retained generated-output path.

## Source And Selection Domains

The first focused run caught an implementation error before qualification: it
applied the selected run set `{1, 2, 3}` to every bundle in the full generated
inventory. The established producer legitimately carries other run indices in
its ineligible structural rows. The corrected implementation canonicalizes
all syntactically valid inventory run indices, then enforces runs 1/2/3 only
on the selected fit and held-out rows.

This preserves both sides of the registration: BIDS-compatible numeric index
syntax for the source and the unchanged experiment-specific selected split.

## Measured Qualification

One fresh-process generated qualification completed route `MARC2VR16A-G1`:

| Measure | Result |
|---|---:|
| Width variants | 6 |
| Orders / replays | 2 / 2 |
| Success paths | 24 |
| Direct refusals | 50 |
| Distinct raw-source hashes | 6 |
| Distinct selected-name hashes | 6 |
| Generated input | 17,532,166 bytes |
| Temporary peak | 917,845 bytes |
| Aggregate output | 2,843 bytes |
| Retained generated output | 0 bytes |
| Runtime | 2.224372999975458 seconds |
| Peak RSS | 34,717,696 bytes |
| Threads / workers / numerical jobs | 1 / 1 / 1 |
| Raw-data / real-cache reads | 0 / 0 |
| Model / training runs | 0 / 0 |

Every spelling produced semantic digest
`254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba`.
Source objects remained byte-identical and reservations replayed from the
source-exact selected names.

## Verification

- 25 focused registration, behavior, and record-integrity tests passed.
- The complete dependency-light suite passed 4,471 tests with 204 expected
  skips in 101.135 seconds, 19 tests above the 4,452-test registration
  baseline and with zero new failures.
- Ruff passed the implementation module and behavior test.
- Python compilation and `git diff --check` passed before closeout.
- The measured CLI qualification respected every registered cap.

## Boundary

This implementation proves that the frozen generated structural pipeline can
preserve one semantic selection across unpadded, two-, three-, six-, 64-digit,
and bundle-consistent mixed-width zero padding. It does not reveal the hidden
VR15P token or prove the real source passes the repaired adapter.

No private path, archive member, neural payload, signal sample, target, model,
prediction, score, FW2/CIL1 operation, provider, hardware, release, or
scientific claim was opened. A real structural confirmation and cohort freeze
remain a separately frozen Tier C packet and fresh packet-bound decision after
this exact implementation and result are remotely green.
