# MARC2-VR13P Invalid Preproof Invocation Incident

Date: 2026-08-20

Lane: `MARC2-VR13P`

Status: consumed, invalid, parked, no retry, no result

## What Happened

Final proof-state-hardened implementation
`4fb242483a169f95be31e9652b240c2139efaaac` passed both required jobs in CI
`32442008002`. While preparing the separate local proof-only closeout, the
implementation registry temporarily contained the green implementation IDs
before that closeout had a commit or remote proof.

Focused test
`test_execute_refuses_before_readiness_or_private_path_access` expected F01.
It mocked readiness collection and source preflight, but the executor trusted
the uncommitted registry proof fields and continued. The assertion failed only
after the executor returned.

This is a sequencing and proof-verification failure. It is not an acceptable
registered execution.

## Known Boundary

The call took zero actual readiness samples and performed zero source-preflight
operations because those functions were mocked. It then opened the registered
target-free structural source once, read exactly 418,755 bytes, strict-parsed
once, and called VR12A once.

The test did not retain the returned report. The route, residual-map call
count, private-manifest status, output bytes, runtime, peak RSS, and cohort are
unavailable. The ignored output was not inspected after the failure. No neural
payload, target, label, model, prediction, score, network, FW2/CIL1, or other-
project operation occurred.

## Disposition

VR13P is consumed and parked. There will be no retry, rerun, resume, cleanup,
ignored-output inspection, inference, or claim from this invocation. Remote
proof is restored to null so `execute` refuses at F01 again.

Any future recovery of even the aggregate ignored report requires a new frozen
Tier C packet and a fresh packet-bound decision. FW2 and CIL1 remain
ineligible.

After proof was restored to null, 33 focused tests and all 4,302 base tests
passed with 204 expected skips and zero failures. The focused suite explicitly
reproved F01 before readiness or private access. Ruff, all 302 registry JSON
files, and diff hygiene also pass.

Engineering capability learned: execution must verify the current proof-
closeout commit and remote CI independently, rather than trusting proof fields
written into a mutable local registry.

Scientific claim not established: the invalid call accessed only target-free
structural metadata and produced no retained valid route, cohort, neural
effect, decoding metric, language result, live result, or thought-to-text
evidence.
