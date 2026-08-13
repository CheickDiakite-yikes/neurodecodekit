# MARC2-FW1 Freewill Prefix Selection Preregistration

Date: 2026-08-13

Status: **Generated-fixture-only contract frozen; implementation not started;
the retained private Freewill inventory remains unopened under MARC-2**

Registry: `registries/marc2_freewill_prefix_selection_contract.v0.json`

## Decision

MARC2-FW1 will select the largest storage-safe contiguous prefix of an already
preregistered participant rank. The rule may use only public eligibility,
private ZIP-directory structure, and exact byte reservations. It may not use
an event count, target, label, bad-trial flag, onset, signal sample, quality
metric, technical-validation outcome, model result, or score.

The selector has a hard floor of 12 participants and a ceiling of all 19
publicly eligible 250 Hz participants. It cannot skip a large or incomplete
participant to admit a later one. This preserves the previously frozen first
12 while allowing more participant-level power if the exact six-run bundles
fit the maintainer's 8 GiB incremental-data ceiling.

This contract authorizes generated fixtures only after its exact commit is
pushed and both required CI jobs are green. It does not authorize the retained
private inventory, an archive request, a local header, member payload, signal,
event, target, derivative, model, prediction, score, or provider call.

## Green Research Anchor

The five-work-order MARC-2 architecture is exact commit
`ae4d43aabbbe058658c1d77057431f7de331c958`. It passed Base Python job
`94368928633` and Optional Neuro Readers job `94368928658` in CI
`31675452031` before this contract was created.

The source inventory result remains the consumed public central-directory
audit. It binds:

```text
Freewill archive bytes:              13,591,548,048
central-directory entries:          1,227
regular files / directories:        1,025 / 202
retained private manifest bytes:     418,755
retained private manifest SHA-256:   2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
canonical inventory SHA-256:         da0270a2d8f86106fe25e2246c1b969be448084b1a40c492c885580992c48d69
whole/member payload bytes:          0 / 0
```

MARC1-P1A later opened and parsed that private inventory once, then consumed
before joint selection because its Wrist transport gate failed. That read is
historical evidence, not MARC2-FW1 authority. The old selector, consumed root,
and old marker may not be reused, reopened, renamed, or repaired.

## Public Eligibility

Freewill-23 reports 23 participants, 49 recordings, 238 runs, and 6,808
trials. MARC2-FW1 keeps the published eligibility rule from the earlier
prospective design:

- use the 250 Hz acquisition tier;
- require both `ses-01` and `ses-02`;
- require at least three runs in each selected session;
- exclude single-session `sub-02` and `sub-17`; and
- exclude 1,000 Hz `sub-13` and `sub-15`.

The 19 eligible IDs are fixed before private access:

```text
sub-01 sub-03 sub-04 sub-05 sub-06 sub-07 sub-08 sub-09 sub-10 sub-11
sub-12 sub-14 sub-16 sub-18 sub-19 sub-20 sub-21 sub-22 sub-23
```

No private row may add an ID, rehabilitate an excluded participant, change a
sampling tier, or create an eligibility exception.

## Preserved Participant Rank

To avoid a new seed after earlier metadata work, MARC2-FW1 preserves the exact
MARC1-P1 Freewill seed:

```text
MARC1-P1|10.6084/m9.figshare.28632599.v1|participant-rank-v0
```

For each public eligible ID, compute:

```text
SHA256(UTF8(seed) || 0x00 || UTF8(subject_id))
```

Sort by lowercase hexadecimal digest and then subject ID. The complete rank is:

```text
sub-08 sub-10 sub-07 sub-22 sub-19 sub-16 sub-14 sub-04 sub-05 sub-03
sub-09 sub-11 sub-12 sub-23 sub-20 sub-01 sub-18 sub-21 sub-06
```

The first 12 are byte-identical to the old preregistration. No seed, encoding,
separator, digest, case, tie breaker, eligibility list, or order override is
available.

## Run Bundle And Split

For every candidate participant in rank order:

- use `ses-01` as fit;
- use `ses-02` as target-blind held-out;
- ignore later sessions;
- take the first three numerically ordered complete run bundles in each
  selected session; and
- refuse if a required prefix participant lacks a complete bundle.

One complete run bundle has exactly four regular members with the same BIDS
subject, session, task, and run stem:

```text
_eeg.eeg
_eeg.vhdr
_eeg.vmrk
_events.tsv
```

The selector sees only the central-directory declarations. It does not open a
ZIP local header or any of those four members. An `_events.tsv` filename is
structural metadata; event content and event count remain forbidden.

Each selected participant contributes exactly six bundles, 24 members, three
fit bundles, and three held-out bundles. At the floor this is 72 bundles and
288 members. At the ceiling it is 114 bundles and 456 members.

## Maximal Storage-Safe Prefix

For each regular member, reserve:

```text
compressed_size + 30 + UTF8(member_name)_bytes + 65,535
```

This includes the declared compressed payload plus the fixed local-header
prefix, filename, and maximum ZIP extra-field length. It is a future network
and incremental-disk reservation, not permission to request those bytes.

Walk the frozen participant rank in order. For each participant, form the
exact six complete bundles and add the reservations for all 24 members.

1. If the first 12 participants exceed 8 GiB, route to a measured refusal.
2. After the floor, include each next participant only if its complete
   24-member addition keeps the total at or below 8 GiB.
3. Stop at the first participant that would exceed the cap.
4. Never inspect or admit a later participant after that stop.
5. If all 19 fit, select all 19.

This is a maximal contiguous prefix, not a knapsack, quality filter, or
convenience sample. Size can determine where the frozen prefix stops; it can
never reorder participants, alter a split, choose a run, drop a companion, or
substitute a later ID.

## Target Firewall

The selector must have no event parser, VHDR or VMRK parser, neurophysiology
reader, archive extractor, model, predictor, trainer, or scorer. Forbidden
selection inputs include:

- event or trial content and counts;
- target, label, response, or class balance;
- bad-trial, rejection, or signal-quality fields;
- movement-onset or timing values;
- channel, geometry, reference, or impedance values;
- local-header or payload bytes;
- technical-validation outcomes; and
- any model prediction, loss, or score.

The future scientific split remains session-held-out. A later analysis must
physically separate fit targets, held-out target-blind signals and controls,
hash-frozen predictions, and one post-green held-out target delivery. This
selector does not create any of those surfaces.

## Privacy And Output

A future real selector may create exactly two new files in a separately bound,
absent, Git-ignored root:

- a mode-`0600` private manifest with exact selected member identities,
  offsets, sizes, CRC declarations, split roles, and source hashes; and
- an aggregate public result with the public participant IDs, participant,
  bundle and member counts, fit and held-out counts, byte reservations,
  domain-separated hashes, warnings, and route.

The aggregate result may not expose a member name, local-header offset, CRC,
raw URL, local path, private source row, raw response, or raw header. Aggregate
inspection must reject the private schema. Overwrite, symlink output, output
outside the registered root, and old-root access refuse.

## Generated Qualification

After this exact contract is committed, pushed, and remotely green, a new
dependency-free module may qualify only generated data:

- exactly 1,227 generated inventory rows using the retained private schema;
- all 19 public eligible participants and their 114 complete bundles;
- a main fixture with 505,000,000 declared compressed bytes per participant,
  producing a maximal 16-participant prefix under the exact overhead formula;
- exactly 96 selected bundles and 384 selected members in that main fixture;
- cap-minus-zero, cap-plus-one, floor-12, and all-19-fit boundaries;
- at least two irrelevant row-order replays;
- 40 exact adversarial mutations; and
- byte-identical deterministic replay with all real-operation counters zero.

The generated module may expose only `plan`, `qualify`, and aggregate
`inspect`. It may not accept a real path, URL, host, credential, participant,
seed, cap, split, member, target, model, or score override. It may not expose
`execute`.

## Resource Limits

```text
generated CPU threads / workers / jobs:      1 / 1 / 1
generated runtime / peak RSS:                30 sec / 256 MiB
generated combined output:                   <= 2 MiB
generated aggregate output:                  <= 1 MiB
future private inventory opens / bytes:      1 / 418,755 exact
future archive/local-header/member bytes:    0 in MARC2-FW1
future selected reservation:                 <= 8 GiB
future incremental data ceiling:             <= 8 GiB
future free disk before any acquisition:     >= 15 GiB
future private derivatives:                  <= 64 MiB
```

The current contract performs zero private reads and zero payload movement.

## Router

1. `MARC2FWG-F00`: contract, artifact, or green-proof mismatch.
2. `MARC2FWG-F01`: generated inventory identity, schema, field, count, or
   source mismatch.
3. `MARC2FWG-F02`: unsafe member, unsupported ZIP declaration, malformed BIDS
   identity, or incomplete bundle.
4. `MARC2FWG-F03`: eligibility, rank, participant, run, session, split, or
   prefix-order mismatch.
5. `MARC2FWG-F04`: floor, cap, reservation, maximal-prefix, or boundary
   mismatch.
6. `MARC2FWG-F05`: privacy, output, overwrite, resource, cleanup, or replay
   mismatch.
7. `MARC2FWG-R1`: every generated selection gate passes.

`MARC2FWG-R1` is engineering evidence only. It cannot authorize the retained
private inventory, archive members, payload acquisition, neural data, targets,
models, predictions, scores, language work, or a scientific claim.

## Acceptance Gates

The generated closeout is eligible only if:

- the green MARC-2 research anchor and all artifact hashes match;
- the full 19-person preserved rank replays exactly;
- the generated inventory has exactly 1,227 rows and 114 complete bundles;
- the main fixture selects the maximal 16-person contiguous prefix;
- selected counts are exactly 96 bundles and 384 members;
- fit and held-out sessions contribute equal bundle counts;
- the floor-12, all-19, exact-cap, and cap-plus-one routes are correct;
- row order, member size, and CRC cannot alter participant rank or run choice;
- no skipped participant, substitution, later-session use, or backfill occurs;
- no content, signal, event, target, quality, model, or score interface exists;
- all 40 mutations refuse in their frozen class;
- private and aggregate surfaces remain separated;
- deterministic replay is byte-identical;
- runtime, RSS, output, cleanup, and one-thread limits pass; and
- every private, real-data, neural, target, model, score, provider, retry, and
  claim counter remains zero.

## Next Gate

1. Commit and push this exact contract.
2. Require Base Python and Optional Neuro Readers to pass at that commit.
3. Implement and qualify the generated/mock-only selector.
4. Commit and push that exact implementation and require both jobs green.
5. Record one bounded generated closeout.
6. Only after its green result may Tier A prepare an all-false Tier C request
   for one exact read of the retained private inventory.

The maintainer's earlier continuation was already bound to a different packet
and is not retroactive authority for the private read. Archive, payload, signal,
target, model, prediction, scoring, replication, and language operations remain
closed after generated success.

## Claim Boundary

Engineering capability added if successful: NeuroDecodeKit can maximize a
target-free, session-held-out participant prefix under an exact storage ceiling
without using signal quality or scientific outcomes.

Scientific claim not established even if successful: generated ZIP-directory
metadata contain no human neural signal, prediction, or score and establish no
neural effect, decoding accuracy, language decoding, or thought-to-text result.
