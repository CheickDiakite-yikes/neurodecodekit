# Thought to text hypotheses and discriminating experiments

October 2, 2026. The maintainer requested a coordinated scientific swarm aimed
at discoveries, not additional infrastructure. Three independent reviews covered
identifiability, neural representation and decisive source data; the lead agent
reconciled their claims and challenged the proposed mechanisms. No new recording
was acquired or analyzed during this review.

## The milestone that matters

Recover information about an intended word that the external prompt, timing,
language prior and measured peripheral activity cannot already explain, then
test transfer to an untouched linguistic combination or recording day. A
four-class accuracy improvement is an intermediate result, not thought-to-text.

Our existing spectral experiment was negative. The first session-2 temporal
attempt [stopped before physiology](INNER_SPEECH_TEMPORAL_FAILURE.md); its
separately approved [narrow successor completed](INNER_SPEECH_TEMPORAL_ATTENTION_RESULT.md)
and was also negative. Ordered signed bin means failed the primary and cue
sensitivity criteria, with 0/10 people beating every primary control. This
weakens that fixed representation, not every temporal EEG hypothesis.

## The team's strongest finding is a limit of the question

In the current prompted-word task, the instructed target Y is determined by the
cue C. Thus H(Y|C)=0 and I(Y;EEG|C,P,T)=0, where P denotes peripheral measurements
and T timing/history. This is **our mathematical deduction**, not a measured
zero-information result: conditioning on the full cue already supplies the answer.
Without that conditioning, successful decoding cannot uniquely distinguish
imagery from cue perception, remembered meaning, spatial attention or movement.
The [dataset authors](https://www.nature.com/articles/s41597-022-01147-2) also
acknowledge uncertainty about whether participants perform the intended mental task.

Changing cue format can weaken a visual-cue explanation, but does not by itself
exclude semantic memory. A stronger future design permits different privately
selected words under identical external inputs, with the randomized reporting
layout revealed only after the analyzed interval. Reporting fidelity, peripheral
coverage and adherence remain assumptions; new human research requires separate
authorization and appropriate oversight. No collection is proposed for execution now.

## Competing hypotheses

| Hypothesis | Smallest useful falsifier | What would reject it |
|---|---|---|
| Ordered beta-amplitude trajectories carry information lost by averaging | One fixed 12–24 Hz envelope representation and linear model, compared with whole-window power, independently scrambled time bins per trial, matched peripheral features and label nulls | No held-out increment, or the advantage survives temporal scrambling |
| Reusable phonetic features transfer better than memorized word identities | One prespecified distinction trained on two syllable contexts and tested on an unseen third, with cue and peripheral controls | Only familiar contexts or selectively chosen people work |
| Apparent word information is largely cue/history/peripheral prediction | Identical external input with privately chosen content; pre-choice, timing/history and expanded peripheral controls; an untouched day | The pre-choice or nuisance model explains the apparent decoding advantage |

The first hypothesis is motivated by a
[September 29, 2026 ECoG study](https://www.nature.com/articles/s41593-026-02456-0)
linking speech imagery to beta1 articulatory dynamics. Its invasive measurement
and overt-derived imagery target proxies limit transfer to our scalp setting.
This is a **candidate mechanism**, not a result of our project.

Our frozen raw-bin test is not this envelope test. Thirty-two action bins over
two seconds yield 16 summaries/second and an 8 Hz Nyquist limit. Boxcar averaging
has its first zero at 16 Hz and can alias surviving higher-frequency components.
This does not destroy every beta-related effect, but it is not extraction of a
12–24 Hz amplitude envelope. These are code/sampling deductions, not empirical
findings. The consumed experiment is not amended or reopened by this observation.

The adversarial review caught an important null-design trap: one common time-bin
permutation would only rename columns and leave isotropic ridge predictions
unchanged. The proposed scramble must use a label-independent, reproducibly
seeded permutation per trial, synchronized across channels, before training-only
scaling. It preserves simultaneous spatial patterns but destroys alignment and
autocorrelation as well as order; beating it supports useful time-locked structure,
not specifically a causal language mechanism. Envelope filtering must not borrow
cue, neighboring-trial or held-out samples. These are requirements for a future
protocol, not an authorized analysis or an edit to the consumed experiment.

## Use published knowledge without confusing reproduction with discovery

[Kunz et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC12360486/) provide an
intracortical reference contrasting verbal and visual rehearsal within the same
arrow-sequence task, including transfer from attempted speech. Those effects
are already published: reproducing them would validate an assay, not constitute
our discovery. They also do not prove scalp feasibility or arbitrary thought decoding.

The [primary Dryad record](https://datadryad.org/dataset/doi%3A10.5061/dryad.gf1vhhn1j)
lists three relevant archives totaling approximately 360.11 MB compressed:
speech sequence recall, verbal memory and visual memory. Only public metadata
were reviewed; transport, extracted size, exact matching sessions and local
runtime remain unverified. No download is authorized by this document.

The team found no verified, immediately accessible scalp dataset that settles
cue-independent spontaneous thought-to-text. The relevant
[EEG/MEG preprint](https://www.biorxiv.org/content/10.1101/2025.10.13.682161v1)
reports mostly chance-level inner-speech results despite silent-reading success.
Treat it as a counterweight, not as either a scalp ceiling or an acquisition-ready source.

## How the swarm will work

Keep three scientific roles: a mechanism advocate, an independent falsifier,
and a source/measurement reviewer. Each returns one hypothesis, its strongest
alternative explanation, a quantitative endpoint and a rejection condition.
The lead chooses **one** bounded experiment by expected information gain and
cost. No parallel parameter sweeps, favorable-participant selection or language
model rescue. If a language model is later used, compare the identical model,
context, search and timing with content-bearing neural evidence removed.

The all-ten structural audit and approved numerical successor are complete.
Both publication CI suites for result commit `53098f3` passed in
[workflow 37038468059](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/37038468059).
The source review below changes the next recommendation; it does not reopen
the failed experiment or authorize another data-accessing run.

## Source review changes the next experiment

The next recommended observation is a **reference reproduction of attempted
speech transfer to verbal versus visual memory**, preserving the remaining
scalp evidence. Train one fixed linear readout on attempted speech, then compare
its predictions during the memory delay under the two strategies, with arrow
content, evaluation blocks and timing matched. Use no language model. This is
a design candidate, not an executable or already approved experiment.

The [Kunz primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12360486/)
provides the same-arrow strategy contrast and attempted-speech reference in
intracortical recordings. Its processed spike features are not verified beta
field potentials. A successful reproduction would show sensitivity to known
speech-related information modulated by strategy, not novel thought-to-text,
scalp feasibility or recovery of privately selected content. Strategy-dependent
attention and task differences would remain alternative explanations.

Public [Dryad metadata](https://datadryad.org/dataset/doi:10.5061/dryad.gf1vhhn1j)
and its [dataset API](https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gf1vhhn1j)
were checked on October 2, 2026: version 2, version ID 379376, CC0-1.0.
The [file inventory](https://datadryad.org/api/v2/versions/379376/files) advertises:

| Selected archive | File ID | Compressed bytes |
| --- | ---: | ---: |
| seqRecallSpeech.zip | 4203849 | 79,443,728 |
| seqRecallVerbalMemory.zip | 4203853 | 175,492,315 |
| seqRecallVisualMemory.zip | 4203851 | 105,176,285 |
| Total | | 360,112,328 |

License and advertised size are verified, not actual archive transport or
contents. Exact paired participant/session/block coverage, event definitions,
decompressed size and available peripheral measurements remain unresolved.
No archive, neural sample, target, prediction or weight was opened in this review.

### Approved acquisition stopped at HTTP transport

The sole approved acquisition is now **failed and consumed**. Implementation
`40c052f` passed nine generated-only tests and Ruff before its one invocation.
It stopped during the first archive attempt with `HTTPError` after 1.062 seconds,
at 36,548,608-byte peak RSS. Zero archive bytes were copied; the local archive
file is empty. No ZIP inventory, internal README, neural array, event, target,
fit or score was opened or produced. The local start and failure markers remain
unchanged; their hashes and measured outcome are in the
[aggregate failure record](../registries/kunz_reference_qualification.v0.json).

The helper did not retain the HTTP status or headers. Do not infer 401, 403,
rate limiting, an authentication cause or a permanent source restriction.
[Dryad's API documentation](https://github.com/datadryad/dryad-app/blob/main/documentation/apis/api_accounts.md)
requires tokens for API downloads, but that does not diagnose a failure on its
separate web-download route. No credential, account, retry, alternate endpoint
or workaround was used. This is an access blocker, not a biological null or a
thought-to-text result.

**Next proposed boundary:** one separately approved, thirty-second,
header-only diagnostic of the first approved web-download URL, at most four
HTTPS redirects, retaining only status and sanitized technical header metadata.
No explicit response-body read, archive retention, array or trial access,
acquisition retry, model or score is included. This can distinguish HTTP failure
classes without another blind full-download attempt. It does not promise a fix.

**Approved October 2, 2026:** the maintainer replied "continue approved, lets
please get closer to thought to text" to the explicit acquisition-only request.
The source-decision commit `4182ec8` passed both
[CI jobs](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/37042602118).
That approval admitted one acquisition and documentation check, not a neural
experiment, and is now consumed. Its original scope was to acquire only these three
archives once into local storage outside OneDrive; inspect ZIP directories and
their documentation, not neural arrays or per-trial event/target records.
Approved limits: ten minutes, 500 MiB transferred, 512 MiB retained archives,
256 MiB RSS, one worker, at most 64 KiB of documentation, and no extraction
of scientific arrays. Stop on mismatch, missing matching coverage, timeout or
resource failure; no automatic retry or substitution. The output should be
only a source-fit decision and the exact information needed to freeze one
reference experiment. No training or scoring is included in that permission.

## Keep beta dynamics as a separate hypothesis

The [new ECoG paper](https://www.nature.com/articles/s41593-026-02456-0)
motivates 12–24 Hz analytic-amplitude trajectories, not signed waveform bins.
It used nine surgical participants; imagery articulation targets were derived
from overt speech, and EMG monitoring covered four. Its human recordings are
controlled-access, so an open paper is not an acquisition-ready dataset.
This supports a hypothesis to test, not evidence of scalp translation.

The adversarial review makes three prospective improvements to a beta test:

- Compare ordered envelopes against the **same envelope's mean and mean squared
  amplitude**. Comparing only against the old 13–30 Hz power features changes
  the frequency range and amplitude statistic as well as temporal structure.
- Add a trial-specific circular time shift, shared across EEG channels, with
  peripheral inputs unchanged. It preserves the cyclic autocorrelation and
  simultaneous spatial pattern more closely than arbitrary bin scrambling.
  Superiority indicates useful task alignment, not a uniquely linguistic
  sequence; one fixed null is not a randomization significance distribution.
- Predeclare separate content and measurement-sensitivity interpretations.
  Failed cue decoding does not alone validate an absence-of-imagery conclusion.
  No threshold in the completed experiment is relaxed.

The [scalp dataset descriptor](https://www.nature.com/articles/s41597-022-01147-2)
places all three sessions on the same day and gives session 3 variable trial
counts. Subtracting the first two 200-trial sessions from published totals
implies 75–170 session-3 trials per person; these are derived bounds, not
verified event counts or task-cell coverage. The current five-by-forty parser
is therefore not a drop-in fit. Refitting within session 3 would test fresh
trials in familiar people and context, not cross-day or cross-session transfer.

For planning only, if independent people each have probability p of passing
all controls, the chance of at least nine passes in ten is
10*p^9*(1-p)+p^10: 37.58% at p=0.8 and 73.61% at p=0.9. This is an assumption-
based consistency-gate calculation, not power for the whole experiment;
additional effect thresholds can only lower the pass probability. Preserve
uncertainty rather than calling every failed gate a biological null.

**Do not acquire or open session 3 now.** Keep beta testing parked until a
source-specific design can answer its question. The later approved archive
attempt failed as recorded above. No neural experiment, outreach, human study
or model tuning occurred.

The substantive change is the research target: **identify a transferable
content-bearing mechanism**, not optimize a score whose origin we cannot distinguish.
