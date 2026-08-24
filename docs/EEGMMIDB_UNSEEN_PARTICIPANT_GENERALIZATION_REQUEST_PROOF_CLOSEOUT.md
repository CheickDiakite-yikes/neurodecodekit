# EEGMMIDB-UG1 Request Proof Closeout

Date: 2026-08-24

Status: **Proof-only closeout recorded locally; remote green pending**

Machine proof:

- `registries/eegmmidb_unseen_participant_generalization_request_proof.v0.json`

## Green Request Anchor

Exact request commit `c642d90b646ff32c6d83e648f7d7779810605e11`
passed:

- Base Python job `97322606634`;
- Optional Neuro Readers job `97322606501`; and
- CI run `32690289547`.

Both jobs completed successfully before this proof closeout was prepared.

## Immutable Artifact Set

The closeout binds nine exact UG1 research, preregistration, request, and test
artifacts totaling 56,516 bytes. Every artifact is bound by path, byte count,
SHA-256, and Git blob at the exact green commit. The canonical artifact-set
SHA-256 is:

```text
0aa60317de6ca5a3afe568eeccaef07ff1134275e1ebd8ccca38d8c76c0d5b43
```

This closeout changes no participant, run, target, model, gate, control,
resource limit, route, or claim ceiling. The one-thread, 256 MiB new-payload,
512 MiB incremental-disk, 1 GiB RSS, 300-fit, 640-prediction, one-delivery,
one-score, and zero-rerun envelope remains exact.

## Operation Record

Preparation performed only tracked-artifact and Git-proof reads. It made zero
network metadata or payload requests, touched zero real/retained/ignored data
paths, opened zero EDF or signal bytes, read zero annotation/target/label
bytes, ran zero fits or inferences, froze zero predictions, delivered zero
targets, and performed zero scores or scientific-claim upgrades.

The full pre-change dependency-light suite passed 5,699 tests with 204
expected skips. The 20 focused UG1 tests, pinned Ruff, registry JSON parsing,
compilation, and diff hygiene also passed. The repository-wide Ruff formatting
check has a pre-existing 605-file backlog; the three new tests are formatted
and the authoritative Ruff lint check is green.

## Next Gate

Commit, push, and require both CI jobs green for this exact closeout. Only
afterward may `EEGMMIDB-UG1` be identified as the sole active Tier C packet.
The maintainer's next fresh unambiguous `continue`, `approve`, or `proceed` may
then authorize the unchanged staged packet by reference. No earlier message is
retroactive authority.

Engineering capability added: a remotely anchored, immutable one-shot
unseen-participant EEG experiment packet can now be audited before any real
operation.

Scientific claim not established: this closeout performs no real-data access,
training, inference, target delivery, or scoring and therefore establishes no
unseen-person generalization or neural decoding result.
