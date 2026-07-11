# Governance

## Project Model

NeuroDecodeKit is currently maintainer-led. Cheick Diakite is the lead
maintainer and final decision maker for repository scope, releases, security,
licensing, and scientific claim boundaries.

The project is young enough that a lightweight model is more honest than
inventing committees. Governance should become more distributed as sustained
contributors take ownership of real areas.

## Decision Principles

Decisions are ordered by these priorities:

1. participant privacy, consent, security, and license compliance;
2. reproducibility and protection against leakage or false claims;
3. accessibility on ordinary local hardware;
4. inspectable interfaces and bounded resource use;
5. scientific usefulness;
6. model novelty or benchmark performance.

A result that is slower, smaller, or negative can still be the correct result.

## Roles

### Contributor

Anyone who files a useful issue, improves documentation, submits code, adds a
fixture, validates a format, or contributes research context.

### Area Reviewer

A contributor who has demonstrated sustained judgment in an area such as file
formats, privacy, evaluation, hardware, documentation, or release engineering.
Area reviewers may be requested in `CODEOWNERS` as the project grows.

### Maintainer

A trusted contributor who can triage issues, review and merge changes, protect
proof boundaries, and coordinate releases. Maintainer status requires a record
of careful review, not only code volume.

### Lead Maintainer

Responsible for final scope, governance, security, license, and release
decisions. The lead should document consequential decisions and recuse from
conduct or security reviews where there is a conflict of interest.

## How Decisions Are Made

Routine fixes can be decided in pull-request review. New schemas, optional
dependencies, data sources, hardware adapters, real-data reads, model families,
evaluation protocols, license changes, and claim-boundary changes require a
design issue or preregistration document before implementation.

The maintainer may:

- `proceed` when the frozen gate and evidence pass;
- `park` when a measured threshold fails or evidence is insufficient;
- `kill` a path that violates privacy, consent, security, or scientific
  integrity;
- request a smaller synthetic-first milestone.

Major decisions are recorded in `docs/DECISIONS.md`. Experimental closeouts
record exact inputs, outputs, resources, access counts, failures, and claims.

## Protected Evidence

Consumed test sets, participant recordings, target text, and private artifacts
are not ordinary project resources. A maintainer cannot waive a dataset license,
participant consent boundary, or institutional obligation.

Once a test split has been opened, it must be marked consumed for the decisions
it informed. A new result that tuned against it cannot call it fresh. Maintainers
may reject technically correct code that obscures this distinction.

## Releases

Before a public release, maintainers should verify:

- complete base and relevant optional test suites;
- Ruff, compile, CLI help, and `git diff --check`;
- no tracked recordings, caches, secrets, or inspection debris;
- repository history secret scan;
- current README, contribution, security, citation, and third-party notices;
- measured artifact/resource caps;
- explicit engineering and scientific claim sentences;
- release notes that identify parked and negative results.

Pre-1.0 schema compatibility may change, but changes must be versioned and
documented. Silent reinterpretation of an existing cache or report is not
allowed.

## License And Contributions

The current project license is Apache-2.0 for NeuroDecodeKit's original work.
Third-party software, datasets, recordings, and derived materials retain their
own terms. A license change requires explicit lead-maintainer approval, a
documented compatibility audit, and contributor-rights review.

No CLA or DCO is currently required. Contributions are accepted under the
license terms described in `CONTRIBUTING.md`.

## Governance Changes

Changes to this file should be proposed in an issue and reviewed like code.
Material changes to maintainer powers, contribution licensing, or conduct
enforcement should not be merged as incidental documentation edits.
