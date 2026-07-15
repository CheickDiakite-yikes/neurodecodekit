# Loop 50 Multi-Source Frozen Encoder Research

Date: 2026-07-15

Status: **Planning research complete; experiment `Not Started`; no S24 or
protected payload access; no model selected, trained, inferred, or scored**

Machine boundary: `registries/loop50_research_boundary.v0.json`

## Decision In Plain Language

Loop 50 should test one narrow question:

> After the existing S21 failure is understood and one development-only S24
> cohort is qualified, can one small shared causal CTC encoder use both
> participants without winning from sentence overlap, participant identity, or
> a pooled average that hides failure on one person?

The recommended design is deliberately smaller than Brain2Qwerty v2:

- one shared architecture with no participant ID, participant embedding,
  participant-specific affine, adapter, checkpoint, or finetuning path;
- globally grouped sentence-text partitions so identical text never crosses a
  fit/evaluation boundary through another participant;
- equal participant weight in the fit objective, regardless of row count;
- one fresh S24 development-qualification partition plus a clearly labeled
  historical S21 out-of-fold diagnostic;
- per-person, worst-person, and pooled reporting, with no pooled-only pass;
- fixed no-signal, exact-zero, channel, time, timing-only, linear, and
  source-only controls; and
- one primary seed named before targets plus two nonselectable stability seeds.

This document is a planning boundary, not a preregistration. Loop 48 Stage B
has no result, S24 remains metadata-only, and the exact S21/S24-compatible
architecture and executable run contract cannot be frozen honestly until those
gates close. The 20-run inventory below is a bounded recommendation that a
later preregistration may preserve or tighten. No acquisition or protected
operation is authorized here.

## Why This Is The Next Useful Design

The consumed Loop 26 event answered one exact question negatively. Its
2,908-parameter candidate reached macro sentence CER `0.938177`, while the
train-only no-signal prior reached `0.751235`. The candidate was also
blank-dominant and seed-sensitive. Loop 48 Stage A classified that aggregate
phenotype as `F5`, but did not identify a cause.

Loop 48 Stage B is therefore upstream of new acquisition. It is designed to
distinguish a fixed-recipe problem, a gross transformed-cache defect, timing
sensitivity, registered-probe nonseparability, prior dominance, and a bounded
data-regime effect using only the existing 10,632,576-byte S21 cache. A new
participant should not be downloaded merely to discover that the old optimizer
or transformed cache was broken.

Loop 49 then provides a scientifically separate role. It selected S24 session
2 block 2 from pinned public metadata as a permanently development-only person,
while preserving S25 as the final-only strict zero-shot person. S24 can help us
make a better decision before spending S25, but it can never become independent
or final evidence.

## Primary-Source Findings

### Brain2Qwerty v2 Makes Multi-Person Training Worth Testing

The June 29, 2026 Brain2Qwerty v2 paper reports that joint nine-participant
training outperformed matched-compute per-participant training and
leave-one-out pretraining plus finetuning for its best, median, and worst
participants. It also reports that early encoder representations retained
participant signatures, while later representations organized more strongly
by key class. This supports testing shared multi-person training while directly
auditing participant shortcuts.

The same paper makes three boundaries especially important here:

1. It assigns all occurrences of the same sentence text across participants
   and sessions to one deterministic hash partition.
2. It still reports substantial inter-participant variability and names
   cross-participant transfer as an open priority.
3. Its current architecture is noncausal and whole-sentence, so its reported
   decoding results are not proof of low-latency real-time operation.

NeuroDecodeKit adopts the text firewall and per-person reporting, but not the
large Conformer, participant-conditioned affine, LLM, or eight-GPU training
regime. Those additions would make the current tiny-data question less
identifiable and less locally accessible.

### Participant Leakage Is A Real Neural-Data Failure Mode

Brookshire and colleagues reproduced EEG classifiers under segment-based and
subject-based holdouts and found that segment-based splitting can strongly
overstate performance on unseen people because participant-specific patterns
leak across partitions. Loop 50 is not an unseen-person test because both S21
and S24 contribute fit rows. It must therefore be labeled development evidence,
and Loop 52's untouched S25 person remains the only planned strict person-level
holdout.

Within Loop 50, participant identity can still act as a target shortcut when
the participants saw different sentence lists. The design therefore forbids
participant identity as model input, globally binds repeated sentence text,
and includes a participant-ID-only no-signal predictor.

### Worst-Person Reporting Is Stronger Than A Pooled Average

Group distributionally robust optimization was developed to improve worst-
group behavior when average performance hides systematic group failures. Its
authors also show that naive group DRO can fail in overparameterized networks
without adequate regularization. With only two development people and fewer
than 10,000 model parameters, Loop 50 does not add a learned group-DRO
optimizer or another tuning axis. It uses the simpler identifiable rule:

```text
pooled_fit_loss = 0.5 * mean_S21_CTC_loss + 0.5 * mean_S24_CTC_loss
```

The acceptance gate is then applied separately to both participants, and the
worst-person margin is primary. Pooled CER remains descriptive.

### Small Development Sets Cannot Carry A Final Claim

Varoquaux shows that small neuroimaging prediction samples produce large and
often underestimated uncertainty. Varma and Simon show that using a validation
procedure both to select a model and estimate its error biases the reported
performance. S24's 16 selection groups therefore choose only whether to
proceed or park. They do not estimate final generalization, and their p-value
cannot be presented as confirmatory after model selection. S25 remains the
future one-time final test.

## Evidence Roles

| Source | Future Loop 50 role | What it can support | What it cannot support |
|---|---|---|---|
| S21 session-1 source-train | Historically used development fit plus text-grouped out-of-fold diagnostic | Regression control and source-person behavior | Fresh validation, source-test performance, or independent confirmation |
| S24 session 2 block 2 | Permanently development-only fit plus 16-group qualification | Whether one frozen multi-source recipe works on both development people | Final or unseen-person evidence |
| S25 session 2 block 2 | No Loop 50 role; remains physically unopened | A later one-time strict zero-shot verdict if every prior gate passes | Development, normalization, calibration, or model selection |
| S21 validation/source-test/session 2 and S7 | Closed/consumed | Historical audit only | Any Loop 50 fit, selection, threshold, or claim |

S21 and S24 are development domains. They are not independent replications.
S24 becomes consumed for development selection when its 16 targets are scored.

## Stage B Outcome Router

No S24 acquisition should happen automatically after Loop 48 Stage B. A future
closeout must apply this ordered router:

| Stage B state | Loop 49/50 action | Reason |
|---|---|---|
| Identity, feasibility, nonfinite telemetry, or gross transformed-cache failure | Park acquisition; repair and separately requalify mechanics | New participant data cannot repair an invalid input or fit path |
| Corrected timing shift materially beats intact | Park acquisition; resolve causal timing/preprocessing first | The intended input representation is not the best registered timing condition |
| Stable intact candidate or linear probe clears the train-only prior/control rule | Permit preparation of the separately gated S24 intake | There is at least a viable signal-to-target development probe to transfer |
| Stable mechanics plus registered `H6` non-saturation, even if prior dominance remains | Permit S24 intake only as a bounded data-regime test | The exact diagnostic supports testing whether added person/sentence diversity changes the regime |
| Stable nonseparability or prior dominance with registered plateau evidence | Park S24 acquisition | The evidence does not support spending storage on the same model family |
| Mixed or unresolved outcome | Park and document; no automatic fallback person | Ambiguity is not permission to acquire |

This router does not authorize Stage B, S24, or Loop 50. A future Stage B
result may trigger only the next preparation step, never automatic acquisition.

## Future Global Text Firewall

The future split must extend Loop 49's canonical text rule across every person
and every model fit:

1. Canonicalize target text with Unicode NFKC, trim surrounding whitespace,
   collapse internal whitespace, and lowercase.
2. Hash the canonical UTF-8 text with a contract-bound salt and SHA-256.
3. Treat all rows with the same canonical text as one global group, regardless
   of participant, session, trial, or list.
4. Assign the first 16 salt-hash-ordered S24 groups to
   `development_selection`; assign all remaining usable S24 groups to
   `development_fit`, requiring at least 32 fit groups.
5. Remove every S21 row matching an S24 selection group from every fit,
   normalizer, prior, comparator, and source diagnostic.
6. For each S21 out-of-fold diagnostic, remove from that fold's training set
   every S24 row whose text matches the held-out S21 fold.
7. Never persist sentence plaintext or raw canonical sentence hashes. Emit only
   opaque item IDs, roles, overlap counts, and one split-manifest SHA-256.

This is stricter than assigning trial numbers. It prevents a shared text from
being a training target for one participant and an evaluation target for the
other.

## Historical S21 Out-Of-Fold Diagnostic

Loop 50 needs a per-person S21 number without pretending the historically used
rows are fresh. The recommended future diagnostic is five deterministic
canonical-text folds over eligible S21 source-train rows:

```text
fold_assignment = SHA256("neurodecodekit-loop50-s21-oof-v0" + NUL + canonical_text) mod 5
```

For each fold:

- fit the candidate, train-only scaler, priors, and any separately trained
  comparator without that fold;
- exclude any S24 fit row sharing text with the held-out fold;
- predict the held-out S21 rows once;
- concatenate the five out-of-fold prediction sets in opaque item-ID order;
  and
- label the result `historical_development_oof`, never validation or test.

All five folds may be known indirectly from prior S21 work, so prediction
freezing does not restore historical freshness. Out-of-fold prediction merely
prevents direct in-sample scoring and gives the no-regression rule a coherent
implementation.

## Future Compatibility And Normalization Gate

Before any target-bearing fit, S21 and S24 must have:

- exactly the same 102 named magnetometer channels in the same canonical order;
- compatible units, sampling rate, time axis, padding semantics, and CTC
  vocabulary;
- no silent interpolation, channel substitution, geometry warp, rereference,
  or participant-specific sensor map; and
- at least 48 usable unique S24 text groups after redacted audit.

If exact geometry or reference semantics cannot be established under the Loop
36 boundary, park. Nominally sharing a Megin system is not enough.

Normalization must be fitted only from the rows participating in the current
fit. For S21 out-of-fold predictions, each fold gets a fold-train pooled scaler.
For the final development candidate, one pooled S21-plus-S24-fit scaler is
frozen with the checkpoint. Per-participant scalers and target-corpus
normalization are forbidden because a later strict S25 zero-shot test permits
no S25-wide signal statistics.

## Future Candidate Policy

Stage B must close before the exact architecture is chosen. The later
preregistration may select exactly one shared candidate from the already
implemented causal family, subject to all of these limits:

- at most 10,000 trainable parameters;
- zero right context and no bidirectional or whole-sentence layer;
- one primary shared checkpoint, two nonselectable shared stability
  checkpoints, and one shared pooled fit-only scaler;
- no participant ID, participant embedding, participant-conditioned affine,
  adapter, prompt, threshold, or per-participant finetuning;
- no language model, n-gram correction, NeuroToken semantic target, or target-
  text-derived input;
- primary seed `5001`, stability seeds `5002` and `5003`, no best-seed
  selection, and no restart; and
- no architecture or recipe change after S24 selection targets open.

The current 2,908-parameter `TinyCausalSentenceCTC-v0` and 2,884-parameter
linear comparator are the bounded references, not automatically selected
future models. If Stage B supports a fixed-recipe failure, reusing that recipe
is prohibited until a separate train-only repair gate closes.

The recommended parameter-update inventory is bounded at 20 runs:

```text
pooled candidate, primary seed, five S21 OOF folds:       5
pooled candidate, final fit, seeds 5001/5002/5003:        3
shared linear comparator, five OOF folds + final fit:     6
S21-only causal comparator, five OOF folds + final fit:   6
total parameter-update runs:                             20
```

No-signal priors use deterministic counts. Exact-zero, channel, and time
conditions reuse frozen candidate checkpoints. The timing/length-only control
must be deterministic or closed-form and may not add a gradient-update run.
The later preregistration must either preserve this inventory or tighten it;
the four-run gap below the absolute cap is not rerun permission.

## Future Comparators And Controls

The later contract should include the following fixed inventory:

| ID | Condition | Purpose |
|---|---|---|
| `L50-C00` | Shared multi-source causal candidate | Primary condition |
| `L50-C01` | Pooled fit-only most-frequent-sentence prior | Global no-signal baseline |
| `L50-C02` | Per-participant fit-only prior | Participant-ID-only target shortcut baseline |
| `L50-C03` | S21-only prior applied without S24 targets | Source-only no-signal baseline |
| `L50-C04` | Exact-zero signal through `C00` checkpoint | Signal-use control |
| `L50-C05` | Channel-name-hash derangement through `C00` | Spatial-identity control |
| `L50-C06` | Nonwrapping zero-filled positive time displacement | Temporal-information control |
| `L50-C07` | Timing/length-only train-fit model | Task-structure control |
| `L50-C08` | Shared parameter-matched linear CTC comparator | Architecture-complexity control |
| `L50-C09` | S21-only causal checkpoint | Descriptive value of adding S24 fit data |

The exact channel map and time displacement must be target-independent and
hash-bound before fit targets. Corruption controls reuse the same primary
checkpoint. The source-only neural comparator is descriptive because Loop 50
is not a clean unseen-person experiment.

## Future Training Objective

Rows must not be pooled naively. For every optimization step or exact epoch:

```text
loss_S21 = mean CTC loss over eligible S21 rows in the batch
loss_S24 = mean CTC loss over eligible S24 rows in the batch
loss = 0.5 * loss_S21 + 0.5 * loss_S24
```

Each participant must contribute before an optimizer update. Replacement or
cycling rules must be deterministic and disclosed. Participant identity may
index the loss ledger and sampler only; it may not enter the model, scaler, or
decoder.

## Future Metrics And Selection Rule

The primary table must report, for every fixed seed and condition:

- S21 historical out-of-fold macro sentence CER;
- S24 development-selection macro sentence CER;
- worst-person macro CER and worst-person candidate-minus-comparator margin;
- pooled macro CER as descriptive context only;
- per-person corpus CER, WER, exact sequences, wins/ties/losses, blank fraction,
  output length, and unavailable fields;
- each no-signal and corruption margin;
- parameter count, optimizer steps, runtime, peak RSS, and output bytes; and
- every fit, inference, target-delivery, scoring, and access counter.

The recommended pass conjunction is:

1. Primary seed `5001` is finite, feasible, and at least `0.05` absolute macro
   CER better than the strongest no-signal prior separately on S21 and S24.
2. Primary seed is strictly better than exact-zero, channel-deranged, time-
   displaced, timing-only, and linear conditions separately on both people.
3. The multi-source primary seed strictly improves S24 over the frozen S21-only
   neural comparator and worsens S21 by no more than `0.02` macro CER.
4. Stability seeds `5002` and `5003` preserve the S24 no-signal direction of
   the primary final fit; no seed may replace `5001`. Stage B separately
   records source-person seed behavior before this experiment.
5. The participant-ID-only prior does not erase the candidate's margin.
6. Worst-person and both per-person gates pass. Pooled improvement cannot rescue
   any failed person.

These are development qualification rules, not a final hypothesis test.
Paired randomization summaries and intervals should be reported, but no S24
selection p-value may be called confirmatory. Failure parks Loop 50 and blocks
the Loop 51 S25 freeze packet. No post-selection rerun is allowed.

## Future Target Firewall

The future execution order must be:

1. Close or park Loop 48 Stage B and apply its registered router.
2. Separately qualify and authorize S24 acquisition, hash, header, redacted
   trial audit, and split.
3. Freeze the exact Loop 50 architecture, scaler rule, folds, controls, seeds,
   metrics, thresholds, resources, and claim ceiling in a preregistration.
4. Commit, push, and obtain remote-green authorization and implementation
   milestones before fit-target delivery.
5. Deliver only S21 source-train and S24 fit targets; create no S25 derivative.
6. Run the exact bounded fit and target-blind inference inventory.
7. Commit and push a hash-only prediction-freeze record; require remote-green
   CI.
8. Deliver the same 16 S24 selection targets once to an isolated scorer.
9. Emit one result, consume the S24 selection partition, and proceed or park
   without rerun or post-target tuning.

## Resource Boundary

This planning pass used no numerical model or protected payload. A future
preregistration must fit inside:

```text
CPU threads / workers / concurrent numerical jobs: 1 / 1 / 1
trainable parameters:                           <= 10,000
planned parameter-update runs:                          20
absolute parameter-update run ceiling:              <= 24
total parameter-update runtime:                  <= 3,600 sec
peak RSS:                                  <= 2,147,483,648 bytes
generated output:                            <= 67,108,864 bytes
minimum free disk before protected execution: 21,474,836,480 bytes
new download under this planning boundary:                    0 bytes
persistent background processes:                                  0
```

The future S24 bundle remains separately capped at 1,342,177,280 bytes. Storage
capacity is not acquisition permission. The tracked tracker workbook was not
reopened because its last artifact-tool pass exceeded the ordinary 1 GiB RSS
envelope; its adjacent user-owned inspection sidecar remains untouched.

## Current Access Ledger

```text
S24 local stat/hash/header/signal/MAT/target reads: 0 / 0 / 0 / 0 / 0 / 0
S25 path/payload/target operations:                         0 / 0 / 0
S21 cache/member/array/target reads this pass:              0 / 0 / 0 / 0
validation/source-test/session-2/S7/S20 reads:              0 / 0 / 0 / 0 / 0
models/training/updates/inferences/prediction sets:         0 / 0 / 0 / 0 / 0
scoring events / target-conditioned choices:                       0 / 0
downloads / network payload bytes:                                 0 / 0
language model / RW3 / stream / device / hardware runs:      0 / 0 / 0 / 0 / 0
scientific claim upgrades:                                             0
```

Primary-source web research read public documents only. It did not access a
neural payload or protected target.

## What This Planning Milestone Proves

**Engineering capability added:** NeuroDecodeKit now has a reviewable design
for a text-leakage-resistant, participant-balanced, worst-person-gated
multi-source experiment that can be frozen before any S24 target or model run.

**Scientific claim not established:** no S24 payload or target was opened and
no model ran, so this work establishes no neural advantage, sensor-signal
dependence, brain-specific origin, decoding accuracy, unseen-person
generalization, causal end-to-end behavior, real-time latency, EEG or portable
hardware performance, assistive utility, diagnostic value, or clinical result.

## Next Exact Boundary

Loop 48 Stage B remains the next protected decision. Until it closes or is
explicitly parked, do not acquire S24. After a qualifying Stage B outcome, the
next reversible work is implementation and synthetic testing of the global
text-group splitter, S21 out-of-fold ledger, participant-balanced sampler,
control transforms, and prediction firewall. S24 still requires its own
acquisition and redacted-audit decisions before Loop 50 can be preregistered.

## Primary Sources

1. Zhang et al., *Accurate Decoding of Natural Sentences from Non-Invasive
   Brain Recordings*, Brain2Qwerty v2 preprint, June 29, 2026:
   <https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf>
2. BCBL, SpanishBCBL official dataset card, pinned metadata source and public
   license/identity/file-format record:
   <https://huggingface.co/datasets/bcbl190626/SpanishBCBL>
3. Brookshire et al., *Data leakage in deep learning studies of translational
   EEG*, Frontiers in Neuroscience 18, 2024:
   <https://doi.org/10.3389/fnins.2024.1373515>
4. Sagawa et al., *Distributionally Robust Neural Networks for Group Shifts:
   On the Importance of Regularization for Worst-Case Generalization*, 2020:
   <https://arxiv.org/abs/1911.08731>
5. Varoquaux, *Cross-validation failure: small sample sizes lead to large error
   bars*, NeuroImage 180, 2018:
   <https://arxiv.org/abs/1706.07581>
6. Varma and Simon, *Bias in error estimation when using cross-validation for
   model selection*, BMC Bioinformatics 7:91, 2006:
   <https://doi.org/10.1186/1471-2105-7-91>
