# MARC-1 Freewill Central-Directory Range Research

Date: 2026-08-11

Status: **Tier A transport and archive-format research complete; no Figshare
metadata body, archive byte range, member payload, local real-data path, signal,
event, target, model, prediction, or score was accessed or authorized**

Registry:
`registries/marc1_freewill_central_directory_research.v0.json`

## Decision

Advance a separately named lane, **MARC1-CD1: Freewill Archive Metadata Range
Audit**, before selecting or acquiring any Freewill-23 participant payload.

The 13,591,548,048-byte archive is larger than the maintainer's whole-file
ceiling. The next useful fact is not another model score; it is the exact ZIP
member inventory needed to choose a scientifically adequate subset that fits
the storage budget. That inventory can be learned from the ZIP trailer and
central directory without downloading, extracting, or opening a member.

The future live audit must be fail-closed and conditional:

1. retrieve one bounded version-specific Figshare file-metadata response;
2. retrieve exactly the final 131,072 archive bytes with one HTTP byte range;
3. validate the classic EOCD, ZIP64 locator, and ZIP64 EOCD entirely inside
   that tail; and
4. only when the declared central directory is plain, in bounds, and no larger
   than 16 MiB, retrieve exactly that one directory range and parse it.

Any unsupported range behavior, identity drift, unresolved ZIP64 structure,
oversized directory, malformed member, or resource-cap breach parks the lane.
There is no fallback to a whole download and no retry.

## Evidence Anchor

MARC-1 generated qualification is complete and consumed at commit
`a5f3ff51583898bcd0de1ce10bd8967fc3d8da92`. CI run `31506699956`
passed both required jobs:

```text
Base Python:             93830009939
Optional Neuro Readers: 93830009975
```

That generated result established deterministic ZIP inventory and multimodal
firewall mechanics only. It made zero network requests and read zero real
archive, signal, event, or target bytes.

## Bound Source Identity

The audit is limited to the versioned Freewill-23 file already recorded by
MARC-1 research:

```text
repository:    Figshare
record ID:     28632599
version:       1
DOI:           10.6084/m9.figshare.28632599.v1
file ID:       57518986
file name:     Freewill_EEG_Reaching_Grasping.zip
file bytes:    13,591,548,048
file MD5:      3b7c3039c5c9fb6abf1429a830301711
license:       CC BY 4.0
```

The future metadata endpoint is fixed to:

```text
https://api.figshare.com/v2/articles/28632599/versions/1/files
```

The response must contain exactly one compatible row for file ID `57518986`.
Its name, size, supplied MD5, computed MD5, link-only state, and download URL
must reconcile with the bound identity. A changed version, missing checksum,
link-only file, extra selected row, query-bearing download URL, or non-HTTPS
download URL refuses before any archive request.

Figshare's official API guidance states that every record file has its own
`download_url`, and the public file presenter uses the
`https://ndownloader.figshare.com/files/{file_id}` form. The documentation does
not promise byte-range behavior. Range support therefore remains an observed
future gate, never an assumption.

Sources:

- [Figshare API guide](https://info.figshare.com/user-guide/how-to-use-the-figshare-api/)
- [Figshare public file presenter](https://docs.figshare.com/old_docs/api/presenters/file/)
- [Figshare article endpoints](https://docs.figshare.com/old_docs/api/articles/)

## HTTP Range Semantics

RFC 9110 permits a non-zero suffix range and defines `206 Partial Content` plus
`Content-Range` as the self-describing response to a successful range request.
It also warns that `Accept-Ranges: bytes` is advisory and cannot guarantee that
a later request will return partial content.

The audit therefore validates the terminal response itself. Every archive
response must have:

- status `206`;
- exactly one `Content-Range` in canonical `bytes START-END/TOTAL` form;
- `TOTAL == 13,591,548,048`;
- exact requested start and end positions;
- exact `Content-Length` equal to the returned range length;
- no multipart response;
- absent or identity `Content-Encoding`;
- no cookies, authorization, request body, or content negotiation; and
- a cap-plus-one body read that proves the response stopped at the expected
  byte count.

`ETag`, `Last-Modified`, `Accept-Ranges`, and redirect observations are inert
provenance. They cannot replace the version, file ID, size, and checksum
identity. An absent `Accept-Ranges` header does not fail a correct `206`, while
a `200` response always refuses before a body can exceed the cap.

Source: [RFC 9110, Range Requests](https://datatracker.ietf.org/doc/rfc9110/)

## ZIP And ZIP64 Structure

PKWARE APPNOTE 6.3.10 defines the archive order as member records followed by
the central directory, optional ZIP64 end records, and the classic end-of-
central-directory record. It defines:

- classic EOCD signature `0x06054b50`;
- ZIP64 EOCD signature `0x06064b50`;
- ZIP64 locator signature `0x07064b50`; and
- central-directory file-header signature `0x02014b50`.

Source: [PKWARE ZIP File Format Specification
6.3.10](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)

The future audit requests this fixed trailer interval:

```text
Range: bytes=13591416976-13591548047
length: 131,072 bytes
```

The fixed tail is deliberately larger than the 65,557-byte classic EOCD plus
maximum archive-comment envelope. The parser searches backward for exactly one
candidate whose declared comment length ends at archive byte
`13,591,548,048`. A signature embedded inside a comment or random bytes cannot
win.

For this archive size, the audit requires a valid ZIP64 locator immediately
before the classic EOCD and a complete ZIP64 EOCD record already inside the
same 128 KiB tail. The ZIP64 record must end exactly at the locator, describe
one disk, contain no unsupported extensible sector, and provide finite entry
count, central-directory size, and central-directory offset values. If the
record begins before the tail or declares extra bytes, the audit parks instead
of issuing another exploratory range.

The classic and ZIP64 values must agree wherever the classic fields are not
sentinels. Split, spanned, encrypted, compressed, or digitally signed central
directories are unsupported and refuse.

## Conditional Central-Directory Request

The central-directory request is eligible only when all trailer gates pass and
all of these predicates are true:

```text
0 < entry_count <= 250,000
0 < central_directory_size <= 16,777,216
0 <= central_directory_offset
central_directory_offset + central_directory_size <= ZIP64_EOCD_offset
central_directory_size / entry_count >= 46
```

The executor then makes exactly one inclusive range request:

```text
bytes=central_directory_offset-(central_directory_offset + size - 1)
```

No byte before or after that range may be returned. The parser consumes the
directory sequentially with `struct`, bounded slices, and strict field lengths.
It must consume the response exactly; trailing bytes, a digital-signature
record, a second archive, or an unrecognized signature refuses.

## Member Inventory Policy

Each central-directory entry keeps these private fields:

- decoded normalized member name;
- CRC-32;
- compression method and general-purpose flags;
- compressed and uncompressed size;
- relative local-header offset;
- version-made-by and external attributes;
- directory or regular-file kind; and
- ZIP64-extra-field use.

Member names decode as strict UTF-8 when bit 11 is set and strict CP437
otherwise. Names must be NFC-normalized POSIX-relative paths with no NUL,
control character, backslash, empty component, repeated separator, `.`, `..`,
absolute prefix, drive prefix, or duplicate after normalization.

The inventory permits safe regular files and explicit directory entries.
Directory entries must end in `/`, have zero compressed and uncompressed size,
and use stored compression. Symbolic links, devices, sockets, FIFOs, encrypted
entries, patched data, strong encryption, masked headers, unsupported methods,
and multi-disk offsets refuse.

ZIP64 extended-information field `0x0001` is parsed in the order required by
the sentinel fields. Missing, duplicated, truncated, surplus, or inconsistent
ZIP64 values refuse. Local headers and member payloads remain unopened, so the
future audit cannot independently verify member CRC-32 values or whole-archive
MD5. Those verification states must be explicitly `unavailable_not_read`.

## Private And Aggregate Outputs

The future audit writes two isolated artifacts:

1. a private manifest with exact member names and byte metadata; and
2. an aggregate report with only counts, byte totals, suffix/role summaries,
   structural hashes, transport measurements, warnings, and unavailable
   fields.

The aggregate report must not contain member names, local-header offsets,
download URLs, redirect URLs, query strings, response headers, or per-member
checksums. The private manifest is never accepted by the public `inspect`
command and must remain Git-ignored.

The aggregate inventory hash is computed over a canonical projection that
replaces member names with a domain-separated SHA-256 while preserving the
nonidentifying structural fields. A separate private-manifest hash binds the
exact inventory for later participant selection.

## Resource Envelope

The prospective live audit is intentionally tiny relative to the archive:

```text
metadata response:             <= 131,072 bytes
archive tail range:            exactly 131,072 bytes
central-directory range:       <= 16,777,216 bytes
total network response bytes:  <= 17,039,360 bytes
network requests:              <= 3
redirect responses:            <= 2, bodyless only
incremental disk:              <= 32 MiB
combined written output:       <= 8 MiB
aggregate public output:       <= 1 MiB
runtime:                       <= 120 seconds
peak RSS:                      <= 256 MiB
CPU threads/workers/jobs:      1/1/1
free disk before marker:       >= 12 GiB
retries/reruns:                0/0
```

The exact 17,039,360-byte network cap is the sum of the three allowed response
bodies. Redirect headers do not authorize redirect bodies. A future executor
must create its consumed marker only after machine, output, contract, and green-
proof preflights pass, but before its first public request.

## Prospective Router

1. `MARC1CD-F00`: contract, green proof, source identity, or license mismatch.
2. `MARC1CD-F01`: machine, output, consumed-marker, runtime, RSS, or cap failure.
3. `MARC1CD-F02`: metadata status, shape, field, URL, size, or checksum failure.
4. `MARC1CD-F03`: redirect, status, framing, encoding, range, or byte-count
   failure.
5. `MARC1CD-F04`: EOCD, ZIP64, disk, offset, size, or directory-bound failure.
6. `MARC1CD-F05`: central-entry, path, flag, method, kind, ZIP64-extra, or
   duplicate failure.
7. `MARC1CD-F06`: privacy, deterministic replay, hash, or output failure.
8. `MARC1CD-R1`: one exact archive inventory completed without member-content
   access.

`MARC1CD-R1` is an engineering and acquisition-planning result only. It makes
selected participant/member acquisition eligible for a new preregistration;
it does not authorize that acquisition.

## Ordered Next Steps

1. Commit and remotely qualify this Tier A research record.
2. Freeze a generated/mock-only preregistration anchored to the green research.
3. Implement a standard-library transport and structural ZIP64 parser with no
   live endpoint or execute mode.
4. Qualify fixed, redirect, short, overlong, `200`, multipart, malformed EOCD,
   malformed ZIP64, unsafe-member, privacy, and cap fixtures.
5. Commit, push, and require both CI jobs green.
6. Prepare one all-false Tier C packet for one conditional three-response live
   audit.
7. Only after a fresh packet-bound maintainer decision and green decision
   commit may the first Figshare response be requested.

## Claim Boundary

Engineering capability added by this research: NeuroDecodeKit now has a
standards-bound, 17,039,360-byte maximum plan for learning the exact inventory
of a 13.59 GB ZIP without downloading or opening member payloads.

Scientific claim not established: no real metadata body, archive range,
member, neural signal, event, target, model, prediction, or score was accessed,
so this design establishes no neural effect or decoding result.
