# IACKD-2 Registered Stream Result

Date: 2026-08-11

Status: **Consumed and parked at metadata transport identity; no retry**

Route: `IACKD2-F08-payload_size_ETag_SHA_or_run_group_cap_failure`

Registry:
`registries/iackd_role_aware_dual_reversal_stream_failure_result.v0.json`

## Ordered Evidence Gate

The exact real-executor implementation was commit
`dab5dd47ee47f285430311e4fe0f38f457d1118a`. CI run `31461818620`
passed Base Python job `93686690177` and Optional Neuro Readers job
`93686690138` before the sole stream invocation.

The launch used one CPU thread, one worker, one numerical job, the exact
registered implementation evidence, and the existing qualified optional
environment. An external preflight observed 24,862,810,112 free bytes, above
the 10 GiB minimum. The tracked worktree was clean. The unrelated untracked
tracker inspection file was not staged, read, changed, or deleted.

## What Happened

The executor wrote its exclusive no-retry consumed marker at
`2026-08-11T05:51:05.419830Z`, created empty invocation-owned derivative and
temporary directories, and opened the first of four registered metadata
responses.

That first source was the already public and committed dataset-description
identity:

| Field | Registered value |
|---|---|
| URL | `https://s3.amazonaws.com/openneuro.org/ds006840/dataset_description.json` |
| Expected body bytes | 1,178 |
| Expected SHA-256 | `275cf1d24f93832ed17fd32d46a589286453042f8d2788b4f3dc1933c6523d93` |

The exact HTTP status and final-URL checks passed, because execution advanced
to the next ordered guard. The response then failed the strict condition that
its `Content-Length` header exist and equal 1,178. The implementation did not
retain whether the header was absent or had a different numeric value. It did
not read the response body, compute a body hash, parse JSON, or open a second
metadata response.

The stable failure is therefore the registered `IACKD2-F08` transport/body-
identity family. It is not evidence that the body content changed, and it is
not evidence that the body content stayed the same. That distinction is
unavailable because the no-retry executor correctly stopped before reading the
body after its header gate failed.

## Exact Access Boundary

The invocation performed:

- one public metadata GET open;
- zero metadata body reads and zero metadata semantic parses;
- zero selected-object requests and zero selected-object bytes;
- zero VHDR, VMRK, EEG, events, channel, geometry, ball, or Leap parses;
- zero signal-sample, trajectory, target, or label reads;
- zero model or sealed-target derivative files;
- zero parameter-update fits, model inferences, prediction sets, freezes,
  target deliveries, or scores;
- zero old retained-bundle operations;
- zero provider, language-model, stream-device, hardware, release, or claim
  operations; and
- zero retry, rerun, resume, or restart.

The private invocation root contains one 267-byte consumed marker and four
empty invocation-owned directories. No aggregate acquisition receipt was
created because acquisition did not pass its first metadata identity stage.
Runtime, peak RSS, response-header wire bytes, response-body wire transfer,
and the observed `Content-Length` value were not retained and are reported as
unavailable rather than estimated.

## Why The Stop Is Correct

The frozen contract required zero retries and zero reruns. Its consumed marker
was intentionally written before the first real request so a transport failure
could not become an unregistered second look. Running the command again,
deleting or renaming the consumed marker, changing the expected byte count,
probing the same URL, or relaxing the parser after seeing this result would
violate the evidence boundary.

Because no complete derivative exists, the authorized downstream sequence
cannot continue:

- the 660-fit target-blind analysis is not executable;
- no 900-set prediction matrix exists;
- no prediction freeze can be created or committed;
- no final target may be delivered; and
- no scoring route may be applied.

IACKD-2 is consumed and parked at the stream stage. The analysis and scoring
permissions were conditional on a complete accepted stream, so they were not
consumed by separate model or target operations; they are simply unreachable
inside this closed lane.

## Engineering Insight

The useful result is architectural. A body SHA-256 and a bounded exact body
read are content-evidence checks. `Content-Length` is an HTTP transport header:
it may be absent or represented differently even when a bounded body can still
be read and hashed. Requiring exact `Content-Length` before reading the first
pinned metadata body made the acquisition brittle without producing stronger
content evidence.

A separately named prospective recovery design should distinguish metadata
transport from payload identity:

1. keep exact URL, status, redirect, encoding, timeout, body-size cap, and
   no-retry controls;
2. permit an absent or non-authoritative metadata `Content-Length` while
   reading at most the registered cap plus one byte;
3. decide metadata identity from the observed body byte count and immutable
   SHA-256 after the bounded read;
4. retain exact size, ETag, and one-pass SHA-256 requirements for the large
   selected dataset objects;
5. record the observed transport headers in an aggregate non-sensitive failure
   receipt before any later content stage; and
6. require a fresh preregistration, implementation proof, Tier C decision, and
   new invocation identity before any request.

This proposal does not authorize that recovery lane. It only localizes why the
current lane stopped and how a future contract can gain robustness without
weakening content integrity.

## Claim Boundary

Engineering capability added: the exact one-shot executor proved that its
pre-request evidence gate, consumed marker, strict transport check, target
firewall ordering, and no-retry stop work on a real public endpoint.

Scientific claim not established: no EEG payload, signal, event, trajectory,
target, model, prediction, or score was reached, so this result establishes no
neural effect, action decoding, brain-specific origin, unseen-person
generalization, language or thought decoding, real-time operation, hardware
capability, assistive benefit, home use, or clinical use.
