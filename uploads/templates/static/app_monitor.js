// static/js/app_monitor.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("appScanForm");

    if (form) {
        form.addEventListener("submit", scanAppListing);
    }
});

async function scanAppListing(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const message = document.getElementById("appMessage");
    const button = form.querySelector('button[type="submit"]');

    const payload = {
        app_name: document.getElementById("appName").value.trim(),
        platform: document.getElementById("appPlatform").value,
        publisher: document.getElementById("appPublisher").value.trim(),
        app_url: document.getElementById("appUrl").value.trim(),
        description: document.getElementById("appDescription").value.trim()
    };

    if (!payload.app_name) {
        showAppResult(message, "Enter an app name first.", "danger");
        return;
    }

    button.disabled = true;
    button.textContent = "Analyzing…";

    try {
        const response = await fetch("/api/apps/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "App analysis failed.");
        }

        const detection = result.detection || result;
        const score = detection.risk_score ?? result.risk_score ?? "—";
        const level = detection.risk_level ?? result.risk_level ?? "Recorded";

        message.replaceChildren();
        message.className = "mt-3 alert alert-success";

        const heading = document.createElement("strong");
        heading.textContent = `Risk level: ${level}`;

        const paragraph = document.createElement("p");
        paragraph.textContent = `Risk score: ${score}/100`;

        const link = document.createElement("a");
        link.href = "/detections";
        link.className = "btn btn-sm btn-outline-success";
        link.textContent = "View detections";

        message.append(heading, paragraph, link);
    } catch (error) {
        showAppResult(message, error.message, "danger");
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-search"></i> Analyze App';
    }
}

function showAppResult(container, text, type) {
    container.className = `mt-3 alert alert-${type}`;
    container.textContent = text;
}