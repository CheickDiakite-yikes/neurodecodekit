# TESSCCo Communication EEG Source Readiness

Date: 2026-08-27

Status: **Tier A public-source identity research only; source not
acquisition-ready; zero dataset payload or scientific claim operation**

Machine record:
`registries/communication_eeg_tesscco_source_readiness.v0.json`

## Why This Check Matters

The triangulated communication router names TESSCCo as the mandatory
independent partial-transportability key. That role is scientifically useful
only if its exact public dataset can be versioned, listed, bounded, licensed,
and frozen before any discovery target is delivered. A paper citation alone
does not make a reproducible source.

## Verified Public Identity

The Scientific Data article and PubMed record identify TESSCCo as a bilingual
TV-command EEG corpus with:

- 21 native Spanish speakers and three non-native Spanish speakers;
- five covert and overt commands in English and Spanish;
- 7,936 available epochs / approximately 11.02 hours;
- 32 EEG channels at 256 Hz; and
- recorded audio in addition to EEG.

The article cites dataset DOI `10.34740/KAGGLE/DS/9993149`. On 2026-08-27, one
headers-only DOI resolution reached `https://www.kaggle.com/ds/9993149`, but
that landing returned HTTP 404. No Kaggle API, authenticated request, dataset
manifest, metadata body, or file request was made.

## Readiness Decision

TESSCCo remains the frozen **planned** independent partial key, but it is not
operationally qualified and no acquisition packet should be prepared yet.
These source-lock requirements remain unavailable:

- a reachable immutable dataset version or revision;
- owner/slug and exact canonical landing identity;
- complete file manifest, per-file bytes, and checksums;
- total raw and selected-slice byte counts;
- dataset license and access/authentication requirements;
- exact raw versus preprocessed file roles;
- exact participant/session/language/condition completeness;
- channel labels, geometry, reference, and whether separate EOG or oral EMG
  exist; and
- event, cue, timing, audio, target, and trial grammar.

The article's CC BY-NC-ND 4.0 license applies to the article and must not be
silently copied onto the underlying dataset. The article reports EEG and audio;
it does not verify a separately recorded EOG or oral-EMG control surface in
this pass. Even after source qualification, TESSCCo therefore remains a
partial transportability test rather than independent full peripheral
attribution unless its exact public payload proves otherwise before any score.

## Router Consequence

- Keep `ds003626-v2.1.2` as full-control discovery attribution.
- Keep `ds007591-v1.0.1` as a nonrouting three-person mechanistic bridge.
- Keep TESSCCo as the named independent partial key, but mark that key blocked
  at source identity rather than pretending an inaccessible DOI is runnable.
- Do not substitute another source after seeing a discovery result. Any future
  replacement must be independently justified, frozen, and remotely green
  before discovery target delivery.
- Do not promote the bridge or a partial-control cohort to full replication.

## Measured Research Operation

- one public article-page GET returned 228,070 HTML bytes when the advertised
  PDF endpoint served the article page rather than a PDF;
- one DOI-resolution invocation produced two headers-only responses: DOI 302
  to Kaggle, then Kaggle 404;
- exact transport-header bytes and browser-search request counts are
  unavailable;
- zero Kaggle metadata API requests;
- zero dataset payload requests or bytes;
- zero private paths, neural headers, signals, events, targets, labels, models,
  predictions, scores, providers, streams, devices, releases, or claim
  upgrades; and
- no cleanup, deletion, overwrite, or write outside NeuroDecodeKit except the
  228,070-byte public article response retained under `/tmp`.

## Next Gate

Do not create a TESSCCo acquisition packet until a public source exposes a
reachable immutable version, manifest, byte envelope, dataset license, and
exact sensor/event roles. A future source-readiness refresh may make only a
target-free metadata request under its own exact decision; it may not request
an EEG file or displace the sole active Tier C packet silently.

`DREYER-C5R-1-HL` remains the sole active Tier C packet and every authority
flag remains false.

Engineering capability added: the independent replication router now refuses
to treat a paper-cited but currently unreachable dataset landing as an
acquisition-ready source.

Scientific claim not established: no TESSCCo neural payload was accessed, so
this work did not test communication decoding, EEG beyond peripheral signals,
unseen-person generalization, independent replication, causal live decoding,
hardware performance, or clinical value.

## Primary Sources

- [Scientific Data article](https://doi.org/10.1038/s41597-026-07745-8)
- [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42387018/)
- [Dataset DOI](https://doi.org/10.34740/KAGGLE/DS/9993149)
- [DOI target observed on 2026-08-27](https://www.kaggle.com/ds/9993149)
