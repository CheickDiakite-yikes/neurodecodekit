# Classical EEG Adapter Preregistration

Status: **Tier B contract frozen; implementation and execution not started**

Date: 2026-08-08

Machine contract:
`registries/classical_eeg_adapter_contract.v0.json`

## Question

Can NeuroDecodeKit define optional classical EEG baselines in a way that makes
group leakage, evaluation-time fitting, target-bearing features, noncausal
context, and silent dependency substitution impossible before a package is
installed or a model is fit?

This work order defines plans and refusals only. It does not extract a feature,
fit a baseline, infer a class, select a family, or score an outcome.

## Frozen Adapter Families

Three complementary families are registered without choosing a winner:

1. `fixed_low_frequency_shrinkage_lda` uses four fixed pre-event time-bin means
   and one slope per channel, train-only standardization, train-only class
   means and pooled covariance, and fixed `0.1` trace shrinkage. Its feature
   dimension is `5C`.
2. `fixed_8_to_30_hz_csp_lda` consumes only a future registered causal
   8–30 Hz view, fixes four CSP components and `0.1` regularization, and binds
   CSP, scaling, LDA, and class priors to train groups.
3. `regularized_riemannian_mdm` consumes that same future causal motor-band
   view, uses per-item covariance with fixed `0.1` trace regularization and the
   Riemannian metric, and fits class centroids only on train groups.

The strategy intentionally does not choose CSP or Riemannian now. Only a
separately authorized public positive control may make that bounded choice.
Synthetic fixture behavior, S20 outcomes, and a final partition may not select
the family. A train-only no-signal prior remains mandatory in every future
comparison.

## Measured Dependency Route

The committed zero-network tooling audit is the only availability source for
this contract:

- NumPy `2.5.0` and SciPy `1.18.0` make the low-frequency specification's
  substrate available, but no adapter is implemented or fitted;
- MNE `1.12.1` is installed, but its CSP capability is incomplete because
  scikit-learn is absent; and
- pyRiemann and scikit-learn are absent.

No import is retried, no package is installed, and no adapter silently falls
back to another family. Future missing-dependency errors must name the exact
optional extra. The future implementation module must remain standard-library
only until a separately gated adapter execution imports an optional backend
inside a function.

## Group And Fit Firewall

Every future plan requires explicit item, group, pair when available,
partition, channel, sampling-rate, length, mask, and strictly pre-event
timestamp identities. Groups and pairs may never cross train, check, and final
partitions. Row-level random splitting and reassignment after labels or outcomes
are visible are forbidden.

Six stages are train-only or data-independent by construction:

- causal preprocessing state;
- channel quality or channel selection;
- feature standardization;
- spatial or covariance transform;
- classifier or class centroid; and
- class prior.

Check targets cannot enter a fit or transform. Final targets remain unavailable
until a future prediction freeze. Evaluation batch statistics, test-time
adaptation, post-evaluation updates, target-derived channel selection, event
position features, semantic markers, language models, and post-event samples
are forbidden.

## Synthetic Plan Fixture

Implementation may construct only a deterministic plan from the work-order-3
identity formula, without reading its deleted NPZ or sidecar. Seed `5504`
describes 96 symbolic items in 48 paired groups across eight factor families:
48 train items/24 groups, 32 check items/16 groups, and 16 final items/8 groups.
No actual target or label value is created or read.

The validator must reject all twelve registered mutations:

1. group crossing;
2. pair crossing;
3. duplicate item identity;
4. missing group identity;
5. row-level random split declaration;
6. check or final target access;
7. evaluation-time fit or update;
8. global or evaluation normalization;
9. post-event or right context;
10. forbidden target or identity fields;
11. unknown adapter; and
12. silent dependency fallback or substitution.

## Resource And Evidence Boundary

- One CPU thread and one worker.
- At most 15 seconds and 256 MiB peak RSS.
- At most one 1 MiB symbolic plan file.
- No optional import or install.
- No array payload, raw data, real cache, public EEG, target/label value,
  feature extraction, parameter update, model inference, scoring, selection,
  network, provider, stream, device, or hardware operation.

Implementation may proceed under the active Research Autonomy Charter only
after this contract is committed, pushed, and remotely green. A future public
or protected adapter execution remains Tier C and needs its own exact decision.

Engineering capability if all gates pass: NeuroDecodeKit can express and
validate leakage-resistant optional classical EEG adapter plans before
installing or fitting them.

Scientific claim not established even if all gates pass: adapter contracts
establish no real EEG signal effect, neural origin, decoding accuracy,
generalization, latency, device performance, home use, or clinical result.
