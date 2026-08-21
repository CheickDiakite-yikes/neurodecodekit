# MARC2-VR17A Variable-Width R4 Decomposition Preregistration

Date: 2026-08-21

Lane: `MARC2-VR17A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_variable_width_r4_decomposition_contract.v0.json`

## Why This Lane Exists

The sole VR16P execution called the exact VR16A adapter on the registered
418,755-byte target-free structural source and consumed at
`MARC2VR16P-R4`. R4 preserves three broad possibilities: numeric identity,
exact task token, or companion validation. It does not expose a failed value or
authorize another private read.

Committed evidence may narrow that class without reopening the source. VR15P
previously found only the run-token-width grammar class, VR16A generated-
qualified six numeric widths, and the older producer audit excluded generic
row/path/duplicate failures. This lane tests that composition explicitly rather
than treating it as fact.

## Static Hypotheses

The unchanged VR16A module has ten refusal call sites across
`_canonical_run_token`, `_validate_variable_entry`, and
`_group_variable_rows` for F03-F05. The generated implementation must prove:

1. the nonnumeric-token helper guard is unreachable after the core regex has
   matched `[0-9]+`;
2. the post-normalization `Freewill task differs` guard is unreachable because
   unchanged VR12A rejects the wrong task first;
3. the same six width-only witnesses classified by VR15A as width failures pass
   VR16A with identical semantic selection; and
4. after the committed producer and width evidence is applied, four reachable
   first-failure classes remain.

If any hypothesis fails, park the lane. Do not silently retain the four-class
conclusion.

## Frozen Residual Classes

| Route | Generated class | Exact VR16A branch |
|---|---|---|
| `MARC2VR17A-R1` | exact lowercase Freewill task token | F04 task/core identity |
| `MARC2VR17A-R2` | companion lexical run spelling | F05 mixed spelling inside one semantic bundle |
| `MARC2VR17A-R3` | normalized companion collision | F05 duplicate semantic run/suffix key |
| `MARC2VR17A-R4` | four-companion completeness | F05 missing required companion |

`MARC2VR17A-G1` is the unchanged generated success control. These routes are
generated diagnostic classes, not claims about the consumed private source.

## Frozen Generated Matrix

The implementation may begin only after this exact registration is committed,
pushed, and both required CI jobs are green.

- Equivalence matrix: six VR16A width variants, two source orders, and two
  replays. Each of 24 paths calls unchanged VR15A once and unchanged VR16A once
  and proves width-only classification becomes VR16A success.
- Residual matrix: one control and four mutations, two orders, and two replays.
  Each of 20 paths calls unchanged VR16A once. G1 and R1-R4 must each appear
  exactly four times.
- Total: 24 VR15A calls, 44 VR16A calls, deterministic replay, byte-identical
  source objects, and zero retained output.

Direct tests must also bind all ten static call sites, both compositionally
unreachable guards, exact route/reason pairs, artifact hashes, output privacy,
resources, and every forbidden operation. At least 48 direct refusals are
required.

## Resource Boundary

- one CPU thread, one worker, one numerical job;
- 30 seconds maximum;
- less than 256 MiB peak RSS;
- at most 40 MiB generated input;
- at most 1 MiB aggregate output; and
- zero retained generated output.

No private or ignored path, consumed marker, readiness state, archive, neural
payload, signal, event, target, model, prediction, score, network, provider,
device, hardware, other project, FW2/CIL1, release, or claim operation is
allowed.

Seven focused contract tests and all 4,536 dependency-light tests pass with
204 expected skips and zero failures. Ruff, strict registry JSON, and diff
hygiene also pass.

## Next Gate

After exact generated implementation and result are committed, pushed, and
remotely green, Tier A may prepare one all-false private four-route
discriminator packet. That future read remains Tier C and requires a fresh
packet-bound decision. No current or prior continuation authorizes it.

Engineering capability sought: prove whether committed evidence and unchanged
adapter semantics reduce VR16P R4 to four deterministic, privacy-safe
task/companion classes without another private read.

Scientific claim not established: artifact-only analysis and generated
structural manifests establish no neural effect, decoding accuracy, language
decoding, live decoding, or thought-to-text capability.
