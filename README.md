# NeuroDecodeKit

Open-source, local-first, reproducible tools for turning EEG and MEG recordings
into small, inspectable neural language-decoding experiments without hiding
data access, split leakage, resource cost, or negative results.

NeuroDecodeKit is an independent research toolkit inspired by the access and
reproducibility problems around Brain2Qwerty-style decoding. It is not an
official Brain2Qwerty project, a medical device, or a demonstrated mind-reading
system.

```text
manifest -> selective download -> tiny shard -> event/sentence cache
         -> no-signal baseline -> neural baseline -> CER/WER report
```

The core thesis is practical: before another large model matters, a researcher
should be able to identify one legal dataset slice, inspect it locally, build a
bounded cache, preserve provenance, compare against a language-only control,
and explain exactly what the result does not prove.

Why the gates? Most routine engineering is reversible, but opening a held-out
target, reusing a consumed evaluation, or changing a rule after seeing the
outcome is not scientifically reversible. The approved
[Research Autonomy Charter](docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md) and its
[activation decision](docs/RESEARCH_AUTONOMY_CHARTER_DECISION.md) let
routine code, tests, synthetic work, bounded development experiments, commits,
pushes, and CI proceed autonomously while reserving exact approval for those
irreversible Tier C events.

## Results At A Glance

> The standout result is not an inflated decoder score. It is a complete,
> reproducible evidence chain that validates difficult engineering, preserves
> negative scientific results, and knows when a gate should stop.

### The Result Ladder

| Evidence layer | Strongest result so far | What that means now |
|---|---|---|
| Trial identity | All 66 S21 session-1 trials and all 63 performed session-2 trials reconcile to MAT provenance; empty session-2 slots remain explicit | The real MEG evidence has exact trial identity instead of fuzzy sentence matching |
| Local neurodata access | Six EEG/MEG file families are covered by 40 bounded fixtures: 38 readable and 2 exact refusals | Contributors can test metadata, readers, privacy, and caps without sharing participant recordings |
| Continuous interfaces | NeuroTokenCache preserves 553 valid synthetic frames; causal replay is exact across 5/5 schedules with zero right context | Cache and streaming contracts exist, but they do not establish useful neural representations or text decoding |
| Full-path causality gate | Loop 25 v1 passed a dedicated causal anti-alias audit, 65,537 response points, 23 alias probes, 168 schedule checks, 240 resume checks, and 72 future-mutation controls across 24 target-free items | The exact 1000-to-100 Hz path is mechanically causal with zero right context; this is synthetic mechanics evidence, not proof that neural information survives |
| Consumed S21 validation | The registered 2,908-parameter candidate reached macro CER `0.938177`; the train-only no-signal prior reached `0.751235`, so the candidate was worse by `0.186942` | Loop 26 is parked after one consumed six-target event; this is a clear negative result, not neural advantage |
| Artifact-only failure localization | The one-shot Stage A pass reproduced `99.3477%` primary blank, all 6/6 unstable fixed-prefix groups, and all 3/3 size-55 seeds worse than the prior | Loop 48 selected descriptive `F5` output-distribution instability in `0.0166` sec and 23.4 MB RSS; that phenotype is not a proven root cause |
| Train-only failure discrimination | The consumed Stage B primary reached macro CER `0.953566` versus `0.822045` for its train-only prior; all six full-size causal/linear fits were finite and stable, but none cleared the prior | `H4` stable nonseparability is supported and fixed timing-offset `H3` has evidence against it; the exact `L50-R05` route parks S24 acquisition for this model family, with no neural advantage or rerun |
| Temporal-representation repair | The consumed Stage C synthetic candidate reached CER `0.433333` and `1/8` exact versus ablation CER `1.000000`; its `0.566667` CER advantage passed, but the absolute `<=0.10` CER and `>=7/8` exact gates failed | Temporal context was usable on the purpose-built fixture, but Stage C is parked without rerun and establishes no real neural-decoding benefit |
| Fresh EEG acquisition gate | Loop 53 acquired and opaque-verified the exact public S20 session-2 block-2 bundle: 4 files, `96,090,264` bytes, `3.629499s`, 63,225,856-byte peak RSS, and all 10 gates passed | Acquisition mechanics are proven and the one invocation is consumed; no header, marker, signal sample, MAT field, target, cache, split, or model was interpreted or run |
| Fresh EEG qualification design | Loop 54 now separates strict VHDR-only metadata, target-blind VHDR+EEG quality, isolated target-bearing VMRK+MAT reconciliation, and aggregate closeout through 22 gates and 30 exact refusals | Planning research is complete and Loop 53 acquisition passed; every real interpretation stage remains separately unauthorized, and the current monolithic extractor is excluded from this future claim path |
| Fresh EEG neural-effect design | Loop 55 now separates a causal pre-keypress performed-hand gate from a harder causal 29-key gate, with performed actions as primary targets, a post-keypress diagnostic, 12 matched conditions, exact trial-level tests, and one-shot target order | Planning research is complete and Loop 54 dependent; the S20 bundle is acquired but uninterpreted, the experiment is `Not Started`, and no target, model, prediction, score, neural advantage, or decoding result exists |
| Bounded AI research guard | A dependency-free Loop 55 policy now validates and hashes strict synthetic AI recipe proposals, rejects target leakage, future context, LLMs, pretrained weights, unknown fields, model runs, and cap expansion, and reserves at most four future train-inner proposal rounds inside the existing 12-fit ceiling | The synthetic interface is implemented and measured; no AI proposal has accessed S20, trained a model, or produced neural evidence, and any future real proposal phase remains Loop 54 dependent and separately Tier C authorized |
| Cross-modality accessibility verdict design | Loop 56 freezes five verdict classes, 12 non-skippable capability levels, 18 EEG/MEG comparison dimensions, a 16-field claim sentence, and a 12-part at-home conjunction | Planning research is complete and Loop 55 result dependent; only modality-aware interfaces are shared, tested MEG/EEG predictors remain negative, S20 has acquisition evidence only, and no equivalence, transfer, real-time, device, home, or clinical claim exists |
| Development-person intake planning | Loop 49 metadata research selects S24 session 2 block 2: one MEG FIF plus one protected MAT log, exactly `1,048,579,727` bytes; a future text-grouped split reserves 16 unique sentence groups for selection and requires at least 32 fit groups | S24 avoids the S1/S18 alias and preserves S25 final-only, but no S24 path or payload was opened and the `>=48` usable-row, channel, geometry, and overlap gates are unproven; Loop 49 remains `Not Started` |
| Multi-source encoder planning | Loop 50 research freezes global text grouping, five-fold historical S21 out-of-fold diagnostics, one 16-group S24 development gate, equal-person loss, ten fixed conditions, and an exact 20-update inventory led by seed `5001` | Stage B route `L50-R05` now parks the same-family S24 path; Loop 50 remains `Not Started`, with S24 qualification, model selection, training, scoring, and every scientific claim unavailable |
| Fresh transfer candidate | Loop 27 metadata research selects S25 session 2 block 2: one MEG FIF plus one protected MAT log, exactly 1,009,939,983 bytes under 1 GiB | S25 is not downloaded or qualified; preregistration waits for the causal source model, controls, and target isolation |
| Transfer decision rule | Loop 28 research separates T0-T3 evidence and recommends a strict S25 T2 zero-shot gate: zero target fit, at least 48 final rows, at least 0.05 macro-CER improvement, 65,535 paired swaps plus observed, and strict corruption-control wins | The experiment is `Not Started`; this resolves one planning dependency without authorizing S25, a model run, calibration, or final access |
| Portable sensing decision | Loop 29 research separates cryogenic MEG, partner/lab OPM-MEG, local-first scalp EEG, and non-neural controls through 15 requirements and six qualification levels | Planning research is complete while the experiment is `Not Started`; no device, download, stream, hardware session, or portable decoding result exists |
| Local replay interaction decision | Loop 30 research freezes four source modes, a 30-field target-free trace, nine clock domains, six latency levels, 18 gates, 30 refusals, and fixed loopback/browser/accessibility controls | Planning research is complete while the experiment is `Not Started`; no trace, UI, server, browser run, live source, confidence, or end-to-end latency result exists |
| Neural-attribution decision | The candidate beat exact-zero and timing-only controls on 6/6 items, but failed the complete prior, derangement, displacement, and corruption conjunction | Loop 31 is parked; the partial control wins are diagnostic hints and do not establish sensor-signal dependence or brain-specific origin |
| Peripheral-confound decision | Loop 35 research freezes 10 confound classes, 9 synchronized stream classes, 13 conditions, 3 separately authorized stages, 24 gates, and 32 refusals | Planning research is complete while the experiment is `Not Started`; current data cannot support the complete firewall, and even a future pass can claim only incremental brain-sensor information beyond recorded controls |
| Geometry/reference decision | Loop 36 research freezes 6 representation layers, 5 modality profiles, a 24-field channel record, 12 operation classes, 16 fixture families, 22 gates, and 30 refusals | Planning research is complete while the experiment is `Not Started`; a future header pass can establish at most declared metadata compatibility, not numerical/model/device equivalence |
| BIDS provenance decision | Loop 37 research freezes 6 export layers, 5 artifact profiles, 15 stable-field mappings, 16 NeuroDecodeKit extension fields, 20 fixtures, 24 gates, and 32 refusals | Planning research is complete while the experiment is `Not Started` and unauthorized; future NeuroToken/report payloads remain explicitly non-standard inside a BIDS-organized envelope |
| Neural-data privacy decision | Loop 38 research freezes 5 sensitivity levels, 8 artifact classes, 10 lifecycle surfaces, 12 sensitive-field classes, 5 deletion-receipt levels, 24 fixtures, 26 gates, and 36 refusals | Planning research is complete while the experiment is `Not Started` and unauthorized; unknown copies remain unresolved, and path absence is not media sanitization |
| Cross-machine reproducibility decision | Loop 39 research freezes 7 qualification levels, 18 environment fields, 8 output classes, 6 comparison classes, 6 future matrix cells, 28 gates, and 38 refusals | Planning research is complete while the experiment is `Not Started` and unauthorized; current Python 3.10, macOS, cross-OS, dependency-lock, and built-package claims remain unqualified |
| Edge-runtime packaging decision | Loop 40 research freezes 7 qualification levels, 6 package layers, 4 backend profiles, 20 identity fields, 24 fixtures, 30 gates, and 40 refusals around the retained 1,130-parameter float32 reference | Planning research is complete while the experiment is `Not Started` and unauthorized; ExecuTorch/XNNPACK is a research lead only, with no selected target, export, package, inference, simulator, or hardware result |
| One-device qualification decision | Loop 42 selects the exact OpenBCI Cyton base 8-channel USB-radio path and freezes 28 identity fields, 7 timing observables, 10 anomalies, 4 stages, 34 gates, and 46 refusals | Current evidence is Q0 official-specification eligibility only; no device is owned, purchased, connected, streamed, or qualified, and no signal or decoding claim exists |
| Independent reproduction decision | Loop 43 freezes a future target-free NeuroToken causal-replay challenge with 7 qualification levels, 16 independence fields, 28 packet fields, 34 submission fields, commit-reveal ordering, 36 gates, and 48 refusals | Planning research is complete while the challenge is `Not Started` and unauthorized; a local validator incident parsed 136 cache JSON files, including 11 known consumed session-2 report/metadata files, but no content was used for tuning, scoring, or claim selection |
| Claim and release decision | Loop 44 binds 16 claim cards to 7 evidence levels, 5 model cards, 4 dataset cards, 14 release gates, and 8 risks | Artifact review is complete; engineering release is held, scientific performance release is parked, and no tag, release, DOI, payload, or claim upgrade exists |
| Real predictive evidence | Both the same-person cross-session MEG model and the bounded S7 EEG classifier lose to no-signal controls | The current scientific result is negative, explicit, and frozen against post-hoc tuning |
| Local execution gate | Float16 preserved exact behavior but ran `1.170x` slower on the producer; qint8 cut payload to `47.1%` but changed behavior and ran `2.785x` slower | Float32 is retained, qualification stayed unopened, and Loop 24 is parked after the full run exceeded its 60-second cap |
| Next transport layer | Stage A is specified as 90 future schedule-by-fixture cases with 30 exact refusals under a 32 MiB cap | The decision packet is review-ready; no replay runtime, socket, board, or hardware path is authorized yet |

### The Next Scientific Tranche

Loops 45-64 are specified in
[`docs/LOOPS_45_64_SCIENTIFIC_ROADMAP.md`](docs/LOOPS_45_64_SCIENTIFIC_ROADMAP.md)
and `registries/next_scientific_loops.v0.json`. Loop 45 is complete at its
target-free mechanics boundary. Loops 46 and 47 are now parked after the one
registered S21 validation event failed its primary and attribution gates. Loop
48 completed one post-outcome artifact-only Stage A over four exact committed
JSON artifacts. The frozen eight-class tree selected descriptive `F5`
output-distribution instability; the 10,643-byte result is consumed and is not
a proven root cause.

The separate Stage B protocol was frozen in
`docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md` and
`registries/loop48_train_only_discrimination_contract.v0.json`. It starts from
the immutable five-hypothesis portfolio and additive H1-H6/T1 research, then
binds a deterministic 44-fit/11-check source-train split, exact model/control
inventory, prediction-before-target order, paired statistics, resource caps,
and stop rules. All 55 rows were used by earlier fits, so the new check split
is prospective only inside this execution; Stage B can reach at most E2
diagnostic evidence. The exact decision at `8d17342` and implementation at
`1d840e3` were separately pushed and remotely green before protected access.
The target-blind run then completed 20 fits, 4,800 optimizer steps, 35 model
inferences, five priors, and 41 prediction sets. Hash-only freeze commit
`00215b1` passed push CI `29461934145` and PR CI `29461935560` before the same
11 train-check targets opened once.

The consumed result in
`registries/loop48_train_only_discrimination_result.v0.json` supports `H4`,
stable but nonseparable representation, and records evidence against `H3`, the
four registered fixed timing offsets. The primary candidate reached macro CER
`0.953566` versus `0.822045` for its train-only prior, a `-0.131522` margin.
`H1`, `H2`, `H5`, and `H6` remain unresolved. The frozen Loop 50 router selects
`L50-R05`, so S24 acquisition is parked for this model family. Stage B is
consumed, no rerun is open, S24 remains metadata-only, and S25 remains sealed.
See `docs/LOOP_48_STAGE_B_RESULT.md`.

Stage C tested one narrower explanation for the failed family: the original
causal probe may have been starved of temporal context. After correction commit
`2836ecc` passed push CI `29467415680` and PR CI `29467416894`, the registered
synthetic gate ran once. The `7,692`-parameter, 470 ms causal temporal encoder reached
final CER `0.433333` and `1/8` exact sequences, versus CER `1.000000` and `0/8`
for the `7,568`-parameter zero-context ablation. The `0.566667` relative CER
improvement passed, along with replay, causality, mutation, resume, padding,
and resource checks. The candidate still failed the frozen absolute CER
`<=0.10` and exact-sequence `>=7/8` gates, so Stage C is consumed and parked
without tuning or rerun. The run took 7.829308 seconds internally, peaked at
310,509,568 bytes RSS, generated 83,132 bytes, and opened no real signal,
target, or cache. See `docs/LOOP_48_STAGE_C_SYNTHETIC_RESULT.md` and
`registries/loop48_stage_c_synthetic_result.v0.json`.

The accessible-modality path has now completed Loop 53. Authorization commit
`2a47bbc` and implementation commit `8ec5b1b` each passed push and PR CI before
the one registered invocation ran. The exact S20 BrainVision VHDR/EEG/VMRK
triplet plus MAT log totaled `96,090,264` bytes and matched every frozen path,
size, Git/LFS, and Xet identity. The pass took `3.629499` seconds, peaked at
`63,225,856` bytes RSS and `102,035,529` incremental disk bytes, and generated
an `8,265`-byte private receipt. Every header, marker, signal, MAT, target,
cache, split, model, training, inference, scoring, device, and rerun counter is
zero. Loop 53 is consumed with no rerun; see
`docs/LOOP_53_ACQUISITION_RESULT.md`.

Loop 54 planning research now defines what happens only after a clean Loop 53
receipt. The source audit found that MNE's standard BrainVision reader exposes
marker-derived annotations and that NeuroDecodeKit's historical Loop 19 bridge
also excludes EOG-named channels, loads MAT labels, reads signal, and writes
plaintext labels in one invocation. That path remains valid for its consumed
engineering result, but it is not eligible for a fresh scientific gate. The
new design requires a dependency-light VHDR-only parser, a target-blind signal-
quality pass that retains every channel, and an isolated VMRK+MAT reconciler
that emits no plaintext target values. At least 48 unique performed trials must
reconcile, event windows may not masquerade as independent trials, and Loop 54
creates no split or model. See `docs/LOOP_54_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop54_eeg_trial_geometry_research.v0.json`.

Loop 55 planning research then defines the scientific question that becomes
eligible only after Loop 54 reports at least 48 unambiguous performed trials.
It does not use one vague "EEG decoding" endpoint. The same future compact
model has two prospectively ordered tests: causal pre-keypress left/right-hand
prediction and harder 29-class performed-key prediction. The published
`[-200,+300] ms` keypress-centered window remains a noncausal diagnostic
because it includes post-keypress execution and feedback. Intended sentence
text is secondary; performed action is primary. The future gate requires a
grouped trial-level split, at most 10,000 parameters and 12 fits, twelve matched
no-signal/timing/corruption/peripheral conditions, exact paired final-trial
tests, and a committed, pushed, remotely green prediction freeze before final
targets open once. Even a clean key-level pass would establish only one-block
EEG sensor-signal dependence with known keypress onsets, not brain-specific
origin, continuous thought-to-text, generalization, real-time operation, or
home use. See `docs/LOOP_55_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop55_eeg_neural_effect_research.v0.json`.

The additive Loop 55 AI policy makes that future search more disciplined
without pretending it has run. One compact causal family remains fixed. An AI
proposer may eventually choose from a small preregistered recipe menu using at
most four aggregate train-inner rounds, while a deterministic local runner
retains all data access. Selection/final outcomes, raw protected EEG, trial
labels, intended text, language models, pretrained weights, and scientific
claim decisions remain unavailable to the agent. The currently implemented
surface validates synthetic manifests only:

```bash
neurodecode inspect-ai-research-policy
neurodecode validate-ai-research-proposal \
  --proposal fixtures/loop55_ai_synthetic_proposal.v0.json
```

The committed roundtrip reads 11,949 policy bytes and 1,771 proposal bytes,
takes approximately 0.001 seconds, peaks near 22 MB RSS, and records zero real
data, cache, model, training, inference, scoring, network, or device operations.
See `docs/LOOP_55_AI_ASSISTED_REPRESENTATION_RESEARCH.md` and
`registries/loop55_ai_research_policy.v0.json`.

Loop 56 planning research defines how to report whatever survives those gates
without pretending EEG and MEG are interchangeable. It freezes five classes:
shared proven artifact, shared interface only, modality-specific
requalification, unavailable, and prohibited inference. Its 12-level ladder
separates source identity, bounded reading, signal quality, trial integrity,
sensor-signal effect, key/text prediction, continuous input, causal incremental
output, measured end-to-end latency, local device mechanics, repeated at-home
feasibility, and assistive or clinical utility. Missing levels cannot be
skipped. The current provisional route is mechanics and interfaces only:
registered local MEG and historical EEG predictors both lost to no-signal
comparators, but they are not a matched modality comparison, and fresh S20 EEG
is acquired but remains uninterpreted. A future final verdict may read only
hash-bound committed aggregate reports after Loop 55 closes and a separate Tier
C claim decision is green. See `docs/LOOP_56_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop56_cross_modality_accessibility_research.v0.json`.

Loop 49 planning research now selects S24 session 2 block 2 as the preferred
permanently development-only participant from pinned public metadata. The exact
two-file bundle is `1,048,579,727` bytes, `293,597,553` bytes below its 1.25 GiB
cap. S24 is preferred over the `29,701,559`-byte-smaller S18 pair because S18
belongs to the published S1/S18 alias group; S25 remains the final-only person.
The future recommendation assigns 16 canonical sentence groups to development
selection, all remaining usable groups to fit, and excludes any matching S21
selection text from future fit. No S24 local path, payload, header, signal, MAT
content, target, split, model, or training operation occurred. The `>=48`
unique-row floor and compatibility fields remain unavailable, so Loop 49 is
planning-complete but experimentally `Not Started`, unpreregistered, and
unauthorized. See `docs/LOOP_49_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop49_research_boundary.v0.json`. Planning commit `5afa61e` passed
push CI `29454969710` and PR #27 CI `29455166081`, with both required jobs green.

Loop 50 planning research is complete in
[`docs/LOOP_50_PRIMARY_SOURCE_RESEARCH.md`](docs/LOOP_50_PRIMARY_SOURCE_RESEARCH.md)
and `registries/loop50_research_boundary.v0.json`, while the experiment remains
`Not Started`. The future design globally groups identical text across people,
uses five historical S21 out-of-fold folds plus one 16-group S24 development
qualification, weights S21 and S24 equally, forbids participant-conditioned
model paths and target-corpus normalization, and requires both participants and
the worst-person margin to pass. Primary seed `5001` cannot be replaced by the
two stability seeds. Five pooled out-of-fold fits, three pooled final fits, six
linear fits, and six S21-only fits bound the recommendation to 20 parameter-
update runs; the four-run gap below the absolute cap is not rerun permission.
Pooled gain cannot rescue a failed person. Stage B has now closed at route
`L50-R05`: stable nonseparability parks S24 acquisition for this model family.
The Loop 50 planning snapshot still correctly preserves 31 false authorization
fields and zero protected/model counters; no S24 or S25 operation is open.
Planning commit `085f341` passed push CI `29458102674` and PR #28 CI
`29458116994`, with Base Python and Optional Neuro Readers green in both.

| Phase | Loops | Decisive goal |
|---|---:|---|
| Real Signal Truth | 45-48 | Qualify causality, then require frozen S21 validation to beat no-signal and corrupted-signal controls |
| Unseen-Person Verdict | 49-52 | Add one nonfinal development person, freeze once, and make one final-only S25 decision |
| Accessible EEG Evidence | 53-56 | Acquire fresh S20 only after approval and test EEG without borrowing a MEG claim |
| Causal Local Use | 57-60 | Prove stream parity, device mechanics, measured latency, and home acquisition as separate claims |
| Independent Evidence And Release | 61-64 | Cross-machine qualify, reproduce externally, define replication, and promote only supported claims |

If S21 validation does not beat the prior and every signal corruption, model
scaling stops and failure localization begins. S25 stays sealed until a multi-
person source model is fully frozen; a failed final gate becomes the durable
negative result and S25 is never repurposed for calibration.

### Detailed Engineering Scorecard

| Result | Measured evidence | Proof label | Why it matters |
|---|---|---|---|
| Complete S21 trial reconciliation | 66/66 session-1 trials; 63/63 performed session-2 trials; empty MAT slots 54, 58, and 60 preserved | real-data validated | Turns ambiguous trigger/log ordering into exact trial provenance instead of fuzzy text matching |
| Task-matched EEG bridge | 2,534 MAT triggers aligned; 2,197 windows; `2197 x 61 x 25`; 12,428,800-byte cache | real-data validated | Proves bounded BrainVision plus MAT mechanics on EEG without pretending the classifier succeeded |
| Sampling-rate characterization | identical 66-row caches at 100/50/25 Hz; 1,663,209 / 846,334 / 431,451 bytes | real-data validated | Quantifies storage and temporal feasibility without selecting a rate from unmeasured accuracy |
| Geometry-aware channel subsets | one 102-magnetometer base plus 20 exact-identity subset caches under 128 MiB | real-data validated | Makes sensor-cost tradeoffs inspectable while keeping geometry proxies separate from decoding claims |
| Precision/storage sweep | qint16 is 49.84% smaller; qint8 is 80.75% smaller with worst relative RMSE 0.9531%; no clipping | real-data cache mechanics | Measures representation distortion without calling it retained model accuracy |
| NeuroTokenCache v0 | `48 x 16 x 32`; 76,646 bytes; exact payload replay; zero target-member reads | fixture-backed interface | Establishes a strict modality/timing/mask/split/hash contract without unreleased embeddings |
| Causal frame replay | 553 canonical frames; 5/5 schedules exact; zero right context; 300-byte mutable state | synthetic mechanism only | Separates true producer causality from transport scheduling and decoder latency |
| Tiny learned causal producer | 1,130 parameters; validation and one-time test balanced accuracy 1.0 versus 0.166667 signal-free prior; 5/5 replay | synthetic mechanism only | Proves the bounded stream can carry a learned signal on an intentionally easy generated task |
| Blank calibration mechanism | validation and one-time test both 16/16 exact at CER 0; 9 test corrections; 0 regressions | synthetic mechanism only | Shows one preregistered scalar can solve a specific tail-error mechanism without post-test trimming |
| Local precision/runtime gate | 3 exact candidates; 12/12 balanced rounds; 990 frames; float16 exact but full path `1.088x`; qint8 payload `47.1%` but full path `1.812x` and incorrect; qualification 0 opens | parked target-free synthetic result | Demonstrates why payload size, correctness, steady-state speed, and orchestration cost must be separate gates |
| Metadata-only local intake | 6 format families; 532 source bytes; 11,545 report bytes; 0 binary/raw/target/model/network reads | fixture-backed | Lets EEG owners start with safe structure and provenance instead of uploading a recording |
| Bounded signal-quality interface | 40 fixtures; 38 readable and 2 exact refusals across 6 format families; 3.839 sec; 76,592 output bytes | fixture-backed | Validates readers, metrics, privacy, caps, and no-mutation identity before any real quality claim |
| Replay/live-source authorization gate | 5 schedules x 18 fixture families = 90 future cases; 30 refusal IDs; 4 separately gated stages; 10 invariants | review-ready, not authorized | Binds the exact Stage A scope and caps before any source-chunk, socket, board, fixture, or hardware implementation |
| Causal preprocessing v1 | 4 anti-alias and 9 total SOS sections; 65,537 response points; 23/23 alias probes; 24/24 target-free items; 168 schedules; 240 resumes; 72 mutation controls; 0 protected reads | completed target-free synthetic mechanics | Establishes one strict, resumable 1000-to-100 Hz causal path with zero right context while leaving retained neural information and decoding performance unproven |
| Loop 26/31/33 shared validation gate | 55/6/5 source split; 2,908/2,884-parameter models; 21 fits; 24 target-blind inferences; six priors; 31 frozen prediction sets; one post-freeze six-target score; candidate/prior macro CER `0.938177/0.751235` | consumed negative result; all three gates parked; no rerun | Proves the target firewall and bounded research runtime work while showing this exact predictive design does not beat an honest no-signal baseline |
| Loop 48 artifact-only failure localization | 4 exact committed JSON inputs; 155,545 input bytes; 18 blank fractions; 6 fixed-prefix ranges; `F5`; 0.016568875 sec; 23,429,120-byte peak RSS; 10,643 output bytes; 0 protected/model/training operations | consumed post-outcome descriptive result; no rerun | Reproduces the failure phenotype mechanically while keeping causal root cause, neural advantage, and every decoding or device claim explicitly unavailable |
| Loop 48 Stage B failure discrimination | 44 fit / 11 check rows; prefixes `8,16,24,32,44`; seeds `4801-4803`; 20 fits; 4,800 steps; 35 target-blind inferences; 5 priors; 41 frozen sets; one post-freeze 11-target score; candidate/prior macro CER `0.953566/0.822045` | consumed E2 diagnostic; `H4` supported, `H3` evidence against, `L50-R05` parks S24 for this family; no rerun | Distinguishes stable nonseparability from a simple fixed timing offset while preserving the negative neural result and refusing independent-validation or neural-advantage wording |
| Loop 48 Stage C synthetic representation gate | 40 synthetic rows; 24/8/8 split; 4 fits; 1,680 steps; candidate/ablation CER `0.433333/1.000000`; candidate exact `1/8`; replay, mutation, resume, causality, padding, and resource checks passed | consumed synthetic gate; absolute CER and exact-sequence gates failed; no rerun | Shows the causal temporal model can use ordered synthetic history while refusing to transfer that contrast into a real neural-decoding claim |
| Loop 53 fresh EEG acquisition result | 4 exact S20 files; 96,090,264 network/final bytes; 3.629499 sec; 63,225,856-byte peak RSS; 102,035,529-byte peak disk; 8,265 receipt bytes; all 10 gates passed | consumed acquisition-mechanics pass; one invocation; no rerun; zero interpretive or model operations | Establishes a reproducible local EEG byte bundle while keeping header, geometry, signal, target, cache, model, and scientific decisions closed |
| Loop 49 development-person boundary | 396 pinned metadata rows; S24 session 2 block 2; 2 exact files; 1,048,579,727 bytes; 293,597,553-byte cap margin; 16 future selection groups; 32 minimum fit groups; 25 false authorization fields | metadata research only; experiment `Not Started` | Creates a clean development-person path without consuming final-only S25, while keeping trial count, channels, geometry, targets, signal, models, and transfer claims closed |
| Loop 50 multi-source research boundary | 6 primary sources; 5 S21 out-of-fold folds; 16 future S24 selection groups; 10 fixed conditions; 20 parameter-update runs; seeds `5001-5003`; 30 refusals; 31 false authorization fields | planning research only; experiment `Not Started` | Defines a text-leakage-resistant, participant-balanced, worst-person-gated development experiment while keeping S24/S25 payloads, model choice, training, scoring, and claims closed |
| Loop 27 fresh-holdout boundary | 315 pinned MEG metadata entries; 23 strict single-FIF/log pairs; 16 eligible; S25 selected at 1,009,939,983 bytes; S23 excluded; 18 false authorization fields | metadata research only | Finds the smallest honest same-modality transfer candidate while keeping its local MAT payload, remote FIF, targets, and backups sealed |
| Loop 28 transfer boundary | T0-T3 taxonomy; strict zero-shot/transductive split; 48-row floor; 0.05 macro-CER margin; 65,535 paired assignments plus observed; 4 comparators; 21 false authorization fields | planning research only | Makes the future one-time S25 decision falsifiable while reserving calibrated transfer for a physically separate design |
| Loop 29 portability boundary | 15 modality requirements; 4 profiles; 6 qualification levels; 12 future packet gates; 24 false authorization fields; 5,000,000,000-byte preferred storage ceiling | planning research only | Chooses EEG as the immediate local-first lane and OPM-MEG as a partner/lab lane without treating channel ablation, vendor specifications, or home acquisition as text decoding |
| Loop 30 replay interaction boundary | 4 source modes; 30 event fields; 9 clock domains; 6 latency levels; 18 future gates; 30 refusals; 30 false authorization fields | planning research only | Defines how a future target-free local replay can show revisions, finalization, clocks, privacy, and proof posture without implying live or low-latency neural decoding |
| Loop 31 neural-attribution boundary | 10 encoder conditions; zero/timing controls passed individually; prior, row/channel/time/target conjunction failed; 5 contingent LLM conditions remained closed | consumed shared gate; parked | Separates useful diagnostic components from the failed claim-level conjunction and blocks sensor-signal or brain-origin overclaiming |
| Loop 48 failure-localization boundary | primary blank `0.993477`; all-condition blank range `0.997146`; all 6 prefix groups cross `0.25` seed dispersion; 17 unavailable root-cause fields; 30 refusals | one consumed artifact-only Stage A; descriptive `F5`; no rerun | Reproduces model-fit/output-distribution instability as the leading artifact phenotype while refusing to call CTC, preprocessing, signal quality, or weak neural information the proven cause |
| Loop 48 hypothesis-discrimination boundary | 6 coexisting hypotheses; 1 orthogonal shortcut threat; 5 evidence levels; 6 sequential shared-evidence stages; 5 primary-source bindings; 15 false authorization fields | additive design research only | Separates fixed-recipe, quality, timing, representation, prior, and data-regime explanations while capping any future Stage B result below brain-specific origin |
| Loop 34 confidence boundary | 7 confidence semantics; 8 score/control roles; recommended fresh `128/64/256` synthetic partitions; 20 future gates; 30 refusals; 26 false authorization fields | planning research only; confidence unavailable | Separates ranking, calibrated probability, abstention, conformal risk, revision stability, and product confidence while refusing reuse of six real validation rows |
| Loop 35 peripheral-confound boundary | 10 confound classes; 9 future synchronized stream classes; 13 conditions; 3 stages; 24 future gates; 32 refusals; 31 false authorization fields | planning research only; complete real controls unavailable | Requires timing, ocular, distal/proximal muscle, motion, audio/environment, and combined nonbrain comparators before any bounded incremental brain-sensor claim |
| Loop 36 geometry/reference boundary | 6 representation layers; 5 modality profiles; 24 channel fields; 12 operation classes; 16 fixture families; 22 gates; 30 refusals; 29 false authorization fields | planning research only; complete real metadata unavailable | Separates identity-preserving metadata operations from signal scaling, rereference, compensation, interpolation, model transfer, and device-equivalence claims |
| Loop 37 BIDS provenance boundary | 6 export layers; 5 artifact profiles; 15 stable BIDS fields; 16 explicit NeuroDecodeKit extension fields; 20 fixture families; 4 stages; 24 gates; 32 refusals; 29 false authorization fields | planning research only; no derivative tree exists | Separates a standards-valid dataset envelope from non-standard NPZ/report payloads while refusing raw copies, local paths, target text, invented source URIs, and release overclaims |
| Loop 38 privacy/lifecycle boundary | 5 sensitivity levels; 8 artifact classes; 10 lifecycle surfaces; 12 sensitive-field classes; 12 threats; 5 receipt levels; 24 fixtures; 4 stages; 26 gates; 36 refusals; 32 false authorization fields | planning research only; copies outside current Git metadata remain unresolved | Separates redaction, de-identification, local path receipts, repository coordination, media sanitization, consent, license, and sharing authority |
| Loop 39 reproducibility boundary | 7 qualification levels; 18 environment fields; 8 output classes; 6 comparison classes; 6 future cells; 20 fixtures; 4 stages; 28 gates; 38 refusals; 36 false authorization fields | planning research only; no matrix cell has run | Separates semantic identity, field-specific numerical compatibility, descriptive resources, same-team repeatability, supported-matrix compatibility, independent reproduction, and scientific replication |
| Loop 40 edge-package boundary | 7 qualification levels; 6 package layers; 4 unselected backends; 20 identity fields; 8 outputs; 6 comparisons; 24 fixtures; 4 stages; 30 gates; 40 refusals; 40 false authorization fields | planning research only; no backend, target, export, package, or inference exists | Separates graph export from host normalization/state/timestamps/decoder, total deployment cost from model bytes, simulator evidence from physical devices, and packaging from science |
| Loop 41 stream-to-token boundary | 6 integration layers; 7 clock views; 8 anomaly classes; 5 schedules; 5 resume cuts; 18 hash bindings; 28 fixtures; 4 stages; 32 gates; 42 refusals; 42 false authorization fields | planning research only; no source chunk, adapter, preprocessing output, NeuroToken runtime, stream, or latency result exists | Preserves source time, derived corrections, anomaly evidence, resume state, and provenance without calling replay scheduling capture-to-text latency |
| Loop 42 named-device boundary | OpenBCI Cyton base 8-channel USB-radio; Q0 only; 28 identity fields; 16 packet fields; 7 timing observables; 10 anomalies; 30 fixtures; 4 stages; 34 gates; 46 refusals; 45 false authorization fields | planning research only; no purchase, SDK, serial read, board connection, participant, recording, or device result exists | Makes a future local-device mechanics test exact while refusing to turn host timestamps, local files, connectivity, or eight channels into latency, privacy, EEG-quality, or text-decoding claims |
| Loop 43 independent-reproduction boundary | 7 qualification levels; 16 independence fields; 28 packet fields; 34 submission fields; 8 comparison classes; 12 discrepancy classes; 32 fixtures; 4 stages; 36 gates; 48 refusals; 48 false authorization fields | planning research only; no packet, oracle, outreach, contributor, submission, adjudication, archive, or release exists | Defines how one future external environment can reproduce a released target-free software artifact without inflating that result into scientific replication, neural advantage, or population generalization |
| Loop 44 claim-release matrix | 16 claims; 7 evidence levels; 5 model cards; 4 dataset cards; 14 gates; 8 risks; 0 tag/release/DOI operations | artifact-only review complete; engineering release held; scientific release parked | Makes every public claim traceable to cohort, task, split, comparator, uncertainty, resources, access, privacy, license, and evidence while preserving negative results |
| Current Loop 48 Stage B verification | 63 focused Stage B tests; complete dependency-light suite 887 tests with 149 expected skips; complete optional-neuro suite 934 tests with 3 expected skips | Authorization `8d17342`, implementation `1d840e3`, freeze `00215b1`, and result closeout `ad4410c` passed both push and PR CI; closeout runs were `29464527230` / `29464529524` and added exactly 9 tests over the implementation baseline | Makes one-shot access order, target isolation, freeze binding, exact operation counts, hypothesis rules, outcome routing, tamper checks, and the no-rerun boundary executable and reviewable |
| Current Loop 48 Stage C verification | 64 focused tests; 919 dependency-light tests with 156 expected skips; 966 optional-neuro tests with 3 expected skips | Research `9579be9`, implementation `59b30a3`, and correction `2836ecc` passed push and PR CI before one execution; result is consumed and no rerun is open | Makes synthetic selection, absolute-gate failure, replay, causal controls, resource accounting, zero protected access, and the parked disposition machine-checkable |
| Current Loop 53 verification | 68 focused closeout tests; final full suite 1,062 tests with 3 expected skips in 44.090 sec and 581,648,384-byte external peak RSS; baseline was 1,056 tests, 3 skips, 30.623 sec, and 568,688,640 bytes | Authorization `2a47bbc` passed CI `29589212626` / `29589225113`; implementation `8ec5b1b` passed CI `29591387642` / `29591391286` before the single pass; workbook formula-error scan found 0 matches | Adds exactly 6 aggregate-result tests while making identity, green-gate order, no-overwrite behavior, caps, opaque hashing, counters, private receipt binding, no-rerun status, and claim ceiling machine-checkable |

### Real-Data Scientific Scorecard

| Evaluation | Neural result | No-signal result | Honest decision |
|---|---:|---:|---|
| S21 session-1 strict five-row sentence test | 163 character edits | 164 character edits | Near-null difference; paired interval spans benefit and harm |
| S21 session-2 same-person transfer | CER `0.9179` | CER `0.7755` | Neural model is materially worse; session is consumed |
| S7 EEG within-session key events | exact accuracy `0.91%` | exact accuracy `12.27%` | Neural template is materially worse; EEG bridge is mechanics only |
| S21 session-1 reserved six-sentence gate | macro CER `0.938177` | macro CER `0.751235` | Fixed causal candidate is worse by `0.186942`; Loops 26/31/33 are consumed and parked |
| S21 source-train 11-row diagnostic | macro CER `0.953566` | macro CER `0.822045` | Post-outcome Stage B supports stable nonseparability for this model family; these historically used rows are not fresh validation |

**Scientific headline:** the real MEG and EEG evaluations run so far do not
show a reliable neural advantage. That negative result is preserved beside the
engineering wins, not hidden behind synthetic accuracy.

### Resource Highlights

| Gate | Runtime | Peak RSS | Persistent output |
|---|---:|---:|---:|
| Dependency-light Python unittest run | 1.80 sec wall | 107,659,264 bytes | 637 tests with 124 expected optional skips; temporary output only |
| RW1 metadata intake roundtrip | 0.001659 sec | 21,643,264 bytes | 11,545 bytes |
| RW2 bounded FIF quality roundtrip | 3.839168 sec | 150,749,184 bytes | 76,592 bytes |
| RW3 contract/request invariant suite | 0.040 sec | 20,529,152 bytes | no generated payload |
| Loop 24 authorization plus frozen-boundary suite | 0.210 sec | 21,397,504 bytes | no generated payload |
| Loop 25 v1 amendment plus immutable-v0 request suite | 0.120 sec | 22,560,768 bytes | no generated payload |
| Loop 25 registered static plus complete gates | 5.542175 sec internal | 136,806,400 bytes max | 788,967 generated bytes; 24/24 items, all caps and 23 counters exact |
| Loop 26 research plus roadmap/Loop 25 boundary suite | 0.140 sec wall max | 22,986,752 bytes max | no generated payload |
| Loop 27 pinned metadata selector | 3.100 sec wall | 63,766,528 bytes | zero downloaded payload bytes |
| Loop 24-36 focused boundary suite | 3.74 sec wall | 240,041,984 bytes | 248 tests; no generated experiment payload |
| Loop 36 plus roadmap invariants | 0.07 sec wall | 20,365,312 bytes | 26 tests; no fixture, real header, protected cache, signal, transform, rereference, interpolation, target, model, training, device, or hardware operation |
| Loop 24-37 planning boundary suite | 0.20 sec wall | 50,167,808 bytes | 226 tests; no generated experiment payload |
| Loop 37 plus roadmap invariants | 0.09 sec wall | 34,865,152 bytes | 26 tests; no fixture, exporter, derivative tree, validator, protected payload, raw copy, release, model, training, device, or hardware operation |
| Loop 24-38 planning boundary suite | 0.16 sec wall | 58,589,184 bytes | 240 tests; no generated experiment payload |
| Loop 38 plus roadmap invariants | 0.07 sec wall | 34,390,016 bytes | 23 tests; no fixture, scanner, deletion, protected-root scan, identity attack, history rewrite, release, model, training, device, or hardware operation |
| Loop 24-39 planning boundary suite | 0.25 sec wall | 66,093,056 bytes | 256 tests; no generated experiment payload |
| Loop 39 plus roadmap invariants | 0.09 sec wall | 34,930,688 bytes | 25 tests; no fixture, environment manifest, matrix job, dependency lock, package build, protected payload, model, training, independent reproducer, edge, device, or hardware operation |
| Loop 24-40 planning boundary suite | 1.28 sec wall | 74,825,728 bytes | 269 tests; no generated experiment payload |
| Loop 40 plus roadmap invariants | 1.10 sec wall | 42,139,648 bytes | 22 tests; zero fixtures, installs, exports, packages, inference, profiler, simulator, device, or hardware operations |
| Loop 24-42 planning boundary suite | 1.99 sec wall | 88,997,888 bytes | 263 tests; zero generated experiment, protected-data, model, stream, participant, device, or hardware operations |
| Loop 42 plus roadmap invariants | 0.043 sec internal | not separately measured | 24 tests; zero SDK imports, fixtures, playback, serial reads, discovery, connections, recordings, model runs, or latency measurements |
| Loop 24-43 planning boundary suite | 1.33 sec wall | 91,504,640 bytes | 308 tests; no generated experiment payload, model, training, stream, device, or hardware operation |
| Loop 43 plus roadmap invariants | 0.049 sec internal | not separately measured | 24 tests; 48 false authorizations, 20 false roadmap executions, and the 136/11-file validator incident machine-recorded |
| Loop 48 contract plus roadmap invariants | 0.009 sec internal | not separately measured | 25 tests; 4 exact aggregate artifacts, 8 ordered classes, 17 unavailable root-cause fields, 30 refusals, and every execution authorization false |
| Loop 48 hypothesis-discrimination invariants | 0.004 sec internal | not separately measured | 10 tests; 6 unresolved hypotheses, 1 orthogonal shortcut threat, 5 evidence levels, 6 sequential stages, 5 public sources, 15 false authorizations, and zero protected/model operations |
| Loop 48 artifact-only Stage A | 0.016568875 sec internal / 0.38 sec wall | 23,429,120 bytes internal / 23,560,192 bytes external | 155,545 input bytes; 10,643-byte aggregate report; `F5`; 0 model, training, target, protected, network, stream, device, or hardware operations |
| Loop 48 train-only Stage B | 190.140486 sec through prediction freeze; 0.112110 sec scoring | 483,540,992 bytes maximum | 20 fits; 4,800 steps; 35 inferences; 41 frozen sets; 9,623,773 generated bytes; one 10,632,576-byte cache hash pass; one post-freeze target delivery; no rerun |
| Loop 48 synthetic Stage C | 7.829308 sec internal / 8.31 sec wall | 310,509,568 bytes internal / 320,405,504 bytes external | 4 fits; 1,680 steps; 8 inferences; 83,132 generated bytes; 0 raw, real-cache, real-signal, real-target, download, S24/S25, stream, device, or hardware operations; no rerun |
| Loop 49 metadata-only candidate pass | 3.51 sec wall | 62,685,184 bytes | 396 pinned metadata rows; exact 1,048,579,727-byte future S24 bundle; 0 payload downloads, local candidate stats, real reads, targets, derivatives, models, training, predictions, or scores |
| Loop 44 plus Loops 45-64 invariants | 0.06 sec wall | 18,546,688 bytes | 24 tests; 16 claim cards, 20 false roadmap execution flags, and 9 false global authorizations |
| Loop 28 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 10 web operations, 1 GitHub metadata call, zero code/data payload bytes |
| Loop 29 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 14 public web operations, zero protected data/model/device operations, zero downloaded payload bytes |
| Loop 30 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 10 public web operations, zero trace/server/browser/protected-data/model/stream operations, zero downloaded payload bytes |
| Loop 31 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 16 public network operations including 8 GitHub API requests; zero protected-data/model/training/validation/LLM operations and zero downloaded data/model bytes |
| Loop 32 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 6 public network operations including 2 pinned GitHub source reads; zero participant/cache/signal/target/model/adapter/training/evaluation operations |
| Loop 33 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 6 public web operations; zero protected cache/signal/target/model/training/scoring/acquisition/device operations |
| Loop 34 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 5 public web operations; zero fixture/protected-data/target/model/confidence-fit/scoring/product-confidence/device operations |
| Loop 35 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 6 public web operations; zero protected-data/target/model/training/acquisition/S20/S25/stream/device/hardware operations |
| Loop 36 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 3 high-level public web operations; zero protected download bytes, real headers, signal/cache/target reads, fixtures, transforms, model/training runs, S20/S25 operations, streams, devices, or hardware operations |
| Loop 37 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 7 high-level public web operations including 2 official GitHub repository reads; zero protected downloads, payload/header/cache/signal/target reads, fixtures, derivative bytes, raw copies, validator/model/training runs, releases, devices, or hardware operations |
| Loop 38 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 6 high-level public web operations and 8 official/primary page opens; zero protected reads, fixtures, scanners, deletions, identity attacks, history rewrites, models, training runs, releases, uploads, devices, or hardware operations |
| Loop 39 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 6 high-level public web operations and 8 official/primary page opens; zero fixtures, manifests, matrix jobs, installs, lockfiles, package builds, protected reads, models, training runs, edge, stream, device, or hardware operations |
| Loop 40 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 3 high-level web operations and 12 official/primary page opens; zero fixtures, installs, exports, packages, inference, profiler, memory-planner, delegate, simulator, app, protected-data, model, training, device, or hardware operations |
| Loop 42 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 4 high-level web operations, 12 search queries, and 9 official page opens; zero SDK, fixture, device, participant, signal, target, model, training, decoder, stream, network/cloud, or hardware operations |
| Loop 43 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 5 high-level web operations, 8 search queries, 10 official/primary page opens, and 4 GitHub metadata operations; local validation later parsed 136 cache JSON files including 11 known consumed session-2 files, with zero tuning/scoring/model use |
| Loop 24 registered selection | 65.154951 sec internal | 222,248,960 bytes max worker | 262,822 bytes fixture plus output |
| Current Loop 25 full unittest runner | 26.17 sec wall | 618,528,768 bytes | 684 tests with 3 expected skips; temporary output only |

Proof labels are deliberately narrow:

- **real-data validated** means the named interface or identity claim ran on the
  exact local recording described;
- **fixture-backed** means deterministic generated files exercised the contract;
- **synthetic mechanism only** means the result cannot be transferred to brain
  data, people, or devices;
- **review-ready, not authorized** means the bounded protocol and decision packet
  exist, but their planned runtime does not;
- **preregistered, no runtime** means candidates, data independence, metrics,
  thresholds, and refusals are frozen before any candidate implementation or
  benchmark execution;
- **authorized, no runtime** means a separate hash-bound decision permits the
  exact frozen work after its commit is pushed, but no fixture, candidate, or
  measurement result exists yet;
- **parked** means a registered primary gate failed and the project did not tune
  past it.

Detailed evidence is linked from the
[documentation map](#documentation-map), including
[the RW2 closeout](docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md).

## Current Proof Boundary

Read this before interpreting any number in the repository.

### What Is Established

- **Base package:** dependency-free CLI, metrics, schemas, manifests, split
  audits, and report validation run without MNE, Torch, Zarr, or Hugging Face.
- **Real S21 MEG alignment:** all 66 performed session-1 trials are reconciled
  to target/response/timing provenance under the validated S21 parser.
- **Strict split mechanics:** session 1 has a deterministic 55/6/5
  train/validation/test protocol with train-only preprocessing.
- **Independent same-person session mechanics:** session 2 has 63 performed
  trials, preserves three empty MAT slots, and is bound to frozen session-1
  train statistics.
- **Real EEG bridge mechanics:** one S7 BrainVision recording and matching MAT
  log produce 2,197 lazily read key-event windows shaped `61 x 25`.
- **NeuroTokenCache v0:** a strict modality-aware continuous embedding cache
  preserves masks, lengths, timestamps, source identities, geometry status,
  splits, configuration, hashes, causality, context, resources, and warnings.
- **Causal producer mechanics:** synthetic replay proves schedule-invariant
  causal frame production with zero right context and bounded state.
- **Metadata-only neurodata intake:** BrainVision, EDF/EDF+, BDF, continuous
  EEGLAB external-FDT, FIF, and BIDS bundles can be recognized and reported at
  compatibility level 0 without reading binary samples or event content.
- **Synthetic signal-quality adapters:** RW2 exercises 38 readable fixtures and
  two frozen refusal fixtures across those six format families using bounded
  optional MNE readers, strict source binding, descriptive metrics, privacy
  redaction, and before/after no-mutation checks.
- **RW3 protocol registration:** a versioned, machine-checked contract freezes
  source identity, raw/corrected/arrival timestamps, gaps, duplicates,
  reordering, reconnects, state, five schedules, 18 future fixture families,
  30 refusal IDs, and four separately gated adapter stages. No source-chunk or
  adapter runtime exists yet.
- **RW3 Stage A decision packet:** a hash-bound request now defines 90 future
  schedule-by-fixture cases, all 30 deterministic refusals, one-thread resource
  caps, and the exact authorization sequence. The request says
  `authorized_now: false`; preparing it did not authorize implementation.
- **Loop 24 precision/runtime execution:** the frozen target-free gate ran all
  12 balanced selection rounds over 990 frames. Float16 preserved every exact
  decoder behavior and tolerance but was slower; QNNPACK qint8 exposed the
  required operator and halved payload but failed behavior/numerical gates and
  was much slower. No candidate earned qualification, seed 2402 remained
  physically unopened, and the final gate parked at `65.154951` seconds versus
  its 60-second cap. Real data, targets, training, energy measurement, RW3,
  devices, and hardware remained outside Loop 24.
- **Loop 25 causal-preprocessing result:** the original registration at
  `a36d97b` remains immutable history; v1 amendment `b6b92d8`, authorization
  commit `1e7296a`, and implementation commit `439f151` preserve the complete
  audit trail. The static gate passed before either partition opened; seed
  2501 development then passed and froze, and seed 2502 qualification passed
  once unchanged. Across 24 target-free items, all 168 schedule, 240 resume,
  and 72 future-mutation checks passed with zero protected reads. Generated
  output was 788,967 bytes and maximum RSS was 136,806,400 bytes. Loop 25 is
  complete, consumed, and not authorized for rerun.
- **Loop 26/31/33 shared validation:** green commit `881145d` freezes the
  left-padded 2,908-parameter candidate, 2,884-parameter comparator, 21 fits,
  24 target-blind model inferences, six train-only priors, 31 prediction sets,
  ten encoder conditions, six nested data sizes, and one six-target scoring
  delivery after a green prediction freeze. The exact request was separately
  authorized at green commit `1c0e52c`; implementation `91409bd`, static-ledger
  correction `4015677`, and prediction-freeze commit `54bdca9` were pushed and
  remotely green before the targets opened once. The candidate macro CER was
  `0.938177` versus `0.751235` for the train-only prior, a `-0.186942` margin.
  The primary, attribution-conjunction, and scaling gates failed. The event is
  consumed, all three loops are parked, and no rerun or post-target tuning is
  authorized. See `docs/LOOP_26_SHARED_VALIDATION_RESULT.md`.
- **Loop 48 Stage B failure discrimination:** one exact train-only execution
  split the historically used 55 source-train rows into 44 fit and 11
  target-withheld check rows, froze 41 prediction sets at remotely green commit
  `00215b1`, then scored the same 11 targets once. The primary candidate reached
  macro CER `0.953566` versus prior `0.822045`. All six full-size causal and
  linear fits were finite and stable but lost their prior rule, supporting
  `H4` stable nonseparability. None of four fixed timing offsets improved all
  three seeds, providing evidence against registered `H3`. The complete
  signal-control conjunction failed, so no neural advantage or sensor-signal
  dependence is established. Route `L50-R05` parks S24 acquisition for this
  model family. Stage B is consumed with no rerun.
- **Loop 27 planning research:** pinned official metadata selects S25 session 2
  block 2 as the smallest eligible clean MEG candidate after excluding observed
  S21 identity, consumed S7, and the official S23 metallic-implant case. Exact
  paths, bytes, LFS hashes, identity, license, task, unavailable fields, and 18
  false authorization flags are machine checked. No candidate payload opened.
- **Loop 28 planning research:** the future S25 question is T2 strict unseen-
  person zero-shot, not calibrated transfer. The frozen recommendation requires
  zero target-person fit, at least 48 final rows, at least 0.05 macro sentence-
  CER improvement over the source-train-only prior, 65,535 deterministic paired
  assignments plus observed, and strict wins over three signal corruptions.
  All 21 authorization flags remain false and the experiment is `Not Started`.
- **Loop 29 planning research:** the portability map keeps cryogenic MEG,
  OPM-MEG, scalp EEG, and peripheral inputs noninterchangeable. Scalp EEG is
  the immediate local-first research lane; OPM-MEG remains a specialist
  partner/lab lane. The exact S20 and S25 future bundles total 1,106,030,247
  bytes inside the user's 5-10 GB storage envelope, but the envelope is not
  download permission. All 24 authorization flags remain false, no device is
  selected, and the experiment is `Not Started`.
- **Loop 53 fresh EEG acquisition:** authorization `2a47bbc` and implementation
  `8ec5b1b` were separately green before the one registered invocation acquired
  and opaque-verified all 4 files and `96,090,264` bytes. All 10 gates passed in
  `3.629499` seconds at 63,225,856-byte peak RSS. The gate is consumed with no
  rerun; header, marker, signal, MAT, target, cache, split, model, training,
  inference, scoring, and device counters all remain zero.
- **Loop 54 EEG qualification research:** planning commit `aec440a` freezes
  four ordered future stages, five sensitivity classes, 22 acceptance gates,
  30 refusal IDs, a 48-unique-trial floor, all-channel preservation, and a
  32 MiB public-output ceiling. VMRK descriptions and MAT behavior/target fields
  are target-bearing, MNE is forbidden from the VHDR-only stage, and exact
  Loop 55 split counts remain intentionally unfrozen until the target-blind
  usable-trial count exists. Loop 53 has completed cleanly, but no Loop 54 real
  stage or scientific result is authorized. Documentation-sync commit `b6785d7`
  passed push CI `29471589279` and PR #32 CI `29471598364`, with Base Python
  and Optional Neuro Readers green in both workflows.
- **Loop 55 EEG neural-effect research:** planning commit `f3158c7` freezes two
  ordered causal endpoints from the same future final trials: performed-hand
  error and 29-class performed-key keypress-aligned CER. It makes performed
  action primary, keeps intended text secondary, and treats `[-200,+300] ms`
  as a noncausal diagnostic only. A future execution needs at least 48 Loop 54-
  qualified trials, a grouped split, one `<=10,000`-parameter family, at most
  12 fits, twelve matched conditions, exact trial-level tests, and a remotely
  green hash-only prediction freeze before one final target delivery. Planning
  currently passes 24 focused roadmap/contract tests plus 9 public-status
  subtests, and the full local suite passes 1007 tests with 3 expected skips.
  Documentation-sync commit `8efcb17` passed push CI `29473032843` and PR #33
  CI `29473045583`, with Base Python and Optional Neuro Readers green in both.
  The experiment remains `Not Started` and every
  S20, split, target, model, training, inference, and scoring permission is
  false.
- **Loop 55 bounded AI research guard:** policy commit `8855fae` and
  implementation commit `bd52cce` add a strict synthetic proposal schema,
  canonical SHA-256 identity, three CLI commands, one 1,771-byte fixture, and
  adversarial checks for target leakage, noncausal context, language models,
  pretrained weights, protected observation scopes, unknown fields, Boolean
  counter tricks, and output/resource expansion. The guard makes no network or
  AI-service call and executes no proposal. The future real agent phase remains
  Loop 54 dependent and needs an exact preregistration plus separate Tier C
  authorization. Historical-hash repair `f50be96` passed push CI `29621564301`;
  the complete local suite passes 1,087 tests with 3 expected skips.
- **Loop 56 cross-modality accessibility research:** the planning boundary
  freezes five verdict classes, a 12-level capability ladder, 18 comparison
  dimensions, 16 mandatory claim fields, 28 gates, 34 refusals, and a 12-part
  at-home conjunction. Published Brain2Qwerty v1/v2 evidence remains external;
  v2 continuous MEG is explicitly noncausal and cannot establish local EEG,
  latency, device, or home capability. The current provisional outcome is
  `L56-O2`, mechanics and interfaces only. The final artifact-only verdict is
  `Not Started`, Loop 55 result dependent, and separately unauthorized; no raw
  or protected payload, target, prediction, checkpoint, model, score, device,
  or latency trace was opened or produced. Planning commit `6583ca3` passed
  push CI `29586877054` and PR #34 CI `29586915269`, with both required jobs
  green.
- **Loop 30 planning research:** the future product is a loopback-only target-
  free replay inspector. The boundary separates artifact, synthetic, recorded,
  and live source modes; freezes a 30-field trace, nine clocks, six latency
  levels, 18 gates, and 30 refusals; and requires fixed localhost, zero external
  browser traffic, explicit finalization, accessible status updates, and
  unavailable confidence. All 30 authorization flags remain false, no seed or
  payload exists, and the experiment is `Not Started`.
- **Loop 31 attribution result:** exact-zero and timing-only components each
  passed at 6/6 wins and one-sided `p = 0.015625`, but the complete registered
  conjunction failed against the prior and corrupted-signal controls. The
  partial wins are diagnostic only; sensor-signal dependence and brain-specific
  attribution were not established. The LLM/Neuro Token extension stayed closed.
- **Loop 32 planning research:** the fresh-person calibration firewall
  recommends one causal 32-parameter hidden affine adapter, four distinct
  zero-shot/unlabeled/label-light/supervised modes, six nested sentence
  budgets, 32/16/48 physical partition floors, six controls, 20 gates, and 26
  refusals. All 22 authorization flags remain false, no candidate is selected,
  and the experiment is `Not Started`; S25 remains final-only.
- **Loop 33 bounded-scaling result:** nested `8, 16, 24, 32, 44, 55`
  unique-sentence prefixes, three fixed seeds, 18 candidate fits, and six
  matched priors ran inside the consumed event. All seed slopes were negative
  and the 8-to-55 descriptive gain was `0.289202`, but the 55-row candidate was
  still `0.186942` worse than its prior. The gate is parked with no scaling-law
  or acquisition claim.
- **Loop 34 planning research:** the confidence firewall separates seven
  semantics from raw ranking through product-visible confidence, eight
  score/control roles, and recommended fresh target-free synthetic
  calibration/selection/final counts of `128/64/256`. It requires registered
  working points, generalized risk, bounded losses, revision-delay reporting,
  and one final-target open only after every choice and hash freezes. The six
  real validation rows cannot fit and independently qualify confidence. Twenty
  gates, 30 refusals, and 26 false authorization flags are machine checked.
  The experiment is `Not Started`; confidence is unavailable and all fixture,
  fit, target, scoring, product-confidence, and real-data work is unauthorized.
- **Loop 35 planning research:** the peripheral-confound firewall inventories
  ten shortcut classes and nine synchronized stream classes, then separates 13
  timing, leakage-sentinel, peripheral, brain-sensor, residualized, and combined
  conditions across three independently authorized stages. Missing controls
  cannot be imputed as clean or synthetic. Twenty-four gates, 32 refusals, and
  31 false authorization flags are machine checked. The experiment is `Not
  Started`; current S21/S7 evidence cannot establish incremental brain-sensor
  information beyond recorded controls, absolute brain origin, or no-keypress
  and patient transfer.
- **Loop 36 planning research:** the geometry/reference firewall separates
  source and channel identity, signal and coordinate units, sensor/electrode
  geometry, directional rigid transforms, reference/ground, compensation,
  interpolation, and missingness. Only explicit bijective aliases, declared
  unit factors, and named right-handed transforms can preserve identity.
  Twenty-two gates, 30 refusals, and 29 false authorization flags are machine
  checked. The experiment is `Not Started`; declared metadata compatibility,
  numerical compatibility, model transfer, and device equivalence remain
  distinct claims.
- **Loop 37 planning research:** the derivative/provenance firewall separates
  the stable BIDS 1.11.1 dataset envelope and file metadata from non-standard
  NeuroDecodeKit NPZ caches, split reports, report cards, and manifests. It
  freezes truthful BIDS URI handling, path/identifier redaction, no-raw-copy
  checks, 24 gates, 32 refusals, and 29 false authorization flags. The
  experiment is `Not Started` and unauthorized; no derivative tree, validator
  result, privacy/license qualification, or public release exists.
- **Loop 38 planning research:** the privacy/lifecycle firewall pins stable NIST
  PF 1.0, maps predictability/manageability/disassociability, and separates five
  sensitivity levels, eight artifact classes, ten copy surfaces, 12 sensitive-
  field classes, five deletion-receipt levels, and consent/license/release
  authority. Unknown backups, clones, PR refs, CI artifacts, and remotes remain
  unresolved. The experiment is `Not Started` and unauthorized; no fixture,
  scanner, deletion, protected-root scan, identity attack, history rewrite,
  consent determination, release, or upload exists.
- **Loop 39 planning research:** the cross-machine firewall separates seven
  qualification levels, 18 environment fields, eight output classes, six
  comparison classes, six required future cells, field-specific floating
  tolerances, and exact semantic identity. The experiment is `Not Started` and
  unauthorized. Current Python 3.10, macOS, cross-OS, lockfile, package-build,
  and independent-reproduction evidence remains unavailable; no fixture,
  manifest, CI matrix, install, build, protected read, model, training, edge,
  stream, device, or hardware operation exists.
- **Loop 40 planning research:** the deployment firewall separates the frozen
  float32 graph, exported graph, numeric payload, runtime/kernels, host causal
  state/timestamps/decoder, and named app/device envelope. ExecuTorch/XNNPACK
  is a research lead only beside ONNX Runtime Mobile, LiteRT, and Core ML; no
  backend or target is selected. The experiment is `Not Started` and
  unauthorized because the relevant Loop 39 matrix has not run. No install,
  export, conversion, package, inference, profiler, delegate, simulator, app,
  device, or hardware operation exists.
- **Loop 41 planning research:** the first proposed RW3-to-NeuroToken join now
  has a machine-checkable firewall for seven distinct clock views, eight
  anomaly classes, five schedules, five resume cuts, bounded state, and 18
  provenance/hash bindings. The experiment remains `Not Started` and
  unauthorized: no source chunk, fixture, preprocessing run, adapter, token
  runtime, end-to-end latency measurement, live source, device, or scientific
  result exists.
- **Loop 42 planning research:** OpenBCI Cyton base 8-channel over USB radio is
  the one future mechanics candidate, with Daisy, Wi-Fi, cloud, targets, and
  models excluded. The Q0 boundary freezes exact firmware/host/configuration
  identity, packet and clock semantics, locality, battery-only safety, four
  separately authorized stages, 34 gates, and 46 refusals. No device is known
  to be present; there was no purchase, install, connection, stream, recording,
  participant contact, signal result, latency measurement, or decoding claim.

### What The Results Actually Say

- The fixed real same-person cross-session MEG CTC is **worse** than the
  no-signal prior: corpus CER `0.9179` versus `0.7755`.
- The real S7 EEG nearest-centroid classifier is **worse** than its train-only
  no-signal prior: `0.91%` versus `12.27%` exact key-label accuracy.
- Loop 13 parks a lazy-backend migration because measured NPZ access did not
  justify building a second storage backend.
- Loop 23 parks a synthetic streaming CTC gate after missing its registered
  exact-sequence threshold, even though several secondary metrics passed.
- Loop 23.5 shows that one supervised blank-logit intercept fixes one fresh
  synthetic motif/symbol task. That is a mechanism result, not brain decoding.
- Loop 24 retains float32. Float16 passes correctness but misses every runtime
  replacement threshold; qint8 is smaller but fails correctness and runtime;
  the complete target-free gate parks on its 60-second orchestration cap.
- Loop 25 now has a passed causal-preprocessing mechanics result: the exact
  target-free path is causal with zero right context and passes anti-alias,
  timing, schedule, resume, mutation, access, and resource gates. It does not
  show that neural information survives preprocessing, and no rerun is open.
- Loop 26 has one consumed protected validation result, not a neural advantage.
  The candidate was worse than the no-signal prior; no rerun is authorized, and
  six sentences from one person and session cannot establish transfer or
  population generalization.
- Loop 27 identifies an acquisition candidate, not an acquired holdout. Exact
  channels, performed trials, sentence overlap, target freshness, transfer
  behavior, and one-time performance remain unavailable.
- Loop 28 defines a falsifiable strict zero-shot rule, not a transfer result.
  Brain2Qwerty v2's joint and target-finetuned evidence does not establish
  strict unseen-person zero-shot behavior, and one future S25 pass could not
  establish population generalization.
- Loop 29 defines the evidence needed to translate modalities, not a portable
  sensing result. Brain2Qwerty v2's 76/153/230-channel cryogenic ablations are
  not OPM-MEG or EEG device qualification, and repeated at-home EEG recording
  mechanics are not at-home text decoding.
- Loop 30 defines the evidence needed for a trustworthy replay interaction,
  not a running streaming decoder. A stable partial can be wrong, replay time
  is not capture time, and a localhost label without network and file-exposure
  QA is not a measured privacy result.
- Loop 31's consumed matrix failed its complete conjunction. Individual wins
  over zero and timing controls do not establish sensor-signal dependence;
  language gain, Neuro Token gain, and brain-specific origin remain unavailable.
- Loop 48 Stage B localizes the current failure to stable nonseparability for
  the registered causal and linear probe families, not to one of the four fixed
  timing offsets. The candidate still loses to the train-only prior, the rows
  are historically used development data, raw signal quality remains
  unresolved, and the result cannot be called validation or neural advantage.
- Loop 32 defines the evidence needed for honest one-person calibration, not a
  calibrated result. The 32-parameter adapter is a planning recommendation,
  unlabeled adaptation remains transductive rather than zero-shot, and one
  future participant could not establish population or device generalization.

### What Is Not Established

There is no demonstrated:

- neural advantage on the real evaluated MEG or EEG cohorts;
- unseen-person generalization;
- useful open-vocabulary EEG sentence decoder;
- result on unreleased Brain2Qwerty v2 data or embeddings;
- end-to-end real-time text latency;
- portable, consumer, or at-home hardware result;
- arbitrary-thought decoding;
- clinical, diagnostic, or assistive efficacy.

S21 session 2, the S7 EEG evaluation, and synthetic test seeds 2203, 2303, and
2353 are consumed for the decisions they informed. They must not be reopened
for tuning and then described as fresh evidence.

The detailed risk language lives in
[docs/RISK_AND_ETHICS.md](docs/RISK_AND_ETHICS.md).

## Why This Project Exists

The practical barrier to neural language-decoding research is often not the
last model layer. It is everything before and around it:

- public neuroimaging releases can be hundreds of gigabytes;
- event and behavioral logs can use undocumented timing domains;
- participant aliases can invalidate nominal subject splits;
- preprocessing fit on evaluation rows can leak information;
- language priors can be credited to neural signal;
- a cache can silently lose channel, timing, geometry, or split identity;
- “causal,” “streaming,” “online,” and “real-time” are often collapsed;
- a successful file read can be overstated as device or decoding support.

NeuroDecodeKit turns those risks into explicit interfaces, counters, hashes,
caps, tests, and report fields.

## Quickstart

### 1. Base Install

Python 3.10 or newer is required.

```bash
git clone https://github.com/CheickDiakite-yikes/neurodecodekit.git
cd neurodecodekit
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The base install has zero runtime dependencies. Exercise pure-Python metrics:

```bash
neurodecode eval-text \
  --target "HOLA MUNDO" \
  --prediction "HOLA MUNCO"
```

Run the base-aware test suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Tests for unavailable optional dependencies skip cleanly. A skipped optional
test is not evidence that its MNE or Torch path passed.

### 2. Tiny Array Smoke

Install only NumPy for synthetic shards and NPZ interfaces:

```bash
python -m pip install -e '.[array]'

neurodecode make-synthetic-shard \
  --out cache/synthetic_tiny.npz \
  --samples 64 \
  --channels 8 \
  --times 25

neurodecode load-cache \
  --cache cache/synthetic_tiny.npz \
  --metadata-out cache/synthetic_tiny.metadata.json

neurodecode report \
  --cache cache/synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/synthetic_report.json \
  --out-md cache/synthetic_report.md \
  --run-name synthetic_identity_plumbing \
  --split synthetic-smoke
```

`--identity-smoke` copies targets to predictions to prove report plumbing. It
is deliberately labeled as **not a model result**.

### 3. Choose Optional Capabilities

Install only what the task needs:

| Extra | Adds | Typical use |
|---|---|---|
| `array` | NumPy | synthetic shards, NPZ caches, NeuroToken interfaces |
| `neuro` | MNE 1.12.x, NumPy, SciPy | format readers, bounded signal inspection, extraction |
| `ml` | NumPy, scikit-learn, Torch | optional small baselines and synthetic learned gates |
| `hf` | Hugging Face Hub | metadata listing and explicit selective download |
| `cache` | Zarr, numcodecs, NumPy | measured storage-backend experiments |
| `demo` | Gradio | local artifact-backed evidence console |
| `dev` | Ruff, pytest | contributor checks |
| `all` | all optional groups | full local development; large |

Examples:

```bash
python -m pip install -e '.[neuro,dev]'
python -m pip install -e '.[array,demo]'
```

Heavy imports remain inside the commands that need them. Adding an optional
feature should not make `import neurodecodekit` import MNE, NumPy, or Torch.

## I Have EEG Data

You can contribute without uploading the recording.

1. Read [CONTRIBUTING.md](CONTRIBUTING.md), especially **I Have EEG Data**.
2. Open the **EEG data compatibility** issue form.
3. Share only non-sensitive aggregate facts: format, device family, nominal
   channels/rate, reference availability, task cohort, license, and byte cap.
4. Run metadata-only intake locally.
5. Reproduce the relevant format condition with a deterministic synthetic
   fixture.
6. Request a separately frozen bounded real-read protocol only if the synthetic
   gate passes and the data terms permit it.

Do not attach raw EEG, event files, target text, participant tables, private
cloud links, derived embeddings, or subject-level predictions to an issue.

### Metadata-Only Local Intake

The base command inspects structure without opening binary signal samples or
event/target content:

```bash
neurodecode inspect-recording \
  --path /absolute/path/to/recording-or-bids-root \
  --root /absolute/path/to/allowed-root \
  --out-dir /absolute/path/to/private/intake-report \
  --modality EEG \
  --device-type "your device or amplifier"

neurodecode inspect-intake-report \
  --report /absolute/path/to/private/intake-report/intake.json
```

The output includes deterministic JSON/Markdown plus a measured audit sidecar,
relative source identity, companion validation, known/unavailable fields,
warnings, access counters, hashes, runtime, RSS, and output bytes.

Review it locally before sharing. Metadata can still be sensitive.

### Compatibility Is Staged

| Level | Evidence |
|---:|---|
| 0 | File family and companions recognized |
| 1 | Bounded samples readable |
| 2 | Channels, timing, units, geometry status, and aggregate events validated |
| 3 | Deterministic preprocessing/replay validated |
| 4 | Leakage-resistant classification beats registered controls |
| 5 | Sequence metrics beat no-signal controls on a fresh split |
| 6 | Live/replay timing and end-to-end behavior measured |

A level applies only to the exact format, adapter, configuration, and evidence
cohort tested. It does not transfer automatically to another headset, dataset,
task, subject, or session.

## I Have An EEG Headset Or Board

Use the **EEG hardware qualification** issue form. Include:

- model, revision, firmware, SDK, and operating system;
- EEG/ExG channel roles, electrode placement, reference, and ground;
- nominal and measured sampling rate;
- raw API or file export;
- USB, serial, BLE, Wi-Fi, LSL, XDF, or cloud transport;
- timestamp clock, correction, packet counter, and packet-loss behavior;
- local/offline capability and SDK license;
- separate peripheral streams such as EOG, EMG, PPG, IMU, gaze, or audio.

The preferred first result is offline replay equivalence on deterministic
samples. A connected device or live waveform plot is not a language decoder.
Four-channel consumer EEG is not assumed equivalent to 64-channel research EEG
or 306-channel MEG.

Replay and hardware contributions must begin from the frozen
[RW3 preregistration](docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md) and
[machine contract](registries/replay_equivalence_contract.v0.json). The
[Stage A authorization packet](docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md) and its
[machine request](registries/rw3_stage_a_authorization_request.v0.json) make the
next permission exact, but both still say that Stage A is unauthorized. A
hardware contribution, issue, or pull request cannot substitute for that
decision; each runtime stage requires a separate review.

The current metadata device registry is
[registries/devices.v0.json](registries/devices.v0.json). Registry presence is
not device qualification.

## Safe Workflows

### RW2 Synthetic Signal-Quality Roundtrip

This workflow requires `.[neuro]`, reads no participant data, and creates less
than the frozen 16 MiB fixture/report cap:

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

neurodecode make-signal-quality-fixtures \
  --out-dir cache/rw2-fixtures \
  --contract registries/signal_quality_contract.v0.json

neurodecode inspect-signal-quality-fixtures \
  --manifest cache/rw2-fixtures/signal_quality_fixtures.json

neurodecode inspect-signal-quality \
  --path cache/rw2-fixtures/fixtures/clean_multitype_continuous__fif/source/recording_raw.fif \
  --root cache/rw2-fixtures \
  --intake-report cache/rw2-fixtures/fixtures/clean_multitype_continuous__fif/intake/intake.json \
  --fixture-manifest cache/rw2-fixtures/signal_quality_fixtures.json \
  --contract registries/signal_quality_contract.v0.json \
  --out-dir cache/rw2-quality

neurodecode inspect-signal-quality-report \
  --report cache/rw2-quality/signal_quality.json
```

RW2 reports descriptive time-domain and Welch PSD summaries, units, geometry
availability, reference status, aggregate annotation status, source filters and
projectors, bounded windows, access counts, resource measurements, warnings,
and no-mutation identity. It performs no filtering, rereferencing, bad-channel
repair, interpolation, ICA, clipping, scaling, model run, or training.

RW2 is a synthetic reader and report-interface proof. It says nothing about the
quality of a person's recording.

### Dataset Manifest Without Download

Build and inspect a manifest from an existing path list:

```bash
neurodecode manifest-from-paths \
  --paths data/file_list.txt \
  --out data/manifest.jsonl

neurodecode inspect-manifest \
  --manifest data/manifest.jsonl

neurodecode select-tiny \
  --manifest data/manifest.jsonl \
  --out data/tiny_selection.json \
  --modality EEG \
  --blocks 1 \
  --max-files 4 \
  --max-total-gb 1
```

`select-tiny` records exact paths, known bytes, unknown-size warnings,
revision, and caps.

### Selective Download Is Dry-Run First

Hugging Face access is optional:

```bash
python -m pip install -e '.[hf]'

neurodecode download-selection \
  --selection data/tiny_selection.json \
  --local-dir data/spanishbcbl_tiny
```

That command does not download by default. `--execute` is required, unknown
sizes fail closed unless explicitly allowed after review, and the default worker
count is one.

Do not use this example as authorization to download SpanishBCBL. Check the
dataset license, exact revision, local disk, protocol, and approval boundary.

### Event-Window Extraction

For an explicitly acquired, legally usable, validated FIF/MAT pair:

```bash
python -m pip install -e '.[neuro]'

neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../logs.mat \
  --out cache/b2qmini_s1_block1.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3 \
  --picks meg \
  --max-events 200
```

This command does not download data. It reports source bytes, events found,
kept and dropped events, shape, rate, channels, parser warnings, runtime, and
output bytes.

Generic MAT schemas do not inherit the validated S21 trial-ordering claim.

### Honest Baselines

Run the no-brain comparator before interpreting a neural model:

```bash
neurodecode prior-baseline \
  --cache cache/synthetic_tiny.npz \
  --out-predictions cache/prior_predictions.txt \
  --out-json cache/prior_report.json \
  --out-md cache/prior_report.md \
  --run-name synthetic_prior \
  --split synthetic-smoke

neurodecode template-baseline \
  --cache cache/synthetic_tiny.npz \
  --train-fraction 0.5 \
  --out-predictions cache/template_predictions.txt \
  --out-json cache/template_report.json \
  --out-md cache/template_report.md \
  --run-name synthetic_template \
  --split synthetic-holdout
```

Synthetic separability proves plumbing and model mechanics only. A real neural
result must use train-only fitting, frozen split identity, a no-signal prior,
and uncertainty appropriate to the evaluation unit.

## CLI Map

The CLI intentionally exposes small auditable stages:

| Area | Commands |
|---|---|
| Text metrics/reports | `eval-text`, `report`, `build-leaderboard` |
| No-signal/small baselines | `prior-baseline`, `sentence-prior-baseline`, `template-baseline`, `tiny-conv-baseline` |
| Discovery/download | `manifest-from-paths`, `inspect-manifest`, `select-tiny`, `list-hf-files`, `download-selection` |
| Local intake | `inspect-recording`, `inspect-intake-report` |
| Synthetic quality | `make-signal-quality-fixtures`, `inspect-signal-quality-fixtures`, `inspect-signal-quality`, `inspect-signal-quality-report` |
| Event/sentence extraction | `extract-windows`, `extract-eeg-windows`, `extract-sentence-cache`, `align-sequences` |
| Cache interfaces | `make-synthetic-shard`, `load-cache`, `make-synthetic-sentence-cache`, `inspect-sentence-cache`, `make-neurotoken-cache`, `inspect-neurotoken-cache` |
| Split/session controls | `split-protocol`, `apply-frozen-scaler`, `cross-session-ctc` |
| Resource experiments | `sampling-rate-sweep`, `channel-subset-sweep`, `precision-storage-sweep`, `inspect-representation-cache`, `lazy-backend-gate` |
| Synthetic causal gates | `causal-replay-gate`, `make-causal-motif-fixture`, `tiny-causal-encoder-gate`, `make-ctc-symbol-stream-fixture`, `streaming-ctc-gate`, `make-blank-calibration-fixture`, `blank-intercept-gate` |
| Research/demo | `eeg-bridge-gate`, `synthetic-adapter-gate`, `synthetic-calibration-curve`, `demo` |

Use `neurodecode COMMAND --help` for exact arguments and safety defaults.

## Architecture

```text
src/neurodecodekit/
  datasets/       manifests, local intake, safe selection, optional Hub access
  preprocess/     format readers, event alignment, window/sentence extraction
  cache/          NPZ schemas, packed representations, NeuroToken interfaces
  models/         prior, template, tiny Conv/CTC, causal encoder components
  training/       deterministic synthetic fixtures and bounded runners
  evaluation/     CER/WER, controls, reports, splits, uncertainty, report cards
  experiments/    preregistered resource, session, causal, and EEG gates
  demo/           artifact-backed local evidence console
```

The CLI defers heavy imports into individual commands. Source modules use strict
schemas and dataclasses where structured records cross boundaries.

## Stable Interfaces

### B2Q-Mini Event Cache v0

An event cache stores:

```text
windows             [events, channels, timepoints]
labels              per-event labels when validated
event_start_sec     event timing
event_source_index  source row or trigger identity
channel_names       ordered selected channels
metadata            schema, source, transforms, warnings, hashes
```

### Continuous Sentence Cache v0

Sentence caches preserve variable true lengths, trial identity, target/response
provenance, source sampling rate, channel order, geometry availability, split
binding, fit scope, and transformation history.

### NeuroTokenCache v0

NeuroTokenCache is shaped `[items, time, embedding]` and preserves:

- modality and device type;
- item, subject, session, trial, and split identities;
- source rate and token timestamps;
- true lengths and padding masks;
- channel names and available geometry;
- causal/noncausal status and required context;
- source-cache, split-protocol, configuration, and payload hashes;
- warnings, unavailable fields, access counters, and claim boundaries.

The current Loop 20 producer is a deterministic target-free projection from
synthetic signals. It is not a learned representation or decoding result.

## Evaluation Discipline

NeuroDecodeKit separates:

- language-only priors from neural models;
- train/validation/test/calibration membership;
- split membership from preprocessing fit scope;
- event classification from sentence decoding;
- within-recording, cross-session, and unseen-person evidence;
- EEG from MEG and peripheral modalities;
- producer causality from decoder causality;
- intrinsic context, transport delay, compute time, and end-to-end latency;
- synthetic mechanisms from real-data results;
- fresh tests from consumed evaluations.

Every report should name the dataset/revision, task, modality, subject/session
scope, split, fit rows, metrics, controls, runtime, RSS, input/output bytes,
access counts, warnings, and unavailable fields.

CER and WER are not enough by themselves. Tiny test sets need paired examples
and uncertainty; key-event tasks may need exact label accuracy; sequence tasks
need blank/repeat diagnostics and exact-sequence counts.

## Data And Privacy

Neural recordings and derived features are sensitive, even when filenames are
de-identified.

- Raw data and caches are ignored by Git.
- Reports should use relative identity and hashes, not absolute paths.
- Participant rows, free-text annotations, target sentences, serial numbers,
  exact acquisition timestamps, and exact head/sensor coordinates are omitted
  from shareable intake/quality reports.
- Prediction/error reports can reveal typed text and should remain local unless
  dataset terms and disclosure have been reviewed.
- Hashes are integrity tools, not anonymization.
- Do not attempt participant identification.

See [SECURITY.md](SECURITY.md) for private reporting and
[docs/RISK_AND_ETHICS.md](docs/RISK_AND_ETHICS.md) for the complete scope.

## Resource Discipline

The repository is designed for bounded local work:

- one worker/thread where applicable;
- dry-run downloads by default;
- explicit file and byte caps;
- no full SpanishBCBL download;
- optional dependencies;
- small synthetic fixtures;
- measured runtime, peak RSS, input bytes, output bytes, and access counts;
- no new backend or larger model without a measured reason.

RW2 freezes at most 512 selected channels, three windows, 4,194,304
channel-sample values, 32 MiB of materialized float64 arrays, 30 seconds, 1 GiB
peak RSS, 4 MiB of report output per run, and 16 MiB for the complete synthetic
fixture/report set.

Loop 24 used one numerical thread and one sequential worker at a time, 48
target-free items per partition, 455,472 working-array bytes, 262,822 total
generated bytes, and at most 222,248,960 worker-RSS bytes. It stayed below every
storage, memory, concurrency, and access cap but took 65.154951 seconds against
the frozen 60-second runtime cap. Seed 2401 is consumed; seed 2402 remains
unopened and closed. Real data, targets, training, energy, RW3, and hardware
remain outside the gate.

Generated artifacts belong in ignored `cache/` or `outputs/`, not in Git.

## Project Status And Roadmap

The original numbered development sequence has reached:

- Loops 1-12: completed;
- Loop 13: parked after measured lazy-backend gate;
- Loops 14-22: completed at their exact proof boundaries;
- Loop 23: parked after the frozen synthetic decoder test missed its primary
  threshold;
- Loop 23.5: completed as a supervised synthetic calibration mechanism;
- Loop 24: parked after one registered target-free selection at implementation
  commit `3a5dc0b`; float32 is retained, no replacement or storage-only candidate
  passed, seed 2401 is consumed, seed 2402 qualification stayed unopened, and
  runtime was 65.154951 seconds versus the 60-second cap;
- Loops 25-44: a primary-source-informed tranche spans causal
  evidence, translation/generalization, reliability/confounds,
  reproducibility/local deployment, and live translation/release. Loop 25 is
  complete after one registered target-free execution: authorization commit
  `1e7296a` and implementation commit `439f151` were remotely green before the
  static, development, and conditional qualification gates passed. Its current
  execution flag is false because no rerun is authorized. Loop 26/31/33 share
  the green preregistration at `881145d` and authorization at `1c0e52c`; the
  one six-target event is consumed and all three registered gates are parked
  after the candidate lost to the no-signal prior. All execution flags are now
  false and no rerun is open. Loop 27
  planning research is green at `b3d61b6` and selects
  S25 metadata, while preregistration and acquisition remain blocked. Loop 28
  planning research defines the strict zero-shot final-only rule while its
  experiment remains `Not Started`. Loop 29 planning research at green commit
  `f5fc740` defines a local-first EEG lane, a partner/lab OPM-MEG lane, and a bounded 5-10 GB
  capacity envelope while its experiment remains `Not Started`. Loop 30
  planning research now freezes the local target-
  free replay interaction boundary while its experiment remains `Not Started`.
  Loop 31's encoder conditions were scored in the consumed shared event and
  failed their complete conjunction; its contingent five-condition LLM
  extension remained closed. Loop 32
  planning research defines a causal 32-parameter adapter,
  four calibration modes, and physically separate calibration/selection/final
  evidence while its experiment remains `Not Started`. Loop 33 planning
  research defines the bounded `8, 16, 24, 32, 44, 55` unique-sentence curve,
  one target-blind shared validation event, and no acquisition now; the curve
  executed once and failed because its 55-row model remained worse than the
  matched prior. Loop 34 planning research defines the
  three-way confidence, abstention, and revision firewall while its experiment
  remains `Not Started` and confidence is unavailable; Loop 35 planning
  research defines the staged peripheral-confound firewall while its experiment
  remains `Not Started`; Loop 36 planning research defines the geometry/
  reference identity firewall while its experiment remains `Not Started`;
  Loop 37 planning research defines the BIDS-envelope/non-standard-payload
  firewall while its experiment remains `Not Started`; Loop 38 planning
  research defines the privacy/lifecycle and deletion-claim firewall while its
  experiment remains `Not Started`; Loop 39 planning research defines the
  environment, semantic-identity, and numerical-tolerance firewall while its
  experiment remains `Not Started`; Loop 40 planning research defines the
  edge-package, host-state, fallback, complete-cost, and target-identity
  firewall while its experiment remains `Not Started`; Loop 41 planning
  research defines the stream-to-NeuroToken clock, anomaly, state, schedule,
  and provenance firewall while its experiment remains `Not Started` and
  unauthorized; Loop 42 planning research selects the exact OpenBCI Cyton
  8-channel USB-radio path for future mechanics only while its experiment
  remains `Not Started` and unauthorized; Loop 43 planning research defines the
  independent artifact-reproduction firewall while its challenge remains `Not
  Started` and unauthorized. Loop 44 artifact-only planning is complete; its
  engineering release is held and scientific performance release is parked.
  All 20 current execution flags are false. Loop 25's mechanics closeout
  satisfies that dependency only; the Loop 26 request and every later
  experiment remain unauthorized.

The parallel Real-World Practice track has reached:

- RW0: primary-source dataset/device research and bounded acquisition planning;
- RW1: dependency-free metadata-only local intake, fixture-backed;
- RW2: bounded synthetic signal-read and descriptive quality-report interface,
  fixture-backed;
- RW3: replay/live-source equivalence preregistered at `c3d1f01`; the Stage A
  decision packet is ready for explicit review, while Stage A and all runtime
  adapters remain unauthorized;
- RW4+: not authorized by RW3 registration;
- proposed S20 acquisition: dry-run only until exact approval.

The next tranche is a claim graph, not a feature wish list. A failed real
validation gate parks model scaling; a failed neural ablation blocks neural
attribution; a failed replay gate blocks device work. Negative results remain
valid closeouts. Roadmap approval and general continuation are not execution
authorization.

See [docs/POST_20_ROADMAP.md](docs/POST_20_ROADMAP.md) and
[docs/LOOPS_25_44_ROADMAP.md](docs/LOOPS_25_44_ROADMAP.md), plus the separate
[real-world practice track](docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md).

## Documentation Map

| Document | Purpose |
|---|---|
| [START_HERE.md](START_HERE.md) | shortest current orientation |
| [docs/CODEX_HANDOFF.md](docs/CODEX_HANDOFF.md) | exact continuation boundary for coding agents |
| [docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md](docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md) | byte-identical approved charter snapshot defining autonomous Tier A/B work and exact Tier C stops |
| [docs/RESEARCH_AUTONOMY_CHARTER_DECISION.md](docs/RESEARCH_AUTONOMY_CHARTER_DECISION.md) | exact maintainer approval, frozen charter hashes, standing resource envelope, and nonretroactive Tier C boundary |
| [docs/BUILD_NOTES.md](docs/BUILD_NOTES.md) | chronological measured build journal |
| [docs/DECISIONS.md](docs/DECISIONS.md) | consequential architecture and research decisions |
| [docs/NEXT_20_LOOPS_TRACKER.md](docs/NEXT_20_LOOPS_TRACKER.md) | original 20-loop tracker, current post-roadmap gate, and planning-only Loops 25-44 summary |
| [docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx](docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx) | ten-sheet visual tracker preserved at the last reviewed Stage A snapshot; use the Markdown tracker and machine roadmap for the current Stage B result because a prior workbook import reached 1.57 GiB peak RSS |
| [docs/POST_20_ROADMAP.md](docs/POST_20_ROADMAP.md) | closed/current post-NeuroToken gates plus links to the next tranche |
| [docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md](docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md) | Brain2Qwerty, MNE, BIDS, MOABB, LSL, privacy, uncertainty, and edge-runtime research behind Loops 25-44 |
| [docs/LOOPS_25_44_ROADMAP.md](docs/LOOPS_25_44_ROADMAP.md) | detailed goals, controls, metrics, acceptance gates, stop rules, dependencies, caps, and authorization boundaries for the next 20 loops |
| [registries/next_20_loops.v0.json](registries/next_20_loops.v0.json) | machine-readable five-phase roadmap with 20 false execution flags and row-level primary-source bindings |
| [docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md) | six-item identifiability limit, causal candidate repair, parameter-matched comparator, control design, and exact no-execution boundary |
| [registries/loop26_research_boundary.v0.json](registries/loop26_research_boundary.v0.json) | machine-readable Loop 26 planning evidence, recommendations, zero access counters, and 14 false authorization fields |
| [docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md](docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md) | green prospective Loop 26/31/33 model, attribution, scaling, prediction-freeze, scoring, access, and resource protocol |
| [docs/LOOP_26_AUTHORIZATION_PACKET.md](docs/LOOP_26_AUTHORIZATION_PACKET.md) | immutable plain-language exact decision surface for the shared event |
| [docs/LOOP_26_AUTHORIZATION_DECISION.md](docs/LOOP_26_AUTHORIZATION_DECISION.md) | separately green one-time authorization, exact scope, order, resources, and refusals |
| [docs/LOOP_26_SHARED_VALIDATION_IMPLEMENTATION.md](docs/LOOP_26_SHARED_VALIDATION_IMPLEMENTATION.md) | bounded reader, causal models, controls, freeze, scorer, CLI stages, synthetic qualification, and pre-access boundary |
| [registries/loop26_shared_validation_contract.v0.json](registries/loop26_shared_validation_contract.v0.json) | machine-readable 21-fit, 31-prediction, 40-refusal shared validation contract and archive-access correction |
| [registries/loop26_authorization_request.v0.json](registries/loop26_authorization_request.v0.json) | green-commit-bound request with every authorization flag false and every protected/model/training/scoring counter zero |
| [docs/LOOP_48_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_48_PRIMARY_SOURCE_RESEARCH.md) | post-outcome aggregate diagnosis, eight-class tree, exact artifact evidence, unavailable root-cause fields, and no-execution boundary |
| [registries/loop48_failure_localization_contract.v0.json](registries/loop48_failure_localization_contract.v0.json) | green hash-bound four-input Stage A contract with `F5` as a phenotype, 30 refusals, measured caps, and every authorization false |
| [docs/LOOP_48_AUTHORIZATION_PACKET.md](docs/LOOP_48_AUTHORIZATION_PACKET.md) | exact four-JSON Stage A permission surface, one-thread resource envelope, exclusions, and claim ceiling |
| [registries/loop48_authorization_request.v0.json](registries/loop48_authorization_request.v0.json) | request bound to green commit `83309bf` and both CI runs; no implementation or execution is authorized |
| [docs/LOOP_48_AUTHORIZATION_DECISION.md](docs/LOOP_48_AUTHORIZATION_DECISION.md) | separately committed exact user decision, four-input scope, caps, order, exclusions, and claim ceiling |
| [docs/LOOP_48_FAILURE_LOCALIZATION_RESULT.md](docs/LOOP_48_FAILURE_LOCALIZATION_RESULT.md) | one-shot Stage A evidence, ordered `F5` trace, measurements, access ledger, and no-root-cause closeout |
| [registries/loop48_failure_localization_result.v0.json](registries/loop48_failure_localization_result.v0.json) | hash-bound 10,643-byte aggregate result with four verified input identities, all resource checks, and zero protected/model counters |
| [docs/LOOP_48_TRAIN_ONLY_HYPOTHESIS_PORTFOLIO.md](docs/LOOP_48_TRAIN_ONLY_HYPOTHESIS_PORTFOLIO.md) | five coexisting future train-only hypotheses, shared evidence design, sequential compute policy, and leakage firewall |
| [registries/loop48_hypothesis_portfolio.v0.json](registries/loop48_hypothesis_portfolio.v0.json) | design-only H1-H5 support-vector schema with unfrozen Stage B inventory/caps and zero operation counters |
| [docs/LOOP_48_HYPOTHESIS_DISCRIMINATION_RESEARCH.md](docs/LOOP_48_HYPOTHESIS_DISCRIMINATION_RESEARCH.md) | primary-source refinement adding data-regime hypothesis `H6`, evidence levels, non-identifiability rules, and the `T1` shortcut firewall |
| [registries/loop48_hypothesis_discrimination.v0.json](registries/loop48_hypothesis_discrimination.v0.json) | additive H1-H6 discrimination map with shared sequential stages, strict claim ceilings, 15 false authorizations, and zero protected/model operations |
| [docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md](docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md) | exact 44/11 split, model/control inventory, telemetry, paired statistics, prediction-freeze order, resource caps, and E2 historical-use correction |
| [registries/loop48_train_only_discrimination_contract.v0.json](registries/loop48_train_only_discrimination_contract.v0.json) | machine-readable 20-fit, 35-inference, 41-prediction Stage B contract with 25 refusals, zero protected activity, and every authorization false |
| [docs/LOOP_48_STAGE_B_AUTHORIZATION_PACKET.md](docs/LOOP_48_STAGE_B_AUTHORIZATION_PACKET.md) | plain-language exact Stage B operation, control, access-order, storage, resource, and claim decision surface |
| [registries/loop48_stage_b_authorization_request.v0.json](registries/loop48_stage_b_authorization_request.v0.json) | request bound to green preregistration commit `0ee0ab7` and both CI runs; no implementation, protected access, or execution is authorized |
| [docs/LOOP_48_STAGE_B_AUTHORIZATION_DECISION.md](docs/LOOP_48_STAGE_B_AUTHORIZATION_DECISION.md) | exact one-run maintainer decision, ordered three-green-gate sequence, resource boundary, refusals, and E2 claim ceiling |
| [registries/loop48_stage_b_authorization_decision.v0.json](registries/loop48_stage_b_authorization_decision.v0.json) | machine-readable Stage B authorization with exact counts, conditional target delivery, immutable request bindings, and zero pre-implementation counters |
| [docs/LOOP_48_STAGE_B_IMPLEMENTATION.md](docs/LOOP_48_STAGE_B_IMPLEMENTATION.md) | bounded reader, deterministic transforms, exact tiny models, private prediction freezer, isolated scorer, CLI stages, and pre-access qualification evidence |
| [registries/loop48_stage_b_prediction_freeze.v0.json](registries/loop48_stage_b_prediction_freeze.v0.json) | remotely qualified hash-only record for 20 fit telemetry bundles and 41 target-blind prediction sets, with zero check-target delivery or score |
| [docs/LOOP_48_STAGE_B_RESULT.md](docs/LOOP_48_STAGE_B_RESULT.md) | one-shot H1-H6 verdict, candidate/prior and control results, exact access/resource ledger, `L50-R05` route, and no-rerun claim boundary |
| [docs/LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md](docs/LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md) | primary-source temporal-context hypothesis, exact causal candidate and parameter-matched ablation, bounded synthetic gate, and protected-evidence firewall |
| [registries/loop48_stage_c_representation_repair_research.v0.json](registries/loop48_stage_c_representation_repair_research.v0.json) | machine-readable `R1` comparison, architecture math, synthetic caps, outcome router, zero protected/model counters, and false protected authorization fields |
| [docs/LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md](docs/LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md) | exact model/fixture/gate implementation, fail-closed preflight correction, consumed execution summary, and protected-evidence firewall |
| [registries/loop48_stage_c_synthetic_implementation.v0.json](registries/loop48_stage_c_synthetic_implementation.v0.json) | hash-bound model, fixture, gate, CLI, correction CI, consumed synthetic-result binding, and false protected authorization fields |
| [docs/LOOP_48_STAGE_C_SYNTHETIC_RESULT.md](docs/LOOP_48_STAGE_C_SYNTHETIC_RESULT.md) | one-shot candidate/ablation result, absolute gate failure, mechanics checks, resource and access ledger, and no-rerun disposition |
| [registries/loop48_stage_c_synthetic_result.v0.json](registries/loop48_stage_c_synthetic_result.v0.json) | compact aggregate result with hashes, metrics, counters, warnings, and no plaintext target or prediction |
| [registries/loop48_train_only_discrimination_result.v0.json](registries/loop48_train_only_discrimination_result.v0.json) | consumed 11-row train-check diagnostic supporting `H4`, recording evidence against fixed-shift `H3`, and preserving the E2 ceiling without plaintext targets or predictions |
| [docs/LOOP_49_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_49_PRIMARY_SOURCE_RESEARCH.md) | S24 development-person metadata decision, clean-identity tradeoff, exact bytes/hashes, text-group split recommendation, access order, and claim ceiling |
| [registries/loop49_research_boundary.v0.json](registries/loop49_research_boundary.v0.json) | machine-readable S24 selection, 25 false authorization fields, zero payload/model counters, `>=48` blocker, and permanent development-only role |
| [docs/LOOP_53_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_53_PRIMARY_SOURCE_RESEARCH.md) | source-verified S20 selection, exact four-file identities, staged EEG evidence rationale, resource envelope, and zero-payload research boundary |
| [docs/LOOP_53_FRESH_EEG_ACQUISITION_PREREGISTRATION.md](docs/LOOP_53_FRESH_EEG_ACQUISITION_PREREGISTRATION.md) | exact acquisition-only order, caps, integrity rules, stop conditions, receipt fields, and post-pass nonclaims |
| [registries/loop53_fresh_eeg_acquisition_contract.v0.json](registries/loop53_fresh_eeg_acquisition_contract.v0.json) | machine-readable 96,090,264-byte S20 contract with pinned source hashes, no-overwrite paths, one-invocation cap, and every execution permission false |
| [docs/LOOP_53_AUTHORIZATION_PACKET.md](docs/LOOP_53_AUTHORIZATION_PACKET.md) | plain-language exact Tier C sentence for implementation plus one bounded acquisition, with all interpretive and model work excluded |
| [registries/loop53_authorization_request.v0.json](registries/loop53_authorization_request.v0.json) | immutable pre-decision request bound to green registration `bccd367` and both registration CI runs |
| [docs/LOOP_53_AUTHORIZATION_DECISION.md](docs/LOOP_53_AUTHORIZATION_DECISION.md) | exact user decision, immutable contract/request hashes, authorized acquisition surfaces, excluded interpretation/model work, and ordered green gates |
| [registries/loop53_authorization_decision.v0.json](registries/loop53_authorization_decision.v0.json) | machine-readable authorization record at `2a47bbc`, with exact identity, caps, operation ledger, and nonclaims |
| [docs/LOOP_53_ACQUISITION_IMPLEMENTATION.md](docs/LOOP_53_ACQUISITION_IMPLEMENTATION.md) | standard-library executor, dry-run CLI, metadata-first refusal logic, opaque hashes, atomic promotion, receipts, tests, and implementation boundary |
| [registries/loop53_acquisition_implementation.v0.json](registries/loop53_acquisition_implementation.v0.json) | hash-bound implementation record for commit `8ec5b1b`, 51 focused tests, resource controls, zero pre-execution S20 access, and remote-green dependency |
| [docs/LOOP_53_ACQUISITION_RESULT.md](docs/LOOP_53_ACQUISITION_RESULT.md) | consumed four-file acquisition pass, exact measured resources and counters, ten gate results, unavailable fields, and stop-before-Loop-54 boundary |
| [registries/loop53_acquisition_result.v0.json](registries/loop53_acquisition_result.v0.json) | content-free aggregate result binding the private receipts, `96,090,264` bytes, `3.629499` seconds, all-zero forbidden counters, and no rerun |
| [docs/LOOP_54_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_54_PRIMARY_SOURCE_RESEARCH.md) | primary-source BrainVision/BIDS/MNE audit, current extractor gap analysis, staged target firewall, trial-unit rule, resource caps, and claim ceiling |
| [registries/loop54_eeg_trial_geometry_research.v0.json](registries/loop54_eeg_trial_geometry_research.v0.json) | machine-readable four-stage protocol with exact file-role isolation, 22 gates, 30 refusals, zero protected access counters, and false real-stage authorizations |
| [docs/LOOP_50_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_50_PRIMARY_SOURCE_RESEARCH.md) | primary-source multi-person design, global text firewall, historical S21 out-of-fold protocol, S24 development gate, controls, resources, and claim ceiling |
| [registries/loop50_research_boundary.v0.json](registries/loop50_research_boundary.v0.json) | machine-readable two-person design with six Stage B routes, ten conditions, 30 refusals, 31 false authorizations, and zero protected/model counters |
| [docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md) | official metadata ranking, selected S25 MEG candidate, exact bytes/hashes, target-isolation design, and preregistration blockers |
| [registries/loop27_research_boundary.v0.json](registries/loop27_research_boundary.v0.json) | machine-readable Loop 27 candidate identity, unavailable fields, resource boundary, zero payload access, and 18 false authorization fields |
| [docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md) | v2 transfer audit, T0-T3 taxonomy, strict zero-shot/transductive distinction, final-only rule, and calibrated-design boundary |
| [registries/loop28_research_boundary.v0.json](registries/loop28_research_boundary.v0.json) | machine-readable Loop 28 estimand, controls, access order, resource limits, dependencies, zero protected access, and 21 false authorization fields |
| [docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md) | primary-source OPM-MEG and EEG review, two-lane portability decision, storage allocation, qualification ladder, and result-oriented real-data path |
| [registries/loop29_research_boundary.v0.json](registries/loop29_research_boundary.v0.json) | machine-readable modality requirements, device gates, storage ceilings, source bindings, zero protected access, and 24 false authorization fields |
| [docs/LOOP_42_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_42_PRIMARY_SOURCE_RESEARCH.md) | official OpenBCI/BrainFlow audit, exact future Cyton candidate, packet/clock/locality/safety boundaries, staged gates, and no-execution decision |
| [registries/loop42_research_boundary.v0.json](registries/loop42_research_boundary.v0.json) | machine-readable candidate identity, packet and timing semantics, anomaly/privacy/safety controls, resource caps, zero operation counters, and 45 false authorization fields |
| [docs/LOOP_43_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_43_PRIMARY_SOURCE_RESEARCH.md) | ACM, CODECHECK, ReScience, FAIR4RS, NeurIPS, and GitHub security research; future commit-reveal challenge design; privacy, independence, outcome, and claim boundaries |
| [registries/loop43_research_boundary.v0.json](registries/loop43_research_boundary.v0.json) | machine-readable challenge taxonomy, exact field sets, discrepancy classes, stage gates, resource caps, recorded local metadata-read incident, zero experiment operations, and 48 false authorization fields |
| [docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md) | primary-source calibration taxonomy, 32-parameter adapter recommendation, physical split and burden contract, access order, controls, and one-time final gate |
| [registries/loop32_research_boundary.v0.json](registries/loop32_research_boundary.v0.json) | machine-readable four-mode calibration boundary, six-point budget, 32/16/48 partition floors, zero protected operations, and 22 false authorization fields |
| [docs/REAL_DATA_VALIDATION_2026-07-10.md](docs/REAL_DATA_VALIDATION_2026-07-10.md) | S21 alignment, session, and upstream audit |
| [docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md](docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md) | real EEG bridge and negative classifier result |
| [docs/LOOP_20_NEUROTOKEN_CACHE_V0.md](docs/LOOP_20_NEUROTOKEN_CACHE_V0.md) | NeuroTokenCache schema and synthetic interface proof |
| [docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md) | PyTorch precision, timing, memory, and energy primary-source review |
| [docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md](docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md) | frozen Loop 24 candidates, fresh fixtures, measurements, thresholds, caps, and decision language |
| [registries/local_precision_runtime_contract.v0.json](registries/local_precision_runtime_contract.v0.json) | machine-readable Loop 24 identities, schedules, refusals, access rules, and false authorization flags |
| [docs/LOOP_24_AUTHORIZATION_DECISION.md](docs/LOOP_24_AUTHORIZATION_DECISION.md) | scope-narrowed Loop 24 authorization, execution order, zero-runtime boundary, and real-data/training routing |
| [registries/loop24_authorization_decision.v0.json](registries/loop24_authorization_decision.v0.json) | hash-bound authorization record for the consumed target-free Loop 24 execution; every data/training/RW3/device flag remains false |
| [docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md](docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md) | measured float32/float16/qint8 result, unopened qualification proof, resources, access ledger, and parked decision |
| [docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md) | original official Brain2Qwerty, MNE, SciPy, and local-pipeline audit separating offline preprocessing from causal proof |
| [docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md](docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md) | immutable historical v0 registration, superseded before authorization |
| [registries/causal_preprocessing_contract.v0.json](registries/causal_preprocessing_contract.v0.json) | immutable historical v0 machine contract; never authorized |
| [docs/LOOP_25_ANTI_ALIAS_AUDIT.md](docs/LOOP_25_ANTI_ALIAS_AUDIT.md) | pinned Brain2Qwerty-to-NeuralSet-to-MNE execution trace and full folding-band defect analysis |
| [docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md](docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md) | current v1 dedicated anti-alias design, static pre-seed gate, timing semantics, and supersession boundary |
| [registries/causal_preprocessing_contract.v1.json](registries/causal_preprocessing_contract.v1.json) | current machine-readable Loop 25 amendment with every execution flag false |
| [docs/LOOP_25_AUTHORIZATION_PACKET_V1.md](docs/LOOP_25_AUTHORIZATION_PACKET_V1.md) | current exact bounded decision language and the work still forbidden even after authorization |
| [registries/loop25_authorization_request.v1.json](registries/loop25_authorization_request.v1.json) | green-amendment-bound replacement request; currently `authorized_now: false` |
| [registries/loop25_authorization_decision.v1.json](registries/loop25_authorization_decision.v1.json) | separate hash-bound authorization record for the one completed target-free execution; protected scopes remain false |
| [docs/LOOP_25_CAUSAL_PREPROCESSING_RESULT.md](docs/LOOP_25_CAUSAL_PREPROCESSING_RESULT.md) | measured static, fixture, replay, access, resource, warning, and claim-boundary closeout |
| [registries/loop25_causal_preprocessing_result.v1.json](registries/loop25_causal_preprocessing_result.v1.json) | machine-readable Loop 25 measurements, hashes, counters, pass decision, and no-rerun boundary |
| [docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md](docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md) | metadata-only file intake closeout |
| [docs/RW2_PRIMARY_SOURCE_RESEARCH.md](docs/RW2_PRIMARY_SOURCE_RESEARCH.md) | reader/quality primary-source review |
| [docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md](docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md) | frozen RW2 protocol |
| [docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md](docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md) | measured six-format RW2 implementation result |
| [docs/RW3_PRIMARY_SOURCE_RESEARCH.md](docs/RW3_PRIMARY_SOURCE_RESEARCH.md) | BrainFlow, LSL, PyXDF, and clock primary-source review |
| [docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md](docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md) | frozen replay/live-source protocol; no implementation |
| [registries/replay_equivalence_contract.v0.json](registries/replay_equivalence_contract.v0.json) | machine-readable RW3 schedules, fixtures, refusals, caps, and authorization flags |
| [docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md](docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md) | exact Stage A scope, acceptance gates, caps, forbidden work, and decision language |
| [registries/rw3_stage_a_authorization_request.v0.json](registries/rw3_stage_a_authorization_request.v0.json) | hash-bound machine request; currently `authorized_now: false` |
| [docs/BYO_NEURODATA_WORKBENCH_SPEC.md](docs/BYO_NEURODATA_WORKBENCH_SPEC.md) | staged local neurodata workbench contract |
| [docs/OPEN_SOURCE_READINESS.md](docs/OPEN_SOURCE_READINESS.md) | licensing, history, privacy, GitHub, and release gates |
| [registries/datasets.v0.json](registries/datasets.v0.json) | task-separated dataset candidates |
| [registries/devices.v0.json](registries/devices.v0.json) | device and modality metadata, not qualification |
| [docs/RISK_AND_ETHICS.md](docs/RISK_AND_ETHICS.md) | privacy, licensing, ethics, and communication boundary |

Loop-specific closeouts in `docs/LOOP_*.md` preserve exact commands, metrics,
resources, failures, and claims.

## Contributing

Contributions are welcome, especially:

- deterministic format fixtures and malformed cases;
- metadata-only compatibility reports;
- EEG reference, geometry, timing, and unit validation;
- offline device replay and packet-loss audits;
- no-signal controls and split-leakage tests;
- accessibility, setup, and documentation improvements;
- small CPU-bounded baselines with honest negative reporting.

Start with [CONTRIBUTING.md](CONTRIBUTING.md). It contains dedicated safe paths
for people with EEG recordings and people with EEG headsets or boards.

| You have | Best first contribution | Keep private or gated |
|---|---|---|
| An EEG recording | Run metadata-only intake locally and share a redacted compatibility summary | Waveforms, event text, participant paths, demographics, and unreviewed derived caches |
| An EEG headset or board | Document channels, reference, clocks, transport, packet counters, export formats, and SDK license | Live connection details, private endpoints, credentials, and unapproved recordings |
| No EEG hardware | Add deterministic fixtures, malformed cases, refusal tests, docs, or no-signal controls | No real data is needed for these high-value paths |

Precision or local-runtime contributions should begin by reviewing the parked
Loop 24 closeout and proposing a fresh hash-bound protocol. A benchmark pull
request is not authorization to retune seed 2401 or open seed 2402, smaller
weights are not proof of faster inference, and neither result is evidence of
brain decoding or end-to-end text latency.

Loop 43 planning research also defines a future independent artifact
reproduction challenge. That challenge is currently `Not Started` and
unauthorized: opening an issue, rerunning the repository, or contributing EEG
does not create a challenge submission. A future eligible result would show
that one released target-free software artifact reproduced in one independent
environment; it would not be scientific replication, neural decoding evidence,
or generalization to people, platforms, devices, or home use.

The project deliberately treats an exact refusal, a privacy-preserving metadata
report, or a reproducible negative result as a meaningful contribution. See
[I Have EEG Data](#i-have-eeg-data) and
[I Have An EEG Headset Or Board](#i-have-an-eeg-headset-or-board) for the
step-by-step routes.

Community files:

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Governance](GOVERNANCE.md)
- [Support](SUPPORT.md)
- [Security](SECURITY.md)

## License And Third-Party Terms

NeuroDecodeKit's original source code and documentation are licensed under the
[Apache License 2.0](LICENSE).

That license does not relicense Brain2Qwerty, SpanishBCBL, participant data,
models, papers, device SDKs, or optional dependencies. Brain2Qwerty and the
SpanishBCBL release are separately identified as `CC-BY-NC-4.0`; work using
them must respect their noncommercial and attribution terms.

Read [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before using upstream code,
data, or assets.

## Citation And Acknowledgments

Use [CITATION.cff](CITATION.cff) to cite NeuroDecodeKit. Cite every dataset,
paper, and upstream implementation separately; a software citation does not
replace participant-data attribution.

NeuroDecodeKit builds on the public research ecosystem around Brain2Qwerty,
SpanishBCBL/DECOMEG, MNE-Python, BIDS, and the broader EEG/MEG community. It is
independent and is not endorsed by those projects or institutions.

## Plain-English Bottom Line

**Engineering capability:** NeuroDecodeKit provides a bounded, local,
reproducible path from neurodata discovery and file qualification through
caches, controls, small baselines, causal interface tests, and inspectable
reports.

**Scientific claim not established:** the repository has not shown that neural
signal beats language-only controls for practical text decoding, generalizes to
new people, runs end to end in real time, or works on portable EEG hardware.
