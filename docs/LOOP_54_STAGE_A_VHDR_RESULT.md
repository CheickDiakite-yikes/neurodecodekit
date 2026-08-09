# Loop 54 Stage A Strict VHDR Result

Date: 2026-08-08

Status: **Consumed; parked at L54A-F11; no rerun**

## Registered execution

Exact implementation commit
`b486fdf13d8a2293432f9dca5f3fb8ba97527be0` passed push CI
`31287819503` before the one invocation. Base Python job `93179736029`
passed in 18 seconds and Optional Neuro Readers job `93179736035` passed in
55 seconds. Branch parity was `0/0`, the tracked worktree was clean, and
45,895,475,200 bytes of free disk were available before execution.

The invocation used one CPU thread and one worker. It consumed the one
registered execution and returned code `2` after 0.20 seconds external wall
time at 24,051,712-byte peak RSS. It read exactly 11,705 VHDR bytes in one
content open. The exact size and registered Git-blob identity matched before
semantic parsing began.

## Result

The strict codepage detector and decoder completed without replacement or
control-character failure. Parsing then parked at the registered refusal:

`L54A-F11_missing_duplicate_or_malformed_required_section_or_key`

Safe diagnostic: `VHDR format preamble is missing`.

The raw first line is deliberately not reported. Its content, codepage value,
comments, declared channels, `DataFile`, `MarkerFile`, and every other header
value remain unavailable. No post-result parser change, alternate preamble,
fallback reader, MNE read, substitution, or second attempt is permitted.

## Gate map

| Gate | Result | Evidence |
|---|---|---|
| Dependency and source identities | Passed | Frozen contract, decision, implementation sources, exact commit, and source blob matched |
| Authorization and implementation remote green | Passed | Decision CI `31286428489`; implementation CI `31287819503` |
| One regular non-symlinked 11,705-byte VHDR open | Passed | No-follow component and descriptor checks completed once |
| VHDR Git-blob identity | Passed | Registered blob matched before parsing |
| No sibling path resolved, statted, or opened | Passed | All sibling counters remained zero |
| No heavy dependency imported | Passed | Registered parser path is standard-library-only |
| Strict codepage detection and decoding | Passed | Execution advanced beyond strict decoding without F09 or F10 |
| Required structure and declarations | **Failed** | F11 at the format-preamble requirement |
| Inert DataFile and MarkerFile basenames | Not reached | No value was emitted or sibling path constructed |
| Complete ordered channel table | Not reached | Channel parsing did not begin |
| Unique decoded channel names | Not reached | Channel parsing did not begin |
| Declared references, resolutions, and units | Not reached | Channel parsing did not begin |
| Sampling interval and derived rate | Not reached | Common declarations were not accepted |
| Explicit unavailable fields | Passed in closeout | No unavailable value was inferred or promoted |
| No raw, comment, protected, or local-path publication | Passed | Only the stable refusal and aggregate counters are reported |
| Forbidden operation counters zero | Passed | No sibling, signal, target, model, network, or hardware operation ran |
| Resource, output, thread, and no-overwrite limits | Passed | 0.20 sec, 24,051,712 bytes RSS, one thread/worker, zero output bytes |
| Claim at or below L54-Q2 | Passed | L54-Q2 was not reached; the route remains at L54-Q1 acquisition identity |

The all-gates conjunction failed. L54-A did not establish declared-header
compatibility. The private registered output root is absent because output
creation occurs only after a successful parse; registered ledger and summary
bytes are both zero.

## Access ledger

| Operation | Count |
|---|---:|
| Registered real executions | 1 |
| Registered VHDR content opens | 1 |
| Registered VHDR bytes read | 11,705 |
| Size checks | 1 |
| Git-blob checks over the in-memory payload | 1 |
| Strict decode attempts | 1 |
| Strict parse attempts | 1 |
| VMRK/EEG/MAT or sibling path resolutions, stats, hashes, or opens | 0 |
| Signal, marker, event, trial, response, key, sentence, label, or target reads | 0 |
| Cache, split, feature, representation, model, checkpoint, inference, training, scoring, or selection operations | 0 |
| Network, download, provider, language-model, RW3, stream, device, hardware, or release operations | 0 |
| Registered ledger or summary writes | 0 |
| Raw-header or comment bytes published | 0 |
| Reruns or post-result amendments | 0 |

End-to-end decoding latency was not measured. The 0.20-second value is only
the bounded CLI compatibility invocation.

## Verification

The complete Loop 54 route passes 83 tests with 40 mutation subchecks. The
complete CI-style unittest suite passes 1,359 tests with three expected skips
in 32.088 seconds internal time and 33.11 seconds external wall time at
650,461,184-byte peak RSS.

The complete pytest suite passes 1,356 tests with three expected skips and 493
subtests in 32.79 seconds internal time and 33.99 seconds external wall time at
658,030,592-byte peak RSS. This is five passing tests above the exact
implementation milestone's 1,351-test pytest baseline, with no lost test,
skip, or subtest. An initial full unittest pass exposed three stale queue-status
assertions from earlier work orders; only those documentation expectations were
advanced, and the final complete suite passed without a real-data rerun.

Repository-wide Ruff, compileall, all 93 registry JSON files, root and both
Loop 54-A CLI help surfaces, and `git diff --check` pass. No execute command was
called during closeout verification.

## Route

L54-A is consumed and parked with no rerun. Loop 54-B and Loop 54-C remain
blocked because their prerequisite declared-header compatibility gate did not
pass. This result does not authorize a fallback parser, sibling inspection,
signal read, target reconciliation, model run, new download, or claim upgrade.

Engineering capability added: NeuroDecodeKit executed one exact, bounded,
sibling-blind VHDR compatibility gate and preserved a fail-closed result when
the registered source did not satisfy the strict preamble contract.

Scientific claim not established: no EEG signal, marker, event, trial, target,
or model was accessed, and no neural advantage, decoding accuracy,
generalization, real-time, portable-hardware, home-use, or clinical result was
established.
