# MARC2-VR9P Two-Layer Private Diagnostic Implementation

Date: 2026-08-17

Lane: `MARC2-VR9P`

Status: **Generated/mock implementation qualified; private structural command
remains closed until this exact implementation commit is pushed and both
required CI jobs are green**

Module:
`src/neurodecodekit/datasets/marc2_two_layer_private_diagnostic.py`

Registry:
`registries/marc2_two_layer_private_diagnostic_implementation.v0.json`

Shared proof:
`registries/marc2_two_layer_private_diagnostic_proof.v0.json`

## Green Authorization Bound

Packet-bound decision `4cdd3d386b6c2c16b5187e0854b2bcb1f673b45a`
passed Base Python job `95280728093`, Optional Neuro Readers job `95280728134`,
and CI `31993388608` before implementation began. The module binds that exact
decision document, registry, test, request packet, request registry, and
request test by SHA-256.

The implementation does not import, call, patch, copy, edit, or otherwise
reuse the consumed VR7P executor. It composes generated cases through the exact
green VR8B parser/producer fixture path, calls the exact green VR6 adapter, and
uses the shared proof-record and machine-readiness validators.

## Command Surface

```text
python -m neurodecodekit.datasets.marc2_two_layer_private_diagnostic plan
python -m neurodecodekit.datasets.marc2_two_layer_private_diagnostic qualify
python -m neurodecodekit.datasets.marc2_two_layer_private_diagnostic inspect
python -m neurodecodekit.datasets.marc2_two_layer_private_diagnostic execute \
  --implementation-commit <40-lowercase-hex> \
  --ci-run-id <positive-int> \
  --base-job-id <positive-int> \
  --optional-job-id <positive-int>
```

There is no generic source, output, path, URL, threshold, retry, resume,
fallback, cleanup, substitution, or arbitrary execution argument. The execute
proof identifiers cannot redirect the fixed source or outputs.

## Generated Qualification

The qualification ran F03 and F04 sources in canonical and reversed order,
then replayed the complete four-path matrix exactly. Each of the eight paths:

1. materialized an exact generated 1,227-row parser/producer source;
2. wrote only an invocation-created mode-`0600` generated fixture;
3. exercised the same fresh-readiness, preflight, marker, strict-JSON, VR6,
   aggregate-firewall, and output-cap path used by the future private command;
4. called VR6 exactly once; and
5. retained only the expected outer F02 and nested F03 or F04 code.

The two complete replays were byte-identical after deterministic probes. The
qualification also exercised 70 direct refusals across decision, proof,
implementation, JSON, route, privacy, thread, resource, and path boundaries.

Measured generated result:

```text
route:                              MARC2VR9P-G1
matrix paths / exact replays:       4 / 2
exact VR6 calls:                    8
direct refusal mutations:           70
fixed committed reads / bytes:      15 / 328,313
generated source input bytes:       3,407,792
generated transient output bytes:   53,528
retained output bytes:              0
qualification report bytes:         6,541
runtime:                             1.2402790839987574 seconds
peak RSS:                            63,799,296 bytes
CPU threads / workers / jobs:        1 / 1 / 1
raw-data / real-cache reads:         0 / 0
model / training runs:               0 / 0
end-to-end latency measured:         no
```

All generated acceptance gates and all 70 direct refusals passed. Every real
readiness, `.codex_work`, private-source, output-root, consumed-executor,
archive, signal, target, model, prediction, score, network, provider, hardware,
FW2, CIL1, release, and claim counter remained zero.

## Future Fixed Private State Machine

Only after this exact implementation commit is pushed and both CI jobs are
green may one command:

1. verify the supplied commit, CI, two job IDs, clean tracked worktree,
   decision ancestry, implementation registry, and shared proof record;
2. obtain three consecutive passing readiness samples under the one-thread,
   load, RSS, free-disk, and 600-second limits;
3. create one new mode-`0600` certificate at
   `.codex_work/marc2_machine_readiness/vr9p/readiness.v0.json`;
4. recheck thread, RSS, and disk safety;
5. no-follow preflight the exact mode-`0600`, 418,755-byte structural source;
6. create the absent fixed output root and write one mode-`0600` consumed
   marker immediately before content open;
7. read, hash, and strict-parse exactly 418,755 bytes once;
8. call VR6 exactly once; and
9. write one mode-`0644` aggregate report only for outer F02 plus nested F03 or
   F04.

The real aggregate report has no reason, exception, predicate, failed value,
row, member name, path, offset, CRC, private hash, participant, session, run,
companion, candidate, selection, private manifest, or cohort. Success, nested
F02, a missing/unknown nested route, drift, or leakage consumes and parks the
lane.

## Caps And Failure Semantics

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
generated qualification:                <= 30 seconds
future private command:                 <= 650 seconds
peak RSS:                               < 256 MiB
minimum free disk:                      >= 15 GiB
fresh readiness wait:                   <= 600 seconds
private source read:                    exactly 418,755 bytes once
combined output:                        <= 1 MiB
network / archive / signal bytes:       0 / 0 / 0
retry / rerun / resume / fallback:      0 / 0 / 0 / 0
```

A pre-marker refusal opens zero private content and still consumes the one
registered invocation. A post-marker refusal consumes the one diagnostic. The
module grants no deletion, overwrite, retry, rerun, resume, repair, fallback,
substitution, or operation on another project or consumed root.

## Next Gate

Commit and push the exact module, tests, implementation registry, shared proof
record, and this document. Both Base Python and Optional Neuro Readers jobs
must pass before the fixed private command may be invoked. Generated success is
not permission to touch `.codex_work`.

An eventual F03 or F04 result would only identify the subject of a later
prospective structural repair. It would not authorize that repair, freeze a
cohort, open an archive member, or enter `MARC2-FW2` or `MARC2-CIL1`.

Engineering capability added: a proof-gated fixed-path wrapper can preserve
only one of two frozen target-free structural refusal classes while discarding
all private diagnostic context.

Scientific claim not established: generated qualification accessed no real
structural source, archive member, neural payload, target, prediction, or score
and establishes no neural effect, decoding performance, language decoding,
live decoding, or thought-to-text capability.
