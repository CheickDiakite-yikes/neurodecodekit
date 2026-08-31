# Public Motor Cross-Cohort Scientific Synthesis Result

Date: 2026-08-31

Result ID: `PUBLIC-MOTOR-SYNTHESIS-v0`

Status: **completed retrospective synthesis of hash-bound public aggregate
results from three real-data cohorts; no raw payload, private prediction,
target, or consumed experiment was reopened or rescored**

Machine result:
`registries/public_motor_cross_cohort_synthesis_result.v0.json`

## Scientific result

The strongest reproducible signal is low-frequency **task information**, not a
central-motor-specific signal.

The three-person EEGMMIDB discovery cohort and the disjoint twelve-person
confirmation cohort together contain 15 participants and 225 held-out
execution events. Their fixed low-frequency arms produced 159 correct events,
a descriptive combined accuracy of `0.706667`, and a participant-count-weighted
mean macro balanced accuracy of `0.705952`.

The discovery within-participant label-permutation test and the confirmation
participant sign-flip test had `p=0.0001831055` and `p=0.0029296875`.
Fisher's retrospective combination is
`X2(4)=28.876616`, `p=0.00000828175`. That combined value is not a new
confirmatory p-value because the low-frequency family was promoted after the
pilot outcome and the two tests use different null randomizations. The valid
prospective confirmation remains the disjoint S004-S015 result at
`p=0.0029296875`. These are fresh participants in the same dataset and the
same research program, not an independent-dataset or independent-team
replication.

## Cross-cohort spatial result

The registered central or selected-EEG contrast failed to outperform the
strongest available spatial control in all three real-data cohort phases:

| Cohort | People | Registered candidate | Candidate macro BA | Strongest spatial control | Control macro BA | Candidate minus control |
|---|---:|---:|---|---:|---:|
| EEGMMIDB S001-S003 | 3 | central sensorimotor | 0.520833 | frontal/occipital | 0.613095 | **-0.092262** |
| EEGMMIDB S004-S015 | 12 | central sensorimotor | 0.649554 | frontal | 0.671131 | **-0.021577** |
| BNCI 2014-001 | 9 | selected E | 0.383488 | posterior | 0.392361 | **-0.008873** |

The participant-count-weighted descriptive margin is `-0.025649` balanced-
accuracy points. All three cohort signs are negative. The value `0.125` is only
the nominal probability of three negative signs under an unverified
independent-fair-sign assumption; it is not a valid inferential p-value because
two phases share one dataset/program and the BNCI contrast is not harmonized.
Participant-level paired margins are not public, and the tasks, features, and
controls differ. BNCI's registered candidate-versus-posterior contrast is not
the same model contrast as the EEGMMIDB central-versus-proxy comparisons, and
choosing the strongest control structurally favors negative margins. A formal
pooled effect is therefore not valid.

This is therefore convergent negative evidence against candidate spatial
specificity on the available surfaces. The first two candidates are central
sensorimotor models; BNCI's registered candidate is `selected_E`. This is not
proof that central EEG never carries motor information.

## Peripheral-attribution result

Only BNCI recorded EOG. Adding selected EEG to EOG improved macro log loss by
`0.025524`; the advantage over EOG plus deranged EEG was `0.018431`. Both were
positive in only six of nine people and nonsignificant (`p=0.291016` and
`p=0.322266`). None of the three cohorts recorded the required task-relevant
EMG.

The full FMSR1 claim—central EEG increment beyond joint EOG, every relevant-
effector EMG, posterior EEG, cue/pre-cue/shifted timing, and deranged EEG—remains
untested. The present evidence instead says that task information replicates
while central-source attribution repeatedly fails or remains unresolved.

## Evidence and integrity boundary

The deterministic analysis read six tracked public JSON files exactly once:
three aggregate results, two EEGMMIDB contracts, and one BNCI source-identity
record. It verified their SHA-256 identities, the disjoint EEGMMIDB participant
sets S001-S003 and S004-S015, and distinct dataset identifiers `eegmmidb`
v1.0.0 versus `BNCI_001_2014` / NEMAR `nm000139` v1.0.2. Biological-person
overlap across the anonymized datasets is unknown. The analysis made zero
network requests and performed zero raw neural reads, private or ignored reads,
target deliveries, model fits, predictions, or scores.

No individual prediction, probability, target, or participant outcome is
published here. This synthesis does not reactivate, retry, reinterpret, or
alter any consumed experiment.

## Claim boundary

Scientific evidence supported: a fixed low-frequency EEG representation
prospectively replicated held-out-run left/right task information in twelve
fresh participants after a three-person discovery cohort.

Convergent negative result: none of three examined registered candidate
contrasts outperformed its strongest available spatial control.

Not established: the complete nuisance-controlled FMSR1 conjunction, a
brain-specific or motor-cortex source, unseen-person generalization,
independent replication, intention, language or thought decoding, prospective
operation, assistive benefit, or clinical utility.
