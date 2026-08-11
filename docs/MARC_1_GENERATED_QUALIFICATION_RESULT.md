# MARC-1 Generated Qualification Result

Date: 2026-08-11

Status: **consumed at `MARC1G-R1`; generated engineering qualification passed;
no retry or rerun; no public or real-data access authorized**

Registry: `registries/marc1_generated_qualification_result.v0.json`

## Green Implementation Gate

The one registered closeout ran only after exact implementation commit
`e35a58743766ba404ae16f63804481a5f51531c9` passed both required jobs in CI
run `31505555044`:

```text
Base Python:             93826102571
Optional Neuro Readers: 93826102044
```

The execution bound implementation registry SHA-256
`88a08c797f9ac2c719e510fe822da2eee43963849334eed02ff37ed7b8ad93d2`.

## Registered Execution

Exactly one fresh process ran with one CPU thread, one worker, one numerical
job, Python `-S`, `PYTHONPATH=src`, and a new output directory under the real
`/private/tmp` parent. It generated all bytes in memory and made no network or
real-path input request.

The command completed once with `MARC1G-R1`:

```text
generated input bytes:    81,139
generated archive bytes:  67,916
generated output bytes:   7,813
runtime:                   0.006588957970961928 seconds
peak RSS:                  23,511,040 bytes
range read calls:          14
range bytes returned:      202,529
payload-overlap bytes:     0
```

The aggregate report was 5,018 bytes with SHA-256
`f7c4de84f7d80bee7461ae38e13c560e54f075a6a6df41faa1aa853a48599c70`.
The generated private manifest was 2,795 bytes with SHA-256
`008ae558bd0192bb853ddc0d8dafa873ba6f048dcc62b0ebaeb6104b0f1150cf`.
The aggregate report was inspected once through the registered CLI. The
temporary output directory was then removed; only these hashes and aggregate
measurements are retained.

## Archive Result

- Exactly 14 members were inventoried: four root metadata members and five
  members for each of two generated subjects.
- One forced ZIP64 member was observed.
- Two members used stored compression and twelve used deflate.
- Compressed member bytes were 329; uncompressed member bytes were 310.
- Two deterministic fixture/inventory replays were byte-identical.
- No member was opened for reading or extracted.
- No range read intersected a writer-recorded compressed-payload interval.
- Archive SHA-256 was
  `4058a3520ea3dece36fced09edf0b4e8183f145943e383fe29fcee8c5daf15ed`;
  canonical inventory SHA-256 was
  `8f76c98e3d057ff8f40cc51aa2dd044925cb5ab9bf15c5aa79a47d9895dd5d50`.

## Multimodal Result

Both generated source profiles passed strict validation. The plan contained
18 channel records: eight EEG, two EOG, two EMG, three acceleration, one
encoder, one audio, and one trigger record. Source type, functional role, and
model inclusion remained separate. Every non-EEG stream was nonpredictive.

The causal `[-1.5, -0.2)` interface window, zero future context, fit-only
normalization, explicit geometry/clock/synchronization states, and all twelve
comparator roles passed. Four fit rows, four target-blind prediction rows, and
four isolated scorer rows passed strict identity and target-firewall checks.
Plan SHA-256 was
`843ba53699ab024d915a8988887477285f93410f607a920e7dfa409856931c5e`.

No fit, inference, prediction, freeze, delivery, or score occurred. The rows
are interface fixtures, not model inputs or a decoding result.

## Adversarial Result

All 24 frozen mutations refused in their assigned class:

```text
MARC1G-F01: 3
MARC1G-F02: 9
MARC1G-F03: 6
MARC1G-F04: 2
MARC1G-F05: 3
MARC1G-F06: 1
```

Every acceptance gate passed. All public, real archive, signal, event/onset,
target/label, derivative, model, prediction, delivery, score, and claim-upgrade
counters remained zero.

## Warnings And Unavailable Fields

- Generated fixtures contain no human neural data.
- The causal window is an interface fixture, not a selected real-data window.
- Unavailable controls remain unavailable rather than becoming zero-valued
  substitutes.
- Real participant identity and geometry are unavailable.
- Human EEG, EOG, EMG, acceleration, encoder, events, onsets, and targets are
  unavailable.
- Decoding accuracy and end-to-end latency are unavailable; latency was not
  measured.
- `MARC1G-R1` does not authorize a public request or scientific claim.

## Disposition

The generated closeout is consumed with no retry or rerun. The next eligible
work is Tier A design of one metadata-only central-directory range audit. A
live HEAD, byte range, public archive response, member payload, signal, event,
onset, target, model, score, or claim upgrade still requires a separately
named Tier C packet and a new exact maintainer decision.

Engineering capability added: a dependency-free generated qualification has
now demonstrated bounded ZIP inventory, deterministic multimodal causal
firewalls, strict target isolation, comparator availability, adversarial
refusal, output privacy, and resource accounting without reading member
payloads.

Scientific claim not established: no human neural data or model was used, so
this result establishes no neural effect, movement decoding, source
attribution, thought decoding, or real-time capability.
