import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield,
    AlertTriangle,
    Activity,
    Users,
    Globe,
    Clock,
    X,
    Eye,
    CheckCircle,
    ArrowLeft,
    FileText
} from 'lucide-react';
import { LanguageToggle } from './LanguageToggle';
import { useLanguage } from '../contexts/LanguageContext';

interface Alert {
    id: string;
    risk_score: number;
    user: string;
    domain: string;
    category: string;
    timestamp: string;
    status?: string;
    ai_message?: string;
    url?: string;
    method?: string;
    upload_size_bytes?: number;
}

interface Stats {
    total_alerts: number;
    high_risk: number;
    medium_risk: number;
    low_risk: number;
    unique_users: number;
    avg_risk_score: number;
}

export const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const { t, language } = useLanguage();
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [stats, setStats] = useState<Stats | null>(null);
    const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
    const [updatingStatus, setUpdatingStatus] = useState(false);
    const hasAutoReset = useRef(false);

    // Fetch data on mount and poll every 5 seconds
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [alertsRes, statsRes] = await Promise.all([
                    fetch('/api/alerts?limit=50'),
                    fetch('/api/stats')
                ]);

                if (alertsRes.ok) {
                    const alertsData = await alertsRes.json();
                    setAlerts(alertsData.alerts || []);
                }

                if (statsRes.ok) {
                    const statsData = await statsRes.json();
                    setStats(statsData);
                }

                setError(null);
            } catch (err) {
                console.error('Error fetching data:', err);
                setError(err instanceof Error ? err.message : 'Failed to fetch data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    // Auto-reset when high risk > 100 or total alerts > 500
    useEffect(() => {
        if (stats && !hasAutoReset.current) {
            const highRisk = stats.high_risk || 0;
            const total = stats.total_alerts || 0;

            if (highRisk > 100 || total > 500) {
                console.log(`🔄 Auto-reset triggered: High Risk=${highRisk}, Total=${total}`);
                hasAutoReset.current = true;

                // Silently reset
                fetch('/api/alerts/reset', { method: 'POST' })
                    .then(() => {
                        setAlerts([]);
                        setStats(null);
                        hasAutoReset.current = false;
                        console.log('✅ Auto-reset completed');
                    })
                    .catch(err => console.error('Auto-reset failed:', err));
            }
        }
    }, [stats]);

    // Get risk level info
    const getRiskInfo = (score: number) => {
        if (score > 70) return { level: t.dashboard.riskHigh, color: 'bg-red-500/20 text-red-400 border-red-500/30' };
        if (score > 40) return { level: t.dashboard.riskMedium, color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' };
        return { level: t.dashboard.riskLow, color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' };
    };

    // Format file size
    const formatSize = (bytes?: number) => {
        if (!bytes) return '-';
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    // Format time ago
    const formatTimeAgo = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return t.dashboard.justNow;
        if (diffMins < 60) return `${diffMins}${t.dashboard.minsAgo}`;
        if (diffHours < 24) return `${diffHours}${t.dashboard.hoursAgo}`;
        return `${diffDays}${t.dashboard.daysAgo}`;
    };

    // Get status display text
    const getStatusText = (status?: string) => {
        if (!status) return t.dashboard.statusNew;
        if (status === 'investigating') return t.dashboard.statusInvestigating;
        if (status === 'resolved') return t.dashboard.statusResolved;
        return status;
    };

    // Update alert status
    const updateStatus = async (alertId: string, status: string) => {
        setUpdatingStatus(true);
        try {
            const res = await fetch(`/api/alerts/${alertId}/status?status=${status}`, { method: 'PATCH' });
            if (res.ok) {
                const data = await res.json();
                setSelectedAlert(data.alert);
                setAlerts(prev => prev.map(a => a.id === alertId ? data.alert : a));
            }
        } catch (err) {
            console.error('Failed to update status:', err);
        } finally {
            setUpdatingStatus(false);
        }
    };

    const statCards = [
        { label: t.dashboard.totalAlerts, value: stats?.total_alerts || 0, icon: Activity, color: 'text-emerald-400' },
        { label: t.dashboard.highRisk, value: stats?.high_risk || 0, icon: AlertTriangle, color: 'text-red-400' },
        { label: t.dashboard.affectedUsers, value: stats?.unique_users || 0, icon: Users, color: 'text-blue-400' },
        { label: t.dashboard.avgRiskScore, value: stats?.avg_risk_score?.toFixed(1) || '0', icon: Shield, color: 'text-orange-400' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-b from-black via-slate-950 to-black text-white">
            {/* Header */}
            <header className="border-b border-emerald-500/10 bg-black/50 backdrop-blur-md sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/')}
                            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5 text-gray-400" />
                        </button>
                        <div className="flex items-center gap-3">
                            <div className="relative">
                                <div className="absolute inset-0 bg-emerald-500/30 blur-lg rounded-full"></div>
                                <Shield className="w-8 h-8 text-emerald-400 relative z-10" />
                            </div>
                            <span className="text-xl font-bold">{t.common.shadowGuard}</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                            <div className={`w-2 h-2 rounded-full ${loading ? 'bg-yellow-400 animate-pulse' : 'bg-emerald-400'}`}></div>
                            {loading ? t.dashboard.syncing : t.dashboard.liveStatus}
                        </div>
                        <LanguageToggle />
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                {/* Title */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold mb-2">{t.dashboard.securityOverview}</h1>
                    <p className="text-gray-400">{t.dashboard.securityOverviewSubtitle}</p>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    {statCards.map((stat, i) => (
                        <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="glass-card p-5"
                        >
                            <div className="flex items-center gap-3 mb-3">
                                <div className={`p-2 rounded-lg bg-white/5 ${stat.color}`}>
                                    <stat.icon className="w-5 h-5" />
                                </div>
                            </div>
                            <div className="text-2xl font-bold text-white">{stat.value}</div>
                            <div className="text-sm text-gray-400">{stat.label}</div>
                        </motion.div>
                    ))}
                </div>

                {/* Alerts Table */}
                <div className="glass-card overflow-hidden">
                    <div className="p-6 border-b border-emerald-500/10">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Activity className="w-5 h-5 text-emerald-400" />
                                <h2 className="text-lg font-semibold">{t.dashboard.recentAlerts}</h2>
                                <span className="text-sm text-gray-500">({alerts.length})</span>
                            </div>
                        </div>
                    </div>

                    {/* Table */}
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-emerald-500/10 text-left text-sm text-gray-500">
                                    <th className="px-6 py-4 font-medium">{t.dashboard.time}</th>
                                    <th className="px-6 py-4 font-medium">{t.dashboard.user}</th>
                                    <th className="px-6 py-4 font-medium">{t.dashboard.domain}</th>
                                    <th className="px-6 py-4 font-medium">{t.dashboard.category}</th>
                                    <th className="px-6 py-4 font-medium">{t.dashboard.risk}</th>
                                    <th className="px-6 py-4 font-medium">{t.dashboard.status}</th>
                                    <th className="px-6 py-4 font-medium text-right">{t.dashboard.action}</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-emerald-500/5">
                                {loading && alerts.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} className="px-6 py-16 text-center text-gray-500">
                                            <Activity className="w-8 h-8 animate-spin mx-auto mb-3 text-emerald-400" />
                                            <p>{t.dashboard.loadingAlerts}</p>
                                        </td>
                                    </tr>
                                ) : error ? (
                                    <tr>
                                        <td colSpan={7} className="px-6 py-16 text-center text-gray-500">
                                            <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-amber-400" />
                                            <p className="text-lg font-medium mb-1">{t.dashboard.failedToLoad}</p>
                                            <p className="text-sm">{t.dashboard.failedToLoadDesc}</p>
                                        </td>
                                    </tr>
                                ) : alerts.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} className="px-6 py-16 text-center text-gray-500">
                                            <Shield className="w-12 h-12 mx-auto mb-3 text-emerald-500/30" />
                                            <p className="text-lg font-medium mb-1">{t.dashboard.allClear}</p>
                                            <p className="text-sm">{t.dashboard.allClearDesc}</p>
                                        </td>
                                    </tr>
                                ) : (
                                    alerts.map((alert) => {
                                        const risk = getRiskInfo(alert.risk_score);
                                        return (
                                            <tr
                                                key={alert.id}
                                                onClick={() => setSelectedAlert(alert)}
                                                className="hover:bg-white/[0.02] cursor-pointer transition-colors"
                                            >
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center gap-2 text-sm text-gray-400">
                                                        <Clock className="w-4 h-4" />
                                                        {formatTimeAgo(alert.timestamp)}
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 text-sm text-white">{alert.user}</td>
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center gap-2 text-sm">
                                                        <Globe className="w-4 h-4 text-gray-500" />
                                                        <span className="text-white">{alert.domain}</span>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className="px-2 py-1 rounded bg-white/5 text-xs text-gray-300 border border-white/10">
                                                        {alert.category}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${risk.color}`}>
                                                        {risk.level} ({alert.risk_score})
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className={`text-xs ${alert.status === 'resolved' ? 'text-emerald-400' :
                                                            alert.status === 'investigating' ? 'text-yellow-400' :
                                                                'text-gray-400'
                                                        }`}>
                                                        {getStatusText(alert.status)}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-right">
                                                    <button className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors flex items-center gap-1 ml-auto">
                                                        <Eye className="w-4 h-4" />
                                                        {t.common.view}
                                                    </button>
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>

            {/* Alert Details Modal */}
            <AnimatePresence>
                {selectedAlert && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                        onClick={() => setSelectedAlert(null)}
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="glass-card w-full max-w-2xl max-h-[90vh] overflow-auto"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {/* Modal Header */}
                            <div className="flex items-center justify-between p-6 border-b border-emerald-500/10">
                                <div>
                                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                                        <span className={`${getRiskInfo(selectedAlert.risk_score).color} px-2 py-0.5 rounded text-sm`}>
                                            {getRiskInfo(selectedAlert.risk_score).level}
                                        </span>
                                        {selectedAlert.category}
                                    </h2>
                                    <p className="text-sm text-gray-400 mt-1">{selectedAlert.user}</p>
                                </div>
                                <button
                                    onClick={() => setSelectedAlert(null)}
                                    className="p-2 rounded-lg hover:bg-white/5 transition-colors text-gray-400 hover:text-white"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Modal Body */}
                            <div className="p-6 space-y-6">
                                {/* Summary */}
                                <div className="p-4 rounded-lg bg-white/5 border border-emerald-500/10">
                                    <p className="text-gray-300">
                                        {language === 'ja' ? (
                                            <>
                                                ユーザー <span className="text-white font-medium">{selectedAlert.user}</span> が{' '}
                                                <span className="text-white font-medium">{selectedAlert.domain}</span> にアクセス
                                                {selectedAlert.method && <> (<span className="text-emerald-400">{selectedAlert.method}</span>経由)</>}
                                                {selectedAlert.upload_size_bytes && selectedAlert.upload_size_bytes > 0 && (
                                                    <> - <span className="text-orange-400">{formatSize(selectedAlert.upload_size_bytes)}</span>をアップロード</>
                                                )}
                                            </>
                                        ) : (
                                            <>
                                                User <span className="text-white font-medium">{selectedAlert.user}</span> accessed{' '}
                                                <span className="text-white font-medium">{selectedAlert.domain}</span>
                                                {selectedAlert.method && <> via <span className="text-emerald-400">{selectedAlert.method}</span></>}
                                                {selectedAlert.upload_size_bytes && selectedAlert.upload_size_bytes > 0 && (
                                                    <> uploading <span className="text-orange-400">{formatSize(selectedAlert.upload_size_bytes)}</span></>
                                                )}.
                                            </>
                                        )}
                                    </p>
                                </div>

                                {/* AI Analysis */}
                                {selectedAlert.ai_message && (
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-400 mb-2">{t.dashboard.aiAnalysis}</h3>
                                        <p className="text-gray-300">{selectedAlert.ai_message}</p>
                                    </div>
                                )}

                                {/* Metadata Grid */}
                                <div>
                                    <h3 className="text-sm font-medium text-gray-400 mb-3">{t.dashboard.alertMetadata}</h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                                            <p className="text-xs text-gray-500 mb-1">{t.dashboard.riskScore}</p>
                                            <p className="text-white font-medium">{selectedAlert.risk_score}/100</p>
                                        </div>
                                        <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                                            <p className="text-xs text-gray-500 mb-1">{t.dashboard.status}</p>
                                            <p className="text-white font-medium capitalize">{getStatusText(selectedAlert.status)}</p>
                                        </div>
                                        <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                                            <p className="text-xs text-gray-500 mb-1">{t.dashboard.category}</p>
                                            <p className="text-white font-medium">{selectedAlert.category}</p>
                                        </div>
                                        <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                                            <p className="text-xs text-gray-500 mb-1">{t.dashboard.timestamp}</p>
                                            <p className="text-white font-medium text-sm">{new Date(selectedAlert.timestamp).toLocaleString()}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Raw JSON */}
                                <div>
                                    <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                                        <FileText className="w-4 h-4" />
                                        {t.dashboard.rawLog}
                                    </h3>
                                    <pre className="terminal-output text-xs overflow-x-auto">
                                        {JSON.stringify(selectedAlert, null, 2)}
                                    </pre>
                                </div>

                                {/* Action Buttons */}
                                <div className="flex gap-3 pt-2">
                                    <button
                                        onClick={() => updateStatus(selectedAlert.id, 'investigating')}
                                        disabled={updatingStatus || selectedAlert.status === 'investigating'}
                                        className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${selectedAlert.status === 'investigating'
                                                ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                                                : 'bg-white/5 text-white border border-white/10 hover:bg-white/10'
                                            } ${updatingStatus ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    >
                                        <Eye className="w-4 h-4" />
                                        {t.dashboard.markInvestigating}
                                    </button>
                                    <button
                                        onClick={() => updateStatus(selectedAlert.id, 'resolved')}
                                        disabled={updatingStatus || selectedAlert.status === 'resolved'}
                                        className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${selectedAlert.status === 'resolved'
                                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                                : 'bg-emerald-500 text-white hover:bg-emerald-600'
                                            } ${updatingStatus ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    >
                                        <CheckCircle className="w-4 h-4" />
                                        {t.dashboard.resolve}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};