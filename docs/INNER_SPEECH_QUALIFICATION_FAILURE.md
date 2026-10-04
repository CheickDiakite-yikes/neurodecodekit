# Inner-speech run stopped at event qualification

September 28, 2026. **The decoding question remains untested.**

The single corrected launch used `d137b52dd1198d91e5fe2786e6d196c69f877003`
after both remote CI jobs passed (workflow `36496762314`). The narrow path fix
worked. All ten recordings passed the frozen receipt, path/size and full-file
SHA-256 checks. The run then stopped at `event_grammar` for `sub-01`, after
**9.645 seconds**, with peak RSS **43,851,776 bytes (41.82 MiB)**.

The [aggregate failure record](../registries/inner_speech_qualification_failure.v0.json)
preserves the sanitized marker and explicitly separates observed metadata from
facts established by its position in the frozen code. The private attempt and
failure marker remain untouched. There was no retry, partial score or source
row inspection after failure.

## What was and was not learned

Participant 01's header validated and its full Status channel was decoded.
Event format and chronological order passed, but a required event was missing
or unexpected at some grammar position. The marker does **not** identify that
position; it does not distinguish source corruption from a parser assumption
that differs from the recording. Do not invent a specific missing marker.

No participant completed qualification. No fold preflight, physiological
EEG/EXG window extraction, feature computation, fitting, prediction, target
export, freeze or scoring occurred. The Status list contains cue/target codes,
so the earlier claim that labels remained unopened no longer applies. Their
values were neither inspected nor disclosed outside the runner; the number of
partially parsed trials is unknown.

This is not a failed primary endpoint or a biological null. It changes no
belief about how much imagined-word information EEG contains. It establishes
byte identity and functioning path handling, but not event compatibility.

## Next priority

Resolve the exact event-structure mismatch before another model run. The next
proposed action is a separately approved bounded structural audit of event
categories, with no physiological sample analysis, fitting or scoring. Return
only the failing structural state and sanitized aggregate diagnostics—not raw
event rows, direction identities or guessed labels. Then decide whether a
source-faithful parser correction is justified. Do not automatically repair,
rerun, drop participants/trials or weaken any scientific control.
