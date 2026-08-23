# MARC2-VR35A Task-Aware Eligibility Repair Preregistration

Date: 2026-08-23

Lane: `MARC2-VR35A`

Status: preregistered artifact-only and generated-only; no private access

Machine contract:
`registries/marc2_task_aware_eligibility_repair_contract.v0.json`

## Why This Is The Next Repair

Protocol-conforming VR34P returned aggregate R2: the current participant-and-
session eligibility classifier sees more than the registered 195 eligible run
bundles. It exposed no count, task distribution, identity, participant, or
cohort, so this preregistration does not guess any of those values.

Static review identifies one concrete representation problem. VR2's
`_classify_key` receives only `(subject, session, run)` and destructures it as
`subject, session, _run`; task is absent. VR20A groups companions under the
same three-part key. The exact published task token is checked later when
selected rows are validated, after the task-blind eligibility total has
already been required to equal 195.

That ordering makes mixed-task surplus a mechanism compatible with R2, not a
proven explanation of the private result. Genuine
`task-reachingandgrasping` surplus or public count drift remains an explicit
alternative. VR35A tests both possibilities rather than choosing the positive
one.

## Frozen Repair

The generated adapter must preserve the existing strict source envelope,
normalized numeric run identity, four-companion completeness, participant and
session taxonomy, deterministic rank, fit/held-out split, 8 GiB reservation
cap, source-exact selected names, and privacy firewall.

It changes one ordering rule: retain one exact task token per logical bundle
and project exact lowercase ASCII `reachingandgrasping` bundles before
eligibility arithmetic and selection. Non-target task bundles may remain in a
valid full-source fixture but may never enter the projected count or selected
rows.

A successful projection still requires exactly 195 target-task eligible run
bundles and the frozen participant-session counts. It then runs the unchanged
rank-prefix selector and VR20A selected-row validation. Count, threshold, task,
rank, cap, and route overrides do not exist.

## Parallel Hypotheses

| Generated case | Frozen route | Meaning |
|---|---|---|
| baseline exact task and total | `MARC2VR35A-G1` | task-aware selection reproduces the frozen cohort |
| mixed-task surplus | `MARC2VR35A-G2` | task-blind total is above 195, exact-task total is 195, and the cohort equals baseline |
| exact-task surplus | `MARC2VR35A-R1` | exact-task projection remains above 195 |
| exact-task deficit | `MARC2VR35A-R2` | exact-task projection is below 195 |
| task/selection firewall witness | `MARC2VR35A-R3` | identity, companion, selection, split, storage, or privacy validation refuses |

The five cases run in canonical and reversed order across two exact replays:
20 paths total, with each route appearing four times. G1 and G2 must have the
same semantic cohort hash, and selected non-target rows must be zero. At least
80 direct refusal checks cover task case/alias drift, mixed companions,
normalized collisions, incomplete bundles, count drift, rank/split/storage
mutation, output leakage, replay, and resource boundaries.

## Resource And Access Boundary

- standard library only;
- one CPU thread, one worker, and one numerical job;
- 45 seconds maximum;
- peak RSS strictly below 256 MiB;
- at most 16 MiB generated input and 1 MiB aggregate output;
- zero retained output, network bytes, and new payload bytes;
- commands only `plan` and `qualify`;
- no private executor or generic path, task, count, threshold, rank, cap,
  output, retry, or resource override.

Registration and implementation may not touch `.codex_work`, a private or
Git-ignored path, consumed VR20P/VR34P state, archive headers or members,
signals, events, channels, geometry, targets, labels, caches, features,
models, predictions, scores, FW2/CIL1, providers, streams, devices, hardware,
release state, or another project.

## Acceptance And Next Gate

This registration must be committed, pushed, and green in both required CI
jobs before implementation. Only then may one generated implementation and
one registered qualification run. A future private wrapper or cohort freeze
requires a new all-false Tier C packet, proof closeout, and packet-bound
maintainer decision.

Engineering capability proposed: exact task identity becomes part of
structural eligibility before deterministic generated cohort selection, while
mixed-task and genuine target-task count drift remain separately observable.

Scientific claim not established: this preregistration reads no private or
neural data, creates no real cohort, and performs no training, inference,
prediction, scoring, streaming, or hardware operation; it establishes no
neural effect or decoding result.
