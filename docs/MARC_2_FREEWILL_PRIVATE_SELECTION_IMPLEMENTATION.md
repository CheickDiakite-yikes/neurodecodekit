# MARC2-FW1A Private Selection Wrapper Implementation

Date: 2026-08-13

Status: **Generated/mock wrapper complete and locally qualified; the retained
private manifest has not been statted, opened, read, hashed, or parsed by this
implementation milestone**

Registry:
`registries/marc2_freewill_private_selection_implementation.v0.json`

Module:
`src/neurodecodekit/datasets/marc2_freewill_private_selection.py`

## Proof Order

The packet-bound decision is exact commit
`ad1e4064256f963b2d03daeb27e4a4779b32415f`. It passed Base Python job
`94656172494` and Optional Neuro Readers job `94656172528` in CI
`31764052451` before wrapper work resumed.

The wrapper pins that decision, its all-false request, the authorization
packet, the frozen `MARC2-FW1` selector, and the selector contract by SHA-256.
The live `execute` path also requires externally supplied proof that the exact
wrapper implementation commit passed both remote jobs and is the clean current
HEAD. Generated qualification cannot satisfy or bypass that proof.

## What Was Implemented

The additive standard-library module exposes only:

```text
plan
qualify --output-dir <new generated directory>
inspect <aggregate report>
execute --output-root <exact registered root> <exact green proof>
```

There is no source-path, subject, seed, cap, split, member, URL, credential,
payload, model, or target override. The module does not import or call either
consumed `MARC1` live executor. It does not include a network client, archive
member reader, EEG reader, event parser, trainer, predictor, scorer, or
language-model provider.

The generated adapter builds the exact 1,227-row private-manifest shape and
source identity expected from the retained central-directory inventory. It
then applies only the remotely green frozen selector:

- preserve the 19-person DOI-bound participant rank;
- hold `ses-01` as fit and `ses-02` as held out;
- select the first three complete numeric run bundles in each session;
- require exactly four structural companions per run;
- reserve compressed bytes plus the frozen ZIP header/name/extra-field bound;
- preserve the 12-person floor and 19-person ceiling;
- take the maximal contiguous participant prefix under 8 GiB; and
- stop at the first nonfitting participant without skip or substitution.

Target, label, response, sentence, trial, quality, channel, onset, signal,
event, model, prediction, and score fields are structurally forbidden from the
private selection. The aggregate walker separately blocks member names,
offsets, CRC fields, private rows, local paths, raw bodies, and raw headers.

## One-Shot Live Boundary

The future live path is fixed to one exact retained source identity and one
exact absent output root. It requires:

1. green implementation proof and a clean exact HEAD;
2. one-thread environment, load, RSS, free-disk, and output preflight;
3. no-follow checks over each literal path component and the final regular
   file;
4. exact owner, mode `0600`, byte count, and SHA-256;
5. one `O_NOFOLLOW` content open and one `fstat` identity reconciliation;
6. one bounded sequential read pass, one hash pass, and one strict JSON parse;
7. a mode-`0600` consumed marker before the content open;
8. separate mode-`0600` private selection and aggregate report outputs; and
9. an aggregate-only consumed failure receipt if a post-marker gate refuses.

Bounded readers accept legitimate short reads without opening the file again.
Duplicate keys, BOM/NUL encodings, nonfinite values, short/overflow bodies,
identity races, symlinks, wrong owner/mode/size/hash/schema, and output
confusion fail closed. The 30-second runtime covers the full registered
invocation, including proof and machine preflight.

No retry, rerun, resume, repair, alternate path, fallback, or old-root access
exists. A consumed failure publishes only its stable route and stage, never the
private reason or row. Success and failure both stop before every ZIP local
header and archive member.

## Adversarial Qualification

The wrapper preserves all 40 frozen selector refusals and adds exactly 18
wrapper refusals:

```text
F00 proof, commit, CI, job, HEAD, or tracked artifact       3
F01 machine, output, symlink, owner, mode, or preflight     8
F02 size, hash, open/fstat, strict JSON, or source identity 4
F06 privacy, output cap, or forbidden operation             3
```

Generated tests additionally cover deterministic reverse-row replay,
target-field exclusion, no-site-packages import, fixed CLI surface, one-pass
short-read handling, output modes and caps, private-schema inspection refusal,
and aggregate failure reporting after a consumed marker.

## Measured Generated Qualification

One fresh generated qualification used one CPU thread, one worker, and one
numerical job:

```text
generated input bytes:          846,712
combined output bytes:          296,659
internal runtime:               0.2679154590005055 sec
reported peak RSS:              36,126,720 bytes
inherited selector refusals:    40 / 40
wrapper refusals:               18 / 18
selected generated subjects:    16
selected generated bundles:     96
selected generated members:     384
generated reservation bytes:    8,105,207,776
```

The generated aggregate report SHA-256 was
`0812b79d0ee98bda05526ad7bac1f9fef40a8577a681b59f6060dfb9a4616eda`.
The generated selection identity SHA-256 was
`349c5be46055a4757245099b0d44acb3dd0b6e9bdced0a5d841cd10aa25cc321`.
These are fixture qualification identities, not retained-manifest results.

Every registered-private, network, archive-member, signal, target, derivative,
training, inference, prediction, score, provider, hardware, retry, and claim
counter remained zero.

## Verification

Twenty-six focused functional tests cover the wrapper and generated
qualification. Fourteen implementation-record tests bind the exact code,
tests, proof artifacts, generated measurements, refusal inventory, access
counters, next gate, and claim boundary.

Ruff, Python compilation, strict JSON behavior, CLI help and generated
roundtrip, artifact hashes, and diff hygiene pass. Complete base and optional
suite totals are recorded in the machine registry after the final local run.
Remote CI remains pending for this exact implementation commit.

## Access Accounting

```text
retained private path checks / opens / bytes:         0 / 0 / 0
real participant / member selections:                 0 / 0
consumed markers / private outputs / aggregate reports: 0 / 0 / 0
network requests / bytes:                             0 / 0
archive local-header or member payload reads:          0
signal or event/target/quality/channel reads:          0 / 0
real derivative rows:                                 0
training / inference / prediction / scoring:          0 / 0 / 0 / 0
provider / language-model / hardware operations:      0 / 0 / 0
retry / rerun / claim upgrades:                       0 / 0 / 0
```

## Next Gate

1. Commit and push this exact implementation.
2. Require Base Python and Optional Neuro Readers to pass at that commit.
3. Only then run the one already authorized private-manifest selection once.
4. Inspect only its aggregate result, never the private selection output.
5. Record, test, commit, push, and green that consumed result.
6. Prepare a separate all-false `MARC2-FW2` payload packet only if the result
   route permits it.

The current authorization ends at target-free structural selection. It does
not authorize a ZIP local header, archive member, EEG sample, event, target,
model, prediction, score, download, or `MARC2-FW2` execution.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now has a proof-gated one-shot
wrapper that can convert one exact private ZIP-directory manifest into a
deterministic storage-bounded target-free participant selection.

Scientific claim not established: generated structural metadata contain no
human neural signal, prediction, or score and establish no neural effect,
decoding accuracy, language decoding, or thought-to-text result.
