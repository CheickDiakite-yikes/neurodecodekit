# BNCI-C3C5-1 Stage G1 Recovery Request Proof Closeout

Date: 2026-08-24

Status: **Proof-only closeout recorded locally; remote green pending**

Machine proof:

- `registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_recovery_request_proof.v0.json`

## Green Request Anchor

The recovery request first appeared in implementation/failure commit
`d65294967ec80c08844af55354da72b11f1dacc1`. CI run `32758324335`
passed Base Python and every focused BNCI check, but the complete optional
suite exposed a historical test-harness defect: two causal-replay success
tests compared their 256 MiB fixture cap with the lifetime RSS of the entire
6,026-test process.

Repair commit `b1f68e50823792ccedb5ef8962c584c1bb573f3a` changed only
those two historical test files. It injects a bounded synthetic RSS value in
their success paths and adds an explicit 257 MiB versus 256 MiB refusal
assertion. Production RSS measurement and enforcement are unchanged. The
unchanged recovery request then passed:

- Base Python job `97534565977` in 6m42s;
- Optional Neuro Readers job `97534565813` in 8m43s; and
- CI run `32759468410`.

## Immutable Artifact Set

This closeout binds seven exact implementation, failure, recovery-request, and
request-test artifacts totaling 22,514 bytes. Every artifact is bound by path,
byte count, SHA-256, and Git blob at the exact green repair commit. The
canonical artifact-set SHA-256 is recorded in the machine proof.

```text
931089ec08bb154f95181f918b3f13f448987d91473207c59d49704ef476d447
```

The closeout changes no generated case, fixture, participant, session, run,
trial, channel, window, feature, model, selector, control, gate, route,
resource cap, stage order, publication boundary, or claim ceiling. The
replacement pass remains generated/mock only and must stop before Stage A.

## Verification Record

At the green request anchor, Base Python passed all 5,970 tests with 218
expected skips in 381.002 seconds. Optional Neuro Readers passed all 6,026
tests with 44 expected skips in 468.652 seconds; its focused RW2 and UG1
suites also passed. The five repaired causal-replay tests pass locally in
0.365 seconds. Ruff and diff hygiene pass.

The recovery proof adds six self-verifying tests. The clean dependency-free
closeout suite passes all 5,976 tests with 216 expected skips in 209.174
seconds, exactly six tests above the 5,970-test green-request baseline. It does
not rerun the consumed G1 attempt or the requested replacement pass. Pinned
Ruff, compilation, all 471 JSON registries, and diff hygiene pass.

## Operation Record

Preparation performed only tracked-artifact and Git-proof reads, public GitHub
CI reads, and ordinary local tests. It made zero protected or payload network
requests; touched zero real, retained, ignored, consumed, or other-project
data paths; opened zero MAT/BDF, signal, event, target, or label bytes; ran
zero replacement qualifications, fits, or inferences; froze zero predictions;
delivered zero targets; and performed zero scores, releases, or scientific-
claim upgrades.

## Next Gate

Commit, push, and require both CI jobs green for this exact closeout. Only
afterward may `BNCI-C3C5-1-G1-recovery` be identified as the sole active Tier C
packet. The maintainer's next fresh unambiguous `continue`, `approve`, or
`proceed` may then authorize the unchanged one-pass generated recovery by
reference. No earlier message is retroactive authority.

Engineering capability added: the failed launcher, repaired implementation,
and bounded one-pass recovery request are now tied to one auditable green
artifact chain.

Scientific claim not established: this closeout performs no replacement run
and no real-data access, training, inference, target delivery, or scoring, so
it establishes no decoding, unseen-person, or EEG-beyond-EOG result.
