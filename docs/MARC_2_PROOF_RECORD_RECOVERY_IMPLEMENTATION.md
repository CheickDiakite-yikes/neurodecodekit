# MARC2-FW1B Proof-Record Recovery Implementation

Date: 2026-08-13

Status: **Generated shared validator qualified; exact implementation must pass
both remote CI jobs before an all-false live-recovery request is eligible**

Registry:
`registries/marc2_proof_record_recovery_implementation.v0.json`

Module:
`src/neurodecodekit/datasets/marc2_proof_record_recovery.py`

## What Was Added

NeuroDecodeKit now has one dependency-free public validator:

```text
neurodecodekit.datasets.marc2_proof_record_recovery
  .validate_implementation_record
```

It accepts three explicit inputs:

1. strict implementation-record bytes;
2. an expected remote-green proof envelope; and
3. a separately observed remote-green proof envelope.

The validator requires those proof envelopes to agree, requires observed HEAD
to equal the implementation commit, requires a clean tracked worktree and the
registered green ancestor, and requires the separately supplied registry hash
to equal the actual record bytes. This makes expected authority and observed
repository state distinct inputs instead of allowing one object to stand in
for both.

The generated qualifier and any future additive live wrapper must call this
same public function. The validator checks its own module, symbol, and source
hash through the candidate record. A copied, aliased, forked, or weaker closure
routes `MARC2FWR-F05`.

## Strict Record Boundary

The accepted record has exactly 15 top-level fields in frozen order and now
includes the field missing from the consumed predecessor:

```json
"lane_id": "MARC2-FW1B"
```

The parser rejects malformed UTF-8, a BOM, raw NUL bytes, duplicate keys,
non-finite numbers, non-object roots, trailing content, oversized input, and
unknown or reordered top-level fields.

Tracked artifacts must be unique normalized repository-relative regular files
with exact lowercase SHA-256 values. The implementation registry is prohibited
from binding itself; its bytes arrive as the separately hashed validator input.
The validator source must be one of the bound artifacts, and the declared
source hash must match both its binding and filesystem bytes.

## Runtime-Name Portability Repair

The first generated CLI development probe correctly refused at
`MARC2FWR-F02` before candidate construction because Python `-m` execution
sets runtime `__name__` to `__main__`. Imported tests used the canonical package
name, so a runtime-derived module identity would have made CLI and library
proofs disagree.

The final implementation freezes this canonical identity instead:

```text
neurodecodekit.datasets.marc2_proof_record_recovery
```

Both imported tests and `python -m` now emit the same validator identity. The
refused development probe used no private, real, network, payload, neural,
target, model, or score input and created no output.

## Commands

The standalone module exposes only:

```bash
python -m neurodecodekit.datasets.marc2_proof_record_recovery plan
python -m neurodecodekit.datasets.marc2_proof_record_recovery qualify \
  --output /private/tmp/neurodecodekit-marc2fw1b-check
python -m neurodecodekit.datasets.marc2_proof_record_recovery inspect \
  --report /path/to/marc2_proof_record_recovery_qualification.v0.json
```

There is no `execute` command, URL, network client, retained private path,
archive reader, signal reader, target interface, model interface, or scorer.
`qualify` creates one aggregate generated report, reads it back through
`inspect`, and removes the report and its invocation-created directory before
returning. It refuses an existing destination and never cleans a directory it
did not create.

## Qualification Matrix

The canonical candidate is validated twice. Its deterministic aggregate
summaries are byte-identical. The qualifier then calls the same public
validator for all 32 ordered mutations:

| Route | Count | Covered defect class |
|---|---:|---|
| `MARC2FWR-F00` | 7 | schema, version, lane, implementation ID, or status |
| `MARC2FWR-F01` | 7 | empty, unsafe, duplicate, malformed, mismatched, or circular bindings |
| `MARC2FWR-F02` | 5 | predecessor, commit, CI/job, registry hash, HEAD, or green proof |
| `MARC2FWR-F03` | 4 | qualification gates, inherited counts, or mutation order |
| `MARC2FWR-F04` | 7 | execution state, retry, access, authority, or next gate |
| `MARC2FWR-F05` | 2 | claim boundary or shared-validator closure |

All 32 refused on their registered routes. Together with the two canonical
calls, the generated qualifier exercised the shared validator 34 times.

## Measured Generated Run

One fresh one-thread process produced:

```text
route:                         MARC2FWR-G1
canonical validations:        2
registered mutations:         32 / 32 passed
shared-validator calls:       34
top-level candidate fields:   15
tracked generated artifacts:  4
generated input bytes:        84,701
generated output bytes:       6,711
internal runtime seconds:     0.01692712500516791
reported peak RSS bytes:      27,099,136
CPU threads / workers / jobs: 1 / 1 / 1
network bytes:                0
private or real input bytes:  0
temporary output removed:     yes
report SHA-256:               80ee6a1222c53a5545504421eaec0216d14e724d1b3dec2d8e6023c81456634f
```

The generated input is the candidate record plus four committed public source,
contract, documentation, and test artifacts. It is not a participant manifest
or neural payload.

## Test Coverage

Twenty-three focused behavior tests cover:

- exact green-contract loading;
- canonical CLI and import module identity;
- strict JSON encoding and object rules;
- all 15 fields and the required lane ID;
- artifact safety, exact hashes, and anti-self-binding;
- expected-versus-observed proof separation;
- deterministic replay and all 32 mutations;
- all-false authority and zero access counters;
- output caps, aggregate inspection, existing-output preservation, and exact
  cleanup;
- one generated CLI roundtrip and aggregate refusal output; and
- the absence of an `execute` subcommand or non-standard-library import.

The implementation-record test separately binds every committed file and the
measured qualification. The complete dependency-light suite passes 3,134 tests
with 204 expected skips. The optional-neuro inventory passes 3,205 tests with
35 skips across fresh A-M and N-Z processes: 2,692 tests with 28 skips and 513
tests with seven skips. Ruff, compilation, strict parsing of all 214 registry
documents, CLI help/plan/roundtrip, artifact hashes, and diff hygiene pass.

## Access and Authority

The implementation and qualification performed zero:

- retained private path checks, lstats, opens, reads, hashes, or parses;
- real participant or archive-member selections;
- network requests or payload bytes;
- archive local-header or member reads;
- EEG samples, events, targets, labels, quality, onset, or channel reads;
- derivatives, caches, splits, features, training, inference, predictions,
  freezes, target deliveries, or scores;
- provider, language-model, stream, device, or hardware operations; and
- retries, reruns, consumed-root operations, or scientific claim upgrades.

Private execution limit remains zero. The next eligible artifact after this
exact implementation is remotely green is an all-false Tier C request. That
request may propose a new additive live wrapper and at most one later private
selection, but it cannot itself authorize either operation.

## Claim Boundary

Engineering capability added: a shared implementation-record validator now
accepts the complete generated `MARC2-FW1B` record and rejects all 32 registered
proof defects through the exact code path reserved for any future live gate.

Scientific claim not established: no human neural data, target, prediction, or
score was accessed, so this establishes no neural effect, decoding accuracy,
language decoding, or thought-to-text capability.
