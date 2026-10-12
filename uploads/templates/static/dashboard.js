// static/js/dashboard.js

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});

async function loadDashboard() {
    try {
        const [statsResponse, recentResponse] = await Promise.all([
            fetch("/api/dashboard/stats"),
            fetch("/api/dashboard/recent")
        ]);

        if (!statsResponse.ok || !recentResponse.ok) {
            throw new Error("Could not retrieve dashboard data.");
        }

        const stats = await statsResponse.json();
        const recentData = await recentResponse.json();

        setText("totalDetections",
            stats.total_detections ?? stats.total ?? 0);

        setText("highDetections",
            stats.high_risk ?? stats.high ?? 0);

        setText("reviewDetections",
            stats.needs_review ?? stats.review ?? 0);

        const detections = Array.isArray(recentData)
            ? recentData
            : recentData.detections || recentData.recent || [];

        renderRecentDetections(detections);
    } catch (error) {
        console.error("Dashboard error:", error);

        const body = document.getElementById("recentDetections");
        if (body) {
            body.replaceChildren();
            const row = body.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 5;
            cell.textContent = "Could not load dashboard data. Check the Flask server.";
            cell.className = "text-center text-danger";
        }
    }
}

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}

function renderRecentDetections(items) {
    const tbody = document.getElementById("recentDetections");
    if (!tbody) return;

    tbody.replaceChildren();

    if (!items.length) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 5;
        cell.textContent = "No detections yet. Start a scan to create a record.";
        cell.className = "text-center text-muted";
        return;
    }

    items.forEach((item) => {
        const row = tbody.insertRow();

        const target = row.insertCell();
        const platform = row.insertCell();
        const risk = row.insertCell();
        const status = row.insertCell();
        const action = row.insertCell();

        target.textContent = item.target_name || "Unknown";
        platform.textContent = item.platform || "—";

        const riskBadge = document.createElement("span");
        riskBadge.textContent =
            `${item.risk_level || "Unknown"} (${item.risk_score ?? 0})`;
        riskBadge.className = getRiskClass(item.risk_level);
        risk.appendChild(riskBadge);

        status.textContent = item.status || "Needs Review";

        const link = document.createElement("a");
        link.href = `/detection/${encodeURIComponent(item.id)}`;
        link.className = "btn btn-sm btn-light";
        link.textContent = "View";
        action.appendChild(link);
    });
}

function getRiskClass(level) {
        const normalized = String(level || "").toLowerCase();

    if (normalized === "critical") return "risk-high";
    if (normalized === "high") return "risk-high";
    if (normalized === "medium") return "risk-medium";

    return "risk-low";
}
