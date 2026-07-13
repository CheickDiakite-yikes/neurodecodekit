# Loop 44 Primary-Source Research: Evidence-Gated Release

- **Status:** planning and artifact-only claim review complete
- **Experiment status:** `Not Started`
- **Prepared:** 2026-07-13
- **Execution authorization created:** no
- **Release authorization created:** no

## Research Decision

A public repository is not automatically a research release, and a research
software release is not automatically a scientific result. Loop 44 therefore
uses three independent gates:

1. **software availability:** source, license, installation, tests, version,
   archive, security, and privacy lifecycle;
2. **computational reproducibility:** exact artifacts, environments,
   comparisons, and independent execution;
3. **scientific support:** cohort, task, split, comparator, uncertainty,
   controls, and claim-specific external validity.

NeuroDecodeKit currently passes meaningful parts of the first gate, has only
planning evidence for the second, and has negative or inconclusive evidence
for the desired positive neural claim in the third. The release decision is
therefore `hold` for an engineering source release and `park` for a scientific
performance release.

## Primary Sources And Consequences

| Primary source | Stable principle used | NeuroDecodeKit consequence |
|---|---|---|
| [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) | Released models should state intended uses, evaluation conditions, performance, and limitations. | Every model card records signal use, comparator role, real/synthetic scope, and whether a release payload exists. |
| [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) | Dataset motivation, composition, collection, use, and maintenance should be documented. | S21 session 1, consumed S21 session 2, S7 EEG, and synthetic fixtures remain separate cards with distinct roles and licenses. |
| [NIST AI RMF 1.0](https://doi.org/10.6028/NIST.AI.100-1) | Risk management spans Govern, Map, Measure, and Manage; evaluation should be documented, repeatable, benchmarked, and uncertainty-aware. | Claims fail closed on missing comparators, uncertainty, access, risk, or evidence; negative outcomes stay visible. |
| [COBIDAS-MEEG](https://cobidasmeeg.wordpress.com/) | M/EEG methods, analysis choices, and sharing conditions need transparent reporting. | Modality, cohort, task, preprocessing role, split, and unavailable acquisition fields cannot be collapsed into generic “brain data.” |
| [ACM Artifact Review and Badging](https://www.acm.org/publications/policies/artifact-review-and-badging-current) | Repeatability, reproducibility, and replication are different evidence levels. | Maintainer CI is not independent reproduction; author-artifact reproduction is not independent scientific replication. |
| [FAIR4RS v1.0](https://doi.org/10.15497/RDA00068) | Research software is executable, composite, evolving, and versioned. | A mutable branch is not the final citable object; dependency, revision, license, and access metadata remain explicit. |
| [GitHub citation guidance](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content) | `CITATION.cff` and archive integration make releases more citable. | The existing citation file is a prerequisite, not proof that a tagged or archived release exists. |
| [Zenodo DOI versioning](https://zenodo.org/help/versioning) | Published versions and the evolving concept receive different DOI identities. | Any future archive must bind an exact release commit and distinguish version DOI from concept DOI. |

## Frozen Evidence Levels

| Level | Meaning | Current example |
|---|---|---|
| `E0` unavailable | no qualifying evidence | unseen-person, real-time, home hardware, clinical utility |
| `E1` contract/planning | reviewed protocol, no run | Loops 25-43 planning boundaries |
| `E2` synthetic mechanism | bounded fixture-backed execution | NeuroToken, causal replay, motif encoder |
| `E3` real-data mechanics | identity/preprocessing validated | S21 66/66 trial reconciliation |
| `E4` real-data predictive result | frozen model and comparator scored | S21 session 1/2 and S7 EEG results |
| `E5` independent artifact reproduction | different qualifying team reproduces author artifact | unavailable |
| `E6` independent scientific replication | independent scientific protocol reproduces effect | unavailable |

Higher is not synonymous with positive. The strongest current scientific
evidence is `E4`, but its result is negative or inconclusive.

## Repository And Release Audit

Measured on the Loop 44 branch before release mutation:

```text
repository visibility:            public
default branch:                    main
current evidence on main:          no
tracked files:                     295 before Loop 44 additions
tracked neural/array payloads:      0 found by tracked-path audit
tags:                              0
GitHub releases:                   0
archival DOI:                      unavailable
current source version:            0.1.0 in CITATION.cff
current Loop 43 push/PR CI:         green
Loop 38 execution:                 not started
Loop 39 execution:                 not started
Loop 43 execution:                 not started
```

The repository already has strong community, license, security, citation, and
contribution files. Its open-source readiness note had drifted to an early
two-PR state and must be refreshed. The current evidence lives across a stacked
branch series and is therefore not current default-branch evidence.

## Claim Promotion Rule

The machine registry freezes seven statuses:

- `promoted_engineering`;
- `retained_negative_scientific`;
- `fixture_backed_only`;
- `parked_measured`;
- `planning_only`;
- `unavailable`;
- `prohibited_overclaim`.

No status is inferred from prose. Each claim card must name its cohort, task,
split, comparator, uncertainty, resource record, access record, privacy state,
license, and evidence path when those fields apply.

## Why The Negative Results Matter

The desired positive neural claim has now failed three straightforward local
checks:

- S21 session 1 is a five-row near-null, not a stable advantage;
- S21 session 2 materially favors the no-signal prior;
- S7 EEG materially favors the no-signal prior.

That pattern rules out “just make the small model a little larger” as an honest
next move. A high-value next experiment must instead preserve target blindness,
prove source-validation signal dependence against derangements, and then use a
strict final-only unseen participant. It must also keep language priors outside
the neural-contribution gate.

## No Release Mutation

Loop 44 did not merge branches, create a tag, publish a GitHub release, reserve
or mint a DOI, upload an archive, release a participant payload, or contact an
external reproducer. Those are separate maintainer and execution decisions.

## Access Boundary

The review used tracked reports and public metadata only. It opened no raw
FIF/MAT payload, NumPy cache, consumed evaluation record, target list, model,
checkpoint, stream, SDK, or device. One overbroad documentation search did
display the untracked tracker inspection sidecar once; it remained unmodified
at closeout and unstaged and was not used as scientific evidence. During
workbook export it was overwritten once by an artifact-tool side effect, then
restored byte-exact from a local prior copy to its original SHA-256.

## Result

Loop 44's planning and artifact-review question is complete. The engineering
release remains held, the scientific performance release remains parked, and
the evidence gaps become the design inputs for Loops 45-64.
