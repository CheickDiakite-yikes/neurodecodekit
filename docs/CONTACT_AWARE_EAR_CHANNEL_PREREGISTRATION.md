# Contact-Aware Ear-Channel Adapter Preregistration

Status: **Tier B synthetic-only contract frozen; implementation and execution
not started**

Date: 2026-08-08

Machine contract:
`registries/contact_aware_ear_channel_contract.v0.json`

## Question

Can NeuroDecodeKit represent changing contact quality, noisy channels, and
missing samples in an ear-centered interface without inventing measurements,
silently changing the reference, losing source identities, or allowing target
or future information to choose channels?

This work order is a synthetic post-acquisition adapter only. It does not
control electrodes, read hardware, fit a predictor, select a scientific model,
or score an outcome.

## Primary-Source Boundary

Apple application
[`US20230225659A1`](https://patents.google.com/patent/US20230225659A1/en)
describes ear-worn active and reference electrode subsets and selection using
criteria such as impedance and noise. It is a pending application, not an
open-source implementation, a freedom-to-operate opinion, evidence that current
AirPods expose EEG, or a thought-to-text result.

[OpenBCI's cEEGrid documentation](https://docs.openbci.com/ThirdParty/cEEGrid_Kit/)
provides a concrete 16-channel around-the-ear research surface. The original
[cEEGrid paper](https://doi.org/10.3389/fnhum.2017.00163) emphasizes that
ear-centered sensors can observe both brain and non-brain sources. The open
[OpenBCI-cEEGrid adapter paper](https://doi.org/10.1016/j.ohx.2022.e00357)
also makes impedance and mechanical artifacts relevant engineering concerns.
None of these sources establishes typing transfer, brain-specific origin, or a
portable decoder.

This contract therefore uses our own generic post-acquisition representation.
It does not copy a device layout, switching algorithm, or active/reference
topology.

## Frozen Synthetic Fixture

Seed `5505` defines 48 target-free items with 16 generic source channels, eight
per synthetic side, sampled at 128 Hz for 256 strictly pre-event samples from
`-2.0` seconds to `0.0` seconds exclusive. Eight scenarios contain six items
each:

1. all contacts observed;
2. partial left contact loss;
3. partial right contact loss;
4. sparse bilateral contact;
5. unavailable contact quality;
6. line-noise contamination;
7. common-mode motion contamination; and
8. mixed dropout, noise, and contact degradation.

Channel names follow `ear-L00` through `ear-L07` and `ear-R00` through
`ear-R07`. Side and ring index are synthetic nominal identities, not measured
coordinates or anatomy. No participant, device, session, trial, target, text,
or class identity is created.

## Mask Semantics

The implementation must keep these concepts separate:

- `observed_mask`: finite samples that were actually generated as observed;
- `channel_present_mask`: whether the source channel exists for an item;
- `contact_score_valid_mask`: whether the normalized synthetic contact proxy is
  available;
- `eligible_mask`: whether the fixed target-blind policy permits a channel;
- `selected_mask`: which eligible channels receive nonzero adapter weight; and
- `adapted_observed_mask`: observed samples on selected channels only.

Missing values may be encoded as zero in the adapted transport array, but the
mask must remain false. Zero is never relabeled as a measured sample,
interpolation, or reconstructed EEG. The source signal, source order, channel
names, and source reference state remain unchanged and inspectable.

`contact_score` is a dimensionless synthetic quality proxy in `[0,1]`. It is
not impedance. No value in ohms may be invented when impedance was not
measured.

## Fixed Selection Rule

The rule has no learned parameter and sees no target or outcome. A channel is
eligible only when it is present, its contact score is valid and at least
`0.6`, its synthetic noise score is at most `0.4`, and at least `95%` of its
pre-event samples are observed.

Eligible channels are ranked independently on each side by
`0.6 * contact_score + 0.4 * (1 - noise_score)`, with ascending source index as
the exact tie break. At most four channels and at least two channels per side
are required. If either side has fewer than two eligible channels, the adapter
selects none and emits `insufficient_bilateral_contact`.

For a passing item, nonnegative weights sum to `0.5` on the left and `0.5` on
the right. Every unselected weight is zero. This gives missingness a stable,
visible representation without silently letting the side with more surviving
contacts dominate.

The policy acts on already acquired differential channels. It does not select
physical active/reference electrodes, rereference, interpolate, or control a
switching circuit.

## Refusal Matrix

The future validator must reject all sixteen registered mutations:

1. duplicate or missing channel identity;
2. unknown or mismatched side;
3. payload/sidecar source-order drift;
4. nonfinite sample marked observed;
5. absent channel marked selected;
6. invalid or unknown contact marked selected;
7. over-threshold noise marked selected;
8. emitted selection without the bilateral minimum;
9. more than four selected channels on either side;
10. nonzero weight outside the selected mask;
11. incorrect left or right weight total;
12. zero-filled missing value marked measured;
13. invented impedance or contact provenance;
14. measured-geometry claim from synthetic nominal fields;
15. forbidden target, identity, or outcome field; and
16. post-event or right-context dependency.

The implementation must also test deterministic replay, strict hashes, unknown
fields, malformed payloads, output caps, collision refusal, and future-tail
prefix invariance.

## Resource And Evidence Boundary

- Lazy NumPy only through the existing `[array]` extra; no new dependency.
- One CPU thread and one worker.
- At most 60 seconds, 256 MiB peak RSS, 4 MiB generated output, and two files.
- At least 1 GiB free disk before generation; both files are removed after the
  one measured closeout.
- No real/public/protected data, target, label, model, feature extraction,
  parameter update, inference, training, score, network, provider, stream,
  device, or hardware operation.

Implementation may begin only after this exact contract is committed, pushed,
and remotely green. One measured synthetic create/inspect roundtrip may occur
only after the exact implementation is also remotely green.

Seven focused contract tests pass. The complete pre-implementation suite passes
1,286 tests with 3 expected skips and 469 subtests in 34.24 seconds wall time at
621,395,968-byte peak RSS. That RSS belongs to the whole repository suite and is
not judged against the future single-fixture 256 MiB cap.

Engineering capability if all gates pass: NeuroDecodeKit can preserve and
validate contact quality, missingness, bilateral selection, and mask semantics
for a bounded synthetic ear-channel interface.

Scientific claim not established even if all gates pass: no real ear EEG
hardware signal, brain origin, decoding accuracy, generalization, latency,
home-use, or clinical result is established.
