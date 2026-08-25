# BNCI-C3C5-1 Stage A Redirect Recovery Implementation Activation

Date: 2026-08-24

Status: **activation remotely green after a shallow-checkout proof-test
correction; sole live recovery passed and is consumed**

Machine activation:

- `registries/bnci_2014_001_stage_a_redirect_recovery_implementation_activation.v0.json`

## Green Implementation Bound

Exact implementation commit `09a19d1c1c498bdd6e0ece2fbecb6d15917bdefa`
passed CI `32806186972`, Base Python job `97676637882`, and Optional
Neuro Readers job `97676637728`.

The activation binds the exact module, sidecar CLI, and implementation test
blobs from that commit. At execution, the recovery refuses unless those files
still match the green commit, this activation matches `HEAD`, the implementation
is an ancestor of `HEAD`, and the complete tracked tree is clean. The unrelated
untracked tracker-inspection artifact is neither read nor bound.

The first activation commit `0dd507a` failed CI `32806829323` because GitHub's
depth-one checkout did not contain the prior implementation commit required by
two proof tests. Production code and implementation artifacts did not fail.
The test-only correction verifies checked-out Git blobs and explicit fail-
closed behavior when ancestry is unavailable. Corrected activation
`492a36a818bb00ca6bb86de6592c6cd0d5134f90` passed Base job `97680849177`,
Optional Neuro Readers job `97680849465`, and CI `32807676008`.

## Delayed Effect

This record and its correction performed no ignored-path read, manifest
request, payload request, MAT open, model operation, target delivery, score,
release, or claim change. A later local execute command was rejected before
process creation by the obsolete repository stop instruction; it made zero
request and did not consume the replacement recovery.

Control-plane commit `21cedd5` passed both required jobs in CI `32811586786`
before the one replacement recovery. The recovery then completed exactly once.
The immediate gate is the aggregate result's commit, push, and remote-green
proof before Stage Q.

Engineering authority added after green activation: the exact generated-qualified
implementation may perform one bounded signed-object Stage A recovery.

Scientific claim not established: activation proves code identity and ordering,
not EEG information, decoding performance, or unseen-person generalization.
