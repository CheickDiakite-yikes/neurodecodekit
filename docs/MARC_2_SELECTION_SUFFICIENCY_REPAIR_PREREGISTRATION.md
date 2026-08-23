# MARC2-VR38A Selection-Sufficiency Repair Preregistration

Date: 2026-08-23

Status: **Generated-only registration; implementation blocked until this exact
registration is committed, pushed, and both required CI jobs are green.**

Machine contract:

- `registries/marc2_selection_sufficiency_repair_contract.v0.json`

## Decision

Do not execute `MARC2-VR37P`. Its seven frozen routes can classify the topology
of the target-task surplus, but every route freezes zero cohorts and leaves
`MARC2-FW2` and `MARC2-CIL1` closed. The packet remains remotely proven,
unexecuted, unauthorized, and unconsumed.

The next reversible step is `MARC2-VR38A`: prove on generated sources that the
scientific cohort depends on the exact required selection core, not on an
unnecessary equality between the full eligible inventory and the published
total of 195 bundles.

## Research Question

Can one deterministic target-free selector preserve the same participant rank,
first-three fit and held-out runs, source-exact member identities, split, and
storage reservation while safely ignoring additional complete target-task runs
that cannot enter the selected cohort?

This is a selection-sufficiency question, not an attempt to infer the private
surplus topology.

## Frozen Selection Rule

The future generated implementation must:

1. validate the exact source envelope, every row, path grammar, normalized run
   identity, participant taxonomy, task identity, and four-file companion set;
2. project the exact published task `reachingandgrasping` before candidate
   construction;
3. preserve the DOI-derived participant rank and the 8 GiB reservation cap;
4. require runs `1`, `2`, and `3` in both `ses-01` and `ses-02` for every
   participant examined before the maximal prefix stops;
5. select no run above `3`, no non-target task, and no ineligible participant;
6. retain at least 12 and at most 19 participants, six run bundles and 24
   source-exact core members per participant; and
7. fail closed if any selected identity, split, byte fact, companion, rank, or
   reservation differs.

Additional complete runs above `3` are optional inventory. They may be present
or absent only when they cannot change the selected semantic cohort. A global
eligible total above or below the public map is not itself a selection failure.

## Generated Witness Matrix

Ten cases run in canonical and reversed source order with two exact replays,
for 40 required paths:

| Case | Frozen route | Meaning |
|---|---|---|
| public map exact control | `MARC2VR38A-G1` | Baseline exact map selects the frozen cohort. |
| one contiguous optional surplus | `MARC2VR38A-G2` | One complete later run is ignored. |
| one noncontiguous optional surplus | `MARC2VR38A-G2` | One complete later noncontiguous run is ignored. |
| multi-cell optional surplus | `MARC2VR38A-G2` | Later complete runs in multiple cells are ignored. |
| mixed optional surplus and deficit | `MARC2VR38A-G2` | Later optional changes do not alter the required core. |
| required fit run missing | `MARC2VR38A-R1` | A required fit identity is unavailable. |
| required held-out run missing | `MARC2VR38A-R1` | A required held-out identity is unavailable. |
| unknown participant | `MARC2VR38A-R2` | Taxonomy validation refuses. |
| incomplete companion set | `MARC2VR38A-R2` | Source structural validation refuses. |
| fewer than 12 subjects fit the cap | `MARC2VR38A-R3` | The minimum scientific cohort cannot be reserved. |

All 20 accepted paths must share one semantic selection identity after removing
only the whole-source hash field that necessarily differs between generated
witnesses. Within each case, replay output must be byte exact. No accepted row
may contain a run above `3`, a non-target task, an ineligible participant, or a
member absent from the generated source.

At least 80 direct refusal probes must cover contract drift, malformed source
envelopes, duplicate names, normalized-run collisions, missing companions,
unknown taxonomy, selected-run mutation, split overlap, rank drift, storage-cap
changes, output leakage, private-path constants, and forbidden operations.

## Implementation Boundary

After this registration is remotely green, one additive standard-library-only
module may expose only `plan` and `qualify`. It may reuse unchanged generated
builders and selection helpers, but it may not import or call a private
executor, name `.codex_work`, inspect a real or consumed source, access an
archive member, or perform network, neural, target, model, prediction, score,
stream, device, release, or claim operations.

The one generated qualification is limited to one CPU thread, one worker, one
numerical job, 30 seconds, less than 256 MiB peak RSS, 1 MiB generated output,
zero network bytes, zero new payload bytes, and zero retained generated files.

## Terminal Next Gate

If VR38A qualifies and its proof-only closeout becomes remotely green, the next
Tier C request must be terminal for structural selection:

- one target-free 418,755-byte structural read;
- one deterministic selection attempt;
- success freezes a source-bound cohort of at least 12 participants; and
- any failure parks the Freewill/CIL1 lane without another topology-only
  discriminator, retry, rerun, repair, substitution, or private reinspection.

Only a separately authorized and remotely proven terminal packet may perform
that read. `MARC2-FW2`, archive members, neural payloads, targets, models,
predictions, scoring, and scientific claims remain closed now.

Engineering capability proposed: a generated selector can demonstrate that a
scientifically fixed cohort is invariant to harmless optional-run surplus while
remaining fail-closed on every fact that can alter selection.

Scientific claim not established: this registration reads no real or private
data and performs no training, inference, prediction, or scoring; it establishes
no neural effect, no advantage over a no-signal or peripheral baseline, and no
language, unseen-person, or live-decoding result.
