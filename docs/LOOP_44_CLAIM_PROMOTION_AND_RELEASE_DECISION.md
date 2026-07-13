# Loop 44: Claim Promotion And Release Decision

- **Status:** artifact-only review complete; release held
- **Prepared:** 2026-07-13
- **New experiment executed:** no
- **Protected, real-cache, consumed-evaluation, target, model, or device reads:** zero
- **Tag, GitHub release, archive, or DOI created:** no

## Decision

Loop 44 closes the first 20-loop post-roadmap with an evidence decision, not a
release ceremony. NeuroDecodeKit has earned several engineering claims and has
three real-data predictive results worth retaining. It has not earned a
positive neural-decoding, unseen-person, real-time, portable-hardware, or
clinical claim.

The decision is:

| Surface | Decision | Exact reason |
|---|---|---|
| Loop 44 artifact review | **Proceed / complete** | Every public claim now has a machine-readable evidence card and explicit ceiling. |
| Engineering source release | **Hold** | The current evidence stack is not on `main`; no version tag, archival DOI, Loop 38 lifecycle qualification, Loop 39 cross-machine run, or Loop 43 independent reproduction exists. |
| Scientific performance release | **Park** | S21 session 1 is inconclusive; S21 session 2 and S7 EEG are worse than their no-signal priors. |
| Clinical or arbitrary-thought wording | **Prohibit** | The project studies constrained typed tasks and has no clinical or arbitrary-thought evidence. |

The machine source of truth is
`registries/loop44_claim_release_matrix.v0.json`.

## What The Evidence Actually Says

### Engineering capabilities earned

1. Dry-run-first, byte-capped selective access can prevent accidental
   full-dataset movement.
2. Real S21 session-1 trial identity was reconciled for all 66 trials.
3. NeuroTokenCache v0 preserves modality, timing, masks, split identity,
   geometry, provenance, hashes, warnings, and causal status.
4. Target-free synthetic causal replay and bounded model/runtime gates are
   executable and inspectable on one CPU thread.

These are useful research-software results. They are not evidence that neural
signal improves text decoding.

### Real scientific results retained

| Frozen result | Signal model | No-signal comparator | Interpretation |
|---|---:|---:|---|
| S21 session-1, 5 test sentences | CER `0.947674` | CER `0.953488` | One fewer character edit; delta `-0.005814`; interval crosses zero; inconclusive near-null result. |
| S21 session-2, 63 trials | CER `0.917949` | CER `0.775458` | Delta `+0.142491`; the signal model is materially worse; consumed evaluation stays closed. |
| S7 EEG, 1,100 key events | accuracy `0.009091` | accuracy `0.122727` | Delta `-0.113636`; the signal model is materially worse. |

The honest current scientific conclusion is that these small local baselines do
not demonstrate neural advantage. That negative result narrows the next
experiment: a positive claim now needs a frozen source-validation event and a
strict unseen-person final comparison against no-signal and neural
derangement controls.

### Synthetic results stay synthetic

- Loop 22's learned motif result demonstrates a constructed mechanism.
- Loop 23 missed its frozen `6/8` exact-sequence gate at `5/8`.
- Loop 23.5's `16/16` blank calibration demonstrates one supervised synthetic
  correction, not neural decoding.
- Loop 24 found no faster behavior-preserving float32 replacement on the tested
  local CPU.

None can be combined with the real-data mechanics to imply a real neural
effect.

## Evidence Card Rule

Every promoted claim must bind:

```text
claim -> cohort -> task -> split -> comparator -> uncertainty
      -> resources -> access -> privacy -> license -> evidence path
```

Missing fields fail closed. Green tests, public source, a release tag, or a DOI
may strengthen software availability; none can fill a missing scientific
comparator or participant evaluation.

## Reporting Basis

The claim matrix applies:

- Model Cards for intended use, evaluation conditions, and limitations;
- Datasheets for dataset motivation, composition, collection, use, and
  maintenance;
- NIST AI RMF's documented, repeatable test/evaluation and risk controls;
- COBIDAS-MEEG transparency for M/EEG method, analysis, and sharing;
- ACM's separation of repeatability, reproduction, and replication;
- FAIR4RS versioning and reuse principles;
- GitHub/Zenodo's separation of a mutable repository from a versioned archived
  research object.

## Release Blockers

1. Review and merge the stacked evidence branches onto `main`.
2. Re-run complete tests, secret scanning, and tracked-payload checks at the
   exact candidate commit.
3. Execute, do not merely plan, the bounded Loop 38 lifecycle and Loop 39
   cross-machine gates.
4. Obtain one qualifying Loop 43 independent artifact-reproduction result.
5. Make an explicit maintainer decision before any tag, GitHub release, archive,
   or DOI.

An engineering alpha could eventually pass those gates without a positive
neural result, provided its negative and unavailable claims remain prominent.
A scientific-performance release additionally needs a qualifying real neural
effect.

## Access Incident

During this review, one overbroad `rg` command displayed text from the untracked
user-owned tracker inspection sidecar. A later artifact-tool workbook export
also overwrote that adjacent sidecar as an undocumented export side effect. The
exact prior copy was recovered from a local comparison artifact and restored to
SHA-256 `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.
It remains untracked and unstaged and was not used as neural/scientific
evidence. This incident is recorded because access claims must describe what
happened, not what was intended.

## Closeout

**Engineering capability added:** NeuroDecodeKit now has a strict,
machine-readable claim ledger that binds each engineering or scientific
statement to its evidence, limitations, access, privacy, and license record.

**Scientific or decoding claim not established:** Loop 44 performed no new
experiment and establishes no positive neural advantage, unseen-person
generalization, real-time decoding, portable or home-hardware performance,
independent reproduction, scientific replication, or clinical utility.
