# OFNER-C6R-1-HL Range-Header Result Closeout

Date: 2026-08-29

Status: **sole invocation consumed at transport H0; closeout becomes immutable
after this exact result set is committed, pushed, and both required CI jobs are
green**

Machine records:

- `registries/ofner_gdf_header_live_result.v0.json`
- `registries/ofner_gdf_header_live_result_closeout.v0.json`
- `registries/current_research_frontier.v6.json`

## Result

The sole `OFNER-C6R-1-HL-R0` invocation is permanently consumed at aggregate
route `OFNER-H0-TRANSPORT` with sanitized refusal `OHL-TRANSPORT`.

The exact NEMAR `nm000173` `v1.0.3` manifest completed identity selection. The
wrapper then attempted the first registered `bytes=0-255` request for
`sourcedata/motorimagination_subject1_run1.gdf`, but no GDF body byte passed the
strict transport firewall. The second range was never attempted.

The public aggregate intentionally cannot distinguish whether the refusal was
caused by response status, final URL, content length, duplicate or encoded
headers, multipart framing, content range, body delivery, or close behavior.
No more specific cause may be claimed from this artifact.

## Measured Boundary

- one manifest GET and 1,352,270 manifest body bytes;
- one first-range GET attempt and zero accepted GDF body bytes;
- zero full-file requests or full-payload SHA-256 passes;
- zero fixed-header reads or semantic parses;
- zero event, annotation, signal, target, or label reads;
- zero model, inference, training, prediction, target-delivery, or score runs;
- zero retries, reruns, fallbacks, substitutions, provider calls, device work,
  release operations, or claim upgrades;
- 1.1932796670589596 seconds runtime;
- 48,021,504-byte peak process RSS;
- 4,096 private allocated bytes and 2,340 public result bytes;
- 66,082,369,536 free disk bytes after the attempt; and
- zero retained payload bytes.

The durable private consumed marker was written before live source access. The
closeout records only its reported 455-byte size and does not reopen it.

## Interpretation

This is a fail-closed transport observation, not a biological null. It neither
accepts nor rejects the frozen Ofner hypothesis, because no GDF header, sensor
roster, geometry, event, signal, target, model prediction, or score was
observed.

The generated parser and firewall remain valid generated engineering evidence.
They do not establish that this public endpoint can deliver the registered
ranges or that the source contains the reported real 61 EEG, three EOG, 19
glove, and 13 arm channels at 512 Hz.

## No-Rerun Boundary

Never retry, rerun, repair, resume, substitute, or reinterpret
`OFNER-C6R-1-HL-R0`. Do not reopen its Git-ignored marker or create a new packet
that merely disguises the same attempt as a retry.

No remaining Ofner GDF, bulk acquisition, event, annotation, signal, target,
model, score, stream, device, release, or claim operation is authorized by
this result.

## Next Gate

After this closeout is remotely green, the next reversible work is a Tier A
artifact-only transport postmortem and fresh transport-verified source
selection. Any later network or real-data operation requires a separately
named, exactly scoped, remotely green Tier C packet and must not reopen the
consumed attempt.

Engineering capability added: the exact range-only wrapper failed closed on a real public endpoint, preserved a durable no-rerun boundary, and emitted a bounded aggregate result without accepting or retaining a GDF payload byte.

Scientific claim not established: no real GDF header, neural signal, nuisance channel, target, model prediction, or score was observed, so this establishes no neural advantage, unseen-person generalization, movement-intention or motor-cortex attribution, thought or language decoding, live decoding, hardware result, or clinical value.
