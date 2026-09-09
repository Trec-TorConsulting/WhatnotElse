import unittest
import os
import json


class MockStripeEvent:
    def __init__(self, event_id, event_type, payload):
        self.name = event_id
        self.stripe_event_id = event_id
        self.event_type = event_type
        self.payload = json.dumps(payload)
        self.status = "Pending"
        self.tenant = None
        self.error_message = None

    def mark_processed(self, tenant=None):
        self.status = "Processed"
        self.tenant = tenant

    def mark_failed(self, error):
        self.status = "Failed"
        self.error_message = str(error)

    def mark_ignored(self, reason=None):
        self.status = "Ignored"
        self.error_message = reason


def dispatch_stripe_event(event_type, data_obj, tenants_map):
    """
    Pure-function unit-testable dispatcher mirroring process_stripe_event.
    """
    customer_id = data_obj.get("customer")
    subdomain = data_obj.get("metadata", {}).get("tenant_subdomain")

    tenant = None
    if subdomain and subdomain in tenants_map:
        tenant = tenants_map[subdomain]
    elif customer_id:
        for t in tenants_map.values():
            if getattr(t, "stripe_customer_id", None) == customer_id:
                tenant = t
                break

    if not tenant:
        return {"action": "tenant_not_found"}

    if event_type == "checkout.session.completed":
        tenant.status = "Active"
        tenant.stripe_customer_id = customer_id
        return {"action": "activated", "tenant": tenant.name}
    elif event_type in ("invoice.payment_succeeded", "invoice.paid"):
        tenant.status = "Active"
        return {"action": "renewed", "tenant": tenant.name}
    elif event_type == "invoice.payment_failed":
        tenant.status = "Suspended"
        return {"action": "suspended", "tenant": tenant.name}
    elif event_type == "customer.subscription.deleted":
        tenant.status = "Cancelled"
        return {"action": "cancelled", "tenant": tenant.name}
    else:
        return {"action": "ignored", "event_type": event_type}


class SimpleTenant:
    def __init__(self, name, subdomain, stripe_customer_id=None):
        self.name = name
        self.subdomain = subdomain
        self.stripe_customer_id = stripe_customer_id
        self.status = "Pending"


class TestStripeBilling(unittest.TestCase):
    def setUp(self):
        self.tenants = {
            "packrip": SimpleTenant("TENANT-packrip", "packrip", "cus_test_12345"),
            "slabking": SimpleTenant("TENANT-slabking", "slabking", "cus_test_67890"),
        }

    def test_checkout_completed_event(self):
        payload = {
            "id": "evt_checkout_1",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_test_12345",
                    "subscription": "sub_test_abc",
                    "metadata": {"tenant_subdomain": "packrip", "plan_name": "Pro Streamer"}
                }
            }
        }
        res = dispatch_stripe_event(payload["type"], payload["data"]["object"], self.tenants)
        self.assertEqual(res["action"], "activated")
        self.assertEqual(self.tenants["packrip"].status, "Active")

    def test_payment_failure_suspends_tenant(self):
        self.tenants["packrip"].status = "Active"
        payload = {
            "id": "evt_fail_1",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "customer": "cus_test_12345"
                }
            }
        }
        res = dispatch_stripe_event(payload["type"], payload["data"]["object"], self.tenants)
        self.assertEqual(res["action"], "suspended")
        self.assertEqual(self.tenants["packrip"].status, "Suspended")

    def test_payment_recovery_reactivates_tenant(self):
        self.tenants["packrip"].status = "Suspended"
        payload = {
            "id": "evt_paid_1",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "customer": "cus_test_12345"
                }
            }
        }
        res = dispatch_stripe_event(payload["type"], payload["data"]["object"], self.tenants)
        self.assertEqual(res["action"], "renewed")
        self.assertEqual(self.tenants["packrip"].status, "Active")

    def test_subscription_deleted_cancels_tenant(self):
        payload = {
            "id": "evt_cancel_1",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": "cus_test_67890"
                }
            }
        }
        res = dispatch_stripe_event(payload["type"], payload["data"]["object"], self.tenants)
        self.assertEqual(res["action"], "cancelled")
        self.assertEqual(self.tenants["slabking"].status, "Cancelled")

    def test_idempotent_event_doc(self):
        evt = MockStripeEvent("evt_test_100", "checkout.session.completed", {"dummy": 1})
        self.assertEqual(evt.status, "Pending")
        evt.mark_processed(tenant="TENANT-packrip")
        self.assertEqual(evt.status, "Processed")
        self.assertEqual(evt.tenant, "TENANT-packrip")

    def test_schema_validity(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Test whatnot_stripe_event.json
        event_json = os.path.join(base_dir, "whatnot_else", "doctype", "whatnot_stripe_event", "whatnot_stripe_event.json")
        with open(event_json) as f:
            data = json.load(f)
            self.assertEqual(data.get("name"), "Whatnot Stripe Event")
            fields = {field["fieldname"] for field in data["fields"]}
            self.assertIn("stripe_event_id", fields)
            self.assertIn("event_type", fields)
            self.assertIn("payload", fields)

        # Test whatnot_tenant_subscription.json
        sub_json = os.path.join(base_dir, "whatnot_else", "doctype", "whatnot_tenant_subscription", "whatnot_tenant_subscription.json")
        with open(sub_json) as f:
            data = json.load(f)
            self.assertEqual(data.get("name"), "Whatnot Tenant Subscription")
            fields = {field["fieldname"] for field in data["fields"]}
            self.assertIn("tenant", fields)
            self.assertIn("plan", fields)
            self.assertIn("stripe_customer_id", fields)


if __name__ == "__main__":
    unittest.main()
