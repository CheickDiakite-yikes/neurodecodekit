# Ofner Fixed-Header Generated Qualification

Date: 2026-08-29

Protocol: `OFNER-C6R-1-HG0`

Status: **accepted generated-only result; exact implementation pending remote proof**

Machine result:

- `registries/ofner_gdf_header_generated_qualification.v0.json`

Implementation:

- `src/neurodecodekit/datasets/ofner_gdf_header.py`
- `python -m neurodecodekit.ofner_gdf_header_cli`

## What Was Built

The dependency-free parser accepts exactly one complete GDF 2.x header and
decodes only the eight fields allowed by the preregistration: version, header
length, record-duration numerator and denominator, signal count, channel
labels, samples per record, and sensor XYZ positions. It never decodes patient
or recording identity, dates, events, annotations, or signal samples.

The transport firewall accepts injected HTTP transcripts only. It requires two
uncompressed `206` responses over non-overlapping, gapless ranges: bytes
0-255, followed by bytes 256 through the declared end of the header. Redirect,
retry, encoding, duplicate-header, length, range, overlap, gap, and over-read
conditions fail closed. No network library or real execution command exists.

## Measured Result

| Measure | Result |
|---|---:|
| Generated replays | 2 |
| Header bytes per replay | 24,832 |
| Range transcripts per replay | 2 |
| Named adversarial refusals | 41 |
| Runtime | 0.002138459 seconds |
| Peak RSS | 26,214,400 bytes |
| Network bytes | 0 |
| Retained generated payload | 0 bytes |

Both replays produced the same parsed summary and transcript digest
`84504f39c8360076318e4e425b22a8a1a2afb038b4f33fa6d0a950e67e436c11`.
The generated header recovered 96 unique labels partitioned as 61 EEG, three
EOG, 19 glove, and 13 arm channels at 512 Hz, with 61 finite nonzero generated
EEG positions.

The 41 refusals cover fixed-header size and version, header-length bounds,
duration, signal count, truncation and trailing bytes, label encoding and role
drift, sampling, non-finite geometry, HTTP status, redirects, duplicate and
missing headers, malformed or wrong ranges, compression, transfer encoding,
body length, gaps, overlap, and over-read.

All real manifest, GDF, header, event, annotation, signal, target, label,
model, training, prediction, and score counters were zero.

## Verification

- Complete dependency-light suite: 6,932 passed and 278 skipped in 255.434
  seconds, compared with 6,903 passed and 278 skipped before this milestone.
- Focused header, preregistration, result, and knowledge-ledger suite: 34
  passed in 0.183 seconds.
- Ruff, Python compilation, strict JSON loading, CLI help, the bounded
  generated CLI roundtrip, and `git diff --check` passed.
- A `pytest` wrapper run exposed one historical COMM-G2 environment-firewall
  failure because that wrapper injected `COLUMNS` and `LINES`; the complete
  dependency-light `unittest` surface above passed with those wrapper-only
  variables absent.

## Interpretation

This closes the generated parser and minimum-byte transport design risk. A
future real checkpoint can be constrained to header bytes only; it does not
need to download the 105,365,484-byte source member merely to determine
whether the claimed 96-channel representation is present.

The fixture is not EEG. Its channel names, sampling, and geometry were created
from the public contract, so recovering them is a parser test, not biological
evidence or an independent confirmation of the real file.

## Next Gate

After this exact implementation and result are committed, pushed, remotely
green, and proof-bound, prepare one all-false Tier C packet for the exact
subject-1/run-1 range-only real-header checkpoint. That packet cannot activate
itself. A fresh packet-bound maintainer decision and green decision commit are
required before any new manifest request, GDF byte, or real header read.

Engineering capability added: NeuroDecodeKit can now validate a complete GDF
2.x measurement header through a deterministic two-range, no-overread,
dependency-free interface with explicit channel-role and sampling checks.

Scientific claim not established: only generated header bytes were parsed, so
no real EEG, neural advantage, nuisance-controlled decoding, unseen-person
generalization, movement-intention, language, live, portable, or clinical
result was shown.
