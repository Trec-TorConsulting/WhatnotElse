import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class WhatnotFulfillmentTray(Document):
    def validate(self):
        self.recalculate_metrics()

    def recalculate_metrics(self):
        """
        Calculates item counts, packed state, and combined weight warning.
        """
        total = len(self.items) if self.items else 0
        sorted_count = sum(1 for item in self.items if item.is_sorted)
        packed_count = sum(1 for item in self.items if item.is_packed)
        total_weight = sum(item.weight_oz or 0.0 for item in self.items)

        self.total_items = total
        self.sorted_items = sorted_count
        self.packed_items = packed_count
        self.total_weight_oz = round(total_weight, 2)

        # Shipping tier warning (USPS First Class / Ground Advantage 16 oz limit)
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

        # Lifecycle status progression
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
        """
        Marks an item in this tray as physically sorted from stream.
        """
        for item in self.items:
            if item.barcode == barcode or item.item_code == barcode:
                item.is_sorted = 1
                self.recalculate_metrics()
                self.save(ignore_permissions=True)
                return True
        return False

    def mark_item_packed(self, barcode):
        """
        Verifies and packs an item into shipping box.
        """
        for item in self.items:
            if (item.barcode == barcode or item.item_code == barcode) and not item.is_packed:
                item.is_packed = 1
                item.verified_at = now_datetime()
                self.recalculate_metrics()
                self.save(ignore_permissions=True)
                return True
        return False
