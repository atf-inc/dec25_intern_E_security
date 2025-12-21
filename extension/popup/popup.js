/* popup.js */

document.addEventListener('DOMContentLoaded', () => {
    updateUI();

    // Refresh every 2 seconds
    const intervalId = setInterval(updateUI, 2000);

    // Toggle monitoring
    document.getElementById('toggleBtn').addEventListener('click', () => {
        chrome.runtime.sendMessage({ action: 'getStats' }, (response) => {
            if (response && response.config) {
                const newConfig = { ...response.config, enabled: !response.config.enabled };
                chrome.storage.sync.set({ config: newConfig }, () => {
                    updateUI();
                });
            }
        });
    });

    // Send now
    document.getElementById('sendNowBtn').addEventListener('click', () => {
        const btn = document.getElementById('sendNowBtn');
        const originalText = btn.textContent;
        btn.textContent = '⌛ Sending...';
        btn.disabled = true;

        chrome.runtime.sendMessage({ action: 'sendNow' }, (response) => {
            setTimeout(() => {
                btn.textContent = originalText;
                btn.disabled = false;
                updateUI();
            }, 1000);
        });
    });

    // Open options
    document.getElementById('optionsBtn').addEventListener('click', () => {
        chrome.runtime.openOptionsPage();
    });

    // Manual refresh
    document.getElementById('refreshBtn').addEventListener('click', updateUI);

    // Initial load
    function updateUI() {
        chrome.runtime.sendMessage({ action: 'getStats' }, (response) => {
            if (response) {
                const { stats, config, queueLength } = response;

                // Update stats
                document.getElementById('totalLogs').textContent = stats.total;
                document.getElementById('sentLogs').textContent = stats.sent;
                document.getElementById('queuedLogs').textContent = queueLength;
                document.getElementById('failedLogs').textContent = stats.failed;

                // Update info
                document.getElementById('userEmail').textContent = config.userId || 'Not configured';
                document.getElementById('collectorUrl').textContent = config.collectorUrl || 'Not configured';

                // Update status
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const toggleIcon = document.getElementById('toggleIcon');
                const toggleText = document.getElementById('toggleText');
                const toggleBtn = document.getElementById('toggleBtn');

                if (config.enabled) {
                    statusDot.className = 'status-dot enabled';
                    statusText.textContent = 'Monitoring Active';
                    toggleIcon.textContent = '■';
                    toggleText.textContent = 'Disable';
                    toggleBtn.className = 'btn-primary danger';
                } else {
                    statusDot.className = 'status-dot disabled';
                    statusText.textContent = 'Monitoring Paused';
                    toggleIcon.textContent = '▶';
                    toggleText.textContent = 'Enable';
                    toggleBtn.className = 'btn-primary success';
                }
            }
        });
    }

    // Cleanup interval on popup close
    window.addEventListener('unload', () => {
        clearInterval(intervalId);
    });
});
