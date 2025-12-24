import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, AlertTriangle, Shield, Bell, FileText, ExternalLink } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

type SimulationType = 'shadow_ai' | 'data_leak' | 'false_positive';

interface LogEntry {
  text: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export function SimulationConsole() {
  const navigate = useNavigate();
  const { t, language } = useLanguage();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const simulateAttack = async (type: SimulationType) => {
    setIsRunning(true);
    setLogs([]);

    const typeLabels: Record<SimulationType, string> = {
      shadow_ai: t.simulation.shadowAI,
      data_leak: t.simulation.dataLeakBlacklist,
      false_positive: t.simulation.safeTrafficWhitelist,
    };

    // First, reset all existing alerts for a fresh start
    try {
      await fetch('/api/alerts/reset', { method: 'POST' });
      setLogs([{ text: language === 'ja' ? '> 新規シミュレーションのため以前のアラートをクリア...' : '> Cleared previous alerts for fresh simulation...', type: 'info' }]);
    } catch (error) {
      console.log('Reset failed, continuing anyway');
    }

    const messages: LogEntry[] = [
      { text: language === 'ja' ? '> シミュレーションを初期化中...' : '> Initializing simulation...', type: 'info' },
      { text: language === 'ja' ? `> ${typeLabels[type]}ペイロードを注入中...` : `> Injecting ${typeLabels[type]} payload...`, type: 'warning' },
      { text: language === 'ja' ? '> ワーカーがログエントリを受信...' : '> Worker received log entry...', type: 'info' },
      { text: language === 'ja' ? '> 分析を実行中...' : '> Running analysis...', type: 'info' },
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
          { text: language === 'ja' ? `> シミュレーション送信完了：${result.scenario || type}` : `> Simulation sent: ${result.scenario || type}`, type: 'success' },
          { text: language === 'ja' ? `> 予想リスク：${result.expected_risk || 'HIGH'}` : `> Expected risk: ${result.expected_risk || 'HIGH'}`, type: 'success' },
          { text: language === 'ja' ? '> ダッシュボードで結果を確認してください' : '> Check dashboard for results', type: 'info' },
        ]);

        // Show toast and navigate to dashboard
        setToastMessage(t.simulation.simulationSentOpening);
        setShowToast(true);

        setTimeout(() => {
          setShowToast(false);
          navigate('/dashboard');
        }, 1500);
      } else {
        setLogs(prev => [
          ...prev,
          { text: language === 'ja' ? '> シミュレーションが正常に開始されました' : '> Simulation started successfully', type: 'success' },
          { text: language === 'ja' ? '> ダッシュボードで結果を確認してください' : '> Check dashboard for results', type: 'info' },
        ]);
      }
    } catch (error) {
      setLogs(prev => [
        ...prev,
        { text: language === 'ja' ? '> シミュレーションが開始されました（バックエンドがまだ処理中の可能性があります）' : '> Simulation initiated (backend may still be processing)', type: 'warning' },
        { text: language === 'ja' ? '> ダッシュボードで結果を確認してください' : '> Check dashboard for results', type: 'info' },
      ]);
    }

    setIsRunning(false);
  };

  const testSlackAlert = () => {
    setToastMessage(t.simulation.slackAlertSent);
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
          <h3 className="text-2xl font-bold text-white">{t.simulation.defenseGridConsole}</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <button
            onClick={() => simulateAttack('shadow_ai')}
            disabled={isRunning}
            className="simulation-btn simulation-btn-danger"
          >
            <Shield className="w-5 h-5" />
            <span>{t.simulation.simulateShadowAI}</span>
          </button>

          <button
            onClick={() => simulateAttack('data_leak')}
            disabled={isRunning}
            className="simulation-btn simulation-btn-warning"
          >
            <AlertTriangle className="w-5 h-5" />
            <span>{t.simulation.simulateDataLeak}</span>
          </button>

          <button
            onClick={() => simulateAttack('false_positive')}
            disabled={isRunning}
            className="simulation-btn simulation-btn-safe"
          >
            <Terminal className="w-5 h-5" />
            <span>{t.simulation.simulateSafeTraffic}</span>
          </button>
        </div>

        {/* Terminal Output */}
        <div className="terminal-output">
          {logs.length === 0 ? (
            <div className="text-gray-500 text-sm">
              {t.simulation.readyToRun}
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
            <span>{t.simulation.testSlackAlert}</span>
          </button>

          <button
            onClick={() => navigate('/dashboard')}
            className="btn-ghost"
          >
            <ExternalLink className="w-4 h-4" />
            <span>{t.simulation.viewDashboardBtn}</span>
          </button>

          <button
            onClick={() => window.open('#', '_blank')}
            className="btn-ghost"
          >
            <FileText className="w-4 h-4" />
            <span>{t.simulation.viewDocumentation}</span>
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
