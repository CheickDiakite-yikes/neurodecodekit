# COMM-L0 Metadata Authorization Packet

Date: 2026-08-27

Status: **All authority false; queued request only**

Machine request:
`registries/communication_eeg_source_identity_metadata_authorization_request.v0.json`

Packet ID: `COMM-L0-META`

## Why this is the next communication gate

The communication program cannot freeze a real cohort until it knows the exact
OpenNeuro `ds003626` snapshot tree and whether the preregistered all-participant,
peripheral-preserving slice actually exists below 10 GiB. COMM-L0's strict
canonicalizer and selector have already passed their sole generated
qualification and are remotely green.

This packet asks for no EEG payload. It proposes one metadata response that can
freeze source identity, aggregate participant/session structure, and the hash
and byte size of the bounded prospectively selected raw-session manifest. It
cannot inspect BDF headers, channels, events, targets, or signal samples.

## Immutable proof anchors

Generated engineering closed at proof commit
`4acd82bcc460f3e7a7668ec3c1c6a49c8d964aca`, which passed Base Python job
`98409242950`, Optional Neuro Readers job `98409242802`, and CI
`33039371687`. The machine request binds 20 exact program, registration,
amendment, implementation, result, proof, and test artifacts totaling 156,361
bytes.

The frozen request is exactly one direct HTTPS `POST` to
`https://openneuro.org/crn/graphql`. Its 322-byte GraphQL query has SHA-256
`04bdf1ed30fc7bc48ac4a96cb7b93ca6651133856844aad07b92b8b38cc006cc`.
Its canonical 361-byte JSON body has SHA-256
`db465645cdea29b3fdca3fd70e742b15a1dc3732d8f8900775b595871ab68a20`.

## Requested ordered stages

This request grants no authority now. If it later becomes the sole active Tier
C packet and receives a fresh packet-bound decision, the order is:

1. Implement a standard-library transport wrapper with only generated bodies
   and injected mock responses. It must have no active real command.
2. Qualify strict request identity, TLS, redirect/proxy/retry refusal, bounded
   reading, response-shape refusal, consumed-marker ordering, no-clobber
   publication, secure cleanup, and aggregate-only inspection.
3. Commit and push the exact wrapper and generated result; require both remote
   CI jobs green.
4. Commit and push a separate activation that binds those exact green
   artifacts; require both remote jobs green.
5. Execute one irreversible metadata invocation. Exclusively create and fsync
   the permanent consumed
   marker before constructing the real opener. Make the exact request once,
   read at most 16,777,216 response bytes, canonicalize in memory, select by the
   frozen rule, retain one private no-clobber manifest, and publish one
   aggregate result.

The same remotely green decision artifact must be hash-bound by M1, M2, and M3.
Success or failure consumes the one real invocation. There is no retry, rerun,
fallback query, alternate snapshot, participant drop, session substitution, or
post-response change to the selection rule.

## Exact transport and output boundary

- verified system TLS;
- `Accept: application/json`, `Content-Type: application/json`, and
  `Accept-Encoding: identity`;
- no authentication, cookie, proxy, redirect, retry, range, resume, fallback,
  pagination, variable, or alternate endpoint;
- one direct HTTP 200 response at the exact final URL;
- exact application headers plus deterministic `Host` and `Content-Length`, a
  60-second socket timeout, a 240-second monotonic real-operation deadline,
  and 60 seconds of reserved shutdown, cleanup, and receipt-publication
  headroom inside the 300-second process-tree watchdog;
- reject any `Content-Encoding` other than absent or `identity`;
- strict UTF-8 JSON with the already-qualified exact schema;
- raw response bytes hashed but never persisted;
- invocation root
  `data/communication_eeg/ds003626-v2.1.2/comm-l0-meta/`;
- durable marker `comm-l0-meta-consumed.v0.json`, private manifest
  `selected-source-manifest.v0.json`, and invocation-unique private `.tmp-*`
  entries only inside that ignored root;
- marker mode `0600`, exclusive no-follow descriptor-relative creation,
  file-plus-parent fsync, exact proof-binding fields, preexisting-marker
  refusal, and permanent retention outside every cleanup path;
- public result
  `registries/communication_eeg_source_identity_metadata_result.v0.json`;
- permit exactly one invocation-nonce public-result temporary file beside that
  final result in the verified `registries/` parent; create it descriptor-
  relatively with `O_CREAT|O_EXCL|O_NOFOLLOW`, mode `0600`, and verify its open
  descriptor still names the expected inode before promotion;
- refuse before marker creation if that public path already exists or its
  repository-relative parent is not a no-symlink directory chain;
- after every post-marker success or failure route, publish one aggregate
  result by descriptor-relative `os.link()` from a same-parent temporary file
  to the final name, fail on `EEXIST`, unlink the temporary name, and fsync the
  file and parent directory;
- generated qualification must create the destination after preflight but
  before promotion, then prove the existing file remains byte-identical, the
  new receipt is not substituted, and the consumed marker remains permanent;
- retain that result outside cleanup; every failure receipt must include its
  route, warning, unavailable fields, and measured counters;
- one private manifest, mode `0600`, at most 1 MiB, containing only canonical
  metadata needed for later acquisition;
- one public aggregate result at most 1 MiB containing counts, byte totals,
  hashes, route, warnings, and unavailable fields, with no path, URL, version
  ID, command, target, trial, or participant outcome; and
- cleanup limited to invocation-created private temporary files and that exact
  inode-verified public-result temporary file.

## Resource envelope

| Resource | Frozen maximum or requirement |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 0 |
| Wall time | 300 seconds |
| Peak process-tree RSS | 256 MiB |
| Metadata POST requests | exactly 1 |
| Request-body bytes | exactly 361 |
| Metadata response body | 16 MiB maximum |
| BDF payload requests / bytes | 0 / 0 |
| Private manifest | 1 MiB maximum |
| Public output | 1 MiB maximum |
| Combined retained manifest + public result | 2 MiB maximum |
| Atomic staging peak | 4 MiB maximum |
| Incremental disk | 8 MiB maximum |
| Required free disk | 10 GiB |
| Redirects / retries / reruns | 0 / 0 / 0 |

The existing 20 GiB total research allowance and 10 GiB selected-raw ceiling
are unchanged. This metadata packet consumes neither allowance beyond its 8 MiB
temporary/output envelope. Before creating the marker, the wrapper must verify
at least 10 GiB plus 8 MiB free within the invocation filesystem.

The frozen router is `COMM-L0-META-R1` only when transport, strict JSON,
snapshot identity, recursive-tree validation, all-ten participant/session
selection, privacy, publication, and resource gates all pass. Transport,
schema, snapshot, tree, selection, privacy/publication, and resource failures
route respectively to `F01` through `F07`. Every route consumes the invocation;
no partial response, manifest, or aggregate result is success.

## Explicit exclusions

This packet does not authorize implementation, generated execution, activation,
network access, response reading, private-manifest writing, or any real
operation now. Its proposed future scope excludes every BDF or other dataset
payload request; header, channel, geometry, sample, event, annotation, target,
label, sentence, command, trial-count, or class-balance read; cache, split,
feature, derivative, checkpoint, model, training, inference, prediction,
delivery, score, provider, language model, stream, device, hardware, release,
publication, or claim operation.

It may not displace `DREYER-C5R-1-HL`, which remains the sole active Tier C
packet with all authority false. It may not touch another project or clean up
the unrelated tracker inspection file.

## Decision boundary

The request and a separate proof-only closeout must become remotely green.
Even then, `COMM-L0-META` remains queued until the active Dreyer gate is closed
or parked and the maintainer explicitly activates this exact packet. Only a
fresh packet-bound decision after that transition can authorize M1; that same
decision must be hash-bound through M2 and M3.

Engineering capability proposed: freeze a real, peripheral-preserving
communication cohort identity and bounded acquisition manifest without reading
neural content or adapting selection to outcomes.

Scientific claim not established: no real EEG, communication decoding,
unseen-person generalization, EEG-beyond-peripheral effect, replication, live
operation, hardware performance, or clinical value is tested by this request.
