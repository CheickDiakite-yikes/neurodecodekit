# SPEECH-REPRO-1 timing diagnosis and recovery feasibility

September 21, 2026. **The blocker is a reader-format assumption, not a decoding
result.** A label-blind audit explains the stopped run: participant 3's covert
recordings contain concatenated original trials with retained trigger activity.
Our reader incorrectly selects the continuous-recording path whenever it finds
a trigger rise. No production extraction fix or recovery is activated here.

## Evidence

All 13 EDF SHA-256 identities and 13 event-file Git identities still match the
pinned manifest. Eleven recordings have exact event/selected-trigger agreement
and retain their existing continuous buffer boundaries. The remaining two are:

| Participant 3, covert | Original trials | Trigger rises | EDF samples | Timing signature |
|---|---:|---:|---:|---|
| Calibration, 20230524 | 100 | 160 | 288,000 | Exactly 100 consecutive 2,880-sample buffers |
| Online, 20230524 | 50 | 77 | 144,128 | 50 such buffers plus 128 trailing samples |

Both event sequences begin at zero and advance exactly 2,880 samples. None of
their event samples matches the last N rising edges; the discrepancies are not
a constant offset. All 13 recordings have in-bounds original buffers under the
source-supported timing routes. No shifting, dropping or relabeling is needed
to define those buffers.

This interpretation is corroborated by the pinned author's
[converter](https://github.com/arayabrain/uhd-gmail-public/blob/0dca00584c528b288392684dcec0d496b6aa4951/bids/convert_to_bids.py):
`load_npy_concatenated` joins complete 139-channel, 2,880-sample trials, retaining
the trigger channel; `create_events_from_npy` separately places events on the
fixed trial grid. Trigger activity therefore does not establish continuous
acquisition. The audit's route names are classifications based on this source
code and timing evidence, not independently supplied acquisition metadata.

The source-consistency checks used only onset fields and decoded TRIGGER
samples. Hash verification read complete files as opaque bytes; no label fields
were parsed, no EEG/auxiliary features were decoded, and private targets were
not opened. No training, prediction or scoring ran. The
[aggregate timing receipt](../registries/speech_reproduction_timing_audit.v0.json)
is reproducible with `scripts/audit_speech_reproduction_timing.py`; seven
generated-only tests cover its timing assumptions and refusal cases.

Separately, a read-only checkpoint audit used `torch.load(weights_only=True)`
and the existing canonical state hash, without model execution. All **50/50**
saved states match their five pair reports, all tensors are finite, and all
**20/20** selected ensemble hashes match. Each fold report records 100 epochs.
The serialized checkpoints total 2,808,200 bytes; tensor payload is 2,491,800
bytes. These are integrity findings, not evidence of predictive performance.

## Feasible recovery, pending authorization

The next useful action is to finish the original scientific comparison, not
start a different experiment. A narrowly scoped recovery should:

1. Recognize the exact concatenated-buffer timing signature independently of
   retained triggers. Keep continuous alignment strict. Validate all 13 timing
   routes before any new fit; preserve the original action crop and all-channel
   padding checks. This audit verified the 128 trailing samples only in TRIGGER,
   not EEG/auxiliary channels, so complete extraction is not yet proven.
2. Reuse the five completed pairs' 50 hash-matching EEGNet checkpoints and their
   original four-fold selections. Re-extract unchanged features, refit the fixed
   compact ridge comparators deterministically, and regenerate predictions.
   The old probabilities and compact models were RAM-only; no saved probability
   hash exists, so bit-identical reconstruction cannot be claimed.
3. Train only the remaining ten EEGNet folds, with the same 100 epochs, seed,
   folds and settings. Keep all participants, both conditions, controls and
   endpoints unchanged. Do not infer a runtime guarantee from this audit.
4. Preserve the failed invocation, its failure marker and sealed targets.
   Record any explicitly authorized recovery separately with bounded resource
   limits. Only complete predictions may be frozen and pushed before one score;
   partial scoring and automatic retry remain prohibited.

The user authorized this diagnosis, not implementation or resumption. The
heartbeat remains paused. The [failure record](SPEECH_REPRODUCTION_EXECUTION_FAILURE.md)
is preserved; its failure marker still has SHA-256
`cc260c268518fe2764132a57f83bf4b519ba07003c04192f036be45648fc33b6`.

## Scientific belief update

This reduces uncertainty about whether the fixed dataset selection is
extractable and whether completed training can be reused. It does **not**
change our belief about EEG word decoding: reference reproduction and EEG's
increment beyond measured nuisance signals are both still untested. The next
milestone remains the complete held-out result, including all nulls. Even a
positive result would not establish cortical origin, cue-independent thoughts,
clinical utility or generalization to unseen people.
