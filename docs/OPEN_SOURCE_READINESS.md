# Open-Source Readiness

Date: 2026-07-10

Status: **Prepared on a review branch; repository visibility remains private**

## Purpose

This record separates public-release preparation from the act of changing
GitHub visibility. Documentation, community workflows, licensing, privacy
checks, and metadata can be reviewed safely while the repository remains
private.

## Current GitHub State

| Field | State before this milestone |
|---|---|
| Repository | `CheickDiakite-yikes/neurodecodekit` |
| Visibility | Private |
| Default branch | `main` |
| Active preparation branch | `codex/loops-8-19-validated` |
| Issues | Enabled |
| Discussions | Disabled |
| Wiki | Disabled |
| Description | Empty |
| Homepage | Empty |
| Topics | Empty |
| Detected license | None |

The active branch is materially ahead of `main`. Public visibility must not be
changed until the open-source milestone is reviewed and merged, or the default
branch is deliberately updated. Publishing the current default branch would
present stale proof boundaries and omit the new safety/community files.

## Added Public Surface

- detailed proof-first `README.md`;
- `CONTRIBUTING.md` with dedicated EEG data and hardware paths;
- `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`, `SUPPORT.md`, and `SECURITY.md`;
- `CITATION.cff`;
- provisional Apache-2.0 `LICENSE` and `NOTICE`;
- `THIRD_PARTY_NOTICES.md` preserving Brain2Qwerty/SpanishBCBL terms;
- bug, EEG data, EEG hardware, and research-result issue forms;
- pull-request template and code ownership;
- one-thread base and optional-neuro GitHub Actions jobs;
- Gitleaks default configuration plus one exact documented-hash finding
  fingerprint.

## License Boundary

The proposed public license is Apache-2.0 for NeuroDecodeKit's original source
code and documentation.

This does not relicense:

- Brain2Qwerty source, models, papers, names, or assets;
- SpanishBCBL recordings, logs, labels, or derived participant-level data;
- optional dependencies;
- device SDKs, firmware, sample recordings, or trademarks;
- contributor material that the contributor had no right to submit.

Brain2Qwerty and SpanishBCBL are documented separately as
`CC-BY-NC-4.0`. The lead maintainer should explicitly approve the Apache-2.0
choice before changing repository visibility. This is an engineering readiness
record, not legal advice.

## Tracked-Content Audit

Measured on the active branch before the documentation additions:

```text
tracked files:                 182
git object store:              6.22 MiB loose objects plus 332.37 KiB pack
largest historical blob:      321,169 bytes
tracked data/ entries:         data/.gitkeep
tracked cache/ entries:        cache/.gitkeep
tracked neural recordings:    0 found by extension/name scan
tracked NPZ/Zarr caches:       0 found by extension/name scan
git-lfs dependency:           not used
```

Local ignored `data/`, `cache/`, `outputs/`, `.venv/`, and `.codex_work/`
content is not evidence of tracked public content. Run the audit again from the
exact release commit.

## Secret Scan

Gitleaks 8.30.0 scanned 31 commits and approximately 2.58 MB of additions.
It reported one `generic-api-key` candidate in
`docs/LOOP_20_NEUROTOKEN_CACHE_V0.md`.

Manual review confirmed that the candidate is a labeled 64-character SHA-256 of
a deterministic NeuroToken numerical payload. Adjacent lines contain source
cache and split-report SHA-256 values for reproducibility. It is not a token,
credential, signed URL, or identifier with authority.

`.gitleaks.toml` keeps the complete default rule set. `.gitleaksignore` records
the exact commit/path/rule/line fingerprint of this one reviewed finding. It
does not suppress another hexadecimal string, another line, another commit, or
another rule.

The scan must be rerun after all documentation and before publication.

## Neural-Data Privacy Gate

Before release, confirm:

- no raw recording or behavioral/event target file is tracked in current or
  historical commits;
- no participant table, free-text annotation dump, target sentence list, exact
  acquisition timestamp, device serial, or private cloud link is tracked;
- no generated cache, embedding, prediction/error report, or inspection debris
  is tracked;
- every example uses synthetic or placeholder paths;
- local ignored artifacts remain outside staged changes;
- GitHub issue forms warn against uploads;
- private vulnerability reporting is available or an alternate private route is
  documented.

## Community Gate

Before release:

- validate every issue form on GitHub after merge;
- create the referenced labels and descriptions;
- ensure issue-template links resolve on `main`;
- decide whether to enable Discussions;
- decide whether branch protection and required CI should be enabled;
- enable private vulnerability reporting when GitHub permits it;
- verify `CODEOWNERS` resolves to the maintainer account;
- review the conduct-reporting route for a sustainable private contact.

## Repository Metadata Gate

Safe metadata can be applied while the repository remains private:

- description;
- topics;
- issue labels.

Do not invent a homepage. The GitHub repository is the documentation home until
a maintained project site exists.

Recommended description:

```text
Local-first, reproducible EEG and MEG language-decoding research tools with bounded data access, honest baselines, and explicit proof boundaries.
```

Recommended topics:

```text
brain-computer-interface
brain-decoding
eeg
meg
neural-decoding
neurotechnology
signal-processing
mne-python
bids
python
local-first
reproducible-research
assistive-technology
machine-learning
brain2qwerty
```

## Verification Gate

The release candidate must pass:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m unittest discover -s tests -p 'test_signal_quality.py' -v
ruff check .
python -m compileall -q src tests
git diff --check
gitleaks git . --redact --no-banner
neurodecode --help
neurodecode inspect-recording --help
neurodecode make-signal-quality-fixtures --help
```

Also run one bounded synthetic RW2 create/inspect/report roundtrip and record:

- input and output bytes;
- runtime and peak RSS;
- reader/fixture counts;
- requested/returned sample values;
- materialized array bytes;
- raw/real/cache/target/model/training/network access;
- causality and end-to-end latency status;
- warnings and unavailable fields.

## Visibility Decision

Changing from private to public is a separate, explicit maintainer action. It
should happen only after:

1. this branch is reviewed and merged or made the deliberate default;
2. CI passes on the merged commit;
3. the license choice is approved;
4. the tracked-content and Gitleaks scans pass;
5. issue forms and security reporting are verified;
6. the README proof boundary matches the current closeout;
7. the maintainer confirms that publishing repository history is intended.

No command in this milestone changes repository visibility.

## Closeout Language

**Engineering capability added:** the repository gains a complete, reviewable
open-source collaboration surface with EEG-specific contribution paths,
licensing boundaries, security/privacy reporting, structured intake forms, and
bounded CI.

**Scientific or decoding claim not established:** documentation, community
files, and synthetic interface tests do not establish neural advantage,
unseen-person generalization, real-time decoding, portable EEG performance, or
clinical utility.
