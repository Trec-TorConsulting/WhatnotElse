/**
 * WhatnotElse Warehouse Fulfillment Station & Sound Engine
 * Dual-Mode: Scan-to-Tray (Post-Show Sort) & Scan-to-Box (Packing Verifier)
 */

class FulfillmentStation {
    constructor() {
        this.mode = 'tray'; // 'tray' | 'box'
        this.activeShow = '';
        this.activeTrayData = null;
        this.audioEnabled = true;
        this.audioCtx = null;

        this.initDOMElements();
        this.bindEvents();
    }

    initDOMElements() {
        // Audio
        this.btnAudioToggle = document.getElementById('btn-audio-toggle');
        this.audioIcon = document.getElementById('audio-icon');
        this.audioStatusText = document.getElementById('audio-status-text');

        // Show controls
        this.showInput = document.getElementById('show-input');
        this.btnAllocateTrays = document.getElementById('btn-allocate-trays');

        // Tabs
        this.tabScanToTray = document.getElementById('tab-scan-to-tray');
        this.tabScanToBox = document.getElementById('tab-scan-to-box');
        this.secScanToTray = document.getElementById('section-scan-to-tray');
        this.secScanToBox = document.getElementById('section-scan-to-box');

        // Mode 1: Scan-to-Tray
        this.trayScanInput = document.getElementById('tray-scan-input');
        this.btnTrayScan = document.getElementById('btn-tray-scan');
        this.routingDisplay = document.getElementById('tray-routing-display');
        this.routingBadge = document.getElementById('routing-badge');
        this.routingTrayNum = document.getElementById('routing-tray-num');
        this.routingBuyer = document.getElementById('routing-buyer');
        this.routingItem = document.getElementById('routing-item');
        this.routingLot = document.getElementById('routing-lot');
        this.routingProgressFill = document.getElementById('routing-progress-fill');
        this.routingProgressText = document.getElementById('routing-progress-text');
        this.routingWeightWarning = document.getElementById('routing-weight-warning');

        // Mode 2: Scan-to-Box
        this.activeTrayInput = document.getElementById('active-tray-input');
        this.btnLoadTray = document.getElementById('btn-load-tray');
        this.boxHeaderCard = document.getElementById('box-header-card');
        this.boxTrayLabel = document.getElementById('box-tray-label');
        this.boxBuyerTitle = document.getElementById('box-buyer-title');
        this.boxWeightBadge = document.getElementById('box-weight-badge');
        this.packingFill = document.getElementById('packing-fill');
        this.packingCountLabel = document.getElementById('packing-count-label');
        this.packingPctLabel = document.getElementById('packing-pct-label');
        this.boxItemScanInput = document.getElementById('box-item-scan-input');
        this.btnVerifyItem = document.getElementById('btn-verify-item');
        this.boxManifestCard = document.getElementById('box-manifest-card');
        this.manifestItemsList = document.getElementById('manifest-items-list');
        this.boxCompleteCard = document.getElementById('box-complete-card');
        this.btnPrintLabel = document.getElementById('btn-print-thermal-label');
        this.btnNextTray = document.getElementById('btn-next-tray');

        // Modal
        this.misShipModal = document.getElementById('mis-ship-modal');
        this.misShipMsg = document.getElementById('mis-ship-msg');
        this.misShipTargetTray = document.getElementById('mis-ship-target-tray');
        this.misShipTargetBuyer = document.getElementById('mis-ship-target-buyer');
        this.btnDismissAlarm = document.getElementById('btn-dismiss-alarm');
    }

    bindEvents() {
        // Audio activation & toggle
        this.btnAudioToggle.addEventListener('click', () => this.toggleAudio());

        // Mode Switching
        this.tabScanToTray.addEventListener('click', () => this.switchMode('tray'));
        this.tabScanToBox.addEventListener('click', () => this.switchMode('box'));

        // Allocate trays
        this.btnAllocateTrays.addEventListener('click', () => this.handleAllocateTrays());

        // Mode 1 scanning
        this.btnTrayScan.addEventListener('click', () => this.handleTrayScan());
        this.trayScanInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.handleTrayScan();
        });

        // Mode 2 Box packing
        this.btnLoadTray.addEventListener('click', () => this.handleLoadTray());
        this.activeTrayInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.handleLoadTray();
        });

        this.btnVerifyItem.addEventListener('click', () => this.handleVerifyBoxItem());
        this.boxItemScanInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.handleVerifyBoxItem();
        });

        // Mis-ship dismissal
        this.btnDismissAlarm.addEventListener('click', () => {
            this.misShipModal.classList.add('hidden');
            this.boxItemScanInput.focus();
        });

        // Print & Next Tray
        this.btnPrintLabel.addEventListener('click', () => this.handlePrintLabel());
        this.btnNextTray.addEventListener('click', () => this.handleNextTray());
    }

    /* Web Audio Sound Synthesis */
    ensureAudioContext() {
        if (!this.audioCtx) {
            const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
            if (AudioCtxClass) {
                this.audioCtx = new AudioCtxClass();
            }
        }
        if (this.audioCtx && this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }
    }

    toggleAudio() {
        this.ensureAudioContext();
        this.audioEnabled = !this.audioEnabled;
        if (this.audioEnabled) {
            this.audioIcon.textContent = '🔊';
            this.audioStatusText.textContent = 'Audio Active';
            this.playSuccessChime();
        } else {
            this.audioIcon.textContent = '🔇';
            this.audioStatusText.textContent = 'Muted';
        }
    }

    playSuccessChime() {
        if (!this.audioEnabled) return;
        this.ensureAudioContext();
        if (!this.audioCtx) return;

        const now = this.audioCtx.currentTime;
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(587.33, now); // D5
        osc.frequency.exponentialRampToValueAtTime(880.00, now + 0.12); // A5

        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.35);

        if (navigator.vibrate) navigator.vibrate([80]);
    }

    playAlarmBuzzer() {
        if (!this.audioEnabled) return;
        this.ensureAudioContext();
        if (!this.audioCtx) return;

        const now = this.audioCtx.currentTime;
        // Dissonant dual sawtooth oscillators
        [150, 215].forEach(freq => {
            const osc = this.audioCtx.createOscillator();
            const gain = this.audioCtx.createGain();

            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(freq, now);

            gain.gain.setValueAtTime(0.4, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);

            osc.connect(gain);
            gain.connect(this.audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.6);
        });

        if (navigator.vibrate) navigator.vibrate([250, 100, 250, 100, 250]);
    }

    playFanfare() {
        if (!this.audioEnabled) return;
        this.ensureAudioContext();
        if (!this.audioCtx) return;

        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
        notes.forEach((freq, idx) => {
            const now = this.audioCtx.currentTime + (idx * 0.1);
            const osc = this.audioCtx.createOscillator();
            const gain = this.audioCtx.createGain();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, now);

            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

            osc.connect(gain);
            gain.connect(this.audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.25);
        });

        if (navigator.vibrate) navigator.vibrate([100, 50, 100, 50, 200]);
    }

    speak(text) {
        if (!this.audioEnabled || !('speechSynthesis' in window)) return;
        try {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.05;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.warn('Speech synthesis error:', e);
        }
    }

    /* Mode Switching */
    switchMode(mode) {
        this.ensureAudioContext();
        this.mode = mode;
        if (mode === 'tray') {
            this.tabScanToTray.classList.add('active');
            this.tabScanToBox.classList.remove('active');
            this.secScanToTray.classList.remove('hidden');
            this.secScanToBox.classList.add('hidden');
            this.trayScanInput.focus();
        } else {
            this.tabScanToBox.classList.add('active');
            this.tabScanToTray.classList.remove('active');
            this.secScanToBox.classList.remove('hidden');
            this.secScanToTray.classList.add('hidden');
            this.activeTrayInput.focus();
        }
    }

    /* Backend Calls */
    async handleAllocateTrays() {
        this.ensureAudioContext();
        const showName = this.showInput.value.trim();
        if (!showName) {
            alert('Please enter a Live Show ID first.');
            this.showInput.focus();
            return;
        }

        try {
            const res = await fetch('/api/method/whatnot_else.api.fulfillment.allocate_show_trays', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': window.csrf_token || ''
                },
                body: JSON.stringify({ show_name: showName })
            });
            const data = await res.json();
            const result = data.message;

            if (result && result.success) {
                alert(`Allocated ${result.total_trays_allocated} physical trays for show '${showName}'. Ready to sort!`);
                this.activeShow = showName;
                this.playSuccessChime();
            } else {
                alert(result ? result.message : 'Error allocating trays.');
            }
        } catch (err) {
            console.error('Tray allocation error:', err);
            alert('Failed to connect to fulfillment API.');
        }
    }

    async handleTrayScan() {
        this.ensureAudioContext();
        const code = this.trayScanInput.value.trim();
        if (!code) return;

        this.trayScanInput.value = '';
        const showName = this.showInput.value.trim() || this.activeShow;

        try {
            const res = await fetch('/api/method/whatnot_else.api.fulfillment.scan_item_to_tray', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': window.csrf_token || ''
                },
                body: JSON.stringify({ barcode: code, show_name: showName })
            });
            const data = await res.json();
            const result = data.message;

            if (result && result.success) {
                // Update Giant Routing Target
                this.routingDisplay.className = 'tray-routing-card routed';
                this.routingBadge.textContent = 'Routed to Tray';
                this.routingTrayNum.textContent = `TRAY ${result.tray_number}`;
                this.routingBuyer.textContent = `@${result.buyer_username}`;
                this.routingItem.textContent = result.item_name;
                this.routingLot.textContent = `Lot #${result.lot_number || 1}`;

                const pct = result.total_items > 0 ? (result.sorted_items / result.total_items * 100) : 0;
                this.routingProgressFill.style.width = `${pct}%`;
                this.routingProgressText.textContent = `${result.sorted_items} of ${result.total_items} items sorted`;

                if (result.weight_warning) {
                    this.routingWeightWarning.classList.remove('hidden');
                    this.routingWeightWarning.textContent = result.weight_warning_notes || '⚠️ Weight Alert: Exceeds 16 oz';
                } else {
                    this.routingWeightWarning.classList.add('hidden');
                }

                // Audio guidance
                this.playSuccessChime();
                if (result.speech_text) {
                    this.speak(result.speech_text);
                }
            } else {
                this.routingDisplay.className = 'tray-routing-card idle';
                this.routingBadge.textContent = 'Not Found';
                this.routingTrayNum.textContent = 'UNASSIGNED';
                this.routingItem.textContent = (result && result.message) || `Code '${code}' not found in show.`;
                this.playAlarmBuzzer();
            }
        } catch (err) {
            console.error('Tray scan error:', err);
            this.playAlarmBuzzer();
        } finally {
            this.trayScanInput.focus();
        }
    }

    async handleLoadTray() {
        this.ensureAudioContext();
        let trayId = this.activeTrayInput.value.trim();
        if (!trayId) return;

        // Auto-prefix if numeric
        if (!isNaN(trayId) && this.showInput.value.trim()) {
            trayId = `TRAY-${trayId}-${this.showInput.value.trim()}`;
        }

        try {
            const res = await fetch(`/api/resource/Whatnot%20Fulfillment%20Tray/${encodeURIComponent(trayId)}`);
            if (!res.ok) {
                alert(`Tray '${trayId}' not found.`);
                return;
            }
            const docData = await res.json();
            const tray = docData.data;
            this.activeTrayData = tray;

            // Render Box View
            this.renderBoxView(tray);
            this.boxItemScanInput.focus();
            this.playSuccessChime();
        } catch (err) {
            console.error('Error loading tray:', err);
            alert('Failed to load tray.');
        }
    }

    renderBoxView(tray) {
        this.boxHeaderCard.classList.remove('hidden');
        this.boxManifestCard.classList.remove('hidden');

        this.boxTrayLabel.textContent = `Packing Tray #${tray.tray_number}`;
        this.boxBuyerTitle.textContent = `@${tray.buyer_username}`;
        this.boxWeightBadge.textContent = `${tray.total_weight_oz || 0.0} oz`;

        const pct = tray.total_items > 0 ? Math.round(tray.packed_items / tray.total_items * 100) : 0;
        this.packingFill.style.width = `${pct}%`;
        this.packingCountLabel.textContent = `${tray.packed_items} / ${tray.total_items} Items Verified`;
        this.packingPctLabel.textContent = `${pct}% Complete`;

        if (pct === 100 && tray.total_items > 0) {
            this.boxCompleteCard.classList.remove('hidden');
        } else {
            this.boxCompleteCard.classList.add('hidden');
        }

        // Render checklist items
        this.manifestItemsList.innerHTML = '';
        (tray.items || []).forEach(item => {
            const row = document.createElement('div');
            row.className = `manifest-item-row ${item.is_packed ? 'packed' : ''}`;
            row.innerHTML = `
                <div class="item-row-left">
                    <span class="item-check-icon">${item.is_packed ? '✅' : '⚪'}</span>
                    <div>
                        <div class="item-row-name">${item.item_name}</div>
                        <div class="item-row-code">${item.barcode || item.item_code} · ${item.weight_oz || 0} oz</div>
                    </div>
                </div>
                <div class="item-status-pill ${item.is_packed ? 'packed' : 'pending'}">
                    ${item.is_packed ? 'Packed' : 'In Tray'}
                </div>
            `;
            this.manifestItemsList.appendChild(row);
        });
    }

    async handleVerifyBoxItem() {
        this.ensureAudioContext();
        if (!this.activeTrayData) {
            alert('Please load a Tray to pack first.');
            return;
        }

        const code = this.boxItemScanInput.value.trim();
        if (!code) return;

        this.boxItemScanInput.value = '';

        try {
            const res = await fetch('/api/method/whatnot_else.api.fulfillment.verify_box_item', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': window.csrf_token || ''
                },
                body: JSON.stringify({ tray_name: this.activeTrayData.name, barcode: code })
            });
            const data = await res.json();
            const result = data.message;

            if (result && result.success) {
                this.playSuccessChime();
                // Reload tray
                await this.handleLoadTray();

                if (result.is_complete) {
                    this.playFanfare();
                    this.speak(`Tray ${result.tray_number} 100% packed. Zero mis-ships.`);
                }
            } else if (result && result.error_type === 'MIS_SHIP_ALARM') {
                // Show Mis-Ship modal
                this.misShipMsg.textContent = result.message;
                this.misShipTargetTray.textContent = `TRAY ${result.actual_tray}`;
                this.misShipTargetBuyer.textContent = `@${result.actual_buyer}`;
                this.misShipModal.classList.remove('hidden');

                this.playAlarmBuzzer();
                this.speak(`Mis ship alarm! Item belongs to Tray ${result.actual_tray}!`);
            } else {
                alert((result && result.message) || 'Item not recognized.');
                this.playAlarmBuzzer();
            }
        } catch (err) {
            console.error('Box verify error:', err);
            this.playAlarmBuzzer();
        } finally {
            this.boxItemScanInput.focus();
        }
    }

    handlePrintLabel() {
        if (!this.activeTrayData) return;
        // Launch print format in new window
        window.open(`/app/print/Whatnot%20Fulfillment%20Tray/${encodeURIComponent(this.activeTrayData.name)}`, '_blank');
    }

    handleNextTray() {
        this.boxHeaderCard.classList.add('hidden');
        this.boxManifestCard.classList.add('hidden');
        this.boxCompleteCard.classList.add('hidden');
        this.activeTrayInput.value = '';
        this.activeTrayData = null;
        this.activeTrayInput.focus();
    }
}

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
    window.fulfillmentStation = new FulfillmentStation();
});
