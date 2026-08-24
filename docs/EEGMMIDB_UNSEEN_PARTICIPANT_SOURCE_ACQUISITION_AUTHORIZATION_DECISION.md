# EEGMMIDB-UG1 Stage S-A Source Acquisition Authorization Decision

Date: 2026-08-24

Lane: `EEGMMIDB-UG1-SA`

Status: **Packet-bound short-form authorization recorded; ineffective until
this exact decision is committed, pushed, and both required CI jobs are green**

Machine decision:

- `registries/eegmmidb_unseen_participant_source_acquisition_authorization_decision.v0.json`

## Maintainer Decision

After Codex identified `EEGMMIDB-UG1-SA` as the sole active Tier C packet and
reported its exact request commit, proof-closeout commit, CI evidence,
two-stage scope, and fresh-decision boundary, the maintainer's next message
was exactly:

```text
continue
```

The machine decision preserves those actual eight UTF-8 bytes and their
SHA-256. Under the approved Research Autonomy Charter short-form rule, this
unambiguous continuation binds only the unchanged, remotely green Stage S-A
packet by reference. It does not fabricate a long-form user utterance or
expand the registered scope.

## Green Packet Bound By This Decision

```text
request commit:       2085ea061d936bb18ef08e93fb7d3f874ef0f9d8
request CI:           32722744301
request Base job:     97417435948
request Optional job: 97417435670
proof commit:         b0b4632ffbdaca10c1e4bbc93ad26ebd8e1368ca
proof CI:             32724357118
proof Base job:       97422237667
proof Optional job:   97422237272
```

Both required jobs passed for both commits. The packet and proof artifact set
contains six unchanged files totaling 44,910 bytes. The unrelated untracked
tracker inspection NDJSON remains untouched.

## Delayed Effect

This decision does not become effective merely because these files exist.
Before Stage S-A1 implementation or generated qualification, this exact
decision must pass local checks, be committed and pushed, and pass both
required remote CI jobs.

Recording the decision performs zero generated qualification, network request,
checksum-manifest access, URL or local real-data operation, EDF access, payload
acquisition, target delivery, model operation, training, prediction, scoring,
release, or claim upgrade.

## Authorized Sequence After Green Decision

### Stage S-A1: generated/mock source acquisition

After this decision is remotely green, one additive standard-library module
and sidecar CLI may be implemented and qualified using only generated local
sentinel payloads and mocked HTTP responses. The existing proof-bound Stage G
acquisition module, central CLI, contracts, amendments, metadata implementation,
and consumed results must remain byte-identical.

The sidecar may expose only dry `plan` and generated `qualify` commands. The
implementation must freeze the live executor behind later proof evidence,
enforce the exact ordered six-file allowlist, strict direct response identity,
bounded streaming, official checksum equality, no-follow local verification,
atomic no-replace complete-bundle publication, a durable pre-request consumed
marker, bounded canonical serializers, exact resource accounting, and narrow
cleanup of invocation-created temporary files only.

The one registered qualification may use no network, real URL, existing local
payload, EDF parser, MNE import, target, model, training, inference, prediction,
or scoring operation. It must cover successful deterministic replay plus
aliases, symlinks, hardlinks, traversal, redirects, compression, malformed or
conflicting checksums, truncated and oversized bodies, header drift, output
collisions, target-like public output, cap breaches, fresh-final paths, and a
second invocation.

The exact implementation and generated result must be committed, pushed, and
pass both remote jobs. A separate proof-only closeout must then also be
committed, pushed, and pass both jobs before Stage S-A2 exists.

### Stage S-A2: one real opaque source acquisition

Only after all Stage S-A1 barriers are green may one no-retry invocation make
one bounded HTTPS `GET` of the exact versioned official `SHA256SUMS.txt`, freeze
exactly six allowlisted checksums, and then make exactly six sequential EDF
`GET` requests in the registered order.

Each request must be direct, identity encoded, conditional on the frozen ETag
and modification time, and validated against the frozen size and response
headers before body consumption. Every EDF body must remain opaque, stream in
chunks no larger than 1 MiB, match the official SHA-256 during transfer, and
pass exactly one no-follow local size and SHA-256 verification before the
complete bundle can be promoted.

The invocation may create only the new isolated Git-ignored bundle, one
private machine manifest, one durable consumed marker, and one aggregate
public receipt. A pass or failure consumes the authority. There is no retry,
rerun, repair, resume, fallback, substitution, overwrite, or partial success.

## Resources

```text
CPU threads / workers / jobs: <= 1 / <= 1 / <= 1
wall time per stage:          <= 300 seconds
peak process-tree RSS:        <= 256 MiB
checksum / EDF requests:      exactly 1 / exactly 6 at complete S-A2
successful EDF body bytes:    exactly 15,498,816
payload-network body cap:     <= 16 MiB
incremental disk:             <= 64 MiB
combined metadata:            <= 1 MiB
stream chunk size:            <= 1 MiB
minimum free disk:            >= 2 GiB
retry / rerun:                0 / 0
```

## Explicitly Not Authorized

This decision does not authorize Stage S-A1 before its own decision CI is
green; Stage S-A2 before the exact Stage S-A1 implementation, result, and
proof-only closeout are remotely green; any request or path operation over the
54 already-retained source EDFs or 30 fresh-final EDFs; EDF header, annotation,
event, sample, channel, geometry, montage, reference, sampling, task, target,
label, epoch, trial, or quality reads; MNE or another EDF reader in the
acquisition executor; a sidecar, extra file, participant, run, dataset,
download, retry, rerun, substitution, or fallback; cache, split, feature,
derivative, checkpoint, model, inference, training, prediction, target
delivery, selection, or scoring; language models, RW3, streams, devices, or
hardware; upload, publication, or release; or any scientific, neural,
decoding, unseen-person, movement-intention, motor-cortex, eye-independent,
language, live, portable, home-use, assistive, or clinical claim upgrade.

## Next Gate

Commit, push, and green this exact decision. Then implement and generated-
qualify Stage S-A1 once. Only after that exact implementation and a separate
proof-only closeout are remotely green may Stage S-A2 acquire the six opaque
source payloads once.

Engineering capability authorized after green decision: one strictly bounded,
source-only opaque acquisition gate may be qualified on mocks and later obtain
the six registered source files with immutable integrity evidence.

Scientific claim not established: this decision is authorization, not neural
data or a model result, and establishes no EEG effect, decoding performance,
movement intention, motor-cortex origin, eye independence, language decoding,
live performance, or unseen-person generalization.
