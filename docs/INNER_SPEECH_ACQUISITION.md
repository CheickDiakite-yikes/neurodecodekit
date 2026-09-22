# Fresh imagined-word cohort: bounded acquisition

September 22, 2026. Acquisition only; no decoding or biological result.

The user approved the previously proposed **ds003626 v2.1.2, all ten people,
first common complete raw session, EEG/eye/lip channels preserved, at most
10 GiB, local-only** acquisition: "that was a glitch. i meant approved, lets
do that, get us closer to thought to text". This is a new source-specific
approval, not activation or reuse of the historical generated-only COMM-L0
qualification. It does not authorize an unspecified scoring experiment.

## Source and exact slice

The release tag resolves to Git commit
`d96743351ae4e5d0ee7a1384320ea8d52a2ce698`; its complete 298-entry tree has
all ten people and sessions 01, 02 and 03. Select **ses-01 for every person**,
without looking at outcomes. The ten raw BDFs total **6,904,627,200 bytes
(6.4304 GiB)**. Preserve every channel, including status. The pinned root
README and CC0 dataset description accompany them. The
[manifest](../registries/inner_speech_source_manifest.v0.json) lists exact
paths, sizes, Git-annex pointers and publisher MD5 identities.

The actual raw tree has **no separate event/channel sidecars**. The old
generated selector assumed an arbitrary companion existed; that assumption
does not describe this release. No channels are removed or substitutes
introduced. Header-only qualification must verify the EEG and EXG channel
layout and 1024 Hz sampling. Event/condition completeness remains unverified
until a separately frozen event qualification; file presence cannot prove it.

## Execution boundary

One streaming acquisition, no parallel workers, retries, overwrite or resume.
Cap elapsed acquisition at 60 minutes, RSS at 1 GiB, generated metadata at
32 MiB, and retain at least 20 GiB free disk. Stop and preserve partial evidence
on any identity, geometry, resource or transport failure; do not drop a person.
Raw bytes live under the user's **local AppData**, outside the OneDrive project.
Only public identities and sanitized technical receipts may enter Git.

Verify each BDF's exact byte count and publisher MD5; record a local SHA-256.
MD5 is the publisher's legacy integrity identifier, not modern collision-proof
authentication. All ten metadata-only HEAD requests matched the pinned lengths
and MD5 ETags; the manifest now also pins their returned S3 object versions.
HTTPS, the release tree and versioned objects provide additional provenance.
Read only the BDF technical header;
do not emit its patient/date fields or decode any physiological samples,
status events, target values or decoding results. No MNE preprocessing runs.

## Scientific step this unlocks

Freeze one four-word imagined-speech comparison: peripheral-only versus
auxiliary-independent EEG plus peripherals, with matched misalignment,
label-shuffle and cue/timing controls; retain pronounced and visualization
conditions. Freeze source-specific event handling, splits, training, primary
endpoint and interpretation before opening outcomes. Do not silently use the
author parser's missing-direction imputation or condition corrections.

Target-free source-code review is pinned to author commit
`65bd162a32f38546b6596cb25d46f4a862fa87fb`. Its
[parser](https://github.com/N-Nieto/Inner_Speech_Dataset/blob/65bd162a32f38546b6596cb25d46f4a862fa87fb/Python_Processing/lib/events_analysis.py)
identifies a missing direction by global minimum class count. Its
[extraction](https://github.com/N-Nieto/Inner_Speech_Dataset/blob/65bd162a32f38546b6596cb25d46f4a862fa87fb/Python_Processing/lib/data_extractions.py)
uses a special 2 ms trigger-duration rule for participant 10/session 1.
These are prospective parser-design dependencies, not observations from our
participant data. No author code is executed during acquisition.

The paper's ad-hoc correction also says participant 03/session 1 performed
one inner-speech run and three visualization runs. A uniform inner-run-1 to
inner-run-2 split would therefore fail the all-person scope. This must be
resolved prospectively without discarding that person.
[Published correction](https://pmc.ncbi.nlm.nih.gov/articles/PMC8844234/).

Before payload access, seven generated-only safety tests and focused Ruff
passed; independent review found no remaining acquisition blocker. The first
test invocation used a OneDrive temporary fixture and correctly refused it;
the final tests used local AppData. No participant data or network is used by
those tests. Remote CI must also pass before executing the acquisition.

The source has three consecutive sessions on **one day** and direction-linked
visual cues. This is a fresh-cohort, same-day attribution opportunity, not
new-day robustness, unseen-person decoding, cue-independent thoughts, arbitrary
text, prospective use or clinical utility. Acquiring files is not a breakthrough;
the test must tell us whether EEG adds imagined-word information beyond the
recorded alternatives. [Dataset paper](https://www.nature.com/articles/s41597-022-01147-2).
