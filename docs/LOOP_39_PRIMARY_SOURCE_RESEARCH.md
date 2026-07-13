# Loop 39 Primary-Source Research: Cross-Machine Reproducibility Matrix

**Status:** planning research complete; experiment `Not Started`
**Prepared:** 2026-07-13
**Execution authorized:** no
**Protected payloads opened:** zero
**Generated experiment artifacts:** zero bytes

## Executive Decision

Loop 39 should eventually qualify six explicit Python, operating-system, and
dependency-profile cells. This research freezes the meanings, environment
fields, comparisons, resources, failure states, and claim ceiling. It does not
create a fixture, environment manifest, dependency lock, matrix job, package,
or result.

The maximum current claim is `L39-C0_no_cross_machine_result`. Existing CI is
valuable, but it currently exercises two profiles on one floating
`ubuntu-latest` and CPython 3.12 environment. That does not establish
cross-machine artifact reproduction, macOS support, all declared Python
versions, or a reproducible dependency environment.

The selected future matrix is intentionally small:

1. Ubuntu 24.04 x64, CPython 3.10, base profile.
2. Ubuntu 24.04 x64, CPython 3.11, base profile.
3. Ubuntu 24.04 x64, CPython 3.12, base profile.
4. macOS 15 arm64, CPython 3.12, base profile.
5. Ubuntu 24.04 x64, CPython 3.12, optional-neuro profile.
6. macOS 15 arm64, CPython 3.12, optional-neuro profile.

These cells test the repository's declared support and the most relevant local
Mac/Linux path without multiplying jobs across every dependency extra or
unqualified architecture. Windows, GPUs, edge runtimes, Python 3.13+, devices,
and independent contributors remain separate future decisions.

## Why This Is On The Scientific Critical Path

A future neural advantage is scientifically useful only if another clean
environment can obtain the same semantic result without private maintainer
state. Cross-machine qualification cannot create that neural effect, but it
can prevent operating-system, package, BLAS, SIMD, thread, path, or serializer
differences from masquerading as a model change.

This loop also protects later work:

- Loop 40 may package only a path that passes its relevant matrix cells.
- Loop 41 cannot call a replay portable when timestamps or state change by
  environment.
- Loop 43 still needs a different team; maintainer-run CI cannot substitute.
- Loop 44 cannot promote a result whose environment and artifact comparison
  are unresolved.

## Primary Sources And Exact Consequences

| Source | Stable finding used here | NeuroDecodeKit consequence |
|---|---|---|
| [ACM Artifact Review and Badging](https://www.acm.org/publications/policies/artifact-review-and-badging-current) | ACM separates same-team repeatability, different-team same-setup reproducibility, and different-team different-setup replication. It permits domain-appropriate tolerances when claims do not change. | Use explicit qualification levels. Maintainer-run multi-OS CI is not independent-team reproduction or scientific replication. |
| [Reproducible Builds definition](https://reproducible-builds.org/docs/definition/) | Bit-identical specified artifacts require the same source, environment, and instructions, with relevant environment attributes declared. | Freeze which bytes are expected exact and record source, dependencies, flags, locale, and build/runtime environment. |
| [Python `PYTHONHASHSEED`](https://docs.python.org/3.12/using/cmdline.html#envvar-PYTHONHASHSEED) | String and byte hashes vary across invocations unless the seed is fixed. | Preserve the current explicit seed and test that semantic artifacts do not depend on accidental unordered traversal. |
| [pip inspect report](https://pip.pypa.io/en/stable/reference/inspect-report/) | The stable version-1 JSON report records environment markers and installed distribution metadata. | Use a sanitized deterministic subset as the package/environment manifest; local paths and hosts stay outside the public core. |
| [PyPA `pylock.toml`](https://packaging.python.org/en/latest/specifications/pylock-toml/) | Python now has a standard lock-file format for reproducible environments. | Treat it as a future option, not a current lock. A version range or `pip freeze` alone is not a cross-platform environment contract. |
| [NumPy global configuration](https://numpy.org/doc/stable/reference/global_state.html) | BLAS thread counts, SIMD dispatch, and import-time configuration can change performance and numerical paths. | Record BLAS/LAPACK, SIMD, thread variables, dtype, shape, and field-specific numerical drift. |
| [PyTorch reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html) | Complete reproducibility is not guaranteed across releases, platforms, or CPU/GPU, even with identical seeds. | Keep model/backend claims platform-bound and fail on semantic behavior changes; never promise universal bitwise tensor identity. |
| [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) | GitHub provides explicit Ubuntu and macOS labels, architectures, memory, storage, and per-run image evidence. | Replace `latest` aliases in future registered cells, record image versions, and cap concurrency and artifacts. |
| [MNE installation check](https://mne.tools/stable/install/check_installation.html) | `mne.sys_info()` reports platform, Python, CPU, memory, NumPy/BLAS, SciPy, and MNE dependencies. | Capture the optional-neuro numerical stack without treating the diagnostic output itself as deterministic or privacy-safe. |
| [Scientific Python SPEC 0](https://scientific-python.org/specs/spec-0000/) | SPEC 0 gives time-based minimum-support guidance, not an exact environment lock or test result. | Use it when revising support policy, but qualify every declared cell with actual evidence. |

## Current Repository Support Audit

No protected payload was opened. The audit read project metadata, workflow
configuration, source/test import names, and installed package metadata only.

| Surface | Current evidence | Honest status |
|---|---|---|
| Python support | `requires-python = ">=3.10"`; classifiers list 3.10, 3.11, and 3.12 | declared, not fully qualified |
| Operating systems | classifier says `OS Independent` | declared, not cross-OS qualified |
| Public CI | base and optional-neuro jobs use `ubuntu-latest`, CPython 3.12 | one OS/Python cell with two profiles |
| macOS | this local arm64 host passes the suite on CPython 3.13.5 | diagnostic observation, not a registered support cell |
| Python 3.10 | two tests import standard-library `tomllib`, introduced in Python 3.11, with no declared fallback | collection gap must be resolved or support refused |
| Dependency identity | optional ranges exist; no `pylock.toml`, requirements lock, Poetry lock, or uv lock is tracked | exact environment unavailable |
| Package identity | editable installs are tested; no wheel/sdist reproducibility job exists | built-package identity unavailable |
| Determinism controls | one-thread variables and `PYTHONHASHSEED=0` are present in CI | useful controls, not a full environment manifest |
| Output contracts | several modules already separate deterministic core artifacts from measured audit fields | reusable design pattern, no cross-cell matrix result |

The Python 3.10 finding is a qualification gap, not proof that the package
itself cannot run there. A future stage must either add an allowed fallback and
run the complete cell or narrow the public support declaration. The result
cannot be guessed from Python 3.12 CI.

The observed local stack is CPython 3.13.5 on Darwin 25.6.0 arm64 with
NeuroDecodeKit 0.1.0, NumPy 2.5.0, SciPy 1.18.0, MNE 1.12.1, and Torch 2.13.0.
This is useful diagnostic context only. Python 3.13 is not one of the declared
classifier cells, and one successful local run is not an OS support claim.

## Qualification Levels

Loop 39 freezes seven levels:

| Level | Evidence | Maximum wording |
|---|---|---|
| `Q0` unavailable | no registered environment or comparison | no reproducibility result |
| `Q1` contract declared | cells, fields, comparisons, resources, and claims frozen | registered interface only |
| `Q2` same process | repeated output under identical state and seeds | same-process repeatable |
| `Q3` clean roots, same host | two clean roots reproduce semantic and numeric gates | same-host repeatable |
| `Q4` separate host, same cell | another host with the same registered cell passes | same-cell computationally reproduced |
| `Q5` supported cross-platform matrix | every required cell passes exact semantics and registered numeric rules | supported-matrix compatible |
| `Q6` independent team | a different team succeeds without private guidance | reserved for Loop 43 |

Scientific replication with independently developed artifacts or new
participant data is beyond this matrix. A `Q5` software result cannot become a
Brain2Qwerty decoding result by wording.

## Environment Manifest Boundary

Every future cell must record at least:

- source commit, dirty state, workflow revision, and job profile;
- explicit runner image label and image version;
- OS, kernel, CPU architecture, and exposed instruction set;
- Python implementation, full version, executable origin, ABI, and platform
  tags;
- installer, requested extras, dependency graph, versions, direct URLs, and
  available distribution hashes;
- NumPy build/runtime BLAS and LAPACK, SIMD baseline and dispatch;
- Torch version, device backend, and determinism flags when present;
- MNE and core dependency report for optional-neuro cells;
- thread, worker, hash seed, locale, timezone, encoding, and filesystem case
  behavior;
- source/build/temp path policy, resource limits, and unavailable fields.

The deterministic public manifest must exclude usernames, hostnames, home
paths, runner tokens, temporary roots, and other Loop 38-sensitive fields.
Those details may exist in a measured local audit but cannot enter the semantic
hash or a public artifact.

## Output Comparison Firewall

Outputs are not one undifferentiated byte blob.

1. **Semantic metadata:** schema, IDs, split membership, configuration,
   provenance, warnings, and claims use canonical JSON and an exact SHA-256.
2. **Time and state:** indices, timestamps, lengths, masks, causal flags,
   context, and transitions are exact.
3. **Discrete arrays:** dtype, shape, and every value are exact.
4. **Floating arrays:** dtype and shape are exact; each named field gets a
   frozen maximum absolute, relative, and where meaningful ULP policy.
5. **Containers:** exact bytes are required only when archive timestamps,
   member order, compression, and metadata are frozen. Otherwise the canonical
   member manifest and payloads are compared exactly.
6. **Human reports:** canonical content is exact; runtime, RSS, host, and temp
   paths remain in a separate measured audit.
7. **Resources:** runtime and RSS are descriptive environment measurements,
   never semantic identity.
8. **Failures:** unsupported cells need an exact reason code and complete
   diagnostics.

Matching rounded CER, accuracy, or latency does not establish artifact
identity. Conversely, a runtime difference does not fail a semantic result
unless it exceeds a separately registered resource cap.

## Numerical Tolerance Firewall

There is no global `allclose` threshold. Every floating output field needs:

- exact schema, dtype, shape, axis meaning, and finite-value policy;
- field-specific maximum absolute and relative error;
- an ULP policy when it is meaningful for that operation and dtype;
- explicit NaN, infinity, signed-zero, and subnormal handling;
- one frozen reference semantic hash;
- a versioned reason for every tolerance value.

Tolerances freeze before any candidate matrix result. Protected data, consumed
caches, targets, labels, model scores, or hidden failures cannot set them. A
future public failure may justify a new contract version and fresh evidence,
but the old result remains failed. Widening a threshold and rerunning the same
evidence until it passes is forbidden.

## Future Stages

Each stage requires its own exact authorization-only commit and green CI.

| Stage | Future work | Maximum claim |
|---|---|---|
| A | dependency-free manifest/canonicalization interface plus new target-free synthetic comparison fixtures | registered same-process and same-host repeatability |
| B | four required base cells | supported base semantic reproduction |
| C | two optional-neuro cells with BLAS/SIMD and numerical diagnostics | supported optional-neuro numerical compatibility |
| D | clean handoff to a different contributor | reserved for Loop 43 independent-team reproduction |

Stage A may not silently add workflow jobs. Stage B may not install the neuro
extra. Stage C cannot reopen real data or run a model. Stage D cannot share
neural recordings or use private maintainer state.

## Failure And Stop Rules

The future run must publish an explicit failure or unsupported record when:

- a runner uses a floating alias or missing image identity;
- source, workflow, dependency, ABI, BLAS, SIMD, thread, or locale identity is
  incomplete;
- a semantic hash, timestamp, split, mask, state, dtype, shape, or discrete
  value differs;
- a floating field has no frozen policy or exceeds it;
- Python 3.10 cannot collect the complete suite;
- one profile is promoted into another;
- diagnostics disappear because matrix fail-fast cancels the other cells;
- runtime, RSS, timeout, disk, or artifact limits fail;
- any protected data, target, model, training, release, stream, device, or
  hardware operation occurs.

One failing required cell blocks the corresponding support claim. It does not
license a quiet exclusion, post-hoc tolerance, `continue-on-error`, or a switch
to a different environment.

## Resource Boundary

The future six-cell matrix is capped at two parallel jobs. Each job uses one
worker and one numerical thread, 20 minutes, 1 GiB peak RSS, and 4 MiB of
uploaded diagnostics. Total uploaded artifacts are capped at 24 MiB, below the
repository's 32 MiB loop cap. No large cache, protected data, model, or training
operation is allowed.

Dependency installation requires a separate execution decision because it
uses network and storage. The planning pass did not install anything, create a
lockfile, build a package, add a workflow job, or upload an artifact.

## Research Access And Resource Record

```text
high-level public web operations:          6
official or primary pages opened:          8
public response bytes/runtime/RSS:         unavailable by tool contract
current generated experiment bytes:        0
new CI jobs or matrix cells:                0
new installs, lockfiles, or builds:         0
protected download/cache/signal reads:      0
target, label, model, or training runs:      0
edge, stream, device, or hardware runs:      0
```

## Closeout

Engineering capability added: a machine-checkable cross-machine
reproducibility taxonomy, environment identity contract, six-cell future
matrix, output comparison firewall, numerical tolerance policy, resource
envelope, and strict claim ceiling now exist.

Scientific claim not established: no fixture, environment manifest, matrix
job, dependency lock, package build, protected payload, model, training run,
target, score, independent reproducer, edge runtime, device, or hardware was
accessed, so there is no cross-machine reproduction, independent replication,
neural advantage, decoding accuracy, unseen-person generalization, real-time
behavior, or portable-hardware result.
