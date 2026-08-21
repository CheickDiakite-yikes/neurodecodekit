# MARC2-VR15A Suffix-Identity Grammar Decomposition Preregistration

Date: 2026-08-21

Lane: `MARC2-VR15A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_suffix_identity_grammar_decomposition_contract.v0.json`

## Why This Lane Exists

The sole VR14P aggregate recovery consumed at `MARC2VR13P-R2`. Under the
frozen VR13P route table, that result means only that the unchanged VR12A
adapter reached its P15 suffix-bearing BIDS identity refusal. It does not
reveal a failed value, predicate, row, path, identity, person, run, task,
selection, or cohort.

P15 is still broad because one regular-file member can preserve a required
EEG/events suffix while failing anywhere inside the repaired path and filename
grammar. This lane decomposes that grammar using committed code and generated
full-scale manifests only. It does not inspect VR14P output or any private or
Git-ignored path.

## Frozen Ordered Classes

The classifier evaluates normalized suffix-bearing names in this exact order:

| Route | Frozen class |
|---|---|
| `MARC2VR15A-R1` | fewer than four terminal path components |
| `MARC2VR15A-R2` | invalid root-prefix segment grammar |
| `MARC2VR15A-R3` | subject-directory entity shape |
| `MARC2VR15A-R4` | session-directory entity shape |
| `MARC2VR15A-R5` | modality directory is not exact `eeg` |
| `MARC2VR15A-R6` | filename subject-entity shape |
| `MARC2VR15A-R7` | path/filename subject disagreement |
| `MARC2VR15A-R8` | filename session-entity shape |
| `MARC2VR15A-R9` | path/filename session disagreement |
| `MARC2VR15A-R10` | task-entity shape |
| `MARC2VR15A-R11` | optional pre-run entity shape |
| `MARC2VR15A-R12` | run entity absent |
| `MARC2VR15A-R13` | run entity present but not terminal |
| `MARC2VR15A-R14` | run token is not ASCII numeric |
| `MARC2VR15A-R15` | run token is outside the frozen one/two-digit width |
| `MARC2VR15A-R16` | more than one distinct suffix-identity class is present |

`MARC2VR15A-G1` is reserved for the unchanged generated control that passes
VR12A. The ordered classes are a diagnostic grammar, not a claim about the
consumed private source.

## Generated Matrix

One generated control and one generated witness for each R1-R15 class run in
canonical and reversed row order across two exact replays. A seventeenth case
combines two distinct witnesses and must deterministically return R16. Every
path calls the unchanged `vr12a.adapt_repaired_source` exactly once.

All 16 single-failure witnesses must reach exact VR12A route
`MARC2VR12A-F03` with reason `P15 suffix-bearing BIDS identity differs` before
the new classifier emits its aggregate route. The control must pass VR12A.
Each aggregate route must appear exactly four times across 68 total paths.

The classifier may scan only the generated in-memory manifest supplied by the
test harness. It emits route counts, deterministic digests, resources,
warnings, and zero operation counters. It must never emit a member name, path,
subject, session, run, task, row, source identity, candidate, or selection.

## Acceptance Gates

1. All 11 fixed tracked inputs match 215,394 bytes and their SHA-256 hashes.
2. Static source analysis binds the exact repaired core regex and P15 guard.
3. The 15 single classes and one multiple-class route are ordered and unique.
4. All 68 generated paths call unchanged VR12A exactly once.
5. Every single witness reaches exact VR12A F03/P15 before classification.
6. G1 and R1-R16 each appear exactly four times.
7. Canonical/reversed order and both complete replays agree.
8. Every generated source is byte-identical before and after validation.
9. At least 70 direct contract, grammar, route, privacy, determinism,
   resource, and output mutations refuse.
10. No generated output is retained.
11. Runtime stays below 30 seconds, peak RSS below 256 MiB, generated input
    below 32 MiB, and aggregate output below 1 MiB using one thread, worker,
    and numerical job.
12. Every private, ignored-path, source, archive, neural, target, model,
    prediction, score, network, provider, hardware, FW2/CIL1, retry, release,
    and claim counter remains zero.

## Stop Rules

- Park if a generated witness reaches a non-P15 VR12A route.
- Park if route output changes with row order or replay.
- Park if the classifier cannot assign exactly one ordered class or the
  explicit multiple-class route.
- Do not modify VR12A or a consumed executor.
- Do not inspect VR13P/VR14P ignored state or any private source.
- A future private discriminator remains a separately frozen Tier C packet and
  fresh packet-bound decision.

Engineering capability sought: convert the broad P15 aggregate failure into a
deterministic, privacy-preserving grammar diagnosis using only generated
manifests and the unchanged repaired adapter.

Scientific claim not established: artifact-only code analysis and generated
structural manifests establish no neural effect, decoding accuracy, language
decoding, live decoding, or thought-to-text capability.
