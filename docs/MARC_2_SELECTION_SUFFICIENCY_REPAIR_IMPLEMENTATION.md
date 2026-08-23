# MARC2-VR38A Selection-Sufficiency Repair Implementation

Date: 2026-08-23

Lane: `MARC2-VR38A`

Status: **Generated qualification passed; remote implementation proof pending**

Machine records:

- `registries/marc2_selection_sufficiency_repair_implementation.v0.json`
- `registries/marc2_selection_sufficiency_repair_result.v0.json`

## Proof Before Implementation

Exact registration `25205b1d2a1033cf3cefcab022c885025ac76928`
passed Base Python job `97270563617`, Optional Neuro Readers job
`97270563773`, and CI `32670514251` before implementation began. The
registration contract is 9,183 bytes with SHA-256
`0ab620ca0e424247899b5ba4e58c3cbd5f670f7c4ee27a241c52d58d075080d5`.

## Implemented Surface

The standard-library module
`src/neurodecodekit/datasets/marc2_selection_sufficiency_repair.py` exposes
only `plan` and `qualify`. It has no private executor, private path constant,
filesystem discovery, write, network, retry, or scientific route.

For each generated source, the implementation:

1. validates the exact live-shaped envelope, every row, normalized run,
   lowercase task token, companion set, and known participant/session taxonomy;
2. projects exact task `reachingandgrasping` before eligibility filtering;
3. filters recognized eligible participant/session pairs without requiring the
   full inventory to equal 195 bundles;
4. preserves the DOI-derived rank, sessions, runs 1-3, four companions,
   source-exact member identity, split, and 8 GiB reservation cap;
5. supports any valid maximal prefix from 12 through 19 participants; and
6. compares the complete selected structural result after removing only the
   whole-source hash binding and recomputing its derived manifest hash.

The implementation calls no VR25A, VR35A, or VR37A public adapter. It reuses
only their generated builders and narrow validation helpers, so the old exact-
195 gate is not reintroduced.

## Measured Qualification

The sole qualification passed all ten cases in canonical and reversed order
across two exact replays. All 40 paths matched the frozen case-to-route map:
G1 appeared 4 times, G2 16, R1 8, R2 8, and R3 4. The 20 accepted paths
shared one full structural selection identity and one source-exact selected-
name identity. Each selected 16 generated participants, 96 run bundles, and
384 core members. No accepted selection contained a run above 3, a non-target
row, or an ineligible row.

All 101 direct refusal probes passed. The run processed 17,674,816 generated
input bytes in 7.651170833967626 seconds at 50,528,256-byte peak RSS. Its
canonical aggregate report was 3,606 bytes and retained output was zero. It
used one CPU thread, one worker, and one numerical job. Raw-data reads, real-
cache reads, model runs, training runs, network calls, new payload bytes,
private operations, VR37P operations, FW2/CIL1 operations, and operations on
other projects were all zero.

## Interpretation And Boundary

VR38A closes the generated engineering question that blocked a terminal cohort
attempt: a larger or differently distributed optional inventory cannot alter
the required scientific selection so long as every selected rank, run,
companion, split, byte fact, and storage boundary remains exact. It does not
state which optional-run topology exists privately.

After this implementation and a proof-only closeout are remotely green, the
next structural request must be terminal: one target-free structural read and
one deterministic selection attempt must either freeze at least 12 people or
park the Freewill/CIL1 lane. Another topology-only discriminator is forbidden.

Engineering capability added: deterministic cohort selection is now proven on
generated sources to be invariant to harmless optional-run drift while staying
fail-closed on every selected-core defect.

Scientific claim not established: no private source, archive member, neural
signal, target, model, prediction, or score was accessed, so this establishes
no neural effect, decoding performance, advantage over a no-signal or
peripheral baseline, language decoding, unseen-person generalization, or live
decoding capability.
