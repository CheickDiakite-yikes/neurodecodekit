# MARC2-VR2 Live-Domain Eligibility Adapter Preregistration

Date: 2026-08-16

Lane: `MARC2-VR2`

Status: **Frozen generated-only contract; implementation pending remote-green
registration**

Machine contract:
`registries/marc2_live_domain_eligibility_adapter_contract.v0.json`

## Question

Can NeuroDecodeKit validate an exact live-shaped 1,227-row structural source,
separate source validity from selection eligibility, and preserve the frozen
target-free prefix without assuming how the 43 valid-but-ineligible run bundles
are distributed across exclusion classes?

This is an engineering question over generated structural metadata. It is not
a private-data, neural-signal, or decoding experiment.

## Why VR2 Is Necessary

`MARC2-VR1` fixed the first validation-order defect and passed its full
generated domain. It proved that 238 source-shaped bundles can be validated,
classified, filtered to 195 eligible bundles, and selected without leakage.

VR1 deliberately used one constructed adversary assignment:

```text
single-session exclusion: 12 bundles
sampling-tier exclusion:  24 bundles
extra session:              7 bundles
total ineligible:          43 bundles
```

That assignment is a test fixture, not a recovered private or published run
map. Requiring those exact 43 identities in a future live adapter would replace
the old global-count bug with a new synthetic-layout assumption.

VR2 removes that assumption prospectively. It freezes the source taxonomy and
eligible inventory that are public and already committed, while allowing the
three ineligible predicate counts to vary as long as every source row is valid,
every run bundle is complete, all participants are known, the full source has
238 bundles, the exact eligible subset has 195 bundles, and the other 43 are
unambiguously ineligible.

## Green Inputs

VR2 binds the remotely green VR1 closeout:

```text
proof addendum commit: f70d54923c5a0443ee179d6d580aafde94250589
CI run:               31944164607
Base Python job:      95157571747
Optional Neuro job:  95157571692
VR1 route:            MARC2VR-G1
```

It also binds the public Figshare inventory result, frozen selector contract,
consumed LA2 aggregate result, and VL1 diagnosis. No private or Git-ignored
artifact is an input to this registration.

## Live-Shaped Generated Source

Every success profile uses the exact private-manifest envelope shape without
using private bytes:

```text
schema:          neurodecodekit.marc1_central_directory_private_manifest
schema version:  0.1.0
proof posture:   live_archive_private_central_directory_metadata_only
provider:        Figshare
record/version:  28632599 / 1
file ID:         57518986
archive bytes:   13,591,548,048
registered MD5:  3b7c3039c5c9fb6abf1429a830301711
transport keys:  metadata / tail / directory
rows:            1,227
regular files:   1,025
directories:     202
run bundles:     238
```

The generated entries contain only structural test values. No payload, signal,
event, target, label, response, quality, channel, geometry, or human text is
present.

## Frozen Participant Taxonomy

The classifier must use only the frozen public selector taxonomy:

- eligible participants: the exact 19 IDs in the selector contract;
- single-session exclusions: `sub-02` and `sub-17`;
- sampling-tier exclusions: `sub-13` and `sub-15`;
- known participants: the union of those 23 IDs; and
- eligible sessions: only `ses-01` and `ses-02`.

For every complete source-valid bundle, classification is ordered:

1. `MARC2VR2-P01`: eligible participant in `ses-01` or `ses-02`;
2. `MARC2VR2-P02`: participant in the single-session exclusion set;
3. `MARC2VR2-P03`: participant in the sampling-tier exclusion set;
4. `MARC2VR2-P04`: eligible participant in any other session; or
5. refuse an unknown, overlapping, or unclassified participant/session pair.

Classification may not use compressed size, uncompressed size, CRC, offset,
quality, event count, target, outcome, or later technical success.

## Frozen Invariants, Variable Breakdown

The exact live-domain invariants are:

```text
all complete source bundles:          238
eligible session-1/2 bundles:         195
valid ineligible bundles:              43
eligible participant/session counts:  exact frozen public map
```

The individual `P02`, `P03`, and `P04` counts are not frozen for live use. They
must each be nonnegative, sum to 43, and cover every noneligible bundle exactly
once. Aggregate counts may be emitted; individual ineligible IDs or rows may
not be emitted by the public adapter report.

## Generated Success Matrix

The implementation must construct four deterministic profiles, each in
canonical and reversed row order:

| Profile | `P02` | `P03` | `P04` | Ineligible total |
|---|---:|---:|---:|---:|
| A | 12 | 24 | 7 | 43 |
| B | 8 | 20 | 15 | 43 |
| C | 16 | 12 | 15 | 43 |
| D | 4 | 4 | 35 | 43 |

Every profile preserves the exact 195 eligible bundle identities and sizes.
Each profile must therefore reproduce:

```text
selected subjects:              16
selected run bundles:           96
selected core members:         384
fit / heldout bundles:      48 / 48
fit-heldout overlap:              0
selected reservation: 8,105,207,776 bytes
selection identity: dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641
ineligible selected bundles:      0
```

Profile-specific full-source hashes may differ. Selection identity, split, and
reservation must not.

## Validation Order

The generated implementation must:

1. Verify this contract and exact green VR1 proof.
2. Validate the exact live envelope and transport provenance.
3. Validate every structural row and safe member path.
4. Group all 238 complete unique four-companion run bundles.
5. Classify all bundles using the frozen participant taxonomy.
6. Assert the full 238-bundle source total.
7. Filter to `P01` eligibility.
8. Assert the exact 195 eligible bundles and per-participant session counts.
9. Assert that the other predicates sum to 43 without freezing their split.
10. Apply VR1's green target-free rank, split, reservation, and prefix
    mechanics.
11. Compare all eight profile/order success paths.
12. Emit only aggregate generated evidence.

No global 195-bundle assertion may occur before classification and filtering.
No generated profile identity may become a live-data requirement.

## Implementation Surface

After this registration is remotely green, one additive standard-library
module may expose only:

```text
plan
qualify
inspect
```

It may expose a public in-memory adapter function for later composition, but it
may not expose `execute`, a path, URL, output root, credential, network client,
archive reader, signal reader, target reader, trainer, predictor, or scorer.

It may import exact public or stable internal mechanics from the remotely green
VR1 module and frozen selector. It must not import, call, modify, copy, or
expose LA2's consumed executor or either consumed output root.

## Refusal Coverage

Generated qualification must exercise at least these classes:

| Route | Meaning |
|---|---|
| `MARC2VR2-F01` | contract, artifact, or green-proof binding differs |
| `MARC2VR2-F02` | live envelope, source identity, transport, or row count differs |
| `MARC2VR2-F03` | member path, ZIP row, BIDS identity, or companion set differs |
| `MARC2VR2-F04` | participant taxonomy, classification, or 238/195/43 arithmetic differs |
| `MARC2VR2-F05` | generated profile identity is frozen into live acceptance |
| `MARC2VR2-F06` | rank, split, reservation, selection, or replay differs |
| `MARC2VR2-F07` | aggregate privacy or forbidden-operation boundary differs |
| `MARC2VR2-F08` | thread, runtime, RSS, input, output, or retention cap differs |
| `MARC2VR2-G1` | all generated live-domain profiles pass |

At least 44 named mutations must cover all eight refusal routes, including an
unknown participant, taxonomy overlap, each profile redistribution, eligible
count drift, ineligible total drift, exact-breakdown overconstraint, prefilter
195 assertion, target leakage, public identity leakage, and resource drift.

## Resource Caps

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
runtime:                                 <= 30 seconds
peak RSS:                               <= 256 MiB
generated input:                         <= 16 MiB
aggregate output:                         <= 2 MiB
retained generated output:                     0
network bytes:                                 0
private or Git-ignored bytes:                  0
```

The base dependency delta is zero.

## Gate After Registration

After this exact registration commit is pushed and both CI jobs are green,
Tier B generated implementation and one measured generated qualification may
proceed autonomously. The exact implementation/result must then be committed,
pushed, and remotely green before an all-false Tier C request for a new private
structural recovery may be prepared.

This registration itself authorizes no path operation, private read, output
root, archive member, payload, neural data, target, model, score, network
operation, LA2 reuse, `MARC2-FW2`, release, or claim upgrade.

## Boundary

Engineering capability sought: accept any source-valid distribution of the 43
known ineligible run bundles while preserving the exact 195-bundle eligible
inventory and frozen target-free prefix.

Scientific claim not established: generated structural metadata cannot
establish neural signal, decoding accuracy, language decoding, thought-to-text,
generalization, real-time performance, portability, or clinical utility.
