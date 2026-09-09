import frappe
from frappe.model.document import Document

class WhatnotBuyer(Document):
    def update_metrics(self):
        orders = frappe.db.sql("""
            SELECT 
                COUNT(name) as count,
                SUM(gross_amount) as total_spend,
                MAX(order_date) as last_date
            FROM `tabWhatnot Order`
            WHERE buyer_username = %s
              AND docstatus < 2
        """, self.username, as_dict=True)

        if orders:
            res = orders[0]
            self.total_orders_count = res.get("count") or 0
            self.lifetime_spend = res.get("total_spend") or 0.0
            self.last_order_date = res.get("last_date")
            if self.total_orders_count > 0:
                self.average_order_value = round(self.lifetime_spend / self.total_orders_count, 2)

            # Auto-assign VIP tiers based on spend thresholds
            if self.lifetime_spend >= 5000.0:
                self.vip_tier = "Whale VIP"
            elif self.lifetime_spend >= 1500.0:
                self.vip_tier = "Gold VIP"
            elif self.lifetime_spend >= 500.0:
                self.vip_tier = "Silver VIP"
            else:
                self.vip_tier = "Standard"
            
            self.save(ignore_permissions=True)
