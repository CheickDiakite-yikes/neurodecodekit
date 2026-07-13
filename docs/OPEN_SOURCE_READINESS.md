# Open-Source Readiness

Date: 2026-07-13

Status: **public development repository; Loop 44 engineering release held;
scientific performance release parked**

## Purpose

This record separates four facts that are easy to blur:

1. the GitHub repository is publicly visible;
2. the current evidence branch stack is not yet merged to `main`;
3. no versioned, archived research-software release exists;
4. no positive real neural-decoding claim has been established.

Loop 44's machine-readable decision is
`registries/loop44_claim_release_matrix.v0.json`. Public visibility, green CI,
a tag, or a DOI cannot upgrade a scientific claim.

## Current GitHub State

| Field | Current state |
|---|---|
| Repository | `CheickDiakite-yikes/neurodecodekit` |
| Visibility | Public |
| Default branch | `main` |
| Current Loop 44 branch | `codex/loop-44-claim-release-research` |
| Current evidence on `main` | No; Loops 8-44 remain a stacked review series |
| Detected license | Apache-2.0 for original NeuroDecodeKit work |
| Upstream Brain2Qwerty/SpanishBCBL boundary | CC BY-NC 4.0; not relicensed |
| Issues | Enabled |
| Discussions | Disabled |
| Wiki | Disabled |
| Homepage | Empty by design until a maintained site exists |
| Topics | 20 research, modality, reproducibility, and open-source topics |
| Git tags | 0 |
| GitHub releases | 0 |
| Archival DOI | Unavailable |
| Independent reproduction | Not executed |
| Positive real neural advantage | Not established |

The last pre-Loop-44 tracked-path audit counted 295 tracked files and zero
tracked neural/array/model binary candidates. That is a branch-development
fact, not a final release scan. The exact candidate commit must be rescanned.

## What Is Ready

The repository has a substantial collaboration surface:

- proof-first `README.md` and `START_HERE.md`;
- `CONTRIBUTING.md` with dedicated EEG data, hardware, model, documentation,
  and reproduction paths;
- `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`, `SUPPORT.md`, and `SECURITY.md`;
- `CITATION.cff`, Apache-2.0 `LICENSE`, `NOTICE`, and
  `THIRD_PARTY_NOTICES.md`;
- structured bug, EEG data, EEG hardware, and research-result issue forms;
- pull-request template and code ownership;
- one-thread dependency-light and optional-neuro CI profiles;
- explicit privacy, license, target-leakage, no-signal-comparator, storage,
  runtime, and claim boundaries;
- a strict Loop 44 claim matrix with 16 evidence cards.

These are engineering prerequisites. They do not constitute a release or a
neural-decoding result.

## Claim Surface

### Promotable engineering claims

- bounded, dry-run-first selective data access;
- strict modality/timing/mask/split/provenance NeuroTokenCache contracts;
- 66/66 S21 session-1 trial identity reconciliation;
- target-free synthetic causal replay and bounded local mechanics tests.

### Real scientific findings that must remain visible

| Evidence | Signal model | No-signal comparator | Status |
|---|---:|---:|---|
| S21 session-1 frozen test, 5 sentences | CER `0.947674` | CER `0.953488` | inconclusive near-null |
| S21 session-2 consumed evaluation, 63 trials | CER `0.917949` | CER `0.775458` | signal model worse |
| S7 EEG consumed evaluation, 1,100 key events | accuracy `0.009091` | accuracy `0.122727` | signal model worse |

### Unavailable claims

- positive real neural advantage;
- zero-shot unseen-person generalization;
- end-to-end real-time neural text decoding;
- portable or home EEG/OPM-MEG performance;
- independent artifact reproduction;
- independent scientific replication;
- clinical utility or arbitrary-thought decoding.

## License Boundary

Apache-2.0 applies to original NeuroDecodeKit source and documentation. It does
not relicense:

- Brain2Qwerty source, models, papers, names, or assets;
- SpanishBCBL recordings, logs, labels, or participant-derived artifacts;
- optional dependencies;
- device SDKs, firmware, sample recordings, or trademarks;
- contributor material the contributor lacks authority to submit.

Brain2Qwerty and SpanishBCBL are separately identified as CC BY-NC 4.0. The
project must not bundle participant data, derived caches, predictions, target
text, or upstream model payloads into an Apache-2.0 release. This record is not
legal advice.

## Privacy And Payload Gate

Before any release candidate, confirm at the exact candidate commit and across
reachable Git history:

- no raw EEG, MEG, EOG, EMG, gaze, motion, audio, or behavioral payload;
- no event target list, sentence text, participant table, free-text annotation,
  precise acquisition timestamp, device serial, or signed/private link;
- no derived participant cache, NeuroToken payload, embedding, checkpoint,
  individual prediction, or error-row artifact;
- no generated inspection sidecar, local path, secret, credential, cookie, or
  environment file;
- all examples use synthetic or placeholder identities;
- issue forms and contribution docs reject participant uploads;
- private security and conduct-reporting routes work.

Loop 38 is planning research only. Its unexecuted lifecycle gate is a release
blocker, not paperwork that may be waived.

## Reproducibility Gate

Before calling the project a versioned reproducible release:

1. Review and merge the stacked evidence series onto `main`.
2. Freeze an exact source commit, supported environments, dependencies,
   commands, inputs, expected outputs, comparisons, and resource caps.
3. Run the Loop 39 cross-machine matrix rather than citing maintainer CI.
4. Run the Loop 43 independent author-artifact challenge with public-only
   communication and immutable discrepancy records.
5. Keep independent artifact reproduction separate from scientific
   replication.

Green maintainer CI establishes neither independent reproduction nor scientific
replication.

## Candidate Verification

The exact candidate commit must pass at minimum:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m unittest discover -s tests -p 'test_loop44_claim_release_matrix.py' -v
ruff check .
python -m compileall -q src tests
git diff --check
gitleaks git . --redact --no-banner
neurodecode --help
```

Verification must also report:

- exact commit and environment;
- test counts, skips, runtime, and peak RSS when available;
- tracked files and historical blobs;
- generated, data, cache, model, and secret candidates;
- license and citation validation;
- unresolved privacy, security, reproduction, and claim blockers;
- every unavailable field.

Do not rerun consumed scientific evaluations merely to qualify a release.

## Version And Archive Gate

`CITATION.cff` currently identifies version `0.1.0`, but no matching tag,
GitHub release, or archive DOI exists. A future release decision must:

1. select a version only after the exact candidate is green;
2. synchronize `pyproject.toml`, `CITATION.cff`, release notes, and docs;
3. create a signed or otherwise attributable maintainer decision;
4. create the Git tag and GitHub release only after approval;
5. archive the exact version if desired and record version-specific and concept
   DOI identities separately;
6. verify the public archive contains no protected or nonredistributable
   payload.

A DOI improves citability. It does not peer-review the work or establish a
neural effect.

## Community Gate

Before a first formal release:

- validate issue forms and links on `main`;
- create and document referenced labels;
- verify `CODEOWNERS` resolves correctly;
- decide branch protection and required checks;
- enable private vulnerability reporting if available;
- verify the conduct-reporting route is sustainable;
- label beginner, EEG-data, hardware, documentation, and reproduction
  contribution paths clearly;
- state that contributor-owned EEG remains local unless a separate consent,
  license, privacy, retention, and aggregate-output protocol is approved.

## Loop 44 Decision

| Decision | State |
|---|---|
| Artifact-only claim review | Proceed / complete |
| Engineering source release | Hold |
| Scientific performance release | Park |
| Clinical or arbitrary-thought claim | Prohibit |

The engineering hold can be cleared by completing the branch, security,
privacy-lifecycle, reproducibility, and maintainer gates. The scientific park
requires new qualifying evidence, not stronger release language.

## Closeout Language

**Engineering capability added:** Loop 44 provides a strict evidence and
release ledger that keeps source availability, reproducibility, scientific
support, privacy, and licensing as separate reviewable gates.

**Scientific or decoding claim not established:** Open source, tests,
documentation, tags, or archival identifiers do not establish positive neural
advantage, unseen-person generalization, real-time decoding, portable/home
hardware performance, scientific replication, or clinical utility.
