import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class WhatnotTenantSubscription(Document):
    """
    Tracks active Stripe or trial subscription mapped to a WhatnotTenant.
    """

    def validate(self):
        self.sync_with_tenant()

    def on_update(self):
        self.sync_with_tenant()

    def sync_with_tenant(self):
        if not self.tenant:
            return

        tenant_doc = frappe.get_doc("Whatnot Tenant", self.tenant)
        updated = False

        if tenant_doc.subscription != self.name:
            tenant_doc.subscription = self.name
            updated = True

        if self.plan and tenant_doc.plan != self.plan:
            tenant_doc.plan = self.plan
            tenant_doc.sync_plan_limits()
            updated = True

        if self.stripe_customer_id and tenant_doc.stripe_customer_id != self.stripe_customer_id:
            tenant_doc.stripe_customer_id = self.stripe_customer_id
            updated = True

        # Check tenant status based on subscription state
        if self.status in ("Active", "Trialing"):
            if tenant_doc.status == "Suspended":
                tenant_doc.status = "Active"
                tenant_doc.suspended_at = None
                updated = True
        elif self.status in ("Past Due", "Unpaid"):
            if tenant_doc.status == "Active":
                tenant_doc.status = "Suspended"
                tenant_doc.suspended_at = now_datetime()
                tenant_doc.admin_notes = f"{tenant_doc.admin_notes or ''}\n[Auto-Suspended] Subscription status: {self.status}".strip()
                updated = True
        elif self.status == "Canceled":
            if tenant_doc.status != "Cancelled":
                tenant_doc.status = "Cancelled"
                tenant_doc.admin_notes = f"{tenant_doc.admin_notes or ''}\n[Auto-Cancelled] Subscription canceled".strip()
                updated = True

        if updated:
            tenant_doc.save(ignore_permissions=True)
