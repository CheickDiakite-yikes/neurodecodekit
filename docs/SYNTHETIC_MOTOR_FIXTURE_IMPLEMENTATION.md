# Synthetic Motor And Shortcut Fixture Implementation

Status: **implemented and locally qualified; measured retained closeout pending
remote-green implementation commit**

Date: 2026-08-08

Frozen contract:
`registries/synthetic_motor_fixture_contract.v0.json`

Implementation receipt:
`registries/synthetic_motor_fixture_implementation.v0.json`

## Added Capability

`neurodecodekit.training.synthetic_motor_fixture` now provides:

- an exact registered-contract loader;
- deterministic construction of 96 synthetic, strictly pre-event items with
  eight invented channels and invented geometry;
- explicit valid lengths, masks, timestamps, pair identities, synthetic design
  classes, factor identities, and 48/32/16 pair-bound partitions;
- potential, mu, beta, mixed, spatial-reversal, timing-only,
  peripheral-common-mode, and pure-noise factors;
- eight deterministic line-noise, dropout, derangement, displacement,
  peripheral-only, zero-signal, and future-tail mutations;
- array hashes, deterministic NPZ bytes, a strict full loader, and a
  metadata-only sidecar inspector that verifies the payload hash and ZIP member
  inventory without opening an array; and
- collision refusal, a 4 MiB output ceiling, lazy optional NumPy/SciPy imports,
  and exact zero-padding checks.

The CLI surfaces are:

```bash
neurodecode make-synthetic-motor-fixture --help
neurodecode inspect-synthetic-motor-fixture --help
```

No generated NPZ or metadata sidecar is retained in Git. Test fixtures live
only in disposable temporary directories.

## Local Verification

The pre-implementation contract milestone passed 1,225 tests with 3 expected
skips. The implementation passes:

- 12 focused implementation tests;
- 31 combined implementation, contract, receipt, and prior-result regression
  tests;
- 1,242 complete tests with 3 expected skips and 469 subtests;
- Ruff on the implementation, CLI, and touched regression test; and
- `git diff --check`.

The complete test run took 32.93 seconds wall time and reached 658,866,176 bytes
peak RSS. That is a repository-wide test-run measurement, not the future
single-fixture execution measurement and therefore is not evaluated against
the fixture's 512 MiB execution cap.

The disposable implementation probe produced shape `[96, 8, 256]`, 20,448
valid time samples, padding fraction `0.16796875`, a 572,292-byte NPZ, an
11,841-byte sidecar, and 584,133 total bytes. Those values are development
observations only. The exact retained measurement and receipt must be produced
once after this implementation commit is pushed and remotely green.

## Execution Order

1. Commit and push the implementation and this receipt.
2. Require both CI jobs to pass for that exact implementation commit.
3. Run one bounded synthetic CLI roundtrip in a disposable directory with one
   numerical thread and one worker.
4. Retain only aggregate measurements, hashes, and claim boundaries. Do not
   commit the generated NPZ or metadata sidecar.

No remote-green result means no measured closeout. A resource, replay,
validation, or CLI failure parks the work order instead of widening scope.

## Boundaries

All channels, geometry, classes, factors, and waveforms are synthetic. The
implementation reads no S20, PhysioNet, EEG, MEG, target, label, text,
participant identity, pretrained weight, checkpoint, or external embedding. It
performs no model inference, parameter update, scientific scoring, network
call, provider call, stream, device, or hardware operation. CML-v0 remains a
separate later work order.

Engineering capability added: NeuroDecodeKit can now generate, validate,
inspect, and mutate one deterministic synthetic motor-factor fixture under
strict identities, causality, leakage, hash, padding, and resource contracts.

Scientific claim not established: this implementation demonstrates no real
EEG physiology, neural origin, decoding accuracy, generalization, end-to-end
latency, device performance, home use, or clinical utility.
