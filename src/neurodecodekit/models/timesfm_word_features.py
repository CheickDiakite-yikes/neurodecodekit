"""Three frozen TimesFM-3 feature uses; optional dependencies, local weights only.

Inputs contain only completed EEG windows in volts. No labels, prompts, event
codes, future covariates, network calls, or word generation enter this module.
Official code remains separate; its weights must not be redistributed.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


FEATURE_MODES = ("joint_hidden", "independent_hidden", "forecast_residual")


def resample_windows(windows):
    import numpy as np
    from scipy.signal import resample_poly

    x = np.asarray(windows)
    if x.ndim != 3 or x.shape[1:] != (8, 500) or not np.isfinite(x).all():
        raise ValueError("Expected finite [trials, 8, 500] filtered EEG windows in volts")
    return resample_poly(x.astype(np.float64), 32, 125, axis=-1).astype(np.float32)


def load_frozen_model(vendor_src, checkpoint):
    import torch
    from safetensors.torch import load_file

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.manual_seed(20260905)
    sys.path.insert(0, str(Path(vendor_src).resolve()))
    from timesfm3 import TimesFM3Torch

    config = json.loads((Path(checkpoint) / "config.json").read_text())
    config.update(use_stitching=False, use_linear_detrending=False, use_iterative_cpm_revin=False)
    # The vendor has nonpersistent rotary buffers; meta construction would leave
    # those buffers unmaterialized even after all checkpoint weights are loaded.
    model = TimesFM3Torch(**config)
    model.load_state_dict(
        load_file(str(Path(checkpoint) / "model.safetensors")), strict=True, assign=True
    )
    model.eval().requires_grad_(False)
    return model


def hidden_features(model, windows_uv, *, independent=False):
    """Retain sensor order and the last causal context token of each sensor."""
    import torch

    n = windows_uv.shape[0]
    values = windows_uv.reshape(n * 8, 1, 4, 32) if independent else windows_uv.reshape(n, 8, 4, 32)
    output = model.forward(
        {
            "values": values,
            "masks": torch.zeros_like(values, dtype=torch.bool),
            "patch_is_target": torch.ones(values.shape[:-1], dtype=torch.bool),
        },
        return_aux_outputs=True,
    )["__call__:transformer_output"]
    return output[:, :, -1, :].reshape(n, -1)


def extract_features(model, windows, *, mode):
    """Windows are [B,8,128] at 64 Hz; output is target-free CPU float32."""
    import numpy as np
    import torch

    x = np.asarray(windows, dtype=np.float32)
    if x.ndim != 3 or x.shape[1:] != (8, 128) or not np.isfinite(x).all():
        raise ValueError("Expected finite [trials, 8, 128] resampled windows")
    with torch.inference_mode():
        # TimesFM treats std below 1e-6 as degenerate: use physical microvolts.
        tensor = torch.from_numpy(x.copy()) * 1e6
        if mode in FEATURE_MODES[:2]:
            out = hidden_features(model, tensor, independent=mode == "independent_hidden")
        elif mode == "forecast_residual":
            forecast = model.decode(target=tensor[:, :, :64], horizon=64)
            median = forecast[..., list(model.quantiles).index(0.5)]
            out = (tensor[:, :, 64:] - median).flatten(1)
        else:
            raise ValueError(f"Unknown mode: {mode}")
        result = out.detach().cpu().numpy().copy()
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite TimesFM features")
    return result


def fit_readout(train, labels, test):
    """Same train-only 32-dimensional readout for every numerical feature arm."""
    import numpy as np
    from sklearn.decomposition import PCA
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.exceptions import ConvergenceWarning
    from threadpoolctl import threadpool_limits
    import warnings

    if min(train.shape) < 32 or not np.isfinite(train).all() or not np.isfinite(test).all():
        raise ValueError("Need at least 32 finite training rows and feature dimensions")
    model = make_pipeline(
        StandardScaler(),
        PCA(n_components=32, whiten=True, svd_solver="randomized", random_state=20260905),
        LogisticRegression(C=0.1, max_iter=2000, tol=1e-8, solver="lbfgs", random_state=20260905),
    )
    with threadpool_limits(limits=1), warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(train, labels)
        result = model.predict_proba(test)
    return result, model.classes_.tolist()
