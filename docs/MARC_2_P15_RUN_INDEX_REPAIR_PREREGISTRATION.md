# MARC2-VR12A P15 Run-Index Repair Preregistration

Date: 2026-08-18

Lane: `MARC2-VR12A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_p15_run_index_repair_contract.v0.json`

## Why This Lane Exists

The consumed VR11P execution reached aggregate route `MARC2VR11P-R2`. Under
the frozen discriminator, that route maps only to F03 predicate class P15:
suffix-bearing BIDS path or filename identity. It does not reveal a member
name, failed value, row, person, selection, or cohort.

Static review found one standards mismatch in the generated selector: its
Freewill core regex requires exactly two digits in `run-[0-9]{2}`. The BIDS
1.11.1 entity specification defines `run-<index>` as a nonnegative integer and
uses unpadded examples such as `run-1`. The EEG filename template also treats
`run-<index>` as an optional numeric entity and BrainVision recordings as an
`.eeg`, `.vhdr`, and `.vmrk` triplet.

Primary references:

- [BIDS 1.11.1 entity table](https://bids-specification.readthedocs.io/en/stable/appendices/entity-table.html)
- [BIDS entities appendix](https://bids-specification.readthedocs.io/en/stable/appendices/entities.html)
- [BIDS EEG file templates](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html)

This mismatch is a prospective repair target, not a claim about the consumed
private value. VR11P remains consumed and must not be reopened.

## Frozen Repair

VR12A is additive. It must not edit a consumed executor or mutate a source
row. Its repaired parser accepts only one or two ASCII digits for the run
entity and converts the token to an integer for logical grouping.

The following invariants remain exact:

1. subject and session directory labels use the frozen two-digit Freewill
   domain and must match the filename entities exactly;
2. the task token is exactly lowercase `task-freewill`;
3. only the four registered suffixes are core companions;
4. every logical run has exactly one `.eeg`, `.vhdr`, `.vmrk`, and
   `_events.tsv` member;
5. all four companions in one logical run use the same lexical run token;
6. `run-1` and `run-01` map to the same semantic run and cannot coexist as
   duplicate logical companions;
7. public `238 -> 195 + 43` bundle arithmetic, published participant-session
   counts, deterministic rank, fit session 1, held-out session 2, first-three
   runs, and the 8 GiB reservation cap remain unchanged;
8. selected member names and reservation accounting remain source-exact; and
9. no path, row, private identity, target, signal, or outcome is emitted by
   the generated qualification.

The repair intentionally does not broaden subject labels, session labels,
task spelling, suffixes, entity order, path prefixes, or run indices beyond
two source digits. A later standards extension would require another frozen
contract.

## Generated Matrix

After this registration is committed, pushed, and both CI jobs are green, one
dependency-free implementation may exercise the exact 1,227-row generated
source in canonical and reversed order with two exact replays.

Success variants:

| Variant | Run spelling | Required outcome |
|---|---|---|
| `padded_control` | all generated indices retain two digits | same semantic selection as the frozen control |
| `unpadded_single_digit` | every run 1 through 9 loses one leading zero | same subjects, splits, runs, and source-exact names |
| `bundle_consistent_mixed_width` | complete bundles deterministically choose padded or unpadded spelling | same semantic selection and no normalized collision |

Required refusal witnesses include subject/path disagreement, session/path
disagreement, nonnumeric run text, a three-digit run token, mixed lexical run
forms within one companion set, duplicate normalized companions, wrong task,
and an incomplete companion set. Existing path, ZIP, row-schema, count, rank,
split, privacy, resource, and output guards remain in force.

## Acceptance Gates

1. All ten committed inputs match exact size and SHA-256.
2. The standards references, version, and narrow one-or-two-digit policy are
   byte-stable.
3. All 12 success paths pass: three variants, two orders, and two replays.
4. Every success path preserves the same selected subject IDs, semantic run
   bundles, fit/held-out split, and selected-core-member count.
5. Source-exact selected names differ where the source spelling differs, and
   each row's reservation bytes replay from that exact name.
6. Raw source hashes differ across distinct spellings while one normalized
   semantic cohort digest remains identical.
7. Every required P15, P16, P18, and P19 witness refuses at its frozen class.
8. A normalized `run-1`/`run-01` collision cannot enter a selection.
9. A companion set with mixed lexical run tokens cannot enter a selection.
10. The source object is byte-identical before and after every pass or refusal.
11. At least 36 direct contract, parser, grouping, privacy, resource, and
    output mutations refuse.
12. No generated output is retained.
13. One thread, one worker, one numerical job, 30 seconds, less than 256 MiB
    peak RSS, 16 MiB generated input, and 1 MiB aggregate output are respected.
14. Every private, archive, neural, target, model, prediction, score, network,
    provider, hardware, FW2/CIL1, other-project, retry, release, and claim
    counter remains zero.

## Stop Rules

- If unpadded and padded sources do not produce the same semantic cohort and
  split identity, park the lane.
- If source-exact member names or reservation bytes are rewritten, park the
  lane.
- If any neighboring P15/P16/P18/P19 refusal is weakened, park the lane.
- Do not open a private or Git-ignored path, inspect a consumed result, or
  infer that the private source used an unpadded run index.
- Do not prepare a Tier C confirmation packet until the exact implementation
  and measured generated result are committed, pushed, and remotely green.

## Claim Boundary

Engineering capability sought: add a standards-aligned, source-preserving
run-index adapter that accepts generated padded and unpadded Freewill bundle
names without weakening identity, companion, split, or storage controls.

Scientific claim not established: artifact-only design and generated ZIP
metadata establish no real cohort, neural effect, decoding accuracy, language
decoding, live decoding, or thought-to-text capability.
