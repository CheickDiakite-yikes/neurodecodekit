# Third-Party Notices And Data Terms

NeuroDecodeKit's original source code and documentation are offered under the
Apache License 2.0. That license does **not** relicense third-party software,
datasets, recordings, behavioral logs, models, papers, names, or trademarks.

## Brain2Qwerty

NeuroDecodeKit is an independent developer and research toolkit informed by the
public Brain2Qwerty work. The repository does not vendor the Brain2Qwerty source
tree or model weights. It cites specific public code, paper, and configuration
revisions when a comparison depends on them.

The public Brain2Qwerty repository is separately released under Creative
Commons Attribution-NonCommercial 4.0 International (`CC-BY-NC-4.0`). Review
the upstream license before copying code, using released models, or relying on
upstream assets:

- https://github.com/facebookresearch/brain2qwerty
- https://creativecommons.org/licenses/by-nc/4.0/

## SpanishBCBL / DECOMEG

SpanishBCBL recordings and behavioral logs are not included in this Git
repository. The official dataset page identifies the release as
`CC-BY-NC-4.0`. Local raw data, labels, caches, predictions, and participant-
level derivatives remain governed by the dataset's terms, consent boundary,
and applicable privacy rules:

- https://huggingface.co/datasets/bcbl190626/SpanishBCBL
- https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/studies/spanishbcbl.py

Do not assume that Apache-2.0 permits commercial use of Brain2Qwerty code,
SpanishBCBL data, or derivatives of either. Obtain separate rights where the
upstream license, institutional agreement, consent language, or law requires
them.

## Optional Python Dependencies

MNE-Python, NumPy, SciPy, PyTorch, scikit-learn, Hugging Face Hub, Zarr,
numcodecs, Gradio, and their transitive dependencies are installed separately
through optional dependency groups. They are not vendored here and retain
their own licenses. Consult the exact installed package metadata before
redistributing an environment or binary bundle.

## Contributor Responsibility

Before contributing a dataset adapter, device integration, fixture, screenshot,
report, or benchmark artifact, confirm that you have the right to share it.
Never add raw neural recordings, event/target files, participant data, device
credentials, proprietary SDK files, or derived participant-level features to a
pull request. See `CONTRIBUTING.md` and `SECURITY.md` for the safe contribution
path.
