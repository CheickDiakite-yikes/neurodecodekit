# BNCI-C3C5-1 Request Proof Closeout

Date: 2026-08-24

Status: **Proof-only closeout recorded locally; remote green pending**

Machine proof:

- `registries/bnci_2014_001_cross_participant_eeg_gain_request_proof.v0.json`

## Green Request Anchor

Exact request commit `3197390d45bfc8d19c9df2f3675166815f56f028`
passed:

- Base Python job `97503845918` in 6m37s;
- Optional Neuro Readers job `97503846151` in 8m35s; and
- CI run `32749812954`.

Both jobs completed successfully before this proof closeout was prepared.

## Immutable Artifact Set

The closeout binds nine exact BNCI research, preregistration, request, and test
artifacts totaling 87,813 bytes. Every artifact is bound by path, byte count,
SHA-256, and Git blob at the exact green commit. The canonical artifact-set
SHA-256 is:

```text
72e7ebf7de421b723a668ee2076c223c45c0ab5fca724457d66314951a1e3823
```

This closeout changes no source member, participant, session, run, trial,
channel, window, model, feature, selector, comparator, control, gate, route,
resource limit, publication boundary, or claim ceiling. G1 -> A -> Q -> P -> T
remains the only requested order.

## Verification Record

The 28 focused BNCI research/contract/request/proof checks pass. The valid
dependency-light full suite passes all 5,948 tests with 212 expected skips in
231.508 seconds, exactly six tests above the 5,942-test green-request baseline.
Repository-local Ruff, compilation, all 466 JSON registries, and diff hygiene
pass. Remote Base and Optional Neuro Readers jobs are both green for the bound
request; this closeout still requires its own remote-green proof.

A dependency-rich local full-suite process was also attempted and is reported
honestly as a non-baseline environment result: accumulated process RSS tripped
two old fixture caps, one multiprocessing test could not bind a sandboxed
socket, and two old mechanical checks remained false. The same optional suite
passed in clean remote CI. No runtime source was changed by this registration.

## Operation Record

Preparation performed only nine tracked-artifact reads, nine Git-proof reads,
one public GitHub run-list invocation, and one public CI-watch invocation. It
made zero protected or payload network requests, touched zero real, retained,
ignored, consumed, or other-project data paths, opened zero MAT/BDF, signal,
event, target, label, or artifact bytes, ran zero fits or inferences, froze zero
predictions, delivered zero targets, and performed zero scores, releases, or
scientific-claim upgrades.

## Next Gate

Commit, push, and require both CI jobs green for this exact closeout. Only
afterward may `BNCI-C3C5-1` be identified as the sole active Tier C packet. The
maintainer's next fresh unambiguous `continue`, `approve`, or `proceed` may then
authorize the unchanged staged packet by reference. No earlier message is
retroactive authority.

Engineering capability added: a remotely anchored, immutable independent
unseen-participant and EOG-conditional EEG experiment packet can now be audited
before any real operation.

Scientific claim not established: this closeout performs no real-data access,
training, inference, target delivery, or scoring and therefore establishes no
unseen-person result, EEG gain beyond eyes, or neural decoding result.
