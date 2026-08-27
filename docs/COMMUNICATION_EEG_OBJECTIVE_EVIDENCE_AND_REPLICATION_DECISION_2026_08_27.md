# Communication EEG Objective Evidence And Replication Decision

Date: 2026-08-27

Status: **Tier A public-source and aggregate-evidence decision only; no real or
private data, model, target, prediction, score, provider, stream, or device
operation**

Machine record:
`registries/communication_eeg_objective_evidence_and_replication_decision.v0.json`

## Why This Decision Exists

NeuroDecodeKit now has substantial evidence-control engineering, but the final
research objective is not "run an EEG classifier." It is to show that a
causal decoder extracts user-intended communication information from EEG that
cannot be explained by eyes, mouth activity, timing, prompts, participant
identity, or a language model, and that the result repeats in new people and a
separate cohort.

This record turns that objective into an auditable evidence ledger. A stage may
advance engineering without upgrading a scientific claim. A partial-control
dataset may answer a useful narrower question without being called a full
replication.

This is an additive sequencing correction to the earlier proof-bound program
record. It does not rewrite that immutable artifact: where the earlier order
placed replication source qualification after discovery scoring, this record
narrows the route by requiring the replication protocol freeze before any
discovery target delivery.

## Current Evidence Ledger

| Requirement | Current evidence | Status |
| --- | --- | --- |
| Real held-out task information | The closed BNCI lane produced above-prior and above-timing candidate EEG performance, but posterior EEG performed slightly better and participant consistency failed. | Directional evidence only |
| Prompted communication information | No target-firewalled real inner-speech communication score has run in this program. | Not established |
| EEG beyond recorded eye and mouth activity | The BNCI EEG increment over EOG was small and missed the frozen magnitude, consistency, and significance gates. No oral-EMG-adjusted communication score exists. | Not established |
| Completely unseen-person communication | Existing motor and BNCI work does not establish zero-calibration communication decoding in a new person. | Not established |
| Independent communication replication | No second communication cohort has passed a separately frozen prediction-and-score sequence. | Not established |
| Causal continuous decoding | Reusable causal components exist, but no claim-bearing communication model has processed a source stream without trial-boundary oracles. | Engineering only |
| Live neural decoding | No actual-device communication run has measured capture-to-stable-output latency, dropout recovery, abstention, and accuracy together. | Not established |
| External reproducibility | The toolkit and contracts are public and testable, but an outside group has not repeated the target scientific result because that result does not yet exist. | Engineering only |

The ledger is intentionally strict. Above-chance classification is not enough
if posterior, EOG, EMG, cue, time, or prior controls explain the same outcome.
An LLM cannot repair this evidence gap: language-only and deranged-neural plus
language arms must remain in the final comparison.

## Source Roles

### Discovery cohort: OpenNeuro `ds003626-v2.1.2`

This remains the best verified first test because the primary descriptor
reports prompted inner-speech commands with 128 EEG, four EOG, and two oral-EMG
channels across ten participants. It is a **discovery** cohort, not an
independent replication. Its exact public identity sequence is registered but
the metadata packet remains queued, inactive, and all-false.

### Full-control replication watchlist: SilentSpeech-EEG

At public repository commit
`16ac8686627a74820e59cb02e6b8506a7abc24b2`, BrainStack describes 120+ hours, 12 collected
participants, ten in the claimed public release, 24 words, and 122 EEG plus 11
extra channels. The repository contains `data/load_data.py`, but an open issue
documents that its imported `data/dataset.py` and expected dataset layout are
absent. Its availability statement still says the full dataset was under
preparation and not included in the submission. No stable dataset DOI or
immutable release, complete payload manifest and hashes, dataset license,
reproducible loader, or exact public EOG/oral-EMG channel map was verified in
this pass. It remains scientifically promising and operationally unqualified.

### Partial external challenge: TESSCCo

The 2026 Scientific Data descriptor reports 24 participants, five bilingual TV
commands, covert and overt speech, 32 EEG channels at 256 Hz, and 7,936 epochs.
It provides a strong independent prompted-command surface, but the public
descriptor reviewed here does not verify recorded EOG or oral EMG. It can test
cross-dataset command decoding after exact payload and license qualification;
it cannot alone establish EEG information beyond both eye and mouth activity.

### Partial eye/face challenge: Kara One

The official University of Toronto page verifies 14 participant archives,
64-channel EEG, four ocular electrodes, Kinect facial features, 1 kHz
sampling, and participant-held-out evaluation in the original work. It does
not verify separately recorded oral EMG, and the complete archive is about
24 GB. A deterministic selected subset would need its own completeness and
storage proof. Kara One cannot silently stand in for a full oral-EMG-adjusted
replication.

### Confound-focused and engineering sources

Directional Word 2026 is useful for oral-muscle and timing checks because it
reports two EMG channels, but only six of 22 participants have EMG and no
separate EOG was reported. ArEEG and other compact imagined-speech sources can
qualify loaders and participant firewalls, but missing peripheral controls
keep them below the full claim boundary.

Dreyer Dataset A remains a motor-imagery control-method precursor. Even a
successful Dreyer result could validate unseen-person EEG-beyond-EOG/EMG
methodology for visually cued left/right motor imagery; it would not establish
language, spontaneous intention, communication, or live decoding.

## Frozen Routing Decision

1. Preserve `DREYER-C5R-1-HL` as the sole active Tier C packet and keep every
   authority flag false until a separate exact maintainer decision becomes
   remotely green.
2. Keep `COMM-L0-META` queued and all-false. Do not contact OpenNeuro or inspect
   a private path under this decision.
3. Treat `ds003626` as discovery only. Its future score may not be used to
   select a replication cohort, preprocessing family, threshold, or capacity.
4. Freeze the independent replication source, hypothesis, feature/control
   family, model family, thresholds, and exclusion rules before discovery
   targets are delivered or scored. Replication execution still occurs only
   after the discovery result.
5. Monitor SilentSpeech-EEG for an immutable public release and exact external
   channel roles. Promote it only if it passes every source gate without
   private clarification.
6. Keep TESSCCo and Kara One as named partial replications. Their maximum claim
   must enumerate the unavailable peripheral control rather than borrowing the
   discovery cohort's controls.
7. If no full-control public release qualifies, preregister a small prospective
   cohort with synchronized EEG, EOG, bilateral oral EMG, randomized prompts,
   untouched participants, consent, privacy, and hardware receipts. That is a
   future Tier C and ethics decision, not authority granted here.

## Needle-Moving Order

The shortest credible scientific route is:

1. prove exact source identity and a complete under-cap `ds003626` slice;
2. qualify one bounded real reader and the frozen nuisance/EEG control matrix
   on generated fixtures;
3. create participant-isolated derivatives without held-out target delivery;
4. freeze source-trained discovery predictions;
5. preregister and freeze the independent replication before any discovery
   target delivery or score;
6. score discovery once, then execute the independently frozen full or
   explicitly partial replication;
7. only after offline evidence passes, bind the model into the causal stream
   and conduct one prospective actual-device run.

This order does not promise a positive result. It maximizes the chance that a
positive result is scientifically interpretable and that a negative result
identifies the next useful constraint instead of consuming a cohort ambiguously.

## Resource And Authority Boundary

- one CPU thread, one worker, and one numerical job by default;
- 20 GiB total incremental research-storage allowance;
- 10 GiB maximum selected raw data for the communication discovery lane;
- zero payload, private-path, signal, target, model, score, provider, stream,
  device, deletion, release, or claim operation in this decision;
- no write outside NeuroDecodeKit; and
- no change to the active Tier C packet.

Engineering capability added: the program now has a machine-tested evidence
ledger and source-role router that separates discovery, full replication,
partial replication, method precursors, and live evidence.

Scientific claim not established: this decision did not demonstrate
communication decoding, EEG information beyond eye or mouth activity,
unseen-person generalization, independent replication, causal continuous
decoding, live neural decoding, or clinical value.

## Primary Sources

- [Thinking Out Loud descriptor](https://www.nature.com/articles/s41597-022-01147-2)
- [OpenNeuro `ds003626-v2.1.2`](https://openneuro.org/datasets/ds003626/versions/2.1.2)
- [BrainStack repository snapshot](https://github.com/Jacoo-Zhao/BrainStack/tree/16ac8686627a74820e59cb02e6b8506a7abc24b2)
- [BrainStack availability snapshot](https://github.com/Jacoo-Zhao/BrainStack/blob/16ac8686627a74820e59cb02e6b8506a7abc24b2/Code_and_data_availability_statement.md)
- [BrainStack missing-loader issue](https://github.com/Jacoo-Zhao/BrainStack/issues/1)
- [BrainStack paper](https://openaccess.thecvf.com/content/CVPR2026F/papers/Zhao_BrainStack_Neuro-MoE_with_Functionally_Guided_Expert_Routing_for_EEG-Based_Language_CVPRF_2026_paper.pdf)
- [TESSCCo descriptor](https://www.nature.com/articles/s41597-026-07745-8)
- [Kara One official dataset page](https://www.cs.toronto.edu/~complingweb/data/karaOne/karaOne.html)
- [Directional Word descriptor](https://www.nature.com/articles/s41597-026-07809-9)
- [ArEEG descriptor](https://www.nature.com/articles/s41597-025-05387-w)
