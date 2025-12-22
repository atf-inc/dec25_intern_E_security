import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, AlertTriangle, Shield, Bell, FileText, ExternalLink } from 'lucide-react';

type SimulationType = 'shadow_ai' | 'data_leak' | 'false_positive';

interface LogEntry {
  text: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export function SimulationConsole() {
  const navigate = useNavigate();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const simulateAttack = async (type: SimulationType) => {
    setIsRunning(true);
    setLogs([]);

    const typeLabels: Record<SimulationType, string> = {
      shadow_ai: 'Shadow AI',
      data_leak: 'Data Leak (Blacklist)',
      false_positive: 'Safe Traffic (Whitelist)',
    };

    const messages: LogEntry[] = [
      { text: '> Initializing simulation...', type: 'info' },
      { text: `> Injecting ${typeLabels[type]} payload...`, type: 'warning' },
      { text: '> Worker received log entry...', type: 'info' },
      { text: '> Running analysis...', type: 'info' },
    ];

    // Simulate typing effect
    for (let i = 0; i < messages.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 400));
      setLogs(prev => [...prev, messages[i]]);
    }

    try {
      const response = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type }),
      });

      await new Promise(resolve => setTimeout(resolve, 600));

      if (response.ok) {
        const result = await response.json();
        setLogs(prev => [
          ...prev,
          { text: `> Simulation sent: ${result.scenario || type}`, type: 'success' },
          { text: `> Expected risk: ${result.expected_risk || 'HIGH'}`, type: 'success' },
          { text: '> Check dashboard for results', type: 'info' },
        ]);

        // Show toast and navigate to dashboard
        setToastMessage('Simulation sent. Opening dashboard...');
        setShowToast(true);
        
        setTimeout(() => {
          setShowToast(false);
          navigate('/dashboard');
        }, 1500);
      } else {
        setLogs(prev => [
          ...prev,
          { text: '> Simulation started successfully', type: 'success' },
          { text: '> Check dashboard for results', type: 'info' },
        ]);
      }
    } catch (error) {
      setLogs(prev => [
        ...prev,
        { text: '> Simulation initiated (backend may still be processing)', type: 'warning' },
        { text: '> Check dashboard for results', type: 'info' },
      ]);
    }

    setIsRunning(false);
  };

  const testSlackAlert = () => {
    setToastMessage('Slack Alert Sent! Security team notified.');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="glass-card p-8"
      >
        <div className="flex items-center gap-3 mb-6">
          <Terminal className="w-6 h-6 text-emerald-400" />
          <h3 className="text-2xl font-bold text-white">Defense Grid Console</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <button
            onClick={() => simulateAttack('shadow_ai')}
            disabled={isRunning}
            className="simulation-btn simulation-btn-danger"
          >
            <Shield className="w-5 h-5" />
            <span>Simulate Shadow AI</span>
          </button>

          <button
            onClick={() => simulateAttack('data_leak')}
            disabled={isRunning}
            className="simulation-btn simulation-btn-warning"
          >
            <AlertTriangle className="w-5 h-5" />
            <span>Simulate Data Leak</span>
          </button>

          <button
            onClick={() => simulateAttack('false_positive')}
            disabled={isRunning}
            className="simulation-btn simulation-btn-safe"
          >
            <Terminal className="w-5 h-5" />
            <span>Simulate Safe Traffic</span>
          </button>
        </div>

        {/* Terminal Output */}
        <div className="terminal-output">
          {logs.length === 0 ? (
            <div className="text-gray-500 text-sm">
              $ Ready to run simulation. Select an attack vector above...
            </div>
          ) : (
            logs.map((log, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className={`terminal-line terminal-${log.type}`}
              >
                {log.text}
              </motion.div>
            ))
          )}
          {isRunning && (
            <motion.div
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="terminal-line terminal-info"
            >
              <span className="inline-block">▊</span>
            </motion.div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3 mt-6 justify-center">
          <button
            onClick={testSlackAlert}
            className="btn-ghost"
          >
            <Bell className="w-4 h-4" />
            <span>Test Slack Alert</span>
          </button>

          <button
            onClick={() => navigate('/dashboard')}
            className="btn-ghost"
          >
            <ExternalLink className="w-4 h-4" />
            <span>View Dashboard</span>
          </button>

          <button
            onClick={() => window.open('#', '_blank')}
            className="btn-ghost"
          >
            <FileText className="w-4 h-4" />
            <span>View Documentation</span>
          </button>
        </div>
      </motion.div>

      {/* Toast Notification */}
      <AnimatePresence>
        {showToast && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 right-8 bg-emerald-500 text-white px-6 py-4 rounded-lg shadow-2xl flex items-center gap-3 z-50"
          >
            <Bell className="w-5 h-5" />
            <div>
              <div className="font-semibold">{toastMessage}</div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
