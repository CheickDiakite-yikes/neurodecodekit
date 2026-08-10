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
| 9 | Run grouped public motor positive control | C | Participant/run grouping, prediction + physiology + confound conjunction, remotely green prediction freeze | Gated; Implementation Qualified Locally; Execution Pending Remote Green |
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
Work order 9 has now advanced through its own green authorization and local
generated-fixture implementation, but real execution remains closed until the
exact implementation commit is pushed and remotely green.

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
work order 9 is locally qualified but its real execution remains gated. A
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
router output has no claim value. No local PhysioNet path, private receipt, EDF,
real target, or real model operation has begun. The exact implementation must
now be committed, pushed, and remotely green before the one real execution.

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
