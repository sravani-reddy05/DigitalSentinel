// static/js/detections.js

document.addEventListener("DOMContentLoaded", () => {
    const applyButton = document.getElementById("applyFilters");
    const clearButton = document.getElementById("clearFilters");

    if (applyButton) {
        applyButton.addEventListener("click", loadDetections);
    }

    if (clearButton) {
        clearButton.addEventListener("click", () => {
            document.getElementById("filterPlatform").value = "";
            document.getElementById("filterStatus").value = "";
            loadDetections();
        });
    }

    loadDetections();
});

async function loadDetections() {
    const body = document.getElementById("detectionsBody");
    const message = document.getElementById("detectionsMessage");

    if (!body) return;

    body.replaceChildren();
    if (message) message.textContent = "Loading detections…";

    const params = new URLSearchParams();
    const platform = document.getElementById("filterPlatform")?.value;
    const status = document.getElementById("filterStatus")?.value;

    if (platform) params.set("platform", platform);
    if (status) params.set("status", status);

    try {
        const response = await fetch(`/api/detections?${params.toString()}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not load detections.");
        }

        const items = Array.isArray(data)
            ? data
            : data.detections || [];

        if (!items.length) {
            const row = body.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 7;
            cell.className = "text-center text-muted";
            cell.textContent = "No records found.";
            if (message) message.textContent = "";
            return;
        }

        items.forEach((item) => {
            const row = body.insertRow();

            addCell(row, item.target_name || "Unknown");
            addCell(row, item.platform || "—");
            addCell(row, `${item.risk_score ?? 0}/100`);

            const riskCell = row.insertCell();
            const badge = document.createElement("span");
            badge.className = riskClass(item.risk_level);
            badge.textContent = item.risk_level || "Unknown";
            riskCell.appendChild(badge);

            addCell(row, item.status || "Needs Review");
            addCell(row, item.created_at || "—");

            const actionCell = row.insertCell();
            const link = document.createElement("a");
            link.href = `/detection/${encodeURIComponent(item.id)}`;
            link.className = "btn btn-sm btn-outline-primary";
            link.textContent = "Review";
            actionCell.appendChild(link);
        });

        if (message) {
            message.textContent = `${items.length} record(s) displayed.`;
        }
    } catch (error) {
        if (message) message.textContent = error.message;

        const row = body.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 7;
        cell.className = "text-center text-danger";
        cell.textContent = "Could not load records. Check the Flask server.";
    }
}

function addCell(row, value) {
    const cell = row.insertCell();
    cell.textContent = value;
    return cell;
}

function riskClass(level) {
    switch (String(level || "").toLowerCase()) {
        case "critical": return "risk-high";
        case "high": return "risk-high";
        case "medium": return "risk-medium";
        default: return "risk-low";
    }
}
