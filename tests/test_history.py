import unittest

from medical_prescription.domain import build_grid, protect_signed_orders


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "item_unique_key": "order-a",
            "medication": "Synthetic",
            "frequency": "BID",
            "dosage": "1-0-1",
            "dose_number": "5",
            "dose_uom": "mg",
            "route": "PO",
        }
        self.grid = build_grid([self.item], [], "2026-11-04")

    def test_signed_order_cannot_be_removed_or_rekeyed(self):
        self.grid[0]["step_1_done"] = 1
        for items in ([], [{**self.item, "item_unique_key": "other"}]):
            with self.assertRaises(ValueError):
                protect_signed_orders([self.item], items, self.grid)

    def test_completed_order_cannot_have_dose_changed(self):
        self.grid[0]["completed"] = 1
        with self.assertRaises(ValueError):
            protect_signed_orders([self.item], [{**self.item, "dose_number": "50"}], self.grid)

    def test_stopping_signed_order_retains_context(self):
        self.grid[0]["given"] = 1
        protect_signed_orders([self.item], [{**self.item, "is_stopped": 1}], self.grid)

    def test_unsigned_grid_updates_but_signed_slot_is_immutable(self):
        self.grid[0].update(step_1_done=1, step_1_by="synthetic-nurse")
        result = build_grid([{**self.item, "dosage": "1-1-1"}], self.grid, "2026-11-04")
        self.assertEqual(result[0], self.grid[0])
        self.assertEqual(result[1]["dosage"], "1-1-1")
        self.assertEqual(self.grid[1]["dosage"], "1-0-1")
