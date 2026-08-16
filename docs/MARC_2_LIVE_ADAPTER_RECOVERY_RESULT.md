# MARC2-LA2 Live Adapter Recovery Result

Date: 2026-08-16

Lane: `MARC2-LA2`

Status: **Consumed and parked at `MARC2LAR-F02`; no retry or rerun**

Result registry:
`registries/marc2_live_adapter_recovery_failure_result.v0.json`

## Required Order

The one private structural execution did not begin until exact executor commit
`5390e068bff24beaf878ac1facff7708c5449249` was pushed and passed Base
Python job `95146470514`, Optional Neuro Readers job `95146470539`, and CI
`31939483560`.

The preconsumption machine gate observed 168,321,097,728 free bytes, 12 logical
CPUs, one-minute load `1.79345703125`, normalized load
`0.14945475260416666`, and 26,902,528-byte peak RSS. It passed before the new
consumed marker was written.

## What Ran

The executor performed exactly the registered structural sequence:

1. verified the decision, native LA2 registry, distinct FW1B certificate,
   exact clean implementation commit, ancestry, CI, and job identities;
2. checked three fixed private path components and the final file identity;
3. created one new v2 output root and one consumed marker;
4. opened the retained structural manifest once with no-follow semantics;
5. read exactly 418,755 bytes once, computed one SHA-256, and performed one
   strict duplicate-key-controlled JSON parse; and
6. delivered that parsed structural object to LA1.

LA1 refused the source. The executor routed `MARC2LAR-F02` at stage
`live_adapter_and_frozen_selector` and stopped. Its aggregate-safe reason is:

```text
LA1 adapter refused source
```

The nested LA1 predicate was intentionally not retained. It is therefore
unavailable, and this result does not infer whether the refusal came from a
top-level field, source identity, transport digest, entry schema, run inventory,
or another frozen LA1 condition. Determining that from the retained manifest
would require a forbidden reinspection or rerun.

## Selection Result

No LA1 success was recorded and the selector was never called.

| Structural result | Value |
|---|---:|
| selected subjects | 0 |
| selected run bundles | 0 |
| selected core members | 0 |
| selected reservation bytes | 0 |
| private selection manifests | 0 |
| archive members opened | 0 |
| archive payload bytes | 0 |

The prior generated 16-subject prefix was interface evidence only. It did not
become a real selection.

## Measurements

```text
route:                              MARC2LAR-F02
registered input bytes:             418,755
content opens/reads/hashes/parses:   1 / 1 / 1 / 1
runtime seconds:                    0.06782554200617597
peak RSS bytes:                     29,425,664
CPU threads/workers/jobs:           1 / 1 / 1
raw-data reads:                     0
real-cache reads:                   0
model runs:                         0
training runs:                      0
producer causal status:             not applicable, metadata only
end-to-end latency measured:        no
aggregate receipt bytes observed:   5,695
aggregate receipt SHA-256:          22900982d87a5d6565da2734011358fc6ef137cfc2fc002ddc9c4cb26c7a9f90
receipt-reported output bytes:       6,096
```

The 401-byte difference between the receipt's internal output measurement and
the final aggregate file size is preserved as an engineering discrepancy. The
consumed marker was not inspected, so total invocation-created bytes are
unavailable. Both observed values remain far below the 2 MiB output and 4 MiB
incremental-disk ceilings.

## Zero Operations

The aggregate receipt records zero archive local-header or member-payload
reads, signal samples, events, targets, labels, quality values, channels,
derivative rows, model fits, inference, predictions, freezes, target delivery,
scores, network traffic, provider or language-model calls, hardware actions,
retries, reruns, resumes, cross-project operations, and scientific claim
upgrades.

## Disposition

`MARC2-LA2` is consumed. Do not rerun, resume, repair, relax, substitute, rename,
delete, or inspect its private root, retained manifest, or marker. Do not use
the generated prefix as if it were a real cohort. `MARC2-FW2` remains
ineligible, and all archive, neural, target, model, score, language, release,
and claim work remains closed.

A future diagnosis may use only fixed committed code and aggregate artifacts
under a separately named artifact-only lane. Any new private read requires a
new prospective contract and a separate Tier C decision.

## Boundary

Engineering capability added: the proof-gated executor completed one exact
integrity-checked structural pass and failed closed before selection or archive
access when LA1 rejected the source.

Scientific claim not established: no neural payload, target, prediction, or
score was accessed, so this result establishes no neural effect, decoding
accuracy, language decoding, or thought-to-text capability.
