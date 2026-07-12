# Loop 25 Anti-Alias Audit

Date: 2026-07-12

Status: **Preauthorization design audit; no coefficients, fixtures, or numeric
preprocessing were created**

Authoritative amendment:
`docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md`

Machine contract: `registries/causal_preprocessing_contract.v1.json`

## Verdict

The original Loop 25 v0 registration is not strong enough to authorize.

It correctly separated the proposed causal path from the official offline
path, but it treated a fourth-order 0.5-45 Hz Butterworth task filter as the
anti-alias filter for 10x decimation. Its only above-Nyquist gate checked 60 Hz
at -6 dB. That leaves almost the complete 50-500 Hz source folding band
unbounded and cannot establish that energy above the new 50 Hz Nyquist will
not fold into the 0-50 Hz output.

The official dependency chain confirms that the public 0.5-45 Hz setting and
resampling are separate operations. Loop 25 therefore needs a separate causal
anti-alias stage and a full folding-band gate before either synthetic seed is
opened.

## Exact Evidence Chain

The audit follows executable source rather than inferring behavior from one
configuration line.

1. The official Brain2Qwerty v2 configuration declares `MegExtractor`,
   `frequency=100`, `filter=(0.5, 45.0)`, `notch_filter=50`,
   `RobustScaler`, and clamp 5.
2. The official dataset code imports `MegExtractor` from NeuralSet.
3. The official dependency manifest pins NeuralSet 0.2.2, MNE 1.11.0, and
   SciPy 1.14.1.
4. NeuralSet 0.2.2 applies notch filtering, then bandpass filtering, then a
   separate `raw.resample(...)`, then scaling.
5. MNE 1.11.0 documents `Raw.resample` as applying anti-aliasing when needed.
   Its default method is complete-signal FFT resampling.
6. MNE's resampling tutorial describes the default as a frequency-domain
   brick-wall anti-alias operation at the new Nyquist frequency and warns that
   manual decimation needs sufficient pre-decimation attenuation.

The result is important but narrow: the public upstream path has a separate
anti-aliasing operation. It is still offline and cannot be copied into a
zero-lookahead runtime.

### Source Identities

| Source | Frozen identity | Relevant fact |
|---|---|---|
| Brain2Qwerty | commit `3bf5a4099ca0d23bbe994b2287905760236e56e0` | Public v2 configuration and dependency pins |
| `brain2qwerty_v2/data.py` | blob `e0270e9e63aca4ba13950306dbf08f37c887d720`; SHA-256 `6afaff41eb107454120aac99b1ff0b6cd796a7735d78fd1fa971764a275f4408` | Imports NeuralSet `MegExtractor` |
| Brain2Qwerty `pyproject.toml` | blob `b669c64967ca7cfde62c7dbf3df917739a09bd52`; SHA-256 `d70988a152b21bbd3354ce210fe6e1fb716acec8a86d973661af6155b6fb034f` | Pins NeuralSet 0.2.2, MNE 1.11.0, SciPy 1.14.1 |
| NeuralSet | tag `v0.2.2`, commit `02bd64b93d5b1cfc785e6fd576b40fad27556765` | Exact extractor implementation |
| NeuralSet `neuro.py` | blob `d2747b37c6f5a356dc638782be7244482edce54f`; SHA-256 `503d854548ad57e36beea2838b75fb7b4d31ecd2cf2c8fcb190f17128ce3e7c1` | Calls filter and resample as separate stages |
| MNE | tag `v1.11.0`, commit `6f6802c54b85c38effb0b3cca7f3f96ea4a1e109` | Pinned resampling behavior |
| MNE `io/base.py` | blob `314f981dcaf2fc7b58e37bedd02f604e392a4912`; SHA-256 `f1e116dd1c86bba5c16947f4e2f2495b9be5467f4e08594153729b396294d0ed` | `Raw.resample` defaults to FFT and invokes MNE resampling |
| MNE `filter.py` | blob `8d5d3e48ea7f89eb6b5e6b56ee7270f3f9949269`; SHA-256 `48e4971ff601f77d45956881b03e3f282be32cd716190eb7a8743fb4778c2fb1` | FFT and polyphase implementations |

Primary links:

- [Brain2Qwerty v2 configuration](https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/xp_config.py)
- [Brain2Qwerty dependency manifest](https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/pyproject.toml)
- [NeuralSet 0.2.2 MNE extractor](https://github.com/facebookresearch/neuroai/blob/v0.2.2/neuralset-repo/neuralset/extractors/neuro.py#L334-L381)
- [MNE 1.11 `Raw.resample` source](https://github.com/mne-tools/mne-python/blob/v1.11.0/mne/io/base.py#L1304-L1424)
- [MNE filtering and resampling tutorial](https://mne.tools/stable/auto_tutorials/preprocessing/30_filtering_resampling.html)

## Why 50-500 Hz Matters

The source rate is 1,000 Hz, so its Nyquist frequency is 500 Hz. After keeping
one sample in ten, the output rate is 100 Hz and its Nyquist frequency is 50
Hz. Every source frequency from 50 through 500 Hz can fold into the retained
0-50 Hz band.

For a source frequency `f`, the registered alias destination is:

```text
abs(((f + 50) % 100) - 50)
```

Examples:

| Source frequency | Output alias destination |
|---:|---:|
| 50 Hz | 50 Hz |
| 55 Hz | 45 Hz |
| 60 Hz | 40 Hz |
| 75 Hz | 25 Hz |
| 99 Hz | 1 Hz |
| 100 Hz | 0 Hz |
| 149 Hz | 49 Hz |
| 250 Hz | 50 Hz |
| 499 Hz | 1 Hz |
| 500 Hz | 0 Hz |

A 60 Hz probe alone covers only one of these collisions. A -6 dB threshold
also allows half-amplitude contamination at that one frequency. It says
nothing about 50.5 Hz, 99 Hz, 100 Hz, or the repeated folding zones through
500 Hz.

## Why The Official Resampler Is Not The Causal Replacement

The official extractor calls MNE's default FFT resampler. MNE documents two
properties that make it unsuitable for this gate's runtime:

- the default treats the complete signal as one block;
- the frequency-domain result is not localized to only past samples.

That is valid offline preprocessing. It does not meet Loop 25's zero-right-
context and resumable-state requirements. The amendment uses the official
path only to establish that anti-aliasing is a separate responsibility, not as
a numeric identity target.

SciPy's `resample_poly` also centers a symmetric FIR result and uses boundary
padding. SciPy's `decimate` applies anti-aliasing, but defaults to zero-phase
processing and does not expose the exact chunk-resume state contract required
here. Neither convenience function is selected as the streaming primitive.

## Candidate Review

| Candidate | Strength | Reason not selected for v1 |
|---|---|---|
| MNE FFT resample | Strong offline brick-wall behavior | Complete-signal and noncausal |
| Centered polyphase FIR | Finite support and established multirate method | Centering, padding, and delay compensation use future context in the convenience path |
| Long causal FIR | Fixed delay and transparent state | Sharp 45-50 Hz transition at 1,000 Hz adds a materially larger history and delay contract |
| Default causal Chebyshev decimator | Established small IIR anti-alias baseline | Its default 40 Hz edge changes the public 45 Hz boundary and still needs an explicit state wrapper |
| Dedicated elliptic SOS | Sharp explicit pass/stop constraints with bounded state | Selected, with mandatory ripple, ringing, pole, phase, and dense-response reporting |

SciPy documents `iirdesign` as producing a minimum-order IIR filter from
explicit passband loss and stopband attenuation requirements, and recommends
SOS output for numerical stability. SciPy also documents the cost: elliptic
filters achieve a fast transition using ripple in both bands and can ring more
in the step response. The amendment exposes those costs instead of hiding
them.

Primary links:

- [SciPy `iirdesign`](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.signal.iirdesign.html)
- [SciPy elliptic filter tradeoffs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ellip.html)
- [SciPy stateful SOS filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html)
- [SciPy `decimate`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.decimate.html)

## Superseding Design

The amended causal chain is:

```text
finite float32 [5, time] at exactly 1,000 Hz
  -> float64 computation
  -> stateful 50 Hz notch SOS
  -> stateful fourth-order 0.5-45 Hz Butterworth bandpass SOS
  -> stateful dedicated elliptic anti-alias SOS
       passband edge: 45 Hz
       maximum passband loss: 1 dB
       stopband edge: 50 Hz
       minimum designed stopband attenuation: 60 dB
  -> keep absolute source indices 0, 10, 20, ...
  -> apply frozen center/scale and clamp +/-5
  -> float32 [5, time] at exactly 100 Hz
```

The exact anti-alias design call is registered as:

```python
scipy.signal.iirdesign(
    wp=45.0,
    ws=50.0,
    gpass=1.0,
    gstop=60.0,
    analog=False,
    ftype="ellip",
    output="sos",
    fs=1000.0,
)
```

No call has been made in this audit. The future authorization permits one
design call, followed immediately by coefficient and pipeline hashing.

## Static Gate Before Seed Access

The v0 sequence opened development seed 2501 before coefficient design. The
amendment reverses that order.

After separate authorization, the future runner must:

1. validate contract, source, environment, and API bindings;
2. design the exact coefficients once;
3. bind coefficient, section-order, pipeline, and state hashes;
4. run pole, dense response, alias-map, impulse, and step checks;
5. park immediately with both partitions unopened if any static check fails;
6. inspect the fixture manifest only after the static filter passes;
7. open seed 2501 once and continue the unchanged development gate;
8. open seed 2502 once only after a frozen complete development pass.

This ordering is both more scientific and cheaper. A structurally bad filter
cannot consume the development partition and cannot reach qualification.

## Full Folding-Band Gate

The future static audit uses 65,537 inclusive linearly spaced frequencies from
0 through 500 Hz. It checks the dedicated anti-alias stage and the complete
notch-bandpass-antialias cascade separately.

Required results:

- dedicated anti-alias response from 0-45 Hz stays between -1 dB and 0 dB,
  within the registered numerical edge tolerance;
- dedicated anti-alias response from 50-500 Hz is no greater than -59.5 dB;
- complete-chain response at 5, 10, 20, and 35 Hz stays between -3 and
  +0.5 dB;
- complete-chain response from 50-500 Hz is no greater than -59.5 dB;
- every registered alias source probe maps to its exact output destination and
  has source gain no greater than -59.5 dB;
- all poles are inside the unit circle and no pole magnitude exceeds
  0.999999;
- impulse and step responses are finite;
- impulse peak, step overshoot, ringing, and frequency-dependent delay are
  reported, not silently summarized as one latency number.

The 45-50 Hz interval is an explicit transition band. It has no passband
claim. A future result must disclose that the causal replacement can alter
that interval even though the public offline configuration names 45 Hz.

## Time Semantics

Three times must stay separate:

| Time | Meaning |
|---|---|
| Sample-grid timestamp | `source_start + source_index / 1000` for kept source indices |
| Earliest availability | Not earlier than arrival of the kept source sample; computation and transport are not included |
| Effective signal time | Unavailable as one scalar because IIR delay depends on frequency |

Zero right context means no future sample is read. It does not mean zero phase
delay, zero computation time, or measured capture-to-text latency. No delay
compensation is allowed.

## Measured Activity In This Audit

| Operation | Count |
|---|---:|
| Filter design or coefficient generation | 0 |
| Synthetic fixture generation | 0 |
| Development partition opens | 0 |
| Qualification partition opens | 0 |
| Numeric preprocessing runs | 0 |
| Real data/cache/consumed evidence reads | 0 |
| Target/label/text/prediction reads | 0 |
| Checkpoint/model/training operations | 0 |
| RW3/stream/socket/device/hardware operations | 0 |

Only public source text and local registration metadata were read.

## Claim Boundary

This audit proves that v0's anti-alias evidence was incomplete and records a
stronger protocol before execution. It does not prove that the amended filter
will pass, that its phase or ringing is acceptable for neural decoding, that
it preserves official offline outputs, that it retains neural information, or
that it improves CER/WER. It measures no end-to-end latency and establishes no
portable-device, assistive, medical, or clinical result.
