# Session 2 event audit supports a narrow attention boundary revision

October 2, 2026. The single approved Status-only audit completed all ten
recordings in **29.58 seconds**, with exact ordered event agreement between the
two existing decoders for every recording. It supports proposing a narrow
attention-placement successor to the failed temporal experiment. It does **not**
establish a decoding improvement or authorize that successor to run.

## Observations across the complete cohort

The [unchanged aggregate](../registries/inner_speech_session2_audit_result.v0.json)
contains 10,457 events summarized into 2,000 diagnostic segments: five intact
run-boundary pairs per person, each containing 40 segments and one condition
marker. There were no detected duplicate phases, ambiguous segments, malformed
run boundaries, non-increasing sample pairs, unrecognized event families or
attention groups interleaved between observed phases. All available phase
interval and core-window checks were within their fixed bounds; unavailable
checks remain unavailable.

Of 119 attention groups, 118 followed an observed rest. **One group in participant
3 followed relax without an observed rest**, after a contiguous, ordered
start→cue→action→relax sequence and before the next observed start. This is
consistent with an absent rest marker beside an otherwise intact core, not proof
that a rest event occurred. Two other groups contained an answer without an
observed question; both followed rest. No event was inserted, inferred or removed.

Nine segments each lacked exactly one phase marker; the other 1,991 contained
all five. These omissions were not hidden by the attention finding:

| Absent phase | Segments | Participants |
| --- | ---: | --- |
| Start | 1 | 9 |
| Cue | 1 | 6 |
| Action | 4 | 7 and 10, two each |
| Relax | 1 | 5 |
| Rest | 2 | 3 |

Thus **1,994 diagnostic segments contain all three core markers** and six do
not. Six is within the existing twenty-per-cohort exclusion cap; the respective
person counts of one, one, two and two are within the existing two-per-person
cap. These are structural counts, **not 1,994 qualified trials**. Condition
identities/layout, condition-specific coverage, class support and all thirty
split preflights were deliberately not evaluated. Structural exclusions are
not proven missing at random.

## Belief update and next experiment

The evidence narrows the blocker: the observed attention boundary is unsupported
by our frozen rule, while the other observed phase omissions fit the existing
structural allowance. It does not show that the recordings are generally corrupt,
nor that every scientific eligibility check will pass. The temporal-information
hypothesis remains untested and the prior negative session-1 result is unchanged.

**Next priority:** propose one explicitly opted-in successor that accepts an
single question/answer pair after observed relax with rest absent only when the
other four phases are present once, ordered, within their available timing
bounds, and followed by the next observed trial start. Preserve the old behavior
by default, all immutable attempts, both decoders and their full ordered
agreement check. Never fabricate the absent rest or ignore attention anywhere
else.

Keep the existing all-ten, three-condition, thirteen-arm temporal-versus-spectral
comparison, features, controls, exclusion limits and decision thresholds unchanged.
Require complete qualification and split checks before physiology, a fresh
20-minute total cap including freeze publication and one score, and fresh
approval before data access. No automatic retry, new acquisition, participant
dropping or session-1/session-3 exposure. Do not fold the separate beta-envelope
hypothesis into this correction: the existing test concerns ordered signed bin
means, not beta-envelope trajectories.

Even a later positive result would not prove cue-independent thoughts, cortical
origin, arbitrary text, new-day or unseen-person transfer, or clinical utility.
The next meaningful milestone remains a measured EEG improvement against the
fixed controls, not acceptance by a parser.

## Verification and preservation

Implementation `85511a9da6d9b7ea625c5e620c61aeab97718448` was pushed and both
[CI suites passed](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/37030991525)
before the run. Forty-eight focused generated tests and Ruff passed locally.
Peak audit RSS was 45,690,880 bytes; start plus local/public aggregate copies
total 214,611 bytes, below the 256 MiB and 1 MiB limits. Full source hashes were
verified before and after; prior evidence and scientific code were unchanged.

The local/public aggregate SHA256 is
`c07767e099cb88185548245b5cfc64d89bcc75cbde93323b27fc9d3b59a200f5`.
Opaque whole-file hashing read physiological bytes without decoding them; there
were **zero physiological windows, trial-parser calls, fits or scores**. Only
collapsed structural counts and hashes were published. The data-quality review
kept unavailable checks and ancillary/core defects separate; two independent swarm
reviews verified the totals and interpretation against the frozen rules. No audit rerun or
numerical successor was launched.
