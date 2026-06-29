# Research Brief — Brain2Qwerty Accessibility Layer

This brief is a starting point for modern/future-oriented research. Re-check source pages before publishing because the Brain2Qwerty v2 release and dataset status may change.

## What changed recently

Meta announced Brain2Qwerty v2 as a non-invasive, real-time brain-to-text pipeline using MEG recordings while participants typed. The public Meta blog says v2 was trained on approximately 22,000 sentences from nine participants, each recorded for 10 hours, and reports 61% average word accuracy and 78% word accuracy for the best participant.

Source: https://ai.meta.com/blog/brain2qwerty-brain-ai-human-communication/

## What is public now

The public GitHub repo contains Brain2Qwerty v1 and v2 code. The repo states that Brain2Qwerty v1 data is on Hugging Face and Brain2Qwerty v2 data is under embargo until paper acceptance.

Source: https://github.com/facebookresearch/brain2qwerty

## v1 data reality

The SpanishBCBL Hugging Face dataset is the practical starting point. The dataset card says it contains non-invasive MEG/EEG recordings from healthy adults typing briefly memorized Spanish sentences on a QWERTY keyboard. It lists:

- 35 healthy adult volunteers
- Spanish sentences
- MEG: about 5.1K sentences / 193K characters
- EEG: about 4K sentences / 146K characters
- MEG recordings as `.fif`
- EEG recordings as BrainVision `.vhdr/.eeg/.vmrk`
- behavioral logs as `.mat`
- total size around 262GB
- CC BY-NC 4.0 license

Source: https://huggingface.co/datasets/bcbl190626/SpanishBCBL

## v1 model reality

The Nature Neuroscience paper reports average 29% character error rate with MEG, 65% character error rate with EEG, and 18% CER for the best participants. The model uses 0.5-second windows around keystrokes in the v1 setup, so v1 is not the same as unrestricted thought decoding or fully asynchronous language decoding.

Source: https://www.nature.com/articles/s41593-026-02303-2

## The accessibility gap

The practical bottleneck is not just model sophistication. It is:

```text
large raw files
+ specialized neuroimaging formats
+ event alignment
+ preprocessing choices
+ subject-specific data
+ unclear baselines
+ noncommercial licensing
```

The project opportunity is to make the first research loop small and reproducible.

## Future-facing bet

The durable abstraction may be:

```text
raw neural stream → calibrated neurotokens → text/action model
```

For now, “neurotokens” should be treated as a research interface, not a solved standard. The v0 version can simply be cached event-window embeddings with metadata.

## Useful ecosystem

- MNE-Python / MNE-BIDS for MEG/EEG loading and BIDS-compatible workflows: https://mne.tools/mne-bids/stable/index.html
- Braindecode for PyTorch-based EEG/ECoG/MEG deep-learning baselines: https://braindecode.org/
- Hugging Face Hub helpers for listing/selective download: https://huggingface.co/docs/huggingface_hub/
- Hugging Face streaming docs are useful conceptually, though SpanishBCBL does not expose a normal dataset viewer because the files are raw neuroimaging formats: https://huggingface.co/docs/datasets/en/stream
- Zarr for chunked, compressed N-dimensional arrays: https://zarr.dev/

## High-signal research loops

### 1. Accessibility/compression loop

Question: how small can the dataset slice/cache become while preserving meaningful decoding signal?

Metrics:

- bytes downloaded
- bytes cached
- seconds to first batch
- CER/WER
- accuracy retained per GB

### 2. Baseline honesty loop

Question: how much performance comes from neural signal vs language prior?

Required baselines:

- random character baseline
- frequency baseline
- keyboard-neighbor baseline
- language-model-only baseline
- neural-only tiny classifier
- neural + simple language cleanup

### 3. Subject adaptation loop

Question: how many minutes of data are needed for a new subject?

Metrics:

- CER/WER vs calibration minutes
- train-on-A, adapt-to-B performance
- adapter-only fine-tuning performance

### 4. Hardware realism loop

Question: can the workflow generalize beyond lab MEG?

Treat this as research only. Do not imply consumer-readiness.
