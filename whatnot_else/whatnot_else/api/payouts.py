import csv
import io
import frappe
from frappe.utils import flt, getdate, nowdate

@frappe.whitelist()
def import_stripe_payout_csv(seller_profile, csv_content=None, file_url=None):
    """
    Ingest Stripe/Whatnot payout statement CSV to create Whatnot Payout Batch records
    and reconcile against existing Whatnot Orders.
    """
    if not csv_content and file_url:
        _file = frappe.get_doc("File", {"file_url": file_url})
        csv_content = _file.get_content()

    if not csv_content:
        frappe.throw("CSV content or valid file URL is required.")

    if isinstance(csv_content, bytes):
        csv_content = csv_content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(csv_content))
    batches_created = 0
    orders_linked = 0

    for row in reader:
        payout_id = row.get("Payout ID") or row.get("Transfer ID") or row.get("Id") or row.get("Reference")
        date_str = row.get("Date") or row.get("Created") or row.get("Payout Date") or nowdate()
        gross = flt(row.get("Gross") or row.get("Total") or 0.0)
        fee = flt(row.get("Fee") or row.get("Commission") or (gross * 0.11))
        net = flt(row.get("Net") or (gross - fee))
        stripe_po = row.get("Stripe Payout ID") or payout_id
        bank_acc = row.get("Destination") or row.get("Bank Account") or ""

        if not payout_id:
            continue

        if frappe.db.exists("Whatnot Payout Batch", {"payout_id": payout_id}):
            batch = frappe.get_doc("Whatnot Payout Batch", {"payout_id": payout_id})
        else:
            batch = frappe.get_doc({
                "doctype": "Whatnot Payout Batch",
                "payout_id": payout_id,
                "seller_profile": seller_profile,
                "payout_date": getdate(date_str),
                "status": "Reconciled",
                "gross_amount": gross,
                "whatnot_fees": fee,
                "net_deposit_amount": net,
                "stripe_payout_id": stripe_po,
                "stripe_bank_account": bank_acc
            })
            batch.insert(ignore_permissions=True)
            batches_created += 1

        # Match any order ID referenced in the row
        order_ref = row.get("Order ID") or row.get("Whatnot Order")
        if order_ref and frappe.db.exists("Whatnot Order", {"whatnot_order_id": order_ref}):
            order = frappe.get_doc("Whatnot Order", {"whatnot_order_id": order_ref})
            batch.append("orders", {
                "whatnot_order": order.name,
                "whatnot_order_id": order.whatnot_order_id,
                "gross_amount": order.gross_amount,
                "fee_amount": order.whatnot_fee,
                "net_amount": order.net_payout
            })
            batch.save(ignore_permissions=True)
            orders_linked += 1

    return {
        "status": "success",
        "batches_created": batches_created,
        "orders_linked": orders_linked
    }

@frappe.whitelist()
def get_annual_1099k_summary(seller_profile, year=None):
    """
    Calculate annual 1099-K gross receipt figures and deductible platform expenses.
    """
    if not year:
        year = frappe.utils.now_datetime().year

    start_date = f"{year}-01-01 00:00:00"
    end_date = f"{year}-12-31 23:59:59"

    orders = frappe.db.sql("""
        SELECT 
            COUNT(name) as total_transactions,
            SUM(gross_amount) as gross_sales,
            SUM(whatnot_fee) as total_fees,
            SUM(shipping_fee) as total_shipping,
            SUM(net_payout) as total_net
        FROM `tabWhatnot Order`
        WHERE seller_profile = %s
          AND order_date BETWEEN %s AND %s
          AND docstatus < 2
    """, (seller_profile, start_date, end_date), as_dict=True)

    summary = orders[0] if orders else {}

    gross = flt(summary.get("gross_sales") or 0.0)
    fees = flt(summary.get("total_fees") or 0.0)
    shipping = flt(summary.get("total_shipping") or 0.0)
    net = flt(summary.get("total_net") or 0.0)

    # 1099-K threshold check (historical $20,000 / 200 items, or current $5,000 threshold)
    threshold = 5000.0
    qualifies_1099k = gross >= threshold

    return {
        "seller_profile": seller_profile,
        "tax_year": int(year),
        "total_transactions": summary.get("total_transactions") or 0,
        "gross_reportable_volume": round(gross, 2),
        "deductible_platform_fees": round(fees, 2),
        "deductible_shipping": round(shipping, 2),
        "net_received": round(net, 2),
        "1099k_issued": qualifies_1099k,
        "threshold_limit": threshold
    }
