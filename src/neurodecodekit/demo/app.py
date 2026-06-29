"""Gradio demo scaffold.

Run with:

    pip install -e '.[demo]'
    python -m neurodecodekit.demo.app
"""

from __future__ import annotations

from neurodecodekit.evaluation.keyboard import aligned_keyboard_distance
from neurodecodekit.evaluation.metrics import summarize_text_metrics


def score_text(target: str, prediction: str) -> dict[str, float | bool]:
    metrics = summarize_text_metrics(target, prediction)
    metrics["keyboard_distance"] = aligned_keyboard_distance(target, prediction)
    return metrics


def main() -> None:  # pragma: no cover - optional UI
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError("Install demo dependencies with `pip install -e '.[demo]'`.") from exc

    with gr.Blocks(title="NeuroDecodeKit demo") as demo:
        gr.Markdown("# NeuroDecodeKit text metric demo")
        gr.Markdown("This v0 demo scores target vs decoded text. Neural trace visualization comes later.")
        target = gr.Textbox(label="Target", value="HOLA MUNDO")
        prediction = gr.Textbox(label="Prediction", value="HOLA MUNCO")
        out = gr.JSON(label="Metrics")
        btn = gr.Button("Score")
        btn.click(score_text, inputs=[target, prediction], outputs=out)
    demo.launch()


if __name__ == "__main__":
    main()
