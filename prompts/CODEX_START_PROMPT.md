# Prompt to continue NeuroDecodeKit in Codex

Continue NeuroDecodeKit from the current branch. Read `AGENTS.md`,
`START_HERE.md`, `docs/CODEX_HANDOFF.md`,
`docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`,
`docs/BYO_NEURODATA_WORKBENCH_SPEC.md`, and
`docs/POST_20_ROADMAP.md` before editing.

Primary task: preregister Real-World Practice Track RW2 as a bounded optional
signal-read and quality-report contract. Do not implement a reader, open a
recording, install a dependency, or generate signal artifacts in this work
order.

Requirements:

1. Preserve all existing work and the unrelated tracker inspection NDJSON.
2. Do not open consumed S7/S21 raw arrays or caches, and do not use seeds 2203,
   2303, or 2353.
3. Do not download anything. The S20 packet remains unapproved.
4. Research current primary MNE, MNE-BIDS, EDF/BDF, BrainVision, EEGLAB, and
   FIFF reader behavior before freezing any adapter assumption.
5. Define exact bounded-header/sample access, channels, duration, units,
   reference, source filters, geometry, events, annotation, and clock fields
   for each format family.
6. Preregister PSD and signal-quality methods, thresholds, unavailable states,
   synthetic controls, and warning semantics. A warning must not automatically
   delete or interpolate a channel.
7. Freeze path/privacy behavior for participants, measurement dates,
   annotations, device serials, and report redaction.
8. Freeze one-thread limits for files, channels, samples, seconds, text/binary
   bytes, runtime, peak RSS, and generated output before implementation.
9. Define optional-dependency errors and prove that the base install remains
   dependency-free.
10. Keep format readability, task compatibility, model compatibility, and
    benchmark authorization as separate levels. Do not create labels, target
    text, predictions, CER/WER, or decoding output.
11. Specify synthetic fixtures and malformed/refusal tests before any real
    source is considered.
12. Close the preregistration with docs, tracker/decision/handoff updates, a
    coherent commit, and a push. Implementation needs a later explicit gate.

RW1 is complete at compatibility level 0 only. RW2 preregistration may define
how to test bounded signal readability and quality reporting, but it adds no
signal result, neural advantage, decoding, latency, live-device, or hardware
claim.
