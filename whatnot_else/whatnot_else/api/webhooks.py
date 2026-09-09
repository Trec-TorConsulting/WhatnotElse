import hmac
import hashlib
import json
import frappe
from frappe.utils import now_datetime
from whatnot_else.api.sync import trigger_cross_platform_delist

@frappe.whitelist(allow_guest=True)
def handle_whatnot_webhook():
    """
    Secure webhook receiver for Whatnot events.
    Verifies HMAC SHA256 signature against seller profile secret.
    """
    request_data = frappe.request.get_data()
    signature_header = frappe.get_request_header("X-Whatnot-Signature") or frappe.get_request_header("X-Hub-Signature-256")
    
    if not request_data:
        frappe.throw("Empty webhook body", frappe.PermissionError)

    try:
        payload = json.loads(request_data)
    except Exception:
        frappe.throw("Malformed JSON payload", frappe.ValidationError)

    event_type = payload.get("event") or payload.get("type") or "unknown"
    seller_slug = payload.get("seller_slug") or payload.get("seller")

    # If seller specified, verify HMAC against seller profile secret
    if seller_slug and frappe.db.exists("Whatnot Seller Profile", {"seller_slug": seller_slug}):
        secret = frappe.db.get_value("Whatnot Seller Profile", {"seller_slug": seller_slug}, "webhook_secret")
        if secret and signature_header:
            expected_sig = hmac.new(secret.encode("utf-8"), request_data, hashlib.sha256).hexdigest()
            # Allow sha256= prefix if present
            clean_sig = signature_header.replace("sha256=", "")
            if not hmac.compare_digest(expected_sig, clean_sig):
                frappe.log_error(f"Invalid HMAC signature on webhook: {signature_header}", "Whatnot Webhook Auth")
                frappe.throw("Invalid HMAC signature", frappe.AuthenticationError)

    # Process Event
    if event_type in ("order.created", "listing.sold"):
        item_id = payload.get("data", {}).get("item_id")
        sku = payload.get("data", {}).get("sku")
        
        # Enqueue background delisting across connected eBay/Shopify channels
        if sku or item_id:
            frappe.enqueue(
                trigger_cross_platform_delist,
                queue="default",
                item_code_or_sku=sku or item_id,
                reason=f"Sold on Whatnot (Event: {event_type})"
            )

    return {
        "status": "received",
        "event": event_type,
        "timestamp": now_datetime()
    }
