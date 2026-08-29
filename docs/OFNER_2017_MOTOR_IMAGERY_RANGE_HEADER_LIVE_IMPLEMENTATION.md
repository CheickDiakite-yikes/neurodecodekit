# Ofner 2017 Range-Only Header Live Implementation

Date: 2026-08-29

Packet: `OFNER-C6R-1-HL`

Status: **generated-qualified implementation; remote-green proof required before activation**

Machine record:

- `registries/ofner_gdf_header_live_implementation.v0.json`

Generated result:

- `registries/ofner_gdf_header_live_generated_qualification.v0.json`

## What Was Added

The additive standard-library wrapper in
`src/neurodecodekit/datasets/ofner_gdf_header_live.py` exposes four bounded
surfaces through `src/neurodecodekit/ofner_gdf_header_live_cli.py`:

1. `plan` inspects the exact activation-locked member and range schedule;
2. `qualify` performs the sole generated/mock qualification;
3. `execute` remains unusable without an exact separately green activation;
4. `inspect` validates an aggregate terminal result under the 1 MiB cap.

The wrapper reuses the remotely qualified Ofner manifest selector and GDF 2.x
header parser byte-for-byte. It does not add a second parser, a payload cache,
an event reader, a signal reader, or a model path.

## Exact Live Firewall

The live capability remains locked behind fresh proof of the exact decision,
implementation, and activation commits plus both named CI jobs. It also
requires a clean tracked checkout at the activation commit, one-thread
environment variables, at least 2 GiB free disk, RSS below 256 MiB, an absent
public result, and an absent no-clobber consumed marker.

Only after those checks does the wrapper durably write and sync the unique
private consumed marker. The verified-TLS opener is then constructed with an
empty proxy map, no redirect handler, no cookie or credential state, no retry,
and `Accept-Encoding: identity`.

The exact success schedule is:

1. one in-memory GET of the pinned `nm000173` `v1.0.3` manifest;
2. canonical identity verification after deleting only each row's volatile
   `url` field;
3. exact selection of participant 1, run 1 by path, size, declared SHA-256,
   and stable URL;
4. one `bytes=0-255` request;
5. one `bytes=256-(declared_header_length-1)` request; and
6. one complete-header semantic parse with no trailing bytes.

No manifest body, signed URL, GDF range body, or raw header is retained or
published. The full 105,365,484-byte GDF is never requested or hashed.

## Generated Qualification Result

The sole registered generated qualification passed on its first invocation:

| Measurement | Result |
|---|---:|
| Deterministic wrapper replays | 2 |
| Mock requests per replay | 3 |
| Named adversarial refusals | 35 |
| Generated input bytes | 244,228 |
| Runtime | 0.19265995896421373 seconds |
| Peak process RSS | 40,435,712 bytes |
| Network bytes | 0 |
| Retained generated payload bytes | 0 |

The refusal matrix covers proof drift, remote-main drift, missing resource
caps, low disk, RSS, nonfinite time, symlinked private state, prior consumption,
output collision, manifest identity and target-like fields, redirect-equivalent
URL drift, encoded or chunked responses, duplicate lengths, truncation,
non-byte bodies, wrong range status and `Content-Range`, multipart ranges,
GDF version, channel roster, and sampling-rate drift.

The two accepted generated replays produced the same aggregate measurement
contract, issued the same manifest-plus-two-range schedule, wrote the consumed
marker before opener construction, closed all three responses, and retained no
generated body.

## Terminal Semantics

After the marker is durable, every outcome is terminal:

- `OFNER-H1`: the exact 24,832-byte GDF 2.x header satisfies the frozen 96-
  channel, 512 Hz representation contract;
- `OFNER-H0-REPRESENTATION`: valid range transport produced a header that does
  not satisfy the frozen representation; or
- `OFNER-H0-TRANSPORT`: the source identity, HTTP transcript, body, or resource
  firewall refused before a valid complete header existed.

No route permits a retry, rerun, repair, resume, fallback, or substitution.
`OFNER-H0-TRANSPORT` has no biological interpretation. `OFNER-H1` would permit
only a later full-cohort acquisition preregistration.

## Remaining Barrier

This implementation and generated result must now be committed, pushed to
GitHub `main`, and pass both Base Python and Optional Neuro Readers. A separate
activation record must then bind that exact green implementation and itself
become remotely green. Until then, the real command is structurally present
but proof-locked and no NEMAR request is available.

Engineering capability added: an activation-locked, range-only, no-retention
wrapper can verify one exact public GDF fixed-header representation under
strict proof, transport, resource, and publication controls.

Scientific claim not established: generated mock qualification is not EEG
evidence and establishes no neural effect, EEG beyond EOG or kinematics,
unseen-person generalization, movement intention, motor-cortex causation,
thought or language decoding, live decoding, hardware result, or clinical
utility.
