# DREYER-C5R-1 H-L1R1 Generated Qualification Closeout

Date: 2026-08-29

Status: **passed, consumed, and pending closeout remote green; H-L2 remains
blocked**

The sole registered generated-only qualification `DREYER-C5R-1-HL1R1-Q0`
ran after exact coordinator commit
`0ef634e4852d9f8a18d4b8a1f50e6a1331bd020a` passed Base Python
`99103540731`, Optional Neuro Readers `99103540620`, and CI `33253657120`
on GitHub `main`.

## Result

The qualification passed all 65 frozen cases:

- two byte-identical valid H1 recovery transactions;
- two inherited valid Stage H fixed-header cases;
- all 18 inherited Stage H refusal cases; and
- all 43 ordered H-L1R1 successor refusal cases.

The matrix verified marker-before-capability ordering, exactly one opener and
one request on valid H1, response closure, invocation-contained cleanup, no
staging or unaccepted-payload debris, aggregate H0 behavior after post-marker
failure, no-replace publication, and consumed-rerun refusal. The valid H1
aggregate report SHA-256 was
`a44145a8ffa6d0ff4672635b90088f6781cb1de9b55e3194cd190b68bb867fef`.

## Measured Envelope

```text
registered attempts:                    1 of 1, now consumed
matrix cases:                           65 of 65 passed
runtime:                                0.1789909170474857 seconds
peak process-tree RSS:                  37,699,584 bytes
generated fixture input:                1,452,034 bytes
generated temporary and marker bytes:   162,682 bytes
final public result:                    9,046 bytes
generated input plus output:            1,623,762 bytes
temporary allocated bytes:              372,882 bytes
free disk before / after:               65,651,572,736 / 65,651,560,448 bytes
CPU threads / workers / numerical jobs: 1 / 1 / 0
producer causal:                        unavailable
required context:                       unavailable
end-to-end latency measured:            false
```

The ignored consumed marker is 251 bytes with SHA-256
`b91c3827daa55734046c64b6d98729dccaf8fc85c335f9a7f4536b15cf37a63b`.
The ignored aggregate result is 9,046 bytes with SHA-256
`766ccc9bc760fc6861f3a1b9dd47f135d5d976d0bcefcfff4a8a2cdc792f2e93`.
Neither generated evidence file is committed.

## Access Ledger

The attempt made zero raw-data reads, real-cache reads, real/private path
operations, HTTP requests, network bytes, real EDF payload or header reads,
annotation/signal/target/label reads, model runs, training runs, inference
runs, prediction sets, target deliveries, scores, provider calls,
stream/device/hardware operations, releases, or scientific-claim upgrades.

## Next Gate

This result closeout must become remotely green. After that proof, the next
scientifically useful step is a separate all-false H-L2 activation request for
one exact Dreyer `sub-01` R1 EDF fixed-header observation. H-L2 may not use the
current generated authority: the real EDF remains closed until that later
packet, proof, decision, and exact implementation barriers are green.

Engineering capability added: the corrected one-file recovery wrapper passed
its complete frozen 65-case generated qualification and is now safely consumed.

Scientific claim not established: no real EEG was accessed or tested, so this
result establishes no neural information, decoding, unseen-person,
peripheral-adjusted, live, hardware, or clinical result.
