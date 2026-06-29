# Risk, Ethics, and Scope

## Scope

NeuroDecodeKit is a research/developer tool for making non-invasive neural decoding datasets easier to inspect and benchmark. It is not a medical device, not a clinical diagnostic system, and not a consumer “mind reading” product.

## Important limitations

- Brain2Qwerty v1 data comes from healthy adult volunteers typing briefly memorized sentences.
- v1 uses keystroke-aligned windows, so the system is partly tied to motor execution and timing.
- MEG hardware is specialized and not consumer-ready.
- EEG is more accessible but substantially noisier for this task in the published v1 results.

## Privacy posture

Treat brain data as highly sensitive even when de-identified.

Rules:

- Do not attempt subject identification.
- Do not upload derived neural features by default.
- Do not include raw data in Git.
- Do not publish subject-level examples without checking dataset terms.
- Prefer aggregate reports unless a subject-level analysis is necessary.

## Licensing posture

The public Brain2Qwerty code and SpanishBCBL dataset are released under CC BY-NC 4.0 according to their public pages. Treat all work using those artifacts as noncommercial research unless separate rights are obtained.

## Communication posture

Use careful language:

Good:

```text
"decodes typed sentence production signals from MEG/EEG under a controlled task"
```

Avoid:

```text
"reads arbitrary thoughts"
"consumer mind-reading"
"clinical-ready communication restoration"
```
