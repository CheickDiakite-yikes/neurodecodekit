# MARC2-VR19A F04 Task-Implication Preregistration

Date: 2026-08-21

Lane: `MARC2-VR19A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_f04_task_implication_contract.v0.json`

## Why VR19A Exists

The consumed VR18P invocation returned `MARC2VR18P-R4`. Its frozen evidence is
exactly VR16A F04 / `core identity differs`, but the public route name retains
the broader phrase “core task or identity.” VR19A asks a narrower code-level
question: under the exact committed VR16A producer, what condition can emit
that exact route-and-reason pair?

This lane never reads VR18P private or ignored state. It uses only committed
source, committed aggregate records, and generated 1,227-row fixtures.

## Frozen Static Inventory

Within VR16A `_validate_variable_entry`, F04 has two production references:

1. the exception translator selects F04 only when
   `match.group("task") != "freewill"`, then emits `core identity differs`;
2. the later explicit task guard emits F04 / `Freewill task differs` under the
   same inequality.

The private R4 map accepts only the first pair. The later explicit task reason
would not map to R4. VR19A must AST-bind both producer references and prove that
the exact F04 / `core identity differs` pair has the non-`freewill` task guard.

## Frozen Generated Matrix

Eight cases run under canonical and reversed row order with two exact replays:

| Class | Cases | Exact expected VR16A evidence |
|---|---:|---|
| control | 1 | success |
| non-`freewill` task | 4 | F04 / `core identity differs` |
| identity counterexample with task unchanged | 3 | F03 / `suffix-bearing identity differs` |

The four task witnesses are `motor`, `rest`, `Freewill`, and `freewill2`. They
are generated tokens, not guesses about the private source. The three identity
counterexamples are subject-repeat mismatch, session-repeat mismatch, and
subject-width mismatch. G1 must occur four times, R1 sixteen times, and R2
twelve times across 32 unchanged VR16A calls.

## Frozen Hypotheses

1. The exact committed function has two F04 producer references and both are
   dominated by `task != "freewill"`.
2. F04 / `core identity differs` is produced only by the first guarded
   exception translation; the later reason remains distinct.
3. Every generated non-`freewill` task witness reaches that exact pair in both
   orders and both replays.
4. Every generated identity counterexample that leaves task unchanged routes
   to F03 rather than F04.

Any failed hypothesis parks VR19A. No post-result amendment is allowed.

## Resource And Authority Boundary

- one CPU thread, one worker, one numerical job;
- 30 seconds maximum;
- less than 256 MiB peak RSS;
- at most 32 MiB generated input;
- at most 1 MiB aggregate output; and
- zero retained output.

Implementation may begin only after this exact registration commit passes
both required CI jobs. The lane authorizes no `.codex_work`, private or
consumed source, archive member, neural payload, signal, event, target, label,
model, training, inference, prediction, score, network, provider, device,
hardware, other project, FW2/CIL1, release, retry, or scientific-claim
operation.

Eight focused contract tests and all 4,637 dependency-light tests pass with
204 expected skips. Ruff, strict parsing of 340 registry JSON files, and diff
hygiene also pass.

## Result Ceiling

A passing result may tighten the aggregate interpretation from “task or
identity” to “non-`freewill` task class under exact VR16A semantics.” It may
not identify the token, row, path, person, task spelling, cohort, or cause
outside that frozen code version. It does not authorize another private read.

Engineering capability sought: exact code-and-fixture proof of the condition
that produces the consumed aggregate route.

Scientific claim not established: this lane contains no neural payload,
target, model, prediction, score, language result, live run, or thought-to-text
evidence.
