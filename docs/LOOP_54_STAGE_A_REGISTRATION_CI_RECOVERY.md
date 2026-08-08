# Loop 54 Stage A Registration CI Recovery

Date: 2026-08-08

Status: **Historical exact-commit replay classified; immutable registration
payload recovered through a green pinned-toolchain descendant; authorization
still false**

## Purpose

The original Loop 54 Stage A registration commit is
`c1146233a6178ca5e1153b92565915abad029719`. Its first GitHub Actions attempt,
run `31127199848`, was cancelled before any job started during the 2026-08-06
Actions outage. On 2026-08-08 that same run was retried as attempt 2 against
the exact commit.

Attempt 2 created and ran both jobs. Optional Neuro Readers passed in 48
seconds. Base Python stopped at Ruff in 13 seconds after the floating
`ruff>=0.5` declaration installed Ruff `0.16.2`. That release reported 400
repository-wide findings that were not part of the frozen L54-A registration
payload. Compile, unit tests, and CLI help did not run in that Base Python job.
The failure is retained as toolchain-drift evidence; it is not relabeled an
infrastructure cancellation or a green exact-commit run.

## Immutable Payload Check

The three registration artifacts are byte-identical at the original commit,
the pinned-toolchain descendant `223299381036217631374d096fc842add5f6baf7`,
and the current branch before this recovery record:

| Artifact | SHA-256 |
|---|---|
| `docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md` | `9b17d31a70c88eff3ab77d731abf1c0c759152f5c2ee6c8b3c5153bbd57875b6` |
| `registries/loop54_stage_a_vhdr_contract.v0.json` | `a0a466d845bff79e9461646f76791a3583fe7c567aeb532b6e951e570411124e` |
| `tests/test_loop54_stage_a_vhdr_contract.py` | `33591567aab4999d7f9c9bab8986147869b0a9339b0c618149a8fd60ffb86ef5` |

No frozen preregistration, contract, invariant test, resource limit, refusal,
input identity, or claim boundary changed during recovery.

## Pinned Remote Proof Anchor

Commit `223299381036217631374d096fc842add5f6baf7` pinned Ruff to `0.15.20`
without changing the three frozen registration artifacts. Push CI run
`31132586790` passed Base Python in 18 seconds and Optional Neuro Readers in 51
seconds. The green jobs included Ruff, compilation, the base suite, the
neuro-enabled suite, focused RW2 tests, and CLI help.

This is a byte-identical-payload descendant proof anchor. It is not described
as a successful CI run whose head SHA was `c114623`.

## Exact-Tree Local Replay

A detached worktree at exact commit `c114623` was replayed locally with the
repository's pinned Ruff `0.15.20` and one configured compute thread:

```text
Ruff:                         pass
Ruff wall time:               0.05 seconds
Ruff peak RSS:          49,659,904 bytes
complete tests:              1,095
expected skips:                  3
test runtime:               28.824 seconds
external wall time:         30.26 seconds
external peak RSS:     626,622,464 bytes
compileall:                   pass
all registry JSON:            pass
CLI help:                     pass
```

The temporary detached worktree was removed after replay. No project file was
edited there.

## Recovery Decision

The original requirement for a green rerun whose head SHA is exactly
`c114623` is retired with a measured reason: its unbounded development
dependency no longer recreates the reviewed toolchain. Repeating that run
would test changing lint policy rather than the immutable registration
payload.

Future L54-A authorization may bind all of the following together:

1. original registration commit `c114623`;
2. the three immutable artifact hashes above;
3. pinned proof-anchor commit `2232993` and green CI run `31132586790`;
4. this additive recovery record and its remotely green commit; and
5. a new exact authorization request that leaves the frozen contract unchanged.

The old draft authorization request remains historical and non-actionable.
No parser implementation or real execution may begin from this recovery record
alone.

## Access Accounting

```text
S20 path stats:                         0
VHDR content opens / hashes / parses: 0 / 0 / 0
VMRK / EEG / MAT stats or reads:      0 / 0 / 0
signal / marker / target reads:       0 / 0 / 0
downloads / network payloads:        0 / 0
model / training / inference / score: 0 / 0 / 0 / 0
provider / device / hardware runs:    0 / 0 / 0
generated real-data artifacts:            0
```

Engineering capability added: NeuroDecodeKit can recover an immutable
preregistration from dependency drift without rewriting its scientific scope
or pretending a failed historical run was green.

Scientific claim not established: this recovery used no S20 content and
establishes no header readability, signal quality, trial validity, neural
advantage, decoding accuracy, generalization, latency, device, home-use, or
clinical result.
