# Loop 23.5 - Blank Intercept Calibration

Loop 23.5 is complete as a supervised synthetic calibration mechanism gate.
The registered seed-2353 test was opened once after validation passed and is
now consumed. This closeout does not reopen or reinterpret Loop 23 seed 2303,
Loop 22 seed 2203, S21 session 2, or any other observed neural holdout.

## Decision

Proceed only to a separately preregistered Loop 24 local precision/runtime
gate. The result authorizes comparison of local numeric execution paths against
this frozen synthetic float64 decoder reference. It does not authorize a
larger model, endpoint rule, language model, real-cache evaluation, or neural
decoding claim.

## Frozen Mechanism

The implementation follows `docs/LOOP_23_5_PREREGISTRATION.md` exactly:

- fresh physical train/validation/test partitions contain 64/16/16 items at
  seeds 2351/2352/2353;
- the exact frozen Loop 22 checkpoint and existing Loop 23 greedy and width-8
  prefix decoders are unchanged;
- one float64 scalar is added to only the blank logit;
- the scalar is fitted with exactly 80 bisection iterations in `[-8, 8]` on
  fresh train-frame blank/nonblank labels;
- the fit opens no train target IDs or target lengths;
- the train-only sequence prior uses a separate target-only view;
- validation freezes the open-or-park decision before any test access;
- the test receives one canonical evaluation and no schedule replay or fit;
- no target-length trim, endpoint, language model, temperature, per-symbol
  offset, model update, or additional candidate is present.

Frozen identities:

```text
fixture protocol SHA-256:     ac8b0dfa1ee512dd55645356546a068bc6b7e145f945a2e947d63dcf87185cc9
calibration config SHA-256:   43de56b1d275c0fd5b08a92d9dabc6893f7fe7ee49e02195623f6d61caa57e47
gate thresholds SHA-256:     7b2c7c061d1a286b1dc051677c19f4395601e5cbb3e80c5b8f3c991ee912ac58
checkpoint file SHA-256:      75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1
checkpoint payload SHA-256:   d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98
implementation commit:       baeea77
```

Commit `baeea77` was pushed before the registered fixture or seed-2353 test
partition existed.

## Implementation

Loop 23.5 adds:

- a dependency-free blank-margin, binary calibration, bisection-fit, paired
  no-harm, and deterministic bootstrap module;
- frame-only train access alongside the existing target-only/full views, with
  exact member tracking and manifest binding;
- optional blank-logit bias hooks in the unchanged CTC decode/replay path;
- a strict gate that fits once, freezes, evaluates validation, and conditionally
  opens test;
- calibrated and unmodified prefix/greedy decoders, a train-only sequence
  prior, and calibrated/unmodified zero-signal controls;
- report byte convergence, collision refusal, one-thread enforcement, and
  fixture/item/frame/state/runtime/RSS/output caps;
- create, metadata-only inspect, and strict gate CLI commands.

## Alternate Rehearsal

The full-size alternate fixture used seeds 9351/9352/9353. It ran before the
implementation commit and did not satisfy registered-protocol identity.

```text
alternate fixture bytes:                   204,720
alternate report bytes:                    756,215
alternate fixture plus report:             960,935
fitted blank intercept:                    5.15305226064133
validation calibrated CER / exact:         0.000000 / 16 of 16
alternate test calibrated CER / exact:     0.008929 / 15 of 16
alternate test unmodified CER / exact:     0.062500 / 9 of 16
alternate test corrections / new errors:   6 / 0
runtime / peak RSS:                        1.276594 sec / 212,959,232 bytes
decision:                                  nonregistered mechanics only
```

This rehearsal established mechanics and report headroom only. It was not
combined with the registered result or treated as another registered test.

## Registered Result

Validation passed the frozen rule, so seed 2353 opened once. Both the
validation and frozen test passed every registered threshold.

| Metric | Validation | Frozen test |
|---|---:|---:|
| Calibrated CER | 0.000000 | 0.000000 |
| Calibrated exact sequences | 16/16 | 16/16 |
| Unmodified CER | 0.087719 | 0.081818 |
| Unmodified exact sequences | 6/16 | 7/16 |
| Corrected items | 10 | 9 |
| New exact errors | 0 | 0 |
| Items with worse CER | 0 | 0 |
| Removed strict tail tokens | 10 | 9 |
| Repeated-pair reconstruction | 19/19 | 19/19 |

The test paired-bootstrap lower bounds are positive:

```text
exact-accuracy gain 95% interval: [0.312500, 0.812500]
CER reduction 95% interval:      [0.045387, 0.119420]
resamples / seed:                 2,000 / 2354
```

The fitted blank intercept is `5.130175197684084`. Its eight-byte parameter
payload hash is
`10ed3f4fd2bf29841aebe31b81d7726910361df5ecc10a2c29ae7de4563d174f`.
Train binary NLL falls from `0.084489` to `0.007248`, and train Brier score
falls from `0.025056` to `0.000898`.

The same frozen scalar also improves held-out frame calibration:

| Frame metric | Validation before / after | Test before / after |
|---|---:|---:|
| Binary NLL | 0.066514 / 0.005539 | 0.079330 / 0.009696 |
| Brier score | 0.021745 / 0.000441 | 0.021292 / 0.001860 |

These are generated-frame and generated-sequence measurements. They do not
show that the scalar is appropriate for MEG, EEG, natural text, or a different
model.

## Access And Replay Audit

The recorded semantic access order is:

```text
manifest -> checkpoint -> train frames -> calibration freeze ->
train targets -> prior freeze -> validation -> validation decision ->
test open -> one test evaluation
```

- train partition opens: 2, once per disjoint member view;
- validation partition opens: 1;
- test partition opens: 1;
- target IDs opened during calibration fit: false;
- calibration/model fits after test open: 0;
- test schedule replays: 0;
- calibrated validation schedules: 5/5 exact;
- unmodified validation schedules: 5/5 exact;
- combined validation pushes: 5,472;
- right context: 0 samples;
- maximum encoder/prefix/greedy state: 300/294/24 bytes.

Seed 2353 is consumed. Do not rerun the registered gate, reopen its partition
for analysis, select a precision candidate from it, or convert it into a tuning
set. Loop 24 must define its comparison protocol without using seed-2353
outputs for selection.

## Resources And Artifacts

```text
fixture items / valid frames:             96 / 2,190
fixture bytes:                            203,700 of 1 MiB
report bytes:                             765,477 of 1 MiB
fixture plus report:                      969,177 of 2 MiB
working core arrays:                      438,874 of 16,777,216 bytes
internal runtime:                         1.266573 of 20 sec
peak RSS:                                 213,958,656 of 805,306,368 bytes
calibration parameters / bytes:           1 / 8
training runs / parameter updates:        0 / 0
raw / real / network reads:               0 / 0 / 0
language-model runs:                      0
one-thread numeric environment:           passed
end-to-end latency measured:              no
```

Local ignored evidence:

```text
cache/loop235_blank_intercept/fixture/manifest.json
  SHA-256 fe1ebb0fec776367113088ff23f8db2933587e8426a7c3674330362e7abaad3e
cache/loop235_blank_intercept/gate.json
  SHA-256 07d6f075e670c901d5296226bac641af192d473d9b95710f52340907ca9d5262
cache/loop235_blank_intercept/gate.md
  SHA-256 cc8fcb3e2aaeab9810bca873da88fe113481913f9c56500f3db0d4d1aa15d54c
```

The cache directory occupies 960 KiB on disk. It is ignored and must not be
committed.

## Verification

Before registered fixture creation:

- focused calibration/fixture/CTC/gate suite: 26 tests passed;
- full unittest discovery: 238 passed, 3 skipped;
- full pytest: 235 passed, 3 skipped, 25 subtests passed;
- Ruff, `git diff --check`, and all three Loop 23.5 CLI help paths passed;
- full-size alternate rehearsal passed its mechanical validation and test
  gates under every cap;
- implementation commit `baeea77` was pushed and matched upstream.

The pre-change Loop 23 closeout baseline was 225 unittest tests and 222 pytest
tests, each with 3 skips. Loop 23.5 adds 13 passing tests without regressing the
prior suite. Final verification after documentation must use temporary
alternate fixtures only and must not reopen registered evidence.

## Claim Boundary

Engineering capability added: one frozen causal synthetic CTC pipeline can now
fit, hash, replay, and audit a target-length-independent one-scalar blank-logit
calibration under strict split, access, resource, and no-harm gates.

Scientific or decoding claim not established: this does not demonstrate neural
advantage, natural-text decoding, MEG/EEG transfer, unseen-person performance,
endpoint detection, online commitment, end-to-end latency, portable hardware,
arbitrary-thought decoding, or clinical utility.
