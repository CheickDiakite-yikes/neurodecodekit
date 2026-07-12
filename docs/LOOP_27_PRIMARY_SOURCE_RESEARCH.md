# Loop 27 Primary-Source Research And Holdout Selection Note

Date: 2026-07-12

Status: **Planning research complete; no preregistration, acquisition, or
content access is authorized**

Machine boundary: `registries/loop27_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 27

## Decision Summary

The metadata-only selector recommends **SpanishBCBL MEG S25 session 2 block
2** as the smallest clean candidate for a future unseen-canonical-person,
same-modality, same-task, final-only transfer test:

```text
MEG/FIF/25_12032/240530/block2.fif       1,009,713,753 bytes
MEG/logs/S25-session2_block2_list1.mat         226,230 bytes
                                               ---------
exact bundle                               1,009,939,983 bytes
1 GiB cap                                  1,073,741,824 bytes
cap margin                                    63,801,841 bytes
```

This is a candidate selection, not a download plan ready for authorization.
Loop 25 has no mechanics result, Loop 26 has no frozen source model or control
package, exact S25 channels and trials are unopened, and no Loop 28 decision
rule exists. Loop 27 remains `Not Started` as an experiment and has no
preregistration or authorization sentence.

## Measured Research Boundary

```text
official MEG metadata entries:            315
strict single-FIF plus log pairs:           23
eligible pairs after exclusions:            16
measured selector wall time:              3.10 sec
measured selector peak RSS:         63,766,528 bytes
CPU threads / workers:                     1 / 1

remote signal or MAT payload downloads:       0
candidate FIF header reads:                    0
candidate signal reads:                        0
candidate MAT content reads:                   0
candidate target/label/text reads:             0
source consumed-evidence reads:                0
model or checkpoint runs:                      0
training or parameter updates:                 0
RW3, stream, board, device operations:          0
```

The selector used pinned Hugging Face repository metadata only. The official
`HfApi` returns file paths, byte sizes, Git blob IDs, LFS SHA-256 identities,
Xet hashes, and last-commit metadata without downloading the file payloads.

## Why A New MEG Person, Not Merely New Data

The current source model contract uses 102 magnetometers from S21. A fresh EEG
recording can move the EEG practice track, but it cannot test transfer of that
MEG sensor model. This separates three properties that are easy to blur:

| Property | S25 candidate | S20 EEG packet |
|---|---|---|
| Fresh participant relative to S21 | Yes, provisionally | Yes |
| Same prompted typing task | Yes | Yes |
| Same modality and nominal MEG sensor system | Yes | No |
| Eligible for future S21-MEG transfer claim | Candidate | No |
| Authorized now | No | No |

The existing S20 packet remains the independent RW4 EEG question. It is not a
backup or substitute for Loop 27.

## Official Cohort And Identity Boundary

The canonical SpanishBCBL card states:

- 35 healthy Spanish-speaking skilled typists performed read, wait, then type
  trials without visual feedback;
- each session used 128 unique Spanish sentences;
- MEG used a 306-channel Megin/Elekta Neuromag system at 1 kHz, comprising 102
  magnetometers and 204 planar gradiometers;
- S1/S18, S4/S14, and S5/S10/S21 are repeated-ID groups for the same people;
- S23 is excluded from the 19-person MEG cohort because of a metallic implant;
- the public release is CC BY-NC 4.0.

S25 is not in a published alias group and is not S7, S21, or an S21 alias. It
is therefore a candidate unseen canonical person relative to the observed S21
source cohort. That identity conclusion does not prove channel compatibility,
target freshness, or transfer performance.

Primary sources:

- dataset card and license:
  https://huggingface.co/datasets/bcbl190626/SpanishBCBL
- immutable dataset revision:
  https://huggingface.co/datasets/bcbl190626/SpanishBCBL/tree/88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
- official loader:
  https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/studies/spanishbcbl.py
- Brain2Qwerty v1 paper:
  https://www.nature.com/articles/s41593-026-02303-2
- Hub metadata API:
  https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api

## Candidate Ranking

The strict selector required one primary FIF with no split-continuation file,
one matching subject/session/block MAT log, prompted-typing MEG, standard block
naming, and no tapping/localizer or failed recording. It canonicalized
published aliases, excluded the observed S5/S10/S21 person, excluded consumed
S7, and applied the official S23 exclusion before ranking exact bytes.

| Candidate | Exact bytes | Decision | Reason |
|---|---:|---|---|
| S21 session 1 block 2 | 621,786,920 | Ineligible | Already observed source person and recording |
| S23 session 2 block 2 | 958,422,728 | Ineligible | Official metallic-implant exclusion |
| **S25 session 2 block 2** | **1,009,939,983** | **Selected** | Smallest eligible strict pair; no published alias |
| S18 session 2 block 2 | 1,018,878,168 | Not selected | Larger and carries S1/S18 alias bookkeeping |
| S24 session 2 block 2 | 1,048,579,727 | Not selected | Larger |
| S22 session 1 block 1 | 1,107,866,218 | Not selected | Larger and above 1 GiB |

S23 is a useful illustration of why byte rank cannot make the decision by
itself: it is smaller than S25 but scientifically ineligible under the public
cohort definition.

No backup can be substituted automatically. If S25 fails a future pre-open
gate, the correct outcome is a measured park or a new amendment before any
other candidate opens.

## Exact Selected File Identities

### Raw MEG

```text
path:
MEG/FIF/25_12032/240530/block2.fif

bytes:
1,009,713,753

Git blob:
59e7d2f7b0bc57aa6b10c729475fcfe241a1ed43

LFS SHA-256:
ef6b36fbf3efbfc86580cf68f45edf5254f2e134083a77e1fd88b22084f654be

Xet hash:
d7e3d6f06f01efdc25cac231d1ee07c93a208420187c148b9b2bd4ab09fe2185
```

### Protected Behavioral Log

```text
path:
MEG/logs/S25-session2_block2_list1.mat

bytes:
226,230

Git blob:
7dcb9236aad504ee65f8e43268d30d77bd12bfb8

LFS SHA-256:
470888435ddf8ab3a7fc50ab568d015e260aff908b08cb58aeb7aabe1da97557

Xet hash:
bb16d4ee60c453f2e1d6c9edac6cbe8dfbc7010e2df1081e2f33cd21739d8cf3
```

The MAT file is already present locally at the expected byte size from earlier
metadata work. This pass did not hash or open its payload. A future reuse
decision must separately authorize a payload hash and fail closed on mismatch;
local presence is not provenance proof.

The raw FIF is absent locally. No remote payload was downloaded.

## What Is Still Unknown

Metadata compatibility is necessary and insufficient:

| Field | Current status | Future gate |
|---|---|---|
| Exact channel names/order | Unavailable | Separately authorized header-only audit |
| Geometry compatibility | Unavailable | Header-only audit, no signal samples |
| Recording duration and valid samples | Unavailable | Target-free bounded signal gate |
| Performed trial count | Unavailable | Redacted MAT audit after model/control freeze |
| Unique sentence count | Unavailable | Redacted canonical-hash audit |
| Sentence overlap with S21 | Unavailable | Count-only comparison if a separately authorized source hash set exists |
| External/manual target viewing history | Unprovable | Require explicit provenance declaration; keep claim qualified |

No committed S25 target-content access was found, and this pass opened none.
That does not prove nobody ever viewed the local MAT file outside the recorded
workflow. The future packet must preserve this limitation rather than calling
freshness metaphysically certain.

## Recommended Final-Only Design

The future candidate should not be split into tiny train/validation/test
subsets. Its value is that it is a new person:

```text
candidate training rows:       0
candidate validation rows:     0
candidate calibration rows:    0
candidate final rows:          every eligible performed row, opened once
```

The card states 128 unique sentences per session, but it does not guarantee
that this exact block has 64 usable performed rows. The planning recommendation
is therefore:

- expect at most the nominal 64-row half-session;
- require at least 48 performed unique rows after a redacted audit;
- treat 48 as a pragmatic 75% retention floor, not a prospective power claim;
- park before a model or final target open if the floor fails;
- forbid every candidate-side fit, calibration, restart, threshold choice, or
  hyperparameter decision.

This design can potentially answer an unseen-person, same-modality, same-task
zero-shot question. It cannot answer a calibrated-transfer question without a
different physically separated design. It cannot claim unseen text unless a
future overlap audit reports zero source overlap.

## Target Isolation

The future MAT procedure must be implemented and hash-bound before it can run.
It may output only:

- performed-row count;
- unique canonical sentence-hash count;
- duplicate and empty/missing counts;
- source-overlap count if an authorized source hash set exists.

It must never emit sentence plaintext, typed-response plaintext, per-item
targets, or a label distribution used for model selection. The model,
preprocessing, controls, reports, and failure thresholds must be frozen before
candidate content opens.

## Future Controls

The following control families are required but not yet frozen:

1. Source-train-only no-signal sentence prior.
2. Same checkpoint with candidate signal replaced by exact zeros.
3. Channel-name-hash derangement.
4. Nonwrapping, zero-filled time displacement.

Their exact configurations and hashes depend on the eventual Loop 25 input and
Loop 26 source model. This is the main reason the current note cannot become a
preregistration or acquisition authorization.

## Future Access Sequence

1. Loop 25 closes with a compatible causal input path.
2. Loop 26 freezes one source model and every control without S25 content.
3. Loop 27 preregistration binds those hashes, target isolation, final-only
   rules, resources, and the exact two-file candidate.
4. A separate acquisition request is prepared with every permission false.
5. Exact user authorization is recorded in its own tested, pushed, green
   commit before download or local MAT hashing.
6. A dry run verifies revision, paths, bytes, disk headroom, no collisions,
   and one worker.
7. Only absent approved files are acquired under the 1 GiB cap; hashes are
   verified without opening FIF or MAT content.
8. Header, signal, target audit, model execution, and final open each remain
   later separately gated stages.
9. Any failure parks S25; S24 or another candidate cannot open automatically.

## Resource Recommendation

```text
current downloaded payload:       0 bytes
current planning-artifact cap:    8 MiB

future selected files:            exactly 2
future exact bundle:              1,009,939,983 bytes
future acquisition cap:           1 GiB
future minimum free disk:         4 GiB
future workers / CPU threads:     1 / 1
future automatic backup files:    0
```

The 4 GiB preflight protects temporary transfer, final file, and later bounded
derivative headroom without treating free space as permission to download.

## Preregistration Blockers

Do not prepare a Loop 27 acquisition authorization request until all of these
are resolved:

1. Compatible Loop 25 mechanics result.
2. Frozen Loop 26 source model and checkpoint identity.
3. Frozen no-signal and corrupted-signal controls.
4. Header-only sensor compatibility protocol.
5. Redacted target-isolation implementation and hash.
6. Final-only estimand, threshold, tie rule, and failure behavior.
7. Exact source sentence-hash availability or explicit familiar-text claim.
8. Separate staged permissions for acquisition, header, signal, targets, model,
   and final open.

## Closeout Decision

```text
loop27_planning_research_complete_s25_selected_preregistration_blocked
```

This note identifies the smallest honest same-modality transfer candidate
without consuming it. It does not establish an acquired holdout, compatible
channels, fresh targets, a causal source model, transfer, neural advantage,
unseen text, population generalization, real-time use, portable hardware,
assistive benefit, diagnosis, or clinical utility.
