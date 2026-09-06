"""Render stored public aggregates; never load predictions, labels or EEG."""

from pathlib import Path
import html
import json


def main():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    repo = Path(__file__).resolve().parents[1]
    d1 = json.loads((repo / "registries/word_recording_diagnostic_result.v0.json").read_text())
    d2 = json.loads((repo / "registries/word_recording_balanced_result.v0.json").read_text())
    out = repo / ".codex_work/word-recording-d2/report"
    out.mkdir(exist_ok=True)
    modes = ["joint_hidden", "covariance", "temporal"]
    names = ["TimesFM-3", "Log covariance", "Raw temporal"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, axs = plt.subplots(1, 2, figsize=(12.8, 6.6))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.75, bottom=0.23, wspace=0.26)
    for ax, metric, multiplier, baseline, ylabel in (
        (axs[0], "balanced_accuracy", 100, 20, "Balanced word accuracy (%) — higher is better"),
        (axs[1], "log_loss", 1, np.log(5), "Class-macro log loss — lower is better"),
    ):
        x = np.arange(len(modes))
        for offset, condition, color, label in (
            (-0.19, "within", "#176b89", "Within recording"),
            (0.19, "cross", "#d78239", "Matched donor recording"),
        ):
            values = [d2["summary"][f"{condition}/{m}"][metric] * multiplier for m in modes]
            bars = ax.bar(x + offset, values, 0.34, color=color, label=label)
            ax.bar_label(bars, fmt="%.2f", fontsize=10, padding=5)
        ax.axhline(baseline, color="#41484c", linestyle="--", lw=1.4)
        ax.set_xticks(x, names)
        ax.set_ylabel(ylabel)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis="y", alpha=0.15)
    axs[0].set_ylim(0, 29)
    axs[1].set_ylim(0, 3.6)
    axs[0].text(
        0.98,
        0.96,
        "Dashed line: uniform 20%",
        ha="right",
        va="top",
        transform=axs[0].transAxes,
        fontsize=10,
    )
    axs[1].text(
        0.98,
        0.96,
        "Dashed line: uniform 1.609",
        ha="right",
        va="top",
        transform=axs[1].transAxes,
        fontsize=10,
    )
    fig.suptitle(
        "Useful within-recording word decoding was not demonstrated",
        x=0.07,
        y=0.97,
        ha="left",
        fontsize=19,
        fontweight="bold",
    )
    fig.text(
        0.07,
        0.90,
        "D2: balanced training loss • 12 people • 48 development recordings • 1,198 trials",
        fontsize=12,
    )
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="upper left", bbox_to_anchor=(0.062, 0.86), ncol=2, frameon=False
    )
    fig.text(
        0.07,
        0.125,
        "TimesFM's within-versus-donor accuracy gain: −0.90 percentage points",
        fontsize=12,
        fontweight="bold",
    )
    fig.text(
        0.07,
        0.08,
        "Descriptive participant-bootstrap 95% interval: −4.46 to +2.33 points. "
        "16–19 training trials per fit.",
        fontsize=10,
    )
    fig.text(
        0.07,
        0.035,
        "Reused development data; D2 followed D1. Visible prompts, no EOG/EMG; "
        "no isolated-inner-speech or thought-to-text claim.",
        fontsize=9,
    )
    for ext in ("png", "svg"):
        fig.savefig(out / f"word_recording_results.{ext}", dpi=160)
    plt.close(fig)

    sections = []
    for title, result in (("D1 — original training loss", d1), ("D2 — balanced training loss", d2)):
        rows = []
        for key, v in result["summary"].items():
            rows.append(
                f"<tr><td>{html.escape(key)}</td><td>{v['balanced_accuracy'] * 100:.2f}%</td>"
                f"<td>{v['log_loss']:.5f}</td></tr>"
            )
        sections.append(
            f"<h2>{title}</h2><table><thead><tr><th>Condition / arm</th>"
            "<th>Balanced accuracy</th><th>Log loss</th></tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )
    (out / "report.html").write_text(
        """<!doctype html><meta charset="utf-8">
<title>Word-recording diagnostic</title><style>
body{font:17px/1.5 system-ui,sans-serif;max-width:1100px;margin:45px auto;padding:0 24px;color:#20313b}
h1{font-size:34px;line-height:1.2}h2{margin-top:38px}img{width:100%}
table{width:100%;border-collapse:collapse;font-size:15px}th,td{text-align:left;padding:8px;border-bottom:1px solid #dce2e6}
th{background:#f0f4f6}td:nth-child(n+2){font-variant-numeric:tabular-nums}
</style><h1>No demonstrated word-decoding advantage within recordings</h1>
<p>TimesFM reached 18.71% within a recording and 19.60% with a matched donor recording
after balancing the classifier's training loss. Uniform guessing gives 20% and had
better log loss than every real feature arm. The within-versus-donor TimesFM gap
remains unresolved. Small training sets limit this conclusion.</p>
<img src="word_recording_results.png" alt="Matched within and donor accuracy and log loss">
<p>D1 exposed an EEG-free sampling artifact: its empirical word prior scored 8.92%.
D2 changed only class weighting in the learned heads; the same fixed examples and
controls were retained. Better scores after balancing do not establish neural language
information. Both analyses reuse development data; sessions 2, 5 and 6 stayed closed.</p>
"""
        + "".join(sections)
        + "<p>All intervals are descriptive and exploratory. "
        "Visible prompts and absent EOG/EMG prevent attribution to isolated inner speech.</p>"
    )
    print(out / "report.html")


if __name__ == "__main__":
    main()
