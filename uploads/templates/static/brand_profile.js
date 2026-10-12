// static/js/brand_profile.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("brandForm");

    if (form) {
        form.addEventListener("submit", saveBrand);
    }

    loadCurrentBrand();
});

async function loadCurrentBrand() {
    const container = document.getElementById("currentBrand");
    if (!container) return;

    try {
        const response = await fetch("/api/brands/current");
        if (!response.ok) throw new Error("Could not load brand.");

        const brand = await response.json();
        container.replaceChildren();

        if (!brand || !brand.id) {
            container.textContent =
                "No brand registered yet. Use the form to add one.";
            return;
        }

        const heading = document.createElement("h2");
        heading.textContent = brand.brand_name || "Unnamed brand";

        const website = document.createElement("p");
        website.textContent =
            `Website: ${brand.official_website || "Not provided"}`;

        const description = document.createElement("p");
        description.textContent =
            brand.description || "No description provided.";

        const id = document.createElement("p");
        id.className = "text-muted small";
        id.textContent = `Brand ID: ${brand.id}`;

        container.append(heading, website, description, id);
    } catch (error) {
        container.textContent = error.message;
    }
}

async function saveBrand(event) {
    event.preventDefault();

    const message = document.getElementById("brandMessage");
    const form = event.currentTarget;

    const payload = {
        brand_name: document.getElementById("brandName").value.trim(),
        official_website: document.getElementById("brandWebsite").value.trim(),
        description: document.getElementById("brandDescription").value.trim()
    };

    message.textContent = "Saving brand…";

    try {
        const response = await fetch("/api/brands", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to save brand.");
        }

        message.className = "mt-3 text-success";
        message.textContent = "Brand saved successfully.";

        form.reset();
        await loadCurrentBrand();
    } catch (error) {
        message.className = "mt-3 text-danger";
        message.textContent = error.message;
    }
}