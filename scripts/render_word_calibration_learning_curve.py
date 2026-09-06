"""Render D4 public aggregate means; no data, models or scoring."""

from pathlib import Path
import html
import json


def main():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    repo = Path(__file__).resolve().parents[1]
    result = json.loads((repo / "registries/word_calibration_result.v0.json").read_text())
    summary, sizes = result["summary"], result["sizes"]
    out = repo / ".codex_work/word-calibration-d4/report"
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.6))
    fig.subplots_adjust(left=0.075, right=0.97, top=0.69, bottom=0.28, wspace=0.26)
    styles = [
        ("joint_hidden", "TimesFM + real labels", "#126887", "-", "o"),
        ("joint_hidden_shuffled", "TimesFM + shuffled labels", "#95699c", "--", "s"),
        ("joint_hidden_noise", "Gaussian features", "#cd7634", "-.", "^"),
        ("metadata", "Trial-position metadata", "#648775", ":", "d"),
        ("uniform", "Uniform / training prior", "#41484c", "--", None),
    ]
    for ax, metric, scale, ylabel in (
        (axes[0], "log_loss", 1, "Log loss — lower is better"),
        (axes[1], "balanced_accuracy", 100, "Balanced accuracy (%) — higher is better"),
    ):
        for arm, label, color, linestyle, marker in styles:
            values = [summary[f"late/{n}/{arm}"][metric] * scale for n in sizes]
            ax.plot(
                sizes,
                values,
                color=color,
                ls=linestyle,
                marker=marker,
                lw=2.4 if arm == "joint_hidden" else 1.6,
                label=label,
            )
        ax.set(
            xticks=sizes,
            xlabel="Calibration examples from the same three donor recordings",
            ylabel=ylabel,
        )
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.15)
    axes[0].set_ylim(1.603, 1.65)
    axes[1].set_ylim(16, 24)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper left",
        bbox_to_anchor=(0.065, 0.83),
        ncol=3,
        frameon=False,
        fontsize=10,
    )
    fig.suptitle(
        "More calibration did not establish word decoding",
        x=0.075,
        y=0.96,
        ha="left",
        fontsize=20,
        fontweight="bold",
    )
    fig.text(
        0.075,
        0.875,
        "Primary late-window TimesFM comparison · same 1,198 evaluation trials at every size",
        fontsize=11,
    )
    fig.text(
        0.075,
        0.065,
        "Probability loss improved, but shuffled labels showed a similar improvement.\n"
        "At 60 examples: 19.58% accuracy versus 20% uniform guessing; no clear log-loss advantage.\n"
        "12 people · reused development data · fixed model size and mean-loss penalty · descriptive means",
        fontsize=11,
        color="#39474e",
        linespacing=1.5,
    )
    fig.savefig(out / "calibration.png", dpi=160)
    fig.savefig(out / "calibration.svg")
    plt.close(fig)
    rows = []
    for window in ("late", "early"):
        for arm in result["freeze"]["arms"]:
            values = [summary[f"{window}/{n}/{arm}"] for n in sizes]
            cells = "".join(
                f"<td>{v['balanced_accuracy']:.2%}</td><td>{v['log_loss']:.5f}</td>" for v in values
            )
            rows.append(f"<tr><td>{html.escape(window + '/' + arm)}</td>{cells}</tr>")
    page = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NeuroDecodeKit — calibration learning curve</title>
<style>body{font:17px/1.5 system-ui;margin:32px auto;padding:0 24px;max-width:1150px;
color:#20333b}img{width:100%}table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:right;padding:8px;border-bottom:1px solid #d9e0e4}
th:first-child,td:first-child{text-align:left}.table{overflow:auto}</style>
<h1>Four times more calibration did not establish word decoding</h1>
<p>TimesFM's primary word accuracy was <b>21.10% → 18.92% → 19.58%</b> at
15, 30 and 60 examples; uniform guessing is 20%. Probability loss improved,
but the gain beyond shuffled labels was unresolved: 0.00220 nats,
descriptive 95% interval −0.00911 to 0.01293.</p>
<img src="calibration.png" alt="TimesFM calibration curves and matched controls">
<p>This tests extra examples using the same three donor recordings, identical
held-out recordings, fixed model size and constant regularization on mean loss.
It does not test new people, isolated imagined speech or open-ended text.</p>
<h2>All representations and controls</h2>
<p>Accuracy is higher-is-better; log loss is lower-is-better. All six real
feature/window mean log losses at 60 examples remained worse than uniform 1.60944.
These are equal-person averages over 12 people, 48 recordings and 1,198 reused
development trials. The split differs from D2/D3; compare training sizes within D4.</p>
<div class="table"><table><thead><tr><th>Window / arm</th>
<th>15 accuracy</th><th>15 loss</th><th>30 accuracy</th><th>30 loss</th>
<th>60 accuracy</th><th>60 loss</th></tr></thead><tbody>"""
    page += "".join(rows) + "</tbody></table></div></html>"
    (out / "index.html").write_text(page)
    print(out / "index.html")


if __name__ == "__main__":
    main()
