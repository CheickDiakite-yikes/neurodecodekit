## Purpose

<!-- What single problem does this pull request solve? -->

## Proof Posture

<!-- Examples: fixture-backed, metadata only, synthetic mechanism only, real-data validated, parked after measured gate. -->

## Scope

- Dataset/modality/task:
- Subject/session/split:
- Optional dependencies:
- Data, cache, model, training, and network access:

## Verification

<!-- Paste concise command outcomes, not private data or full logs. -->

- [ ] Relevant focused tests pass.
- [ ] Complete unit test suite passes, or skipped/unavailable checks are explained.
- [ ] `ruff check .` passes.
- [ ] `python -m compileall -q src tests` passes.
- [ ] `git diff --check` passes.
- [ ] Root and changed-command CLI help were exercised.
- [ ] Runtime, peak RSS, input bytes, output bytes, and thread count are reported where applicable.
- [ ] Deterministic replay, malformed input, collision, tamper, and cap tests were added where applicable.

## Data And Privacy

- [ ] No raw/derived neural data, event targets, participant details, absolute paths, credentials, or signed URLs are included.
- [ ] Dataset/code/device licenses and sharing rights were checked.
- [ ] No consumed holdout was reopened for tuning.
- [ ] Real data access, downloads, model runs, and training runs are explicitly counted.

## Scientific Integrity

- [ ] A no-signal comparator is included for predictive neural results.
- [ ] Train-only fit scope and exact split binding are preserved.
- [ ] EEG, MEG, and peripheral modalities remain separate evidence cohorts.
- [ ] Causal context, scheduling delay, compute time, and end-to-end latency are not conflated.
- [ ] Documentation and reports state every warning and unavailable field.

## Required Closeout

**Engineering capability added:** <!-- One sentence. -->

**Scientific or decoding claim not established:** <!-- A separate sentence. -->

## Documentation

- [ ] README/help/setup updated if the user-facing surface changed.
- [ ] Decision log, build notes, tracker, handoff, or closeout updated when the next gate changed.
- [ ] Generated local artifacts are ignored and were not committed.
