# BNCI-C3C5-1 Stage A Redirect Recovery Authorization Packet

Date: 2026-08-24

Status: **request only; all authority remains false**

Machine request:

- `registries/bnci_2014_001_stage_a_redirect_recovery_authorization_request.v0.json`

## Why Recovery Is Necessary

The original Stage A invocation is permanently consumed at `BNCIC3C5-A-R1`.
It received HTTP `302` on the first registered NEMAR payload URL and refused
before reading a payload byte. Failure closeout commit
`162fddcfa2f399f4e5919a2daa0de4d7d33bf1f4` passed CI `32782670936`,
Base job `97607889466`, and Optional job `97607889659`.

The pinned public NEMAR manifest explains the response. Each selected
`bytes_url` resolves to a one-hour signed HTTPS object on exactly
`nemar.s3.us-east-2.amazonaws.com`. The object key itself embeds the registered
size and SHA-256:

```text
/nm000139/objects/SHA256E-s{bytes}--{sha256}.mat
```

No neural payload was read during this metadata confirmation.

## Requested Recovery

After a separate decision is committed, pushed, and remotely green, implement
and generated-qualify one additive recovery wrapper. It must parse only a
generated NEMAR-manifest fixture, validate the exact 18 selected identities,
accept only signed HTTPS URLs on the one allowlisted S3 host with object keys
derived from each registered byte count and digest, and refuse arbitrary
redirects, hosts, paths, queries, records, or files.

Only after that exact implementation is committed, pushed, and remotely green,
run one replacement invocation:

1. preserve the original consumed marker byte-for-byte;
2. write a distinct recovery marker before network construction;
3. read the pinned public manifest exactly once, bounded to 1 MiB;
4. validate its 18 selected records against the frozen member table;
5. stream only the 18 signed objects directly from the allowlisted host;
6. accept exactly 779,873,919 bytes after per-file size and SHA-256 checks; and
7. write a new isolated private bundle plus one aggregate receipt.

The recovery permits at most 54 payload requests, three attempts per file,
2.501 GiB total network including metadata, 2 GiB incremental disk, 1 GiB RSS,
1,800 seconds, and one thread, worker, and numerical job. It retains all
original scientific, publication, and privacy boundaries.

## Explicitly Not Requested

This packet does not authorize changing or deleting the original marker;
arbitrary redirect following; another participant, file, representation, or
dataset; MAT parsing; signal, event, target, or label reads; cache creation;
training; inference; prediction; scoring; release; or a claim upgrade.

## Decision Gate

This packet and its proof must first be committed, pushed, and remotely green.
It must then be identified as the sole active Tier C packet. Only the
maintainer's next unambiguous decision can authorize it under the short-form
charter rule.

Engineering capability requested: recover the exact registered payload from
NEMAR's validated signed-object indirection without loosening file identity or
resource controls.

Scientific claim not established: this request contains no payload, neural
read, model, prediction, target delivery, score, or evidence of EEG gain.
