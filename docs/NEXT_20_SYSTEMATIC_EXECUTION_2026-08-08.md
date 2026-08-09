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
| 8 | Acquire tiny PhysioNet motor slice | C | Exactly nine pinned EDF files, 23,248,224 bytes, isolated receipt, no substitutions | Gated |
| 9 | Run grouped public motor positive control | C | Participant/run grouping, fixed classical family, no-signal and corruption controls | Gated |
| 10 | Execute Loop 54-B signal quality | C | Target-blind VHDR+EEG read, every channel retained, no transform, bounded aggregate output | Gated |
| 11 | Execute Loop 54-C trial reconciliation | C | Isolated VMRK+MAT target-bearing stage, no plaintext protected public output | Gated |
| 12 | Close Loop 54-D eligibility ledger | A after C evidence | At least 48 unique performed trials or explicit park; confounds and missing geometry remain visible | Gated |
| 13 | Implement CML-v0 synthetically | B | Exact 4,535-parameter 64-channel reference, causal controls, deterministic replay, no real data | Contract Frozen; Implementation Qualified Locally; Execution Pending Remote Green |
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
no rerun, and work orders 10-12 remain blocked. Work order 8 remains a separate
gated Tier C acquisition and is not opened by this result.

Work order 13 now has a frozen Tier B synthetic-only contract in
`docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_PREREGISTRATION.md` and
`registries/causal_motor_lattice_synthetic_contract.v0.json`. It binds the
existing seed-5503 synthetic fixture to a new seed-5513 experiment, exact
pair-anchored pre-event crops, fixed 64-channel projection and causal FIR
hashes, one 4,535-parameter model, one 600-step fit, check-before-final gates,
no rerun, and a 4 MiB output cap. Contract commit `67709a3` passed exact push CI
`31294479865` before implementation. The import-light model, execution shell,
dry-run CLI, inspector, and adversarial tests are now qualified locally with
zero registered training, scoring, or retained output. The one measured run
cannot start until this exact implementation is committed, pushed, and
remotely green. The contract opens no real or public data and does not qualify
Loop 55.

This queue never authorizes S20 interpretation, PhysioNet acquisition, target
delivery, training, scoring, hardware, release, or a scientific claim by
implication.
