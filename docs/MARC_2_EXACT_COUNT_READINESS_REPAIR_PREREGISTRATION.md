# MARC2-VR33A Exact-Count Readiness Repair Preregistration

Date: 2026-08-23

Lane: `MARC2-VR33A`

Status: **Frozen artifact-only and generated-only registration**

Machine contract:
`registries/marc2_exact_count_readiness_repair_contract.v0.json`

## Why This Is Next

The sole VR32P invocation returned aggregate route `MARC2VR32P-R2`, but its
aggregate telemetry reported five readiness samples against the packet's
registered three. VR32P is consumed and cannot be retried or repaired.

Static review localizes the mechanism to the wrapper's open-ended readiness
loop. It samples until it observes three consecutive passing values or reaches
600 seconds. That policy can produce more than three total samples, which is
incompatible with an exact three-sample contract.

VR33A is a generated-only repair for future lanes. It does not modify VR32P
or reinterpret R2. It freezes a reusable sampler that always attempts exactly
three samples, sleeps exactly twice between them, and returns ready only when
all three samples pass.

## Frozen Behavior

The sampler has one immutable sample count of three and one immutable interval
of five seconds. It accepts only injected in-memory callbacks for generated
qualification. It has no path, URL, timeout, sample-count, route, output,
retry, or resource override.

Eight generated pass/fail patterns are fixed:

| Pattern | Expected result |
|---|---|
| `PPP` | ready |
| `PPF` | not ready |
| `PFP` | not ready |
| `FPP` | not ready |
| `PFF` | not ready |
| `FPF` | not ready |
| `FFP` | not ready |
| `FFF` | not ready |

Each pattern runs across two exact replays. All 16 paths must make exactly 48
sample-provider calls and 32 sleeper calls. Every successful path must return
exact sequences 1, 2, and 3, preserve an immutable copy of each generated
sample, and retain zero output.

An adversarial matrix must reject malformed mappings, sequence mismatch,
non-Boolean pass values, non-finite or non-JSON values, provider exceptions,
sleeper exceptions, constant mutation, CLI overrides, and attempts to expose
an execute command. At least 40 direct refusals must pass.

## Implementation Shape

The future implementation is one additive standard-library module:

`src/neurodecodekit/datasets/marc2_exact_count_readiness.py`

It may expose only `plan` and `qualify`. Its collection function must contain
no `while` loop, must use a bounded three-iteration path, and must not read or
write the filesystem. Qualification must use generated in-memory samples and
must not call the VR32P sampler.

The implementation must leave the consumed VR32P wrapper byte-identical. A
future private wrapper may adopt VR33A only through a new, separately frozen
contract and Tier C decision.

## Boundaries

VR33A may read only the five committed artifacts bound in the machine
contract and may create generated in-memory fixtures. It may not touch
`.codex_work`, readiness files, consumed markers, private paths, consumed
VR20P/VR22P/VR24P/VR26P/VR28P/VR30P/VR32P state, archives, signal, events,
targets, labels, models, predictions, scores, network, providers, streams,
devices, hardware, or another project.

It authorizes no real execution, private source access, retry, rerun, cohort
freeze, FW2/CIL1 work, release, or scientific claim. Heavy dependencies and
base dependency changes are forbidden.

## Resource Envelope

- one CPU thread, worker, and numerical job;
- 15 seconds maximum generated qualification runtime;
- less than 128 MiB peak RSS;
- at most 1 MiB generated input;
- at most 1 MiB aggregate output;
- zero retained output;
- zero network and new payload bytes.

## Acceptance Gates

1. All five fixed inputs match exact byte counts and SHA-256 digests.
2. VR32P result commit `2c3b901b5536191d181c12d54106e45d9574b309`
   and both jobs in CI `32633522416` are bound before implementation.
3. The consumed VR32P wrapper remains byte-identical.
4. The new collection function has no `while` loop and no count override.
5. All 16 generated paths make exactly 48 provider and 32 sleeper calls.
6. Only `PPP` returns ready; all other patterns return not ready.
7. Every successful path returns exactly three immutable samples with
   sequences 1, 2, and 3.
8. Both replays are exact.
9. At least 40 direct refusals pass.
10. No generated source or report is retained.
11. Complete dependency-light tests, pinned Ruff, compilation, registry
    parsing, CLI help, and diff hygiene pass.
12. Every private, archive, neural, target, model, network, hardware,
    FW2/CIL1, other-project, and claim counter remains zero.

Engineering capability proposed: make future proof-gated readiness checks
obey an exact finite sample budget instead of an open-ended consecutive-pass
loop.

Scientific claim not established: this registration accesses no neural
payload, target, model, prediction, or score and establishes no neural effect,
decoding accuracy, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
