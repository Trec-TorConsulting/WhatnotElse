document.addEventListener("DOMContentLoaded", () => {
    const html5QrCode = new Html5Qrcode("reader");
    let currentItem = null;
    let cameraFacing = "environment";
    const recentScans = [];

    // UI Elements
    const itemCard = document.getElementById("item-result-card");
    const manualInput = document.getElementById("manual-code-input");
    const manualBtn = document.getElementById("btn-manual-lookup");
    const showSelect = document.getElementById("select-show");
    const stageBtn = document.getElementById("btn-stage-item");
    const aiBtn = document.getElementById("btn-ai-rewrite");
    const aiBox = document.getElementById("ai-output-box");
    const aiContent = document.getElementById("ai-content");
    const closeAiBtn = document.getElementById("btn-close-ai");
    const historyList = document.getElementById("scan-history-list");
    const toggleCamBtn = document.getElementById("btn-toggle-cam");

    // Load upcoming/active shows into dropdown
    fetchShows();

    // Start Camera Scanner
    startCamera(cameraFacing);

    function startCamera(facingMode) {
        html5QrCode.start(
            { facingMode: facingMode },
            { fps: 10, qrbox: { width: 250, height: 250 } },
            (decodedText) => {
                onScanSuccess(decodedText);
            },
            (error) => {
                // scanning frame error (ignore)
            }
        ).catch(err => {
            console.warn("Camera start failed, falling back to manual input:", err);
        });
    }

    // Toggle Camera Facing
    toggleCamBtn.addEventListener("click", () => {
        html5QrCode.stop().then(() => {
            cameraFacing = (cameraFacing === "environment") ? "user" : "environment";
            startCamera(cameraFacing);
        }).catch(err => console.error("Error switching camera:", err));
    });

    // Manual Lookup
    manualBtn.addEventListener("click", () => {
        const code = manualInput.value.trim();
        if (code) onScanSuccess(code);
    });

    manualInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            const code = manualInput.value.trim();
            if (code) onScanSuccess(code);
        }
    });

    // On Scan Callback
    function onScanSuccess(code) {
        // Debounce if same item just scanned
        if (currentItem && (currentItem.barcode === code || currentItem.item_code === code)) {
            return;
        }

        fetch(`/api/method/whatnot_else.api.lookup.lookup_item_by_code?code=${encodeURIComponent(code)}`)
            .then(res => res.json())
            .then(data => {
                if (data.message && data.message.found) {
                    renderItem(data.message.item);
                    addToHistory(data.message.item);
                } else {
                    alert(`Item with code "${code}" not found.`);
                }
            })
            .catch(err => {
                console.error("Lookup error:", err);
                alert("Network error performing barcode lookup.");
            });
    }

    function renderItem(item) {
        currentItem = item;
        itemCard.classList.remove("hidden");
        document.getElementById("res-name").textContent = item.item_name;
        document.getElementById("res-code").textContent = item.item_code;
        document.getElementById("res-status").textContent = item.status || "Available";
        document.getElementById("res-cogs").textContent = `$${parseFloat(item.cogs || 0).toFixed(2)}`;
        document.getElementById("res-price").textContent = `$${parseFloat(item.target_listing_price || 0).toFixed(2)}`;
        document.getElementById("res-qty").textContent = item.stock_qty || 1;
        aiBox.classList.add("hidden");
    }

    function addToHistory(item) {
        if (!recentScans.some(i => i.item_code === item.item_code)) {
            recentScans.unshift(item);
            if (recentScans.length > 5) recentScans.pop();
            renderHistory();
        }
    }

    function renderHistory() {
        historyList.innerHTML = "";
        recentScans.forEach(item => {
            const chip = document.createElement("span");
            chip.className = "chip";
            chip.textContent = item.item_name.substring(0, 18) + "...";
            chip.addEventListener("click", () => renderItem(item));
            historyList.appendChild(chip);
        });
    }

    function fetchShows() {
        fetch("/api/method/whatnot_else.api.lookup.get_active_shows")
            .then(res => res.json())
            .then(data => {
                if (data.message) {
                    showSelect.innerHTML = '<option value="">Select an active broadcast...</option>';
                    data.message.forEach(show => {
                        const opt = document.createElement("option");
                        opt.value = show.name;
                        opt.textContent = `[${show.status}] ${show.show_title}`;
                        showSelect.appendChild(opt);
                    });
                }
            })
            .catch(err => console.warn("Failed fetching shows:", err));
    }

    // Stage Item to Show
    stageBtn.addEventListener("click", () => {
        if (!currentItem) return;
        const showId = showSelect.value;
        if (!showId) {
            alert("Please select a live show first.");
            return;
        }

        const payload = {
            item_code: currentItem.item_code,
            show_id: showId,
            starting_bid: 1.0,
            reserve_price: currentItem.target_listing_price || 0.0
        };

        fetch("/api/method/whatnot_else.api.lookup.assign_item_to_show", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Frappe-CSRF-Token": frappe?.csrf_token || ""
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.message && data.message.status === "success") {
                alert(data.message.message);
                document.getElementById("res-status").textContent = "Assigned to Show";
            } else {
                alert("Failed to assign item to show.");
            }
        })
        .catch(err => console.error("Error staging item:", err));
    });

    // AI Pitch Rewrite Button
    aiBtn.addEventListener("click", () => {
        if (!currentItem) return;
        aiBox.classList.remove("hidden");
        aiContent.textContent = "Connecting to Gemini AI / Ollama for stream shoutout points...";

        fetch(`/api/method/whatnot_else.api.ai.generate_listing_content?item_title=${encodeURIComponent(currentItem.item_name)}&category=${encodeURIComponent(currentItem.category || '')}`)
            .then(res => res.json())
            .then(data => {
                if (data.message && data.message.content) {
                    aiContent.textContent = data.message.content;
                } else {
                    aiContent.textContent = "Unable to generate AI listing pitch.";
                }
            })
            .catch(err => {
                aiContent.textContent = "Error communicating with AI engine.";
            });
    });

    closeAiBtn.addEventListener("click", () => {
        aiBox.classList.add("hidden");
    });
});
