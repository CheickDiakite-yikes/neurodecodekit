# MARC-1 Privacy-Preserving Pilot Selection Live Implementation

Date: 2026-08-12
Lane: `MARC1-P1A`
Status: generated/mock wrapper qualified; real metadata remains closed until
this exact implementation commit passes both remote CI jobs

## Why This Is The Same Research Path

The project endpoint remains defensible non-invasive thought-to-text. MARC-1
does not replace that endpoint. It repairs a blocker exposed by the held-out
EEG positive control: low-frequency task information was real, but cue timing,
ocular activity, muscle activity, and movement could not be separated well
enough to call the effect brain-specific. A cleaner movement positive control
is therefore a required calibration rung before stronger language experiments
can be interpreted honestly.

This implementation does not perform that experiment. It provides the narrow,
target-free metadata bridge needed to bind a storage-safe two-axis pilot before
any payload is acquired.

## Green Authorization Basis

The all-false request became green first:

```text
request commit:          7f1ba0936e4e0266c0210648aa641feab63cd0eb
request CI:              31573969646
Base Python:             94041819046
Optional Neuro Readers:  94041819022
request SHA-256:         8eebf5f34294bc266e81552d31ff376cb81240d2ee18b2fc6857600fbd3aba85
```

The maintainer then supplied the fresh packet-bound message recorded verbatim
in the separate decision. The decision was committed and both jobs passed:

```text
decision commit:         9726d07ab08e9c2815dbe68398659f454693be5e
decision CI:             31574870204
Base Python:             94044627592
Optional Neuro Readers:  94044627647
decision SHA-256:        fb97887d332749bc50e1dcdc69418b7f63b631a166032e6823565442c5c3fb39
```

That decision authorizes this generated/mock implementation. It does not make
the private manifest or public endpoint available before this exact wrapper is
also committed, pushed, and green.

## Added Surface

The additive module is:

```text
src/neurodecodekit/datasets/marc1_pilot_selection_live.py
```

It imports only the Python standard library and the frozen generated selector.
It does not modify the green selector, add a dependency, expose a user-selected
path or URL, open an archive, parse an event, read a signal, or provide a model
or scorer.

The module CLI has four commands:

```text
python -m neurodecodekit.datasets.marc1_pilot_selection_live plan
python -m neurodecodekit.datasets.marc1_pilot_selection_live qualify --output-dir PATH
python -m neurodecodekit.datasets.marc1_pilot_selection_live inspect REPORT
python -m neurodecodekit.datasets.marc1_pilot_selection_live execute [green-proof fields]
```

`plan`, `qualify`, and `inspect` cannot select an alternate source. `execute`
has no source path, endpoint, credential, retry, fallback, payload, signal,
target, model, or score argument.

## Proof And Machine Gates

Before a real consumed marker can exist, the executor requires:

- the exact decision, request, contract, generated selector, generated result,
  and Freewill live-inventory result hashes;
- a clean exact `HEAD` equal to the operator-supplied wrapper commit;
- the green decision as a Git ancestor;
- the exact implementation-registry SHA-256 and all tracked source hashes;
- positive CI run, Base Python job, and Optional Neuro Readers job IDs;
- all five numerical-thread variables equal to `1`;
- at least `12,884,901,888` free bytes;
- one-minute load no greater than `1.0` per logical CPU; and
- pre-consumption peak RSS no greater than `268,435,456` bytes.

A machine failure occurs before the output root, consumed marker, private input,
DNS, or HTTP operation.

## Private Freewill Reader

The real route is fixed to the existing Git-ignored manifest:

```text
.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
```

The reader requires exactly:

```text
bytes:       418,755
mode:        0600
SHA-256:     2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
path checks: one no-follow validation
opens:       one content open
reads:       one cap-plus-one read
hashes:      one SHA-256 pass
parses:      one strict JSON parse
```

The descriptor identity must match the pre-open device and inode. The wrapper
then reuses the frozen selector's exact row, path, bundle, participant-rank,
session-split, and byte-cap logic. It never resolves, stats, opens, or hashes a
Freewill archive member or sibling.

## Frozen Wrist Parser

The only future endpoint is the unauthenticated Figshare v3 files list for
record `29666735`. The wrapper accepts exactly seven fields per row:

```text
id name size is_link_only download_url supplied_md5 computed_md5
```

The source-specific participant rule was frozen before a real request:

```text
sub-01.zip through sub-45.zip, exactly once each
```

Every participant URL must be exactly the Figshare downloader URL implied by
its integer file ID. Supplied and computed lowercase MD5 values must agree. The
known public `sub-01` anchor is fixed at file ID `62570743`, `33,690,749` bytes,
and MD5 `6b01cf5bd30de0c670d2837d112a17fa`. The remaining ten rows must be safe
supplementary basenames. The complete list must contain 55 rows totaling
exactly `3,683,416,050` declared bytes.

An extra target, label, class, condition, response, outcome, trial, event,
sentence, answer, or movement-direction field is refused. There is no fallback
name parser and no rule can change after a response is observed.

## Transport

The transport uses `urllib` with proxy discovery and automatic redirects
disabled. It sends only `GET`, `Accept: application/json`, identity encoding,
and a fixed user agent. It permits at most three HTTP attempts and two bodyless
HTTPS redirects. Redirect hosts must resolve through the injected resolver to
globally routable addresses. Redirect loops, credentials, non-HTTPS targets,
private addresses, duplicate critical headers, transfer encoding, compressed
content, a non-JSON terminal response, length disagreement, and cap-plus-one
overflow all refuse.

Exactly one terminal body may be accepted, with a maximum of `2,097,152`
bytes. Its observed byte count and SHA-256 are reported; raw headers, the URL,
and body are not published or persisted.

## Selection And Privacy

The selector preserves the preregistered cohorts:

```text
Freewill: sub-08 sub-10 sub-07 sub-22 sub-19 sub-16
          sub-14 sub-04 sub-05 sub-03 sub-09 sub-11

Wrist:    sub-08 sub-11 sub-09 sub-23 sub-20 sub-16
          sub-42 sub-38 sub-36 sub-30 sub-45 sub-21
```

Freewill session 1 and Wrist runs 1-6 are fit identities. Freewill session 2
and Wrist runs 7-8 are held out. Selection uses only source identity, lexical
participant identity, numeric session/run identity, completeness, and declared
bytes after selection. Signal quality, CRC, target, event, response, class,
movement direction, model output, and outcome cannot alter the cohort or split.

The private result contains 288 Freewill member rows and 12 Wrist archive rows.
It is mode `0600` under a new Git-ignored root. The public report contains only
preregistered participant IDs, aggregate counts and bytes, selection hashes,
resource measures, counters, warnings, unavailable fields, and claim bounds.
Names, file IDs, offsets, CRCs, raw URLs, raw headers, raw bodies, and local
paths are forbidden from the public result.

## One-Shot Semantics

For a future green real invocation, the order is fixed:

1. verify the exact green wrapper and machine gate;
2. refuse if the private execution root or public result already exists;
3. create a new mode-`0700` root and mode-`0600` consumed marker;
4. read the exact private manifest once;
5. accept at most one public Wrist body;
6. perform the target-free metadata selection;
7. write one private selection and one aggregate public result; and
8. stop.

Any post-marker failure emits one aggregate failure route where possible. The
marker remains. Retry, rerun, resume, restart, fallback, substitution,
overwrite, cleanup, and post-result parser amendment are unavailable.

## Generated Qualification

The final measured qualification used generated real-shape metadata, direct
and two-redirect mocked HTTP exchanges, reversed irrelevant row order for
replay, and 26 adversarial mutations spanning all five input/transport/privacy
failure classes.

```text
route:                              MARC1PSL-G1
generated input bytes:              866,578
aggregate report bytes:               8,044
private manifest bytes:             206,509
combined output bytes:              214,553
selected subjects per axis:              12
selected private rows:                  300
Freewill run bundles/core members:     72 / 288
Wrist selected archives:                    12
Freewill reserved bytes:             623,853,450
Wrist reserved bytes:                600,000,299
joint reserved bytes:              1,223,853,749
mutations refused:                         26 / 26
acceptance gates:                          15 / 15
internal runtime:                    0.1832679167855531 sec
reported peak RSS:                  50,905,088 bytes
external wall:                            0.36 sec
external maximum RSS:               50,987,008 bytes
real/network operation sum:                   0
```

Output identities:

```text
aggregate report SHA-256: 7d6ae39addfab24b74fbf7af2769d02acf92682b7985bbe94efd1db81a96538d
private manifest SHA-256: 70570ff568d54acee9fafd3d5df08498977c09fde82646b3689da3b567305f08
```

The disposable generated outputs were inspected once and removed. They are not
committed evidence and have no scientific value.

## Verification

The focused live-wrapper suite has 19 tests. It covers proof bindings, machine
ordering, exact no-follow reads, strict Figshare parsing, target-field refusal,
direct and redirect transport, malformed headers and bodies, all 26 required
mutations, deterministic replay, output caps and privacy, mocked one-shot
success, consumed failure, second-invocation refusal, aggregate inspection, CLI
planning, and the absence of heavy or payload-reading interfaces.

The implementation-record suite adds 12 immutable artifact and boundary tests.
Together, the two focused modules pass 31 tests in 0.881 seconds. The complete
MARC family passes 329 tests. The dependency-light suite passes 2,468 tests
with 204 expected skips in 20.570 seconds at 271,728,640-byte external peak
RSS. The optional-neuro suite passes 2,539 tests with 35 expected skips in
56.969 seconds at 765,165,568-byte external peak RSS. Both complete suites add
exactly 31 tests and zero skips over the green authorization-decision baseline.
The whole-suite RSS values include thousands of unrelated tests and optional
readers; the isolated wrapper measurement remains 50,987,008 bytes.

Ruff, compileall, strict parsing of every registry JSON document, CLI help,
one generated qualify/inspect roundtrip, and `git diff --check` also pass. No
generated output is tracked.

## Next Gate

No real input is available yet. This exact implementation must be committed,
pushed, and pass Base Python and Optional Neuro Readers CI. Only then may the
single registered MARC1-P1A metadata invocation read the sealed Freewill
manifest once and accept one Wrist metadata body. Passing that future metadata
gate would still require a new Tier C packet before any selected payload can be
acquired.

Engineering capability added: a proof-gated, target-free, storage-capped
selector can bind the exact two-axis pilot through bounded metadata without
opening a neural payload.

Scientific claim not established: this generated qualification contains no
human signal, target, prediction, or score and establishes no neural effect,
language decoding, or thought-to-text capability.
