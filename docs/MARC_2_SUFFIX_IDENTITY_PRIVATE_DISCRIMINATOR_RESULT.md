# MARC2-VR15P Suffix-Identity Private Discriminator Result

Date: 2026-08-21

Lane: `MARC2-VR15P`

Status: consumed at `MARC2VR15P-R15`; no retry, rerun, resume, repair,
fallback, substitution, cleanup, or reinspection

Machine result:
`registries/marc2_suffix_identity_private_discriminator_result.v0.json`

## Proof Before Execution

Activation attempt `64fa1144d9412b983796b3da2bdfd5904a1562a1` failed both
jobs in CI `32455530795` because two tests required a parent commit object that
was unavailable in GitHub Actions' shallow checkout. No private operation was
performed after that failed proof.

The portable correction `a9ebef4fb7cafdd281cfa1c4034a63ddcd08f0a1` passed
Base Python job `96694803139`, Optional Neuro Readers job `96694803152`, and
CI `32456531938`. The tracked tree was clean, except for one unrelated
untracked tracker-inspection file that the executor deliberately ignores, and
the exact one-shot arm was present.

## One-Shot Result

The registered command collected three fresh readiness samples, opened the
fixed 418,755-byte target-free structural source once, strict-parsed it once,
called VR15A once with one nested unchanged VR12A call, and returned
`MARC2VR15P-R15`. Runtime was 10.096426583011635 seconds, peak RSS was
29,016,064 bytes, combined generated output was 2,288 bytes, and network and
new payload bytes were zero.

Under the frozen route table, R15 is only the run-token width class: the source
does not satisfy the repair's one-or-two-ASCII-digit `run-<index>` assumption.
The result does not retain or reveal the token, filename, path, row, identity,
participant, candidate, selection, or cohort. No cohort manifest was created.

This is a concrete real-data structural finding. It falsifies the narrow width
assumption used by VR12A and gives the next generated repair a specific target:
support standards-compatible variable-width numeric run indices while keeping
all existing identity, companion, collision, count, rank, split, and storage
guards.

## Operation Boundary

The invocation wrote only its authorized readiness certificate, consumed
marker, and aggregate report. Archive members, neural payloads, signals,
events, channels, geometry, targets, labels, caches, features, splits, models,
training, inference, predictions, scoring, FW2/CIL1, network, providers,
streams, devices, hardware, releases, and other projects were untouched.

The ignored source and output were not listed, reopened, hashed, or inspected
after execution. This result is transcribed only from the command's returned
aggregate JSON and the already committed route table.

## What Comes Next

The next safe task is a separately frozen artifact-only and generated-only
variable-width run-index repair. Any new private read, cohort freeze, archive
or neural payload access, target/model/score work, FW2, or CIL1 remains a new
Tier C packet and decision.

Engineering capability added: the proof-separated one-shot localized the real
structural blocker to the frozen run-token width class without retaining
private identity details.

Scientific claim not established: no neural payload, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding performance, language decoding, live decoding, or thought-to-text
capability.
