import frappe
from frappe.model.document import Document

class WhatnotShow(Document):
    def validate(self):
        if self.items:
            self.total_items_planned = len(self.items)
            sold = sum(1 for item in self.items if item.status == "Sold")
            self.total_items_sold = sold
            self.gross_sales = sum(item.sold_price or 0.0 for item in self.items if item.status == "Sold")
            self.total_platform_fees = round(self.gross_sales * 0.11, 2)
            self.total_cogs = sum(item.cogs or 0.0 for item in self.items if item.status == "Sold")
            self.net_profit = round(self.gross_sales - self.total_platform_fees - self.total_cogs, 2)

    @frappe.whitelist()
    def start_stream(self):
        self.status = "Live"
        self.save()
        return {"status": "Live"}

    @frappe.whitelist()
    def finish_stream(self):
        self.status = "Completed"
        self.save()
        return {"status": "Completed"}
