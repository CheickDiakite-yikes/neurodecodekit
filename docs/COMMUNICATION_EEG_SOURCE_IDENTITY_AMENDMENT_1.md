# COMM-L0 Source Identity Amendment 1

Date: 2026-08-27

Status: **Prospective metadata-transport correction; no execution authority**

Machine amendment:
`registries/communication_eeg_source_identity_amendment_1.v0.json`

## Problem

The original contract fixed a 2 MiB future response ceiling before the real
recursive OpenNeuro tree count was known. The query requests a versioned URL
for every object, so the generated 121-row fixture cannot prove that the real
response fits. Consuming the one real metadata invocation on an avoidable size
overflow would not move the research forward.

## Narrow correction

For a future separately authorized metadata wrapper only:

- raise the response-body cap from 2 MiB to 16 MiB;
- raise the bounded read limit from 2 MiB plus one byte to 16 MiB plus one byte;
- retain the 256 MiB peak process-tree RSS cap;
- require generated boundary qualification at the new limit before activation;
- require byte-identical canonical output against the consumed COMM-L0
  canonicalizer for every accepted fixture at or below 2 MiB; and
- implement the larger bounded parser in a new additive wrapper without
  modifying or rerunning the consumed generated implementation or result.

All query bytes, endpoint, snapshot, strict JSON, file-tree, selection,
participant, privacy, output, target, payload, and scientific boundaries remain
unchanged. A response larger than 16 MiB still refuses and consumes the future
one-shot invocation.

## Qualification requirement

The future generated wrapper must pass exact boundary fixtures at 16 MiB minus
one byte, 16 MiB, and 16 MiB plus one byte; deterministic replay; truncation;
declared-length mismatch; non-identity encoding; timeout; process-tree RSS;
and canonical-equivalence checks against the frozen implementation below its
original ceiling. Generated fixture bytes are inert metadata only and remain
under a 48 MiB combined cap.

## Boundary

This amendment makes no request, reads no response or private path, downloads
no payload, modifies no consumed artifact, and runs no model, prediction,
score, stream, device, release, or claim operation. `DREYER-C5R-1-HL` remains
the sole active Tier C packet.

Engineering capability proposed: avoid wasting the sole future metadata
attempt on an unsupported response-size assumption while preserving strict
resource and compatibility proof.

Scientific claim not established: no real EEG or communication information is
read or tested by this amendment.
