# COMM-P0 generated FS2 rehearsal result

Date: 2026-08-28
Gate: `COMM-P0-G-FS2-v0`
Run: `COMM-P0-G-FS2-R0`
Route: `FS2_PARK`

## Result

The sole receipt-consuming full-scale generated rehearsal is complete and
permanently consumed. One of the two required sequential fictional replay
children completed, but the shared runtime reached `180.05074683297426`
seconds, exceeding the frozen 180-second ceiling by
`0.05074683297426` seconds. The executor routed the run to
`FS2-resource_or_monitor_failure` and did not start or complete a permissible
second replay within the deadline.

No retry, rerun, resume, repair, substitution, or reinterpretation of
`COMM-P0-G-FS2-R0` is allowed. The official generated qualification remains
inactive.

## Measured envelope

| Measure | Observed | Gate |
|---|---:|---:|
| Runtime | 180.05074683297426 s | at most 180 s |
| Peak process-tree RSS | 305,119,232 bytes | at most 536,870,912 bytes |
| Process-monitor samples | 1,510 | at least 1 |
| Free disk before reservation | 37,863,190,528 bytes | at least 22,012,755,968 bytes |
| Free disk after reservation | 37,325,271,040 bytes | at least 21,474,836,480 bytes |
| Reserved-disk delta | 537,919,488 bytes | exactly the registered ceiling |
| Retained generated payload | 0 bytes | exactly 0 bytes |
| Public result | 2,286 bytes | at most 1,048,576 bytes |
| Rehearsal receipt | 531 bytes | separate target-free receipt |

The peak RSS, free-space, reservation, monitor, retained-payload, and public
output gates passed. The shared runtime and two-child completion gates failed.

## Completion and unavailable fields

- completed replay children: 1 of 2;
- canonical replay equivalence: unavailable because two completed surfaces did
  not exist;
- canonical replay SHA-256: unavailable;
- distinct replay-worker PIDs: unavailable from the aggregate park result;
- observed generated counters: unavailable from the aggregate park result;
- end-to-end device latency: not measured.

The first child's completion means it passed the registered child validator
before being counted. The aggregate result intentionally withholds partial
prediction and per-child counter surfaces, so the unavailable fields above are
not reconstructed from the registered schedule.

## Exact evidence identities

- contract SHA-256:
  `ce533db97ace7b1d8c1423f48227119699f66e454252b78b9acd80b65a8f0a7a`;
- implementation-proof SHA-256:
  `3ca7ad91893716b751abc60a2e828132d2c8682a4f5491e4bca2e46172ef8919`;
- target-free public-result SHA-256:
  `17dcb54837eff1932bec474051ee1981f8e139146f35f4c5f6a0e0ef2f8de881`;
- rehearsal-receipt SHA-256:
  `0e76a4ce898e93b85bdf2602876b6539909acc354c0ac5296d654751f823792e`.

The ignored result and receipt remain local execution evidence and are not
committed. This closeout records only their target-free aggregate identities
and measurements.

## Zero-operation boundary

Measured network bytes and provider/network operations were zero. Official
qualification, official activation reads, official marker operations,
real/private path operations, real signal reads, real target or label reads,
real-data training or inference, humans, devices, streams, microphones,
releases, post-target updates, and scientific claim upgrades were all zero.

Warnings: the records were fictional and generated; this was not the official
qualification; generated runtime is not device latency; and this has no
scientific evidentiary value.

## Next engineering decision

FS2 answered the resource question negatively under the exact frozen envelope:
two complete 21-person-per-cohort replays did not fit inside 180 seconds on
this machine. Future work may use this measured result prospectively to design
a new generated-only gate with a justified runtime or workload change, but may
not rerun or repair FS2-R0 and may not silently activate the official
qualification.

## Claim boundary

Engineering capability added: NeuroDecodeKit executed and safely parked a
resource-monitored, zero-network, full-scale fictional replay under a durable
one-shot receipt while cleaning all temporary payload bytes.

Scientific claim not established: no real EEG, human target, official
qualification, neural decoding, EEG-beyond-peripheral effect, unseen-person
generalization, independent replication, causal-live operation, device
latency, or clinical value was tested or established.
