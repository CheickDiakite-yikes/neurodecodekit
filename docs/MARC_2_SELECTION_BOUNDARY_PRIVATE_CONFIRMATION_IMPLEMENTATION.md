# MARC2-VR26P Selection-Boundary Private Confirmation Implementation

Date: 2026-08-22

Lane: `MARC2-VR26P`

Status: **Generated Stage 1 qualified; private Stage 2 unavailable until the
exact implementation and a separate proof-only closeout are remotely green**

Module:
`src/neurodecodekit/datasets/marc2_selection_boundary_private_confirmation.py`

Machine record:
`registries/marc2_selection_boundary_private_confirmation_implementation.v0.json`

## Green Authorization Boundary

Packet-bound decision `8b9ce248f6cbce1205addf113f97325a98c1992e`
passed Base Python job `97116976065`, Optional Neuro Readers job
`97116976016`, and CI `32608318342` before implementation began. The wrapper
binds that decision, the unchanged request, and the exact VR25A module,
contract, implementation registry, and result registry by SHA-256.

The implementation neither imports nor calls the consumed VR22P or VR24P
executors. Its public interface has only fixed `plan`, `qualify`, `inspect`,
and proof-gated `execute` commands. There is no source, output, URL, threshold,
route, retry, resume, fallback, substitution, or resource override.

## Fixed State Machine

The wrapper preserves the registered order:

1. verify the decision and fixed tracked artifacts;
2. require all five numerical thread variables to equal `1`;
3. require three passing readiness samples and write one mode-`0600`
   certificate;
4. require a fresh fixed output root and safe parent chains;
5. no-follow preflight only the fixed source identity;
6. write one mode-`0600` consumed marker before content open;
7. read, hash, and strict-parse the source once;
8. call exact VR25A once without source mutation;
9. write a mode-`0600` source-exact cohort manifest only on success; and
10. write one mode-`0644` aggregate-safe report.

The private executor refuses at `MARC2VR26P-F01` before readiness or any
private-path operation while `remote_implementation_proof` is null. The
generated qualification uses invocation-created temporary roots only and
retains none of them.

## Generated Qualification

The single recorded `MARC2VR26P-G1` qualification replayed all ten frozen
VR25A cases in canonical and reversed order twice:

| Measure | Result |
|---|---:|
| cases / orders / replays | `10 / 2 / 2` |
| total paths | `40` |
| accepted / refused paths | `20 / 20` |
| exact VR25A calls | `40` |
| generated source opens | `40` |
| compatibility true / false accepted paths | `4 / 16` |
| route counts | `G1=20`, `R4=4`, `R5=16` |
| direct refusal checks | `106` |
| selected subjects | `16` |
| selected run bundles | `96` |
| selected core members | `384` |
| generated input bytes | `17,672,740` |
| cumulative temporary writes | `4,526,083` bytes |
| peak incremental output | `223,419` bytes |
| retained generated output | `0` bytes |
| aggregate qualification report | `6,303` bytes |
| runtime | `2.444166875036899` seconds |
| peak RSS | `34,701,312` bytes |
| CPU threads / workers / numerical jobs | `1 / 1 / 1` |

All accepted paths shared semantic cohort SHA-256
`254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba`
and source-exact selected-name SHA-256
`496a960435928ab09d2c479d4576d1e9c2a4af244c0e1575bd37f5997046432e`.
Every replayed generated source hash matched exactly. The aggregate report
exposes only the compatibility boolean, never a complete-bundle count,
difference, or direction.

The 4,526,083-byte cumulative write count is the sum across 40 isolated roots
that were deleted sequentially. Peak incremental output was 223,419 bytes,
well below the 2 MiB per-invocation output cap, and retained output was zero.

## Route Ceiling

`R1` and `R2` are the only future cohort-freeze routes. Both require the same
16-subject, 96-bundle, 384-member source-exact cohort; they differ only in the
public compatibility boolean. `R3` through `R7` consume the invocation without
a cohort and expose only readiness/path, source integrity, eligibility,
selection, or privacy/resource classes.

No public report may contain a member name, source path, participant, session,
run, companion, row, predicate, reason, exception, label, target, prediction,
probability, score, observed complete-bundle count, count difference, or count
direction.

## Verification And Next Gate

Behavior tests cover standard-library-only import, the 40-path matrix,
deterministic replay, all envelope mutations, strict JSON, file modes, source
identity, aggregate-only failure, null-proof refusal before readiness, exact
artifact proof, resource caps, public-field rejection, and CLI shape.

The implementation registry deliberately leaves `remote_implementation_proof`
null. Commit, push, and require both CI jobs green for these exact bytes. Then
add a proof-only closeout that repeats no qualification and performs zero
private operation. Only after that closeout is separately remotely green may
the single registered target-free private confirmation execute.

Engineering capability added: a fixed-path, proof-gated wrapper can apply the
strict VR25A selection firewall and prepare one exact source-bound cohort
manifest without opening neural payloads.

Scientific claim not established: this generated qualification accessed no
real or private source and establishes no neural effect, decoding accuracy,
language or thought decoding, unseen-person generalization, live decoding, or
portable-hardware result.
