# Loop 38 Primary-Source Research: Neural Data Privacy And Lifecycle

**Status:** planning research complete; experiment `Not Started`
**Prepared:** 2026-07-13
**Execution authorized:** no
**Protected payloads opened:** zero
**Generated experiment artifacts:** zero bytes

## Executive Decision

Loop 38 should eventually build a target-free synthetic lifecycle and redaction
contract, but this research does not authorize that build. The contract must
classify every artifact, every copy surface, and every deletion claim before a
real-derived BIDS envelope or public release can be called shareable.

The key design decision is to separate four things that are often collapsed:

1. **Redaction** removes prohibited fields from one representation.
2. **De-identification** reduces direct association but does not make neural
   data, stable hashes, or embeddings anonymous.
3. **Deletion receipts** describe a named scope and evidence level; path
   absence is not storage-media sanitization.
4. **Sharing authority** depends on consent, license, institutional governance,
   and release review, not only technical cleanliness.

The maximum current claim is `L38-C0_no_new_result`. No privacy scanner,
lifecycle inventory tool, synthetic fixture, deletion operation, identity
attack, protected-root scan, Git history rewrite, consent determination, or
release exists.

## Why This Is On The Scientific Critical Path

The future unseen-person result needs fresh participant evidence. If that
evidence cannot be inventoried, isolated, retained, deleted, and shared under
an explicit policy, a positive model score would still be scientifically and
operationally incomplete. Loop 38 therefore protects the route to the result;
it is not the result itself.

Published EEG work supports the risk premise. Meng et al. report that user
identity can be learned across EEG sessions and paradigms, and Chen et al.
demonstrate identity-protection methods over multiple EEG datasets. Those
studies justify treating raw EEG and learned representations as potentially
identifying. They do **not** establish a local attack rate, prove that a given
NeuroToken is identifiable, or authorize an attack here.

## Primary Sources And Exact Consequences

| Source | Stable finding used here | NeuroDecodeKit consequence |
|---|---|---|
| [NIST Privacy Framework](https://www.nist.gov/privacy-framework) | PF 1.0 is the stable published framework; PF 1.1 remains an initial public draft as of this research. | Pin 1.0, record the 1.1 draft status, and do not present a voluntary framework as certification. |
| [NISTIR 8062](https://doi.org/10.6028/NIST.IR.8062) | Privacy engineering uses predictability, manageability, and disassociability plus a problematic-data-action risk model. | Every future control maps to an objective and an observable repository behavior. Security alone is not privacy proof. |
| [NIST PRAM](https://www.nist.gov/privacy-framework/nist-pram) | PRAM helps identify data processing, risks to individuals, impacts, and controls. | Use it as a risk-analysis structure, not a compliance badge or legal determination. |
| [NIST SP 800-88 Rev. 2](https://doi.org/10.6028/NIST.SP.800-88r2) | Sanitization depends on media, sensitivity, technique, and a level of effort that makes recovery infeasible. | An application receipt can prove only its named path/copy checks. Media sanitization requires separate storage-owner evidence. |
| [GitHub sensitive-data removal](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) | History rewriting changes hashes, needs collaborator coordination, risks recontamination, and cannot clean unknown clones by itself. | Worktree deletion, `.gitignore`, and a clean current tree never imply clean history, forks, clones, pull-request refs, LFS, or CI artifacts. |
| [Open Brain Consent](https://doi.org/10.1002/hbm.25351) | Open neural-data sharing requires participant-facing consent designed for secondary sharing and local legal/ethics adaptation. | A template is evidence for planning, not proof that SpanishBCBL or a contributor recording may be redistributed. |
| [User Identity Protection in EEG-based BCIs](https://arxiv.org/abs/2412.09854) | Participant identity can be learned from EEG across multiple datasets and sessions. | Raw EEG, derived arrays, embeddings, individual predictions, and stable linkers default to sensitive or pseudonymous, never anonymous. |
| [OECD responsible neurotechnology guidance](https://www.oecd.org/en/topics/responsible-innovation.html) | Responsible neurotechnology includes safeguarding brain data, stewardship, accountability, transparency, and avoiding hype. | Lifecycle ownership and claim language are release gates, not optional documentation polish. |

## Stable Framework Pin

NIST PF 1.1 is visible but still labelled an initial public draft. Loop 38 pins
PF 1.0 and records 1.1 only as watched draft context. Future updates require an
explicit decision and tests; a draft cannot silently change field names or the
meaning of a frozen experiment.

The three NISTIR 8062 objectives map as follows:

| Objective | Required evidence |
|---|---|
| Predictability | A person or artifact owner can tell what data is collected, why, where it flows, what is emitted, and which copies remain unavailable. |
| Manageability | Named owners can review, restrict, retain, export, or narrowly delete artifacts according to consent and policy. |
| Disassociability | Processing avoids unnecessary identity association; pseudonyms and hashes are still treated as linkable unless release-scoped. |

## Sensitivity Model

Loop 38 freezes five levels:

| Level | Default content | Release posture |
|---|---|---|
| `L38-S0_public` | reviewed code, docs, schemas, synthetic aggregate examples | allowlist review |
| `L38-S1_internal_operational` | local paths, usernames, hosts, logs, environment details | redact before sharing |
| `L38-S2_pseudonymous_research` | subject/session/trial identity, timing, geometry, stable hashes, individual aggregate rows | privacy, consent, license, and cell-size review |
| `L38-S3_neural_or_derived_sensitive` | raw signals, windows, continuous caches, embeddings, Neuro Tokens, checkpoints, individual predictions | local by default; separate release review |
| `L38-S4_direct_or_governance_restricted` | direct mappings, consent/IRB records, targets, free text, credentials, release authority | separate controlled root; forbidden by default |

Sensitivity inherits from the highest source. Compression, quantization,
feature extraction, model training, aggregation, hashing, or renaming does not
automatically lower the level.

## Artifact And Copy Inventory

Every future inventory row needs:

- artifact class and schema version;
- named owner and approving authority;
- sensitivity and source sensitivity;
- exact approved root and relative path;
- creation purpose and producing command/commit;
- consent, license, and data-use status as separate fields;
- retention trigger, review date, and maximum duration;
- redaction behavior and prohibited fields;
- deletion scope, receipt level, and unresolved-copy count;
- release status, warnings, and claim boundary.

Eight artifact classes are mandatory: raw recording; event/target/consent;
derived signal cache; embedding/NeuroToken/checkpoint; report/aggregate/
manifest; log/trace/runtime metadata; temporary/intermediate/backup; and
Git/CI/release/remote copies.

Ten copy surfaces remain separate: approved raw root, approved cache root,
authorized ignored run root, OS temporary root, application logs, local sync or
backup, Git worktree/index/history/LFS, origin/forks/clones/PR refs, CI
logs/caches/artifacts, and release/download copies. A clean result on one
surface cannot upgrade another surface from `unresolved`.

## Redaction Boundary

The future scanner must test at least these classes:

- absolute paths, home directories, usernames, and hostnames;
- participant aliases, mapping tables, and identity-bearing filenames;
- acquisition dates, wall clocks, and high-resolution timestamps;
- device serials, MAC/IP addresses, board IDs, and stream identities;
- contact, institution, and operator identity;
- credentials, tokens, cookies, secrets, and environment values;
- consent, IRB, protocol, and data-use identifiers;
- target, prompt, response, sentence, label, and unrestricted free text;
- rare demographic, clinical, behavioral, and small-cell combinations;
- stable source, payload, membership, and bundle hashes;
- individual prediction, error, and confidence rows;
- neural windows, embeddings, Neuro Tokens, and checkpoints.

Hashes are not globally public by default. A stable hash can link the same
participant-derived object across reports or releases. Future public bundles
need release-scoped source identity, a documented threat model, and an explicit
decision about whether each hash is public, restricted, or omitted.

## Deletion Receipt Levels

| Level | What can be claimed | What remains unavailable |
|---|---|---|
| `D0` | no deletion claim | everything |
| `D1` | exact named paths are absent under one authorized root | aliases, backups, Git, remotes, media |
| `D2` | a local manifest rescan finds expected paths and aliases absent and lists unresolved copies | remote clones, provider copies, physical recovery |
| `D3` | Git/LFS/origin/PR/clone coordination status is explicitly recorded | unknown third-party copies and media sanitization |
| `D4` | external owner-approved sanitization evidence exists under SP 800-88 Rev. 2 or equivalent | only the exact media and method covered by that evidence |

Future deletion is dry-run by default, limited to a newly created or exact
fixture-owned root, and requires a pre-operation manifest and hash. It must not
follow symlinks, cross a root, remove unrelated files, rewrite Git history, or
touch user backups. Receipts list deleted, already missing, skipped, failed,
and unresolved objects without embedding sensitive bytes.

The wording `securely deleted` is forbidden unless the exact external
sanitization evidence supports it. `Deleted from the fixture root` is the
preferred narrow form for a future Stage A result.

## Consent, License, And Privacy Are Independent

The project must not infer any of the following:

- a public dataset is authorized for every redistribution;
- CC BY-NC 4.0 establishes participant consent;
- de-identification creates open sharing authority;
- a BIDS validator checks consent or privacy;
- an Open Brain Consent template proves local IRB approval;
- contributor ownership of a headset proves authority to share every recorded
  participant;
- a deletion request can recall unknown downstream public copies.

Any missing consent, license, institutional authority, retention owner, or
copy inventory blocks sharing while preserving the local research record.
This document is an engineering boundary, not legal advice.

## Local Metadata Audit

This planning pass used filenames, tracked metadata, source code, public docs,
and repository history names only. It opened no ignored cache, neural signal,
embedding, target, consent record, or protected MAT payload.

Measured current findings:

```text
current tracked neural/model candidate files:       0
current tracked neural/model candidate bytes:       0
all-ref history neural/model candidate paths:       0
real header/signal/cache/embedding/target reads:     0
identity or re-identification runs:                  0
deletion operations or Git history rewrites:        0
fixtures, scanner runs, releases, and uploads:       0
```

`.gitignore` excludes `data/*`, `cache/*`, `outputs/`, NPZ, Zarr, virtual
environments, and tool caches. That is a useful prevention layer, not a
lifecycle result. The current code also uses temporary directories extensively
in tests and preserves many ignored artifact paths in documentation. No
repository-wide owner, retention, copy, or receipt schema exists yet.

The unrelated untracked workbook inspection sidecar remains outside this scope.
It was not opened, modified, staged, deleted, or used as a privacy fixture.

## Future Stages

### Stage A: synthetic contract

After a separate authorization-only commit, create target-free synthetic path,
identifier, secret, archive, alias, temporary, Git-metadata, and deletion-
receipt fixtures under a fresh ignored root. No real values or identity model.

Maximum claim: synthetic inventory, redaction, refusal, and narrow deletion-
receipt behavior.

### Stage B: read-only local metadata coverage

After another authorization, scan only named repository and local-root
metadata. Payload bytes remain closed. Report checked, blocked, unavailable,
and unresolved surfaces separately.

Maximum claim: repository and named-local-root lifecycle coverage.

### Stage C: named real-derived lifecycle qualification

After exact protected-root authorization, qualify one named artifact set's
ownership, consent/license status, retention, redaction, and local receipts.
No identity attack and no automatic public export.

Maximum claim: named artifact local lifecycle qualified.

### Stage D: public release

Requires Loop 39 cross-machine evidence, external consent/license/governance
approval, Loop 44 release review, and a separately authorized allowlisted
bundle. No prior stage self-authorizes it.

## Future Acceptance Surface

The machine registry freezes:

- 32 false authorization fields;
- five sensitivity levels;
- eight artifact classes;
- ten lifecycle surfaces;
- 12 sensitive-field classes;
- 12 threat scenarios;
- five deletion-receipt levels;
- 24 fixture families;
- four separately authorized stages;
- eight outcomes and six claim levels;
- 26 acceptance gates and 36 refusal IDs.

Stage A remains capped at one thread, one worker, 120 seconds, 512 MiB peak
RSS, 8 MiB generated reports, 128 files, zero network/download/upload bytes,
zero real signal reads, and zero nonfixture destructive mutations. Standard-
library scanners are preferred and no base dependency was added now.

## Research Access And Resource Record

```text
high-level public web operations:          6
official or primary pages opened:          8
public response bytes/runtime/RSS:         unavailable by tool contract
current generated experiment bytes:        0
protected download bytes:                  0
real header/signal/cache/target reads:      0
S20/S25/S7/S21 protected operations:       0
identity attacks, models, training runs:    0
scanner runs and deletion operations:       0
uploads, releases, streams, devices:        0
```

## Closeout

Engineering capability added: a machine-checkable privacy risk map,
sensitivity taxonomy, artifact/copy inventory contract, redaction surface,
deletion-receipt ladder, consent/license firewall, staged evidence program,
and strict claim ceiling now exist.

Scientific claim not established: no fixture, protected payload, scanner,
deletion operation, identity attack, consent determination, model, training
run, target, score, release, device, or hardware was accessed, so there is no
privacy-safe dataset, anonymous neural representation, verified media
sanitization, shareable release, neural advantage, decoding accuracy,
unseen-person generalization, real-time behavior, or portable-hardware result.
