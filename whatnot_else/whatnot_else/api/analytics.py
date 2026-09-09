import frappe
from frappe.utils import flt, now_datetime, add_days

@frappe.whitelist()
def get_dashboard_analytics(seller_profile=None):
    """
    Aggregate high-level KPIs and operational metrics for the Whatnot Seller Dashboard.
    """
    conditions = ""
    values = []
    if seller_profile:
        conditions = " AND seller_profile = %s"
        values.append(seller_profile)

    # 30-Day Orders Metric
    start_30 = add_days(now_datetime(), -30)
    order_stats = frappe.db.sql(f"""
        SELECT 
            COUNT(name) as total_orders,
            SUM(gross_amount) as gross_sales,
            SUM(whatnot_fee) as platform_fees,
            SUM(net_payout) as net_sales
        FROM `tabWhatnot Order`
        WHERE order_date >= %s {conditions}
          AND docstatus < 2
    """, [start_30] + values, as_dict=True)

    orders = order_stats[0] if order_stats else {}

    # Show Performance Metrics
    show_stats = frappe.db.sql(f"""
        SELECT 
            COUNT(name) as total_shows,
            SUM(total_items_planned) as total_planned,
            SUM(total_items_sold) as total_sold,
            SUM(net_profit) as total_show_profit
        FROM `tabWhatnot Show`
        WHERE 1=1 {conditions}
    """, values, as_dict=True)

    shows = show_stats[0] if show_stats else {}
    planned = shows.get("total_planned") or 0
    sold = shows.get("total_sold") or 0
    avg_sell_through = round((sold / planned * 100), 1) if planned > 0 else 0.0

    # Active VIP Buyers
    vip_count = frappe.db.sql(f"""
        SELECT COUNT(name) as count
        FROM `tabWhatnot Buyer`
        WHERE vip_tier != 'Standard' {conditions}
    """, values, as_dict=True)[0].get("count") or 0

    # Upcoming Shows
    upcoming_shows = frappe.db.sql(f"""
        SELECT name, show_title, status, scheduled_start_time, total_items_planned
        FROM `tabWhatnot Show`
        WHERE status IN ('Draft', 'Scheduled', 'Live') {conditions}
        ORDER BY scheduled_start_time ASC
        LIMIT 5
    """, values, as_dict=True)

    # Top Categories by Item Count
    category_breakdown = frappe.db.sql(f"""
        SELECT category, COUNT(name) as count
        FROM `tabWhatnot Item`
        WHERE 1=1 {conditions}
        GROUP BY category
        ORDER BY count DESC
        LIMIT 6
    """, values, as_dict=True)

    return {
        "kpis": {
            "gross_revenue_30d": round(flt(orders.get("gross_sales") or 0.0), 2),
            "net_revenue_30d": round(flt(orders.get("net_sales") or 0.0), 2),
            "total_orders_30d": orders.get("total_orders") or 0,
            "avg_sell_through": avg_sell_through,
            "vip_buyers_count": vip_count,
            "total_shows_hosted": shows.get("total_shows") or 0
        },
        "upcoming_shows": upcoming_shows,
        "categories": category_breakdown
    }
