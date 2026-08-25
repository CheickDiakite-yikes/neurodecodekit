# BNCI-C3C5-1 Stage A Redirect Recovery Implementation

Date: 2026-08-24

Status: **generated qualification passed; exact implementation and corrected
activation are remotely green; live recovery is pending the control-plane
documentation proof**

Machine records:

- `registries/bnci_2014_001_stage_a_redirect_recovery_implementation.v0.json`
- `registries/bnci_2014_001_stage_a_redirect_recovery_generated_result.v0.json`

## Capability Added

The additive recovery layer validates the pinned NEMAR manifest against the
same 18 registered MAT identities, extracts only direct allowlisted signed-URL
fields, requires HTTPS on `nemar.s3.us-east-2.amazonaws.com`, and derives every
accepted object path from the frozen byte count and SHA-256.

The manifest request and payload requests disable redirects, proxies, and
content encoding. Signed credentials remain in memory only. Opaque acquisition,
resume, hashing, atomic publication, and cleanup are anchored to no-follow
directory descriptors so a changed pathname cannot redirect mutation outside
the repository. A process wall-clock alarm plus per-chunk runtime, RSS, network,
and disk checks enforce the registered resource envelope.

Live execution requires a tracked activation record that is clean against
`HEAD` and proves every implementation artifact byte-identical to its remotely
green implementation commit. The entire tracked tree must also be clean, so a
modified imported dependency cannot alter execution. That activation now
exists: corrected activation `492a36a` passed both required jobs in CI
`32807676008`.

## Generated Qualification

The single generated invocation passed 18 case classes. It validated all 18
registered identities totaling 779,873,919 bytes without opening them, then ran
one tiny three-file end-to-end roundtrip through the generated manifest client,
strict parser, signed range transport, interrupted resume, descriptor-anchored
downloader, SHA-256 verification, publication, and cleanup.

Measurements:

- generated fixture bytes: 11,558;
- temporary generated payload bytes: 76;
- generated manifest requests: 1;
- generated payload requests: 4, including 1 resume;
- direct adversarial refusals: 12;
- runtime: 0.010994000011123717 seconds;
- peak process RSS: 29,786,112 bytes; and
- retained generated payload bytes: 0.

Real manifest requests, real payload requests, ignored-path operations, MAT
semantic opens, model runs, training, predictions, targets, and scores were all
zero. The result registry closes the generated qualification against repetition.
The final local gate passed 6,049 dependency-light tests with 216 expected
optional skips in 275.733 seconds, plus 129 focused BNCI checks.
After the single generated run, review hardened only the pre-live Git cleanliness
gate; no generated behavior changed and the consumed qualification was not rerun.

## Next Gate

The implementation and activation barriers are complete. Commit, push, and
remotely green the aligned control-plane documentation and current-frontier
record. Only then may the one replacement Stage A recovery read the public
manifest and acquire the exact 18 opaque payloads. Record and remotely green
its aggregate result before Stage Q.

Engineering capability added: a generated-qualified, path-anchored signed-object
recovery can reproduce the registered Stage A payload identity after proof gates.

Scientific claim not established: no real neural payload was opened or modeled,
so this milestone establishes no EEG gain, decoding performance, or unseen-person
generalization.
