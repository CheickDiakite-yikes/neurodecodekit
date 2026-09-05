# Real EEG result: this fixed candidate did not qualify for unseen-person testing

EEGMMIDB-SMR-D1-R0, 5 September 2026. **Terminal development-check failure.**

The fixed central-EEG-plus-timing-metadata model achieved **57.95% mean
held-run balanced accuracy** across ten participants. Its probability
improvement was small and insufficiently consistent: only **3 of 10** people
exceeded the prespecified 0.020-nat log-loss improvement over their
training-only prior; six were required. The candidate therefore stopped
before unseen-person prediction, exactly as registered.

| Prespecified adequacy criterion | Observed | Required | Outcome |
|---|---:|---:|---|
| Mean participant balanced accuracy | 57.9464% | At least 55% | Passed |
| People with class-macro log-loss improvement >0.020 nats | 3/10 | At least 6/10 | Failed |

Mean class-macro log loss was **0.69129699**, versus **0.69314718** for the
training-only prior: an improvement of **0.00185019 nats**. Mean binary
class-macro Brier score was **0.24770123**. These are descriptive development
results; the 57.95% accuracy is not a claim of statistically significant
above-chance performance.

Ten source participants (S031–S040) each supplied R03 for training and R07
for evaluation. The broker retained **300/300 trials across training and
evaluation combined**, with zero exclusions. Ten fixed logistic models were
fitted once. There was no tuning, recalibration, model selection, or retry.
The common mask, three central bipolar channels, three frequency bands,
timing features, weighting, scaling and classifier were fixed before access.

This is negative evidence about this candidate's readiness to advance.
It does not establish absent neural information or explain the weak result.
Timing metadata alone and the other EEG controls were not fitted because the
development check stopped the experiment first. The observed performance
therefore cannot be attributed specifically to central EEG. Visual cues,
eye/muscle activity, participant variability and probability calibration
remain unresolved explanations.

**The unseen-person hypothesis remains untested.** The twenty confirmation
participants (S041–S060) received file-size HEAD checks only: zero confirmation
EDF GETs, feature extraction, predictions, target deliveries or final scores.
This is not a failed seven-control conjunction or a confirmation null.

The run completed in **371.808 seconds**, comprising 293.603 seconds of
acquisition and 76.751 seconds of numerical processing. It made 62 source
requests: two metadata GETs, forty EDF HEADs and twenty development EDF GETs.
Metadata bodies totalled 317,701 bytes; EEG bodies totalled 51,277,440 bytes
(48.902 MiB). Peak process-tree RSS was 220,577,792 bytes (210.359 MiB).
Peak incremental allocation was 65,269,760 bytes (62.246 MiB), with
64,974,848 bytes retained (61.965 MiB) and zero retained invocation temporary
bytes. All measured resource totals remained within the frozen limits.

Source: [PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/),
DOI 10.13026/C28G6P, ODC-By 1.0. The runner verified the source identity,
license, named checksum entries, all forty sizes, and all twenty acquired
development file hashes before numerical use.

The complete [request](EEGMMIDB_SMR_D1_END_TO_END_REQUEST.md) was approved
by the maintainer's exact “continue” at decision commit
`d129e16ccc636279878a3c03aebdecf0692d7c21`. Implementation
`2befbc14073ad96aca61e22066dd74aaa3a1c61e` passed
[CI 33989065199](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/33989065199)
before source contact. Small generated tests and an actual OS access-denial
canary supported execution; they are not neural evidence. The
[machine result](../registries/eegmmidb_smr_d1_result.v0.json) contains the
aggregate measurements and exact implementation identity. Three read-only
critics reviewed the interpretation; this is not independent replication.

The attempt is consumed and cannot be resumed or rescued. A useful separate
future hypothesis would ask whether central EEG improves held-run log loss
over timing metadata alone and timing metadata plus deranged EEG on fresh,
prospectively selected development data. That comparison was not performed
here and has no execution authorization from this closeout.
