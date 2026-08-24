# EEGMMIDB-UG1 Stage S-A2 Proof-Only Closeout

Date: 2026-08-24

Status: **Proof recorded; no operation repeated; remote green pending**

Machine proof:
`registries/eegmmidb_unseen_participant_source_acquisition_stage_sa2_proof_closeout.v0.json`

## Green Result Evidence

Exact consumed-failure result
`ba8645e66d98020daa0139d561e92e33551b9255` passed Base Python job
`97474420839`, Optional Neuro Readers job `97474421286`, and CI
`32740773041` before this closeout.

That result establishes only that the sole Stage S-A2 invocation failed closed
during verified TLS certificate-chain validation before any HTTP response or
EDF request. It retained a 212-byte consumed marker and no bundle. It is not a
successful acquisition or a neural result.

## Immutable Binding

This closeout binds six exact artifacts from the green result revision by Git
revision, byte count, SHA-256, and Git blob:

1. the Stage S-A2 human result;
2. the Stage S-A2 machine result;
3. the Stage S-A2 result test;
4. the Stage S-A1 proof activation registry;
5. the activated Stage S-A1 proof registry; and
6. the unchanged qualified acquisition module.

They total 108,663 bytes under canonical artifact-set SHA-256
`87f551e1a19db3dbc3fbd2f7976aaac45da87e971f232d502f53f7863c9dde6f`.

## Operations

The closeout performs six tracked-artifact reads and six Git-proof reads only.
It does not inspect the ignored consumed marker or any output path. It makes no
network request, opens no real or ignored payload, reads no EDF byte or
semantic content, and performs no target, model, training, prediction, score,
release, cleanup, deletion, repair, or claim operation.

## Verification

Twenty-three focused activation/result/closeout checks pass. The complete
dependency-light, one-thread suite passes 5,920 tests with 212 expected skips
in 229.919 seconds, exactly seven passing tests above the green result
milestone. Changed-file Ruff, compilation, all 462 registry JSON parses, and
Git diff hygiene pass. The result's separate disclosure of 1,205 pre-existing
findings from the latest unpinned repository-wide Ruff scan remains unchanged.

## Terminal Boundary

Stage S-A2 remains consumed and permanently parked. There is no retry, rerun,
repair, resume, certificate bypass, alternate client, fallback, substitution,
marker deletion, or payload completion gate. The dependent UG1 source-LOSO
stage remains unexecutable because the registered six-file bundle does not
exist.

After this exact closeout is committed, pushed, and remotely green, the safe
next step is artifact-only design of a genuinely independent scientific lane.
Any new real-data, target, model, or score action remains Tier C and requires a
new frozen packet and exact decision.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now has an immutable, remotely
verifiable closeout for a consumed acquisition failure without reopening its
ignored state or weakening its no-retry rule.

Scientific claim not established: the closeout performs no EEG access or
analysis and establishes no neural effect, decoding advantage, unseen-person
generalization, movement intention, motor-cortex origin, eye independence,
language or thought decoding, live latency, hardware result, or clinical
utility.
