import re
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


# Reserved subdomains that cannot be claimed by tenants
RESERVED_SUBDOMAINS = frozenset({
    "www", "app", "api", "admin", "mail", "smtp", "imap", "ftp",
    "blog", "docs", "status", "staging", "dev", "test", "demo",
    "support", "help", "billing", "dashboard", "cdn", "assets",
    "internal", "ops", "cluster", "k8s", "registry",
})

SUBDOMAIN_REGEX = re.compile(r"^[a-z0-9]([a-z0-9\-]{1,61}[a-z0-9])?$")


class WhatnotTenant(Document):
    """
    Represents a single SaaS tenant on the WhatnotElse platform.
    Each tenant gets a dedicated Frappe site at <subdomain>.whatnotelse.com.
    """

    def validate(self):
        self.validate_subdomain()
        self.sync_plan_limits()

    # ── Subdomain Rules ─────────────────────────────────────────────

    def validate_subdomain(self):
        """Enforce DNS-safe, unique, non-reserved subdomain."""
        subdomain = (self.subdomain or "").strip().lower()
        if not subdomain:
            frappe.throw("Subdomain is required.")

        if subdomain in RESERVED_SUBDOMAINS:
            frappe.throw(f"'{subdomain}' is a reserved subdomain and cannot be used.")

        if not SUBDOMAIN_REGEX.match(subdomain):
            frappe.throw(
                "Subdomain must be 3-63 characters, lowercase alphanumeric and hyphens only, "
                "and cannot start or end with a hyphen."
            )

        self.subdomain = subdomain
        self.site_name = f"{subdomain}.whatnotelse.com"

    # ── Plan Feature Gating ─────────────────────────────────────────

    def sync_plan_limits(self):
        """Pull feature limits from the linked Subscription Plan."""
        if not self.plan:
            return

        plan = frappe.get_cached_doc("Whatnot Subscription Plan", self.plan)
        self.max_shows_per_month = plan.max_shows_per_month or 10
        self.max_trays = plan.max_trays or 50
        self.enable_multi_channel_sync = plan.enable_multi_channel_sync
        self.enable_ai_copilot = plan.enable_ai_copilot

    # ── Lifecycle Helpers ───────────────────────────────────────────

    def mark_active(self, cluster_host=None):
        """Transition tenant to Active after successful provisioning."""
        self.status = "Active"
        self.provisioned_at = now_datetime()
        if cluster_host:
            self.cluster_host = cluster_host
        self.save(ignore_permissions=True)

    def suspend(self, reason=None):
        """Suspend tenant (e.g. payment failure)."""
        self.status = "Suspended"
        self.suspended_at = now_datetime()
        if reason:
            self.admin_notes = f"{self.admin_notes or ''}\n[Suspended] {reason}".strip()
        self.save(ignore_permissions=True)

    def cancel_tenant(self, reason=None):
        """Permanently cancel a tenant."""
        self.status = "Cancelled"
        if reason:
            self.admin_notes = f"{self.admin_notes or ''}\n[Cancelled] {reason}".strip()
        self.save(ignore_permissions=True)
