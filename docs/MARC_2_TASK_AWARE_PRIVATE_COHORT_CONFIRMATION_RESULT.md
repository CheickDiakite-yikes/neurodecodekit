# MARC2-VR36P Task-Aware Private Cohort Confirmation Result

Date: 2026-08-23

Lane: `MARC2-VR36P`

Status: **Consumed at aggregate R3 without a cohort freeze**

Machine record:

- `registries/marc2_task_aware_private_cohort_confirmation_private_result.v0.json`

## Proof Chain

The one invocation ran only after every registered barrier was remotely green:

| Barrier | Commit | CI | Base | Optional |
| --- | --- | ---: | ---: | ---: |
| Decision | `fd08dd6ee40b16d3b4f4312601fed3370b7e2ca5` | `32648347577` | `97215989173` | `97215989332` |
| Stage 1 | `8179f6fd4acb721ef25b023e02ac9160789f9d49` | `32650171033` | `97220389999` | `97220389862` |
| Proof closeout | `d4074081b86e6b6247f91150daa1e3253f6e2bd9` | `32651006809` | `97222491265` | `97222491354` |

## One Registered Invocation

The executor collected exactly three readiness samples with two fixed sleeps,
opened and strict-parsed exactly 418,755 target-free structural bytes once,
called VR33A once, and called unchanged VR35A once. It returned
`MARC2VR36P-R3` and wrote no cohort.

Measured execution:

```text
runtime:               10.088516000076197 seconds
peak RSS:              30,670,848 bytes
CPU / workers / jobs:  1 / 1 / 1
input bytes:           418,755
network / new payload: 0 / 0 bytes
signal / target bytes: 0 / 0
model / training runs: 0 / 0
cohort files written:  0
```

The registered two-MiB output cap was enforced before successful return. Exact
readiness-certificate, marker, and report-file sizes were not recovered because
that would require inspecting private output state after consumption.

## What R3 Means

R3 maps only to VR35A R1: after projecting to the exact published task, the
eligible structural total remains above 195. The exact count, difference
magnitude, private task distribution, row, path, identity, participant, and
selection remain unavailable.

This rules out mixed-task contamination as the sole explanation for the
aggregate surplus seen by the earlier task-blind lane. It does not reveal why
the exact-task inventory is still above the frozen expectation. Because R3 is
a diagnostic route rather than G1/G2, no real cohort was frozen and FW2/CIL1
remain ineligible.

VR36P is consumed. There is no retry, rerun, resume, repair, fallback,
substitution, cleanup, amendment, private-output inspection, or private
reinspection. The next safe work is artifact-only research and generated
predicate decomposition for the exact-task-surplus class; another private read
requires a separate frozen Tier C packet and decision.

Engineering capability added: one protocol-conforming real structural pass
localized the remaining blocker to an exact-task eligible-total surplus class
without exposing private counts, distributions, identities, or rows.

Scientific claim not established: no archive member, neural signal, target,
model, prediction, or score was accessed, so this establishes no neural effect,
decoding accuracy, language decoding, unseen-person generalization, or live
decoding result.
