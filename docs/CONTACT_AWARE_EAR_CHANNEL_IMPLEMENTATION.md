# Contact-Aware Ear-Channel Adapter Implementation

Status: **implemented and locally qualified; measured synthetic closeout pending
remote-green implementation commit**

Date: 2026-08-08

Frozen contract:
`registries/contact_aware_ear_channel_contract.v0.json`

Implementation receipt:
`registries/contact_aware_ear_channel_implementation.v0.json`

## Added Capability

`neurodecodekit.preprocess.contact_aware_ear_channels` now provides:

- an exact hash-bound registered-contract loader;
- deterministic seed-5505 construction of 48 target-free items with 16 generic
  bilateral channels and 256 strictly pre-event samples at 128 Hz;
- separate source-observed, channel-present, contact-valid, eligible, selected,
  and adapted-observed masks;
- a fixed target-blind policy with stable ranking, at most four and at least two
  selected channels per side, equal side totals, and explicit select-none
  behavior when bilateral contact is insufficient;
- source-preserving weighted transport values whose zero fill remains marked
  unavailable rather than measured or imputed;
- strict source identity, synthetic geometry, reference-state, array, mask,
  policy, causality, warning, unavailable-field, and claim validation;
- deterministic array, configuration, source-order, selected-subset, metadata,
  and compressed-payload SHA-256 bindings;
- a metadata-only inspector that verifies the whole payload hash and ZIP member
  inventory without opening a NumPy array;
- deterministic constructors for all 16 registered refusal classes; and
- bounded exclusive creation, collision refusal, a 1 GiB free-disk preflight,
  a 4 MiB output ceiling, and cleanup limited to a newly created output
  directory if writing fails.

The CLI surfaces are:

```bash
neurodecode make-contact-aware-ear-fixture --help
neurodecode inspect-contact-aware-ear-fixture --help
```

NumPy remains a lazy optional import through the existing `[array]` extra.
SciPy, MNE, scikit-learn, pyRiemann, Torch, hardware SDKs, and model code are
not imported by this implementation.

## Local Verification

The contract milestone passed 1,286 tests with 3 expected skips. The
implementation adds 12 focused tests covering:

- byte-identical replay and exact provenance hashes;
- all eight six-item scenarios and all 16 generic channel identities;
- distinct mask semantics, preserved NaNs in unavailable source samples, and
  explicit zero-filled transport values;
- bilateral count caps, exact side weights, unknown-contact behavior, and
  future-tail invariance;
- every registered refusal mutation;
- forbidden target fields and strict unknown-field rejection;
- metadata-only inspection with zero NumPy array opens;
- payload tampering, malformed NPZ, cap, collision, and low-disk refusals;
- lazy optional imports; and
- CLI create/inspect summary equality.

Before adding the implementation-receipt invariants, the complete suite passed
1,298 tests with 3 expected skips and 469 subtests in 34.82 seconds wall time
at 606,126,080-byte peak RSS. With five receipt invariants included, the final
complete suite passed 1,303 tests with 3 expected skips and 469 subtests in
35.35 seconds external wall time at 614,825,984-byte peak RSS. Complete-suite
RSS is not the future single-fixture execution measurement and is not judged
against the 256 MiB fixture cap.

A disposable development probe produced shape `[48, 16, 256]`, 168,192
observed source samples, 76,800 adapted-observed samples, and a source missing
fraction of `0.14453125`. Forty-two items passed the bilateral policy and six
explicitly selected none. The deterministic NPZ was 923,980 bytes, the sidecar
was 14,894 bytes, and total output was 938,874 bytes. No probe file was
retained.

The probe payload SHA-256 was
`caf1be67271a3753eb638e78e01fa8cae17154bc306eaff15ae1ed672a4c7051`.
Its canonical fixture-metadata SHA-256 was
`ce3aa6bc6e3056ebcb66fad6ce19461a11b9e445cdd1cf064ae26dc02550d931`.
These are deterministic development observations, not the measured closeout
receipt.

## Execution Order

1. Commit and push this implementation and receipt.
2. Require both CI jobs to pass for that exact commit.
3. Create and metadata-inspect one fixture in an automatically removed
   temporary directory using one numerical thread and one worker.
4. Measure wall time and peak RSS, verify every frozen gate, retain only
   aggregate metrics and hashes, and remove both generated files.

A validation, replay, resource, hash, or CLI failure parks work order 5. It
does not permit another measured run, hardware access, a larger architecture,
or a real-data action.

## Boundaries

All channel names, sides, ring indices, quality values, missingness, noise, and
signals are synthetic. This implementation reads no S20, PhysioNet, EEG, MEG,
raw file, real cache, target, label, text, participant identity, checkpoint,
or external embedding. It performs no feature extraction, parameter update,
model inference, training, scoring, network/provider call, stream, device,
physical switching, rereference, interpolation, or hardware operation.

Engineering capability added: NeuroDecodeKit can deterministically generate,
hash, validate, inspect, and reject invalid contact, missingness, bilateral
selection, and transport-mask states in a bounded synthetic ear-channel
interface.

Scientific claim not established: no real ear EEG hardware signal, brain
origin, decoding accuracy, generalization, end-to-end latency, device
performance, home use, or clinical result was established.
