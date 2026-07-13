# Loop 25 Causal Preprocessing Result

Date: 2026-07-13

Status: **Complete - registered mechanics gate passed; no rerun authorized**

Proof posture: **target-free synthetic causal-preprocessing mechanics only**
Scientific roadmap mapping: **Loop 45 Causal Source-Path Qualification complete**

Machine-readable result:
`registries/loop25_causal_preprocessing_result.v1.json`

## Decision

The exact Loop 25 v1 causal preprocessing path passed its static design gate,
development gate, and conditional one-time qualification gate. The registered
decision is:

```text
loop25_causal_preprocessing_mechanics_passed_ready_for_separate_loop26_decision
```

This closes the target-free mechanics prerequisite represented by Loop 45 in
the scientific roadmap. It does not authorize Loop 26 or Loop 46. Any real
S21 source-validation model, target open, inference, or training requires a
new hash-bound preregistration and separate authorization.

## Frozen Sequence

1. The v1 authorization-only record was committed at `1e7296a` and passed
   GitHub CI run `29275552886`.
2. The implementation was committed at `439f151` and passed both jobs in
   GitHub CI run `29277702513`.
3. The registered filter was designed exactly once.
4. The 65,537-point static response gate and 23-probe alias map passed before
   either fixture partition opened.
5. The target-free fixture was generated exactly once from seed 2501 and
   physically separate seed 2502.
6. Development opened once, passed, and its report was frozen and hashed.
7. Qualification opened once only after that freeze, then passed unchanged.
8. No post-result tuning or rerun is authorized.

The v0 contract and request remain immutable superseded history. The v1
request also remains immutable and says `authorized_now: false`; the separate
authorization decision is the record that enabled this one completed run.

## Static Filter Gate

| Measurement | Result | Frozen gate |
|---|---:|---:|
| Dedicated anti-alias SOS sections | 4 | at most 12 |
| Total SOS sections | 9 | at most 17 |
| Filter-state array | 720 bytes | at most 1,360 bytes |
| Maximum pole magnitude | 0.9988174290 | at most 0.999999 |
| Dedicated passband minimum | -1.000000 dB | at least -1.0 dB, numeric tolerance applied |
| Dedicated stopband maximum | -60.000000 dB | at most -59.5 dB |
| Complete-chain 50-500 Hz maximum | -67.503786 dB | at most -59.5 dB |
| 50 Hz complete-chain gain | -132.250670 dB | at most -20 dB |
| Response grid | 65,537 points, 0-500 Hz | exact |
| Alias probes | 23/23 passed | exact |
| Static runtime | 1.073600 sec | at most 45 sec |
| Static peak RSS | 136,806,400 bytes | at most 1 GiB |
| Static artifacts | 27,385 bytes | included in 8 MiB total |

The filter bundle is 9,149 bytes with SHA-256
`e2bc30198072ca16609eada9b024e7f2fbe591faa64739dc1c0226f0ea2396ca`.
Its SOS semantic hash is
`fd4563bc539171fa7f6c806da7308c89b875f52d867fd7bb14b7f1479e10bc81`.

## Fixture

The fixture contains only `signals`, `input_lengths`, `item_ids`,
`source_start_samples`, and metadata. ZIP central-directory inspection rejects
hidden or unsafe members before NumPy opens an array. Targets, labels, text,
predictions, participant identity, recording paths, model outputs, and
checkpoints are forbidden.

| Partition | Seed | Items | Bytes | SHA-256 |
|---|---:|---:|---:|---|
| Development | 2501 | 12 | 360,701 | `c6319bab31167c7e2ff323ddc2793fe9261a90a288119e94ab96d32ffdc85f66` |
| Qualification | 2502 | 12 | 361,240 | `6e7276e0e53c49d9a3e02b1b7ad8ba0b8215d7e409f14f374b8c585c719684c2` |

The three fixture files total 728,596 bytes against a 4 MiB cap. Metadata-only
inspection opened zero signal arrays. The fixture command completed in 0.057
seconds of observed command wall time; that command did not record its own
separate peak RSS, so that stage-specific field remains unavailable. Static
and complete-gate peak RSS were measured directly.

## Replay Result

Development and qualification each contain 12 items, 29,440 valid source
samples, and 2,949 emitted output samples. Every item passed.

| Check | Development | Qualification | Combined |
|---|---:|---:|---:|
| Items passed | 12/12 | 12/12 | 24/24 |
| Seven-schedule checks | 84/84 | 84/84 | 168/168 |
| Ten-cut resume checks | 120/120 | 120/120 | 240/240 |
| Three-cut future-mutation checks | 36/36 | 36/36 | 72/72 |
| Valid source samples | 29,440 | 29,440 | 58,880 |
| Valid output samples | 2,949 | 2,949 | 5,898 |
| Input-array bytes | 985,872 | 985,872 | 1,971,744 |
| Output bytes | 106,164 | 106,164 | 212,328 |
| Padding fraction | 0.401042 | 0.401042 | 0.401042 |
| Partition runtime | 1.831797 sec | 1.808358 sec | 3.640155 sec |

All output values were finite and inside `[-5, 5]`. Kept source indices were
exactly `0, 10, 20, ...` below each true input length. Sample-grid timestamps
matched `(source_start_sample + source_index) / 1000` exactly. Flush invented
zero source samples and zero output samples.

The producer is causal with zero right-context samples and zero right-context
milliseconds. Its effective signal timestamp remains unavailable because the
IIR chain has frequency-dependent delay. End-to-end latency was not measured.

## Resources And Access

The complete gate took 4.468575 seconds and reached 121,356,288 bytes peak
RSS. Static plus complete-gate internal runtime was 5.542175 seconds. The
maximum observed peak RSS was 136,806,400 bytes. The largest materialized
partition used 985,872 bytes, and mutable filter state used 720 bytes.

Static artifacts, fixture files, and complete-gate artifacts total 788,967
bytes, or 9.41% of the 8 MiB cap. All report, fixture, working-array, mutable-
state, runtime, RSS, thread, and total-output limits passed.

Exact nonzero counters were one manifest read, one development open, one
qualification open, one filter design, one static gate, one alias map, one
frequency response, 24 canonical runs, 168 schedule runs, 240 resume runs, and
72 future-mutation runs.

Every protected or forbidden counter was zero:

- normalization fits
- real-data reads
- real-cache reads
- consumed-evidence reads
- target, label, text, or prediction reads
- checkpoint reads
- model runs
- training runs
- parameter updates
- external network calls
- RW3 operations
- stream, socket, board, device, or hardware operations

## What Was Proven

NeuroDecodeKit now has one strict, stateful, 1000-to-100 Hz causal
preprocessing implementation with a dedicated anti-alias stage, phase-locked
decimation, frozen normalization, exact state snapshots, deterministic resume,
sample-grid timestamps, bounded fixture generation, fail-closed validation,
four CLI commands, and audit-hashed reports. The exact registered synthetic
path passed its mechanics gates on this host with one thread.

## What Was Not Proven

No neural recording was used. No target text was used. No model ran and no
parameter was trained. The result does not show retained neural information,
neural advantage, decoding accuracy, unseen-person generalization, confidence,
capture-to-text latency, real-time operation, EEG utility, portable hardware,
home use, arbitrary-thought decoding, or clinical utility. The path is not
numerically equivalent to the official offline MNE FFT resampler.

## Next Gate

The next high-value decision is a new preregistration for the reserved S21
source-validation neural-effect experiment described by Loop 26 planning and
Loop 46 of the scientific roadmap. It must preserve the 55/6/5 split, keep
source test and session 2 closed, freeze six validation predictions before one
target open, compare against the prior and every registered corruption
control, and stay within the 2,908-parameter ceiling. This closeout does not
authorize that experiment.
