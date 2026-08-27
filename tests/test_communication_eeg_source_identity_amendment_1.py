from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMENDMENT = (
    ROOT / "registries" / "communication_eeg_source_identity_amendment_1.v0.json"
)
DOCUMENT = ROOT / "docs" / "COMMUNICATION_EEG_SOURCE_IDENTITY_AMENDMENT_1.md"


class CommunicationEEGSourceIdentityAmendment1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))

    def test_parent_and_consumed_module_are_exact_and_unchanged(self) -> None:
        parent = self.amendment["parent_contract"]
        payload = (ROOT / parent["path"]).read_bytes()
        self.assertEqual(parent["bytes"], len(payload))
        self.assertEqual(parent["sha256"], hashlib.sha256(payload).hexdigest())
        module = self.amendment["consumed_generated_implementation_preserved"]
        module_payload = (ROOT / module["module_path"]).read_bytes()
        self.assertEqual(module["module_bytes"], len(module_payload))
        self.assertEqual(module["module_sha256"], hashlib.sha256(module_payload).hexdigest())
        self.assertFalse(module["modified_or_rerun"])

    def test_only_future_transport_cap_is_increased(self) -> None:
        values = self.amendment["overrides_for_future_additive_wrapper_only"]
        self.assertEqual(values["response_body_cap_bytes_original"], 2 << 20)
        self.assertEqual(values["response_body_cap_bytes_amended"], 16 << 20)
        self.assertEqual(values["read_limit_bytes_amended"], (16 << 20) + 1)
        self.assertEqual(values["peak_process_tree_RSS_bytes"], 256 << 20)
        self.assertEqual(values["real_payload_requests"], 0)
        self.assertEqual(values["real_payload_bytes"], 0)

    def test_new_boundary_requires_new_generated_qualification(self) -> None:
        qualification = self.amendment["required_generated_qualification"]
        self.assertTrue(qualification["new_additive_wrapper_required"])
        self.assertFalse(qualification["existing_consumed_module_modified"])
        self.assertFalse(qualification["existing_generated_qualification_rerun"])
        self.assertEqual(
            qualification["boundary_cases_bytes"],
            [(16 << 20) - 1, 16 << 20, (16 << 20) + 1],
        )
        self.assertTrue(qualification["over_cap_refuses"])
        self.assertTrue(
            qualification["canonical_equivalence_with_frozen_module_below_original_cap"]
        )

    def test_authority_and_scientific_claims_remain_false(self) -> None:
        self.assertTrue(all(value is False for value in self.amendment["authority_now"].values()))
        counters = self.amendment["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 3)
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key != "tracked_artifact_reads")
        )
        self.assertTrue(all(value is False for value in self.amendment["claim_boundary"].values()))
        self.assertEqual(
            self.amendment["active_gate_preserved"]["gate_id"],
            "DREYER-C5R-1-HL",
        )

    def test_document_is_plain_about_reason_and_boundary(self) -> None:
        text = " ".join(DOCUMENT.read_text(encoding="utf-8").split())
        for phrase in (
            "real recursive OpenNeuro tree count was known",
            "raise the response-body cap from 2 MiB to 16 MiB",
            "without modifying or rerunning",
            "no execution authority",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
