import frappe
from frappe.model.document import Document

class WhatnotOrder(Document):
    def validate(self):
        if not self.net_payout:
            self.net_payout = (self.gross_amount or 0.0) - (self.whatnot_fee or 0.0) - (self.shipping_fee or 0.0)

    def on_submit(self):
        create_erpnext_sales_order(self)
        update_buyer_record(self)
        trigger_cross_platform_updates(self)

def trigger_cross_platform_updates(doc):
    from whatnot_else.api.sync import trigger_cross_platform_delist
    for item in (doc.items or []):
        if item.item_code:
            frappe.enqueue(
                trigger_cross_platform_delist,
                queue="default",
                item_code_or_sku=item.item_code,
                reason=f"Order {doc.whatnot_order_id} submitted"
            )

def update_buyer_record(doc):
    if not doc.buyer_username:
        return
    if not frappe.db.exists("Whatnot Buyer", {"username": doc.buyer_username}):
        buyer = frappe.get_doc({
            "doctype": "Whatnot Buyer",
            "username": doc.buyer_username,
            "seller_profile": doc.seller_profile
        })
        buyer.insert(ignore_permissions=True)
    else:
        buyer = frappe.get_doc("Whatnot Buyer", {"username": doc.buyer_username})
    
    buyer.update_metrics()

def create_erpnext_sales_order(doc, method=None):
    if doc.erpnext_sales_order:
        return
    # Check if ERPNext Sales Order doctype is installed in the bench
    if not frappe.db.exists("DocType", "Sales Order"):
        return
    
    # Check if customer exists for buyer_username, otherwise create a light customer
    customer_name = doc.buyer_username
    if not frappe.db.exists("Customer", customer_name):
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "customer_group": "All Customer Groups",
            "territory": "All Territories"
        })
        customer.insert(ignore_permissions=True)
    
    so_items = []
    for item in (doc.items or []):
        so_items.append({
            "item_code": item.item_code or "Whatnot Item",
            "item_name": item.item_name or "Whatnot Item",
            "qty": item.qty or 1,
            "rate": item.price or 0.0,
            "amount": (item.qty or 1) * (item.price or 0.0)
        })
    
    if not so_items:
        so_items.append({
            "item_code": "Whatnot Item",
            "item_name": "Whatnot Auction Item",
            "qty": 1,
            "rate": doc.gross_amount or 0.0,
            "amount": doc.gross_amount or 0.0
        })

    so = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer_name,
        "transaction_date": frappe.utils.today(),
        "delivery_date": frappe.utils.add_days(frappe.utils.today(), 3),
        "items": so_items
    })
    so.insert(ignore_permissions=True)
    doc.db_set("erpnext_sales_order", so.name)
