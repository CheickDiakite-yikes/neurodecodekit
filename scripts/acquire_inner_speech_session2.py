"""Fixed, one-shot ses-02 acquisition; dry-run opens no manifest or source.

The predecessor's transport/hash/header/budget lifecycle is reused unchanged.
No resume, retries, alternate session, source endpoint or output root is exposed.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
BASE = Path(r"C:\Users\80714\AppData\Local\NeuroDecodeKit")
OUTPUT_NAME = "ds003626_v2_1_2_ses02_20261002"


def canonical_output(output, require):
    """Admit only direct AppData or its exact current Codex package-cache alias."""
    parent = BASE.parent.absolute()
    require(parent.resolve(strict=True) == parent and BASE.is_dir(), "local_parent_identity")
    root = BASE.resolve(strict=True)
    require(root.is_relative_to(parent) and "onedrive" not in str(root).lower(),
            "local_root_containment")
    parts = root.relative_to(parent).parts
    direct = root == BASE.absolute()
    packaged = (len(parts) == 5 and parts[0].casefold() == "packages" and
                re.fullmatch(r"OpenAI\.Codex_[a-z0-9]{13}", parts[1]) is not None and
                tuple(p.casefold() for p in parts[2:]) ==
                ("localcache", "local", BASE.name.casefold()))
    require(direct or packaged, "unrecognized_local_redirect")
    require(root.resolve(strict=True) == root, "canonical_root_changed")
    declared, canonical = BASE / OUTPUT_NAME, root / OUTPUT_NAME
    require(Path(output).absolute() in (declared.absolute(), canonical), "fixed_local_output_required")
    require(declared.resolve() == canonical and canonical.resolve() == canonical,
            "local_output_containment")
    return canonical


def configured_runner():
    spec = importlib.util.spec_from_file_location("inner_speech_session2_acquisition",
                                                REPO / "scripts/acquire_inner_speech.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.ACQUISITION_ID = "INNER-SPEECH-ACQ-S2"
    runner.CONFIGURATION_SCRIPT = Path(__file__).resolve()
    runner.MANIFEST = REPO / "registries/inner_speech_session2_source_manifest.v0.json"
    runner.RESULT = REPO / "registries/inner_speech_session2_acquisition_result.v0.json"
    runner.OUTPUT = BASE / OUTPUT_NAME
    runner.PAYLOAD_BYTES = 6870116352
    runner.PATHS = tuple(f"sub-{i:02d}/ses-02/eeg/sub-{i:02d}_ses-02_task-innerspeech_eeg.bdf"
                         for i in range(1, 11))
    original_acquire = runner.acquire

    def acquire(manifest, output, *, result_path=None, budget=None, opener=None):
        destination = canonical_output(output, runner.require)
        runner.require(result_path is None or Path(result_path).absolute() == runner.RESULT.absolute(),
                       "fixed_result_path_required")
        runner.OUTPUT = destination
        return original_acquire(manifest, destination, result_path=runner.RESULT,
                                budget=budget, opener=opener)

    runner.acquire = acquire
    return runner


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    runner = configured_runner()
    if not args.execute:
        print(json.dumps({"mode": "dry_run", "acquisition_id": runner.ACQUISITION_ID,
            "dataset": "ds003626", "version": "2.1.2", "session": "ses-02",
            "files": list(runner.PATHS), "payload_bytes": runner.PAYLOAD_BYTES,
            "required_output": str(runner.OUTPUT), "manifest_or_source_files_opened": 0,
            "network_requests": 0, "sample_or_status_values_parsed": False}, indent=2))
        return 0
    runner.require(os.name == "nt" and args.output is not None, "explicit_windows_output_required")
    runner.acquire(runner.load_manifest(), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
