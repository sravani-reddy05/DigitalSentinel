// static/js/app.js

document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const menuToggle = document.getElementById("menuToggle");

    // Mobile sidebar
    if (sidebar && menuToggle) {
        menuToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });

        document.addEventListener("click", (event) => {
            if (
                window.innerWidth < 992 &&
                sidebar.classList.contains("open") &&
                !sidebar.contains(event.target) &&
                !menuToggle.contains(event.target)
            ) {
                sidebar.classList.remove("open");
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth >= 992) {
                sidebar.classList.remove("open");
            }
        });
    }

    // Highlight current sidebar link
    document.querySelectorAll(".sidebar-nav a").forEach((link) => {
        const linkPath = new URL(link.href, window.location.origin).pathname;
        const currentPath = window.location.pathname;

        if (linkPath === currentPath) {
            link.classList.add("active");
        }
    });

    // Homepage-only navigation transition. Native navigation remains the fallback.
    if (document.body.classList.contains("home-page") && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        document.addEventListener("click", (event) => {
            const link = event.target.closest("a[href]");
            if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || link.target || link.hasAttribute("download")) return;
            const destination = new URL(link.href, window.location.href);
            if (destination.origin !== window.location.origin || destination.pathname === window.location.pathname || link.dataset.noTransition === "true") return;
            event.preventDefault();
            document.body.classList.add("is-navigating");
            window.setTimeout(() => { window.location.href = destination.href; }, 150);
        });
    }
});

// Shared notification helper
window.showAlert = function (message, type = "info") {
    const alertBox = document.getElementById("globalAlert");

    if (!alertBox) {
        console.log(message);
        return;
    }

    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = message;
    alertBox.classList.remove("d-none");

    window.scrollTo({ top: 0, behavior: "smooth" });
};

// Safely convert a value to display text
window.displayValue = function (value, fallback = "—") {
    if (value === null || value === undefined || value === "") {
        return fallback;
    }

    return String(value);
};
