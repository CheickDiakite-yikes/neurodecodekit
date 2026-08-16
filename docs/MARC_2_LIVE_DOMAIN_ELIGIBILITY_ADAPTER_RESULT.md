# MARC2-VR2 Live-Domain Eligibility Adapter Result

Date: 2026-08-16

Lane: `MARC2-VR2`

Route: `MARC2VR2-G1`

Status: **Generated qualification passed and consumed; no rerun or private
authority**

Contract:
`registries/marc2_live_domain_eligibility_adapter_contract.v0.json`

Implementation:
`registries/marc2_live_domain_eligibility_adapter_implementation.v0.json`

Result:
`registries/marc2_live_domain_eligibility_adapter_result.v0.json`

## Short Answer

The live-domain eligibility adapter passed its complete generated
qualification.

NeuroDecodeKit validated eight live-shaped source paths spanning four distinct
valid distributions of the 43 ineligible run bundles and two row orders per
distribution. Every path validated all 1,227 rows and 238 complete bundles,
recovered exactly 195 eligible and 43 ineligible bundles from the frozen public
taxonomy, and reproduced the same target-free 16-subject, 96-run selection.

All 58 registered adversarial mutations refused. The adapter did not receive a
profile identity and did not require the generated `12/24/7` exclusion mix.
This closes VR1's remaining generated overconstraint. It does not establish
that a private source will pass, and it is not a neural or decoding result.

## Green Implementation Barrier

The registered closeout ran only after exact implementation commit
`f62a3f5b9966967c569e734552cbc3f11d009401` passed:

| Required proof | ID | Result |
|---|---:|---|
| CI run | `31946112252` | green |
| Base Python | `95162220059` | green |
| Optional Neuro Readers | `95162220159` | green |

That proof opened one generated in-memory qualification only. It did not open
a private path, consumed root, archive member, payload, neural value, event,
target, model, score, network operation, or `MARC2-FW2`.

## Variable-Domain Result

| Profile | Single-session | Sampling-tier | Extra-session | Row orders | Result |
|---|---:|---:|---:|---:|---|
| A | 12 | 24 | 7 | 2 | pass |
| B | 8 | 20 | 15 | 2 | pass |
| C | 16 | 12 | 15 | 2 | pass |
| D | 4 | 4 | 35 | 2 | pass |

All eight paths agreed on:

```text
source rows:                       1,227
complete source bundles:             238
eligible / ineligible bundles:  195 / 43
eligible subjects:                     19
selected subjects:                     16
selected run bundles:                  96
selected core members:                384
fit / heldout run bundles:        48 / 48
fit-heldout overlap:                     0
selected reservation bytes:  8,105,207,776
reservation cap bytes:       8,589,934,592
selection identity SHA-256:  dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641
ineligible bundles selected:             0
ineligible companions selected:          0
target, quality, or outcome used:        no
```

Canonical and reversed source hashes matched within every profile. Source
hashes were allowed to differ between profiles because their generated
ineligible identities differed. Neither profile identity nor an exact
predicate breakdown is required of a future live source.

## Adversarial Result

All 58 registered mutations refused, and every refusal route was exercised:

| Route | Refusals |
|---|---:|
| `MARC2VR2-F01` | 4 |
| `MARC2VR2-F02` | 13 |
| `MARC2VR2-F03` | 18 |
| `MARC2VR2-F04` | 8 |
| `MARC2VR2-F05` | 2 |
| `MARC2VR2-F06` | 4 |
| `MARC2VR2-F07` | 3 |
| `MARC2VR2-F08` | 6 |

This covers contract drift, source envelope and counts, row/path and companion
safety, unknown or overlapping taxonomy, exact-breakdown overconstraint,
prefilter equality, selection drift, identity leakage, and resource drift.

## Measured Closeout

One fresh one-thread CLI invocation produced:

```text
route:                          MARC2VR2-G1
fixed input artifacts:                   12
fixed input bytes:                  230,072
generated input bytes:            3,435,280
aggregate output bytes:               4,748
runtime seconds:          0.5122641660127556
peak RSS bytes:                   32,620,544
CPU threads / workers / jobs:          1 / 1 / 1
retained generated output bytes:               0
network bytes:                                 0
private or Git-ignored bytes:                  0
raw-data reads / real-cache reads:         0 / 0
model runs / training runs:               0 / 0
producer causal:      not applicable, structural metadata
end-to-end latency measured:                   no
```

The canonical aggregate report was emitted to stdout and deliberately not
retained. Its post-execution SHA-256 is unavailable rather than reconstructed
by rerunning a consumed qualification.

All registered caps passed: 30 seconds, 256 MiB peak RSS, 16 MiB generated
input, 2 MiB aggregate output, zero retained output, zero network bytes, and
zero private or Git-ignored bytes.

## Verification

Forty-three registration, behavior, implementation-record, and result-record
tests pass. The complete dependency-free suite passes 3,586 tests with 204
skips. Fresh optional A-M and N-Z processes pass 3,144 tests with 28 skips and
513 tests with seven skips, respectively, for 3,657 optional-enabled tests with
35 skips.

Ruff, compilation, 241 registry parses, CLI help/plan/inspect, tracked hashes,
and diff hygiene pass locally. The exact result commit and both remote jobs are
pending; this document must receive a separate proof update after remote green.

## Disposition

`MARC2-VR2` is complete locally at `MARC2VR2-G1`. Its one measured generated
closeout is consumed with no retry or rerun.

LA2 remains consumed. This result does not authorize operating on either
consumed root, retained manifest, marker, or executor. It also does not
authorize a new private source, archive member, payload, neural value, event,
target, model, score, network operation, release, or `MARC2-FW2`.

After this exact result record is remotely green, the next safe work is a
separately named generated-qualified one-shot private structural recovery
packet. That packet must be all false until a fresh packet-bound maintainer
decision becomes remotely green. The current `continue to eureka` is not
retroactive Tier C authority.

## Boundary

Engineering capability added: NeuroDecodeKit now validates a live-shaped full
source domain without freezing a synthetic exclusion distribution and
preserves the exact target-free eligible selection across variable valid
ineligible layouts.

Scientific claim not established: no private archive, neural payload, target,
prediction, or score was accessed, so this result establishes no neural
effect, decoding accuracy, language decoding, or thought-to-text capability.
