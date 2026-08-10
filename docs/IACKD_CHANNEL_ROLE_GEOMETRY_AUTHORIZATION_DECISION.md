# IACKD Channel Role and Geometry Authorization Decision

Date: 2026-08-10

Status: **Authorized only after this decision is tested, committed, pushed,
and remotely green; zero real-metadata operations at recording**

Machine decision:
`registries/iackd_channel_role_geometry_authorization_decision.v0.json`

Authorization parent:
`86174bc86123bc010bac2f40a9d72147dc8aef05`

Green request CI:
`31431064259`

## Actual Maintainer Decision

After Codex identified IACKD-H2 as the sole active Tier C packet, named request
commit `86174bc86123bc010bac2f40a9d72147dc8aef05`, CI `31431064259`, both
required green jobs, the exact 316-object/457,602-byte scope, and the need for a
fresh decision, the maintainer said:

> continue :)

This record preserves those words exactly. It does not claim that the
maintainer typed the packet's long scope. The short instruction incorporates
the immutable, remotely green packet by reference without widening it.

## Why The Short Form Is Valid

1. IACKD-H2 was the sole active Tier C packet.
2. Request `86174bc86123bc010bac2f40a9d72147dc8aef05` was already committed
   and pushed.
3. Base Python job `93594327147` and Optional Neuro Readers job `93594327069`
   were green in CI `31431064259`.
4. Codex named that packet, proof, sole scope, and decision gate first.
5. The maintainer then unambiguously said `continue :)`.
6. This separate record quotes the actual words and binds the frozen artifacts.
7. No release, destructive, hardware, scientific, or other scope is inferred.

The decision is ineffective until its own commit passes both remote CI jobs.

## Exact Authorized Operation

After that green gate, one invocation may:

1. verify the frozen contract, inventory, implementation, request, decision,
   commits, CI identifiers, hashes, clean tracked worktree, and ordinal one;
2. write one private Git-ignored consumed marker before the first request;
3. request exactly 316 registered public OpenNeuro metadata bodies
   sequentially: 128 channel tables, 128 EEG sidecars, 30 electrode tables,
   and 30 coordinate-system files;
4. require exact status, URL, Content-Length, ETag, identity encoding, and an
   8,192-byte maximum for each body;
5. read exactly 457,602 expected body bytes total, hash and strictly parse each
   body once in memory, and discard it before the next request;
6. pair channel tables with sidecars by private run identity and electrode
   tables with coordinate systems by private participant/hand identity;
7. reconcile H1 declarations, source BIDS roles, channel counts, sampling,
   reference declarations, and central/occipital geometry coverage;
8. aggregate only allowlisted compatibility evidence and apply frozen route
   `IACKDR-R0` through `IACKDR-R4`; and
9. emit one bounded aggregate ledger and stop.

There is no fallback, redirect, retry, substitution, parser amendment, or
rerun. A failure after the consumed marker consumes the one execution.

## Exact Limits

```text
public metadata requests / expected bytes: 316 / 457,602
maximum bytes per body:                    8,192
network body ceiling:                      2,097,152 bytes
wall time / peak RSS:                      180 sec / 268,435,456 bytes
incremental disk / public output:          4,194,304 / 2,097,152 bytes
minimum free disk:                         2,147,483,648 bytes
threads / workers / jobs:                  1 / 1 / 1
retries / reruns:                          0 / 0
```

No dependency installation, inventory refresh, local IACKD bundle operation,
VHDR/VMRK/EEG or sibling access, signal sample, event, trajectory, target,
label, cache, split, feature, model, prediction, scoring, provider, stream,
device, hardware, release, or claim upgrade is authorized.

## Decision-Only Measurements

```text
GitHub CI verification calls:                  1
real metadata requests / bytes / parses:       0 / 0 / 0
local IACKD path stats or opens:               0
VHDR or sibling resolutions, stats, or opens:  0
signal, event, trajectory, target reads:       0 / 0 / 0 / 0
model loads / training / inference / scoring:  0 / 0 / 0 / 0
dependency installs / provider calls:          0 / 0
stream, device, or hardware operations:        0
retries / reruns / releases / claim upgrades:  0 / 0 / 0 / 0
end-to-end latency measured:                   false
```

## Claim Boundary

**Engineering capability authorized for testing:** one exact, resource-bounded
public metadata audit may freeze whether a count-agnostic, source-declared
sensor-role and geometry contract is compatible with all registered IACKD
files.

**Scientific claim not established:** this decision is not data or a result. It
establishes no neural effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit, or
clinical use.
