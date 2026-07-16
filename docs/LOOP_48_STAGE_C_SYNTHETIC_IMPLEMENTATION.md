# Loop 48 Stage C Synthetic Temporal-Representation Implementation

Date: 2026-07-15

Status: **Implemented and locally qualified without parameter updates; remote
green implementation gate pending; synthetic calibration not executed**

Machine record:
`registries/loop48_stage_c_synthetic_implementation.v0.json`

## What Is Implemented

The Stage C research comparison now has an executable synthetic-only path:

- `TinyCausalTemporalCTC-v0`: 7,692 parameters, 470 ms required left context,
  zero right context, and a 25 Hz output grid;
- `TinyCausalTemporalAblation-v0`: 7,568 parameters, no learned temporal
  history, zero right context, and the same 25 Hz output grid;
- an exact seed-4850 fixture with 40 rows, 102 channels, 100 Hz source timing,
  variable true lengths, strict zero padding, and physically separate 24/8/8
  train/selection/final identities;
- final-step-only Adam/AdamW training for the three frozen candidate recipes
  and one selected-recipe ablation;
- safe numeric NPZ checkpoints loaded with `allow_pickle=False` and strict
  schema, config, shape, dtype, parameter, and payload-hash checks;
- one aggregate result with selection, final, replay, future-mutation,
  prefix-resume, access-order, resource, warning, and claim-boundary fields; and
- `neurodecode loop48-stage-c-synthetic` plus
  `neurodecode loop48-stage-c-inspect-synthetic`.

The implementation imports NumPy and Torch only inside the functions that need
them. The base package still has no heavy dependency.

## Fixture Design

The ablation samples only source indices `0,4,8,...`. Every one of those source
frames is exactly zero in the fixture. Synthetic token identity is encoded in
the ordered six-value history immediately before selected output timestamps.
The candidate can inspect that past; the ablation cannot. This creates a clean
mechanics question about causal temporal context without using any real target,
real signal statistic, real prediction, participant identity, source path, or
cache.

The exact in-memory fixture contains:

| Field | Value |
|---|---:|
| rows | 40 |
| split | 24 train / 8 selection / 8 final |
| channels | 102 |
| source rate | 100 Hz |
| valid source samples | 3,996 |
| valid output steps | 999 |
| array bytes | 1,699,920 |
| fixture SHA-256 | `0322b5d2a89c5b0bd95cd8829e0a5d463fb1c8a9da3a7aad82f6e00fd1e95537` |

## Frozen Execution Order

The implemented one-shot command will:

1. verify the remotely green research registry and one-thread environment;
2. require at least 20 GiB free disk and a new or empty output directory;
3. generate and validate the 40 synthetic rows in memory;
4. fit all three candidate recipes and select by lowest selection CER, then
   fewer steps, then lexical recipe ID;
5. fit the zero-context ablation once under the selected recipe;
6. save the selected candidate and ablation checkpoints before final scoring;
7. open the same eight synthetic final rows once for both models;
8. reload the candidate checkpoint and require bitwise replay;
9. require eight future-mutation and eight prefix-resume row checks; and
10. emit one JSON report and one Markdown sidecar under the 16 MiB cap.

The command refuses output reuse. It accepts no real-data, cache, raw recording,
participant, target-file, S24, or S25 argument.

## Local Qualification

Thirteen focused tests pass. They cover deterministic fixture replay, strict
split identity, zero signal and target padding, sampled-frame leakage refusal,
exact model parameter counts, output lengths, zero right context, ablation
blindness, numeric checkpoint replay, malformed checkpoint refusal, nonzero
padding refusal, cap non-expansion, forbidden reader imports, malformed result
refusal, and CLI argument scope.

The qualification performed zero parameter updates and wrote no persistent
artifact. Temporary initialized-model checkpoints lived only inside test
temporary directories. The four registered training runs have not occurred.

The complete dependency-light suite passes 910 tests with 156 expected skips
in 1.745 seconds internal time and 1.97 seconds wall time at 121,733,120-byte
external peak RSS. The complete optional-neuro suite passes 957 tests with 3
expected skips in 29.474 seconds internal time and 30.38 seconds wall time at
611,270,656-byte external peak RSS. Both suites add exactly 13 tests over the
897/944 green research baseline. Repository-wide Ruff, compileall, all registry
JSON, both CLI help surfaces, and `git diff --check` pass.

## Authorization Boundary

Research commit `9579be9` passed push CI `29466218879` and PR CI `29466225955`
before implementation began. The approved charter permits the one synthetic
calibration only after this implementation commit is pushed and remotely green.
That later condition is not yet satisfied in this document.

No protected Stage C contract exists. No S21 cache stat, hash, member, target,
44-row reuse, 11-row reopen, validation, source test, session 2, S24, S25, real
model operation, download, stream, device, hardware, RW3, or claim upgrade is
authorized.

Engineering capability added: NeuroDecodeKit now implements the exact causal
temporal candidate, parameter-matched ablation, deterministic fixture, bounded
gate, safe checkpoints, and inspect surface selected by Stage C research.

Scientific claim not established: no synthetic calibration or real model run
occurred and no real signal or target was opened, so neural advantage,
sensor-signal dependence, brain-specific origin, decoding improvement,
generalization, real-time performance, and portable or home EEG performance
remain unestablished.
