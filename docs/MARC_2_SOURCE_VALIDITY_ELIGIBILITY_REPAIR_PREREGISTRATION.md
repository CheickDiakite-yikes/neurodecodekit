# MARC2-VR1 Source-Validity / Eligibility Repair Preregistration

Date: 2026-08-16

Lane: `MARC2-VR1`

Status: **Frozen generated-only contract; implementation pending remote-green
registration proof**

Contract:
`registries/marc2_source_validity_eligibility_repair_contract.v0.json`

## Why This Lane Exists

The consumed LA2 execution stopped before selection because LA1 rejected the
structural source at its aggregate `F02` class. The later artifact-only
`MARC2-VL1` audit found a concrete certification gap:

- the public source registry binds 23 participants and 238 runs;
- the generated LA1 fixture represented only the 19 eligible participants and
  195 session-1/2 runs;
- 43 published run slots, or 172 required companion rows, were replaced with
  generic auxiliary names; and
- LA1 compared every matched run group with the eligible total of 195 before
  applying participant and session eligibility.

This lane repairs that design prospectively. It does not alter, retry, resume,
or reinterpret LA2.

## Hypothesis

The validator can preserve strict source safety and the frozen selector while
treating these as two different questions:

1. Is each source row structurally valid and safe?
2. Is the resulting complete run bundle eligible for the frozen selection?

The generated qualification passes only if all source-valid bundles are
validated first, valid-but-ineligible bundles are retained in source
provenance but excluded from selection, and the exact 195 eligible bundles are
counted only after filtering.

## Generated Source Domain

The qualification source remains the exact 1,227-row structural envelope:

```text
directory rows:                                  202
regular-file rows:                             1,025
complete Freewill-shaped run bundles:            238
four-companion rows:                              952
generic auxiliary regular-file rows:               73
eligible session-1/2 bundles after filtering:     195
source-valid but ineligible adversary bundles:      43
```

The 43 adversaries are constructed values, not recovered source identities:

| Predicate | Generated participants/sessions | Bundles |
| --- | --- | ---: |
| excluded single-session participant | `sub-02`, `sub-17`; `ses-01`, runs 1-6 | 12 |
| excluded sampling-tier participant | `sub-13`, `sub-15`; `ses-01` and `ses-02`, runs 1-6 | 24 |
| session outside selection pair | seven eligible participants; `ses-03`, run 1 | 7 |
| **Total** | constructed source-valid adversaries | **43** |

Every adversary has exactly `_eeg.eeg`, `_eeg.vhdr`, `_eeg.vmrk`, and
`_events.tsv`. No row contains signal, event content, target, label, response,
channel, geometry, quality, model output, or human text.

This distribution deliberately exercises each known exclusion class. It does
not claim to reproduce the unobserved participant/session assignment of the 43
published slots.

## Validation Order

The implementation must use this order:

1. Verify the generated-only contract and one-thread environment.
2. Validate the complete source envelope, provenance fields, row counts, and
   transport digests.
3. Validate every row's ZIP metadata type and POSIX-relative path safety.
4. Parse every Freewill-shaped row and require one unique four-companion set
   per logical run bundle.
5. Classify each complete bundle with an aggregate-safe predicate code.
6. Filter to the 19 frozen participants and sessions `ses-01` / `ses-02`.
7. Compare only that filtered inventory with the frozen per-subject map and
   exact total of 195.
8. Apply the unchanged participant rank, first-three-run session split,
   reservation formula, contiguous-prefix rule, and 8 GiB cap.
9. Verify canonical and reversed source order replay exactly.
10. Emit only aggregate generated qualification output.

No global 195-bundle assertion may occur before step 6.

## Predicate Codes

The generated implementation must expose only counts for these codes:

- `MARC2VR-P01`: eligible session-1/2 bundle;
- `MARC2VR-P02`: excluded single-session participant bundle;
- `MARC2VR-P03`: excluded sampling-tier participant bundle; and
- `MARC2VR-P04`: session outside the frozen selection pair.

Malformed content uses refusal routes and never receives an eligibility code.
No predicate output may contain a member name, participant ID, local path,
offset, CRC, compressed size, or source row.

## Frozen Success Conditions

Generated route `MARC2VR-G1` requires all of the following:

- 238 complete source-valid bundles and 952 companion rows;
- exact predicate counts `195 / 12 / 24 / 7` for `P01` through `P04`;
- 195 eligible bundles after filtering and the frozen per-subject counts;
- zero ineligible bundle or companion in selection candidates;
- 16 selected subjects, 96 selected bundles, and 384 selected companions;
- 48 fit and 48 held-out bundles with no overlap;
- selected reservation of 8,105,207,776 bytes under the unchanged cap;
- selection identity SHA-256
  `dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641`;
- canonical/reversed replay equality;
- every required mutation refusing at its registered route;
- one thread, one worker, zero network, and zero retained output; and
- every private, archive, neural, target, model, score, FW2, and claim counter
  remaining zero.

## Failure Classes

The generated implementation must fail closed at these aggregate routes:

- `MARC2VR-F01`: contract, source binding, or proof identity differs;
- `MARC2VR-F02`: generated source envelope or count differs;
- `MARC2VR-F03`: row, path, ZIP, or Freewill identity is unsafe;
- `MARC2VR-F04`: duplicate, incomplete, or ambiguous run companions;
- `MARC2VR-F05`: eligibility policy, filtered count, or predicate count differs;
- `MARC2VR-F06`: rank, split, reservation, selection, or replay differs;
- `MARC2VR-F07`: privacy, public-output, or forbidden-operation boundary differs;
  and
- `MARC2VR-F08`: runtime, RSS, thread, output, or cleanup cap differs.

The implementation must exercise every registered mutation using generated
objects only.

## Resource Envelope

```text
CPU threads / workers / numerical jobs:      1 / 1 / 1
runtime cap:                                  30 seconds
peak RSS cap:                            256 MiB
generated input cap:                       8 MiB
generated output cap:                      2 MiB
retained generated output:                     0
network bytes:                                 0
private or Git-ignored bytes:                  0
```

The base install remains dependency-free. The future module may expose only
`plan`, `qualify`, and `inspect`; it may not expose `execute`, a URL, a generic
source path, or a private-root argument.

## Gate After Registration

After this exact registration commit is pushed and both required CI jobs are
green, Tier B generated-only implementation may begin autonomously. The exact
implementation must then be committed, pushed, and remotely green before any
new Tier C packet may even be prepared.

A future private structural read is not authorized here. It would require a
separately named prospective contract, an all-false request, a fresh
packet-bound maintainer decision, and a new one-shot executor. The consumed
LA2 root and every old executor remain forbidden.

## Boundary

Engineering capability sought: validate a complete generated source domain,
separate structural validity from selection eligibility, and preserve the
frozen target-free prefix selection without admitting excluded source rows.

Scientific claim not established: generated metadata mechanics cannot
establish neural signal, decoding accuracy, language decoding, thought-to-text,
generalization, real-time performance, portability, or clinical utility.
