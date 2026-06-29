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
  "extension": ".fif"
}
```

## Selection policy for B2Q-mini v0

Default tiny selection:

```text
modality: MEG
subject: first subject with both raw block and logs
blocks: 1
include logs: yes
include localizer/tapping: no, unless needed later
```

Download behavior:

- default is dry-run
- print all matching paths
- print estimated total size when sizes are known
- require `--execute` or equivalent for real download

## Why `.npz` before Zarr

For the very first end-to-end loop, `.npz` is easier to inspect and test. Zarr should become the main cache format once real data extraction works. Zarr is the right long-term target because it supports chunked, compressed N-dimensional arrays.

## Cache schema v0

```text
windows: float32 or float16 array [n_events, n_channels, n_times]
labels: unicode/string array [n_events]
event_start_sec: float array [n_events]
subject: metadata
modality: metadata
sfreq: metadata
tmin/tmax: metadata
source_files: metadata
```

## Cache schema v1

Move to Zarr:

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

## Things to avoid

- No automatic full repo snapshots.
- No hidden downloads inside preprocessing.
- No destructive overwrites of local data.
- No private/derived data uploads by default.
