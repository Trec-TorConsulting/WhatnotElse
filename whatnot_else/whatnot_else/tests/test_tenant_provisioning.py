import unittest
import os
import json
import re

RESERVED_SUBDOMAINS = frozenset({
    "www", "app", "api", "admin", "mail", "smtp", "imap", "ftp",
    "blog", "docs", "status", "staging", "dev", "test", "demo",
    "support", "help", "billing", "dashboard", "cdn", "assets",
    "internal", "ops", "cluster", "k8s", "registry",
})
SUBDOMAIN_REGEX = re.compile(r"^[a-z0-9]([a-z0-9\-]{1,61}[a-z0-9])?$")


def validate_subdomain(subdomain, existing_subdomains=None):
    if not subdomain:
        return False, "Subdomain is required."
    subdomain = subdomain.strip().lower()
    if len(subdomain) < 3 or len(subdomain) > 63:
        return False, "Subdomain must be between 3 and 63 characters."
    if not SUBDOMAIN_REGEX.match(subdomain):
        return False, "Subdomain must contain only lowercase alphanumeric characters and hyphens."
    if subdomain in RESERVED_SUBDOMAINS:
        return False, f"'{subdomain}' is a reserved subdomain."
    if existing_subdomains and subdomain in existing_subdomains:
        return False, f"'{subdomain}' is already taken."
    return True, subdomain


class MockTenant:
    def __init__(self, tenant_name, subdomain, owner_email, plan_doc=None):
        self.name = f"TENANT-{subdomain}"
        self.tenant_name = tenant_name
        self.subdomain = subdomain
        self.owner_email = owner_email
        self.status = "Pending"
        self.site_name = f"{subdomain}.whatnotelse.com"
        self.cluster_host = None
        self.provisioned_at = None
        self.suspended_at = None
        self.admin_notes = ""
        self.plan = plan_doc.name if plan_doc else None
        self.max_shows_per_month = getattr(plan_doc, "max_shows_per_month", 10)
        self.max_trays = getattr(plan_doc, "max_trays", 50)
        self.enable_multi_channel_sync = getattr(plan_doc, "enable_multi_channel_sync", 0)
        self.enable_ai_copilot = getattr(plan_doc, "enable_ai_copilot", 0)

    def mark_active(self, cluster_host=None):
        self.status = "Active"
        self.provisioned_at = "2026-09-09 13:00:00"
        if cluster_host:
            self.cluster_host = cluster_host

    def suspend(self, reason=None):
        self.status = "Suspended"
        self.suspended_at = "2026-09-09 14:00:00"
        if reason:
            self.admin_notes = f"{self.admin_notes}\n[Suspended] {reason}".strip()

    def cancel_tenant(self, reason=None):
        self.status = "Cancelled"
        if reason:
            self.admin_notes = f"{self.admin_notes}\n[Cancelled] {reason}".strip()


class MockPlan:
    def __init__(self, name, price_cents=4900, max_shows=20, max_trays=100, multi_channel=1, ai_copilot=1):
        self.name = name
        self.price_cents = price_cents
        self.max_shows_per_month = max_shows
        self.max_trays = max_trays
        self.enable_multi_channel_sync = multi_channel
        self.enable_ai_copilot = ai_copilot


class TestTenantProvisioning(unittest.TestCase):
    def test_subdomain_validation(self):
        # Valid cases
        valid, _ = validate_subdomain("ripnpak")
        self.assertTrue(valid)

        valid, _ = validate_subdomain("elite-cards-2026")
        self.assertTrue(valid)

        # Reserved
        valid, msg = validate_subdomain("admin")
        self.assertFalse(valid)
        self.assertIn("reserved", msg)

        valid, msg = validate_subdomain("api")
        self.assertFalse(valid)

        # Invalid formats
        valid, msg = validate_subdomain("-invalid")
        self.assertFalse(valid)

        valid, msg = validate_subdomain("ab") # < 3 chars
        self.assertFalse(valid)

        valid, _ = validate_subdomain("VALID-CAPS")
        self.assertTrue(valid) # auto-lowercased to valid-caps

        # Underscores are not permitted in DNS hostnames
        valid, _ = validate_subdomain("invalid_caps")
        self.assertFalse(valid)

        # Collision with existing
        existing = {"pokeking", "vintagebreaks"}
        valid, msg = validate_subdomain("pokeking", existing_subdomains=existing)
        self.assertFalse(valid)
        self.assertIn("already taken", msg)

    def test_tenant_lifecycle(self):
        pro_plan = MockPlan("Pro Streamer", price_cents=12900, max_shows=50, max_trays=150, multi_channel=1, ai_copilot=1)
        tenant = MockTenant("Poke Breakers LLC", "pokebreakers", "owner@pokebreakers.com", plan_doc=pro_plan)

        self.assertEqual(tenant.status, "Pending")
        self.assertEqual(tenant.site_name, "pokebreakers.whatnotelse.com")
        self.assertEqual(tenant.max_shows_per_month, 50)
        self.assertEqual(tenant.enable_ai_copilot, 1)

        # Activate
        tenant.mark_active(cluster_host="k3s-gateway.whatnotelse.com")
        self.assertEqual(tenant.status, "Active")
        self.assertEqual(tenant.cluster_host, "k3s-gateway.whatnotelse.com")

        # Suspend
        tenant.suspend(reason="Failed Stripe payment")
        self.assertEqual(tenant.status, "Suspended")
        self.assertIn("Failed Stripe payment", tenant.admin_notes)

        # Cancel
        tenant.cancel_tenant(reason="Requested account closure")
        self.assertEqual(tenant.status, "Cancelled")

    def test_schema_validity(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Test whatnot_tenant.json
        tenant_json = os.path.join(base_dir, "whatnot_else", "doctype", "whatnot_tenant", "whatnot_tenant.json")
        with open(tenant_json) as f:
            data = json.load(f)
            self.assertEqual(data.get("name"), "Whatnot Tenant")
            fields = {field["fieldname"] for field in data["fields"]}
            self.assertIn("subdomain", fields)
            self.assertIn("owner_email", fields)
            self.assertIn("plan", fields)
            self.assertIn("site_name", fields)

        # Test whatnot_subscription_plan.json
        plan_json = os.path.join(base_dir, "whatnot_else", "doctype", "whatnot_subscription_plan", "whatnot_subscription_plan.json")
        with open(plan_json) as f:
            data = json.load(f)
            self.assertEqual(data.get("name"), "Whatnot Subscription Plan")
            fields = {field["fieldname"] for field in data["fields"]}
            self.assertIn("price_cents", fields)
            self.assertIn("stripe_price_id", fields)
            self.assertIn("enable_ai_copilot", fields)


if __name__ == "__main__":
    unittest.main()
