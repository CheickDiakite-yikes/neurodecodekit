# FMSR1 Live Witness Implementation Correction Decision

Date: 2026-08-31  
Decision: `FMSR1-R1-W-I1-D0`  
Packet: `FMSR1-R1-W-v0`

## Decision

The maintainer's exact words were:

> get needle moving, eureka results

Those words followed an explicit identification of the named packet, the
green generated implementation at
`ea37358d8f34efd70f4e95c2a8452aa727f1b2bd`, CI run `33361847146`, and the
fact that the implementation could not execute the packet's live witness.
They therefore authorize the packet's still-missing, reversible first stage:
one additive standard-library live executor, its generated-fixture
qualification, tests, documentation, commit, push, and both required CI jobs.

They do **not** authorize the live witness. The exact live implementation,
artifact hashes, and CI proof did not exist when the words were given, so the
words cannot serve as the packet's required second, execution-bound decision.
No GitHub API or official source index may be contacted under this decision.

## Implementation Boundary

The additive implementation may contain only the capabilities needed to make
the already-frozen witness executable after a later decision:

- strict loading of a future tracked execution decision from clean local
  `main`;
- no-follow path admission, a `0700` attempt root, and a durable `0600`
  consumed marker before any contact;
- exact direct-TLS HTTP transport, the three-request `CI-W0` proof, bounded
  17-root pagination-only traversal, and opaque body byte count/hash records;
- runtime, RSS, disk, request, byte, redirect, output, environment, and
  one-thread enforcement;
- deterministic generated transport fixtures, adversarial refusals, exact
  output accounting, and a CLI with no path, URL, token, retry, or model
  override.

The implementation may not parse, rank, or select a candidate; access a
payload, header, EEG, EOG, EMG, event, target, or label; run a model or score;
contact a provider; touch another project; delete existing work; publish a
release; or upgrade a scientific claim.

## Ordered Barrier

1. Commit this decision without the live implementation.
2. Push it and require both GitHub CI jobs to pass.
3. Commit the exact live implementation and one generated-only qualification.
4. Push it and require both GitHub CI jobs to pass.
5. Stop and obtain fresh maintainer words that explicitly follow the known
   live implementation commit and CI proof.
6. Record and green the separate execution decision before one network byte.

This correction repairs an implementation-ordering defect. It is engineering
progress, not source evidence and not a neural result.

