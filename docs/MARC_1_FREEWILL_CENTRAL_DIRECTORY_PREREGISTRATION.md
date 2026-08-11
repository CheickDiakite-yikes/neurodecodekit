# MARC-1 Freewill Central-Directory Preregistration

Date: 2026-08-11

Status: **generated/mock-only contract frozen; implementation not started;
all live metadata, HTTP archive, local real-data, member payload, signal, event,
target, model, score, and claim operations unauthorized**

Contract:
`registries/marc1_freewill_central_directory_contract.v0.json`

## Purpose

Qualify the exact transport and ZIP64 parser needed for one future MARC1-CD1
metadata audit without making a network request or allocating a 13.59 GB
archive.

The generated implementation must prove that it can:

1. validate the bound version-specific Figshare file row;
2. validate exact single-part HTTP range framing through a mocked transport;
3. recover EOCD and ZIP64 central-directory bounds from a 128-KiB generated
   tail representing the bound 13,591,548,048-byte archive;
4. parse one generated central directory without local headers or member
   content;
5. separate a private exact-member manifest from aggregate output; and
6. fail closed under identity, transport, archive, member, privacy, and resource
   mutations.

Generated success is engineering evidence only. It cannot authorize or
substitute for the later live audit.

## Green Research Anchor

Research commit `93faf368ed01dda418b836e794ba354d8f180794` passed CI run
`31507965329`:

```text
Base Python:             93834276391
Optional Neuro Readers: 93834276150
```

Implementation may begin only after this exact contract is committed, pushed,
and both required CI jobs are green.

## Interface

The future dependency-free module is fixed at:

```text
python -m neurodecodekit.datasets.marc1_central_directory_audit plan
python -m neurodecodekit.datasets.marc1_central_directory_audit qualify --output-dir PATH
python -m neurodecodekit.datasets.marc1_central_directory_audit inspect REPORT
```

It must expose no `execute`, URL, host, header, archive path, participant,
member, target, model, provider, network, or credential option. `qualify` may
read only the committed contract and generated in-memory fixtures. `inspect`
accepts only an aggregate generated report.

## Generated Virtual Archive

The qualification represents the exact bound archive length
`13,591,548,048` without allocating it. A deterministic fixture builder emits
only:

- one version-files metadata JSON body;
- one 131,072-byte final-tail body;
- one generated central-directory body; and
- inert response metadata needed by the mock transport.

The valid central directory has exactly 18 entries:

- four safe directory entries;
- fourteen safe regular-file entries;
- two generated participant prefixes;
- stored and deflated methods;
- one UTF-8 flagged member;
- one regular member whose 32-bit size and local-offset fields use ZIP64
  sentinels plus a valid `0x0001` extended-information field; and
- no encrypted, patched, masked, split, symlink, device, socket, or FIFO entry.

The generated central directory remains below 1 MiB. Its fictional local-header
offsets and compressed sizes are nonoverlapping and entirely before the
central-directory offset, but no local header or member payload byte exists in
the fixture.

The tail includes one classic EOCD with a nonempty comment, one ZIP64 locator,
and one fixed-size ZIP64 EOCD. The classic EOCD uses the appropriate sentinel
fields and ends exactly at virtual archive byte `13,591,548,048`. A decoy EOCD
signature appears inside the comment so the parser must use structural end-
position validation rather than the first or last raw signature alone.

## Mock Transport Contract

Transport is dependency-free and injected. The module contains no real opener.
Mock responses expose status, final URL, headers, and a read-limited byte
stream. The valid path consists of:

1. one `200` metadata JSON response at the exact version-files endpoint;
2. zero, one, or two bodyless HTTPS redirects from the exact ndownloader URL;
3. one terminal `206` final-tail response; and
4. one terminal `206` central-directory response.

Response bodies remain exactly three; redirects have zero body bytes. Every
redirect is handled manually. The initial URL is fixed and not user supplied.
A redirect refuses unless it is HTTPS, has no user information or fragment,
uses port 443 or no explicit port, resolves only to globally routable addresses
under an injected generated resolver, and stays within the two-hop limit.

Each range request carries exact `Range` and `Accept-Encoding: identity`
headers and no authorization, cookie, body, or referrer. The terminal response
must be nonmultipart `206` with exact `Content-Range`, exact `Content-Length`,
and absent or identity `Content-Encoding`. A cap-plus-one read must prove exact
body termination. `Accept-Ranges`, `ETag`, and `Last-Modified` are recorded as
inert availability/provenance states only.

The mock transport records requests, redirect count, body read calls, returned
bytes, and cap-plus-one probes. It refuses an unexpected method, URL, request
header, request order, or additional request.

## Structural Trailer Parser

Use only `struct`, bounded byte slices, strict integer checks, and standard-
library codecs. Do not call `zipfile.ZipFile` because the real design never has
a full seekable archive.

The parser must:

- find EOCD candidates backward;
- accept exactly one candidate whose comment ends at the virtual archive end;
- require the ZIP64 locator immediately before that EOCD;
- require the ZIP64 EOCD fully inside the tail and ending at the locator;
- require the fixed ZIP64 record size with no extensible sector;
- require one disk and consistent entry counts;
- reconcile every nonsentinel classic value with ZIP64;
- enforce `1..250,000` entries and `46..16,777,216` directory bytes;
- prove `offset + size <= ZIP64_EOCD_offset`; and
- derive one exact inclusive central-directory range before requesting it.

No additional ZIP64 probe is available. A missing or out-of-tail record
refuses.

## Structural Central-Directory Parser

Consume each `0x02014b50` entry sequentially. Fixed fields and variable-length
name, extra, and comment regions must fit exactly inside the response. The
parser must consume all bytes after exactly the declared entry count; trailing
records or bytes refuse.

Names decode with strict UTF-8 when general-purpose bit 11 is set and strict
CP437 otherwise. Every decoded name must be NFC-normalized and a safe POSIX-
relative path. Reject NUL/control characters, backslashes, absolute/drive
prefixes, empty/repeated components, `.` or `..`, and normalized duplicates.

Only stored method 0 and deflate method 8 are accepted. Encryption bit 0,
patched-data bit 5, strong-encryption bit 6, and masked-header bit 13 refuse.
Data-descriptor bit 3 may be inventoried because local headers and descriptors
are not opened. Every other unsupported flag refuses.

Classify entries from version-made-by and external attributes. Safe regular
files and explicit zero-size stored directory entries are allowed. Symlinks and
special files refuse. ZIP64 field `0x0001` must contain exactly the values
required by sentinel fields, in specification order, with no duplicate,
truncation, or surplus.

## Deterministic Outputs

Qualification writes exactly:

```text
marc1_central_directory_generated_report.v0.json
marc1_central_directory_generated_private_manifest.v0.json
```

The output directory must not exist, its parent must be a real non-symlink
directory, and creation must be atomic with no overwrite.

The private manifest contains exact generated names and structural fields. The
aggregate report contains no member name, local offset, download or redirect
URL, query, response header value, per-member CRC-32, or private-manifest body.
It may contain only aggregate counts/bytes, method and kind summaries,
domain-separated canonical hashes, transport/resource measurements, mutation
routes, warnings, unavailable fields, counters, and claim boundaries.

`inspect` must refuse the private manifest. Two independent generated replays
must produce byte-identical canonical reports after excluding runtime and RSS
measurements. Private-manifest hashes must match exactly.

## Frozen Mutations

Exactly 32 generated mutations are required:

```text
contract_or_artifact_hash_mismatch
metadata_status_or_JSON_shape
metadata_missing_or_duplicate_selected_row
metadata_name_size_or_MD5_drift
metadata_link_only_or_download_URL
redirect_loop_limit_or_order
redirect_body_or_unsafe_destination
unexpected_method_URL_header_or_extra_request
archive_status_200_416_or_multipart
archive_content_encoding_or_Content_Range
archive_Content_Length_short_or_overlong_body
tail_range_or_virtual_total_mismatch
EOCD_missing_truncated_or_comment_mismatch
EOCD_decoy_or_ambiguous_candidate
ZIP64_locator_missing_misplaced_or_truncated
ZIP64_record_outside_tail_or_wrong_end
ZIP64_record_size_or_extensible_sector
ZIP64_multidisk_or_classic_disagreement
central_directory_zero_entry_or_size_cap
central_directory_offset_overlap_or_bounds
central_directory_status_range_or_length
central_entry_signature_count_or_trailing_bytes
duplicate_normalized_member_name
unsafe_absolute_parent_or_separator_path
invalid_UTF8_CP437_NFC_or_control_name
encrypted_patched_strong_or_masked_entry
unsupported_compression_or_flag
symlink_device_socket_FIFO_or_kind
invalid_directory_entry
ZIP64_extra_missing_duplicate_truncated_or_surplus
aggregate_privacy_leak_or_private_inspect
output_symlink_overwrite_cap_or_replay_mismatch
```

Each mutation must refuse in its frozen route. The valid direct path and a
valid two-bodyless-redirect path must both pass, but only one aggregate
qualification artifact is emitted.

## Router

1. `MARC1CDG-F00`: contract, artifact, or green-proof failure.
2. `MARC1CDG-F01`: machine, output, runtime, RSS, or resource failure.
3. `MARC1CDG-F02`: metadata identity, shape, or download-URL failure.
4. `MARC1CDG-F03`: redirect, request, status, range, framing, encoding, or
   byte-count failure.
5. `MARC1CDG-F04`: EOCD, ZIP64, disk, offset, size, or directory-bound failure.
6. `MARC1CDG-F05`: central-entry, path, flag, method, kind, ZIP64-extra, or
   duplicate failure.
7. `MARC1CDG-F06`: privacy, deterministic replay, hash, or output failure.
8. `MARC1CDG-R1`: every generated direct, redirect, archive, member, privacy,
   mutation, and resource gate passes.

## Resource Caps

```text
CPU threads/workers/jobs:        1/1/1
runtime:                         <= 30 seconds
peak RSS:                        <= 256 MiB
generated fixture bytes:        <= 2 MiB
mock response body bytes/path:   <= 17,039,360
mock response bodies/path:       <= 3
mock redirect responses/path:    <= 2
mock requests/path:              <= 5
combined written output:         <= 1 MiB
network requests/bytes:          0/0
real archive/local-path bytes:   0
member/local-header reads:       0
signal/event/target/model/score: 0
```

The generated central directory is below 1 MiB, so the actual fixture remains
far below the prospective live cap. Cap mutations may use declared lengths and
bounded stream sentinels; they must not allocate cap-sized hostile bodies.

## Acceptance Gates

The generated closeout is eligible only if:

- exact metadata identity validates;
- valid direct and two-bodyless-redirect paths pass;
- exact tail and virtual total reconcile;
- decoy-resistant EOCD and complete ZIP64 parsing pass;
- one exact central-directory range is derived before its response is read;
- all 18 entries parse and classify correctly;
- no local header or member content exists or is requested;
- public/private output separation passes;
- all 32 mutations refuse in the intended route;
- deterministic replay and private-manifest hashes match;
- runtime, RSS, body, request, fixture, and output caps pass; and
- every live, real-data, signal, target, model, score, and claim counter is
  zero.

## Claim Boundary

Engineering capability added if successful: a dependency-free generated/mock
executor can validate exact HTTP range and ZIP64 central-directory mechanics
for a virtual 13.59 GB archive with zero member-content access.

Scientific claim not established even if successful: generated transport and
archive metadata contain no human neural signal, event, target, or model result
and establish no neural effect or decoding capability.
