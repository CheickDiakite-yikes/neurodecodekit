# IACKD Channel Inventory Primary-Source Research

Date: 2026-08-10

Status: **Tier A research complete; a 128-header metadata-only audit is
recommended; no IACKD header, companion, sample, event, trajectory, target, or
model was opened or run in this research pass**

Proposed lane: **IACKD-H1 Header Inventory Audit**

Machine record:
`registries/iackd_channel_inventory_research.v0.json`

## Decision In One Sentence

Read every public IACKD BrainVision header, but no linked file, to replace the
unsupported exact-36-channel assumption with a deterministic aggregate channel
inventory before any new scientific analysis is designed.

## Why This Is The Next Useful Step

IACKD-1 acquired and opaque-verified all 1,340 registered objects and
7,249,113,684 bytes. Its one analysis then stopped on the first lazy
BrainVision reader with:

```text
BrainVision channel inventory is not 32+4
```

That registered `IACKD-F10` refusal happened before signal samples, BIDS
channel metadata, events, kinematics, targets, fitting, inference, prediction,
or scoring. The actual count and names were intentionally not retained. This
is an integrity-contract failure, not a null neural result.

Guessing an alias or relaxing the parser now would tune against a consumed
failure. The correct response is a new, smaller metadata experiment whose only
question is what the released headers actually declare.

## What The Primary Sources Support

### The article does not establish a 36-channel file invariant

The version-of-record article reports a 32-channel Compumedics Neuroscan cap at
1,024 Hz. Its preprocessing section separately says that M1, M2, HEOG, and VEOG
were removed as non-EEG channels. It does not say that every BIDS-converted
BrainVision file contains exactly 36 data channels or that those four names are
byte-identical in every run.

Source: [IACKD data descriptor](https://doi.org/10.1038/s41597-026-07146-x)

### The authors' public code uses two different deletion vocabularies

At upstream commit
`c0b595de7571c7e04abae7477c61d0b92b5702cd`, the premovement MATLAB pipeline
deletes M1, M2, HEOG, VEOG, and TRIGGER if present. The movement-execution
pipeline instead deletes HEO, VEO, TRIGGER, HEOG, and VEOG; it does not list M1
or M2. Both functions use presence-based deletion and neither asserts a raw
channel count.

These scripts make three possibilities credible without proving any of them:

- TRIGGER may be a declared data channel in some exports;
- ocular channels may use HEO/VEO rather than HEOG/VEOG in some sources; or
- the published 32-channel cap count may include rather than precede some
  reference channels.

The code also leaves run heterogeneity possible. None of those possibilities
may be reported as the observed IACKD-1 cause until an independently gated
header audit measures it.

Sources:

- [premovement pipeline](https://github.com/Boketto1/IACKD/blob/c0b595de7571c7e04abae7477c61d0b92b5702cd/code/scripts/matlab/preprocess_premove_55_14.m)
- [movement-execution pipeline](https://github.com/Boketto1/IACKD/blob/c0b595de7571c7e04abae7477c61d0b92b5702cd/code/scripts/matlab/preprocess_eeg_pipeline.m)

### The complete header surface is tiny

The already committed OpenNeuro metadata inventory contains exactly 128 VHDR
objects across all 15 participants. They total 161,792 bytes. Individual
headers are 1,254, 1,256, 1,290, or 1,292 bytes. This is 0.0023 percent of the
acquired 7.249 GB source subset and can be audited sequentially without opening
the retained local bundle.

The deterministic first object is:

```text
sub-01/eeg/sub-01_task-ihc_acq-left_run-01_eeg.vhdr
size: 1,254 bytes
ETag: 14379d265eeae77af2670d63a7051151
```

Source: [OpenNeuro ds006840 v1.0.0](https://openneuro.org/datasets/ds006840/versions/1.0.0)

## Proposed Audit

After a separately green implementation and exact Tier C decision, perform one
no-retry execution that:

1. loads only the committed metadata inventory;
2. selects its exact 128 VHDR objects and expected 161,792 bytes;
3. requests each header sequentially from the pinned OpenNeuro object base;
4. requires exact path, status, response URL, size, and ETag agreement;
5. computes SHA-256 in memory and retains no raw header payload;
6. parses only format, codepage, inert sibling basenames, declared sampling,
   channel count, and ordered channel declarations;
7. never resolves, stats, requests, hashes, or opens either named sibling; and
8. emits one aggregate, target-free signature ledger under 1 MiB.

The public ledger may contain:

- total headers and bytes;
- unique inventory-signature count and occurrence counts;
- declared channel count per signature;
- SHA-256 of each ordered normalized name list;
- exact-presence booleans only for M1, M2, HEOG, VEOG, HEO, VEO, and TRIGGER;
- the first deterministic header's signature and old-gate diagnosis;
- whether all 128 headers share one signature; and
- explicit unavailable fields.

It must not contain raw header text, comments, unallowlisted channel names,
local paths, individual signals, events, trajectories, labels, targets,
predictions, or participant outcomes.

## Falsifiable Diagnostic Outcomes

| Route | Meaning |
|---|---|
| `IACKDH-R0` | A source, integrity, decode, or parse gate fails; no inventory conclusion. |
| `IACKDH-R1` | The first header satisfies exact 36 plus M1/M2/HEOG/VEOG; the prior failure remains unexplained. |
| `IACKDH-R2` | A stable count mismatch explains the prior combined gate. |
| `IACKDH-R3` | A stable exact-name mismatch explains the prior combined gate. |
| `IACKDH-R4` | Stable count and exact-name mismatches both explain the gate. |
| `IACKDH-R5` | Multiple header signatures exist; a future reader must handle preregistered source heterogeneity. |

No route authorizes a corrected IACKD analysis. A later scientific experiment
would require a new reader contract, synthetic qualification, real-data
decision, prediction freeze, and scoring gate.

## Resource Boundary

The proposed real audit is limited to one CPU thread, one worker, 128
sequential VHDR requests, 161,792 expected payload bytes, 1 MiB network body,
256 MiB peak RSS, 120 seconds, 2 MiB incremental disk, 1 MiB public output,
zero retries, and zero reruns. It retains no downloaded VHDR file.

The existing 7.249 GB bundle is not statted, opened, moved, deleted, renamed,
uploaded, or published. No new dependency, MNE call, provider call, language
model, model fit, inference, score, device, stream, or hardware operation is
needed.

## Current Access Ledger

This Tier A research read the published article, the authors' public source
repository, and committed aggregate metadata. It made zero OpenNeuro VHDR
payload requests and zero local IACKD path operations. Header content reads,
sibling accesses, signal samples, events, trajectories, targets, fits,
inferences, predictions, and scores are all zero.

Engineering capability proposed: a bounded, sibling-blind aggregate
BrainVision header inventory that can diagnose an invalid channel contract
without touching neural samples or target-bearing files.

Scientific claim not established: no real header content, EEG sample, event,
trajectory, target, model, prediction, or score was accessed, so this research
establishes no neural effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit, or
clinical use.
