# Loop 43 Primary-Source Research: Independent Reproduction Challenge

- **Status:** planning research complete; experiment `Not Started`
- **Prepared:** 2026-07-13
- **Execution authorized:** no
- **External people contacted:** zero
- **Challenge packets, fixtures, or submissions created:** zero
- **Raw neural arrays or FIF/MAT payloads opened:** zero
**Verification incident:** 136 local cache JSON files parsed, including 11
known S21 session-2 report/metadata files; not used for tuning, scoring, or
claim selection

## Executive Decision

Loop 43 should eventually challenge one independent contributor to reproduce a
bounded, target-free NeuroToken causal-replay artifact using only a frozen
public packet. That artifact is **not eligible today**: Loop 37 has not produced
a release envelope, Loop 38 has not qualified its public lifecycle, and Loop
39 has not executed its required cross-machine matrix or independent handoff.

This research therefore closes the planning question without launching the
challenge. It freezes:

- the exact difference between maintainer repeatability, assisted external
  execution, independent artifact reproduction, and scientific replication;
- a commit-reveal order that prevents the expected result from informing the
  submitted result;
- public-only communication, independence disclosures, and a record-don't-fix
  checker role;
- strict untrusted-fork, secret, privacy, neural-data, and artifact caps;
- first-class exact, tolerance, partial, negative, unavailable, and invalid
  outcomes;
- four separately authorized stages and a hard Loop 44 claim-review ceiling.

The maximum current claim is `L43-C0_no_independent_result`. No challenge
packet, hidden oracle, public call, reproducer, submission, adjudication,
certificate, archive, DOI, badge, or independent result exists.

## Why This Is On The Scientific Critical Path

NeuroDecodeKit's real MEG and EEG predictive results are negative. That is a
scientific result, but it is not yet a positive neural-decoding result and it
has not been independently reproduced. Before a future positive result can be
trusted, another person must be able to exercise the public evidence path
without private maintainer state and obtain the registered outcome or a
well-classified failure.

Independent artifact reproduction is still not scientific replication. It can
show that the published computation is exercisable and that the same artifact
contract survives another qualifying environment and operator. It cannot show
that a neural effect generalizes to another participant, modality, acquisition,
device, task, or independently implemented method.

This distinction makes Loop 43 valuable even before the desired scientific
breakthrough. It tests whether the engineering evidence is actually usable by
someone outside the author workflow, and it makes failures useful inputs to the
next version instead of embarrassing outputs to hide.

## Primary Sources And Exact Consequences

| Source | Stable finding used here | NeuroDecodeKit consequence |
|---|---|---|
| [ACM Artifact Review and Badging](https://www.acm.org/publications/policies/artifact-review-and-badging-current) | Repeatability is same team/same setup; reproducibility is a different team using the same setup and author artifacts; replicability uses independently developed artifacts. Results Reproduced and Results Replicated are separate labels. | Loop 43's core target is one ACM-style artifact reproduction. A maintainer rerun cannot pass it, and reproduction cannot be relabeled scientific replication. |
| [CODECHECK principles](https://codecheck.org.uk/) | Independent execution is recorded by a checker; checkers record rather than investigate or fix, communication matters, credit matters, and the workflow must be auditable. | The reproducer records commands, obstacles, and evidence. Any repair creates a new version rather than mutating the submitted run. Public communication and contributor credit are explicit fields. |
| [CODECHECK project](https://codecheck.org.uk/project/) | A certificate concerns executable computation; openness is the default but sensitive human data can require restricted handling. | A future certificate can cover only the named computation. Neural recordings stay outside the public challenge and openness never overrides consent, license, or privacy. |
| [ReScience C author guidance](https://resciencec.readthedocs.io/en/latest/submitting.html) | A reproduction report reruns published code in another environment, while a replication article independently reimplements a protocol; obstacles and partial results are documented. | The core challenge uses author artifacts and is reproduction. A separate implementation is a later scientific protocol, not a stronger label applied to this run. |
| [ReScience C FAQ](https://rescience.github.io/faq/) | Reproduction tests the same computation/input; replication changes technical details and implementation. Failed attempts can be scientifically useful when checked carefully. | Exact, partial, negative, and unavailable outcomes remain in the evidence record. A failed run is not silently fixed, deleted, or rerun until it passes. |
| [NeurIPS reproducibility program](https://www.jmlr.org/papers/v22/20-303.html) | Code policy, a community reproduction challenge, and a checklist were complementary interventions rather than one magic tool. | NeuroDecodeKit needs a packet, checklist, submission contract, and public discrepancy record; CI alone does not establish independent use. |
| [FAIR4RS v1.0](https://doi.org/10.15497/RDA00068) | Research software is executable, composite, versioned, and must be reusable under qualified access conditions. | Source revision, instructions, dependencies, inputs, outputs, license, and access restrictions are separate machine fields. A mutable branch is not a reproducible research object. |
| [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use) | Untrusted pull-request code and workflow artifacts can compromise secrets, tokens, caches, and privileged jobs. | Contributor code must run only in an unprivileged read-only context, with no secrets or trusted caches. Untrusted artifacts are treated as data until validated. |
| [GitHub `pull_request_target` security](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) | Executing fork code from privileged `pull_request_target` or similar contexts creates a pwn-request path; ordinary `pull_request` is preferred when no secret access is required. | A future challenge may not use privileged workflow context to execute a fork. No secret, write token, trusted cache, protected data, or release credential is exposed. |

## Frozen Terminology

Loop 43 uses the ACM terminology consistently:

| Level | Team and artifacts | Allowed claim |
|---|---|---|
| Maintainer repeatability | Same author team, same public packet | The packet can be repeated by its authors in the measured environment. |
| Assisted external execution | Different person, but private or result-specific help is used | Usability evidence with assistance; not independent reproduction. |
| Independent artifact reproduction | Different qualifying person/team, public packet and author artifacts only | One independent reproduction outcome for the exact artifact and environment. |
| Scientific replication | Different team with independently developed artifacts and an appropriately independent experimental setup or data | Outside the core Loop 43 gate and requires its own scientific protocol. |

The project does not need a contributor to have never interacted with the
repository. It does require that the reproducer did not author the selected
implementation, fixture, oracle, expected outputs, or comparison policy, did
not receive the hidden oracle, and did not use undisclosed private guidance.
Relationships, write access, prior access, and conflicts are disclosed rather
than guessed.

## Selected Future Challenge Lane

The recommended future lane is:

```text
new target-free synthetic sentence cache
    -> deterministic NeuroTokenCache projection
    -> causal replay across the registered schedules
    -> canonical semantic and payload manifest
    -> independent public-only reproduction
```

This lane is close to the project's local real-time interface goal while
remaining free of participant recordings, target text, labels, language-model
outputs, checkpoints, and consumed seeds. It tests modality/timing/mask/split/
causality/provenance identity and deterministic replay, not neural decoding.

The future packet must use a newly registered seed and artifact revision. It
must not reopen seeds 2203, 2303, 2353, 2401, or 2402, reuse S7/S21, access
S20/S25, or use a target-bearing sentence as the oracle. The exact fixture,
seed, commands, and comparison policy remain unselected until the prerequisite
stages pass and a separate preregistration is committed.

## Independence And Commit-Reveal Order

The future order is immutable:

1. Maintainers freeze the packet, source commit, comparison policy, hidden
   oracle commitment, resources, security policy, outcomes, and claim ceiling.
2. A separate authorization-only commit permits a maintainer dry run. Its
   result is repeatability only.
3. After prerequisite closeouts, a separate authorization permits publication
   of the packet and challenge call.
4. The reproducer works from a clean root using only public sources. Every
   result-specific question and answer is retained publicly.
5. The reproducer freezes the submission core and commitment hash before any
   oracle reveal.
6. The oracle is revealed and verified against its prior commitment.
7. A separate adjudicator checks eligibility, order, hashes, comparisons,
   discrepancies, privacy, security, resources, and claims.
8. Any repair produces a versioned new packet or submission. The original
   failure remains visible.

A wall-clock timestamp alone is not the ordering proof. Packet, submission,
and oracle commitments must form a hash-bound sequence, with repository or
archive evidence for their publication order.

## Future Packet And Submission Contracts

The machine boundary freezes 28 packet fields and 34 submission-core fields.
The packet covers source identity, commands, environment, dependencies, input
and output manifests, semantic and numerical comparisons, warnings/refusals,
oracle commitment, security, privacy, independence, resources, outcomes,
credit, archive, and claim limits.

The submission core records:

- source and environment identity;
- every command, manual step, exit status, obstacle, and local modification;
- setup/execution duration, peak RSS, threads, workers, devices, network,
  dependency, input, output, and file counts;
- semantic, discrete, floating, container, warning, refusal, and unavailable
  comparisons;
- all protected/raw/cache/target/model/training access counters;
- independence disclosures, communication log, freeze commitment, oracle
  verification, discrepancies, outcome, and claim boundaries.

Runtime and setup cost are descriptive. They can reveal an accessibility
problem, but they cannot turn a semantic mismatch into a pass. Container bytes
may differ because of compression metadata while canonical payload manifests
remain exact; the packet must state which identity applies to each output.

## Negative And Partial Results Are Deliverables

The outcome taxonomy intentionally includes:

- exact reproduction;
- preregistered numerical reproduction;
- partial reproduction with discrepancies;
- a valid negative nonreproduction record;
- an unavailable supported environment or dependency;
- invalid identity, independence, oracle-order, privacy/security, or resource
  outcomes.

A valid negative outcome means the packet and process were followed but one or
more registered comparisons failed. It is not permission to widen a tolerance,
change a command, patch the reproducer's environment, or rerun until a pass
appears. The discrepancy receives a class, evidence pointer, owner, and state;
the next attempt receives a new version.

## Privacy, Data, And Security Boundary

The core challenge is public-code and target-free synthetic-artifact only.
Contributors must not upload:

- EEG, MEG, EOG, EMG, gaze, motion, audio, or other participant recordings;
- windows, embeddings, NeuroTokens, checkpoints, individual predictions, or
  consumed artifacts derived from a person;
- target text, labels, prompts, responses, participant metadata, consent or IRB
  records, device serials, precise acquisition timestamps, or local paths;
- credentials, signed URLs, tokens, cookies, environment secrets, trusted
  caches, or proprietary packages.

A contributor-owned EEG extension is not part of the core challenge. It must
remain local and requires a separate protocol governing consent, license,
retention, access, comparators, and aggregate outputs. It cannot upgrade a
synthetic artifact reproduction into neural, population, device, or scientific
evidence.

Fork code is untrusted. A future GitHub workflow must use read-only permissions,
no secrets, no privileged cache, and no protected artifacts. A privileged
`pull_request_target` or `workflow_run` job may not fetch and execute fork code.
The current repository already uses `pull_request` with `contents: read`, but
that is a support-audit fact, not a completed challenge security qualification.

## Current Repository Audit

The planning pass measured the current public contribution surface at base
commit `8607897`:

```text
repository visibility:                       public
repository license:                          Apache-2.0
tracked files:                               292
tracked neural/array payload files:          0
Git contributor identities:                  2
tags / releases / archival DOI:              0 / 0 / no
issue forms:                                 4
challenge-specific issue form:               no
challenge packet/submission schema:          no / no
CI workflows / profiles / OS / Python minor: 1 / 2 / 1 / 1
CI permissions:                              contents: read
pull_request_target usage:                   no
challenge packets / submissions / results:  0 / 0 / 0
```

The repository has a detailed contribution guide, pull-request template,
research-result form, code of conduct, governance, security policy, citation
file, and Apache-2.0 license. Those are strong prerequisites. They do not prove
that an external person can run a specific artifact, that the challenge is
safe, or that any result has been reproduced independently.

The unrelated untracked workbook inspection sidecar was not opened, modified,
staged, deleted, or used as challenge evidence.

## Four Separately Authorized Stages

### Stage A: contract, packet, and maintainer dry run

After a dedicated preregistration and authorization, create one new target-free
fixture, packet, hidden-oracle commitment, comparison registry, and maintainer
dry run. Maximum claim: registered interface plus author repeatability.

### Stage B: public challenge launch

Requires compatible Loop 37, 38, and 39 execution closeouts plus security,
contribution, and community review. Publish the exact packet and outreach text.
Maximum claim: public packet available; no external result.

### Stage C: external commit-reveal submission

One eligible external reproducer uses only the public packet, freezes a
submission before oracle reveal, and receives one registered outcome. Maximum
claim: one independent artifact-reproduction outcome for the exact packet.

### Stage D: independent adjudication and archive

A separate qualified adjudicator verifies eligibility, ordering, evidence,
comparisons, discrepancies, privacy, security, resources, and claim language.
Archive or DOI work needs separate authority. Maximum claim: independently
adjudicated artifact reproduction, never scientific replication by itself.

Authorization of one stage cannot authorize another. General continuation,
public repository visibility, open-source intent, or a volunteer message is not
authorization.

## Resource Envelope

| Resource | Future cap |
|---|---:|
| CPU threads / workers / accelerators | `1 / 1 / 0` |
| Stage A / B runtime | `300 / 300 sec` |
| Stage C / D runtime | `900 / 900 sec` |
| Peak RSS | `1 GiB` |
| Challenge packet | `16 MiB` |
| Reproducer submission | `32 MiB` |
| Adjudication and archive output | `16 MiB` |
| Total generated output | `64 MiB` |
| Dependency downloads | `1 GiB` |
| Runtime network requests after setup | `0` |
| Real or contributor neural payload | `0 bytes` |
| Paid/proprietary services | forbidden |

The current pass generated zero experiment bytes. It used five high-level web
operations, eight search queries, ten official or primary pages, and four
public GitHub metadata operations. Public response bytes and public-tool
runtime/RSS are unavailable from the tools. No challenge, contributor, raw
array, FIF/MAT payload, model, stream, device, or hardware operation occurred.

During local acceptance, an overbroad JSON validator used `Path.rglob` instead
of the Git-tracked file list. It read 603 local JSON paths, parsed 602, touched
136 files under `cache/`, and included 11 filenames explicitly bound to the
consumed S21 session-2 cross-session reports or metadata. It displayed no
contents and ran no inference, scoring, tuning, training, or parameter update,
but parsing is still a read. The zero-consumed-read claim is withdrawn. Future
JSON validation is restricted to Git-tracked paths, and this incident remains
part of the Loop 43 evidence rather than being edited away.

## Acceptance And Stop Rule

The future Stage C gate passes only when all 36 requirements and 48 refusals
remain exact, the reproducer qualifies independently, the public-only
communication and commit-reveal order verify, every protected access counter
is zero, all security/privacy/resource caps pass, and the registered output
comparison produces one retained outcome.

Stop or mark the attempt invalid on missing authorization, prerequisite,
identity, independence, public communication, oracle commitment, ordering,
semantic or numerical comparison, privacy, secret, neural payload, untrusted-
code isolation, resource, credit, or claim evidence. Do not repair in place,
weaken the gate, delete a negative result, or call author-artifact reproduction
scientific replication.

## What This Proves Now

Engineering capability added: a machine-checkable independent-reproduction
challenge design now freezes roles, independence, packet and submission fields,
commit-reveal order, comparison semantics, discrepancy handling, privacy,
security, credit, resources, staged authorization, and claim ceilings.

Scientific claim not established: no packet, fixture, oracle, outreach,
external reproducer, submission, raw neural array, model operation, decoding,
latency, device, or scientific experiment occurred, so no independent artifact reproduction,
scientific replication, neural advantage, decoding accuracy, unseen-person
generalization, real-time behavior, or portable-hardware result exists.

## Primary Sources

- [ACM Artifact Review and Badging](https://www.acm.org/publications/policies/artifact-review-and-badging-current)
- [CODECHECK principles](https://codecheck.org.uk/)
- [CODECHECK project](https://codecheck.org.uk/project/)
- [ReScience C author guidance](https://resciencec.readthedocs.io/en/latest/submitting.html)
- [ReScience C FAQ](https://rescience.github.io/faq/)
- [Improving Reproducibility in Machine Learning Research](https://www.jmlr.org/papers/v22/20-303.html)
- [FAIR4RS v1.0](https://doi.org/10.15497/RDA00068)
- [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub `pull_request_target` security](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
