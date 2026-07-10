# NeuroDecodeKit Post-PR1 20-Loop Tracker
This tracker starts after PR1 lands. The core operating rule is simple: **do not add a more complex loop until the previous loop has produced a cache, report, demo, or explicit kill/park decision.**
Each loop should be one PR or one experiment note whenever possible. Complexity is allowed, but only when a simpler loop proves why it is needed.
## How to use
1. Start with the first loop whose status is not `Done` or `Parked`.
2. Copy that loop's prompt seed into Codex.
3. Require tests and a small artifact: cache, report, demo, or decision note.
4. Record the result in `docs/DECISIONS.md` and the spreadsheet tracker.
5. Move forward only when the acceptance gate is met or the loop is deliberately killed/parked.

## Current status

- Loop 1: Done for the synthetic smoke path. See `docs/LOOP_01_PR1_CLOSEOUT_SMOKE.md`.
- Loop 2: Done for local manifest parsing and summary logic. See `docs/LOOP_02_SPANISHBCBL_MANIFEST_V1.md`.
- Loop 3: Done for capped tiny-shard selection and dry-run download planning. See `docs/LOOP_03_SAFE_TINY_SHARD_SELECTOR.md`.
- Loop 4: Done for NPZ cache schema v0 loading, validation, and metadata sidecars. See `docs/LOOP_04_B2Q_MINI_CACHE_V0.md`.
- Loop 5: Done for metrics/error report v1. See `docs/LOOP_05_METRICS_ERROR_REPORT_V1.md`.
- Loop 6: Done for no-brain prior-only baseline. See `docs/LOOP_06_LM_PRIOR_BASELINE.md`.
- Loop 7: Done for template / nearest-centroid window baseline. See `docs/LOOP_07_TEMPLATE_BASELINE.md`.
- Loop 8: Done for optional tiny ConvNet baseline scaffold. See `docs/LOOP_08_TINY_CONV_BASELINE.md`.
- Loop 8.5 real-data gate: cleared for S21 session-1 `block1.fif`. The full
  block yields 66 typed sequences against 66 MAT rows with the strict identity
  mapping `0..65`, zero duplicate targets, and zero backtracks. A separate
  `keyTrig` audit pairs 2,028 keypresses with a 0.246 ms median absolute timing
  residual. See `docs/REAL_DATA_VALIDATION_2026-07-10.md`.
- Loop 9: Done. `b2q-sentence-cache` schema v0, continuous S21 extraction,
  optional tiny CTC, deterministic text-hash holdout, blank-collapse restart
  audit, and an automatic no-brain comparator are verified. The synthetic
  1,372-parameter model reaches zero CER on 20/20 seed runs; the real 66-row
  cache is a shape/preprocessing proof, not a model score. See
  `docs/LOOP_09_CONTINUOUS_SENTENCE_CTC.md`.
- Loop 10: Done for resource and CTC-length characterization. Isolated
  one-thread 100/50/25 Hz workers preserve exact 66-row trial/text/channel
  identity. Cache bytes fall to 50.9% and 25.9% of the 100 Hz reference, while
  extraction memory/runtime remain dominated by fixed preprocessing overhead.
  The exact official v2 kernel-16/stride-4 temporal contract remains feasible
  for 66/66 rows at 100 and 50 Hz but fails 66/66 at 25 Hz. No accuracy winner
  is selected. See `docs/LOOP_10_SAMPLING_RATE_SWEEP.md`.
- Loop 11: Done for real-data resource, geometry, and proxy characterization.
  One 66 x 102 x 617 magnetometer cache records finite device coordinates;
  four nested strategies at 76/51/25/16/8 channels produce 20 exact-identity
  subset caches in 70.3 MiB. Spatial FPS wins the coverage proxy and variance
  ranking wins the post-scaling variance proxy at every count. Neither is a
  decoder-accuracy winner. See `docs/LOOP_11_CHANNEL_SENSOR_SUBSET_SWEEP.md`.
- Loop 12: Done for real-cache representation, reconstruction, and resource
  characterization. Five encodings across the fixed base/FPS-16/variance-16
  inputs produce 15 exact-identity representation caches in 34.4 MiB.
  Qint16 is the fidelity candidate and qint8 is the aggressive storage
  candidate; float32 remains the default because no decoder was evaluated.
  See `docs/LOOP_12_PRECISION_STORAGE_SWEEP.md`.
- Loop 13: Parked after a measured real-cache gate. Nine standard/packed NPZ
  caches preserve exact decoded-signal hashes; the largest is 10.1 MiB, the
  slowest full/partial medians are 60.386/53.634 ms, and the highest worker
  peak RSS is 140.6 MiB. Partial access is inefficient but current absolute
  cost is below every declared budget. No Zarr dependency or backend was added.
  See `docs/LOOP_13_LAZY_BACKEND_GATE.md`.
- Loop 14: Done. The pinned official-exact splitter assigns 66 unique S21
  references to 55/6/5 train/validation/test rows with zero group crossings.
  Replacement preprocessing fits robust statistics on train rows and passes
  strict hash-bound provenance. The first fixed tiny CTC is near-null against
  the no-brain prior: 163 versus 164 character edits on five test sentences,
  with a paired interval spanning benefit and harm. Session and subject
  protocols remain unavailable with one session and one canonical person group.
  See `docs/LOOP_14_SPLIT_PROTOCOL_V1.md`.
- Loop 15: Done. Stage A used a pinned 2.344-GiB selection to acquire the complete
  two-part S21 session-2 recording and log. Three MAT slots (54, 58, 60) are
  explicitly unperformed; 63 raw trials map exactly to the remaining slots.
  Session 2 is scaled only with session-1 train statistics. The fixed tiny CTC
  fails the independent-session gate at CER 0.9179 versus prior CER 0.7755,
  with the paired interval wholly favoring the prior. Stage B never opens that
  consumed evaluation: a fixed 64/16/16 synthetic gate selects unlabeled robust
  channel-affine normalization on validation and reduces frozen synthetic
  holdout CER from 0.344828 to 0.000000. This is a best-case diagonal-shift
  mechanism proof, not real-MEG benefit. See
  `docs/LOOP_15_STAGE_B_SYNTHETIC_ADAPTER.md`.
- Loop 16: Done as a synthetic calibration characterization. Six nested sizes,
  three shift seeds, and an independent 48-row calibration pool are evaluated
  across stationary diagonal, channel-mixing, and within-row time-varying
  shifts. The registered median rule selects one 1.26-second synthetic row for
  stationary diagonal drift; two holdout seeds improve and one ties. Static
  robust affine adaptation harms all six non-diagonal/time-varying holdout
  cases. This is not a real-session or human calibration-time claim. See
  `docs/LOOP_16_SYNTHETIC_CALIBRATION_CURVE.md`.
- Loop 17: Done as an honest local evidence console. One loopback-only command
  loads six compact artifacts, validates 19 held-out synthetic examples, shows
  signal/target/prediction/error/provenance views, and keeps all real metrics
  aggregate-only. Predictive confidence is explicitly unavailable. The 8/8
  startup audit and desktop/mobile browser QA pass without a raw-data read,
  network fetch, real model run, or new cache. See
  `docs/LOOP_17_HONEST_LOCAL_DEMO.md`.
- Loop 18: Done as a versioned artifact-only evidence index. Eleven saved runs
  across six exact cohorts and four method families emit deterministic cards,
  metrics, config snapshots, cache metadata, Markdown, CSV, and one CLI table.
  Four cohorts permit internal ranking; event holdout and fit-on-eval smoke
  remain unranked, and no cross-cohort winner exists. Missing SemER, cache
  hashes, code version, method-specific resources, or uncertainty are explicit.
  The 103,789-byte build performs zero cache/raw reads, model runs, network
  fetches, or holdout reopenings. See
  `docs/LOOP_18_VERSIONED_REPORT_CARDS.md`.
- Loop 19: Done as a bounded native SpanishBCBL EEG bridge. A metadata-only
  gate pins the dataset revision and selects one complete 94,842,381-byte S7
  BrainVision-plus-MAT bundle under a 128-MiB cap. Lazy extraction aligns all
  2,534 MAT triggers with a 2.024-ms median absolute residual and writes a
  12,428,800-byte `2197 x 61 x 25` real EEG event cache. The first deterministic
  nearest-centroid event holdout is negative: 0.91% exact key-label accuracy
  versus 12.27% for a train-only no-signal prior. MOABB is not installed; EEG
  and MEG remain separate cohorts. See
  `docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md`.
- Loop 20: Done as a synthetic NeuroTokenCache v0 interface proof. The schema
  stores continuous `[items,time,embedding]` vectors with lengths, masks,
  timestamps, source rows/trials, subject/session IDs, modality, timebase,
  geometry plus availability, strict split hashes, source hashes, and explicit
  streaming/resource/claim metadata. A target-free deterministic mock producer
  writes a 76,646-byte `48 x 16 x 32` cache under a 4-MiB cap with zero model,
  training, real-data, or holdout reads. Its payload replays exactly; it is not
  a learned representation or decoding result. See
  `docs/LOOP_20_NEUROTOKEN_CACHE_V0.md`.
- Current proof boundary: two real S21 MEG sessions are alignment, sentence-cache,
  rate-resource, channel-proxy, representation-fidelity, and current NPZ-access
  verified at the applicable stages. Sentence-text membership and robust
  scaling are strict train-only, and one same-subject cross-session score is a
  clear negative result. One S7 EEG file is trigger/cache validated, and its
  nearest-centroid event result is also negative. There is no reliable neural
  advantage, unseen-person performance, retained-accuracy,
  optimal-sensor/precision, integer-only inference, OPM-equivalence, or
  low-latency streaming claim.
- Next action: open the post-roadmap causal chunk/replay gate on synthetic
  streams. Specify chunk boundaries, state, right context, offline-versus-
  streaming equivalence, and measured producer latency before implementing a
  causal decoder. Keep observed MEG/EEG results frozen; learned encoders,
  real-cache conversion, and adapter research remain separate gates.

## 20 loops
| # | Phase | Loop | Core question | Deliverable | Acceptance gate | Priority | Effort | Prompt seed |
|---:|---|---|---|---|---|---|---|---|
| 1 | Foundation | PR1 Closeout + Smoke Loop | Can one real/synthetic event-window extraction path run without hidden assumptions? | Finalize `extract-windows`; add synthetic smoke data path; produce one `.npz` cache. | Tests pass; CLI help works; one tiny cache can be produced; blockers documented. | P0 | S | Read PR1 diff, run tests, generate one synthetic cache, then attempt real one-block extraction only if files exist. |
| 2 | Foundation | SpanishBCBL Manifest v1 | Can we map subject/session/block/log files before downloading anything large? | Improve manifest parser with size, modality, subject/session/block, candidate log pairing, and warnings. | Manifest covers expected MEG/EEG/log file families; ambiguous rows are explicit. | P0 | S | Harden `manifest-from-paths` and produce a manifest summary with explicit unknowns rather than guessing. |
| 3 | Foundation | Safe Tiny-Shard Selector | Can a user request the smallest meaningful shard without accidentally downloading the universe? | Add size-aware selection, max-files, max-total-GB, and required `--execute` for downloads. | Dry run prints exact files and size estimate; real download requires explicit confirmation. | P0 | S | Make the tiny selector safety-first: max bytes, max files, dry-run default, and clear planned download report. |
| 4 | Foundation | B2Q-mini Cache v0 | Can one selected block become a reusable tiny cache with enough provenance to trust later results? | Create `.npz` cache schema v0 and optional metadata sidecar JSON. | Cache loads with one function; metadata explains every transformation. | P0 | M | Define the first stable tiny-cache schema and add a `load-cache` smoke command or test. |
| 5 | Foundation | Metrics + Error Report v1 | Can every run produce an honest report without needing a notebook? | Add `neurodecode report` that computes CER, WER, keyboard distance, and simple run metadata. | Report runs from CLI and writes JSON/Markdown; metric tests pass. | P0 | S | Build a report command that turns predictions + targets into a simple JSON/Markdown scorecard. |
| 6 | Baselines | LM-only / Prior-only Baseline | How much performance comes from language priors before using brain data? | Implement baseline that predicts from label distribution, prompts, or known sentence set without neural signal. | Baseline exists and is reported beside every neural result. | P0 | S | Implement an intentionally dumb but critical no-brain baseline and wire it into the report. |
| 7 | Baselines | Template / Nearest-Centroid Baseline | Is there separable signal in the windows before deep learning? | Train/eval nearest-centroid or template classifier over windows/features. | Model trains in seconds and produces a baseline report. | P1 | S | Build a tiny transparent classifier before any neural net. Make it boring and trustworthy. |
| 8 | Baselines | Tiny Conv / EEGNet-style Baseline | Can a small neural model beat transparent baselines on the tiny loop? | Add PyTorch optional tiny ConvNet baseline with CPU-friendly defaults. | Trains on synthetic data in CI-like smoke mode; real data path documented. | P1 | M | Add a tiny neural baseline without making the package heavy; optional deps and fast smoke test only. |
| 9 | Baselines | CTC Character Decoder Scaffold | Can a resource-bounded continuous sentence decoder learn sequence alignment without keystroke timing? | Add a sentence-window cache interface and optional tiny CTC model; prove synthetic training, then run one validated S21 block smoke. | Synthetic CTC trains; one real sentence cache validates shapes, labels, lengths, runtime, memory, and bytes; no performance claim. | P1 | M | Build a CPU-bounded continuous sentence cache and minimal CTC scaffold from validated S21 block1; keep Torch optional and preserve the no-brain comparator. |
| 10 | Compression | Sampling-Rate Sweep | How low can sampling rate go before the tiny-loop signal breaks? | Add experiment runner for 1000/500/250/100/50 Hz or available equivalents. | One report table compares at least 3 sampling rates. | P1 | M | Run a simple sampling-rate sweep and report accuracy/size/time tradeoffs. |
| 11 | Compression | Channel / Sensor Subset Sweep | Can explicit geometry-aware subsets reduce local input cost while preserving distinct signal proxies? | Add channel geometry plus spatial-FPS, variance, random, and file-order subset strategies under an output cap. | A 102-mag base and 20 subset caches preserve exact identity; resources/proxies are reported without an accuracy winner. | P1 | M | Run nested 76/51/25/16/8 subsets and keep geometry, variance, hardware, and accuracy claims separate. |
| 12 | Compression | Precision + Storage Sweep | Can we shrink fixed caches while bounding representation distortion before any decoder test? | Compare float32, float16, and calibrated integer/serialization variants without changing the sentence-cache contract. | At least 3 variants report bytes, encode/load time, reconstruction error, saturation, and exact identity under a cap. | P1 | M | Compare representations on the Loop 11 base/FPS/variance caches; do not call low distortion retained accuracy. |
| 13 | Compression | Measured Lazy-Backend Gate | Is current NPZ full/partial access materially limiting enough to justify another backend? | Isolated access benchmark, exact semantic hashes, explicit thresholds, and a build/park decision. | Optional Zarr is built only after a failed measured gate; otherwise NPZ remains default with revisit triggers. | P2 | M | Run the bounded access gate first; record relative inefficiency and absolute cost separately; add no backend without evidence. |
| 14 | Generalization | Split Protocol v1 | Are we accidentally evaluating on repeated sentence text or fitting transformations on validation/test data? | Deterministic sentence-text split plus explicit event/session/subject capabilities, membership hashes, and leakage audit. | Every report names split type and algorithm; duplicate groups never cross partitions; fit-on-train constraints and unavailable generalization levels are explicit. | P0 | S | Mirror v2's deterministic sentence-text grouping, make membership auditable, and refuse unsupported session/subject claims. |
| 15 | Generalization | Normalization + Adapter Baseline | Can a tiny subject/session adapter improve stability without retraining everything? | Add per-channel normalization, session normalization, and simple adapter hooks. | Synthetic domain-shift adapter works; real-data path is documented. | P2 | M | Implement the lightest adapter experiment possible: normalization first, learned adapter second. |
| 16 | Generalization | Calibration Curve Study | How many examples or minutes are needed before performance becomes useful? | Add a bounded multi-seed runner varying calibration size under independent and non-affine synthetic shifts. | Six calibration points, three seeds, validation-only selection, one frozen holdout pass, uncertainty, and resource/proof reporting complete without real cache access. | P2 | M | Closed: stationary diagonal reaches the registered median rule at one synthetic row, while mixing and temporal drift expose the adapter's failure boundary. |
| 17 | UX & Reproducibility | Gradio Demo v1 | Can a smart outsider understand the loop in 60 seconds? | Load compact artifacts; show synthetic signal/target/prediction/error views plus aggregate real evidence and provenance. | One local command; 19 examples; 8/8 audit; desktop/mobile interaction QA; unavailable confidence and noncausal scope visible. | P1 | M | Closed: artifact-backed console passes resource, proof, interaction, and responsive-layout gates without opening real holdouts. |
| 18 | UX & Reproducibility | Leaderboard + Report Cards | Can every experiment be compared without spreadsheet archaeology? | Versioned cards with metrics, config, cache metadata, source hashes, Markdown, CSV, and a CLI table. | 11 saved runs in 6 exact cohorts; deterministic replay; malformed/mixed schemas rejected; no global rank or holdout reopening. | P1 | M | Closed: artifact-only report cards make missing metadata and proof boundaries visible in 103,789 bytes. |
| 19 | Expansion | EEG / MOABB Bridge | Can the same tooling support easier-to-access EEG without pretending it will match MEG? | Native SpanishBCBL BrainVision gate, complete-triplet selection, lazy trigger-aligned cache, and same-split prior comparison. | One pinned 94,842,381-byte bundle produces a valid `2197 x 61 x 25` cache; exact key-label accuracy is reported as a negative 0.91% versus 12.27% prior without cross-modality claims. | P3 | L | Closed: native task-matched EEG bridge validated under caps; MOABB parked and no useful decoder advantage claimed. |
| 20 | Expansion | Neurotokens / v2-ready Interface | Can we design a future interface for neural embeddings without depending on unreleased data? | Versioned continuous `NeuroTokenCache` schema, create/inspect CLI, and deterministic target-free synthetic projection. | `48 x 16 x 32` smoke preserves timing, masks, modality, geometry availability, strict split/source hashes, and resource/causality boundaries in 76,646 bytes; payload replay is exact; no model, training, real holdout, learned-token, decoding, or real-time claim. | P2 | M | Closed: small official-v2-shaped interface is validated; next gate is causal chunk/replay behavior, not a larger model. |

## Anti-patterns
- Do not download a large dataset slice without an explicit dry-run report and `--execute` confirmation.
- Do not report neural model performance without a no-brain / prior-only baseline.
- Do not make clinical or arbitrary thought-reading claims.
- Do not add a heavy dependency to the base package when an optional extra would work.
- Do not treat a random split score as real generalization.
- Do not call whole-sentence non-causal decoding low-latency streaming or
  thought-only text generation.
