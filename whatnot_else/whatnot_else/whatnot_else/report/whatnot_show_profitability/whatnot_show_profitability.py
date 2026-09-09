import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    report_summary = get_report_summary(data)
    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {"label": "Show ID", "fieldname": "name", "fieldtype": "Link", "options": "Whatnot Show", "width": 140},
        {"label": "Show Title", "fieldname": "show_title", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 130},
        {"label": "Start Time", "fieldname": "scheduled_start_time", "fieldtype": "Datetime", "width": 140},
        {"label": "Items Planned", "fieldname": "total_items_planned", "fieldtype": "Int", "width": 100},
        {"label": "Items Sold", "fieldname": "total_items_sold", "fieldtype": "Int", "width": 90},
        {"label": "Sell-Through %", "fieldname": "sell_through_rate", "fieldtype": "Percent", "width": 110},
        {"label": "Gross Sales", "fieldname": "gross_sales", "fieldtype": "Currency", "width": 120},
        {"label": "Whatnot Fees (11%)", "fieldname": "total_platform_fees", "fieldtype": "Currency", "width": 130},
        {"label": "Total COGS", "fieldname": "total_cogs", "fieldtype": "Currency", "width": 120},
        {"label": "Net Profit", "fieldname": "net_profit", "fieldtype": "Currency", "width": 120},
        {"label": "Net Margin %", "fieldname": "net_margin", "fieldtype": "Percent", "width": 110},
    ]

def get_data(filters):
    conditions = ""
    values = []
    if filters and filters.get("seller_profile"):
        conditions += " AND seller_profile = %s"
        values.append(filters.get("seller_profile"))
    if filters and filters.get("status"):
        conditions += " AND status = %s"
        values.append(filters.get("status"))

    shows = frappe.db.sql(f"""
        SELECT 
            name, show_title, status, category, scheduled_start_time,
            total_items_planned, total_items_sold, gross_sales,
            total_platform_fees, total_cogs, net_profit
        FROM `tabWhatnot Show`
        WHERE 1=1 {conditions}
        ORDER BY scheduled_start_time DESC
    """, values, as_dict=True)

    for row in shows:
        planned = row.get("total_items_planned") or 0
        sold = row.get("total_items_sold") or 0
        gross = flt(row.get("gross_sales") or 0.0)
        profit = flt(row.get("net_profit") or 0.0)

        row["sell_through_rate"] = round((sold / planned * 100), 1) if planned > 0 else 0.0
        row["net_margin"] = round((profit / gross * 100), 1) if gross > 0 else 0.0

    return shows

def get_chart(data):
    if not data:
        return None
    labels = [d.get("show_title")[:15] for d in data[:8]]
    gross_vals = [flt(d.get("gross_sales")) for d in data[:8]]
    profit_vals = [flt(d.get("net_profit")) for d in data[:8]]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Gross Sales", "values": gross_vals},
                {"name": "Net Profit", "values": profit_vals}
            ]
        },
        "type": "bar",
        "colors": ["#3b82f6", "#10b981"]
    }

def get_report_summary(data):
    if not data:
        return []
    total_gross = sum(flt(d.get("gross_sales") or 0.0) for d in data)
    total_fees = sum(flt(d.get("total_platform_fees") or 0.0) for d in data)
    total_cogs = sum(flt(d.get("total_cogs") or 0.0) for d in data)
    total_profit = sum(flt(d.get("net_profit") or 0.0) for d in data)

    return [
        {"value": total_gross, "label": "Total Gross Sales", "datatype": "Currency"},
        {"value": total_fees, "label": "Platform Fees (11%)", "datatype": "Currency"},
        {"value": total_cogs, "label": "Inventory Cost (COGS)", "datatype": "Currency"},
        {"value": total_profit, "label": "Cumulative Net Profit", "datatype": "Currency", "indicator": "Green" if total_profit >= 0 else "Red"}
    ]
