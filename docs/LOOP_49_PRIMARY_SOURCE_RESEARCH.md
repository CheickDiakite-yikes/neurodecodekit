# Loop 49 Primary-Source Research And Development-Person Intake Boundary

Date: 2026-07-15

Status: **Planning research complete; S24 is selected from public metadata only;
Loop 49 qualification, preregistration, acquisition, and execution have not
started and are not authorized**

Machine boundary: `registries/loop49_research_boundary.v0.json`

Roadmap row: `registries/next_scientific_loops.v0.json` Loop 49

## Decision Summary

Select **SpanishBCBL MEG S24 session 2 block 2** as the preferred future
development-only participant:

```text
MEG/FIF/24_7010/240531/block2.fif       1,048,357,252 bytes
MEG/logs/S24-session2_block2_list1.mat        222,475 bytes
                                               ---------
exact bundle                               1,048,579,727 bytes
1.25 GiB future cap                       1,342,177,280 bytes
cap margin                                  293,597,553 bytes
```

This selection does four useful things at once:

1. It preserves S25 as the final-only unseen-person candidate.
2. It uses the same prompted-typing MEG modality and nominal sensor system as
   the S21 source work.
3. It avoids the published S1/S18 repeated-person alias.
4. It remains inside both the 1.25 GiB Loop 49 cap and the user's 10 GB
   cumulative envelope.

This is not an acquisition result. No S24 local path was inspected, no S24
payload was downloaded or opened, and the roadmap's `>=48` usable-unique-trial
gate is still unproven. Loop 49 therefore remains `Not Started` as an
experiment. Metadata selection does not establish cohort qualification or a
scientific performance result.

## Why This Loop Matters

The consumed S21 result was a clear negative: the tiny causal candidate was
worse than the no-signal prior. Loop 48 Stage A then described a blank-dominant,
seed-sensitive output distribution without proving its cause. A future Loop 48
Stage B may distinguish pipeline explanations within historically used S21
source-train rows, but it cannot create fresh person-level evidence.

That leaves two different scientific jobs:

- **S24 development evidence:** learn what architecture, split, controls, and
  training recipe are defensible on a second person without spending the final
  test.
- **S25 final evidence:** run one genuinely frozen zero-shot person test after
  all development choices are over.

Using S25 for development would erase the second job. Skipping a development
person and opening S25 next would make a negative outcome difficult to
interpret and a positive outcome vulnerable to hidden researcher degrees of
freedom. Loop 49 is the bridge between those mistakes.

## Measured Planning Boundary

```text
pinned Hub metadata rows returned:                396
prior strict MEG FIF/log pairs:                    23
prior eligible pairs after exclusions:             16
metadata wall time:                              3.51 sec
metadata peak RSS:                         62,685,184 bytes
CPU threads / workers:                              1 / 1
free disk before documentation:            42,255,929,344 bytes

S24 payload downloads:                               0
S24 local-path stat/hash operations:                  0
S24 FIF header reads:                                 0
S24 signal reads:                                     0
S24 MAT content reads:                                0
target/label/text reads:                              0
source sentence-hash reads:                           0
split derivatives:                                    0
model/checkpoint runs:                                0
training or parameter updates:                        0
prediction sets or scoring events:                    0
RW3, stream, device, or hardware operations:          0
```

The Hub client returned parsed metadata rather than exact compressed transport
bytes, so wire input bytes and low-level HTTP request count are unavailable.
The one high-level operation was a recursive, expanded `list_repo_tree` call at
the pinned revision. No dataset payload was fetched.

## Primary-Source Findings

### Cross-person variability is the actual scientific bottleneck

Brain2Qwerty v2 reports substantial inter-subject variability and identifies
cross-subject transfer or self-supervised pretraining as a priority. Its early
representations retain participant signatures, while joint multi-subject
training improves the reported best, median, and worst participant results over
per-subject training in its larger English cohort.

That does not prove the same strategy works in our tiny SpanishBCBL regime. It
does justify spending development effort on participant separation and
worst-person controls rather than polishing another same-person aggregate.

### Text identity must cross participant boundaries

Brain2Qwerty v2 assigns train, validation, and test partitions by a deterministic
hash of sentence text. Every occurrence of the same text stays in one
partition across participants and sessions. This matters here because a
person-level holdout can still leak target identity if the same sentence is in
another person's fit set.

The future S24 split must therefore operate on canonical sentence groups, not
trial indices. Any S21 source-train row sharing a future S24 selection sentence
must be excluded from that future fit. If overlap remains, a future report may
describe person transfer on seen prompts, but not unseen-text generalization.

### Validation is for choosing; final evaluation is for judging

The Brain2Qwerty v2 auto-research procedure restricted iterative choices to
validation data and performed cross-subject evaluation once after tuning.
Varma and Simon show why this matters: tuning a classifier and reporting the
same cross-validation estimate biases the apparent performance. Varoquaux also
shows that small neuroimaging samples carry large uncertainty that ordinary
fold-level error bars can understate.

Therefore:

- S24 is permanently development-only after first protected access;
- S24 selection rows become consumed for model selection after scoring;
- S25 stays final-only and opens once under a later frozen contract; and
- the `>=48` Loop 49 floor is a pragmatic retention threshold, not a power
  calculation or reliability guarantee.

### Quantity and sentence diversity are separate resources

Brain2Qwerty v2 reports that asynchronous encoder performance improves with
recording quantity and that, at matched sentence count, greater sentence
variety improves CER. A duplicated row is therefore not equivalent to a new
sentence. Loop 49 counts usable unique canonical sentence groups and reports
duplicates separately.

### Brain2Qwerty v2 is not yet the local real-time endpoint

The v2 paper explicitly says the current whole-sentence architecture is
noncausal and necessarily slow for word-by-word feedback. It also reports
results from a 306-sensor cryogenic MEG system. Loop 49 can prepare better
cross-person development evidence, but it cannot establish end-to-end latency,
causal full-pipeline decoding, EEG transfer, OPM-MEG behavior, portable sensing,
or home-device usability.

## Official Cohort, Identity, And License Boundary

The official SpanishBCBL card states that:

- healthy skilled typists performed read, wait, then type trials without
  visual feedback;
- each session used 128 unique Spanish sentences;
- MEG used 306 Megin/Elekta Neuromag channels at 1 kHz, with 102
  magnetometers and 204 planar gradiometers;
- S1/S18, S4/S14, and S5/S10/S21 are repeated-ID groups for the same people;
- S23 is excluded from the 19-person MEG cohort because of a metallic implant;
  and
- the release is CC BY-NC 4.0 and must remain noncommercial absent another
  license.

S24 is not a published alias of S21 or another selected source ID, is not S23,
and is not the final-only S25 person. This establishes metadata-level identity
eligibility only. It does not prove channel order, geometry, signal quality,
trial count, sentence overlap, or target freshness against unrecorded manual
access.

## Candidate Decision

| Candidate | Exact bytes | Decision | Reason |
|---|---:|---|---|
| S18 session 2 block 2 | 1,018,878,168 | Not selected | 29,701,559 bytes smaller, but carries the avoidable S1/S18 alias |
| **S24 session 2 block 2** | **1,048,579,727** | **Selected from metadata** | Smallest preferred clean-identity development bundle after preserving S25 |
| S22 session 1 block 1 | 1,107,866,218 | Not selected | Clean identity but 59,286,491 bytes larger than S24 |
| S25 session 2 block 2 | 1,009,939,983 | Final-only | Loop 27 reserves it for the future zero-shot verdict |
| S23 session 2 block 2 | 958,422,728 | Ineligible | Official metallic-implant exclusion |
| S21 | n/a | Ineligible | Observed source person; aliases S5 and S10 |
| S7 | n/a | Ineligible | Consumed EEG evaluation, not same-modality MEG |
| S20 | n/a | Separate lane | Reserved for accessible EEG research |

Selecting by bytes alone would choose the wrong scientific role. S25 is smaller
but must remain final; S18 is slightly smaller but creates avoidable identity
bookkeeping. The 29.7 MB S24 premium is only about 2.9% of the S18 bundle and
buys a cleaner person identity while staying 293,597,553 bytes below cap.

No automatic backup is allowed. If S24 later fails a hash, exclusion, trial,
geometry, resource, or alignment gate, the outcome is a park or a versioned
amendment before another participant opens.

## Exact Selected Metadata

### Raw MEG

```text
path:        MEG/FIF/24_7010/240531/block2.fif
bytes:       1,048,357,252
Git blob:    87047b090ba1ffd7db68b5c40e8c1bd8b62137d9
LFS SHA-256: b75a60d1dc7210fc6abb2b65e959b392057bc09a884296ccbe15979bd332fb1a
Xet hash:    2a023b8655c759cbd90712bcc93e679d8bcf27a50833c565b9bb2b42bfbb4754
file commit: 072c0eaaa889eb54cc6b23a112fb15905e884cb3
```

### Protected Behavioral Log

```text
path:        MEG/logs/S24-session2_block2_list1.mat
bytes:       222,475
Git blob:    7c611adcebc0c83edefed14aa17a624f32b9e2b5
LFS SHA-256: 4da5387cf099364071bd806970c7db715577b6bcee218296361538a86928ebb3
Xet hash:    248ec34c7fb6892206f1caad10173bd2fc23a73fb2967772b6ef21a43b13a99a
file commit: 072c0eaaa889eb54cc6b23a112fb15905e884cb3
```

This pass deliberately did not check whether either path exists locally. Local
presence is not needed for metadata selection, and a broad path search would
add no scientific evidence. A future acquisition dry run must use exact paths,
collision rules, sizes, and hashes inside the repository's declared data root.

## What Is Available And Unavailable

| Field | Status now | Future gate |
|---|---|---|
| Canonical person identity | Metadata-supported | Preserve alias ledger |
| Same nominal task/modality/system | Metadata-supported | Header and event audit |
| Exact remote paths, sizes, and hashes | Available | Fail closed on mismatch |
| License | CC BY-NC 4.0 | Keep use noncommercial |
| Local presence | Not checked | Acquisition dry run only |
| Exact channel names and order | Unavailable | Separately authorized header-only audit |
| Sensor geometry | Unavailable | Header-only geometry ledger |
| Recording duration and valid samples | Unavailable | Bounded signal audit |
| Performed trial count | Unavailable | Redacted MAT audit |
| Usable unique sentence count | Unavailable | Redacted MAT audit |
| At least 48 usable unique rows | **Unproven** | Mandatory intake stop rule |
| S21 sentence overlap | Unavailable | Count-only canonical-text audit |
| External/manual target-view history | Unprovable | Disclose provenance limitation |

Because the mandatory trial floor is unavailable, the selected candidate is
not yet a qualified Loop 49 cohort.

## Future Development Split Recommendation

This is a research recommendation, not an implemented or authorized contract.
If a later redacted audit finds at least 48 usable unique canonical sentence
groups, use:

```text
development_selection: 16 unique canonical sentence groups
development_fit:       every remaining usable unique group
minimum at gate:       16 selection + 32 fit = 48
nominal at 64 rows:    16 selection + 48 fit = 64
final/test rows:       0
```

The assignment rule should be frozen before target access:

1. Canonicalize text with Unicode NFKC, surrounding-whitespace removal,
   internal-whitespace collapse, and lowercase conversion.
2. Hash `neurodecodekit-loop49-development-split-v0`, a NUL separator, and the
   canonical UTF-8 text with SHA-256.
3. Group every occurrence of the same text across rows and people.
4. Sort unique S24 text groups by digest.
5. Assign the first 16 groups to `development_selection`; assign every
   remaining group to `development_fit`.
6. Exclude from future fit every S21 source-train row whose canonical text is
   in S24 selection.
7. Never read S21 validation, source-test, or session-2 rows for this design.

The future implementation must not persist raw sentence hashes or emit
sentence plaintext. It may emit opaque item IDs, fit/selection roles, aggregate
overlap counts, and one split-manifest SHA-256. Trial order and participant ID
may not assign a split or predict a target.

Fit targets may open only after the split and derivative identities are frozen
under a separate authorization. Selection targets may open only after every
candidate and control prediction is committed, pushed, and remotely green.
Once scored, those 16 selection groups are consumed for model selection and
cannot become independent evidence.

## Future Loop 50 Controls

A later multi-source experiment needs, at minimum:

1. Source-train-only and pooled train-only no-signal sentence priors.
2. Exact-zero signal through the same checkpoint.
3. Channel-name-hash derangement.
4. Nonwrapping, zero-filled time displacement.
5. A participant-ID-only target predictor.
6. Participant-balanced sampling and per-person reporting.
7. Worst-person as well as pooled CER.
8. Frozen candidate and control predictions before S24 selection targets.

A pooled average is insufficient. A model that improves S21 while worsening
S24, or predicts text from participant/list identity rather than sensor input,
does not pass the future transfer-development gate.

## Future Redacted Audit

The MAT log remains opaque today. A separately implemented and authorized audit
may emit only:

- performed-trial count;
- usable unique canonical-sentence count;
- duplicate and missing counts;
- development fit and selection counts;
- aggregate S21 source-train overlap by future partition; and
- one opaque split-manifest hash.

It must not emit sentence plaintext, typed-response plaintext, per-item target
previews, raw canonical sentence hashes, or a target distribution used to
choose a seed, threshold, loss, architecture, or stop rule.

## Access Order

1. Complete or explicitly park the separately authorized Loop 48 Stage B path.
2. Implement and test the target-isolated audit and split without opening S24.
3. Preregister exact files, hashes, resources, minimum trial gate, split,
   controls, target order, and claim ceiling.
4. Prepare a machine acquisition request with every permission false.
5. Record one exact acquisition decision in a separate committed, pushed, green
   artifact.
6. Dry-run revision, paths, bytes, disk headroom, collision policy, one thread,
   and one worker.
7. Download only the two exact files if absent; verify hashes without opening
   FIF or MAT content.
8. Run a separately authorized header-only compatibility gate and then a
   separately authorized redacted trial/split audit.
9. Park before fit-target delivery if the `>=48` unique-row gate or any identity,
   hash, geometry, resource, or overlap boundary fails.
10. Authorize a separately frozen Loop 50 protocol before any training,
    inference, selection-target delivery, or scoring.

## Resource Recommendation

```text
future exact bundle:                    1,048,579,727 bytes
future bundle cap:                      1,342,177,280 bytes
absolute cumulative user envelope:    10,000,000,000 bytes
minimum free disk before acquisition: 21,474,836,480 bytes
CPU threads / workers:                            1 / 1
header or redacted-audit RSS cap:       1,073,741,824 bytes
persistent background processes:                   0
```

The tracked workbook was not reopened. Its last artifact-tool pass measured
1,572,667,392 bytes peak RSS, above this planning boundary's 1 GiB envelope.
The canonical Markdown and JSON trackers are updated instead; the adjacent
user-owned inspection sidecar remains outside scope.

## Claim Boundary

### Established now

- One exact S24 public-metadata bundle is the preferred future development-only
  candidate.
- Its two files total 1,048,579,727 bytes and fit the declared cap.
- S24 avoids the published S1/S18 alias while preserving S25 final-only.

### Maximum possible Loop 49 claim after later qualification

S24 is a qualified same-task, same-modality development cohort for bounded
model fitting and selection.

### Not established

- The `>=48` usable-unique-trial gate.
- S24 signal, channel, geometry, timing, target, or alignment quality.
- Neural advantage over a no-signal prior.
- Independent validation or unseen-person/text generalization.
- Brain-specific rather than peripheral or task-locked origin.
- End-to-end causal or real-time decoding.
- EEG, OPM-MEG, portable, home-device, assistive, diagnostic, or clinical
  performance.

## Primary Sources

1. Brain2Qwerty v2 primary paper:
   https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
2. Official SpanishBCBL dataset card and CC BY-NC 4.0 license:
   https://huggingface.co/datasets/bcbl190626/SpanishBCBL
3. Immutable SpanishBCBL metadata revision:
   https://huggingface.co/datasets/bcbl190626/SpanishBCBL/tree/88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
4. Official Brain2Qwerty SpanishBCBL loader:
   https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/studies/spanishbcbl.py
5. Hugging Face Hub metadata API:
   https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api
6. Brain2Qwerty v1 primary paper:
   https://www.nature.com/articles/s41593-026-02303-2
7. Varma and Simon, model-selection error bias:
   https://europepmc.org/article/PMC/1397873
8. Varoquaux, small-sample cross-validation uncertainty:
   https://arxiv.org/abs/1706.07581

## Closeout Sentence Pair

Engineering capability added: an exact, storage-bounded, identity-aware
metadata decision now preserves separate development-person and final-person
roles before any S24 payload opens.

Scientific claim not established: no S24 payload, trial, target, signal, model,
training, decoding, unseen-person, real-time, EEG, device, or clinical result
exists from this planning pass.
