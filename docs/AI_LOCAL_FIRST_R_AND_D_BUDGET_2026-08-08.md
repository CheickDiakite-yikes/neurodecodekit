# AI And Local-First R&D Budget

**Date:** 2026-08-08
**Status:** $50 aggregate AI-provider ceiling authorized; local-first strategy
active; individual evidence and protected-data gates preserved

## Decision

Use the user's $50 AI budget as a ceiling, not a spending target. Cheap provider
calls should qualify interfaces and language controls; mature open-source tools
and local CPU work should carry preprocessing, benchmarking, baselines, model
comparison, and sensor abstraction whenever possible.

FM-1's locally calculated $0.002394 covers only two completed responses. The
third attempted response did not enter strict usage accounting, so reserve the
entire registered $0.50 FM-1 cap until provider billing is reconciled. This
leaves a conservative $49.50 portfolio ceiling.

This standing budget authorizes bounded synthetic and public, non-protected,
target-free provider-development calls under a committed machine contract,
fixed call/model/cost caps, no hidden retries, and a sanitized receipt. It does
not reopen FM-1 or authorize protected data, target delivery, raw neural
uploads, scientific scoring, hardware, purchases, large downloads, releases,
or claim promotion. Those actions retain their existing exact gates.

## Ceiling Portfolio

| Lane | Ceiling | Release condition |
|---|---:|---|
| FM-1 accounting reserve | $0.50 | Hold until actual provider billing is known; never use it to rerun FM-1 |
| FM-1B independent transport recovery | $1.50 | New fixture and contract; diagnose completion mechanics without replaying observed FM-1 payloads |
| FM-2S synthetic Sol/Terra controls | $3.00 | Only after transport recovery; identical blinded matrix and explicit model-cost comparison |
| Public target-free evidence integration | $5.00 | Public license, privacy screen, compact evidence packets, no target or scoring |
| Public target-bearing four-arm evaluation reserve | $10.00 | Separate exact target/scoring decision and frozen predictions first |
| Protected scientific evaluation reserve | $20.00 | Clean upstream neural gate plus separate exact privacy, target, and claim decision |
| Contingency and unallocated reserve | $10.00 | Spend only when a preregistered question cannot be answered locally |

The ceilings total $50. They are not commitments to spend. Any unused amount
stays unspent. A lane may borrow from contingency only through an additive
ledger update before the call. No experiment may borrow from a later protected
lane merely because earlier provider calls are inexpensive.

## What The Earbud Patent Actually Shows

US patent application `US20230225659A1`, filed by Apple and published on
2023-07-20, describes a wearable earbud-form device with multiple active and
reference electrodes and a switching circuit. The design can select or weight
electrode subsets based on impedance, noise, placement, and contact quality.
The specification names EEG as one possible biosignal and discusses electrical
brain activity.

The document is a pending patent application, not evidence that current
AirPods contain enabled EEG electrodes. The term `AirPods` does not appear in
the application. It contains no thought-to-text experiment, language decoder,
accuracy result, consumer-product release record, or proof of brain-specific
origin. The useful signal for NeuroDecodeKit is architectural: ear-worn sensing
may need dynamic contact-aware channel selection and explicit missingness.

Primary source:

- https://patents.google.com/patent/US20230225659A1/en

## Local Tool Stack

### MNE-Python

Use MNE as the optional file, metadata, annotation, channel-geometry,
preprocessing, visualization, and classical-decoding substrate. NeuroDecodeKit
keeps its base install dependency-free and uses MNE only behind explicit
extras. Future local work should reuse MNE's artifact, referencing, CSP, and
quality tooling rather than duplicate it.

- https://mne.tools/stable/auto_examples/preprocessing/index.html
- https://mne.tools/stable/api/decoding.html

### MOABB

Use MOABB to select and compare public EEG datasets, paradigms, pipelines, and
within-session, cross-session, and cross-subject protocols. Its current
documentation indexes 158 open EEG datasets and builds on MNE plus
scikit-learn. NeuroDecodeKit should wrap a tiny allowlisted dataset slice and
`n_jobs=1`; MOABB's convenient download defaults do not override our separate
network and storage gates.

- https://moabb.neurotechx.com/docs/index.html
- https://moabb.neurotechx.com/docs/auto_examples/how_to_benchmark/index.html

### pyRiemann

Use covariance plus MDM/tangent-space pipelines as serious low-data baselines.
They are inspectable, scikit-learn compatible, and often a better first test
than adding model depth. A neural candidate that cannot beat a properly grouped
Riemannian baseline should park before provider or architecture escalation.

- https://pyriemann.readthedocs.io/en/latest/index.html

### Braindecode

Use Braindecode as an optional architecture and training adapter, not a reason
to download every checkpoint. Its current stable documentation exposes compact
filter-bank/convolution models alongside much larger foundation encoders and
interoperates with MNE and MOABB. Start with compact published architectures,
same split/controls, one thread where practical, and an explicit parameter cap.
Pretrained-weight downloads and fine-tuning remain separate decisions.

- https://braindecode.org/stable/index.html
- https://braindecode.org/stable/models/models_table.html

### Around-The-Ear And Commodity Hardware

OpenBCI documents cEEGrid as a reusable 16-channel around-the-ear electrode
array compatible with Cyton+Daisy, the OpenBCI GUI, and BrainFlow. This is a
more concrete local research prospect than assuming consumer earbuds expose
EEG. It is still hardware: no purchase, SDK install, connection, participant
recording, or claim is authorized by this strategy.

- https://docs.openbci.com/ThirdParty/cEEGrid_Kit/

## Proposed Local Architecture

```text
file or future device adapter
  -> MNE-compatible channel, timing, annotation, and geometry record
  -> target-blind contact/noise/impedance quality views
  -> causal electrode-subset and missingness policy
  -> MNE plus pyRiemann classical baselines
  -> compact Braindecode/CML candidate under the same split
  -> CTC evidence packet
  -> separately bounded foundation-model language layer
```

The electrode policy must preserve every source channel and quality metric,
emit the selected subset and weights as inspectable metadata, and use no target
or post-outcome signal. Synthetic contact-loss, channel-swap, and motion-noise
fixtures come first. A future implementation should describe the mechanism in
our own generic quality-control terms and obtain legal review before any
commercial earbud implementation; a patent publication is not an open-source
license or freedom-to-operate opinion.

## Next High-Value Sequence

1. Finish and freeze the parked FM-1 closeout.
2. Build a zero-network local tool capability matrix against current optional
   dependencies and resource limits.
3. Add synthetic ear-channel quality and subset-selection fixtures with no
   model or provider call.
4. Qualify pyRiemann and one compact Braindecode family on the existing public
   motor positive-control design after its separate data contract.
5. Prepare FM-1B only if the provider question cannot be answered from local
   schema tests; use an independent fixture and a tiny call ceiling.
6. Keep at least $30 reserved until a real upstream neural signal beats its
   no-signal and corruption controls.

## Claim Boundary

Engineering direction added: NeuroDecodeKit now has a budgeted local-first path
that can reuse mature EEG tooling and prepare for contact-variable ear-worn
sensors without coupling the core package to one device.

Scientific claim not established: a patent, toolbox, public dataset catalog,
or hardware prospect does not prove thought reading, useful neural decoding,
brain-specific information, real-time output, portability, home use, or
clinical utility.
