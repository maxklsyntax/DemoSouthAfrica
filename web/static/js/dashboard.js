/**
 * Dashboard auto-refresh — polls API endpoints every 3 seconds.
 */

const REFRESH_INTERVAL = 3000;
const CAMERA_REFRESH_INTERVAL = 1000;

async function fetchJson(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function setStatus(id, ok, label) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = label || (ok ? "Yes" : "No");
    el.className = "status-indicator " + (ok ? "ok" : "error");
}

function formatTimestamp(ts) {
    if (!ts) return "--";
    try {
        const d = new Date(ts);
        return d.toLocaleString();
    } catch {
        return ts;
    }
}

function summarizeData(data) {
    if (!data) return "--";
    if (Array.isArray(data)) {
        return data
            .map(p => `${p.parameterName}: ${p.parameterValue}`)
            .join(", ");
    }
    if (data.parameterValues) {
        return data.parameterValues
            .map(p => `${p.name}: ${p.value}`)
            .join(", ");
    }
    if (data.alertType) {
        return `${data.alertType} (${data.severity})`;
    }
    return JSON.stringify(data).substring(0, 80);
}

// --- Camera preview ---

function refreshCamera() {
    const img = document.getElementById("camera-img");
    if (img) {
        img.src = "/api/camera/snapshot?" + Date.now();
    }
}

async function loadCameraList() {
    const data = await fetchJson("/api/camera/list");
    const select = document.getElementById("camera-select");
    if (!data || !select) return;

    select.innerHTML = "";

    if (data.cameras.length === 0) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "No cameras found";
        select.appendChild(opt);
        return;
    }

    data.cameras.forEach(cam => {
        const opt = document.createElement("option");
        opt.value = cam.index;
        opt.textContent = `${cam.name} — ${cam.resolution}`;
        if (cam.index === data.active) {
            opt.selected = true;
        }
        select.appendChild(opt);
    });
}

async function switchCamera(index) {
    if (index === "") return;

    const select = document.getElementById("camera-select");
    if (select) select.disabled = true;

    try {
        const res = await fetch("/api/camera/select", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ index: parseInt(index) }),
        });
        const data = await res.json();
        if (!data.success) {
            console.error("Failed to switch camera");
        }
    } catch (e) {
        console.error("Camera switch error:", e);
    } finally {
        if (select) select.disabled = false;
    }
}

async function checkLabel() {
    const btn = document.getElementById("btn-check-label");
    const status = document.getElementById("check-status");
    btn.disabled = true;
    btn.textContent = "Checking...";
    if (status) status.textContent = "";

    try {
        const res = await fetch("/api/check/label", { method: "POST" });
        const data = await res.json();
        if (data.error) {
            btn.textContent = "Error";
            if (status) status.textContent = data.error;
        } else {
            const label = data.label_present ? "YES" : "NO";
            const sent = data.sap && data.sap.success ? " > SAP OK" : " > SAP Failed";
            if (status) status.textContent = "Label: " + label + sent;
            btn.textContent = data.label_present ? "Label: YES" : "Label: NO";
        }
        refreshAll();
        setTimeout(() => { btn.textContent = "Check Label"; btn.disabled = false; if (status) status.textContent = ""; }, 3000);
    } catch (e) {
        btn.textContent = "Error";
        setTimeout(() => { btn.textContent = "Check Label"; btn.disabled = false; }, 2000);
    }
}

async function checkWeight() {
    const btn = document.getElementById("btn-check-weight");
    const status = document.getElementById("check-status");
    btn.disabled = true;
    btn.textContent = "Checking...";
    if (status) status.textContent = "";

    try {
        const res = await fetch("/api/check/weight", { method: "POST" });
        const data = await res.json();
        if (data.error) {
            btn.textContent = "Error";
            if (status) status.textContent = data.error;
        } else {
            const sent = data.sap && data.sap.success ? " > SAP OK" : " > SAP Failed";
            if (status) status.textContent = "Weight: " + data.weight + "g" + sent;
            btn.textContent = data.weight + "g";
        }
        refreshAll();
        setTimeout(() => { btn.textContent = "Check Weight"; btn.disabled = false; if (status) status.textContent = ""; }, 3000);
    } catch (e) {
        btn.textContent = "Error";
        setTimeout(() => { btn.textContent = "Check Weight"; btn.disabled = false; }, 2000);
    }
}

// --- Data refresh functions ---

async function refreshScale() {
    const data = await fetchJson("/api/scale");
    if (!data) return;

    setStatus("scale-connected", data.connected);
    setText("scale-weight", data.current_weight != null ? data.current_weight + " g" : "-- g");
    setText("scale-tare", data.tare_weight != null ? data.tare_weight + " g" : "-- g");
}

async function refreshInspection() {
    const data = await fetchJson("/api/inspection/latest");
    if (!data) return;

    const resultEl = document.getElementById("inspection-result");
    if (resultEl && data.label_present != null) {
        const ok = data.label_present && data.weight_ok !== false;
        resultEl.textContent = ok ? "GOOD" : "BAD";
        resultEl.className = "result-badge " + (ok ? "good" : "bad");
    }

    setText("inspection-weight", data.weight != null ? data.weight + " g" : "-- g");
    setText("inspection-label", data.label_present != null ? (data.label_present ? "Yes" : "No") : "--");
    setText("inspection-contamination", data.contamination_detected != null ? (data.contamination_detected ? "Yes" : "No") : "--");
}

async function refreshSapDm() {
    const data = await fetchJson("/api/sap/dm/status");
    if (!data) return;

    setStatus("sap-dm-success", data.success, data.success ? "Success" : data.timestamp ? "Failed" : "--");
    setText("sap-dm-timestamp", formatTimestamp(data.timestamp));
    setText("sap-dm-data", summarizeData(data.data));
}


async function refreshNetwork() {
    const data = await fetchJson("/api/network");
    if (!data) return;

    setStatus("network-wifi", data.connected);
    setText("network-ssid", data.ssid || "--");
    setText("network-ip", data.ip || "--");
    setStatus("network-internet", data.internet);

    const footer = document.getElementById("connection-status");
    if (footer) {
        footer.textContent = data.internet ? "Online" : "Offline";
        footer.className = "status-indicator " + (data.internet ? "ok" : "error");
    }
}

async function refreshAll() {
    await Promise.all([
        refreshScale(),
        refreshInspection(),
        refreshSapDm(),
        refreshNetwork(),
    ]);
}

// Initial load + periodic refresh
refreshAll();
refreshCamera();
loadCameraList();
setInterval(refreshAll, REFRESH_INTERVAL);
setInterval(refreshCamera, CAMERA_REFRESH_INTERVAL);
