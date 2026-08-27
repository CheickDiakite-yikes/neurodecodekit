# Communication EEG Scientific Claim Program

Status: Tier A research decision; zero dataset-payload, private-path, model,
target, provider, stream, or device operations

Date: 2026-08-26

Machine record:
`registries/communication_eeg_scientific_claim_program.v0.json`

## End Goal

Demonstrate independently replicated, unseen-person, causal, live decoding of
user-intended communication where EEG adds measurable information beyond every
recorded peripheral and language-only control. Release the code, frozen
contracts, aggregate evidence, and limitations needed for an outside group to
repeat the result.

This is deliberately harder than producing a flattering accuracy. A prompted
command is not unrestricted thought reading. A replay is not live. A held-out
trial from a familiar person is not unseen-person generalization. A model that
beats chance but not eyes, mouth activity, timing, or the prompt prior has not
shown that EEG added useful information.

## What Would Count

The evidence ladder has four cumulative levels:

1. **Controlled communication information.** On prompted inner-speech commands,
   a frozen EEG-augmented model improves participant-macro held-out log loss
   over the strongest recorded peripheral, timing, cue, and no-signal model and
   over the same model with participant-matched deranged EEG.
2. **Unseen-person generalization.** Each outer fold uses zero signal, target,
   calibration, threshold-selection, or adaptation rows from its held-out
   person.
3. **Independent replication.** The same directional hypothesis passes on a
   separately sourced cohort under its own prediction freeze and one score. A
   weaker control set can provide partial replication but cannot silently
   upgrade the full peripheral-adjusted claim.
4. **Causal live decoding.** A frozen decoder processes an actual device stream
   without a known event-onset or trial-end oracle, records capture-to-output
   latency, handles dropout and reconnects, and abstains when signal quality or
   confidence is inadequate.

The final language comparison must include language-only, neural-only,
neural-plus-language, and item-deranged-neural-plus-language arms with matched
prompt context. No held-out intended text may reach a model before prediction
freeze.

## Source Decision

### Discovery: OpenNeuro `ds003626`

This is the best verified first communication cohort. The primary paper
reports ten native Spanish participants, three sessions, randomized trials,
four directional commands, 128 EEG channels, four eye channels, two
orbicularis-oris mouth channels, and inner-speech, pronounced-speech, and
visualized-direction conditions.

That supports participant-held-out comparisons among no signal, cue/time,
EOG, oral EMG, all recorded nuisance signals, nuisance plus central/temporal
EEG, nuisance plus matched deranged EEG, posterior-only EEG, and visualized-
direction controls. The maximum first claim is prompted four-command
inner-speech information beyond recorded controls, not sentence decoding,
spontaneous communication, semantic reconstruction, or arbitrary thought.

### Replication candidates

No second source is yet verified as a full replacement for `ds003626`'s
simultaneous eye and mouth controls.

- **Kara One** is the leading partial candidate: 14 participants, 64 EEG,
  four ocular electrodes, and Kinect facial tracking. Oral EMG is not verified
  and its academic/nonprofit terms need separate review.
- **SilentSpeech-EEG** is a high-value watchlist source: its 2026 paper reports
  10 usable participants, 24 words, 16 sessions, 128 EEG plus eight external
  channels, and 60,000 trials. Public payload identity, access terms, and exact
  external-channel roles still need verification. Its primary reported split
  is within-person and its accuracy is associated with occipital contribution;
  neither fact proves unseen-person EEG-specific decoding.
- **TESSCCo** has 24 participants and five bilingual TV commands, but the
  primary description did not verify EOG or oral EMG. Payload, license, cue,
  and peripheral roles remain open questions.
- **Directional Word 2026** has 22 participants and EMG in only six. Fixed word
  blocks, right-hand marker presses, protocol variants, and partial EMG make it
  unsuitable for the first replication claim.

If no public cohort satisfies the replication contract, the honest fallback is
a small prospective recording with synchronized EEG, EOG, and bilateral oral
EMG, consented participants, randomized prompts, preregistered exclusions, and
an untouched final cohort. That requires separate ethics, privacy, hardware,
and Tier C decisions.

## Frozen Program Sequence

### Phase 0: protect the current evidence gate

1. Keep `DREYER-C5R-1-HL` as the sole active Tier C packet.
2. Complete H-L1 and the one-file H-L2 header preflight only after the exact
   maintainer decision and remote-proof barriers.
3. If H1 permits continuation, complete Dreyer A -> Q -> P -> T once. This is a
   motor/peripheral-attribution precursor, not a communication claim.

### Phase 1: qualify communication without payload

4. Freeze an exact `ds003626` snapshot, file manifest, license, immutable
   validators, channel roles, event grammar, participant/session grid, and the
   smallest complete fit/evaluation slice under the 10 GiB cap.
5. Keep raw EEG and separately recorded peripheral channels available for
   matched controls; processed EEG that removed EXG-correlated components
   cannot be the sole attribution input.
6. Freeze participant-level outer folds and one compact model family before
   any protected target is opened.

### Phase 2: generated qualification

7. Generate BDF/BIDS-like fixtures with EEG, EOG, EMG, cue, time, labels, gaps,
   malformed roles, and adversarial participant identities.
8. Prove the reader, causal preprocessing, fold capabilities, nuisance
   residualizer, derangement, model schedule, freezer, scorer, resource
   monitors, and no-clobber output using generated data only.
9. Require positive controls where EEG adds information and negatives where
   only EOG, EMG, cue, or time carries class information.

### Phase 3: one discovery execution

10. Acquire only registered files and create target-firewalled derivatives
    under one thread, one worker, one numerical job, and at most 10 GiB.
11. Fit only source-participant models and commit aggregate prediction hashes
    before held-out target delivery.
12. Score once against every frozen control. Require aggregate improvement and
    participant consistency; report calibration, coverage, abstention, and all
    failures without post-target tuning.

### Phase 4: independent replication

13. Qualify a separate cohort without using the discovery score to select its
    people, preprocessing, thresholds, or model family.
14. Freeze a separate target firewall and the same directional hypothesis.
15. Run one prediction freeze and one score, stating whether it is full
    peripheral-adjusted or only partial eye, face, cue, or no-signal
    replication.

### Phase 5: causal stream engineering

16. Implement the existing `SourceChunk` contract with generated packet loss,
    duplication, reordering, clock discontinuity, disconnect, and reconnect
    qualification. Add explicit gaps, stream generations, invalid-output masks,
    and bounded recovery.
17. Add a bounded `LiveSession`: source -> causal preprocessing -> persistent
    model state -> decoder -> quality/confidence abstention -> stable commit.
18. Prove exact offline/incremental parity across arbitrary chunking and
    actual-time replay. Record capture, host-arrival, preprocessing, model,
    first-output, stable-commit, and presentation clocks separately.
19. Replace known trial ends with a source-only onset/endpointer and report
    false/missed activations, coverage, first-output time, stable-commit time,
    and abstention delay.

### Phase 6: prospective live evidence

20. After offline discovery and independent replication pass, preregister one
    actual-device, consented, completely unseen-person run. Freeze the model,
    thresholds, vocabulary, command prior, language context, and stop rules
    before recording. Score once under real stream pacing and publish aggregate
    evidence plus the exact hardware/software receipt.

## Architecture Policy

Start with source-scaled regularized linear and compact spatial-temporal
families because their controls and failure modes are inspectable. A larger
model, pretrained EEG encoder, or functionally routed expert model becomes
eligible only after the compact family fails for a measured representation
reason on generated or training-only diagnostics.

Reusable pieces already include forward-only causal preprocessing, bounded
temporal token streaming, incremental CTC, participant firewalls, derangement,
cache provenance, and freeze/scorer patterns. Missing pieces are a real source
adapter, dropout recovery, persistent model state, neural abstention,
source-only endpointing, and true capture-to-output clocks.

An LLM is downstream, not the neural decoder. It may consume frozen neural
probabilities only after prediction freeze and only when language-only and
deranged-neural controls can measure its incremental contribution.

## Resource And Authority Boundary

- one CPU thread, one worker, and one numerical job by default;
- at most 10 GiB incremental research payload and one real-data lane;
- no payload download, private read, or protected target in this Tier A step;
- no provider call before neural prediction freeze;
- no device, human recording, release, or claim upgrade without its Tier C
  decision;
- no operation outside declared NeuroDecodeKit roots; and
- no cleanup or deletion of unrelated files or projects.

This record adds a falsifiable path. It does not establish inner-speech
decoding, EEG beyond eyes or mouth, unseen-person generalization, independent
replication, live decoding, portable hardware performance, unrestricted
thought reading, or clinical value.

## Primary Sources

- [Thinking Out Loud descriptor](https://www.nature.com/articles/s41597-022-01147-2)
- [OpenNeuro `ds003626`](https://openneuro.org/datasets/ds003626/versions/2.1.2)
- [NEMAR `on003626`](https://nemar.org/dataset/on003626)
- [Kara One](https://www.cs.toronto.edu/~complingweb/data/karaOne/karaOne.html)
- [BrainStack / SilentSpeech-EEG](https://arxiv.org/abs/2601.21148)
- [TESSCCo](https://www.nature.com/articles/s41597-026-07745-8)
- [Directional Word](https://www.nature.com/articles/s41597-026-07809-9)
