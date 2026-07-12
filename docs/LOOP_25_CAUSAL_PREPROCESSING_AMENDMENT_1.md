# Loop 25 Causal Preprocessing Amendment 1

Date: 2026-07-12

Status: **Frozen superseding amendment; no implementation or execution
authorized**

Machine contract: `registries/causal_preprocessing_contract.v1.json`

Anti-alias audit: `docs/LOOP_25_ANTI_ALIAS_AUDIT.md`

Original immutable registration: commit `a36d97b`, contract
`registries/causal_preprocessing_contract.v0.json`

Amendment parent: commit `2e7607b`

Contract SHA-256:
`ecec99a7cc505ec0256c01c3c1e8aeaa05323ab54a71528323fa6d32bd289141`

Proof posture: target-free synthetic causal-preprocessing amendment only

## Decision

The original v0 registration and v0 authorization request are superseded
before authorization. They remain unchanged as provenance, but neither is an
actionable scope for future execution.

The reason is material: v0 used the 0.5-45 Hz task bandpass as its anti-alias
stage, checked only 60 Hz at -6 dB above the new Nyquist, and left the rest of
the 50-500 Hz folding band unbounded. The pinned official NeuralSet extractor
applies a separate `Raw.resample` operation after bandpass filtering.

Amendment 1 adds a dedicated causal anti-alias SOS stage, full folding-band
validation, an alias destination map, stricter time semantics, and a static
design gate that occurs before either fixture partition can open.

No coefficient was generated, no synthetic array was created, and neither
seed 2501 nor 2502 was opened while preparing this amendment.

## Supersession Boundary

Frozen v0 artifacts remain byte-identical:

| Artifact | Frozen SHA-256 |
|---|---|
| `registries/causal_preprocessing_contract.v0.json` | `42781526225c556d0df54d1b6924fd5d9ecf95578a84c3e3922b6d5c7035050e` |
| `registries/loop25_authorization_request.v0.json` | `3d103a0a18bd1d9ea8b320cde9515f891e41646c51132ad9c7adea35838f04b4` |
| `docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md` | `c681be25a633705f14ae5e2850908c4d911762d380ee2342fb7f2a587a3ebe7c` |
| `docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md` | `6e2b6c1ff584fc186926e6c631b2e1397117f13564de13fd276d64497b874ed4` |
| `tests/test_causal_preprocessing_contract.py` | `e0e37d54f0d83103cddab5b7782b30722a52cb21ba8c9ae823421132684c2916` |

The v0 request was never authorized. Its development and qualification seeds
were never opened. Its exact authorization sentence is no longer actionable.
Only a future request bound to this v1 contract can be considered.

## What Stays Frozen

Amendment 1 does not expand the experiment:

- target-free synthetic seeds remain 2501 development and 2502 one-time
  qualification;
- 12 items per partition, five channels, and exact 1,024-4,096 sample lengths
  remain unchanged;
- all six signal families, seven chunk schedules, ten resume cuts, and three
  future-mutation cuts remain unchanged;
- source rate remains exactly 1,000 Hz and output rate exactly 100 Hz;
- kept absolute source indices remain `0, 10, 20, ...`;
- frozen center, scale, clamp, no-fit, no-padding, and no-delay-compensation
  rules remain unchanged;
- one CPU thread, one worker, 4 MiB fixture, 16 MiB working-array, 4 KiB
  mutable-state, 8 MiB total-artifact, 45-second, and 1 GiB RSS caps remain;
- real or consumed data, caches, targets, labels, text, predictions,
  checkpoints, model inference, training, network, RW3, streams, devices, and
  hardware remain forbidden;
- no Loop 26 or later work is authorized by a Loop 25 result.

## What Changes

### 1. Dedicated anti-alias stage

The exact amended chain is:

```text
validate contiguous finite float32 [5, time] at 1,000 Hz
  -> cast once to float64
  -> stateful 50 Hz notch SOS
  -> stateful fourth-order 0.5-45 Hz Butterworth bandpass SOS
  -> stateful dedicated elliptic anti-alias SOS
  -> keep absolute source indices divisible by 10
  -> frozen center and scale
  -> inclusive clamp [-5, +5]
  -> cast once to float32
  -> emit values, indices, and sample-grid timestamps at 100 Hz
```

The anti-alias design is frozen as:

| Parameter | Value |
|---|---:|
| API | `scipy.signal.iirdesign` |
| Passband edge | 45 Hz |
| Maximum passband loss | 1 dB |
| Stopband edge | 50 Hz |
| Minimum designed stopband attenuation | 60 dB |
| Filter family | elliptic |
| Output | SOS |
| Source rate | 1,000 Hz |
| Maximum anti-alias SOS sections | 12 |
| Maximum complete-chain SOS sections | 17 |

The section order is notch, bandpass, then anti-alias. Reordering, omitting,
or silently replacing a stage is a refusal.

Elliptic passband ripple, stopband ripple, step ringing, and nonlinear phase
are explicit tradeoffs. This is a compact causal mechanics candidate, not a
claim that it is scientifically optimal.

### 2. Static design gate before seed access

The future authorized access sequence is now:

1. validate v1 identity, source bindings, environment, and APIs;
2. design the registered coefficients exactly once;
3. freeze coefficient, section-order, pipeline, and state hashes;
4. run static pole, dense response, alias-map, impulse, and step gates;
5. park with both seeds unopened if any static gate fails;
6. inspect fixture metadata without opening arrays;
7. open development seed 2501 once;
8. run the full development mechanics gate and freeze its report;
9. open qualification seed 2502 once only after every development gate passes;
10. run the unchanged qualification gate once and freeze the decision;
11. write and inspect bounded artifacts without reopening a partition.

Coefficient design is independent of fixture content. Moving it before seed
access removes an unnecessary route by which a failed design could consume
the development partition.

### 3. Full folding-band gate

The static response grid contains exactly 65,537 inclusive linearly spaced
frequencies from 0 through 500 Hz.

Required anti-alias results:

- 0-45 Hz remains between -1 dB and 0 dB, subject only to the frozen numeric
  edge tolerance;
- 50-500 Hz is no greater than -59.5 dB on the dense grid;
- the complete chain is no greater than -59.5 dB throughout 50-500 Hz;
- the complete chain remains between -3 and +0.5 dB at 5, 10, 20, and 35 Hz;
- the exact 23-source-frequency alias map passes;
- every pole is strictly inside the unit circle and no pole magnitude exceeds
  0.999999;
- impulse and step outputs are finite;
- impulse peak, step overshoot, ringing, and frequency-dependent delay are
  reported.

The 45-50 Hz interval is a transition band with no passband claim. A passing
gate must still warn that this causal path is not numerically equivalent to
the public offline resampler.

### 4. Explicit time meanings

The output carries a sample-grid timestamp:

```text
source_start_sec + source_index / 1000
```

That timestamp names the retained source sample. Earliest availability cannot
precede arrival of that source sample. Effective signal time is unavailable as
one scalar because group delay varies with frequency. Computation, transport,
decoder, and rendering time are not measured here.

Zero right context therefore means no future sample access. It does not mean
zero filter delay or zero end-to-end latency.

## Amended Counts

| Registered surface | v1 count |
|---|---:|
| Target-free fixture items | 24 |
| Signal families | 6 |
| Chunk schedules | 7 |
| Resume cuts | 10 |
| Future-mutation cuts | 3 |
| Dense response points | 65,537 |
| Alias source probes | 23 |
| Access counters | 23 |
| Refusal IDs | 45 |
| Maximum total SOS sections | 17 |
| Maximum float64 filter-state array | 1,360 bytes |

The five new refusals fail closed on a superseded packet, a missing or
reordered anti-alias stage, an SOS/state cap overflow, incomplete folding-band
attenuation, or an incorrect alias map.

## Authorization Boundary

This amendment is not authorization. Every `authorized_now` field in the v1
contract is false. General continuation, the user's Loop 24 authorization,
approval of the 25-44 roadmap, an RW3 decision, a pull request, or a request to
be creative cannot authorize Loop 25 execution.

After this amendment is tested, committed, pushed, and remotely green, a new
hash-bound request may present this exact sentence:

> Authorize Loop 25 implementation exactly as scoped in
> `docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md` and
> `registries/causal_preprocessing_contract.v1.json`. Do not authorize real or
> consumed data, targets, model inference, training, RW3 Stage A, streams,
> devices, or hardware.

To hold:

> Hold Loop 25 implementation. Keep every Loop 25 execution authorization flag
> false.

Even the exact authorization sentence can permit only a separate tested,
pushed, remotely green authorization record. Implementation must still wait
for that record.

## Planned Runtime Surface Remains Absent

No planned runtime file or CLI command exists at this amendment milestone:

```text
src/neurodecodekit/preprocess/causal_preprocessing.py
src/neurodecodekit/training/causal_preprocessing_fixture.py
src/neurodecodekit/experiments/causal_preprocessing_gate.py
tests/test_causal_preprocessing.py
tests/test_causal_preprocessing_fixture.py
tests/test_causal_preprocessing_gate.py

make-causal-preprocessing-fixture
inspect-causal-preprocessing-fixture
causal-preprocessing-gate
inspect-causal-preprocessing-report
```

NumPy and SciPy remain optional. No base dependency is added.

## Claim Boundary

This amendment establishes only a stronger, source-audited protocol. It does
not establish that coefficients exist, that the filter passes, that outputs
are schedule-identical, that neural information is retained, or that text can
be decoded. It establishes no official Brain2Qwerty equivalence, CER/WER
improvement, unseen-person generalization, end-to-end latency, portable EEG,
assistive efficacy, diagnosis, or clinical utility.
