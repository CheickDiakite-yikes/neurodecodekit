# PhysioNet Low-Frequency Cohort Confirmation Authorization Decision

Date: 2026-08-10

Status: **Authorized only after this decision is tested, committed, pushed,
and remotely green; no implementation, dependency operation, EDF request,
local PhysioNet operation, model run, target delivery, or score has occurred**

Machine decision:
`registries/physionet_low_frequency_cohort_confirmation_authorization_decision.v0.json`

Frozen request commit:
`580708fa1f24772a2f9d7cfd572a421b860a1f14`

Frozen packet:
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_AUTHORIZATION_PACKET.md`

## Actual User Decision

The maintainer explicitly declined further boilerplate recital and directed
the currently presented, remotely green WO9R packet to continue:

> i dont want to type out exact auth sentences anymore -- keep going, move the needle, continue, you approved to go on

This record preserves those words exactly. It does not claim the maintainer
typed the packet's long-form sentence. Because the message immediately followed
a response naming the sole active WO9R packet, request commit, green CI run,
and next Tier C gate, this decision incorporates that packet by reference.

The procedural recital requirement is waived for this decision. Every
substantive file, participant, byte, model, target-firewall, resource,
no-retry, no-rerun, and claim boundary remains unchanged.

## Short-Form Packet Rule

The maintainer's instruction also changes the authorization interface going
forward. A short approval may replace a copied authorization paragraph only
when all of these conditions hold:

1. exactly one Tier C authorization packet is the active gate;
2. that packet and its all-false request are already committed, pushed, and
   remotely green;
3. the assistant has just named the packet, commit, CI evidence, and requested
   decision;
4. the maintainer unambiguously says to approve, continue, or proceed;
5. a separate decision quotes the maintainer's actual words and binds the
   immutable packet, request, contract, hashes, and green CI;
6. the decision becomes remotely green before implementation or access; and
7. no permission is inferred beyond the packet.

Ambiguous approval, multiple active packets, missing green evidence, a changed
packet, or any requested scope expansion fails closed. Short form does not
remove separate Tier C decisions. It removes repetitive recital.

## Bound Evidence

```text
authorization parent: 580708fa1f24772a2f9d7cfd572a421b860a1f14
request push CI:       31355270896
Base Python job:       93353672957
Optional Neuro job:   93353672996
contract SHA-256:     ce0dcf5e5ddd598fb69b5baa73f827bbc3f51c4aeab8578d2d2eebda87cd0935
request SHA-256:      e70d1184be40a1e28275e90906f1781094cfd4a0227133a5c8c6a98333551326
packet SHA-256:       397c9f0f72d4f55f9dbb1046bc84549d3c69b0e6b39c36a7a4b944df8ef7750f
user-message SHA-256: 6d3ed4ff57af0f8574feb8d5b8952ee366182db82f215413c72fd3f062169c67
```

The preregistration, contract, packet, request, and their invariant tests remain
immutable snapshots. Their pending fields are not rewritten after approval.
This additive decision records the permission and the narrowed interpretation.

## Ordered Authorization

### Gate 1: this decision must become remotely green

This exact decision must be tested, committed, pushed, and pass Base Python and
Optional Neuro Readers CI. Until then, every implementation and access flag is
closed.

### Gate 2: generated-fixture implementation

After Gate 1, Codex may implement and qualify only the registered acquisition
allowlist, mocked transport, sequential reader, target firewall, causal
low-frequency features, participant-specific LDA, 18 conditions, physiology
assay, prediction freezer, isolated scorer, resource guards, receipts, and CLI
using generated fixtures. No local PhysioNet path may be statted or opened, and
no public EDF URL may be requested.

The existing Git-ignored environment may be reused only if it already contains
the exact registered dependency versions. No installation, resolution,
substitution, or tooling-network operation is authorized. The implementation
must be committed, pushed, and remotely green before acquisition.

### Gate 3: one exact acquisition and target-blind analysis

After Gate 2 is green, one no-retry acquisition may fetch only the 72 registered
S004-S015 EDFs totaling exactly 184,252,032 bytes. It must finish as one
isolated complete bundle or park.

Only after acquisition succeeds may one analysis parse those same EDFs,
target-firewall exactly 720 fit rows and 360 final rows, perform at most 144
participant-specific fits and exactly 216 target-blind inference runs, and
emit the aggregate hash-only freeze. No final target may reach predictive,
selection, threshold, channel, or normalization code.

### Gate 4: one combined score

The combined freeze must be committed, pushed, and remotely green before the
same 180 execution and 180 imagery final targets are delivered together once.
The scorer then applies the frozen H1/H2/H3 gates, mandatory controls, and
`WO9R-R0` through `WO9R-R4` router and stops. No retry, rerun, or post-target
update is permitted.

## Exact Limits

```text
dataset / version:             PhysioNet EEGMMIDB / 1.0.0
subjects / runs:               S004-S015 / 03, 04, 07, 08, 11, 12
named EDF files / bytes:       72 / 184,252,032
fit / jointly final rows:      720 / 360
model family:                  fixed 0.5-4 Hz participant-specific LDA
fits / inference runs:         <=144 / exactly 216 for a valid freeze
acquisition wall / RSS:        900 sec / 268,435,456 bytes
analysis wall / RSS:           1,800 sec / 1,073,741,824 bytes
incremental disk cap:          402,653,184 bytes
minimum free disk:             21,474,836,480 bytes
private / public output:       67,108,864 / 2,097,152 bytes
threads / workers / jobs:      1 / 1 / 1
final deliveries / scores:     1 / 1
retries / reruns / updates:    0 / 0 / 0
```

## Decision-Only Measurements

```text
GitHub CI verification calls:                      1
metadata / EDF network requests:                   0 / 0
local PhysioNet stats / opens / hashes / parses:   0 / 0 / 0 / 0
header / annotation / signal / target reads:       0 / 0 / 0 / 0
dependency installs / implementation operations:   0 / 0
derivatives / fits / inferences / freezes:          0 / 0 / 0 / 0
final target deliveries / scores:                  0 / 0
provider / stream / device / hardware operations:  0 / 0 / 0 / 0
generated experiment artifacts:                   0
end-to-end latency measured:                       false
```

## Claim Boundary

**Engineering capability authorized for testing:** one exact, resource-bounded,
target-firewalled twelve-person confirmation of the WO9 low-frequency lead may
proceed through the ordered green gates.

**Scientific claim not established:** this decision is not an EEG result. Even
a future `WO9R-R4` cannot establish brain-specific origin, independent-team
replication, unseen-person generalization, typing, language or thought
decoding, real-time operation, portable hardware, home use, assistive benefit,
or clinical utility.
