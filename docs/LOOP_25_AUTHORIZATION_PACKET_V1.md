# Loop 25 Authorization Packet v1

Date: 2026-07-12

Status: **Awaiting an explicit decision; this packet is not authorization**

Machine request: `registries/loop25_authorization_request.v1.json`

Superseding amendment:
`docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md`

Anti-alias audit: `docs/LOOP_25_ANTI_ALIAS_AUDIT.md`

## Review Identity

```text
amendment commit:          b6b92d8ea1cdeadfd6b7cd9f4704aee018516197
push CI run:               29195938038
push CI conclusion:        success
base Python job:           success
optional neuro job:        success
v1 contract:               registries/causal_preprocessing_contract.v1.json
v1 contract SHA-256:       ecec99a7cc505ec0256c01c3c1e8aeaa05323ab54a71528323fa6d32bd289141
v1 amendment SHA-256:      e3d6832583da9d787664e7912cbd3c74a6f4c8e4fc9b205d0475279cc493c4e7
anti-alias audit SHA-256:  c1eec14782620cf7d609bf7af5f68ea5f74ec79bdda4659877012e46c4766c95
amendment tests:           11
complete local unit suite: 342 passed / 3 skipped
```

The CI run is inspectable at
[GitHub Actions run 29195938038](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/29195938038).

Every `authorized_now` field in the machine request is `false`.

## Why This Replaces v0

The original v0 registration at `a36d97b` was reviewed before authorization.
That review found a material gap: v0 treated the 0.5-45 Hz task bandpass as its
anti-alias stage, tested only 60 Hz at -6 dB, and did not bound the full
50-500 Hz folding band.

The pinned public source chain shows that Brain2Qwerty uses NeuralSet 0.2.2,
whose MNE extractor performs filtering and a separate `Raw.resample` step.
The public resampler is offline, so v1 does not copy it into a causal runtime.
Instead, v1 adds a dedicated stateful anti-alias stage and tests its complete
folding band before a fixture array may open.

The v0 files remain immutable evidence, but the v0 request was never
authorized and its authorization sentence is no longer actionable. Only this
v1 packet is current.

## Decision In Plain Language

An exact authorization would permit a small target-free synthetic mechanics
gate, after a separate authorization-only commit is tested, pushed, and
remotely green.

It would permit:

- implementing the three registered runtime modules, three test modules, and
  four CLI commands;
- generating 24 target-free numerical stress items across two physically
  separate seed partitions;
- designing exactly one registered notch, bandpass, and dedicated elliptic
  anti-alias SOS chain;
- running a static filter gate before opening either fixture array;
- opening development seed 2501 once only after the static gate passes;
- opening qualification seed 2502 once only after the complete development
  report is frozen and passes;
- writing bounded reports and a final proceed-or-park decision.

It would not permit:

- real S21, S7, EEG, MEG, or any consumed cache/data access;
- target, label, text, prediction, or prompt access;
- checkpoint reads, encoder/decoder/model inference, training, calibration,
  or parameter updates;
- network calls, downloads, RW3 Stage A, source chunks, BrainFlow, LSL,
  PyXDF, sockets, streams, boards, devices, or hardware;
- Loop 26 or any later loop;
- changing the filter family, frequency edges, attenuation, seeds, schedules,
  tolerances, caps, or stop rules after observing a protected partition.

## Frozen Scope

| Surface | Exact v1 scope |
|---|---|
| Input/output | 5-channel float32, exactly 1,000 Hz to 100 Hz |
| Causal chain | 50 Hz notch, 0.5-45 Hz Butterworth bandpass, dedicated elliptic anti-alias, phase-locked 10x decimation, frozen scale, clamp +/-5 |
| Anti-alias specification | 45 Hz passband edge, <=1 dB loss; 50 Hz stopband edge, >=60 dB designed attenuation; SOS output |
| Static response gate | 65,537 points from 0-500 Hz, complete folding band <=-59.5 dB, 23 exact alias source probes |
| Mutable state | At most 17 SOS sections, 1,360-byte float64 filter-state array, 4 KiB complete state cap |
| Fixture | 24 items, 12 per partition, 6 target-free numerical stress families |
| Fresh seeds | 2501 development, 2502 one-time qualification |
| Transport checks | 7 chunk schedules, 10 resume cuts, 3 future-mutation cuts |
| Safety surface | 45 exact refusal IDs, 23 access counters |
| Resources | 1 CPU thread, 1 worker, 4 MiB fixture, 16 MiB working arrays, 8 MiB all generated artifacts, 45 sec internal runtime, 1 GiB RSS |
| Forbidden counters | Real/consumed/cache/target/checkpoint/model/training/network/RW3/device operations all exactly zero |

The 45-50 Hz interval is a transition band without a passband claim.
Elliptic ripple, step ringing, pole margin, and frequency-dependent phase delay
must be reported.

## Required Order After An Exact Decision

Authorization is deliberately two commits away from implementation:

1. record only the explicit decision in a new v1 authorization record;
2. test it against this request, the v1 contract, and the immutable v0 history;
3. commit and push the authorization-only record;
4. confirm both remote CI jobs are green;
5. implement only the registered files and CLI surface;
6. design and hash coefficients exactly once;
7. pass the static pole, dense-response, alias-map, impulse, and step gate;
8. park with both seeds unopened if that static gate fails;
9. otherwise open seed 2501 once and freeze the development report;
10. open seed 2502 once only after development passes;
11. close without rerun, post-result tuning, or widened tolerance.

## Exact Choices

### Authorize only v1

> Authorize Loop 25 implementation exactly as scoped in
> `docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md` and
> `registries/causal_preprocessing_contract.v1.json`. Do not authorize real or
> consumed data, targets, model inference, training, RW3 Stage A, streams,
> devices, or hardware.

### Hold

> Hold Loop 25 implementation. Keep every Loop 25 execution authorization flag
> false.

### Amend again

Begin with:

> Amend the Loop 25 packet before authorization:

Then state the requested change. Any material change needs a new tested,
pushed preregistration before execution.

General continuation, roadmap approval, creative latitude, a pull request,
silence, Loop 24 authorization, or an RW3 decision is not authorization.

## Engineering Capability If A Future Gate Passes

A future pass could establish that one exact target-free 1,000-to-100 Hz
causal preprocessing implementation has zero undeclared future samples,
passes its full synthetic anti-alias specification, and preserves output,
indices, timestamps, and state across its frozen chunk and resume schedules.

## Scientific Or Decoding Claim Not Established

Neither this packet nor a future mechanics pass establishes official
Brain2Qwerty numeric equivalence, acceptable filter phase/ringing for neural
decoding, retained neural information, real-data quality, neural advantage,
CER/WER improvement, model or decoder causality, end-to-end latency,
unseen-person generalization, portable EEG/MEG behavior, assistive efficacy,
diagnosis, or clinical utility.
