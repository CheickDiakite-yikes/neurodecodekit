"""Render public D3 aggregates; never load EEG, labels or predictions."""

from pathlib import Path
import html
import json


def main():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    repo = Path(__file__).resolve().parents[1]
    result = json.loads((repo / "registries/word_timing_result.v0.json").read_text())
    early, late = result["early"]["summary"], result["late_summary"]
    out = repo / ".codex_work/word-timing-d3/report"
    out.mkdir(parents=True, exist_ok=True)
    modes = ["joint_hidden", "covariance", "temporal"]
    names = ["TimesFM-3\n(primary)", "Log covariance", "Raw temporal"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.5))
    fig.subplots_adjust(left=0.075, right=0.975, top=0.72, bottom=0.27, wspace=0.28)
    for ax, metric, scale, base, label, upper in (
        (axes[0], "balanced_accuracy", 100, 20, "Balanced accuracy (%) — higher is better", 29),
        (axes[1], "log_loss", 1, np.log(5), "Log loss — lower is better", 2.65),
    ):
        for offset, values, color, title in (
            (-0.19, early, "#176b89", "Early: 0–2 seconds"),
            (0.19, late, "#d78239", "Late: 2–4 seconds"),
        ):
            heights = [values[f"within/{m}"][metric] * scale for m in modes]
            bars = ax.bar(np.arange(3) + offset, heights, 0.34, color=color, label=title)
            ax.bar_label(
                bars,
                fmt="%.2f",
                padding=5,
                fontsize=10,
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.2},
            )
        ax.axhline(base, color="#485055", ls="--", lw=1.2)
        ax.text(
            0.98,
            0.96,
            f"Dashed: uniform {base:.2f}",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
        )
        ax.set(xticks=np.arange(3), xticklabels=names, ylabel=label, ylim=(0, upper))
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis="y", alpha=0.15)
    axes[0].legend(loc="upper left", bbox_to_anchor=(-0.02, 1.27), ncol=2, frameon=False)
    fig.suptitle(
        "Moving earlier did not rescue TimesFM word decoding",
        x=0.075,
        y=0.965,
        ha="left",
        fontsize=20,
        fontweight="bold",
    )
    fig.text(
        0.075, 0.875, "Same 1,198 trials · 12 people · within-recording evaluation", fontsize=12
    )
    fig.text(
        0.075,
        0.045,
        "Temporal accuracy improved, but its probabilities still lost to uniform guessing.\n"
        "Exploratory reused development data; 16–19 training examples per head.\n"
        "Early/late marker windows do not isolate cue versus imagined speech.",
        fontsize=11,
        linespacing=1.5,
        color="#3e494f",
    )
    fig.savefig(out / "timing.png", dpi=160)
    fig.savefig(out / "timing.svg")
    plt.close(fig)
    rows = []
    for arm, a in early.items():
        b = late[arm]
        rows.append(
            f"<tr><td>{html.escape(arm)}</td>"
            f"<td>{a['balanced_accuracy']:.2%}</td><td>{b['balanced_accuracy']:.2%}</td>"
            f"<td>{a['log_loss']:.5f}</td><td>{b['log_loss']:.5f}</td></tr>"
        )
    page = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NeuroDecodeKit — word timing result</title>
<style>body{font:17px/1.5 system-ui;margin:32px auto;padding:0 24px;max-width:1100px;
color:#20333b}img{width:100%}table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:right;padding:8px;border-bottom:1px solid #d9e0e4}
th:first-child,td:first-child{text-align:left}p{max-width:900px}</style>
<h1>The early window did not rescue TimesFM</h1>
<p>TimesFM achieved 18.25% early versus 18.71% late balanced word accuracy.
Uniform guessing is 20%. The primary probability metric also showed no demonstrated
timing advantage: gain 0.00314 nats, descriptive 95% interval −0.01310 to 0.01794.</p>
<img src="timing.png" alt="Early and late accuracy and log loss for three fixed representations">
<p>Raw temporal features improved from 15.75% to 21.00% accuracy. That is a relative
pipeline improvement; its probabilities still lost to uniform and noise controls,
and shuffled-adjusted timing intervals included zero. Useful word decoding remains
unproven. The data do not separately timestamp reading and imagined speech.</p>
<h2>All stored arms</h2><p>Equal-person means; 12 people, 48 recordings, 1,198 trials.
Cross means a matched donor recording from the same person. Late scores reuse public
D2 aggregates; no late models or scores were rerun. Noise, prior and metadata controls
matched exactly. All intervals are exploratory and unadjusted.</p>
<table><thead><tr><th>Arm</th><th>Early accuracy</th><th>Late accuracy</th>
<th>Early log loss</th><th>Late log loss</th></tr></thead><tbody>"""
    page += "".join(rows) + "</tbody></table></html>"
    (out / "index.html").write_text(page)
    print(out / "index.html")


if __name__ == "__main__":
    main()
