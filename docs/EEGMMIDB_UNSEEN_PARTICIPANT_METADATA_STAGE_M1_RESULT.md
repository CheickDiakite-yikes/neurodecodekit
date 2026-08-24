# EEGMMIDB-UG1 Stage M1 Generated Metadata Result

Date: 2026-08-24

Lane: `EEGMMIDB-UG1-M1`

Status: **Passed once; consumed; proof-only closeout pending remote green**

Machine result:

- `registries/eegmmidb_unseen_participant_metadata_stage_m1_result.v0.json`

## Proof Order

Authorization decision `021bf8a1f2f12a8e7388a561535328cd0dc0dba2`
passed CI `32712235191` before implementation. The first implementation commit
`3f49821869fc89595741d89d0bf52d4454ca3edd` exposed one historical workflow
hash conflict in the complete suite. Corrective commit
`1c68a775294e08013f6ef0780eb8901917699db0` removed only the two new workflow
help lines and restored the proof-bound Stage G workflow identity.

The corrected implementation passed Base Python job `97395810059`, Optional
Neuro Readers job `97395810337`, and CI `32715529168`. A clean local base run
also passed all 5,822 tests with 212 optional-dependency skips. Only after both
remote jobs were green was the one registered Stage M1 qualification invoked.

## One-Shot Result

The sole generated/mock invocation passed all 20 registered cases in their
frozen order. It covered complete and unavailable optional validators,
deterministic replay, redirect/status/framing/validator/body-byte refusals,
request order and completeness, declared payload size, output collision, and
thread, disk, RSS, and wall-time limits.

| Measure | Result |
|---|---:|
| Generated fixture bytes | 8,354 |
| Aggregate output bytes | 1,416 |
| Aggregate output SHA-256 | `9f91843e6a20f8794cf19105116b3bcf13a2a3deff496a3c44ff30ecbcfeafe3` |
| Metadata bytes emitted across successful cases | 46,324 |
| Mock `HEAD` requests | 297 |
| Runtime | 0.017772541963495314 seconds |
| Peak process-tree RSS | 33,341,440 bytes |
| Initial free disk | 101,540,491,264 bytes |
| Real `HEAD` requests | 0 |
| Response-body reads / bytes | 0 / 0 |
| Real URL or local data-path operations | 0 |
| EDF content reads / payload bytes | 0 / 0 |
| Target reads / model runs / training runs / scores | 0 / 0 / 0 / 0 |

The fixture source was immutable across the pass and had SHA-256
`5ac6cdf00d97ca6b32f7a1f10921a8a875915e07a8944c9cb9030f7f4b34c0f4`.
The aggregate route was `EEGMMIDBUG1M-G1`. The temporary aggregate is recorded
by exact size and hash and is not committed to the repository.

## Interpretation

This pass proves that the exact 36-file, body-blind metadata protocol can be
validated under generated transport before contacting PhysioNet. It proves
fail-closed behavior and deterministic, bounded accounting. It does not prove
that any remote file exists, matches its expected identity, or contains usable
EEG.

Producer causality is unavailable for metadata identity. End-to-end latency
was not measured. Optional remote validators remain unavailable until the
separate Stage M2 invocation.

## Next Gate

Commit, push, and remotely green this result. Then add a proof-only closeout
that binds the exact implementation and result artifacts without repeating the
qualification. Stage M2 remains blocked until that proof-only closeout passes
both required remote jobs.

Engineering capability added: the strict body-blind metadata client passed its
one registered 20-case generated qualification with deterministic replay and
bounded resource use.

Scientific claim not established: no real URL, EEG payload, target, model, or
score was accessed, so this result establishes no neural effect, decoding
advantage, or unseen-person generalization.
