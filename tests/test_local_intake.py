import builtins
import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.cli import main
from neurodecodekit.datasets.local_intake import (
    ARTIFACT_AUDIT,
    ARTIFACT_JSON,
    ARTIFACT_MARKDOWN,
    IntakeLimits,
    inspect_local_recording,
    load_intake_report,
    validate_intake_report,
    write_intake_artifacts,
)


class LocalIntakeTests(unittest.TestCase):
    def _brainvision_fixture(self, root: Path) -> tuple[Path, str]:
        header = root / "fixture.vhdr"
        signal = root / "fixture.eeg"
        marker = root / "fixture.vmrk"
        target_sentinel = "FORBIDDEN_TARGET_SENTINEL"
        header.write_text(
            "\n".join(
                [
                    "Brain Vision Data Exchange Header File Version 1.0",
                    "[Common Infos]",
                    "DataFile=fixture.eeg",
                    "MarkerFile=fixture.vmrk",
                    "DataFormat=BINARY",
                    "DataOrientation=MULTIPLEXED",
                    "NumberOfChannels=2",
                    "SamplingInterval=1000",
                    "[Channel Infos]",
                    "Ch1=Fz,,0.1,uV",
                    "Ch2=Cz,,0.1,uV",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        signal.write_bytes(b"\x01\x02BINARY_SIGNAL_MUST_NOT_BE_READ\x03")
        marker.write_text(
            "Brain Vision Data Exchange Marker File\n"
            "[Marker Infos]\n"
            f"Mk1=Stimulus,{target_sentinel},1,1,0\n",
            encoding="utf-8",
        )
        return header, target_sentinel

    def _registry_fixture(self, root: Path) -> Path:
        path = root / "registry.json"
        path.write_text(
            json.dumps(
                {
                    "schema_name": "fixture.dataset_registry",
                    "schema_version": "0.1.0",
                    "records": [{"id": "fixture"}],
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return path

    def test_brainvision_replay_is_deterministic_and_target_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            header, target_sentinel = self._brainvision_fixture(root)
            registry = self._registry_fixture(root)
            original_open = Path.open

            def guarded_open(path: Path, *args, **kwargs):
                if path.suffix.lower() in {".eeg", ".vmrk"}:
                    raise AssertionError(f"forbidden content read: {path.name}")
                return original_open(path, *args, **kwargs)

            with patch.object(Path, "open", guarded_open):
                first = inspect_local_recording(
                    header,
                    registry_path=registry,
                    modality="EEG",
                    device_type="synthetic-brainvision",
                    hash_text_metadata=True,
                )
                second = inspect_local_recording(
                    header,
                    registry_path=registry,
                    modality="EEG",
                    device_type="synthetic-brainvision",
                    hash_text_metadata=True,
                )
            first_summary = write_intake_artifacts(first, root / "out-a")
            second_summary = write_intake_artifacts(second, root / "out-b")
            first_json = (root / "out-a" / ARTIFACT_JSON).read_bytes()
            second_json = (root / "out-b" / ARTIFACT_JSON).read_bytes()
            first_markdown = (root / "out-a" / ARTIFACT_MARKDOWN).read_bytes()
            second_markdown = (root / "out-b" / ARTIFACT_MARKDOWN).read_bytes()
            audit_exists = (root / "out-a" / ARTIFACT_AUDIT).is_file()
            loaded = load_intake_report(root / "out-a" / ARTIFACT_JSON)

        self.assertEqual(first.report, second.report)
        self.assertEqual(first_json, second_json)
        self.assertEqual(first_markdown, second_markdown)
        self.assertNotIn(target_sentinel.encode(), first_json)
        self.assertNotIn(str(root).encode(), first_json)
        self.assertTrue(audit_exists)
        self.assertEqual(first.report["recording"]["channel_count"], 2)
        self.assertEqual(first.report["recording"]["channel_names"], ["Fz", "Cz"])
        self.assertEqual(first.report["recording"]["sampling_rate_hz"], 1000.0)
        self.assertEqual(first.report["access_counts"]["metadata_files_read"], 2)
        self.assertEqual(first.report["access_counts"]["binary_signal_bytes_read"], 0)
        self.assertEqual(first.report["access_counts"]["target_or_label_files_read"], 0)
        self.assertTrue(first.report["provenance"]["registry"]["bound"])
        self.assertEqual(len(first.report["source"]["source_manifest_sha256"]), 64)
        self.assertTrue(loaded["audit_validated"])
        self.assertFalse(loaded["measurements"]["end_to_end_latency_measured"])
        self.assertLess(first_summary["total_output_bytes"], 4 * 1024 * 1024)
        self.assertLess(second_summary["total_output_bytes"], 4 * 1024 * 1024)

    def test_supported_binary_families_and_fif_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edf = root / "sample.edf"
            bdf = root / "sample.bdf"
            eeglab = root / "sample.set"
            fdt = root / "sample.fdt"
            fif = root / "sample_raw.fif"
            fif_one = root / "sample_raw-1.fif"
            fif_two = root / "sample_raw-2.fif"
            for path in (edf, bdf, eeglab, fdt, fif, fif_one, fif_two):
                path.write_bytes(b"fixture")

            edf_report = inspect_local_recording(edf).report
            bdf_report = inspect_local_recording(bdf).report
            set_report = inspect_local_recording(eeglab).report
            fif_report = inspect_local_recording(fif).report

        self.assertEqual(edf_report["source"]["format_family"], "edf_or_edf_plus")
        self.assertEqual(bdf_report["source"]["format_family"], "bdf")
        self.assertEqual(set_report["source"]["format_family"], "eeglab")
        self.assertEqual(set_report["source"]["file_count"], 2)
        self.assertEqual(fif_report["source"]["format_family"], "fif")
        self.assertEqual(fif_report["source"]["file_count"], 3)
        self.assertEqual(
            fif_report["recording"]["format_metadata"]["split_status"],
            "standard_split_filename_family",
        )
        for report in (edf_report, bdf_report, set_report, fif_report):
            self.assertEqual(report["access_counts"]["metadata_text_bytes_read"], 0)
            self.assertEqual(report["access_counts"]["raw_data_reads"], 0)
            self.assertEqual(report["compatibility"]["current_level"], 0)

    def test_bids_root_omits_sensitive_sidecar_content_and_infers_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bids"
            recording_dir = root / "sub-01" / "ses-02" / "eeg"
            recording_dir.mkdir(parents=True)
            hidden_name = "PRIVATE_DATASET_NAME_SENTINEL"
            event_sentinel = "PRIVATE_EVENT_TARGET_SENTINEL"
            (root / "dataset_description.json").write_text(
                json.dumps(
                    {
                        "Name": hidden_name,
                        "BIDSVersion": "1.10.0",
                        "DatasetType": "raw",
                    }
                ),
                encoding="utf-8",
            )
            raw = recording_dir / "sub-01_ses-02_task-type_run-03_eeg.edf"
            raw.write_bytes(b"binary")
            (recording_dir / "sub-01_ses-02_task-type_run-03_events.tsv").write_text(
                f"onset\tduration\ttrial_type\n0\t1\t{event_sentinel}\n",
                encoding="utf-8",
            )
            (root / "participants.tsv").write_text(
                "participant_id\tage\nsub-01\t99\n", encoding="utf-8"
            )

            result = inspect_local_recording(root, hash_text_metadata=True)
            encoded = json.dumps(result.report, sort_keys=True)

        self.assertEqual(result.report["source"]["format_family"], "bids")
        self.assertEqual(result.report["recording"]["raw_family"], "edf_or_edf_plus")
        self.assertEqual(result.report["recording"]["modality"], "EEG")
        self.assertEqual(result.report["item"]["subject_id"], "01")
        self.assertEqual(result.report["item"]["session_id"], "02")
        self.assertEqual(result.report["item"]["task_id"], "type")
        self.assertEqual(result.report["item"]["run_id"], "03")
        self.assertNotIn(hidden_name, encoded)
        self.assertNotIn(event_sentinel, encoded)
        self.assertEqual(result.report["access_counts"]["metadata_files_read"], 1)
        self.assertIn(
            "bids_participant_or_event_content_present_but_not_read",
            result.report["warnings"],
        )

    def test_unknown_directory_and_fif_gap_produce_inspectable_refusals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unknown = root / "unknown-directory"
            unknown.mkdir()
            (unknown / "notes.txt").write_text("not a recording", encoding="utf-8")
            directory_report = inspect_local_recording(unknown).report

            fif = root / "broken_raw.fif"
            missing_one = root / "broken_raw-2.fif"
            fif.write_bytes(b"primary")
            missing_one.write_bytes(b"continuation two")
            fif_report = inspect_local_recording(fif).report

        self.assertEqual(directory_report["status"], "refused")
        self.assertIn(
            "bids_dataset_description_json_missing", directory_report["refusals"]
        )
        self.assertEqual(directory_report["access_counts"]["metadata_files_read"], 0)
        self.assertEqual(fif_report["status"], "refused")
        self.assertIn(
            "fif_split_continuation_indices_not_contiguous_from_1",
            fif_report["refusals"],
        )

    def test_malformed_brainvision_bundle_produces_level_zero_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            header = root / "bad.vhdr"
            (root / "a.eeg").write_bytes(b"a")
            (root / "b.eeg").write_bytes(b"b")
            header.write_text(
                "[Common Infos]\nDataFile=a.eeg\nDataFile=b.eeg\n",
                encoding="utf-8",
            )
            report = inspect_local_recording(header).report

        self.assertEqual(report["status"], "refused")
        self.assertEqual(report["compatibility"]["current_level"], -1)
        self.assertIn("brainvision_duplicate_datafile_role", report["refusals"])
        self.assertIn("brainvision_missing_markerfile", report["refusals"])
        self.assertFalse(report["compatibility"]["levels"][0]["passed"])

    def test_unsafe_paths_archives_pickles_unknowns_and_symlinks_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside.eeg"
            outside.write_bytes(b"outside")
            header = root / "unsafe.vhdr"
            header.write_text(
                "[Common Infos]\nDataFile=../outside.eeg\nMarkerFile=unsafe.vmrk\n",
                encoding="utf-8",
            )
            (root / "unsafe.vmrk").write_text("marker", encoding="utf-8")
            traversal_report = inspect_local_recording(header).report

            archive = root / "recording.tar.gz"
            archive.write_bytes(b"archive")
            pickle = root / "recording.pkl"
            pickle.write_bytes(b"pickle")
            unknown = root / "recording.xyz"
            unknown.write_bytes(b"unknown")
            real_edf = root / "real.edf"
            real_edf.write_bytes(b"edf")
            linked_edf = root / "linked.edf"
            linked_edf.symlink_to(real_edf)

            archive_report = inspect_local_recording(archive).report
            pickle_report = inspect_local_recording(pickle).report
            unknown_report = inspect_local_recording(unknown).report
            with self.assertRaisesRegex(ValueError, "symlink"):
                inspect_local_recording(linked_edf)

        self.assertTrue(
            any("brainvision_unsafe_datafile" in row for row in traversal_report["refusals"])
        )
        self.assertEqual(traversal_report["access_counts"]["binary_signal_bytes_read"], 0)
        self.assertEqual(archive_report["status"], "refused")
        self.assertIn("archives_are_not_recording_formats", archive_report["refusals"])
        self.assertEqual(pickle_report["status"], "refused")
        self.assertIn(
            "pickle_and_object_numpy_payloads_are_refused", pickle_report["refusals"]
        )
        self.assertEqual(unknown_report["status"], "refused")
        self.assertIn(
            "unsupported_recording_format_expected_vhdr_edf_bdf_set_fif_or_bids_root",
            unknown_report["refusals"],
        )
        for report in (archive_report, pickle_report, unknown_report):
            self.assertEqual(report["access_counts"]["metadata_files_read"], 0)
            self.assertEqual(report["access_counts"]["raw_data_reads"], 0)

    def test_input_text_file_count_depth_and_output_caps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edf = root / "large.edf"
            edf.write_bytes(b"0123456789")
            with self.assertRaisesRegex(ValueError, "Declared input bytes exceed cap"):
                inspect_local_recording(
                    edf,
                    limits=IntakeLimits(max_declared_input_bytes=5),
                )

            header, _ = self._brainvision_fixture(root)
            with self.assertRaisesRegex(ValueError, "per-file cap"):
                inspect_local_recording(
                    header,
                    limits=IntakeLimits(max_text_file_bytes=16),
                )

            registry = self._registry_fixture(root)
            combined_text_bytes = header.stat().st_size + registry.stat().st_size
            with self.assertRaisesRegex(ValueError, "Text metadata reads exceed total cap"):
                inspect_local_recording(
                    header,
                    registry_path=registry,
                    limits=IntakeLimits(max_text_total_bytes=combined_text_bytes - 1),
                )

            bids = root / "bids"
            bids.mkdir()
            (bids / "dataset_description.json").write_text(
                '{"BIDSVersion":"1.10.0"}', encoding="utf-8"
            )
            (bids / "sub-01_task-x_eeg.edf").write_bytes(b"raw")
            with self.assertRaisesRegex(ValueError, "file count exceeds cap"):
                inspect_local_recording(bids, limits=IntakeLimits(max_files=1))

            deep = bids / "a" / "b"
            deep.mkdir(parents=True)
            (deep / "sidecar.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "depth exceeds cap"):
                inspect_local_recording(bids, limits=IntakeLimits(max_depth=1))

            tiny_output_result = inspect_local_recording(
                edf,
                limits=IntakeLimits(max_output_bytes=64),
            )
            output = root / "too-small-output"
            with self.assertRaisesRegex(ValueError, "exceed output cap"):
                write_intake_artifacts(tiny_output_result, output)
            self.assertFalse(output.exists())

    def test_declared_root_and_companion_symlink_escape_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = root / "allowed"
            outside = root / "outside"
            allowed.mkdir()
            outside.mkdir()
            source = outside / "sample.edf"
            source.write_bytes(b"raw")
            with self.assertRaisesRegex(ValueError, "escapes the declared root"):
                inspect_local_recording(source, root_path=allowed)

            outside_signal = outside / "outside.eeg"
            outside_signal.write_bytes(b"signal")
            header = allowed / "linked.vhdr"
            marker = allowed / "linked.vmrk"
            linked_signal = allowed / "linked.eeg"
            linked_signal.symlink_to(outside_signal)
            marker.write_text("marker", encoding="utf-8")
            header.write_text(
                "[Common Infos]\nDataFile=linked.eeg\nMarkerFile=linked.vmrk\n",
                encoding="utf-8",
            )
            report = inspect_local_recording(header, root_path=allowed).report

        self.assertEqual(report["status"], "refused")
        self.assertTrue(
            any("companion cannot be a symlink" in row for row in report["refusals"])
        )
        self.assertEqual(report["access_counts"]["binary_signal_bytes_read"], 0)

    def test_collision_overwrite_and_strict_hash_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edf = root / "sample.edf"
            edf.write_bytes(b"binary")
            result = inspect_local_recording(edf)
            output = root / "out"
            write_intake_artifacts(result, output)
            unrelated = output / "keep.txt"
            unrelated.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "nonempty output directory"):
                write_intake_artifacts(result, output)
            write_intake_artifacts(result, output, overwrite=True)
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")
            self.assertTrue(load_intake_report(output / ARTIFACT_JSON)["audit_validated"])

            tampered = copy.deepcopy(result.report)
            tampered["source"]["files"][0]["path"] = "../escape.edf"
            with self.assertRaisesRegex(ValueError, "Unsafe path"):
                validate_intake_report(tampered)

            tampered = copy.deepcopy(result.report)
            tampered["access_counts"]["model_runs"] = 1
            with self.assertRaisesRegex(ValueError, "forbidden access counts"):
                validate_intake_report(tampered)

            markdown_path = output / ARTIFACT_MARKDOWN
            markdown_bytes = bytearray(markdown_path.read_bytes())
            markdown_bytes[0] = ord("!") if markdown_bytes[0] != ord("!") else ord("#")
            markdown_path.write_bytes(bytes(markdown_bytes))
            with self.assertRaisesRegex(ValueError, "Markdown artifact hash mismatch"):
                load_intake_report(output / ARTIFACT_JSON)

    def test_metadata_path_imports_no_heavy_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            edf = Path(tmp) / "sample.edf"
            edf.write_bytes(b"fixture")
            original_import = builtins.__import__

            def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
                if name.split(".", 1)[0] in {
                    "mne",
                    "mne_bids",
                    "numpy",
                    "scipy",
                    "torch",
                    "brainflow",
                    "pylsl",
                }:
                    raise AssertionError(f"heavy dependency imported: {name}")
                return original_import(name, globals, locals, fromlist, level)

            with patch("builtins.__import__", side_effect=guarded_import):
                report = inspect_local_recording(edf).report

        self.assertEqual(report["access_counts"]["raw_data_reads"], 0)
        self.assertEqual(report["access_counts"]["network_calls"], 0)

    def test_cli_create_inspect_and_collision_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            header, _ = self._brainvision_fixture(root)
            registry = self._registry_fixture(root)
            output = root / "out"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                create_code = main(
                    [
                        "inspect-recording",
                        "--path",
                        str(header),
                        "--out-dir",
                        str(output),
                        "--registry",
                        str(registry),
                        "--modality",
                        "EEG",
                        "--hash-text-metadata",
                    ]
                )
            create_summary = json.loads(stdout.getvalue())
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                inspect_code = main(
                    [
                        "inspect-intake-report",
                        "--report",
                        str(output / ARTIFACT_JSON),
                    ]
                )
            inspect_summary = json.loads(stdout.getvalue())
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                collision_code = main(
                    [
                        "inspect-recording",
                        "--path",
                        str(header),
                        "--out-dir",
                        str(output),
                    ]
                )

        self.assertEqual(create_code, 0)
        self.assertEqual(inspect_code, 0)
        self.assertEqual(collision_code, 2)
        self.assertTrue(create_summary["output_cap_passed"])
        self.assertEqual(create_summary["binary_signal_bytes_read"], 0)
        self.assertTrue(inspect_summary["audit_validated"])
        self.assertIn("nonempty output directory", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
