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

The selector should treat byte caps as planning guardrails, not as permission
to fetch data. A valid selection file is still only a download plan until the
user runs `download-selection --execute`.

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
