# MARC2-VR39P Terminal Private Cohort Freeze Authorization Packet

Date: 2026-08-23

Lane: `MARC2-VR39P`

Status: **All-false Tier C request; no implementation or private access authorized**

Machine request:

- `registries/marc2_selection_sufficiency_private_cohort_freeze_authorization_request.v0.json`

## Why This Is The Scientific Gate

Remotely closed generated-only VR38A proved that the unchanged target-free
selector can preserve the same scientific core when optional runs above the
required first three vary. It accepts a maximal contiguous participant-rank
prefix from 12 through 19 participants under the frozen 8 GiB reservation cap
and refuses required-run, taxonomy, companion, split, and storage defects.

VR38A proof closeout `a599adf3e0320ad420e1c2f5647a0432e645c246`
passed Base Python job `97278761357`, Optional Neuro Readers job
`97278761303`, and CI `32673882729`. That closes the generated repair. It does
not establish that a real cohort exists and it authorizes no private read.

The next useful question is binary: can the exact real target-free inventory
freeze a scientifically valid cohort, or must the Freewill/CIL1 lane stop? A
further topology label would not answer that question and is prohibited.

## Requested Two-Stage Sequence

### Stage 1: generated/mock fixed-path wrapper

Only after a fresh packet-bound decision is committed, pushed, and remotely
green, implement an independent standard-library wrapper with fixed `plan`,
`qualify`, `inspect`, and `execute` commands. Generated qualification must use
only injected temporary paths, readiness providers, nonce providers, and
generated VR38A sources. It must exercise:

- both VR38A success routes at every cohort size from 12 through 19
  participants;
- required fit-run and held-out-run failures;
- one taxonomy-or-companion failure;
- one minimum-prefix reservation failure;
- one uncompressed-payload-ceiling failure;
- ready and not-ready states, canonical and reversed source order, and two
  exact replays.

That is 168 fixed paths: 168 VR33A calls, 504 provider calls, 336 sleeper
calls, 84 unchanged VR38A calls, 64 generated cohort writes, 64 public R1
routes, 104 public R2 routes, at least 200 direct refusals, exact replay, and
zero retained generated output. The other six non-PPP readiness patterns are
tested directly. Not-ready paths construct no source and call VR38A zero
times.

Stage 1 may not stat, resolve, hash, list, open, or parse `.codex_work`, any
private or consumed source, archive member, or neural payload. Its exact
implementation and result must be committed, pushed, and remotely green, then
receive a separately green proof-only closeout before Stage 2.

### Stage 2: one terminal target-free cohort attempt

Only after every proof barrier, request one fixed-path invocation that:

1. creates one new mode-0700 output root and mode-0600 consumed marker before
   readiness, so every attempted route is terminal;
2. collects exactly three readiness samples through unchanged VR33A with
   exactly two fixed five-second sleeps;
3. if and only if readiness is PPP, verifies the registered source through
   no-follow ancestor traversal, opens and strict-parses exactly 418,755 bytes
   once, and calls unchanged VR38A exactly once;
4. on VR38A G1 or G2, validates the variable 12-19 participant arithmetic,
   selected compressed and uncompressed storage ceilings, exact sessions,
   exact runs, exact task, companions, split roles, and source-bound rows;
5. replaces every generated-only provenance name with private-source
   provenance before writing one mode-0600 private cohort manifest;
6. canonicalizes and cap-checks every non-marker output before its first write;
7. generates one private 32-byte commitment key, stores it only in the private
   manifest, and publishes only a domain-separated HMAC-SHA-256 commitment to
   that manifest;
8. writes one fixed-shape aggregate report and one completion marker without
   overwrite.

No archive member, header, neural sample, channel, event, target, label,
model, prediction, or score is opened or written. Not-ready opens zero source
bytes. Every result consumes the lane. Retry, rerun, resume, repair, backfill,
fallback, substitution, cleanup, overwrite, private reinspection, and another
topology successor are excluded.

## Frozen Public Routes

| Route | Maximum public meaning |
|---|---|
| `MARC2VR39P-R1` | One source-bound target-free cohort was frozen and privately committed; a separate FW2 preregistration is eligible. |
| `MARC2VR39P-R2` | No cohort was frozen; the Freewill/CIL1 lane is permanently parked. |

VR38A G1 and G2 both collapse to R1. Every readiness, source, selector,
storage, output, resource, and unexpected failure collapses to R2. The public
surface may not expose selected participant count, identity, rank boundary,
bundle or member count, filename, row, offset, CRC, compressed or uncompressed
total, reservation total, upstream route, surplus topology, failure class,
exception text, private nonce, private manifest hash, private source hash,
timestamp, readiness result, operation count, runtime, RSS, free disk, or
another data-dependent measurement.

The aggregate report uses a strict positive allowlist: schema name/version,
lane, R1/R2 route, constant consumed status, immutable proof anchors, constant
commitment scheme, R1-only HMAC commitment, fixed warnings, unavailable
fields, and claim boundary. Every R2 report is byte-identical regardless of
failure stage. Across valid R1 cohort sizes, every public field except the
secret-keyed commitment is byte-identical.

The public commitment is not a cohort identifier and cannot reveal or replace
the private manifest. HMAC with a random private key prevents enumeration of
the small 12-19 participant space. Future FW2 work must verify the exact
private manifest with constant-time comparison before any payload acquisition.

## Frozen Private Cohort Contract

A successful private manifest must preserve:

- the maximal contiguous frozen participant-rank prefix, with 12-19 subjects;
- `ses-01` as fit and `ses-02` as held-out;
- only runs 1, 2, and 3 in each session;
- exactly six run bundles and 24 structural members per participant;
- exact task `reachingandgrasping` and all four required companions;
- zero fit/held-out overlap and no row-random split;
- source offsets, CRC32 values, compressed sizes, uncompressed sizes, and
  source-bound hashes for every selected row;
- the VR38A contract, configuration, selection-identity, semantic-selection,
  selected-name, selected-row, distinct raw-source-file and canonical-source,
  and split-protocol hashes;
- selected compressed payload at or below 8 GiB; and
- uncompressed payload plus a frozen 1 GiB derivative reserve and 256 MiB
  temporary reserve at or below the 10 GiB incremental-disk ceiling, with at
  least 15 GiB free before the attempt.

The private manifest uses a new real-source schema and proof posture. It may
not contain `generated_inventory_sha256`, a generated-fixture proof posture,
or another generated-only provenance field. Its exact subject count and every
identity-bearing fact remain private.

Generated qualification must also refuse duplicate JSON keys, source mutation,
symlink or ancestor replacement, short writes, nonce/HMAC failure, every
output-cap breach, and injected crashes before each write. A missing completion
marker always means R2 and never permits resume.

## Fixed Source, Paths, And Limits

The future source identity is copied only from committed records:

```text
.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
mode:   0600
bytes:  418755
sha256: 2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
rows:   1227 (1025 regular files, 202 directories)
```

Future VR39P readiness and output paths are new, fixed, non-overwriting
locations. Every prior consumed private lane remains forbidden. The one future
private command is limited to one CPU thread, one worker, one numerical job,
30 seconds, less than 256 MiB peak RSS, at least 15 GiB free disk, 2 MiB
combined metadata output, zero network bytes, zero new payload bytes, and zero
archive, signal, target, or model bytes.

## Current Authorization State

Every authority flag is false. Packet preparation performs zero readiness,
private-path, source, output-root, consumed-state, archive, neural, target,
model, prediction, score, network, provider, device, FW2/CIL1, release, or
claim operation.

The request and a non-scope-changing proof closeout must each be committed,
pushed, and both remotely green. Only then may VR39P be identified as the sole
active Tier C packet. A fresh unambiguous maintainer message after that
identification may authorize the unchanged packet by reference. The current
or any earlier `continue`, `approve`, or `lets go` is not retroactive
authority.

Engineering capability requested: one terminal, source-bound, target-free
cohort commitment that either makes a separately preregistered FW2 neural
experiment possible or permanently parks this real-data lane.

Scientific claim not established: this request performs no private read,
neural access, training, inference, prediction, or score and therefore does
not establish a neural effect, decoding performance, advantage over no-signal
or peripheral controls, movement intention, unseen-person generalization, or
live decoding.
