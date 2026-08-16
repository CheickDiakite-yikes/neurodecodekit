# MARC2-VR4 Machine-Stable Structural Recovery Preregistration

Date: 2026-08-16

Lane: `MARC2-VR4`

Status: **Frozen generated-only contract; implementation may begin only after
this exact registration is committed, pushed, and both CI jobs are green; no
private path or structural pass is authorized**

Contract:
`registries/marc2_machine_stable_structural_recovery_contract.v0.json`

## Objective

Qualify one standard-library machine-readiness certificate without allowing a
transient load condition to consume the future private evidence pass. The
certificate is machine state only. It contains no path, participant, member,
payload, signal, event, target, model, prediction, or score.

The later private executor remains a separate implementation and Tier C gate.
This contract does not implement or authorize it.

## Bound Predecessors

VR3 result commit `a186486fcb3dfb2b6d3a743f180b7ac2fa0b4dd3` passed Base
Python job `95208692240`, Optional Neuro Readers job `95208692213`, and CI
`31964995980`. It consumed at `MARC2VDR-F01` before every output-root and
private-path operation.

Machine-stable research commit
`4c0b0dc5acf56cff5089992a8bcd9954aa532fe5` passed Base Python job
`95209752585`, Optional Neuro Readers job `95209752567`, and CI
`31965424149`. The research freezes the order `VR4 -> FW2 -> CIL1` but grants
no authority.

## Stage A Surface

The generated-only implementation may expose:

```text
plan
qualify
inspect --certificate <generated-certificate>
readiness
```

`plan`, `qualify`, and `inspect` operate only on generated fixtures. The
`readiness` command may observe the current process and repository filesystem
but may write only one fixed mode-`0600` readiness certificate under:

```text
.codex_work/marc2_machine_readiness/vr4/readiness.v0.json
```

It may not accept a path, root, threshold, interval, sample-count, wait,
participant, split, or cap override. It may not contain an execute command,
private source constant, archive reader, neural reader, target interface,
trainer, predictor, freezer, or scorer.

## Readiness Algorithm

The exact command must:

1. require `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`,
   `VECLIB_MAXIMUM_THREADS`, and `NUMEXPR_NUM_THREADS` to equal `1`;
2. require at least one logical CPU;
3. sample one-minute load, process peak RSS, and free disk;
4. compute normalized load as one-minute load divided by logical CPUs;
5. require normalized load `<= 1.0`, peak RSS `< 256 MiB`, and free disk
   `>= 15 GiB`;
6. require three consecutive passing samples separated by at least five
   seconds;
7. wait at most 600 seconds and take at most 121 samples;
8. report every exact value, threshold, timestamp, and refusal reason;
9. bind implementation commit and contract SHA-256; and
10. expire the certificate 300 seconds after its final passing sample.

A timeout or refusal may write the same bounded readiness certificate with
`ready=false`. It performs zero private or scientific operations and consumes
no future private content open.

The eventual private executor must verify a fresh `ready=true` certificate in
the same fixed location, then perform its own immediate thread, disk, and RSS
check. It must not use normalized load as a second opaque consuming gate. The
one irreversible boundary remains a new mode-`0600` marker immediately before
one private content open.

## Generated Qualification

Generated qualification must cover:

- ready on the third passing sample;
- fail-then-three-pass recovery;
- timeout with no passing run;
- exact threshold boundary values;
- non-finite, negative, regressing-time, missing-CPU, and thread-drift inputs;
- deterministic replay and canonical certificate bytes;
- certificate expiry, identity, mode, symlink, and output-cap refusals; and
- all 36 ordered mutations across `MARC2RDY-F00` through `MARC2RDY-F05`.

All generated fixtures must be removed. A generated `ready=true` certificate
has no authority over a private executor.

## Caps

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
maximum wait:                            600 seconds
minimum sample interval:                5 seconds
maximum samples:                        121
generated qualification runtime:        30 seconds
peak RSS:                               256 MiB
certificate/output:                     64 KiB
incremental disk:                       1 MiB
network/private/archive bytes:          0
```

## Future Private Boundary

After exact Stage A implementation and one measured readiness closeout are
remotely green, a separate all-false Tier C packet may propose a new additive
private executor and root. It must preserve the exact 418,755-byte source,
1,227 rows, 238 bundles, dynamic `195 + 43`, one VR2 call, target-free
selection, 8 GiB reservation, one thread, and zero payload boundary.

That future packet must authorize one marker and one content open, not an
opaque machine state. No current or earlier `continue` is retroactive authority
for it.

## Claim Boundary

Engineering capability specified: a deterministic readiness certificate can
separate transient machine state from a later one-shot structural evidence
operation.

Scientific claim not established: this contract contains no neural payload,
target, prediction, or score and establishes no neural effect or decoding
result.
