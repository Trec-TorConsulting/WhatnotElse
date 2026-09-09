import csv
import io
import frappe
from frappe.utils import flt, now_datetime

@frappe.whitelist()
def import_whatnot_orders_csv(seller_profile, csv_content=None, file_url=None):
    """
    Ingest Whatnot Seller Hub orders CSV export into Whatnot Order records.
    """
    if not csv_content and file_url:
        _file = frappe.get_doc("File", {"file_url": file_url})
        csv_content = _file.get_content()
    
    if not csv_content:
        frappe.throw("CSV content or valid file URL is required.")
    
    if isinstance(csv_content, bytes):
        csv_content = csv_content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(csv_content))
    processed = 0
    created = 0
    skipped = 0

    for row in reader:
        processed += 1
        # Extract possible column header variations from Whatnot exports
        order_id = row.get("Order ID") or row.get("order_id") or row.get("Order Number") or row.get("Order #")
        buyer = row.get("Buyer") or row.get("buyer_username") or row.get("Username") or "Anonymous Buyer"
        item_title = row.get("Item Title") or row.get("Product") or row.get("Title") or "Whatnot Item"
        gross = flt(row.get("Total Price") or row.get("Sold Price") or row.get("Gross") or row.get("Price") or 0.0)
        whatnot_fee = flt(row.get("Whatnot Fee") or row.get("Commission") or row.get("Platform Fee") or (gross * 0.11))
        shipping = flt(row.get("Shipping Fee") or row.get("Shipping") or 0.0)
        tracking = row.get("Tracking Number") or row.get("Tracking") or ""
        status = row.get("Status") or "Processing"

        if not order_id:
            continue

        if frappe.db.exists("Whatnot Order", {"whatnot_order_id": order_id}):
            skipped += 1
            continue

        order = frappe.get_doc({
            "doctype": "Whatnot Order",
            "whatnot_order_id": order_id,
            "seller_profile": seller_profile,
            "buyer_username": buyer,
            "order_date": now_datetime(),
            "status": "Processing",
            "gross_amount": gross,
            "whatnot_fee": whatnot_fee,
            "shipping_fee": shipping,
            "net_payout": gross - whatnot_fee - shipping,
            "tracking_number": tracking,
            "shipping_status": "Label Generated" if tracking else "Pending",
            "items": [{
                "doctype": "Whatnot Order Item",
                "item_name": item_title,
                "qty": 1,
                "price": gross,
                "amount": gross
            }]
        })
        order.insert(ignore_permissions=True)
        created += 1

    return {
        "status": "success",
        "processed_rows": processed,
        "created_orders": created,
        "skipped_existing": skipped
    }

@frappe.whitelist()
def import_whatnot_inventory_csv(seller_profile, csv_content=None, file_url=None):
    """
    Ingest Whatnot Inventory ledger CSV export into Whatnot Item catalog records.
    """
    if not csv_content and file_url:
        _file = frappe.get_doc("File", {"file_url": file_url})
        csv_content = _file.get_content()
    
    if not csv_content:
        frappe.throw("CSV content or valid file URL is required.")
    
    if isinstance(csv_content, bytes):
        csv_content = csv_content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(csv_content))
    created = 0
    updated = 0

    for row in reader:
        sku = row.get("SKU") or row.get("Item Code") or row.get("Product ID")
        title = row.get("Title") or row.get("Item Name") or row.get("Product Name")
        category = row.get("Category") or "General/Multi-category"
        cogs = flt(row.get("Cost") or row.get("COGS") or row.get("Buy Price") or 0.0)
        target_price = flt(row.get("Target Price") or row.get("Price") or row.get("Listing Price") or 0.0)
        qty = int(row.get("Quantity") or row.get("Stock") or 1)
        barcode = row.get("Barcode") or sku or ""

        if not title:
            continue

        item_code = sku or frappe.scrub(title).upper()[:20]

        if frappe.db.exists("Whatnot Item", {"item_code": item_code}):
            item = frappe.get_doc("Whatnot Item", {"item_code": item_code})
            item.stock_qty = qty
            item.cogs = cogs
            item.target_listing_price = target_price
            item.save(ignore_permissions=True)
            updated += 1
        else:
            item = frappe.get_doc({
                "doctype": "Whatnot Item",
                "item_name": title,
                "item_code": item_code,
                "seller_profile": seller_profile,
                "category": category,
                "stock_qty": qty,
                "cogs": cogs,
                "target_listing_price": target_price,
                "barcode": barcode,
                "status": "Available"
            })
            item.insert(ignore_permissions=True)
            created += 1

    return {
        "status": "success",
        "created_items": created,
        "updated_items": updated
    }
