# Loop 48 Stage C Synthetic Temporal-Representation Result

Date: 2026-07-15

Status: **Consumed and parked after one synthetic execution; no rerun**

Machine record:
`registries/loop48_stage_c_synthetic_result.v0.json`, SHA-256
`3c1c0d7286526f00a51325c04493b2c07bd5a989f683df03c50d2181f6fa738a`

## Executive Verdict

The one registered Stage C synthetic calibration completed after correction
commit `2836ecc` passed push CI `29467415680` and PR CI `29467416894`. The
causal temporal candidate did substantially better than the zero-context
ablation on the purpose-built fixture, but it failed both frozen absolute
performance gates. Stage C is consumed and parked without tuning or rerun.

The selected candidate reached final macro CER `0.433333` and `1/8` exact
sequences. The ablation reached macro CER `1.000000` and `0/8` exact sequences,
so temporal context improved CER by `0.566667`. The frozen gate nevertheless
required candidate CER at most `0.10` and at least `7/8` exact sequences.

This is synthetic mechanics evidence. It does not show that the model can
extract language from MEG, EEG, or any real neural recording.

## Frozen Identity

| Boundary | Exact evidence |
|---|---|
| Research | commit `9579be9`; push CI `29466218879`; PR CI `29466225955` |
| Implementation | commit `59b30a3`; push CI `29467094688`; PR CI `29467095865` |
| Fail-closed correction | commit `2836ecc`; push CI `29467415680`; PR CI `29467416894` |
| Source result | 13,138 bytes; SHA-256 `1d35b38150a09add7839fe61dd667336f18e19d6a4ef4bea7352aa88468c512a` |
| Committed aggregate | 7,546 bytes; SHA-256 `3c1c0d7286526f00a51325c04493b2c07bd5a989f683df03c50d2181f6fa738a` |
| Fixture | seed `4850`; 40 rows; 24/8/8 split; SHA-256 `0322b5d2a89c5b0bd95cd8829e0a5d463fb1c8a9da3a7aad82f6e00fd1e95537` |

The earlier preflight refusal generated no fixture, model operation, optimizer
step, or output and did not spend the calibration. The corrected execution
described here is the single consumed run.

## Selection And Final Result

| Candidate recipe | Selection macro CER | Selected |
|---|---:|---|
| `L48C-SYN-OPT0` | `0.510417` | yes, by the frozen rule |
| `L48C-SYN-OPT1` | `1.000000` | no |
| `L48C-SYN-OPT2` | `0.533333` | no |

| Final metric | Temporal candidate | Zero-context ablation | Gate |
|---|---:|---:|---|
| Macro CER | `0.433333` | `1.000000` | candidate `<=0.10`: **failed** |
| Exact sequences | `1/8` | `0/8` | candidate `>=7/8`: **failed** |
| Candidate CER improvement | `0.566667` | n/a | `>=0.10`: passed |

The positive candidate-ablation contrast shows that the registered causal
architecture used ordered history on this fixture. It does not rescue the
failed absolute gate: the candidate still decoded seven of eight purpose-built
synthetic sequences inexactly.

## Mechanics Gates

- deterministic numeric checkpoint replay passed;
- all 8/8 future-mutation controls passed;
- all 8/8 prefix-resume checks passed;
- the producer remained causal with 470 ms required left context and zero
  right context;
- strict 24/8/8 split identity, lengths, padding, output geometry, and fixture
  hash checks passed; and
- no plaintext target or prediction was emitted.

The candidate had 7,692 parameters. The ablation had 7,568 parameters, a
124-parameter or 1.612070% gap. Both emitted at 25 Hz from a 100 Hz synthetic
source grid.

## Resource And Access Ledger

| Measure | Result | Cap |
|---|---:|---:|
| Fixture input arrays | `1,699,920` bytes | `4,194,304` bytes |
| Generated artifacts | `83,132` bytes | `16,777,216` bytes |
| Internal runtime | `7.829308` sec | `600` sec |
| External wall runtime | `8.31` sec | `600` sec |
| Internal peak RSS | `310,509,568` bytes | `1,073,741,824` bytes |
| External peak RSS | `320,405,504` bytes | `1,073,741,824` bytes |
| Optimizer steps | `1,680` | `1,800` |
| Training runs | `4` | `4` |
| Free disk before run | `41,574,039,552` bytes | minimum `21,474,836,480` bytes |

The execution used one CPU thread and one worker. It performed 8 model-
inference runs, 2 checkpoint writes, and 1 checkpoint read. Raw-data reads,
real-cache stat/hash/member reads, real signal and target rows, downloads,
S24/S25 operations, and stream/device/hardware/RW3 operations were all zero.
End-to-end latency was not measured.

The ignored run directory contains two numeric checkpoints and aggregate JSON
and Markdown reports totaling 83,132 bytes. None is committed. The committed
machine record contains only identities, aggregate metrics, hashes, counters,
warnings, and the disposition; it contains no plaintext target or prediction.

## Closeout Verification

The focused Stage C and Loop 48 boundary set passed 64 tests. The complete
dependency-light suite passed 919 tests with 156 expected skips in 1.439
seconds internal time and 1.70 seconds wall time at 123,912,192-byte external
peak RSS. The complete optional-neuro suite passed 966 tests with 3 expected
skips in 29.839 seconds internal time and 30.87 seconds wall time at
621,412,352-byte external peak RSS. Both suites added exactly eight tests over
the corrected pre-execution 911/958 baseline without losing a prior test.

Ruff, compileall, every registry JSON file, three CLI help surfaces, source-
result inspection, and `git diff --check` passed. Closeout verification did not
rerun training, inference, final scoring, or any scientific execution.

## Disposition

The registered synthetic gate failed. Do not rerun, change a threshold, select
a different recipe after final scoring, extend steps, change the fixture, or
promote the candidate into protected Stage C evidence from this outcome.

`R1` remains a plausible mechanics explanation only in the narrow sense that
temporal context beat the zero-context ablation on this constructed task. The
result does not justify reopening S21, acquiring S24, opening S25, or claiming
that temporal context repairs real neural decoding.

Engineering capability added: NeuroDecodeKit executed the registered causal
temporal candidate, zero-context ablation, deterministic selection,
checkpoint-replay, causality, padding, resource, and no-leakage gates once
under a bounded synthetic interface.

Scientific claim not established: no real signal or target was opened, so
neural advantage, sensor-signal dependence, brain-specific origin, real
decoding improvement, generalization, real-time performance, and portable or
home EEG performance remain unestablished.
