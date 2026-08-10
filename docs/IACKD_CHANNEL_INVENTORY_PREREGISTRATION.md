# IACKD Header Inventory Audit Preregistration

Date: 2026-08-10

Status: **Prospectively frozen; Tier B synthetic implementation is eligible
only after this registration is remotely green; every real-content operation
remains unauthorized**

Lane: **IACKD-H1 Header Inventory Audit**

Contract: `registries/iackd_channel_inventory_contract.v0.json`

## Question

What channel counts and exact public-code aliases are declared by all 128 IACKD
BrainVision headers, and which part of the consumed IACKD-1 combined `32+4`
gate did the first deterministic header violate?

This is a file-contract diagnostic. It is not a neural experiment and cannot
produce a scientific decoding result.

## Immutable Inputs

- OpenNeuro dataset `ds006840`, version `1.0.0`.
- Committed inventory
  `registries/iackd_openneuro_metadata_inventory.v0.json`, SHA-256
  `aeaa4928192cca9086fcb0abf4711147c68a68ef5c5aacda2ebc67d162a1ef19`.
- Exactly the 128 inventory members whose paths end in `.vhdr`.
- Exactly 161,792 expected VHDR body bytes.
- Object base `https://s3.amazonaws.com/openneuro.org/ds006840/`.
- No local IACKD bundle path and no substitute object.

The first deterministic header is the 1,254-byte
`sub-01/eeg/sub-01_task-ihc_acq-left_run-01_eeg.vhdr`, with registered ETag
`14379d265eeae77af2670d63a7051151`.

## Ordered Stages

### Stage I: synthetic implementation

After this exact registration commit passes both required CI jobs, Tier B may
implement and adversarially qualify a standard-library-only parser, response
validator, aggregate signature builder, bounded writer, and dry-run-first CLI
using generated VHDR bytes and mocked transports only.

Stage I may not make a network call, inspect a local IACKD path, import MNE, or
read any real header. Its exact implementation commit must pass both required
CI jobs before a real execution can become eligible.

### Stage R: one real header audit

Stage R remains Tier C and unauthorized. It requires one separate packet-bound
maintainer decision made after a remotely green Stage I implementation. If
authorized, exactly one no-retry execution may request and parse the registered
128 public VHDR objects. There is no rerun.

## Fetch Contract

For each object in canonical path order:

1. issue one HTTPS GET with no redirect and no retry;
2. require the final response URL to equal the registered URL;
3. require status 200, exact Content-Length, and exact ETag;
4. reject compression or transfer transformations that obscure body length;
5. read at most 4,096 bytes into memory;
6. require exact expected size and compute body SHA-256;
7. parse the in-memory bytes once; and
8. discard the raw bytes before requesting the next object.

No VHDR body may be persisted. DataFile and MarkerFile values are treated only
as inert basenames. They may not be joined to a directory, resolved, statted,
requested, hashed, or opened.

## Parser Contract

The parser is standard-library-only and must:

- support only strict UTF-8, UTF-8 with BOM, or declared Windows-1252;
- reject replacement decoding, NUL, disallowed controls, duplicate required
  sections, duplicate keys, and conflicting codepage declarations;
- require the BrainVision VHDR format preamble and unique Common Infos, Binary
  Infos, and Channel Infos sections;
- require DataFile, MarkerFile, DataFormat, DataOrientation,
  NumberOfChannels, SamplingInterval, and BinaryFormat;
- require positive finite sampling interval and derive rate deterministically;
- require exactly one contiguous `Ch1` through `ChN` table matching the
  declared count;
- decode BrainVision `\1` comma escaping before uniqueness checks;
- require nonempty, unique normalized channel names; and
- preserve no raw text or comment in public output.

Name normalization for signatures is Unicode NFC plus surrounding-whitespace
removal. Exact-presence comparison is case-insensitive only after that
normalization. No fuzzy alias, semantic type, geometry, reference, or channel
deletion is inferred.

The only public allowlist is:

```text
M1 M2 HEOG VEOG HEO VEO TRIGGER
```

## Aggregate Output Contract

The public ledger contains no per-participant outcome. It may contain:

- source version, inventory hash, implementation hash, and execution evidence;
- input object count, bytes, body-hash-set hash, runtime, RSS, and output bytes;
- unique signature groups sorted by canonical signature ID;
- for each group, occurrence count, declared count, ordered-name-list SHA-256,
  sampling declaration, and seven allowlisted presence booleans;
- first deterministic object signature ID and combined-gate diagnosis;
- all-headers-identical boolean;
- access counters, warnings, unavailable fields, gates, and one diagnostic
  route from `IACKDH-R0` through `IACKDH-R5`.

The ledger must not contain raw VHDR text, comments, unallowlisted channel
names, DataFile or MarkerFile values, individual paths, local paths, signals,
events, trajectories, targets, predictions, or participant outcomes.

## Frozen Router

Apply in this order:

1. `IACKDH-R0` if any source, response, resource, decode, parse, output, or
   completeness gate fails.
2. `IACKDH-R5` if more than one channel inventory signature exists.
3. `IACKDH-R1` if the first signature has count 36 and exact M1, M2, HEOG, and
   VEOG presence.
4. `IACKDH-R4` if its count differs from 36 and at least one canonical name is
   absent.
5. `IACKDH-R2` if only the count differs from 36.
6. `IACKDH-R3` if only at least one canonical name is absent.

Routes are diagnostic labels, not model or scientific outcomes.

## Acceptance Gates

- exact remotely green registration precedes Stage I;
- exact remotely green implementation and separate Tier C decision precede
  Stage R;
- 128 and only 128 registered VHDR responses are accepted;
- total accepted body bytes equal 161,792;
- every path, URL, size, and ETag matches the committed inventory;
- every body receives one SHA-256 pass and one parse;
- all bodies yield a complete internally consistent declared channel table;
- signature aggregation and first-object diagnosis replay byte-exactly;
- no existing local IACKD path is statted or opened;
- all sibling, sample, event, trajectory, target, model, prediction, score,
  provider, stream, device, hardware, and release counters remain zero;
- runtime, RSS, network, disk, thread, and output caps pass; and
- the claim remains a metadata compatibility result only.

## Refusal IDs

- `IACKDH-F01`: missing exact real-content decision
- `IACKDH-F02`: registration, implementation, inventory, or green-proof mismatch
- `IACKDH-F03`: wrong object set, order, URL, or source version
- `IACKDH-F04`: redirect, retry, substitution, or rerun
- `IACKDH-F05`: response status, length, ETag, compression, or size mismatch
- `IACKDH-F06`: decode, codepage, preamble, section, or key failure
- `IACKDH-F07`: channel count, index, name, or uniqueness failure
- `IACKDH-F08`: unsafe sibling reference or attempted sibling resolution
- `IACKDH-F09`: raw, comment, unallowlisted name, path, or protected output
- `IACKDH-F10`: local bundle, companion, sample, event, trajectory, or target access
- `IACKDH-F11`: cache, split, feature, model, inference, training, or scoring operation
- `IACKDH-F12`: dependency, provider, language-model, stream, device, or hardware operation
- `IACKDH-F13`: malformed or nondeterministic signature aggregation
- `IACKDH-F14`: resource, thread, network, disk, or output cap breach
- `IACKDH-F15`: overwrite, retained raw payload, deletion, move, upload, or release
- `IACKDH-F16`: scientific, decoding, real-time, portable, assistive, or clinical overclaim

Any refusal consumes Stage R if it had begun. There is no fallback, post-result
parser amendment, alternate allowlist, or second attempt.

## Resource Caps

| Resource | Cap |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Wall time | 120 seconds |
| Peak RSS | 268,435,456 bytes |
| VHDR requests | 128 |
| Expected VHDR body bytes | 161,792 |
| Network body bytes | 1,048,576 |
| Bytes read per VHDR | 4,096 |
| Incremental disk | 2,097,152 bytes |
| Public generated output | 1,048,576 bytes |
| Minimum free disk before execution | 2,147,483,648 bytes |
| Retries / reruns | 0 / 0 |

## Explicitly Forbidden

The existing local IACKD bundle; any VMRK, EEG, channels TSV, events TSV,
coordsystem, electrodes, ball, Leap, derivative, CURRY source, participant
table, or other object; signal samples; markers; event descriptions;
trajectories; labels; targets; caches; splits; models; fitting; inference;
scoring; post-result tuning; MNE or another neural reader; new dependency;
language model or provider; device, stream, or hardware work; deletion, move,
upload, publication, or release; and every scientific claim upgrade.

Engineering capability proposed: a deterministic all-run header compatibility
audit that can replace a failed hard-coded channel assumption with a measured,
hash-bound parser contract.

Scientific claim not established: this preregistration accesses no real header
content, EEG sample, event, trajectory, target, model, prediction, or score and
therefore establishes no neural effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit, or
clinical use.
