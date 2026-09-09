import unittest
from unittest.mock import MagicMock, patch
import json
import os

# Standalone mockable test for fulfillment tray logic
class MockItem:
    def __init__(self, item_code, item_name, barcode, weight_oz=2.0, is_sorted=0, is_packed=0):
        self.item_code = item_code
        self.item_name = item_name
        self.barcode = barcode
        self.weight_oz = weight_oz
        self.is_sorted = is_sorted
        self.is_packed = is_packed
        self.verified_at = None

class MockTray:
    def __init__(self, tray_number=1, show="SHOW-001", buyer_username="test_buyer"):
        self.name = f"TRAY-{tray_number}-{show}"
        self.tray_number = tray_number
        self.show = show
        self.buyer_username = buyer_username
        self.status = "Available"
        self.total_items = 0
        self.sorted_items = 0
        self.packed_items = 0
        self.total_weight_oz = 0.0
        self.weight_warning = 0
        self.weight_warning_notes = ""
        self.items = []

    def recalculate_metrics(self):
        total = len(self.items) if self.items else 0
        sorted_count = sum(1 for item in self.items if item.is_sorted)
        packed_count = sum(1 for item in self.items if item.is_packed)
        total_weight = sum(item.weight_oz or 0.0 for item in self.items)

        self.total_items = total
        self.sorted_items = sorted_count
        self.packed_items = packed_count
        self.total_weight_oz = round(total_weight, 2)

        if self.total_weight_oz > 16.0:
            self.weight_warning = 1
            lbs = round(self.total_weight_oz / 16.0, 2)
            self.weight_warning_notes = (
                f"Combined parcel weight is {self.total_weight_oz} oz ({lbs} lbs). "
                "Exceeds USPS 1-lb Ground Advantage threshold. Verify shipping label tier before dispatch."
            )
        else:
            self.weight_warning = 0
            self.weight_warning_notes = ""

        if self.status != "Shipped":
            if total > 0 and packed_count == total:
                self.status = "Packed"
            elif packed_count > 0:
                self.status = "Sorting"
            elif total > 0 and sorted_count == total:
                self.status = "Ready to Pack"
            elif sorted_count > 0:
                self.status = "Sorting"
            elif total > 0:
                self.status = "Allocated"
            else:
                self.status = "Available"

    def mark_item_sorted(self, barcode):
        for item in self.items:
            if item.barcode == barcode or item.item_code == barcode:
                item.is_sorted = 1
                self.recalculate_metrics()
                return True
        return False

    def mark_item_packed(self, barcode):
        for item in self.items:
            if (item.barcode == barcode or item.item_code == barcode) and not item.is_packed:
                item.is_packed = 1
                self.recalculate_metrics()
                return True
        return False


class TestWhatnotFulfillmentTray(unittest.TestCase):
    def test_empty_tray_initialization(self):
        tray = MockTray(tray_number=1, show="SHOW-001", buyer_username="card_collector")
        tray.recalculate_metrics()
        self.assertEqual(tray.status, "Available")
        self.assertEqual(tray.total_items, 0)
        self.assertEqual(tray.weight_warning, 0)

    def test_items_allocation_and_status_progression(self):
        tray = MockTray(tray_number=14, show="SHOW-001", buyer_username="poke_master")
        item1 = MockItem("ITEM-001", "Charizard Base 1st Ed", "BAR-001", weight_oz=3.0)
        item2 = MockItem("ITEM-002", "Blastoise Holo", "BAR-002", weight_oz=3.0)
        tray.items = [item1, item2]

        tray.recalculate_metrics()
        self.assertEqual(tray.total_items, 2)
        self.assertEqual(tray.status, "Allocated")
        self.assertEqual(tray.total_weight_oz, 6.0)
        self.assertEqual(tray.weight_warning, 0)

        # Sort item 1
        success = tray.mark_item_sorted("BAR-001")
        self.assertTrue(success)
        self.assertEqual(tray.sorted_items, 1)
        self.assertEqual(tray.status, "Sorting")

        # Sort item 2 -> all sorted -> Ready to Pack
        tray.mark_item_sorted("BAR-002")
        self.assertEqual(tray.sorted_items, 2)
        self.assertEqual(tray.status, "Ready to Pack")

        # Pack item 1 -> Sorting/Packing
        tray.mark_item_packed("BAR-001")
        self.assertEqual(tray.packed_items, 1)
        self.assertEqual(tray.status, "Sorting")

        # Pack item 2 -> All packed -> Packed
        tray.mark_item_packed("BAR-002")
        self.assertEqual(tray.packed_items, 2)
        self.assertEqual(tray.status, "Packed")

    def test_weight_tier_threshold_warning(self):
        tray = MockTray(tray_number=5, show="SHOW-001", buyer_username="comic_collector")
        # 10 slabs at 2.5 oz each = 25 oz (exceeds 16 oz)
        tray.items = [
            MockItem(f"COMIC-{i}", f"Spider-Man #{i} CGC 9.8", f"BAR-{i}", weight_oz=2.5)
            for i in range(10)
        ]
        tray.recalculate_metrics()
        self.assertEqual(tray.total_weight_oz, 25.0)
        self.assertEqual(tray.weight_warning, 1)
        self.assertIn("Exceeds USPS 1-lb Ground Advantage threshold", tray.weight_warning_notes)

    def test_schema_definitions_validity(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Test Whatnot Fulfillment Tray schema
        tray_json = os.path.join(base_dir, "whatnot_else", "doctype", "whatnot_fulfillment_tray", "whatnot_fulfillment_tray.json")
        with open(tray_json) as f:
            data = json.load(f)
            self.assertEqual(data.get("name"), "Whatnot Fulfillment Tray")
            self.assertTrue(any(f["fieldname"] == "tray_number" for f in data["fields"]))
            self.assertTrue(any(f["fieldname"] == "weight_warning" for f in data["fields"]))

        # Test Whatnot Item collectible fields
        item_json = os.path.join(base_dir, "whatnot_else", "doctype", "whatnot_item", "whatnot_item.json")
        with open(item_json) as f:
            data = json.load(f)
            self.assertTrue(any(f["fieldname"] == "is_graded" for f in data["fields"]))
            self.assertTrue(any(f["fieldname"] == "grading_company" for f in data["fields"]))
            self.assertTrue(any(f["fieldname"] == "cert_number" for f in data["fields"]))
            self.assertTrue(any(f["fieldname"] == "weight_oz" for f in data["fields"]))

        # Test Whatnot Order fulfillment_tray link field
        order_json = os.path.join(base_dir, "whatnot_else", "doctype", "whatnot_order", "whatnot_order.json")
        with open(order_json) as f:
            data = json.load(f)
            self.assertTrue(any(f["fieldname"] == "fulfillment_tray" for f in data["fields"]))


if __name__ == "__main__":
    unittest.main()
