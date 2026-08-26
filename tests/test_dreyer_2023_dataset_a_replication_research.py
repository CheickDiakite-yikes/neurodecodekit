from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_PATH = ROOT / "registries/dreyer_2023_dataset_a_replication_research.v0.json"
PAYLOAD_MANIFEST_PATH = (
    ROOT / "registries/dreyer_2023_dataset_a_r1_r2_payload_manifest.v0.json"
)
DOC_PATH = ROOT / "docs/DREYER_2023_DATASET_A_REPLICATION_PRIMARY_SOURCE_RESEARCH.md"


class DreyerDatasetAReplicationResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.research = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))
        cls.manifest_bytes = PAYLOAD_MANIFEST_PATH.read_bytes()
        cls.manifest = json.loads(cls.manifest_bytes)

    def test_source_and_selection_are_exact(self) -> None:
        self.assertEqual(self.research["lane_id"], "DREYER-C5R-1")
        source = self.research["primary_sources"]
        self.assertEqual(source["nemar_dataset_id"], "nm000250")
        self.assertEqual(source["nemar_tag"], "v1.0.4")
        self.assertEqual(
            source["nemar_peeled_commit"],
            "86c5e1a6dc066313c8a1aa12f2d7a75dd5ff58f0",
        )
        selection = self.research["selection"]
        self.assertEqual(selection["payload_member_count"], 120)
        self.assertEqual(selection["payload_bytes"], 1_779_763_388)
        self.assertEqual(selection["preserved_runs"], ["R3", "R4", "R5", "R6"])

    def test_exact_payload_manifest_identity_and_grid(self) -> None:
        self.assertEqual(len(self.manifest_bytes), 41_723)
        self.assertEqual(
            hashlib.sha256(self.manifest_bytes).hexdigest(),
            "b21b720138915ae223d8381ed005a03dac3f6062e1d3651676303f41424d7c78",
        )
        members = self.manifest["selection"]["members"]
        self.assertEqual(len(members), 120)
        self.assertEqual(sum(row["size"] for row in members), 1_779_763_388)
        self.assertEqual(len({row["sha256"] for row in members}), 120)
        observed = set()
        pattern = re.compile(
            r"^sourcedata/sub-(\d{2})/eeg/sub-\1_task-R([12])acquisition_eeg[.]edf$"
        )
        for row in members:
            match = pattern.fullmatch(row["path"])
            self.assertIsNotNone(match, row["path"])
            observed.add((int(match.group(1)), match.group(2)))
            self.assertEqual(len(row["sha256"]), 64)
            self.assertTrue(row["bytes_url"].startswith("https://data.nemar.org/"))
        self.assertEqual(observed, {(p, r) for p in range(1, 61) for r in ("1", "2")})

    def test_preflight_fails_closed_before_bulk_acquisition(self) -> None:
        preflight = self.research["preflight"]
        self.assertTrue(preflight["required"])
        self.assertEqual(preflight["must_confirm_EEG_channels"], 27)
        self.assertEqual(preflight["must_confirm_EOG_channels"], 3)
        self.assertEqual(preflight["must_confirm_EMG_channels"], 2)
        self.assertEqual(preflight["must_confirm_sampling_rate_hz"], 512)
        self.assertEqual(
            preflight["failure_action"],
            "park_lane_before_bulk_acquisition_no_substitution",
        )

    def test_research_read_no_neural_payload_or_target(self) -> None:
        counters = self.research["access_counters"]
        self.assertEqual(counters["official_manifest_downloads"], 1)
        self.assertEqual(counters["official_manifest_bytes"], 2_364_825)
        for key in (
            "EDF_payload_downloads",
            "EDF_header_reads",
            "EDF_annotation_reads",
            "signal_sample_reads",
            "target_or_label_reads",
            "training_runs",
            "inference_runs",
            "scores",
        ):
            self.assertEqual(counters[key], 0, key)

    def test_document_names_visual_and_peripheral_confounds(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("lateralized red arrow", text)
        self.assertIn("three right-eye EOG", text)
        self.assertIn("two wrist EMG", text)
        self.assertIn("not EEG versus chance", text)
        self.assertIn("could not establish spontaneous movement intention", text)


if __name__ == "__main__":
    unittest.main()
