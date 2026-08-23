# MARC2-VR28P inventory/taxonomy private discriminator proof closeout

Date: 2026-08-23  
Lane: `MARC2-VR28P`  
Status: proof-only closeout recorded; delayed effect until this exact commit is remotely green

## Remote implementation proof

Exact hardened Stage 1 implementation
`6d3b770d0e67c8b394c6a1a7581c21ae7b202909` passed CI `32616632414`, Base
Python job `97138335047`, and Optional Neuro Readers job `97138335116`.
Both required jobs are green. The wrapper module and its one measured
qualification are unchanged from the first Stage 1 commit.

The closeout binds these immutable preproof snapshots from that commit:

| Artifact | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| Implementation registry | 7,743 | `418b8b09e42ff5e8d12b3c07275afd5ea2160f52788b816c32accb6e94c25fcd` | `ac951c78eff270f921f21539dd6a25348fb97b18` |
| Result registry | 3,580 | `87daeedaa49d6c6a1f8c86e902fc87ef9db15bef889de18d9964cbbd434e608b` | `1456c16d0250f7ee87bfdcaab3cdfeded0b4ee12` |

The canonical implementation-artifact set hash is
`938203de733101dd31070d12453c06059401631407031d11d5092acf0fdfb675`.
The closeout also binds exact Git blobs for the module, behavior tests,
implementation tests, result tests, and implementation document.

## No repeated operation

This closeout does not repeat the registered generated qualification. It does
not run readiness, construct or inspect a `.codex_work` path, read the private
structural source, inspect a consumed lane, create a cohort, or access an
archive member, neural signal, event, channel, geometry, target, model,
prediction, or score. Every such operation counter remains zero.

## Delayed effect

This record is ineffective until its own exact commit is pushed and both CI
jobs are green. Before that remote proof, `execute` remains closed and no
readiness or private path may be touched.

After this exact closeout is remotely green, the existing packet-bound
decision authorizes one registered invocation only: three fresh passing
readiness samples, a consumed marker before the source content open, one exact
418,755-byte target-free structural read, one VR25A call, one VR27A map call,
and one aggregate R1/R2 result or safe failure. There is no retry or rerun.

Engineering capability added: the exact generated-qualified fixed-path
wrapper is now cryptographically bound to its remote CI proof and ready for a
separate proof activation barrier.

Scientific claim not established: this proof-only closeout accessed no private
source or neural payload and established no neural effect, decoding accuracy,
language decoding, unseen-person generalization, or live decoding result.
