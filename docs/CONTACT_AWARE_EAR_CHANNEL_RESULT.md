# Contact-Aware Ear-Channel Adapter Result

Status: **work order 5 complete; one measured synthetic roundtrip consumed**

Date: 2026-08-08

Result registry:
`registries/contact_aware_ear_channel_result.v0.json`

## Order Of Evidence

The synthetic contract was committed at
`c6e216f68a450ac78f7f67501beaf528999626a6` and passed push CI
`31281290300`. The implementation was committed at
`76ccc63bdb62b7695dd12ead6ae629c3ab73bb53` and passed exact-SHA push CI
`31282344300` before the measured roundtrip began. Base Python passed in 16
seconds and Optional Neuro Readers passed in 56 seconds.

Exactly one fixture creation and one metadata-only inspection then ran in an
automatically removed temporary directory. There was no retry, parameter
change, or post-result tuning. Both generated files were measured and removed;
neither is retained in Git or elsewhere in the workspace.

## Measured Result

| Field | Result | Cap |
|---|---:|---:|
| Runtime | 0.40 seconds | 60 seconds |
| Peak RSS | 55,394,304 bytes | 268,435,456 bytes |
| Free disk before execution | 46,367,866,880 bytes | at least 1,073,741,824 bytes |
| Input contract | 15,789 bytes | recorded |
| NPZ payload | 923,980 bytes | combined cap below |
| Metadata sidecar | 14,894 bytes | combined cap below |
| Total generated output | 938,874 bytes | 4,194,304 bytes |
| Temporary files | 2 | 2 |
| Retained generated files | 0 | 0 |

The deterministic payload SHA-256 was
`caf1be67271a3753eb638e78e01fa8cae17154bc306eaff15ae1ed672a4c7051`.
The sidecar SHA-256 was
`da9a2cc90662f5cbd1f29f85b14064998720a8556da6906a9f4c1bbecee15a1e`,
and the canonical embedded metadata SHA-256 was
`ce3aa6bc6e3056ebcb66fad6ce19461a11b9e445cdd1cf064ae26dc02550d931`.
Configuration, source-order, and selected-subset/weight hashes also replayed
exactly.

The payload shape was `[48, 16, 256]`. It retained 168,192 observed source
samples and marked 76,800 samples as both selected and observed in the adapted
transport. The source missing fraction was `0.14453125`; the adapted masked
fraction was `0.609375`. The fixed policy found 504 eligible channel instances
and selected 300: 150 on each synthetic side. Forty-two items passed the
bilateral minimum; all six unknown-contact items selected none and emitted
`insufficient_bilateral_contact`.

The producer is causal at the event boundary for this fixed synthetic window,
with 256 required left-context samples, zero right-context samples, and zero
post-event samples. This is a known-boundary fixture operation. Streaming and
end-to-end latency were not measured.

## Access Ledger

One synthetic payload generation, 48 target-blind per-item policy evaluations,
and one explicit metadata-only inspection occurred. The inspector opened zero
NumPy array members. Raw-data reads, real-cache reads, real or public EEG/MEG
reads, target or label-value reads, adapter imports, feature extraction,
parameter updates, model inference, training, scientific scoring, network or
provider calls, device or hardware operations, and claim upgrades were all
zero.

All 16 malformed-fixture refusals, future-tail invariance, exact replay,
identity, geometry, mask, timestamp, dimension, policy, provenance, hash,
unknown-field, malformed-payload, collision, free-disk, file-count, output,
runtime, RSS, CLI, and cleanup gates passed. Closeout verification includes 35
focused checks and the complete suite at 1,309 tests with 3 expected skips and
469 subtests in 35.01 seconds external wall time at 636,846,080-byte peak RSS.
Ruff, compileall, every registry JSON, root and command help, and diff hygiene
also pass. The repository-wide suite RSS is not the single-fixture RSS.

Warnings remain explicit:

- every channel, side, ring index, contact value, noise value, missing sample,
  and waveform is synthetic;
- normalized contact quality is not impedance;
- zero-filled adapted values remain unavailable under their mask;
- the adapter operates after acquisition and does not control active,
  reference, or ground electrodes;
- ear-centered signals can contain neural and non-neural sources; and
- the cited patent application and open research hardware do not establish
  current consumer-earbud capability or freedom to operate.

## Verdict And Route

All 18 acceptance gates passed. Work order 5 is complete and consumed without
retaining generated output. Work order 6 may now prepare the recovery-bound
Loop 54-A decision surface and qualify a strict parser against synthetic
fixtures only. The real 11,705-byte S20 VHDR open remains a separate Tier C
decision after a green decision packet and green implementation.

Engineering capability added: NeuroDecodeKit can deterministically generate,
hash, validate, inspect, and fail closed on invalid contact, missingness,
bilateral selection, and transport-mask states in a bounded synthetic
ear-channel interface.

Scientific claim not established: no real ear EEG hardware signal, brain
origin, decoding accuracy, generalization, end-to-end latency, device
performance, home use, or clinical result was established.
