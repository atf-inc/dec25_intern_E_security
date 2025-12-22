// ShadowGuard AI Extension - Background Service Worker (FIXED)

let config = {
    collectorUrl: 'http://localhost:8000/logs',
    userId: 'user@company.com',
    enabled: true,
    batchSize: 1,      // REAL-TIME: Send every log immediately
    batchInterval: 5000, // 5s fallback (handled via setTimeout if needed)
    sendOnNavigation: true
};

let logQueue = [];
let stats = { total: 0, sent: 0, failed: 0, queued: 0 };
let isSending = false; // Prevent concurrent sends
let saveTimeout = null; // Debounce storage writes
let recentHashes = new Map(); // hash -> timestamp (for deduplication)
const DEDUPE_WINDOWS_MS = 30000; // 30s dedupe window
let pendingLogs = new Map(); // requestId -> logEntry (to update with headers)

// Initialize on install
chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.set({ logQueue: [], stats: { total: 0, sent: 0, failed: 0, queued: 0 } });
    setupAlarm();
});

// Capture startup time to ignore session restore flood
const STARTUP_GRACE_PERIOD_MS = 3000;
let startupTime = Date.now();

// Load data on startup (Force clear queue for fresh start)
chrome.runtime.onStartup.addListener(() => {
    startupTime = Date.now();
    loadData(true);
    setupAlarm();
});

// Initial load
loadData();

async function loadData(clearQueue = false) {
    const result = await chrome.storage.sync.get(['config']);
    if (result.config) {
        config = { ...config, ...result.config };
    }

    if (clearQueue) {
        logQueue = [];
        stats = { total: 0, sent: 0, failed: 0, queued: 0 };
        await chrome.storage.local.set({ logQueue, stats });
        console.log('[ShadowGuard] Startup: Queue cleared');
    } else {
        const local = await chrome.storage.local.get(['logQueue', 'stats']);
        if (local.logQueue) logQueue = local.logQueue;
        if (local.stats) stats = local.stats;
    }

    updateBadge();
    console.log('[ShadowGuard] Loaded config:', config);
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

        // SKIP logs during startup grace period (prevents Session Restore spam)
        if (Date.now() - startupTime < STARTUP_GRACE_PERIOD_MS) {
            console.log('[ShadowGuard] Startup grace period - ignoring request:', details.url);
            return;
        }

        try {
            // Check if tab is active (reduce background tab noise)
            if (details.tabId !== -1) {
                chrome.tabs.get(details.tabId, (tab) => {
                    if (chrome.runtime.lastError || !tab) return;

                    // Only process active tabs OR tabs that are loading in foreground
                    if (!tab.active) {
                        // Optional: we can still log it but maybe mark it? 
                        // User requirement: "if one tab is opened only that tab" implies focus on active usage.
                        // We will skip inactive tabs for now to reduce noise.
                        return;
                    }

                    processRequest(details, tab);
                });
            } else {
                // Non-tab request (rare for main_frame), proceed
                processRequest(details, null);
            }

        } catch (error) {
            console.error('[ShadowGuard] Error processing request:', error);
        }
    },
    { urls: ["<all_urls>"] },
    ["requestBody"]
);

function processRequest(details, tab) {
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

        // If it's a POST/PUT, wait for headers if size is currently 0
        if ((details.method === 'POST' || details.method === 'PUT') && uploadSize === 0) {
            pendingLogs.set(details.requestId, logEntry);
            // We'll queue it later in onBeforeSendHeaders or onCompleted
            console.log(`[ShadowGuard] Pending size for: ${domain} (ID: ${details.requestId})`);
        } else {
            queueLog(logEntry);
        }

        // CHECK LOCAL RISK (Alerting)
        const riskCategory = checkLocalRisk(domain);
        if (riskCategory && details.tabId !== -1) {
            triggerAlertInTab(details.tabId, riskCategory);
        }

        // Debounced save
        saveData();
        updateBadge();

        // Send if batch size reached
        if (logQueue.length >= config.batchSize && !isSending) {
            sendBatch();
        }
    } catch (e) {
        console.error('[ShadowGuard] Error in processRequest:', e);
    }
}

// Capture Content-Length from headers (more reliable for size)
chrome.webRequest.onBeforeSendHeaders.addListener(
    (details) => {
        const pending = pendingLogs.get(details.requestId);
        if (pending) {
            const contentLengthHeader = details.requestHeaders.find(h => h.name.toLowerCase() === 'content-length');
            if (contentLengthHeader) {
                pending.upload_size_bytes = parseInt(contentLengthHeader.value, 10) || 0;
                console.log(`[ShadowGuard] Found Content-Length: ${pending.upload_size_bytes} for ${pending.domain}`);
            }
            // Now queue it
            queueLog(pending);
            pendingLogs.delete(details.requestId);
        }
    },
    { urls: ["<all_urls>"] },
    ["requestHeaders"]
);

// Cleanup pending logs that never got headers
chrome.webRequest.onCompleted.addListener(
    (details) => {
        const pending = pendingLogs.get(details.requestId);
        if (pending) {
            queueLog(pending);
            pendingLogs.delete(details.requestId);
        }
    },
    { urls: ["<all_urls>"] }
);

function queueLog(logEntry) {
    logQueue.push(logEntry);
    stats.total++;
    stats.queued = logQueue.length;
    console.log(`[ShadowGuard] Queued: ${logEntry.domain} (Size: ${logEntry.upload_size_bytes})`);

    // Auto-send if real-time (batchSize=1)
    if (logQueue.length >= config.batchSize && !isSending) {
        sendBatch();
    }
}

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
            console.error(`[ShadowGuard] ❌ Network error reaching ${config.collectorUrl}:`, error);
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

// ---------------- LOCAL RISK DETECTION (ALERTING) ----------------

const HIGH_RISK_PATTERNS = [
    // GenAI
    { regex: /chatgpt\.com|chat\.openai\.com|gemini\.google\.com|claude\.ai|perplexity\.ai|you\.com|poe\.com/i, category: "Generative AI Chatbot" },

    // Cloud Storage
    { regex: /dropbox\.com|drive\.google\.com|onedrive\.live\.com|box\.com|sync\.com|icedrive\.net|pcloud\.com/i, category: "Unapproved Cloud Storage" },

    // Messaging & Collaboration
    { regex: /web\.whatsapp\.com|signal\.org|slack\.com|trello\.com|asana\.com|notion\.so|monday\.com|airtable\.com|miro\.com/i, category: "Messaging & Collaboration" },

    // Coding Assistants
    { regex: /cursor\.sh|codeium\.com|tabnine\.com|github\.com|gitlab\.com|bitbucket\.org|blackbox\.ai|phind\.com|replit\.com/i, category: "Coding Assistant" },

    // File Transfer & Blacklist
    { regex: /wetransfer\.com|mega\.nz|anonfiles\.com|mediafire\.com|sendspace\.com|file\.io|gofile\.io|pixeldrain\.com|zippyshare\.com|rapidgator\.net|uploaded\.net|hotfile\.com|4shared\.com/i, category: "File Transfer / Blacklisted" },

    // Anon Communication
    { regex: /protonmail\.com|tutanota\.com|guerrillamail\.com|tempmail\.io|10minutemail\.com/i, category: "Anonymous Communication" },

    // Consumer SaaS
    { regex: /grammarly\.com|quillbot\.com|remove\.bg|smallpdf\.com|ilovepdf\.com/i, category: "Consumer SaaS Tool" },

    // Media Creation
    { regex: /midjourney\.com|stability\.ai|leonardo\.ai|firefly\.adobe\.com|canva\.com|figma\.com/i, category: "Media/Design Tool" }
];

function checkLocalRisk(domain) {
    for (const pattern of HIGH_RISK_PATTERNS) {
        if (pattern.regex.test(domain)) {
            return pattern.category;
        }
    }
    return null;
}

async function triggerAlertInTab(tabId, category) {
    try {
        await chrome.tabs.sendMessage(tabId, {
            action: "ALERT_RISK",
            category: category,
            message: "DO NOT UPLOAD ANY PERSONAL OR CONFIDENTIAL INFORMATION."
        });
        console.log(`[ShadowGuard] Alert triggered for tab ${tabId}: ${category}`);
    } catch (e) {
        // Tab might be closed or content script not ready
        // console.warn(`[ShadowGuard] Could not send alert to tab ${tabId}: ${e.message}`);
    }
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
                // Clear queue immediately when disabled
                logQueue = [];
                stats = { ...stats, queued: 0 };
                chrome.storage.local.set({ logQueue, stats });

                chrome.action.setBadgeText({ text: 'OFF' });
                chrome.action.setBadgeBackgroundColor({ color: '#6b7280' });
                console.log('[ShadowGuard] Disabled: Queue cleared');
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