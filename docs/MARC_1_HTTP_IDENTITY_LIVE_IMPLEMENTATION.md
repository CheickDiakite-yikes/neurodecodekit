# MARC-1 HTTP Identity Live Recovery Implementation

Date: 2026-08-12
Lane: `MARC1-HT1A`
Status: generated/mock wrapper qualified; real metadata remains closed until
this exact implementation commit passes both required remote CI jobs

## Same Path, Repaired Gate

This work is not a pivot. The research endpoint remains defensible,
non-invasive thought-to-text. MARC-1 is the control and attribution rung needed
to distinguish a genuine neural contribution from cue timing, eye movement,
muscle activity, and overt movement before stronger language experiments can
be interpreted honestly.

The prior metadata invocation failed before semantic parsing because its
transport wrapper required a literal `Content-Encoding: identity` response
header. HTTP permits an uncoded representation when that header is absent. The
green MARC1-HT1 semantics lane corrected that overly narrow assumption without
loosening the body cap, redirect policy, source schema, cohort rule, target
firewall, payload boundary, or one-shot execution rule.

This implementation applies that correction to a new additive live wrapper.
It does not reopen, import, call, modify, inspect, or reuse the consumed
`MARC1-P1A` executor or its private root.

## Green Authorization Basis

The standards-aligned request passed both required jobs first:

```text
request commit:          27f39aee5f056eafc81b615cec4a178a41a6c5d2
request CI:              31586256906
Base Python:             94080678529
Optional Neuro Readers:  94080678738
request SHA-256:         9d2249005a9cfe3437c0914f471cdc830c2967da25291964cc29357c8d5091f8
```

The separate decision records the maintainer's exact fresh message and also
passed both jobs:

```text
decision commit:         9c7bd48541fbcebabcb9a783cb9047c7f2a2f57a
decision CI:             31587195405
Base Python:             94083644849
Optional Neuro Readers:  94083644932
decision SHA-256:        949050b5c5369bc802e7015fd2c03a279dad15e88d5ab575189f547808a554ce
```

That decision authorizes generated/mock wrapper implementation and, only after
this exact wrapper is remotely green, one bounded target-free metadata
selection. It does not authorize a payload request, signal read, target read,
model operation, score, retry, rerun, or scientific claim upgrade.

## Additive Surface

The new module is:

```text
src/neurodecodekit/datasets/marc1_http_identity_live.py
```

It imports the Python standard library, the green HTTP-identity semantics
module, and the frozen target-free selector. An AST audit requires both allowed
imports and refuses any import of
`neurodecodekit.datasets.marc1_pilot_selection_live`. The module has no archive
reader, decompressor, EDF reader, signal reader, target interface, model,
scorer, credential argument, alternate endpoint argument, or payload command.

The CLI exposes four fixed commands:

```text
python -m neurodecodekit.datasets.marc1_http_identity_live plan
python -m neurodecodekit.datasets.marc1_http_identity_live qualify --output-dir PATH
python -m neurodecodekit.datasets.marc1_http_identity_live inspect REPORT
python -m neurodecodekit.datasets.marc1_http_identity_live execute [green-proof fields]
```

`execute` accepts only the future exact implementation commit, CI run, two job
IDs, and implementation-registry SHA-256. The data path, provider, endpoint,
record, version, cohort, and split cannot be changed from the command line.

## Corrected Transport Contract

The request remains one unauthenticated `GET` to the fixed Figshare v3 files
endpoint. Proxy discovery and automatic redirects are disabled. At most two
bodyless HTTPS redirects are permitted, and every redirect host must resolve
only to globally routable addresses. There are at most three total attempts.

For every redirect and the terminal response:

- absent `Content-Encoding` means the bytes are uncoded and is accepted;
- one case-insensitive `identity` token is accepted;
- empty values, lists, duplicates, and every actual coding are refused;
- `Transfer-Encoding` is refused;
- decoding and decompression operations remain exactly zero; and
- no raw header, terminal URL, or body is published or persisted.

The terminal response must be status `200`, JSON, and no larger than 2 MiB.
An optional decimal `Content-Length` must be within the cap and equal the
observed cap-plus-one body read. The observed byte count and raw-response hash
are provenance only; the frozen semantic schema remains the acceptance gate.

## Input, Selection, And Privacy

The private Freewill input remains the exact sealed 418,755-byte mode-`0600`
manifest with SHA-256
`2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031`.
A future execution may perform one no-follow validation, one bounded content
open, one SHA-256 pass, and one strict JSON parse. It may not resolve or open a
member, sibling, local header, or archive payload.

The Wrist response must contain exactly 55 frozen-schema rows: 45 unique
`sub-01.zip` through `sub-45.zip` participant archives and ten safe
supplementary basenames, totaling exactly 3,683,416,050 declared bytes. The
known `sub-01` ID, size, and MD5 remain fixed. Any target-like extra field,
name mismatch, duplicate, URL mismatch, checksum mismatch, count mismatch, or
byte mismatch refuses without fallback.

The target-free selector binds 12 preregistered participants per axis, 72
Freewill run bundles, 288 Freewill core members, 12 Wrist archives, and 300
private rows. Selection may use only source identity, lexical participant
identity, numeric session/run identity, completeness, and declared size after
selection. It may not use an event, target, response, signal quality value,
prediction, score, or outcome.

The new invocation root is fixed at:

```text
.codex_work/marc1_http_identity/live_recovery_v0
```

The old consumed root
`.codex_work/marc1_pilot_selection/live_selection_v0` is lexically refused
without statting or opening it. A future machine gate must pass before the new
root or consumed marker is created. Once the marker exists, any success or
failure consumes the sole invocation.

## Generated Qualification

The measured generated-only qualification covered four accepted response
forms: absent encoding, lowercase identity, uppercase identity, and mixed-case
identity after two redirects. All four produced byte-identical selection
identities. Thirty-one adversarial mutations covered private-input integrity,
source schema, target leakage, transport framing, actual encoding, duplicate
encoding, old-root access, public privacy, and forbidden target operations.

```text
route:                              MARC1HTL-G1
generated input bytes:                 892,922
accepted response cases:                     4
acceptance gates:                         21 / 21
mutations refused:                        31 / 31
selected private rows:                         300
aggregate report bytes:                     8,951
private manifest bytes:                    206,509
combined output bytes:                     215,460
internal runtime:                          0.2482517089229077 sec
reported peak RSS:                        52,117,504 bytes
external wall time:                        0.37 sec
external maximum RSS:                     53,002,240 bytes
real/network/forbidden counter sum:                 0
```

Output identities:

```text
aggregate report SHA-256: 05940c3c655d31a8a73524f9774cb4c0b7ae4df69ae4b288a4a2f44a57f13a05
private manifest SHA-256: 70570ff568d54acee9fafd3d5df08498977c09fde82646b3689da3b567305f08
```

The disposable outputs were inspected inside a temporary directory and
removed automatically. No generated output is committed, and the generated
route has no scientific value.

## Verification And Next Gate

The focused behavior suite passes 21 tests and 19 subtests. It
covers proof identity, one-thread resource gates, no-follow private reads,
strict Wrist parsing, target leakage, accepted and refused encoding states,
redirects, all 31 required mutations, deterministic replay, output caps,
public privacy, mocked one-shot success and consumed failure, CLI planning,
AST import isolation, and old-root refusal.

The implementation record freezes this exact source, test, document, decision,
semantics proof chain, measured qualification, resource caps, and zero-access
counters. Its 12 tests bring the focused total to 33 tests and 23 subtests.
All 457 MARC tests pass in 5.637 seconds at 96,731,136-byte external peak RSS.
The dependency-light suite passes 2,596 tests with 204 expected skips in
22.559 seconds at 297,320,448-byte external peak RSS. The optional-neuro suite
passes 2,667 tests with 35 expected skips in 59.423 seconds at 797,769,728-byte
external peak RSS. Both complete suites add exactly 33 tests and zero skips
over the green decision baseline.

Repository-wide Ruff, compilation, all 183 registry JSON parses, module CLI
help, one generated CLI qualify/inspect roundtrip, and `git diff --check` pass.
The CLI roundtrip again passed all 21 gates and 31 refusals with zero access
counters and removed its temporary outputs. The exact implementation commit
must now be pushed and both required CI jobs must be green before the sole real
metadata invocation is eligible.

Passing that future metadata selection would establish only a valid,
target-free acquisition plan for the same MARC-1 positive-control program. A
separate prospective Tier C packet would still be required before any selected
EEG payload is acquired or interpreted.

Engineering capability added: a standards-aligned, proof-gated metadata
wrapper can safely bind the same preregistered MARC-1 pilot without reopening
the consumed executor or weakening its privacy and resource controls.

Scientific claim not established: this generated qualification used no human
signal, target, prediction, or score and establishes no neural effect, language
decoding, or thought-to-text capability.
