# Causal Motor Lattice v0 Synthetic Result

Date: 2026-08-09

Status: **one registered Tier B execution consumed; parked at `CML-R0`; no
rerun; synthetic final targets not delivered**

Machine result:
`registries/causal_motor_lattice_synthetic_result.v0.json`

Frozen contract:
`registries/causal_motor_lattice_synthetic_contract.v0.json`

Exact implementation commit:
`90fa467e5acf24a8a47eb8c96b1cb485a6a9076b`

Exact implementation CI: `31295430105`

## Outcome

The one seed-5513 run completed its 600 frozen optimizer steps and source-check
evaluation. Eighteen of 19 check gates passed. The sole failure was the exact
common-mode numerical-invariance gate:

```text
observed maximum key-logit error: 0.0000019073486328125
frozen maximum tolerance:          0.000001
margin above tolerance:            0.0000009073486328125
```

The contract requires every check gate. The run therefore parked at `CML-R0`,
the 16-row synthetic final target delivery did not occur, and no final score
exists. The seed, tolerance, arithmetic, optimizer, checkpoint, and protocol
were not changed. There is no rerun.

## What Worked

The synthetic signal-bearing check rows were recovered perfectly:

| Check metric | Result |
|---|---:|
| signal-bearing rows | `16` |
| hand accuracy | `1.0` |
| key accuracy | `1.0` |
| all-views-muted hand accuracy | `0.5` |
| mirrored spatial-reversal hand accuracy | `1.0` |
| unmirrored spatial-reversal hand accuracy | `0.0` |
| timing-only pair probability difference | `0.0` |
| pure-noise pair probability difference | `0.0` |
| hand/key marginal maximum error | `5.960464477539063e-08` |
| future-tail causal maximum error | `0.0` |
| checkpoint replay hash match | `true` |

Each isolated branch behaved as registered. Muting potential increased its
factor hand NLL by `0.893311`; muting mu increased its factor hand NLL by
`0.340825`; and muting beta increased its factor hand NLL by `1.172072`. On the
mixed factor, all-views-muted hand NLL was `0.743368` versus `0.000170` for the
full checkpoint.

These are useful implementation diagnostics. They show that the exact compact
model can learn the deliberately constructed factors, that the physical
lattice can express their synthetic key classes, and that branch ablations can
route those factors. They do not show that corresponding information exists in
real EEG.

## What Failed And What It Means

The spatial mixer transforms each learned row to zero mean and unit L2 norm.
That makes a uniform common-mode value mathematically invisible. In float32,
the complete learned forward path produced a maximum residual key-logit change
of `1.9073486e-6`, narrowly outside the preregistered `1e-6` tolerance.

This is an exact numerical-invariant failure, not a real-data decoder failure.
It also cannot be waived after seeing the value. A future repair would need a
new contract and separate permission to evaluate again; it may not silently
relax the tolerance or reuse seed 5513.

Two descriptive controls remain important:

- the gradient-ineligible peripheral-proxy-only condition reached hand
  accuracy `1.0`, showing that this architecture can respond strongly to a
  deliberately constructed peripheral pattern; and
- the nonwrapping 16-sample time displacement retained hand accuracy `1.0` on
  the strong synthetic factors, so that mutation is not a sufficient negative
  control for this fixture by itself.

Neither observation proves a real peripheral shortcut or timing robustness.
They sharpen the future control design.

## Execution And Resource Ledger

```text
synthetic fixture generations:      1
synthetic source bytes generated:   1,145,152
parameter-update runs / steps:      1 / 600
model inference stages:             2
prediction sets:                    10
check / final scoring events:       1 / 0
checkpoint reloads:                 1
runtime:                            6.5530732499901205 seconds
peak RSS:                           398,737,408 bytes
free disk before:                   43,543,154,688 bytes
checkpoint / report bytes:          22,952 / 14,419
total generated output:             37,371 bytes
CPU threads / workers:              1 / 1
end-to-end latency measured:        false
```

Every resource gate passed. The checkpoint prediction replayed byte-identically
with SHA-256
`5767de92fa31b3e454f191346113a89cc7ca882516a5904460bfd2962bcfe7ea`.

The generated checkpoint and report are not committed. Their closeout
bindings are:

```text
checkpoint.npz  22,952 bytes  12b34f438c03629813cd6641815af33871e4b50d74188a45f145a27a18c10537
report.json     14,419 bytes  e4cd6d246e1a91975001d1a587488e3e87516c41082164286b8bac95699b582b
```

## Access Boundary

Real/public data reads, protected target or label reads, S20 path stats or
reads, PhysioNet downloads or reads, network and provider calls, pretrained
weights and external embeddings, stream/device/hardware operations, releases,
and scientific claim upgrades were all exactly zero.

**Engineering capability added:** the consumed run demonstrated that the exact
4,535-parameter CML-v0 implementation can learn and localize constructed
potential, mu, beta, mixed, spatial-reversal, timing, peripheral, and noise
behaviors while enforcing check-before-final isolation and deterministic
checkpoint replay.

**Scientific claim not established:** no real EEG or protected evidence was
accessed and the synthetic gate parked, so there is no EEG information, neural
advantage, decoding accuracy, brain-specific origin, generalization, real-time
or portable-hardware result, home-use result, assistive result, or clinical
utility.
