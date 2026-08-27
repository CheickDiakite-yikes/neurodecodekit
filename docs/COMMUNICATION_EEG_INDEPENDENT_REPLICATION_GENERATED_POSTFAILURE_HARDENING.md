# COMM-R0-G Post-Failure Hardening

Date: 2026-08-27

Status: **Generated engineering correction only; consumed run remains closed**

Machine record:
`registries/communication_eeg_independent_replication_generated_postfailure_hardening.v0.json`

## Why This Exists

The sole official `COMM-R0-G` qualification is consumed. It failed closed when
the final temporary-tree audit encountered the symlink intentionally created
by the preceding escape-refusal test. Failure record `9876cf9` and proof
binding `efef655` are remotely green.

This correction does not rerun, repair, reinterpret, or accept that failed
qualification. It makes two future-facing safety changes:

1. The registered failure record is checked before registration, activation,
   replay, model, prediction, target, or score work. The original entry point
   now refuses with `R0G-CONSUMED`.
2. The lower-level generated adversarial helper unlinks its own expected
   symlink without following it, verifies that its target is a real empty
   directory, removes that directory, and then permits a final tree-byte audit.

The historical implementation record retains the exact hashes that ran. This
additive hardening record binds both historical hashes and corrected hashes so
the evidence trail is not rewritten.

## Verification Boundary

Focused tests may exercise the refusal helper over generated fixtures and
confirm that the temporary tree contains no symlink afterward. They may also
confirm the consumed guard directly. The full two-replay development path and
the official qualification must not execute.

No real or private path, EEG, target, model, training, prediction, delivery,
score, network, provider, stream, device, hardware, release, or scientific
operation is authorized or performed here. `DREYER-C5R-1-HL` remains the sole
active all-false Tier C gate.

## Claim Boundary

Engineering capability added: the consumed generated entry point now refuses
before work, and its lower-level adversarial fixture cleanup is regression
tested for a future separately registered lane.

Scientific claim not established: this source correction accesses no real EEG
and establishes no decoding, unseen-person, EEG-beyond-controls, live,
hardware, or clinical result.
