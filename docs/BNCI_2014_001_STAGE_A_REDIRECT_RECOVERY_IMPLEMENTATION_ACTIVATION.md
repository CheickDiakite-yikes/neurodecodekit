# BNCI-C3C5-1 Stage A Redirect Recovery Implementation Activation

Date: 2026-08-24

Status: **activation recorded; delayed until this exact activation is committed,
pushed, and both required CI jobs are green**

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

## Delayed Effect

This record performs no ignored-path read, manifest request, payload request,
MAT open, model operation, target delivery, score, release, or claim change.
Only after this exact activation is committed, pushed, and remotely green may
the one replacement recovery invocation begin.

Engineering authority added after green activation: the exact generated-qualified
implementation may perform one bounded signed-object Stage A recovery.

Scientific claim not established: activation proves code identity and ordering,
not EEG information, decoding performance, or unseen-person generalization.
