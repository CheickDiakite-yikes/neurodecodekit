# NeuroDecodeKit Build Notes

This file is the working journal for the build. It exists so later agents,
engineers, and case-study readers can reconstruct not only what changed, but
why the project moved in small loops.

## Note-taking convention

For each loop, record:

- the smallest useful question
- the code or artifact created
- the tests or smoke commands run
- what was deliberately not done
- any environment, data-access, or security blocker
- the next recommended action

When a loop is interrupted, mark it as pending instead of polishing the story.
An honest partial state is more useful than a false completion signal.

## Operating principles

- Keep the base install lightweight.
- Import heavy neuro/data dependencies only inside the command path that needs
  them.
- Prefer one tiny cache/report/demo over a large fragile pipeline.
- Never download large data silently.
- Keep `download-selection` dry-run by default.
- Require `--execute` plus explicit caps for any real download.
- Do not commit real dataset files, caches, credentials, or large binaries.
- Treat `--identity-smoke` as plumbing verification, not model performance.
- Do not proceed to a more complex loop until the previous loop has a clear
  artifact, decision, or pending handoff.

## Managed workstation observations

These observations are specific to the Bain-managed Windows environment used
for this build. They should guide future agents without being treated as
universal project constraints.

### GitHub push/export

On 2026-07-01, a push attempt after the local Loop 5 WIP commit was blocked by
the admin/reviewer layer because it would export the Bain workspace repo
externally and the privacy/trust status was not verified in that moment.

Implication:

- Do not retry `git push` from this workstation unless the user explicitly
  re-approves the export and the repository/privacy status is understood.
- Local commits are still useful for handoff.
- The next engineer can push from an approved environment or after explicit
  user approval.

### Workbook/tracker tooling

The attempt to close Loop 5 by updating the Excel tracker was interrupted by an
admin/tooling block during the earlier WIP handoff. On 2026-07-01, the tracker
workbook was successfully updated through the bundled spreadsheet runtime in an
ignored `.codex_work/loop5_tracker_closeout/` work area.

Implication:

- `docs/NEXT_20_LOOPS_TRACKER.md`, the root tracker copy, and both
  `NEURODECODEKIT_20_LOOP_TRACKER.xlsx` copies should show Loop 5 as done.
- Prefer the bundled spreadsheet runtime for future workbook edits when it is
  available and keep helper scripts inside `.codex_work/`.
- `.codex_work/` is ignored so transient local helper artifacts do not enter
  commits.

### Network and data access

Network access may be restricted. Real SpanishBCBL data is not present in the
repo, and the project should not fetch it implicitly.

Implication:

- Tests must keep working without Brain2Qwerty/SpanishBCBL files.
- Real extraction commands must only read explicit local `.fif` and `.mat`
  paths.
- Any download path must remain dry-run first and require explicit `--execute`.

### Git and OneDrive

This repo lives under OneDrive. Git commands may occasionally report an
`index.lock` unlink warning. Before any commit, verify no Git process is
running and remove only the exact stale lock path if needed.

Recommended safe lock cleanup:

```powershell
$repo = (Resolve-Path .).Path
$gitDir = Join-Path $repo '.git'
$lockPath = Join-Path $gitDir 'index.lock'
if (Test-Path $lockPath) {
  $resolvedLock = (Resolve-Path $lockPath).Path
  if (-not $resolvedLock.StartsWith($gitDir)) {
    throw "Refusing to remove unexpected path: $resolvedLock"
  }
  Remove-Item -LiteralPath $resolvedLock
}
```

## Loop timeline

| Loop | Status | Durable artifact | Notes |
|---:|---|---|---|
| 1 | Done | `docs/LOOP_01_PR1_CLOSEOUT_SMOKE.md` | Closed the first extraction scaffold with synthetic smoke coverage. Real data remains gated on one explicit `.fif`/`.mat` pair. |
| 2 | Done | `docs/LOOP_02_SPANISHBCBL_MANIFEST_V1.md` | Added manifest parsing and uncertainty reporting before any large download planning. |
| 3 | Done | `docs/LOOP_03_SAFE_TINY_SHARD_SELECTOR.md` | Added capped selection and dry-run download planning so the user sees exact files before execution. |
| 4 | Done | `docs/LOOP_04_B2Q_MINI_CACHE_V0.md` | Made `.npz` cache schema v0 the stable tiny-cache interface. |
| 5 | Done | `docs/LOOP_05_METRICS_ERROR_REPORT_V1.md` | Closed on 2026-07-01 with report command verification, synthetic JSON/Markdown smoke output, Markdown tracker updates, workbook tracker updates, and closeout docs. |

## Loop 5 closeout state

Original WIP commit:

```text
fb3ec1a Add Loop 5 report WIP handoff
```

What exists:

- `neurodecode report`
- text target/prediction report flow
- synthetic cache `--identity-smoke` flow
- JSON and Markdown report writers
- CER, WER, exact-match, keyboard-distance, corpus edit counts, examples,
  worst examples, runtime, warnings, and optional cache metadata
- focused report tests and CLI report tests
- docs marking Loop 5 as done

Final closeout verification on 2026-07-01:

```text
python -m unittest tests.test_report tests.test_cli_report
Ran 8 tests
OK

python -m unittest discover -s tests
Ran 45 tests
OK
```

```text
neurodecode report --help
OK
```

Synthetic smoke output:

```text
cache/loop5_synthetic_tiny.npz
cache/loop5_synthetic_report.json
cache/loop5_synthetic_report.md
```

The cache/report files remain ignored local artifacts, not committed data.

Tracker closeout:

- `docs/NEXT_20_LOOPS_TRACKER.md` updated to Loop 5 done and Loop 6 next.
- Root `NEXT_20_LOOPS_TRACKER.md` updated to the same state.
- `docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx` updated:
  - Dashboard Done = 5.
  - Foundation Done = 5.
  - Loop 5 status = Done.
  - Decision Log includes the Loop 5 proceed row.
- Root `NEURODECODEKIT_20_LOOP_TRACKER.xlsx` updated with the same workbook.

## Case-study notes

The useful story is not "we built a decoder in one leap." The useful story is:

- Big neuro datasets become approachable when the first loop is manifest,
  selection, tiny cache, report, and demo.
- Optional dependencies make the tool usable on ordinary machines while still
  allowing real neuro extraction when the user opts in.
- Dry-run-by-default data access is a product feature, not just a safety guard.
- A report artifact is the bridge between research code and engineering
  repeatability.
- Identity smoke tests are valuable when they are named honestly.
- Managed enterprise environments can block network, workbook, or export paths;
  the project should keep progressing through local commits and explicit
  handoffs rather than pretending those constraints do not exist.

## Next recommended action

Proceed to Loop 6. Loop 6 should add an intentionally no-brain LM-only/prior-only
baseline so every future neural score has a fair comparator.
