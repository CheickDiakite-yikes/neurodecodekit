# Codex Continuation Prompt

Use `prompts/CODEX_START_PROMPT.md` for the current work order. The original
20-loop sequence is complete except parked Loop 13; post-roadmap Loop 23 is
also parked, Loop 23.5 is complete, and Loop 24 requires its own
preregistration.

RW1 metadata-only local intake is closed. RW2's signal-quality contract is
frozen at commit `eacb231`. The next parallel work order is its exact
synthetic-fixture-only implementation. Read:

- `docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md`
- `docs/BYO_NEURODATA_WORKBENCH_SPEC.md`
- `registries/datasets.v0.json`
- `registries/devices.v0.json`
- `docs/FRESH_EEG_BENCHMARK_S20_APPROVAL_PACKET.md`
- `docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`
- `docs/RW2_PRIMARY_SOURCE_RESEARCH.md`
- `docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md`
- `registries/signal_quality_contract.v0.json`

Do not download or open S20: its packet is a dry run and remains unapproved.
Do not reopen consumed S7/S21 evidence or seeds 2203, 2303, and 2353. Keep task
cohorts and sensor modalities separate, preserve optional dependencies, and
implement only the frozen bounded-read, unit/reference, channel/geometry,
event, PSD, quality-warning, privacy, resource, and no-auto-deletion rules.
Generated artifacts must remain below the declared caps and outside git. A
passing synthetic gate still requires separate approval before a real read.
Loop 24 remains independently available for preregistration.
