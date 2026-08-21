# MARC2-VR20A Published-Task Selector Repair Preregistration

Date: 2026-08-21

Lane: `MARC2-VR20A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_published_task_selector_repair_contract.v0.json`

## Why This Lane Exists

Primary-source research established that the public Freewill archive uses the
raw BIDS task entity `task-reachingandgrasping`, including four-digit run
spellings such as `run-0003`. The inherited selector instead requires
`task-freewill`.

Consumed route `MARC2VR18P-R4` and the remotely proven VR19A audit are
compatible with this public namespace mismatch, but no private row was
reopened. VR20A therefore repairs the exact published identity in generated
data before any new private confirmation can be considered.

## Frozen Repair

VR20A is an additive adapter over unchanged, remotely proven selector and
variable-width artifacts.

1. The only accepted task token is exact lowercase ASCII
   `reachingandgrasping`.
2. `freewill`, case variants, prefixes, suffixes, and alternate task labels
   refuse. Freewill remains the dataset/paradigm name, not the BIDS task
   entity.
3. Run tokens remain one or more ASCII digits and preserve their source-exact
   lexical spelling. Published four-digit runs are mandatory success cases.
4. Canonical run identity is `token.lstrip("0") or "0"`; only semantic runs
   1, 2, and 3 are eligible in this generated selector domain.
5. Every logical run has exactly one `.eeg`, `.vhdr`, `.vmrk`, and
   `_events.tsv` companion using one task token and one lexical run token.
6. Distinct source names that normalize to the same task/run/suffix identity
   refuse.
7. Subject and session directory entities must exactly repeat in each
   filename. Existing entity order, safe-path, row-schema, public inventory,
   taxonomy, and eligibility checks remain closed.
8. Selected rows retain their exact source member names, run spellings,
   metadata, and reservation-byte accounting. No source or selected row is
   rewritten.
9. Participant rank, `ses-01` fit / `ses-02` held-out split, first-three-run
   semantics, and the 8 GiB reservation cap remain unchanged.
10. No generated source or output is retained. The implementation exposes no
    private executor, archive reader, model, scorer, or network client.

## Generated Matrix

Five valid source variants run in canonical and reversed order across two
exact replays, for 20 success paths:

| Variant | Example task/run segment |
|---|---|
| `published_four_digit` | `task-reachingandgrasping_run-0001` |
| `unpadded` | `task-reachingandgrasping_run-1` |
| `two_digit` | `task-reachingandgrasping_run-01` |
| `six_digit` | `task-reachingandgrasping_run-000001` |
| `bundle_consistent_mixed_width` | one frozen width per complete bundle |

Every path must select the same subjects, semantic run bundles, fit/held-out
split, and core-member count. Raw source and selected-name hashes must differ
across distinct lexical spellings while one normalized semantic digest stays
identical. Every selected name must exist byte-for-byte in its input source.

Required refusal witnesses include `task-freewill`, task case drift, alternate
tasks, task prefixes/suffixes, mixed task labels within a companion set, mixed
run spellings, normalized companion collisions, incomplete companions,
subject/session disagreement, unsafe or overlong paths, malformed row schema,
semantic run zero/four, contract substitution, source mutation, and
resource/output overage. At least 50 direct mutations must refuse.

## Acceptance Gates

1. All ten committed inputs match exact size and SHA-256.
2. The primary-source DOI, Figshare version, archive identity, published task
   token, run example, and four suffixes remain exact.
3. All 20 success paths pass and both replays match byte-for-byte.
4. Every success path preserves source-exact names, source-exact run spelling,
   reservation bytes, semantic cohort, split, and storage identity.
5. Distinct lexical source hashes coexist with one semantic digest.
6. Every required task, run, identity, companion, collision, schema, privacy,
   resource, and output witness refuses.
7. Source objects remain byte-identical across success and refusal paths.
8. At least 50 direct refusals pass.
9. No generated source or output is retained.
10. One thread, one worker, one numerical job, 30 seconds, less than 256 MiB
    peak RSS, 32 MiB generated input, 2 MiB temporary output, and 1 MiB
    aggregate output are respected.
11. Every private, consumed-state, archive, neural, target, model, prediction,
    score, network, provider, hardware, FW2/CIL1, other-project, retry,
    release, and claim counter remains zero.

## Stop Rules

- Park if the published task token requires an alias, heuristic, case fold, or
  source-name rewrite.
- Park if a valid source spelling changes cohort, split, rank, reservation, or
  semantic identity.
- Park if a source-exact name is rewritten or a normalized collision passes.
- Do not open or list `.codex_work`, a private source, consumed output, archive
  member, or neural payload.
- Do not prepare a private confirmation packet until the exact generated
  implementation, result, and proof-only closeout are committed, pushed, and
  remotely green.

## Claim Boundary

Engineering capability sought: a source-preserving selector that recognizes
the dataset's published BIDS task identity without weakening run, companion,
split, storage, provenance, or privacy controls.

Scientific claim not established: generated structural qualification proves no
real cohort, neural effect, decoding accuracy, language decoding, live
decoding, or thought-to-text capability.
