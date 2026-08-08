# Local EEG Tooling Audit

Status: **Complete at the zero-network environment-capability boundary**

Date: 2026-08-08

This audit answers one narrow question before NeuroDecodeKit adds dependencies:
which useful EEG library surfaces already work in the current local Python
environment under one-thread, zero-network, data-free probes?

It does not inspect an EEG file, qualify a dataset, load a checkpoint, run a
model, or score an outcome.

## Evidence Order

1. Commit `e1de855f8767840c04e719bade616ba7a22514ed` added the dependency-light
   inspector, CLI command, isolated import probes, output cap, and eight tests.
2. Push CI run `31277731869` passed for that exact commit. Base Python completed
   in 16 seconds and Optional Neuro Readers completed in 49 seconds.
3. Only after that green run, one local audit wrote the 9,416-byte report at
   `registries/local_eeg_tooling_audit_result.v0.json`.
4. The raw report is bound by
   `registries/local_eeg_tooling_audit_receipt.v0.json` at SHA-256
   `1466d1c19fdd80cf8f478677df7746c9d7ef1aa625120c2ca1a4b9b27a506f80`.

## Measured Result

| Surface | Installed version | Probe result | Current use |
|---|---:|---|---|
| NumPy | `2.5.0` | `ndarray` and `asarray` available | Ready for bounded arrays and fixture generation |
| SciPy | `1.18.0` | `signal.butter` and `linalg.eigh` available | Ready for deterministic signal and spectral mechanics |
| MNE | `1.12.1` | BrainVision reader and ICA available; CSP unavailable in this environment | Ready for a later separately authorized reader/QC stage, not needed for the next synthetic step |
| scikit-learn | unavailable | No import probe executed | Classical adapter contract can be built first; no install is justified yet |
| pyRiemann | unavailable | No import probe executed | Defer until a bounded classical comparison is registered |
| MOABB | unavailable | No import probe executed | Defer until the public acquisition and benchmark protocol are separately authorized |
| Braindecode | unavailable | No import probe executed | Defer until classical positive controls justify a compact neural comparison |

The MNE CSP surface being unavailable is consistent with the missing
scikit-learn layer, but this audit did not perform a dependency-root-cause
investigation and does not claim one.

## Resource And Access Accounting

- Runtime: `14.52799025` seconds.
- Parent peak RSS: `25,083,904` bytes.
- Maximum isolated-child peak RSS: `173,211,648` bytes.
- Retained report: `9,416` bytes under a `1,048,576`-byte cap.
- Workers and configured numerical threads: `1`.
- Distribution metadata queries: `7`; isolated import probes: `3`.
- MNE created one `290,596`-byte cache file inside a disposable audit home; the
  temporary directory was removed when the probe ended.
- Network attempts blocked: `0`; successful network operations and downloads:
  `0`.
- Real/protected reads, raw-signal reads, target/label reads, model loads,
  training, inference, scoring, provider calls, and device/hardware operations:
  all `0`.

One MNE probe emitted 63 bytes to its captured terminal stream. The report
retains only byte count and SHA-256
`cace1071573ef725e762e8856427937617c8c67e5d0784c45c0e854e56a803a8`,
not terminal text or local paths.

Input byte volume is unavailable because distribution metadata lookup and
Python imports do not expose a stable byte-read counter. Dataset compatibility,
real signal quality, model accuracy, neural advantage, and device compatibility
also remain unavailable.

## Decision

Do not install a broad EEG stack yet. The next work order builds deterministic
motor, timing, ocular, line-noise, dropout, and channel-corruption fixtures with
the already-ready NumPy/SciPy core. Classical, Riemannian, benchmark, and compact
neural adapters remain optional interfaces until their own bounded gates make an
install useful.

The 23,248,224-byte PhysioNet prospect remains unopened. S20 remains
uninterpreted. Neither this audit nor its next synthetic work order authorizes a
download, protected read, target, model run, training run, scoring event, or
hardware action.

Engineering capability added: NeuroDecodeKit can now inventory a fixed local
EEG tool matrix through isolated, sanitized, zero-network probes with measured
resource and access accounting.

Scientific claim not established: library availability establishes no EEG
quality, neural effect, decoding accuracy, generalization, latency, portable
hardware, home-use, or clinical result.
