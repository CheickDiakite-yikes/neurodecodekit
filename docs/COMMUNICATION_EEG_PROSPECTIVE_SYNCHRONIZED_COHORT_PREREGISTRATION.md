# Prospective Synchronized Communication EEG Cohort Preregistration

**Registration:** `COMM-P0-SYNC-v0`
**Date:** 2026-08-27
**Status:** Tier A study-design freeze; no human, device, or real-data authority
**Machine contract:**
`registries/communication_eeg_prospective_synchronized_cohort_contract.v0.json`

## Why This Is The Next Scientific Route

The public-source router is exhausted under the frozen evidence and storage
rules. SilentSpeech-EEG is still an unqualified watchlist source, TESSCCo's
paper-cited landing is unavailable, and Kara One is approximately 24 GB with
no member-level proof of a complete all-participant slice below 10 GiB. None
currently supports the required independent EEG-plus-eye-plus-mouth claim.

The shortest honest alternative is to design the missing evidence surface
directly: synchronized EEG, EOG, bilateral oral EMG, microphone, and triggers;
an untouched participant cohort; a target firewall; causal streaming; and a
single compact model. This registration freezes that study before recruitment,
recording, or hardware selection can be influenced by results.

It does not recruit anyone, collect consent, operate a device, read data, train
a model, deliver a target, score an outcome, or authorize a scientific claim.
Those are separate ethics, privacy, hardware, and Tier C decisions.

## Study Structure

The study has two sequential cohorts of 21 complete participants each. The
first cohort is discovery and may freeze the model and thresholds. The next 21
complete people form an untouched independent replication cohort. Enrollment
is capped at 22 per cohort, allowing at most one replacement solely for
withdrawal or a preregistered target-free hardware failure. Fewer than 21
complete people at that cap parks the cohort. No participant may move between
cohorts, be replaced because of performance, or be dropped because their data
hurt the result.

The participant is the unit of inference. At `n=21`, the 70% consistency gate
requires 15 positive participant margins and has one-sided exact sign-test
`p=0.039177`. The frozen claim still requires the stronger registered
effect-size threshold and exhaustive exact sign-flip test, with at most
`2^22 = 4,194,304` assignments. Discovery and replication must each pass
separately; pooling cannot rescue either failure. A planning proxy using an
assumed `0.06` nats/item mean margin and `0.07` between-person SD estimates
about 80% probability that both cohorts clear effect and consistency gates;
that assumption is not evidence and cannot replace exact inference.

## Task That Separates Prompt From Intention

The vocabulary is four immediately useful commands: `yes`, `no`, `help`, and
`stop`. Each participant completes at most 256 trials in 27.5 recorded minutes:

| Block | Trials | Scientific role |
|---|---:|---|
| Prompted intend | 64, 16 per command | Balanced positive control and prompted-communication endpoint |
| Prompted no-intent | 32 | Same class cue while deliberately remaining blank |
| Free-choice intend | 64 | Primary voluntary user-intention endpoint |
| Free-choice no-intent | 32 | Same private selection action while deliberately remaining blank |
| Rest | 32 | False activation, abstention, and endpoint control |
| Peripheral calibration | 32 | Eye and oral-muscle nuisance positive controls fitted on source participants only |

On a free-choice trial, an isolated controller presents a trial-randomized
button-to-command map. The participant chooses voluntarily, and the controller
immediately commits the target into an encrypted `TargetVault`. Neither the
target nor its key is available to the decoder, operator, prediction freezer,
or language context. After a randomized 6–10 second washout, the map disappears
and generic fixation begins. The continuously running decoder receives no
block or trial identity. Output during washout, no-intent, or rest counts as a
false activation. This makes the free choice verifiable without letting the
selection movement, screen position, or a post-prediction self-report define
the target.

## Synchronized Acquisition

The minimum sensor contract is 64 EEG, four EOG, four bilateral oral-EMG
channels, one photodiode display-onset channel, mono microphone, and a hardware
trigger. Biosignals are sampled at 512 Hz; audio is 16 kHz mono. EEG geometry,
exact auxiliary-channel roles, the
hardware clock, cross-stream clock mapping, and capture-to-presentation timing
must be preserved in BIDS 1.11.1-compatible records.

One common biosignal clock is preferred. Cross-stream synchronization must
still record source capture, host arrival, feature availability, first output,
stable commit, and presentation timestamps. Lab Streaming Layer can carry and
time-map multimodal streams, but a future hardware qualification must measure
this exact setup rather than borrow a latency number from another device.

Before human collection, the exact hardware must pass three 30-minute
cold-start bench replays on a wired acquisition network. A common pulse must
reach both the amplifier and acquisition host; beginning/end synchronization
bursts and the shared audio waveform must quantify drift. The photodiode must
verify visual onset. Each replay must preserve raw timestamps and correction
uncertainty with zero missing, duplicated, reordered, or silently interpolated
samples. The provisional gates are LSL clock-uncertainty p99 at or below 1 ms
and hardware residual p99 within two EEG samples (`3.90625 ms`). Actual CPU,
RSS, disk throughput, dropped frames, thermal behavior, amplifier filters,
channel capacity, and bytes must be measured. Any failure parks collection.

Raw EEG cannot be irreversibly cleaned before nuisance analysis. EOG, oral
EMG, microphone, posterior EEG, cue, and time remain separately available so a
candidate cannot get credit for eye, mouth, acoustic, visual, or schedule
information.

Pseudonymous BIDS records and protected voice are separate capabilities. Full
audio, consent, recruitment identity, and date mappings stay in a separately
encrypted protected root and are not public by default. Release-scoped hashes
or audio sharing require a separate consent, privacy, release, and Tier C
decision.

## Frozen Analysis

The model remains a source-scaled, forward-only spatial-temporal bandpower
producer plus multinomial L2 logistic regression and source-only probability
calibration. No participant-specific fit, test-time adaptation, larger model,
pretrained EEG encoder, or provider language model is eligible.

The primary replication estimand is the smaller participant-macro log-loss
gain of `P + residual central EEG` over:

1. all recorded peripheral/cue/timing context `P`; and
2. `P + class-destroyed residual central EEG`.

The minimum gain is `0.03` nats per item. It must be positive in at least 70%
of participants with exact one-sided sign-flip `p <= 0.05`, and balanced
accuracy must exceed the strongest frozen prior, cue, timing, posterior, or
peripheral control by at least `0.05`. The free-choice endpoint is primary;
prompted success cannot rescue its failure.

Required controls include equal and source priors, cue, timing, EOG, oral EMG,
microphone, all peripherals, central EEG, posterior EEG, residual central EEG,
class-destroyed residual EEG, prechoice/early EEG, null trials, language only,
neural plus language, and deranged-neural plus language.

## Causal And Live Evidence

The primary claim may not use a trial-boundary oracle. A source-only endpointer
must drive the already qualified `SourceChunk` and `LiveSession` contracts.
Offline/incremental parity, packet loss, gaps, reconnects, clock discontinuity,
abstention, and stable-commit behavior must pass generated qualification before
any human recording.

Replication first runs in shadow mode, with outputs hidden. Predictions and
targets freeze once. The same unchanged model, thresholds, vocabulary, prior,
and code then enter the live-display block. The report must include accuracy,
log loss, false and missed activations, abstention, coverage, dropped chunks,
first-output latency, stable-commit latency, and capture-to-presentation
latency. Accuracy alone cannot establish live decoding.
Stable-commit coverage must reach 60%, false commits must stay at or below 0.1
per inactive minute, at least 99% of frames must complete before their next
frame deadline, and every commit needs a valid mapped capture-to-presentation
latency.

## Storage Proof

For the maximum 44 enrolled people at the 27.5-minute hard stop:

```text
73 channels * 512 samples/s * 3 bytes * 1,650 s * 44 = 8,140,492,800 bytes
16,000 samples/s * 2 bytes * 1,650 s * 44       = 2,323,200,000 bytes
raw total                                         = 10,463,692,800 bytes
                                                  = 9.7451 GiB
```

The raw cap is 10 GiB, leaving 273,725,440 bytes of raw headroom. The complete
20 GiB permission is partitioned into 10 GiB raw, 6 GiB private derivatives,
2 GiB temporary output, 1 GiB aggregate public output, and 1 GiB unallocated
headroom. Full float32 raw copies and duplicate raw backups are forbidden
inside this budget; derivatives must be streamed or epoch-selective. A future
executor must park before recording if any cap fails or if reserving its output
would leave less than 20 GiB free disk.

## Claim Ceiling

If both cohorts and the live stage pass every frozen gate, the strongest
internal claim is: same-site, independently replicated, unseen-person, causal,
live four-command user-intention information with incremental EEG sensor value
beyond the recorded peripheral, cue, timing, posterior, and language-only
controls.

That would still not establish arbitrary thought reading, sentence decoding,
semantic reconstruction, a portable device, clinical utility, or external
reproduction. `E7` requires a separate external team or site using the frozen
toolkit and remains outside this same-site protocol.

## Next Reversible Engineering Gate

Build a generated-only qualification for the complete study grammar, channel
roles, participant firewall, free-choice report seal, storage monitor, causal
stream, prediction freezer, and scorer. It must include positive fixtures where
only EEG adds information and negative fixtures where only EOG, EMG,
microphone, cue, time, or language carries class information. That work remains
Tier B and has no scientific value by itself.

Engineering capability added: NeuroDecodeKit now has one byte-accounted,
falsifiable prospective protocol connecting synchronized acquisition,
peripheral attribution, unseen-person replication, and causal live operation.

Scientific claim not established: no participant was recruited and no device,
real EEG, target, model, score, or live neural operation occurred.

## Primary Sources

- [BIDS 1.11.1 entity table](https://bids-specification.readthedocs.io/en/stable/appendices/entity-table.html)
- [Lab Streaming Layer multimodal synchronization](https://pmc.ncbi.nlm.nih.gov/articles/PMC12434378/)
- [2025 online imagined-speech BCI study](https://www.nature.com/articles/s42003-025-07464-7)
- [Speech-production EMG artifact study](https://pubmed.ncbi.nlm.nih.gov/20480401/)
- [General EMG inference risk in EEG](https://pubmed.ncbi.nlm.nih.gov/19214730/)
