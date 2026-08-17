# MARC2-VR7P Dynamic Private Selection Recovery Implementation

Date: 2026-08-16

Lane: `MARC2-VR7P`

Status: **Generated/mock implementation and measured qualification complete;
real target-free structural pass remains unconsumed pending exact remote-green
implementation proof**

Decision `a318521cf9adb057617e839ead0003d89c3cab84` passed Base Python
job `95244335512`, Optional Neuro Readers job `95244335508`, and CI
`31979669507` before implementation began. The decision binds only the VR7P
two-stage sequence. It does not authorize FW2, archive payload access, neural
data, training, prediction, target delivery, scoring, or a live run.

## Additive Surface

The new dependency-free module is:

```text
src/neurodecodekit/datasets/marc2_dynamic_private_selection_recovery.py
```

Its commands are `plan`, `qualify`, `inspect`, and `execute`. The `execute`
surface accepts only an exact implementation commit and three remote CI proof
identifiers. It exposes no configurable source, output, URL, cleanup, retry,
resume, repair, fallback, or substitution argument.

The module does not import, call, patch, alias, or alter the consumed VR4P
executor. It independently implements the fixed machine, file, output, and
privacy state machine and calls the remotely green VR6 adapter exactly once.
The only heavy-operation count is zero; the base dependency set is unchanged.

## Fixed Future Sequence

After this exact implementation is remotely green, one command may:

1. validate the distinct committed proof record, exact supplied commit and CI
   identifiers, clean tracked worktree, and green-decision ancestry;
2. obtain three consecutive machine samples under the registered one-thread,
   load, RSS, disk, interval, wait, and sample-count thresholds;
3. create one fresh mode-`0600` certificate only at
   `.codex_work/marc2_machine_readiness/vr7p/readiness.v0.json`;
4. recheck threads, peak RSS, and free disk without adding a second load gate;
5. no-follow preflight the exact 418,755-byte structural source by parent
   shape, regular-file type, owner, mode, size, and race-sensitive identity;
6. create the new fixed output root and one mode-`0600` consumed marker;
7. open the structural source immediately after that marker, read and hash its
   exact bytes once, and strict-parse one JSON object;
8. call `adapt_dynamic_live_source` once and retain only an allowlisted VR6
   route code if it refuses; and
9. write one mode-`0600` private selection manifest and one mode-`0644`
   aggregate report under the combined 4 MiB output cap.

The generated stage touched no real or consumed `.codex_work` path: none was
statted, resolved, hashed, opened, changed, deleted, or reused during
implementation or qualification.

## Dynamic Boundary

The real result is not compared with a generated subject count, reservation
total, source hash, selection hash, or private-manifest hash. VR6 must measure a
maximal contiguous target-free rank prefix of 12 through 19 subjects. Every
selected subject must contribute six complete run bundles and 24 structural
companions, with session 1 assigned to fit, session 2 assigned to heldout, zero
split overlap, no row-random split, and no target, label, quality, outcome,
signal, prediction, or score field.

The aggregate report permits measured counts, byte totals, hashes, route codes,
and resource measurements. It rejects subject or participant IDs, member names,
paths, offsets, CRCs, private rows, upstream reasons, and private predicate
values. A VR6 refusal can expose only one code from `MARC2VR6-F01` through
`MARC2VR6-F08`; an unknown code fails closed without being echoed.

## Generated Qualification

The generated qualification exercised five subject boundaries in canonical and
reversed source-row order:

| Subjects | Bundles | Members | Selected reservation bytes | Paths |
| ---: | ---: | ---: | ---: | ---: |
| 12 | 72 | 288 | 8,589,934,592 | 2 |
| 14 | 84 | 336 | 8,489,934,592 | 2 |
| 16 | 96 | 384 | 8,539,934,592 | 2 |
| 18 | 108 | 432 | 8,579,934,592 | 2 |
| 19 | 114 | 456 | 8,589,934,592 | 2 |

All ten paths replayed twice with byte-identical outputs for the same exact
input. Canonical and reversed rows retained distinct raw-input hashes while
producing the same normalized private cohort and selection identity within
each profile.

The qualification passed 85 direct refusal mutations: 34 inherited VR6
selection/firewall mutations and 51 wrapper mutations. The wrapper matrix
covers certificate schema and expiry, machine samples, explicit thread state,
RSS and disk thresholds, strict JSON, missing/mode/owner/size/symlink/hash/race
file failures, output collisions, aggregate identity leakage, forbidden
counters, claims, and resource caps.

## Measurements

```text
fixed committed artifact reads:          12
fixed committed input bytes:        250,996
generated structural input bytes: 4,291,134
generated sequence output bytes:   2,681,772
retained generated output bytes:           0
runtime:                    5.951104625 sec
peak RSS:                      54,280,192 bytes
CPU threads / workers / jobs:         1 / 1 / 1
raw-data reads / real-cache reads:    0 / 0
model runs / training runs:           0 / 0
producer causal:       not applicable, structural metadata only
end-to-end latency measured:               no
```

Every real readiness, private source, output-root, content-open, real VR6,
cohort, archive, neural, target, derivative, model, prediction, score,
network, provider, device, hardware, other-project, release, and claim counter
remained zero.

## Verification Boundary

- Fourteen focused behavior tests and seven implementation/proof tests pass.
- The tests cover all five dynamic outcomes, both row orders, deterministic
  replay, marker-before-open adjacency, one VR6 call, output modes and
  inventory, aggregate privacy, route allowlisting, 51 wrapper mutations, the
  complete 85-mutation qualification, and CLI-safe refusal output.
- Ruff and module compilation pass.
- The canonical complete inventory ran 3,953 tests: 3,916 passed in the primary
  process, 35 skipped, one state-sensitive causal gate failed after the long
  process, and one forkserver worker was denied its Unix socket by the sandbox.
  All five causal-gate tests passed together in a fresh process. The exact
  worker passed outside the sandbox in 3.67 seconds. Thus all 3,918 non-skipped
  tests pass under their required process conditions, adding exactly 21 tests
  to the 3,932-test pre-change inventory with no new regression.
- Registry and proof JSON parsing, CLI plan/inspect/qualify, Ruff, compilation,
  and diff hygiene pass. Remote CI remains the final implementation gate.
- Until the exact implementation commit is pushed and both required CI jobs
  are green, no readiness invocation or private-path operation may begin.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now has a generated-qualified,
fixed-path, proof-gated wrapper that can freeze a dynamically measured
target-free structural cohort after exact remote-green proof.

Scientific claim not established: generated qualification accessed no real
structural source, archive or neural payload, target, prediction, or score and
therefore establishes no neural effect, decoding performance, language
decoding, live decoding, or thought-to-text capability.
