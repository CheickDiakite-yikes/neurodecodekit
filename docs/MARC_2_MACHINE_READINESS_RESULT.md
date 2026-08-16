# MARC2-VR4 Machine-Readiness Result

Date: 2026-08-16

Lane: `MARC2-VR4`

Route: `MARC2RDY-G1`

Status: **One machine-only readiness closeout passed; certificate is transient
and grants no private authority; no structural cohort, payload, target, model,
prediction, or score was accessed**

Registry: `registries/marc2_machine_readiness_result.v0.json`

## Proof Order

The generated/readiness implementation was committed and pushed as
`9fdda316441fef4f245544c90dc0a373993140e0`. That exact commit passed Base
Python job `95213934048`, Optional Neuro Readers job `95213934126`, and CI
`31967145837` before the machine command ran.

The implementation's frozen predecessor registration remained:

```text
commit:             3af2e3d654b91c13aefce76e74b38ae19b2a3d6f
CI:                 31965823863
Base Python:        95210732393
Optional Readers:  95210732329
contract SHA-256:  93d63b273809f05608aaa18f9a52611d6073110e74b3c62ae5cf08d756b6b191
```

## Measured Result

One `readiness` invocation ran under the exact all-one numerical thread
environment. It took three samples over 10.009114208 monotonic seconds:

| Sample | One-minute load | Logical CPUs | Normalized load | Peak RSS | Free disk |
|---:|---:|---:|---:|---:|---:|
| 1 | 6.5048828125 | 12 | 0.5420735677 | 18,055,168 bytes | 158,862,835,712 bytes |
| 2 | 6.30419921875 | 12 | 0.5253499349 | 18,055,168 bytes | 158,862,741,504 bytes |
| 3 | 5.79931640625 | 12 | 0.4832763672 | 18,055,168 bytes | 158,861,668,352 bytes |

All three samples passed the frozen limits:

```text
normalized load:  <= 1.0
peak RSS:         < 268,435,456 bytes
free disk:        >= 16,106,127,360 bytes
sample interval:  >= 5 seconds
passing tail:     3
```

The command wrote one mode-`0600`, 4,551-byte certificate with SHA-256
`5c268ffaefe6e557ace92214c6ec3bab6db29d0a89dee4c83ebd94dbf07b522e` at
the fixed Git-ignored path. It was valid from
`2026-08-16T19:21:01.928507Z` through
`2026-08-16T19:26:01.928507Z`. The certificate is now only a closeout artifact;
it must not be treated as fresh authority for a later private executor.

## Access Ledger

```text
machine-readiness checks / certificates:               3 / 1
private path operations:                               0
private content opens / input bytes:                   0 / 0
private output-root operations:                        0
network requests / bytes:                              0 / 0
archive-member reads:                                  0
signal-sample reads:                                   0
event/target/label/onset/channel/geometry reads:        0
real derivative rows:                                  0
training or parameter-update fits:                     0
model inference or prediction sets:                    0
prediction freezes / target deliveries / scores:       0
provider or language-model calls:                      0
hardware or other-project operations:                  0
scientific claim upgrades:                             0
```

No private or cohort path was resolved, statted, opened, read, hashed, or
parsed. No structural selector ran. No archive member or neural payload was
requested. No target, onset, label, model, prediction, or score was opened.

## Next Gate

This result must be committed, pushed, and pass both remote jobs. A separate
all-false Tier C request may then bind one new additive structural executor,
one fresh readiness certificate, one mode-`0600` consumed marker immediately
before one private content open, and the unchanged target-free cohort
invariants.

Because this closeout certificate expires and the fixed writer refuses an
existing destination, that future packet must explicitly bind safe handling of
this exact expired 4,551-byte certificate before requesting a fresh one. It
must not delete, rename, overwrite, or substitute any other file, project, or
consumed root.

A successful future structural pass would freeze cohort identity only. FW2
member acquisition and semantic qualification would still require their own
prospective contract. CIL1 training, prediction freezing, target delivery, and
scoring remain later gates.

## Claim Boundary

Engineering capability added: the exact VR4 implementation produced a
deterministic, bounded, expiring machine-readiness certificate after three
stable real machine samples.

Scientific claim not established: no neural payload, target, prediction, or
score was accessed, so this result establishes no neural effect or decoding
performance.
