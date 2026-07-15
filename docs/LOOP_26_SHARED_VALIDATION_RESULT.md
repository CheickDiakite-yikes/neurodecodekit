# Loop 26/31/33 Shared S21 Validation Result

**Status:** Parked; registered gate failed  
**Scoring date:** 2026-07-15  
**Scoring event:** consumed; no rerun or post-target tuning is authorized  
**Public result:** `registries/loop26_shared_validation_result.v0.json`  
**Public result SHA-256:** `7577c84eaea7579250b5c1fcdf53234a3d56fdab4640df2edebaee9ae8bd31b4`

## Plain-language result

The engineering protocol worked as designed, but the scientific gate did not.
The fixed 2,908-parameter causal candidate produced a macro sentence CER of
`0.938177` on the six reserved S21 session-1 validation sentences. The
train-only no-signal prior produced `0.751235`, so the candidate was worse by
`0.186942` absolute macro CER instead of meeting the registered requirement to
be better by at least `0.05`.

This is a useful negative result. It says that this exact small model, source
slice, causal producer, training schedule, and decoding rule do not justify a
neural-advantage claim or a larger-model escalation. The correct action is to
park Loops 26, 31, and 33 and move only to a separately bounded, artifact-first
Loop 48 failure-localization design.

## Registered primary comparison

| Measure | Fixed candidate | Train-only prior | Gate interpretation |
|---|---:|---:|---|
| Macro sentence CER | `0.938177` | `0.751235` | candidate worse by `0.186942` |
| Corpus CER | `0.938547` | `0.748603` | candidate worse |
| Corpus WER | `0.966667` | `0.833333` | candidate worse |
| Exact sentences | `0/6` | `0/6` | no exact decode |
| Candidate blank fraction | `0.993477` | unavailable | severe blank dominance |
| Candidate wins / ties / losses | `0 / 1 / 5` | reference | primary comparison failed |
| One-sided exact p-value | `1.0` | reference | registered `p <= 0.05` rule failed |
| Two-sided exact p-value | `0.0625` | reference | descriptive only |

The primary gate, required-control gate, and conjunctive
intersection-union gate all failed. The 2,884-parameter linear comparator gate
passed, but that isolated component cannot rescue a failed primary gate.

## Loop 31 attribution matrix

The candidate beat exact-zero signal and timing-only controls on all six items
with a `0.061823` mean CER advantage and one-sided exact `p = 0.015625` for each.
That is a diagnostic hint, not a claim: the candidate did not pass the complete
registered attribution matrix.

| Control | Wins / ties / losses | Mean candidate CER advantage | One-sided exact p | Outcome |
|---|---:|---:|---:|---|
| Train-only no-signal prior | `0 / 1 / 5` | `-0.186942` | `1.0` | failed |
| Exact-zero signal | `6 / 0 / 0` | `0.061823` | `0.015625` | passed component |
| Validation-row derangement | `1 / 4 / 1` | `0.006158` | `0.5` | failed |
| Channel derangement | `3 / 0 / 3` | `-0.012163` | `0.71875` | failed |
| Time displacement | `2 / 4 / 0` | `0.011161` | `0.25` | failed |
| Timing-only | `6 / 0 / 0` | `0.061823` | `0.015625` | passed component |
| Train-target derangement | `4 / 2 / 0` | `0.033445` | `0.0625` | failed threshold |

Because the required conjunction failed and the intact candidate was worse
than the prior, this event does not establish sensor-signal dependence,
brain-specific origin, neural advantage, or decoding utility.

## Loop 33 bounded scaling curve

All three registered seed slopes were negative, and the median macro CER fell
from `1.514517` at 8 unique sentences to `0.938177` at 55. The descriptive
smallest-to-upper gain was `0.289202`, but the 55-row model remained `0.186942`
worse than its matched prior. The registered scaling gate therefore failed.

| Unique train sentences | Median macro sentence CER |
|---:|---:|
| 8 | `1.514517` |
| 16 | `0.944502` |
| 24 | `0.928779` |
| 32 | `0.982745` |
| 44 | `0.942438` |
| 55 | `0.938177` |

The curve is descriptive over one person and one session. It is not a universal
scaling law, a saturation estimate, or evidence that more data would produce a
neural advantage.

## Access order and resource proof

The protected access sequence remained exact:

1. The source cache was hashed once.
2. Exactly 55 train signal/target rows and six validation signal rows were
   delivered into isolated derivatives.
3. Twenty-one bounded training runs, 24 target-blind model-inference runs, six
   train-only prior fits, and 31 prediction sets completed.
4. Prediction hashes were committed at `54bdca9`, pushed, and remotely green.
5. The same six validation targets were delivered once and scored once.
6. Five source-test rows and all session-2 rows remained closed.

| Resource or access measure | Observed |
|---|---:|
| Source cache bytes | `10,632,576` |
| Source cache hash passes | `1` |
| Train signal / target rows | `55 / 55` |
| Validation signal / target rows | `6 / 6` |
| Source-test / session-2 rows | `0 / 0` |
| Candidate / control training runs | `18 / 3` |
| Optimizer steps | `5,040` |
| Target-blind inference runs | `24` |
| Train-only prior fits | `6` |
| Frozen prediction sets | `31` |
| Validation scoring runs | `1` |
| Post-target updates / configuration changes | `0 / 0` |
| Registered training and inference runtime | `184.046922 s` end to end |
| Scoring runtime | `0.017592 s` |
| Maximum measured peak RSS | `532,955,136` bytes |
| Final generated artifact bytes | `10,148,673` |
| Raw FIF/MAT reads / downloads / network calls | `0 / 0 / 0` |
| Language-model, RW3, stream, device, hardware runs | `0` |

The one-thread run stayed below the registered 20-minute, 1 GiB RSS, and
32 MiB generated-artifact caps. Public output contains hashes and aggregate
metrics, not plaintext targets or predictions.

## Claim boundary

**Engineering capability proven:** NeuroDecodeKit can stream selected rows from
the monolithic S21 cache, isolate train and validation derivatives, train and
freeze a registered multi-control prediction package, enforce a remote-green
target firewall, and score one consumed validation event within strict CPU,
memory, storage, and access ledgers.

**Scientific claim not established:** This event establishes no neural
advantage, sensor-signal dependence, brain-specific origin, source-test
performance, unseen-person generalization, real-time decoding, portable or
home-hardware result, assistive utility, diagnostic result, or clinical claim.

The upstream sentence cache is offline and noncausal. End-to-end capture or
real-time latency was not measured. S21 session 2 remains consumed and closed;
S25 remains final-only and unopened; no rerun of this six-target event is
authorized.

## Closeout verification

- Focused result, planning-boundary, and roadmap suite: 70 tests passed in
  `0.021` seconds with `27,967,488`-byte maximum RSS.
- Fully provisioned suite: 748 tests passed with three expected skips in
  `24.603` seconds, compared with the 744-test, three-skip pre-change baseline;
  process maximum RSS was `625,442,816` bytes.
- Dependency-light suite: 701 tests passed with 142 expected optional skips in
  `1.596` seconds; process maximum RSS was `118,538,240` bytes.
- Ruff, compileall, registry JSON, all five Loop 26 CLI help surfaces, workbook
  ZIP/formula/render checks, diff hygiene, and staged secret scanning passed.
- Closeout commit `f407ffb` passed push CI `29428087084` and PR CI
  `29428091698`, including Base Python and Optional Neuro Readers.
