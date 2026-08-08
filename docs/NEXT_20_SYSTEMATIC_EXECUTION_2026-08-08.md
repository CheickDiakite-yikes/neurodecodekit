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
| 3 | Build synthetic physiology/confound fixtures | B | Deterministic motor, timing, ocular, line-noise, dropout, and corruption cases with no target leakage | In Progress: Implementation Awaiting Green |
| 4 | Add classical EEG adapter contracts | B | Optional dependency boundaries, grouped-fit rules, leakage tests, no real execution | Queued |
| 5 | Add a contact-aware ear-channel adapter | B | Synthetic contact/noise/missingness fixtures and exact channel-mask semantics only | Queued |
| 6 | Freeze Loop 54-A decision and qualify parser | A/B then C decision | Recovery-bound exact packet, strict synthetic parser tests, green implementation before real access | Gated |
| 7 | Execute Loop 54-A once | C | One 11,705-byte VHDR open; no sibling resolution; all 18 gates pass | Gated |
| 8 | Acquire tiny PhysioNet motor slice | C | Exactly nine pinned EDF files, 23,248,224 bytes, isolated receipt, no substitutions | Gated |
| 9 | Run grouped public motor positive control | C | Participant/run grouping, fixed classical family, no-signal and corruption controls | Gated |
| 10 | Execute Loop 54-B signal quality | C | Target-blind VHDR+EEG read, every channel retained, no transform, bounded aggregate output | Gated |
| 11 | Execute Loop 54-C trial reconciliation | C | Isolated VMRK+MAT target-bearing stage, no plaintext protected public output | Gated |
| 12 | Close Loop 54-D eligibility ledger | A after C evidence | At least 48 unique performed trials or explicit park; confounds and missing geometry remain visible | Gated |
| 13 | Implement CML-v0 synthetically | B | Exact 4,535-parameter 64-channel reference, causal controls, deterministic replay, no real data | Queued |
| 14 | Freeze measured Loop 55 contract | A then C decision | One <=10,000-parameter family, <=12 fits, fixed controls, resource and target order frozen | Gated |
| 15 | Create opaque grouped trial split | C | Trial-level grouping, no key-window leakage, targets isolated by stage | Gated |
| 16 | Run bounded Loop 55 training/selection | C | One thread, <=45 CPU minutes, <=1 GiB RSS, <=64 MiB output, no post-selection final access | Gated |
| 17 | Freeze final predictions | C evidence order | Hash-only predictions committed, pushed, and remotely green before final targets | Gated |
| 18 | Score Loop 55 once and route | C | Exact paired tests and all controls together; no rerun or post-target tuning | Gated |
| 19 | Produce Loop 56 aggregate verdict | C claim decision | One of five frozen verdict classes; no individual protected payload reopening | Gated |
| 20 | Open parity or reproducibility branch | Evidence dependent | Proceed only from the measured result; otherwise preserve the parked boundary | Gated |

## Current Route

Work orders 1 and 2 are complete. Work order 3 is next because the local audit
found NumPy `2.5.0` and SciPy `1.18.0` ready without adding dependencies. MNE
`1.12.1` exposes the BrainVision reader and ICA, while scikit-learn, pyRiemann,
MOABB, and Braindecode are absent. No broad install is justified before the
synthetic fixture and adapter contracts show exactly what is needed.

Work order 3's fixture-only contract is now frozen in
`registries/synthetic_motor_fixture_contract.v0.json`. Its generator, strict
loader, metadata-only inspector, mutation surface, two CLI commands, and 12
focused tests are implemented locally. The implementation commit must be
pushed and remotely green before one measured synthetic closeout; no generated
array payload will be retained in Git.

This queue never authorizes S20 interpretation, PhysioNet acquisition, target
delivery, training, scoring, hardware, release, or a scientific claim by
implication.
