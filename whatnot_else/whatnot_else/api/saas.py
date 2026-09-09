import re
import frappe
from frappe.utils import now_datetime, add_days

RESERVED_SUBDOMAINS = frozenset({
    "www", "app", "api", "admin", "mail", "smtp", "imap", "ftp",
    "blog", "docs", "status", "staging", "dev", "test", "demo",
    "support", "help", "billing", "dashboard", "cdn", "assets",
    "internal", "ops", "cluster", "k8s", "registry",
})

SUBDOMAIN_REGEX = re.compile(r"^[a-z0-9]([a-z0-9\-]{1,61}[a-z0-9])?$")


@frappe.whitelist(allow_guest=True)
def check_subdomain_available(subdomain):
    """
    Checks whether a desired subdomain can be claimed.
    Validates DNS compatibility, reserved names, and active tenants.
    """
    if not subdomain:
        return {"available": False, "reason": "Subdomain is required."}

    subdomain = subdomain.strip().lower()

    if len(subdomain) < 3 or len(subdomain) > 63:
        return {"available": False, "reason": "Subdomain must be between 3 and 63 characters."}

    if not SUBDOMAIN_REGEX.match(subdomain):
        return {
            "available": False,
            "reason": "Subdomain must contain only lowercase letters, numbers, and hyphens (not leading/trailing)."
        }

    if subdomain in RESERVED_SUBDOMAINS:
        return {"available": False, "reason": f"'{subdomain}' is a reserved system domain."}

    existing = frappe.db.exists("Whatnot Tenant", {"subdomain": subdomain})
    if existing:
        return {"available": False, "reason": f"'{subdomain}.whatnotelse.com' is already taken."}

    return {
        "available": True,
        "subdomain": subdomain,
        "full_domain": f"{subdomain}.whatnotelse.com"
    }


@frappe.whitelist(allow_guest=True)
def get_public_plans():
    """
    Returns active subscription plans for the public onboarding and marketing page.
    """
    plans = frappe.get_all(
        "Whatnot Subscription Plan",
        filters={"is_active": 1},
        fields=[
            "name", "plan_name", "plan_slug", "price_cents", "billing_interval",
            "max_shows_per_month", "max_trays", "max_items",
            "enable_multi_channel_sync", "enable_ai_copilot", "enable_obs_overlay",
            "description", "features_summary", "is_default"
        ],
        order_by="price_cents asc"
    )

    for p in plans:
        p["monthly_price_usd"] = round((p.price_cents or 0) / 100.0, 2)

    return {"plans": plans}


@frappe.whitelist(allow_guest=True)
def provision_tenant(tenant_name, subdomain, owner_email, plan_name=None):
    """
    Self-service tenant onboarding endpoint.
    Validates subdomain, allocates tenant record, provisions site metadata,
    and initializes a 14-day trial subscription.
    """
    subdomain_check = check_subdomain_available(subdomain)
    if not subdomain_check["available"]:
        frappe.throw(subdomain_check["reason"], frappe.ValidationError)

    subdomain = subdomain_check["subdomain"]

    # Select plan
    if not plan_name:
        default_plan = frappe.db.get_value("Whatnot Subscription Plan", {"is_default": 1, "is_active": 1}, "name")
        if not default_plan:
            default_plan = frappe.db.get_value("Whatnot Subscription Plan", {"is_active": 1}, "name", order_by="price_cents asc")
        plan_name = default_plan

    if not plan_name or not frappe.db.exists("Whatnot Subscription Plan", plan_name):
        frappe.throw("Invalid or missing subscription plan.", frappe.ValidationError)

    # Create Whatnot Tenant
    tenant = frappe.new_doc("Whatnot Tenant")
    tenant.tenant_name = tenant_name
    tenant.subdomain = subdomain
    tenant.owner_email = owner_email
    tenant.plan = plan_name
    tenant.status = "Provisioning"
    tenant.site_name = f"{subdomain}.whatnotelse.com"
    tenant.cluster_host = "k3s-gateway.whatnotelse.com"
    tenant.insert(ignore_permissions=True)

    # Create Tenant Subscription (14-day trial)
    trial_start = now_datetime()
    trial_end = add_days(trial_start, 14)

    sub = frappe.new_doc("Whatnot Tenant Subscription")
    sub.tenant = tenant.name
    sub.plan = plan_name
    sub.status = "Trialing"
    sub.is_trial = 1
    sub.trial_start = trial_start
    sub.trial_end = trial_end
    sub.current_period_start = trial_start
    sub.current_period_end = trial_end
    sub.insert(ignore_permissions=True)

    # Update Tenant to Active with linked subscription
    tenant.subscription = sub.name
    tenant.mark_active(cluster_host=tenant.cluster_host)
    frappe.db.commit()

    return {
        "success": True,
        "message": f"Tenant {subdomain}.whatnotelse.com provisioned successfully.",
        "tenant_id": tenant.name,
        "subdomain": subdomain,
        "site_url": f"https://{subdomain}.whatnotelse.com",
        "plan": plan_name,
        "trial_end": trial_end
    }


@frappe.whitelist(allow_guest=False)
def suspend_tenant(subdomain, reason=None):
    """
    Administrative suspension of a tenant.
    """
    tenant_name = frappe.db.get_value("Whatnot Tenant", {"subdomain": subdomain}, "name")
    if not tenant_name:
        frappe.throw(f"Tenant with subdomain '{subdomain}' not found.")

    tenant = frappe.get_doc("Whatnot Tenant", tenant_name)
    tenant.suspend(reason=reason)
    frappe.db.commit()

    return {
        "success": True,
        "status": tenant.status,
        "subdomain": subdomain,
        "suspended_at": tenant.suspended_at
    }


@frappe.whitelist(allow_guest=False)
def reactivate_tenant(subdomain):
    """
    Administrative reactivation of a suspended tenant.
    """
    tenant_name = frappe.db.get_value("Whatnot Tenant", {"subdomain": subdomain}, "name")
    if not tenant_name:
        frappe.throw(f"Tenant with subdomain '{subdomain}' not found.")

    tenant = frappe.get_doc("Whatnot Tenant", tenant_name)
    tenant.mark_active()
    frappe.db.commit()

    return {
        "success": True,
        "status": tenant.status,
        "subdomain": subdomain
    }
