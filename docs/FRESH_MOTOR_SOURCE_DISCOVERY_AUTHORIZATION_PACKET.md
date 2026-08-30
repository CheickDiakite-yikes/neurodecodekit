# Fresh Motor Source Discovery Authorization Packet

Date: 2026-08-29

Packet: `FMSR1-DISCOVERY-M0`

Status: **all authorities false; request pending this exact packet commit and
remote proof; no network access**

Machine request:

- `registries/fresh_motor_source_discovery_authorization_request.v0.json`

## Purpose

This packet requests one future, bounded, metadata-only discovery pass over the
exact official-index universe and exact query grammar frozen by `FMSR1-v1`.
Its sole purpose is to determine whether exactly one public candidate is
eligible for a later candidate-specific target-free metadata packet, or whether
the correct result is `NO_QUALIFYING_SOURCE` or `DISCOVERY_CAP_PARK`.

This packet selects no source and authorizes nothing by itself.

## Exact-Green Predecessor

`FMSR1-v1` is exact-green at commit
`e09f6cc014744485940713c148dacad9dbbe59e3`, Base Python job
`99197577034`, Optional Neuro Readers job `99197577007`, and CI
`33289147031` on GitHub `main`. The additive proof-only closeout in this
milestone binds five artifacts / 47,128 bytes and repeats no protected work.

## Requested Ordered Authority

Only after this packet and its proof are remotely green and the maintainer gives
fresh packet-bound words may a separate decision record activate the following
ordered work:

1. implement a standard-library discovery planner, strict response reader,
   every-hop redirect verifier, canonicalizer, complete pagination ledger,
   deterministic router, aggregate reporter, resource monitor, and CLI;
2. qualify that exact implementation only with generated fixtures and mocked
   network responses, including cap, truncation, duplicate page, pagination
   cycle, redirect, identity, ordering, authority, and retained-field refusals;
3. commit, push, and require both remote CI jobs green for that exact
   implementation; and then
4. execute once, with no retry or rerun, over only the five frozen official
   index surfaces and four exact queries or complete motor/EEG category
   traversal where text search is unavailable.

No implementation or execution is authorized until the separate decision is
remotely green. The future execution is consumed whether it succeeds, parks,
or refuses.

## Frozen Discovery Surface

The exact ordered indexes are:

1. OpenNeuro dataset search;
2. NEMAR dataset search;
3. PhysioNet data index;
4. GigaDB dataset search; and
5. BNCI Horizon 2020 dataset catalogue.

The exact ordered text queries are:

```text
"motor imagery" EEG EOG EMG
"movement intention" EEG EOG EMG
"motor execution" EEG EOG EMG
"hand movement" EEG EOG EMG
```

The implementation record must bind every exact endpoint URL, official
revision, GET or POST method, and scheme/host/port/method allowlist before the
one execution. General web search, search providers, ad hoc candidates, query
changes, authentication, cookies, and private credentials are forbidden.

## Network And Resource Ceiling

- at most 128 total metadata requests;
- increment the request counter before every initial contact, redirect hop,
  pagination request, error-response open, or failed open; all count toward the
  same 128-request ceiling;
- apply separate 32 MiB cumulative ceilings to both wire-body bytes and decoded
  body bytes across every HTTP status, with cap-plus-one streaming used only to
  detect and fail closed at either boundary;
- reject unsupported content encodings before body consumption and retain at
  most 8 MiB of allowlisted public artifacts;
- 300 seconds, 256 MiB peak RSS, one CPU thread, and one worker;
- zero retries, at most 30 seconds per request, and at most three redirects per
  request;
- every redirect hop's scheme, host, port, and resolved method must match the
  exact allowlist before contact; method rewriting is forbidden and the ordered
  redirect transcript is retained;
- complete pagination with every cursor or page identity recorded; and
- zero payload, archive, member, header, range, signal, event, annotation,
  target, label, model, prediction, score, provider, stream, or device bytes.

Any cap breach, truncation, pagination cycle, duplicate page, incomplete index,
off-allowlist hop, unsupported content encoding, unregistered method, or
malformed response yields
`DISCOVERY_CAP_PARK` or a named fail-closed refusal. Partial results cannot be
ranked or selected.

## Candidate Boundary

Canonicalization, metadata eligibility, consumed-source exclusions, total sort
order, joint-control requirements, and storage arithmetic must remain byte-for-
byte equivalent to the exact-green v1 contract. Unknown, missing, ambiguous,
or conflicting is false. The only successful scientific-routing output is one
top `ELIGIBLE_FOR_METADATA_RESEARCH` candidate; `FULL_CONFIRMATION_SOURCE`
cannot be emitted at discovery time.

The public report may contain only aggregate counts, the allowlisted candidate
identity/provenance fields, deterministic route or exclusion, request and byte
counts, runtime, peak RSS, and every warning. It may not retain download URLs,
targets, labels, participant outcomes, or hidden payload properties.

## Explicit Exclusions

This packet does not authorize source-specific metadata, publication reads,
payload URLs, acquisition, opaque transport canaries, sensor headers, real EEG
or peripheral signals, events, annotations, targets, labels, model or
checkpoint access, training, inference, prediction freezing, scoring,
language models or providers, RW3, streams, devices, hardware, release,
deletion, cleanup, another project, rerun, substitution, or scientific-claim
upgrade.

Engineering capability requested: one deterministic, complete-or-park, metadata-only public source-discovery pass with exact network, redirect, pagination, output, CPU, memory, runtime, and retained-field boundaries.

Scientific claim not established: this packet performs no discovery request and accesses no neural measurement, so it establishes no neural advantage, unseen-person generalization, movement-intention decoding, language decoding, live operation, hardware result, or clinical value.
