# Classical EEG Adapter Plan Implementation

Status: **implemented and locally qualified; measured symbolic closeout pending
remote-green implementation commit**

Date: 2026-08-08

Frozen contract:
`registries/classical_eeg_adapter_contract.v0.json`

Implementation receipt:
`registries/classical_eeg_adapter_implementation.v0.json`

## Added Capability

`neurodecodekit.models.classical_eeg_adapters` is a standard-library-only
symbolic planning layer. It provides:

- an exact hash-bound registered-contract loader;
- immutable copies of the three registered adapter specifications;
- a deterministic seed-5504 plan with 96 target-free item identities in 48
  pair groups across 48/32/16 train/check/final rows;
- strict item, factor, partition, group, pair, fit-scope, target-firewall,
  causality, dependency-route, access-counter, warning, and claim validation;
- a canonical plan SHA-256 that excludes only its self-referential hash field;
- bounded save, load, and compact summary APIs with collision refusal; and
- deterministic constructors for all twelve registered malformed-plan cases.

The two CLI surfaces are:

```bash
neurodecode make-classical-eeg-adapter-plan --help
neurodecode inspect-classical-eeg-adapter-plan --help
```

Neither command imports NumPy, SciPy, MNE, scikit-learn, or pyRiemann. No
adapter backend, feature extractor, estimator, or scorer exists in this work
order.

## Local Verification

The contract milestone passed 1,255 tests with 3 expected skips. The
implementation adds 10 focused tests and passes:

- all twelve refusal mutations;
- exact canonical replay at
  `66800348e76d03b9b994a460b2e78fbe569c450fdb289be5948cecbcea860bf1`;
- 96 unique items, 48 groups and pairs, and exact 48/32/16 partition counts;
- six train-only or data-independent fit stages;
- zero post-event and right-context samples;
- no winner, fallback, optional import, class value, or protected item field;
- hash, unknown-field, contract-substitution, cap, and collision refusals;
- fresh-process standard-library-only import; and
- CLI create/inspect summary equality.

Thirty-three combined adapter, contract, implementation-receipt, and
prior-receipt checks pass. The complete suite passes 1,273 tests with 3
expected skips and 469 subtests in 35.18 seconds wall time at
612,794,368-byte peak RSS. That RSS belongs to the
whole repository suite, not the future single-plan execution and is not judged
against the 256 MiB plan cap.

A disposable development probe serialized the plan to 27,335 bytes. No plan
file was retained. The exact runtime, peak RSS, and retained-plan hash must be
measured once only after the implementation commit is pushed and remotely
green.

## Execution Order

1. Commit and push this implementation and receipt.
2. Require both CI jobs to pass for that exact commit.
3. Create and inspect one symbolic plan in an automatically removed temporary
   directory using one thread and one worker.
4. Retain only aggregate metrics and hashes, never the generated plan file.

A validation, resource, hash, or CLI failure parks the work order. It does not
permit an import, install, fallback, adapter run, or broader architecture.

## Boundaries

The implementation reads only the committed contract. It reads no array,
signal, raw data, real cache, public EEG, target, label value, participant
identity, or protected path. It performs no feature extraction, parameter
update, model inference, training, scoring, selection, network/provider call,
stream, device, or hardware operation. A future public or protected adapter run
remains Tier C.

Engineering capability added: NeuroDecodeKit can deterministically construct,
hash, save, inspect, and reject leakage in optional classical EEG adapter plans
without importing or fitting an adapter.

Scientific claim not established: this symbolic implementation establishes no
real EEG effect, neural origin, decoding accuracy, generalization, latency,
device performance, home use, or clinical result.
