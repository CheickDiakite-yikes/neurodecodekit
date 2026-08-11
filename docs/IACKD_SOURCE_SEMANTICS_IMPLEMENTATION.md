# IACKD Source Semantics Generated-Fixture Implementation

Date: 2026-08-10

Status: **implementation qualified on generated fixtures; measured closeout
held until this exact implementation is remotely green**

Lane: **IACKD-H3 Source Semantics Policy**

Registry: `registries/iackd_source_semantics_implementation.v0.json`

## Green Research Gate

Research commit `ed5ce8292c2c1dc842898023cfe8cb608e9d4476` passed Base
Python job `93639606343` and Optional Neuro Readers job `93639606403` in CI
`31445790741` before implementation began. The bound candidate policy is
`IACKD-SourceSemanticsPolicy` v0.1.0 with canonical SHA-256
`1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4`.

The implementation reads only that committed policy registry. It performs no
network request, Git-ignored read, local IACKD path operation, source-body
read, signal or event operation, target read, model run, or score.

## Implemented Interface

`src/neurodecodekit/preprocess/iackd_source_semantics.py` provides:

- strict loading and canonical hash verification of the green H3 policy;
- explicit BIDS-version-to-MISC-count-field binding for 1.7.0 and 1.11.1,
  while refusing to apply 1.11.1 to the dataset-pinned 1.7.0 fixture;
- deterministic target-free 29-row and 31-row generated metadata fixtures;
- exact source-count reconciliation before functional-role assignment;
- separate source type, functional role, and model-inclusion projections;
- one fixed 26-channel predictive output order in both fixture families;
- optional finite M1/M2 geometry without predictive inclusion;
- unavailable geometry for HEOG, VEOG, and Trigger controls;
- hashes for source order, source counts, functional roles, model mask, and
  geometry-availability mask;
- a recursive forbidden-target-field firewall;
- exclusive bounded report writing, strict loading, validation, and compact
  summary APIs; and
- a dry-run-first module CLI with only plan, `--fixture`, and `--inspect`
  surfaces. There is no real-data or `--execute` mode.

## Adversarial Qualification

Thirteen generated mutations exercise twelve distinct refusal classes:

1. dataset BIDS-version drift;
2. newer MISC count-field spelling under the pinned older version;
3. malformed fixture schema;
4. source-index or order drift;
5. duplicate channel identity;
6. source-type drift;
7. sidecar count drift;
8. reference drift;
9. required geometry loss;
10. derivative-binding hash drift;
11. target-field leakage;
12. functional-role overlap; and
13. predictive model-mask drift.

Additional tests cover unknown and missing channels, sampling drift, nonfinite
geometry, normalized-name matching with preserved display spelling, output
collisions, small output caps, malformed reports, forbidden counters, a newly
imported heavy module, byte-identical replay under fixed monitors, and the
module CLI roundtrip.

## Resource And Output Contract

- one CPU thread, one worker, and one numerical job;
- at most 30 seconds wall time;
- at most 268,435,456 bytes peak RSS;
- at most 2,097,152 generated output bytes;
- zero dependency installation;
- zero network bytes;
- zero real or public metadata bodies; and
- zero local IACKD bundle operations.

The report contains aggregate fixture summaries and binding hashes, not raw
fixture channel rows or generated coordinates. It reports input/output bytes,
runtime, peak RSS, fixture and row counts, semantic passes, mutation attempts,
distinct refusals, causality as not applicable, end-to-end latency as not
measured, warnings, unavailable fields, and every access counter.

## Next Gate

Run complete verification, commit and push this exact implementation, and
require both remote CI jobs green. Only then run one measured generated-fixture
closeout under the registered caps. That closeout may write one temporary
report for inspection and hash capture; it cannot add a real reader, access a
public body or local bundle, or enter IACKD-2.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now has a deterministic,
version-aware policy validator that preserves source BIDS counts before
assigning functional roles and model inclusion, with strict derivative hashes
and fail-closed synthetic qualification.

Scientific claim not established: no real or public IACKD body, local bundle,
signal, event, trajectory, target, model, prediction, or score was accessed,
so this implementation establishes no neural effect, action decoding,
brain-specific origin, generalization, typing, language or thought decoding,
real-time operation, hardware capability, assistive benefit, or clinical use.
