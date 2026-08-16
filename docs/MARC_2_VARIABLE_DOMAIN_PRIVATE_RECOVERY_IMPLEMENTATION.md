# MARC2-VR3 Variable-Domain Private Recovery Implementation

Date: 2026-08-16

Lane: `MARC2-VR3`

Status: **Generated/mock wrapper implemented and qualified; exact
implementation must be committed, pushed, and pass both required CI jobs
before the one registered private structural pass**

Machine implementation record:
`registries/marc2_variable_domain_private_recovery_implementation.v0.json`

Distinct shared-validator certificate:
`registries/marc2_variable_domain_private_recovery_proof_certificate.v0.json`

## Order Preserved

Authorization decision `944b6e8af434c2a6820435e0f18fe9490bf44248`
passed Base Python job `95202667384`, Optional Neuro Readers job
`95202667483`, and CI `31962561043` before this module was written. The
implementation uses that decision only for the exact two-stage `MARC2-VR3`
sequence. It does not treat the maintainer's requested future FW2 direction as
authority to read a payload, train, freeze predictions, open targets, or score.

## New Additive Module

The implementation is isolated in:

```text
neurodecodekit.datasets.marc2_variable_domain_private_recovery
```

It exposes four commands:

```text
plan
qualify
inspect --report <aggregate-report>
execute --implementation-commit <sha> --ci-run-id <id> \
  --base-job-id <id> --optional-job-id <id>
```

There is no source, output-root, URL, credential, subject, seed, split, cap,
member, exclusion-profile, or predicate override. The execute command contains
only remote-proof values that are unknown until the exact implementation has
passed both GitHub jobs. The source and destination identities are fixed in the
module and cannot be changed from the CLI.

The module imports only the green VR2 public adapter and the exact shared proof
validator. It does not import, call, copy, edit, alias, or expose a consumed
private executor. It does not contain a network client, archive-member reader,
neural reader, target reader, trainer, predictor, freezer, scorer, provider,
stream, device, or hardware interface. Heavy scientific dependencies remain
optional and are not imported.

## Two Distinct Proof Records

The native implementation registry has lane `MARC2-VR3`. The proof certificate
has lane `MARC2-FW1B` and is a distinct hashed input to the exact
`validate_implementation_record` function. The certificate binds the new
module, native registry, both new tests, packet-bound decision and request,
green VR2 module/contract/implementation/result, shared validator, and frozen
selector lineage. Neither record self-hashes.

Generated qualification calls the exact shared validator twice on the
canonical certificate and once for each of its 32 frozen malformed-certificate
cases. A different validator function, stale HEAD, dirty tracked worktree,
missing decision ancestry, changed certificate, changed registry, or changed
tracked artifact refuses before an output-root or retained-path operation.

At the later real gate, expected and observed proof envelopes must be identical
and must bind the current HEAD, implementation CI, both job IDs, clean tracked
state, decision ancestry, and certificate SHA-256. Proof validation is local
and performs no network call.

## Generated Qualification

Stage 1 uses only generated live-shaped manifests. It covers four valid
distributions of the 43 ineligible bundles and both canonical and reversed row
orders, for eight success paths. Every path calls VR2's exact
`adapt_live_domain_source` once, validates all 1,227 rows and all 238 complete
bundles before filtering, dynamically reconciles 195 eligible plus 43 valid
ineligible bundles, proves source immutability and mutable-object independence,
and accepts only VR2's unchanged target-free selector result.

The generated wrapper also exercises 32 ordered refusal cases across
`MARC2VDR-F00` through `MARC2VDR-F06`. Together with the 32 shared certificate
mutations, the direct matrix contains 64 refusals. Inherited VR2 and selector
tests independently preserve their 58 and 40 mutation matrices.

The final generated qualification processed 3,445,032 input bytes in
1.850114875 seconds at 38,322,176-byte peak RSS and emitted one 4,464-byte
aggregate report. It selected the same generated 16-subject, 96-bundle,
384-member structural prefix in every one of the eight success paths. Forty-one
focused wrapper, record, and decision tests pass under the one-thread
environment. The complete optional inventory covers 3,716 tests with 35 skips:
the A-M shard's one sandbox-blocked forkserver test passed in an exact isolated
process outside that socket restriction, and the N-Z shard passed directly.

This is not the private structural pass. Generated qualification performs zero
retained-path, private-manifest, consumed-root, network, archive, neural,
target, derivative, model, prediction, score, provider, hardware, retry,
release, or claim operations and retains no generated output.

## Fixed Private Reader

After this exact implementation becomes remotely green, the one registered
execution may operate only on the already registered 418,755-byte structural
manifest. Before the sole content open, it requires:

1. exact green implementation proof and shared certificate acceptance;
2. clean tracked HEAD and authorization-decision ancestry;
3. five numerical-thread environment variables fixed to one;
4. normalized one-minute load at or below one per logical CPU;
5. at least 15 GiB free disk and preflight RSS below 256 MiB;
6. the exact new output root to be absent and free of symlinks; and
7. every literal source component plus final file to be non-symlinked, with
   exact owner, mode `0600`, regular-file status, and size.

Only then does it create the new output root and atomically write a mode-`0600`
consumed marker. It performs one `O_NOFOLLOW` content open, reconciles the open
descriptor with the prior `lstat`, reads sequentially under a cap-plus-one
guard, computes one SHA-256, and performs one strict UTF-8 JSON parse with
duplicate-key and non-finite-number rejection. There is no second open,
fallback, retry, rerun, resume, repair, or alternate path.

## Output And Privacy

At most three files can be written under the new root:

```text
consumed_marker.v0.json
cohort_selection.private.v0.json
cohort_manifest.aggregate.v0.json
```

The marker and structural selection are mode `0600`. The aggregate report
contains only public participant IDs, predicate and split counts, reservation
totals, canonical hashes, measurements, warnings, unavailable fields, and
claim boundaries. Recursive validation refuses private rows, member names,
offsets, CRCs, source bodies, local paths, and private output paths. The
aggregate inspector rejects the private schema.

The whole sequence is limited to one CPU thread, one worker, one numerical
job, 30 seconds, 256 MiB peak RSS, 2 MiB combined output, 4 MiB incremental
disk, zero network bytes, and zero archive-member bytes. The 8 GiB value is
future reservation accounting only and creates no payload bytes.

## Verification Boundary

Focused behavior and implementation-record tests cover generated replay,
certificate validation, all 64 direct mutations, strict JSON, no-follow path
handling, source immutability, alias refusal, one-call VR2 integration, machine
caps, three-file output, aggregate leakage refusal, CLI shape, and dependency
isolation. Project-pinned Ruff, compilation, registry parsing, complete unit
tests, CLI help/plan/qualify/inspect rehearsal, and diff hygiene are required
before commit. Both remote CI jobs are then required before the private pass.

No archive member, signal sample, event, target, label, channel, geometry,
quality value, derivative, model, prediction, or score was accessed while
implementing or qualifying this wrapper.

## Next Gate

Commit and push the exact module, native registry, proof certificate, tests,
and documentation. Require both GitHub jobs to pass on that exact HEAD. Only
then may one no-retry execution use the fixed proof arguments from that green
run. Every route consumes the invocation. A success freezes only a target-free
structural cohort and still does not authorize `MARC2-FW2`.

Engineering capability added: NeuroDecodeKit now has a proof-gated,
single-open wrapper that can freeze a real target-free cohort from the full
variable structural domain without reading an archive member.

Scientific claim not established: generated qualification contains no human
neural payload, target, prediction, or score and establishes no neural effect,
decoding accuracy, brain-specific origin, language decoding, or thought-to-text
capability.
