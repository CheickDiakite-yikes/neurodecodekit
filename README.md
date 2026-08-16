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
| IACKD source compatibility | H1 found 96 29-row and 32 31-row headers. H2 then parsed all 316 public BIDS metadata bodies and confirmed one 26-channel predictive EEG core, 1024 Hz sampling, average reference, and complete central/occipital geometry in all 30 groups | The exact-36 reader assumption was wrong, but H2 still routed `IACKDR-R1`: HEOG, VEOG, and Trigger are source-typed `MISC`, exposing a frozen control-taxonomy bug before any EEG sample, event, target, model, or score was accessed |
| MARC-1 source eligibility | The Freewill central-directory inventory passed without payload, but the one source-aware Wrist metadata check later routed `MARC1SAL-R2` with zero selected subjects and zero payload bytes | The Wrist branch is consumed and blocked before acquisition; the private source route remains unavailable and is not inferred or repaired |
| MARC-2 confound triangulation | Five ordered work orders now test Freewill target choice, conditional EEG information beyond peripheral controls, one orthogonal cohort, and a Spanish inner-speech control ladder before any LLM can receive neural evidence | `MARC2-FW1C` consumed at `MARC2FWC-F02` after one structural read and zero selections. Artifact-only `MARC2-SL1` then found the exact integration defect: MARC-1 emits transport key `directory`, while the generated fixture and both MARC-2 validators require `central_directory`. This explains the refusal without reopening private data; archive, neural, target, model, and score access remain zero |
| Continuous interfaces | NeuroTokenCache preserves 553 valid synthetic frames; causal replay is exact across 5/5 schedules with zero right context | Cache and streaming contracts exist, but they do not establish useful neural representations or text decoding |
| Full-path causality gate | Loop 25 v1 passed a dedicated causal anti-alias audit, 65,537 response points, 23 alias probes, 168 schedule checks, 240 resume checks, and 72 future-mutation controls across 24 target-free items | The exact 1000-to-100 Hz path is mechanically causal with zero right context; this is synthetic mechanics evidence, not proof that neural information survives |
| Consumed S21 validation | The registered 2,908-parameter candidate reached macro CER `0.938177`; the train-only no-signal prior reached `0.751235`, so the candidate was worse by `0.186942` | Loop 26 is parked after one consumed six-target event; this is a clear negative result, not neural advantage |
| Artifact-only failure localization | The one-shot Stage A pass reproduced `99.3477%` primary blank, all 6/6 unstable fixed-prefix groups, and all 3/3 size-55 seeds worse than the prior | Loop 48 selected descriptive `F5` output-distribution instability in `0.0166` sec and 23.4 MB RSS; that phenotype is not a proven root cause |
| Train-only failure discrimination | The consumed Stage B primary reached macro CER `0.953566` versus `0.822045` for its train-only prior; all six full-size causal/linear fits were finite and stable, but none cleared the prior | `H4` stable nonseparability is supported and fixed timing-offset `H3` has evidence against it; the exact `L50-R05` route parks S24 acquisition for this model family, with no neural advantage or rerun |
| Temporal-representation repair | The consumed Stage C synthetic candidate reached CER `0.433333` and `1/8` exact versus ablation CER `1.000000`; its `0.566667` CER advantage passed, but the absolute `<=0.10` CER and `>=7/8` exact gates failed | Temporal context was usable on the purpose-built fixture, but Stage C is parked without rerun and establishes no real neural-decoding benefit |
| Fresh EEG acquisition gate | Loop 53 acquired and opaque-verified the exact public S20 session-2 block-2 bundle: 4 files, `96,090,264` bytes, `3.629499s`, 63,225,856-byte peak RSS, and all 10 gates passed | Acquisition mechanics are proven and the one invocation is consumed; no header, marker, signal sample, MAT field, target, cache, split, or model was interpreted or run |
| Fresh EEG qualification gate | Loop 54 separates strict VHDR-only metadata, target-blind VHDR+EEG quality, isolated target-bearing VMRK+MAT reconciliation, and aggregate closeout; L54-A bound one exact 11,705-byte header, 18 gates, 22 refusals, and a one-shot strict parser boundary | The one execution passed source size/hash and strict decoding but parked at `F11` because the format preamble did not match; L54-Q2 failed, no rerun is open, and stages B/C remain blocked |
| Fresh EEG neural-effect design | Loop 55 now separates a causal pre-keypress performed-hand gate from a harder causal 29-key gate, with performed actions as primary targets, a post-keypress diagnostic, 12 matched conditions, exact trial-level tests, and one-shot target order | Planning research is complete and Loop 54 dependent; the S20 bundle is acquired but uninterpreted, the experiment is `Not Started`, and no target, model, prediction, score, neural advantage, or decoding result exists |
| Bounded AI research guard | A dependency-free Loop 55 policy now validates and hashes strict synthetic AI recipe proposals, rejects target leakage, future context, LLMs, pretrained weights, unknown fields, model runs, and cap expansion, and reserves at most four future train-inner proposal rounds inside the existing 12-fit ceiling | The synthetic interface is implemented and measured; no AI proposal has accessed S20, trained a model, or produced neural evidence, and any future real proposal phase remains Loop 54 dependent and separately Tier C authorized |
| Open EEG R&D strategy | Current 2025-2026 evidence supports the compact specialist path and adds a prospective 23,248,224-byte public motor positive control, an interpretable motor-physiology rung, classical EEG baselines, and local-first contributor receipts | Research and planning only: no public EEG payload, S20 content, model, target, or pretrained weight was opened, and every real execution remains separately Tier C gated |
| Causal Motor Lattice architecture | The exact 4,535-parameter `CML-v0` learned all constructed signal-bearing check rows at `1.0` hand/key accuracy, localized all three registered branches, passed hand/key marginal-consistency and causal future-tail checks, and replayed its checkpoint exactly | The one synthetic run passed 18/19 gates but parked at `CML-R0` when float32 common-mode error `1.9073486e-6` exceeded the frozen `1e-6` tolerance; final stayed closed, there is no rerun, and no real EEG or scientific result exists |
| Foundation-model decoder bridge | FM-0 compiled all 12 synthetic plans; the one FM-1 Terra invocation then attempted 3 calls, returned 2 strict responses, and parked on a non-completed `FM-A02` response after 8.406 seconds at 39.3 MB peak RSS | Live bounded transport and fail-closed receipts worked, but the four-arm matrix did not complete and has no rerun; no real neural evidence or target was used, so no decoding or neural result exists |
| AI budget and local-tool leverage | A $50 aggregate provider ceiling is split into conservative experiment caps while MNE, MOABB, pyRiemann, Braindecode, and future cEEGrid adapters carry local work first | The budget is not a spend target; $0.50 is reserved for incomplete FM-1 accounting, at least $30 stays behind future evidence gates, and a pending earbud-electrode patent is architecture context, not proof that AirPods read thoughts |
| Local EEG tooling inventory | One green, zero-network audit found NumPy `2.5.0`, SciPy `1.18.0`, and MNE `1.12.1`; array/signal mechanics, BrainVision reading, and ICA are available in 14.53 seconds at 173.2 MB maximum child RSS, while scikit-learn, pyRiemann, MOABB, and Braindecode are absent | The next synthetic fixture work can proceed without an install; availability is engineering evidence only and establishes no dataset quality, neural effect, model accuracy, or device result |
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

The first real-content stage is now consumed and parked. L54-A
binds exactly one 11,705-byte S20 VHDR and requires a strict standard-library
parser that cannot resolve, stat, or open its EEG, VMRK, or MAT siblings. Its
18 acceptance gates, 22 refusal classes, one-thread/worker limit, 30-second and
256 MiB caps, one content open, one execution, and 1 MiB output ceiling are in
`docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md` and
`registries/loop54_stage_a_vhdr_contract.v0.json`. Recovery-bound decision
`2177b36` passed CI `31286428489` before implementation. The parser now strictly
supports declared UTF-8, UTF-8 BOM, and explicitly declared Windows-1252;
rejects malformed sections, keys, channels, sampling, source hashes, paths,
outputs, operations, and claims; and emits only allowlisted declarations. Its
24 focused tests and 24 mutation subchecks cover all 22 refusal classes.
Implementation `b486fdf` passed CI `31287819503` before the one registered
execution opened exactly 11,705 VHDR bytes once. Source size, Git-blob identity,
and strict decoding passed; required-structure validation parked at
`L54A-F11` because the format preamble was missing under the frozen contract.
The command used 0.20 seconds and 24,051,712-byte peak RSS, touched no sibling,
signal, marker, MAT, target, model, network, or hardware surface, and wrote no
registered output. L54-Q2 was not established, no rerun is open, and Loop 54-B
and 54-C remain blocked. See `docs/LOOP_54_STAGE_A_VHDR_RESULT.md` and
`registries/loop54_stage_a_vhdr_result.v0.json`.

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

The 2026-08-06 open EEG strategy refresh confirms that this specialist-first
path is still the correct laptop-scale scientific choice. Two current open
benchmarks report that specialist models remain competitive, linear probing is
often insufficient, and larger EEG foundation models do not consistently
generalize better. The refresh therefore adds three prospective upgrades
without changing any authorization: a tiny public left/right motor-execution
positive control before protected discovery, one externally selected classical
EEG baseline plus an interpretable pre-keypress physiology assay, and
local-first hash-bound receipts for EEG contributors. Foundation models remain
a separate public-data watch lane, and generative channel imputation may not
support primary evidence. See
`docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md` and
`registries/open_eeg_rd_strategy.v0.json`.

The architecture research made that specialist path concrete, and a separate
bounded synthetic gate has now exercised it. `CML-v0` separates slow potential
shape, causal mu energy, and causal beta energy; each view has a rank-8 spatial
mixer and three time cells. A 24-dimensional bottleneck feeds a fixed physical
keyboard lattice plus a small 29-key residual. Hand probability is an exact
marginal of the key distribution rather than a contradictory second head. The
exact parameter formula is `24C + 2,549 + 25P`; at 64 channels and the maximum
18 primitives it is 4,535 parameters.

The one synthetic run learned all 16 constructed signal-bearing check rows,
routed each registered factor to its matching branch, preserved exact replay,
and passed every resource and access gate. It nevertheless parked because the
maximum float32 common-mode logit difference was `1.9073486e-6`, above the
preregistered `1e-6` ceiling. That exact failure cannot be waived after seeing
it; seed 5513 is consumed, final remained undelivered, and there is no rerun.
Perfect performance on invented factors is software evidence only and cannot
prove cortical physiology or neural decoding.

The qualification ladder is now two-axis because one tiny public dataset does
not test both questions. The existing 23,248,224-byte PhysioNet prospect tests
left/right execution mechanics; a separately scoped 2026 EEG+EMG MRCP slice
would test true pre-movement alignment against EMG onset. Both remain
undownloaded and unauthorized, and both must pass independently before this
architecture can become eligible for a future S20 freeze. See the architecture
research plus `docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_PREREGISTRATION.md`,
`docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_IMPLEMENTATION.md`, and
`docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_RESULT.md` with their matching registries.

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
| Current WO9R result verification | 29 implementation tests, 5 public-freeze invariants, and 7 aggregate-result invariants; 72 real EDFs; 1,080 events; 144 fits; 216 frozen prediction sets; one 360-target score | Implementation `8242674` passed CI `31359548779`; freeze `8cd45d7` passed CI `31360781199` before the one target delivery; result routed `WO9R-R3` with zero post-target updates or reruns | Makes the positive execution/imagery task-information result and the failed localization/confound conjunction independently checkable without publishing individual outputs |
| MARC-1 next-effect research | 2 selected licensed axes; 14-member generated ZIP; 2 modality profiles; 12 comparators; 24/24 adversarial refusals; 51 focused tests; 2,273 complete-suite tests; 0 payload/model/score operations | Exact implementation `e35a587` passed CI `31505555044` before one generated closeout; `MARC1G-R1` passed in 0.006589 sec at 23.5 MB peak RSS and is consumed | Proves the bounded ZIP and multimodal firewall mechanics needed for the next experiment, while adding no human-neural or decoding evidence |
| MARC1-CD1 storage-safe archive qualification | 13.59 GB virtual ZIP; 280,249 generated bytes; 128 KiB trailer; 148,910-byte central directory; 18 entries; 32/32 refusals; 14/14 gates; 0 live requests | Exact implementation `211fd78` passed CI `31511626051` before one closeout; `MARC1CDG-R1` passed in 0.006544 sec at 27.1 MB peak RSS and is consumed | Validates exact range, redirect, EOCD/ZIP64, directory, privacy, replay, and resource mechanics without a whole download; live inventory and all neural claims remain unavailable |
| MARC1-CD1A decision routing | 12 decision invariants; 168 focused tests; 2,378 optional-neuro tests with 35 expected skips; 0 public requests | Request `950796d` passed CI `31513578445`; decision `624cc4e` passed CI `31519016891` before wrapper work | Authorized only the staged wrapper-then-one-audit sequence after two green milestones; added no archive-content or neural evidence |
| MARC1-CD1A live archive inventory | 13.59 GB virtual ZIP; 306,758 accepted metadata bytes; 1,227 entries; 1,025 files; 202 directories; 14/14 gates; 0 archive/member payload bytes | Exact wrapper `5dfa3c4` passed CI `31521510374` before one invocation; `MARC1CD-R1` passed in 2.727 sec at 43,974,656-byte peak RSS and is consumed | Adds a real, storage-safe map of the public archive without downloading it; member selection, neural data, models, scores, and scientific claims remain closed |
| MARC1-P1 generated pilot selector | 1,227 + 55 generated rows; 12 preregistered participants per axis; 72 Freewill bundles/288 members; 12 Wrist archives; 36/36 refusals; 15/15 gates; 0 real operations | Exact implementation `0c0a698` passed CI `31571668853` before the one closeout; `MARC1PSG-R1` used 873,348 input and 182,564 output bytes in 0.227 sec at 32.4 MB reported RSS and is consumed | Proves deterministic, private, size-independent pilot selection mechanics under an 8-GiB ceiling; adds no neural or thought-to-text evidence |
| MARC1-P1A live metadata attempt | 418,755 private metadata bytes read once; 1 Wrist response opened; 0 public-body or payload bytes; 0 selected participants; route `MARC1PS-F03` | Exact wrapper `702e613` passed CI `31578614616` before the sole attempt; it failed the explicit identity-encoding gate in 0.532 sec at 37.3 MB reported RSS and is consumed | Proves one-shot fail-closed audit behavior; the cohort was not selected and no neural or language evidence was produced |
| MARC1-HT1 HTTP identity research | RFC 9110 Sections 8.4 and 12.5.3; 4 future acceptance cases; 20 future refusals; 17 false authorization flags; 0 real operations | Artifact-only standards review after green consumed result `8d9cae1`; candidate policy hash `ac1b98ee...` | Separates absent content coding from actual coding without inferring the unretained live header; implementation and real access remain closed |
| MARC1-HT1 generated recovery contract | 1,227 + 55 generated rows; 4 accepted forms; 20 refusals; 16 gates; 5 refusal routes; 0 real/network bytes | Green research `f515b36` / CI `31580575669` precedes the frozen contract | Allows only a new `plan`/`qualify`/`inspect` harness after contract CI; real metadata, payload, neural work, and claims remain closed |
| MARC1-HT1 generated recovery implementation | 923,052 generated input bytes; 4/4 accepted forms; 20/20 refusals; 16/16 gates; exact 12+12 cohort and split replay; 0 real/network bytes | Development `MARC1HT-G1` passed in 0.109 sec at 32.7 MB external peak RSS; 29 new tests; registered closeout awaits implementation CI | Proves the standards-aligned uncoded-response predicate and frozen selector compose deterministically; live-source compatibility and all neural/language claims remain untested |
| MARC1-HT1 registered generated closeout | 923,052 generated input bytes; 182,681 temporary output bytes; 4/4 forms; 20/20 refusals; 16/16 gates; 0 real/network bytes | Exact implementation `b2cb48c` passed CI `31583931303` before one 0.112-sec closeout at 33.1 MB external peak RSS; consumed with no rerun | Confirms the repaired transport/selector/privacy stack end to end on fixtures; a new live attempt still needs a separate Tier C sequence and no scientific claim changed |
| MARC1-HT1A live-recovery request | One future 418,755-byte sealed-manifest read; one future Wrist body capped at 2 MiB; one new isolated root; 0 payload bytes; all current permissions false | Binds green result `5344d73` / CI `31584662864`, the frozen selector, and the consumed `MARC1PS-F03` boundary; requires its own green CI before any decision | Proposes one additive wrapper and one metadata-only attempt on the same thought-to-text path; the packet itself performs no operation and establishes no scientific result |
| MARC1-HT1A packet-bound decision | Exact 76-byte maintainer message; one green packet; one future generated/mock wrapper; one future metadata-only attempt; 0 current data/model operations | Request `27f39ae` passed CI `31586256906`; decision records the fresh approval but is ineffective until its own CI is green | Preserves thought-to-text as the objective without predeclaring an outcome or expanding the zero-payload metadata scope |
| MARC1-PG1 generated pagination lane | Development: 4/4 accepted cases, 41/41 refusals, 18/18 gates. Registered closeout: route `MARC1PG-F07`, 0 output bytes, 0 real/network bytes | Exact implementation `2c98a2a` passed CI `31593790492`; the sole closeout then refused a symlink output parent in 0.17 sec at 30,064,640-byte external peak RSS and is consumed without retry | Preserves a real process defect: output preflight happened after fixture construction. A new generated recovery must move it first; no live pagination or scientific result exists |
| MARC1-OP1 output-capability research | One 672-byte candidate policy; held parent descriptor; device/inode binding; ancestor no-follow checks; parent-relative create/write/cleanup; 19 required pre-capability refusals; 0 fixture/network/real operations | Green consumed result `a4dcaea` / CI `31594881048` precedes this artifact-only design | Makes safe output authority the first future operation and refuses platforms that cannot enforce it; implementation and another generated run remain closed until their own green milestones |
| MARC1-OP1 generated recovery contract | 6 accepted cases; 32 refusals; 10 routes; 20 gates; one exact `/private/tmp` path probe; one conditional generated qualifier; 0 current operations | Green research `d02830b` / CI `31595996923` precedes the frozen contract | Requires capability acquisition before any repository/fixture work, bans the consumed qualifier, and preserves exact pagination/cohort identity; implementation remains closed until contract CI |
| MARC1-OP1 output-capability implementation | 1,019,776 generated input bytes; 184,173 temporary output bytes; 6/6 accepted cases; 32/32 refusals; 20/20 gates; exact cleanup; 0 real/network bytes | Green contract `baade51` / CI `31597291352` preceded development `MARC1OP-G1`, which ran in 0.096 sec at 33.8 MB reported RSS; 36 new tests | Proves generated pagination and selection can run only after held output authority and leave no artifact; the registered probe awaits implementation CI and no neural/language claim changed |
| MARC1-OP1 registered generated result | `MARC1OP-P0` preflight then `MARC1OP-G1`; 1,019,776 generated input bytes; 184,173 temporary output bytes; exact cleanup; 0 live/network bytes | Exact implementation `fcedcc3` passed CI `31600085119` before the one 0.098-sec qualifier at 33.9 MB reported RSS; both invocations consumed | Establishes the capability-first generated stack under registered controls; a live metadata request remains a separate Tier C gate and no scientific claim changed |
| MARC1-LM1 paginated live-metadata request | One future exact `page=1&page_size=1000` GET; one body capped at 2 MiB; one 55-row target-free inventory; 0 payload bytes; all current permissions false | Green capability result `ca4679a` / CI `31601329375` precedes the packet; 13 focused, 612 MARC, 2,751 base, and 2,822 optional tests pass locally | Proposes one additive wrapper and one no-retry metadata check on the same thought-to-text path; the packet itself performs no operation and establishes no scientific result |
| MARC1-LM1 packet-bound decision | Exact 76-byte maintainer approval; one immutable green request; one conditional generated wrapper and one later metadata response; 0 decision-time data/model operations | Request `4d3eb19` passed CI `31603530015`; decision `060a365` passed CI `31604608307` before implementation | Preserves thought-to-text as the objective while binding only the registered metadata scope and refusing to predeclare a scientific outcome |
| MARC1-LM1 generated/mock implementation | 4/4 transport forms; 36/36 refusals; 20/20 gates; exact 55/45/10 inventory and frozen 12-subject split; 184,466 generated input bytes; 19,030 temporary output bytes | Corrected development `MARC1LM-G1` ran in 0.0303 sec at 43,057,152-byte reported RSS; first push `8f67af2` failed only Linux temp-parent portability and performed zero real operations | Adds a capability-first, target-firewalled, aggregate-safe one-response wrapper on the same path; generated metadata work is not neural, decoding, language, or thought-to-text evidence |
| MARC1-LM1 consumed live metadata | One 15,652-byte version-3 metadata body; strict JSON parse; `MARC1LM-F04` at the frozen inventory validator; 0 selected subjects and 0 payload bytes | Exact implementation `f9a1ece` passed CI `31611639130` before the sole request; 1.095 sec, 33,996,800-byte peak RSS, 4,207 output bytes; no retry | Proves bounded live fail-closed behavior and invalidates use of the frozen inventory as a payload gate; it does not identify the changed predicate or add neural, language, or thought-to-text evidence |
| MARC1-SA1 source-aware attestation research | Five-field official public core; two optional MD5 extensions; 21 aggregate predicates; seven domain-separated identity hashes; 0 real operations | Green consumed result `d859509` / CI `31612923903` anchors a Tier A design with 12 invariant tests | Separates source schema, cohort identity, and later byte-level integrity so the next one-shot check can localize drift without weakening privacy or changing the scientific path |
| MARC1-SA1 generated-only contract | Six semantic fixture families; 21 predicates; seven identity domains; 52 refusals; 25 gates; exactly `plan`/`qualify`/`inspect`; 0 live or payload operations | Research `aa80503` passed CI `31614330447` before the strict versioned contract was frozen; 13 focused tests pass | Freezes a source-aware attestor before implementation while keeping every live, neural, target, model, and claim boundary closed; this remains cohort-integrity work on the same thought-to-text path |
| MARC1-SA1 generated implementation | Six family routes; 52/52 refusals; 25/25 gates; 732,811 generated input bytes; 109,589 temporary output bytes; exact cleanup | Green contract `8f64ccb` / CI `31616551270` preceded development `MARC1SA-G1`; exact implementation `feb3b83` later passed CI `31619037335` | Adds deterministic aggregate drift localization and optional-MD5 handling without a network or payload surface; no neural/language claim changed |
| MARC1-SA1 registered generated closeout | Six family routes; 21 predicates; seven identity domains; 52/52 refusals; 25/25 gates; 732,811 generated input and 109,589 temporary output bytes; exact cleanup | Exact implementation `feb3b83` passed CI `31619037335` before the one 0.0534-sec closeout at 27,885,568-byte reported peak RSS; consumed with no rerun | Confirms source-aware schema, optional checksum, aggregate drift, privacy, and resource mechanics compose on fixtures; live metadata and every neural/language claim remain closed |
| MARC1-SA1A live-metadata request | One future exact GET; one body capped at 2 MiB; source-aware R1-R4 routing; 0 payload bytes; all current permissions false | Green generated result `094b6cb` / CI `31620515340` anchors the immutable packet; 14 request invariants pass | Proposes one additive wrapper and one metadata-only attempt after a fresh packet-bound decision; the packet performs no operation and preserves the same thought-to-text path |
| MARC1-SA1A packet-bound decision | Exact 31-byte maintainer instruction; one immutable green request; one conditional generated/mock wrapper and one later metadata response; 0 decision-time data/model operations | Request `b077550` passed CI `31621794066`; this decision remains ineffective until its own commit passes both CI jobs | Authorizes only the identified metadata sequence; selective acquisition, neural experiments, scoring, replication, and language work remain separately gated |
| MARC1-SA1A source-aware wrapper | Six source-schema families; three HTTP framing forms; 31 refusals; 20 gates; 84,422 generated response bytes; 24,064 transient output bytes; 0 development-time real requests or payload bytes | Decision `ef9ab91` passed CI `31670457497` before development `MARC1SAL-G1`; exact wrapper `74aff21` then passed CI `31672761644` before the sole request | Adds a capability-first, privacy-separated one-response implementation that can retain an eligible cohort or block on localized drift; generated metadata is not neural or language evidence |
| MARC1-SA1A consumed source-aware metadata | One bounded metadata response; wrapper route `MARC1SAL-R2`; 0 selected subjects; 0 archive requests; 0 payload bytes; 23,112 retained bytes | Exact wrapper `74aff21` passed both CI jobs before the one 0.697-sec request at 33,439,744-byte peak RSS; lane consumed with no retry | The source-aware gate correctly blocked the frozen Wrist cohort before payload. R3 versus R4 details remain unavailable; this is an engineering stop, not neural or thought-to-text evidence |

### Real-Data Scientific Scorecard

| Evaluation | Neural result | No-signal result | Honest decision |
|---|---:|---:|---|
| S21 session-1 strict five-row sentence test | 163 character edits | 164 character edits | Near-null difference; paired interval spans benefit and harm |
| S21 session-2 same-person transfer | CER `0.9179` | CER `0.7755` | Neural model is materially worse; session is consumed |
| S7 EEG within-session key events | exact accuracy `0.91%` | exact accuracy `12.27%` | Neural template is materially worse; EEG bridge is mechanics only |
| S21 session-1 reserved six-sentence gate | macro CER `0.938177` | macro CER `0.751235` | Fixed causal candidate is worse by `0.186942`; Loops 26/31/33 are consumed and parked |
| S21 source-train 11-row diagnostic | macro CER `0.953566` | macro CER `0.822045` | Post-outcome Stage B supports stable nonseparability for this model family; these historically used rows are not fresh validation |
| PhysioNet S004-S015 held-out execution | balanced accuracy `0.680975`; 123/180; 9/12 participants above chance; `p=0.002930` | balanced accuracy `0.490722` | Prespecified low-frequency task-information confirmation passed, but localization and confound gates failed |
| PhysioNet S004-S015 held-out imagery | balanced accuracy `0.728014`; 131/180; 12/12 participants above chance; `p=0.000244` | balanced accuracy `0.507411` | Task-mode robustness passed; this remains cue/ocular-compatible and is not brain-specific proof |

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
- **Loop 54-A strict VHDR preregistration:** registration commit `c114623`
  freezes one exact 11,705-byte S20 VHDR, a base-Python-only parser, inert
  sibling basenames, 18 acceptance gates, 22 refusals, one content open, and
  one registered execution under 30-second, 256 MiB RSS, and 1 MiB output
  limits. Contract preparation performed zero S20 path stats and zero header,
  marker, signal, MAT, target, model, or network reads. Exact Tier C
  authorization remains pending. Exact-commit CI run `31127199848` was retried:
  the neuro-reader job passed, while Base Python selected Ruff `0.16.2` from a
  floating historical requirement and stopped on 400 later lint findings. The
  three frozen registration artifacts remain byte-identical at pinned commit
  `2232993`, whose CI `31132586790` passed both jobs, and an exact-tree Ruff
  `0.15.20` replay passed 1,095 tests with three skips. The additive recovery
  record preserves that distinction. The recovery-bound v1 packet in
  `docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md` and machine request in
  `registries/loop54_stage_a_recovery_authorization_request.v1.json` bind the
  immutable registration, green pinned anchor, green recovery record, exact
  resource envelope, and two-step green evidence order. Every authorization
  flag remains false in those immutable snapshots. Request commit `19813a8`
  passed CI `31283297030`, and the exact Tier C sentence is now preserved in
  `docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_DECISION.md` and its machine
  decision. Decision commit `2177b36` passed CI `31286428489`, including Base
  Python job `93176025548` and Optional Neuro Readers job `93176025560`, before
  parser work began. The dependency-free implementation validates strict
  codepages, sections, inert sibling basenames, ordered channels, decimal
  sampling, no-follow source identity, bounded exclusive output, and all 22
  refusal classes on generated synthetic fixtures. No generated fixture was
  retained. Exact implementation `b486fdf` then passed CI `31287819503` before
  the one execution. It opened and read the exact 11,705-byte VHDR once; source
  size, Git-blob identity, and strict decoding passed, but the frozen format
  preamble gate failed at `F11`. The raw first line was not published, sibling
  and protected counters stayed zero, output bytes stayed zero, L54-Q2 did not
  pass, and no rerun or Loop 54-B/C route is open.
- **Local EEG tooling audit:** implementation commit `e1de855` passed exact-SHA
  push CI `31277731869` before one zero-network inventory. NumPy `2.5.0` and
  SciPy `1.18.0` expose the bounded array/signal core; MNE `1.12.1` exposes its
  BrainVision reader and ICA, while CSP is incomplete and scikit-learn,
  pyRiemann, MOABB, and Braindecode are absent. The run finished in
  `14.52799025` seconds at `173,211,648`-byte maximum child RSS and wrote 9,416
  bytes. All real/protected, raw-signal, target, model, training, inference,
  scoring, network, provider, and hardware counters are zero. No broad install
  follows; the next work order is a NumPy/SciPy synthetic physiology fixture
  pack. Its fixture-only Tier B contract freezes seed `5503`, 96 paired items,
  eight factor families, a 48/32/16 split, eight deterministic mutations, and
  a 4 MiB cap. Contract commit `9238fd7` and implementation commit `ad361c8`
  were remotely green before one measured closeout. All 18 gates passed in
  `1.20` seconds at `118,177,792`-byte peak RSS with 584,308 output bytes. The
  generated NPZ and sidecar were removed, and every real-data, target, model,
  training, inference, scoring, network, provider, and hardware counter was
  zero. Work order 4 now freezes three unexecuted adapter plans: low-frequency
  shrinkage LDA, causal CSP-LDA, and Riemannian MDM. No winner is selected, no
  optional package is installed or imported, and twelve leakage mutations must
  fail closed before any future adapter execution. Exact implementation
  `eefb7b0` passed CI `31280581308` before one measured symbolic roundtrip.
  All 18 gates passed in `0.12` seconds at `22,822,912`-byte peak RSS with a
  27,335-byte plan that was removed. This qualifies the interface and leakage
  guards only; no adapter was selected, imported, fitted, inferred, or scored.
  Work order 5 now freezes synthetic contact-mask, channel-noise, and
  missing-channel semantics: 48 seed-5505 items, 16 generic bilateral channels,
  six separate masks, a fixed four-per-side target-blind policy, and 16
  fail-closed mutations. It is a post-acquisition interface, not physical
  switching, a consumer-earbud claim, hardware work, or real data. Contract
  commit `c6e216f` passed CI `31281290300` before a lazy-NumPy implementation
  added deterministic NPZ/sidecar creation, strict mask and provenance hashes,
  metadata-only inspection, resource guards, and two CLI commands. Exact
  implementation `76ccc63` passed CI `31282344300` before one measured
  synthetic roundtrip. All 18 gates passed in 0.40 seconds at 55,394,304-byte
  peak RSS with 938,874 generated bytes; both temporary files were removed.
  Work order 5 is complete. This is interface evidence only, not ear-EEG or
  decoding evidence.
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
- **Open EEG R&D strategy refresh:** current EEG-FM-Compass, ST-EEGFormer,
  preprocessing, motor-physiology, and official tool evidence supports keeping
  the specialist-first route. A prospective public positive control binds only
  S001-S003 PhysioNet motor-execution runs 3/7/11, nine EDF files and
  23,248,224 public-metadata bytes under a future 32 MiB network cap. It would
  qualify one classical family before S20, then pair that family with a fixed
  causal motor-physiology assay and the compact model. No public payload,
  protected content, model, checkpoint, target, or pretrained weight opened;
  the strategy is not an execution contract.
- **PhysioNet motor acquisition implementation:** registration `2a7b418` and
  authorization decision `00b91ed` were remotely green before a separate
  standard-library executor was built. `neurodecode physionet-motor-acquire`
  defaults to a no-stat, no-network plan. Its gated mode allowlists three
  metadata documents and nine EDF HEADs, refuses redirects and retries,
  streams only the nine exact S001-S003 runs 03/07/11 files, hashes each local
  file exactly once without parsing it, promotes only the complete directory,
  and writes bounded private receipts. Twenty-three adversarial tests use only
  generated invalid-UTF-8 bytes and mocked responses; the implementation suite
  passed 1,448 tests with 3 expected skips and 493 subtests. Exact implementation
  `92760ce` then passed both CI jobs before the one registered invocation. All
  12 acquisition gates passed: nine requests transferred exactly 23,248,224
  EDF bytes, every one-pass local SHA-256 matched, runtime was 50.682373
  seconds, peak RSS was 55,181,312 bytes, and peak incremental disk was
  28,327,635 bytes. Every header, annotation, event, signal, target, channel,
  split, model, training, inference, scoring, retry, rerun, and work-order-9
  counter stayed zero. This is an acquisition-integrity result, not an EEG or
  decoding result. Work order 8 is complete and consumed; the Git-ignored
  payload and private receipts must not be published or reopened. The later
  10 GB allowance remains future headroom. Work order 9 later consumed its own
  separately gated target-blind execution without adding data.
  The post-result suite passes 1,455 tests with the same 3 expected skips and
  493 subtests.
- **Public EEG positive-control result:** work order 9 is no longer a
  generic "try a classifier" idea. Its prospective contract reuses only the
  nine acquired EDFs and requires three evidence axes to pass together:
  held-out run-11 prediction, motor-compatible central mu/beta physiology, and
  fixed confound/leakage controls. Runs 03/07 alone may select between
  four-component CSP plus shrinkage LDA and regularized Riemannian MDM. All 12
  primary/control prediction sets must freeze in a hash-only commit that is
  pushed and remotely green before the isolated scorer receives the same 45
  run-11 targets once. The primary gate requires at least 30/45 correct,
  pooled balanced accuracy at least 0.65, macro-participant balanced accuracy
  at least 0.60, a one-sided fixed-seed permutation p-value at most 0.05, and a
  win over the train-only no-signal prior. Pre-cue, timing-only, label-
  deranged, trial-displaced, channel-deranged, hemisphere-swapped, central,
  and frontal/occipital proxy results prevent an accuracy-only claim. Even a
  complete pass is only a three-person motor-task EEG pilot; it is not typing,
  language, thought reading, unseen-person generalization, or brain-specific
  proof. Registration authorizes no EDF access or model operation. Read
  [the primary-source rationale](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PRIMARY_SOURCE_RESEARCH.md)
  and [the preregistration](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREREGISTRATION.md).
  Registration `3c00557` passed both jobs in CI `31346882592`. A separate
  [exact Tier C packet](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_PACKET.md)
  binds that green snapshot. Request `c62b10a` then passed Base Python job
  `93331241434` and Optional Neuro Readers job `93331241411` in CI
  `31347209691`, after which the maintainer supplied the exact registered
  sentence. Authorization-only commit `da9399c` passed both required jobs in
  CI `31348287824` before implementation. The new dry-run-first CLI, sequential
  MNE reader, exact 90/45 participant-run split, target-firewalled derivatives,
  causal filters, fixed CSP-LDA/Riemannian families, 12 prediction/control
  sets, per-condition hashes, and isolated aggregate scorer are now qualified
  on generated arrays. The final fixture used nine runs and 135 events, made
  33 fits and 45 target-blind inferences, froze 12 sets, and passed in 8.961233
  seconds at 327,647,232-byte peak RSS with 20,825,424 generated bytes. Real
  data, real target, and network reads were zero, and the fixture output was
  removed. Its synthetic `WO9-V2` route has no claim value. Read the
  [implementation record](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_IMPLEMENTATION.md).
  Exact implementation `52b9b15` then passed both jobs in CI `31351728650`
  before the one real target-blind execution. All nine EDF hashes and semantic
  parses passed; 135 events produced 90 fit rows and 45 target-free final
  signal rows. CSP-LDA was selected from runs 03/07, 33 fits and 45 target-
  blind inferences produced all 12 aggregate-hashed prediction sets, and the
  model stage stopped with zero final-target deliveries or scores. Runtime was
  3.054760 seconds, peak RSS was 460,734,464 bytes, private output was
  20,852,059 bytes, and network/retry/rerun counters were zero. Read the
  [aggregate freeze record](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREDICTION_FREEZE.md).
  Freeze `01eeff6` passed both jobs in CI `31352250838` before the same 45
  targets opened once. The selected 8-30 Hz primary reached **27/45**, **0.604
  balanced accuracy**, and `p=0.137`; it beat the 0.500 no-signal prior but
  failed the frozen primary gate, so the registered verdict is **`WO9-V1`**.
  The prespecified 0.5-4 Hz comparator delivered the strongest real result:
  **36/45**, **0.800 balanced accuracy**, **3/3 participants above chance**,
  and **`p=0.000183`** on held-out run 11. That is genuine task-information
  evidence, but it is not retrospectively promoted to the primary result.
  Motor-compatible physiology was directionally negative in 2/3 participants
  but nonsignificant (`p=0.108`), and central sensors did not beat the
  frontal/occipital proxy. The correct conclusion is a strong, compact
  low-frequency lead that now deserves independent replication and confound
  localization, not proof of brain-specific motor decoding. Read the
  [full result and condition breakdown](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_RESULT.md).
  Work order 9 is complete and consumed with no rerun.
- **WO9R low-frequency cohort-confirmation result:** the strongest WO9 lead
  survived a prospective test in twelve untouched participants. The fixed
  `0.5-4 Hz` whole-head shrinkage-LDA recipe was trained within participant on
  runs 03/07 or 04/08, frozen across 216 participant-condition prediction sets,
  and scored once on held-out execution run 11 and imagery run 12. Combined
  freeze `8cd45d7` passed both jobs in CI `31360781199` before the 360 targets
  opened. Execution passed all H1 gates at **123/180**, pooled balanced
  accuracy **0.680975**, macro-participant balanced accuracy **0.682292**,
  9/12 participants above chance, and **`p=0.002930`**. Imagery passed all H2
  gates at **131/180**, pooled **0.728014**, macro **0.728423**, 12/12 above
  chance, and **`p=0.000244`**. Execution-to-imagery and imagery-to-execution
  transfer were also positive at pooled balanced accuracies **0.728261** and
  **0.695077**. This is the project's clearest preregistered multi-person EEG
  task-information result so far.

  The maximum claim gate still failed. Central sensorimotor balanced accuracy
  was **0.647575**, below the frontal proxy's **0.671821**; only 5/12
  participants followed the registered physiology direction; and the early
  cue window reached **0.762865**, stronger than the primary execution window.
  Frontal and frontal-asymmetry controls also exceeded their ceilings. The
  frozen router therefore returned **`WO9R-R3`**: robust task information
  across execution and imagery, without motor-compatible localization. The
  result does not establish brain-specific origin, unseen-person
  generalization, typing, language or thought decoding, real-time operation,
  portable hardware, or clinical utility. Read the [full aggregate result and
  control breakdown](docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_RESULT.md).
  WO9R is complete and consumed with no rerun or post-target tuning.
- **IACKD-1 Cue-to-Action Reversal, consumed at its reader gate:** WO9R's strongest
  unresolved question is now a direct prospective test rather than another
  classifier comparison. The public CC0 OpenNeuro `ds006840` release provides
  15 participants, 32-channel 1,024 Hz EEG, raw HEOG/VEOG, synchronized Leap
  Motion hand trajectories, and congruent/incongruent visuomotor mappings. The
  frozen design fits the exact compact `0.5-4 Hz` shrinkage-LDA family only on
  earlier congruent trials, then freezes one held-out incongruent run per
  participant and moving hand. The isolated scorer applies actual hand
  direction and the opposite visual target direction to the **same**
  predictions. That cleanly distinguishes an action-following representation
  from a cue-following one.

  The metadata-only inventory binds 1,340 raw-source objects totaling exactly
  **7,249,113,684 bytes**, under the approved 10 GiB ceiling, while excluding
  published MATLAB derivatives, demographics, and scan tables. The contract
  keeps one CPU thread, no dependency installation, a 300-fit ceiling, exactly
  420 prediction sets, a 30 ms target-blind motion guard, direct EOG and timing
  controls, one hash-only prediction freeze, and one combined target delivery.
  Exact implementation `f5c36ba` passed both jobs in CI `31409141349` before
  real access. The one acquisition then passed: **1,340 objects**, exactly
  **7,249,113,684 bytes**, 1,340 streaming SHA-256 passes, zero content parses,
  679.749484 seconds, and 126,205,952-byte peak RSS. The one analysis completed
  a second full object-hash pass, then failed closed on its first lazy
  BrainVision parse at registered refusal **`IACKD-F10`** because the observed
  channel inventory did not satisfy the frozen combined `32+4` gate. The
  actual channel count and names were not retained, so the result does not
  guess which predicate failed. No signal sample, channels TSV, geometry,
  event, ball/Leap stream, target, derivative, fit, inference, prediction,
  freeze, or score followed. This is an integrity-gate result, not a null
  neural result. IACKD-1 is consumed and parked with no rerun; the private
  bundle remains isolated. Read the [primary-source research](docs/IACKD_CUE_ACTION_DISSOCIATION_PRIMARY_SOURCE_RESEARCH.md),
  [frozen preregistration](docs/IACKD_CUE_ACTION_DISSOCIATION_PREREGISTRATION.md),
  [implementation record](docs/IACKD_CUE_ACTION_DISSOCIATION_IMPLEMENTATION.md),
  and [aggregate closeout](docs/IACKD_CUE_ACTION_DISSOCIATION_RESULT.md).
- **Completed engineering gate, IACKD-H1 Header Inventory Audit:** the published
  article supports a 32-channel cap and separately names M1, M2, HEOG, and
  VEOG, but it never establishes an exact 36-channel BrainVision invariant.
  The authors' pinned public code also uses two different presence-based
  deletion lists: one includes M1/M2/HEOG/VEOG/TRIGGER, while the other uses
  HEO/VEO/HEOG/VEOG/TRIGGER. Those are testable explanations, not observed
  answers. The new prospective contract audits all **128 VHDR headers** and
  only **161,792 bytes** in canonical order, emits aggregate signature hashes
  and seven public-code alias flags, and forbids the retained 7.249 GB bundle,
  siblings, samples, events, trajectories, targets, models, and scores.
  Registration `0e52278` passed both jobs in CI `31412667060` before Tier B
  implementation. The dependency-free parser, mocked response validator,
  signature router, bounded writer, and module CLI were then frozen at
  `16621cc`, which passed both jobs in CI `31415213841`.
  One isolated fixture qualification processed all 128 registered sizes in
  0.037819 seconds at 36,634,624-byte peak RSS and emitted 4,465 bytes with
  zero network or real-content operations. Its constructed `IACKDH-R1` has no
  real-source meaning. Request `56531c6` passed both jobs in CI `31416489006`;
  decision `04f2706` then passed both jobs in CI `31424361969` before the sole
  audit. All eleven gates passed over 128 requests and 161,792 bytes in
  23.576352333 seconds at 94,650,368-byte peak RSS. Route `IACKDH-R5` measured
  two signatures: 96 declarations have 29 channels without M1/M2, and 32 have
  31 channels with M1/M2; all contain HEOG, VEOG, and TRIGGER at 1024 Hz. The
  retained local bundle, siblings, samples, events, targets, models, and scores
  stayed closed. The run is consumed with no retry or rerun.
  Read the [primary-source diagnosis](docs/IACKD_CHANNEL_INVENTORY_PRIMARY_SOURCE_RESEARCH.md),
  [frozen preregistration](docs/IACKD_CHANNEL_INVENTORY_PREREGISTRATION.md),
  [implementation record](docs/IACKD_CHANNEL_INVENTORY_IMPLEMENTATION.md),
  [authorization packet](docs/IACKD_CHANNEL_INVENTORY_AUTHORIZATION_PACKET.md),
  [decision record](docs/IACKD_CHANNEL_INVENTORY_AUTHORIZATION_DECISION.md), and
  [aggregate result](docs/IACKD_CHANNEL_INVENTORY_RESULT.md).
- **Design history, role-aware dual reversal:** a target-free code audit found
  that changing the failed `36` check alone would still misclassify TRIGGER as
  EEG and retain an invalid 32/34-EEG-row assumption. The next smallest gate is
  therefore IACKD-H2: **316 public BIDS metadata files totaling 457,602 bytes**
  covering channel roles, EEG sidecars, electrodes, and coordinate systems.
  It needs no local-bundle access and will freeze a `SensorRoleMap` before any
  future sample read. The prospective IACKD-2 science is also stronger than
  IACKD-1: congruent-to-incongruent and incongruent-to-congruent arms must both
  prefer actual hand direction over the exact-opposite cue surrogate, and the
  weaker arm determines the participant statistic. This is a design, not a
  neural result; H2 real metadata and every IACKD-2 operation remain separately
  gated. Read the [role-aware dual-reversal research](docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_RESEARCH.md).
- **Frozen next engineering gate, IACKD-H2 Channel Role and Geometry Audit:**
  the exact prospective contract covers 128 `channels.tsv` files, 128 EEG
  sidecars, 30 electrode tables, and 30 coordinate-system files: **316 public
  metadata objects and 457,602 bytes total**. It selects predictive EEG by
  source-declared BIDS type, keeps HEOG/VEOG and TRIGGER out of the predictive
  set, treats M1/M2 as optional run properties, preserves missing reference or
  geometry as unavailable, and publishes aggregate hashes and coverage only.
  This registration authorizes generated fixtures only after its commit is
  remotely green. It does not authorize the metadata fetch, retained bundle,
  signal, target, model, or score and is not a neural result. Read the
  [H2 preregistration](docs/IACKD_CHANNEL_ROLE_GEOMETRY_PREREGISTRATION.md).
- **H2 implementation, generated-fixture qualified:** registration `228ccd0`
  passed both jobs in CI `31427931578` before the dependency-free parser,
  private run/geometry joins, response firewall, aggregate router, writer,
  inspector, and module CLI were implemented. One final generated traversal
  covered all 316 registered object sizes and 457,602 bytes in 0.054680 seconds
  at 34,996,224-byte peak RSS, emitting 8,282 bytes. It produced two full
  schemas but one core schema after removing optional M1/M2, 26 constructed
  predictive EEG roles, and complete constructed C3/C4/Cz and O1/Oz/O2
  geometry in all 30 groups, routing `IACKDR-R4`. Those are fixture mechanics,
  not observations of the public data. Forty-seven focused, 1,751 base, and
  1,822 optional tests pass locally. The implementation must still be
  committed, pushed, and remotely green before an all-false real-content
  packet can be prepared. Read the
  [implementation record](docs/IACKD_CHANNEL_ROLE_GEOMETRY_IMPLEMENTATION.md).
- **H2 real-content request, all false:** implementation `9f6fef9` passed both
  jobs in CI `31430151368`, so the repository now contains one hash-bound
  request for a possible later 316-body, 457,602-byte public metadata audit.
  The packet permits no action by itself: every request, parse, consumed
  marker, output, local-bundle, signal, target, model, score, retry, rerun, and
  claim flag is false. Its own commit and both CI jobs must become green before
  it can be identified to the maintainer for one fresh short-form decision.
  Read the [authorization packet](docs/IACKD_CHANNEL_ROLE_GEOMETRY_AUTHORIZATION_PACKET.md).
- **H2 decision recorded, not yet effective:** after the exact green packet was
  identified, the maintainer replied `continue :)`. The separate
  [decision record](docs/IACKD_CHANNEL_ROLE_GEOMETRY_AUTHORIZATION_DECISION.md)
  preserves those words and binds request `86174bc`, CI `31431064259`, both
  green job IDs, and the unchanged 316-object scope. The decision must itself
  be committed, pushed, and remotely green before the single metadata audit;
  recording it made zero metadata requests or local-bundle operations.
- **H2 measured result, consumed at `IACKDR-R1`:** decision `f6eb5ab` passed
  both jobs in CI `31444154297` before one 316-request, 457,602-byte audit.
  Response, parsing, privacy, geometry, resource, and replay gates passed in
  `55.592999708s` at 86,769,664-byte peak RSS. The metadata consistently shows
  26 predictive EEG channels, three `MISC` controls, 1024 Hz, average reference,
  and complete central/occipital geometry across all 30 groups. The frozen
  contract rejected its own candidate because it did not accept `MISC` for
  HEOG/VEOG and separated the named trigger from the sidecar's three-MISC
  count. Read the [aggregate result](docs/IACKD_CHANNEL_ROLE_GEOMETRY_RESULT.md).
  H2 has no rerun and establishes no neural or decoding result.
- **Prospective H3 source-semantics repair:** a new artifact-only policy now
  separates dataset-pinned BIDS source type, functional control role, and model
  inclusion. It preserves the two exact source count groups, keeps one fixed
  26-channel predictive EEG core, treats M1/M2 as optional nonpredictive EEG,
  and gives HEOG/VEOG/Trigger nonpredictive roles without moving them out of
  their declared MISC count. Read the
  [policy research](docs/IACKD_SOURCE_DECLARED_CONTROL_POLICY_RESEARCH.md).
  The [dependency-free implementation](docs/IACKD_SOURCE_SEMANTICS_IMPLEMENTATION.md)
  now qualifies 29-row and 31-row generated fixtures, five separate derivative
  hashes, deterministic replay, target leakage refusal, and 13 adversarial
  mutations spanning 12 fail-closed classes. Exact implementation `8c5784a`
  passed both jobs in CI `31446902756` before one measured closeout: all 13
  gates passed over 6,093 generated input bytes in 0.00747 seconds at 20.25 MiB
  peak RSS, with every real-data, signal, target, model, network, and scoring
  counter at zero. Read the [H3 result](docs/IACKD_SOURCE_SEMANTICS_RESULT.md).
  This validates policy mechanics only; no real reader or IACKD-2 execution is
  authorized.
- **Frozen prospective IACKD-2 experiment:** the new
  [dual-reversal preregistration](docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_PREREGISTRATION.md)
  turns the repaired sensor semantics into a harder scientific test. Separate
  congruent-to-incongruent and incongruent-to-congruent models must both favor
  measured hand direction over the exact cue-derived opposite, and the weaker
  participant-level arm margin is primary. The contract freezes the 26-channel
  predictive core, central, occipital, EOG, pre-window, timing, displacement,
  permutation, derangement, and opposite-hand controls; exactly 660 fits and
  900 target-blind prediction sets; one remote-green aggregate freeze; and one
  combined final target delivery and score. To protect storage, a future
  separately authorized run must stream one of 128 ten-object run groups at a
  time, never retain a second 7.25 GB raw bundle, and stay below 1 GiB peak
  incremental disk. The largest registered run group is 82,064,564 bytes. The
  existing private bundle is forbidden. Registration `5bdab30` passed both
  jobs in CI `31448911258` before the
  [generated-only implementation](docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_IMPLEMENTATION.md).
  It now exercises strict model/scorer isolation, 29/31-row source semantics,
  causal features, exactly 660 fits and 900 target-blind prediction sets, a
  recomputed hash freeze, exact replay, and all six routes. Portability
  correction `af7488a` passed both jobs in CI `31451262840` before the one
  [registered generated closeout](docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_SYNTHETIC_RESULT.md).
  All 15 gates passed in 5.024801 seconds at 257,130,496-byte peak RSS with
  30,170 output bytes. Every real/public/private/network counter stayed zero,
  and the temporary report was removed. Constructed `IACKD2-R5` is planted
  interface evidence only, not a neural result. The generated closeout is
  consumed with no rerun. The
  [all-false real-execution packet](docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_AUTHORIZATION_PACKET.md)
  froze one possible 7.249 GB streaming public-EEG sequence, 660 fits, 900
  target-blind predictions, one remotely green freeze, and one score. Request
  `862141f` passed both jobs in CI `31454131606`; the maintainer's fresh
  `continue` was then bound without scope expansion, and decision `2ce87fa`
  passed both jobs in CI `31456317734`. The new
  [real-executor implementation](docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_REAL_IMPLEMENTATION.md)
  uses exact metadata/object integrity checks, one-run-at-a-time MNE parsing,
  explicit unavailable geometry handling, causal 0.5-4 Hz derivatives,
  physically separate model and scorer shards, deterministic private
  predictions, aggregate freeze validation, and a one-shot scorer. Its final
  generated qualification passed all 15 gates: 660 fits, 900 predictions,
  exact replay, 5.604450 seconds, 270,745,600-byte peak RSS, 4,523 output
  bytes, and zero public, real-data, old-bundle, provider, or hardware
  operations. The planted `IACKD2-R5` remains non-scientific. Exact
  implementation `dab5dd4` then passed both jobs in CI `31461818620` before
  the sole [registered stream](docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_STREAM_RESULT.md).
  That invocation wrote its no-retry consumed marker, opened only the first
  pinned metadata response, and parked at `IACKD2-F08` when its HTTP
  `Content-Length` was absent or differed from the registered 1,178 bytes.
  No response body, EEG object, signal, trajectory, target, derivative, model,
  freeze, delivery, or score was reached. IACKD-2 is consumed with no rerun;
  the old retained bundle remains forbidden. The engineering lesson is to
  make immutable bounded body bytes and SHA-256 authoritative for metadata in
  any separately preregistered recovery, rather than treating a transport
  header as content evidence.
  That lesson is now frozen prospectively in
  [IACKD-T1 research](docs/IACKD_TRANSPORT_STABLE_RECOVERY_RESEARCH.md) and its
  [strict contract](docs/IACKD_TRANSPORT_STABLE_RECOVERY_PREREGISTRATION.md).
  The four small metadata bodies may use fixed-length, chunked, or clean
  close-delimited framing, but exact observed bytes and registered SHA-256 are
  still mandatory; all large-object and scientific gates remain unchanged.
  Registration `ee0f62a` passed both jobs in CI `31472269070` before the
  [zero-network implementation](docs/IACKD_TRANSPORT_STABLE_RECOVERY_IMPLEMENTATION.md).
  Its final generated run passed 10 acceptance validations, deterministic
  replay, and all 22 refusals in 0.00105 seconds at 20.3 MB peak RSS with a
  5,540-byte report. The module has no URL opener, local-path executor, or
  `--execute` mode. Two intermediate candidates exposed and preserved an
  optional-suite RSS test-boundary issue; exact implementation `93a067c` then
  passed Base Python job `93724709807` and Optional Neuro Readers job
  `93724709840` in CI `31474412246`. The new
  [all-false IACKD-2R request](docs/IACKD_TRANSPORT_STABLE_RECOVERY_AUTHORIZATION_PACKET.md)
  binds one possible future additive executor, one fresh storage-safe stream,
  the unchanged 660-fit/900-prediction target firewall, one green freeze, and
  one score. It also refuses before consumption when free disk, one-thread
  settings, or per-CPU machine load are unsafe. The packet authorizes nothing;
  it must be committed, pushed, and remotely green before a fresh later
  packet-bound maintainer decision can open any public operation. Request
  `525e97e` passed both jobs in CI `31475356506`; after Codex identified it as
  the sole packet, the maintainer's fresh `continue` was recorded verbatim in
  the additive
  [decision](docs/IACKD_TRANSPORT_STABLE_RECOVERY_AUTHORIZATION_DECISION.md).
  Decision `feef8f7` passed Base Python job `93730242015` and Optional Neuro
  Readers job `93730242090` in CI `31476158747` before the new
  [additive executor](docs/IACKD_TRANSPORT_STABLE_DUAL_REVERSAL_REAL_IMPLEMENTATION.md)
  was implemented. The module neither imports nor calls the consumed executor,
  has a new isolated root, integrates the green metadata validator, and keeps
  exact fixed-length/ETag/byte/SHA-256 payload checks. Its machine gate refuses
  before consumption below 10 GiB free, above normalized one-minute load
  `1.0`, or when load is unavailable. One measured generated qualification
  passed 18/18 gates in 4.939357 seconds at 261,488,640-byte peak RSS with
  5,825 output bytes, all three metadata framing profiles, deterministic
  660-fit/900-prediction replay, 13 refusal mutations, and zero real, public,
  network, target, or claim operations. The planted `IACKD2-R5` is still only
  synthetic mechanics. Exact implementation `b32dc25` passed both jobs in CI
  `31478167292` before the sole
  [IACKD-2R stream](docs/IACKD_TRANSPORT_STABLE_DUAL_REVERSAL_STREAM_RESULT.md).
  The machine gate passed and the new marker consumed the attempt. The first
  metadata body passed status, URL, framing, encoding, and exact 1,178-byte
  count, then its SHA-256 differed from the pinned digest before parsing. No
  selected payload, EEG, event, trajectory, target, derivative, model, freeze,
  delivery, or score was reached. IACKD-2R is parked at `IACKD2R-F05` with no
  retry or rerun. This is a useful fail-closed content-drift result, not neural
  or decoding evidence.
  The next architecture is now specified in
  [IACKD-M1 snapshot identity research](docs/IACKD_SNAPSHOT_IDENTITY_RECOVERY_RESEARCH.md).
  Official OpenNeuro API and pinned platform-source evidence show that a named
  snapshot exposes a `hexsha` and a recursive content-addressed file tree with
  full paths, Git object IDs, sizes, annexed status, and public S3 `versionId`
  URLs. A future validator will bind that immutable snapshot layer separately
  from the 1,340 selected acquisition objects and the critical
  Name/BIDSVersion/License/DatasetDOI projection. Raw GraphQL bytes, HTTP
  framing, ETag, and last-modified values are provenance only; they cannot
  rescue snapshot, tree, selected-inventory, or critical-metadata drift. This
  research made zero dataset-specific requests. The next bounded step is a
  generated-only standard-library canonicalizer; any one-response 2 MiB public
  audit remains a fresh Tier C gate and must pass before another 7.25 GB EEG
  acquisition is considered.
  The follow-on
  [IACKD-M1 preregistration](docs/IACKD_SNAPSHOT_IDENTITY_PREREGISTRATION.md)
  now freezes one exact 316-byte query and 355-byte request, strict
  duplicate-free response schemas, 1,679 versioned file rows, all twelve
  historical role summaries, a private-manifest/public-hash boundary, 37
  adversarial refusals, and one-thread resource caps. Research `723c8e2`
  passed both jobs in CI `31480538821`; registration `1667e30` then passed
  both jobs in CI `31481270697`. The generated-only
  [IACKD-M1 implementation](docs/IACKD_SNAPSHOT_IDENTITY_IMPLEMENTATION.md)
  is now complete locally. Its standard-library module has no network client,
  real endpoint, execute mode, or local IACKD path. One final constructed
  roundtrip reconciled all 1,679 tree rows and the exact 1,340 historical
  selected paths, passed 37 refusal mutations and two deterministic replays,
  and emitted 426,792 bytes in 0.888773 seconds at 38,436,864-byte peak RSS.
  Forty-nine focused, 2,084 base, and 2,155 optional tests pass. This proves a
  bounded identity interface, not current public-snapshot compatibility or a
  neural result. Public GraphQL access remains closed until the exact
  implementation is remotely green and a new all-false Tier C request receives
  a fresh packet-bound decision.
  Exact implementation `7b8f47b` is now green in CI `31483435801`. The
  follow-on
  [IACKD-M1A all-false packet](docs/IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_PACKET.md)
  binds one possible standard-library transport wrapper, one exact 355-byte
  GraphQL POST, one 2 MiB-capped response, a 2 GiB free-disk gate, and zero
  payload requests. It authorizes nothing yet. The packet itself must become
  remotely green and be identified as the sole Tier C request before a fresh
  maintainer decision can unlock generated/mock wrapper work; public access
  remains behind another green wrapper milestone.
  The maintainer then said `keep going, move the needle, continue, you
  approved to go on`. The separate
  [packet-bound decision](docs/IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_DECISION.md)
  preserves that exact message and binds only request `ce84738` and its hash.
  Decision `4165c24` passed both jobs in CI `31485359989` before the
  [public-wrapper implementation](docs/IACKD_SNAPSHOT_IDENTITY_PUBLIC_IMPLEMENTATION.md)
  began. The dependency-free wrapper now freezes one 355-byte POST, a
  no-redirect one-read response path, three framing profiles, pre-consumption
  disk/load/thread checks, a private marker and row manifest, and an
  aggregate-only result. One generated/mock qualification passed 20 wrapper
  refusals and two semantic replays in 0.098865 seconds at 46,563,328-byte
  peak RSS, emitting 429,430 bytes with zero public requests or neural,
  target, model, and score operations. The single public response remains
  closed until this exact wrapper commit passes both CI jobs; EEG payload
  access remains out of scope. Exact wrapper `406bff8` then passed both jobs
  in CI `31487183289` before the
  [one public snapshot audit](docs/IACKD_SNAPSHOT_IDENTITY_PUBLIC_RESULT.md).
  The machine gate passed and one 355-byte POST returned 595,082 bytes, but
  strict canonicalization refused the response's top-level field set at
  `IACKDMP-F05`. The lane is consumed with no retry: no selected manifest,
  payload request, neural read, target, model, or score followed. This is a
  precise metadata-envelope failure, not public-snapshot compatibility or a
  scientific result.
- **MARC-1 is the next scientific effect lane:** WO9R is a real positive
  task-information result, but its stronger early-cue score and failed central
  localization leave cue, ocular, and peripheral explanations alive. MARC-1
  therefore freezes one common compact causal `0.5-4 Hz` shrinkage-LDA family
  across two complementary licensed sources. Freewill-23 supplies 23 people,
  self-selected target and onset timing, four EOG channels, and synchronized
  wrist acceleration. Wrist-45 supplies 45 people, eight forearm EMG channels,
  and synchronized encoder kinematics in participant-level archives as small
  as 33,690,749 bytes. The top route requires both axes to beat no-signal,
  timing, and every available non-EEG comparator; the weaker axis margin is
  primary.

  This is also storage-aware. The 13,591,548,048-byte Freewill archive may
  never be downloaded whole; a later separately authorized metadata gate must
  prove exact byte-range member selection first, and all future selected
  payloads remain capped below 8 GiB. The generated qualification contract now
  freezes a 14-member ZIP64 fixture, no member-content reads, two modality-role
  profiles, a past-only interface window, twelve comparators, and 24 refusal
  mutations before any live range request. Contract `4494d57` passed both CI
  jobs before the dependency-free implementation was written. Exact
  implementation `e35a587` passed both jobs in CI `31505555044` before one
  generated closeout. It passed all gates in 0.006589 seconds at 23,511,040
  bytes peak RSS, with 14 bounded range reads, zero payload-overlap bytes, two
  deterministic modality plans, and 24/24 refusals. This is engineering proof
  only: all real-data, target, model, score, and claim counters were zero. The
  [full generated result](docs/MARC_1_GENERATED_QUALIFICATION_RESULT.md) is
  consumed with no rerun. A scientifically attractive ten-person
  self-paced EEG/EOG/EMG source remains parked because its dataset license is
  unavailable. MARC-1 has opened no payload, signal, event, target, model, or
  score, so it is a better experiment design, not a new neural result. Read the
  [full source comparison and claim router](docs/MARC_1_MULTIMODAL_ARTIFACT_RESOLVED_MOVEMENT_RESEARCH.md).

  The next storage gate is now designed as `MARC1-CD1`. A future audit may read
  only one 128-KiB version-metadata body, one exact 128-KiB archive tail, and
  one central-directory range capped at 16 MiB, for 17,039,360 response-body
  bytes maximum. ZIP64 must reconcile fully inside the tail; otherwise the
  lane parks with no exploratory request or whole-file fallback. Exact member
  names remain private, and whole-archive MD5, member CRC verification, local
  headers, payload content, and neural evidence remain unavailable. The
  [central-directory research record](docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_RESEARCH.md)
  authorizes no live response. Its green successor now freezes an 18-entry
  virtual archive, direct and two-bodyless-redirect mock paths, complete
  in-tail ZIP64 parsing, strict private/public separation, deterministic
  replay, and 32 adversarial refusals. Read the
  [generated/mock contract](docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_PREREGISTRATION.md).
  Contract `cf63043` passed Base Python job `93837415016` and Optional Neuro
  Readers job `93837415174` in CI `31508903399` before implementation. The
  dependency-free generated module now validates direct and bodyless-redirect
  range paths, structurally parses the decoy-bearing EOCD and complete in-tail
  ZIP64 records, inventories all 18 entries, keeps names and offsets private,
  replays deterministically, and refuses all 32 frozen mutations. Its latest
  development qualification represented the 13.59 GB archive with 280,249
  generated bytes and emitted 11,573 temporary bytes in 0.007407 seconds at
  26,181,632-byte peak RSS; the files were removed. This is not the registered
  closeout. Read the
  [implementation record](docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_IMPLEMENTATION.md).
  Exact implementation `211fd78` passed Base Python job `93846584402` and
  Optional Neuro Readers job `93846584527` in CI `31511626051` before one
  registered generated closeout. That run passed `MARC1CDG-R1` with 280,249
  generated input bytes, 11,574 temporary output bytes, all 18 entries, all 32
  refusals, and all 14 gates in 0.006544 seconds at 27,131,904-byte peak RSS.
  Every public, real-data, target, model, score, and claim counter remained
  zero; the exact temporary outputs were hash-bound and removed. Read the
  [generated result](docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_RESULT.md). The
  closeout is consumed with no rerun. The next eligible artifact is an
  all-false Tier C request for one live metadata/range audit; no public request
  is authorized yet. That request is now specified in the
  [live-audit authorization packet](docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_AUTHORIZATION_PACKET.md).
  It binds one future standard-library wrapper, one metadata body, one exact
  128-KiB tail, and one conditional directory body under a 17,039,360-byte
  accepted-response cap. Request `950796d` passed both required jobs in CI
  `31513578445`, then the maintainer's fresh continuation was recorded
  verbatim in the
  [packet-bound decision](docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_AUTHORIZATION_DECISION.md).
  Decision `624cc4e` passed both jobs in CI `31519016891`, and the
  [live-wrapper implementation](docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_LIVE_IMPLEMENTATION.md)
  is generated-qualified. It reuses the green ZIP64 parser, disables automatic
  redirects, caps all bodies, validates globally routable redirect addresses,
  writes exact member rows only to a private mode-`0600` manifest, and has no
  whole-download or extraction interface. Generated `MARC1CDL-G1` passed
  14/14 gates with 40 refusal checks and zero network or forbidden counters.
  Exact wrapper `5dfa3c4` then passed both jobs in CI `31521510374` before the
  [one live inventory](docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_LIVE_RESULT.md).
  `MARC1CD-R1` mapped 1,227 entries in the current 13,591,548,048-byte public
  ZIP from one 304-byte metadata body, one 131,072-byte tail, and one
  175,382-byte central-directory body. It downloaded zero archive or member
  payload bytes, passed all 14 gates in 2.727 seconds at 43,974,656-byte peak
  RSS, and is consumed with no retry or rerun. The exact inventory remains in
  a private Git-ignored mode-`0600` manifest; only aggregate counts and hashes
  are public. Member selection or access, participant data, neural signals,
  targets, models, scores, and scientific-claim operations remain closed.
  Task 4 is now frozen in the
  [MARC1-P1 pilot-selection preregistration](docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_PREREGISTRATION.md).
  It selects 12 participants per axis using DOI-bound SHA-256 ranks before any
  private row is inspected. Freewill uses three session-1 runs for fitting and
  three session-2 runs for held-out cross-day evaluation; Wrist uses runs 1-6
  for fitting and runs 7-8 for an 80-trial balanced holdout. The selection is
  forbidden from using size, CRC, event count, target, signal quality, or an
  outcome, and the future joint acquisition ceiling is 8 GiB. This is the path
  toward a defensible EEG effect; movement data cannot establish thought-to-
  text, which remains a later language-specific evidence lane.
  Contract `d121806` passed both jobs in CI `31569417204` before the
  [generated selector implementation](docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_IMPLEMENTATION.md)
  began. The dependency-free module now exercises the full 1,227-row plus
  55-row metadata scale, both frozen cohorts, exact splits, private mode-`0600`
  output, row-order replay, cap refusal, and all 36 adversarial mutations. A
  disposable development run passed constructed `MARC1PSG-R1`; its outputs
  were removed. Exact implementation `0c0a698` then passed Base Python job
  `94034790262` and Optional Neuro Readers job `94034790315` in CI
  `31571668853` before the
  [one registered generated closeout](docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_RESULT.md).
  That run passed all 15 gates and 36 refusals over 873,348 generated input
  bytes in 0.227 seconds at 32,374,784-byte reported peak RSS. Its 6,946-byte
  aggregate report and mode-`0600` 175,618-byte private manifest were
  hash-bound, inspected once, and removed. All real, network, signal, target,
  model, score, and claim counters stayed zero. The generated lane is consumed;
  real metadata selection remains a later Tier C gate. The
  [MARC1-P1A authorization packet](docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_AUTHORIZATION_PACKET.md)
  freezes one staged wrapper and one selection over exactly one 418,755-byte
  sealed Freewill-manifest read plus one Wrist metadata body capped at 2 MiB.
  Request `7f1ba09` passed both jobs in CI `31573969646`, and the maintainer's
  fresh words `approved, continue, achieve a scientific claim, achieve thought
  to text 😎` are preserved verbatim in the
  [MARC1-P1A decision](docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_AUTHORIZATION_DECISION.md).
  Decision `9726d07` passed Base Python job `94044627592` and Optional Neuro
  Readers job `94044627647` in CI `31574870204` before wrapper work began.
  Read the
  [live-selector implementation](docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_LIVE_IMPLEMENTATION.md)
  and its
  [machine record](registries/marc1_privacy_preserving_pilot_selection_live_implementation.v0.json).
  The additive standard-library wrapper freezes `sub-01.zip` through
  `sub-45.zip`, the known public `sub-01` identity anchor, strict seven-field
  Figshare rows, a target-field firewall, one no-follow private-manifest read,
  manual global-only redirects, a pre-input machine gate, consumed failure,
  and private/public output separation. Generated `MARC1PSL-G1` selected the
  exact 12+12 cohorts and 300 private rows, passed 26/26 refusals and 15/15
  gates over 866,578 input bytes, and emitted 214,553 temporary bytes in 0.183
  seconds at 50,905,088-byte reported peak RSS. All real, network, payload,
  neural, target, model, score, and claim counters stayed zero, and the
  temporary outputs were removed. Exact wrapper `702e613` then passed Base
  Python job `94056321843` and Optional Neuro Readers job `94056321914` in CI
  `31578614616` before the
  [one live metadata attempt](docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_LIVE_RESULT.md).
  The executor read and verified the 418,755-byte private inventory exactly
  once, opened one Wrist response, and failed closed at `MARC1PS-F03` because
  the response did not meet the frozen explicit identity-encoding rule. It
  accepted zero public-body bytes, selected zero participants, and opened zero
  archive payload, signal, target, model, or score data. The attempt is
  consumed with no retry or rerun. A separately named transport-semantics
  recovery must be frozen and reauthorized before another real metadata
  request. MARC-1 remains a confound-resolution rung on the same thought-to-
  text path, not a pivot, and movement evidence is not language evidence.
  The follow-on
  [MARC1-HT1 research](docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RECOVERY_RESEARCH.md)
  binds RFC 9110 Sections 8.4 and 12.5.3. Its candidate rule accepts an absent
  `Content-Encoding` as the standards-preferred uncoded representation and a
  lone case-insensitive `identity` token only as a narrow compatibility form;
  every real coding, list, duplicate, empty field, transfer coding, overflow,
  redirect violation, retry, and fallback still refuses. The actual live
  header was not retained and must not be inferred. MARC1-HT1 is artifact-only
  research: it authorizes no implementation, private read, public request, or
  payload operation.
  The follow-on
  [generated recovery contract](docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RECOVERY_PREREGISTRATION.md)
  freezes four accepted response forms, 20 refusals, 16 acceptance gates, five
  refusal routes, exact replay of the 12+12 generated cohorts, zero network or
  private bytes, and no `execute` command. Only after this exact contract is
  committed, pushed, and green may the additive generated/mock harness be
  implemented. A live request remains Tier C and payload acquisition remains
  ineligible.
  The [generated recovery implementation](docs/MARC_1_HTTP_IDENTITY_SEMANTICS_IMPLEMENTATION.md)
  now accepts exactly the four frozen uncoded forms, refuses all 20 mutations,
  replays the exact 12+12 target-free cohorts, and passes all 16 gates over
  923,052 generated input bytes. Its 182,682-byte output was inspected and
  removed; no live metadata, network body, payload, EEG, target, model, or score
  was accessed. The exact implementation must be committed, pushed, and green
  before its one registered generated closeout. This is a transport repair on
  the same positive-control-to-language path, not a scientific pivot.
  Exact implementation `b2cb48c` then passed Base Python job `94073234688`
  and Optional Neuro Readers job `94073234607` in CI `31583931303` before the
  [one registered generated closeout](docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RESULT.md).
  `MARC1HT-G1` passed all gates in 0.112 seconds at 33.1 MB external peak RSS.
  Its aggregate was inspected once, both temporary outputs were hashed and
  removed, and the closeout is consumed with no rerun. This remains generated
  engineering evidence only; another live metadata attempt is not yet open.
  The next gate is now specified in the all-false
  [MARC1-HT1A authorization packet](docs/MARC_1_HTTP_IDENTITY_LIVE_RECOVERY_AUTHORIZATION_PACKET.md).
  It proposes a new additive wrapper and, only after separate green decision
  and implementation milestones, one metadata-only attempt using the sealed
  418,755-byte upstream inventory and one Wrist response capped at 2 MiB. It
  forbids the consumed `MARC1-P1A` root, all payload bytes, signals, targets,
  models, and scores. The packet authorizes nothing and is explicitly a
  control checkpoint on the same path toward held-out language decoding.
  Request `27f39ae` passed Base Python job `94080678529` and Optional Neuro
  Readers job `94080678738` in CI `31586256906`. The fresh maintainer approval
  is now quoted in the separate
  [MARC1-HT1A decision](docs/MARC_1_HTTP_IDENTITY_LIVE_RECOVERY_AUTHORIZATION_DECISION.md).
  That decision is ineffective until its own commit is pushed and both CI jobs
  are green; no implementation or real-input operation has begun.
  Decision `9c7bd48` and exact wrapper `68ade0d` subsequently passed both
  required CI jobs before the single metadata-only invocation. The corrected
  transport accepted and parsed one 2,917-byte uncoded response, then the
  selector consumed at `MARC1HTL-F04` because its row count differed from the
  frozen 55-row identity. The actual count and rows were not retained. Zero
  participants were selected and zero payload, signal, target, model,
  prediction, or score operations followed. Read the
  [consumed result](docs/MARC_1_HTTP_IDENTITY_LIVE_RESULT.md).
  Result `1337a91` then passed Base Python job `94091696454` and Optional
  Neuro Readers job `94091696340` in CI `31589739739` before the
  [MARC1-PG1 pagination research](docs/MARC_1_VERSIONED_PAGINATION_RECOVERY_RESEARCH.md)
  was recorded. Pinned official Figshare OpenAPI source says the version-files
  operation defaults `page_size` to 10 and permits up to 1,000. Omitted
  pagination is therefore the leading engineering hypothesis, not a proven
  description of the consumed response. The prospective request binds exactly
  `page=1&page_size=1000`, still requires all 55 frozen rows, and forbids a
  second page, fallback, partial cohort, or live request before generated-only
  contract, implementation, and closeout milestones are independently green.
  This is the same confound-control to neural-positive-control to held-out-
  language path, not a pivot; it establishes no new scientific result.
  Research `7a7883a` passed Base Python job `94095736694` and Optional Neuro
  Readers job `94095736770` in CI `31591022429` before the
  [MARC1-PG1 generated contract](docs/MARC_1_VERSIONED_PAGINATION_RECOVERY_PREREGISTRATION.md)
  was frozen. The contract permits only a future `plan`/`qualify`/`inspect`
  harness after its own commit is green. It binds four equivalent generated
  replay cases, 41 refusals, 18 gates, exact request serialization, unchanged
  selection and split identities, private/public output separation, one-thread
  resource caps, zero network/private bytes, and no `execute` command. A live
  request and payload acquisition remain closed.
  Contract `ccb3ba8` passed Base Python job `94098410925` and Optional Neuro
  Readers job `94098410868` in CI `31591853349` before the
  [generated pagination implementation](docs/MARC_1_VERSIONED_PAGINATION_IMPLEMENTATION.md)
  was built. Development `MARC1PG-G1` passed 4/4 accepted cases, all 41
  refusals across eight routes, and all 18 gates. It replayed the unchanged
  55-row identity and 12+12 target-free selection from 1,019,776 generated
  input bytes in 0.089257 seconds at 40,091,648-byte reported peak RSS. Its
  183,355 temporary output bytes were inspected, hash-bound, and removed.
  Exact implementation `2c98a2a` passed Base Python job `94104455930` and
  Optional Neuro Readers job `94104455857` in CI `31593790492` before the one
  [registered closeout](docs/MARC_1_VERSIONED_PAGINATION_GENERATED_RESULT.md).
  That invocation consumed at `MARC1PG-F07` because `/tmp` was a symlink
  output parent. Contract loading, both generated inventories, four accepted
  cases, and target-free selection had already run in memory, so this is not
  an unspent preflight and no corrected invocation is allowed. It created zero
  files and used zero real/private or network bytes.
  A separately named generated recovery must move output preflight before all
  fixture operations and become green before another registered generated run.
  No live request, payload, signal, target, model, score, or claim operation is
  open. This remains the same path to cue-resistant neural evidence and held-
  out language decoding; it is not a pivot.
  Result `a4dcaea` passed Base Python job `94107907276` and Optional Neuro
  Readers job `94107907246` in CI `31594881048` before the artifact-only
  [MARC1-OP1 research](docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_RESEARCH.md).
  The candidate architecture obtains and holds a no-follow parent-directory
  capability, binds device/inode identity, and requires parent-relative
  exclusive writes. That capability must exist before any repository read,
  contract load, deferred pagination import, fixture, or selection. The local
  runtime supports the needed `dir_fd` primitives, but a future implementation
  must feature-detect and refuse rather than downgrade on another platform.
  This research made zero fixture, network, private, payload, signal, target,
  model, or score operations. Its next gate is research commit, push, and both
  CI jobs green before a generated-only contract may be frozen.
  Research `d02830b` passed Base Python job `94111539407` and Optional Neuro
  Readers job `94111539431` in CI `31595996923` before the
  [MARC1-OP1 contract](docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_PREREGISTRATION.md)
  was frozen. It binds six accepted cases, 32 refusals, ten routes, 20 gates,
  one exact path-only probe, and one conditional qualifier. The future wrapper
  cannot import the consumed pagination module eagerly, call its qualifier, or
  modify it. Every current access and authorization flag remains zero/false.
  Contract `baade51` passed Base Python job `94115807028` and Optional Neuro
  Readers job `94115807008` in CI `31597291352` before the
  [MARC1-OP1 implementation](docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_IMPLEMENTATION.md).
  Its capability acquisition is the first call in `preflight` and `qualify`;
  it holds parent device/inode identity through two exclusive relative writes,
  one public-only inspection, and exact cleanup. Development `MARC1OP-G1`
  passed six accepted cases, 32 refusals, and 20 gates using 184,173 temporary
  bytes and zero live/private, neural, target, model, or score operations. The
  exact registered path remains untouched until this implementation is pushed
  and both CI jobs are green. This remains the same scientific path.
  Exact implementation `fcedcc3` then passed Base Python job `94125013790`
  and Optional Neuro Readers job `94125013956` in CI `31600085119` before the
  [registered generated result](docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_RESULT.md).
  The one path-only preflight reached `MARC1OP-P0` with every experiment-work
  counter zero; the one conditional qualifier reached `MARC1OP-G1` in 0.098
  seconds at 33,882,112-byte reported RSS and removed all 184,173 temporary
  bytes. Both invocations are consumed. Current live inventory compatibility
  and every neural, language, and thought-to-text claim remain unestablished.
- **MARC1-LM1 paginated live-metadata gate:** exact result `ca4679a` passed Base
  Python job `94129199903` and Optional Neuro Readers job `94129199993` in CI
  `31601329375` before the
  [all-false packet](docs/MARC_1_PAGINATED_LIVE_METADATA_AUTHORIZATION_PACKET.md).
  The proposed sequence adds one generated/mock standard-library wrapper and,
  only after its own green proof, one exact no-retry Figshare request for
  `page=1&page_size=1000`. The response is capped at 2 MiB and may create only
  a consumed marker, a small Git-ignored 55-row private manifest, and one
  aggregate report. No payload, signal, target, model, prediction, score, or
  scientific claim is authorized. This is the next cohort-integrity step on
  the same route to cue-resistant neural evidence and held-out language
  decoding.
  The maintainer then supplied the exact 76-byte instruction `approved,
  continue, achieve a scientific claim, achieve thought to text 😎` after the
  packet was identified. The
  [separate decision](docs/MARC_1_PAGINATED_LIVE_METADATA_AUTHORIZATION_DECISION.md)
  quotes those words and binds only request `4d3eb19`, CI `31603530015`, and
  the unchanged one-response, zero-payload scope. Decision `060a365` passed
  Base Python job `94140250333` and Optional Neuro Readers job `94140250412`
  in CI `31604608307` before the
  [generated/mock implementation](docs/MARC_1_PAGINATED_LIVE_METADATA_IMPLEMENTATION.md).
  Development `MARC1LM-G1` accepted all four transport forms, refused all 36
  adversarial mutations, and passed all 20 gates while replaying the exact
  55-row inventory and frozen 12-subject split. It read 184,466 generated
  response bytes, created and removed exactly 19,030 temporary output bytes,
  ran in 0.0303 seconds at 43,057,152-byte reported RSS, and made zero real
  network, payload, signal, target, model, score, retry, or claim operations.
  The exact implementation must now be committed, pushed, and pass both CI
  jobs before the registered path or Figshare may be touched once. The
  research objective is unchanged and no result is predeclared.
  First push `8f67af2` failed both CI jobs only because generated tests used a
  macOS-only temporary parent; the correction uses the platform's canonical
  real temporary parent and leaves the registered execution path unchanged.
- **MARC1-LM1 consumed live metadata result:** corrected implementation
  `f9a1ece` passed Base Python job `94164152160` and Optional Neuro Readers job
  `94164152302` in CI `31611639130` before the sole request. One 15,652-byte
  metadata body passed transport and strict JSON parsing, then the frozen
  inventory validator refused at `MARC1LM-F04`. The actual failed predicate is
  unavailable; no cohort was selected and participant archive, payload,
  signal, target, model, prediction, and score counters remained zero. The
  consumed lane has no retry. The next gate is a separately named prospective
  current-inventory identity design on the same research path.
- **MARC1-SA1 source-aware inventory design:** current official Figshare
  surfaces do not give one stable cross-surface guarantee for MD5 fields. The
  new architecture treats five public fields as source core, two MD5 fields as
  validated optional provenance, and acquired-byte SHA-256 as a later payload
  integrity gate. A 21-field aggregate predicate vector can distinguish schema,
  count, participant, byte-total, anchor, URL, and checksum classes without
  publishing rows. This is Tier A design only: zero dataset requests and zero
  neural or model work.
- **MARC1-SA1 generated-only preregistration:** after research `aa80503`
  passed both jobs in CI `31614330447`, the next harness was frozen around six
  generated semantic families, 21 aggregate predicates, seven separated hash
  domains, 52 adversarial refusals, and 25 acceptance gates. Its command
  surface is only `plan`, `qualify`, and `inspect`; it has no network client,
  live path, payload reader, signal, target, model, prediction, or score. The
  exact contract must now pass both CI jobs before implementation begins.
- **MARC1-SA1 generated implementation:** contract `8f64ccb` passed both jobs
  in CI `31616551270` before the standard-library attestor was built. Final
  development route `MARC1SA-G1` passed six semantic families, 52 refusals,
  and 25 gates using 732,811 generated input and 109,589 temporary output
  bytes in 0.0524 seconds at 27,426,816-byte peak RSS. Output capability was
  acquired first, public/private schemas stayed separate, and both files were
  removed. The exact implementation must now pass both CI jobs before one
  registered generated closeout; no live metadata, payload, target, model, or
  scientific evidence was accessed.
- **MARC1-SA1 registered generated closeout:** exact implementation `feb3b83`
  passed Base Python job `94188922905` and Optional Neuro Readers job
  `94188922771` in CI `31619037335` before one fixture-only execution.
  `MARC1SA-G1` passed all six routes, 52 refusals, and 25 gates using 732,811
  generated input and 109,589 temporary output bytes in 0.053358083 seconds at
  27,885,568-byte reported peak RSS. Both files and the invocation directory
  were removed. The closeout is consumed; a live metadata response remains a
  new Tier C sequence, and no EEG or language evidence changed.
- **MARC1-SA1A all-false live-metadata request:** green result `094b6cb` / CI
  `31620515340` now anchors one possible future source-aware wrapper and one
  exact 2-MiB-capped metadata GET. R1/R2 may retain the frozen target-free
  cohort; R3/R4 must block selection and publish only aggregate diagnosis.
  Every current implementation, network, output, payload, neural, target,
  model, score, and claim permission is false. The packet must become remotely
  green and receive a fresh packet-bound maintainer decision before wrapper
  implementation or source access.
- **MARC1-SA1A packet-bound decision:** request `b077550` passed Base Python
  job `94198174069` and Optional Neuro Readers job `94198173901` in CI
  `31621794066` before the maintainer's exact 31-byte instruction was
  recorded. The decision binds only one generated/mock wrapper followed,
  after separate green proof, by one 2-MiB-capped metadata response and zero
  payload bytes. It must itself become remotely green before implementation.
  Later acquisition, neural analysis, target delivery, scoring, replication,
  and language decoding remain separately gated; no scientific result changed.
- **MARC1-SA1A source-aware wrapper:** decision `ef9ab91` passed Base Python
  job `94353799568` and Optional Neuro Readers job `94353799602` in CI
  `31670457497` before implementation. The additive standard-library wrapper
  accepts exactly one fixed, unauthenticated Figshare files response capped at
  2 MiB, supports exact-length, chunked, or clean-close framing, rejects target
  fields and schema ambiguity, and stops before every participant archive.
  Generated route `MARC1SAL-G1` passed six semantic families, 31 adversarial
  cases, and 20 gates using 84,422 generated response bytes and 24,064
  transient output bytes in 0.00929 seconds at 37,552,128-byte reported peak
  RSS. All temporary files were removed; real requests, payload bytes, neural
  reads, targets, fits, predictions, scores, and claim upgrades were zero.
  Thirty focused, 765 MARC, and 2,904 dependency-light tests pass. One old
  optional rehearsal inherited a process-wide RSS high-water in the full local
  optional run but passes alone; fresh remote Base and Optional jobs remain the
  exact eligibility gate. Exact wrapper `74aff21` then passed both jobs in CI
  `31672761644` before the one registered request.
- **MARC1-SA1A consumed source-aware result:** the one request completed in
  0.6967 seconds at 33,439,744-byte peak RSS and routed `MARC1SAL-R2`.
  That is the preregistered blocked-selection branch: zero subjects became
  eligible, no participant archive opened, and payload, signal, target, model,
  prediction, score, retry, and rerun counts remained zero. The three retained
  private/aggregate files total 23,112 bytes. Because the executor had already
  performed the allowed aggregate inspection and its CLI did not emit the
  private R3-versus-R4 source route, historical differences and body size are
  recorded as unavailable rather than inferred. This Wrist lane is consumed;
  acquisition and the remaining experiments do not proceed against it.
- **MARC-2 conditional-information route:** the replacement architecture keeps
  Freewill-23 as the cue-reduced primary axis, ranks Biomed-SPC-9 and a bounded
  PhysioNet Gait-59 subset for one later peripheral-control cohort, and reserves
  OpenNeuro `ds003626-v2.1.0` for a Spanish inner-speech control experiment.
  Its primary endpoint is participant-macro held-out log-loss gain from adding
  EEG after the strongest available timing/EOG/EMG/kinematic model. Three
  compact causal families are registered as separate hypotheses rather than a
  final-target model search. Any hosted LLM remains downstream of a remotely
  green neural freeze and must beat both LLM-only and item-deranged-neural
  conditions. This milestone read public primary-source pages only; all
  dataset, private-path, payload, signal, target, model, score, provider, and
  claim counters remain zero.
- **MARC2-FW1 storage-aware participant power:** the first work order now
  freezes the old DOI-derived Freewill rank instead of inventing a new seed,
  keeps the original 12-person cohort as a hard floor, and selects the largest
  contiguous prefix up to 19 people whose exact six-run member reservations
  fit within 8 GiB. It cannot skip a large participant to admit a later one,
  change run choice by size, inspect event content, or use signal quality or
  outcomes. The generated main fixture must select 16 people, 96 run bundles,
  and 384 members, plus pass floor, all-19, exact-cap, cap-plus-one, privacy,
  replay, and 40-refusal gates. This is a frozen fixture contract, not a real
  private-inventory read or a scientific result.
- **MARC2-FW1 generated implementation:** the new dependency-free module
  validates 1,227 generated ZIP-directory rows, replays the frozen rank, forms
  exact session-held-out bundles, and writes separate private and aggregate
  outputs. One local qualification passed 4/4 storage boundaries and 40/40
  refusal probes in 0.214 seconds at 30.9 MB reported peak RSS, with 846,690
  generated input bytes and 221,068 output bytes. It exposes only `plan`,
  generated `qualify`, and aggregate `inspect`; there is no `execute`, network,
  archive, signal, target, model, or score surface. A registered generated
  closeout was permitted only after this exact implementation became remotely
  green.
- **MARC2-FW1 consumed generated result:** exact implementation `36f8775`
  passed both CI jobs before one registered closeout routed `MARC2FWG-R1` in
  0.211 seconds at 32.0 MB reported peak RSS. It emitted and removed 221,068
  temporary bytes, preserved the 16-person/8.105-GB fixture result, passed all
  4 boundaries and 40 refusals, and left every private/real counter at zero.
  This closes generated qualification; the next gate is an all-false packet
  for one exact private-inventory read, not payload acquisition or science.
- **MARC2-FW1A private-selection request:** the repository now binds an all-
  false Tier C packet to the exact 418,755-byte, mode-`0600`, 1,227-row private
  central-directory manifest and a new isolated output root. A future additive
  wrapper must pass the inherited 40 selector mutations plus 18 filesystem,
  proof, privacy, and one-shot refusals before one no-follow read can occur.
  Even a successful future selection stops before every archive local header,
  member payload, neural sample, event, target, model, prediction, and score.
  The packet itself performs zero private operations and grants no authority.
- **MARC2-FW1A packet-bound decision:** after the all-false request became
  remotely green and was identified as the sole Tier C gate, the maintainer's
  exact fresh `continue` was recorded additively. The decision authorizes only
  a generated/mock wrapper after the decision itself is green and one exact
  private-manifest selection after that wrapper is separately green. It does
  not authorize an archive member, EEG payload, neural analysis, target,
  model, score, provider, `MARC2-FW2`, or scientific claim.
- **MARC2-FW1A proof-gated wrapper:** decision `ad1e406` passed Base Python job
  `94656172494`, Optional Neuro Readers job `94656172528`, and CI
  `31764052451` before implementation. The additive standard-library wrapper
  has fixed `plan`, `qualify`, `inspect`, and proof-disabled `execute`
  commands; exact no-follow owner/mode/size/hash/schema gates; bounded
  short-read handling; a pre-content consumed marker; separate private and
  aggregate outputs; and an aggregate-only consumed failure receipt. Its final
  generated run passed all 40 inherited selector refusals and 18 wrapper
  refusals, selecting the same 16-person/384-member fixture prefix at
  8,105,207,776 reservation bytes in 0.268 seconds at 36.1 MB peak RSS. All
  3,071 base and 3,142 optional-neuro tests pass. Retained-private, network,
  archive-member, neural, target, model, and score counters remain zero. The
  exact wrapper commit `d9a3853` subsequently passed both remote jobs; that
  proof did not itself access the private inventory or authorize payload work.
- **MARC2-FW1A consumed proof failure:** the sole registered invocation exited
  at `MARC2FWS-F00` with `implementation record differs`. The proof gate ran
  before the machine gate, retained source path, consumed marker, content open,
  hash, parse, selection, or output writers. A tracked-artifact-only diagnosis
  found the implementation registry omitted its required top-level
  `lane_id: MARC2-FW1A`; no private file was inspected to find that cause.
  Private-path checks, opens, bytes, hashes, parses, participant/member
  selections, payload reads, signal/target/model/score operations, and outputs
  all remained zero. The invocation is consumed without repair or rerun.
  `MARC2-FW2` remains ineligible; any recovery must be separately named,
  generated-qualified, and newly gated before private access.
- **MARC2-FW1B generated proof-record recovery:** the new frozen contract makes
  the implementation record itself a strict interface. It requires
  `lane_id: MARC2-FW1B` among 15 exact top-level fields, unique non-self
  artifact bindings, one shared `validate_implementation_record` entry point,
  deterministic replay, and 32 ordered malformed-record refusals under a
  30-second, 256-MiB, one-thread envelope. This milestone authorizes only a
  generated validator implementation after both CI jobs are green. Its private
  execution limit is zero; the retained manifest, archive members, EEG,
  targets, models, scores, `MARC2-FW2`, and scientific claims remain closed.
- **MARC2-FW1B shared-validator implementation:** the exact implementation
  accepts the complete 15-field registry itself, including top-level
  `lane_id`, and separates expected remote proof from observed Git/CI proof.
  One fresh generated run made 34 calls through the same public validator: two
  replay-identical canonical passes and 32 exact refusals. It processed 84,701
  generated bytes, emitted and removed a 6,711-byte aggregate report, ran in
  0.016927 seconds at 27,099,136-byte peak RSS, and used one thread. All 3,134
  base and 3,205 optional-neuro tests pass locally. Real/private, network,
  archive, EEG, target, model, score, provider, and hardware counters remain
  zero. Exact commit `6f613b3` passed Base Python job `94669566174`, Optional
  Neuro Readers job `94669566187`, and CI `31768593977` before the next packet
  was prepared.
- **MARC2-FW1C all-false live-recovery request:** the new packet proposes two
  separately gated stages: a standard-library generated/mock wrapper that must
  prove its own future HEAD through the exact shared validator, then one
  no-retry target-free read of the exact 418,755-byte structural manifest. It
  names a new output root, caps live output at 2 MiB, requires 15 GiB free, and
  stops before every archive member, EEG sample, target, model, or score. Every
  authorization flag is false and every operation counter is zero. Exact
  request `7804c3e` passed Base Python job `94672387003`, Optional Neuro
  Readers job `94672386941`, and CI `31769518851`.
- **MARC2-FW1C packet-bound decision:** after the packet was identified as the
  sole Tier C gate, the maintainer's fresh exact `continue` was recorded without
  a fabricated long recital. The decision binds the request hashes, future
  wrapper HEAD proof, 90 required future refusals, one possible later 418,755-byte
  structural read, and zero archive-member/payload bytes. All 3,170 base and
  3,241 optional-neuro tests pass locally. Exact decision `b0466e5` passed Base
  Python job `95120011473`, Optional Neuro Readers job `95120011519`, and CI
  `31928627432`; private access remains closed until the generated/mock wrapper
  is separately remotely green.
- **MARC2-FW1C shared-proof recovery wrapper:** the new standard-library module
  keeps a native `MARC2-FW1C` registry separate from an FW1B-format certificate
  and calls the exact shared validator twice canonically plus once for each of
  32 proof mutations. One final generated closeout passed 32/32 proof-record,
  40/40 selector, and 18/18 wrapper refusals, then replayed the same 16-person,
  96-bundle, 384-row structural prefix at 8,105,207,776 future reservation
  bytes. It processed 846,712 generated bytes and emitted 298,059 temporary
  bytes in 0.374161 seconds at 38,666,240-byte peak RSS. All 3,214 base and
  3,285 optional-neuro tests pass; every private, network, archive, neural,
  target, model, score, retry, and claim counter is zero. The temporary output
  was removed. Exact wrapper `7b924be` then passed Base Python job
  `95123374369`, Optional Neuro Readers job `95123374211`, and CI
  `31930051249` before its one registered structural-manifest selection.
- **MARC2-FW1C consumed source-identity failure:** the sole invocation opened,
  read, hashed, and strictly parsed exactly 418,755 structural bytes once, then
  routed `MARC2FWC-F02` because strict live source identity differed. It
  selected zero participants and zero members, wrote no private selection, and
  performed zero network, archive-member, signal, target, model, prediction,
  or score operations. Runtime was 0.091374 seconds at 25,280,512-byte peak
  RSS with 6,944 total output bytes. The aggregate does not retain which
  private field differed. The invocation is consumed without retry, no
  selection result exists, and `MARC2-FW2` remains ineligible.
- **MARC2-SL1 exact schema-lineage diagnosis:** a fixed artifact-only AST/JSON
  audit reconciled the exact producer, generated fixture, selector validator,
  and FW1C validator. MARC-1 forwards keys `directory`, `metadata`, and `tail`;
  every consumer-side artifact instead requires `central_directory`,
  `metadata`, and `tail`. That one alias mismatch is sufficient to explain
  `MARC2FWC-F02`. Generated tests missed it because fixture and validators were
  internally consistent with each other but not source compatible. The audit
  read 310,015 committed bytes in 0.027645 seconds at 35,717,120-byte peak RSS
  and performed zero private, archive, neural, target, model, or network work.
  A future repair must validate the producer-native vocabulary first, then map
  `directory` to `central_directory` exactly once in a new adapter.
- **MARC2-TA1 generated adapter result:** after registration commit `0c0e1c8`
  passed CI `31932701989`, the standard-library adapter validated all 1,227
  producer-native generated rows before deep-copying and mapping only
  `directory` to `central_directory`. All 26 refusal mutations and both entry
  orders passed, every transport digest replayed byte for byte, and the
  unchanged selector reproduced 16 generated subject identities, 96 bundles,
  384 members, and 8,105,207,776 reserved bytes. The one measured run used
  846,708 input bytes, 4,931 output bytes, 0.453316 seconds, and 39,108,608-byte
  peak RSS; every private, neural, target, model, and network counter was zero
  and the temporary report was removed. This fixes a generated integration
  boundary; it is not neural or decoding evidence. Live/private use remains a
  separate Tier C decision.
- **Causal Motor Lattice synthetic gate:** contract commit `67709a3` and exact
  implementation `90fa467` were separately green before one seed-5513 run of
  the 4,535-parameter `CML-v0`. The model reached `1.0` hand and key accuracy on
  all 16 constructed signal-bearing check rows, localized potential, mu, and
  beta factors under matching branch ablations, passed key-to-hand marginal
  consistency and zero-right-context future-tail checks, and replayed its
  checkpoint hash exactly. Eighteen of 19 check gates passed. Float32
  common-mode key-logit error was `1.9073486e-6`, above the frozen `1e-6`
  tolerance, so the one run parked at `CML-R0`; synthetic final targets stayed
  closed and no rerun is permitted. Runtime was 6.553 seconds at 398,737,408
  bytes peak RSS with 37,371 generated bytes. PhysioNet, Loop 54-B/C, S20,
  protected targets, model claims, hardware, and scientific promotion remain
  closed.
- **Foundation-model decoder strategy:** the product path now explicitly uses
  a compact causal sensor adapter as a bridge into frozen `gpt-5.6-sol`, not as
  the final language model. Hosted Sol receives only CTC n-best text and
  compact causal key evidence because its API does not accept custom hidden
  embeddings. The matched matrix keeps `FM-A00` language-only, `FM-A01`
  CTC-only, `FM-A02` matched CTC plus neural evidence, and `FM-A03` fixed
  item-deranged evidence. FM-0 is now implemented as a deterministic no-call
  compiler: its committed 7,327-byte fixture produced 12 plans in 34,349 bytes,
  0.00275 seconds, and about 21.5 MB peak RSS. The additive FM-1 qualification
  freezes `gpt-5.6-terra` as the lower-cost synthetic transport candidate while
  preserving Sol as the quality-first product candidate. Its contract,
  authorization, and implementation were remotely green before one live
  invocation. Three calls were attempted: language-only `FM-A00` abstained,
  CTC-only `FM-A01` returned `HELLO WURLD`, and the first matched `FM-A02`
  returned a non-completed provider status. The no-retry runner parked and
  preserved a 5,882-byte sanitized receipt after 8.406 seconds at 39,337,984
  bytes peak RSS. Two completed responses used 339 input and 143 output tokens
  for a $0.002394 partial local estimate; usage and charge for the third attempt
  are unavailable. No `FM-A03` response or matched-versus-deranged comparison
  exists. FM-1 is consumed with no rerun. Real rows, targets, scoring, training,
  fine-tuning, and scientific claim promotion remain closed.
- **AI budget and local-first leverage:** the user authorized a $50 aggregate
  AI-provider ceiling for the next R&D steps. The complete $0.50 FM-1 cap is
  conservatively reserved because usage for its non-completed third response is
  unavailable; the remaining $49.50 is divided into ceilings for an independent
  transport recovery, synthetic Sol/Terra controls, public target-free
  integration, later target-bearing work, protected evaluation, and
  contingency. These are release gates, not spending targets. Local work should
  reuse MNE for data/QC, MOABB for grouped public benchmarks, pyRiemann for
  serious low-data baselines, and compact Braindecode models before buying more
  inference. Apple application `US20230225659A1` describes dynamic electrode
  selection in an earbud form and names EEG, but does not mention AirPods or
  prove a shipping thought-to-text product. A future generic ear-channel
  adapter begins with synthetic contact/noise fixtures; hardware, SDKs,
  purchases, participant recording, and commercial implementation remain
  separate.
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

The project is moving toward a local-first cohort federation: contributors
would validate source identity, geometry, timing, trials, splits, controls, and
resources on their own machines, then share a hash-bound aggregate receipt
rather than raw EEG or plaintext targets. That direction is researched but not
implemented or authorized for real-data aggregation yet. See
[`docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md`](docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md).

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
| [docs/MARC_2_LIVE_SELECTION_RECOVERY_IMPLEMENTATION.md](docs/MARC_2_LIVE_SELECTION_RECOVERY_IMPLEMENTATION.md) | native FW1C wrapper, distinct FW1B certificate, exact shared-validator chain, 90-mutation qualification, resources, and closed private/scientific boundary |
| [registries/marc2_live_selection_recovery_implementation.v0.json](registries/marc2_live_selection_recovery_implementation.v0.json) | machine-readable native FW1C implementation, frozen source/output identity, qualification metrics, zero access counters, and remote-green next gate |
| [registries/marc2_live_selection_recovery_proof_certificate.v0.json](registries/marc2_live_selection_recovery_proof_certificate.v0.json) | distinct 15-field FW1B-format certificate binding the recovery wrapper, native registry, tests, decision, shared validator, and selector |
| [docs/MARC_2_LIVE_SELECTION_RECOVERY_RESULT.md](docs/MARC_2_LIVE_SELECTION_RECOVERY_RESULT.md) | consumed one-read source-identity failure, exact resources and counters, unavailable private detail, no-rerun disposition, and claim boundary |
| [registries/marc2_live_selection_recovery_failure_result.v0.json](registries/marc2_live_selection_recovery_failure_result.v0.json) | aggregate machine result binding green proof, report identity, one-open counters, `MARC2FWC-F02`, zero forbidden operations, and closed FW2 authority |
| [docs/MARC_2_SOURCE_SCHEMA_LINEAGE_AUDIT.md](docs/MARC_2_SOURCE_SCHEMA_LINEAGE_AUDIT.md) | exact producer-versus-consumer transport-key diagnosis, why generated tests missed it, measured artifact-only audit, and prospective one-way adapter design |
| [registries/marc2_source_schema_lineage_result.v0.json](registries/marc2_source_schema_lineage_result.v0.json) | machine-readable `MARC2SL-R2` result, exact key sets, source-binding proof, zero forbidden counters, and closed live/FW2 boundary |
| [docs/MARC_2_TRANSPORT_ALIAS_ADAPTER_PREREGISTRATION.md](docs/MARC_2_TRANSPORT_ALIAS_ADAPTER_PREREGISTRATION.md) | frozen generated-only producer-native adapter design, mutation matrix, selector integration target, resources, and closed live boundary |
| [registries/marc2_transport_alias_adapter_contract.v0.json](registries/marc2_transport_alias_adapter_contract.v0.json) | machine-readable `MARC2-TA1` contract binding green lineage proof, exact vocabularies, 26 mutations, three-command surface, and zero live authority |
| [docs/MARC_2_TRANSPORT_ALIAS_ADAPTER_IMPLEMENTATION.md](docs/MARC_2_TRANSPORT_ALIAS_ADAPTER_IMPLEMENTATION.md) | generated-only adapter implementation, validation order, exact selector replay, measured qualification, verification, and scientific boundary |
| [registries/marc2_transport_alias_adapter_implementation.v0.json](registries/marc2_transport_alias_adapter_implementation.v0.json) | hash-bound adapter code, tests, generated result, resources, zero forbidden counters, and remote-green gate |
| [registries/marc2_transport_alias_adapter_result.v0.json](registries/marc2_transport_alias_adapter_result.v0.json) | machine-readable consumed `MARC2TA-G1` result, 26 mutation routes, exact measurements, unavailable fields, and closed live/FW2 disposition |
| [docs/FOUNDATION_MODEL_DECODER_STRATEGY_2026-08-06.md](docs/FOUNDATION_MODEL_DECODER_STRATEGY_2026-08-06.md) | layered compact-adapter plus GPT-Sol architecture, four matched conditions, and staged authorization boundary |
| [docs/FOUNDATION_MODEL_BRIDGE_V0.md](docs/FOUNDATION_MODEL_BRIDGE_V0.md) | implemented FM-0 synthetic no-call schemas, CLI, strict refusals, hashes, and measured roundtrip |
| [docs/FOUNDATION_MODEL_LIVE_SMOKE_PREREGISTRATION.md](docs/FOUNDATION_MODEL_LIVE_SMOKE_PREREGISTRATION.md) | frozen one-shot FM-1 Terra matrix, privacy boundary, provider settings, resource caps, and no-science ceiling |
| [docs/FOUNDATION_MODEL_LIVE_SMOKE_AUTHORIZATION_DECISION.md](docs/FOUNDATION_MODEL_LIVE_SMOKE_AUTHORIZATION_DECISION.md) | exact user authorization bound to the remotely green FM-1 contract |
| [docs/FOUNDATION_MODEL_LIVE_SMOKE_IMPLEMENTATION.md](docs/FOUNDATION_MODEL_LIVE_SMOKE_IMPLEMENTATION.md) | dependency-free provider transport, dry-run and inspect CLI, strict receipts, local measurements, and pre-execution remote-green gate |
| [registries/foundation_model_live_smoke_implementation.v0.json](registries/foundation_model_live_smoke_implementation.v0.json) | machine-readable FM-1 code hashes, request shape, guards, measurements, zero counters, and current not-executed state |
| [docs/FOUNDATION_MODEL_LIVE_SMOKE_RESULT.md](docs/FOUNDATION_MODEL_LIVE_SMOKE_RESULT.md) | consumed FM-1 partial-call trace, measurements, terminal boundary, gate verdict, and no-rerun closeout |
| [registries/foundation_model_live_smoke_result.v0.json](registries/foundation_model_live_smoke_result.v0.json) | machine-readable parked result, response summaries, counters, unavailable fields, and claim ceiling |
| [docs/AI_LOCAL_FIRST_R_AND_D_BUDGET_2026-08-08.md](docs/AI_LOCAL_FIRST_R_AND_D_BUDGET_2026-08-08.md) | $50 provider ceiling portfolio, local open-source tool strategy, earbud-patent boundary, and ordered next work |
| [registries/ai_local_first_rd_budget.v0.json](registries/ai_local_first_rd_budget.v0.json) | machine-readable ceilings, release conditions, standing target-free scope, local tools, and closed scientific gates |
| [docs/LOCAL_EEG_TOOLING_AUDIT_2026-08-08.md](docs/LOCAL_EEG_TOOLING_AUDIT_2026-08-08.md) | measured zero-network capability inventory, resource accounting, missing tools, and no-science boundary |
| [registries/local_eeg_tooling_audit_result.v0.json](registries/local_eeg_tooling_audit_result.v0.json) | raw bounded seven-tool capability report with sanitized warnings and zero access counters |
| [registries/local_eeg_tooling_audit_receipt.v0.json](registries/local_eeg_tooling_audit_receipt.v0.json) | exact green-implementation, result-hash, resource, route, and claim receipt |
| [docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md](docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md) | active 20-work-order execution overlay with Tier A/B autonomy and exact Tier C stops |
| [docs/PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md](docs/PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md) | frozen nine-EDF work-order-8 identity, access order, resource caps, no-retry rule, and acquisition-only ceiling |
| [docs/PHYSIONET_MOTOR_ACQUISITION_IMPLEMENTATION.md](docs/PHYSIONET_MOTOR_ACQUISITION_IMPLEMENTATION.md) | fixture-qualified standard-library metadata, transfer, one-pass hash, atomic promotion, receipt, CLI, and refusal implementation |
| [registries/physionet_motor_acquisition_implementation.v0.json](registries/physionet_motor_acquisition_implementation.v0.json) | hash-bound implementation sources, green authorization parent, fixture metrics, resources, and zero-real-access ledger |
| [docs/PHYSIONET_MOTOR_ACQUISITION_RESULT.md](docs/PHYSIONET_MOTOR_ACQUISITION_RESULT.md) | consumed 12-of-12 acquisition closeout with exact bytes, runtime, RSS, disk, zero forbidden counters, and scientific ceiling |
| [registries/physionet_motor_acquisition_result.v0.json](registries/physionet_motor_acquisition_result.v0.json) | sanitized machine-readable nine-file identity result, private-receipt hashes, measurements, gates, and closed work-order-9 boundary |
| [docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PRIMARY_SOURCE_RESEARCH.md](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PRIMARY_SOURCE_RESEARCH.md) | work-order-9 method, cue/ocular/muscle caveats, prediction-physiology-confound triangulation, verdict ladder, and replication route |
| [docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREREGISTRATION.md](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREREGISTRATION.md) | frozen S001-S003 grouped split, causal views, models, controls, remote-green prediction freeze, thresholds, resources, and claim ceiling |
| [registries/physionet_motor_positive_control_contract.v0.json](registries/physionet_motor_positive_control_contract.v0.json) | machine-readable 9-file, 135-event prospective contract with 12 final prediction sets, one sealed score, and all current permissions false |
| [docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_PACKET.md](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_PACKET.md) | exact conditional work-order-9 implementation, dependency, EDF, prediction-freeze, scoring, resource, exclusion, and claim decision surface |
| [registries/physionet_motor_positive_control_authorization_request.v0.json](registries/physionet_motor_positive_control_authorization_request.v0.json) | all-false request bound to green registration `3c00557`, CI `31346882592`, exact hashes, and one exact maintainer sentence |
| [docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_DECISION.md](docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_DECISION.md) | exact maintainer decision, parent request proof, four remotely green gates, one-shot limits, and unchanged scientific ceiling |
| [registries/physionet_motor_positive_control_authorization_decision.v0.json](registries/physionet_motor_positive_control_authorization_decision.v0.json) | machine-checkable work-order-9 authorization with conditional implementation, EDF, freeze, and scoring permissions plus explicit refusals |
| [docs/SYNTHETIC_MOTOR_FIXTURE_PREREGISTRATION.md](docs/SYNTHETIC_MOTOR_FIXTURE_PREREGISTRATION.md) | frozen work-order-3 factor, pair, partition, mutation, resource, leakage, and no-model fixture boundary |
| [registries/synthetic_motor_fixture_contract.v0.json](registries/synthetic_motor_fixture_contract.v0.json) | machine-readable seed-5503, 96-item, eight-family Tier B fixture contract with zero execution counters |
| [docs/SYNTHETIC_MOTOR_FIXTURE_IMPLEMENTATION.md](docs/SYNTHETIC_MOTOR_FIXTURE_IMPLEMENTATION.md) | locally qualified deterministic generator, validator, inspector, mutation, CLI, and pre-execution boundary |
| [registries/synthetic_motor_fixture_implementation.v0.json](registries/synthetic_motor_fixture_implementation.v0.json) | hash-bound work-order-3 source, test, resource, and pending-remote-green implementation receipt |
| [docs/SYNTHETIC_MOTOR_FIXTURE_RESULT.md](docs/SYNTHETIC_MOTOR_FIXTURE_RESULT.md) | consumed one-shot synthetic closeout with measured shape, bytes, runtime, RSS, counters, warnings, and claim boundary |
| [registries/synthetic_motor_fixture_result.v0.json](registries/synthetic_motor_fixture_result.v0.json) | machine-readable all-gates-pass work-order-3 receipt and no-real-data access ledger |
| [docs/CLASSICAL_EEG_ADAPTER_PREREGISTRATION.md](docs/CLASSICAL_EEG_ADAPTER_PREREGISTRATION.md) | frozen no-install shrinkage-LDA, CSP-LDA, Riemannian-MDM, grouped-fit, target-firewall, and refusal boundary |
| [registries/classical_eeg_adapter_contract.v0.json](registries/classical_eeg_adapter_contract.v0.json) | machine-readable three-adapter work-order-4 plan contract with twelve leakage refusals and zero execution counters |
| [docs/CLASSICAL_EEG_ADAPTER_IMPLEMENTATION.md](docs/CLASSICAL_EEG_ADAPTER_IMPLEMENTATION.md) | locally qualified standard-library symbolic plan, hash, validation, refusal, CLI, and pre-execution boundary |
| [registries/classical_eeg_adapter_implementation.v0.json](registries/classical_eeg_adapter_implementation.v0.json) | hash-bound pre-execution work-order-4 implementation sources, tests, resources, and zero-access ledger |
| [docs/CLASSICAL_EEG_ADAPTER_RESULT.md](docs/CLASSICAL_EEG_ADAPTER_RESULT.md) | consumed one-shot symbolic roundtrip with bytes, runtime, RSS, refusals, access counters, and no-science boundary |
| [registries/classical_eeg_adapter_result.v0.json](registries/classical_eeg_adapter_result.v0.json) | machine-readable all-gates-pass work-order-4 receipt and route to synthetic contact semantics |
| [docs/CONTACT_AWARE_EAR_CHANNEL_PREREGISTRATION.md](docs/CONTACT_AWARE_EAR_CHANNEL_PREREGISTRATION.md) | primary-source-bounded work-order-5 contact, missingness, bilateral weighting, causality, and no-hardware contract |
| [registries/contact_aware_ear_channel_contract.v0.json](registries/contact_aware_ear_channel_contract.v0.json) | machine-readable 48-item, 16-channel, 16-refusal synthetic ear-channel contract and zero-action ledger |
| [docs/CONTACT_AWARE_EAR_CHANNEL_IMPLEMENTATION.md](docs/CONTACT_AWARE_EAR_CHANNEL_IMPLEMENTATION.md) | locally qualified deterministic fixture, fixed bilateral policy, hashes, validation, refusal, CLI, and pre-execution boundary |
| [registries/contact_aware_ear_channel_implementation.v0.json](registries/contact_aware_ear_channel_implementation.v0.json) | hash-bound work-order-5 implementation sources, tests, resources, probe observations, and zero-access ledger |
| [docs/CONTACT_AWARE_EAR_CHANNEL_RESULT.md](docs/CONTACT_AWARE_EAR_CHANNEL_RESULT.md) | consumed one-shot synthetic roundtrip with masks, hashes, bytes, runtime, RSS, cleanup, counters, and no-science boundary |
| [registries/contact_aware_ear_channel_result.v0.json](registries/contact_aware_ear_channel_result.v0.json) | machine-readable all-gates-pass work-order-5 receipt and gated route to Loop 54-A parser qualification |
| [docs/LOOP_54_STAGE_A_VHDR_IMPLEMENTATION.md](docs/LOOP_54_STAGE_A_VHDR_IMPLEMENTATION.md) | green-decision-bound strict parser, synthetic adversarial qualification, one-shot filesystem order, CLI, resources, and no-S20-access boundary |
| [registries/loop54_stage_a_vhdr_implementation.v0.json](registries/loop54_stage_a_vhdr_implementation.v0.json) | machine-readable parser source hashes, 22 refusal classes, zero real-access ledger, and pending exact-implementation-green gate |
| [docs/LOOP_54_STAGE_A_VHDR_RESULT.md](docs/LOOP_54_STAGE_A_VHDR_RESULT.md) | consumed one-shot F11 park with passed source/decode gates, failed preamble gate, resource measurements, zero sibling/protected access, and no-rerun route |
| [registries/loop54_stage_a_vhdr_result.v0.json](registries/loop54_stage_a_vhdr_result.v0.json) | machine-readable 18-gate result map, one-open access ledger, unavailable fields, blocked downstream route, and L54-Q1 claim ceiling |
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
| [docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md](docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md) | current open EEG benchmark review, public motor positive-control prospect, specialist baseline and physiology upgrades, foundation-model deferral, and local-first contributor strategy |
| [registries/open_eeg_rd_strategy.v0.json](registries/open_eeg_rd_strategy.v0.json) | machine-readable source pins, tool decisions, nine-file public prospect, resource caps, authorization zeros, and claim boundary |
| [docs/LOOP_55_CAUSAL_MOTOR_LATTICE_ARCHITECTURE_RESEARCH.md](docs/LOOP_55_CAUSAL_MOTOR_LATTICE_ARCHITECTURE_RESEARCH.md) | failure-addressable compact EEG architecture, physical key lattice, exact hand marginal, causal DSP rules, two-axis public qualification, and stop strategy |
| [registries/loop55_causal_motor_lattice_research.v0.json](registries/loop55_causal_motor_lattice_research.v0.json) | machine-readable CML-v0 graph, parameter formula, source ceilings, branch escrow, public gates, authorization zeros, and nonclaims |
| [docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_PREREGISTRATION.md](docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_PREREGISTRATION.md) | frozen work-order-13 synthetic factors, exact model, check-before-final order, one-run resource caps, stop routes, and no-real-data boundary |
| [registries/causal_motor_lattice_synthetic_contract.v0.json](registries/causal_motor_lattice_synthetic_contract.v0.json) | machine-readable seed-5513 CML-v0 architecture, hashes, training schedule, 19 check gates, final firewall, resources, and refusals |
| [docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_IMPLEMENTATION.md](docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_IMPLEMENTATION.md) | exact 4,535-parameter model, deterministic synthetic runner, dry-run and inspector CLI, adversarial qualification, and remote-green execution gate |
| [registries/causal_motor_lattice_synthetic_implementation.v0.json](registries/causal_motor_lattice_synthetic_implementation.v0.json) | hash-bound source, implementation, fixture projection, lattice, resource, test, and zero-execution receipt |
| [docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_RESULT.md](docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_RESULT.md) | consumed 18-of-19-gate synthetic result, constructed-factor diagnostics, exact common-mode failure, withheld final, resources, and no-rerun closeout |
| [registries/causal_motor_lattice_synthetic_result.v0.json](registries/causal_motor_lattice_synthetic_result.v0.json) | machine-readable `CML-R0` result, checkpoint/report hashes, metrics, access counters, warnings, unavailable fields, and scientific claim ceiling |
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
| [docs/LOOP_54_STAGE_A_REGISTRATION_CI_RECOVERY.md](docs/LOOP_54_STAGE_A_REGISTRATION_CI_RECOVERY.md) | exact-commit retry failure, frozen-payload identity, pinned remote proof anchor, exact-tree replay, and unchanged authorization boundary |
| [registries/loop54_stage_a_registration_ci_recovery.v0.json](registries/loop54_stage_a_registration_ci_recovery.v0.json) | machine-readable toolchain-drift classification, immutable hashes, measured replay, green anchor, zero access counters, and false authorization flags |
| [docs/LOOP_54_STAGE_A_AUTHORIZATION_PACKET.md](docs/LOOP_54_STAGE_A_AUTHORIZATION_PACKET.md) | historical non-actionable v0 request retained for audit and superseded by the recovery-bound v1 request |
| [docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md](docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md) | current recovery-bound exact Tier C decision surface, ordered green gates, one-file resource caps, full refusals, and scientific nonclaims |
| [registries/loop54_stage_a_recovery_authorization_request.v1.json](registries/loop54_stage_a_recovery_authorization_request.v1.json) | machine-readable v1 request binding the immutable registration, green proof anchor, recovery record, superseded v0 request, all-false permissions, zero S20 access counters, and exact user sentence |
| [docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_DECISION.md](docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_DECISION.md) | exact user decision, green request binding, two-stage evidence order, resource ceiling, authorization-only zero counters, and nonclaims |
| [registries/loop54_stage_a_recovery_authorization_decision.v1.json](registries/loop54_stage_a_recovery_authorization_decision.v1.json) | machine decision enabling synthetic parser work only after decision CI and one conditional VHDR execution only after implementation CI |
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
