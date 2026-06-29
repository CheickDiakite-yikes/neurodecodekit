# Loop 1 - PR1 Closeout + Smoke Loop

Date: 2026-06-29

## Loop

Loop ID: 1

Loop name: PR1 Closeout + Smoke Loop

Core question: Can one real/synthetic event-window extraction path run without hidden assumptions?

Acceptance gate:

- Tests pass.
- CLI help works.
- One tiny cache can be produced.
- Blockers are documented.

## Result

Status: Done for the synthetic smoke path; real extraction remains blocked until a user supplies one selected `.fif` block and one matching `.mat` log file.

The PR1 extraction scaffold is present and intentionally narrow:

- `neurodecode extract-windows` reads one explicit `.fif` and one explicit `.mat`.
- Heavy neuro dependencies remain optional behind `pip install -e '.[neuro]'`.
- The command does not download data.
- Event parser warnings and keep/drop counts are surfaced in the CLI report and saved in metadata.

## Verified commands

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\neurodecode.exe --help
.\.venv\Scripts\neurodecode.exe extract-windows --help
.\.venv\Scripts\neurodecode.exe make-synthetic-shard --out cache\loop1_synthetic_smoke.npz --samples 16 --channels 4 --times 10
```

Expected synthetic cache shape:

```text
[16, 4, 10]
```

The generated `.npz` is a local smoke artifact and should not be committed.

## Real-data blocker

No real SpanishBCBL `.fif` / `.mat` pair is present in the repo. Real extraction should be attempted only after the tiny selection flow has produced an explicit dry-run plan and the user has intentionally downloaded the selected files.

Example real extraction command once files exist:

```powershell
.\.venv\Scripts\neurodecode.exe extract-windows `
  --raw data\spanishbcbl_tiny\...\block1.fif `
  --events data\spanishbcbl_tiny\...\S1_block1.mat `
  --out cache\b2qmini_s1_block1.npz `
  --sfreq 50 `
  --tmin -0.2 `
  --tmax 0.3 `
  --picks meg `
  --max-events 200
```

## Decision

Proceed to Loop 2: SpanishBCBL Manifest v1.

Reason: Loop 1 has a working synthetic smoke path and documented real-data blocker. The next bottleneck is safer manifesting and file-pair understanding before any real data download.
