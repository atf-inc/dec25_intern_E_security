// ShadowGuard AI Extension - Background Service Worker (FIXED)

let config = {
    collectorUrl: 'http://localhost:8000/logs',
    userId: 'user@company.com',
    enabled: true,
    batchSize: 10,
    batchInterval: 60000,
    sendOnNavigation: true
};

let logQueue = [];
let stats = { total: 0, sent: 0, failed: 0, queued: 0 };
let isSending = false; // Prevent concurrent sends
let saveTimeout = null; // Debounce storage writes
let recentHashes = new Map(); // hash -> timestamp (for deduplication)
const DEDUPE_WINDOWS_MS = 30000; // 30s dedupe window

// Initialize on install
chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.set({ logQueue: [], stats: { total: 0, sent: 0, failed: 0, queued: 0 } });
    setupAlarm();
});

// Load data on startup ONCE
chrome.runtime.onStartup.addListener(() => {
    loadData();
    setupAlarm();
});

// Initial load
loadData();

async function loadData() {
    const result = await chrome.storage.sync.get(['config']);
    if (result.config) {
        config = { ...config, ...result.config };
    }

    const local = await chrome.storage.local.get(['logQueue', 'stats']);
    if (local.logQueue) logQueue = local.logQueue;
    if (local.stats) stats = local.stats;
    updateBadge();

    console.log('[ShadowGuard] Loaded config:', config);
    console.log('[ShadowGuard] Loaded queue size:', logQueue.length);
}

function setupAlarm() {
    chrome.alarms.create('batchSender', { periodInMinutes: 1 });
    chrome.alarms.create('heartbeat', { periodInMinutes: 0.5 }); // 30s heartbeat
}

// ✅ FIX: Debounced storage save
function saveData() {
    if (saveTimeout) clearTimeout(saveTimeout);

    saveTimeout = setTimeout(async () => {
        await chrome.storage.local.set({ logQueue, stats });
        console.log('[ShadowGuard] Saved queue:', logQueue.length);
    }, 500); // Wait 500ms for burst of requests
}

// ✅ FIX: Remove loadData() call - use in-memory state
chrome.webRequest.onBeforeRequest.addListener(
    (details) => {
        // Skip if disabled or internal
        if (!config.enabled) return;
        if (isInternalUrl(details.url)) return;
        if (details.initiator && details.initiator.includes('chrome-extension://')) return;

        // Filter for relevant request types to reduce noise:
        // - main_frame: actual sites visited
        // - xmlhttprequest/websocket: cloud app/AI interactions
        const relevantTypes = ['main_frame', 'xmlhttprequest', 'websocket'];
        if (!relevantTypes.includes(details.type)) return;

        try {
            const url = new URL(details.url);
            const domain = url.hostname;
            const path = url.pathname + url.search;

            let uploadSize = estimateUploadSize(details.requestBody || {});

            // Deduplication Check
            const hash = `${details.method}|${domain}|${path}|${uploadSize}`;
            const now = Date.now();
            if (recentHashes.has(hash) && (now - recentHashes.get(hash)) < DEDUPE_WINDOWS_MS) {
                return; // Recent duplicate, skip
            }
            recentHashes.set(hash, now);

            // Periodically clean cache (every 100 entries)
            if (recentHashes.size > 100) {
                for (let [h, ts] of recentHashes) {
                    if (now - ts > DEDUPE_WINDOWS_MS) recentHashes.delete(h);
                }
            }

            const logEntry = {
                ts: new Date().toISOString(),
                user_id: config.userId,
                domain: domain,
                url: path,
                method: details.method,
                upload_size_bytes: uploadSize,
                type: details.type // Added type for worker context
            };

            // Add to in-memory queue
            logQueue.push(logEntry);
            stats.total++;
            stats.queued = logQueue.length;

            console.log(`[ShadowGuard] Captured: ${domain}${path} (Queue: ${logQueue.length})`);

            // Debounced save
            saveData();
            updateBadge();

            // Send if batch size reached
            if (logQueue.length >= config.batchSize && !isSending) {
                console.log('[ShadowGuard] Batch size reached, sending...');
                sendBatch();
            }
        } catch (error) {
            console.error('[ShadowGuard] Error processing request:', error);
        }
    },
    { urls: ["<all_urls>"] },
    ["requestBody"]
);

function isInternalUrl(url) {
    const ignoredProtocols = ['chrome://', 'chrome-extension://', 'about:', 'data:', 'blob:'];
    return ignoredProtocols.some(protocol => url.startsWith(protocol));
}

function estimateUploadSize(requestBody) {
    let size = 0;

    if (requestBody.raw) {
        size = requestBody.raw.reduce((sum, part) => {
            return sum + (part.bytes ? part.bytes.byteLength : 0);
        }, 0);
    } else if (requestBody.formData) {
        size = JSON.stringify(requestBody.formData).length;
    }

    return size;
}

// Alarm handler
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'batchSender') {
        if (logQueue.length > 0 && !isSending) {
            console.log('[ShadowGuard] Alarm triggered, sending batch...');
            sendBatch();
        }
    } else if (alarm.name === 'heartbeat') {
        sendHeartbeat();
    }
});

async function sendHeartbeat() {
    console.log('[ShadowGuard] Sending heartbeat...');
    const heartbeat = {
        ts: new Date().toISOString(),
        user_id: config.userId,
        type: 'heartbeat',
        stats: stats
    };
    try {
        await fetch(config.collectorUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(heartbeat)
        });
    } catch (e) {
        console.warn('[ShadowGuard] Heartbeat failed:', e.message);
    }
}

// ✅ FIX: Proper async handling + mutex
async function sendBatch() {
    if (isSending) {
        console.log('[ShadowGuard] Already sending, skipping...');
        return;
    }

    if (logQueue.length === 0) return;

    isSending = true;
    const toSend = logQueue.splice(0, Math.min(config.batchSize, logQueue.length));
    stats.queued = logQueue.length;

    console.log(`[ShadowGuard] Sending ${toSend.length} logs...`);

    // Send all logs in parallel (faster)
    const sendPromises = toSend.map(async (log) => {
        try {
            const response = await fetch(config.collectorUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(log)
            });

            if (response.ok) {
                stats.sent++;
                console.log(`[ShadowGuard] ✅ Sent: ${log.domain}`);
                return { success: true };
            } else {
                console.error(`[ShadowGuard] ❌ Server error (${response.status})`);
                stats.failed++;
                return { success: false, log };
            }
        } catch (error) {
            console.error('[ShadowGuard] ❌ Network error:', error.message);
            stats.failed++;
            return { success: false, log };
        }
    });

    const results = await Promise.all(sendPromises);

    // Re-queue failed logs
    const failedLogs = results.filter(r => !r.success).map(r => r.log);
    if (failedLogs.length > 0 && logQueue.length < 1000) {
        logQueue.push(...failedLogs);
        console.log(`[ShadowGuard] Re-queued ${failedLogs.length} failed logs`);
    }

    stats.queued = logQueue.length;
    await chrome.storage.local.set({ logQueue, stats });
    updateBadge();

    isSending = false;
}

function updateBadge() {
    const count = stats.queued;

    if (count > 0) {
        chrome.action.setBadgeText({ text: count.toString() });
        chrome.action.setBadgeBackgroundColor({ color: '#7c3aed' });
    } else {
        chrome.action.setBadgeText({ text: '' });
    }

    chrome.action.setTitle({
        title: `ShadowGuard AI - ${stats.total} logs captured, ${stats.sent} sent`
    });
}

// Listen for config changes
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (changes.config && namespace === 'sync') {
        const oldEnabled = config.enabled;
        config = { ...config, ...changes.config.newValue };

        console.log('[ShadowGuard] Configuration updated:', config);

        if (oldEnabled !== config.enabled) {
            if (config.enabled) {
                updateBadge();
            } else {
                chrome.action.setBadgeText({ text: 'OFF' });
                chrome.action.setBadgeBackgroundColor({ color: '#6b7280' });
            }
        }
    }
});

// Send remaining logs on suspend
chrome.runtime.onSuspend.addListener(() => {
    if (logQueue.length > 0) {
        console.log('[ShadowGuard] Extension suspending, sending remaining logs');
        sendBatch();
    }
});

// Message handler
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getStats') {
        sendResponse({
            stats: stats,
            config: config,
            queueLength: logQueue.length
        });
    } else if (request.action === 'sendNow') {
        sendBatch().then(() => {
            sendResponse({ success: true });
        });
        return true; // Keep channel open
    } else if (request.action === 'clearStats') {
        stats = { total: 0, sent: 0, failed: 0, queued: logQueue.length };
        chrome.storage.local.set({ stats });
        updateBadge();
        sendResponse({ success: true });
    }
    return true;
});

console.log('[ShadowGuard] Background service worker started');