import frappe

@frappe.whitelist(allow_guest=False)
def lookup_item_by_code(code):
    """
    Lookup a Whatnot Item by barcode, QR code string, or item_code SKU.
    Designed for rapid mobile camera scanning lookups during live shows or warehouse fulfillment.
    """
    if not code:
        frappe.throw("Scanning code is required.")
    
    code = code.strip()

    # Match barcode, qr_code, or item_code
    item = frappe.db.get_value(
        "Whatnot Item",
        {"barcode": code},
        ["name", "item_code", "item_name", "category", "condition", "status", "stock_qty", "cogs", "target_listing_price", "image_url"],
        as_dict=True
    )

    if not item:
        item = frappe.db.get_value(
            "Whatnot Item",
            {"qr_code": code},
            ["name", "item_code", "item_name", "category", "condition", "status", "stock_qty", "cogs", "target_listing_price", "image_url"],
            as_dict=True
        )

    if not item:
        item = frappe.db.get_value(
            "Whatnot Item",
            {"item_code": code},
            ["name", "item_code", "item_name", "category", "condition", "status", "stock_qty", "cogs", "target_listing_price", "image_url"],
            as_dict=True
        )

    if not item:
        return {
            "found": False,
            "message": f"No item found matching code '{code}'."
        }

    # Fetch active shows this item is assigned to
    assigned_shows = frappe.db.sql("""
        SELECT parent as show_id, status, starting_bid, reserve_price
        FROM `tabWhatnot Show Item`
        WHERE item_code = %s
    """, item.name, as_dict=True)

    item["assigned_shows"] = assigned_shows
    return {
        "found": True,
        "item": item
    }
