# Loop 25 Authorization Decision v1

Date: 2026-07-13

Status: **Authorized after this record is tested, committed, pushed, and
remotely green; no implementation or runtime exists yet**

Machine decision: `registries/loop25_authorization_decision.v1.json`

Frozen contract: `registries/causal_preprocessing_contract.v1.json`

## Executive Decision

The user authorized Loop 25 and delegated research decision-making authority:

> Authorize Loop 25 implementation exactly as scoped in
> docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md and
> registries/causal_preprocessing_contract.v1.json. I also authorize real or
> consumed data, targets, model inference, training, RW3 Stage A.

They then clarified that this is a broader co-researcher mandate, with the
governing operational constraint being protection of the computer, storage,
and other projects.

The frozen Loop 25 v1 experiment is target-free mechanics. Adding protected
data, targets, models, training, or RW3 after preregistration would destroy its
independence and interpretation. Exercising the delegated authority
conservatively therefore means:

```text
Loop 25 implementation:                 authorized after green CI
target-free fixture generation:         authorized after green CI
registered filter design:               authorized once after green CI
registered numerical preprocessing:     authorized after static gate
seed 2501 development open:             authorized once after static pass
seed 2502 qualification open:           conditional on frozen development pass
registered reports and CLI:             authorized after green CI
real or consumed data:                  not used or authorized in Loop 25
targets, labels, text, predictions:      not used or authorized in Loop 25
model inference or checkpoints:         not used or authorized in Loop 25
training or parameter updates:          not used or authorized in Loop 25
RW3, streams, devices, or hardware:      not used or authorized in Loop 25
Loop 26 or later execution:              separately gated
```

The broader research mandate is preserved for later protocols. It is not
discarded, and it is not allowed to mutate an already frozen experiment.

## Bound Evidence

```text
authorization parent: 6174b37b24a408a6b953538d85d43d3b30d36f26
amendment commit:      b6b92d8ea1cdeadfd6b7cd9f4704aee018516197
contract SHA-256:      ecec99a7cc505ec0256c01c3c1e8aeaa05323ab54a71528323fa6d32bd289141
request SHA-256:       9587a0a19cea36e175020fa6bd43bb7c79e86a814dd88e5437a2f33dd316eb97
```

The v1 contract and authorization request remain immutable snapshots with
false authorization flags. This separate decision is the future execution
authority only after its own pushed CI is green.

## Required Order

1. Test this decision against the immutable request, v1 contract, and v0
   history.
2. Commit and push authorization-only files before implementation.
3. Confirm both remote CI jobs are green.
4. Implement only the six registered source/test files and four CLI commands.
5. Construct and hash the registered coefficients exactly once.
6. Run the complete static pole, response, folding-band, alias-map, impulse,
   and step gate before opening a fixture array.
7. Park with seeds 2501 and 2502 unopened if the static gate fails.
8. Otherwise open seed 2501 once and freeze its complete report.
9. Open seed 2502 once only if every development gate passes.
10. Close without rerun, post-result tuning, or widened scope.

## Resource Boundary

```text
CPU threads / workers:             1 / 1
fixture bytes:                     <= 4 MiB
materialized working arrays:       <= 16 MiB
mutable state:                     <= 4 KiB
single report:                     <= 1 MiB
all generated artifacts:           <= 8 MiB
internal runtime:                  <= 45 sec
peak RSS:                          <= 1 GiB
downloads / real reads:            0 / 0
targets / models / training / RW3: 0 / 0 / 0 / 0
```

## Authorization-Only Measurements

```text
filter coefficients generated:       0
fixture items / bytes generated:      0 / 0
partition arrays opened:              0
numeric preprocessing runs:           0
raw / real-cache / consumed reads:    0 / 0 / 0
target / label / text reads:          0 / 0 / 0
checkpoint / model / training runs:   0 / 0 / 0
network / RW3 / device operations:    0 / 0 / 0
generated runtime payload bytes:      0
end-to-end latency measured:           false
```

## Claim Boundary

**Engineering capability authorized for testing:** one exact target-free,
1,000-to-100 Hz causal preprocessing chain may now proceed through its static,
chunk, resume, timestamp, state, mutation, and resource gates after this
authorization commit is remotely green.

**Scientific or decoding claim not established:** this decision is not a
runtime result and establishes no official Brain2Qwerty equivalence, neural
information, decoding accuracy, CER/WER improvement, unseen-person transfer,
end-to-end latency, useful EEG/MEG, portable hardware, home typing, assistive
efficacy, or clinical utility.
