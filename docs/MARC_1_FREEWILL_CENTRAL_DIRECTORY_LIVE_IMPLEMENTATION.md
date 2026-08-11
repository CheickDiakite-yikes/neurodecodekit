# MARC1-CD1A Live Archive Audit Implementation

Date: 2026-08-11

Status: **Generated/mock wrapper qualified; exact implementation must be
committed, pushed, and remotely green before one public request is eligible**

Machine record:
`registries/marc1_freewill_central_directory_live_implementation.v0.json`

Implementation:
`src/neurodecodekit/datasets/marc1_central_directory_live.py`

Focused tests:
`tests/test_marc1_freewill_central_directory_live.py`

## Gate Order

The wrapper was implemented only after packet-bound decision
`624cc4e99a4aa600b68a333c1bcd84e6cebb9dcd` passed Base Python job
`93871192638` and Optional Neuro Readers job `93871192713` in CI
`31519016891`.

This implementation does not make the public audit eligible by itself. The
exact source, tests, documentation, and registry must first be committed,
pushed, and pass both remote jobs. A future executor must bind that exact
wrapper commit, CI run, both job IDs, and implementation-registry SHA-256
before the pre-consumption machine gate or any public operation.

## Capability Added

The additive standard-library wrapper now provides:

1. Exact hash-bound loading of the green MARC1-CD1A decision, all-false
   request, generated parser, and generated contract.
2. A fixed zero-network `plan` path with no user-selected provider, URL,
   record, version, file, range, credential, or local archive path.
3. A strict sequential HTTP adapter that disables automatic redirects,
   requires GET plus identity encoding, caps every body read at one byte past
   its allowed size, rejects duplicate critical headers, and ignores unrelated
   duplicate server headers.
4. Manual bodyless redirect handling through the frozen parser, with no more
   than two tail redirects, no directory redirect, HTTPS-only destinations,
   loop detection, and injected DNS validation requiring every returned
   address to be globally routable.
5. Reuse of the green EOCD, ZIP64, central-entry, safe-path, file-kind,
   compression, ZIP64-extra, overlap, privacy, and deterministic inventory
   parser without modifying its source.
6. A machine gate requiring all five numerical thread variables to equal one,
   at least 12 GiB free disk, normalized one-minute load no greater than one,
   and pre-consumption RSS no greater than 256 MiB.
7. Exclusive no-follow output paths, a private consumed marker before the
   first request, a mode-`0600` exact member manifest, and an aggregate public
   result containing no member name, local-header offset, URL, raw header,
   response body, or per-member row.
8. A consumed aggregate failure result and no-rerun collision check for any
   registered failure after the marker.
9. `plan`, `qualify`, `inspect`, and proof-gated `execute` module CLI modes.

There is no whole-archive download function, ZIP extraction function, member
local-header function, member-payload function, participant selector, neural
reader, model, scorer, credential, alternate endpoint, retry, or rerun
interface.

## Frozen Live Sequence

After exact wrapper CI proof, one invocation may use only:

```text
metadata:  GET one bounded Figshare version-files body
tail:      GET bytes=13591416976-13591548047
redirects: at most two bodyless globally routable HTTPS destinations
directory: GET the exact ZIP64-derived range from the same terminal URL
responses: exactly three accepted bodies, <= 17,039,360 bytes combined
attempts:  <= 5
HEAD:      0
whole ZIP: 0 bytes
members:   0 local-header or payload requests
```

The registered 13,591,548,048-byte archive size and MD5 are identity fields.
The implementation never turns that declared size into a whole-file transfer.

## Adversarial Qualification

The focused suite exercises:

- direct and two-bodyless-redirect generated paths;
- exact request order, headers, timeout, and response URL;
- duplicate critical-header refusal and harmless unrelated-duplicate handling;
- transfer-encoding, over-cap, nonbytes, opener, and automatic-redirect
  refusals;
- globally routable versus loopback redirect resolution;
- thread, disk, load, RSS, output-collision, symlink, and private-inspection
  boundaries;
- marker-before-request ordering;
- mocked three-body live success;
- consumed directory-redirect failure and second-run refusal;
- aggregate privacy and forbidden-counter checks; and
- absence of heavy dependencies, ZIP extraction, and whole-download
  interfaces.

The wrapper also reruns all 32 frozen parser mutations. Those inherited tests
do not make the live archive known; they confirm that the unchanged parser
still refuses the registered malformed generated cases.

## Registered Generated Closeout

One fresh `python -S` process ran with one thread, one worker, one numerical
job, a patched network-client constructor that would raise on use, and a new
temporary output directory. It produced:

```text
route:                              MARC1CDL-G1
generated input bytes:              280,249
virtual archive bytes:              13,591,548,048
central-directory bytes:            148,910
entries:                            18
inherited parser refusals:           32 / 32
wrapper refusals:                    8 / 8
acceptance gates:                    14 / 14
runtime:                             0.006050459109246731 sec
reported peak RSS:                   40,763,392 bytes
external wall / maximum RSS:         0.18 sec / 40,878,080 bytes
aggregate report:                    5,995 bytes
private generated manifest:          6,187 bytes
combined generated output:           12,182 bytes
network-client calls:                0
public or forbidden counter sum:     0
```

Aggregate report SHA-256:
`149eec28f847d072495f1212d8281a63d5b881e821ada57f2668cf5c77195939`

Private generated manifest SHA-256:
`94124a9dbbc67099fb0ccfa1cffa5d3c62db4e97d9b6de289e156c9089306ded`

The two exact temporary files and their invocation-created directory were
removed after hashing. Nothing generated is committed.

## Final Local Verification

```text
wrapper plus implementation-record tests:  30 passed in 0.070 sec
all MARC1 tests:                            198 passed in 0.500 sec
dependency-light suite:                     2,337 passed, 204 skipped, 16.718 sec
optional-neuro suite:                       2,408 passed, 35 skipped, 54.949 sec
optional-neuro pre-change baseline:         2,378 passed, 35 skipped
test delta:                                 +30, with no additional skip
Ruff / compile / JSON / CLI / diff:         pass / pass / pass / pass / pass
```

External maximum RSS was 275,447,808 bytes for the dependency-light complete
suite and 730,267,648 bytes for the complete optional-neuro suite. Those
repository-wide processes import and exercise unrelated models and readers;
they are not the future live executor. The isolated `python -S` wrapper
qualification is the comparable resource proof for the 256 MiB executor cap.

## Resource And Access Accounting

```text
public metadata requests:                      0
public tail / directory requests:              0 / 0
DNS queries / redirects:                       0 / 0
accepted public bodies / bytes:                0 / 0
whole-archive / local-header / member bytes:   0 / 0 / 0
real archive or local data path operations:    0
participant / signal / event / target reads:   0 / 0 / 0 / 0
model / prediction / score runs:               0 / 0 / 0
dependency installs:                           0
hardware / release operations:                 0 / 0
scientific claim upgrades:                     0
end-to-end latency measured:                   false
```

## Remaining Gate

1. Commit and push the locally verified implementation milestone.
2. Require Base Python and Optional Neuro Readers CI to pass.
3. Independently verify the exact commit, CI run, both job IDs, and registry
   hash.
4. Only then evaluate the pre-consumption machine gate and, if it passes,
   consume the one no-retry public metadata/tail/directory audit.

Any failed remote job leaves public access closed. Any failure after the later
private consumed marker consumes the registered execution and permits no
retry, rerun, fallback, amendment, or whole-download substitution.

## Claim Boundary

Engineering capability added: a proof-gated standard-library wrapper can
inventory a 13.59 GB ZIP through bounded metadata ranges without opening a
member payload.

Scientific claim not established: this implementation and its generated
qualification contain no human neural signal, event, target, model result, or
score and establish no neural effect or decoding capability.
