# Open-Source Readiness

Date: 2026-07-10

Status: **Open-source collaboration surface merged to public `main`; latest RW2
evidence closeout remains in green draft PR #2**

## Purpose

This record separates public-release preparation from GitHub visibility,
default-branch publication, and scientific proof claims. Documentation,
community workflows, licensing, privacy checks, and metadata each require an
explicit review trail even after the repository is visible publicly.

## Current GitHub State

| Field | Current state after PR #1 and before PR #2 merge |
|---|---|
| Repository | `CheickDiakite-yikes/neurodecodekit` |
| Visibility | Public; no visibility-changing command was issued in this work |
| Default branch | `main` at merge commit `18a705e` |
| Open-source surface on `main` | Through commit `e5d89ed` via merged PR #1 |
| Active evidence closeout | Draft PR #2 from `codex/loops-8-19-validated` |
| Issues | Enabled |
| Discussions | Disabled |
| Wiki | Disabled |
| Description | Proof-accurate local-first EEG/MEG research description set |
| Homepage | Empty |
| Topics | 16 research, modality, reproducibility, and local-first topics set |
| Detected license | Default-branch API currently null; canonical Apache-2.0 text is corrected in PR #2 |
| Draft PR CI | 4/4 base and optional-neuro push/PR checks pass |

The repository was private at the start of this milestone and later reported
public; no visibility-changing command was issued in this work. PR #1 has now
merged the safety/community files, description, and contribution surface to
`main`. Draft PR #2 contains the latest RW2 closeout, README results dashboard,
current handoff, canonical license-text correction, and CI portability record.
Do not describe those latest results as default-branch content until PR #2 is
reviewed and merged.

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

Public visibility is active and PR #1 has merged the community surface. The
maintainer must still explicitly decide whether public visibility should
remain. The latest evidence closeout should be called current on the public
default only after:

1. draft PR #2 is reviewed and merged;
2. CI passes on the merge result;
3. Apache-2.0 for original NeuroDecodeKit work is approved and detected;
4. the tracked-content and Gitleaks scans pass;
5. issue forms and security reporting are verified;
6. the README proof boundary matches the current closeout;
7. the maintainer confirms that publishing repository history is intended.

No command in this milestone changed repository visibility. The description,
topics, and labels were updated without a visibility flag. The current state
should therefore be reviewed in GitHub's repository settings before release
signoff.

## Closeout Language

**Engineering capability added:** the repository gains a complete, reviewable
open-source collaboration surface with EEG-specific contribution paths,
licensing boundaries, security/privacy reporting, structured intake forms, and
bounded CI.

**Scientific or decoding claim not established:** documentation, community
files, and synthetic interface tests do not establish neural advantage,
unseen-person generalization, real-time decoding, portable EEG performance, or
clinical utility.
