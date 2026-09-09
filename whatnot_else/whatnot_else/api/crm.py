import frappe

@frappe.whitelist()
def get_buyer_profile(username):
    """
    Rapid lookup of a Whatnot buyer by username for streamer auction awareness.
    Returns LTV, VIP tier, total orders, average order value, and streamer notes.
    """
    if not username:
        frappe.throw("Username is required.")

    username = username.strip().lstrip("@")

    buyer = frappe.db.get_value(
        "Whatnot Buyer",
        {"username": username},
        ["name", "username", "vip_tier", "lifetime_spend", "total_orders_count", "average_order_value", "favorite_category", "streamer_notes"],
        as_dict=True
    )

    if not buyer:
        return {
            "found": False,
            "username": username,
            "message": f"Buyer @{username} has no purchase history."
        }

    # Fetch last 5 orders
    recent_orders = frappe.db.sql("""
        SELECT name, whatnot_order_id, order_date, gross_amount, net_payout, status
        FROM `tabWhatnot Order`
        WHERE buyer_username = %s
        ORDER BY order_date DESC
        LIMIT 5
    """, username, as_dict=True)

    buyer["recent_orders"] = recent_orders

    return {
        "found": True,
        "buyer": buyer
    }

@frappe.whitelist()
def add_buyer_note(username, note):
    """
    Append or update private streamer notes for a buyer.
    """
    if not username or not note:
        frappe.throw("Username and note content are required.")

    username = username.strip().lstrip("@")

    if not frappe.db.exists("Whatnot Buyer", {"username": username}):
        buyer = frappe.get_doc({
            "doctype": "Whatnot Buyer",
            "username": username,
            "streamer_notes": note
        })
        buyer.insert(ignore_permissions=True)
    else:
        buyer = frappe.get_doc("Whatnot Buyer", {"username": username})
        if buyer.streamer_notes:
            buyer.streamer_notes += f"\n- {note}"
        else:
            buyer.streamer_notes = f"- {note}"
        buyer.save(ignore_permissions=True)

    return {
        "status": "success",
        "username": username,
        "streamer_notes": buyer.streamer_notes
    }
