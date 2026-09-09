/**
 * WhatnotElse OBS Live Broadcast Overlay Controller
 * Polls stream telemetry endpoint and updates live lot card, VIP popups, and stats.
 */

(function () {
  const urlParams = new URLSearchParams(window.location.search);
  const showParam = urlParams.get('show');
  const subdomainParam = urlParams.get('subdomain');
  const pollInterval = parseInt(urlParams.get('poll') || '2500', 10);

  // DOM Elements
  const elShowTitle = document.getElementById('show-title');
  const elStreamStatus = document.getElementById('stream-status');
  const elStatOrders = document.getElementById('stat-orders');
  const elStatRevenue = document.getElementById('stat-revenue');

  const elLotNumber = document.getElementById('lot-number');
  const elLotTitle = document.getElementById('lot-title');
  const elLotSku = document.getElementById('lot-sku');
  const elLotCert = document.getElementById('lot-cert');
  const elGradeBadge = document.getElementById('grade-badge');
  const elStartBid = document.getElementById('start-bid');
  const elCurrentBid = document.getElementById('current-bid');

  const elVipBanner = document.getElementById('vip-banner');
  const elVipTier = document.getElementById('vip-tier');
  const elVipUsername = document.getElementById('vip-username');

  let lastBid = null;
  let shownVipSet = new Set();

  async function fetchTelemetry() {
    try {
      let endpoint = '/api/method/whatnot_else.api.overlay.get_active_stream_telemetry';
      const params = [];
      if (showParam) params.push(`show_name=${encodeURIComponent(showParam)}`);
      if (subdomainParam) params.push(`subdomain=${encodeURIComponent(subdomainParam)}`);
      if (params.length > 0) endpoint += `?${params.join('&')}`;

      const res = await fetch(endpoint);
      if (!res.ok) return;

      const data = await res.json();
      const payload = data.message || data;

      if (!payload || !payload.success) return;

      updateUI(payload);
    } catch (err) {
      console.error('[WhatnotElse Overlay] Telemetry poll error:', err);
    }
  }

  function updateUI(data) {
    // 1. Header & Stats
    if (elShowTitle && data.show_title) {
      elShowTitle.textContent = data.show_title;
    }
    if (elStatOrders && data.stats) {
      elStatOrders.textContent = data.stats.total_orders || 0;
    }
    if (elStatRevenue && data.stats) {
      elStatRevenue.textContent = `$${(data.stats.total_revenue || 0).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`;
    }

    // 2. Active Lot
    const lot = data.lot;
    if (lot) {
      if (elLotNumber) elLotNumber.textContent = lot.lot_number || 1;
      if (elLotTitle) elLotTitle.textContent = lot.title || 'Live Auction';
      if (elLotSku) elLotSku.textContent = lot.item_code || 'ITEM';

      // Graded Collectible Badge
      if (elGradeBadge) {
        if (lot.is_graded && lot.grade) {
          elGradeBadge.textContent = `${lot.grading_company || 'PSA'} ${lot.grade}`;
          elGradeBadge.classList.remove('hidden');
        } else {
          elGradeBadge.classList.add('hidden');
        }
      }

      // Cert Number
      if (elLotCert) {
        if (lot.cert_number) {
          elLotCert.textContent = `CERT: #${lot.cert_number}`;
          elLotCert.classList.remove('hidden');
        } else {
          elLotCert.classList.add('hidden');
        }
      }

      // Bids
      if (elStartBid) {
        elStartBid.textContent = `$${lot.starting_bid || 1}`;
      }
      if (elCurrentBid) {
        const curBid = lot.current_bid || lot.starting_bid || 1;
        elCurrentBid.textContent = `$${curBid}`;

        // Pulse animation if bid updated
        if (lastBid !== null && curBid > lastBid) {
          elCurrentBid.animate([
            { transform: 'scale(1.25)', color: '#38bdf8' },
            { transform: 'scale(1)', color: '#10b981' }
          ], { duration: 400 });
        }
        lastBid = curBid;
      }
    }

    // 3. VIP Alerts Pop-Up
    if (data.vip_alerts && data.vip_alerts.length > 0) {
      const latestVip = data.vip_alerts[0];
      if (latestVip && !shownVipSet.has(latestVip.username)) {
        shownVipSet.add(latestVip.username);
        triggerVipAlert(latestVip);
      }
    }
  }

  function triggerVipAlert(vip) {
    if (!elVipBanner) return;
    elVipTier.textContent = vip.tier || 'VIP BUYER';
    elVipUsername.textContent = `@${vip.username}`;
    elVipBanner.classList.remove('hidden');

    // Auto-hide alert after 5.5 seconds
    setTimeout(() => {
      elVipBanner.classList.add('hidden');
    }, 5500);
  }

  // Initial poll + interval
  fetchTelemetry();
  setInterval(fetchTelemetry, pollInterval);
})();
