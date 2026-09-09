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
        {"label": "SKU", "fieldname": "item_code", "fieldtype": "Link", "options": "Whatnot Item", "width": 140},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 130},
        {"label": "Condition", "fieldname": "condition", "fieldtype": "Data", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Stock Qty", "fieldname": "stock_qty", "fieldtype": "Int", "width": 80},
        {"label": "COGS", "fieldname": "cogs", "fieldtype": "Currency", "width": 110},
        {"label": "Target BIN", "fieldname": "target_listing_price", "fieldtype": "Currency", "width": 110},
        {"label": "Est. Net (minus 11%)", "fieldname": "est_net", "fieldtype": "Currency", "width": 130},
        {"label": "Projected Profit", "fieldname": "proj_profit", "fieldtype": "Currency", "width": 120},
        {"label": "Projected ROI %", "fieldname": "roi_percent", "fieldtype": "Percent", "width": 110},
    ]

def get_data(filters):
    conditions = ""
    values = []
    if filters and filters.get("seller_profile"):
        conditions += " AND seller_profile = %s"
        values.append(filters.get("seller_profile"))
    if filters and filters.get("category"):
        conditions += " AND category = %s"
        values.append(filters.get("category"))

    items = frappe.db.sql(f"""
        SELECT 
            item_code, item_name, category, condition, status, stock_qty,
            cogs, target_listing_price
        FROM `tabWhatnot Item`
        WHERE 1=1 {conditions}
        ORDER BY creation DESC
    """, values, as_dict=True)

    for row in items:
        cogs = flt(row.get("cogs") or 0.0)
        target = flt(row.get("target_listing_price") or 0.0)
        fee = round(target * 0.11, 2)
        est_net = round(target - fee, 2)
        profit = round(est_net - cogs, 2)
        roi = round((profit / cogs * 100), 1) if cogs > 0 else 0.0

        row["est_net"] = est_net
        row["proj_profit"] = profit
        row["roi_percent"] = roi

    return items

def get_chart(data):
    if not data:
        return None
    # Group profit by category
    categories = {}
    for d in data:
        cat = d.get("category") or "Uncategorized"
        categories[cat] = categories.get(cat, 0.0) + flt(d.get("proj_profit") or 0.0)

    labels = list(categories.keys())[:6]
    vals = [round(categories[k], 2) for k in labels]

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": "Projected Profit", "values": vals}]
        },
        "type": "donut",
        "colors": ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899", "#6b7280"]
    }

def get_report_summary(data):
    if not data:
        return []
    total_items = len(data)
    total_inventory_val = sum(flt(d.get("cogs") or 0.0) * (d.get("stock_qty") or 1) for d in data)
    total_target_rev = sum(flt(d.get("target_listing_price") or 0.0) * (d.get("stock_qty") or 1) for d in data)
    total_proj_profit = sum(flt(d.get("proj_profit") or 0.0) * (d.get("stock_qty") or 1) for d in data)

    return [
        {"value": total_items, "label": "Catalog SKUs", "datatype": "Int"},
        {"value": total_inventory_val, "label": "Total Inventory COGS", "datatype": "Currency"},
        {"value": total_target_rev, "label": "Target Gross Realization", "datatype": "Currency"},
        {"value": total_proj_profit, "label": "Projected Total Profit", "datatype": "Currency", "indicator": "Green"}
    ]
