# Loop 24 Local Precision And Runtime Closeout

Date: 2026-07-12

Status: **Parked after one preregistered target-free selection run**

Decision: **Retain float32; do not open qualification; do not tune or rerun**

Proof posture: **Target-free synthetic, platform-bound precision/runtime evidence only**

## Executive Result

Loop 24 implemented the exact frozen float32, CPU-float16, and dynamic-QNNPACK-
qint8 paths around the existing 1,130-parameter causal producer. All 12
balanced timing rounds completed, the checkpoint and three candidate identities
matched, the QNNPACK operator was profiler-proven, all forbidden access counters
stayed zero, and seed 2402 qualification remained physically unopened.

Neither nonreference candidate earned qualification. Float16 preserved every
registered decoder behavior and passed every numerical tolerance, but its
producer path was `1.169950x` the float32 latency and its full pipeline was
`1.087904x`; qint8 reduced the numeric payload to `47.10%` of float32 but
changed decoder behavior, exceeded numerical tolerances, and was materially
slower. The complete selection orchestration also took `65.154951` seconds
against the frozen `60`-second cap, so the final decision is
`park_resource_cap_exceeded`.

This is a successful negative optimization result. Smaller numeric payloads
did not imply faster execution, behavior retention, integer-only kernels, lower
end-to-end latency, or better decoding.

## Frozen Identity

| Field | Registered value |
|---|---|
| Preregistration commit | `186bb6f` |
| Authorization commit | `b7738c7` |
| Implementation commit | `3a5dc0b` |
| Contract SHA-256 | `58e9d5407fef9419bc3bb0dc8cd3fa68d36dd238cb636d2f833dd9c5c6c3ae5d` |
| Checkpoint SHA-256 | `75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1` |
| Parameter payload SHA-256 | `d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98` |
| Model config SHA-256 | `8b331beeb236eaf54a938c5aca6b12c59d81fb87e28d2ff92e5edf66ef26dcc2` |
| Decoder config SHA-256 | `3a70a3e7890487eb8a1d5c871eb8540e8265ea524a62a5d3be8c5ac55f760544` |
| Blank intercept | `5.130175197684084` (`float64`, unchanged) |
| Selection / qualification seeds | `2401` / `2402` |
| CPU environment | Apple M4 Pro, macOS 26.6, Python 3.13.5, NumPy 2.5.0, Torch 2.13.0 |

The immutable preregistration still contains its original false authorization
snapshot. Current authority and its excluded real-data/training/RW3 scopes are
recorded separately in `registries/loop24_authorization_decision.v0.json`.

## Target-Free Fixture

The registered fixture contains two separate physical NPZ files plus one
metadata manifest. Manifest inspection checks identity, paths, sizes, split
disjointness, seeds, and declared hashes without opening or hashing either NPZ;
the selected partition is file-hashed only at its first authorized open.

| Measure | Selection | Qualification |
|---|---:|---:|
| Seed | 2401 | 2402 |
| Items | 48 | 48 |
| Waveform families | 6 x 8 | 6 x 8 |
| Valid samples | 4,536 | 4,536 |
| Shape | `48 x 5 x 128` | `48 x 5 x 128` |
| File bytes | 64,438 | 64,216 |
| Open count during gate | 1 | 0 |

The manifest is 8,234 bytes; the complete fixture is 136,888 bytes under its
512-KiB cap. Generation took 0.17 seconds wall with 45,154,304-byte peak RSS;
metadata-only inspection took 0.06 seconds wall with 22,183,936-byte peak RSS.
No target, label, text, participant identity, prediction, model output, real
recording, or consumed evidence created or selected a row.

## Candidate Result

All latency ratios below are paired against the float32 candidate in the same
balanced round. Lower is better; a replacement required producer median
`<= 0.80`, full median `<= 0.90`, full p95 `<= 0.95`, and paired-bootstrap
upper 95% bound `<= 0.98`, in addition to correctness, storage, and RSS gates.

| Candidate | Correctness | Payload bytes | Payload ratio | Producer median ratio | Full median ratio | Full p95 ratio | Bootstrap upper | Result |
|---|---|---:|---:|---:|---:|---:|---:|---|
| float32 eager | Reference replay bitwise exact 3/3 | 5,210 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | Retained |
| CPU float16 | Exact behavior and all numeric tolerances pass | 2,949 | 0.566 | 1.169950 | 1.087904 | 1.079073 | 1.095454 | Reject: slower; storage-only rule also fails |
| QNNPACK qint8 | Behavior and numeric tolerances fail | 2,454 | 0.471 | 2.784595 | 1.812123 | 1.807080 | 1.855377 | Reject: incorrect and slower |

Float16 reduced the deterministic numeric payload by 2,261 bytes and added
only 40,960 median worker-RSS-delta bytes relative to float32. It still missed
the storage-only payload-ratio limit of `0.50` and both no-slowdown limits of
`1.05`.

Qint8 saved 2,756 bytes and exposed `quantized::linear_dynamic` under the exact
QNNPACK module/dtype contract without fallback. Its maximum embedding error was
`0.325687` against `0.10`, maximum logit error was `0.549222` against `0.10`,
blank-margin error was `0.624358` against `0.15`, log-probability error was
`0.747147` against `0.15`, and greedy/prefix observable behavior differed.
Storage reduction cannot override those failures.

## Timing And Resource Audit

| Measure | Result | Frozen cap | Pass |
|---|---:|---:|---:|
| Balanced selection rounds | 12 | 12 | Yes |
| Fresh sequential workers | 36 | 48 maximum | Yes |
| CPU threads / concurrent workers | 1 / 1 | 1 / 1 | Yes |
| Selection frames | 990 | complete frame grid | Yes |
| Internal runtime | 65.154951 sec | 60 sec | **No** |
| External wall time | 65.62 sec | reported separately | N/A |
| Maximum worker peak RSS | 222,248,960 bytes | 1,073,741,824 bytes | Yes |
| Parent peak RSS | 300,957,696 bytes | reported separately | N/A |
| Working arrays | 455,472 bytes | 33,554,432 bytes | Yes |
| Input bytes | 144,782 bytes | fixture plus checkpoint | Yes |
| Report bytes | 110,073 bytes | 1,048,576 bytes | Yes |
| Gate output bytes | 125,934 bytes | included below | Yes |
| Total fixture plus output | 262,822 bytes | 4,194,304 bytes | Yes |

The steady-state timed paths exclude process startup, candidate construction,
and report I/O as preregistered. The 65-second internal cap covers the complete
selection orchestration through the frozen decision, so worker isolation and
startup remain a real local operational cost even though they do not distort
the per-frame path medians.

## Access Ledger

```text
manifest metadata reads:                 1
checkpoint file reads:                   1
selection partition opens:               1
qualification partition opens:           0
candidate conversions:                   3
reference inference protocol runs:      15
candidate inference protocol runs:      26
profiler runs:                            1
timing worker processes:                 36
training runs / parameter updates:      0 / 0
target/label/text reads:                  0
real-data / S7-S21 reads:               0 / 0
consumed seed 2203/2303/2353 reads:     0 / 0 / 0
network calls:                            0
RW3 source/socket/stream/board/XDF ops: 0 / 0
```

The counters represent registered protocol-level inference operations, not the
inner repetitions selected by `adaptive_autorange`. No energy measurement was
authorized or attempted. Thermal state, CPU frequency, float16 hardware
accumulation dtype, and qualification metrics remain explicitly unavailable.

## Artifacts And Replay

Generated fixture, payload, timing, and report artifacts remain ignored under
`.codex_work/loop24/`; none enters Git.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Fixture manifest | 8,234 | `17f66bc2cfd0f769993cce477ef4bc432022cd193217c18486ccc57e4e642ce1` |
| Selection partition | 64,438 | `a08eac84c059bcad1fb82d52f8b2706651d788be63bd3ada178b06965af82f28` |
| Unopened qualification partition | 64,216 | `8791b20982ab8b400230c8b854752736575f9d6d2b53e53ba309d043757651a0` |
| Frozen selection document | 5,248 | `5774d9bfeb13f90d7b1fcb7f1d2d1357f4f9ce526aa931205ef46398e5c7f9ce` |
| Gate JSON | 104,394 | `f877b7d88b00ce93ee8dd5091a6a0ba973c28a5d33d0a6972ca4dc82405dc098` |
| Gate Markdown | 3,615 | audit-bound locally |
| Measured audit | 2,064 | intentionally does not self-hash |

The inspect command validates report schema, frozen contract identity, all 20
access counters, 12 ordered events, causality, unavailable fields, resource
caps, artifact sizes and hashes, the report/audit binding, the internal
selection hash, and the fact that selection was frozen before qualification.

## Acceptance Gates

1. Authorization was recorded, tested, committed, pushed, and remotely green
   before implementation: **pass**.
2. Implementation was committed and remotely green before registered fixture
   generation or checkpoint access: **pass**.
3. Source, contract, checkpoint, scalar, decoder, and environment identities:
   **pass**.
4. Deterministic target-free physical fixture, strict split binding, and caps:
   **pass**.
5. All candidate statuses explicit, no fallback, exact QNNPACK operator proven:
   **pass**.
6. Reference replay and float16 correctness: **pass**; qint8: **candidate
   rejected exactly as required**.
7. Twelve balanced rounds, raw timing, bootstrap, and timing protocol:
   **pass**.
8. Selection-before-qualification access order: **pass**; no candidate selected,
   so qualification stays unopened.
9. Runtime resource gate: **fail**, 65.154951 seconds versus 60 seconds.
10. Output, privacy, tamper, malformed-cache, warning, and access audits:
    **pass**.

Because one primary acceptance gate failed, Loop 24 is parked. The selection
seed 2401 is consumed for this decision. Seed 2402 remains unopened and may not
be repurposed as fresh evidence. Changing worker startup, thresholds, fixture,
candidates, or tolerances and rerunning after seeing this result would be a
post-selection amendment, not the preregistered experiment.

## Verification

| Gate | Result | Wall time | Maximum RSS |
|---|---:|---:|---:|
| Focused Loop 24 optional suite | 36 passed | 4.07 sec | 308,510,720 bytes |
| Complete optional unittest suite | 313 tests, 3 skipped | 21.32 sec | 570,753,024 bytes |
| Complete optional pytest suite | 310 passed, 3 skipped, 105 subtests passed | 22.38 sec | 583,499,776 bytes |
| True zero-dependency Python 3.12 suite | 281 tests, 121 optional skips | 0.60 sec | 42,450,944 bytes |

The pre-implementation authorization-only baseline was 293 unittests and 290
pytest tests, so the exact Loop 24 implementation adds 20 passing optional-
environment tests. Ruff check, compileall, `git diff --check`, 10 JSON parses,
2 TOML parses, 54 local Markdown links, all five CLI help surfaces, and both
strict inspect commands pass. The fixture/report inspection takes 0.08/0.10
seconds wall with 22,282,240/27,590,656-byte peak RSS; qualification remains
unchanged and unopened. The nine-sheet tracker reloads with zero formula-error
matches. A full 49-commit, 3.38-MB Gitleaks scan reports no leaks.

## Decision And Next Boundary

- Retain `float32_eager_reference` for this frozen synthetic pipeline.
- Do not call float16 a speedup; it was slower on every replacement path.
- Do not call qint8 retained behavior, integer-only execution, or a speedup.
- Do not open seed 2402 qualification.
- Do not rerun or tune Loop 24 under the same evidence claim.
- Keep RW3 Stage A, real data, training, devices, and hardware unauthorized.
- Treat Loop 25 as planning only until a separate causal-preprocessing
  preregistration and explicit authorization are recorded and pushed.

## Claim Boundary

**Engineering capability added:** NeuroDecodeKit can now create, execute, audit,
and strictly inspect one bounded target-free local precision/runtime experiment
with physical selection/qualification separation and exact provenance.

**Scientific or decoding claim not established:** Loop 24 provides no neural
advantage, real-data accuracy, CER/WER improvement, unseen-person transfer,
end-to-end latency, energy-efficiency, useful EEG, portable-hardware,
arbitrary-thought, assistive, diagnostic, or clinical result.
