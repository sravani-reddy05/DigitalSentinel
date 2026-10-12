// static/js/social_monitor.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("socialScanForm");

    if (form) {
        form.addEventListener("submit", scanSocialProfile);
    }
});

async function scanSocialProfile(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const message = document.getElementById("socialMessage");
    const button = form.querySelector('button[type="submit"]');

    const payload = {
        username: document.getElementById("socialUsername").value.trim(),
        platform: document.getElementById("socialPlatform").value,
        profile_url: document.getElementById("socialUrl").value.trim(),
        description: document.getElementById("socialDescription").value.trim()
    };

    if (!payload.username) {
        showResult(message, "Enter a username first.", "danger");
        return;
    }

    button.disabled = true;
    button.textContent = "Analyzing…";

    try {
        const response = await fetch("/api/social/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Social profile analysis failed.");
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
        showResult(message, error.message, "danger");
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-search"></i> Analyze Profile';
    }
}

function showResult(container, text, type) {
    container.className = `mt-3 alert alert-${type}`;
    container.textContent = text;
}