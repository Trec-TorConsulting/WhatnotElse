import re
import frappe
from frappe.model.document import Document


class WhatnotSubscriptionPlan(Document):
    """
    Defines a SaaS subscription tier with pricing, Stripe bindings,
    and feature limit gates.
    """

    def validate(self):
        self.generate_slug()
        self.validate_stripe_ids()

    def generate_slug(self):
        """Auto-generate a URL-safe slug from plan_name."""
        if self.plan_name:
            slug = re.sub(r"[^a-z0-9]+", "-", self.plan_name.lower()).strip("-")
            self.plan_slug = slug

    def validate_stripe_ids(self):
        """Warn if Stripe IDs look malformed (basic prefix check)."""
        if self.stripe_price_id and not self.stripe_price_id.startswith("price_"):
            frappe.msgprint(
                "Stripe Price ID typically starts with 'price_'. Please verify.",
                indicator="orange",
                alert=True,
            )
        if self.stripe_product_id and not self.stripe_product_id.startswith("prod_"):
            frappe.msgprint(
                "Stripe Product ID typically starts with 'prod_'. Please verify.",
                indicator="orange",
                alert=True,
            )

    def get_monthly_price_usd(self):
        """Return price in dollars for display."""
        return round((self.price_cents or 0) / 100.0, 2)
