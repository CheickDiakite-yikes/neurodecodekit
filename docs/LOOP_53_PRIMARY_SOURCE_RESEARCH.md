# Loop 53 Primary-Source Research

Date: 2026-07-15

Status: **Research complete; acquisition preregistered; authorization pending**

Machine contract:
`registries/loop53_fresh_eeg_acquisition_contract.v0.json`

## Research Question

Can NeuroDecodeKit acquire one fresh, task-matched EEG bundle without turning a
download into an unregistered signal, target, or model experiment?

The answer is a staged design. Loop 53 acquires and verifies bytes only. Loop
54 may later inspect headers, markers, geometry, signal, and targets under its
own ordered authorization. Loop 55 may later fit and score a small EEG model
only after Loop 54 fixes the usable rows and claim ceiling.

This separation replaces the broader historical
`FRESH_EEG_BENCHMARK_S20_APPROVAL_PACKET.md` for future S20 work. That earlier
packet is retained as provenance, but it bundled acquisition, parsing, splitting,
training, and scoring into one decision. The Loop 53 contract does not.

## Why S20 And Why This Block

Loop 29 selected S20 session 2 block 2 from public repository metadata. It is a
complete task-matched EEG bundle with one BrainVision triplet and one companion
MAT log. At 96,090,264 bytes, it is much smaller than the approved 5 GB preferred
incremental envelope and does not justify acquiring another participant or
block merely because storage is available.

S7 is not a substitute. It is a consumed development cohort with a prior local
negative classifier result. S20 is reserved as fresh evidence and is not opened
for header, signal, target, split, model, or score work in this milestone.

## Public Source Verification

The contract binds the public Hugging Face dataset at one immutable revision:

```text
repository:       bcbl190626/SpanishBCBL
revision:         88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
last modified:    2026-06-29T11:56:46Z
public:           yes
gated:            no
disabled:         no
license metadata: cc-by-nc-4.0
```

Metadata was rechecked on 2026-07-15 through the pinned revision endpoint and
the exact paths-info endpoint. No repository payload was downloaded. No local
S20 path was listed, stated, hashed, or opened.

Selected source identities:

| Role | Repository path | Bytes | Frozen source identity |
|---|---|---:|---|
| Header | `EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr` | 11,705 | Git blob SHA-1 `9ab325a0f8523b675ecab1c97e16169143f1f341` |
| Signal | `EEG/EEG/020_DECOMEG_S2_11966_task2.eeg` | 95,782,400 | LFS SHA-256 `57664457ca2f2f47e6eed5d942beda68536812e607e735a7118ce4f91a623d65` |
| Markers | `EEG/EEG/020_DECOMEG_S2_11966_task2.vmrk` | 91,219 | Git blob SHA-1 `a06044503e415872a3c8a9a344e6d9a51d5d2a34` |
| Log | `EEG/logs/S20_session2_block2_list1.mat` | 204,940 | LFS SHA-256 `bdc6b8fa123b041b45f277f9cffb33d64bb3fd557d0facf0e969db5a222c0414` |
| **Total** | **4 exact files** | **96,090,264** | No wildcard or backup |

For the small Git files, a future authorized acquisition verifies the Git blob
OID over opaque bytes. For the LFS files, it verifies the LFS SHA-256 over
opaque bytes. Hashing is an identity check, not permission to decode text,
markers, samples, or MAT fields.

Primary sources:

- Dataset revision and card:
  https://huggingface.co/datasets/bcbl190626/SpanishBCBL
- Dataset metadata API:
  https://huggingface.co/api/datasets/bcbl190626/SpanishBCBL
- Brain2Qwerty v1 methods and EEG/MEG results:
  https://www.nature.com/articles/s41593-026-02303-2
- Official SpanishBCBL loader at the pinned Brain2Qwerty code revision:
  https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/studies/spanishbcbl.py
- CC BY-NC 4.0 license text:
  https://creativecommons.org/licenses/by-nc/4.0/

## What The Paper Establishes

The primary Brain2Qwerty study reports a prompted typing task with 20 EEG
participants and 15 MEG participants. Its EEG acquisition used a 64-channel
BrainVision setup at 1 kHz, including ocular channels, and reported materially
higher character error for EEG than MEG.

Those cohort-level facts justify studying the accessible modality. They do not
pre-qualify S20, prove this block is readable, establish its channel/reference
geometry, or predict a local S20 model result. Those fields remain unavailable
until a separately authorized Loop 54 pass.

## Acquisition-Only Boundary

A future authorized Loop 53 execution may:

1. reverify the pinned public metadata;
2. confirm at least 2 GiB free disk and a new isolated destination;
3. download exactly the four named files once;
4. verify sizes and source identities through opaque sequential hashes;
5. promote only a complete verified bundle;
6. emit a manifest and human receipt under 1 MiB; and
7. clean up only temporary files created by that invocation.

It may not decode or parse `.vhdr`, `.vmrk`, `.eeg`, or `.mat`; inspect signal,
targets, channels, events, or trials; create a cache or split; run a model; train;
score; substitute another file or participant; or rerun.

The destination must be new. A collision, symlink, incomplete bundle, metadata
mismatch, hash mismatch, cap breach, or unauthorized read parks the gate without
overwriting or deleting preexisting data.

## Resource Envelope

```text
expected final payload:             96,090,264 bytes
maximum network payload:           134,217,728 bytes
maximum incremental disk peak:     268,435,456 bytes
minimum free disk before start:  2,147,483,648 bytes
maximum receipt output:              1,048,576 bytes
maximum wall time:                         600 seconds
maximum peak RSS:                   536,870,912 bytes
CPU threads / workers:                       1 / 1
download invocations:                         1
```

The 256 MiB disk cap accommodates one temporary copy plus the final 96 MB
bundle without approaching the user's broader 5 GB preferred allowance. The
implementation must measure actual network bytes, disk peak, runtime, RSS, and
every access counter. It must not infer missing measurements.

## Measured Research Boundary

```text
public metadata API operations:              4
remote payload bytes read:                   0
payload download invocations:                0
local S20 path stats or payload hashes:      0
header / marker / signal / MAT reads:         0 / 0 / 0 / 0
target or label reads:                       0
cache / split operations:                    0 / 0
model inference / training / scoring runs:   0 / 0 / 0
device or hardware operations:               0
generated experiment bytes:                  0
```

Process-level runtime and peak RSS for the external metadata research are not
available from the API tool and are not estimated. The future registered
executor must measure both.

## Proof Boundary

Proven now: the prospective contract names one public revision, four exact
files, exact source identities, a 96,090,264-byte total, a CC BY-NC 4.0
metadata boundary, and fail-closed resource/access rules.

Not proven now: no S20 payload was acquired or opened, so there is no evidence
about file readability, channels, geometry, reference, events, trials, signal
quality, targets, neural advantage, decoding accuracy, generalization, latency,
portable hardware, at-home use, or clinical utility.

Even a clean Loop 53 execution would prove acquisition mechanics only. It
would not be a scientific performance result.
