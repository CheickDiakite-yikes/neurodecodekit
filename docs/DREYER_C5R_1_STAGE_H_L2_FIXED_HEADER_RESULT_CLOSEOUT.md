# DREYER-C5R-1 H-L2 Fixed-Header Result Closeout

Date: 2026-08-29

Status: **sole registered invocation consumed at aggregate `DREYER-H0`; no
retry, rerun, repair, resume, substitution, or reinterpretation is allowed**

Machine result:

- `registries/dreyer_c5r_1_stage_h_l2_fixed_header_result.v0.json`

Machine closeout:

- `registries/dreyer_c5r_1_stage_h_l2_fixed_header_result_closeout.v0.json`

Current frontier:

- `registries/current_research_frontier.v1.json`

Execution ID: `DREYER-C5R-1-HL2-R0`

## Result

Activation commit `e3adab26e867f6de7e56f406f59ede51718b577c`
passed Base Python job `99123725366`, Optional Neuro Readers job
`99123725302`, and CI `33261346763` on GitHub `main`. The invocation bound
activation-record SHA-256
`20e3c55347a88a27ebfe3446ace7ba4ea9f3cb3bee7d0d4fbd63a43db07c22fd`.

The transaction constructed one response and made the sole registered GET,
then refused with sanitized code `HL2-TRANSPORT` before reading any response
body. The aggregate route is `DREYER-H0`.

```text
real HTTP GET requests:                 1
real response opens:                    1
real network body bytes:                0
payload SHA-256 passes:                 0
fixed-header reads / parses:            0 / 0
annotation / signal / target reads:     0 / 0 / 0
model / training / scoring operations:  0 / 0 / 0
runtime:                                0.6479716249741614 seconds
peak process-tree RSS:                  36,454,400 bytes
private allocated bytes:                4,096
accepted payload retained:              false
cleanup complete:                       true
```

## What Can Be Localized

The public artifact proves that the refusal occurred in strict transport
validation after a response was opened and before body streaming. The strict
validator accepts only HTTP 200, the exact final URL, one exact
`Content-Length: 14805604`, no content encoding, and no transfer encoding.

The aggregate artifact intentionally does not retain the server status or raw
headers. Therefore this result cannot distinguish among status drift, final-URL
drift, missing or differing content length, duplicate critical headers,
content encoding, transfer encoding, or an unavailable header interface.
Claiming a more specific cause would invent evidence.

## Scientific Interpretation

No EDF payload byte, fixed header, channel label, sensor role, sampling rate,
geometry, annotation, or signal sample was read. The result says nothing about
whether the Dreyer dataset contains the expected sensors and nothing about the
neural hypothesis. It is a fail-closed transport result, not a biological null.

The frozen stop rule is nevertheless operational: the sole no-retry checkpoint
did not establish an eligible source surface, so `DREYER-C5R-1-HL2` and the
dependent 1.78 GB acquisition/model path are parked. A future scientific lane
must use a newly registered source and transport identity; it cannot reopen or
rename this consumed attempt.

## Storage And Safety

The 14,805,604-byte payload was not downloaded or retained. The public result
is 2,624 bytes. The private transaction marker is reported as 268 bytes; it and
all ignored evidence remain unopened and must not be moved, modified, deleted,
published, or committed.

Engineering capability added: the one-shot H-L2 transaction proved that the activation, marker-first consumption, strict transport firewall, bounded resources, sanitized H0 publication, and invocation-owned cleanup work on a real public endpoint.

Scientific claim not established: no EDF body or header was read, so this result establishes no Dreyer sensor roster, neural information, decoding performance, unseen-person generalization, peripheral-adjusted effect, live operation, hardware result, or clinical value.
