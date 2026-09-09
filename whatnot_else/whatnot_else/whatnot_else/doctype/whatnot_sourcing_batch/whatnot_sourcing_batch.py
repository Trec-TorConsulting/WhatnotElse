import frappe
from frappe.model.document import Document
from frappe.utils import flt

class WhatnotSourcingBatch(Document):
    def validate(self):
        if self.items:
            self.total_items_count = len(self.items)
            if self.allocation_method == "Equal Split" and self.total_items_count > 0:
                unit_cogs = round(flt(self.total_cost) / self.total_items_count, 2)
                for item in self.items:
                    item.allocated_cogs = unit_cogs

    @frappe.whitelist()
    def generate_catalog_items(self):
        """
        Create official Whatnot Item catalog records from the sourcing items.
        """
        created = 0
        for item in (self.items or []):
            if item.linked_item:
                continue
            
            item_code = frappe.scrub(item.item_title).upper()[:20]
            new_item = frappe.get_doc({
                "doctype": "Whatnot Item",
                "item_name": item.item_title,
                "item_code": item_code,
                "seller_profile": self.seller_profile,
                "category": item.category or "General/Multi-category",
                "condition": item.condition or "Good",
                "stock_qty": 1,
                "cogs": item.allocated_cogs or 0.0,
                "target_listing_price": item.target_price or 0.0,
                "status": "Available"
            })
            new_item.insert(ignore_permissions=True)
            item.db_set("linked_item", new_item.name)
            created += 1

        return {
            "status": "success",
            "created_count": created
        }
