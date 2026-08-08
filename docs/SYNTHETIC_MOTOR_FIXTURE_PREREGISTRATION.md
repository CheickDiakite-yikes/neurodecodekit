# Synthetic Motor And Shortcut Fixture Preregistration

Status: **Tier B fixture contract frozen; implementation and measured fixture
result not started**

Date: 2026-08-08

Machine contract:
`registries/synthetic_motor_fixture_contract.v0.json`

## Question

Can NeuroDecodeKit create one tiny deterministic array fixture that isolates the
motor and shortcut factors required by the open EEG strategy before installing
more libraries, opening public EEG, interpreting S20, or implementing CML-v0?

This is fixture infrastructure. It is not a model experiment and has no
scientific endpoint.

## Frozen Scope

The generator will create exactly 96 synthetic pre-event items: 12 items for
each of eight factor families. Each family contains six paired left/right design
classes assigned as complete pairs to `train`, `check`, and `final` partitions:
6/4/2 items per family and 48/32/16 items overall.

The factor families are:

1. potential-shape signal;
2. mu-energy signal;
3. beta-energy signal;
4. mixed potential/mu/beta signal;
5. left/right spatial reversal;
6. timing-only class structure with class-independent waveform content;
7. peripheral-like common-mode artifact with an explicit synthetic peripheral
   proxy; and
8. pure paired noise with no class relation.

Every channel identity is synthetic (`SYN00` through `SYN07`). Geometry is an
explicitly invented left/right layout in arbitrary units, not an anatomical
montage. The arrays use 128 Hz, at most 256 strictly pre-event samples, float32
signals, explicit true lengths, valid masks, pre-event timestamps, synthetic
design-class IDs, pair IDs, factor IDs, and partition IDs.

Synthetic design classes are generator controls, not participant labels or
text targets. No target text, intended text, prompt, real channel name,
participant identity, protected path, real payload, pretrained weight, or
external embedding may enter generation.

## Frozen Mutations

The implementation may expose only these deterministic, shape-preserving
mutations:

- 50 Hz and 60 Hz line components;
- one declared-channel dropout;
- one frozen channel derangement;
- one nonwrapping 16-sample displacement;
- peripheral-proxy-only signal;
- all-zero signal; and
- future-tail mutation after a declared cutoff for prefix-invariance tests.

Padding must remain exactly zero under every applicable mutation. A future-tail
mutation must leave every value at or before its cutoff byte-identical.

## Resource And Dependency Contract

- Fresh fixture seed: `5503`.
- One CPU thread and one worker.
- At most 60 seconds wall time and 512 MiB peak RSS.
- At most 4 MiB retained output across one deterministic NPZ and one JSON
  sidecar.
- NumPy `>=1.26` and SciPy `>=1.11` are optional, lazily imported generation
  dependencies. Base package import must remain dependency-free.
- No generated array payload is committed. Tests may replay in disposable
  directories; one measured closeout may retain only bounded hashes and
  aggregate metadata.

## Acceptance Gates

1. Byte-identical replay from seed `5503`.
2. Exact 96-item, eight-family, 48/32/16 partition inventory with paired rows
   never split across partitions.
3. Strict schema, dtype, shape, mask, timestamp, zero-padding, geometry, and
   hash validation.
4. Analytic factor checks distinguish potential, mu, beta, mixed, spatial, and
   peripheral families without fitting a model.
5. Timing-only and pure-noise pairs have class-independent waveform content by
   construction.
6. Every mutation is deterministic, bounded, and preserves masks/padding.
7. No forbidden real, protected, text-target, pretrained, path, model, network,
   stream, device, or hardware field or access.
8. CLI creation and metadata-only inspection refuse overwrite and malformed
   payloads.
9. Runtime, RSS, input/output bytes, warnings, unavailable fields, causality,
   and all operation counters are reported.
10. Full tests, focused tests, Ruff, compileall, JSON validation, CLI help, and
    `git diff --check` pass.

## Boundaries

The approved Research Autonomy Charter and the user's systematic-continuation
request permit this new reversible Tier B fixture contract. The older CML
research artifact remains unchanged and does not itself authorize a model,
training, inference, scoring, real-data operation, or claim. This contract does
not implement CML-v0, create a protected split, consume a scientific test, or
authorize any Tier C action.

Engineering capability if all gates pass: a deterministic synthetic fixture
can exercise motor-factor, timing-shortcut, peripheral, padding, and corruption
interfaces before real evidence is spent.

Scientific claim not established even if all gates pass: generated factors
cannot establish real EEG physiology, neural origin, decoding accuracy,
generalization, latency, device performance, home use, or clinical utility.
