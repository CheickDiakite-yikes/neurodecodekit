# Research Autonomy Charter

Date: 2026-07-15

Status: **Draft for maintainer approval; this document grants no authorization**

## Purpose

NeuroDecodeKit uses gates for two different reasons:

1. **Machine safety:** prevent surprise downloads, storage growth, concurrent
   heavy jobs, destructive cleanup, long-running processes, and operations on
   unrelated projects.
2. **Scientific validity:** prevent target leakage, repeated use of consumed
   evaluations, post-outcome tuning, hidden protocol changes, and inflated
   claims.

The second class is often irreversible. A file can be restored; a held-out
target cannot become unseen again. This charter keeps those irreversible stops
while allowing routine research engineering to move continuously.

## Default Operating Envelope

Unless a narrower registered contract applies, autonomous work would use:

- one CPU thread, one worker, and one numerical job at a time;
- no persistent background process after verification;
- at most 1 GiB peak RSS for ordinary code or analysis;
- at most 32 MiB of generated artifacts per loop;
- no new real-data download under this standing charter;
- no deletion outside this repository and no destructive Git operation;
- no secrets, real participant payloads, caches, or generated inspection debris
  in commits;
- coherent commits and pushes after local tests, with remote CI checked before
  a dependent milestone;
- explicit runtime, RSS, storage, access, training, inference, and claim
  reporting whenever a numerical stage runs.

A loop-specific contract may tighten these limits. It cannot silently loosen
them.

## Tier A - Autonomous Routine Work

After approval of this charter, the co-researcher may proceed without another
permission message for:

- repository inspection, primary-source research, hypothesis development, and
  documentation;
- code, tests, schemas, validators, CLI surfaces, and synthetic fixtures;
- target-free synthetic experiments inside the default envelope;
- static analysis of Git-tracked aggregate artifacts that contain no plaintext
  targets, private predictions, or per-item target-conditioned records;
- dry-run manifests and metadata-only selection that download no payload;
- linting, complete test suites, bounded smoke tests, commits, pushes, and CI
  inspection;
- preregistration, authorization-packet preparation, and measured closeout
  records that do not themselves execute a protected experiment.

Tier A cannot create a scientific performance claim.

## Tier B - Autonomous Bounded Development Experiments

After approval of this charter, a Tier B experiment may proceed without a new
permission message only when all of these conditions are machine-recorded
before execution:

- the input is synthetic, public aggregate data, or an already-authorized
  development-only partition;
- no held-out, final-only, source-test, cross-person final, or consumed
  validation target is read;
- target use, if any, is confined to an explicitly development-only training
  partition and is disclosed;
- split identities, hypotheses, comparators, controls, metrics, thresholds,
  seeds, stop rules, and claim ceiling are frozen first;
- the default resource envelope is sufficient;
- the result can be discarded without consuming a future scientific test;
- failed results are retained and reported rather than silently rerun.

Tier B may support engineering decisions and hypothesis refinement. It cannot
establish unseen-person generalization, final decoding performance,
brain-specific origin, real-time behavior, portable hardware performance, or a
clinical claim.

## Tier C - Explicit One-Time Permission Still Required

The co-researcher must stop for an exact maintainer decision before:

- first access to a new real participant signal or protected target payload;
- opening a held-out, final-only, source-test, or unseen-person evaluation;
- scoring a prediction set against targets that were previously sealed;
- rerunning, retuning, or changing a protocol after a validation result is
  known;
- reusing a consumed evaluation for model, threshold, seed, architecture, or
  claim selection;
- downloading real data or exceeding the default RSS, runtime, or output cap;
- using session 2, S7, S20, S25, or another frozen cohort beyond its current
  recorded boundary;
- connecting hardware, recording a participant, opening a live stream, or
  starting RW3 or another independently gated track;
- deleting data, rewriting history, merging, tagging, releasing, publishing,
  uploading payloads, or making clinical-facing claims.

Tier C is one stop immediately before the irreversible action. The
co-researcher should autonomously prepare the research, contract, tests,
implementation, and decision packet first whenever those preparations stay in
Tier A or B.

## Stop Conditions

Autonomous work stops when:

- free disk space would fall below 20 GiB;
- measured RSS, runtime, or generated output exceeds its registered cap;
- an input identity or hash differs from the frozen record;
- a target, split, cache, or participant boundary is ambiguous;
- the worktree contains overlapping user changes that cannot be preserved;
- a result would tempt a protocol change after outcome inspection;
- remote CI fails for a milestone required by the next stage.

Stopping means preserving evidence and reporting the measured reason. It does
not authorize cleanup, reruns, or wider access.

## Standing Approval Sentence

The charter becomes active only if the maintainer sends this exact sentence
and it is recorded in a separate committed decision:

> Authorize the NeuroDecodeKit Research Autonomy Charter dated 2026-07-15. I
> authorize Tier A routine work and Tier B bounded development experiments
> exactly as written, including autonomous commits, pushes, and CI checks. Tier
> C irreversible evidence, real-data acquisition, hardware, destructive,
> release, and scientific-claim actions still require my separate exact
> permission.

Approval would apply prospectively. It would not retroactively reopen any
consumed loop, loosen an existing contract, authorize Loop 48 Stage B, authorize
RW3, or open S25.
