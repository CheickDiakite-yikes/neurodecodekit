"""Deterministic, target-free synthetic recording fixtures for RW2."""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

from neurodecodekit.datasets.local_intake import (
    ARTIFACT_JSON as INTAKE_JSON,
    inspect_local_recording,
    write_intake_artifacts,
)
from neurodecodekit.preprocess.signal_quality import (
    FIXTURE_SCHEMA_NAME,
    SCHEMA_VERSION,
    SignalQualityLimits,
    canonical_payload_sha256,
    select_window_ranges,
)


MANIFEST_NAME = "signal_quality_fixtures.json"
FIXTURE_SET_CAP_BYTES = 16 * 1024 * 1024
SFREQ = 128
DURATION_SECONDS = 20
N_SAMPLES = SFREQ * DURATION_SECONDS
CHANNEL_NAMES = ["Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "EOG1"]
FIF_CHANNEL_TYPES = ["eeg"] * 8 + ["eog"]
ALL_EEG_CHANNEL_TYPES = ["eeg"] * len(CHANNEL_NAMES)
SAFE_ANNOTATION_SENTINEL = "RW2_PRIVATE_NONSEMANTIC_ANNOTATION_SENTINEL"

_VARIANTS = (
    "clean_multitype_continuous",
    "exact_flat_channel",
    "nonfinite_samples",
    "relative_rms_outlier",
    "line_components_50_60_hz",
    "missing_geometry_and_reference",
    "safe_nonsemantic_annotations",
)
_FORMATS = ("brainvision", "edf_or_edf_plus", "bdf", "eeglab", "fif", "bids")


def make_signal_quality_fixtures(
    out_dir: str | Path,
    *,
    contract_path: str | Path,
) -> dict[str, Any]:
    """Create the complete bounded RW2 synthetic fixture and RW1-binding set."""

    started_at = time.perf_counter()
    output_dir = Path(out_dir).expanduser()
    if output_dir.exists():
        if output_dir.is_symlink() or not output_dir.is_dir():
            raise ValueError("Fixture output path must be a real directory.")
        if any(output_dir.iterdir()):
            raise FileExistsError("Refusing to write into a nonempty fixture directory.")
    output_dir.mkdir(parents=True, exist_ok=True)

    mne, np, scipy = _require_neuro_dependencies()
    contract_file = _safe_contract_file(contract_path)
    contract_bytes = contract_file.read_bytes()
    contract = json.loads(contract_bytes.decode("utf-8"))
    if contract.get("schema_name") != "neurodecodekit.signal_quality_contract":
        raise ValueError("Unsupported RW2 contract schema.")
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported RW2 contract version.")

    fixture_rows: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, str]] = []
    for variant_id in _VARIANTS:
        data = _variant_signal(variant_id, np=np)
        for format_family in _FORMATS:
            skip_reason = _skip_reason(variant_id, format_family)
            if skip_reason is not None:
                skipped_rows.append(
                    {
                        "variant_id": variant_id,
                        "format_family": format_family,
                        "reason": skip_reason,
                    }
                )
                continue
            fixture_id = f"{variant_id}__{format_family}"
            fixture_dir = output_dir / "fixtures" / fixture_id
            source_dir = fixture_dir / "source"
            source_dir.mkdir(parents=True)
            selected_source, encoded_truth = _write_format_fixture(
                format_family,
                source_dir,
                data,
                variant_id=variant_id,
                mne=mne,
                np=np,
                scipy=scipy,
            )
            intake_result = inspect_local_recording(
                selected_source,
                modality="EEG",
                device_type=f"synthetic-rw2-{format_family}",
                hash_text_metadata=True,
            )
            intake_dir = fixture_dir / "intake"
            write_intake_artifacts(intake_result, intake_dir)
            intake_path = intake_dir / INTAKE_JSON
            intake_bytes = intake_path.read_bytes()
            channel_types = (
                list(FIF_CHANNEL_TYPES)
                if format_family == "fif"
                else list(ALL_EEG_CHANNEL_TYPES)
            )
            windows = select_window_ranges(
                N_SAMPLES,
                float(SFREQ),
                len(CHANNEL_NAMES),
                limits=SignalQualityLimits(),
            )
            values_by_window = [encoded_truth[:, start:stop] for start, stop in windows]
            times_by_window = [
                np.arange(start, stop, dtype=np.float64) / float(SFREQ)
                for start, stop in windows
            ]
            payload_sha256 = canonical_payload_sha256(
                list(CHANNEL_NAMES),
                windows,
                values_by_window,
                times_by_window,
            )
            source_path = selected_source.relative_to(output_dir).as_posix()
            fixture_rows.append(
                {
                    "fixture_id": fixture_id,
                    "variant_id": variant_id,
                    "format_family": format_family,
                    "status": "readable",
                    "source_path": source_path,
                    "selected_path": intake_result.report["source"]["selected_path"],
                    "source_layout": (
                        "continuous_external_fdt"
                        if format_family == "eeglab"
                        else "direct_continuous"
                    ),
                    "intake_report_path": intake_path.relative_to(output_dir).as_posix(),
                    "intake_report_sha256": _sha256_bytes(intake_bytes),
                    "source_manifest_sha256": intake_result.report["source"][
                        "source_manifest_sha256"
                    ],
                    "expected_payload_sha256": payload_sha256,
                    "expected_channel_types": channel_types,
                    "expected_geometry_status": _expected_geometry_status(
                        variant_id,
                        format_family,
                    ),
                    "expected_reference_status": _expected_reference_status(
                        variant_id,
                        format_family,
                    ),
                    "expected_event_status": (
                        "present_aggregate_only"
                        if variant_id == "safe_nonsemantic_annotations"
                        else "absent_by_fixture_contract"
                    ),
                    "expected_structural_warnings": _expected_structural_warnings(
                        variant_id,
                        format_family,
                    ),
                    "expected_advisory_channels": (
                        ["P4"] if variant_id == "relative_rms_outlier" else []
                    ),
                    "expected_peak_hz_by_channel": (
                        {"Fp1": 50.0, "Fp2": 60.0}
                        if variant_id == "line_components_50_60_hz"
                        else {}
                    ),
                    "expected_refusal": None,
                }
            )

    fixture_rows.extend(
        _make_refusal_fixtures(
            output_dir,
            mne=mne,
            np=np,
            scipy=scipy,
        )
    )
    fixture_rows.sort(key=lambda row: row["fixture_id"])
    skipped_rows.sort(key=lambda row: (row["variant_id"], row["format_family"]))
    manifest: dict[str, Any] = {
        "schema": {"name": FIXTURE_SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": "deterministic_synthetic_target_free_fixtures",
        "contract_sha256": _sha256_bytes(contract_bytes),
        "generation": {
            "sampling_rate_hz": SFREQ,
            "duration_sec": DURATION_SECONDS,
            "sample_count": N_SAMPLES,
            "channel_names": list(CHANNEL_NAMES),
            "variant_ids": list(_VARIANTS) + ["malformed_and_cap_refusals"],
            "format_families": list(_FORMATS),
            "source_payloads_persisted_as_recording_files_only": True,
            "target_text_or_labels_created": False,
        },
        "fixtures": fixture_rows,
        "skipped_exports": skipped_rows,
        "access_counts": {
            "real_data_reads": 0,
            "consumed_cache_reads": 0,
            "target_label_values_emitted_or_used": 0,
            "model_runs": 0,
            "training_runs": 0,
            "network_calls": 0,
        },
        "claim_boundary": {
            "allowed": [
                "generated_format_reader_validation",
                "generated_quality_metric_validation",
            ],
            "prohibited": [
                "real_recording_quality",
                "prediction_or_decoding",
                "neural_advantage",
                "real_time_or_hardware_performance",
            ],
        },
        "hashes": {"manifest_payload_sha256": None},
    }
    manifest["hashes"]["manifest_payload_sha256"] = _manifest_payload_sha256(manifest)
    manifest_path = output_dir / MANIFEST_NAME
    manifest_path.write_bytes(_json_bytes(manifest))
    total_bytes = _tree_bytes(output_dir)
    if total_bytes > FIXTURE_SET_CAP_BYTES:
        raise ValueError(
            f"Synthetic fixture set exceeds cap: {total_bytes} > {FIXTURE_SET_CAP_BYTES}"
        )
    runtime_sec = round(time.perf_counter() - started_at, 6)
    return {
        "manifest": str(manifest_path),
        "readable_fixture_count": sum(row["status"] == "readable" for row in fixture_rows),
        "refusal_fixture_count": sum(row["status"] == "refused" for row in fixture_rows),
        "skipped_export_count": len(skipped_rows),
        "format_families": list(_FORMATS),
        "variant_ids": list(_VARIANTS) + ["malformed_and_cap_refusals"],
        "total_bytes": total_bytes,
        "max_total_bytes": FIXTURE_SET_CAP_BYTES,
        "output_cap_passed": True,
        "runtime_sec": runtime_sec,
        "peak_rss_bytes": _peak_rss_bytes(),
        "real_data_reads": 0,
        "consumed_cache_reads": 0,
        "target_label_values_emitted_or_used": 0,
        "model_runs": 0,
        "training_runs": 0,
        "network_calls": 0,
    }


def load_signal_quality_fixture_manifest(
    manifest_path: str | Path,
    *,
    max_bytes: int = 4 * 1024 * 1024,
) -> dict[str, Any]:
    """Load and validate the deterministic synthetic fixture manifest."""

    path = Path(manifest_path).expanduser()
    if path.is_symlink() or not path.is_file():
        raise ValueError("Fixture manifest must be a regular non-symlink file.")
    if path.stat().st_size > max_bytes:
        raise ValueError("Fixture manifest exceeds the inspection cap.")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Fixture manifest JSON is invalid.") from exc
    if manifest.get("schema") != {"name": FIXTURE_SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("Unsupported fixture manifest schema.")
    if manifest.get("proof_posture") != "deterministic_synthetic_target_free_fixtures":
        raise ValueError("Fixture manifest proof posture is invalid.")
    if manifest.get("hashes", {}).get("manifest_payload_sha256") != _manifest_payload_sha256(
        manifest
    ):
        raise ValueError("Fixture manifest payload hash mismatch.")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("Fixture manifest contains no fixtures.")
    ids = [row.get("fixture_id") for row in fixtures]
    if any(not isinstance(value, str) or not value for value in ids):
        raise ValueError("Fixture manifest contains an invalid fixture ID.")
    if len(ids) != len(set(ids)):
        raise ValueError("Fixture manifest contains duplicate fixture IDs.")
    for key in (
        "real_data_reads",
        "consumed_cache_reads",
        "target_label_values_emitted_or_used",
        "model_runs",
        "training_runs",
        "network_calls",
    ):
        if manifest.get("access_counts", {}).get(key) != 0:
            raise ValueError(f"Fixture manifest has forbidden access count: {key}")
    return {
        "schema": dict(manifest["schema"]),
        "contract_sha256": manifest["contract_sha256"],
        "manifest_payload_sha256": manifest["hashes"]["manifest_payload_sha256"],
        "fixture_count": len(fixtures),
        "readable_fixture_count": sum(row.get("status") == "readable" for row in fixtures),
        "refusal_fixture_count": sum(row.get("status") == "refused" for row in fixtures),
        "skipped_export_count": len(manifest.get("skipped_exports", [])),
        "format_families": list(manifest["generation"]["format_families"]),
        "variant_ids": list(manifest["generation"]["variant_ids"]),
        "access_counts": dict(manifest["access_counts"]),
    }


def _variant_signal(variant_id: str, *, np: Any) -> Any:
    times = np.arange(N_SAMPLES, dtype=np.float64) / float(SFREQ)
    frequencies = [6.0, 8.0, 10.0, 12.0, 14.0, 18.0, 22.0, 30.0, 1.0]
    amplitudes_uv = [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 20.0]
    data = np.vstack(
        [
            amplitude * 1e-6 * np.sin(2.0 * np.pi * frequency * times + 0.13 * index)
            for index, (amplitude, frequency) in enumerate(zip(amplitudes_uv, frequencies))
        ]
    )
    if variant_id == "exact_flat_channel":
        data[0, :] = 0.0
    elif variant_id == "nonfinite_samples":
        data[1, 300] = np.nan
    elif variant_id == "relative_rms_outlier":
        data[7, :] *= 1000.0
    elif variant_id == "line_components_50_60_hz":
        data[0, :] += 30e-6 * np.sin(2.0 * np.pi * 50.0 * times)
        data[1, :] += 30e-6 * np.sin(2.0 * np.pi * 60.0 * times)
    elif variant_id not in {
        "clean_multitype_continuous",
        "missing_geometry_and_reference",
        "safe_nonsemantic_annotations",
    }:
        raise ValueError(f"Unknown synthetic signal variant: {variant_id}")
    return data


def _skip_reason(variant_id: str, format_family: str) -> str | None:
    if variant_id == "nonfinite_samples" and format_family in {"edf_or_edf_plus", "bdf"}:
        return "integer_format_cannot_preserve_nonfinite_fixture"
    if variant_id == "safe_nonsemantic_annotations" and format_family in {
        "edf_or_edf_plus",
        "bdf",
    }:
        return "minimal_writer_does_not_add_edf_bdf_plus_annotation_channel"
    return None


def _write_format_fixture(
    format_family: str,
    root: Path,
    data: Any,
    *,
    variant_id: str,
    mne: Any,
    np: Any,
    scipy: Any,
) -> tuple[Path, Any]:
    annotations = variant_id == "safe_nonsemantic_annotations"
    geometry = variant_id != "missing_geometry_and_reference"
    reference = variant_id != "missing_geometry_and_reference"
    if format_family == "brainvision":
        source = _write_brainvision(root, data, annotations=annotations, np=np)
        truth = _float_microvolt_truth(data, np=np)
    elif format_family == "edf_or_edf_plus":
        source, truth = _write_edf_bdf(root, data, bdf=False, np=np)
    elif format_family == "bdf":
        source, truth = _write_edf_bdf(root, data, bdf=True, np=np)
    elif format_family == "eeglab":
        source = _write_eeglab(
            root,
            data,
            annotations=annotations,
            geometry=geometry,
            np=np,
            scipy=scipy,
        )
        truth = _float_microvolt_truth(data, np=np)
    elif format_family == "fif":
        source = _write_fif(
            root,
            data,
            annotations=annotations,
            geometry=geometry,
            reference=reference,
            mne=mne,
            np=np,
        )
        truth = np.asarray(data, dtype="<f4").astype(np.float64)
    elif format_family == "bids":
        bids_root = root / "bids"
        recording_dir = bids_root / "sub-01" / "eeg"
        recording_dir.mkdir(parents=True)
        (bids_root / "dataset_description.json").write_text(
            json.dumps(
                {
                    "Name": "RW2 synthetic fixture",
                    "BIDSVersion": "1.10.0",
                    "DatasetType": "raw",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        source = _write_brainvision(
            recording_dir,
            data,
            annotations=annotations,
            np=np,
            stem="sub-01_task-synthetic_eeg",
        )
        source = bids_root
        truth = _float_microvolt_truth(data, np=np)
    else:  # pragma: no cover
        raise ValueError(f"Unsupported synthetic format: {format_family}")
    return source, truth


def _write_brainvision(
    root: Path,
    data: Any,
    *,
    annotations: bool,
    np: Any,
    stem: str = "recording",
) -> Path:
    header = root / f"{stem}.vhdr"
    marker = root / f"{stem}.vmrk"
    signal = root / f"{stem}.eeg"
    signal.write_bytes(np.asarray(data.T / 1e-6, dtype="<f4").tobytes(order="C"))
    header.write_text(
        "\n".join(
            [
                "Brain Vision Data Exchange Header File Version 1.0",
                "[Common Infos]",
                "Codepage=UTF-8",
                f"DataFile={signal.name}",
                f"MarkerFile={marker.name}",
                "DataFormat=BINARY",
                "DataOrientation=MULTIPLEXED",
                f"NumberOfChannels={len(CHANNEL_NAMES)}",
                f"SamplingInterval={1_000_000 / SFREQ:.10f}",
                "[Binary Infos]",
                "BinaryFormat=IEEE_FLOAT_32",
                "[Channel Infos]",
                *[
                    f"Ch{index + 1}={name},,1,uV"
                    for index, name in enumerate(CHANNEL_NAMES)
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )
    marker_rows = [
        "Brain Vision Data Exchange Marker File, Version 1.0",
        "[Common Infos]",
        "Codepage=UTF-8",
        f"DataFile={signal.name}",
        "[Marker Infos]",
        "Mk1=New Segment,,1,1,0",
    ]
    if annotations:
        marker_rows.append(
            f"Mk2=Comment,{SAFE_ANNOTATION_SENTINEL},{5 * SFREQ + 1},32,0"
        )
    marker.write_text("\n".join(marker_rows + [""]), encoding="utf-8")
    return header


def _write_edf_bdf(root: Path, data: Any, *, bdf: bool, np: Any) -> tuple[Path, Any]:
    suffix = ".bdf" if bdf else ".edf"
    path = root / f"recording{suffix}"
    physical_uv = np.asarray(data, dtype=np.float64) / 1e-6
    digital_min = -8_388_608 if bdf else -32_768
    digital_max = 8_388_607 if bdf else 32_767
    physical_min = -20_000.0 if np.max(np.abs(physical_uv)) > 100.0 else -100.0
    physical_max = -physical_min
    scaled = np.rint(
        (physical_uv - physical_min)
        * (digital_max - digital_min)
        / (physical_max - physical_min)
        + digital_min
    ).astype(np.int64)
    scaled = np.clip(scaled, digital_min, digital_max)
    calibration = (physical_max - physical_min) / (digital_max - digital_min)
    offset = physical_min - digital_min * calibration
    decoded = (scaled.astype(np.float64) * calibration + offset) * 1e-6
    n_records = DURATION_SECONDS
    header_bytes = 256 + len(CHANNEL_NAMES) * 256
    fixed = b"".join(
        [
            (b"\xffBIOSEMI" if bdf else _edf_field("0", 8)),
            _edf_field("X X X X", 80),
            _edf_field("Startdate X", 80),
            _edf_field("01.01.01", 8),
            _edf_field("00.00.00", 8),
            _edf_field(header_bytes, 8),
            _edf_field("", 44),
            _edf_field(n_records, 8),
            _edf_field(1, 8),
            _edf_field(len(CHANNEL_NAMES), 4),
        ]
    )
    signal_headers = b"".join(_edf_field(name, 16) for name in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field("", 80) for _ in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field("uV", 8) for _ in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field(physical_min, 8) for _ in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field(physical_max, 8) for _ in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field(digital_min, 8) for _ in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field(digital_max, 8) for _ in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field("HP:0 LP:64", 80) for _ in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field(SFREQ, 8) for _ in CHANNEL_NAMES)
    signal_headers += b"".join(_edf_field("", 32) for _ in CHANNEL_NAMES)
    body = bytearray()
    for record in range(n_records):
        start = record * SFREQ
        stop = start + SFREQ
        for channel in range(len(CHANNEL_NAMES)):
            values = scaled[channel, start:stop]
            if bdf:
                unsigned = values & 0xFFFFFF
                packed = np.empty((len(values), 3), dtype=np.uint8)
                packed[:, 0] = unsigned & 0xFF
                packed[:, 1] = (unsigned >> 8) & 0xFF
                packed[:, 2] = (unsigned >> 16) & 0xFF
                body.extend(packed.tobytes())
            else:
                body.extend(np.asarray(values, dtype="<i2").tobytes())
    path.write_bytes(fixed + signal_headers + body)
    return path, decoded


def _write_eeglab(
    root: Path,
    data: Any,
    *,
    annotations: bool,
    geometry: bool,
    np: Any,
    scipy: Any,
) -> Path:
    path = root / "recording.set"
    fdt = root / "recording.fdt"
    fdt.write_bytes(np.asarray(data / 1e-6, dtype="<f4").tobytes(order="F"))
    chanlocs = np.empty(len(CHANNEL_NAMES), dtype=object)
    positions = _positions()
    for index, name in enumerate(CHANNEL_NAMES):
        row: dict[str, Any] = {"labels": name}
        if geometry:
            x, y, z = positions[name]
            row.update({"X": x * 1000.0, "Y": y * 1000.0, "Z": z * 1000.0})
        chanlocs[index] = row
    if annotations:
        events = np.empty(1, dtype=object)
        events[0] = {
            "type": SAFE_ANNOTATION_SENTINEL,
            "latency": float(5 * SFREQ + 1),
            "duration": 32.0,
        }
    else:
        events = np.array([], dtype=object)
    eeg = {
        "setname": "rw2_synthetic",
        "filename": path.name,
        "filepath": "",
        "subject": "",
        "group": "",
        "condition": "",
        "session": 1,
        "comments": "",
        "nbchan": len(CHANNEL_NAMES),
        "trials": 1,
        "pnts": N_SAMPLES,
        "srate": SFREQ,
        "xmin": 0.0,
        "xmax": (N_SAMPLES - 1) / SFREQ,
        "times": np.array([], dtype=np.float64),
        "data": fdt.name,
        "icaact": np.array([], dtype=np.float64),
        "icawinv": np.array([], dtype=np.float64),
        "icasphere": np.array([], dtype=np.float64),
        "icaweights": np.array([], dtype=np.float64),
        "icachansind": np.array([], dtype=np.float64),
        "chanlocs": chanlocs,
        "urchanlocs": np.array([], dtype=object),
        "chaninfo": {"nodatchans": np.array([], dtype=object)},
        "ref": "common" if geometry else "",
        "event": events,
        "urevent": events,
        "epoch": np.array([], dtype=object),
        "reject": {"rejjp": np.array([], dtype=np.float64)},
        "stats": {"jp": np.array([], dtype=np.float64)},
        "specdata": np.array([], dtype=np.float64),
        "specicaact": np.array([], dtype=np.float64),
        "splinefile": "",
        "icasplinefile": "",
        "dipfit": {"model": np.array([], dtype=object)},
        "history": "",
        "saved": "yes",
        "etc": {"synthetic": 1},
        "datfile": fdt.name,
    }
    scipy.io.savemat(
        path,
        {"EEG": eeg},
        appendmat=False,
        do_compression=False,
        long_field_names=True,
    )
    _normalize_mat_header(path)
    return path


def _write_fif(
    root: Path,
    data: Any,
    *,
    annotations: bool,
    geometry: bool,
    reference: bool,
    mne: Any,
    np: Any,
) -> Path:
    path = root / "recording_raw.fif"
    info = mne.create_info(CHANNEL_NAMES, SFREQ, FIF_CHANNEL_TYPES)
    raw = mne.io.RawArray(np.asarray(data, dtype=np.float64), info, verbose="ERROR")
    raw.set_meas_date(None)
    if geometry:
        positions = _positions()
        montage = mne.channels.make_dig_montage(ch_pos=positions, coord_frame="head")
        raw.set_montage(montage, on_missing="ignore", verbose="ERROR")
        raw.info["chs"][-1]["loc"][:3] = np.asarray(positions["EOG1"], dtype=float)
        raw.info["chs"][-1]["coord_frame"] = 4
    if reference:
        raw.set_eeg_reference(ref_channels=[], projection=False, verbose="ERROR")
    if annotations:
        raw.set_annotations(
            mne.Annotations(
                onset=[5.0],
                duration=[0.25],
                description=[SAFE_ANNOTATION_SENTINEL],
            )
        )
    raw.save(path, fmt="single", overwrite=True, verbose="ERROR")
    return path


def _make_refusal_fixtures(
    output_dir: Path,
    *,
    mne: Any,
    np: Any,
    scipy: Any,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    data = _variant_signal("clean_multitype_continuous", np=np)

    fixture_id = "malformed_and_cap_refusals__eeglab_embedded"
    fixture_dir = output_dir / "fixtures" / fixture_id
    source_dir = fixture_dir / "source"
    source_dir.mkdir(parents=True)
    set_path = source_dir / "recording.set"
    embedded = {
        "nbchan": len(CHANNEL_NAMES),
        "trials": 1,
        "pnts": N_SAMPLES,
        "srate": SFREQ,
        "xmin": 0.0,
        "xmax": (N_SAMPLES - 1) / SFREQ,
        "data": np.asarray(data / 1e-6, dtype=np.float32),
        "chanlocs": np.array(
            [{"labels": name} for name in CHANNEL_NAMES], dtype=object
        ),
    }
    scipy.io.savemat(set_path, {"EEG": embedded}, appendmat=False, do_compression=False)
    _normalize_mat_header(set_path)
    rows.append(
        _refusal_fixture_row(
            output_dir,
            fixture_id=fixture_id,
            variant_id="malformed_and_cap_refusals",
            format_family="eeglab",
            selected_source=set_path,
            source_layout="embedded_set",
            expected_refusal="eeglab_embedded_or_epoched_source_refused",
        )
    )

    fixture_id = "malformed_and_cap_refusals__bids_events_sidecar"
    fixture_dir = output_dir / "fixtures" / fixture_id
    source_dir = fixture_dir / "source" / "bids"
    recording_dir = source_dir / "sub-01" / "eeg"
    recording_dir.mkdir(parents=True)
    (source_dir / "dataset_description.json").write_text(
        '{"BIDSVersion":"1.10.0","DatasetType":"raw","Name":"RW2 synthetic"}\n',
        encoding="utf-8",
    )
    _write_brainvision(
        recording_dir,
        data,
        annotations=False,
        np=np,
        stem="sub-01_task-synthetic_eeg",
    )
    (recording_dir / "sub-01_task-synthetic_events.tsv").write_text(
        "onset\tduration\ttrial_type\n5\t0.25\tPRIVATE_EVENT_SENTINEL\n",
        encoding="utf-8",
    )
    rows.append(
        _refusal_fixture_row(
            output_dir,
            fixture_id=fixture_id,
            variant_id="malformed_and_cap_refusals",
            format_family="bids",
            selected_source=source_dir,
            source_layout="bids_with_events_sidecar",
            expected_refusal="bids_event_sidecar_requires_content_access",
        )
    )
    return rows


def _refusal_fixture_row(
    output_dir: Path,
    *,
    fixture_id: str,
    variant_id: str,
    format_family: str,
    selected_source: Path,
    source_layout: str,
    expected_refusal: str,
) -> dict[str, Any]:
    fixture_dir = output_dir / "fixtures" / fixture_id
    intake_result = inspect_local_recording(
        selected_source,
        modality="EEG",
        device_type=f"synthetic-rw2-{format_family}-refusal",
        hash_text_metadata=True,
    )
    intake_dir = fixture_dir / "intake"
    write_intake_artifacts(intake_result, intake_dir)
    intake_path = intake_dir / INTAKE_JSON
    intake_bytes = intake_path.read_bytes()
    return {
        "fixture_id": fixture_id,
        "variant_id": variant_id,
        "format_family": format_family,
        "status": "refused",
        "source_path": selected_source.relative_to(output_dir).as_posix(),
        "selected_path": intake_result.report["source"]["selected_path"],
        "source_layout": source_layout,
        "intake_report_path": intake_path.relative_to(output_dir).as_posix(),
        "intake_report_sha256": _sha256_bytes(intake_bytes),
        "source_manifest_sha256": intake_result.report["source"][
            "source_manifest_sha256"
        ],
        "expected_payload_sha256": "0" * 64,
        "expected_channel_types": [],
        "expected_geometry_status": "unavailable",
        "expected_reference_status": "unknown",
        "expected_event_status": "present_sidecar_not_authorized",
        "expected_structural_warnings": [],
        "expected_advisory_channels": [],
        "expected_peak_hz_by_channel": {},
        "expected_refusal": expected_refusal,
    }


def _expected_geometry_status(variant_id: str, format_family: str) -> str:
    if variant_id == "missing_geometry_and_reference":
        return "unavailable"
    if format_family in {"fif", "eeglab"}:
        return "available_all_selected_channels"
    return "unavailable"


def _expected_reference_status(variant_id: str, format_family: str) -> str:
    if format_family == "fif" and variant_id != "missing_geometry_and_reference":
        return "custom_reference_applied_in_source"
    return "unknown"


def _expected_structural_warnings(variant_id: str, format_family: str) -> list[str]:
    warnings: set[str] = set()
    if variant_id == "exact_flat_channel":
        warnings.add("exact_constant_channel_window")
    if variant_id == "nonfinite_samples":
        warnings.add("nonfinite_samples_present")
    if _expected_geometry_status(variant_id, format_family) != "available_all_selected_channels":
        warnings.add("geometry_unavailable_or_partially_finite")
    if _expected_reference_status(variant_id, format_family) == "unknown":
        warnings.add("reference_unknown")
    return sorted(warnings)


def _float_microvolt_truth(data: Any, *, np: Any) -> Any:
    return np.asarray(data / 1e-6, dtype="<f4").astype(np.float64) * 1e-6


def _positions() -> dict[str, tuple[float, float, float]]:
    return {
        "Fp1": (-0.03, 0.085, 0.055),
        "Fp2": (0.03, 0.085, 0.055),
        "F3": (-0.045, 0.045, 0.075),
        "F4": (0.045, 0.045, 0.075),
        "C3": (-0.055, 0.0, 0.085),
        "C4": (0.055, 0.0, 0.085),
        "P3": (-0.045, -0.045, 0.075),
        "P4": (0.045, -0.045, 0.075),
        "EOG1": (0.06, 0.09, 0.035),
    }


def _edf_field(value: object, width: int) -> bytes:
    if isinstance(value, float):
        text = f"{value:g}"
    else:
        text = str(value)
    encoded = text.encode("ascii")
    if len(encoded) > width:
        raise ValueError(f"EDF field exceeds width {width}: {text}")
    return encoded.ljust(width, b" ")


def _normalize_mat_header(path: Path) -> None:
    payload = bytearray(path.read_bytes())
    header = b"MATLAB 5.0 MAT-file, RW2 deterministic synthetic fixture"
    payload[:116] = header.ljust(116, b" ")
    path.write_bytes(payload)


def _safe_contract_file(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError("RW2 contract must be a regular non-symlink file.")
    if candidate.stat().st_size > 4 * 1024 * 1024:
        raise ValueError("RW2 contract exceeds the read cap.")
    return candidate.resolve(strict=True)


def _require_neuro_dependencies() -> tuple[Any, Any, Any]:
    try:
        import mne
        import numpy as np
        import scipy
    except ImportError as exc:
        raise RuntimeError("RW2 fixture generation requires: pip install -e '.[neuro]'") from exc
    version = str(mne.__version__).split(".")
    if len(version) < 2 or tuple(map(int, version[:2])) != (1, 12):
        raise RuntimeError("RW2 fixtures are validated only for MNE 1.12.x.")
    return mne, np, scipy


def _tree_bytes(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def _manifest_payload_sha256(manifest: dict[str, Any]) -> str:
    payload = json.loads(json.dumps(manifest))
    payload["hashes"]["manifest_payload_sha256"] = None
    return _sha256_json(payload)


def _json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_json(payload: Any) -> str:
    compact = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return _sha256_bytes(compact)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _peak_rss_bytes() -> int | None:
    try:
        import resource
    except ImportError:  # pragma: no cover
        return None
    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return peak if sys.platform == "darwin" else peak * 1024
