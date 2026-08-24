# EEGMMIDB-UG1 Stage S-A1 Green-Proof Activation

Date: 2026-08-24

Lane: `EEGMMIDB-UG1-SA1-ACTIVATION`

Status: **Activation recorded; exact commit must be remotely green before any
Stage S-A2 operation**

Machine activation:

- `registries/eegmmidb_unseen_participant_source_acquisition_stage_sa1_proof_activation.v0.json`

## Green Input

Proof-only closeout `b3902cf50bef478055255570d1b78813207fb8d1`
passed Base Python job `97456050452`, Optional Neuro Readers job
`97456050604`, and CI `32735141922` before this transition was prepared.

The three exact preactivation proof artifacts are bound from that Git revision
by byte size, SHA-256, and Git blob. The qualified implementation and consumed
result are not modified, repeated, reconstructed, or reinterpreted.

## Activation

The proof registry's previously null `green_proof_closeout` field now copies
the exact closeout commit, CI run, and both job IDs. Its
`both_required_stages_remotely_green` field becomes true. These are the exact
fields the frozen Stage S-A2 executor validates before it can construct a live
network opener.

The activation registry freezes the resulting proof-registry SHA-256 and the
complete future `SA1ProofEvidence` value set. This transition is inert until
its own commit is pushed and both required CI jobs pass.

## Operation Boundary

This transition performs three tracked-artifact reads and three Git-proof
reads. It performs zero qualification, network request, checksum-manifest
request, real path operation, payload byte, EDF read, retained-source or
fresh-final operation, target read, model fit, inference, training, prediction,
score, release, or scientific-claim operation.

Local verification passed 37 focused checks, including direct target-free
acceptance by the unchanged frozen proof reader. The complete dependency-light
suite passed 5,904 tests with 212 expected optional-dependency skips, exactly
seven above the 5,897-test proof-closeout milestone. Ruff, compilation, every
JSON registry parse, and `git diff --check` passed.

## Next Gate

Commit, push, and remotely green this exact activation. Only after that may the
already-authorized one-shot Stage S-A2 acquisition be considered with the
frozen proof-registry hash and exact evidence values. Before then, no live
opener may be constructed.

The later acquisition ceiling remains one checksum-manifest request followed
by six direct opaque source EDF requests totaling exactly 15,498,816 successful
payload bytes. It may not parse EDF content or touch the 54 retained source
files, 30 fresh-final files, targets, models, scores, devices, releases, or
claims.

Engineering capability added: the exact remotely green Stage S-A1 proof is
copied into the fail-closed evidence fields required by the frozen live gate.

Scientific claim not established: this activation performs no real request or
EEG operation and establishes no neural effect, decoding advantage, movement
intention, motor-cortex origin, eye independence, language decoding, live
performance, or unseen-person generalization.
