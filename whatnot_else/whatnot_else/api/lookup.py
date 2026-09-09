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

@frappe.whitelist(allow_guest=False)
def assign_item_to_show(item_code, show_id, starting_bid=1.0, reserve_price=0.0):
    """
    Directly allocate an item to an active or upcoming live show from mobile scanner.
    """
    if not frappe.db.exists("Whatnot Item", {"item_code": item_code}):
        frappe.throw(f"Item {item_code} not found.")
    if not frappe.db.exists("Whatnot Show", show_id):
        frappe.throw(f"Show {show_id} not found.")

    item_doc = frappe.get_doc("Whatnot Item", {"item_code": item_code})
    show_doc = frappe.get_doc("Whatnot Show", show_id)

    # Append to child table
    show_doc.append("items", {
        "item_code": item_doc.name,
        "item_name": item_doc.item_name,
        "listing_type": "Auction",
        "status": "Planned",
        "starting_bid": float(starting_bid or 1.0),
        "reserve_price": float(reserve_price or 0.0),
        "cogs": float(item_doc.cogs or 0.0)
    })
    show_doc.save(ignore_permissions=True)

    # Update item status
    item_doc.status = "Assigned to Show"
    item_doc.save(ignore_permissions=True)

    return {
        "status": "success",
        "message": f"Successfully assigned {item_doc.item_name} to {show_doc.show_title}"
    }

@frappe.whitelist(allow_guest=False)
def get_active_shows():
    """
    Fetch upcoming or live shows for quick assignment picker in scanner UI.
    """
    return frappe.db.get_list(
        "Whatnot Show",
        filters={"status": ["in", ["Draft", "Scheduled", "Live"]]},
        fields=["name", "show_title", "status", "scheduled_start_time"],
        order_by="scheduled_start_time asc"
    )
