# Research Autonomy Charter Activation Decision

Date: 2026-07-15

Status: **Tier A and Tier B authorized after this decision is tested,
committed, pushed, and remotely green; Tier C remains separately gated**

Machine decision: `registries/research_autonomy_charter_decision.v0.json`

Frozen charter snapshot: `docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md`

## Exact User Decision

The maintainer supplied the charter's standing approval sentence verbatim:

> Authorize the NeuroDecodeKit Research Autonomy Charter dated 2026-07-15. I authorize Tier A routine work and Tier B bounded development experiments exactly as written, including autonomous commits, pushes, and CI checks. Tier C irreversible evidence, real-data acquisition, hardware, destructive, release, and scientific-claim actions still require my separate exact permission.

This activates the unchanged charter prospectively. It does not reopen any
consumed evaluation or authorize any Tier C event by implication.

## Bound Charter Snapshot

```text
authorization parent: d49f026fc3eee5f78bca9cf0640cbe73fe8684d8
charter commit:        df9035a74ac3201c1f7dda740e417537044be966
charter SHA-256:       c9381bfc729dfca4aaab03929a6623f23c3cf06eb33fbae5379b0517981dcb64
charter Git blob:      e55d7d88202021280ec70185ce8bb99892ca4a64
charter push CI:       29446791389
charter PR CI:         29446794979
parent push CI:        29458544066
parent PR CI:          29458546300
```

The file retains `DRAFT` in its historical path and retains its original
inactive status text so the approved proposal remains byte-identical. This
separate decision is the activation record.

## Authorized Standing Scope

After this decision commit is remotely green, the co-researcher may proceed
without another permission message for:

- Tier A repository research, documentation, code, tests, validators, schemas,
  synthetic fixtures and experiments, metadata-only dry runs, commits, pushes,
  and CI inspection;
- Tier B bounded development experiments only when the development-only input,
  split, hypotheses, controls, metrics, thresholds, seeds, stop rules,
  resources, and claim ceiling are frozen before execution; and
- measured negative-result retention and honest closeout within the charter's
  resource envelope.

The standing envelope remains one CPU thread, one worker, one numerical job,
at most 1 GiB peak RSS, at most 32 MiB generated per loop, no persistent
background process, no new real-data download, no destructive Git operation,
and no deletion outside this repository. A narrower registered contract wins.

## Tier C Remains Closed By Default

Separate exact permission is still required for new real participant payloads,
sealed or final targets, consumed-evaluation reuse, post-outcome protocol
changes, real-data downloads, cap increases, hardware or live streams,
destructive operations, merge/tag/release/publication actions, and scientific
claim promotion.

The charter itself does not authorize Loop 48 Stage B, RW3, S25, or any other
independently gated operation. The maintainer supplied a separate exact Loop 48
Stage B sentence in the same work session; that sentence must receive its own
authorization-only decision and remote-green gate before implementation.

## Authorization-Only Measurements

```text
protected payload / target reads:                   0 / 0
model inference / training / parameter updates:     0 / 0 / 0
downloads / network payload bytes:                  0 / 0
stream / device / hardware operations:              0 / 0 / 0
destructive / release / claim-promotion operations: 0 / 0 / 0
generated experiment artifacts:                     0
end-to-end latency measured:                        false
```

## Claim Boundary

**Engineering capability authorized:** routine research engineering and
fully frozen bounded development experiments may advance autonomously through
local verification, coherent commits, pushes, and remote CI.

**Scientific claim not established:** this governance decision is not an
experiment and establishes no neural advantage, decoding accuracy,
sensor-signal dependence, brain-specific origin, unseen-person generalization,
real-time behavior, EEG or portable-device performance, assistive value,
diagnostic value, or clinical utility.
