# MARC1-CD1A Live Archive Inventory Result

Date: 2026-08-11

Status: **Passed `MARC1CD-R1`; the one live invocation is consumed with no
retry or rerun**

Machine result:
`registries/marc1_freewill_central_directory_live_result.v0.json`

Private outputs, retained only under Git-ignored
`.codex_work/marc1_central_directory/live_audit_v0/`:

- `execution_consumed.v0.json`
- `member_inventory.private.v0.json`

## Result In One Line

NeuroDecodeKit inventoried the current 13,591,548,048-byte public Freewill ZIP
from 306,758 bytes of bounded metadata responses, without downloading the ZIP
or opening any member.

## Proof Order

The registered execution began only after exact wrapper commit
`5dfa3c4c8cd7f0e990b7b1db7b35c4df8694171f` passed Base Python job
`93879378282` and Optional Neuro Readers job `93879378362` in CI
`31521510374`.

The executor then verified:

```text
implementation registry SHA-256:
b0e2c0fe20a20b142fa53c387ffd4fe467aff9898ecd1ab1eadc3a441f8405b0

exact clean HEAD:                    pass
green decision ancestor:             pass
five numerical thread values = 1:   pass
free disk:                            23,095,480,320 bytes
logical CPUs:                         12
one-minute load:                      8.443359375
load per logical CPU:                0.70361328125
pre-consumption peak RSS:             32,833,536 bytes
prior private root:                   absent
prior public result:                  absent
```

The private consumed marker was written before the first HTTP request. This
lane cannot be retried or rerun.

## Transport Result

```text
HTTP attempts:                        4 / 5 cap
metadata requests / body bytes:       1 / 304
tail attempts / body bytes:           2 / 131,072
directory requests / body bytes:      1 / 175,382
accepted response bodies:             3
accepted response-body bytes:         306,758 / 17,039,360 cap
bodyless HTTPS redirects:             1 / 2 cap
redirect DNS checks:                  1
HEAD requests:                        0
retries / reruns:                     0 / 0
whole-archive downloads:              0
member local-header requests:         0
member payload requests / bytes:      0 / 0
```

The metadata body matched the frozen record, version, file ID, name, size,
download URL, supplied MD5, and computed MD5 identity. The tail response
matched the exact final 131,072-byte range and virtual archive total. The
directory response matched the exact range derived from the in-tail ZIP64
record and used the same terminal URL without redirect.

Raw response bodies were discarded after in-memory parsing. The aggregate
result retains only three body SHA-256 values and availability booleans for
ETag and Last-Modified. It publishes no response body, raw header value,
terminal URL, redirect URL, member name, member offset, or member row.

## Archive Inventory

```text
declared virtual archive bytes:       13,591,548,048
central-directory bytes:              175,382
archive comment bytes:                0
entries:                              1,227
regular files:                        1,025
directories:                          202
stored entries, method 0:             202
deflated entries, method 8:           1,025
entries using ZIP64 extra fields:     796
aggregate compressed member bytes:    13,591,200,154
aggregate uncompressed member bytes:  17,362,624,734
whole archive materialized bytes:     0
```

The parser passed every frozen EOCD, ZIP64, entry-count, directory-size,
compression, flag, file-kind, path-safety, duplicate-name, extra-field, and
overlap gate. Exact member names, local-header offsets, CRC values, sizes, and
flags exist only in the private mode-`0600` manifest.

This result does not verify the registered whole-archive MD5. It also does not
verify member CRCs, local headers, decompression, or payload integrity because
none of those bytes were requested.

## Resource And Output Result

```text
executor runtime:                     2.7274372498504817 sec
reported peak RSS:                    43,974,656 bytes
external wall time:                   2.95 sec
external maximum RSS:                 45,301,760 bytes
public result bytes:                  6,118
private manifest bytes:               418,755
combined report + manifest bytes:     424,873
consumed marker bytes:                450
incremental disk bytes:               425,323
CPU threads / workers / jobs:         1 / 1 / 1
```

Public result SHA-256:
`fee969818b4e3e2ef7aee86096ad676c9bd70f80d19f2fd6dbe0e8069175257b`

Private manifest SHA-256:
`2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031`

Consumed marker SHA-256:
`421cec0380b23d87d78aadf97adea20625af39e874b15d39cadd844b672087c1`

All 14 acceptance gates passed. The result stayed below the 120-second,
256-MiB RSS, 32-MiB incremental-disk, 1-MiB public-output, and 8-MiB combined-
output caps.

## Zero Counters

```text
whole archive / local header / member bytes:    0 / 0 / 0
local archive or data path operations:          0
participant selections / acquisitions:          0 / 0
signal / channel-event / target reads:           0 / 0 / 0
derivative or feature operations:                0
training / inference / prediction sets:          0 / 0 / 0
prediction freezes / target deliveries / scores: 0 / 0 / 0
dependency installs / provider-model calls:      0 / 0
stream-device-hardware / release operations:     0 / 0
retries-reruns / post-result updates:             0 / 0
scientific claim upgrades:                       0
end-to-end neural latency measured:              false
```

## What This Unlocks

The repository now has a private, integrity-bound map of the public archive
that can support a future prospective member-selection design without first
moving 13.59 GB. Any inspection, selection, or acquisition from that private
map is a separate real-data action and remains closed until a new frozen scope
and decision make the exact member-level boundary explicit.

MARC1-CD1A itself is complete and consumed. It cannot be amended into member
access, participant selection, signal reading, training, scoring, or a rerun.

## Claim Boundary

Engineering capability added: NeuroDecodeKit can safely inventory the current
13.59 GB public Freewill ZIP from 306,758 bounded metadata bytes without
downloading the archive or opening a member.

Scientific claim not established: archive metadata contain no neural signal,
event, target, model prediction, or score, so this result establishes no
neural effect or decoding capability.
