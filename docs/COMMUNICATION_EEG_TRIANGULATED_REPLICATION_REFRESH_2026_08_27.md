# Communication EEG Triangulated Replication Refresh

Date: 2026-08-27

Status: **Tier A public-source and design refresh only; zero dataset payload,
private path, signal, target, model, prediction, score, provider, stream, or
device operations**

Machine record:
`registries/communication_eeg_triangulated_replication_refresh.v0.json`

## What Changed

A newly public source materially improves the replication design. OpenNeuro
`ds007591-v1.0.1` now provides a stable CC0 release of a five-word overt,
minimally overt, and covert-speech experiment with 128 EEG channels plus
recorded EOG, upper/lower orbicularis-oris EMG, microphone, and trigger
channels. Its official NEMAR mirror reports three participants, six sessions,
and approximately 1.62 GB. The public analysis repository provides the BIDS
loader and identifies 139 total recorded channels.

This is a useful full-sensor **mechanistic bridge**, but it is not a
participant-level inferential replication. With three held-out participants,
an exact one-sided sign-flip test has only `2^3 = 8` assignments, so its
smallest attainable p-value is `1/8 = 0.125`. It therefore cannot satisfy the
already frozen `p <= 0.05` participant-consistency gate, even if all three
participants show a positive margin. The source is also too small for the
registered full-control minimum of ten complete participants.

The 24-participant around-ear EEG study is scientifically important, but its
paper states that the supporting data cannot be made publicly available due to
sensitive personal information. It is an external benchmark, not an
operational NeuroDecodeKit source. The separate OpenNeuro `ds007808-v1.0.0`
JapanEEG archive is public and includes covert speech, EEG, EMG/EOG, and audio,
but it has only three long-term participants and is approximately 1.575 TB.
It is ineligible under the current participant and 10 GiB selected-raw gates.

## Triangulated Evidence Design

No currently verified public cohort can independently establish every part of
the final claim. The strongest bounded route therefore uses two mandatory,
noninterchangeable evidence keys plus one nonrouting mechanistic bridge:

1. **Attribution key: `ds003626-v2.1.2`.** Ten participants, prompted inner
   speech, 128 EEG, four EOG, and two oral-EMG channels. This remains the
   full-control discovery cohort. It must beat nuisance-only, deranged-EEG,
   posterior, cue, timing, and no-signal controls in unseen participants.
2. **Nonrouting mechanistic bridge: `ds007591-v1.0.1`.** Three participants,
   five covert words, EEG plus EOG and oral EMG, different language, hardware,
   and research group. Covert speech is the sole primary condition;
   minimally overt and overt conditions are prespecified mechanistic contrasts.
   Every participant, comparator, microphone/display nuisance, calibration
   measure, and abstention measure must be reported. The bridge is descriptive
   because participant-level significance is mathematically unavailable at
   `n=3`, and it can neither pass nor rescue the router.
3. **Independent-transportability key: TESSCCo.** Twenty-four participants and
   five covert TV commands provide a better participant-level independent
   challenge. Because separate EOG and oral EMG are not verified, this key can
   test held-out-person prompted-command information beyond the available
   no-signal, cue, timing, posterior, derangement, and audio controls, not
   peripheral-adjusted neural attribution.

The two keys cannot rescue one another, and the bridge is never a third chance
to pass. A negative or failed discovery is
not repaired by a positive partial replication. A positive `ds007591` bridge
does not satisfy participant-level replication significance. A positive
TESSCCo result does not prove EEG information beyond unrecorded eye or mouth
activity.

## Maximum Claim If Both Keys Pass And The Bridge Is Concordant

The strongest allowed statement would be:

> Closed-set prompted-command information in scalp EEG recordings generalized
> to unseen participants across independently sourced datasets. In the ten-person
> discovery cohort, the candidate information exceeded the recorded eye,
> oral-muscle, cue, timing, posterior, derangement, and no-signal controls; a
> three-person full-sensor cohort was directionally concordant, and a separate
> 24-person cohort replicated held-out-person command information without full
> peripheral attribution.

Even that outcome would **not** establish independently replicated
EEG-beyond-eye-and-mouth attribution, spontaneous language, unrestricted
thought reading, sentence reconstruction, a live device result, or clinical
benefit. The final attribution claim still requires a separate complete cohort
with at least ten participants and synchronized raw EEG, EOG, and oral EMG.

## Routing And Freeze Rules

- Preserve `COMM-R0-REPLICATION-v0` unchanged. Its minimum cohort sizes,
  features, controls, model family, thresholds, target firewall, and one-score
  rule remain authoritative.
- Keep SilentSpeech-EEG as the leading full-control watchlist source. Promote
  it only after a stable dataset identity, license, complete manifest, loader,
  and exact channel roles are independently verified.
- Add `ds007591-v1.0.1` only as the full-sensor mechanistic bridge. It cannot
  enter the registered full-control router because `n=3 < 10`, and its
  historical online sessions do not establish a NeuroDecodeKit live result.
- Keep TESSCCo first in the registered partial-command route. Its exact source
  lock must become remotely green before discovery target delivery.
- Keep `ds007808-v1.0.0` out of acquisition planning under the current 10 GiB
  selected-raw and participant-count gates.
- Freeze source identities, participants, files, sensors, events, class IDs,
  and claim ceilings before any discovery score. Discovery outcomes may not
  choose a source, subset, threshold, or model capacity.

## Immediate Needle-Moving Sequence

1. Close or park the sole active Dreyer Tier C gate through its existing exact
   decision path; this refresh does not activate it.
2. Execute the already queued `COMM-L0-META` source-identity sequence only
   after a separate exact Tier C decision becomes remotely green.
3. Freeze exact target-free source locks for `ds003626`, `ds007591`, and
   TESSCCo, including byte manifests and claim ceilings, before any target
   delivery.
4. Build one additive generated source-adapter qualification for the two new
   BIDS surfaces without rerunning consumed `COMM-R0-G`, `COMM-G1`, or
   `COMM-G2` lanes.
5. Run the discovery prediction freeze and score once; only then execute every
   independently frozen bridge and partial replication, reporting all results.
6. Advance to a prospective actual-device test only after offline attribution
   and replication evidence passes.

## Resource And Authority Boundary

- one CPU thread, one worker, and one numerical job by default;
- 20 GiB total incremental research storage;
- 10 GiB maximum selected raw data for the communication lane;
- zero payload requests or bytes in this refresh;
- zero private or Git-ignored path reads;
- zero signal, event, target, label, model, prediction, score, provider,
  stream, device, cleanup, deletion, release, or claim operations;
- no write outside NeuroDecodeKit; and
- no change to sole active Tier C packet `DREYER-C5R-1-HL`, whose authority
  flags remain false.

Engineering capability added: the replication plan now separates full-control
attribution, full-sensor mechanistic concordance, and adequately sized
independent command generalization instead of asking one unavailable public
cohort to prove all three.

Scientific claim not established: this refresh accessed no neural payload and
did not demonstrate communication decoding, EEG information beyond peripheral
signals, unseen-person generalization, independent replication, causal live
decoding, or clinical value.

## Primary Sources

- [OpenNeuro `ds007591-v1.0.1` DOI](https://doi.org/10.18112/openneuro.ds007591.v1.0.1)
- [NEMAR `on007591-v1.0.0`](https://nemar.org/dataset/on007591)
- [`ds007591` public analysis repository](https://github.com/arayabrain/uhd-gmail-public)
- [JapanEEG official data specification](https://japaneeg.araya.org/data/)
- [OpenNeuro `ds007808-v1.0.0` DOI](https://doi.org/10.18112/openneuro.ds007808.v1.0.0)
- [NEMAR `on007808-v1.0.0`](https://nemar.org/dataset/on007808)
- [Around-ear EEG study](https://doi.org/10.1088/1741-2552/ae54d0)
- [Thinking Out Loud descriptor](https://www.nature.com/articles/s41597-022-01147-2)
- [TESSCCo descriptor](https://www.nature.com/articles/s41597-026-07745-8)
- [SilentSpeech-EEG repository](https://github.com/Jacoo-Zhao/BrainStack)
