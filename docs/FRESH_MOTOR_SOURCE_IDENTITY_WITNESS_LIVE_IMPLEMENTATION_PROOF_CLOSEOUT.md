# Fresh Motor Source Identity Witness Live Implementation Proof Closeout

Date: 2026-08-31

Implementation: `FMSR1-R1-W-I1`

Qualification: `FMSR1-R1-W-I1-Q0`

Status: **exact implementation remotely green; proof-only closeout effective
after this exact closeout commit is pushed and both required GitHub `main` jobs
are green**

Machine proof:

- `registries/fresh_motor_source_identity_witness_live_implementation_proof.v0.json`

## Remotely Green Implementation

Exact implementation commit
`a2af6c4c016a81652b3c1bae13d8c8e5e56ef4e9` passed on GitHub `main`:

- Base Python job `99515316155` in 7m02s;
- Optional Neuro Readers job `99515315921` in 9m45s; and
- CI run `33400484765`.

The first implementation commit, `ec946835f4e3f34a1ae3e3f0aef8cc1cf4aa6b7b`,
correctly failed clean shallow CI because one authority loader attempted to read
the historical decision with `git show`. The repair removed that history-depth
dependency while preserving exact no-follow local bytes, SHA-256, Git-blob,
and semantic decision validation. A regression test now proves the loader does
not invoke Git at all. This was an engineering repair; the consumed generated
qualification was not repeated.

## Bound Evidence

This proof binds the exact 10,859-byte implementation ledger, which binds 15
implementation and qualification artifacts totaling 303,497 bytes. Including
the ledger itself, the proof covers 16 artifacts totaling 314,356 bytes. Their
canonical artifact-set SHA-256 is:

```text
4868b4891f5d2885bf33426dcfcac31ad4e2774a6e0ca7a2416eb3a7d2521b03
```

The accepted sole generated qualification remains two deterministic
five-profile, 17-root, 34-page replays; 76 generated transport calls; 16
refusals, including six direct transport refusals; and zero candidate semantic
accesses. It completed in 0.1274927919730544 seconds at 40,583,168-byte peak
RSS. Generated input was 19,898 bytes, temporary peak storage was 737 bytes,
the report was 3,018 bytes, and retained generated payload was zero bytes.

Both replays produced global ledger digest
`9f567e28e2424ad71aa724834f82b89b182f27e36df0f4c7d04e33a29b73c97f`.
The generated `CI-W0` receipt digest was
`028bca65f22f88b0084eb1efbbea1617b517c614e6b74b1f23f7f236741889a9`.

## Proof Boundary

This closeout reads only tracked implementation artifacts and their local Git
identities, plus the public GitHub status of the exact implementation commit.
It does not rerun qualification `Q0`, invoke the live witness, contact any
official source index, decode a candidate record, select a dataset, access a
payload or EEG, read a header, signal, event, annotation, target, or label, run
or train a model, freeze a prediction, score an outcome, operate a stream or
device, publish a release, or upgrade a scientific claim.

The production adapter remains one-shot, parameterless, and authority-locked.
Its ability to make the registered three GitHub `CI-W0` requests and bounded
official-index requests is code capability, not present execution authority.

## Next Gate

After this proof-only closeout is remotely green, fresh maintainer words may be
bound to this exact implementation commit, its 16-artifact proof set, CI run,
two job IDs, repository, workflow, packet, and `CI-W0` contract in a separate
execution decision. That decision must itself be committed, pushed, and pass
both required jobs before the sole live source-identity witness may run.

No current words pre-authorize that later decision. No discovery pass, neural
payload, model, prediction, score, or scientific claim is authorized by this
closeout.

Engineering capability added: the exact dependency-free, fail-closed live source-identity witness is now artifact-bound and proven in both clean remote environments.

Scientific claim not established: no official source index or EEG was accessed and no model was run, so no neural advantage, nuisance resistance, movement intention, unseen-person generalization, language decoding, or live neural operation was established.
