# Causal Motor Lattice v0 Synthetic Preregistration

Date: 2026-08-09

Status: **Tier B synthetic contract frozen; implementation and execution not
started**

Machine contract:
`registries/causal_motor_lattice_synthetic_contract.v0.json`

Work order: `13` in
`docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md`

## Question

Can the proposed Causal Motor Lattice v0 (`CML-v0`) be implemented exactly as
a 4,535-parameter, 64-channel, strictly causal model and recover deliberately
constructed potential, mu, beta, and mixed synthetic factors without learning
from timing-only or pure-noise controls?

This is an architecture-mechanics test. It is not an EEG experiment, a model
selection result, or a scientific endpoint.

## Frozen Source And Split

The only input is a fresh in-memory replay of the already qualified synthetic
motor fixture bound by the machine contract. Its seed remains `5503`, with 96
items and paired `48/32/16` train/check/final partitions. No retained fixture
payload, real channel, public EEG, S20 path, target text, pretrained weight, or
external embedding may be read.

The CML experiment seed is `5513`. Only the 24 source-train rows from the first
four deliberately signal-bearing factor families may update parameters:

1. potential-shape signal;
2. mu-energy signal;
3. beta-energy signal; and
4. mixed potential/mu/beta signal.

The spatial-reversal, timing-only, peripheral-like, and pure-noise families are
diagnostics and never contribute an optimizer gradient. Check targets are used
once for a synthetic development gate. Synthetic final targets remain
undelivered to the scorer unless every check gate passes. A failed check parks
the run without final scoring, tuning, or rerun. This synthetic final partition
does not consume or stand in for a future scientific test.

## Pair-Anchored Causal Adapter

The source timing-only pair deliberately has different true lengths. Allowing
the model to crop each member independently would turn length into a hidden
class cue. The adapter therefore uses the same source interval for both members
of every pair:

```text
pair anchor = minimum true length across the pair
crop         = [pair anchor - 96, pair anchor)
left context = first 32 crop samples
analysis     = final 64 crop samples
```

All 96 samples are strictly pre-event. The model receives only projected,
train-normalized signal and a valid mask. It never receives true length,
timestamp, pair, factor, partition, class, or event-position metadata as an
input. Factor identity is allowed only inside the synthetic-only training
ledger to select the frozen matched-view auxiliary loss and inside aggregate
diagnostics.

The eight synthetic source channels are expanded to 64 generic channels by the
target-free formula and SHA-256 in the machine contract. The output channels
are named `CML_SYN00` through `CML_SYN63`; they have no anatomical identity or
geometry. The fixed projection has rank eight and no trainable parameter.

## Frozen Causal Views

All numerical work is CPU float32 with one thread and deterministic algorithms.
Train-only channel location is the median of the 24 eligible training crops;
scale is `max((Q75 - Q25) / 1.349, 1e-4)`. These statistics are fitted without
labels after the 8-to-64 projection and then frozen.

- `V0 potential`: three means over the final 64 normalized samples.
- `V1 mu`: one-sided 33-tap `8-13 Hz` FIR, then energy and `log1p`.
- `V2 beta`: one-sided 33-tap `13-30 Hz` FIR, then energy and `log1p`.

The FIR coefficients, little-endian hashes, response gates, 16-sample nominal
group delay, 32-sample left context, and three temporal cells (`[0,21)`,
`[21,42)`, `[42,64)`) are frozen in the registry. There is no downsampling, so
an anti-alias response is not applicable. Centered filtering, zero-phase
filtering, reflected future padding, circular padding, and post-event samples
are forbidden.

Each view has one learned rank-8 spatial mixer. Every raw spatial row is
mean-centered and unit-L2-normalized before use. Fixed filters, the source
projection, masks, incidence map, temporal cells, row normalization, residual
gain, and exact hand marginal have zero trainable parameters.

## Exact Model And Lattice

The trainable ledger is fixed:

| Component | Parameters |
|---|---:|
| three `64 -> 8` spatial mixers with bias | `1,560` |
| `72 -> 24` bottleneck with bias | `1,752` |
| 24-feature layer normalization | `48` |
| `24 -> 18` primitive head with bias | `450` |
| `24 -> 29` bounded residual head with bias | `725` |
| **Total** | **`4,535`** |

The fixed synthetic lattice has 29 keys and 18 primitives: two hands, four
rows, four zones, seven columns, and one special primitive. Keys `0-13` form
the left marginal, keys `14-27` form the right marginal, and key `28` is
hand-ambiguous. The hand prediction is the exact renormalized probability mass
over the two eligible key sets. There is no independent hand head. The direct
key residual is bounded as `0.25 * tanh(z)`.

Only eight hand-key combinations are active in signal-bearing training. Their
map, every diagnostic map, the primitive incidence formula, and its byte hash
are frozen before implementation. These are synthetic design classes, not
participant labels or text.

## Frozen Training Recipe

Exactly one parameter-update run is allowed:

- CPU float32, deterministic algorithms, seed `5513`;
- full-batch AdamW over the 24 eligible rows;
- exactly 600 optimizer steps, no early stopping or checkpoint selection;
- learning rate `0.01`, betas `0.9/0.999`, epsilon `1e-8`, weight decay
  `1e-4`, and global gradient-norm cap `5.0`;
- key cross-entropy weight `1.0`;
- exact hand-marginal negative-log-likelihood weight `0.5`;
- primitive multi-label BCE weight `0.25`; and
- an additional weight `0.5` for the matching isolated view on potential,
  mu, and beta training rows.

The matched-view term is a synthetic mechanics control: nonmatching views are
replaced by the registered zero-view neutral. It cannot be carried into a real
protocol by implication. Spatial-reversal, timing, peripheral, and noise rows
remain gradient-ineligible.

Nonfinite loss, parameter drift, cap drift, or a mismatched source hash parks
the run immediately.

## Check-Then-Final Gates

The single checkpoint must pass all of the following on the source-check
partition before final target delivery:

1. exact 4,535-parameter count and exact lattice, FIR, projection, mask, and
   source bindings;
2. at least `0.875` hand accuracy and `0.75` key accuracy across the 16
   signal-bearing check rows;
3. all-views-muted hand accuracy at most `0.625`, with full accuracy at least
   `0.25` higher;
4. for potential, mu, and beta rows, muting the matching view increases hand
   NLL by at least `0.02` versus full and is no smaller than either nonmatching
   single-view ablation;
5. on mixed rows, all-views-muted hand NLL exceeds full hand NLL by at least
   `0.10`;
6. mirrored spatial-reversal hand accuracy is at least `0.75` and at least
   `0.25` above its unmirrored value;
7. timing-only and pure-noise pair members produce hand probabilities within
   `1e-7` of each other;
8. the exact hand marginal and the marginal recomputed from key probabilities
   differ by at most `1e-7`;
9. common-mode and future-tail causal mutations change the relevant logits by
   at most `1e-6`; and
10. every resource, padding, output, warning, unavailable-field, provenance,
    counter, and forbidden-content gate passes.

If check passes, the same frozen checkpoint is scored once on synthetic final.
It must reach at least `0.875` hand accuracy and `0.75` key accuracy over the
eight signal-bearing final rows, preserve timing/noise pair equality and exact
hand-key consistency, and classify both mirrored spatial-reversal rows
correctly. No final outcome can select a seed, threshold, optimizer, mask,
architecture, or rerun.

The same checkpoint also emits the registered full, branch-muted,
all-views-muted, channel-deranged, time-displaced, hemisphere-mirrored, and
peripheral-proxy-only aggregate diagnostics. Branch ablations do not prove
that a feature is cortical potential, mu, or beta.

## Replay And Output

Deterministic replay means loading the one frozen checkpoint once and
recomputing the full check and conditional full final prediction hashes. It
does not mean retraining. The hashes must match byte-for-byte.

One invocation may create at most one numeric checkpoint NPZ and one aggregate
JSON report, together under 4 MiB. Neither file may contain per-item targets,
text, identities, or predictions. The measured closeout may commit only
aggregate hashes and metrics; invocation files are removed after validation.

Hard caps are one CPU thread, one worker, 600 seconds, 512 MiB peak RSS, 4 MiB
generated output, and at least 20 GiB free disk before execution. No dependency
is added to the base install. NumPy, SciPy, and PyTorch remain lazy optional
dependencies already present in the local research environment.

## Authorization And Stop Boundary

The approved Research Autonomy Charter permits this fully frozen, reversible
Tier B synthetic experiment only after:

1. this contract is tested, committed, pushed, and remotely green;
2. the exact implementation is separately tested, committed, pushed, and
   remotely green; and
3. the worktree and resource preflight pass.

No real or public EEG, S20, PhysioNet, target text, participant identity,
download, pretrained model, language model, external embedding, hardware,
stream, release, or scientific claim is authorized. A failed or capped run is
retained as the result and receives no rerun under this contract.

## Claim Boundary

**Engineering capability if all gates pass:** NeuroDecodeKit can instantiate
and deterministically replay the exact 4,535-parameter CML-v0 interface, route
constructed potential, mu, beta, spatial, timing, peripheral, and noise
failures, and enforce causal and hand-key consistency controls.

**Scientific claim not established even if all gates pass:** synthetic factors
establish no real EEG information, neural or brain-specific origin, decoding
accuracy, neural advantage, unseen-person generalization, real-time behavior,
portable or earbud sensing, home use, assistive value, or clinical utility.
