# IACKD Cue-to-Action Reversal Authorization Decision

Date: 2026-08-10

Status: **Authorized only after this decision is tested, committed, pushed,
and remotely green; no implementation, dependency operation, IACKD request,
local IACKD operation, model run, target delivery, or score has occurred**

Machine decision:
`registries/iackd_cue_action_dissociation_authorization_decision.v0.json`

Frozen request commit:
`ef78c061682781d9decd3ecc9dca55e99ea86e5d`

Frozen packet:
`docs/IACKD_CUE_ACTION_DISSOCIATION_AUTHORIZATION_PACKET.md`

## Actual User Decision

After Codex identified the sole IACKD packet, its exact request commit, green
CI run, and requested decision, the maintainer directed:

> keep going, move the needle, continue, you approved to go on

This record preserves those words exactly. It does not claim that the
maintainer typed the packet's full scope. The instruction incorporates the
immutable, remotely green IACKD packet by reference and authorizes only its
registered sequence.

The procedural recital is waived for this decision. Every substantive object,
byte, participant, model, target-firewall, resource, no-retry, no-rerun, and
claim boundary remains unchanged.

## Why The Short Form Is Valid

All fail-closed conditions were satisfied before the instruction:

1. IACKD-1 was the sole active Tier C packet.
2. The packet and all-false request were committed and pushed at `ef78c06`.
3. CI `31401738032` was green for both required jobs.
4. Codex named the packet, commit, CI evidence, exact scope, and next gate.
5. The maintainer then unambiguously said `continue`.
6. This separate decision quotes the actual words and binds every immutable
   scope artifact.
7. No scope expansion is inferred.

The decision is ineffective until its own commit passes both remote CI jobs.

## Bound Evidence

```text
authorization parent: ef78c061682781d9decd3ecc9dca55e99ea86e5d
request push CI:       31401738032
Base Python job:       93498128228
Optional Neuro job:   93498128143
contract SHA-256:     bb2433bb1d2b4a6257a80382764c5392aad0eaa65fa34427f76b52838755f814
request SHA-256:      de5974546665e655cf90ee61e2cc20fe0d6a3d1daa2c47a67973b6ced00fb3d2
packet SHA-256:       575ca42e3960b761af98c14b6571a812d5fdd36d05d1cb8693f8713849ea771c
user-message SHA-256: c97c7d04ef3fb6e70265325d4805026948a1474554de1725374ae47c64a19371
```

The preregistration, contract, packet, request, and invariant tests remain
immutable snapshots. Their pending fields are not rewritten after approval.
This additive record supplies the packet-bound permission.

## Ordered Authorization

### Gate 1: this decision must become remotely green

This exact decision must be tested, committed, pushed, and pass Base Python
and Optional Neuro Readers CI. Until then, implementation and access remain
closed.

### Gate 2: generated-fixture implementation

After Gate 1, Codex may implement and qualify the registered allowlisted
downloader, mocked transport, sequential BrainVision/event/ball/Leap readers,
target firewall, motion guard, fixed low-frequency model and controls,
prediction freezer, isolated scorer, resource guards, receipts, and CLI using
generated fixtures only.

The existing Git-ignored environment may be reused only if it already reports
NumPy 2.5.2, SciPy 1.18.0, MNE 1.12.1, and scikit-learn 1.9.0. No dependency
installation, version substitution, or tooling network is authorized. The
exact implementation must be committed, pushed, and remotely green before any
IACKD metadata or payload operation.

### Gate 3: one exact acquisition and target-blind analysis

After Gate 2 is green, one no-retry invocation may reverify the registered
OpenNeuro metadata and fetch only the 1,340 allowlisted objects totaling
7,249,113,684 bytes into one new isolated bundle. It must validate every
registered identity and either promote one complete bundle or park.

Only after exact acquisition may one no-network analysis parse the 128 runs,
retain all registered EEG/EOG and available geometry, build congruent fit rows
and target-free incongruent rows, complete at most 300 fits and exactly 420
prediction sets, and emit one aggregate hash-only prediction freeze. Final
signed action and visual directions remain sealed from predictive code.

### Gate 4: one combined score

The prediction freeze must be committed, pushed, and green in both CI jobs
before the same final trials receive their actual-hand and visual-target views
together once. The isolated scorer applies H1 through H4 and the ordered
`IACKD-R1`, `R0`, `R2`, `R3`, `R4` router, emits aggregate output, and stops.
No retry, rerun, second delivery, second score, or post-target update is open.

## Exact Limits

```text
dataset / version:             OpenNeuro ds006840 / 1.0.0
participants / model units:    15 / 30 participant-hand units
named objects / bytes:         1,340 / 7,249,113,684
fit / final conditions:        earlier red congruent / held-out yellow incongruent
model family:                  fixed causal 0.5-4 Hz shrinkage LDA
fits / prediction sets:        <=300 / exactly 420
acquisition wall / RSS:        7,200 sec / 536,870,912 bytes
analysis wall / RSS:           3,600 sec / 2,147,483,648 bytes
network / incremental disk:    <=10 GiB / <=9 GiB
minimum free disk:             20 GiB
private / public output:       <=512 MiB / <=2 MiB
threads / workers / jobs:      1 / 1 / 1
final deliveries / scores:     1 / 1
retries / reruns / updates:    0 / 0 / 0
```

## Decision-Only Measurements

```text
GitHub CI verification calls:                   1
OpenNeuro metadata / payload requests:          0 / 0
payload bytes:                                  0
local IACKD stats / opens / hashes / parses:    0 / 0 / 0 / 0
EEG / EOG / marker / trajectory / target reads: 0 / 0 / 0 / 0 / 0
dependency installs / implementation operations: 0 / 0
derivatives / fits / predictions / freezes:      0 / 0 / 0 / 0
final target deliveries / scores:                0 / 0
provider / stream / device / hardware operations: 0 / 0 / 0 / 0
generated experiment artifacts:                 0
end-to-end latency measured:                     false
```

## Claim Boundary

**Engineering capability authorized for testing:** one exact, resource-bounded,
target-firewalled IACKD cue-to-action reversal may proceed through the ordered
remote-green gates.

**Scientific claim not established:** this decision is not an EEG result. Even
a future `IACKD-R4` cannot establish absolute brain-specific origin,
independent-team replication, unseen-person generalization, typing, language
or thought decoding, real-time operation, portable hardware, home use,
assistive benefit, or clinical utility.
