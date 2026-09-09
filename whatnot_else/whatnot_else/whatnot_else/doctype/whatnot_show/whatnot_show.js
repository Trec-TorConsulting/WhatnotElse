frappe.ui.form.on('Whatnot Show', {
	refresh: function(frm) {
		if (frm.doc.status === 'Scheduled') {
			frm.add_custom_button(__('Start Stream (Go Live)'), function() {
				frappe.call({
					method: 'start_stream',
					doc: frm.doc,
					callback: function(r) {
						frm.reload_doc();
						frappe.show_alert({message: __('Stream is now LIVE!'), indicator: 'green'});
					}
				});
			}).addClass('btn-danger');
		} else if (frm.doc.status === 'Live') {
			frm.add_custom_button(__('Finish Stream'), function() {
				frappe.confirm(__('Are you sure you want to complete this stream broadcast?'), function() {
					frappe.call({
						method: 'finish_stream',
						doc: frm.doc,
						callback: function(r) {
							frm.reload_doc();
							frappe.show_alert({message: __('Stream Completed!'), indicator: 'blue'});
						}
					});
				});
			}).addClass('btn-primary');
		}
	}
});
