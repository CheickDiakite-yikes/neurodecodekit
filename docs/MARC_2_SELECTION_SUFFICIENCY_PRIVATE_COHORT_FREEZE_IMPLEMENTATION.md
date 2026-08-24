# MARC2-VR39P Selection-Sufficiency Private Cohort Freeze Implementation

Date: 2026-08-23

Lane: `MARC2-VR39P`

Status: **Generated Stage 1 qualified once; remote implementation proof pending**

Machine records:

- `registries/marc2_selection_sufficiency_private_cohort_freeze_implementation.v0.json`
- `registries/marc2_selection_sufficiency_private_cohort_freeze_result.v0.json` after the sole qualification

## Decision Proof

Packet-bound decision `dbde5f84b3fac0ac0b23208afd56e00d678aff00`
passed CI `32681510484`, Base Python job `97298894039`, and Optional Neuro
Readers job `97298894171` before implementation began.

## Independent Fixed-Path Wrapper

The standard-library module is
`neurodecodekit.datasets.marc2_selection_sufficiency_private_cohort_freeze`.
It imports only unchanged VR33A readiness and unchanged VR38A
selection-sufficiency interfaces. It does not import or call a consumed private
executor.

The CLI has only fixed `plan`, `qualify`, `inspect`, and `execute` commands.
There is no path, URL, output, task, count, threshold, rank, cap, route, nonce,
retry, resource, or provider override.

## Generated State Machine

The generated matrix is frozen at 21 cases, PPP and FFF readiness, canonical
and reversed source order, and two exact replays: 168 paths total. The expected
measured totals are 168 VR33A calls, 504 provider calls, 336 sleeper calls, 84
source constructions and no-follow content opens, 84 unchanged VR38A calls,
64 cohort writes, 64 R1 routes, and 104 R2 routes. The six other non-PPP
readiness patterns are separate named witnesses.

Every generated case creates a mode-0700 temporary output root and mode-0600
consumed marker before readiness. The output-root directory descriptor and
device/inode identity remain pinned through all writes. Readiness gates source
construction. Every non-marker output is canonicalized and cap-checked before
the first non-marker write. The completion marker is last and binds hashes of
the consumed marker, readiness certificate, optional private manifest, public
report, and public route. Each case directory is removed before the next case,
and generated output retention is zero.

## Private Manifest And Public Firewall

Successful generated fixtures exercise the future private transformation for
all cohort sizes from 12 through 19. The transformation independently checks
the maximal target-free rank-prefix decision, fit session `ses-01`, held-out
session `ses-02`, runs 1-3, four required companion types, split separation,
subject and bundle arithmetic, row provenance, and compressed/uncompressed
storage limits. It removes generated provenance, binds raw and canonical source
hashes, preserves the real selection-identity hash, and recursively rejects any
remaining generated or fixture marker.

The private commitment is domain-separated HMAC-SHA-256 over the canonical
manifest without its commitment envelope. The 32-byte key is private. The
verifier checks the exact scheme, domain, nonce encoding, stored digest, public
digest, and recomputed digest with constant-time comparison.

The public report has exactly eleven fields. Its commitment scheme is constant
on R1 and R2; only R1 carries a 64-character lowercase commitment. Every R2 is
byte-identical. R1 reports differ only by the commitment. Inspection rebuilds
the expected report and rejects any extra field, altered constant, route/value
mismatch, malformed proof anchor, or incomplete state binding.

## Sole Generated Qualification

The one registered invocation passed:

```text
paths:                         168
VR33A / provider / sleeper:    168 / 504 / 336
source constructions / opens:  84 / 84
VR38A calls:                    84
temporary cohort writes:        64
R1 / R2 routes:                 64 / 104
direct refusals:               268
named critical classes:        12
source mutations:                0
retained output bytes:            0
```

Every expected VR38A route appeared with exact counts G1/G2/R1/R2/R3 of
36/32/8/4/4. The two replay signatures matched. Not-ready paths constructed no
source and called VR38A zero times.

Measured resources:

```text
fixed tracked input:          374,043 bytes
generated input:           37,159,376 bytes
cumulative temporary writes:16,623,104 bytes
peak live output:             313,627 bytes
peak temporary case:          755,606 bytes
aggregate result:               4,841 bytes
runtime:           12.816678500035778 seconds
peak RSS:                  67,158,016 bytes
CPU / workers / jobs:          1 / 1 / 1
network / new payload:         0 / 0 bytes
raw/cache/model/training:      0 / 0 / 0 / 0
```

The cumulative write count is throughput across isolated temporary cases, not
simultaneous storage. Each case was removed before the next; peak live output
was 313,627 bytes and retained output was zero. The qualification may not be
repeated.

## Qualification Capture Procedure

The sole qualification ran once in a fresh process under the registered
one-thread environment. Its canonical JSON return was captured outside the
repository. The measured return was copied once into the tracked result registry
with `qualification_invocations: 1` and
`qualification_may_be_repeated: false`. Tests inspect that record; they never
rerun qualification.

Before the invocation, focused tests, the complete dependency-light suite,
Ruff, compilation, JSON validation, and `git diff --check` passed. After the
result was recorded, those gates run again. The implementation and result are
then committed, pushed, and remotely green. A separate proof-only closeout
registry must itself be committed, pushed, and remotely green before private
`execute` or `inspect` can pass their first proof check.

Engineering capability added: an independently validated, terminal,
selection-sufficiency cohort-freeze state machine with source-bound private
provenance, secret-keyed commitments, exact public firewalls, and crash-safe
completion semantics.

Scientific claim not established: Stage 1 opens no private inventory, archive
member, neural signal, target, model, prediction, or score and therefore proves
no neural effect, decoding accuracy, movement intention, unseen-person
generalization, or live decoding.
