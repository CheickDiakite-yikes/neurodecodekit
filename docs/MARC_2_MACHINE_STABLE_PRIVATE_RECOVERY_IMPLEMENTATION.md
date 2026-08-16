# MARC2-VR4P Machine-Stable Private Recovery Implementation

Date: 2026-08-16

Lane: `MARC2-VR4P`

Status: **Additive executor implemented and qualified on generated/mock inputs
only; the real expired certificate, retained structural manifest, output root,
archive payload, neural values, targets, models, predictions, and scores remain
untouched pending exact implementation commit, push, and two-job remote green**

Native registry:
`registries/marc2_machine_stable_private_recovery_implementation.v0.json`

Distinct shared-validator proof:
`registries/marc2_machine_stable_private_recovery_proof.v0.json`

## What Was Added

The dependency-free module
`neurodecodekit.datasets.marc2_machine_stable_private_recovery` exposes four
commands:

```text
plan
qualify
inspect
execute --implementation-commit ... --ci-run-id ... --base-job-id ... --optional-job-id ...
```

There is no source, output, root, cleanup, URL, dataset, participant, threshold,
sample-count, wait, retry, or model override. `plan` and `inspect` read only
committed public metadata. `qualify` uses temporary generated fixtures. The
fixed `execute` command remains ineligible until this exact implementation is
committed, pushed, and both required CI jobs are green.

## Proof Chain

The executor first validates:

1. green decision commit `eac37262dcf7cd4167475b7cc9145e3698d6dd9b`,
   CI `31969063955`, Base job `95218521665`, and Optional job `95218521647`;
2. the immutable request and decision hashes;
3. the native `MARC2-VR4P` implementation registry;
4. a distinct `MARC2-FW1B`-format proof record through the exact shared
   `validate_implementation_record` symbol;
5. supplied implementation commit and CI identifiers against local HEAD,
   tracked-worktree cleanliness, and green-decision ancestry.

The proof record binds the implementation module, tests, this document, native
registry, decision, request, readiness module, VR2 adapter, selector, and shared
validator. It never binds itself and does not use ambient HEAD as the fresh
certificate identity.

## Frozen State Machine

The real command can proceed only in this order:

1. no-follow preflight the exact expired mode-`0600`, 4,551-byte certificate;
2. open and read it once, require its exact SHA-256 and canonical semantics,
   require that it is expired, recheck its inode, and unlink only that file;
3. collect three consecutive passing readiness samples at least five seconds
   apart and write a fresh mode-`0600` certificate bound to the supplied exact
   green implementation commit;
4. validate certificate freshness, then recheck one-thread environment, peak
   RSS, and free disk without performing a second load gate;
5. no-follow preflight the exact mode-`0600`, 418,755-byte structural source;
6. require the fixed output root to be absent and create it mode `0700`;
7. write the mode-`0600` consumed marker; the marker write is the immediately
   preceding state-machine event before the one no-follow source content open;
8. read, hash, and strict duplicate-key-controlled parse the source once;
9. call the green VR2 adapter once, require source-object immutability, and
   reconcile `238 -> 195 + 43 -> 16 subjects / 96 bundles / 384 members`;
10. write one mode-`0600` private manifest and one mode-`0644` aggregate-safe
    report, with the fresh certificate and marker included in the combined
    4 MiB incremental-output cap.

Every refusal is final. There is no retry, rerun, resume, repair, substitution,
or fallback. Cleanup authority is restricted to the exact expired certificate
and invocation-created temporary files. No consumed executor or root is
imported, called, copied, edited, aliased, or exposed.

## Generated Qualification

The final measured qualification runs the complete state machine twice using
temporary generated certificate and 1,227-row structural fixtures. It requires
byte-identical certificates, markers, private manifests, and aggregate reports.
Twenty-seven direct mutations cover:

- certificate schema, commit, path, counters, canonical bytes, and expiry;
- thread environment, load, RSS, and disk refusals;
- no-follow file mode, size, symlink, hash, and inode-race checks;
- existing and symlink output roots;
- duplicate-key and non-object source JSON; and
- aggregate participant/member/path leakage, forbidden counters, claim drift,
  output cap, runtime cap, and RSS cap.

The selected qualification completed in `0.10705108400725294` seconds at
36,864,000-byte peak RSS. It processed 433,847 generated input bytes, emitted
222,279 generated output bytes inside invocation-created temporary roots, and
retained zero bytes. All real certificate, private source, archive, neural,
target, derivative, model, prediction, score, network, provider, hardware,
other-project, release, and claim counters remain zero.

## Resource And Privacy Boundary

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
real command runtime:                    <= 650 seconds
generated qualification runtime:        <= 30 seconds
peak RSS:                                < 256 MiB
minimum free disk before marker:         >= 15 GiB
combined registered output:              <= 4 MiB
network / archive payload bytes:         0 / 0
retry / rerun / resume / fallback:       0 / 0 / 0 / 0
```

The aggregate validator rejects participant IDs, member names, offsets, CRCs,
private paths, local paths, or `.codex_work` values. Selected declared bytes
remain reservation metadata and are never allocated or read by this stage.

## Verification

- Focused recovery/proof verification: 61 tests and 35 subtests pass.
- Complete pytest process: 3,827 tests pass, 35 skip, and 2,117 subtests pass.
- CI-shaped unittest process: 3,840 tests run with 35 skips.
- Both monolithic commands expose the same three pre-existing process-state
  failures: one sandbox-denied forkserver socket and two order-sensitive
  mechanical gates after accumulated process state. All three exact tests pass
  in fresh processes; the forkserver case requires permission to create its
  local Unix socket.
- Repository-wide Ruff, compilation, all 254 registry JSON parses, CLI help,
  plan, inspect, generated qualification, and `git diff --check` pass.

No MARC2-VR4P recovery test fails. Both remote CI jobs remain the required
clean-process acceptance gate for the exact implementation commit.

## Next Gate

Commit and push this exact implementation and require both CI jobs green. Only
then may the one fixed `execute` command use those exact proof identifiers. A
successful structural result must itself be recorded and remotely green before
Tier A `MARC2-FW2` preregistration. Archive payload, neural derivative,
training, prediction freeze, target delivery, and scoring remain a separate
Tier C packet and fresh-decision boundary.

## Claim Boundary

Engineering capability added: a proof-gated, machine-stable wrapper can freeze
a real target-free cohort identity from one exact structural manifest without
opening an archive member.

Scientific claim not established: generated qualification contains no real
private manifest, archive payload, neural value, target, prediction, or score
and establishes no neural effect, decoding performance, language decoding, or
thought-to-text capability.
