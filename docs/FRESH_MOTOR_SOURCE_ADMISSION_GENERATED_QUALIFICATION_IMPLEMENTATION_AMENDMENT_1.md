# Fresh Motor Source Admission Generated Qualification Implementation Amendment 1

Date: 2026-08-30

Protocol: `FMSR1-R1-G-v0`

Corrected implementation: `FMSR1-R1-G-I1`

Status: **local corrective successor complete; activation absent; official
qualification not run; fresh exact commit and both remote CI jobs required**

Machine record:

- `registries/fresh_motor_source_admission_generated_implementation.v1.json`

## Why The Green Predecessor Was Rejected

Implementation `FMSR1-R1-G-I0` reached GitHub `main` at exact commit
`c3f536d3e527117d9347ed0d6c4fdbc39d7d44ac`. CI `33345237136` passed both
required jobs:

```text
Base Python:             99347978123
Optional Neuro Readers: 99347978190
```

That green status proved the committed tests passed. It did not prove that the
one-shot filesystem design was complete. A new independent post-green review
rejected activation for two exact reasons:

1. `consumed.json` and the attempt directory were fsynced, but the repository
   root and `.codex_work` directory entries were not both explicitly fsynced
   after creation of their children; and
2. the implementation record said every failed attempt remained consumed even
   though contract, activation, and thread-environment checks intentionally run
   before the official attempt is armed.

No activation was created and the official generated qualification was not
run. The rejected predecessor therefore consumed no official attempt and
performed no network, source, payload, model, score, release, or claim work.

## Corrected Durability Chain

The `I1` successor opens and verifies the repository root, `.codex_work`, and
official attempt directory with `O_DIRECTORY | O_NOFOLLOW`. It binds each open
descriptor to the observed device and inode, creates child directories relative
to already opened parent descriptors, and rechecks the official path identity
before replay.

The one-shot arming sequence is now:

```text
pre-arm contract + activation + thread checks
-> fsync repository root after .codex_work admission
-> create official attempt directory
-> fsync .codex_work
-> create consumed.json with O_CREAT | O_EXCL | O_NOFOLLOW
-> fsync consumed.json
-> fsync official attempt directory
-> reverify attempt path identity
-> generated replay begins
```

The official marker contributes one file fsync and three directory fsyncs.
The two generated acceptance replays each contribute one marker file fsync and
one marker-directory fsync, so the aggregate public report must contain exactly
three marker creations, three file fsyncs, and five directory fsyncs.

## Exact Consumption Semantics

A refusal during contract verification, implementation activation loading, or
thread-environment validation is **pre-arm**. It creates neither the official
attempt directory nor `consumed.json`, so it does not spend the sole attempt.

Creation of `.codex_work/fmsr1-r1-g-v0-official` first establishes a pending
reservation. The arming event is the successful `fsync` of its parent work
directory, which makes that directory entry durable. Once armed, success,
refusal, exception, interruption, crash, or missing report leaves the attempt
consumed. The directory and marker must never be deleted, repaired, resumed, or
reused. Any second invocation refuses before a replay.

An `fsync` failure before that durable arming boundary cannot honestly claim
crash persistence. The runner therefore preserves the pending reservation and
refuses a second invocation while it remains present, but reports the failure
as pre-arm reservation-durability failure rather than an armed consumed
attempt. A repository-root `fsync` failure happens before the attempt
reservation exists and remains retryable after the durability fault is fixed.

## New Adversarial Coverage

The additive durability suite verifies:

- repository-root, work-root, and attempt-root fsync order and exact count;
- repository-root fsync failure remaining pre-arm and retryable;
- work-root fsync failure retaining an unmarked, fail-closed pending reservation;
- repository-root and work-root symlink or non-directory refusal;
- expected attempt device/inode binding before marker creation;
- pre-arm contract, activation, and thread-environment refusal without official
  root creation;
- post-arm injected failure retaining the official root and marker; and
- a second invocation refusing before another replay.

Together with the original focused suite, 37 focused tests now pass locally.
The 82 registered mutation routes remain unchanged and all pass in reversible
component tests. These checks do not invoke the official qualification.
Final independent re-review found no P0/P1 issue and accepted this milestone
for commit and fresh CI only; its sole P2 stale-count note was corrected in the
build journal.

## Scientific Evidence Clarification

Independent scientific-governance review also found that exact-green
`FMSR1-v1` grouped posterior EEG inside a joint nuisance list and omitted the
later structure-preserving shifted-EEG temporal comparator. The parent bytes
remain immutable. Additive strategy-only clarification
`FMSR1-v1-EVIDENCE-MAP-C0` now requires future source-specific contracts to
keep posterior EEG spatial, shifted EEG temporal, joint EOG/EMG/metadata
physiological nuisance-only, and nuisance plus deranged central EEG the
physiological counterfactual. This clarification creates no operational or
scientific authority.

## Ordered Next Gate

1. complete local focused, full-suite, Ruff, compile, JSON, CLI, and diff checks;
2. commit and push this exact `I1` successor;
3. require both GitHub `main` jobs to pass;
4. add a separate activation binding the exact `I1` commit, CI run, job IDs,
   and four runtime artifact hashes;
5. commit, push, and remotely green that activation without running the
   qualification;
6. invoke `qualify-generated` exactly once under the five one-thread
   environment variables;
7. commit its aggregate result and then a proof-only closeout without rerun; and
8. stop before `R1-W` or any network/source contact.

Engineering capability added: the generated admission runner now has a fully
fsynced, no-follow, inode-bound one-shot ancestry and an exact pre-arm,
pending-reservation, and durably armed consumption contract.

Scientific claim not established: no real source or human neural data was
accessed, so no source authenticity, neural advantage, motor-cortex
attribution, intention decoding, unseen-person generalization, thought or
language decoding, or live operation was established.
