"""Local artifact-backed NeuroDecodeKit evidence console."""

from __future__ import annotations

import argparse
import difflib
import html
import json
import resource
import sys
import time
from pathlib import Path
from typing import Any

from neurodecodekit.demo.evidence import DemoEvidence, load_demo_evidence
from neurodecodekit.evaluation.keyboard import aligned_keyboard_distance
from neurodecodekit.evaluation.metrics import summarize_text_metrics


DEMO_TITLE = "NeuroDecodeKit Evidence Console"
METRIC_HEADERS = ["Metric", "Value", "Meaning"]
EVIDENCE_HEADERS = [
    "Evidence",
    "Domain",
    "Rows",
    "Method CER",
    "Comparator CER",
    "Delta",
    "Uncertainty",
    "Interpretation",
]
PROVENANCE_HEADERS = ["Artifact", "Local path", "SHA-256"]
SIGNAL_COLORS = ("#0F766E", "#2563EB", "#B45309", "#BE123C", "#6D28D9", "#374151")


def score_text(target: str, prediction: str) -> dict[str, float | bool]:
    """Score editable text without changing the recorded artifact."""

    metrics = summarize_text_metrics(target, prediction)
    metrics["keyboard_distance"] = aligned_keyboard_distance(target, prediction)
    return metrics


def build_demo(
    project_root: str | Path,
    *,
    evidence: DemoEvidence | None = None,
):
    """Build the Gradio Blocks app while keeping Gradio an optional import."""

    try:
        import gradio as gr
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Install demo dependencies with `pip install -e '.[demo]'`."
        ) from exc

    bundle = evidence or load_demo_evidence(project_root)
    available_channels = bundle.channel_names
    default_channels = available_channels[:4]
    initial = _render_example(bundle, 0, default_channels, None)
    calibration_figure = _calibration_figure(bundle)
    proof = bundle.proof_summary()
    with gr.Blocks(
        title=DEMO_TITLE,
        fill_width=True,
        analytics_enabled=False,
    ) as demo:
        gr.HTML(_header_html(), elem_id="ndk-header")
        gr.HTML(_proof_strip_html(proof), elem_id="ndk-proof-strip")

        with gr.Tabs(elem_id="ndk-tabs"):
            with gr.Tab("Example", id="example"):
                with gr.Row(equal_height=False):
                    with gr.Column(scale=4, min_width=260):
                        example_picker = gr.Dropdown(
                            choices=[(example.label, example.display_index) for example in bundle.examples],
                            value=0,
                            label="Held-out synthetic example",
                            filterable=True,
                        )
                        channels = gr.Dropdown(
                            choices=available_channels,
                            value=default_channels,
                            multiselect=True,
                            label="Visible signal channels",
                            max_choices=len(available_channels),
                        )
                        target = gr.Textbox(
                            value=initial[1],
                            label="Target",
                            interactive=False,
                            lines=2,
                        )
                        prediction = gr.Textbox(
                            value=initial[2],
                            label="Prediction under review",
                            interactive=True,
                            lines=2,
                        )
                        recorded_prediction = gr.State(initial[2])
                        restore = gr.Button("Restore recorded prediction", size="sm")
                    with gr.Column(scale=8, min_width=360):
                        signal_plot = gr.Plot(
                            value=initial[0],
                            label="Synthetic continuous sentence signal",
                            elem_id="ndk-signal-plot",
                        )
                        metrics = gr.Dataframe(
                            value=initial[3],
                            headers=METRIC_HEADERS,
                            datatype=["str", "str", "str"],
                            interactive=False,
                            wrap=True,
                            row_count=4,
                            column_count=3,
                            column_widths=[80, 70, 160],
                            elem_id="ndk-metrics",
                        )
                diff_view = gr.HTML(initial[4], elem_id="ndk-diff")
                example_status = gr.Markdown(initial[5], elem_id="ndk-example-status")

            with gr.Tab("Evidence", id="evidence"):
                gr.Markdown("## Aggregate evidence")
                evidence_table = gr.Dataframe(
                    value=bundle.aggregate_rows(),
                    headers=EVIDENCE_HEADERS,
                    datatype=["str", "str", "number", "str", "str", "str", "str", "str"],
                    interactive=False,
                    wrap=True,
                    column_widths=[190, 100, 70, 90, 100, 85, 150, 190],
                    max_height=430,
                    elem_id="ndk-evidence-table",
                )
                gr.Plot(
                    value=calibration_figure,
                    label="Loop 16 validation calibration curve",
                    elem_id="ndk-calibration-plot",
                )
                gr.Markdown(_evidence_boundary_markdown(bundle), elem_id="ndk-evidence-boundary")

            with gr.Tab("Provenance", id="provenance"):
                gr.Markdown("## Local artifact provenance")
                provenance = gr.Dataframe(
                    value=bundle.provenance_rows(),
                    headers=PROVENANCE_HEADERS,
                    datatype=["str", "str", "str"],
                    interactive=False,
                    wrap=True,
                    column_widths=[170, 470, 430],
                    max_height=420,
                    elem_id="ndk-provenance-table",
                )
                gr.JSON(value=proof, label="Proof contract", elem_id="ndk-proof-json")

        def select_example(display_index: int, selected_channels: list[str] | None):
            rendered = _render_example(bundle, display_index, selected_channels, None)
            return (*rendered, rendered[2])

        def select_channels(display_index: int, selected_channels: list[str] | None):
            return _signal_figure(bundle, display_index, selected_channels)

        def rescore(target_value: str, prediction_value: str, recorded_value: str):
            return _metric_rows(target_value, prediction_value), _diff_html(
                target_value,
                prediction_value,
            ), _comparison_status(
                target_value,
                prediction_value,
                recorded_value,
            )

        def restore_prediction(target_value: str, recorded_value: str):
            return (
                recorded_value,
                _metric_rows(target_value, recorded_value),
                _diff_html(target_value, recorded_value),
                _comparison_status(target_value, recorded_value, recorded_value),
            )

        example_picker.change(
            select_example,
            inputs=[example_picker, channels],
            outputs=[
                signal_plot,
                target,
                prediction,
                metrics,
                diff_view,
                example_status,
                recorded_prediction,
            ],
            queue=False,
            show_progress="hidden",
        )
        channels.change(
            select_channels,
            inputs=[example_picker, channels],
            outputs=signal_plot,
            queue=False,
            show_progress="hidden",
        )
        prediction.change(
            rescore,
            inputs=[target, prediction, recorded_prediction],
            outputs=[metrics, diff_view, example_status],
            queue=False,
            show_progress="hidden",
            trigger_mode="always_last",
        )
        restore.click(
            restore_prediction,
            inputs=[target, recorded_prediction],
            outputs=[prediction, metrics, diff_view, example_status],
            queue=False,
            show_progress="hidden",
        )

        _ = evidence_table, provenance
    return demo


def audit_demo(
    project_root: str | Path,
    *,
    evidence: DemoEvidence | None = None,
) -> dict[str, Any]:
    """Build the complete app without launching a server and report resources."""

    started_at = time.perf_counter()
    bundle = evidence or load_demo_evidence(project_root)
    load_sec = time.perf_counter() - started_at
    demo = build_demo(project_root, evidence=bundle)
    config = demo.get_config_file()
    serialized = json.dumps(config, sort_keys=True, default=str)
    demo.close()
    required_text = (
        "Held-out synthetic example",
        "Synthetic continuous sentence signal",
        "Aggregate evidence",
        "Local artifact provenance",
        "Proof contract",
    )
    checks = {
        "synthetic_cache_loaded": bundle.sentence_cache.summary.kind
        == "synthetic_continuous_sentences",
        "nineteen_held_out_examples": len(bundle.examples) == 19,
        "real_reports_are_aggregate_only": bundle.proof_summary()["real_results_displayed"]
        == "aggregate metrics only",
        "predictive_confidence_is_not_fabricated": bundle.proof_summary()[
            "predictive_confidence"
        ].startswith("unavailable"),
        "noncausal_boundary_visible": "Noncausal" in serialized,
        "required_ui_surfaces_present": all(value in serialized for value in required_text),
        "no_real_model_run_triggered": bundle.proof_summary()[
            "real_holdout_model_runs_triggered"
        ]
        == 0,
        "no_network_data_fetch": bundle.proof_summary()["network_data_fetches"] == 0,
    }
    return {
        "schema": {"name": "neurodecodekit-demo-audit", "version": 1},
        "proof_posture": bundle.proof_summary()["proof_posture"],
        "project_root": str(bundle.project_root),
        "gradio_version": _gradio_version(),
        "load_evidence_sec": round(load_sec, 6),
        "build_total_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "component_count": len(config.get("components") or []),
        "dependency_count": len(config.get("dependencies") or []),
        "source_cache_bytes": bundle.sentence_cache.summary.bytes,
        "display_examples": len(bundle.examples),
        "checks": checks,
        "gate_passed": all(checks.values()),
        "warnings": [
            "synthetic_example_only",
            "real_results_are_aggregate_only",
            "model_confidence_unavailable",
            "decoder_is_noncausal",
            "not_arbitrary_thought_decoding",
            "not_at_home_hardware_evidence",
        ],
    }


def launch_demo(
    project_root: str | Path,
    *,
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
    inbrowser: bool = False,
    prevent_thread_lock: bool = False,
):
    """Launch the local-only demo with remote sharing disabled."""

    import gradio as gr

    demo = build_demo(project_root)
    return demo.launch(
        server_name=server_name,
        server_port=server_port,
        share=False,
        inbrowser=inbrowser,
        prevent_thread_lock=prevent_thread_lock,
        max_threads=4,
        show_error=True,
        quiet=False,
        footer_links=[],
        theme=_demo_theme(gr),
        css=_demo_css(),
    )


def main() -> None:  # pragma: no cover - optional UI
    parser = argparse.ArgumentParser(description=DEMO_TITLE)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--inbrowser", action="store_true")
    args = parser.parse_args()
    launch_demo(
        args.project_root,
        server_name=args.host,
        server_port=args.port,
        inbrowser=args.inbrowser,
    )


def _render_example(
    evidence: DemoEvidence,
    display_index: int,
    channel_names: list[str] | None,
    prediction_override: str | None,
):
    example = evidence.example(display_index)
    prediction = example.prediction if prediction_override is None else prediction_override
    return (
        _signal_figure(evidence, display_index, channel_names),
        example.target,
        prediction,
        _metric_rows(example.target, prediction),
        _diff_html(example.target, prediction),
        _example_status(evidence, display_index),
    )


def _signal_figure(
    evidence: DemoEvidence,
    display_index: int,
    channel_names: list[str] | None,
):
    import matplotlib.pyplot as plt
    import numpy as np

    selected = channel_names or evidence.channel_names
    rows = evidence.signal_rows(display_index, selected)
    time_values = rows["time_sec"]
    signals = rows["signals"]
    figure, axis = plt.subplots(figsize=(9.2, 3.4), layout="constrained")
    for index, (name, values) in enumerate(zip(rows["channel_names"], signals)):
        robust_scale = float(np.quantile(np.abs(values), 0.95)) or 1.0
        offset = (len(rows["channel_names"]) - index - 1) * 2.4
        axis.plot(
            time_values,
            values / robust_scale + offset,
            color=SIGNAL_COLORS[index % len(SIGNAL_COLORS)],
            linewidth=1.25,
        )
    offsets = [
        (len(rows["channel_names"]) - index - 1) * 2.4
        for index in range(len(rows["channel_names"]))
    ]
    axis.set_yticks(offsets, [_plot_channel_label(name) for name in rows["channel_names"]])
    axis.set_xlabel("Time (seconds)")
    axis.set_ylabel("Channel (individually scaled)")
    axis.set_title(
        f"Held-out synthetic row {rows['source_row_index']} | {rows['duration_sec']:.2f} sec",
        loc="left",
        fontsize=11,
        fontweight="bold",
    )
    axis.grid(axis="x", color="#D1D5DB", linewidth=0.65, alpha=0.8)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="both", labelsize=8)
    axis.set_facecolor("#FFFFFF")
    figure.set_facecolor("#FFFFFF")
    plt.close(figure)
    return figure


def _calibration_figure(evidence: DemoEvidence):
    import matplotlib.pyplot as plt

    rows = evidence.calibration_rows()
    labels = {
        "stationary_diagonal": "Stationary diagonal",
        "stationary_channel_mixing": "Channel mixing",
        "within_row_time_varying": "Within-row drift",
    }
    colors = {
        "stationary_diagonal": "#0F766E",
        "stationary_channel_mixing": "#BE123C",
        "within_row_time_varying": "#B45309",
    }
    figure, axis = plt.subplots(figsize=(9.2, 3.8), layout="constrained")
    for family in labels:
        family_rows = [row for row in rows if row["shift_family"] == family]
        axis.plot(
            [row["calibration_rows"] for row in family_rows],
            [row["median_adapted_cer"] for row in family_rows],
            marker="o",
            linewidth=1.8,
            color=colors[family],
            label=f"{labels[family]} adapted",
        )
        axis.plot(
            [row["calibration_rows"] for row in family_rows],
            [row["median_identity_cer"] for row in family_rows],
            linestyle="--",
            linewidth=1.0,
            color=colors[family],
            alpha=0.55,
        )
    selected = evidence.calibration_report["decision"]["selected_calibration_rows"]
    if selected is not None:
        axis.axvline(float(selected), color="#111827", linewidth=1.0, linestyle=":")
    axis.set_xscale("log", base=2)
    axis.set_xticks([1, 2, 4, 8, 16, 32], ["1", "2", "4", "8", "16", "32"])
    axis.set_xlabel("Unlabeled calibration sentences")
    axis.set_ylabel("Median validation CER")
    axis.set_ylim(bottom=0)
    axis.set_title("Static robust affine helps only the shift family it can represent", loc="left")
    axis.grid(color="#D1D5DB", linewidth=0.65, alpha=0.8)
    axis.legend(frameon=False, fontsize=8, ncols=3, loc="upper center")
    axis.spines[["top", "right"]].set_visible(False)
    figure.set_facecolor("#FFFFFF")
    plt.close(figure)
    return figure


def _metric_rows(target: str, prediction: str) -> list[list[str]]:
    values = score_text(target, prediction)
    return [
        ["CER", _format_metric(values["cer"]), "character edits / target characters"],
        ["WER", _format_metric(values["wer"]), "word edits / target words"],
        [
            "Keyboard distance",
            _format_metric(values["keyboard_distance"]),
            "aligned key-position error; diagnostic only",
        ],
        ["Exact match", "yes" if values["exact_match"] else "no", "normalized text equality"],
    ]


def _diff_html(target: str, prediction: str) -> str:
    matcher = difflib.SequenceMatcher(a=target, b=prediction)
    target_parts: list[str] = []
    prediction_parts: list[str] = []
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        target_value = html.escape(target[a0:a1])
        prediction_value = html.escape(prediction[b0:b1])
        if opcode == "equal":
            target_parts.append(f"<span class='same'>{target_value}</span>")
            prediction_parts.append(f"<span class='same'>{prediction_value}</span>")
        elif opcode == "replace":
            target_parts.append(f"<span class='removed'>{target_value}</span>")
            prediction_parts.append(f"<span class='added'>{prediction_value}</span>")
        elif opcode == "delete":
            target_parts.append(f"<span class='removed'>{target_value}</span>")
        elif opcode == "insert":
            prediction_parts.append(f"<span class='added'>{prediction_value}</span>")
    return (
        "<section class='diff-block' aria-label='Character comparison'>"
        "<div class='diff-label'>Character comparison</div>"
        f"<div class='diff-row'><strong>Target</strong><code>{''.join(target_parts)}</code></div>"
        f"<div class='diff-row'><strong>Prediction</strong><code>{''.join(prediction_parts)}</code></div>"
        "</section>"
    )


def _example_status(evidence: DemoEvidence, display_index: int) -> str:
    example = evidence.example(display_index)
    return (
        f"**Recorded artifact:** held-out synthetic row `{example.source_row_index}` · "
        f"trial `{example.trial_index}` · `{example.input_length}` valid frames · "
        f"`{example.duration_sec:.2f}` seconds  \n"
        "**Predictive confidence:** unavailable; this report stores a greedy CTC sequence, "
        "not a calibrated posterior.  \n"
        "**Scope:** synthetic token motifs, noncausal decoder, typed-sentence surrogate."
    )


def _comparison_status(target: str, prediction: str, recorded_prediction: str) -> str:
    source = "recorded artifact" if prediction == recorded_prediction else "user-edited comparison"
    exact = summarize_text_metrics(target, prediction)["exact_match"]
    return (
        f"**Comparison source:** {source} · **Exact match:** {'yes' if exact else 'no'}  \n"
        "**Predictive confidence:** unavailable; text edits do not create calibrated confidence.  \n"
        "**Scope:** synthetic token motifs, noncausal decoder, typed-sentence surrogate."
    )


def _evidence_boundary_markdown(evidence: DemoEvidence) -> str:
    strict = evidence.strict_real_report["comparisons"]["tiny_ctc_vs_prior_only"]
    cross = evidence.cross_session_report["comparisons"]["tiny_ctc_vs_prior_only"]
    return (
        "### Evidence boundary\n\n"
        f"- Strict real test: `{strict['n_paired_sentences']}` sentences; the tiny CTC differs "
        f"from the prior by `{strict['corpus_cer_delta_a_minus_b']:+.4f}` CER and its interval "
        "crosses zero.\n"
        f"- Same-person session transfer: `{cross['n_paired_sentences']}` sentences; the fixed "
        f"CTC is worse than the prior by `{cross['corpus_cer_delta_a_minus_b']:+.4f}` CER.\n"
        "- Calibration: synthetic stationary benefit does not transfer to channel mixing or "
        "within-row drift.\n"
        "- No real sentence text is displayed in this console."
    )


def _header_html() -> str:
    return (
        "<header class='ndk-header'>"
        "<div><div class='ndk-product'>NeuroDecodeKit</div>"
        "<div class='ndk-title'>Evidence console</div></div>"
        "<div class='ndk-header-note'>Local artifacts only<br>No model training</div>"
        "</header>"
    )


def _proof_strip_html(proof: dict[str, Any]) -> str:
    items = [
        ("Example", "Synthetic"),
        ("Task", "Typed sentence surrogate"),
        ("Decoder", "Noncausal"),
        ("Confidence", "Unavailable"),
        ("Real adapter", "Unauthorized"),
    ]
    rendered = "".join(
        f"<div class='proof-cell'><span>{html.escape(label)}</span>"
        f"<strong>{html.escape(value)}</strong></div>"
        for label, value in items
    )
    return f"<section class='proof-strip' data-posture='{proof['proof_posture']}'>{rendered}</section>"


def _demo_css() -> str:
    return """
    :root { --ndk-ink: #111827; --ndk-muted: #5B6472; --ndk-line: #D7DCE2; }
    .gradio-container { max-width: 1180px !important; margin: 0 auto !important; color: var(--ndk-ink); }
    #ndk-header { margin: 0; }
    .ndk-header { background: #111827; color: white; padding: 16px 20px; display: flex;
      align-items: center; justify-content: space-between; gap: 18px; }
    .ndk-product { font-size: 13px; font-weight: 700; color: #5EEAD4; }
    .ndk-title { color: #F9FAFB !important; font-size: 24px; font-weight: 650;
      letter-spacing: 0; }
    .ndk-header-note { border-left: 1px solid #4B5563; padding-left: 18px; color: #D1D5DB;
      font-size: 12px; line-height: 1.45; text-align: right; }
    #ndk-proof-strip { margin: 0; }
    .proof-strip { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr));
      border: 1px solid var(--ndk-line); border-top: 0; background: #F8FAFC; }
    .proof-cell { min-height: 68px; padding: 12px 14px; border-right: 1px solid var(--ndk-line); }
    .proof-cell:last-child { border-right: 0; }
    .proof-cell span { display: block; color: var(--ndk-muted); font-size: 11px; margin-bottom: 5px; }
    .proof-cell strong { display: block; font-size: 13px; line-height: 1.25; overflow-wrap: anywhere; }
    #ndk-tabs { margin-top: 12px; }
    #ndk-signal-plot { min-height: 360px; }
    #ndk-metrics table { font-size: 12px; }
    .diff-block { border-top: 1px solid var(--ndk-line); border-bottom: 1px solid var(--ndk-line);
      padding: 14px 2px; margin-top: 10px; }
    .diff-label { color: var(--ndk-muted); font-size: 11px; margin-bottom: 8px; }
    .diff-row { display: grid; grid-template-columns: 92px minmax(0, 1fr); gap: 12px;
      align-items: baseline; margin: 6px 0; }
    .diff-row code { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 14px; }
    .removed { background: #FEF3C7; color: #92400E; text-decoration: line-through; }
    .added { background: #FFE4E6; color: #9F1239; }
    .same { color: #1F2937; }
    #ndk-example-status, #ndk-evidence-boundary { color: var(--ndk-muted); font-size: 12px; }
    #ndk-evidence-table table, #ndk-provenance-table table { font-size: 11px; }
    .block, .form { border-radius: 6px !important; }
    @media (max-width: 760px) {
      #ndk-header, #ndk-proof-strip, #ndk-tabs { width: calc(100vw - 64px) !important;
        max-width: calc(100vw - 64px) !important; min-width: 0 !important; }
      #ndk-tabs .row { min-width: 0 !important; flex-wrap: wrap !important; }
      #ndk-tabs .row > .column { width: 100% !important; max-width: 100% !important;
        min-width: 0 !important; flex: 1 1 100% !important; }
      .ndk-header { padding: 14px; }
      .ndk-title { font-size: 20px; }
      .proof-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .proof-cell { border-bottom: 1px solid var(--ndk-line); }
      .diff-row { grid-template-columns: 1fr; gap: 3px; }
      #ndk-signal-plot { min-height: 180px; }
    }
    """


def _demo_theme(gr):
    return gr.themes.Base(
        primary_hue=gr.themes.colors.teal,
        secondary_hue=gr.themes.colors.blue,
        neutral_hue=gr.themes.colors.gray,
        font=["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
    )


def _format_metric(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    return f"{float(value):.4f}"


def _plot_channel_label(name: str) -> str:
    return name.removeprefix("synthetic_sentence_")


def _gradio_version() -> str:
    import gradio

    return str(gradio.__version__)


def _peak_rss_bytes() -> int | None:
    try:
        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (OSError, ValueError):
        return None
    return value if sys.platform == "darwin" else value * 1024


if __name__ == "__main__":
    main()
