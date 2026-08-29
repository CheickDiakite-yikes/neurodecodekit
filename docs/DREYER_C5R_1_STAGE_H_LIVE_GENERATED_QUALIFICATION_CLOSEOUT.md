# DREYER-C5R-1 H-L1 Generated Qualification Closeout

Date: 2026-08-28

Status: **consumed and rejected; H-L2 remains blocked**

The sole registered generated/mock H-L1 attempt ran after decision commit
`de6cf80f4bd243e7e60a6933445d0a65291abb90` passed Base Python
`99041680696`, Optional Neuro Readers `99041680703`, and CI
`33230243142`. It used generated EDF bytes and an injected opener only.

## What Worked

The run completed two deterministic H1 wrapper replays, one aggregate H0
header-geometry route, 17 wrapper mutation refusals, and the inherited Stage H
matrix of two valid cases plus 18 refusals. Marker-before-opener ordering,
one opener and request per successful replay, response closure, parser
restoration, and no-replace implementation were observed.

The run took 0.2434542920673266 seconds at 31,916,032-byte peak RSS over
321,538 generated input bytes. Its raw 2,371-byte receipt has SHA-256
`85ecd170ec9d618da2f004d3f5595a5cc03ba3b3f1ed0950e8f983281d6945fc`.

## Why It Failed Acceptance

The raw executor labeled itself passed, but the required post-run safety audit
found an untested failure-ordering defect. The wrapper creates its staging
directory and then constructs the opener before entering the cleanup
`try/finally`. A generated opener-construction refusal therefore produced:

- sanitized refusal `HL1-TRANSPORT`;
- the durable consumed marker, as required;
- a leftover invocation-owned staging directory; and
- no aggregate H0 result.

That violates the frozen invocation-scoped cleanup and aggregate-publication
controls. The stricter acceptance decision overrides the raw self-report.
H-L1 R0 is consumed and cannot be rerun, repaired in place, or used to create
an H-L2 activation.

## Access Ledger

The qualification and post-run reproduction made zero real or private path
opens, HTTP requests, network bytes, EDF payload or header reads, annotation or
signal reads, target or label reads, model or checkpoint opens, training or
inference runs, predictions, target deliveries, scores, provider calls,
device operations, releases, or claim upgrades. H-L2 has not been consumed.

## Next Gate

Freeze this failed source and receipt, then prepare an additive generated-only
H-L1 successor that moves all post-marker setup inside one cleanup boundary
and proves the complete mandatory case matrix. Because the registered H-L1
qualification allowance is consumed, a successor qualification needs its own
exact packet and remotely green decision. No real EDF access is appropriate
before that successor passes and receives a separately green activation.

Engineering capability added: the one-shot generated audit caught and
localized a pre-network cleanup defect before it could touch real data.

Scientific claim not established: no real EEG was accessed or tested, so no
neural information, decoding, unseen-person, peripheral-adjusted, live,
hardware, or clinical result was established.
