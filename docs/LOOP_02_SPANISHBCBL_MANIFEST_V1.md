# Loop 2 - SpanishBCBL Manifest v1

Date: 2026-06-29

## Loop

Loop ID: 2

Loop name: SpanishBCBL Manifest v1

Core question: Can we map subject/session/block/log files before downloading anything large?

Acceptance gate:

- Manifest covers expected MEG, EEG, and log file families.
- Ambiguous or unknown rows are explicit.
- Candidate raw/log pairings are visible before selection or download.
- Tests pass.

## Result

Status: Done for local manifest parsing and summary logic.

Manifest rows now include:

- `family`: stable coarse file family, for example `meg_fif_raw`, `meg_log_mat`, `eeg_brainvision_vhdr`, or `unknown`.
- `warnings`: explicit parser uncertainty such as `unknown_modality`, `missing_subject`, or `missing_block`.
- `size_bytes`: parsed when the input line provides JSON or tab-separated size metadata.

`inspect-manifest` summaries now include:

- counts by modality, kind, extension, and family
- known-byte coverage
- record warning previews
- raw-to-log candidate pairing status and examples

Pairing statuses:

```text
exact              one block/session-compatible log found
fallback_subject   one subject/session-compatible log found but not exact by block
ambiguous          multiple candidate logs found
missing_log        no candidate log found
```

## Verified commands

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\neurodecode.exe manifest-from-paths --paths cache\loop2_paths.txt --out cache\loop2_manifest.jsonl
.\.venv\Scripts\neurodecode.exe inspect-manifest --manifest cache\loop2_manifest.jsonl
```

The cache files above are local smoke artifacts and should not be committed.

## Limits

- This loop does not download or query the full dataset.
- Size metadata is parsed only when present in the input file list.
- Pairing is heuristic until a real SpanishBCBL file list validates all naming patterns.
- Safe max-file/max-size enforcement belongs to Loop 3.

## Decision

Proceed to Loop 3: Safe Tiny-Shard Selector.

Reason: manifest parsing now exposes the information and uncertainty needed for safer tiny-shard selection.
