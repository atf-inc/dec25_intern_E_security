# ShadowGuard AI - Browser extension

A cross-browser extension (Chrome, Edge, Firefox) designed for passive monitoring of browsing activity for Shadow AI/IT detection.

## 🚀 Features

- **Passive Monitoring**: Captures domain, URL path, HTTP method, and upload size metadata.
- **Privacy First**: Does NOT capture page content, passwords, or personal form data.
- **High Performance**:
    - **In-Memory Capture**: Minimal impact on browsing speed.
    - **Parallel Processing**: Logs are sent to the collector in parallel for high throughput.
    - **Persistent Queue**: Logs are cached in `chrome.storage.local` to survive browser restarts or background process suspension (Manifest V3).
- **Batching & Sync**: Automatically groups logs and syncs them periodically via Chrome Alarms.
- **Stats Dashboard**: Modern dark-mode popup to view captured/sent log statistics.

## 🛠️ Installation (Development)

1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** in the top-right corner.
3. Click **Load unpacked**.
4. Select the `extension` folder from this project.
5. (Optional) Pin the extension to your toolbar for easy access to the dashboard.

## ⚙️ Configuration

Click the extension icon and select **Settings** to configure:
- **User ID**: Your corporate email (used for log attribution).
- **Collector URL**: The endpoint of your ShadowGuard Collector (e.g., `http://localhost:8000/logs`).
- **Batch Size**: Number of logs to group before sending (Default: 10).
- **Interval**: How often to sync remaining logs (Default: 1 minute).

## 📄 Technical implementation

- **Manifest V3**: Compliant with the latest browser extension standards.
- **Service Worker**: Uses a background service worker to monitor `webRequest` events.
- **Storage API**: Uses `chrome.storage.sync` for configuration and `chrome.storage.local` for the log queue.
- **Alarms API**: Uses `chrome.alarms` for reliable periodic syncing, overcoming Service Worker suspension.

---
*Part of the ShadowGuard AI Security Suite.*
