# Start Here

1. Read `README.md` for the mission and quickstart.
2. Read `AGENTS.md` for coding-agent rules.
3. Read `docs/CODEX_HANDOFF.md` for the next three PRs.
4. Paste `prompts/CODEX_START_PROMPT.md` into Codex to continue.
5. Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Current verified state: two complete S21 SpanishBCBL MEG recordings plus one
94,842,381-byte S7 SpanishBCBL EEG BrainVision bundle and their matching MAT
logs have been selectively downloaded under exact caps; the full dataset and
12.79-GB EEG subtree have not been downloaded. Loops 9-12 and 14-20 are
complete; Loop 13 is parked.
Session 1 provides a strict 55/6/5 split with
train-only robust scaling. Session 2 is a complete two-part FIFF recording with
63 performed trials; MAT slots 54, 58, and 60 are explicitly empty and are
preserved as gaps. Its 102-magnetometer cache is scaled only with frozen
session-1 train statistics. The fixed same-subject cross-session tiny CTC fails
to generalize: corpus CER 0.9179 versus 0.7755 for the no-signal prior, with a
paired interval wholly favoring the prior. There is no reliable neural
advantage, unseen-person result, retained-accuracy result, integer-only
inference, real-time decoder, or at-home hardware claim. Session 2 is now a
consumed evaluation set. Loop 15 Stage B separately proves unlabeled robust
channel-affine recovery on a fixed synthetic diagonal shift: identity/adapted
holdout CER is 0.3448/0.0000, with zero real cache reads and only 21,354 bytes
of artifacts. Loop 16 then tests six calibration sizes, three shift seeds, and
three independently calibrated shift families. One 1.26-second synthetic row
meets the registered median stationary-diagonal rule, but one seed only ties;
the adapter harms all channel-mixing and time-varying holdout seeds. This is
not a human calibration-time or real-MEG claim. Loop 17 adds a local
artifact-backed evidence console with 19 synthetic examples, aggregate-only
real metrics, explicit unavailable confidence, noncausal/task scope, and
responsive browser QA. It performs no real model run or raw-data read. Loop 18
adds 11 versioned cards across six exact cohorts and four method families from
saved reports only. Four within-cohort rankings are authorized; no global rank
exists, all missing recommended metadata stays visible, and the 103,789-byte
build opens no cache or holdout. Loop 19 then passes a metadata-only access and
dependency gate, lazily aligns all 2,534 MAT triggers to one real S7 EEG file,
and writes a 12,428,800-byte `2197 x 61 x 25` cache. Its first transparent
within-session classifier is a negative result: 0.91% exact key-label accuracy
versus 12.27% for the train-only no-signal prior. This is bridge validation,
not useful EEG decoding or a portable-hardware claim. Loop 20 adds a
76,646-byte synthetic `NeuroTokenCache v0` shaped `48 x 16 x 32`, with timing,
masks, modality, geometry availability, strict split/source hashes, and
explicit causality/resource boundaries. The deterministic target-free payload
replays exactly, but it is not learned, not a decoding result, and not an
end-to-end streaming claim. Loop 21 then passes a five-schedule synthetic
causal replay gate: zero right context, exact frame/timestamp identity, bitwise
stream-schedule identity, 300-byte mutable state, and no target/model/decoder/
real-data access. Transport delay still ranges from 0 to 610 ms depending on
chunking, and end-to-end text latency remains unmeasured. Continue with Loop
22's tiny learned causal encoder gate on synthetic train rows only. See
`docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md` and `docs/POST_20_ROADMAP.md`.
