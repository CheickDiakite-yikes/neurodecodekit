# COMM-G2 Generated Proof Implementation

**Date:** 2026-08-27  
**Status:** implementation ready; official qualification not executed  
**Scientific value:** none

## Green registration barrier

Registration commit `38f5e725f46ad7a8a18ff92dae665a1569e13d07` passed
Base Python job `98450778567`, Optional Neuro Readers job `98450778321`, and
CI `33052381349` before implementation began.

## What was implemented

The new module
`src/neurodecodekit/experiments/comm_g2_generated_proof.py` wraps the exact
frozen COMM-G1 scientific core without modifying it. It adds:

- canonical fixture digests over every registered row field and array byte;
- two sequential full replay coordinators in distinct spawned processes and
  exclusive clean workdirs;
- one spawned prediction worker per held-out fold, receiving only source
  targets and held-out signals;
- a separate scorer child that receives synthetic held-out targets only after
  the aggregate prediction freeze;
- exact prediction row, condition, dimension, finiteness, probability-sum,
  duplicate, and missing-row validation;
- fold-level source, held-out, and source-fit identity hashes;
- no-follow directory capabilities, exclusive temporary creation,
  non-replacing hard-link publication, file and directory fsync, and
  invocation-owned cleanup;
- all 35 registered adversarial families, including ancestor and leaf symlinks,
  publication race, resource-cap breaches, and fixture/prediction replay
  mismatch; and
- generated `plan`, proof-gated `qualify`, and aggregate `inspect` CLI commands.

The frozen 46,496-byte COMM-G1 module remains SHA-256
`99178d463558c27dcfe8c4346d6f47c207cb8dc60b6d45cd6ad3dab4b08fb3f4`.

## Development evidence

Dependency-free structural tests pass with optional numerical tests skipped.
The neuro-enabled environment passes the complete focused implementation and
contract suite.

One opt-in single-replay development probe exercised the integration without
calling the two-replay official qualifier. A final replay after binding the
child temporary directory to the invocation root passed in 10.345 seconds of
unittest wall time. The internal measurement below comes from the immediately
preceding probe of the same implementation module; the final test-harness-only
change did not alter that module.

| Measure | Observed |
|---|---:|
| Runtime | 10.540717291994952 s |
| Peak process-tree RSS | 245,727,232 bytes |
| Generated input | 16,515,072 bytes |
| Private generated predictions | 244,033 bytes |
| Temporary disk | 7,876 bytes |
| Parameter updates | 60 |
| Prediction sets / rows | 60 / 1,440 |
| Adversarial refusal IDs | 35 |
| Injected generated route | `COMM-G2-R1` |

This probe is disposable generated engineering evidence. It is not the one
registered two-replay qualification, does not satisfy replay equivalence by
itself, and has no scientific value.

## Boundaries

The official COMM-G2 qualification count remains zero. The implementation must
be committed, pushed, and remotely green before that one invocation. No real or
private path, EEG/MEG signal, event, target, label, model, network, provider,
stream, device, release, or claim operation occurred. `DREYER-C5R-1-HL`
remains the sole active Tier C packet with every authority flag false.
