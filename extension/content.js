// ShadowGuard AI - Content Script
// Injected into pages to display alerts

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "ALERT_RISK") {
        showWarningBanner(request.category, request.message);
    }
});

function showWarningBanner(category, message) {
    // 1. Check if the user has already dismissed the alert for this domain (session-based)
    try {
        if (sessionStorage.getItem("shadowguard-alert-dismissed") === "true") {
            return;
        }
    } catch (e) {
        // Fallback if interactions with storage are blocked
    }

    // Prevent duplicate banners
    if (document.getElementById("shadowguard-alert-banner")) return;

    const banner = document.createElement("div");
    banner.id = "shadowguard-alert-banner";
    banner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #ef4444; /* Red-500 */
        color: white;
        text-align: center;
        padding: 12px;
        font-family: system-ui, -apple-system, sans-serif;
        font-weight: bold;
        z-index: 2147483647; /* Max z-index */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
    `;

    const icon = document.createElement("span");
    icon.textContent = "⚠️";
    icon.style.fontSize = "1.2em";

    const text = document.createElement("span");
    text.innerText = `SHADOWGUARD ALERT: This is a ${category} site. ${message}`;

    const closeBtn = document.createElement("button");
    closeBtn.textContent = "✖";
    closeBtn.title = "Dismiss alert for this session";
    closeBtn.style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 1.2em;
        cursor: pointer;
        padding: 0 8px;
        margin-left: 20px;
    `;

    closeBtn.onclick = () => {
        banner.remove();
        // Mark as dismissed for this session (per origin)
        try {
            sessionStorage.setItem("shadowguard-alert-dismissed", "true");
        } catch (e) { console.error(e); }
    };

    banner.appendChild(icon);
    banner.appendChild(text);
    banner.appendChild(closeBtn);

    document.body.prepend(banner);
}
