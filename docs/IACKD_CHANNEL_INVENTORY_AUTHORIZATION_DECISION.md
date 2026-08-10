# IACKD Header Inventory Audit Authorization Decision

Date: 2026-08-10

Status: **Authorized only after this decision is tested, committed, pushed,
and remotely green; zero real-header operations at recording**

Machine decision:
`registries/iackd_channel_inventory_authorization_decision.v0.json`

Authorization parent:
`56531c64b6733f93c9def80ad57125e0ee998fd8`

Green request CI:
`31416489006`

## Actual Maintainer Decision

After Codex identified IACKD-H1 as the sole active Tier C packet, named request
commit `56531c6`, CI `31416489006`, both required green jobs, the exact
128-header/161,792-byte scope, and the need for a fresh decision, the maintainer
said:

> not bad, that actually good research thank you, makes me feel a little better. keep going, move the needle, continue, you approved to go on

This record preserves those words exactly. It does not claim that the
maintainer typed the packet's long scope. The short instruction incorporates
the immutable, remotely green packet by reference without widening it.

## Why The Short Form Is Valid

1. IACKD-H1 was the sole active Tier C packet.
2. Request `56531c6` was already committed and pushed.
3. Base Python job `93546632359` and Optional Neuro Readers job `93546632280`
   were green in CI `31416489006`.
4. Codex named that packet, proof, sole scope, and decision gate first.
5. The maintainer then unambiguously said `continue`.
6. This separate record quotes the actual words and binds the frozen artifacts.
7. No release, destructive, hardware, scientific, or other scope is inferred.

The decision is ineffective until its own commit passes both remote CI jobs.

## Exact Authorized Operation

After that green gate, one invocation may:

1. verify the frozen contract, inventory, implementation, request, decision,
   commits, CI identifiers, hashes, clean tracked worktree, and ordinal one;
2. write one private Git-ignored consumed marker before the first request;
3. request exactly 128 registered public OpenNeuro VHDR bodies sequentially;
4. require exact status, URL, Content-Length, ETag, identity encoding, and a
   4,096-byte maximum for each body;
5. read exactly 161,792 expected bytes total, hash and strictly parse each body
   once in memory, and discard it before the next request;
6. validate DataFile and MarkerFile only as inert basenames without resolving
   or touching a sibling;
7. aggregate header signatures and apply frozen route `IACKDH-R0` through
   `IACKDH-R5`; and
8. emit one bounded aggregate ledger and stop.

There is no fallback, redirect, retry, substitution, parser amendment, or
rerun. A failure after the consumed marker consumes the one execution.

## Exact Limits

```text
public VHDR requests / expected bytes: 128 / 161,792
maximum bytes per body:                4,096
network body ceiling:                  1,048,576 bytes
wall time / peak RSS:                  120 sec / 268,435,456 bytes
incremental disk / public output:      2,097,152 / 1,048,576 bytes
minimum free disk:                     2,147,483,648 bytes
threads / workers / jobs:              1 / 1 / 1
retries / reruns:                      0 / 0
```

No dependency installation, metadata refresh, local IACKD bundle operation,
sibling access, signal sample, event, trajectory, target, label, cache, split,
feature, model, prediction, scoring, provider, stream, device, hardware,
release, or claim upgrade is authorized.

## Decision-Only Measurements

```text
GitHub CI verification calls:                 1
real VHDR requests / bytes / parses:          0 / 0 / 0
local IACKD path stats or opens:              0
sibling resolutions, stats, hashes, or opens: 0
signal, event, trajectory, target reads:      0 / 0 / 0 / 0
model loads / training / inference / scoring: 0 / 0 / 0 / 0
dependency installs / provider calls:         0 / 0
stream, device, or hardware operations:       0
retries / reruns / releases / claim upgrades: 0 / 0 / 0 / 0
end-to-end latency measured:                  false
```

## Claim Boundary

**Engineering capability authorized for testing:** one exact, resource-bounded,
sibling-blind public-header audit may replace a failed hard-coded channel
assumption with a measured aggregate compatibility diagnosis.

**Scientific claim not established:** this decision is not data or a result. It
establishes no neural effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit, or
clinical use.
