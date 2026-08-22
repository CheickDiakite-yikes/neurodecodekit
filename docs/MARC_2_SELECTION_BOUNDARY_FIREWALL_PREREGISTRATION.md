# MARC2-VR25A Selection-Boundary Firewall Preregistration

Date: 2026-08-22

Lane: `MARC2-VR25A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_selection_boundary_firewall_contract.v0.json`

## Why This Lane Exists

The sole VR24P invocation passed strict row, path, identity, companion, and
entry-kind validation, then consumed at the exact 238 complete-bundle gate.
The count itself was not retained. Accepting an unknown count globally would
be unsafe, but requiring an exact full-source count is not necessary to prove
that the frozen candidate inventory is complete and isolated.

VR25A freezes a narrower repair. It must validate every source row and every
recognized bundle, classify every bundle against the frozen participant
taxonomy, require the exact 195 eligible participant/session inventory, and
only then quarantine known ineligible bundles. The 238 total becomes an
explicit compatibility status, never a hidden success assumption. Candidate
membership, rank, splits, reservation bytes, and selected member identities
must remain identical across accepted nuisance-count variants.

## Frozen Routes

| Route | Meaning |
|---|---|
| `MARC2VR25A-G1` | exact 238/195/43 generated control accepted |
| `MARC2VR25A-G2` | eligible inventory and selection exact; only known non-selected bundle count differs, with warning |
| `MARC2VR25A-R1` | eligible total or participant/session distribution differs |
| `MARC2VR25A-R2` | recognized bundle belongs to an unknown taxonomy subject |
| `MARC2VR25A-R3` | row, path, task, run, uniqueness, or companion integrity differs |
| `MARC2VR25A-R4` | ineligible firewall, rank, split, reservation, selection, or replay differs |
| `MARC2VR25A-F01` | contract, fixed artifact, or green proof differs |
| `MARC2VR25A-F02` | generated matrix, route, or source immutability differs |
| `MARC2VR25A-F03` | privacy, public output, retention, or forbidden operation differs |
| `MARC2VR25A-F04` | thread, runtime, RSS, input, or output cap differs |

No route may expose a source row, member name, participant, session, run,
count vector, private value, candidate, or selected identity.

## Frozen Generated Matrix

Ten generated 1,227-row cases run in canonical and reversed order across two
exact replays, for 40 paths:

| Case | Mutation | Expected route |
|---|---|---|
| `exact_public_control` | none | `MARC2VR25A-G1` |
| `single_session_exclusion_removed` | replace one complete known-ineligible bundle with four valid auxiliary rows | `MARC2VR25A-G2` |
| `single_session_exclusion_added` | transform four auxiliary rows into one complete known-ineligible bundle | `MARC2VR25A-G2` |
| `sampling_exclusion_removed` | replace one complete sampling-tier bundle with four valid auxiliary rows | `MARC2VR25A-G2` |
| `outside_pair_bundle_added` | transform four auxiliary rows into one complete third-session bundle for a known eligible participant | `MARC2VR25A-G2` |
| `eligible_bundle_removed` | replace one eligible bundle with four auxiliary rows | `MARC2VR25A-R1` |
| `eligible_bundle_added` | transform four auxiliary rows into one additional eligible bundle | `MARC2VR25A-R1` |
| `eligible_distribution_shift` | move one eligible bundle between eligible participant/session cells while preserving 195 total | `MARC2VR25A-R1` |
| `unknown_participant_bundle` | move one complete ineligible bundle to a syntactically valid unknown subject | `MARC2VR25A-R2` |
| `incomplete_companion_set` | replace one companion with one auxiliary row | `MARC2VR25A-R3` |

The five accepted cases must produce one identical semantic selection hash,
source-exact selected-name hash, split, and reservation total. G2 must emit an
aggregate warning flag without the observed full count. The three R1 cases
prove that eligible drift never inherits the nuisance exception.

## Implementation Boundary

After this exact registration is remotely green, Tier B may add one
dependency-free generated-only module with `plan`, `qualify`, and `inspect`
commands. It may reuse immutable VR20A, VR2, VR12A, and selector helpers, but
must not edit or reinterpret them. It must not include `execute`, a generic
path or URL argument, an ignored-path reader, a consumed-state reader, or an
output-root interface.

The implementation must preserve validation order:

1. bind the exact green contract and fixed artifacts;
2. validate the strict 1,227-row source envelope and exact entry-kind counts;
3. validate every row and group complete source-exact companions;
4. classify every recognized bundle against the frozen taxonomy;
5. require exact 195 eligible bundles and exact participant/session counts;
6. quarantine all non-P01 bundles before candidate construction;
7. run unchanged rank, split, reservation, and prefix selection;
8. compare accepted variants for exact semantic selection identity;
9. emit aggregate route, warning, measurements, and unavailable fields only.

## Acceptance Gates

1. All 12 fixed tracked inputs match exact byte size and SHA-256.
2. VR24P result commit `a873f1a2ac796d5616339c7827b11af2a02bc63c`
   and both jobs in CI `32602610854` are bound before implementation.
3. Static analysis binds the exact validation order and the two independent
   full-total versus eligible-inventory predicates.
4. All 40 generated paths produce the frozen route distribution: G1 four,
   G2 sixteen, R1 twelve, R2 four, and R3 four.
5. Every accepted path validates all 1,227 rows, exact 1,025/202 entry kinds,
   every recognized complete bundle, and all known taxonomy memberships.
6. Every accepted path contains exactly 195 eligible bundles with the frozen
   participant/session map.
7. Every accepted path yields the exact same 16-subject, 96-bundle,
   384-member selection, split, and reservation identity.
8. No known ineligible bundle enters candidate, rank, split, reservation, or
   selected output.
9. G2 exposes only `full_source_bundle_count_matches_public: false`; it does
   not expose the observed count or difference.
10. Sources remain byte-identical across every call and exact replay.
11. At least 72 direct contract, route, eligible-firewall, privacy, output,
   replay, and resource mutations refuse.
12. No generated output is retained.
13. One thread, one worker, one numerical job, 60 seconds, less than 256 MiB
   peak RSS, 40 MiB generated input, 2 MiB temporary output, and 1 MiB
   aggregate output are respected.
14. Every private, ignored-path, consumed-state, archive, signal, target,
   model, provider, hardware, FW2/CIL1, retry, release, and claim counter
   remains zero.

## Stop Rules

- If eligible inventory or selection identity changes under any accepted
  ineligible-only mutation, park the lane.
- If an eligible mutation reaches G1 or G2, park the lane.
- If any unknown subject or incomplete group reaches G1 or G2, park the lane.
- If the implementation needs a private count, private path, or a relaxation
  of row/identity/companion validation, park the lane.
- Do not prepare a private packet until the exact generated implementation,
  result, and proof closeout are remotely green.
- A future private confirmation remains a new Tier C action. It could freeze
  a target-free cohort only if every selection-sufficient invariant passes;
  it cannot authorize archive members or neural work by itself.

Engineering capability sought: separate full-source count compatibility from
selection-sufficient cohort integrity while proving that only complete known
non-selected bundle drift can be quarantined without changing the frozen
target-free selection.

Scientific claim not established: generated structural metadata establish no
neural effect, decoding accuracy, language decoding, unseen-person
generalization, live decoding, or thought-to-text capability.
