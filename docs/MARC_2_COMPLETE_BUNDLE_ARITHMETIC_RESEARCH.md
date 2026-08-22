# MARC2-VR25R Complete-Bundle Arithmetic Research

Date: 2026-08-22

Lane: `MARC2-VR25R`

Status: **Tier A public/artifact-only research complete; no private source or
dataset payload operation performed**

## Executive Finding

`MARC2-VR24P` did not find a malformed recognized run bundle. It found a
boundary error in how NeuroDecodeKit combines two different questions:

1. Does the complete archive match a frozen public total of 238 run bundles?
2. Is the exact 195-bundle candidate inventory needed for the bounded study
   complete, structurally valid, and unchanged?

The current adapter makes both questions one hard gate. That is stricter than
the scientific selection requires. A difference confined to complete bundles
from already excluded participants or sessions cannot alter the eligible
candidate set, split, or reservation. A difference involving any eligible
bundle can alter them and must still refuse.

The safe repair is therefore not "accept any count." It is a layered
selection-boundary firewall: validate every row and complete companion group,
classify every recognized group, require the exact published eligible
participant/session inventory, quarantine every known ineligible group before
selection, and preserve the old 238 total only as a compatibility warning.

## What R2 Proves

The frozen VR23A decision tree evaluates the relevant conditions in this
order:

1. strict source envelope;
2. row fields, normalized paths, and suffix-bearing identity;
3. unique member names;
4. consistent task and run spelling within a logical bundle;
5. exactly one `.eeg`, `.vhdr`, `.vmrk`, and `_events.tsv` companion;
6. exact 1,025 regular-file and 202 directory counts; and
7. exact 238 recognized complete bundles.

The sole private pass returned `MARC2VR24P-R2`. Therefore the preceding
conditions passed for that execution and only step 7 differed. The observed
bundle count and the direction or magnitude of the difference were not
retained and must not be inferred.

If `B` is the unavailable recognized complete-bundle count, then the validated
structure implies:

```text
recognized companion rows = 4 * B
other regular-file rows    = 1,025 - 4 * B
```

That algebra does not reveal `B`. It does show that the discrepancy is a
partition/count issue after companion completeness, not evidence that a
recognized bundle is partial.

## Public Source Boundary

The official Scientific Data descriptor reports 23 participants, 49 recording
days, 6,808 trials, and a variable three-to-seven runs per session. It also
publishes the exact raw BIDS identity
`task-reachingandgrasping_run-zzzz` and the four raw companions used by the
adapter. The repository's frozen 238 total is an aggregate public-source
invariant derived in earlier work; it is not a substitute for validating the
eligible participant/session map.

Primary source:
[Scientific Data descriptor](https://www.nature.com/articles/s41597-025-06039-9)

The public central-directory result independently binds the exact current
archive envelope at 1,227 entries: 1,025 regular files and 202 directories. It
did not publish member names or a bundle count.

## Selection-Sufficient Invariants

A future generated-only adapter may treat the 238 total as non-blocking only
if all of these remain hard gates:

1. exact source identity, transport hash, row count, and entry-kind counts;
2. strict validation of every row, including safe normalized paths and ZIP
   declarations;
3. unique names and complete four-companion recognized bundles;
4. exact lowercase `task-reachingandgrasping` and source-exact run spelling;
5. every recognized participant in the frozen public taxonomy;
6. exactly 195 eligible bundles with the exact frozen participant/session
   distribution;
7. no ineligible bundle entering rank, split, reservation, or selection;
8. exact 16-subject, 96-bundle, 384-member target-free selection replay;
9. source immutability, deterministic order/replay, and aggregate-only output;
10. an explicit warning whenever the full recognized-bundle total is not 238.

This design deliberately refuses an eligible bundle being added, removed, or
moved even when the full count remains constant. It also refuses unknown
participants and incomplete companions. Only complete bundles already outside
the candidate taxonomy may vary without changing selection.

## Why This Moves The Program

The current blocker is no longer an unknown parser failure. It is a brittle
global aggregate placed before a stronger selection-specific invariant. The
new boundary can be tested entirely with generated manifests before any
future private confirmation. If it passes, a separately authorized one-shot
confirmation could either freeze the real cohort or stop at a new aggregate
class without weakening row, identity, eligibility, split, or storage guards.

## Boundary

Engineering insight established: complete-source snapshot compatibility and
selection-sufficient cohort integrity can be validated separately without
allowing excluded source structure into the candidate set.

Scientific claim not established: no archive member, neural signal, event,
target, model, prediction, or score was accessed, so this research establishes
no neural effect, decoding performance, unseen-person generalization, live
decoding, or thought-to-text capability.
