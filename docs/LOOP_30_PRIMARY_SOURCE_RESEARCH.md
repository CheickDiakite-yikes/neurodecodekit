# Loop 30 Primary-Source Research And Local Replay Interaction Boundary

Date: 2026-07-12

Status: **Planning research complete; no UI implementation, server launch,
trace generation, replay execution, model operation, stream, network, or real-
data access is authorized**

Machine boundary: `registries/loop30_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 30

## Decision Summary

Loop 30 remains `Not Started`. Its future product is a **loopback-only,
target-free replay inspector**, not a live neural decoder and not a second
modeling experiment.

The interface may eventually show incremental hypotheses, explicit revisions,
commit points, finalization, stage clocks, resource use, warnings, hashes, and
proof posture. It may not silently turn a replay schedule into a capture clock,
turn a stable string into a correct string, turn an uncalibrated score into
confidence, or turn aggregate real scorecards into sentence-level real output.

The research closes with five decisions:

1. **Use a new target-free synthetic trace after separate authorization.** Do
   not reopen Loop 23 seed 2303, Loop 24 seed 2401, S7, or either S21 session to
   make a more persuasive replay.
2. **Expose revisions and explicit finalization.** A final result is a named
   event with a reason, not a hypothesis that happened not to change.
3. **Keep nine clock domains distinct.** Durations may be computed only within
   one monotonic origin or after a separately recorded mapping.
4. **Fail closed on locality.** The future launcher is fixed to `127.0.0.1`,
   disables sharing, analytics, monitoring, uploads, and broad file paths, and
   fails browser QA on any non-loopback request or WebSocket.
5. **Keep scientific evidence beside the interaction.** Source mode, producer
   and decoder causality, no-signal comparator, unavailable confidence,
   warnings, and exact proof posture remain visible throughout replay.

This is an interaction and measurement contract. No code path, fixture, seed,
payload, or browser session is created by this closeout.

## Measured Research Boundary

```text
high-level public web research operations:  10
remote code/data payload downloads:           0
local real-data path or hash checks:           0
real header/signal/target reads:               0
consumed-evidence payload reads:               0
model/checkpoint/training/calibration runs:    0
server launches or browser QA runs:            0
SDK imports, sockets, or streams:              0
physical device or hardware sessions:          0
CPU threads / workers:                       1 / 1
```

The external research tool does not expose process-level peak RSS or one end-
to-end runtime. Both values are unavailable rather than estimated. The current
planning artifact cap is 8 MiB; a future authorized Loop 30 prototype remains
under 32 MiB generated artifacts and 1 GiB peak RSS.

## Existing Evidence: Useful, But Not A Live Demo

### Loop 17: honest artifact-backed console

The existing Gradio evidence console already proves several useful behaviors:

- 19 held-out synthetic examples are inspectable;
- six real result rows remain aggregate-only;
- predictive confidence is explicitly unavailable;
- the displayed decoder is explicitly noncausal and not real time;
- analytics are disabled, sharing is false, and the default host is
  `127.0.0.1`;
- a build-time audit checks proof labels without running a real model.

It is not the Loop 30 interface. The current CLI accepts an arbitrary `--host`,
the launcher allows four threads, monitoring is not explicitly disabled, and
the console displays final artifact outputs rather than an incremental trace.
Those are implementation gaps, not permission to edit or launch it here.

Evidence: `docs/LOOP_17_HONEST_LOCAL_DEMO.md`,
`src/neurodecodekit/demo/app.py`, and `src/neurodecodekit/demo/evidence.py`.

### Loop 21: causal producer mechanics

Loop 21 established a deterministic causal frame producer across five chunk
schedules with zero right context. Its first possible frame is 160 ms after
item start. It also showed why throughput and latency differ: whole-item
delivery can batch efficiently while imposing the worst schedule delay.

This does not establish decoder causality, text emission, device capture
latency, browser rendering latency, or user-perceived end-to-end latency.

Evidence: `docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md`.

### Loop 23: stability can be wrong

Loop 23 is the strongest reason the future UI must show both revisions and
quality boundaries. Its registered synthetic streaming CTC test produced zero
revision events and zero edit overhead, yet only 5 of 8 exact test sequences
passed against a preregistered 6-of-8 threshold. A stable tail error remained
wrong. Seed 2303 is consumed and must not be reopened for interface tuning.

The interface therefore reports stability descriptively. It never displays
stability as confidence, correctness, neural evidence, or qualification.

Evidence: `docs/LOOP_23_STREAMING_CTC_DECODER.md`.

### Loop 24 and RW3: keep execution boundaries separate

Loop 24 consumed seed 2401 and parked after a resource and behavior gate. Its
arrays cannot become a convenient Loop 30 trace. RW3 preregisters future
replay/live source equivalence, packet semantics, and source/corrected/arrival
time views, but every RW3 stage remains unauthorized. A Loop 30 artifact replay
cannot authorize RW3, a socket, a board, a live source, or hardware.

Evidence: `docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md` and
`docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md`.

## Finding 1: Continuous Output Is Not Yet Low-Latency Output

Brain2Qwerty v2 removes keystroke-onset dependence with CTC over continuous
response windows. Its published encoder nevertheless uses a noncausal
architecture over an entire sentence. The paper explicitly states that users
cannot see a word before sentence end and names a fully real-time, low-latency
version as future work.

Loop 30 must therefore distinguish all of the following:

| Property | Meaning | Current project evidence |
|---|---|---|
| Asynchronous | Does not require known keystroke onsets | Published v2 result |
| Causal producer | Emits a frame without future samples | Loop 21 synthetic proof |
| Causal decoder | Emits text without future frames | Loop 23 synthetic decoder only |
| Replay paced | Delays recorded/generated events against a local schedule | Future Loop 30 only |
| Live source | Receives a currently captured device stream | Outside Loop 30 |
| End-to-end low latency | Measures capture through user-visible render | Unavailable |

Primary source:

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

## Finding 2: Partial Hypotheses Need A Revision Ledger

Incremental speech-recognition research is useful for interaction mechanics,
not as evidence that neural decoding behaves identically. It establishes two
portable lessons:

- partial hypotheses may be revised before finalization, so a UI needs a
  history rather than only the latest string;
- quality, latency, and update/revoke behavior are separate metrics.

The future trace therefore records each event's prior-event identity, edit
distance, cumulative revision count, cumulative edit overhead, committed
prefix length, stable duration, and explicit finalization state. No target,
label, prompt text, correctness, CER, WER, or confidence field is permitted in
the trace producer.

Stability is a behavior of the displayed sequence. Correctness requires a
separate authorized evaluation with independent targets. Confidence requires
Loop 34 calibration and cannot be inferred from stability, logits, entropy, or
UI color.

Primary sources:

- Streaming ASR quality and stability:
  https://arxiv.org/abs/2006.01416
- Incremental ASR evaluation with latency and revokes:
  https://arxiv.org/abs/2302.12049

## Finding 3: One Timestamp Field Would Create A False Latency Claim

Python's `time.perf_counter_ns()` provides a high-resolution monotonic clock
for local durations. Browser `performance.now()` is also monotonic relative to
its own time origin. Neither clock can be subtracted from an unrelated source,
process, or browser origin without a measured mapping.

Loop 30 freezes nine clock domains:

1. artifact source time;
2. replay scheduler time;
3. backend queue time;
4. producer compute time;
5. decoder compute time;
6. serialization and local transport time;
7. browser receive time;
8. browser render-commit time;
9. user-observed time.

Source time may be recording-relative, device-relative, or unavailable. The
five backend domains use integer monotonic nanoseconds. Browser receive and
render use the browser performance time origin. User-observed time is
unavailable unless a separate human/perceptual protocol measures it.

The future UI may report within-domain durations and an explicitly mapped
local replay timeline. It may not subtract source time from backend monotonic
time, backend time from browser time, or call replay scheduling capture
latency. LSL's raw, corrected, and local-arrival views remain relevant to a
future authorized live-source stage, not to this replay-only loop.

Primary sources:

- Python `perf_counter_ns`:
  https://docs.python.org/3.12/library/time.html#time.perf_counter_ns
- W3C High Resolution Time, Working Draft:
  https://www.w3.org/TR/2026/WD-hr-time-3-20260225/
- LSL time synchronization:
  https://labstreaminglayer.readthedocs.io/info/time_synchronization.html

## Latency Claim Ladder

The machine registry freezes six noninterchangeable levels:

| Level | Required evidence | Maximum wording |
|---:|---|---|
| 0 | Artifact chronology only | Ordered replay events |
| 1 | Backend monotonic stage spans | Local compute durations |
| 2 | Scheduler plus backend spans in one mapped origin | Local replay scheduling and compute |
| 3 | Browser receive and render spans in the browser origin | Local replay presentation latency |
| 4 | Explicit backend/browser origin mapping and fixed interaction protocol | Local prototype interaction latency |
| 5 | Authorized device capture through user-visible render | End-to-end latency |

The current research closeout is Level 0 because nothing ran. A future Loop 30
prototype can qualify at most Level 3: it has no live capture and no human-
perception protocol. Level 4 requires a separate measurement design. Level 5
is outside Loop 30.

The latency ledger keeps cold start, steady-state scheduling, queueing,
producer compute, decoder compute, serialization, browser receive, render,
first partial, first committed token, and finalization separate. Missing stages
are displayed as unavailable, never zero.

## Finding 4: Localhost Is A Measured Security Property

Current Gradio documentation says:

- `127.0.0.1` is the default local host while `0.0.0.0` exposes the app to the
  local network;
- `share=True` creates a public tunnel;
- the default maximum thread count is 40;
- analytics default on unless disabled;
- monitoring is enabled unless explicitly disabled;
- strict CORS normally remains true for a localhost server;
- state capacity defaults to 10,000 sessions;
- directories in `allowed_paths` expose all descendants;
- cached and returned files can become URL-accessible.

Loop 30 therefore does not merely label a page "private." Its future launcher
must use the exact fixed settings below:

```text
server_name:                  127.0.0.1
share:                        false
analytics_enabled:            false
enable_monitoring:            false
strict_cors:                  true
max_threads:                  1
state_session_capacity:       2
allowed_paths:                []
uploads:                      disabled
external network dependency: none
```

Repository and local data roots must be blocked from file serving. No arbitrary
file browser, upload component, static directory, share link, MCP server,
service worker, popup, or new tab is permitted. Browser QA must record every
request, response, and WebSocket and fail on any non-loopback destination.

Primary sources:

- Gradio Blocks and launch parameters:
  https://www.gradio.app/main/docs/gradio/blocks
- Gradio file-access security:
  https://www.gradio.app/main/guides/file-access
- Playwright network and WebSocket inspection:
  https://playwright.dev/docs/network

## Finding 5: Browser Responsiveness Is Not Neural Latency

The W3C Long Tasks API uses 50 ms as its long-task threshold. Loop 30 can use
that definition to fail a fixed replay browser test that produces one or more
long tasks. This is a browser responsiveness gate, not a neuroscience or
brain-to-text latency threshold.

The Event Timing API can separate input delay, event processing, and
presentation delay through the next render. It is a Working Draft and browser
support must be detected. Measurements are reported when available and cannot
be silently replaced with zeros.

Primary sources:

- W3C Long Tasks:
  https://www.w3.org/TR/longtasks-1/
- W3C Event Timing, Working Draft:
  https://www.w3.org/TR/2026/WD-event-timing-20260223/

## Finding 6: Incremental Status Must Remain Accessible

Changing partial text without moving focus is a status update. WCAG 2.2's
Status Messages criterion requires those changes to be programmatically
determinable so assistive technologies can announce them without taking focus.

The future interface must provide:

- a textual source mode and proof posture, not color alone;
- `role="status"` for concise state and warning changes;
- `role="log"` or an equivalent live-region pattern for sequential trace
  events;
- polite announcements that do not repeat every character unnecessarily;
- keyboard access without focus theft;
- no forced autoscroll;
- reduced-motion support;
- persistent access to the full revision and warning history.

Primary source:

- WCAG 2.2 Understanding Status Messages:
  https://www.w3.org/WAI/WCAG22/Understanding/status-messages

## Future Trace Contract

After a separate Loop 30 authorization-only commit, one new deterministic,
target-free synthetic trace may be generated. Its seed and payload hash must be
frozen before the payload exists. It may use synthetic character IDs or neutral
text generated solely from that seed; it may not use target text, labels,
prompts, consumed predictions, real sentence text, or evaluation accuracy.

Every trace event binds:

- schema, trace, event, sequence, and item identity;
- source mode, proof posture, and artifact identity;
- source frame and source time when available;
- replay, queue, producer, decoder, transport, browser, and render clocks when
  available;
- hypothesis, committed-prefix length, explicit finalization, and reason;
- previous-event identity, edit distance, cumulative revisions, edit overhead,
  and stable duration;
- producer and decoder causality plus required left/right context;
- source, configuration, trace, and payload hashes;
- warnings, unavailable fields, and all access counters.

The artifact must remain inspectable without starting the server. A sidecar
stores metadata, hashes, byte counts, runtime, peak RSS, source mode, causality,
warnings, and claim boundary. Neither file may be committed until an
authorization packet expressly allows a tiny generated fixture; the current
research milestone generates neither.

## Future Acceptance Gates

A separately authorized Loop 30 implementation may pass only if all 18 machine requirements and all 30 refusal cases pass. At minimum it must show:

1. one new target-free, hash-bound synthetic trace;
2. deterministic event replay and summary inspection without server launch;
3. visible replay, source, proof, causality, confidence-unavailable, and no-
   signal labels in every relevant view;
4. explicit revision and finalization semantics;
5. nine non-overloaded clock domains and six latency claim levels;
6. fixed loopback-only security settings and zero non-loopback browser traffic;
7. keyboard, focus, status-message, and reduced-motion accessibility checks;
8. one worker, one numerical thread, 32 MiB artifacts, 1 GiB RSS, and no
   external network dependency;
9. exact raw, real-cache, consumed-artifact, target, model, training,
   calibration, socket, stream, SDK, and hardware access counters;
10. a browser QA packet with desktop/mobile screenshots, console errors,
    request/WebSocket ledger, long-task count, and unavailable Event Timing
    fields.

The implementation parks if any label disappears during replay, any clock is
silently converted across origins, any external request occurs, any target or
consumed artifact contributes to the trace, any uncalibrated confidence is
shown, or any cap fails.

## Next Result-Oriented Decision

Loop 30 is not the active numbered execution gate. Loop 25 remains the causal
preprocessing decision and still requires its exact v1 authorization sentence.
Loop 30 also depends on Loop 25 because a trustworthy interaction surface must
not imply a causal pipeline before preprocessing causality is earned.

A future Loop 30 packet should be prepared only after Loop 25 closes or after a
documented amendment explicitly narrows the prototype to artifact chronology
with no causal-pipeline implication. That packet must freeze the new target-
free trace seed, exact fixture bytes, launcher settings, 18 requirements, 30
refusals, browser matrix, output cap, and stop rules before any implementation
or replay.

Loop 30 authorization could permit only the bounded synthetic replay interface.
It could not authorize RW3, a live source, real data, a model run, training,
calibration, a device, or hardware.

## Closeout Decision

```text
loop30_planning_research_complete_local_target_free_replay_execution_blocked
```

This work adds a machine-checkable interaction, timing, privacy, accessibility,
and browser-QA contract for a future local replay inspector. It does not
establish a running UI, live neural stream, causal end-to-end decoder,
confidence, neural advantage, decoding accuracy, unseen-person generalization,
capture-to-user latency, portable hardware, arbitrary-thought typing,
assistive benefit, diagnosis, or clinical utility.
