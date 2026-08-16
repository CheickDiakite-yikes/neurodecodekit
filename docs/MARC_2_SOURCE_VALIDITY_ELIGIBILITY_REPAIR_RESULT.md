# MARC2-VR1 Source-Validity / Eligibility Repair Result

Date: 2026-08-16

Lane: `MARC2-VR1`

Route: `MARC2VR-G1`

Status: **Generated qualification passed and consumed; no rerun or private
authority**

Contract:
`registries/marc2_source_validity_eligibility_repair_contract.v0.json`

Implementation:
`registries/marc2_source_validity_eligibility_repair_implementation.v0.json`

Result:
`registries/marc2_source_validity_eligibility_repair_result.v0.json`

## Short Answer

The repair worked on its complete generated qualification domain.

NeuroDecodeKit validated all 1,227 generated structural rows and all 238
complete source-shaped run bundles before deciding eligibility. It classified
195 eligible bundles and 43 source-valid but ineligible adversaries, filtered
those adversaries out, and only then applied the exact 195-bundle assertion.

The unchanged target-free selection mechanics reproduced the frozen
16-subject, 96-run, 384-member, 8,105,207,776-byte result. No ineligible bundle
or companion entered the candidate set or selection.

This closes the generated validation blind spot found by `MARC2-VL1`. It does
not establish that a private source will pass, and it is not a neural or
decoding result.

## Green Implementation Barrier

The registered closeout ran only after exact implementation commit
`4d587dfc552f4a034d38444634cb87e22483bc54` passed:

| Required proof | ID | Result |
|---|---:|---|
| CI run | `31943437003` | green |
| Base Python | `95155811373` | green |
| Optional Neuro Readers | `95155811384` | green |

That proof opened one generated in-memory qualification only. It did not open
a private path, archive member, neural payload, target, model, score, network
operation, or `MARC2-FW2`.

## Source-Domain Result

| Predicate | Meaning | Bundles | Companions |
|---|---|---:|---:|
| `MARC2VR-P01` | eligible session-1/2 | 195 | 780 |
| `MARC2VR-P02` | excluded single-session participant | 12 | 48 |
| `MARC2VR-P03` | excluded sampling-tier participant | 24 | 96 |
| `MARC2VR-P04` | extra session | 7 | 28 |
| **total** | complete generated source | **238** | **952** |

The source also retained 73 generic auxiliary regular files and 202 directory
rows, preserving the exact 1,227-row envelope. Canonical and reversed entry
orders produced the same source hash, predicate counts, selection identity,
and byte summary.

All 43 adversaries are deterministic generated values. They do not reveal or
claim the unavailable identities of private archive rows.

## Frozen Selection Replay

```text
eligible subjects:                  19
selected subjects:                  16
selected run bundles:               96
selected core members:             384
fit / heldout run bundles:      48 / 48
fit-heldout overlap:                  0
selected reservation bytes: 8,105,207,776
reservation cap bytes:      8,589,934,592
selection identity SHA-256: dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641
ineligible bundles selected:          0
ineligible companions selected:       0
target, quality, or outcome used:     no
```

These values prove deterministic selection mechanics over generated metadata.
They are not acquired payload bytes, participant outcomes, model outputs, or
scientific measurements.

## Adversarial Result

All 36 registered mutations refused, and every refusal route was exercised:

| Route | Refusals |
|---|---:|
| `MARC2VR-F01` | 1 |
| `MARC2VR-F02` | 10 |
| `MARC2VR-F03` | 16 |
| `MARC2VR-F04` | 3 |
| `MARC2VR-F05` | 3 |
| `MARC2VR-F06` | 1 |
| `MARC2VR-F07` | 1 |
| `MARC2VR-F08` | 1 |

This covers contract drift, source envelope and counts, row and path safety,
companion uniqueness, eligibility leakage, selector drift, public-output
privacy, and resource caps.

## Measured Closeout

One fresh one-thread CLI invocation produced:

```text
route:                           MARC2VR-G1
fixed input artifacts:                   8
fixed input bytes:                 161,159
generated input bytes:             858,844
aggregate output bytes:              4,680
runtime seconds:        0.20698016599635594
peak RSS bytes:                  32,391,168
CPU threads / workers / jobs:         1 / 1 / 1
retained generated output bytes:              0
network bytes:                                0
private or Git-ignored bytes:                 0
raw-data reads / real-cache reads:        0 / 0
model runs / training runs:              0 / 0
producer causal:     not applicable, structural metadata
end-to-end latency measured:                  no
```

The canonical aggregate report was emitted to stdout and deliberately not
retained. Its post-execution SHA-256 is therefore unavailable rather than
reconstructed by rerunning a consumed qualification.

## Verification

Forty-seven registration, behavior, implementation-record, and result-record
tests pass. The complete dependency-free suite passes 3,543 tests with 204
skips. Fresh optional A-M and N-Z processes pass 3,101 tests with 28 skips and
513 tests with seven skips, respectively, for 3,614 optional-enabled tests with
35 skips.

Ruff, compilation, 238 registry parses, CLI help/plan/inspect, tracked hashes,
and diff hygiene pass locally. The closeout commit still requires both remote
CI jobs before the proof record is complete.

## Disposition

`MARC2-VR1` is complete at `MARC2VR-G1`. Its one measured generated closeout is
consumed with no retry or rerun.

LA2 remains consumed. This result does not authorize operating on its private
root, retained manifest, marker, or executor. It also does not authorize a new
private source, archive member, payload, neural value, target, model, score,
network operation, release, or `MARC2-FW2`.

A future private structural attempt requires a separately named prospective
contract, a generated-qualified one-shot executor, an all-false Tier C request,
and a fresh packet-bound maintainer decision after the relevant proofs are
remotely green.

## Boundary

Engineering capability added: NeuroDecodeKit now validates a full generated
238-bundle source domain, separates source validity from selection eligibility,
and preserves the frozen target-free prefix without admitting excluded
bundles.

Scientific claim not established: no private archive, neural payload, target,
prediction, or score was accessed, so this result establishes no neural
effect, decoding accuracy, language decoding, or thought-to-text capability.
