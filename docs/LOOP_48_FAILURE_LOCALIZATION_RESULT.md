# Loop 48 Artifact-Only Failure Localization Result

Date: 2026-07-15

Status: **Complete at the one-shot artifact-only Stage A boundary; consumed;
no rerun authorized**

Machine result: `registries/loop48_failure_localization_result.v0.json`

Result SHA-256:
`dbfb4c7cc6163ff31fa216c1b33e7510a87b0b843ef714754037d37275924659`

## Decision

The frozen eight-class tree selected `F5`,
`model_fit_output_distribution_instability`, from the four exact committed
aggregate JSON artifacts. This is a strong descriptive match to the consumed
output pattern. It is not a causal root cause and it is not new independent
predictive evidence.

Loop 48 Stage A is consumed. Do not run the classifier again, change its
thresholds, select a favorable seed, inspect ignored Loop 26 payloads, reopen
targets, or use this result to justify a larger model.

## Registered Sequence

```text
contract commit:              83309bfc29300c542c7a7a6dc0f193baba28d42e
request commit:               0ffdf47384a35a09e61158921711b033fd62707d
authorization commit:         5bae88092525206b1d3cf3add055c75665943f14
authorization push / PR CI:   29442914090 / 29442916230
implementation commit:        ca21539cb25949650e1b5a79ccba8fa586e88ccf
implementation push / PR CI:  29444008688 / 29444012075
Stage A executions:           1
reruns:                       0
```

Both implementation CI runs were complete and successful before Stage A
opened any registered input. The tracked worktree was clean at the exact
implementation commit. The adjacent user-owned tracker inspection sidecar was
not read, modified, staged, or committed.

## Exact Inputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Loop 26 consumed result | 83,713 | `7577c84eaea7579250b5c1fcdf53234a3d56fdab4640df2edebaee9ae8bd31b4` |
| Loop 26 prediction freeze | 31,271 | `10191558a68a8c646e32c4ab0516f84ee99d127b9e6a2ea277c432c6c28b2348` |
| Loop 26 shared contract | 31,988 | `c4f94b214993973ec4b4ea7e7b27174023dfef227c8dd4d9b912ac48bb98ccce` |
| Loop 25 causal-mechanics result | 8,573 | `5f80c4d282be79aadaf78908c151acd3949e0a754182cf58b27dcca681218ab1` |
| **Total** | **155,545** | four exact verifications passed |

The run read no ignored output, cache member, train or validation array,
target, checkpoint, private prediction, source-test or session-2 payload, S7,
S20, S25, raw FIF/MAT, stream, device, or hardware source.

## Recomputed Evidence

| Measure | Result |
|---|---:|
| Primary condition | `L33-N55-S2601` |
| Primary macro sentence CER | `0.9381765674382471` |
| Train-only no-signal prior CER | `0.7512350583540796` |
| Prior minus candidate margin | `-0.1869415090841675` |
| Primary blank fraction | `0.9934773746432939` |
| Exact validation sentences | `0 / 6` |
| Candidate wins / ties / losses vs prior | `0 / 1 / 5` |
| One-sided exact paired p-value | `1.0` |
| Size-55 blank fractions | `0.993477`, `0.997146`, `0.523848` |
| Size-55 blank-fraction range | `0.4732980024459845` |
| Size-55 seed CERs | `0.938177`, `0.966413`, `0.881506` |
| Size-55 seeds worse than prior | `3 / 3` |
| All-condition blank range | `0.9971463514064411` |
| Blank fraction at least `0.95` | `8 / 18` |
| Blank fraction at most `0.05` | `1 / 18` |
| Prefix groups with range at least `0.25` | `6 / 6` |

The six fixed-prefix blank-fraction ranges were:

```text
8:  0.2751732572360376
16: 0.9910313901345291
24: 0.8573175703220546
32: 0.8695474928658786
44: 0.3318385650224216
55: 0.4732980024459845
```

## Ordered Tree

| Order | Class | Stage A state |
|---:|---|---|
| 1 | `F1` identity or provenance breach | not triggered; all four identities matched |
| 2 | `F2` temporal or CTC infeasibility | unavailable from aggregate artifacts |
| 3 | `F5` model-fit/output-distribution instability | **triggered** |
| 4 | `F3` signal-quality insufficiency | unresolved after higher-priority selection |
| 5 | `F4` preprocessing/temporal mismatch | unresolved after higher-priority selection |
| 6 | `F6` stable but nonseparable representation | unresolved after higher-priority selection |
| 7 | `F7` prior-dominated task regime | unresolved after higher-priority selection |
| 8 | `U0` unresolved | root cause remains unresolved despite `F5` phenotype |

`F5` triggered because all four frozen descriptive checks passed: primary
blank fraction at least `0.95`, at least one unstable fixed-prefix group, all
three size-55 seeds worse than the prior, and zero exact primary sentences.
These checks were deliberately post-outcome sorting rules, not prospective
performance tests.

## Access And Resources

```text
governance JSON reads:                    2
registered aggregate JSON reads:          4
input SHA-256 verifications:               4
aggregate diagnostic reports:              1
ignored output / cache / member reads:      0 / 0 / 0
train or validation array / target reads:   0 / 0
checkpoint / private prediction reads:      0
source-test / session-2 reads:              0 / 0
S7 / S20 / S25 operations:                 0 / 0 / 0
raw FIF/MAT reads:                          0
model inference / training / updates:       0 / 0 / 0
threshold / seed / architecture selection:  0
network calls / downloaded bytes:           0 / 0
language model / NeuroToken runs:           0
RW3 / stream / device / hardware:           0
scientific claim upgrades / reruns:         0 / 0
```

```text
CPU threads / workers:       1 / 1
internal runtime:            0.016568875 sec      (cap: 30 sec)
external wall time:          0.38 sec
internal peak RSS:           23,429,120 bytes     (cap: 268,435,456)
external maximum RSS:        23,560,192 bytes
generated report:            10,643 bytes         (cap: 1,048,576)
end-to-end latency measured: false
```

Every registered resource check passed. The producer-causality field is not
applicable to this artifact analyzer; the upstream source cache remains
offline and noncausal.

## What This Proves

**Engineering capability added:** one dependency-light, hash-bound,
single-thread artifact analyzer can reproduce the frozen aggregate arithmetic,
apply an ordered failure tree, reject protected or plaintext expansion, and
emit one bounded audit report without reopening experiment payloads.

**Scientific or decoding claim not established:** Stage A does not establish a
causal root cause, independent evidence, neural advantage, sensor-signal
dependence, brain-specific origin, decoding improvement, unseen-person
generalization, real-time behavior, EEG performance, portable or home-device
performance, assistive efficacy, diagnostic value, or clinical capability.

## Next Boundary

The separate H1-H6 train-only hypothesis-discrimination map remains design
research. Stage A did not authorize its split, fixture, train-array read,
telemetry, model, training, checkpoint, inference, scoring, or target access.
Any future Stage B must first freeze its own exact train-only data boundary,
measurement inventory, thresholds, stop rules, resource caps, and separate
authorization. S25 remains unopened and final-only.
