# Synthetic Motor And Shortcut Fixture Result

Status: **work order 3 complete; one measured synthetic closeout consumed**

Date: 2026-08-08

Result registry:
`registries/synthetic_motor_fixture_result.v0.json`

## Order Of Evidence

The fixture contract was committed at `9238fd7` and passed push CI
`31278502496`. The implementation was then committed at
`ad361c89d480d697d79c10733eeaea3855716424` and passed push CI
`31279302969` before the measured closeout began. Base Python passed in 17
seconds and Optional Neuro Readers passed in 52 seconds.

One synthetic creation and one metadata-only inspection were then run in an
automatically removed temporary directory. There was no retry or post-result
tuning. The NPZ and sidecar were hashed and measured, then both were removed;
neither is retained in Git.

## Measured Result

| Field | Result | Cap |
|---|---:|---:|
| Runtime | 1.20 seconds | 60 seconds |
| Peak RSS | 118,177,792 bytes | 536,870,912 bytes |
| Input contract | 9,998 bytes | recorded |
| NPZ payload | 572,307 bytes | part of output cap |
| Metadata sidecar | 12,001 bytes | part of output cap |
| Total output | 584,308 bytes | 4,194,304 bytes |
| Retained generated files | 0 | 0 in Git |

The payload SHA-256 is
`32af9949516aecb4e78951087f8c720227f479d83babf39cea6b56e9bfac4c29`.
The sidecar SHA-256 is
`3d17a1b6669f485720dba85e8d670a4073c6ff52886c16eeac681899617debb2`.

The array shape was `[96, 8, 256]`. It contained 20,448 valid time samples and
a padding fraction of `0.16796875`. Every factor had 12 items; partitions held
48 train, 32 check, and 16 final items with every synthetic pair kept together.
The producer is causal at this fixture boundary, all valid timestamps are
strictly pre-event, and required right context is zero. End-to-end latency was
not measured.

Creation and inspection both returned zero and produced equal summaries. The
metadata-only inspector verified bytes, hashes, and ZIP members while opening
zero arrays. The byte-identical replay gate, analytic factor checks, strict
array validation, all eight mutations, future-tail prefix invariance, and
malformed/leakage/collision/cap refusals were established by the frozen test
suite without rerunning the measured closeout.

## Access Ledger

Exactly one synthetic fixture payload was generated in the measured closeout.
Raw-data reads, real-cache reads, real/protected reads, public EEG reads,
target/label reads, model or checkpoint loads, parameter updates, model
inference, training, scoring/selection, network calls, provider calls,
stream/device/hardware operations, and scientific-claim upgrades were all
zero.

Closeout verification passed 37 focused tests and the complete suite at 1,248
tests, 3 expected skips, and 469 subtests. Ruff, compileall, registry JSON, root
and command help, and diff hygiene are separate acceptance gates.

Warnings remain explicit:

- constructed motor-like factors are not biological observations;
- invented left/right geometry is not an anatomical montage;
- the timing-only family deliberately exposes a metadata shortcut;
- the peripheral common-mode factor is an ocular-like proxy, not validated
  EOG; and
- passing this fixture cannot qualify CML-v0 or a real EEG pipeline.

Real EEG/MEG quality, biological neural origin, decoding accuracy,
unseen-person generalization, end-to-end latency, device/home performance, and
clinical utility remain unavailable.

## Verdict And Route

All 18 acceptance gates passed. Work order 3 is complete. Work order 4 may now
freeze optional classical EEG adapter interfaces and grouped-fit leakage tests,
still without installing a package, opening real data, fitting a model, or
scoring a scientific endpoint.

Engineering capability added: NeuroDecodeKit can deterministically generate,
validate, inspect, and mutate a bounded causal synthetic motor-factor fixture.

Scientific claim not established: no real EEG physiology, neural origin,
decoding accuracy, generalization, end-to-end latency, device performance,
home use, or clinical result was established.
