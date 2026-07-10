# Loop 18 - Versioned Report Cards and Cohort-Local Leaderboard

Status: **Done** on 2026-07-10.

Proof posture: **local artifact only**. This loop read compact saved JSON
reports. It did not open raw neurodata, load a cache array, run a model, fetch
from a network, or reopen an observed holdout.

## Question

Can saved NeuroDecodeKit experiments be compared without spreadsheet
archaeology while keeping unlike tasks, splits, and proof postures separate?

## Registered Gate

- define one versioned report-card contract
- include metrics, split/proof posture, method, comparator, resources, config,
  cache provenance, source hash, and missing-field flags
- ingest at least three existing baselines without retraining
- emit deterministic JSON and Markdown plus a sortable CLI table
- reject malformed and mixed-version cards
- rank only inside exact authorized cohorts; never create a global ranking
- report runtime, peak RSS, source bytes, output bytes, and forbidden accesses
- stay under 32 cards and 2 MiB of output by default

## Research Basis

The contract follows three primary references:

- [Model Cards for Model Reporting](https://research.google/pubs/model-cards-for-model-reporting/)
  motivates intended-use, evaluation-context, and limitation disclosure.
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking/) motivates recording
  run parameters, metrics, datasets, and artifacts while retaining a local
  filesystem workflow.
- [Brain2Qwerty v2](https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf)
  reports CER, WER, and SemER beside baselines and ablations. It also shows why
  these metrics must remain separate: language correction can move semantic and
  word error differently from character error.

## Implementation

`evaluation/report_card.py` adds a dependency-free builder and validators.
`neurodecode build-leaderboard` reads the versioned
`configs/loop18_leaderboard.json` spec and writes:

```text
cache/loop18_leaderboard/
  leaderboard.json
  leaderboard.csv
  leaderboard.md
  audit.json
  cards/<run-id>/card.json
  cards/<run-id>/metrics.json
  cards/<run-id>/config.json
  cards/<run-id>/cache_metadata.json
  cards/<run-id>/report.md
```

Core files omit build timestamps and absolute output paths. The separate audit
holds runtime and RSS, so deterministic report bytes remain stable. Every card
hashes its compact source report and a filtered config snapshot. Cache metadata
is inherited from the source report; the cache file is not opened or hashed.
That missing cache hash is surfaced rather than silently invented.

Run the bounded build with:

```bash
neurodecode build-leaderboard \
  --spec configs/loop18_leaderboard.json \
  --project-root . \
  --out-dir cache/loop18_leaderboard \
  --max-cards 16 \
  --max-output-mb 2
```

## Saved Evidence Indexed

| Exact cohort | Cards | Ranking | Result boundary |
| --- | ---: | --- | --- |
| Synthetic sentence holdout | 2 | authorized | Tiny CTC CER 0.0000; prior 0.7068. Fixture plumbing only. |
| S21 session-1 strict sentence test | 2 | authorized | Tiny CTC/prior CER 0.9477/0.9535 on five rows; uncertainty crosses zero. |
| S21 same-subject session-2 transfer | 2 | authorized | Prior/tiny CTC CER 0.7755/0.9179; session 2 is consumed. |
| Synthetic adapter holdout | 3 | authorized | Robust affine/identity/prior CER 0.0000/0.3448/0.5776. Best-case fixture only. |
| S21 event-key holdout | 1 | not ranked | Nearest-centroid event CER 1.1225; not sentence decoding. |
| S21 event fit-on-eval smoke | 1 | not ranked | Prior CER 2.3694; fit-on-eval and never a held-out result. |

There are 11 cards across six cohorts and four method families. Four cohorts
have internally authorized rankings. The event holdout and fit-on-eval smoke
stay separate. `global_best_run` is `null` and
`cross_cohort_ranking_performed` is `false`.

The cross-session row illustrates the value of retaining multiple metrics. The
prior has lower CER, while tiny CTC has slightly lower WER (1.0000 versus
1.0322). The table therefore does not collapse CER and WER into one invented
score.

## Missing Metadata Is Evidence

All 11 cards contain every required field. Recommended fields remain visibly
missing where old source reports did not record them:

- SemER was not measured for any indexed run.
- most comparator variants lack method-specific runtime, RSS, and parameter
  counts because their source report stores only shared experiment resources.
- cache SHA-256 is absent because this loop intentionally did not open cache
  files, especially observed real holdouts.
- code-version identifiers were not recorded in the historical reports.
- paired uncertainty is available only where the source report saved it.

These gaps lower completeness counts but do not invalidate an otherwise
well-formed historical card.

## Resource Audit

```text
source report references: 11
source report bytes read: 247,440
deterministic core files: 58
deterministic core bytes: 103,013
total artifact bytes: 103,789
runtime: 0.012 sec
peak RSS: 21,643,264 bytes
raw data reads: 0
cache files opened: 0
signal array members loaded: false
model runs: 0
network fetches: 0
holdouts reopened: 0
free disk after build: about 17 GiB
```

A second build under `.codex_work/loop18_repeat` reproduced every deterministic
core file byte for byte. Audit timing and RSS are excluded from that identity
check.

## Validation

Focused tests cover deterministic replay, cohort-local ranking, absent global
ranking, malformed cards, mixed schema versions, duplicate IDs, card caps,
existing-output refusal, CLI output, and forbidden-access counters.

The full closeout verification is recorded in `docs/BUILD_NOTES.md`.

## Decision

Close Loop 18. The report-card layer makes saved evidence easier to inspect but
does not improve any decoder and does not authorize cross-cohort model claims.
Loop 19 may explore an optional EEG/MOABB-style bridge only after a data-access
and dependency gate; MEG and EEG results must remain separate cohorts.
