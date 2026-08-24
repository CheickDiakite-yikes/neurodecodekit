# BNCI-C3C5-1 Stage A Acquisition Failure

Date: 2026-08-24

Status: **first Stage A invocation consumed; no payload body received**

Machine record:

- `registries/bnci_2014_001_stage_a_failure.v0.json`

## What Happened

The exact Stage A implementation commit `619105bda3c39c063bb47bda6793af2ece9e1f53`
passed CI `32781910547`, including Base Python job `97605610792` and Optional
Neuro Readers job `97605610605`. The one registered invocation then wrote its
exclusive consumed marker and issued the first registered HTTPS request.

NEMAR returned HTTP `302`. The frozen implementation permitted only a direct
response and refused without following the redirect. The launcher exited after
`0.39314375` seconds.

## Measured Boundary

- one invocation, request, and HTTP response;
- zero followed redirects and zero payload body bytes;
- zero accepted files and zero private-manifest or receipt bytes;
- zero MAT semantic opens, parses, signals, events, targets, or labels;
- zero caches, fits, model runs, predictions, target deliveries, or scores;
- one retained 297-byte consumed marker; and
- no bundle, receipt, or partial directory.

Peak RSS and response-header wire bytes are unavailable because refusal
preceded aggregate-receipt construction and urllib did not expose counted
wire-header bytes. They are reported as unavailable rather than estimated.

## Consequence

The original Stage A authority is consumed. There is no retry, rerun, resume,
restart, redirect-following amendment, or substitution under that authority.
Stage Q remains closed because no verified payload bundle exists.

A future recovery must be separately preregistered and authorized. It should
permit only a bounded same-origin or explicitly allowlisted NEMAR redirect,
retain TLS and all byte/hash/resource checks, preserve the existing marker,
write a distinct recovery marker and output root, and allow only one
replacement acquisition.

Engineering result: the transport identity boundary failed closed before any
payload byte and cleaned its invocation-created temporary directory.

Scientific claim not established: no neural payload was obtained or opened,
and no unseen-person prediction, EEG gain beyond EOG, or decoding score was
produced.
