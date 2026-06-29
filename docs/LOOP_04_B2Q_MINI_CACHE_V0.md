# Loop 4 - B2Q-mini Cache v0

Date: 2026-06-29

Status: Done for schema v0 loading, validation, and metadata sidecars.

## Question

Can one selected block become a reusable tiny cache with enough provenance to
trust later results?

## Result

Yes. The project now has a stable NPZ cache contract that can load synthetic
smoke caches and real extracted FIF/MAT window caches through the same function.

Implemented behavior:

- `save_npz_cache` validates the required arrays:
  - `windows` shaped `[events, channels, timepoints]`
  - `labels` shaped `[events]`
  - JSON `metadata`
- Optional arrays are validated when present:
  - `event_start_sec` shaped `[events]`
  - `event_source_index` shaped `[events]`
  - `channel_names` shaped `[channels]`
- Cache metadata is normalized with:
  - schema name `b2q-mini-cache`
  - schema version `0`
  - dimensions
  - array descriptors
  - warnings
  - transformations
  - source files when available
- `load_npz_cache(path)` is now the stable one-function loader.
- `neurodecode load-cache` prints a compact cache summary.
- `neurodecode load-cache --metadata-out ...` writes a JSON sidecar with the
  summary and full metadata.
- Synthetic caches are explicitly marked as synthetic and not real neural data.
- Real extraction caches now record a transformation trail for FIF loading,
  channel picking, resampling, MAT event parsing, and event-window extraction.

## Acceptance Gate

Met.

- Cache loads with one function.
- Metadata explains transformations for synthetic and real extraction writers.
- Schema validation rejects bad window ranks, label length mismatches, and
  channel-name mismatches.
- CLI smoke command loads a synthetic cache and writes a metadata sidecar.

## Verified Commands

```bash
python -m unittest tests.test_npz_cache tests.test_cli_cache
```

Result:

```text
Ran 6 tests
OK
```

```bash
python -m unittest discover -s tests
```

Result:

```text
Ran 37 tests
OK
```

## Current Limits

- NPZ remains the only implemented cache backend. Zarr is still intentionally
  deferred until larger real caches make chunking necessary.
- Schema v0 is a practical interface, not a frozen public standard.
- Synthetic caches do not contain real event timestamps.
- Real-data cache quality still depends on validating one actual SpanishBCBL
  `.fif` / `.mat` pair.

## Decision

Proceed to Loop 5: Metrics + Error Report v1.

The next loop should build reports on top of `load_npz_cache` so every metric,
baseline, and demo reads the same cache contract.
