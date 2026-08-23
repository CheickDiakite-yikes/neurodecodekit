# MARC2-VR37A Exact-Task Surplus Decomposition Implementation

Date: 2026-08-23

Lane: `MARC2-VR37A`

Status: **Generated qualification passed; remote implementation proof pending**

Machine records:

- `registries/marc2_exact_task_surplus_decomposition_implementation.v0.json`
- `registries/marc2_exact_task_surplus_decomposition_result.v0.json`

## Proof Before Implementation

Exact registration `a677e7abd2b89e92bb7bcc3f823a3493c6a32ad0` passed Base
Python job `97226913287`, Optional Neuro Readers job `97226913421`, and CI
`32652807264` before implementation began. The registration contract is 7,450
bytes with SHA-256
`4dd92ec97bcd63837174bc9cd1e7562cc395affae3a618677e22fd44fb3a8c2e`.

## Implemented Surface

The standard-library module
`src/neurodecodekit/datasets/marc2_exact_task_surplus_decomposition.py`
exposes only `plan` and `qualify`. It has no private `execute` or `inspect`
surface, private path constant, generic override, network access, retry, or
scientific route.

Each generated path calls unchanged VR35A exactly once. A VR35A exact-total
control or exact-task-surplus route is then compared with the committed public
38-cell subject/session run-prefix map. The aggregate-only classifier separates:

1. exact public-map control;
2. one-cell next-contiguous-run surplus;
3. one-cell noncontiguous-run surplus;
4. surplus in multiple cells with no deficit;
5. mixed surplus and deficit with positive net total;
6. structural or task-firewall refusal.

The implementation never emits a cell identity, run index, cell delta,
participant, member name, or source path. Every generated source is checked
for byte-exact immutability.

## Measured Qualification

The sole qualification passed all six cases in canonical and reversed order
across two exact replays. All 24 paths matched their frozen route, each of G1
and R1-R5 appeared four times, unchanged VR35A was called exactly 24 times,
all 24 source immutability checks passed, and 87 direct refusals passed.

The run processed 10,606,968 generated input bytes in
2.4954585829982534 seconds at 49,266,688-byte peak RSS. Its canonical report
was 2,980 bytes and retained output was zero. It used one CPU thread, one
worker, and one numerical job. Raw-data reads, real-cache reads, model runs,
training runs, network calls, new payload bytes, private operations, and
operations on other projects were all zero.

Twenty-two focused tests pass. The clean dependency-light suite passes 5,538
tests with 204 expected skips, a 16-test increase over the frozen registration
baseline and zero new failures. The optional-neuro run observed 5,604 tests
with 35 expected skips; its only error was an existing multiprocessing socket
operation blocked by the sandbox, and that exact test passed when rerun with
local process permission. Ruff 0.15.20, formatting, compile, strict registry
JSON parsing, and `git diff --check` pass. Qualification was not repeated.

## Interpretation And Boundary

VR37A proves that the four surplus topologies hidden behind consumed VR36P R3
can be distinguished deterministically on generated fixtures without weakening
VR35A. It does not identify which topology exists in the consumed private
source. The private exact-task total, difference, cell topology, identity, run
set, selection, and cohort remain unavailable.

Another private discriminator would require a new frozen Tier C packet and a
fresh packet-bound maintainer decision after this implementation is committed,
pushed, and both required CI jobs are green. FW2 and CIL1 remain ineligible.

Engineering capability added: generated exact-task eligible-total surpluses can
now be separated into four aggregate topology classes behind the unchanged
task-aware eligibility firewall.

Scientific claim not established: no private source, archive member, neural
signal, target, model, prediction, or score was accessed, so this establishes
no neural effect, decoding performance, language decoding, unseen-person
generalization, or live decoding capability.
