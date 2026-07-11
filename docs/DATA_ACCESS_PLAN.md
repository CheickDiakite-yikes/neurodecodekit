# Data Access Plan

## Goal

Never force a user to download 262GB just to run the first loop.

The v0 data-access loop:

```text
Hugging Face file listing
→ manifest JSONL
→ tiny selection JSON
→ dry-run download plan
→ explicit user-approved selective download
```

## Manifest schema

Each manifest row should be JSONL with fields like:

```json
{
  "repo_id": "bcbl190626/SpanishBCBL",
  "path": "pinet2024_public/MEG/FIF/S1/block1.fif",
  "size_bytes": null,
  "modality": "MEG",
  "subject": "S1",
  "session": null,
  "block": "block1",
  "kind": "raw",
  "extension": ".fif",
  "family": "meg_fif_raw",
  "warnings": []
}
```

Manifest v1 intentionally keeps unknowns explicit instead of guessing. Each row
gets a coarse `family` such as:

```text
meg_fif_raw
meg_log_mat
eeg_brainvision_vhdr
eeg_brainvision_eeg
eeg_brainvision_vmrk
eeg_log_mat
localizer_or_tapping
unknown
```

Rows with incomplete classification carry warnings such as
`unknown_modality`, `unknown_kind`, `unknown_file_family`, `missing_subject`,
or `missing_block`. `inspect-manifest` also reports raw-to-log candidate
pairing statuses:

```text
exact              one block/session-compatible log found
fallback_subject   no block match, but one subject/session log found
ambiguous          multiple candidate logs found
missing_log        no candidate log found
```

Input path lists may be plain paths, JSONL rows with `path` and optional
`size_bytes`, or tab-separated `path<TAB>size_bytes` rows. Size metadata is
used only for planning/reporting; it never triggers a download.

## Selection policy for B2Q-mini v0

Default tiny selection:

```text
modality: MEG
subject: subject attached to the smallest complete raw+log candidate when sizes are known
blocks: 1
include logs: yes
include localizer/tapping: no, unless needed later
max files: 8 by default, lower for first smoke runs when possible
max total size: 5 GB by default, lower for first smoke runs when sizes are known
```

Download behavior:

- default is dry-run
- print all matching paths
- print estimated total size when sizes are known
- warn when selected file sizes are unknown
- fail before download when file count or known bytes exceed the cap
- require `--execute` or equivalent for real download
- require `--allow-unknown-size` with `--execute` if the selection lacks size metadata
- allow an explicit `--session` filter when the manifest contains session IDs
- include every required `blockN-K.fif` split continuation beside its primary
  FIFF file and count all parts against file/byte caps
- record an immutable Hub commit with `--revision` for reproducible selections
- default Hub execution to one worker; increase `--max-workers` only explicitly

The selector should treat byte caps as planning guardrails, not as permission
to fetch data. A valid selection file is still only a download plan until the
user runs `download-selection --execute`.

## Why `.npz` before Zarr

For the first end-to-end loop, `.npz` is easy to inspect, test, and move as one
bounded artifact. Zarr supports independently addressable compressed chunks,
but that capability is useful only when the access pattern or absolute resource
cost justifies another backend.

Loop 13 measured complete and partial access across nine real standard/packed
S21 caches. Partial NPZ access was inefficient because it materialized the
complete signal member before slicing, but every tested cache stayed below the
declared 250 ms full-load, 100 ms partial-load, 512 MiB peak-RSS, and 128 MiB
per-cache revisit thresholds. All decoded-signal hashes matched exactly. Zarr
was not installed or benchmarked.

Decision: keep one bounded NPZ per block as the default. Revisit an optional
chunked backend only when a recorded threshold is crossed or a real workflow
repeatedly consumes subarrays. See `docs/LOOP_13_LAZY_BACKEND_GATE.md`.

## Signal-free split audits

`neurodecode split-protocol` inspects sentence membership without decompressing
the large `signals` or `signal_payload` member. It reads only text arrays,
trial indices, and metadata, while streaming the complete file once for a
physical SHA-256 hash. The first 66-row real audit wrote 63,438 bytes of reports
and zero new signal-cache bytes.

The strict replacement cache is 10,632,576 bytes and reuses the existing raw
block. It downloads nothing. Split membership is assigned before scaling; the
scaler fits only 55 train rows and stores hashes that a later signal-free audit
must reproduce. `sentence-prior-baseline` reads the same text/trial members and
never materializes the signal member.

This keeps evaluation planning cheap, but it does not make a one-block cache a
session or subject benchmark.

Loop 15 exercised the expanded acquisition contract on the current
SpanishBCBL revision. The exact S21 session-2 plan contained the primary
`block1.fif`, required `block1-1.fif` continuation, and matching MAT log:

```text
files: 3
known bytes: 2,516,384,765
cap: 2.5 GiB
unknown sizes: 0
revision: 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
workers: 1
```

The dry run was reviewed before explicit execution. MNE then opened both FIFF
parts as one recording. Omitting the continuation would have created a
plausible but incomplete source, so split-file completeness is now a tested
safety property rather than a filename convention.

Acquire any further block/session only through the same pinned manifest,
session filter, split-FIFF completeness, byte cap, dry run, explicit
`--execute`, and bounded-worker controls. See
`docs/LOOP_15_SAME_SUBJECT_CROSS_SESSION.md`.

## Bounded EEG BrainVision acquisition

Loop 19 extends the same safety contract to SpanishBCBL EEG. A `.vhdr` file is
only a header, so EEG selection is valid only when the same stem has all three
BrainVision members (`.vhdr`, `.eeg`, `.vmrk`) plus the exact subject/session/
block MAT log. Every member counts against file and byte caps. Participant 001
and the official loader's known unusable EEG stems are excluded.

The metadata-only gate inspected the current pinned manifest and selected:

```text
subject/session/block: S7 / 2 / block1
files: 4
known bytes: 94,842,381
cap: 128 MiB
unknown sizes: 0
revision: 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
workers: 1
full EEG subtree avoided: 12,790,560,040 known bytes
```

The dry run was reviewed before explicit execution. The acquisition remains a
four-file local bundle, not permission to snapshot the EEG subtree. Any future
EEG selection must repeat the pinned metadata gate, complete-triplet check,
matching-log check, exact byte cap, dry run, explicit `--execute`, and bounded
worker count. See `docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md`.

## Cache schema v0

```text
schema.name: b2q-mini-cache
schema.version: 0
windows: float32 or float16 array [n_events, n_channels, n_times]
labels: unicode/string array [n_events]
event_start_sec: float array [n_events]
event_source_index: int array [n_events]
channel_names: string array [n_channels]
subject: metadata
modality: metadata
sfreq: metadata
tmin/tmax: metadata
source_files: metadata
transformations: ordered metadata list explaining generation/preprocessing
warnings: metadata list of parser/schema/data caveats
```

Schema v0 is enforced by `neurodecodekit.cache.npz_cache.load_npz_cache`.
Required arrays are `windows`, `labels`, and JSON `metadata`; event timestamps,
source indices, and channel names are optional but validated when present.
`neurodecode load-cache` prints a compact summary and can write a JSON sidecar:

```bash
neurodecode load-cache --cache cache/synthetic_tiny.npz --metadata-out cache/synthetic_tiny.metadata.json
```

## Conditional chunked cache candidate

If a measured revisit trigger is reached, compare a Zarr layout behind the
same semantic cache interface before adopting it:

```text
cache.zarr/
  windows
  labels
  event_start_sec
  metadata.json
  source_manifest.jsonl
```

Recommended chunks:

```text
windows chunks: [min(256, n_events), n_channels, n_times]
compressor: start with Blosc/Zstd when available
```

The final chunk shape and compressor must be selected from measured access and
resource evidence. This sketch is not an implemented schema or migration plan.

## Things to avoid

- No automatic full repo snapshots.
- No hidden downloads inside preprocessing.
- No destructive overwrites of local data.
- No private/derived data uploads by default.
