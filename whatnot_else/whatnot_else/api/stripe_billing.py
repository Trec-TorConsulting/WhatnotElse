import hmac
import hashlib
import json
import os
import frappe
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=False)
def create_checkout_session(subdomain, plan_name, success_url=None, cancel_url=None):
    """
    Creates a Stripe Checkout Session for a tenant to upgrade or start paid subscription.
    Returns session URL and ID.
    """
    tenant_name = frappe.db.get_value("Whatnot Tenant", {"subdomain": subdomain}, "name")
    if not tenant_name:
        frappe.throw(f"Tenant '{subdomain}' does not exist.")

    tenant = frappe.get_doc("Whatnot Tenant", tenant_name)
    plan = frappe.get_doc("Whatnot Subscription Plan", plan_name)

    if not plan.stripe_price_id:
        frappe.throw(f"Plan '{plan_name}' has no Stripe Price ID configured.")

    stripe_api_key = os.environ.get("STRIPE_SECRET_KEY") or frappe.conf.get("stripe_secret_key")
    
    # Mock / Sandbox payload if running without external network or Stripe key
    checkout_data = {
        "tenant": tenant.name,
        "subdomain": subdomain,
        "plan": plan.name,
        "stripe_price_id": plan.stripe_price_id,
        "mode": "subscription",
        "customer_email": tenant.owner_email,
        "success_url": success_url or f"https://{subdomain}.whatnotelse.com/app/billing?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": cancel_url or f"https://{subdomain}.whatnotelse.com/app/billing?cancelled=1",
    }

    if not stripe_api_key:
        mock_session_id = f"cs_test_mock_{tenant.subdomain}_{frappe.generate_hash(length=12)}"
        return {
            "success": True,
            "session_id": mock_session_id,
            "url": f"https://checkout.stripe.com/c/pay/{mock_session_id}?mock=1",
            "mock": True
        }

    try:
        import stripe
        stripe.api_key = stripe_api_key

        session_params = {
            "payment_method_types": ["card"],
            "line_items": [{"price": plan.stripe_price_id, "quantity": 1}],
            "mode": "subscription",
            "success_url": checkout_data["success_url"],
            "cancel_url": checkout_data["cancel_url"],
            "client_reference_id": tenant.name,
            "metadata": {"tenant_subdomain": subdomain, "plan_name": plan_name}
        }
        if tenant.stripe_customer_id:
            session_params["customer"] = tenant.stripe_customer_id
        else:
            session_params["customer_email"] = tenant.owner_email

        session = stripe.checkout.Session.create(**session_params)
        return {
            "success": True,
            "session_id": session.id,
            "url": session.url,
            "mock": False
        }
    except Exception as e:
        frappe.log_error(f"Failed to create Stripe Checkout session: {str(e)}", "Stripe Billing")
        frappe.throw(f"Stripe error: {str(e)}")


@frappe.whitelist(allow_guest=True)
def handle_stripe_webhook():
    """
    Idempotent Stripe Webhook endpoint.
    Verifies signature, logs event in WhatnotStripeEvent, and processes event logic.
    """
    request_data = frappe.request.get_data()
    sig_header = frappe.get_request_header("Stripe-Signature")

    if not request_data:
        frappe.throw("Empty webhook payload", frappe.PermissionError)

    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET") or frappe.conf.get("stripe_webhook_secret")

    try:
        payload = json.loads(request_data)
    except Exception:
        frappe.throw("Invalid JSON payload", frappe.ValidationError)

    event_id = payload.get("id") or f"evt_mock_{frappe.generate_hash(length=16)}"
    event_type = payload.get("type", "unknown")

    # Verify signature if secret configured and stripe lib available
    if webhook_secret and sig_header:
        try:
            import stripe
            stripe.Webhook.construct_event(request_data, sig_header, webhook_secret)
        except Exception as e:
            frappe.log_error(f"Invalid Stripe webhook signature: {str(e)}", "Stripe Webhook Auth")
            frappe.throw(f"Webhook signature verification failed: {str(e)}", frappe.AuthenticationError)

    # Idempotency check
    if frappe.db.exists("Whatnot Stripe Event", {"stripe_event_id": event_id}):
        existing = frappe.get_doc("Whatnot Stripe Event", event_id)
        return {"status": "already_processed", "event_id": event_id, "state": existing.status}

    event_doc = frappe.new_doc("Whatnot Stripe Event")
    event_doc.stripe_event_id = event_id
    event_doc.event_type = event_type
    event_doc.received_at = now_datetime()
    event_doc.payload = json.dumps(payload)
    event_doc.status = "Pending"
    event_doc.insert(ignore_permissions=True)

    try:
        result = process_stripe_event(event_type, payload.get("data", {}).get("object", {}))
        tenant_name = result.get("tenant")
        event_doc.mark_processed(tenant=tenant_name)
        frappe.db.commit()
        return {"status": "success", "event_id": event_id, "processed": result}
    except Exception as e:
        frappe.db.rollback()
        event_doc.mark_failed(str(e))
        frappe.db.commit()
        frappe.log_error(f"Error processing Stripe webhook {event_id}: {str(e)}", "Stripe Billing")
        return {"status": "error", "event_id": event_id, "message": str(e)}


def process_stripe_event(event_type, obj):
    """
    Dispatches Stripe event object to the corresponding lifecycle action.
    """
    if event_type == "checkout.session.completed":
        return _handle_checkout_completed(obj)
    elif event_type in ("invoice.payment_succeeded", "invoice.paid"):
        return _handle_invoice_paid(obj)
    elif event_type == "invoice.payment_failed":
        return _handle_payment_failed(obj)
    elif event_type == "customer.subscription.deleted":
        return _handle_subscription_deleted(obj)
    elif event_type == "customer.subscription.updated":
        return _handle_subscription_updated(obj)
    else:
        return {"action": "ignored", "event_type": event_type}


def _find_tenant(customer_id, client_reference_id=None, metadata=None):
    """Locates a Whatnot Tenant by ID, subdomain, or Stripe Customer ID."""
    if client_reference_id and frappe.db.exists("Whatnot Tenant", client_reference_id):
        return client_reference_id

    subdomain = (metadata or {}).get("tenant_subdomain")
    if subdomain:
        tname = frappe.db.get_value("Whatnot Tenant", {"subdomain": subdomain}, "name")
        if tname:
            return tname

    if customer_id:
        tname = frappe.db.get_value("Whatnot Tenant", {"stripe_customer_id": customer_id}, "name")
        if tname:
            return tname

    return None


def _handle_checkout_completed(obj):
    customer_id = obj.get("customer")
    sub_id = obj.get("subscription")
    metadata = obj.get("metadata", {})
    client_ref = obj.get("client_reference_id")

    tenant_name = _find_tenant(customer_id, client_ref, metadata)
    if not tenant_name:
        return {"action": "tenant_not_found"}

    tenant = frappe.get_doc("Whatnot Tenant", tenant_name)
    if customer_id:
        tenant.stripe_customer_id = customer_id

    plan_name = metadata.get("plan_name")
    if plan_name and frappe.db.exists("Whatnot Subscription Plan", plan_name):
        tenant.plan = plan_name
        tenant.sync_plan_limits()

    tenant.status = "Active"
    tenant.suspended_at = None
    tenant.save(ignore_permissions=True)

    # Sync or create Tenant Subscription
    if tenant.subscription:
        sub = frappe.get_doc("Whatnot Tenant Subscription", tenant.subscription)
    else:
        sub = frappe.new_doc("Whatnot Tenant Subscription")
        sub.tenant = tenant.name
        sub.plan = tenant.plan

    sub.status = "Active"
    sub.is_trial = 0
    sub.stripe_customer_id = customer_id
    sub.stripe_subscription_id = sub_id
    sub.save(ignore_permissions=True)

    tenant.subscription = sub.name
    tenant.save(ignore_permissions=True)

    return {"action": "activated", "tenant": tenant.name, "subscription": sub.name}


def _handle_invoice_paid(obj):
    customer_id = obj.get("customer")
    tenant_name = _find_tenant(customer_id)
    if not tenant_name:
        return {"action": "tenant_not_found"}

    tenant = frappe.get_doc("Whatnot Tenant", tenant_name)
    tenant.status = "Active"
    tenant.suspended_at = None
    tenant.save(ignore_permissions=True)

    if tenant.subscription:
        sub = frappe.get_doc("Whatnot Tenant Subscription", tenant.subscription)
        sub.status = "Active"
        sub.save(ignore_permissions=True)

    return {"action": "renewed", "tenant": tenant.name}


def _handle_payment_failed(obj):
    customer_id = obj.get("customer")
    tenant_name = _find_tenant(customer_id)
    if not tenant_name:
        return {"action": "tenant_not_found"}

    tenant = frappe.get_doc("Whatnot Tenant", tenant_name)
    tenant.suspend(reason="Stripe invoice payment failed.")

    if tenant.subscription:
        sub = frappe.get_doc("Whatnot Tenant Subscription", tenant.subscription)
        sub.status = "Past Due"
        sub.save(ignore_permissions=True)

    return {"action": "suspended", "tenant": tenant.name}


def _handle_subscription_deleted(obj):
    customer_id = obj.get("customer")
    tenant_name = _find_tenant(customer_id)
    if not tenant_name:
        return {"action": "tenant_not_found"}

    tenant = frappe.get_doc("Whatnot Tenant", tenant_name)
    tenant.cancel_tenant(reason="Stripe subscription deleted/cancelled.")

    if tenant.subscription:
        sub = frappe.get_doc("Whatnot Tenant Subscription", tenant.subscription)
        sub.status = "Canceled"
        sub.canceled_at = now_datetime()
        sub.save(ignore_permissions=True)

    return {"action": "cancelled", "tenant": tenant.name}


def _handle_subscription_updated(obj):
    customer_id = obj.get("customer")
    status = obj.get("status")
    tenant_name = _find_tenant(customer_id)
    if not tenant_name:
        return {"action": "tenant_not_found"}

    tenant = frappe.get_doc("Whatnot Tenant", tenant_name)
    if tenant.subscription:
        sub = frappe.get_doc("Whatnot Tenant Subscription", tenant.subscription)
        if status in ("active", "trialing"):
            sub.status = "Active" if status == "active" else "Trialing"
            tenant.status = "Active"
        elif status in ("past_due", "unpaid"):
            sub.status = "Past Due"
            tenant.status = "Suspended"
        elif status in ("canceled", "incomplete_expired"):
            sub.status = "Canceled"
            tenant.status = "Cancelled"
        sub.save(ignore_permissions=True)
        tenant.save(ignore_permissions=True)

    return {"action": "status_updated", "tenant": tenant.name, "status": status}
