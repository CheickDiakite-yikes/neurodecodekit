# Next 20 Systematic Execution Work Orders

Status: **Active execution overlay; not a replacement for the frozen Loops
45-64 scientific roadmap**

This queue converts the current EEG and causal-model strategy into an ordered
set of small work orders. It does not renumber scientific loops or loosen any
existing contract. Tier A and bounded Tier B rows may proceed under the approved
Research Autonomy Charter. Every Tier C row still stops for a separate exact
decision after its own frozen packet and required remote-green evidence exist.

| # | Work order | Tier | Acceptance boundary | Status |
|---:|---|---|---|---|
| 1 | Recover Loop 54-A registration CI evidence | A | Preserve frozen artifacts, diagnose toolchain drift, obtain green descendant evidence | Complete |
| 2 | Audit local EEG tool capabilities | A | Fixed zero-network probes, one thread, <=1 MiB output, all data/model counters zero | Complete |
| 3 | Build synthetic physiology/confound fixtures | B | Deterministic motor, timing, ocular, line-noise, dropout, and corruption cases with no target leakage | Complete |
| 4 | Add classical EEG adapter contracts | B | Optional dependency boundaries, grouped-fit rules, leakage tests, no real execution | Complete |
| 5 | Add a contact-aware ear-channel adapter | B | Synthetic contact/noise/missingness fixtures and exact channel-mask semantics only | Complete |
| 6 | Freeze Loop 54-A decision and qualify parser | A/B then C decision | Recovery-bound exact packet, strict synthetic parser tests, green implementation before real access | Complete |
| 7 | Execute Loop 54-A once | C | One 11,705-byte VHDR open; no sibling resolution; all 18 gates pass | Consumed; Parked F11; No Rerun |
| 8 | Acquire tiny PhysioNet motor slice | C | Exactly nine pinned EDF files, 23,248,224 bytes, isolated receipt, no substitutions | Complete; Consumed; 12/12 Gates Passed; No Rerun |
| 9 | Run grouped public motor positive control | C | Participant/run grouping, prediction + physiology + confound conjunction, remotely green prediction freeze | Complete; Consumed; WO9-V1; Low-Frequency Comparator 0.800 BA Secondary; No Rerun; Future Escalation Gated; prior gates: Implementation Qualified Locally, Execution Pending Remote Green, Freeze Pending Remote Green |
| 10 | Execute Loop 54-B signal quality | C | Target-blind VHDR+EEG read, every channel retained, no transform, bounded aggregate output | Gated |
| 11 | Execute Loop 54-C trial reconciliation | C | Isolated VMRK+MAT target-bearing stage, no plaintext protected public output | Gated |
| 12 | Close Loop 54-D eligibility ledger | A after C evidence | At least 48 unique performed trials or explicit park; confounds and missing geometry remain visible | Gated |
| 13 | Implement CML-v0 synthetically | B | Exact 4,535-parameter 64-channel reference, causal controls, deterministic replay, no real data | Consumed; Parked CML-R0; No Rerun; prior gates: Contract Frozen, Implementation Qualified Locally, Execution Pending Remote Green |
| 14 | Freeze measured Loop 55 contract | A then C decision | One <=10,000-parameter family, <=12 fits, fixed controls, resource and target order frozen | Gated |
| 15 | Create opaque grouped trial split | C | Trial-level grouping, no key-window leakage, targets isolated by stage | Gated |
| 16 | Run bounded Loop 55 training/selection | C | One thread, <=45 CPU minutes, <=1 GiB RSS, <=64 MiB output, no post-selection final access | Gated |
| 17 | Freeze final predictions | C evidence order | Hash-only predictions committed, pushed, and remotely green before final targets | Gated |
| 18 | Score Loop 55 once and route | C | Exact paired tests and all controls together; no rerun or post-target tuning | Gated |
| 19 | Produce Loop 56 aggregate verdict | C claim decision | One of five frozen verdict classes; no individual protected payload reopening | Gated |
| 20 | Open parity or reproducibility branch | Evidence dependent | Proceed only from the measured result; otherwise preserve the parked boundary | Gated |

## Current Route

Work orders 1 and 2 are complete. The local audit found NumPy `2.5.0` and SciPy
`1.18.0` ready without adding dependencies. MNE `1.12.1` exposes the
BrainVision reader and ICA, while scikit-learn, pyRiemann, MOABB, and
Braindecode are absent. No broad install has been justified.

Work order 3 is complete. Contract commit `9238fd7` and implementation commit
`ad361c8` were each remotely green before one measured synthetic closeout. The
run used 1.20 seconds, 118,177,792-byte peak RSS, and 584,308 output bytes; all
18 gates passed and the two generated files were removed. Work order 4's
frozen plan registers low-frequency shrinkage LDA, causal CSP-LDA, and
Riemannian MDM without choosing or importing one, plus twelve fail-closed
leakage mutations. Exact implementation `eefb7b0` passed CI `31280581308`
before one measured roundtrip. All 18 gates passed in 0.12 seconds at
22,822,912-byte peak RSS with a 27,335-byte plan that was removed. Work order 4
is complete. Work order 5 closed synthetic contact-mask, channel-noise, and
missing-channel semantics. Its frozen seed-5505 contract
defines 48 items, 16 generic bilateral channels, six explicit masks, a fixed
four-per-side target-blind rule, 16 refusals, and no physical switching. It
authorizes no hardware or real data. Contract commit `c6e216f` passed CI
`31281290300` before implementation. The lazy-NumPy generator, strict loader,
metadata-only inspector, deterministic hashes, 16 refusals, free-disk/output
guards, and two CLI commands are locally qualified. One measured synthetic
roundtrip ran only after exact implementation `76ccc63` passed CI
`31282344300`. All 18 gates passed in 0.40 seconds at 55,394,304-byte peak RSS
with 938,874 generated bytes and 46,367,866,880 free bytes before execution.
Both generated files were removed. Work order 5 is complete. Work order 6 has
a recovery-bound decision packet in
`docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md` and a machine request
in `registries/loop54_stage_a_recovery_authorization_request.v1.json`. Every
authorization flag and S20 access counter remains false in those immutable
snapshots. Request commit `19813a8` passed CI `31283297030`, and the exact user
decision is preserved in separate human and machine records. Decision commit
`2177b36` passed CI `31286428489` before implementation. The strict
standard-library parser and dry-run-first CLI now pass 24 focused tests and 24
mutation subchecks covering all 22 refusal classes, with zero S20 path stats or
reads and no retained fixture. Exact implementation `b486fdf` passed CI
`31287819503` before work order 7 consumed one VHDR open and 11,705 read bytes.
Source size, Git-blob identity, and strict decoding passed, but the frozen
format preamble gate parked at `L54A-F11`. Runtime was 0.20 seconds at
24,051,712-byte peak RSS; sibling, protected, model, network, and output
counters stayed zero. Work orders 6 and 7 are closed. L54-Q2 failed, there is
no rerun, and work orders 10-12 remain blocked.

Work order 8 now has an acquisition-only preregistration and machine contract
for PhysioNet EEGMMIDB v1.0.0. It freezes exactly nine EDF paths from subjects
S001-S003 and motor-execution runs 03/07/11, totaling 23,248,224 bytes with
official SHA-256 identities. Its separately authorized one-shot acquisition
later transferred and verified exactly those nine files and 23,248,224 bytes.
All 12 acquisition gates passed, while every EDF parse, annotation, signal,
target, split, model, training, inference, scoring, retry, rerun, and
work-order-9 counter stayed zero. Work order 8 is complete and consumed.
Work order 9 advanced through its own green authorization and implementation,
then consumed one successful target-blind execution and one final score after
the exact aggregate freeze became remotely green. It is complete at `WO9-V1`.
Work order 9R is an additive evidence-dependent branch, not a replacement for
work order 10 and not a Work Order 9 rerun. Its Tier A research record selects
the contiguous untouched S004-S015 cohort and six runs per participant:
execution `03/07 -> 11` and imagery `04/08 -> 12`. The exact prespecified
`0.5-4 Hz` shrinkage-LDA comparator becomes the one future primary template,
with native and bidirectional transfer questions, central/frontal/occipital
views, an ocular-sensitive frontal asymmetry, early/pre-cue controls, timing,
no-signal, label, displacement, channel, and hemisphere controls. The five-way
router separates failed confirmation, execution-only confirmation,
execution/imagery robustness, and a maximum motor-compatible result. Even its
maximum route cannot establish brain-specific origin. Registration `716e543`
passed both jobs in CI `31354565966` and now freezes the exact 72 files,
184,252,032 bytes, target firewall, 144 fit ceilings, 18 conditions, 216
target-blind participant-condition prediction sets, and one combined final
target delivery. It authorizes no payload, split, model, target, score, or
claim. Read
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PRIMARY_SOURCE_RESEARCH.md`
and its machine registry, then the frozen preregistration and contract. The
all-false authorization packet and machine request are prepared separately;
they authorize nothing before their own remotely green commit and an exact
maintainer decision.

WO9R status: **Complete and consumed at `WO9R-R3`; no rerun or post-target
update.**
Decision `1efeac7` passed CI `31355944651`. The implementation completed one
72-run generated roundtrip with 144 fits and 216 target-blind prediction sets
in 12.083017 seconds at 260,784,128-byte peak RSS and 4,215,687 output bytes.
No real EDF or target was opened, network bytes were zero, and generated files
were removed. Implementation `8242674` passed CI `31359548779` before one
184,252,032-byte acquisition and one target-blind analysis. All 72 official
hashes matched. The analysis accepted 1,080 events and completed 144 fits and
216 prediction sets in 19.864386 seconds at 303,153,152-byte peak RSS. Zero
final targets reached the model stage. Freeze `8cd45d7` then passed both jobs
in CI `31360781199` before the same 360 targets opened once. Execution passed
all H1 gates at 123/180 and pooled balanced accuracy `0.680975`; imagery passed
all H2 gates at 131/180 and `0.728014`; both transfer directions were positive.
The frozen router returned `WO9R-R3`, not `WO9R-R4`, because motor-compatible
localization, physiology, and mandatory cue/frontal controls failed. Read
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_IMPLEMENTATION.md` and
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_RESULT.md`.
Audit label: **short-form packet-bound decision prepared**. It was then
committed, pushed, and remotely green before implementation.
It is deliberately outside the numbered 1-20 table so that the frozen
execution overlay remains exactly 20 rows.

IACKD-1 Cue-to-Action Reversal was the next Tier A research branch. It
uses the public OpenNeuro `ds006840` congruent/incongruent mapping to address
WO9R's unresolved cue-versus-action source question directly: fit a fixed
low-frequency model only where visual and hand directions agree, then score
one frozen held-out conflict prediction set against both actual hand direction
and the opposite visual target direction. The metadata-only inventory selects
1,340 raw EEG, marker, event, EOG-bearing source, ball, and Leap Motion objects
totaling 7,249,113,684 bytes while excluding published MATLAB derivatives.
No IACKD payload content, channel table, event, kinematic sample, target,
model, prediction, or score has been opened. Research commit `d6f955e` passed
both jobs in CI `31399402403`. The exact preregistration freezes the
participant-hand split, 30 ms target-blind motion guard, fixed 0.5-4 Hz model,
recorded HEOG/VEOG controls, 300-fit ceiling, 420 prediction sets, one combined
target delivery, `IACKD-R0` through `IACKD-R4` router, and one-thread 10 GiB
payload ceiling. Request `ef78c06` passed CI `31401738032`, and decision
`1f48b30` passed CI `31403012709` before generated-fixture implementation. The
exact acquisition, parser, target firewall, 300-fit/420-prediction path,
aggregate freeze, and isolated scorer were fixture qualified. Implementation
`f5c36ba` passed both jobs in CI `31409141349` before one real sequence. The
acquisition passed all 1,340 object and 7,249,113,684-byte gates. Analysis then
completed the full object hash pass and consumed at `IACKD-F10` on its first
lazy BrainVision parse because the frozen combined `32+4` channel gate did not
hold. It stopped before samples, targets, models, predictions, freeze, or
score. The lane is parked with no rerun; the retained private bundle is not
open for post-failure inspection. This additive lane does not renumber work
orders 10-20 and does not reopen WO9R.

IACKD-H1 Header Inventory Audit is now prospectively frozen and locally
fixture-qualified as the smallest useful follow-up. The article does not establish the failed exact-36-channel
assumption, and the authors' pinned public pipelines disagree on whether their
presence-based deletion vocabularies include M1/M2 or HEO/VEO while both name
TRIGGER. The contract selects all 128 committed VHDR metadata objects and only
161,792 expected bytes. Its future output is aggregate and hash-bound; the
existing local bundle, every sibling, sample, event, trajectory, target, model,
and score remain closed. Registration `0e52278` passed both jobs in CI
`31412667060` before the dependency-free implementation began. Exact
implementation `16621cc` passed both jobs in CI `31415213841` after one
measured 128-header generated roundtrip at 36,634,624-byte peak RSS. The
all-false request froze the smallest next irreversible step. Request `56531c6`
passed both jobs in CI `31416489006`, and decision `04f2706` passed both jobs
in CI `31424361969` before the sole 128-header/161,792-byte audit. All eleven
gates passed at `IACKDH-R5`: the declarations split 96 at 29 channels without
M1/M2 and 32 at 31 channels with M1/M2; all include HEOG, VEOG, and TRIGGER at
1024 Hz. The old global exact-36 assumption is invalid. Every local-bundle,
sibling, sample, event, target, model, and score counter remained zero. The
lane is consumed with no rerun. A separately named prospective repair is next.

That prospective repair is now designed in
`docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_RESEARCH.md`. Do not patch the consumed
reader in place: its target-free audit found three additional role errors,
including TRIGGER falling through to EEG. First freeze IACKD-H2 over exactly
316 public BIDS metadata bodies and 457,602 bytes, then qualify its parser and
router on generated fixtures, then prepare a separate real-content packet.
Only an aggregate H2 result may freeze IACKD-2. The later experiment requires
both congruent-to-incongruent and incongruent-to-congruent action-over-cue
reversal arms, using the weaker participant margin as the primary statistic.
The exact H2 preregistration is now frozen in
`docs/IACKD_CHANNEL_ROLE_GEOMETRY_PREREGISTRATION.md` and
`registries/iackd_channel_role_geometry_contract.v0.json`. It binds all 316
objects and 457,602 bytes, strict source-declared role parsing, explicit
unavailable values, aggregate-only output, and ordered routes `IACKDR-R0`
through `IACKDR-R4`. Generated-fixture implementation is eligible only after
this registration is committed, pushed, and both CI jobs are green. No H2
body, retained-bundle path, signal, target, model, or score is currently
authorized.

Registration `228ccd0` passed Base Python job `93583989913` and Optional Neuro
Readers job `93583989996` in CI `31427931578` before the exact H2 Tier B
implementation. Read `docs/IACKD_CHANNEL_ROLE_GEOMETRY_IMPLEMENTATION.md` and
its registry. The standard-library module now strictly parses all four
generated metadata roles, pairs runs and geometry privately, reconciles H1 and
sidecar declarations, emits one hashed aggregate role-map candidate, and
implements all `IACKDR-R0` through `IACKDR-R4` routes. A final synthetic pass
covered 316 bodies and 457,602 bytes in 0.054680 seconds at 34,996,224-byte
peak RSS with 8,282 output bytes. Constructed `IACKDR-R4` is not source
evidence. Commit, push, and obtain both green CI jobs before preparing a
separate all-false Tier C request; no H2 body or local bundle is open.

Exact implementation `9f6fef9` passed both jobs in CI `31430151368`. Read the
new all-false packet and machine request. They bind one possible later
316-request/457,602-byte public metadata audit, one private consumed marker,
one aggregate ledger, one thread, 180 seconds, 256 MiB RSS, and zero
retry/rerun. Every real-access flag remains false. Commit, push, and remotely
green the packet, then identify its sole scope before requesting a fresh
packet-bound maintainer decision. Do not issue a request from the packet.

Request `86174bc` passed both jobs in CI `31431064259`. After the packet,
proof, exact scope, and fresh-decision boundary were identified, the maintainer
said `continue :)`. The separate decision preserves those words and leaves the
316-request/457,602-byte scope unchanged. Commit, push, and remotely green the
decision before the private consumed marker or first request; all current
real-access counters remain zero.

Decision `f6eb5ab` passed both jobs in CI `31444154297` before the sole audit.
H2 is consumed at `IACKDR-R1` after exactly 316 requests and 457,602 bytes in
55.592999708 seconds at 86,769,664-byte peak RSS. The source has one stable
26-channel EEG core, 1024 Hz, average reference, and complete central and
occipital geometry across 30 groups. The frozen contract mishandled HEOG,
VEOG, and Trigger because all are source-typed and sidecar-counted as `MISC`.
No sample, event, target, model, prediction, or score was accessed. Do not
rerun or amend H2; specify a new source-type-first policy prospectively.

Registration `2a7b4188553e221133d788a081b838dbbb9f41bb` passed Base Python
job `93215490492` and Optional Neuro Readers job `93215490501` in CI
`31301730612`. The additive authorization packet and all-false machine request
now bind that immutable commit, the three registration artifact hashes, the
one-invocation/no-retry limits, and one exact decision sentence. Preparing the
request is not authorization. Its commit must be pushed and remotely green
before the sentence is accepted, and no implementation or payload operation
may begin from the packet alone.

The maintainer supplied the exact registered Tier C sentence after request
`f6eb577` passed both jobs in CI `31302161647`. Decision `00b91ed` then passed
both jobs in CI `31344104565` before implementation. The standard-library
executor and dry-run-first CLI now pass 23 dedicated adversarial tests using
only generated invalid-UTF-8 bytes and mocked responses. They enforce the exact
three-document/nine-HEAD metadata allowlist, no redirect or retry, bounded
streaming, one opaque local hash pass per EDF, exact membership, atomic
promotion, bounded receipts, and no parser or work-order-9 interface. The full
suite passes 1,448 tests with three expected skips and 493 subtests. Source
metadata, EDF, local-PhysioNet-path, parse, split, model, and experiment
counters remained zero through implementation. Exact implementation `92760ce`
then passed both jobs in CI `31345401581` before the one registered invocation.
All 12 acquisition gates passed: 12 metadata requests used 442,178 response-
body bytes, nine EDF requests transferred exactly 23,248,224 bytes, all nine
one-pass local SHA-256 values matched, and the complete bundle promoted in
50.682373 seconds at 55,181,312-byte peak RSS and 28,327,635-byte peak disk.
Every parser, event, target, model, training, inference, scoring, retry, rerun,
and work-order-9 counter stayed zero. Work order 8 is complete and consumed;
work order 9 later completed under its own separately green sequence. A
later 10 GB data ceiling is available for a
separately contracted future stage; it did not enlarge this immutable
23,248,224-byte inventory.

Work order 9 now has a prospective primary-source research record and strict
machine registration. It binds only the existing S001-S003 runs 03/07/11
inventory. Runs 03 and 07 alone select between fixed CSP-LDA and Riemannian
MDM; run 11 remains a sealed 45-event final set until every primary
and control prediction hash is committed, pushed, and remotely green. The
maximum pass requires held-out prediction, motor-compatible mu/beta physiology,
and timing, pre-cue, label, displacement, channel, hemisphere, and
frontal/occipital proxy controls together. One thread, 1,800 seconds, 768 MiB
RSS, 64 MiB output, zero network, and no rerun are frozen. Registration alone
authorized no operation. The exact Tier C decision is now remotely green and
the synthetic-only implementation is locally qualified; the implementation's
own remote-green gate remains mandatory before a local path stat or EDF read.

Registration `3c00557` passed Base Python job `93330354031` and Optional Neuro
Readers job `93330354047` in CI `31346882592`. A separate hash-bound Tier C
packet and all-false machine request now state the exact conditional sentence.
Request `c62b10a` passed Base Python job `93331241434` and Optional Neuro
Readers job `93331241411` in CI `31347209691`. The maintainer then supplied the
exact sentence. Authorization-only commit `da9399c` passed Base Python job
`93334251403` and Optional Neuro Readers job `93334251379` in CI
`31348287824` before implementation began. The strict reader, target-firewalled
derivatives, causal preprocessing, fixed CSP-LDA and Riemannian families, 12
controls, per-condition hash freeze, isolated aggregate scorer, resource
guards, and two dry-run-first CLI surfaces are now qualified on generated
arrays. The final synthetic roundtrip used nine runs and 135 events, made 33
fits and 45 target-blind model inferences, froze 12 prediction sets, and
completed in 8.961233 seconds at 327,647,232-byte peak RSS with 20,825,424
generated bytes. All gates passed; real-data, real-target, and network reads
were zero, and the disposable artifacts were removed. The synthetic `WO9-V2`
router output has no claim value. Exact implementation `52b9b15` then passed
Base Python job `93343718364` and Optional Neuro Readers job `93343718355` in
CI `31351728650` before the one real target-blind execution. That execution
verified and parsed all nine EDFs once, accepted 135 events, made 33 fits and
45 target-blind inferences, froze 12 aggregate-hashed sets, and stopped before
scoring in 3.054760 seconds at 460,734,464-byte peak RSS with 20,852,059
private generated bytes. Network, additional-payload, final-target-delivery,
score, retry, and rerun counters were zero. The aggregate freeze contains no
individual output. Freeze `01eeff6` then passed both jobs in CI `31352250838`
before one delivery and one score of the same 45 targets. The selected 8-30 Hz
primary reached 27/45 and 0.604 balanced accuracy versus 0.500 for the prior
but failed the frozen primary gate, routing `WO9-V1`. The prespecified 0.5-4 Hz
comparator reached 36/45, 0.800 balanced accuracy, and `p=0.000183`, which is
real held-out task-information evidence but not the selected primary and not a
brain-specific motor claim. Motor physiology and central-over-proxy
localization also failed. Work order 9 is complete and consumed with no rerun.

Work order 13 now has a frozen Tier B synthetic-only contract in
`docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_PREREGISTRATION.md` and
`registries/causal_motor_lattice_synthetic_contract.v0.json`. It binds the
existing seed-5503 synthetic fixture to a new seed-5513 experiment, exact
pair-anchored pre-event crops, fixed 64-channel projection and causal FIR
hashes, one 4,535-parameter model, one 600-step fit, check-before-final gates,
no rerun, and a 4 MiB output cap. Contract commit `67709a3` passed exact push CI
`31294479865` before implementation, and implementation commit `90fa467`
passed exact push CI `31295430105` before the one run. The seed-5513 checkpoint
reached `1.0` hand and key accuracy on 16 constructed signal-bearing check rows,
correctly localized potential, mu, and beta ablations, and replayed exactly.
Eighteen of 19 check gates passed. The common-mode key-logit error was
`1.9073486e-6`, above the frozen `1e-6` tolerance, so the run parked at
`CML-R0`; synthetic final targets stayed closed and there is no rerun. Runtime
was 6.553 seconds, peak RSS was 398,737,408 bytes, and output was 37,371 bytes.
Every real/public/protected, S20, PhysioNet, network, provider, hardware,
release, and claim counter remained zero. This synthetic result does not
qualify Loop 55.

This queue never authorizes S20 interpretation, PhysioNet acquisition, target
delivery, training, scoring, hardware, release, or a scientific claim by
implication.

## IACKD-H3 - Source-Declared Control Policy

The consumed H2 aggregate showed that the remaining failure is a frozen
taxonomy error, not missing sensor declarations: one stable 26-channel EEG
core, optional M1/M2, three source-typed MISC controls, 1024 Hz, average
reference, and complete central/occipital geometry all reconciled. H3 therefore
freezes source type and source counts first, functional role second, and model
inclusion third. Candidate policy hash
`1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4`
keeps the fixed 26 EEG channels predictive, M1/M2 optional and nonpredictive,
and HEOG/VEOG/Trigger nonpredictive without changing their source MISC bucket.

After the exact H3 research commit is pushed and both CI jobs pass, the next
systematic work item is one standard-library generated-fixture qualification:
29-row and 31-row signatures, BIDS-version count-field mutations, at least 12
refusal classes, one thread and worker, 30 seconds, 256 MiB RSS, and less than
2 MiB output. Network, public or local data, retained-bundle access, signals,
events, trajectories, targets, derivatives, models, scoring, and IACKD-2 stay
at zero.

Research `ed5ce82` is now remotely green in CI `31445790741`, and the bounded
standard-library validator is implemented. It provides generated 29/31-row
fixtures, version-specific MISC count handling, source-before-role
reconciliation, one fixed 26-channel predictive output, five derivative
hashes, 13 mutations covering 12 refusal classes, strict reports, and a
plan/fixture/inspect module CLI with no real executor. Complete local
verification, commit, push, and both green jobs are the next gate; only then
run one measured generated closeout. Every real/public/local data and IACKD-2
counter stays closed.

Exact implementation `8c5784a` passed both jobs in CI `31446902756` before the
measured closeout. One output-parent preflight refused safely before policy or
fixture access. One semantic qualification then passed all 13 gates over 6,093
generated input bytes and 6,834 output bytes in 0.007473916979506612 seconds at
20,250,624-byte peak RSS. Both source-count groups, the fixed 26-channel
predictive core, five derivative hashes, deterministic replay, target
firewall, 13 mutations, and 12 refusal classes passed; every real/public/local
data, signal, target, model, network, and score counter stayed zero. The
temporary report was removed. H3 is complete as generated mechanics evidence;
the next IACKD scientific lane needs a separate prospective contract and Tier
C decision.

## IACKD-2 - Role-Aware Dual Reversal

The separate prospective contract is now frozen. It binds H3's exact
source-type-first policy and fixed 26-channel predictive core, then tests two
opposing transfer directions: congruent-to-incongruent and incongruent-to-
congruent. Both arms must favor measured hand direction over the exact
cue-derived opposite; one arm cannot rescue the other and the participant's
weaker arm margin is primary.

The matrix freezes 11 fits and 15 prediction sets per arm and
participant-hand unit, totaling 660 fits and 900 target-blind prediction sets.
Central, occipital, HEOG/VEOG, EOG-orthogonalized, early/late, pre-window,
timing, no-signal, all-zero, derangement, displacement, channel-permutation,
and opposite-hand conditions are fixed before data.

The future acquisition path no longer requires another retained 7.25 GB
bundle. It must stream the exact 1,340-object identity once, process one
ten-object run group at a time, and remove only invocation-created temporary
raw files after derivative promotion. The committed inventory bounds the
largest group at 82,064,564 bytes. Peak incremental disk is 1 GiB with 10 GiB
free required.

Registration `5bdab30` passed both jobs in CI `31448911258` before Tier B
implementation. The generated-only module now validates the 29/31-row
source-semantics variants, causal dimensions, strict model/scorer firewall,
660 fits, 900 prediction sets, exact replay, prediction freeze, and all six
routes. The first push `25a5692` failed only Linux test portability and did not
open the closeout. Correction `af7488a` passed both jobs in CI `31451262840`
before the one registered generated closeout. All 15 gates passed in 5.024801
seconds at 257,130,496-byte peak RSS with 30,170 output bytes; the full matrix
replayed exactly, every forbidden counter stayed zero, and the temporary report
was removed. Synthetic `IACKD2-R5` is a constructed interface check with no
scientific value. The generated closeout is consumed with no rerun.

The separate all-false Tier C request is now prepared. It binds one fresh
1,340-object stream, 128 one-at-a-time run groups, one private derivative
build, 660 fits, 900 target-blind predictions, one remotely green freeze, one
target delivery, one score, zero retries, and zero reruns. Every authorization
flag and current real-operation counter remains false.

Next: verify, commit, push, and obtain both green CI jobs for the exact packet.
Only then identify it as the sole Tier C gate. Public payload, the old bundle,
real signals, targets, training, prediction, scoring, and scientific claims
remain closed until a fresh later packet-bound decision and subsequent green
implementation and freeze gates.

That sequence has advanced through the implementation gate. Request `862141f`
passed both jobs in CI `31454131606`; the fresh maintainer word `continue` was
recorded in a separate decision, and decision `2ce87fa` passed both jobs in CI
`31456317734` before implementation. The generated-qualified real executor now
covers the exact fresh stream, source semantics, geometry, causal derivatives,
target firewall, 660 fits, 900 predictions, aggregate freeze, and isolated
scorer. All 26 focused tests, 1,929 base tests, and 1,985 optional-neuro tests
pass. Its final fixture run passed 15/15 gates in 5.60445004189387 seconds at
270,745,600-byte peak RSS with 4,523 output bytes and zero public/real/old-
bundle operations.

The next systematic work item is exact implementation proof: commit, push,
and require both CI jobs green. Only then execute the single fresh 1,340-object
stream. Commit its aggregate receipt, run the target-blind matrix once, commit
and remotely green the aggregate freeze, deliver both target views together
once, score once, and stop. The synthetic `IACKD2-R5` route is not evidence of
a neural effect.

The exact implementation became green at `dab5dd4` in CI `31461818620`, then
the one stream consumed and parked at `IACKD2-F08` before any body read. The
first dataset-description response passed status and final URL but did not
satisfy the exact registered `Content-Length` value of 1,178 bytes. The actual
header was not retained. No metadata body, selected object, signal,
trajectory, target, derivative, model, freeze, delivery, or score was reached.

The IACKD-2 analysis and score steps are now unreachable, not pending. Do not
rerun or amend this lane. The next systematic work item is Tier A design of a
separately named transport-stable metadata contract that keeps bounded body
bytes and SHA-256 authoritative while recording `Content-Length` as
non-authoritative transport evidence. Any public execution remains a new Tier
C gate.

That Tier A design is now frozen as `IACKD-T1 Transport-Stable Recovery`.
Small metadata acceptance is based on exact observed bytes plus registered
SHA-256 after one cap-plus-one read; fixed-length, chunked, and clean close-
delimited framing are permitted and recorded. Large payloads retain exact
length and ETag plus full-stream SHA-256, and the entire IACKD-2 scientific
protocol remains unchanged. Registration `ee0f62a` passed both jobs in CI
`31472269070` before a zero-network standard-library validator was built. The
module has no URL opener or real execute path. Its final generated closeout
passed 10 acceptance validations and all 22 refusals with deterministic replay,
5,540 output bytes, 0.001049624988809228-second runtime, 20,332,544-byte peak
RSS, and zero real/public/model operations. The next systematic item is exact
implementation commit, push, and both green jobs, followed by an all-false
Tier C request. No public request, real executor integration, local IACKD path,
model, target, or score is authorized.
