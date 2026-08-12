# MARC-1 Source-Aware Inventory Attestation Preregistration

Date: 2026-08-12

Lane: `MARC1-SA1`

Status: **Frozen generated-only contract; no network, dataset-specific body,
private path, archive, payload, signal, target, model, or score is authorized**

Machine contract:
`registries/marc1_source_aware_inventory_attestation_contract.v0.json`

## Objective

Qualify one dependency-free source-aware attestor that can distinguish public
source schema, optional checksum provenance, target-free cohort identity, and
later payload integrity without exposing file rows.

This contract is eligible because research commit
`aa805038cc28c64ad75ddcb0e14768fdcb3cd96e` passed Base Python job
`94173234952` and Optional Neuro Readers job `94173234944` in CI
`31614330447` before this registration.

The implementation may begin only after this exact contract is committed,
pushed, and both required CI jobs are green.

## Non-Negotiable Boundary

The generated implementation must have:

```text
network client or URL opener:          absent
execute command:                       absent
dataset-specific response body:        absent
registered or consumed path:           absent
participant archive interface:         absent
payload reader:                         absent
signal or target interface:             absent
model, training, prediction, score:     absent
base dependency delta:                  0
```

Allowed commands are exactly `plan`, `qualify`, and `inspect`. The qualifier
must refuse any path reserved for a future live lane before statting or opening
it. All fixture bytes are generated in memory from constants frozen here.

## Frozen Source Schema

Every structurally eligible row requires the five documented public fields:

```text
id                  positive non-boolean integer, unique
name                safe NFC basename, unique
size                positive non-boolean integer
is_link_only        exact false boolean
download_url        exact https://ndownloader.figshare.com/files/{id}
```

The only known optional extension fields are `supplied_md5` and
`computed_md5`. Each present value must be lowercase 32-hex. When both are
present on a row, they must agree. Either or both may be absent without failing
the public-core schema.

Any other key blocks selection and routes the safe aggregate result to
`MARC1SA-R4`. Unknown values are never copied into the private manifest.
Target-like keys at any depth refuse before ordinary predicate evaluation.

## Frozen Historical Comparison

The historical identity remains a comparison vector, not a parser axiom:

```text
rows:                         55
participant archives:        45
supplementary rows:           10
participant grammar:         sub-01.zip through sub-45.zip exactly once
declared bytes:               3,683,416,050
sub-01 file ID:               62,570,743
sub-01 bytes:                 33,690,749
sub-01 MD5 when present:      6b01cf5bd30de0c670d2837d112a17fa
```

A mismatch does not mutate those values and does not become a parser failure.
It becomes `MARC1SA-R3` with an aggregate predicate vector and candidate hashes,
then stops before selection or payload.

## Six Generated Semantic Families

### A - Documented public core exact

Build the exact historical 55-row generated inventory with only the five
public core fields. Every historical predicate matches; MD5 availability is
zero. Expected route: `MARC1SA-R2`.

### B - Observed seven-field extension exact

Add valid agreeing `supplied_md5` and `computed_md5` to all 55 rows. Every
historical predicate matches. Expected route: `MARC1SA-R1`.

### C - Partial optional extension exact

Use this exact availability pattern over the same 55 rows:

```text
both MD5 fields:              18 rows
supplied_md5 only:            18 rows
computed_md5 only:             9 rows
neither field:                10 rows
supplied present total:       36 rows
computed present total:       27 rows
agreeing pairs:               18 rows
```

Every historical inventory predicate matches. Expected route:
`MARC1SA-R2`.

### D - One ordinary historical drift

Start from family B and add one byte to the last supplementary row. Structural,
core, optional-extension, participant, and anchor checks remain valid; only the
historical declared-byte predicate differs. Expected route: `MARC1SA-R3`.

### E - Multiple ordinary historical drifts

Start from family B, replace `sub-45.zip` with a safe supplementary basename,
and change its size. Row count remains 55 while participant count,
supplementary count, participant-name identity, and declared-byte total differ.
The vector must report every mismatch in one pass. Expected route:
`MARC1SA-R3`.

### F - Unknown non-target extension

Start from family B and add one generated `storage_location` field to one row.
The attestor records one unknown-field row and one row-shape hash, retains no
unknown value, blocks selection, and routes `MARC1SA-R4`.

## Determinism

For families A through E, reversing row order and reversing JSON object-key
order must preserve every semantic hash, predicate, route, and private/public
output hash. Family F must preserve the aggregate unknown-key count and key-set
hash under the same reorderings.

The raw transport-body hash may differ under serialization reorder. It is
provenance only and is excluded from semantic replay equality.

## Predicate Vector

The public vector contains exactly these 21 fields:

```text
public_core_fields_present_all
known_optional_MD5_keysets_only
unknown_extra_field_rows
row_count
unique_ID_count
unique_name_count
safe_filename_count
valid_downloader_URL_count
non_link_only_count
participant_archive_count
supplementary_row_count
declared_byte_total
historical_row_count_matches
historical_participant_count_matches
historical_supplementary_count_matches
historical_declared_bytes_match
historical_sub01_anchor_matches
supplied_MD5_present_count
computed_MD5_present_count
MD5_pair_agreement_count
target_like_field_count
```

After structural and target-firewall safety passes, ordinary historical
mismatches never short-circuit this vector.

## Seven Domain-Separated Hashes

The implementation must use these exact domains:

```text
transport_body_sha256       neurodecodekit:MARC1-SA1:transport-body:v0
public_core_sha256          neurodecodekit:MARC1-SA1:public-core:v0
optional_extension_sha256   neurodecodekit:MARC1-SA1:optional-extension:v0
row_shape_sha256            neurodecodekit:MARC1-SA1:row-shape:v0
classification_sha256       neurodecodekit:MARC1-SA1:classification:v0
selection_sha256            neurodecodekit:MARC1-SA1:selection:v0
predicate_vector_sha256     neurodecodekit:MARC1-SA1:predicate-vector:v0
```

No empty placeholder may substitute for an unavailable layer. An unavailable
selection hash is JSON `null` with an explicit reason.

## Private And Public Outputs

The generated qualifier may create exactly two files in one newly created,
nonregistered directory:

```text
marc1_source_aware_inventory.private.v0.json   mode 0600
marc1_source_aware_inventory_result.v0.json    mode 0600
```

Both writes are exclusive and no-follow through a held parent capability. The
private file contains allowlisted public-core rows, optional MD5 values when
present, private classification, private selection when eligible, and hashes.
It contains no unknown-field value.

The public file contains only aggregate predicates, counts, hashes, route,
resources, access counters, warnings, unavailable fields, and claim boundary.
It must contain no filename, file ID, URL, checksum, row, or participant-level
outcome. `inspect` accepts only the public basename. The qualifier inspects it
once and removes both files plus the created directory exactly.

## Exact Refusal Matrix

The generated qualifier must pass all 52 named refusals:

### Proof And Boundary - 6

```text
research_commit_drift
research_registry_drift
contract_registry_drift
consumed_result_binding_drift
consumed_executor_import
URL_opener_or_execute_surface
```

### JSON And Target Firewall - 10

```text
malformed_UTF8
malformed_JSON
duplicate_JSON_key
nonfinite_JSON_constant
non_list_root
non_object_row
target_key_direct
target_key_nested_object
target_key_nested_list
target_key_normalized_variant
```

### Core Fields And Types - 12

```text
missing_id
missing_name
missing_size
missing_is_link_only
missing_download_url
boolean_id
zero_id
boolean_size
zero_size
non_boolean_link_state
link_only_true
name_non_string
```

### Filename And Identity - 10

```text
empty_name
dot_name
parent_name
slash_name
backslash_name
NUL_name
non_NFC_name
control_character_name
duplicate_file_ID
duplicate_filename
```

### URL And MD5 - 8

```text
HTTP_download_URL
wrong_download_host
download_path_ID_mismatch
download_URL_query
download_URL_fragment
malformed_supplied_MD5
malformed_computed_MD5
MD5_pair_disagreement
```

### Output And Resources - 6

```text
symlink_output_parent
existing_output_directory
combined_output_cap
runtime_cap
peak_RSS_cap
thread_environment_mismatch
```

Each refusal must map to one of `MARC1SA-F00` through `MARC1SA-F04`, produce no
partial public acceptance result, and leave no temporary artifact.

## Acceptance Gates

All 25 gates must pass in one generated qualification:

1. green research identity is exact;
2. implementation is standard-library only;
3. network and URL-opener surfaces are absent;
4. command surface is exactly `plan`, `qualify`, `inspect`;
5. all six semantic families reach their registered routes;
6. the predicate vector has exactly 21 fields;
7. every safe predicate is evaluated after the structural gate;
8. the five-field documented core passes;
9. the seven-field observed extension passes;
10. partial optional MD5 availability passes as `R2`;
11. unknown values are excluded and selection is blocked as `R4`;
12. nested target-like keys refuse;
13. single-drift localization is exact;
14. multi-drift localization reports every mismatch;
15. row and key reorder preserve semantic identity;
16. all seven hash domains are exact and distinct;
17. private and public schemas are disjoint;
18. public output contains no protected row field or value;
19. raw response bytes are never persisted;
20. writes are exclusive, no-follow, and parent-relative;
21. public inspection occurs exactly once;
22. exact cleanup removes both files and the directory;
23. all 52 refusals pass;
24. runtime, RSS, input, output, and thread caps pass; and
25. every real, private, payload, neural, target, model, score, retry, and claim
    counter remains zero.

## Resource Caps

```text
CPU threads / workers / jobs:     1 / 1 / 1
runtime:                           30 seconds
peak RSS:                          268,435,456 bytes
generated input:                   2,097,152 bytes
combined output:                   2,097,152 bytes
incremental disk:                  4,194,304 bytes
base dependency delta:             0
network bytes:                     0
payload bytes:                     0
```

## Next Gate

Commit, push, and require both CI jobs green for this exact contract. Then
implement and qualify only the generated interface. Commit, push, and green
that implementation before one measured generated closeout.

A future public request still needs a new all-false Tier C packet, a fresh
packet-bound maintainer decision, and a separately green wrapper. This
preregistration cannot contact Figshare or open a payload.

## Claim Boundary

Engineering capability proposed: a deterministic source-aware attestor can
localize safe metadata drift through aggregate predicates while separating
source identity, cohort identity, and later acquired-byte integrity.

Scientific claim not established: this contract accesses no real metadata,
neural payload, signal, target, model, prediction, or score and adds no neural,
language-decoding, or thought-to-text evidence.
