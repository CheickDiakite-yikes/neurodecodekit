# BNCI-C3C5-1 Stage Q Live Activation

Date: 2026-08-25
Lane: `BNCI-C3C5-1-Q`
Status: prepared with delayed effect pending final activation proof

## Exact Green Predecessors

Stage A result `96d7f0569a54b05f8031d2e3943658ef598e38a5`
passed Base Python job `97700176631`, Optional Neuro Readers job
`97700176787`, and CI `32814564120`.

The final Stage Q implementation commit
`e5ca6a24f65beab12b89eddad938c96fe4ecaf00` passed Base Python job
`97723744136`, Optional Neuro Readers job `97723744450`, and CI
`32822604745`. The activation binds byte and SHA-256 identities for all 11
qualified implementation artifacts at that green commit, including the
consumed generated result. Qualified runtime artifacts remain byte-identical.
This activation milestone changes only the historical live-control test that
previously required the activation path to remain absent; it now verifies that
the exact pre-activation implementation commit was fail-closed.

## Delayed Effect

This activation has delayed effect and no live effect while uncommitted,
unpushed, or remotely unproven. The one Stage Q execution becomes eligible
only after the exact activation commit is pushed. The transition remains
closed until both required CI jobs pass.

Initial activation commit `e67809593de548bf8dd2afb1f1298b7a2c9b26eb`
failed Base job `97727563579` in CI `32823864546`. The failing tests attempted
to read the prior implementation commit from a shallow Actions checkout and
therefore raised before completing the suite. No private path, MAT, target,
model, prediction, score, marker, or derivative was touched. This failure has
no activation effect. A test-only compatibility commit must first pass both
jobs; the activation must then be rebound to that exact green commit and pass
both jobs itself.

Compatibility commit `52b681ed7ec3991527f04f2fc555452d2246c481`
then passed Base Python job `97730713400`, Optional Neuro Readers job
`97730713304`, and CI `32824921855`. This activation is now rebound to that
exact commit and the corrected 21,981-byte live-control test identity. Every
qualified runtime artifact and the consumed generated result remain unchanged.
The rebind still has delayed effect until its own exact commit is pushed and
both required jobs pass.

Immediately before the semantic executor, the public live CLI must obtain a
fresh remote branch SHA and GitHub Actions result for the activation commit.
The commit, remote, CI, and local head SHAs must agree, and both exact jobs must
be complete and successful. The public executor accepts no proof or key-factory
override and uses `secrets.token_bytes` for target sealing.

## Activated Scope

After the delayed-effect gate passes, exactly one target-isolated Stage Q may:

- read the exact green private Stage A manifest;
- open and semantic-parse each of the 18 registered MAT files exactly once;
- validate the frozen 108-run / 5,184-trial inventory;
- produce target-free one-copy participant/session feature shards;
- produce nine fold delivery manifests and fold-scoped source labels;
- seal nine held-out-E target sets and aggregate artifact values; and
- publish one private aggregate receipt with zero participant outcome.

The live executor must pass its 227,843,968-byte conservative layout preflight,
require at least 2 GiB plus that bound free, remain under 1 GiB peak RSS and
3,600 seconds, emit at most 512 MiB private and 4 MiB public output, use one
thread/worker/job, and perform zero analysis network, model, training,
prediction, target-delivery, or score operations.

## Closed Scope

Stage P modeling and prediction remain closed until the aggregate Stage Q
result is committed, pushed, and both jobs are green. Stage T target delivery
and scoring remain closed until the later prediction-freeze proof is remotely
green. There is no retry, rerun, substitution, release, or claim upgrade.

This activation proves only an eligible engineering transition. It has not
opened a private manifest or MAT, read a signal or target, run a model, frozen a
prediction, produced a score, or established neural information, EEG beyond
EOG, unseen-person generalization, language, movement intention, live decoding,
portable hardware, home use, or clinical utility.
