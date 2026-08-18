# MARC2-VR12A P15 Run-Index Repair Implementation

Date: 2026-08-18

Lane: `MARC2-VR12A`

Status: **Generated-only implementation remotely green; proof-only closeout
pending its own remote proof**

Contract:
`registries/marc2_p15_run_index_repair_contract.v0.json`

Implementation:
`src/neurodecodekit/datasets/marc2_p15_run_index_repair.py`

## Implementation Boundary

The new module is additive and dependency-light. It does not edit, import, or
call the consumed VR11P executor and exposes only `plan` and `qualify` CLI
commands. There is no private or real-data execution surface.

The adapter performs four ordered operations on generated 1,227-row sources:

1. validate the exact green registration and existing VR2/selector contracts;
2. validate every source row while accepting only one- or two-digit ASCII run
   indices;
3. group by subject, session, and base-10 run value while requiring one lexical
   run token and four unique companions per logical run; and
4. reuse the frozen eligibility classifier and prefix selector, then separately
   audit source-exact selected names, split roles, semantic run IDs, reservation
   bytes, rank, and cap arithmetic.

Historical selector and VR2 modules remain byte-identical. The adapter returns
source-exact member names, not rewritten padded aliases.

## Generated Qualification

One final measured qualification reached `MARC2VR12A-G1`:

- 12/12 success paths passed across three spelling variants, two row orders,
  and two replays;
- padded, unpadded, and bundle-consistent mixed-width sources produced the same
  semantic cohort digest;
- each spelling retained a distinct raw source hash and distinct selected-name
  hash;
- the generated selection remained 16 subjects, 96 run bundles, and 384 core
  members;
- source objects were unchanged and every reservation replayed from the exact
  UTF-8 member name;
- all eight named P15/P16/P18/P19 witnesses refused;
- all 36 direct refusals passed; and
- no generated output was retained.

Measured resources:

```text
generated input bytes:       5,147,208
aggregate output bytes:          2,498
retained output bytes:               0
runtime seconds:              1.092868332983926
peak RSS bytes:                 44,417,024
CPU threads/workers/jobs:             1/1/1
raw-data reads:                          0
real-cache reads:                        0
model runs:                              0
training runs:                           0
end-to-end latency measured:         false
```

Every private, consumed-state, archive, neural, event, target, cohort, FW2,
CIL1, model, prediction, score, network, provider, hardware, other-project,
release, and claim counter remained zero.

## Verification State

Thirty-four focused contract, behavior, and result tests pass. The complete
dependency-light suite passes 4,160 tests with 204 expected skips, exactly 34
tests above the 4,126-test pre-change baseline. The local optional-neuro sweep
ran 4,231 tests with 35 expected skips and two late mechanical-gate failures;
both affected test files pass in fresh one-thread processes. This is recorded
as an accumulated-process resource-state limitation, not hidden as a green
single-process run. The required clean Linux Base Python and Optional Neuro
Readers jobs remain the authoritative remote gate.

Ruff, compilation, registry parsing, CLI help and plan, and diff checks pass.
The implementation registry intentionally keeps `remote_implementation_proof`
bound to exact implementation `873484aaf270bc5b1499e4b0449c9e8ef138c623`,
which passed Base Python job `95819297085` and Optional Neuro Readers job
`95819297010` in CI `32170217284`. The measured generated qualification was not
rerun and no private operation occurred for this proof-only closeout.

## Next Gate

Commit and push this proof-only closeout, then require both remote jobs to pass.
Only after that closeout is remotely green may an all-false Tier C structural-
confirmation packet be prepared.

Engineering capability added: a generated, standards-aligned run-index adapter
can preserve semantic selection across padded and unpadded names without
rewriting source names or weakening structural controls.

Scientific claim not established: no private source, real cohort, archive
payload, neural sample, target, model, prediction, score, live decoder, or
thought-to-text capability was accessed or established.
