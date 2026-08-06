# Open EEG R&D Strategy Refresh

Date: 2026-08-06

Status: **Research complete; strategy additive; no execution authorized**

Machine-readable boundary: `registries/open_eeg_rd_strategy.v0.json`

## Decision

NeuroDecodeKit is still on the right path. The next scientific advantage is not
a larger local model. It is a faster and more discriminating evidence ladder:

1. finish the staged S20 data-integrity path without spending protected targets;
2. prove the candidate pipeline can recover a known motor effect on a tiny public
   positive-control dataset;
3. add an interpretable pre-keypress motor-physiology assay and strong classical
   EEG baselines before the future S20 neural model freezes;
4. keep EEG foundation models in a separate public-data benchmark lane until a
   specialist baseline is qualified; and
5. turn the open-source project into a local-first contribution network where
   EEG owners can return hash-bound aggregate receipts without uploading raw
   recordings.

This refresh does not amend or authorize Loop 54 or Loop 55. It records the
research basis and the decisions that a future preregistration should consider.

## Why The Current Path Still Holds

### Small specialist models remain scientifically competitive

The 2026 EEG-FM-Compass benchmark evaluates 12 open EEG foundation models and
specialist baselines across 13 datasets and nine paradigms. Its reported
findings are unusually relevant to NeuroDecodeKit: linear probing is often
insufficient, specialist models trained from scratch remain competitive, and
larger foundation models do not consistently generalize better.

The separate ICLR 2026 ST-EEGFormer study reaches a compatible conclusion.
Classic neural decoders remain competitive; a fully fine-tuned model can lead
the average ranking, but its strongest reported variant exceeds 300 million
parameters. That is a different compute and data regime from one protected S20
typing block.

Sources:

- [EEG-FM-Compass paper](https://arxiv.org/abs/2601.17883)
- [EEG-FM-Compass code](https://github.com/Dingkun0817/EEG-FM-Benchmark)
- [ST-EEGFormer paper](https://openreview.net/forum?id=5Xwm8e6vbh)
- [ST-EEGFormer code](https://github.com/LiuyinYang1101/STEEGFormer)

Decision: retain the compact specialist-first Loop 55 path. Do not spend S20 on
pretrained-weight selection, a transformer bake-off, or model-scale search.

### Preprocessing can create impressive but invalid scores

Kessler et al. systematically varied EEG preprocessing across seven ERP
experiments. Artifact correction frequently reduced decoding accuracy, while
uncorrected structure could increase it. The paper's core warning is important:
high predictive performance can reflect structured noise rather than neural
information.

Sources:

- [How EEG preprocessing shapes decoding performance](https://doi.org/10.1038/s42003-025-08464-3)
- [Official analysis repository](https://github.com/kesslerr/m4d)

Decision: do not optimize preprocessing for the highest score. Preserve every
channel through Loop 54, freeze causal transforms before protected scoring, and
require peripheral, timing, and corruption controls. A future diagnostic may
compare minimal causal preprocessing with one artifact-attenuated lane, but the
diagnostic cannot select a winner after final targets open.

### Overt typing contains a known motor-physiology rung

Prior typewriting EEG work measured lateralized motor-response potentials while
participants responded with the left or right hand. Separate simultaneous
MEG/EEG work decoded hand-movement direction and reported above-chance
information before movement onset. These studies do not prove that S20 contains
the same effect, but they identify a more interpretable first target than
29-class key prediction.

Sources:

- [Typewriting and lateralized motor potentials](https://doi.org/10.1080/23273798.2017.1283427)
- [Hand movement direction decoded from MEG and EEG](https://doi.org/10.1523/JNEUROSCI.5171-07.2008)

Decision: retain performed hand as the ordered primary endpoint. Before a future
Loop 55 model freeze, add a data-independent motor-physiology assay using only
causal pre-keypress samples, declared motor-channel identities when available,
fixed low-frequency and mu/beta summaries, trial-level aggregation, and the
same EOG, timing, and displacement controls as the model path. This assay is a
mechanistic sanity check, not permission to call the signal brain-specific.

## Open-Source Tool Decisions

| Tool | Current verified release or snapshot | Decision | Intended role | Boundary |
|---|---|---|---|---|
| MNE-Python | `1.12.1`, BSD-3-Clause | Retain optional | BrainVision/EDF readers and CSP reference implementation | Forbidden in L54-A; no base import |
| MOABB | `1.5`, BSD-3-Clause | Prepare isolated adapter | Public motor-task positive-control benchmark and reproducible evaluation pattern | Never default-download; public lane only |
| Braindecode | `1.7.0`, BSD-3-Clause with component notices | Prepare isolated adapter | Reference EEGNet and compact specialist implementations | Optional environment; no S20 architecture search |
| pyRiemann | `0.12`, BSD-3-Clause | Evaluate on public positive control | Covariance, MDM, and tangent-space classical baseline | Add only as an optional benchmark dependency if measured value is clear |
| MNE-BIDS | `0.19.0`, BSD-3-Clause | Retain for later provenance work | BIDS read/write envelope and contributor interoperability | Not an L54-A reader and not a target firewall |
| OpenEEGBench | `0.6.0`, BSD-3-Clause | Watch and use only in a separate public-data lane | Reproducible foundation-model and parameter-efficient tuning comparisons | Its default multi-dataset behavior must be wrapped with explicit dataset and byte caps |
| EEG-FM-Compass | commit `06b607e`, MIT | Use as research reference | Compare specialist and foundation-model evidence | Do not vendor or reproduce its GPU-scale benchmark locally |
| ST-EEGFormer | commit `542ee17`, MIT code | Watch | Evidence that full fine-tuning can help at large scale | More than 300M parameters is outside the current laptop and Loop 55 boundary |
| ZUNA1.1 | commit `953c258`, Apache-2.0 claimed by project | Do not use in primary evidence | Possible future public-data robustness stress test | It generates plausible missing channels and warns that reconstructions can hallucinate; imputed samples cannot support the primary neural claim |

No package in this table becomes a base dependency from this decision. Any
future integration must run in an optional or isolated environment, report its
exact version and license, and refuse unbounded downloads.

## Upgrade 1: Known-Effect Positive Control Before Protected Discovery

The free PhysioNet EEG Motor Movement/Imagery Dataset contains 64-channel,
160 Hz EDF+ recordings from 109 volunteers. Runs `3`, `7`, and `11` are repeated
left-versus-right motor-execution runs. The first three participants' nine EDF
files total only `23,248,224` bytes according to current public HTTP metadata:

```text
S001R03.edf  2,596,896 bytes
S001R07.edf  2,596,896 bytes
S001R11.edf  2,596,896 bytes
S002R03.edf  2,555,616 bytes
S002R07.edf  2,555,616 bytes
S002R11.edf  2,555,616 bytes
S003R03.edf  2,596,896 bytes
S003R07.edf  2,596,896 bytes
S003R11.edf  2,596,896 bytes
```

Sources:

- [PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/)
- [MNE EEGBCI run definitions](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html)

Prospective use, after a separate exact Tier C contract:

1. acquire only those nine files under a 32 MiB network and disk cap;
2. freeze run `11` before model selection and use runs `3` and `7` for fit and
   train-only choices;
3. compare fixed shrinkage-LDA, CSP-LDA, and Riemannian covariance baselines;
4. retain left/right labels, timing-only, channel-derangement, and EOG or
   peripheral caveats;
5. measure runtime, RSS, bytes, participant/run identities, and every attempt;
6. select at most one externally qualified classical family for the future S20
   hand endpoint; and
7. label the result an off-task engineering positive control, never an S20,
   typing, language, or thought-decoding result.

This lane is valuable even if it fails. A failure would localize basic EDF,
windowing, grouping, or baseline problems before protected S20 targets are
spent. A pass would show only that the implementation can recover a known
motor-task signal on a public dataset.

No PhysioNet file was downloaded or opened during this strategy review.

## Upgrade 2: A Specialist Baseline Triangle

The future S20 preregistration should compare three complementary, frozen ideas
without turning them into a target-driven search:

1. **Low-frequency shrinkage LDA.** Fixed causal waveform summaries provide an
   interpretable linear test of movement-related potential information.
2. **CSP-LDA or Riemannian covariance.** One public-data-qualified spatial or
   covariance pipeline tests motor-band structure with very few trainable
   degrees of freedom.
3. **Compact causal EEGNet-style model.** The existing `<=10,000`-parameter
   family tests whether a learned temporal-spatial representation adds value.

The public positive-control lane, not S20 selection or final targets, should
choose between CSP-LDA and the Riemannian alternative. The future protected run
then carries one classical family and one compact family, plus the already
planned no-signal, timing, zero-signal, derangement, EOG-only, and centered
noncausal diagnostics.

The result router becomes more informative:

- physiology and classical pass, compact fails: representation/optimization
  failure;
- physiology passes, both models fail: aggregation or sample-size failure;
- centered passes, causal fails: post-keypress execution or feedback only;
- EOG/timing matches EEG: peripheral or task-structure explanation;
- all signal paths fail: no demonstrated usable effect in the frozen slice.

## Upgrade 3: Open Cohort Federation Instead Of Centralized Data Hoarding

[Conduit reports a large proprietary collection effort](https://condu.it/thought/10k-hours).
That is competitive context, not independently reproduced scientific evidence.
NeuroDecodeKit cannot and should not imitate that effort on one laptop. Its
credible open-source counterstrategy is a local-first federation:

1. contributors keep raw EEG on their own machine by default;
2. NeuroDecodeKit validates BIDS or explicit source metadata locally;
3. it emits a signed, hash-bound receipt with modality, device, montage,
   sampling, task, trial counts, split identity, resources, warnings, and claim
   ceiling;
4. contributors may share aggregate benchmark cards and code without sharing
   raw signals or plaintext targets;
5. raw-data release remains a separate consent, license, and repository
   decision; and
6. only matched task/protocol evidence enters a scientific aggregate.

MOABB supplies the benchmark posture, MNE-BIDS supplies interoperable dataset
structure, and NeuroDecodeKit supplies stricter access counters, target
firewalls, resource caps, and proof-language checks. This is a future product
and community direction, not an authorization to collect or upload data now.

## Foundation-Model Rule

Foundation models remain a watch lane, not the next protected experiment.

A future evaluation becomes eligible only if all of these are true:

- Loop 54 closes cleanly;
- the public positive-control baseline passes or parks with an explained
  implementation reason;
- the compact specialist S20 result is frozen first;
- the model license and checkpoint provenance are compatible with the dataset;
- input channels, geometry, sampling, causal context, and normalization are
  represented without invented values;
- the run is isolated from final targets and carries a byte, runtime, RSS, and
  parameter-update cap; and
- the exact comparison distinguishes frozen probing, parameter-efficient
  tuning, and full fine-tuning.

ZUNA or another generative imputer may never reconstruct missing primary-input
samples and then have those samples treated as measured evidence. Synthetic or
imputed channels must remain visibly marked and diagnostic-only.

## Revised Execution Order

### Work allowed under current Tier A/B autonomy

1. Keep the exact L54-A registration immutable and obtain replacement CI after
   GitHub Actions recovers.
2. Build synthetic-only motor fixtures that contain independently controlled
   cortical-like, timing-only, and EOG-shortcut components.
3. Add optional adapter contracts for shrinkage LDA, CSP-LDA, and Riemannian
   baselines without downloading data or adding a base dependency.
4. Add local-only contributor receipt fixtures and BIDS metadata validation.
5. Prepare, but do not execute, the public positive-control contract.

### Work requiring separate exact Tier C decisions

1. Open and execute the registered S20 L54-A VHDR stage.
2. Acquire or parse any PhysioNet EEG file.
3. Execute L54-B signal quality or L54-C target-bearing reconciliation.
4. Train or score any protected S20 model.
5. Download or run pretrained EEG foundation-model weights.
6. Upload, release, delete, or transform real neural data.

## Resource Policy

- Base installation remains dependency-free.
- Every new tool starts in an isolated optional environment.
- Public positive-control intake defaults to dry-run and exact files.
- The first proposed PhysioNet intake is at most 32 MiB network, 64 MiB
  incremental disk, one thread, one worker, 10 CPU minutes, 1 GiB peak RSS,
  and 16 MiB output.
- No foundation model runs on the protected path before the specialist result.
- No cloud upload of S20 or contributor raw EEG is allowed by this strategy.
- Every experiment reports input/output bytes, runtime, RSS, runs, targets,
  model operations, warnings, unavailable fields, and claim ceiling.

## Bottom Line

We are not behind on research discipline. Current open benchmarks strengthen
the specialist-first decision, and current preprocessing evidence strengthens
the project's control-heavy design. We are behind on data breadth and external
positive controls. The highest-value correction is therefore to validate the
pipeline on a tiny known motor task, add interpretable classical and physiology
rungs, and make local-first external contribution easy.

Engineering capability proposed: a public positive-control and federated EEG
benchmark layer can de-risk protected experiments and let outside contributors
extend evidence without making NeuroDecodeKit a raw-data warehouse.

Scientific claim not established: this review accessed only public metadata,
papers, code, and committed local artifacts; it downloaded no EEG payload,
opened no S20 content, trained no model, and established no neural advantage,
decoding accuracy, generalization, real-time performance, portable hardware,
at-home use, or clinical utility.
