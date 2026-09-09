import frappe
from frappe.model.document import Document
import re

class WhatnotSellerProfile(Document):
    def validate(self):
        if self.seller_slug:
            self.seller_slug = re.sub(r'[^a-zA-Z0-9-]', '', self.seller_slug.lower())
