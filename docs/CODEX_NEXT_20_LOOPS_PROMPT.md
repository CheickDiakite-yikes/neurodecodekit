# Codex Continuation Prompt

Use `prompts/CODEX_START_PROMPT.md` for the current work order.

The original 20-loop sequence is complete except parked Loop 13. Loop 23 is
parked after its frozen synthetic test gate; Loop 23.5 is complete; Loop 24 is
available for an independent preregistration only. RW1 and RW2 are closed at
their exact synthetic proof boundaries. RW3's replay/live-source contract is
frozen at commit `c3d1f01` as registration-only evidence. Commit `163ff2f`
prepares a hash-bound Stage A authorization packet whose machine request still
says `authorized_now: false`.

The next practice-track decision is **review and explicit authorization of RW3
Stage A only, or an explicit hold**. Review
`docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md` and
`registries/rw3_stage_a_authorization_request.v0.json`. Do not implement it from
this continuation note. The frozen contract already defines the source-chunk,
clock, timestamp, packet-loss, ordering, state, schedule, privacy, resource,
tolerance, refusal, and proceed/park/kill rules.

Do not download or open S20. Do not reopen consumed S7/S21 evidence or seeds
2203, 2303, and 2353. Do not install/use BrainFlow, LSL, or PyXDF, connect
hardware, open a socket or live source, implement an adapter, create targets,
run a model, or train anything without the separate stage authorization.
Passing a future synthetic replay gate could establish interface and accounting
equivalence only; it would not establish signal quality, useful EEG, neural
advantage, decoding, real-time performance, or portable hardware.
