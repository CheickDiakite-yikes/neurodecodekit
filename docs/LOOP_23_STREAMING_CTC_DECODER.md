# Loop 23 - Streaming CTC Prefix Decoder

Closed on 2026-07-10 as a **parked synthetic decoder branch**. The decoder
mechanics, access discipline, controls, replay, and resource gates passed. The
frozen registered test failed the preregistered exact-sequence threshold, so
Loop 23 does not authorize precision work, real-cache conversion, or a decoding
claim.

## Proof Posture

Loop 23 proves that the frozen Loop 22 causal producer can feed deterministic,
incremental greedy and prefix-beam CTC states with correct blank/repeat
semantics, bounded memory, frame-indexed partial traces, and chunk-invariant
outputs on a generated five-symbol task.

It does not prove natural-text decoding, MEG/EEG performance, neural advantage,
online endpointing, user-perceived latency, unseen-person transfer, portable
hardware, arbitrary-thought decoding, or a clinical result.

The implementation follows the protocol frozen in
`docs/LOOP_23_PREREGISTRATION.md`. Decoder code and alternate-seed mechanics
were committed and pushed as `08b23d7` before registered seed 2303 existed.

## Added Capability

- dependency-free CTC path collapse, incremental greedy decoding, and
  log-space prefix beam search with separate blank/nonblank prefix scores;
- exhaustive tiny-path probability enumeration used as an independent oracle;
- strict, hash-bound 48/8/8 synthetic symbol-stream fixtures with physically
  separate train, validation, and test NPZ files;
- target-only train access, full validation access, and conditional one-time
  test access with ordered audit events;
- corpus CER, exact-sequence accuracy, repeated-pair recovery, controls,
  paired bootstrap intervals, and partial-hypothesis timing/stability metrics;
- five-schedule replay of encoder frames plus greedy and prefix traces;
- bounded create, inspect, and gate CLI commands;
- collision, malformed-cache, cap, access-order, and one-thread tests.

No model was trained or updated in Loop 23. The only learned input was the
frozen Loop 22 checkpoint, whose diagnostic probe was trained with frame-level
cross entropy rather than CTC loss.

## Registered Inputs

```text
fixture schema/version:          b2q-ctc-symbol-stream-fixture / 0
manifest schema/version:         b2q-ctc-symbol-stream-manifest / 0
protocol SHA-256:                a170b1a8bf91827f6ddeff4d02391b7c097c26f2149e0dc6d1d0e18eb0821360
manifest SHA-256:                6f6e6bf69e470178eb1d2b116e3570774cb8bad3453504a062b8d1134f4ae557
train/validation/test seeds:     2301 / 2302 / 2303
train/validation/test items:     48 / 8 / 8
train/validation/test frames:    1,110 / 181 / 181
channels / maximum samples:      5 / 116
fixture bytes:                   141,412 of 1,048,576
checkpoint bytes:                7,894
checkpoint SHA-256:              75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1
decoder config SHA-256:          3a70a3e7890487eb8a1d5c871eb8540e8265ea524a62a5d3be8c5ac55f760544
```

Partition SHA-256 values:

```text
train:       ed87a0e3b248aa65ab426521c6e76bc2b0543ee1d0c48d135a9a55e6aef433cd
validation:  74baa030b8245d11599e24758d6b5dd9802544658983bb03c54697c463bb15f4
test:        4ac4797c453853e6b7e7687367dfe7e096c3a774d5de49fbe1862eb0fdc31725
```

The metadata-only inspection validated paths, protocol values, shapes, item
counts, frame counts, target counts, repeated pairs, byte accounting, and
hashes without opening any partition array.

## Access Sequence

The registered gate recorded the required order:

```text
0 manifest validation, no partition array
1 frozen checkpoint validation, no update
2 train targets/item IDs opened once, no train signal
3 train-only complete-sequence prior fit
4 validation arrays opened once
5 decoder config frozen and hashed
6 test arrays opened once after validation passed
7 one canonical frozen test evaluation, no fit or replay
```

Train, validation, and test semantic open counts were `1/1/1`; the access audit
passed. Seed 2303 is now consumed. It must never be rerun as a fresh test or
used to select a blank bias, threshold, endpoint rule, model, or decoder.

## Alternate Rehearsal

One full-size alternate protocol used seeds 3301/3302/3303 before the
registered fixture was created. Validation produced:

```text
prefix/greedy CER:               0.072727
prefix/greedy exact accuracy:    0.500000
repeated-pair recovery:          1.000000
schedules passed:                5/5
test opened:                     no
```

All four incorrect rows contained the complete target followed by one extra
tail symbol. Because the preregistered validation exact-accuracy rule failed,
the alternate test remained physically unopened. No decoder threshold or
protocol value was changed after this result.

## Registered Validation And Test

```text
                                      validation       frozen test
prefix corpus CER                     0.018182         0.054545
greedy corpus CER                     0.018182         0.054545
prefix exact sequence accuracy        0.875000         0.625000
greedy exact sequence accuracy        0.875000         0.625000
repeated-pair reconstruction          1.000000         1.000000
train-only prior CER                  0.763636         0.800000
zero-signal pipeline CER              0.963636         0.890909
prefix CER reduction vs prior         0.745455         0.745455
prefix CER reduction vs zero signal   0.945455         0.836364
exact gain over stronger control      0.875000         0.625000
required exact sequence accuracy      0.750000         0.750000
gate                                  pass             FAIL
```

On the test, the 2,000-resample paired item bootstrap interval for CER
reduction was `[0.638374, 0.870536]` versus the train-only prior and
`[0.766369, 0.897321]` versus the zero-signal pipeline. Those control margins
passed. They do not override the preregistered exact-sequence failure.

## Failure Analysis

The validation error and all three test errors have the same structure:

```text
complete correct target + one spurious final symbol
```

Examples from the frozen report:

```text
validation-2302-0005  target  E B D C C A    output  E B D C C A C
test-2303-0002        target  C E D D B A C  output  C E D D B A C D
test-2303-0004        target  C E A A B D    output  C E A A B D C
test-2303-0007        target  B E D C A A E C output B E D C A A E C D
```

Greedy and prefix beam are identical on every error. The beam therefore did
not introduce or repair the mistake; the frozen upstream probe assigned a
nonblank class to a final tail frame. Target-aware trimming would make the
synthetic score look better by using forbidden knowledge of target length, and
an endpoint heuristic selected after seeing seed 2303 would be test tuning.
Neither was added.

The registered partials had zero revision events and zero edit overhead when
measured against their own final hypotheses. That is a useful warning:
stability is not correctness. A stable extra tail symbol can still make the
whole sequence wrong.

## Streaming And Resources

```text
validation frames / generated duration: 181 / 8.2 sec
registered schedules passed:             5/5
total validation pushes:                 1,327
right context:                           0 samples
maximum schedule delay:                  0 ms aligned / 140 ms jittered / 1,000 ms whole-item
maximum encoder state:                   300 bytes of 1 KiB
maximum prefix state:                    290 bytes of 4 KiB
maximum greedy state:                    22 bytes of 4 KiB
validation canonical RTF:                0.001257
test canonical RTF:                      0.001189
internal runtime before report write:    0.713611 sec of 20
external wall time:                      0.91 sec
internal / external peak RSS:            214,319,104 / 226,410,496 bytes
working core arrays:                     53,214 bytes of 16 MiB
JSON / Markdown / report total:          363,578 / 1,334 / 364,912 bytes
fixture plus report artifacts:           506,324 bytes
numeric threads:                         1
training runs / parameter updates:       0 / 0
raw / real / natural-text / network:     0 / 0 / 0 / 0
```

All five schedules produced exact final outputs and frame-indexed partial
traces. Whole-item delivery still adds one second of transport delay, so low
compute RTF is not an end-to-end latency result. Capture, real preprocessing,
endpoint detection, rendering, and human perception remain unmeasured.

## Commands

```bash
neurodecode make-ctc-symbol-stream-fixture \
  --out-dir cache/loop23_streaming_ctc/fixture \
  --max-total-mb 1

neurodecode inspect-ctc-symbol-stream-fixture \
  --manifest cache/loop23_streaming_ctc/fixture/manifest.json

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
neurodecode streaming-ctc-gate \
  --fixture-manifest cache/loop23_streaming_ctc/fixture/manifest.json \
  --checkpoint cache/loop22_tiny_causal_encoder/checkpoint.npz \
  --out-json cache/loop23_streaming_ctc/gate.json \
  --out-md cache/loop23_streaming_ctc/gate.md
```

The create and gate commands refuse output collisions. The registered gate was
run once. Its exit status was `1`, correctly representing the parked decision.

## Verification

- CTC/fixture/incremental/gate focused suite: 16 tests passed;
- full unittest discovery after closeout: 225 tests, 3 skipped, 13.18-second
  external wall time, and 470,319,104-byte maximum RSS;
- full pytest: 222 passed, 3 skipped, and 25 subtests passed in 13.38 seconds
  external wall time at 481,918,976-byte maximum RSS;
- repository-wide Ruff, compileall, root and three Loop 23 CLI helps, and
  `git diff --check`: passed;
- exhaustive CTC path-sum oracle, blank-separated repeats, deterministic ties,
  malformed fixture rejection, target-only access, output caps, strict split
  binding, one-time test open, and failed-validation no-open behavior: passed;
- full-size alternate validation protected its test after a failed gate;
- implementation commit `08b23d7` was pushed before seed 2303 generation;
- registered fixture create, metadata-only inspection, and one strict gate run
  completed under all caps with zero download or real-data access.

## Decision

Park Loop 23. Preserve the decoder implementation as an inspectable mechanism,
but do not call it a passed sequence-decoding gate and do not proceed to Loop
24 precision work yet.

The next permissible action is preregistration only for a fresh Loop 23.5
target-independent blank/boundary calibration gate. It may use new physical
synthetic splits and train/validation-only selection of one tiny blank-score
calibration rule. It must freeze that rule before one new test exists, retain
the unmodified greedy/prefix comparator, and forbid target-length trimming,
seed-2303 reuse, a language model, a larger encoder, or real holdout access.

Primary research basis remains the original CTC formulation and incremental
stability literature linked in `docs/LOOP_23_PREREGISTRATION.md`.
