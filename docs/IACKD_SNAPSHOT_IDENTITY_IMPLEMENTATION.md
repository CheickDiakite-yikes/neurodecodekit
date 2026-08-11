# IACKD-M1 Snapshot Identity Canonicalizer Implementation

Date: 2026-08-11
Status: generated fixture qualified; exact implementation remote proof pending
Scientific value: none

## Preconditions

The prospective contract in
`registries/iackd_snapshot_identity_contract.v0.json` was committed as
`1667e302e262ad23695f204a88d5a0997ac38270`. CI run `31481270697` passed Base
Python job `93746523491` and Optional Neuro Readers job `93746523322` before
implementation began.

No dataset-specific OpenNeuro response, S3 object, local IACKD path, retained
bundle, EEG sample, event, trajectory, target, derivative, model, prediction,
or score was accessed during this implementation.

## Implemented Interface

`src/neurodecodekit/datasets/iackd_snapshot_identity.py` is a standard-library
generated-response canonicalizer with:

- strict UTF-8 and duplicate-free JSON parsing, including rejection of BOM,
  controls, `NaN`, infinity, and overflowed finite-number syntax;
- exact top-level, snapshot, description, and file-row schemas;
- safe NFC relative POSIX paths, lowercase Git object IDs, canonical sizes,
  and exactly one versioned public S3 URL per file;
- separate canonical hashes for the snapshot anchor, recursive tree, selected
  acquisition manifest, and critical metadata projection;
- exact reconciliation of 1,679 tree rows, 1,340 selected rows, 15
  participants, 30 participant-hand units, 128 runs, and all twelve role
  count/byte summaries;
- a private selected manifest containing individual content identities and a
  separate aggregate public report that rejects path, URL, and version-ID
  leakage;
- 37 ordered fail-closed mutation classes, two deterministic canonical
  replays, one-thread enforcement, runtime/RSS/output caps, exclusive atomic
  output, and metadata-only inspection; and
- a module CLI with only `qualify` and `inspect`. It has no URL opener, socket,
  HTTP client, provider credential, real endpoint, local IACKD path, or
  `--execute` mode.

The constructed selected-path set is byte-for-byte equal as a set to the 1,340
paths in the committed historical metadata inventory. Synthetic object IDs,
version IDs, sizes within each role, and snapshot `hexsha` remain constructed;
they are interface fixtures, not claims about a current public response.

## Measured Generated Qualification

One bounded generated qualification ran under five explicit one-thread
environment controls:

| Measurement | Result | Cap |
| --- | ---: | ---: |
| Constructed response bytes | 531,067 | 2,097,152 |
| Recursive file rows | 1,679 | exactly 1,679 |
| Declared recursive bytes | 7,966,799,433 | exactly 7,966,799,433 |
| Selected rows | 1,340 | exactly 1,340 |
| Declared selected bytes | 7,249,113,684 | exactly 7,249,113,684 |
| Deterministic replays | 2 | exactly 2 |
| Refusal mutations passed | 37 | exactly 37 |
| Runtime | 0.8887734590098262 s | 30 s |
| Peak RSS | 38,436,864 bytes | 268,435,456 bytes |
| Aggregate report bytes | 3,664 | combined cap below |
| Private manifest bytes | 423,128 | combined cap below |
| Combined generated output | 426,792 bytes | 1,048,576 bytes |

Generated input SHA-256:
`3059505bcc0d8a22d1f3c1d350fce16b20b3272dc32854945667c1c0ccfd20b3`

The four constructed canonical hashes were:

- snapshot anchor:
  `285c3572db47bba9bc643dfe4aae8d5896fe6a51d8acbc2177724d1bc885f075`
- recursive tree:
  `d80c144c94d012268cf49bbf371cbcb6623454e19c41b8370eab37ab5f1e94b5`
- selected manifest:
  `8036479b54d542921cc69cccf0189febbae69bec69700364e2cd4d017e49b1cc`
- critical metadata:
  `82ddbc46832f71588130a3e3746410d9a1e025b9068921ffd5160fa3af0ae7c3`

The measured aggregate report SHA-256 was
`4b36d92bf3fb30fcbb6039f725d4959665c31d6691c029d5b98e302d3bdda00a`;
the private generated manifest SHA-256 was
`cbd540afb5cd17507115f83d122ab984a4ca0d685c9fb0258784edea44a73020`.
The final output and one earlier development-smoke output remain untracked in
OS temporary storage because cleanup was not approved. Together they occupy
853,584 bytes and contain generated metadata only.

Every network, dataset-specific response, S3 body, local IACKD path,
old-bundle, signal, event, trajectory, target, training, inference, prediction,
freeze, delivery, score, retry, rerun, and claim-upgrade counter was zero.

## Qualification Boundary

The implementation validates deterministic mechanics only. Its constructed
`IACKDM-R1` route does not establish that the current OpenNeuro snapshot is
compatible. A future public audit needs a new all-false Tier C request, a fresh
packet-bound maintainer decision, a separately qualified real transport
wrapper, and one no-retry response after each prior milestone is remotely
green. That audit still would not authorize an EEG payload.

The current or any earlier `continue` is not retroactive authorization for a
public GraphQL request. Do not use the consumed IACKD-2/IACKD-2R roots, inspect
the changed root body, or reopen either consumed attempt.

Engineering capability added: a dependency-free, adversarially qualified
canonicalizer can reduce a generated snapshot response into separate snapshot,
tree, selected-manifest, and critical-metadata identities with bounded private
and public outputs.

Scientific claim not established: generated metadata and zero neural or target
reads establish no neural effect, action decoding, brain-specific origin,
generalization, language or thought decoding, real-time operation, hardware
capability, assistive benefit, home use, or clinical utility.
