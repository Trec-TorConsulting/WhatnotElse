frappe.views.calendar["Whatnot Show"] = {
	field_map: {
		start: "scheduled_start_time",
		end: "scheduled_end_time",
		id: "name",
		title: "show_title",
		allDay: "all_day",
		status: "status"
	},
	style_map: {
		"Draft": "secondary",
		"Scheduled": "info",
		"Live": "danger",
		"Completed": "success",
		"Cancelled": "dark"
	},
	order_by: "scheduled_start_time",
	get_events_method: "frappe.desk.calendar.get_events"
};
