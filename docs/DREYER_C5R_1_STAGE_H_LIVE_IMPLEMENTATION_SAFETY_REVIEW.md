# DREYER-C5R-1 Stage H Live Implementation Safety Review

Date: 2026-08-26

Status: **pre-decision static review; no authority change**

Machine record:

- `registries/dreyer_c5r_1_stage_h_live_implementation_safety_review.v0.json`

## Decision

Keep `DREYER-C5R-1-HL` as the sole active Tier C packet. The one-file Stage H
preflight remains the shortest credible next step because 14,805,604 bytes can
test the sensor-header assumption on which the later 1,779,763,388-byte cohort
depends. A failed header contract should park the lane before the other 119
files are requested.

This review does not authorize H-L1 implementation, generated qualification,
activation, H-L2, a network request, a real path open, or a real EDF read.

## Frozen Artifact Boundary

The already-qualified Stage H parser, generated CLI, packet, request, and test
remain byte-identical. H-L1 must be additive. In particular, the wrapper must
not weaken or edit the existing exact-response, fixed-header, sensor-roster,
sampling-rate, hash, EOF, and cleanup checks.

## Required Additive Safety Shell

The future H-L1 wrapper must implement all of these controls:

1. **Proof before capability.** Read exact locked decision, implementation,
   and activation identities. Collect fresh remote branch and GitHub Actions
   metadata for each required commit and both required jobs before constructing
   a live opener.
2. **Durable one-shot marker.** After proof and the 10 GiB free-disk gate, write
   the unique consumed marker with `O_EXCL` and `O_NOFOLLOW`, flush the file,
   and fsync its parent directory before constructing the opener or request.
   Any outcome after that write is consumed. The H-L1 implementation record
   must freeze the exact private root, marker, staging, payload, and public
   result paths plus the marker schema before activation.
3. **Capability-safe paths.** Use one fixed Git-ignored relative root beneath a
   caller-supplied non-symlink workspace. Validate every existing component
   with `lstat`, create directories one component at a time with mode `0700`,
   and reject traversal, symlink, hard-link, device, and non-directory races.
4. **Private staging and no-replace promotion.** Give the frozen verifier only
   a unique mode-`0700` staging directory. Its internal `os.rename` then occurs
   inside that private capability. Promote the completed payload to the final
   private path with an atomic platform no-replace rename and fsync the parent
   directory. A destination-appearance race must refuse without overwrite.
5. **Exact transport.** Construct one proxy-free standard-library HTTPS opener
   with the default verified TLS context and a redirect-refusing handler. Send
   one direct `GET` to the exact URL with `Accept-Encoding: identity`; forbid
   Range, credentials, cookies, retries, resume, fallback, and substitutions.
   Reject any `Transfer-Encoding` as well as any `Content-Encoding`.
6. **Bounded response lifetime.** Close the response deterministically. Wrap
   body reads with a monotonic 300-second deadline, retain the one-request
   count on failures, and expose no exception text that contains headers,
   paths, or payload content.
7. **Measured resource enforcement.** Enforce one-thread environment values,
   256 MiB peak process-tree RSS, 16 MiB payload bytes, 32 MiB incremental
   allocated disk, 1 MiB public output, and 1 MiB maximum chunks. Recheck
   runtime, RSS, and free disk while streaming and before publication.
8. **Aggregate-only result.** Publish one H1 or H0 result containing only exact
   object identity, allowlisted sensor counts/names, 512 Hz confirmation,
   operation counters, resource measurements, unavailable transport-header
   accounting, warnings, and the unchanged claim boundary. Never publish raw
   EDF header fields, patient/recording/date text, annotations, samples,
   private paths, or exception bodies.
9. **EDF structural byte identity.** Before H1, require the fixed header's
   `header_bytes + record_count * 2 * sum(samples_per_record)` total to equal
   the registered 14,805,604 bytes exactly. A syntactically valid header with
   impossible record geometry must route H0.

## Generated Adversarial Qualification

H-L1 qualification must use only generated payloads and an injected mock
opener. In addition to replaying the existing 20 Stage H cases, it must refuse
at least these wrapper failures:

- decision, implementation, activation, branch, CI run, job, or artifact hash
  mismatch;
- stale, failed, missing, ambiguous, or shallow-checkout remote proof;
- missing thread cap, low free disk, pre-existing marker, symlinked root or
  ancestor, unsafe relative path, occupied staging name, and final-destination
  race;
- opener construction before marker durability, more than one opener call,
  wrong method or request headers, proxy use, redirect, status/final-URL drift,
  duplicate or malformed transfer headers, timeout, and unclosed response;
- short, oversized, non-bytes, encoded, wrong-hash, malformed-header,
  wrong-roster, wrong-rate, and header-to-payload geometry-mismatch bodies;
- runtime, RSS, payload, disk, chunk, or public-output cap excess; and
- cleanup attempts against any path not created by the current invocation.

The qualification must also prove deterministic H1 replay, H0 aggregation,
marker-before-opener ordering, one-request accounting, atomic no-replace
promotion, rerun refusal, and zero real/private/network/scientific operations.

## Scientific Critical Path

Stage H is a cheap structural gate; Q -> P -> T is the scientific center of
gravity:

1. H-L1: additive generated/mock live-wrapper qualification and green
   activation.
2. H-L2: one exact EDF request and fixed-header-only H1/H0 result.
3. H1 amendment: freeze observed EOG/EMG names without changing their role or
   count; this still grants no Stage A authority.
4. A: acquire and hash-verify the remaining 119 R1/R2 EDFs once.
5. Q: require the complete 60-person, two-run, 40-trial structure and create
   fold-isolated features plus sealed held-out targets.
6. P: run the frozen 60-person leave-one-person-out model schedule without
   held-out targets and commit an aggregate hash-only prediction freeze.
7. T: after the freeze is remotely green, deliver targets once and score once.
8. Replication: if and only if route R1 passes, preregister untouched R3-R6
   confirmation and then a genuinely external cohort before live decoding.

An R1 score could establish participant-independent visually cued left/right
motor-imagery condition information with an incremental contribution from the
predeclared central EEG sensors beyond recorded EOG, wrist EMG, posterior EEG,
timing, and derangement controls in this cohort.

It would not establish spontaneous intention, exclusive motor-cortex origin,
thought or language decoding, live decoding, portable hardware, home use, or
clinical utility.
