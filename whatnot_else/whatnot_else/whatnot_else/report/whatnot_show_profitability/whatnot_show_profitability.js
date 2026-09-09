frappe.query_reports["Whatnot Show Profitability"] = {
	"filters": [
		{
			"fieldname": "seller_profile",
			"label": __("Seller Profile"),
			"fieldtype": "Link",
			"options": "Whatnot Seller Profile"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDraft\nScheduled\nLive\nCompleted\nCancelled"
		}
	]
};
