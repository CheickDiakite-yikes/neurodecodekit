# MARC2-VR37A Exact-Task Surplus Decomposition Preregistration

Date: 2026-08-23

Lane: `MARC2-VR37A`

Status: **Frozen generated-only registration; implementation blocked until
this exact registration is pushed and both required CI jobs are green**

Machine contract:

- `registries/marc2_exact_task_surplus_decomposition_contract.v0.json`

## Why This Is Next

Consumed VR36P R3 maps only to VR35A R1: exact-task projected eligible total
above 195. It excludes mixed-task contamination as the sole explanation, but
VR35A checks that global total before it checks the public subject/session
count map. R3 therefore does not reveal the topology of the surplus.

Artifact-only review identifies four generated topology classes compatible
with a net surplus:

1. one cell with the next contiguous run;
2. one cell with a noncontiguous extra run;
3. multiple cells above the public map with none below;
4. cells both above and below the public map with a positive net difference.

These are generated diagnostic mechanisms, not claims about the consumed
private source.

## Frozen Matrix

The implementation must run six cases across canonical/reversed order and two
exact replays for 24 paths. Baseline G1 and R1-R5 must each appear four times.
VR35A is called exactly 24 times, at least 60 direct refusals pass, every source
remains unchanged, replay is exact, and retained output is zero.

The future standard-library module may expose only `plan` and `qualify`. It has
no private executor, private path constant, generic override, network access,
heavy dependency, retry, or scientific route.

## Resource And Evidence Boundary

The qualification is limited to one CPU thread, worker, and numerical job;
30 seconds; less than 256 MiB peak RSS; less than 1 MiB generated output; and
zero network or new payload bytes.

No `.codex_work` path, private or consumed source, archive member, neural
signal, target, model, prediction, score, FW2/CIL1 surface, device, or other
project may be touched. A future private discriminator would require its own
frozen Tier C packet and decision.

Engineering capability proposed: a deterministic generated-only discriminator
that separates four exact-task-surplus topology classes hidden by VR36P R3.

Scientific claim not established: this registration accesses no private or
neural data and establishes no neural effect, decoding performance, language
decoding, unseen-person generalization, or live decoding result.
