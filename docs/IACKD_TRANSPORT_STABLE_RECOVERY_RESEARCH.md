# IACKD-T1 Transport-Stable Recovery Research

Date: 2026-08-11

Status: **Tier A protocol research complete; no public dataset request, local
IACKD path operation, model operation, target delivery, or score authorized**

Registry:
`registries/iackd_transport_stable_recovery_research.v0.json`

## Question

Can the consumed IACKD-2 transport failure be repaired without weakening
content identity, changing the registered scientific design, or learning from
an EEG, trajectory, target, prediction, or outcome?

Yes, prospectively. The repair is to separate HTTP message framing from object
content identity. It is not a rerun or amendment of the consumed invocation.

## Observed Boundary

The sole IACKD-2 stream invocation opened one public metadata response and
stopped at `IACKD2-F08` before reading its body. The response status and final
URL passed. The exact executor required `Content-Length: 1178`; that header was
absent or numerically different, and the implementation intentionally did not
retain which. It then performed zero body reads, semantic parses, selected
payload requests, signal reads, target reads, fits, predictions, or scores.

The consumed result therefore contains one transport observation and no
scientific observation. Its private invocation root and the older retained
IACKD bundle remain forbidden. Nothing in this research reopens either one.

## Primary-Source Findings

1. [RFC 9110, section 8.6](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6)
   defines `Content-Length` as a decimal representation length and, when a
   representation is transferred as content, as framing information. It does
   not define the field as a cryptographic content identifier.
2. [RFC 9112, sections 6.2-6.3](https://www.rfc-editor.org/rfc/rfc9112.html#section-6.3)
   permits response bodies framed by a valid `Content-Length`, chunked transfer
   coding, or connection close. A response can therefore be valid without a
   `Content-Length` field. Ambiguous `Transfer-Encoding` plus `Content-Length`
   is a separate framing hazard and should fail closed here.
3. Python's standard-library
   [`HTTPResponse.read(amt)`](https://docs.python.org/3/library/http.client.html#http.client.HTTPResponse.read)
   reads at most the requested number of response-body bytes. That supports a
   cap-plus-one overflow check without buffering an unbounded body.
4. Python's
   [`HTTPRedirectHandler`](https://docs.python.org/3/library/urllib.request.html#urllib.request.HTTPRedirectHandler)
   is replaceable, so a no-redirect opener can preserve the exact final-URL
   gate.
5. [OpenNeuro's retention documentation](https://docs.openneuro.org/policy/data_retention.html#content-integrity-assurance)
   describes snapshot replication and content-addressed git/git-annex objects,
   while its [API documentation](https://docs.openneuro.org/api.html#obtain-dataset-file-trees)
   exposes versioned file-tree sizes. These are useful source-inventory anchors
   but do not replace a bounded local body hash.
6. [Amazon S3 integrity documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html)
   distinguishes explicit checksums from transport metadata. S3 also documents
   that an ETag is not necessarily a whole-object MD5 for multipart uploads.
   The recovery must therefore retain the registered ETag as an identity
   anchor while computing its own full-stream SHA-256.

No `ds006840` URL, OpenNeuro object, local IACKD path, or retained private
artifact was requested, resolved, statted, opened, or hashed for this research.

## Architectural Correction

### Small metadata bodies

For the exact four already registered metadata bodies, identity is decided
only after a bounded read:

```text
exact requested/final URL
  + HTTP 200
  + no redirect
  + identity content encoding
  + accepted unambiguous framing profile
  + observed bytes == registered bytes
  + SHA-256(observed bytes) == registered SHA-256
  = accepted metadata content identity
```

The accepted framing profiles are:

- `fixed_length`: one valid decimal `Content-Length` and no
  `Transfer-Encoding`;
- `chunked`: exact case-insensitive `Transfer-Encoding: chunked` and no
  `Content-Length`; or
- `close_delimited`: neither field is present and the standard-library reader
  reaches a clean end of response.

For metadata only, a valid `Content-Length` that is within the per-body cap but
differs from the registered content length is recorded as a warning, not used
as the content verdict. The bounded read still has to return the exact
registered bytes and SHA-256. In practice, a false framing length can still
cause the HTTP client to return too few or too many bytes, which then fails the
body gate.

The following always refuse before semantic parsing:

- malformed, negative, comma-joined, or repeated-looking `Content-Length`;
- both `Content-Length` and `Transfer-Encoding`;
- a declared length above the per-body cap;
- any transfer coding other than one exact `chunked` token;
- compressed representation content;
- redirect, non-200 status, or changed final URL;
- body overflow, underflow, read exception, byte-count drift, or SHA drift; or
- a second read, retry, substitution, or unregistered source.

Each body is read with `registered_size + 1` as the hard call-level limit and
discarded after one strict semantic parse. Across the four bodies, the exact
registered content is 595,400 bytes and the cap-plus-one allowance is 595,404
bytes. The existing 8 MiB metadata network ceiling remains unchanged.

### Large selected objects

The 1,340 selected objects remain stricter because the declared size is also a
resource-allocation guard. Each future payload response still requires exact
URL, status, `Content-Length`, registered ETag, identity encoding, exact
observed bytes, one full-stream SHA-256, and no redirect, transfer coding,
retry, or substitution. ETag is not promoted into a universal cryptographic
claim; it is retained as one registered source identity field alongside the
observed size and locally computed SHA-256.

### Scientific protocol

No scientific field changes. A future recovery must bind the exact IACKD-2:

- 15 participants and 30 participant-hand units;
- congruent-to-incongruent and incongruent-to-congruent arms;
- role-aware 26-channel predictive EEG policy with HEOG, VEOG, Trigger, M1,
  and M2 excluded from prediction;
- causal `[-1.0, 0.0]` second, 0.5-4 Hz primary representation;
- fixed fit/final run split, 30 ms motion guard, and every registered control;
- 660 parameter-update fits and 900 target-blind prediction sets;
- one aggregate prediction freeze that is remotely green before one combined
  final-target delivery and score; and
- the unchanged `IACKD2-R0` through `IACKD2-R5` router and claim ceiling.

If implementing the transport correction would require changing any item in
that list, the recovery must park and a new scientific preregistration is
required.

## Proposed Evidence Order

1. Freeze and remotely green a new IACKD-T1 contract.
2. Build a dependency-free transport validator and qualify every framing and
   mutation path using generated bodies and mocked responses only.
3. Commit, push, and remotely green that exact implementation.
4. Prepare an all-false Tier C request that binds the unchanged IACKD-2
   scientific contract and the new transport implementation.
5. Identify that sole remotely green packet to the maintainer.
6. Only after a fresh packet-bound decision is committed, pushed, and remotely
   green may a distinct real executor be integrated and qualified.
7. Only after that exact executor is remotely green may one new public stream
   be considered under its own no-retry consumed marker.

The current `continue` authorizes Tier A/Tier B progress under the Research
Autonomy Charter. It cannot authorize a packet that does not yet exist and is
not retroactive permission for step 6 or 7.

## Why This Moves The Needle

The prior stop was not a neural-model failure. It was a mismatch between a
transport header and a content-identity role. Fixing that distinction is the
minimum architecture needed to make one already-preregistered, cue/action-
dissociating EEG experiment reachable again without weakening its hashes,
controls, target firewall, or one-shot score.

Engineering capability added: a source-grounded transport/content separation
is specified for a future bounded, hash-verified recovery.

Scientific claim not established: no public dataset body, EEG, event,
trajectory, target, model, prediction, or score was accessed, so this research
establishes no neural effect or decoding result.
