import frappe
from frappe.model.document import Document

class WhatnotItem(Document):
    def validate(self):
        if not self.item_code and self.item_name:
            self.item_code = frappe.scrub(self.item_name).upper()[:20]
        if not self.barcode and self.item_code:
            self.barcode = self.item_code
