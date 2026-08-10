# IACKD Channel Role and Geometry Implementation

Date: 2026-08-10

Status: **Generated-fixture qualified; exact implementation must be committed,
pushed, and remotely green before an all-false Tier C request may be prepared**

Lane: **IACKD-H2 Channel Role and Geometry Audit**

Registry: `registries/iackd_channel_role_geometry_implementation.v0.json`

## Parent Gate

The exact prospective registration is commit
`228ccd03f5e0b5d02ba104e13b77b04f2032df78`. CI run `31427931578`
passed Base Python job `93583989913` and Optional Neuro Readers job
`93583989996` before implementation began.

The implementation does not broaden
`registries/iackd_channel_role_geometry_contract.v0.json`. Its 316-object,
457,602-byte surface, one-thread limits, source-declared role policy, aggregate
output, no-retry/no-rerun real boundary, and metadata-only claim ceiling remain
authoritative.

## Capability Implemented

The dependency-free module provides a dry-run-first CLI without modifying the
central `neurodecode` CLI or the consumed IACKD-1 reader:

```bash
python -m neurodecodekit.preprocess.iackd_channel_roles
python -m neurodecodekit.preprocess.iackd_channel_roles \
  --fixture --out /tmp/iackd-h2-fixture.json
python -m neurodecodekit.preprocess.iackd_channel_roles \
  --inspect /tmp/iackd-h2-fixture.json
```

The default command reconstructs the exact role counts and byte totals from
the committed inventory while making zero network requests and performing zero
local IACKD path operations. Fixture mode generates target-free bodies at all
316 registered sizes, passes them through one-open mocked responses, emits one
bounded aggregate ledger, and retains no fixture when its temporary directory
closes. Inspect mode reads only that ledger under a 2 MiB cap.

## Strict Metadata Boundary

The parser accepts strict UTF-8 with an optional UTF-8 BOM. It rejects
replacement decoding, NUL and disallowed controls, duplicate JSON keys,
non-finite JSON numbers, malformed TSV rows, duplicate normalized names,
unknown BIDS channel types, bad units/status/sampling values, missing EEG
sidecar fields, invalid count fields, malformed coordinates, and invalid
coordinate systems or units.

Channel roles come only from the source table:

- predictive EEG is type `EEG`, excluding exact normalized M1/M2;
- HEOG and VEOG are recorded controls with compatible EOG types;
- TRIGGER must be `TRIG` or `MISC` and is never predictive; and
- M1/M2 are optional source-declared properties, never inferred from count.

Each channel table is paired with its EEG sidecar by private run key. Present
type counts and per-channel sampling declarations are reconciled. Each
electrode table is paired with its coordinate system and joined to channel
names by the frozen normalization within one private participant/hand group.
Private keys, source paths, participants, coordinates, descriptions, task
instructions, and unknown values never enter public output.

## Aggregate Contract

The ledger contains only unique channel-schema groups, aggregate status
counts, unique sidecar groups, one hashed role-map candidate, aggregate
geometry groups, H1 reconciliation booleans, measurements, warnings,
unavailable fields, acceptance gates, and one diagnostic route.

The router is ordered:

1. `IACKDR-R0`: transport, parse, membership, resource, or completeness failure;
2. `IACKDR-R1`: H1, role, sidecar-count, or sampling contradiction;
3. `IACKDR-R2`: more than one core schema after removing only M1/M2;
4. `IACKDR-R3`: stable roles but unavailable/variable reference or incomplete
   finite C3/C4/Cz geometry; and
5. `IACKDR-R4`: one stable role map with source agreement, stable reference,
   and all 30 central geometry groups complete.

Occipital O1/Oz/O2 coverage is reported but cannot rescue R4. It remains a
separate completeness requirement for a future IACKD-2 occipital proxy.

## Future Real Executor

The module contains the future one-shot executor but keeps it unreachable. It
requires a hash-valid implementation registry, exact green implementation
evidence, a separately committed decision quoting actual maintainer words,
the decision's exact SHA-256, a clean tracked worktree at that decision commit,
and execution ordinal one. It writes an exclusive private consumed marker
before constructing the first request.

No decision artifact exists. `--execute` refuses missing evidence before
transport. The module never names, resolves, stats, hashes, or opens the
retained 7.249 GB bundle, a VHDR, VMRK, EEG body, event, trajectory, target,
model, checkpoint, or score.

## Measured Synthetic Qualification

One final isolated generated-only qualification exercised the complete mocked
transport, parsers, pairing, reconciliation, aggregation, router, writer,
loader, and resource accounting:

| Measure | Observed |
|---|---:|
| Generated metadata bodies | 316 |
| Generated input bytes | 457,602 |
| Body SHA-256 passes | 316 |
| Semantic parses | 316 |
| Channel schema groups | 2 |
| Core schema groups after M1/M2 removal | 1 |
| Geometry groups | 30 |
| Constructed route | `IACKDR-R4` |
| Ledger runtime through finalization | 0.052731333 seconds |
| Runtime through return | 0.054679625 seconds |
| Peak RSS through return | 34,996,224 bytes |
| Generated ledger bytes | 8,282 |
| Network bytes | 0 |
| Real or protected operation sum | 0 |
| Real-only gates correctly false | 1 |

The temporary ledger SHA-256 was
`359396ee94c47c901e80aa043667be077bc33f15e808a20df820bc4a348cc1bb`.
The constructed role-map SHA-256 was
`a012ab1f63ed8f4aac5c2b4cf120325e8f5ccc76b0ba0cc4ec0a1f80d6a897e8`.
The output was removed automatically. These values describe generated fixture
mechanics only and predict nothing about the 316 public bodies.

## Adversarial Coverage

Twenty-five focused tests cover:

- exact registration and inventory replay, registered body sizes, role counts,
  and run/geometry membership;
- UTF-8/BOM, JSON duplicate/non-finite, TSV schema/width/name, BIDS type,
  units, status, sampling, sidecar, electrode, and coordinate refusals;
- all `IACKDR-R0` through `IACKDR-R4` routes, including full-surface R1 and R2
  mutations;
- status, URL, ETag, encoding, body-length, thread, output, overwrite, symlink,
  row-set, heavy-import, and forbidden-counter boundaries;
- deterministic full-surface replay, canonical hashes, aggregate-only output,
  forbidden-field/private-value rejection, duplicate-ledger JSON, and input
  caps; and
- default, fixture, inspect, and missing-evidence execute CLI paths with the
  network constructor patched closed where relevant.

## Next Gate

Run the focused and complete test suites, Ruff, compilation, all-registry JSON
validation, CLI help/default/fixture/inspect checks, and `git diff --check`.
Commit and push this exact implementation and require both CI jobs green. Only
then may an all-false Tier C packet request one 316-body audit. No prior
`continue` instruction retroactively authorizes that request or execution.

Engineering capability added: NeuroDecodeKit can now derive and validate a
count-agnostic, source-declared, geometry-aware sensor-role contract through a
bounded aggregate audit interface without touching retained EEG data.

Scientific claim not established: no real H2 metadata body, EEG sample, event,
trajectory, target, model, prediction, or score was accessed, so this work
establishes no neural effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit,
or clinical use.
