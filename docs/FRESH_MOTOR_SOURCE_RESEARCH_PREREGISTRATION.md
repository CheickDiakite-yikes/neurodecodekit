# Fresh Motor Source Research Preregistration

Date: 2026-08-29

Protocol: `FMSR1-v0`

Status: **all authorities false; artifact-only registration; no source selected**

Machine contract:
[`fresh_motor_source_research_contract.v0.json`](../registries/fresh_motor_source_research_contract.v0.json)

## Purpose

The next scientific question is intentionally narrow:

> In completely unseen people, does central EEG add motor-task information
> beyond recorded eye activity, task-relevant muscle activity, posterior EEG,
> cue and timing structure, and a matched deranged-EEG control?

This registration freezes how a fresh public source will be researched and
routed before any source-specific network request. It is not a candidate
announcement, acquisition packet, transport canary, or neural experiment.

Generated `NPA1-G` closed the transport-validator engineering question at exact
commit `2e164fffb00e5db79a6c6d810eabbcc2d447c5a1`. Its proof-only closeout at
`2ec3d4b2b7b8c51f246e948ce9cbc9d667cecfb5` passed Base Python
`99188620896`, Optional Neuro Readers `99188621003`, and CI `33285776358` on
GitHub `main`. No network or neural payload was used in that proof.

## One Scientific Lane

`FMSR1-v0` is a motor-task source-admission protocol. Speech, imagined speech,
language, and prompted-communication datasets cannot satisfy or rescue this
lane. They remain separately governed research programs.

The source must be fresh to NeuroDecodeKit: no selected participant, run, or
evaluation surface may overlap a previously consumed source. The following
surfaces are excluded from promotion here:

- BNCI 2014-001 / NEMAR `nm000139`;
- Dreyer Dataset A / NEMAR `nm000250`;
- Ofner 2017 / NEMAR `nm000173`;
- IACKD / OpenNeuro `ds006840`;
- PhysioNet EEGMMIDB; and
- SpanishBCBL S7/S20/S21/S24/S25.

Their aggregate lessons may inform the design. Their payloads, targets,
predictions, scores, and consumed markers may not be reopened or reused.

## Noncompensatory Admission Gates

A source is eligible for the flagship confirmation only if every requirement
below is independently supported by an official source or primary publication.
A weighted score, model result, convenience, or small download cannot rescue a
failed gate.

1. At least ten complete participants can be evaluated with participant-held-
   out, zero-calibration outer folds.
2. Raw synchronized EEG, EOG, and task-relevant EMG are present for every
   selected participant. Bilateral task-relevant EMG is preferred and any
   asymmetry must be explicit. Kinematics may strengthen the control set but
   cannot replace EMG for a claim beyond muscle activity.
3. EEG channel names and sensor locations are available, including enough
   posterior channels for a spatial-specificity comparator.
4. Reference, sampling, event grammar, cue timing, pre-cue interval, decision
   interval, and target meaning can be recovered without outcome-driven rules.
5. The task supports a motor-information question with at least two identified
   actions or intentions; cue identity cannot be the target itself.
6. An immutable official release identity and a reusable dataset license are
   available. Article terms are not imputed to the payload.
7. A target-free complete-cohort manifest can bind exact selected members,
   sizes, and content hashes before semantic payload access.
8. The deterministic complete cohort fits within 16 GiB of selected source
   payload and 20 GiB total incremental disk, including temporary files and
   derivatives. Participants may not be dropped to meet the cap.
9. A documented public format and dependency-light or established reader path
   exist.
10. The source permits cue, pre-cue, timing, posterior, EOG, EMG, no-signal,
    and matched derangement controls under the same participant-first score.

## Deterministic Routing

Every researched source receives exactly one route:

| Route | Meaning | Promotion |
|---|---|---|
| `FULL_CONFIRMATION` | All ten hard gates pass | Eligible for one later source-specific metadata packet |
| `PARTIAL_CONTROL` | At least ten participants and EEG/EOG exist, but task-relevant EMG or another attribution gate fails | Document only; cannot answer the flagship question |
| `MECHANISTIC_BRIDGE` | Rich synchronized controls exist, but fewer than ten complete participants | Mechanism development only; no confirmatory inference |
| `ENGINEERING_ONLY` | Useful format or transport surface without the scientific controls | Reader/transport work only |
| `PARK` | License, identity, completeness, geometry, task, or storage cannot be verified | Stop |

If no source reaches `FULL_CONFIRMATION`, the correct outcome is
`NO_QUALIFYING_SOURCE`. The criteria remain unchanged and the next decision is
whether to revise the measurement strategy or collect a prospective cohort.

## Comparison After Eligibility

Only full-gate passers may enter deterministic comparison. The order is:

1. larger complete participant count;
2. stronger bilateral EMG plus kinematic coverage;
3. greater laboratory, device, and participant independence from prior work;
4. more trials per participant under a fixed identifiable task;
5. more exact storage headroom; and
6. lexicographically smaller immutable source identifier as the final tie-break.

No model performance, target statistic, participant outcome, or hidden payload
property may influence source selection.

## Future Research Surface

A later, separately named packet may authorize bounded public metadata research
against official dataset pages, immutable manifests, licenses, and primary
papers. That packet must freeze its domains, request methods, request count,
response-byte cap, redirect policy, retained fields, runtime, and one-shot
failure behavior before any request.

This registration itself authorizes none of that. It performs zero network,
payload, header, signal, event, target, model, training, inference, prediction,
score, provider, stream, device, hardware, release, deletion, or claim
operation. It creates no Tier C lane.

## Stop Rules

Park the candidate immediately when any hard gate fails, when the source can be
made feasible only by dropping inconvenient participants, when payload access
would be required to answer a metadata-only question, or when the source
overlaps a consumed evaluation. Unknown is not pass.

Engineering capability added: NeuroDecodeKit now has a falsifiable source-admission contract that separates a scientifically adequate unseen-person motor cohort from partial-control and engineering-only datasets before storage is spent.

Scientific claim not established: no source was selected and no neural measurement was accessed or analyzed, so no neural advantage, unseen-person generalization, movement-intention decoding, language decoding, live operation, hardware result, or clinical value was established.
