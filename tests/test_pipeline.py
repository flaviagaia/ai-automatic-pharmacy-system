from __future__ import annotations

import unittest
from pathlib import Path

from src.data_factory import build_sample_dataset
from src.operations import inventory_status
from src.pipeline import run_pipeline


class AutomaticPharmacyPipelineTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[1]

    def test_dataset_factory_creates_expected_files(self) -> None:
        dataset_info = build_sample_dataset(self.base_dir)
        self.assertEqual(dataset_info["dataset_source"], "synthea_rxnorm_dailymed_openfda_style_sample")
        self.assertTrue(Path(dataset_info["patients_path"]).exists())
        self.assertTrue(Path(dataset_info["knowledge_base_path"]).exists())
        self.assertTrue(Path(dataset_info["dataset_reference_path"]).exists())

    def test_pipeline_summary_contract(self) -> None:
        summary = run_pipeline(self.base_dir)
        self.assertEqual(summary["patient_count"], 4)
        self.assertEqual(summary["prescription_count"], 7)
        self.assertEqual(summary["blocked_count"], 3)
        self.assertEqual(summary["pharmacist_review_count"], 3)
        self.assertEqual(summary["auto_dispense_count"], 1)
        self.assertEqual(summary["top_priority_decision"], "BLOCK")
        self.assertIn("RX-1001", summary["blocked_prescriptions"])
        self.assertIn("RX-1003", summary["blocked_prescriptions"])
        self.assertIn("RX-1002", summary["pharmacist_review_prescriptions"])
        queue_text = Path(summary["queue_artifact"]).read_text(encoding="utf-8")
        self.assertIn("RX-1005", queue_text)
        self.assertIn("interaction_detected", queue_text)
        self.assertIn("rag_guidance", queue_text)
        self.assertIn("retrieved_titles", queue_text)

    def test_inventory_status_uses_pending_demand(self) -> None:
        self.assertEqual(inventory_status(available_units=20, reorder_point=10, pending_units=12), "Repor agora")
        self.assertEqual(inventory_status(available_units=20, reorder_point=10, pending_units=7), "Monitorar")
        self.assertEqual(inventory_status(available_units=40, reorder_point=10, pending_units=5), "Estável")


if __name__ == "__main__":
    unittest.main()
