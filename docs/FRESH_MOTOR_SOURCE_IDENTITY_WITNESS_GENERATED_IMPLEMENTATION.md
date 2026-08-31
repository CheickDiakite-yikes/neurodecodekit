# Fresh Motor Source Identity Witness Generated Implementation

Date: 2026-08-31

Implementation: `FMSR1-R1-W-I0`

Qualification: `FMSR1-R1-W-Q0`

Status: **sole generated qualification passed; implementation pending this
exact commit and both GitHub `main` jobs; no live source or neural result**

Machine record:

- `registries/fresh_motor_source_identity_witness_generated_implementation.v0.json`

## Why This Exists

The next belief-changing operation is one bounded witness over the five frozen
official source indexes. That witness must establish complete replayable source
identity before any candidate metadata is parsed. This implementation is the
smallest dependency directly required for that operation.

It deliberately does not implement transport. The core accepts only generated
in-memory response bytes, decodes only registered pagination controls, and
emits a page-to-root-to-profile-to-global SHA-256 tree. Candidate regions are
raw-skipped and represented only by byte count and digest. The CLI exposes only
`plan`, `inspect-generated`, and `qualify-generated`; no live or execute command
exists.

## Frozen Surface

The implementation binds exact-green decision `FMSR1-R1-W-I0-D0` at commit
`e158e8cef2bc0267e5161e947b35409081ea37d7`, CI `33358495852`, Base Python
job `99385124402`, and Optional Neuro Readers job `99385124488`.

It replays exactly five profiles and 17 frozen roots:

| Profile | Roots | Method |
|---|---:|---|
| OpenNeuro CRN | 4 | POST |
| NEMAR | 4 | GET |
| PhysioNet | 4 | GET |
| GigaDB | 4 | GET |
| BNCI Horizon 2020 | 1 | GET |

OpenNeuro root request bodies preserve their frozen trailing newline. A
continuation mutates only `/variables/after` and is canonically reserialized
without a trailing newline. Generic JSON and HTML branches accept only the
registered typed continuation or terminal evidence. Ambiguous pagination,
noncanonical URLs, hash-tree drift, incomplete roots, transport drift, CI
drift, and target leakage all refuse.

## Sole Generated Qualification

The one authorized generated qualification completed successfully:

| Measurement | Observed |
|---|---:|
| Deterministic replays | 2 |
| Profiles / roots / pages per replay | 5 / 17 / 34 |
| Generated entity bytes | 5,112 |
| Refusal observations | 22 |
| Runtime | 0.035018666880205274 s |
| Peak RSS | 21,364,736 bytes |
| Canonical report | 2,244 bytes |
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |

Both replays produced global ledger digest
`e6c523a33168336f00a77b962ead3b0f785e74c1573edd55a01214c6bfcc1c66`.
The generated CI fixture receipt digest was
`bce73e6adf7456993aa4afa35fd3679c87e313eb4c3295884c5d1194df8a85b4`.

All network, official-index, candidate-semantic, source-selection, payload,
neural, target, label, model, training, prediction, scoring, release, and claim
operations were zero. No generated artifact was retained outside the committed
human and machine records.

## Next Gate

After this exact implementation commit is pushed to GitHub `main` and both
required jobs are green, the maintainer must provide fresh execution-bound
words. A separate decision must bind the exact implementation commit, artifact
set, CI proof, repository identity, workflow identity, three-request `CI-W0`
profile, packet, and maintainer words. Only after that decision is itself
remotely green may one consumed same-process live witness run.

Engineering capability added: a dependency-free, target-opaque validator can
reconcile complete pagination and byte identity across the exact five-profile,
17-root source universe while failing closed on ambiguity or drift.

Scientific claim not established: no official source, candidate metadata,
payload, EEG, EOG, EMG, target, model, prediction, or score was accessed, so no
neural advantage, nuisance resistance, intention decoding, unseen-person
generalization, language decoding, or live operation was established.
