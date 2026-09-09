import json
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class WhatnotStripeEvent(Document):
    """
    Audit log and idempotency tracking for incoming Stripe Webhook events.
    """

    def mark_processed(self, tenant=None):
        self.status = "Processed"
        self.processed_at = now_datetime()
        if tenant:
            self.tenant = tenant
        self.save(ignore_permissions=True)

    def mark_failed(self, error_message):
        self.status = "Failed"
        self.error_message = str(error_message)
        self.processed_at = now_datetime()
        self.save(ignore_permissions=True)

    def mark_ignored(self, reason=None):
        self.status = "Ignored"
        if reason:
            self.error_message = reason
        self.processed_at = now_datetime()
        self.save(ignore_permissions=True)

    def get_payload_dict(self):
        if not self.payload:
            return {}
        try:
            return json.loads(self.payload)
        except Exception:
            return {}
