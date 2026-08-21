# MARC2-VR15P Suffix-Identity Private Discriminator Implementation

Date: 2026-08-21

Lane: `MARC2-VR15P`

Status: **Stage 1 generated implementation complete; private stage proof-gated**

Machine record:
`registries/marc2_suffix_identity_private_discriminator_implementation.v0.json`

## Green Decision Boundary

Decision `fc694a69489913198f0a630bbb0edb04c29310f6` passed Base Python
job `96680587357`, Optional Neuro Readers job `96680587199`, and CI
`32451448725` before implementation began.

The implementation validates the exact decision, all-false request, request
proof, all 17 fixed request inputs totaling 308,187 bytes, and the exact VR15A
module and records. It imports no consumed VR13P or VR14P executor.

## Fixed Interface

The standard-library wrapper exposes only:

- `plan`: validate the green packet and report fixed limits;
- `qualify`: run the bounded generated matrix;
- `inspect`: report only tracked implementation-proof state; and
- `execute`: refuse until both exact Stage 1 and proof-closeout remote proofs
  exist, the tracked tree is clean, and the fixed one-shot arm is present.

No command accepts a source path, output path, URL, threshold, route, retry,
resume, fallback, substitution, or arbitrary execution override.

## Generated State Machine

Each of the 68 registered paths writes one generated 1,227-row source into an
invocation-created temporary directory, reads it once with no-follow semantics,
strict-parses it, calls VR15A once, writes one aggregate marker and report, and
removes that path directory. Both source orders and both exact replays agree.

The matrix performs exactly 68 VR15A calls and therefore 68 unchanged nested
VR12A calls. G1 and R1-R16 each occur exactly four times. The generated input
total is 29,199,868 bytes; peak temporary footprint is 429,857 bytes; retained
output is zero.

## Proof Hardening

`execute` checks remote implementation proof and remote proof-closeout proof
before readiness collection, private preflight, or a private content open. It
also requires a clean tracked tree and an exact one-shot environment arm.
The initial implementation registry intentionally stores both remote proof
fields as null, so all ordinary tests and CLI calls stop at `MARC2VR15P-F10`
without touching `.codex_work`.

This addresses the earlier VR13P pre-proof test incident: an uncommitted proof
edit cannot pass the tracked-clean check, and the private stage remains closed
until the later proof records are committed, pushed, and remotely green.

The deterministic test replay injects the frozen measured 50,135,040-byte RSS
value so it does not inherit the complete test runner's historical high-water
mark. Separate direct refusal cases exercise the exact 256 MiB boundary; the
production CLI still reads and enforces live process peak RSS. Thirty focused
tests pass, and the dependency-free complete suite passes 4,456 tests with 80
expected skips locally.

## Private Stage Still Closed

The private path, readiness path, output root, consumed marker, structural
source, and any consumed prior output were not checked, listed, statted,
resolved, hashed, opened, read, written, or deleted during Stage 1.

The later registered command may read only the exact 418,755-byte target-free
structural source once and emit only one aggregate R1-R16 route. It cannot
freeze a cohort. Archive members, neural payloads, targets, models,
predictions, scores, FW2, and CIL1 remain closed.

Engineering capability added: a fixed proof-gated wrapper can deterministically
exercise all sixteen suffix-identity classes without retaining generated data.

Scientific claim not established: generated qualification accessed no neural
payload, target, prediction, or score and establishes no neural effect or
decoding performance.
