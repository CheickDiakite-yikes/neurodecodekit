# DREYER-C5R-1 H-L1R1 Generated Recovery Authorization Packet

Date: 2026-08-29

Status: **request only; every authority flag remains false**

Machine request:

- `registries/dreyer_c5r_1_stage_h_live_recovery_authorization_request.v0.json`

Packet ID: `DREYER-C5R-1-HL1R1`

## Why This Is The Next Gate

The first H-L1 generated/mock attempt did useful work but failed acceptance.
After writing its durable consumed marker and creating its private staging
directory, it constructed the opener before entering the cleanup boundary. An
opener-construction refusal therefore left staging behind and emitted no
aggregate H0. The exact failed implementation is preserved and may not be
repaired, rerun, or reinterpreted.

Rejected-result proof commit `a70fda0a808751c6057ed07117b7d22ee715a273`
passed Base Python `99049010377`, Optional Neuro Readers `99049010221`, and CI
`33233017769`, then reached GitHub `main`. This packet binds 14 exact public
artifacts / 204,302 bytes from that green state. It requests a generated-only
successor and grants no authority now.

## Corrected Transaction Contract

The successor must be additive. The failed source, CLI, tests, receipt hashes,
and original Stage H parser remain byte-identical.

After preconsumption proof, resource, path, and output checks, the successor
may write the generated qualification marker. The protected transaction must
begin immediately after marker durability and before staging creation, opener
construction, request construction, or any response operation. It must:

1. own an explicit invocation manifest of only paths created by that attempt;
2. convert expected and unexpected standard exceptions into allowlisted codes
   without publishing exception text;
3. close any opened response, remove invocation-owned staging, and remove any
   unaccepted invocation-created final payload through separately accounted
   teardown steps;
4. downgrade H1 to H0 if response closure or teardown fails;
5. publish exactly one sanitized H0 for every post-marker failure while the
   registered public destination remains writable; and
6. if publication itself is the injected failing capability, leave no staging
   or payload and emit only the allowlisted publication refusal to the caller.

Cleanup may never inspect, follow, rename, or delete a path not recorded in the
invocation manifest. A failure during cleanup is not success and may never
activate H-L2.

## Requested Generated Work

Only after one fresh packet-bound maintainer decision is committed, pushed,
and remotely green may an additive standard-library successor module, CLI, and
tests be implemented. The implementation may use generated EDF fixtures,
temporary directories, injected openers, generated proof records, and mocked
resource readers only. It may not expose a usable real command.

After the exact implementation is committed, pushed, and remotely green, a
separate all-false activation may permit at most one registered qualification.
That one qualification must prove:

- two byte-deterministic H1 replays;
- the inherited two valid Stage H cases and 18 Stage H refusals;
- all 43 ordered successor refusal cases in the machine request;
- marker-before-capability ordering and exactly one opener/request on H1;
- response closure, invocation-manifest containment, no staging debris, and no
  unaccepted final payload after every applicable post-marker refusal;
- aggregate H0 publication after opener construction and response-open
  failures;
- no-replace H1/H0 publication and consumed-rerun refusal; and
- zero network, real/private, EDF, target, model, provider, device, release, or
  scientific-claim operation.

The run is consumed whether it passes or fails. There is no retry, rerun,
repair, resume, case substitution, threshold change, or post-result amendment.

## Resource Envelope

| Resource | Frozen maximum |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 0 |
| Wall time | 30 seconds |
| Peak process-tree RSS | 256 MiB |
| Generated input plus output | 8 MiB |
| Incremental temporary disk | 16 MiB |
| Public result | 1 MiB |
| Network bytes / HTTP requests | 0 / 0 |
| Registered qualifications | 1 |

## Explicit Exclusions

This request authorizes nothing now. It excludes H-L2 activation, the real
14,805,604-byte EDF, every other Dreyer object, all network access, all real or
private paths, raw EDF/MAT/EEG data, headers, annotations, signals, targets,
labels, participants, models, training, inference, predictions, scoring,
language models, providers, RW3, streams, devices, hardware, releases, other
projects, and all scientific or product claim upgrades.

Even a successful generated successor would establish only that the wrapper
fails closed under its registered synthetic matrix. It would not authorize or
establish the real sensor header, the full 60-person cohort, an EEG effect,
participant generalization, peripheral-adjusted decoding, language, live
decoding, hardware performance, or clinical value.

## Decision Boundary

Every authority flag in the machine request is false. This request must first
be committed, pushed, pass both required CI jobs, and receive its own green
proof-only closeout. Only then may the maintainer's next unambiguous
packet-bound `approve`, `continue`, or `proceed` authorize the exact additive
generated implementation and its later separately activated one-shot
qualification. No short-form instruction predating this packet may activate
it.

Engineering capability requested: add a transactionally complete generated
wrapper successor that proves cleanup and aggregate refusal behavior across
every registered failure point before any real-data decision.

Scientific claim not established: this all-false request performs no real EEG
operation and establishes no neural, decoding, unseen-person,
peripheral-adjusted, live, hardware, or clinical result.
