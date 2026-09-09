import os
import frappe
import requests

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

@frappe.whitelist()
def send_sms_alert(to_phone_number, message_body):
    """
    Send an SMS alert to seller or buyer via Twilio REST API.
    """
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER):
        # Fall back to local Frappe system notification if Twilio not configured
        frappe.log_error(f"SMS Mock Dispatch to {to_phone_number}: {message_body}", "Whatnot SMS Notification")
        return {
            "status": "mock_sent",
            "message": "Twilio credentials not configured; logged to system notification log."
        }

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    data = {
        "To": to_phone_number,
        "From": TWILIO_PHONE_NUMBER,
        "Body": message_body
    }

    try:
        response = requests.post(url, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=10)
        if response.status_code in (200, 201):
            return {"status": "success", "sid": response.json().get("sid")}
        else:
            frappe.log_error(f"Twilio SMS Error: {response.text}", "Whatnot SMS Notification")
            return {"status": "error", "message": response.text}
    except Exception as e:
        frappe.log_error(f"Twilio SMS Exception: {str(e)}", "Whatnot SMS Notification")
        return {"status": "error", "message": str(e)}

def notify_high_value_order(order_doc):
    """
    Trigger notification when a high-value or VIP order is created.
    """
    if (order_doc.gross_amount or 0.0) >= 250.0:
        seller_email = frappe.db.get_value("Whatnot Seller Profile", order_doc.seller_profile, "email")
        subject = f"🚨 High Value Whatnot Order: ${order_doc.gross_amount} from @{order_doc.buyer_username}"
        content = f"<p>Congratulations! Order <strong>{order_doc.whatnot_order_id}</strong> for <strong>${order_doc.gross_amount}</strong> has been logged from @{order_doc.buyer_username}.</p>"
        
        if seller_email:
            frappe.sendmail(
                recipients=[seller_email],
                subject=subject,
                message=content,
                delayed=False
            )
