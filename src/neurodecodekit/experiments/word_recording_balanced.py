"""D2 discovery sensitivity: D1 engine with only class-balanced logistic heads.

Keeps D1's source file and result immutable. Explicit dependency injection reuses
its exact splitting, features, random controls, resource sandbox and scorer.
The worker entry point is this adapter, so child processes retain the treatment.
"""

from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location(
    "recording_engine", Path(__file__).with_name("word_recording_diagnostic.py")
)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
original_dump = engine.dump


def balanced_fit(train, labels, test):
    import warnings
    import numpy as np
    from sklearn.decomposition import PCA
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.exceptions import ConvergenceWarning

    if min(train.shape) <= 8 or not np.isfinite(train).all() or not np.isfinite(test).all():
        raise ValueError("Invalid PCA8 inputs")
    model = make_pipeline(
        StandardScaler(),
        PCA(8, whiten=True, svd_solver="randomized", random_state=engine.SEED),
        LogisticRegression(C=0.1, max_iter=2000, tol=1e-8, solver="lbfgs", class_weight="balanced"),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(train, labels)
    if not np.all(model.named_steps["pca"].explained_variance_ > 1e-12):
        raise ValueError("Training rank insufficient for PCA8")
    if model.classes_.tolist() != list(engine.CLASSES):
        raise ValueError("Missing readout class")
    return model.predict_proba(test)


def dump(path, value):
    if isinstance(value, dict) and value.get("experiment") == "WORD-RECORDING-D1":
        value = dict(
            value,
            experiment="WORD-RECORDING-D2",
            parent="WORD-RECORDING-D1",
            treatment="class_weight=balanced in every learned logistic head only",
        )
    original_dump(path, value)


def main():
    # run_worker uses __file__ to launch its child. Both adapters occupy the same
    # package depth; replacing the entry point preserves repository resolution.
    engine.__file__ = __file__
    engine.fit = balanced_fit
    engine.dump = dump
    engine.main()


if __name__ == "__main__":
    main()
