# MARC2-VR20A Published-Task Selector Repair Implementation

Date: 2026-08-21

Lane: `MARC2-VR20A`

Status: **Generated-only implementation qualified; exact remote proof pending**

Registration proof:

- commit: `cd71807ac68f449796b6bc97745e9a0b200b2cd3`
- CI: `32484725113`
- Base Python: `96778573327`
- Optional Neuro Readers: `96778573092`

## What Was Added

`marc2_published_task_selector_repair.py` is an additive standard-library
adapter over the remotely proven source-envelope, taxonomy, participant-rank,
split, and reservation-cap machinery.

The adapter accepts only the primary-source-published BIDS task token
`reachingandgrasping`. It parses one or more ASCII run digits, normalizes only
the semantic run identity, and requires exact task/run spelling across all
four companions.

To retain earlier row-schema checks, a deep-copied row is projected to the old
validator's vocabulary. That projection is validation-only. Grouping,
selection, reservation accounting, and returned rows always use the original
source object and original member names. Tests require every selected name to
exist byte-for-byte in the input source and require the source object to remain
unchanged.

The module exposes only `plan` and `qualify`. It has no private executor,
archive reader, payload parser, model, scorer, network client, or output writer.

## Qualification

The generated pass covered five valid lexical variants, canonical/reversed
order, and two exact replays: 20 success paths total. All paths selected 16
subjects, 96 run bundles, and 384 core members with one normalized semantic
digest. Five raw-source hashes and five selected-name hashes remained distinct.

The refusal pass completed 53 direct checks covering exact task identity, run
semantics, companion consistency, normalized collisions, subject/session
agreement, paths, row schema, contract substitution, source envelope, thread
limits, output privacy, and resource caps.

Measured qualification:

- fixed input: 232,361 bytes
- generated input: 17,273,948 bytes
- temporary peak: 885,477 bytes
- aggregate output: 3,050 bytes
- retained output: 0 bytes
- runtime: 1.7907995419809595 seconds
- peak RSS: 35,143,680 bytes
- CPU threads/workers/numerical jobs: 1/1/1
- raw-data reads, real-cache reads, model runs, and training runs: 0
- end-to-end latency measured: no

## Boundary

No private or Git-ignored MARC path, consumed VR18P state, archive member,
signal, event, channel, geometry, target, label, cache, model, prediction,
score, provider, device, hardware, or other project was accessed.

The next gate is exact implementation/result remote proof, followed by a
proof-only closeout that repeats no qualification. A private structural
confirmation packet is not yet eligible.

Engineering capability added: the generated selector now recognizes the
dataset's published BIDS task identity while preserving source-exact names and
the existing run, companion, split, provenance, and storage controls.

Scientific claim not established: no real cohort or neural payload was opened,
so this establishes no neural effect, decoding accuracy, language or thought
decoding, real-time behavior, or FW2/CIL1 result.
