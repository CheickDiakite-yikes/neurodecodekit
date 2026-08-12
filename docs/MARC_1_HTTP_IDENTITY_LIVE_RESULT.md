# MARC-1 HTTP Identity Live Recovery Result

Date: 2026-08-12

Status: **Consumed at `MARC1HTL-F04`; no retry or rerun is available**

Machine result:
`registries/marc1_http_identity_live_result.v0.json`

## Result In One Line

The standards-aligned transport repair worked: one uncoded Wrist metadata body
with absent `Content-Encoding` was accepted, bounded, hashed, and parsed. The
one target-free selection then failed closed because the live file-list row
count differed from the frozen 55-row contract.

No participant was selected and no archive payload, EEG sample, target, model,
prediction, or score was accessed.

## Proof Order

Exact wrapper commit
`68ade0d4f6a58c19dbaae954a608080bdc6f128a` passed Base Python job
`94089099869` and Optional Neuro Readers job `94089099850` in CI
`31588920988` before the one invocation. Its implementation-registry SHA-256
was `30a0728590c1990c7f4d3c68356397fda29e4d5f2158108803d93b21e4ef48af`.

The pre-consumption machine gate passed before the new private marker or either
real input:

```text
free disk:                         17,704,779,776 bytes
logical CPUs:                     12
one-minute load:                  7.171875
load per logical CPU:             0.59765625
pre-consumption peak RSS:         32,964,608 bytes
CPU threads / workers / jobs:     1 / 1 / 1
```

The new mode-`0600` consumed marker was then written under the isolated
`MARC1-HT1A` root. That marker makes the invocation final even though the
selection did not complete.

## What The Repair Proved

The response passed the corrected transport predicate:

```text
HTTP request attempts:            1
redirects:                        0
terminal bodies accepted:         1
accepted body bytes:              2,917
Content-Encoding state:           absent
Content-Length present:           true
decoding/decompression operations: 0
raw response SHA-256:             4fee5117731a4c8f66efb7b48acb847ac3f0fafcd2b60b2017fb47115c37474c
```

This directly resolves the prior `MARC1PS-F03` transport blocker. An absent
response `Content-Encoding` is now handled as an uncoded representation, while
the body cap, exact length check, JSON content type, redirect policy, raw-body
privacy, and zero-decompression rules remain intact.

This is live transport compatibility evidence. It is not neural or scientific
evidence.

## Observed Semantic Failure

After one strict JSON parse, the Wrist source failed the frozen exact-row-count
rule and routed `MARC1HTL-F04`. The body contained a different number of rows
than the registered 55-row snapshot assumption.

The actual row count, rows, names, file IDs, checksums, URLs, and changed fields
were not retained or published. They must not be inferred from the 2,917-byte
body size or raw-response hash. The parser did not fall back, substitute a
version, change the participant rule, or select a partial cohort.

Consequently:

```text
selected participants:            0
selected member/archive rows:     0
private selection manifests:      0
payload requests / bytes:         0 / 0
signal sample reads:              0
target reads:                     0
training / inference / scoring:   0 / 0 / 0
```

This is evidence of metadata identity or inventory drift relative to the
frozen contract. It is not evidence against the MARC-1 neural hypothesis or
against the selected participant design because neither was reached.

## Access And Resource Result

```text
Freewill path operations / opens:       1 / 1
Freewill reads / hashes / parses:       1 / 1 / 1
Freewill input bytes:                   418,755
Wrist requests / response opens:        1 / 1
Wrist body reads / parses:              1 / 1
Wrist body bytes:                       2,917
total accepted input bytes:             421,672
raw-data / real-cache reads:            0 / 0
internal runtime:                       0.5396664168220013 sec
reported peak RSS:                      38,223,872 bytes
external wall time:                     0.70 sec
external maximum RSS:                   38,305,792 bytes
public result bytes:                    5,006
incremental disk bytes:                 5,458
```

Public result SHA-256:
`50a1bd4e97e6149db91d528aa0fce79e6aa5d3cedf79acdb12f03bf4a2d041f2`

Every local-header, payload, signal, channel, geometry, event, target,
derivative, training, inference, prediction, freeze, delivery, score,
provider-model, hardware, release, post-result update, retry, rerun,
other-project, and claim-upgrade counter remained zero.

## Verification

Ten immutable result tests and all 467 MARC tests pass. The complete
dependency-light suite passes 2,606 tests with 204 expected skips in 22.685
seconds at 280,395,776-byte external peak RSS. The optional-neuro suite passes
2,677 tests with 35 expected skips in 58.662 seconds at 761,479,168-byte
external peak RSS. Both complete suites add exactly ten tests and zero skips
over the green wrapper baseline.

Ruff, compilation, strict parsing of all 184 registry JSON documents,
aggregate result inspection, and `git diff --check` also pass. No generated
inspection debris is retained or committed.

## Disposition

`MARC1-HT1A` is consumed. Do not retry, rerun, resume, amend its parser, inspect
the retained private root, reopen the sealed Freewill manifest, or request the
Wrist endpoint again under this lane. The exact public aggregate result is the
only retained evidence surface used for this closeout.

Payload acquisition remains ineligible because the joint 12+12 pilot selection
did not complete. A future repair must be a separately named prospective
metadata-snapshot identity lane. It should determine the current official
record/version relationship and bind an immutable file-list identity before
another one-shot selector is considered. That research may begin from this
aggregate failure only; any public body request remains a new Tier C event.

This remains the same research path: resolve metadata identity, qualify the
MARC-1 control cohort, test a cue-resistant neural positive control, then move
to held-out language decoding. It is not a pivot.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now handles standards-compliant
uncoded HTTP metadata and fails closed at a deeper semantic identity boundary
with a bounded, privacy-preserving consumed audit record.

Scientific claim not established: this metadata failure establishes no neural
effect, brain-specific source, decoding accuracy, language decoding, or
thought-to-text capability.
