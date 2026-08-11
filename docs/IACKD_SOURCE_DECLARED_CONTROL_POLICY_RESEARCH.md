# IACKD Source-Declared Control Policy Research

Date: 2026-08-10

Status: **Tier A artifact-only prospective repair complete; no source body,
local bundle, signal, event, target, model, or score access**

Lane: **IACKD-H3 Source Semantics Policy**

Registry:
`registries/iackd_source_declared_control_policy_research.v0.json`

## Research Question

How should a future IACKD reader preserve BIDS source declarations while also
assigning functional analysis roles, without repeating H2's mistake of
rewriting source type counts from channel names?

This is a new prospective engineering lane. It does not amend or rerun the
consumed H2 router, and it does not approve H2's inadmissible candidate hash.

## Evidence Boundary

The only dataset-specific input is the committed aggregate H2 result at commit
`580f11fc60d2882a11bf4e765bb33b60ffc0bd04`, which passed Base Python job
`93636960404` and Optional Neuro Readers job `93636960360` in CI
`31444931063`. No Git-ignored H2 output was read for this research record.

H2 established one 26-channel `EEG` core, optional M1/M2 rows, three controls
source-typed `MISC`, average reference, 1024 Hz sampling, and complete central
and occipital geometry in all 30 groups. It also established that H2's EOG
compatibility and name-based trigger-count transformation were wrong for this
source.

The dataset pins BIDS `1.7.0`. That specification defines `name`, `type`, and
`units` as required channel fields, allows distinct `MISC`, `HEOG`, `VEOG`, and
`TRIG` types, and defines `MiscChannelCount` as the number of miscellaneous
auxiliary channels. The current BIDS `1.11.1` keeps those distinct channel
types but uses `MISCChannelCount`. A source adapter must therefore bind the
dataset's declared BIDS version instead of silently applying a newer field
spelling or inferring semantic type from a familiar channel name.

Primary sources:

- [BIDS 1.7 EEG specification](https://bids-specification.readthedocs.io/en/v1.7.0/04-modality-specific-files/03-electroencephalography.html)
- [BIDS 1.11.1 EEG specification](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html)
- [IACKD data descriptor](https://doi.org/10.1038/s41597-026-07146-x)
- [OpenNeuro ds006840 v1.0.0](https://openneuro.org/datasets/ds006840/versions/1.0.0)

## Three-Layer Sensor Semantics

The future reader should never overload one field with three meanings:

| Layer | Question | Authority |
|---|---|---|
| Source type | What type did this BIDS release declare? | Exact channel-table `type` under the pinned BIDS version |
| Functional role | How will NeuroDecodeKit treat the named channel? | A separately versioned, prospective policy |
| Model inclusion | Can this channel enter a particular feature matrix? | The frozen experiment view and target firewall |

Source count reconciliation happens **before** functional-role assignment. A
channel declared `MISC` always contributes to the source MISC count, even when
its exact name later gives it an ocular-control or trigger-control role.

## Candidate `SourceSemanticsPolicy-v0`

Names are NFC-normalized, stripped, and case-folded for matching while their
source display spelling and source order remain preserved.

| Source declaration | Functional role | Predictive | Geometry requirement |
|---|---|:---:|---|
| Exact 26-name core with type `EEG` | `predictive_eeg` | yes | finite coordinate required |
| M1 or M2 with type `EEG` | `optional_reference_eeg` | no | finite if present; absence allowed |
| HEOG or VEOG with type `MISC` | `ocular_control` | no | unavailable allowed |
| Trigger with type `MISC` | `trigger_control` | no | unavailable allowed |
| Anything else | refusal | no | no inference |

The 26 predictive names are the fixed H2 aggregate core:

```text
Fp1 Fp2 F7 F3 Fz F4 F8 FC3 FCz FC4 T7 C3 Cz C4 T8
CP3 CPz CP4 P7 P3 Pz P4 P8 O1 Oz O2
```

The policy preserves the two source count groups exactly:

| Occurrences | Source EEG | Source MISC | Total rows | Optional M1/M2 |
|---:|---:|---:|---:|:---:|
| 96 | 26 | 3 | 29 | no |
| 32 | 28 | 3 | 31 | yes |

No functional role changes those source counts. In particular, a channel named
Trigger but declared `MISC` remains in `MiscChannelCount` for BIDS 1.7 source
reconciliation while also receiving the nonpredictive functional role
`trigger_control`.

## Geometry And Reference Contract

- The predictive set is exactly 26 channels in every run.
- C3/C4/Cz and O1/Oz/O2 remain fixed regional views within that set.
- All 26 predictive channels require finite CapTrak coordinates in meters.
- M1/M2 are optional, nonpredictive, and may add two finite coordinates.
- HEOG, VEOG, and Trigger may have unavailable coordinates.
- The common source reference must remain exactly `average`.
- A future derivative binds the source order, source-type counts, functional
  roles, model-inclusion mask, geometry mask, reference, sampling, policy
  version, and policy hash separately.

## Why This Is Not Post-Outcome Tuning

The repair uses only aggregate metadata and the published standard. No signal,
event, trial, action label, target, model prediction, or score influenced it.
It is still post-H2 engineering diagnosis, so it cannot retroactively turn H2
into an R4 pass. Its legitimate use is prospective: freeze a new policy and
qualify it on generated fixtures before any future signal-bearing IACKD stage.

## Next Bounded Qualification

A Tier B generated-fixture implementation may now validate:

1. exact BIDS-version binding and version-specific count-field spelling;
2. source-type counts before functional mapping;
3. one 26-channel predictive core across 29-row and 31-row signatures;
4. optional M1/M2 handling without changing the predictive matrix;
5. nonpredictive MISC controls with no geometry requirement;
6. exact reference, sampling, source-order, role, and geometry hashes;
7. refusals for unknown names, wrong types, count drift, role overlap,
   nonfinite predictive geometry, or source-order mutation; and
8. zero network, local-data, signal, target, model, and score counters.

That qualification should remain standard-library, use one thread and worker,
finish within 30 seconds and 256 MiB RSS, and retain less than 2 MiB. It cannot
authorize a real reader or IACKD-2.

## Scientific Boundary

Engineering capability proposed: a version-aware sensor policy can preserve
source BIDS truth while assigning separate functional and model-inclusion
roles, removing the exact taxonomy error that stopped H2.

Scientific claim not established: this artifact-only policy research accessed
no EEG signal, event, trajectory, target, model, prediction, or score and
therefore establishes no neural effect, action decoding, brain-specific
origin, generalization, typing, language or thought decoding, real-time
operation, hardware capability, assistive benefit, or clinical use.
