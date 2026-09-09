app_name = "whatnot_else"
app_title = "Whatnot Else"
app_publisher = "Tobey Rector"
app_description = "Enterprise Frappe / ERPNext custom app for Whatnot live sellers"
app_email = "trecto282@cable.comcast.com"
app_license = "MIT"

# Apps
# ------------------

# required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "whatnot_else",
# 		"logo": "/assets/whatnot_else/logo.png",
# 		"title": "Whatnot Else",
# 		"route": "/app/whatnot-else",
# 		"has_permission": "whatnot_else.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js in doctype views
# doctype_js = {"Whatnot Order" : "public/js/whatnot_order.js"}
# doctype_list_js = {"Whatnot Order" : "public/js/whatnot_order_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js = {"Whatnot Show": "whatnot_else/doctype/whatnot_show/whatnot_show_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Whatnot Order": {
        "on_submit": "whatnot_else.whatnot_else.doctype.whatnot_order.whatnot_order.create_erpnext_sales_order"
    }
}

# Website Route Rules
# -------------------
website_route_rules = [
    {"from_route": "/overlay", "to_route": "overlay"},
    {"from_route": "/api/stripe/webhook", "to_route": "whatnot_else.api.stripe_billing.handle_stripe_webhook"},
]

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"whatnot_else.tasks.all"
# 	],
# 	"daily": [
# 		"whatnot_else.tasks.daily"
# 	],
# 	"hourly": [
# 		"whatnot_else.tasks.hourly"
# 	],
# 	"weekly": [
# 		"whatnot_else.tasks.weekly"
# 	],
# 	"monthly": [
# 		"whatnot_else.tasks.monthly"
# 	],
# }

