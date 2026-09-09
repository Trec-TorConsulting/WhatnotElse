import frappe
from frappe.utils import now_datetime, flt, cint

@frappe.whitelist(allow_guest=False)
def allocate_show_trays(show_name, max_trays=150):
    """
    Automatically allocates physical fulfillment trays for all unique buyers with orders in a show.
    Assigns sequential tray numbers (Tray 1 to N) and groups all line items per buyer into their tray.
    """
    if not show_name:
        frappe.throw("Show Name is required to allocate trays.")

    show = frappe.get_doc("Whatnot Show", show_name)
    max_trays = cint(max_trays) or 150

    # Fetch all orders associated with this show or orders with items from this show
    orders = frappe.db.sql("""
        SELECT DISTINCT o.name, o.buyer_username
        FROM `tabWhatnot Order` o
        JOIN `tabWhatnot Order Item` oi ON oi.parent = o.name
        WHERE oi.whatnot_show_id = %s OR o.name IN (
            SELECT DISTINCT parent FROM `tabWhatnot Show Item` WHERE parent = %s
        )
    """, (show_name, show_name), as_dict=True)

    if not orders:
        # Fallback: check orders directly tagged or show items sold
        orders = frappe.db.sql("""
            SELECT name, buyer_username
            FROM `tabWhatnot Order`
            WHERE docstatus < 2
        """, as_dict=True)

    # Group orders by buyer_username
    buyer_orders = {}
    for o in orders:
        buyer = o.buyer_username
        if not buyer:
            continue
        buyer_orders.setdefault(buyer, []).append(o.name)

    if not buyer_orders:
        return {
            "success": False,
            "message": f"No orders or buyers found for show '{show_name}'."
        }

    allocated_trays = []
    current_tray_num = 1

    for buyer_username, order_ids in buyer_orders.items():
        if current_tray_num > max_trays:
            break

        # Check if tray already exists for this show and buyer
        existing_tray_name = frappe.db.get_value(
            "Whatnot Fulfillment Tray",
            {"show": show_name, "buyer_username": buyer_username},
            "name"
        )

        if existing_tray_name:
            tray = frappe.get_doc("Whatnot Fulfillment Tray", existing_tray_name)
        else:
            tray = frappe.new_doc("Whatnot Fulfillment Tray")
            tray.tray_number = current_tray_num
            tray.show = show_name
            tray.buyer_username = buyer_username
            tray.status = "Allocated"
            
            # Link Whatnot Buyer doc if exists
            buyer_doc_name = frappe.db.get_value("Whatnot Buyer", {"whatnot_username": buyer_username}, "name")
            if buyer_doc_name:
                tray.buyer = buyer_doc_name

        # Populate or refresh tray items from orders
        tray.items = []
        for order_id in order_ids:
            order_items = frappe.get_all(
                "Whatnot Order Item",
                filters={"parent": order_id},
                fields=["item_code", "item_name", "qty"]
            )
            for idx, oi in enumerate(order_items):
                # Retrieve item details (barcode, weight)
                item_details = frappe.db.get_value(
                    "Whatnot Item",
                    oi.item_code,
                    ["barcode", "weight_oz"],
                    as_dict=True
                ) or {}

                tray.append("items", {
                    "item_code": oi.item_code,
                    "item_name": oi.item_name,
                    "barcode": item_details.get("barcode") or oi.item_code,
                    "order_id": order_id,
                    "lot_number": idx + 1,
                    "weight_oz": flt(item_details.get("weight_oz", 2.0)),
                    "is_sorted": 0,
                    "is_packed": 0
                })

            # Associate order back to tray
            frappe.db.set_value("Whatnot Order", order_id, "fulfillment_tray", tray.name, update_modified=False)

        tray.recalculate_metrics()
        tray.save(ignore_permissions=True)
        allocated_trays.append({
            "tray_name": tray.name,
            "tray_number": tray.tray_number,
            "buyer_username": tray.buyer_username,
            "total_items": tray.total_items,
            "total_weight_oz": tray.total_weight_oz,
            "weight_warning": bool(tray.weight_warning)
        })
        current_tray_num += 1

    frappe.db.commit()
    return {
        "success": True,
        "show": show_name,
        "total_trays_allocated": len(allocated_trays),
        "trays": allocated_trays
    }

@frappe.whitelist(allow_guest=False)
def scan_item_to_tray(barcode, show_name=None):
    """
    Mode 1 (Scan-to-Tray):
    Resolves scanned item to its designated tray and buyer for physical sorting.
    Updates item sorted state and triggers spoken announcement metadata.
    """
    if not barcode:
        frappe.throw("Barcode is required.")

    barcode = barcode.strip()

    # Search for an assigned tray item across active trays for this show
    filters = {}
    if show_name:
        filters["show"] = show_name

    tray_names = frappe.get_all("Whatnot Fulfillment Tray", filters=filters, pluck="name")

    for tname in tray_names:
        tray = frappe.get_doc("Whatnot Fulfillment Tray", tname)
        for item in tray.items:
            if item.barcode == barcode or item.item_code == barcode:
                # Found matching item in tray
                item.is_sorted = 1
                tray.recalculate_metrics()
                tray.save(ignore_permissions=True)
                frappe.db.commit()

                return {
                    "success": True,
                    "tray_number": tray.tray_number,
                    "tray_name": tray.name,
                    "buyer_username": tray.buyer_username,
                    "item_name": item.item_name,
                    "lot_number": item.lot_number,
                    "sorted_items": tray.sorted_items,
                    "total_items": tray.total_items,
                    "status": tray.status,
                    "weight_warning": bool(tray.weight_warning),
                    "weight_warning_notes": tray.weight_warning_notes,
                    "speech_text": f"Tray {tray.tray_number}, {tray.buyer_username}"
                }

    # Item not found in any tray
    return {
        "success": False,
        "barcode": barcode,
        "message": f"Item with code '{barcode}' is not assigned to any tray for show '{show_name or 'All'}'."
    }

@frappe.whitelist(allow_guest=False)
def verify_box_item(tray_name, barcode):
    """
    Mode 2 (Scan-to-Box):
    Verifies that a scanned item belongs to the active box being packed.
    If the item belongs to a DIFFERENT tray, triggers an urgent MIS-SHIP alarm.
    """
    if not tray_name or not barcode:
        frappe.throw("Both tray_name and barcode are required for packing verification.")

    barcode = barcode.strip()
    tray = frappe.get_doc("Whatnot Fulfillment Tray", tray_name)

    # 1. Check if item is in THIS tray
    for item in tray.items:
        if item.barcode == barcode or item.item_code == barcode:
            if item.is_packed:
                return {
                    "success": True,
                    "already_packed": True,
                    "message": f"Item '{item.item_name}' was already packed.",
                    "packed_items": tray.packed_items,
                    "total_items": tray.total_items
                }

            item.is_packed = 1
            item.verified_at = now_datetime()
            tray.recalculate_metrics()
            tray.save(ignore_permissions=True)
            frappe.db.commit()

            is_complete = (tray.packed_items == tray.total_items)
            return {
                "success": True,
                "already_packed": False,
                "tray_name": tray.name,
                "tray_number": tray.tray_number,
                "buyer_username": tray.buyer_username,
                "item_name": item.item_name,
                "packed_items": tray.packed_items,
                "total_items": tray.total_items,
                "is_complete": is_complete,
                "total_weight_oz": tray.total_weight_oz,
                "weight_warning": bool(tray.weight_warning),
                "weight_warning_notes": tray.weight_warning_notes,
                "message": f"Verified '{item.item_name}' into Box ({tray.packed_items}/{tray.total_items})"
            }

    # 2. Check if item belongs to ANOTHER tray (MIS-SHIP PROTECTION)
    other_tray_items = frappe.db.sql("""
        SELECT parent as other_tray_name
        FROM `tabWhatnot Fulfillment Tray Item`
        WHERE (barcode = %s OR item_code = %s) AND parent != %s
    """, (barcode, barcode, tray_name), as_dict=True)

    if other_tray_items:
        other_name = other_tray_items[0].other_tray_name
        other_tray = frappe.get_doc("Whatnot Fulfillment Tray", other_name)
        return {
            "success": False,
            "error_type": "MIS_SHIP_ALARM",
            "message": f"MIS-SHIP DETECTED! Scanned item belongs to Tray #{other_tray.tray_number} (@{other_tray.buyer_username}), NOT this box!",
            "actual_tray": other_tray.tray_number,
            "actual_buyer": other_tray.buyer_username
        }

    return {
        "success": False,
        "error_type": "UNKNOWN_ITEM",
        "message": f"Scanned code '{barcode}' does not belong to Tray #{tray.tray_number} or this show manifest."
    }

@frappe.whitelist(allow_guest=False)
def calculate_combined_weight(tray_name):
    """
    Returns the total cumulative parcel weight and checks USPS Ground Advantage / Priority tier thresholds.
    """
    if not tray_name:
        frappe.throw("tray_name is required.")

    tray = frappe.get_doc("Whatnot Fulfillment Tray", tray_name)
    tray.recalculate_metrics()
    tray.save(ignore_permissions=True)

    return {
        "tray_name": tray.name,
        "tray_number": tray.tray_number,
        "buyer_username": tray.buyer_username,
        "total_items": tray.total_items,
        "total_weight_oz": tray.total_weight_oz,
        "weight_warning": bool(tray.weight_warning),
        "weight_warning_notes": tray.weight_warning_notes,
        "suggested_carrier_service": "USPS Priority Mail / UPS" if tray.total_weight_oz > 16.0 else "USPS Ground Advantage (< 1 lb)"
    }

@frappe.whitelist(allow_guest=False)
def get_show_fulfillment_status(show_name):
    """
    Returns full fulfillment status overview for all trays in a live show.
    """
    if not show_name:
        frappe.throw("show_name is required.")

    trays = frappe.get_all(
        "Whatnot Fulfillment Tray",
        filters={"show": show_name},
        fields=["name", "tray_number", "buyer_username", "status", "total_items", "sorted_items", "packed_items", "total_weight_oz", "weight_warning"],
        order_by="tray_number asc"
    )

    total_trays = len(trays)
    fully_packed = sum(1 for t in trays if t.status in ("Packed", "Shipped"))
    ready_to_pack = sum(1 for t in trays if t.status == "Ready to Pack")

    return {
        "show": show_name,
        "total_trays": total_trays,
        "fully_packed": fully_packed,
        "ready_to_pack": ready_to_pack,
        "completion_pct": round((fully_packed / total_trays * 100), 1) if total_trays else 0.0,
        "trays": trays
    }
