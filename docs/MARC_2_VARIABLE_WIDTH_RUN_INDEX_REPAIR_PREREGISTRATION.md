# MARC2-VR16A Variable-Width Run-Index Repair Preregistration

Date: 2026-08-21

Lane: `MARC2-VR16A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_variable_width_run_index_repair_contract.v0.json`

## Why This Lane Exists

Consumed VR15P route `MARC2VR15P-R15` localizes the current real structural
blocker only to the run-token width class. VR12A accepts `[0-9]{1,2}`, while
BIDS 1.11.1 permits a nonnegative integer with arbitrary leading zeroes.

The actual private token, filename, path, row, identity, participant,
selection, and cohort are unavailable. VR16A therefore repairs the entire
standards-permitted padding class in generated data rather than tuning to a
hidden value.

## Frozen Repair

VR16A is an additive adapter over unchanged VR12A/VR15A artifacts. It must not
edit or invoke a consumed private executor.

1. The lexical run token matches one or more ASCII digits: `[0-9]+`.
2. The existing 1,024-byte UTF-8 member-name ceiling remains the only width
   resource bound.
3. Canonical numeric identity is `token.lstrip("0") or "0"`.
4. The generated Freewill domain remains exactly semantic runs 1, 2, and 3;
   zero or another semantic value is a domain refusal, not a BIDS syntax claim.
5. Canonical identity is checked before conversion to an integer, preventing a
   large-integer parse from an adversarially padded token.
6. Every logical run requires exactly one `.eeg`, `.vhdr`, `.vmrk`, and
   `_events.tsv` companion with one identical lexical run token.
7. Distinct lexical tokens that normalize to the same logical run cannot
   coexist.
8. Selected member names and reservation accounting remain source-exact.
9. Subject/session agreement, exact lowercase `task-freewill`, suffixes,
   entity order, path prefixes, taxonomy, public counts, deterministic rank,
   session split, first-three-run semantics, and the 8 GiB cap remain exact.
10. No source row is mutated and no generated source or output is retained.

## Generated Matrix

Six success variants run in canonical and reversed order across two exact
replays, for 24 success paths:

| Variant | Example for semantic run 1 |
|---|---|
| `unpadded` | `run-1` |
| `two_digit_control` | `run-01` |
| `three_digit` | `run-001` |
| `six_digit` | `run-000001` |
| `sixty_four_digit` | 63 leading zeroes followed by `1` |
| `bundle_consistent_mixed_width` | each complete bundle chooses one frozen width |

Every variant must preserve the same selected subjects, semantic run bundles,
fit/held-out split, and selected-core-member count. Raw source and source-name
hashes must differ where lexical spellings differ; one normalized semantic
cohort digest must remain identical.

Required refusal witnesses include an empty run token, ASCII sign, decimal
point, Unicode digit, alphabetic token, semantic zero, semantic run 4, mixed
lexical tokens within a companion set, normalized duplicate companions, wrong
task, incomplete companions, overlong member names, mutated row schema, and
output/resource overages. At least 48 direct mutations must refuse.

## Acceptance Gates

1. All eight committed inputs match exact size and SHA-256.
2. BIDS version, primary references, and the variable-width inference remain
   exact.
3. All 24 success paths pass and both replays match byte-for-byte.
4. Every success path preserves semantic cohort, split, and storage identity.
5. Source-exact names and reservation bytes replay without rewriting.
6. Distinct lexical source hashes coexist with one semantic digest.
7. Every required syntax, semantic-domain, companion, collision, schema,
   privacy, resource, and output witness refuses.
8. Source objects remain byte-identical across success and refusal paths.
9. At least 48 direct refusals pass.
10. No generated source or output is retained.
11. One thread, one worker, one numerical job, 30 seconds, less than 256 MiB
    peak RSS, 32 MiB generated input, 2 MiB temporary output, and 1 MiB
    aggregate output are respected.
12. Every private, consumed-state, archive, neural, target, model, prediction,
    score, network, provider, hardware, FW2/CIL1, other-project, retry,
    release, and claim counter remains zero.

## Stop Rules

- Park if any valid width changes semantic cohort, split, rank, or reservation.
- Park if a source-exact name is rewritten or a normalized collision passes.
- Park if subject, session, task, suffix, companion, count, taxonomy, privacy,
  storage, or output guards weaken.
- Do not open or list `.codex_work`, a private source, consumed output, archive
  member, or neural payload.
- Do not prepare a private confirmation packet until exact generated
  implementation and result are committed, pushed, and remotely green.

## Claim Boundary

Engineering capability sought: a standards-aligned, source-preserving adapter
that accepts generated variable-width zero padding without weakening the
dataset's semantic-run, identity, companion, split, or storage controls.

Scientific claim not established: generated structural qualification proves no
real cohort, neural effect, decoding accuracy, language decoding, live
decoding, or thought-to-text capability.
