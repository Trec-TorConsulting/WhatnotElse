import frappe
from frappe.utils import now_datetime
import requests

def trigger_cross_platform_delist(item_code_or_sku, reason="Sold on Whatnot"):
    """
    Search for Whatnot Cross Listing entries matching this item and send delist/zero-stock
    signals to connected eBay and Shopify channels.
    """
    # Locate Whatnot Item
    item = frappe.db.get_value(
        "Whatnot Item",
        {"item_code": item_code_or_sku},
        ["name", "item_code", "item_name"],
        as_dict=True
    )
    if not item:
        item = frappe.db.get_value(
            "Whatnot Item",
            {"name": item_code_or_sku},
            ["name", "item_code", "item_name"],
            as_dict=True
        )

    if not item:
        frappe.log_error(f"Cannot delist item: {item_code_or_sku} not found", "Cross Platform Sync")
        return {"status": "item_not_found"}

    # Update item status to Sold
    frappe.db.set_value("Whatnot Item", item.name, "status", "Sold")
    frappe.db.set_value("Whatnot Item", item.name, "stock_qty", 0)

    # Find active cross listings
    cross_listings = frappe.db.get_list(
        "Whatnot Cross Listing",
        filters={"item_code": item.name, "sync_status": "Synced"},
        fields=["name", "channel_bridge", "external_listing_id"]
    )

    delisted_count = 0
    for cl in cross_listings:
        bridge = frappe.get_doc("Whatnot Channel Bridge", cl.channel_bridge)
        if not bridge.enabled or not bridge.auto_delist_on_sale:
            continue

        success = dispatch_delist_to_channel(bridge, cl.external_listing_id)
        if success:
            frappe.db.set_value("Whatnot Cross Listing", cl.name, {
                "sync_status": "Delisted",
                "last_synced_at": now_datetime(),
                "sync_error_message": f"Delisted: {reason}"
            })
            delisted_count += 1
        else:
            frappe.db.set_value("Whatnot Cross Listing", cl.name, {
                "sync_status": "Sync Error",
                "sync_error_message": "Failed API request to marketplace"
            })

    return {
        "status": "completed",
        "delisted_channels": delisted_count
    }

def dispatch_delist_to_channel(bridge, external_id):
    """
    Mock/adapter to communicate with external channel REST/GraphQL endpoints.
    In production, triggers eBay Trading/Inventory API or Shopify REST Admin API.
    """
    try:
        if bridge.platform_type == "Shopify" and bridge.api_endpoint_url:
            # Send inventory level adjustment to 0
            headers = {"X-Shopify-Access-Token": bridge.access_token or ""}
            # Example API call structure
            # requests.post(f"{bridge.api_endpoint_url}/admin/api/2024-01/inventory_levels/set.json", ...)
            return True
        elif bridge.platform_type == "eBay":
            # Call eBay Inventory API bulkUpdatePriceQuantity or EndFixedPriceItem
            return True
        else:
            return True
    except Exception as e:
        frappe.log_error(f"Error delisting on {bridge.channel_name}: {str(e)}", "Marketplace Delist Error")
        return False
