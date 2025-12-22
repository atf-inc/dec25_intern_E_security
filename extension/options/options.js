/* options.js */

// Default configuration
const DEFAULT_CONFIG = {
    collectorUrl: 'http://localhost:8000/logs',
    userId: '',
    enabled: true,
    batchSize: 10,
    batchInterval: 60,
    sendOnNavigation: true
};

// Load settings
document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.sync.get(['config'], (result) => {
        const config = result.config || DEFAULT_CONFIG;

        document.getElementById('userId').value = config.userId || '';
        document.getElementById('collectorUrl').value = config.collectorUrl || 'http://localhost:8000/logs';
        document.getElementById('batchSize').value = config.batchSize || 10;
        document.getElementById('batchInterval').value = config.batchInterval || 60;
    });
});

// Save settings
document.getElementById('saveBtn').addEventListener('click', () => {
    const userId = document.getElementById('userId').value.trim();
    const collectorUrl = document.getElementById('collectorUrl').value.trim();
    const batchSize = parseInt(document.getElementById('batchSize').value);
    const batchInterval = parseInt(document.getElementById('batchInterval').value);

    if (!userId || !collectorUrl) {
        alert('Please provide both email and collector URL.');
        return;
    }

    const config = {
        userId,
        collectorUrl,
        batchSize,
        batchInterval,
        enabled: true,
        sendOnNavigation: true
    };

    chrome.storage.sync.set({ config }, () => {
        const status = document.getElementById('status');
        status.className = 'status success';

        setTimeout(() => {
            status.className = 'status';
        }, 3000);
    });
});
