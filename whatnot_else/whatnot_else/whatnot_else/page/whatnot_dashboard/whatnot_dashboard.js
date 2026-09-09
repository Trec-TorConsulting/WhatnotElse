frappe.pages['whatnot_dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Whatnot Command Center'),
		single_column: true
	});

	page.set_secondary_action(__('Launch Mobile Scanner'), function() {
		window.open('/scanner', '_blank');
	});

	page.add_button(__('Refresh Data'), function() {
		load_dashboard_data(page);
	});

	$(wrapper).find('.layout-main-section').html(`
		<div class="whatnot-dashboard-container">
			<!-- KPI Grid -->
			<div class="kpi-grid">
				<div class="kpi-card">
					<div class="kpi-title">30-Day Gross Revenue</div>
					<div class="kpi-value text-primary" id="kpi-gross">$0.00</div>
					<div class="kpi-subtitle">Across all live shows</div>
				</div>
				<div class="kpi-card">
					<div class="kpi-title">30-Day Net Payout</div>
					<div class="kpi-value text-success" id="kpi-net">$0.00</div>
					<div class="kpi-subtitle">After ~11% platform fees</div>
				</div>
				<div class="kpi-card">
					<div class="kpi-title">Avg Sell-Through</div>
					<div class="kpi-value text-warning" id="kpi-sellthrough">0%</div>
					<div class="kpi-subtitle">Auction conversion velocity</div>
				</div>
				<div class="kpi-card">
					<div class="kpi-title">VIP Buyers</div>
					<div class="kpi-value text-info" id="kpi-vips">0</div>
					<div class="kpi-subtitle">Gold & Whale spenders</div>
				</div>
			</div>

			<!-- Quick Navigation Bar -->
			<div class="quick-nav-bar">
				<a href="/app/whatnot-show" class="nav-btn">📅 Show Calendar</a>
				<a href="/app/whatnot-item" class="nav-btn">📦 Catalog Inventory</a>
				<a href="/app/whatnot-order" class="nav-btn">🛒 Order Ledger</a>
				<a href="/app/whatnot-payout-batch" class="nav-btn">💰 Stripe Payouts</a>
				<a href="/app/whatnot-buyer" class="nav-btn">👥 VIP CRM</a>
			</div>

			<!-- Main Layout Grid -->
			<div class="dashboard-columns">
				<!-- Upcoming Shows Column -->
				<div class="dash-card col-shows">
					<div class="dash-card-header">
						<h3>Upcoming Live Broadcasts</h3>
						<a href="/app/whatnot-show/new" class="btn btn-xs btn-primary">+ Schedule Show</a>
					</div>
					<div id="upcoming-shows-list" class="shows-list">
						<div class="empty-state">Loading broadcasts...</div>
					</div>
				</div>

				<!-- Inventory Category Breakdown -->
				<div class="dash-card col-categories">
					<div class="dash-card-header">
						<h3>Top Product Categories</h3>
					</div>
					<div id="category-bars" class="category-bars-list">
						<div class="empty-state">Loading categories...</div>
					</div>
				</div>
			</div>
		</div>
	`);

	load_dashboard_data(page);
};

function load_dashboard_data(page) {
	frappe.call({
		method: 'whatnot_else.api.analytics.get_dashboard_analytics',
		callback: function(r) {
			if (!r.message) return;
			const data = r.message;
			const kpis = data.kpis;

			// Update KPIs
			$('#kpi-gross').text(format_currency(kpis.gross_revenue_30d));
			$('#kpi-net').text(format_currency(kpis.net_revenue_30d));
			$('#kpi-sellthrough').text(`${kpis.avg_sell_through}%`);
			$('#kpi-vips').text(kpis.vip_buyers_count);

			// Render Upcoming Shows
			const showsContainer = $('#upcoming-shows-list');
			showsContainer.empty();
			if (data.upcoming_shows && data.upcoming_shows.length > 0) {
				data.upcoming_shows.forEach(show => {
					const dateStr = show.scheduled_start_time ? frappe.datetime.str_to_user(show.scheduled_start_time) : 'Unscheduled';
					const badgeClass = show.status === 'Live' ? 'badge-danger' : 'badge-info';
					showsContainer.append(`
						<div class="show-row">
							<div class="show-info">
								<a href="/app/whatnot-show/${show.name}" class="show-title-link"><strong>${show.show_title}</strong></a>
								<div class="show-date">${dateStr} &bull; ${show.total_items_planned || 0} Lots Staged</div>
							</div>
							<span class="badge ${badgeClass}">${show.status}</span>
						</div>
					`);
				});
			} else {
				showsContainer.html('<div class="empty-state">No live broadcasts currently scheduled.</div>');
			}

			// Render Categories
			const catContainer = $('#category-bars');
			catContainer.empty();
			if (data.categories && data.categories.length > 0) {
				const maxCount = Math.max(...data.categories.map(c => c.count));
				data.categories.forEach(cat => {
					const pct = maxCount > 0 ? (cat.count / maxCount * 100) : 0;
					catContainer.append(`
						<div class="cat-bar-item">
							<div class="cat-label">
								<span>${cat.category || 'General'}</span>
								<strong>${cat.count} items</strong>
							</div>
							<div class="cat-progress-bg">
								<div class="cat-progress-fill" style="width: ${pct}%;"></div>
							</div>
						</div>
					`);
				});
			} else {
				catContainer.html('<div class="empty-state">No items cataloged yet.</div>');
			}
		}
	});
}
