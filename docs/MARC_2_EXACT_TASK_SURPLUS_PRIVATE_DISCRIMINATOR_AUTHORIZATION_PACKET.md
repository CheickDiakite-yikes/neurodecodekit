# MARC2-VR37P Exact-Task Surplus Private Discriminator Authorization Packet

Date: 2026-08-23

Lane: `MARC2-VR37P`

Status: **All-false Tier C request; no implementation or private access authorized**

Machine request:

- `registries/marc2_exact_task_surplus_private_discriminator_authorization_request.v0.json`

## Why This Is The Next Gate

Consumed VR36P R3 established only that exact-task projection leaves the
eligible total above 195. Remotely closed generated-only VR37A now separates
four aggregate mechanisms compatible with that result: one cell extended by
the next contiguous run, one cell extended by a noncontiguous run, pure
surplus across multiple cells, or mixed cell surplus and deficit with positive
net total.

VR37A closeout `4287a860ae11b47a9ccb50090ae62e6e4be2b59a` passed Base
Python job `97232723710`, Optional Neuro Readers job `97232723664`, and CI
`32655208775`. This makes a separately authorized route-only private
discriminator technically eligible. It does not authorize that discriminator.

## Requested Two-Stage Sequence

### Stage 1: generated/mock fixed-path wrapper

Only after a fresh packet-bound decision is committed, pushed, and remotely
green, implement an independent standard-library wrapper with fixed `plan`,
`qualify`, `inspect`, and `execute` commands. Generated qualification must use
injected temporary paths and readiness providers only. It must cover the six
exact VR37A cases in ready and not-ready states, two row orders, and two exact
replays: 48 paths, 48 VR33A calls, 144 provider calls, 96 sleeper calls, 24
VR37A calls with 24 nested unchanged VR35A calls, at least 120 direct refusals,
and zero retained generated output.

Stage 1 may not stat, resolve, hash, list, open, or parse `.codex_work`, a
private source, consumed output, archive member, or neural payload. Its exact
implementation and result must be committed, pushed, and remotely green, then
receive a separately green proof-only closeout before Stage 2.

### Stage 2: one aggregate private topology discrimination

Only after every proof barrier, request one fixed-path invocation that:

1. collects exactly three readiness samples through unchanged VR33A, with
   exactly two fixed five-second sleeps;
2. creates one new output root and consumed marker without overwrite;
3. opens and strict-parses only the registered 418,755-byte target-free
   structural JSON source once;
4. calls unchanged VR37A once, including exactly one nested VR35A call;
5. writes one aggregate public report containing only a frozen route,
   operation counts, resources, warnings, and claim boundaries.

No cohort, identity-bearing derivative, archive member, neural payload, target,
model, prediction, or score is written or opened. Not-ready consumes the
invocation and opens zero source bytes. Every outcome consumes the invocation.
Retry, rerun, resume, repair, fallback, substitution, overwrite, and private
reinspection are excluded.

## Frozen Aggregate Routes

| Route | Maximum meaning |
|---|---|
| `MARC2VR37P-R1` | Public 38-cell exact-map control; inconsistent with the prior surplus route but no detail is exposed. |
| `MARC2VR37P-R2` | Exactly one cell has the next contiguous extra run. |
| `MARC2VR37P-R3` | Exactly one cell has one noncontiguous extra run. |
| `MARC2VR37P-R4` | Multiple cells have surplus and no cell has a deficit. |
| `MARC2VR37P-R5` | At least one cell has surplus and at least one has deficit, with positive net total. |
| `MARC2VR37P-R6` | Structural, task, taxonomy, or topology validation refused. |
| `MARC2VR37P-R7` | Readiness, fixed-path, output, deterministic-replay, or resource precondition refused. |

No route may expose the exact total, difference, number of affected cells,
cell identity, task distribution, member name, path, participant, subject,
session, run, reservation, private hash, row, value, or exception text. A
successful route identifies only an aggregate mechanism class and authorizes
no repair or cohort freeze.

## Fixed Source And Limits

The future source identity is copied only from committed records:

```text
.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
bytes:  418755
sha256: 2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
```

Future readiness and output paths are new VR37P-only locations. Every prior
consumed private lane remains forbidden. The private invocation is limited to
one CPU thread, one worker, one numerical job, 120 seconds, less than 256 MiB
peak RSS, at least 2 GiB free disk, 1 MiB combined incremental output, zero
network bytes, zero new payload bytes, and zero archive, signal, target, or
model bytes.

## Current Authorization State

Every authority flag is false. Packet preparation performed zero readiness,
private-path, source, output-root, consumed-state, archive, neural, target,
model, prediction, score, network, provider, device, FW2/CIL1, release, or
claim operation.

The request and a non-scope-changing proof closeout must each be committed,
pushed, and both remotely green. Only then may VR37P be identified as the sole
active Tier C packet. A fresh unambiguous maintainer message after that
identification may authorize the unchanged packet by reference. The current
or any earlier `continue` is not retroactive authority.

Engineering capability requested: one proof-gated target-free structural pass
can identify the aggregate topology class behind the exact-task surplus
without exposing its location or magnitude.

Scientific claim not established: this request performs no real/private read,
neural access, model run, prediction, or score and establishes no neural
effect, decoding accuracy, language decoding, unseen-person generalization, or
live decoding.
