# Kara One Communication EEG Source Readiness

Date: 2026-08-27

Status: **Tier A public-source readiness research only; route parked under the
frozen 10 GiB source lock; zero dataset payload or scientific claim operation**

Machine record:
`registries/communication_eeg_kara_one_source_readiness.v0.json`

## Why This Check Matters

`COMM-R0-REPLICATION-v0` requires the public replication router to evaluate
TESSCCo and then Kara One when the full-control SilentSpeech-EEG route is not
operationally qualified. Every partial route must retain all target-free
eligible participants, preserve its required sensors and classes, fit within
10 GiB of selected raw input, and park rather than drop participants when its
distribution is over-cap or unsplittable.

TESSCCo is already blocked at source identity. This pass therefore checks the
only remaining public partial route without requesting an archive or changing
the frozen selection rules.

## Verified Public Surface

The University of Toronto dataset page reports:

- 14 participant archives, one `.tar.bz2` archive per participant;
- approximately 24 GB across those archives;
- academic non-profit use only, with citation required;
- a 64-channel Neuroscan Quick-cap using the 10-20 system;
- four ocular electrodes, 1 kHz acquisition, Kinect facial animation units,
  and audio;
- seven phonemic or syllabic prompts and four words; and
- continuous CNT EEG, `epoch_inds.mat`, prompt-order files, and Kinect
  companion files inside the participant bundles.

The associated ICASSP paper reports 12 recruited participants and says data
from four were discarded, leaving eight in its analysis. That differs from the
14 public participant archives. No archive was opened to adjudicate that
release-versus-paper discrepancy, and no participant was declared eligible or
ineligible from performance or target information.

The page verifies recorded eye and face information but does not establish a
separate oral-EMG channel. The CNT note says a channel named `EMG` contains
colour-sensor information, so it must not be relabeled as oral EMG.

## Frozen Readiness Decision

Kara One does not qualify for the registered partial route under the currently
exposed public source surface:

1. the public release is approximately 24 GB, above the exact 10 GiB selected-
   raw cap;
2. the source page exposes one compressed archive per participant and no
   remotely selectable per-member manifest, so no smaller complete common
   inventory can currently be verified;
3. the contract forbids dropping participants to fit the cap;
4. per-archive bytes and checksums, an immutable release revision, and a common
   complete sensor/class inventory are not published on the page; and
5. the 14-archive release and eight-participant analyzed cohort leave the exact
   target-free eligibility set unresolved.

This is a design-bound park, not a negative scientific result or a claim that a
smaller valid source slice can never exist. A future official member-level
manifest could qualify the route if it proves a complete all-eligible-
participant EEG plus eye/face inventory at or below 10 GiB before discovery
target delivery. Otherwise reconsideration requires a prospectively frozen
contract change. The current result cannot be rescued by downloading a
convenient subset of participants.

## Router Consequence

- SilentSpeech-EEG remains an operationally unqualified full-control watchlist
  source.
- TESSCCo remains blocked at source identity.
- Kara One is parked by the frozen storage, completeness, and source-lock
  rules.
- No public partial replication route currently qualifies.
- The registered prospective fallback remains a separately approved cohort
  with synchronized raw EEG, EOG, and bilateral oral EMG.
- `ds007591-v1.0.1` remains a three-person nonrouting mechanistic bridge and
  cannot rescue the missing replication cohort.

No acquisition packet is created. `DREYER-C5R-1-HL` remains the sole active
Tier C packet and every authority flag remains false.

## Measured Research Operation

- one public University of Toronto dataset-page retrieval;
- one public associated-paper retrieval;
- zero participant-archive, per-member metadata, or payload requests;
- zero dataset payload bytes or local dataset files;
- zero private paths, neural headers, signals, events, targets, labels, models,
  predictions, scores, providers, streams, devices, releases, or claim
  upgrades; and
- zero cleanup, deletion, overwrite, or write outside NeuroDecodeKit.

Transport response bytes and crawler-internal request counts are unavailable
and are not fabricated.

## Next Gate

Do not prepare a Kara One acquisition packet under the current contract. The
next scientific route is either a newly reachable independently frozen public
source that passes the existing gates, or the separately governed prospective
synchronized-sensor fallback. Any change to the 10 GiB cap, all-participant
rule, sensor requirements, or source router must be prospective, explicit,
committed, pushed, and remotely green before discovery target delivery.

Engineering capability added: the independent replication router now reaches
an explicit, reproducible no-public-route decision instead of silently
subsetting an over-cap cohort.

Scientific claim not established: no Kara One neural payload was accessed, so
this work did not test communication decoding, EEG beyond peripheral signals,
unseen-person generalization, independent replication, causal live decoding,
hardware performance, or clinical value.

## Primary Sources

- [Kara One official dataset page](https://www.cs.toronto.edu/~complingweb/data/karaOne/karaOne.html)
- [Zhao and Rudzicz, ICASSP 2015](https://www.cs.toronto.edu/~complingweb/data/karaOne/ZhaoRudzicz15.pdf)
