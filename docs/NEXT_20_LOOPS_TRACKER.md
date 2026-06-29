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
- Current blocker: no real SpanishBCBL `.fif` / `.mat` pair or full remote file list is present locally.
- Next loop: Loop 5 - Metrics + Error Report v1.

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
| 9 | Baselines | CTC Character Decoder Scaffold | Can we move from event labels toward sequence decoding without overbuilding? | Add minimal CTC data interface and model scaffold; train on synthetic sequence data first. | Synthetic CTC loop works; real-data assumptions are explicit. | P1 | M | Create a minimal CTC scaffold that proves the interface, not SOTA accuracy. |
| 10 | Compression | Sampling-Rate Sweep | How low can sampling rate go before the tiny-loop signal breaks? | Add experiment runner for 1000/500/250/100/50 Hz or available equivalents. | One report table compares at least 3 sampling rates. | P1 | M | Run a simple sampling-rate sweep and report accuracy/size/time tradeoffs. |
| 11 | Compression | Channel / Sensor Subset Sweep | How many channels are actually needed for useful signal in the tiny loop? | Add channel-picking strategy: all, motor-ish if known, random-k, top-variance. | At least 3 channel settings are comparable from the same split. | P1 | M | Implement channel subset sweeps using explicit strategies and honest caveats. |
| 12 | Compression | Precision + Storage Sweep | Can we shrink caches by changing representation before losing too much signal? | Add cache writer variants: float32, float16, optional int8 quantized, compressed NPZ. | Report shows at least 3 storage variants with reproducible commands. | P1 | M | Compare cache precision/storage formats and produce a size-versus-score report. |
| 13 | Compression | Zarr / Lazy Cache Backend | When NPZ becomes awkward, can we stream chunks without rewriting the whole system? | Add optional Zarr backend behind same cache interface. | Zarr is optional; NPZ remains default; same training interface works. | P2 | M | Add Zarr as an optional backend only after NPZ is stable; do not break the simple path. |
| 14 | Generalization | Split Protocol v1 | Are we accidentally evaluating on data that is too similar to training? | Add explicit split types: event, sentence, session, subject where metadata permits. | Every report names the split type; leakage risks are visible. | P0 | S | Make split type explicit and impossible to ignore in every training/eval report. |
| 15 | Generalization | Normalization + Adapter Baseline | Can a tiny subject/session adapter improve stability without retraining everything? | Add per-channel normalization, session normalization, and simple adapter hooks. | Synthetic domain-shift adapter works; real-data path is documented. | P2 | M | Implement the lightest adapter experiment possible: normalization first, learned adapter second. |
| 16 | Generalization | Calibration Curve Study | How many examples or minutes are needed before performance becomes useful? | Add experiment runner varying calibration set size. | Report includes 5+ calibration points or explains why not. | P2 | M | Create a calibration curve runner that works on synthetic data and plugs into real caches. |
| 17 | UX & Reproducibility | Gradio Demo v1 | Can a smart outsider understand the loop in 60 seconds? | Upgrade demo to load a cache, show target/prediction, confidence, errors, and signal snippet. | Demo runs locally from one command and shows at least one example end-to-end. | P1 | M | Make a small honest demo: no hype, just signal, prediction, errors, and uncertainty. |
| 18 | UX & Reproducibility | Leaderboard + Report Cards | Can every experiment be compared without spreadsheet archaeology? | Add standardized run artifacts: metrics.json, config snapshot, report.md, cache metadata. | At least 3 baselines appear in one leaderboard table. | P1 | M | Build the experiment report-card format and local leaderboard; make missing metadata obvious. |
| 19 | Expansion | EEG / MOABB Bridge | Can the same tooling support easier-to-access EEG without pretending it will match MEG? | Add optional adapter for a small public EEG benchmark or MOABB-style dataset path. | Bridge is optional and clearly labeled exploratory. | P3 | L | Explore an EEG adapter only after the core MEG loop is stable; keep claims conservative. |
| 20 | Expansion | Neurotokens / v2-ready Interface | Can we design a future interface for neural embeddings without depending on unreleased data? | Add placeholder `NeuroTokenCache` interface and synthetic embedding demo. | No v2-data assumptions; interface can ingest embeddings later. | P2 | M | Design the neurotoken interface as a small abstraction, not a grand architecture rewrite. |

## Anti-patterns
- Do not download a large dataset slice without an explicit dry-run report and `--execute` confirmation.
- Do not report neural model performance without a no-brain / prior-only baseline.
- Do not make clinical or arbitrary thought-reading claims.
- Do not add a heavy dependency to the base package when an optional extra would work.
- Do not treat a random split score as real generalization.
