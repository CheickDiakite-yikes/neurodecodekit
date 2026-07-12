# Loop 25 Primary-Source Research: Causal Preprocessing

Date: 2026-07-12

Status: **Research and source audit only; no implementation or execution**

Parent commit: `3ae7d97`

Proof posture: **Documentation, public source, and local source-code evidence**

## Research Question

What is the smallest preprocessing path that can accept contiguous neural
samples incrementally, use no future samples or evaluation-fit statistics,
preserve absolute sample timing across arbitrary chunk boundaries, and feed the
existing causal frame producer without pretending to reproduce the official
offline Brain2Qwerty v2 pipeline?

This question comes before another model run. A zero-lookahead encoder does not
make a system causal if filtering, resampling, normalization, sentence
segmentation, or padding has already used future information.

## Access Ledger

This research pass performed:

```text
public documentation reads:              yes
official public source-code reads:        yes
local tracked source-code reads:          yes
filter design or coefficient generation:   0
synthetic fixture generation or opens:      0
numeric preprocessing runs:                 0
raw or real-data reads:                      0
real-cache or consumed-cache reads:          0
target, label, text, or prediction reads:    0
model inference or checkpoint reads:         0
training runs or parameter updates:          0
RW3, socket, stream, board, or hardware ops: 0
generated experiment payload bytes:          0
```

The official repository was inspected at commit
[`3bf5a4099ca0d23bbe994b2287905760236e56e0`](https://github.com/facebookresearch/brain2qwerty/commit/3bf5a4099ca0d23bbe994b2287905760236e56e0).
No unreleased v2 data or embeddings were accessed.

## Executive Finding

The current real sentence-cache path is an honest reproduction-oriented
**offline** path, not a causal preprocessing path. It calls MNE 1.12.1 with
defaults equivalent to:

```text
notch:      FIR, phase="zero", reflect-limited padding
bandpass:   FIR, phase="zero", reflect-limited padding
resample:   FFT, npad="auto"
scaler:     median/IQR fit on a recording or frozen train rows
segment:    first key through ENTER plus 0.45 s post-context
padding:    sentence endpoint known before zero padding
```

MNE documents that its default zero-phase FIR delay compensation is noncausal.
It also warns that resampling a continuous `Raw` object reduces event-time
precision. Brain2Qwerty v2 itself says its MEG signals were preprocessed
offline before a continuous sentence window was decoded. Therefore, the
project must keep two distinct contracts:

1. **Offline Brain2Qwerty-compatible evidence path:** useful for current
   reproduction and historical comparisons, explicitly noncausal.
2. **Causal local path:** a new bounded engineering path with state, timing,
   chunk replay, and frequency-response evidence, explicitly not numerically
   equivalent to the offline path.

## Primary-Source Evidence

| Source | Direct evidence | Loop 25 consequence |
|---|---|---|
| [Brain2Qwerty v2 paper](https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf) | Section 4.1 says MEG was preprocessed offline with 0.5-45 Hz bandpass, 50 Hz notch, 100 Hz downsampling, per-recording median/IQR normalization, and +/-5 clamping. Sentence windows extend 400-500 ms after completion. | Preserve these values as an offline comparator only. Do not infer zero lookahead or live endpointing. |
| [Official v2 experiment config](https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/xp_config.py) | Public config freezes `frequency=100`, `filter=(0.5, 45.0)`, `notch_filter=50`, `RobustScaler`, `clamp=5`, and `apply_proj=False`. | Bind the provenance, but do not silently reuse an offline transform in a causal claim. |
| [Official v2 model config](https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/model_config.py) | The public architecture uses temporal downsampling with kernel 16 and stride 4 after a convolutional encoder, then a Conformer. | Loop 25 must end at a stable 100 Hz sample stream; downstream model causality remains a separate gate. |
| [Official v2 model forward](https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/models.py) | The public forward receives a complete sentence tensor and passes it to an inherited transformer; this file exposes no streaming state or causal attention mask. | “Asynchronous sentence decoding” is not sufficient evidence for causal incremental inference. |
| [MNE `Raw.filter`](https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.filter) | FIR `phase="zero"` is the default and compensates delay, making it noncausal. IIR `phase="forward"` is documented as causal. | The existing default filter calls cannot enter a real-time claim. A future path needs explicit forward state. |
| [MNE filtering background](https://mne.tools/stable/auto_tutorials/preprocessing/25_background_filtering.html) | Causal FIR and IIR filters trade delay, phase behavior, stability, transition width, and ringing. Filtering can distort temporal dynamics. | Register frequency and time-domain diagnostics; do not optimize only for chunk equivalence. |
| [MNE filtering/resampling tutorial](https://mne.tools/stable/auto_tutorials/preprocessing/30_filtering_resampling.html) | For integer-rate changes, MNE recommends low-pass filtering then decimating after event formation; it warns about aliasing and timing precision. | Freeze a 1,000-to-100 Hz integer path with explicit anti-alias evidence and global decimation phase. |
| [SciPy `sosfilt`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html) | SOS filtering accepts initial state and returns final delay state using cascaded direct-form-II sections. | Use one stateful SOS cascade and carry state across every chunk. |
| [SciPy `sosfilt_zi`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt_zi.html) | Provides step-response steady-state initial conditions for SOS filters. | Freeze initialization from the first source sample and test it separately from resumed state. |
| [SciPy `butter`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html) | Butterworth designs can be emitted directly as numerically stable SOS sections. | Freeze one fourth-order bandpass design; do not select order after fixture output. |
| [SciPy `iirnotch`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.iirnotch.html) | Defines a second-order digital notch by frequency, quality factor, and sample rate. | Freeze 50 Hz and Q=30 before coefficient generation. |
| [SciPy `resample_poly`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html) | The convenience function centers output around a symmetric FIR for a zero-phase result and applies boundary padding. | Do not use it as the registered causal resampler; current EEG-window use remains offline. |

## Current Local Source Audit

The source identity below is frozen at parent `3ae7d97`.

| Local file | SHA-256 | Finding |
|---|---|---|
| `src/neurodecodekit/preprocess/sentence_extraction.py` | `da2b51853e1c0bc1c0d8e6263b268b346fe7711a471dc361b44897e6a5af639b` | Whole-recording default MNE notch, bandpass, FFT resampling, endpoint segmentation, and optional recording/train robust fitting. |
| `src/neurodecodekit/preprocess/fif_mat_extraction.py` | `ac97eca1192c0601ea1fbb2e732d18354322be477942d1ed27e6e1df4841f58d` | Whole-Raw MNE resampling before fixed event windows; useful offline extraction, not incremental preprocessing. |
| `src/neurodecodekit/preprocess/brainvision_extraction.py` | `6aa8fcfff84a165cd88432bfd27ced3bab36af254261b28642ae12d9529ef7e9` | `resample_poly` is applied independently to complete key-event windows; boundaries and centered filtering are known. |
| `src/neurodecodekit/cache/neurotoken_stream.py` | `d8c9cd1104c2fa21f0d74b2b25a1e6e6942fa180bc7a57204f2d9182d6b29be0` | Downstream frame buffering has zero right context, absolute frame indices, exact chunk replay, and drop-incomplete flush. |
| `src/neurodecodekit/experiments/causal_replay_gate.py` | `a55156af95f7b6521d1e30e08ae2191efb68d4d4e208c1d277f85d7a613160fd` | Loop 21 proves frame-producer schedule invariance only; it does not audit upstream filter, rate, scaler, or gap state. |

### Transform Classification

| Transform | Current use | Causal status | Loop 25 treatment |
|---|---|---|---|
| Channel selection and fixed order | before loading | causal/stateless if metadata is frozen | Preserve exact order and reject changes. |
| MNE FIR notch, `phase="zero"` | whole recording | noncausal | Offline comparator only. |
| MNE FIR bandpass, `phase="zero"` | whole recording | noncausal | Offline comparator only. |
| MNE FFT `Raw.resample` | whole recording | whole-input and timing-sensitive | Offline comparator only. |
| SciPy `resample_poly` | complete EEG event window | centered, boundary-dependent | Offline event bridge only. |
| Per-recording median/IQR fit | complete recording | future-dependent and transductive | Forbidden in the causal runtime. |
| Train-row median/IQR fit | offline train partition | fit is offline; application can be causal | Allow only pre-frozen statistics and hashes. |
| Clamp to +/-5 | pointwise | causal/stateless | Preserve after frozen normalization. |
| First key through ENTER plus post-context | complete trial | endpoint-dependent | Not part of Loop 25. |
| Sentence zero padding | after endpoint | endpoint-dependent | Never emit padding in the causal stream. |
| Loop 21 kernel/stride framing | incremental sample stream | zero right context | Downstream compatibility target only. |

## Registered Design Direction

The smallest meaningful v0 path is:

```text
contiguous float32 samples at 1,000 Hz
  -> explicit float64 SOS state
  -> 50 Hz IIR notch, Q=30
  -> fourth-order 0.5-45 Hz Butterworth bandpass
  -> phase-locked keep-every-10th-sample decimation
  -> frozen per-channel center/scale
  -> +/-5 clamp
  -> float32 samples at 100 Hz with absolute source indices/timestamps
```

This design is intentionally not called “Brain2Qwerty v2 preprocessing
equivalence.” Its cutoffs and output rate follow the public v2 configuration,
but the phase response, startup transient, and boundary behavior differ because
causality requires a different signal-processing contract.

### Why SOS IIR For This Gate

- It has explicit bounded mutable state.
- `sosfilt` can return and accept exact final state at chunk boundaries.
- The section representation is preferred over one high-order transfer
  function for numerical stability.
- It gives a serious causal baseline without a long FIR history buffer.
- Frequency response, poles, impulse behavior, and schedule replay can all be
  audited before it is allowed near real data.

The tradeoff is frequency-dependent phase delay. Loop 25 must report it and
must not summarize it as one universal end-to-end latency number.

### Why Integer Decimation Instead Of A General Resampler

The existing S21 path starts at 1,000 Hz and targets 100 Hz. After an explicit
anti-alias filter, selecting source indices `0, 10, 20, ...` is state-light,
timestamp-transparent, and exactly schedule-invariant. A general rational
polyphase stream would add coefficient, phase-bank, delay-compensation, and
boundary choices that are unnecessary to audit the current path.

This v0 restriction is not a device-compatibility claim. Rates such as 256 Hz
need a later registered rational-resampling gate, likely under Loop 29 or a
Loop 25 amendment.

### Why Frozen Statistics Only

Computing median and IQR online requires either an unbounded history, an
approximation, or a changing representation. Computing them over a complete
recording uses future samples. Loop 25 therefore accepts only immutable
center/scale arrays created independently of its synthetic partitions. It
tests application mechanics, not normalization fitting or adaptation.

## Controls Required Before Implementation

1. **Whole-versus-chunk replay:** the same causal function receives an item in
   one chunk and seven adversarial schedules.
2. **Future mutation:** paired inputs are identical through a registered cut;
   changing only the future cannot change earlier outputs or state.
3. **Resume:** state exported at ten cuts must reproduce uninterrupted output,
   source indices, timestamps, and final state.
4. **Frequency response:** poles must be stable; DC, passband, 50 Hz notch, and
   post-Nyquist attenuation gates are frozen before coefficients exist.
5. **Startup and flush:** first-sample initialization is explicit; flush adds no
   samples, padding, or future-dependent tail.
6. **Normalization isolation:** center/scale are fixed constants; no fixture or
   target member can influence them.
7. **Index continuity:** gaps, overlap, reorder, or a changed source start are
   refusals, not silently repaired.
8. **Legacy comparator separation:** optional offline outputs are descriptive
   only and cannot be selected as the causal result.

## Alternatives Considered

| Alternative | Why it is not the v0 registered path |
|---|---|
| Keep MNE defaults | Explicitly noncausal and whole-recording dependent. |
| MNE minimum-phase FIR | Potentially valid later, but filter length, startup history, passband delay, and version behavior add another candidate-selection problem. |
| Forward MNE IIR call | MNE documents causal forward IIR, but an array-level SOS state API is more explicit for chunk/resume equivalence. |
| `resample_poly` | The convenience result is centered/zero-phase and boundary padded. |
| General rational streaming resampler | Valuable for portable EEG rates, but unnecessary for the exact 1,000-to-100 Hz path and materially expands state. |
| Online running median/IQR | Changes the feature representation over time and requires a separate adaptation claim. |
| No filtering before decimation | Risks aliasing and cannot support a meaningful 100 Hz output. |
| Compare decoder accuracy now | Would mix a preprocessing mechanism gate with model/target/consumed-evidence access. |

## Recommendation

Freeze Loop 25 as a two-part target-free synthetic gate:

- development seed `2501` and physically separate qualification seed `2502`;
- 12 items per partition, five channels, 1,024-4,096 source samples;
- six stress families and seven exact chunk schedules;
- ten resume cuts and three future-mutation cuts;
- exact same-host schedule/replay identity plus explicit cross-version numeric
  tolerance;
- strict frequency, timing, state, resource, access, refusal, and claim gates;
- one CPU thread, one worker, 8 MiB total generated artifacts, and zero data,
  target, model, training, network, or RW3 operations.

Do not implement that design from this research note. The exact machine
contract and authorization sentence are in
`docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md` and
`registries/causal_preprocessing_contract.v0.json`.

## Claim Boundary

This research establishes why current preprocessing cannot support a causal or
real-time claim and identifies a testable local alternative. It establishes no
filter quality on a recording, no parity with official Brain2Qwerty v2, no
neural advantage, no text accuracy, no endpointing, no end-to-end latency, no
portable-device support, and no clinical or assistive result.
