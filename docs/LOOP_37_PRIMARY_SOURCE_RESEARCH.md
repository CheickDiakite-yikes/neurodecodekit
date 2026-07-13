# Loop 37 Primary-Source Research: BIDS Derivative And Provenance Export

**Status:** planning research complete; experiment `Not Started`

**Prepared:** 2026-07-12

**Machine boundary:** `registries/loop37_research_boundary.v0.json`

## Decision Summary

Loop 37 should eventually build a tiny, target-free, synthetic
**BIDS-organized derivative interface** around NeuroDecodeKit artifacts. It
must not call NeuroToken NPZ caches, split reports, or report cards standard
BIDS derivative data types. The first 20 fixture families, six export layers,
five artifact profiles, 15 standard-field mappings,
16 explicit NeuroDecodeKit extension fields, 24 acceptance gates, 32 refusals,
four separately authorized stages, and 29 false authorization fields are now
frozen as planning research.

No fixture, exporter, derivative tree, validator install, validator run,
protected payload, target, raw copy, upload, release, model, training run,
stream, device, or hardware operation was opened. All execution flags remain
false.

## Why The Wording Matters

The [BIDS Derivatives specification](https://bids-specification.readthedocs.io/en/stable/derivatives/introduction.html)
defines derivatives as outputs of processing that remain understandable and
reusable. It also says transformed derivative files must not use a filename
that could be a valid raw filename unless the file is an identical raw copy.
Source entities must remain in the derivative name when they are still
relevant, and `desc-<label>` should distinguish variants.

NeuroDecodeKit's `.npz` caches and JSON report contracts do not have stable
BIDS derivative suffixes. BIDS permits additional and non-compliant derivative
files, but their presence inside a `derivatives/` directory does not make them
standard. The honest interface therefore has two layers:

1. a standard BIDS dataset envelope and standard metadata where the mapping is
   exact;
2. explicitly non-standard, versioned NeuroDecodeKit payloads and provenance
   files inside that envelope.

The strongest future synthetic wording is **validator-assessed BIDS envelope
with explicitly non-standard NeuroDecodeKit payloads**. `BIDS-certified`,
`BIDS-compliant NeuroToken derivative`, and `shareable neural dataset` are not
available claims.

## Stable BIDS 1.11.1 Requirements

The current stable
[`dataset_description.json` specification](https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/dataset-description.html)
requires `Name` and `BIDSVersion` for every dataset. A derivative dataset must
have `dataset_description.json` at its root and must include `GeneratedBy`.
`DatasetType: "derivative"` makes the interpretation explicit. The pipeline
name should match the derivative directory when nested under a source dataset.

The first future envelope should pin:

- `BIDSVersion: "1.11.1"`;
- `DatasetType: "derivative"`;
- `GeneratedBy[0].Name: "neurodecodekit"`;
- the exact NeuroDecodeKit version and code URL;
- a UTF-8 root `README` that names every non-standard file and unavailable
  claim;
- truthful `SourceDatasets` entries only when a URL, DOI, and/or version is
  actually known.

Unknown source locations, versions, licenses, or pipeline versions stay
unavailable. The exporter may not invent a DOI, public URL, BIDS version,
container, or source dataset identity.

## File-Level Provenance

The stable
[common derivative metadata specification](https://bids-specification.readthedocs.io/en/stable/derivatives/common-data-types.html)
recommends a `Description` and defines `Sources` as the directly used input
files expressed with BIDS URIs. Relative paths in `Sources` and the older
`RawSources` field are deprecated. Named datasets in BIDS URIs require matching
`DatasetLinks` entries in `dataset_description.json`.

This creates a strict fork:

- if a source is a resolvable BIDS dataset, use a BIDS URI and bind its dataset
  name through `DatasetLinks`;
- if a local cache or legacy source has no truthful BIDS URI, omit standard
  `Sources`, preserve an opaque source hash in the explicitly non-standard
  NeuroDecodeKit provenance record, and emit an unavailable warning.

An absolute local path, macOS home directory, username, OneDrive path, drive
letter, or `file://` URI is not a portable source identity and may expose
private information. It must never be exported by default.

## Metadata Propagation Is Conditional

BIDS says required metadata from source files must move forward when it remains
valid after processing. It does not permit copying a field merely because it
exists upstream. Signal units, sampling rate, reference, coordinate frame,
channel identities, timing, and task entities each need a semantic validity
decision after the transformation.

Loop 36 already established the necessary firewall: unit conversion,
rereference, compensation, interpolation, and geometry mapping are operators,
not hidden identity. Loop 37 records their status and provenance; it does not
perform them. Unknown or invalidated standard fields are omitted and surfaced
as unavailable in the NeuroDecodeKit extension record.

## Standard And Non-Standard Field Separation

Standard BIDS fields stay in standard files:

- dataset `Name`, `BIDSVersion`, `DatasetType`, `GeneratedBy`,
  `SourceDatasets`, and `DatasetLinks`;
- root `README`;
- file-level `Description` and resolvable `Sources`;
- relevant source entities, `desc`, and still-valid required metadata.

The future non-standard NeuroDecodeKit provenance record carries:

- schema, artifact kind, and standardization status;
- source, split, configuration, payload, code, manifest, and bundle hashes;
- item, subject, session, trial, and split identity;
- shape, dtype, lengths, masks, and timestamps;
- modality, device, channel, geometry, reference, transform, and missingness;
- causal context, latency status, resources, and access counters;
- warnings, unavailable fields, and exact claim boundaries.

These fields must be versioned under one explicit NeuroDecodeKit object or
separate non-standard provenance file. They must not masquerade as stable BIDS
keys. Proposed provenance fields from development branches or BIDS Extension
Proposals are research inputs, not stable 1.11.1 guarantees.

## Current Repository Audit

The tracked-file inventory contains zero neural or model binary candidate
files and zero bytes under extensions such as `.fif`, `.eeg`, `.vhdr`, `.edf`,
`.bdf`, `.set`, `.fdt`, `.mat`, `.npz`, `.npy`, `.pt`, `.pth`, or `.onnx`.
The tracked workbook is documentation, not a neural payload.

Current internal provenance is useful but not yet portable:

| Artifact | Strong current fields | Export blocker |
|---|---|---|
| NeuroTokenCache v0 | source/split/payload hashes, timing, masks, identities, modality, device, geometry availability, causality, resources, warnings | source cache and split report paths may be local; NPZ/neurotokens are non-standard BIDS payloads |
| Split Protocol v1 | source, protocol, assignment, and membership hashes | no share-qualified subject pseudonym or BIDS URI contract |
| Report Card v0 | config/source-report hashes, proof posture, resources, warnings | source/cache paths may be local; no BIDS derivative mapping |
| Signal/sentence caches | schema, shapes, channels, timing, source metadata | payloads may contain neural arrays or target-bearing members and need stage-specific allowlists |

No current artifact was opened for this audit. The findings come from source
code and committed aggregate documentation only.

## Future Tree Shape

A separately authorized synthetic Stage A may propose a tree like:

```text
neurodecodekit-v0/
  dataset_description.json
  README.md
  manifest.tsv
  manifest.json
  sub-synthetic01/
    ses-01/
      eeg/
        sub-synthetic01_ses-01_task-typing_desc-mock_neurotokens.npz
        sub-synthetic01_ses-01_task-typing_desc-mock_neurotokens.json
        sub-synthetic01_ses-01_task-typing_desc-mock_provenance.json
```

The example payload and `provenance` suffix are explicitly non-standard. The
exact filename and extension remain recommendations until preregistration and
validator experiments. The manifest files are also non-standard and must say
so. Their value is the explicit hash, byte, identity, and claim ledger.

## No-Raw-Copy Boundary

The future exporter must operate on an exact schema/stage allowlist. It may not
recursively copy a source tree. It must refuse:

- known raw recording extensions;
- raw-permissible filename collisions;
- full or sampled byte duplicates of raw sources;
- symlinks, hardlinks, shared inodes, aliases, and traversal;
- unknown payload types or suffixes;
- existing output trees unless the exact clean-root protocol allows them;
- target text, prompts, responses, sentence strings, or unrestricted free
  text;
- unknown or incompatible source and derivative licenses.

The raw-copy count, raw duplicate count, source/output inode overlap, input and
output bytes, file count, and complete manifest hash are acceptance metrics,
not optional diagnostics.

## Validator Boundary

The official
[BIDS Validator](https://github.com/bids-standard/bids-validator) assesses BIDS
compliance and currently publishes a command-line binary as
`bids-validator-deno`. Its repository identifies release `2.4.1` as current at
the time of this research. The
[BIDS examples repository](https://github.com/bids-standard/bids-examples)
provides lightweight datasets for validator tests.

NeuroDecodeKit must not add the validator to its zero-dependency base. A future
Stage B may pin one optional validator version, run it offline on the bounded
synthetic tree, preserve every warning/error, and report exact runtime and RSS.
The validator may ignore or warn about custom files. A zero-error envelope does
not standardize those files and does not verify source hashes, privacy,
license, scientific provenance, model behavior, or decoding accuracy.

## Four Separately Authorized Stages

1. **Stage A: synthetic metadata/refusal fixtures.** Dependency-free internal
   schema and path validation only. Maximum claim: synthetic structure and
   refusal identity.
2. **Stage B: synthetic payload and optional validator.** One bounded bundle,
   deterministic replay, and one pinned offline validator. Maximum claim:
   validator-assessed standard envelope with explicitly non-standard payloads.
3. **Stage C: named local real-derived metadata.** No raw copy and no signal or
   target read unless the exact packet permits it. Requires Loop 38 privacy,
   identifier, license, and lifecycle gates. Maximum claim: source-bound local
   provenance bundle.
4. **Stage D: public release.** Requires privacy, consent, license,
   cross-machine reproduction, contributor documentation, and Loop 44 claim
   review. Loop 37 alone cannot authorize it.

Authorization of one stage cannot authorize another. General continuation,
the user's storage envelope, or a passing prior loop is not authorization.

## Recommended Stage A Caps

| Resource | Frozen recommendation |
|---|---:|
| CPU threads/workers | `1 / 1` |
| Runtime | `120 sec` |
| Peak RSS | `1 GiB` |
| Generated derivative tree | `16 MiB` |
| Generated files | `128` |
| Network/download bytes | `0` |
| Raw-copy bytes | `0` |
| Base dependencies | `0` |

The current pass created zero fixtures and zero derivative bytes. It used seven
high-level public web research operations, including two official GitHub
repository reads. Exact public response bytes and browser runtime/RSS are
unavailable from the research tool.

## Acceptance And Stop Rule

Future Stage A passes only if all 24 gates and 32 refusal IDs remain exact,
every path is portable, every identity mapping roundtrips, every allowlisted
file is hashed, raw-copy counts remain zero, and the complete tree stays within
the cap. Stage B additionally needs deterministic replay across two clean roots
and a pinned offline validator issue ledger.

Any path, collision, provenance, source URI, metadata validity, raw-copy,
target leakage, hash, privacy, license, validator, resource, or claim failure
publishes `invalid`, `unavailable`, `non-standard`, or `blocked`. Do not repair
the output silently, weaken the gate, ignore validator issues, or rerun until a
passing variant appears.

## What This Proves Now

Engineering capability added: a machine-checkable BIDS-envelope mapping,
standard/non-standard field firewall, portable source-identity policy,
no-raw-copy audit design, staged validator protocol, and exact refusal surface
now exist.

Scientific claim not established: no fixture, exporter, derivative tree,
validator, protected payload, raw copy, target, model, training run, release,
device, or hardware was accessed, so there is no BIDS-compliant NeuroToken
result, shareable neural dataset, cross-machine reproduction, neural advantage,
decoding accuracy, unseen-person generalization, real-time behavior, or
portable-hardware result.

## Primary Sources

- [BIDS Derivatives 1.11.1](https://bids-specification.readthedocs.io/en/stable/derivatives/introduction.html)
- [BIDS dataset description 1.11.1](https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/dataset-description.html)
- [BIDS common derivative data and metadata 1.11.1](https://bids-specification.readthedocs.io/en/stable/derivatives/common-data-types.html)
- [BIDS common principles 1.11.1](https://bids-specification.readthedocs.io/en/stable/common-principles.html)
- [BIDS Extension Proposals](https://bids-specification.readthedocs.io/en/stable/extensions.html)
- [BIDS Validator](https://github.com/bids-standard/bids-validator)
- [BIDS examples](https://github.com/bids-standard/bids-examples)
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
