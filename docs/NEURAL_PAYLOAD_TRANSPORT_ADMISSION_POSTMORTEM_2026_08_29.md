# Neural Payload Transport Admission Postmortem

Date: 2026-08-29

Status: **Tier A artifact-only research complete; no source promoted and no
network, real-data, target, model, score, device, release, or claim authority**

Machine record:

- `registries/neural_payload_transport_admission_postmortem.v0.json`

Protocol selected for generated implementation:

- `NPA1-v0`, Neural Payload Admission 1

## Decision

Do not spend a third irreversible neural checkpoint discovering basic endpoint
behavior. Before another dataset becomes the flagship, separately admit its
transport path with a tiny opaque canary, then verify its sensor header, and
only then consider acquisition or modeling.

No fresh source is selected by this postmortem. Existing committed evidence
does not contain a candidate that is both scientifically sufficient for the
nuisance-controlled unseen-person question and already admitted on its current
live transport surface.

## What The Evidence Actually Says

Four committed result classes matter:

1. `DREYER-C5R-1-HL2-R0` opened one NEMAR response but accepted zero body
   bytes and read no EDF header. Its aggregate cause is intentionally unknown.
2. `OFNER-C6R-1-HL-R0` accepted the exact NEMAR manifest, opened the first
   256-byte GDF range response, accepted zero GDF body bytes, and read no
   header. Its aggregate cause is also intentionally unknown.
3. The BNCI Stage A redirect recovery successfully accepted and hash-verified
   779,873,919 bytes across 18 NEMAR signed objects after signed-object
   transport was isolated and generated-qualified.
4. The IACKD transport analysis showed that HTTP framing and content identity
   must be separate decisions; a strict framing assumption can refuse before
   any content is read even when bounded hashing would remain possible.

These artifacts do **not** establish one shared NEMAR bug, a redirect failure,
a range failure, a Python failure, or a server failure. Dreyer and Ofner
deliberately did not publish enough raw response detail to support that claim.

They do establish one shared process failure: live transport admissibility was
still unknown when each irreversible scientific header checkpoint began.

## The NPA1 Architecture

NPA1 separates five identities that earlier lanes partially coupled:

```text
scientific source identity
  -> transport capability identity
  -> HTTP framing admissibility
  -> bounded content identity
  -> semantic sensor eligibility
```

### NPA1-G: generated transport qualification

Build one dependency-free validator around injected responses. Reuse the
tested standard-library patterns already present in the MARC1, IACKD, BNCI,
and Ofner modules instead of creating another general networking framework.

The fixture matrix must cover:

- direct HTTP 200 object delivery;
- direct HTTP 206 single-range delivery;
- zero, one, and two bodyless HTTPS redirects when a source profile explicitly
  permits them;
- stable object identity with refreshed signed capabilities;
- fixed-length, chunked, and close-delimited small metadata bodies;
- exact `Content-Range`, cap-plus-one, identity encoding, and duplicate-header
  handling; and
- private-address, downgrade, loop, host, path, query, expiry, overread,
  underread, close, retry, and second-open refusals.

Two deterministic replays and at least 24 named adversarial families are the
minimum acceptance surface. The implementation may use one CPU thread, one
worker, 30 seconds, 256 MiB peak RSS, and 8 MiB generated input plus output.
It may make no network request and retain no generated payload.

### NPA1-M: source identity research

For each candidate, bind an immutable revision, exact member path, declared
size and checksum, license, and the nuisance-control measurement contract.
Treat a signed URL as a capability, never as the scientific identity. A source
cannot advance merely because its paper is attractive or its total size fits.

### NPA1-C: opaque live transport canary

A later, separately authorized Tier C packet may request at most one exact
256-byte range from one prospectively named member. The bytes are never parsed,
published, cached, or reused scientifically. The wrapper records only a
sanitized transport witness: terminal status class, redirect count, final-host
match, framing profile, encoding state, range-admissibility class, accepted
byte count, segment hash, and close state.

This canary is itself one-shot and consumed. Passing it proves only that the
registered transport profile delivered the bounded opaque segment. It does
not prove full-object identity, file format, sensor contents, or neural value.

### NPA1-H and later

Only a remotely green canary can precede a separately governed fixed-header
read. Only a remotely green header result can precede full acquisition.
Acquisition, semantic validation, prediction freeze, target delivery, and one
score remain distinct later gates.

```text
G generated -> M metadata -> C opaque canary -> H header
            -> A acquisition -> Q semantics -> P freeze -> T score
```

## Candidate Admission Rule

A fresh source must satisfy all of these before promotion:

- at least ten genuinely held-out participants;
- recorded EOG and preferably EMG or kinematics;
- named sensor locations;
- task timing that permits cue, pre-cue, posterior, and derangement controls;
- a clear reusable license;
- an exact selected surface within the 20 GiB allowance; and
- a remotely green NPA1-C transport witness for the exact source profile.

Dreyer and Ofner remain consumed and cannot be renamed into retries. BNCI and
EEGMMIDB are prior evidence surfaces, not fresh nuisance-complete replication
sources. The IACKD transport correction is useful architecture but does not by
itself provide an independent fresh cohort. A later source research pass must
therefore identify a new candidate rather than silently reusing one of these
lanes.

## Why This Is The Fastest Credible Route

The change adds one tiny step but removes a costly failure mode. It prevents a
large model or acquisition plan from being built around an endpoint that has
never delivered even one bounded segment under the exact client rules. It also
keeps transport failures diagnostically useful without exposing raw URLs,
headers, participant information, or neural payload.

This is infrastructure for reaching the next biological test, not the test
itself. The next autonomous milestone is only the NPA1-G generated validator
and qualification. Any NPA1-M network research, NPA1-C canary, real header,
payload, model, target, score, device, release, or claim operation remains
closed until its applicable authority and green barriers exist.

Engineering capability added: NeuroDecodeKit now has a frozen transport-admission architecture that separates endpoint qualification from scientific payload and prevents another one-shot neural gate from being spent on unobserved HTTP behavior.

Scientific claim not established: this artifact-only analysis accessed no EEG, sensor header, event, target, model prediction, or score and therefore establishes no neural advantage, unseen-person generalization, movement-intention decoding, language decoding, live operation, hardware result, or clinical value.
