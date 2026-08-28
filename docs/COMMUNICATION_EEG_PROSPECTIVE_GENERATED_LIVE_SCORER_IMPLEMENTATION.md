# COMM-P0-G Endpoint-Separated Live Scorer

Recorded: 2026-08-28

Status: generated-only implementation committed on the Codex branch; exact
remote-green proof is recorded separately after CI completes.

## Correction implemented

The earlier aggregate scorer pooled replication live rows across prompted and
free-choice endpoints. That was unsafe because a strong prompted result could
make a weak free-choice result look healthier than it was.

The additive live scorer now:

- binds only independent-replication live rows;
- validates a complete condition-by-item prediction inventory against a rebuilt
  prediction freeze;
- accepts one scorer-only target delivery and rejects repeated delivery or score;
- computes free-choice and prompted classification and operational summaries
  separately;
- counts inactive/null intervals exactly once across both endpoints;
- makes `free_choice_intend` the sole primary live gate;
- records prompted live performance as a non-rescuing diagnostic;
- returns only aggregate, target-free output;
- keeps `end_to_end_latency_measured=false` because every timing value is
  generated.

Focused tests include the decisive negative case: perfect prompted performance
cannot rescue a failed free-choice live endpoint.

## Scope boundary

This is scorer architecture over fictional generated rows. It does not access a
person, device, voice, real/private path, EEG sample, provider, or network. It
does not run the registered official qualification and it does not change the
sole active Tier C packet.

Engineering capability added: live communication accounting now preserves the
scientifically important distinction between prompted intent and free choice.

Scientific claim not established: No real live communication, EEG-specific
information, unseen-person performance, device latency, or clinical result was
measured.
