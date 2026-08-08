# Classical EEG Adapter Plan Result

Status: **work order 4 complete; one measured symbolic roundtrip consumed**

Date: 2026-08-08

Result registry:
`registries/classical_eeg_adapter_result.v0.json`

## Order Of Evidence

The three-adapter contract was committed at `ea5fafda3e408972797e579f00d786ab6c8ee6bc`
and passed push CI `31279856066`. The implementation was committed at
`eefb7b066810c2a6b87417b105bdb746218e87dc` and passed exact-SHA push CI
`31280581308` before the measured roundtrip began. Base Python passed in 16
seconds and Optional Neuro Readers passed in 57 seconds.

Exactly one symbolic plan creation and one inspection then ran in an
automatically removed temporary directory. No retry or post-result tuning
occurred. The plan was hashed and measured before removal; it is not retained
in Git or elsewhere in the workspace.

## Measured Result

| Field | Result | Cap |
|---|---:|---:|
| Runtime | 0.12 seconds | 15 seconds |
| Peak RSS | 22,822,912 bytes | 268,435,456 bytes |
| Input contract | 12,025 bytes | recorded |
| Generated plan | 27,335 bytes | 1,048,576 bytes |
| Retained generated plans | 0 | 0 in Git |

The serialized plan SHA-256 was
`680f95e41ea2e4b7b2bcec0961d493c9bc2889294f0652dabc120db79f6ecb2d`.
Its canonical content hash, excluding only the self-referential hash field,
was `66800348e76d03b9b994a460b2e78fbe569c450fdb289be5948cecbcea860bf1`.

The plan contained 96 target-free symbolic items in 48 pair-bound groups:
48 train items in 24 groups, 32 check items in 16 groups, and 16 final items
in 8 groups. Creation and inspection returned zero and emitted equal compact
summaries. No adapter winner was selected.

The registered families remain low-frequency shrinkage LDA, causal 8-30 Hz
CSP-LDA, and regularized Riemannian MDM. Their fit stages are restricted to
train groups or data-independent configuration. Check and final targets remain
unavailable to fit or transformation. The plan requires zero right-context and
zero post-event samples, but no causal producer was executed and end-to-end
latency was not measured.

## Access Ledger

One symbolic plan build and one symbolic inspection occurred. Adapter backend
imports, optional dependency installations, array reads, raw or protected data
reads, public EEG reads, target or label-value reads, feature extraction,
parameter updates, inference, training, scoring or selection, network or
provider calls, stream/device/hardware operations, and scientific-claim
upgrades were all zero.

The deterministic replay, exact hash binding, pair/group isolation, train-only
fit firewall, all twelve malformed-plan refusals, bounded read, exclusive
create, collision refusal, standard-library-only import, and CLI equality gates
passed. Closeout verification passes 39 focused checks and the complete suite
at 1,279 tests, 3 expected skips, and 469 subtests. Ruff, compileall, all
registry JSON, root and command help, and diff hygiene also pass.

Warnings remain explicit:

- this is a symbolic interface plan, not EEG feature extraction;
- no classical adapter was selected or executed;
- synthetic identities are leakage-test surrogates, not participant evidence;
- causal fields constrain future work but do not measure a producer or latency;
  and
- public or protected adapter execution remains a separately gated Tier C
  action.

## Verdict And Route

All 18 acceptance gates passed. Work order 4 is complete and consumed without
retaining generated output. Work order 5 may now freeze and synthetically test
contact-mask, channel-noise, and missing-channel semantics for an ear-channel
adapter. That route authorizes no hardware, real data, model fit, inference, or
scientific scoring.

Engineering capability added: NeuroDecodeKit can deterministically construct,
hash, save, inspect, and fail closed on leakage in three optional classical EEG
adapter plans.

Scientific claim not established: no EEG adapter was executed and no real
neural effect, decoding accuracy, generalization, latency, device performance,
home use, or clinical result was established.
