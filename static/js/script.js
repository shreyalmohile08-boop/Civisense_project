/**
 * Civisense – Client-Side Interactive Engine
 * Handles Leaflet mapping, Chart.js analytics, geolocation,
 * drag-and-drop file preview, and real-time admin status transitions.
 */

// =========================================================
// 1. Core Utilities & Mobile Navigation
// =========================================================

document.addEventListener("DOMContentLoaded", function () {
    // Mobile navigation toggle
    const menuBtn = document.getElementById("mobile-menu-btn");
    const navMenu = document.getElementById("nav-menu");
    if (menuBtn && navMenu) {
        menuBtn.addEventListener("click", function () {
            navMenu.classList.toggle("show");
        });
    }

    // Initialize Report form handlers if present
    initReportForm();

    // Auto-dismiss flash alerts after 6 seconds
    const flashToasts = document.querySelectorAll(".flash-toast");
    flashToasts.forEach(toast => {
        setTimeout(() => {
            toast.style.transition = "opacity 0.4s ease";
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 400);
        }, 6000);
    });
});

// Toast notification trigger
function showToast(message, type = "success") {
    const container = document.getElementById("flash-container") || createToastContainer();
    const toast = document.createElement("div");
    toast.className = `flash-toast flash-${type}`;
    toast.role = "alert";
    
    const icon = type === "success" ? "fa-circle-check" : type === "error" ? "fa-circle-xmark" : "fa-circle-info";
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span class="flash-message">${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove();">&times;</button>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = "opacity 0.4s ease";
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 400);
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement("div");
    container.id = "flash-container";
    container.className = "container flash-container";
    document.querySelector(".navbar").after(container);
    return container;
}

// Copy ID to clipboard
function copyComplaintId(id) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(id).then(() => {
            const btn = document.getElementById("btn-copy-id");
            const textSpan = document.getElementById("copy-text");
            if (btn && textSpan) {
                const oldText = textSpan.innerText;
                textSpan.innerText = "Copied!";
                btn.style.background = "rgba(52, 211, 153, 0.3)";
                setTimeout(() => {
                    textSpan.innerText = oldText;
                    btn.style.background = "";
                }, 2000);
            }
            showToast(`Complaint ID ${id} copied to clipboard!`, "success");
        });
    }
}

// =========================================================
// 2. Report Issue Page Logic (Dropzone & Geolocation)
// =========================================================

let reportMiniMap = null;
let reportMiniMarker = null;

function initReportForm() {
    const dropzone = document.getElementById("image-dropzone");
    const fileInput = document.getElementById("image-input");
    const previewContainer = document.getElementById("dropzone-preview");
    const promptContainer = document.getElementById("dropzone-prompt");
    const previewImg = document.getElementById("preview-img");
    const previewFilename = document.getElementById("preview-filename");
    const previewFilesize = document.getElementById("preview-filesize");
    const btnRemove = document.getElementById("btn-remove-preview");
    const form = document.getElementById("report-issue-form");

    if (dropzone && fileInput) {
        // Drag over / leave effects
        ["dragenter", "dragover"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("drag-over");
            }, false);
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("drag-over");
            }, false);
        });

        // Drop file
        dropzone.addEventListener("drop", (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                displayImagePreview(files[0]);
            }
        });

        // Click file browse
        fileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                displayImagePreview(e.target.files[0]);
            }
        });

        // Remove preview
        if (btnRemove) {
            btnRemove.addEventListener("click", (e) => {
                e.stopPropagation();
                fileInput.value = "";
                const sampleInp = document.getElementById("selected-sample-input");
                if (sampleInp) sampleInp.value = "";
                document.querySelectorAll(".real-photo-card").forEach(c => c.classList.remove("selected-preset"));
                previewContainer.classList.add("hidden");
                promptContainer.classList.remove("hidden");
            });
        }
    }


    function displayImagePreview(file) {
        if (!file.type.startsWith("image/")) {
            showToast("Please select a valid image file (JPG, PNG, WEBP).", "error");
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewFilename.textContent = file.name;
            previewFilesize.textContent = (file.size / 1024).toFixed(1) + " KB";
            promptContainer.classList.add("hidden");
            previewContainer.classList.remove("hidden");
        };
        reader.readAsDataURL(file);
    }

    // Real photo evidence presets click handler
    const realPhotoCards = document.querySelectorAll(".real-photo-card");
    const selectedSampleInput = document.getElementById("selected-sample-input");
    realPhotoCards.forEach(card => {
        card.addEventListener("click", function () {
            const filename = this.getAttribute("data-filename");
            const name = this.getAttribute("data-name");
            const desc = this.getAttribute("data-desc");
            const loc = this.getAttribute("data-loc");
            const lat = parseFloat(this.getAttribute("data-lat"));
            const lon = parseFloat(this.getAttribute("data-lon"));
            const imgSrc = this.querySelector("img").src;

            // Mark visually selected
            realPhotoCards.forEach(c => c.classList.remove("selected-preset"));
            this.classList.add("selected-preset");

            // Set hidden sample input & update live preview
            if (selectedSampleInput) selectedSampleInput.value = filename;
            if (fileInput) fileInput.value = ""; // Clear file input so selected sample takes priority
            if (previewImg) previewImg.src = imgSrc;
            if (previewFilename) previewFilename.textContent = name;
            if (previewFilesize) previewFilesize.textContent = "1.2 MB (High-Res Photographic Evidence)";
            if (promptContainer) promptContainer.classList.add("hidden");
            if (previewContainer) previewContainer.classList.remove("hidden");

            // Populate description & location automatically
            if (descTextarea) descTextarea.value = desc;
            if (locInput) locInput.value = loc;
            if (latInput) latInput.value = lat;
            if (lonInput) lonInput.value = lon;
            if (coordsDisplay) coordsDisplay.textContent = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;

            // Update mini map pin
            if (reportMiniMarker && reportMiniMap) {
                reportMiniMarker.setLatLng([lat, lon]);
                reportMiniMap.setView([lat, lon], 15);
            }

            showToast(`Loaded real evidence photo: ${name}`, "success");
        });
    });

    // Quick description templates
    const quickTagBtns = document.querySelectorAll(".quick-tag-btn");
    const descTextarea = document.getElementById("issue-description");
    quickTagBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            if (descTextarea) {
                descTextarea.value = this.getAttribute("data-text");
                descTextarea.focus();
            }
        });
    });


    // Geolocation button
    const btnGeolocate = document.getElementById("btn-geolocate");
    const locInput = document.getElementById("location-input");
    const latInput = document.getElementById("lat-input");
    const lonInput = document.getElementById("lon-input");
    const coordsDisplay = document.getElementById("coords-display");

    if (btnGeolocate) {
        btnGeolocate.addEventListener("click", function () {
            btnGeolocate.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Locating...';
            btnGeolocate.disabled = true;

            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;

                        latInput.value = lat.toFixed(5);
                        lonInput.value = lon.toFixed(5);
                        coordsDisplay.textContent = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
                        locInput.value = `Verified Citizen GPS: Near Lat ${lat.toFixed(3)}, Lon ${lon.toFixed(3)}, Nagpur`;

                        if (reportMiniMarker && reportMiniMap) {
                            reportMiniMarker.setLatLng([lat, lon]);
                            reportMiniMap.setView([lat, lon], 15);
                        }

                        btnGeolocate.innerHTML = '<i class="fa-solid fa-check"></i> Location Acquired';
                        btnGeolocate.style.backgroundColor = '#d1fae5';
                        btnGeolocate.style.color = '#065f46';
                        showToast("GPS coordinates acquired successfully!", "success");

                        setTimeout(() => {
                            btnGeolocate.innerHTML = '<i class="fa-solid fa-crosshairs"></i> Use Current Location';
                            btnGeolocate.style.backgroundColor = '';
                            btnGeolocate.style.color = '';
                            btnGeolocate.disabled = false;
                        }, 3000);
                    },
                    (error) => {
                        console.warn("Geolocation fallback:", error.message);
                        // Fallback to Nagpur Center
                        latInput.value = "21.1458";
                        lonInput.value = "79.0882";
                        coordsDisplay.textContent = "21.1458, 79.0882";
                        locInput.value = "Nagpur Central District, Civil Lines";

                        if (reportMiniMarker && reportMiniMap) {
                            reportMiniMarker.setLatLng([21.1458, 79.0882]);
                            reportMiniMap.setView([21.1458, 79.0882], 14);
                        }

                        btnGeolocate.innerHTML = '<i class="fa-solid fa-crosshairs"></i> Use Current Location';
                        btnGeolocate.disabled = false;
                        showToast("Browser GPS unavailable. Set default to Nagpur Central. You can select a preset below or drag the pin.", "info");
                    },
                    { timeout: 8000, enableHighAccuracy: true }
                );
            } else {
                showToast("Geolocation is not supported by your browser. Please type location manually.", "error");
                btnGeolocate.innerHTML = '<i class="fa-solid fa-crosshairs"></i> Use Current Location';
                btnGeolocate.disabled = false;
            }
        });
    }

    // Demo Preset Location Chips
    const locChips = document.querySelectorAll(".loc-chip");
    locChips.forEach(chip => {
        chip.addEventListener("click", function () {
            const name = this.getAttribute("data-name");
            const lat = parseFloat(this.getAttribute("data-lat"));
            const lon = parseFloat(this.getAttribute("data-lon"));

            if (locInput) locInput.value = name;
            if (latInput) latInput.value = lat;
            if (lonInput) lonInput.value = lon;
            if (coordsDisplay) coordsDisplay.textContent = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;

            if (reportMiniMarker && reportMiniMap) {
                reportMiniMarker.setLatLng([lat, lon]);
                reportMiniMap.setView([lat, lon], 15);
            }
        });
    });

    // Form submit loading state
    if (form) {
        form.addEventListener("submit", function () {
            const btn = document.getElementById("btn-submit-report");
            if (btn) {
                btn.querySelector(".submit-normal-state").classList.add("hidden");
                btn.querySelector(".submit-loading-state").classList.remove("hidden");
                btn.disabled = true;
            }
        });
    }
}

// Mini Map Picker for Report Page
function initReportMiniMap() {
    const mapElement = document.getElementById("report-mini-map");
    if (!mapElement) return;

    const latInput = document.getElementById("lat-input");
    const lonInput = document.getElementById("lon-input");
    const coordsDisplay = document.getElementById("coords-display");

    const defaultLat = latInput ? parseFloat(latInput.value) || 21.1458 : 21.1458;
    const defaultLng = lonInput ? parseFloat(lonInput.value) || 79.0882 : 79.0882;

    reportMiniMap = L.map("report-mini-map", {
        center: [defaultLat, defaultLng],
        zoom: 13,
        zoomControl: true
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(reportMiniMap);

    // Draggable marker
    reportMiniMarker = L.marker([defaultLat, defaultLng], {
        draggable: true
    }).addTo(reportMiniMap);

    function updateCoords(lat, lng) {
        if (latInput) latInput.value = lat.toFixed(5);
        if (lonInput) lonInput.value = lng.toFixed(5);
        if (coordsDisplay) coordsDisplay.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    }

    reportMiniMarker.on("dragend", function (e) {
        const position = reportMiniMarker.getLatLng();
        updateCoords(position.lat, position.lng);
    });

    reportMiniMap.on("click", function (e) {
        reportMiniMarker.setLatLng(e.latlng);
        updateCoords(e.latlng.lat, e.latlng.lng);
    });
}

// =========================================================
// 3. Track Complaint Leaflet Map
// =========================================================

function initTrackMap() {
    const mapEl = document.getElementById("track-complaint-map");
    if (!mapEl) return;

    const lat = parseFloat(mapEl.getAttribute("data-lat")) || 21.1458;
    const lng = parseFloat(mapEl.getAttribute("data-lng")) || 79.0882;
    const id = mapEl.getAttribute("data-id") || "Complaint";
    const issue = mapEl.getAttribute("data-issue") || "Civic Defect";
    const status = mapEl.getAttribute("data-status") || "Reported";

    const map = L.map("track-complaint-map", {
        center: [lat, lng],
        zoom: 15,
        zoomControl: true
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Create marker
    const marker = L.marker([lat, lng]).addTo(map);
    marker.bindPopup(`
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12.5px;">
            <strong style="color: #059669;">${id}</strong><br/>
            <strong>${issue}</strong><br/>
            <span style="color: #64748b;" id="track-map-popup-status">Status: ${status}</span>
        </div>
    `).openPopup();
}

// =========================================================
// 3.1. Track Complaint Real-Time Live Status Polling & Sync
// =========================================================

let trackPollingInterval = null;

function initTrackLiveSync() {
    const timelineCard = document.getElementById("timeline-card");
    if (!timelineCard) return;

    const complaintId = timelineCard.getAttribute("data-complaint-id");
    if (!complaintId) return;

    // Clear any previous polling loop
    if (trackPollingInterval) clearInterval(trackPollingInterval);

    // Initial check and start 2-second background polling
    trackPollingInterval = setInterval(() => {
        fetch(`/api/complaints/${encodeURIComponent(complaintId)}`)
            .then(res => {
                if (!res.ok) throw new Error("Status check failed");
                return res.json();
            })
            .then(data => {
                if (!data.success) return;

                const currentStatus = (timelineCard.getAttribute("data-current-status") || "").trim();
                if (data.status.toLowerCase() !== currentStatus.toLowerCase()) {
                    console.log(`[Live Status Sync] Detected change: "${currentStatus}" -> "${data.status}"`);
                    updateTrackTimelineDOM(data);
                }
            })
            .catch(err => {
                // Ignore transient network errors during background polling
            });
    }, 2000);
}

function updateTrackTimelineDOM(data) {
    const timelineCard = document.getElementById("timeline-card");
    if (!timelineCard) return;

    const newStatus = data.status;
    const newIdx = data.status_idx;

    // Update container state
    timelineCard.setAttribute("data-current-status", newStatus);
    timelineCard.setAttribute("data-current-idx", newIdx);

    // 1. Update Header Status Badge
    const headerBadge = document.getElementById("track-header-status-badge");
    const headerText = document.getElementById("track-header-status-text");
    if (headerBadge) {
        headerBadge.className = `status-badge-lg status-${newStatus.toLowerCase().replace(" ", "-")}`;
    }
    if (headerText) {
        headerText.textContent = newStatus;
    }

    // 2. Update Map Popup Status if open
    const mapPopupStatus = document.getElementById("track-map-popup-status");
    if (mapPopupStatus) {
        mapPopupStatus.textContent = `Status: ${newStatus}`;
    }

    // 3. Update Timeline Steps (0 to 4)
    for (let i = 0; i <= 4; i++) {
        const stepEl = document.getElementById(`timeline-step-${i}`);
        const markerEl = document.getElementById(`step-marker-${i}`);
        if (!stepEl || !markerEl) continue;

        // Reset classes
        stepEl.classList.remove("step-completed", "step-active");

        if (i < newIdx) {
            // Completed previous stage
            stepEl.classList.add("step-completed");
            markerEl.innerHTML = '<i class="fa-solid fa-check"></i>';
        } else if (i === newIdx) {
            // Current active stage
            stepEl.classList.add("step-completed", "step-active");
            if (i === 4) {
                // Resolved final stage
                markerEl.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
            } else {
                markerEl.innerHTML = '<span class="step-dot-active"></span>';
            }
        } else {
            // Future pending stage
            markerEl.innerHTML = `<span>${i + 1}</span>`;
        }
    }

    // 4. Update Timeline Connectors (0 to 3)
    for (let j = 0; j <= 3; j++) {
        const connectorEl = document.getElementById(`timeline-connector-${j}`);
        if (!connectorEl) continue;

        if (j < newIdx) {
            connectorEl.classList.add("connector-completed");
        } else {
            connectorEl.classList.remove("connector-completed");
        }
    }

    // 5. Highlight Live Sync Badge with flash pulse
    const syncBadge = document.getElementById("live-sync-badge");
    if (syncBadge) {
        syncBadge.style.transition = "all 0.3s ease";
        syncBadge.style.transform = "scale(1.15)";
        syncBadge.style.backgroundColor = "#10b981";
        syncBadge.style.color = "#ffffff";
        setTimeout(() => {
            syncBadge.style.transform = "scale(1)";
            syncBadge.style.backgroundColor = "";
            syncBadge.style.color = "";
        }, 800);
    }

    // 6. Trigger celebration / notification toast
    showToast(`⚡ Live Status Sync: Complaint is now marked as ${newStatus.toUpperCase()}!`, "success");
}

// =========================================================
// 4. Admin Dashboard (Map, Chart.js & AJAX Status Transition)
// =========================================================


let adminMap = null;
let categoryChartInstance = null;
let statusChartInstance = null;
let priorityChartInstance = null;

function initAdminDashboard() {
    initAdminClock();
    initAdminMap();
    initAdminCharts();
    initAdminTableFilters();
}

function initAdminClock() {
    const clockEl = document.getElementById("current-time");
    if (!clockEl) return;

    function update() {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + " | NMC Queue Live";
    }
    update();
    setInterval(update, 1000);
}

// Interactive Map for Admin with priority colored circle markers
function initAdminMap() {
    const mapEl = document.getElementById("admin-interactive-map");
    if (!mapEl) return;

    adminMap = L.map("admin-interactive-map", {
        center: [21.1458, 79.0882], // Nagpur center
        zoom: 12
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(adminMap);

    fetch("/api/map-data")
        .then(res => res.json())
        .then(data => {
            const bounds = [];
            data.complaints.forEach(item => {
                if (!item.lat || !item.lng) return;

                // Color code by priority/severity
                let color = "#10b981"; // Low (Green)
                if (item.severity === "CRITICAL" || item.severity === "HIGH" || item.priority >= 8) {
                    color = "#ef4444"; // High (Red)
                } else if (item.severity === "MEDIUM" || (item.priority >= 5 && item.priority <= 7)) {
                    color = "#f59e0b"; // Medium (Amber)
                }

                const circleMarker = L.circleMarker([item.lat, item.lng], {
                    radius: 9,
                    fillColor: color,
                    color: "#ffffff",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.85
                }).addTo(adminMap);

                circleMarker.bindPopup(`
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13px; min-width: 170px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                            <strong style="color: #059669; font-family: monospace;">${item.complaint_id}</strong>
                            <span style="font-size:11px; font-weight:700; color:${color};">${item.severity}</span>
                        </div>
                        <h4 style="margin: 2px 0 6px 0; font-size: 14px; font-weight:700;">${item.issue}</h4>
                        <div style="font-size:11.5px; color: #475569; margin-bottom: 6px;">
                            <i class="fa-solid fa-location-dot"></i> ${item.location}
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; padding-top:6px; border-top:1px solid #e2e8f0; font-size:11.5px;">
                            <span>Status: <strong>${item.status}</strong></span>
                            <a href="/track?id=${item.complaint_id}" style="color:#0284c7; font-weight:700; text-decoration:none;">Track &rarr;</a>
                        </div>
                    </div>
                `);

                bounds.push([item.lat, item.lng]);
            });

            if (bounds.length > 0) {
                adminMap.fitBounds(bounds, { padding: [30, 30] });
            }
        })
        .catch(err => console.error("Error loading map points:", err));
}

// Chart.js initialization
function initAdminCharts() {
    fetch("/api/analytics")
        .then(res => res.json())
        .then(data => {
            renderCategoryChart(data.categories);
            renderStatusChart(data.statuses);
            renderPriorityChart(data.priorities);
        })
        .catch(err => console.error("Error loading chart analytics:", err));
}

function renderCategoryChart(catData) {
    const ctx = document.getElementById("categoryChart");
    if (!ctx) return;

    if (categoryChartInstance) categoryChartInstance.destroy();

    const colors = ["#ef4444", "#f59e0b", "#0284c7", "#ca8a04", "#ea580c", "#475569", "#8b5cf6"];

    categoryChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: catData.labels,
            datasets: [{
                data: catData.data,
                backgroundColor: colors.slice(0, catData.labels.length),
                borderWidth: 2,
                borderColor: "#ffffff"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "right",
                    labels: {
                        boxWidth: 12,
                        font: { family: "'Plus Jakarta Sans', sans-serif", size: 11.5, weight: '600' }
                    }
                }
            },
            cutout: "68%"
        }
    });
}

function renderStatusChart(statusData) {
    const ctx = document.getElementById("statusChart");
    if (!ctx) return;

    if (statusChartInstance) statusChartInstance.destroy();

    const colors = ["#0284c7", "#0d9488", "#6366f1", "#d97706", "#10b981"];

    statusChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: statusData.labels,
            datasets: [{
                label: "Complaints",
                data: statusData.data,
                backgroundColor: colors,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0, font: { family: "'Plus Jakarta Sans', sans-serif" } },
                    grid: { color: "#f1f5f9" }
                },
                x: {
                    ticks: { font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 } },
                    grid: { display: false }
                }
            }
        }
    });
}

function renderPriorityChart(priData) {
    const ctx = document.getElementById("priorityChart");
    if (!ctx) return;

    if (priorityChartInstance) priorityChartInstance.destroy();

    priorityChartInstance = new Chart(ctx, {
        type: "pie",
        data: {
            labels: priData.labels,
            datasets: [{
                data: priData.data,
                backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                borderWidth: 2,
                borderColor: "#ffffff"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        boxWidth: 12,
                        font: { family: "'Plus Jakarta Sans', sans-serif", size: 11.5, weight: '600' }
                    }
                }
            }
        }
    });
}

// Real-time Status Update via AJAX
function updateComplaintStatus(complaintId, newStatus, selectElement) {
    fetch("/api/admin/update-status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ complaint_id: complaintId, status: newStatus })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(`Complaint ${complaintId} updated to ${newStatus}!`, "success");

            // Update select styling
            if (selectElement) {
                selectElement.className = "status-select status-select-" + newStatus.toLowerCase().replace(" ", "-");
                const row = selectElement.closest(".complaint-row");
                if (row) {
                    row.setAttribute("data-status", newStatus);
                }
            }

            // Dynamically refresh KPI values & charts
            refreshAnalyticsAndKPI();
        } else {
            showToast(data.error || "Failed to update status.", "error");
        }
    })
    .catch(err => {
        console.error("Status update error:", err);
        showToast("Server communication failed.", "error");
    });
}

// Refresh KPI and charts dynamically after status update
function refreshAnalyticsAndKPI() {
    fetch("/api/analytics")
        .then(res => res.json())
        .then(data => {
            renderCategoryChart(data.categories);
            renderStatusChart(data.statuses);
            renderPriorityChart(data.priorities);

            // Re-calculate Pending and Resolved counts from statuses
            const statuses = data.statuses;
            let resolved = 0;
            let total = 0;
            for (let i = 0; i < statuses.labels.length; i++) {
                total += statuses.data[i];
                if (statuses.labels[i] === "Resolved") {
                    resolved = statuses.data[i];
                }
            }
            const pending = total - resolved;

            const resValEl = document.getElementById("kpi-resolved-val");
            const penValEl = document.getElementById("kpi-pending-val");
            if (resValEl) resValEl.textContent = resolved;
            if (penValEl) penValEl.textContent = pending;
        });
}

// Table Filter & Search Engine
function initAdminTableFilters() {
    const searchInput = document.getElementById("admin-table-search");
    const filterStatus = document.getElementById("filter-status");
    const filterPriority = document.getElementById("filter-priority");
    const filterCategory = document.getElementById("filter-category");
    const rows = document.querySelectorAll(".complaint-row");
    const countBadge = document.getElementById("visible-count-badge");

    function applyFilters() {
        const query = (searchInput ? searchInput.value : "").trim().toLowerCase();
        const selStatus = filterStatus ? filterStatus.value : "ALL";
        const selPriority = filterPriority ? filterPriority.value : "ALL";
        const selCategory = filterCategory ? filterCategory.value : "ALL";

        let visibleCount = 0;

        rows.forEach(row => {
            const rowSearch = (row.getAttribute("data-search") || "").toLowerCase();
            const rowStatus = row.getAttribute("data-status") || "";
            const rowPriority = row.getAttribute("data-priority") || "";
            const rowIssue = row.getAttribute("data-issue") || "";

            const matchesQuery = !query || rowSearch.includes(query);
            const matchesStatus = selStatus === "ALL" || rowStatus.toLowerCase() === selStatus.toLowerCase();
            const matchesPriority = selPriority === "ALL" || rowPriority.toUpperCase() === selPriority.toUpperCase();
            const matchesCategory = selCategory === "ALL" || rowIssue.toLowerCase() === selCategory.toLowerCase();

            if (matchesQuery && matchesStatus && matchesPriority && matchesCategory) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        if (countBadge) {
            countBadge.textContent = `${visibleCount} of ${rows.length} Complaints Shown`;
        }
    }

    if (searchInput) searchInput.addEventListener("input", applyFilters);
    if (filterStatus) filterStatus.addEventListener("change", applyFilters);
    if (filterPriority) filterPriority.addEventListener("change", applyFilters);
    if (filterCategory) filterCategory.addEventListener("change", applyFilters);
}

// Photo Modal Functions
function openPhotoModal(imgSrc, complaintId, issueType) {
    const modal = document.getElementById("photo-modal");
    const modalImg = document.getElementById("modal-img");
    const modalId = document.getElementById("modal-id");
    const modalIssue = document.getElementById("modal-issue");

    if (modal && modalImg) {
        modalImg.src = imgSrc;
        if (modalId) modalId.textContent = complaintId;
        if (modalIssue) modalIssue.textContent = " • " + issueType;
        modal.classList.remove("hidden");
    }
}

function closePhotoModal() {
    const modal = document.getElementById("photo-modal");
    if (modal) {
        modal.classList.add("hidden");
    }
}
