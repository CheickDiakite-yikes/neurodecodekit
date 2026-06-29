# Notebook placeholders

Suggested notebook flow:

1. `00_manifest.ipynb` — list HF files and inspect SpanishBCBL path structure.
2. `01_select_tiny.ipynb` — create a tiny selection and dry-run download.
3. `02_extract_windows.ipynb` — load one FIF + logs and create event windows.
4. `03_baseline_report.ipynb` — run tiny baselines and visualize CER/WER/errors.

Keep notebooks thin. Put reusable logic in `src/neurodecodekit/`.
