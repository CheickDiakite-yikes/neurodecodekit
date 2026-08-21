# MARC2-VR19A F04 Task-Implication Result

Date: 2026-08-21

Lane: `MARC2-VR19A`

Status: `MARC2VR19A-G1` generated qualification passed

Machine result: `registries/marc2_f04_task_implication_result.v0.json`

## Result

All four preregistered hypotheses passed. The exact VR16A validator contains
two F04 producer references, both guarded by a task token unequal to lowercase
`freewill`. The exact F04 / `core identity differs` pair retained by consumed
VR18P R4 is unique to the earlier guarded exception translation.

Four generated non-`freewill` witnesses reached that pair under both orders
and two replays. Three task-preserving identity counterexamples instead
reached F03 / `suffix-bearing identity differs`. Route counts were exactly
G1=4, R1=16, and R2=12 across 32 unchanged VR16A calls.

This tightens the consumed aggregate interpretation: under exact committed
VR16A semantics, R4 implies a non-lowercase-`freewill` task class, rather than
an unresolved task-or-identity class. It does not identify the private token,
spelling, row, path, participant, selection, or cohort.

## Measurements

```text
fixed tracked input:    102,770 bytes
generated input:        13,748,732 bytes
aggregate output:       2,326 bytes
retained output:        0 bytes
runtime:                1.759938333008904 seconds
peak RSS:               51,429,376 bytes
VR16A calls:            32
direct refusals:        40
network bytes:          0
```

## Next Gate

Commit, push, and green the exact implementation/result, then add a proof-only
closeout without rerunning qualification. Only after that may a separately
frozen all-false Tier C packet be considered. VR18P itself remains consumed
and may not be retried or reinspected.

Engineering result: the real structural blocker is localized to the
non-lowercase-`freewill` task class under the bound parser, without exposing a
private task value.

Scientific result not established: this is structural code-path evidence, not
neural data or decoding evidence, and it establishes no neural effect,
accuracy, language decoding, live operation, or thought-to-text capability.
