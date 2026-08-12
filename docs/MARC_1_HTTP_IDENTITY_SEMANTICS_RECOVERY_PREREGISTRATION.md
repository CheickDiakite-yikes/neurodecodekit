# MARC1-HT1 HTTP Identity Semantics Recovery Preregistration

Date: 2026-08-12

Status: **Frozen generated/mock contract; real inputs and execution remain
unauthorized**

Machine contract:
`registries/marc1_http_identity_semantics_recovery_contract.v0.json`

## Objective

Qualify one standards-aligned terminal `Content-Encoding` predicate without
reopening consumed MARC1-P1A or accessing any private/public live source.
This is a same-path transport repair, not a scientific pivot.

The only permitted semantic change is:

```text
absent Content-Encoding               -> accept as no content coding
one case-insensitive identity token   -> accept as compatibility tolerance
every other present value             -> refuse
```

The request-side preference remains `Accept-Encoding: identity`. No generated
or future real path may decompress or decode response content.

## Frozen Proof Anchors

This contract binds green artifact-only research commit
`f515b36cfdd2b297bcbba9885af92e59ead066a7`, Base Python job
`94062432262`, Optional Neuro Readers job `94062432241`, and CI
`31580575669`.

It also binds:

- research document SHA-256
  `6b93d476085771d6ab8c5a4f8a994e39733468d09780a07e7da1af4987949343`;
- research registry SHA-256
  `521beacac5f4629382ccab0f1a415efd0fab177a225101ad2474d5e65bc44610`;
- candidate policy SHA-256
  `ac1b98eed57af7e545b925f1529ebf38de72b4277ea54a473ae1d6f7fe0cd3a6`;
- consumed MARC1-P1A result SHA-256
  `3c526ac52f8185f3fe29b8f3843fd808cd9646b5011e9638d6bf55f5a459153a`;
- unchanged generated selector source SHA-256
  `072b9877bff0496ed10b10e4dbccc6751f357ec072390ce406342cc038359374`.

The actual MARC1-P1A live header remains unavailable and must not be inferred.

## Generated-Only Implementation Surface

Only a new additive module may be implemented after this exact contract is
committed, pushed, and both CI jobs are green:

`src/neurodecodekit/datasets/marc1_http_identity_semantics.py`

It may expose only:

- `plan`: print the frozen zero-access contract;
- `qualify`: run generated metadata and mocked-response qualification;
- `inspect`: validate an aggregate generated report.

It must not expose `execute`, accept a URL or local source path, import a
network opener, resolve DNS, inspect `.codex_work`, import or call the consumed
MARC1-P1A live executor, or create a persistent payload or real-selection
surface. Heavy dependencies and dependency changes are forbidden.

## Exact Generated Inputs

The one future generated closeout uses only locally constructed data:

- one 1,227-row Freewill-style central-directory inventory;
- one 55-row Wrist-style metadata list;
- the existing DOI-bound 12+12 participant ranks;
- 72 Freewill run bundles, 288 Freewill core members, and 12 Wrist archives;
- one 300-row generated private selection manifest;
- four accepted mocked terminal response variants;
- twenty rejected mocked terminal response variants.

No generated row may be selected using target, label, response, sentence,
event count, quality, CRC, size, or outcome information.

## Accepted Response Matrix

The implementation must accept exactly these four forms:

1. `Content-Encoding` absent.
2. `Content-Encoding: identity`.
3. `Content-Encoding: IDENTITY`.
4. `Content-Encoding: IdEnTiTy`.

Each accepted form must produce the exact same canonical Wrist metadata hash,
12+12 cohort identities, split identities, private selection hash, and public
aggregate selection hash. Row-order reversal must also replay exactly.

## Refusal Matrix

The implementation must refuse all twenty named mutations:

1. present empty `Content-Encoding`;
2. whitespace-only `Content-Encoding`;
3. `gzip`;
4. `br`;
5. `deflate`;
6. `compress`;
7. unknown coding token;
8. `identity, gzip` list;
9. parameterized identity;
10. duplicate `Content-Encoding` fields;
11. any `Transfer-Encoding`;
12. non-JSON `Content-Type`;
13. malformed `Content-Length`;
14. body overflow beyond 2 MiB;
15. automatic redirect evidence;
16. private or non-global redirect target;
17. alternate endpoint;
18. target-like public metadata field;
19. output-cap breach;
20. second invocation of the generated closeout.

Failures route into five non-overlapping classes:

```text
MARC1HT-F01  proof or contract identity
MARC1HT-F02  content-encoding semantics
MARC1HT-F03  unchanged HTTP envelope or source schema
MARC1HT-F04  resource, output, privacy, or replay boundary
MARC1HT-F05  forbidden operation or second invocation
```

## Unchanged Boundaries

The generated module must preserve the exact record/version/endpoint and
seven-field Wrist schema as inert contract values, the `sub-01` anchor, the
target-field firewall, manual redirect rules, body cap, strict UTF-8/JSON,
selection ranks, split definitions, output privacy, and all payload/scientific
prohibitions.

Source inspection must prove the absence of:

- `urllib.request`, `socket`, `http.client`, `requests`, `aiohttp`, or another
  network client;
- `gzip`, `bz2`, `lzma`, Brotli, zlib decompression, or a decoder call;
- a real endpoint request, private source path, consumed root, `execute`
  subcommand, retry, rerun, resume, fallback, or substitution interface;
- signal, event, target, cache, training, inference, scoring, provider-model,
  stream, device, hardware, or release logic.

## Resource Contract

The one future generated closeout is limited to:

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
runtime:                                  30 seconds
peak RSS:                                 256 MiB
generated input:                          2 MiB
public output:                            1 MiB
private + public output:                  2 MiB
incremental disk:                         4 MiB
network bytes:                            0
real/private source bytes:                0
```

All generated outputs must be written into a new temporary directory, measured,
hash-bound in the aggregate report, inspected once, and removed. Nothing from
the qualification may be committed.

## Acceptance Gates

Constructed route `MARC1HT-G1` requires all sixteen gates:

1. green research proof identity;
2. exact contract identity;
3. exact candidate policy hash;
4. all four accepted forms pass;
5. all accepted forms have identical canonical body and selection hashes;
6. all twenty mutations refuse under the registered route classes;
7. row-order replay is exact;
8. exact 12+12 participant identities;
9. exact 72-bundle/288-member/12-archive selection;
10. exact split binding and zero fit/held-out overlap;
11. target-, quality-, size-, CRC-, and outcome-free selection;
12. private/public output separation;
13. source inspection finds no network, decoder, real-executor, or neural
    interface;
14. every real, payload, neural, target, model, score, and claim counter is
    zero;
15. resource and output caps pass;
16. deterministic aggregate and private output hashes replay.

`MARC1HT-G1` is generated engineering evidence only. It cannot establish that
the live source will pass, that the cohort is available, or that a neural
effect exists.

## Evidence Order

1. Commit and push this exact contract.
2. Require Base Python and Optional Neuro Readers green.
3. Implement and qualify only the additive generated/mock surface.
4. Commit and push that exact implementation and require both jobs green.
5. Run one measured generated closeout, commit its aggregate record, and require
   both jobs green.
6. Only then prepare one all-false Tier C request for a new live wrapper and
   one new metadata invocation.

No current or prior authorization opens step 6. The consumed MARC1-P1A private
root remains forbidden throughout.

## Verification

Eleven focused contract tests and all 360 MARC tests pass. The complete
dependency-light suite passes 2,499 tests with 204 expected skips in 20.636
seconds at 269,434,880-byte external peak RSS. The optional-neuro suite passes
2,570 tests with 35 expected skips in 56.988 seconds at 772,472,832-byte
external peak RSS. Both complete suites add exactly eleven tests and zero skips
over the green research baseline.

Ruff, compileall, strict parsing of every registry JSON document, bound-file
hash replay, canonical policy-hash replay, and `git diff --check` also pass.

## Claim Boundary

Engineering capability proposed: a deterministic generated harness can prove
that the repaired HTTP predicate accepts only uncoded representations while
leaving cohort selection and every safety boundary unchanged.

Scientific claim not established: this contract authorizes no real data,
neural signal, target, prediction, score, language decoding, or thought-to-text
claim.
