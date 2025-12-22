import { useState, useEffect } from 'react';
import {
    Shield,
    AlertTriangle,
    Activity,
    Users,
    Search,
    Menu,
    Globe,
    Clock,
    Filter,
    ChevronDown,
    X,
    Eye,
    CheckCircle,
    Bell
} from 'lucide-react';

interface Alert {
    id: string;
    risk_score: number;
    user: string;
    domain: string;
    category: string;
    timestamp: string;
    status?: string;
    ai_message?: string;
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
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [filteredAlerts, setFilteredAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState('overview');
    const [apiStats, setApiStats] = useState<Stats | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [riskFilter, setRiskFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
    const [showFilterDropdown, setShowFilterDropdown] = useState(false);
    const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
    const [updatingStatus, setUpdatingStatus] = useState(false);

    const stats = [
        { label: 'Total Alerts', value: apiStats?.total_alerts?.toString() || '0', trend: '+0%', icon: Bell, color: 'text-blue-400' },
        { label: 'High Risk', value: apiStats?.high_risk?.toString() || '0', trend: '+0%', icon: AlertTriangle, color: 'text-red-400' },
        { label: 'Active Users', value: apiStats?.unique_users?.toString() || '0', trend: '+0%', icon: Users, color: 'text-green-400' },
        { label: 'Avg Risk Score', value: apiStats?.avg_risk_score?.toFixed(2) || '0.00', trend: '0%', icon: Activity, color: 'text-purple-400' },
    ];

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Build search URL with filters
                const params = new URLSearchParams();
                if (searchQuery) params.append('q', searchQuery);
                if (riskFilter !== 'all') params.append('risk_level', riskFilter);

                const alertsUrl = params.toString()
                    ? `/api/alerts/search?${params.toString()}`
                    : '/api/alerts';

                const [alertsRes, statsRes] = await Promise.all([
                    fetch(alertsUrl),
                    fetch('/api/stats')
                ]);

                if (!alertsRes.ok) throw new Error('Failed to fetch alerts');
                if (!statsRes.ok) throw new Error('Failed to fetch stats');

                const alertsData = await alertsRes.json();
                const statsData = await statsRes.json();

                setAlerts(alertsData.alerts || []);
                setApiStats(statsData);
                setError(null);
            } catch (err) {
                console.error('Error fetching data:', err);
                setError(err instanceof Error ? err.message : 'Failed to fetch data');
            } finally {
                setLoading(false);
                setIsSearching(false);
            }
        };

        // Debounce search
        const timeoutId = setTimeout(() => {
            fetchData();
        }, searchQuery ? 300 : 0);

        // Only set up polling if not actively filtering
        let interval: ReturnType<typeof setInterval> | null = null;
        if (!searchQuery && riskFilter === 'all') {
            interval = setInterval(fetchData, 5000);
        }

        return () => {
            clearTimeout(timeoutId);
            if (interval) clearInterval(interval);
        };
    }, [searchQuery, riskFilter]);

    // Update filtered alerts based on current alerts
    useEffect(() => {
        setFilteredAlerts(alerts);
    }, [alerts]);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-brand-500/30">

            {/* Sidebar */}
            <aside className="fixed left-0 top-0 h-full w-20 lg:w-64 bg-slate-900/50 backdrop-blur-xl border-r border-slate-800/50 hidden md:flex flex-col z-50">
                <div className="p-6 flex items-center gap-3">
                    <div className="relative">
                        <div className="absolute inset-0 bg-brand-500 blur-lg opacity-40 rounded-full animate-pulse-glow"></div>
                        <Shield className="w-8 h-8 text-brand-400 relative z-10" />
                    </div>
                    <span className="text-xl font-bold text-gradient hidden lg:block">
                        ShadowGuard
                    </span>
                </div>

                <nav className="flex-1 px-4 py-8 space-y-2">
                    {['Overview', 'Events', 'Analytics', 'Settings'].map((item) => (
                        <button
                            key={item}
                            onClick={() => setActiveTab(item.toLowerCase())}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
                                activeTab === item.toLowerCase()
                                    ? 'bg-brand-500/10 text-brand-300 border border-brand-500/20 glow'
                                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                            }`}
                        >
                            <Activity className="w-5 h-5" />
                            <span className="hidden lg:block font-medium">{item}</span>
                        </button>
                    ))}
                </nav>

                <div className="p-4 border-t border-slate-800/50">
                    <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/30 border border-slate-700/30">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-400 to-purple-600 flex items-center justify-center font-bold text-xs">
                            AD
                        </div>
                        <div className="hidden lg:block">
                            <p className="text-sm font-medium">Admin User</p>
                            <p className="text-xs text-slate-500">View Profile</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="md:ml-20 lg:ml-64 min-h-screen relative overflow-hidden">
                {/* Background Glow Effects */}
                <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-brand-500/10 rounded-full blur-[100px] -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
                <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[100px] translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

                {/* Header */}
                <header className="sticky top-0 z-40 px-8 py-5 flex items-center justify-between backdrop-blur-md bg-slate-950/50 border-b border-slate-800/50">
                    <div className="flex items-center gap-4 md:hidden">
                        <Menu className="w-6 h-6 text-slate-400" />
                        <Shield className="w-6 h-6 text-brand-500" />
                    </div>

                    <div className="hidden md:flex items-center gap-4 flex-1 max-w-xl">
                        <div className="relative w-full group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-brand-400 transition-colors" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => {
                                    setSearchQuery(e.target.value);
                                    setIsSearching(true);
                                }}
                                placeholder="Search events, users, or domains..."
                                className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/50 transition-all placeholder:text-slate-600"
                            />
                            {isSearching && (
                                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                                    <Activity className="w-4 h-4 text-brand-400 animate-spin" />
                                </div>
                            )}
                        </div>
                    </div>
                </header>

                <div className="p-8 max-w-7xl mx-auto space-y-8">
                    {/* Welcome Section */}
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 animate-slide-up">
                        <div>
                            <h1 className="text-3xl font-bold text-gradient mb-2">
                                Security Overview
                            </h1>
                            <p className="text-slate-400">Real-time monitoring of shadow IT activities</p>
                        </div>
                        <div className="flex gap-2 relative">
                            <div className="relative">
                                <button
                                    onClick={() => setShowFilterDropdown(!showFilterDropdown)}
                                    className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors flex items-center gap-2 ${riskFilter !== 'all'
                                        ? 'bg-brand-600/20 border-brand-500/50 text-brand-300'
                                        : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800'
                                        }`}
                                >
                                    <Filter className="w-4 h-4" />
                                    {riskFilter === 'all' ? 'Filter' : `${riskFilter.charAt(0).toUpperCase() + riskFilter.slice(1)} Risk`}
                                    <ChevronDown className="w-3 h-3" />
                                </button>
                                {showFilterDropdown && (
                                    <div className="absolute top-full mt-2 right-0 bg-slate-800 border border-slate-700 rounded-xl shadow-xl z-50 min-w-[150px] overflow-hidden">
                                        {['all', 'high', 'medium', 'low'].map((level) => (
                                            <button
                                                key={level}
                                                onClick={() => {
                                                    setRiskFilter(level as typeof riskFilter);
                                                    setShowFilterDropdown(false);
                                                    setIsSearching(true);
                                                }}
                                                className={`w-full px-4 py-2 text-left text-sm hover:bg-slate-700 transition-colors flex items-center gap-2 ${riskFilter === level ? 'text-brand-400 bg-slate-700/50' : 'text-slate-300'
                                                    }`}
                                            >
                                                {level === 'all' && 'All Risks'}
                                                {level === 'high' && <><span className="w-2 h-2 rounded-full bg-red-500" /> High Risk</>}
                                                {level === 'medium' && <><span className="w-2 h-2 rounded-full bg-orange-500" /> Medium Risk</>}
                                                {level === 'low' && <><span className="w-2 h-2 rounded-full bg-green-500" /> Low Risk</>}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                            {riskFilter !== 'all' && (
                                <button
                                    onClick={() => { setRiskFilter('all'); setIsSearching(true); }}
                                    className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            )}
                            <button className="px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-500 transition-all shadow-[0_0_20px_-5px_rgba(124,58,237,0.5)]">
                                Download Report
                            </button>
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up delay-100">
                        {stats.map((stat, i) => (
                            <div key={i} className="glass-card p-5 rounded-2xl relative overflow-hidden group">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                    <stat.icon className={`w-16 h-16 ${stat.color}`} />
                                </div>
                                <div className="flex items-start justify-between mb-4">
                                    <div className={`p-2 rounded-lg bg-slate-900/50 border border-slate-800 ${stat.color}`}>
                                        <stat.icon className="w-5 h-5" />
                                    </div>
                                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                                        stat.trend.startsWith('+') ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                                    }`}>
                                        {stat.trend}
                                    </span>
                                </div>
                                <div className="relative z-10">
                                    <h3 className="text-3xl font-bold text-white mb-1">{stat.value}</h3>
                                    <p className="text-sm text-slate-400">{stat.label}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Recent Alerts Table */}
                    <div className="glass-panel rounded-2xl p-6 animate-slide-up delay-200">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                <Activity className="w-5 h-5 text-brand-400" />
                                Recent Alerts {loading && <span className="text-xs text-slate-500">(Loading...)</span>}
                                <span className="text-xs text-slate-500">({filteredAlerts.length} filtered)</span>
                            </h2>
                            <button className="text-sm text-brand-400 hover:text-brand-300 font-medium transition-colors">
                                View All
                            </button>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-slate-800/50 text-left">
                                        <th className="pb-4 pl-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Risk Level</th>
                                        <th className="pb-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Domain</th>
                                        <th className="pb-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">User</th>
                                        <th className="pb-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Category</th>
                                        <th className="pb-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Time</th>
                                        <th className="pb-4 pr-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/30">
                                    {loading && filteredAlerts.length === 0 ? (
                                        <tr>
                                            <td colSpan={6} className="py-12 text-center text-slate-400">
                                                <Activity className="w-8 h-8 animate-spin mx-auto mb-2" />
                                                Loading alerts...
                                            </td>
                                        </tr>
                                    ) : error ? (
                                        <tr>
                                            <td colSpan={6} className="py-12 text-center text-red-400">
                                                <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
                                                Error: {error}
                                            </td>
                                        </tr>
                                    ) : filteredAlerts.length === 0 ? (
                                        <tr>
                                            <td colSpan={6} className="py-12 text-center text-slate-400">
                                                No alerts match your current filters
                                            </td>
                                        </tr>
                                    ) : (
                                        filteredAlerts.map((alert) => {
                                            const riskScore = alert.risk_score / 100;
                                            const status = riskScore > 0.8 ? 'High Risk' : riskScore > 0.4 ? 'Medium Risk' : 'Low Risk';
                                            const timeAgo = new Date(alert.timestamp).toLocaleString();

                                            return (
                                                <tr key={alert.id} className="group hover:bg-slate-800/20 transition-colors">
                                                    <td className="py-4 pl-4">
                                                        <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                                                            riskScore > 0.8
                                                                ? 'bg-red-500/10 text-red-400 border-red-500/20'
                                                                : riskScore > 0.4
                                                                    ? 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                                                                    : 'bg-green-500/10 text-green-400 border-green-500/20'
                                                        }`}>
                                                            <div className={`w-1.5 h-1.5 rounded-full ${
                                                                riskScore > 0.8 ? 'bg-red-400 animate-pulse' :
                                                                riskScore > 0.4 ? 'bg-orange-400' : 'bg-green-400'
                                                            }`}></div>
                                                            {status}
                                                        </div>
                                                    </td>
                                                    <td className="py-4 font-medium text-white flex items-center gap-2">
                                                        <Globe className="w-4 h-4 text-slate-500" />
                                                        {alert.domain}
                                                    </td>
                                                    <td className="py-4 text-slate-400 text-sm">{alert.user}</td>
                                                    <td className="py-4">
                                                        <span className="px-2 py-1 rounded bg-slate-800 text-xs text-slate-300 border border-slate-700">
                                                            {alert.category}
                                                        </span>
                                                    </td>
                                                    <td className="py-4 text-slate-500 text-sm flex items-center gap-1.5">
                                                        <Clock className="w-3.5 h-3.5" />
                                                        {timeAgo}
                                                    </td>
                                                    <td className="py-4 pr-4 text-right">
                                                        <button
                                                            onClick={() => setSelectedAlert(alert)}
                                                            className="text-sm font-medium text-slate-400 hover:text-white transition-colors flex items-center gap-1 ml-auto"
                                                        >
                                                            <Eye className="w-3.5 h-3.5" />
                                                            Investigate
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
                </div>
            </main>

            {/* Investigation Modal */}
            {selectedAlert && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setSelectedAlert(null)}>
                    <div
                        className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-auto"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Modal Header */}
                        <div className="flex items-center justify-between p-6 border-b border-slate-800">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${selectedAlert.risk_score > 70 ? 'bg-red-500/20' :
                                    selectedAlert.risk_score > 40 ? 'bg-orange-500/20' : 'bg-green-500/20'
                                    }`}>
                                    <AlertTriangle className={`w-5 h-5 ${selectedAlert.risk_score > 70 ? 'text-red-400' :
                                        selectedAlert.risk_score > 40 ? 'text-orange-400' : 'text-green-400'
                                        }`} />
                                </div>
                                <div>
                                    <h2 className="text-lg font-semibold text-white">Alert Investigation</h2>
                                    <p className="text-sm text-slate-400">ID: {selectedAlert.id.slice(0, 8)}...</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedAlert(null)}
                                className="p-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Modal Body */}
                        <div className="p-6 space-y-6">
                            {/* Risk Score */}
                            <div className="flex items-center gap-4">
                                <div className="flex-1">
                                    <p className="text-sm text-slate-400 mb-2">Risk Score</p>
                                    <div className="flex items-center gap-3">
                                        <div className="text-4xl font-bold text-white">{selectedAlert.risk_score}</div>
                                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${selectedAlert.risk_score > 70 ? 'bg-red-500/20 text-red-400' :
                                            selectedAlert.risk_score > 40 ? 'bg-orange-500/20 text-orange-400' : 'bg-green-500/20 text-green-400'
                                            }`}>
                                            {selectedAlert.risk_score > 70 ? 'High Risk' : selectedAlert.risk_score > 40 ? 'Medium Risk' : 'Low Risk'}
                                        </div>
                                    </div>
                                </div>
                                <div className="w-24 h-24 rounded-full border-4 border-slate-700 flex items-center justify-center relative">
                                    <svg className="absolute inset-0 w-full h-full -rotate-90">
                                        <circle cx="48" cy="48" r="44" fill="none" stroke="currentColor" strokeWidth="8"
                                            className={selectedAlert.risk_score > 70 ? 'text-red-500/30' : selectedAlert.risk_score > 40 ? 'text-orange-500/30' : 'text-green-500/30'}
                                        />
                                        <circle cx="48" cy="48" r="44" fill="none" stroke="currentColor" strokeWidth="8"
                                            strokeDasharray={`${selectedAlert.risk_score * 2.76} 276`}
                                            className={selectedAlert.risk_score > 70 ? 'text-red-500' : selectedAlert.risk_score > 40 ? 'text-orange-500' : 'text-green-500'}
                                        />
                                    </svg>
                                    <span className="text-xl font-bold">{selectedAlert.risk_score}%</span>
                                </div>
                            </div>

                            {/* Details Grid */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                                    <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Domain</p>
                                    <p className="text-white font-medium flex items-center gap-2">
                                        <Globe className="w-4 h-4 text-slate-500" />
                                        {selectedAlert.domain}
                                    </p>
                                </div>
                                <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                                    <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">User</p>
                                    <p className="text-white font-medium flex items-center gap-2">
                                        <Users className="w-4 h-4 text-slate-500" />
                                        {selectedAlert.user}
                                    </p>
                                </div>
                                <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                                    <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Category</p>
                                    <p className="text-white font-medium">{selectedAlert.category}</p>
                                </div>
                                <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                                    <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Timestamp</p>
                                    <p className="text-white font-medium flex items-center gap-2">
                                        <Clock className="w-4 h-4 text-slate-500" />
                                        {new Date(selectedAlert.timestamp).toLocaleString()}
                                    </p>
                                </div>
                            </div>

                            {/* AI Analysis */}
                            {selectedAlert.ai_message && (
                                <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                                    <p className="text-xs text-slate-400 uppercase tracking-wide mb-2">AI Analysis</p>
                                    <p className="text-slate-200">{selectedAlert.ai_message}</p>
                                </div>
                            )}

                            {/* Status Update */}
                            <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                                <p className="text-xs text-slate-400 uppercase tracking-wide mb-3">Update Status</p>
                                <div className="flex gap-2 flex-wrap">
                                    {['investigating', 'resolved', 'dismissed'].map((status) => (
                                        <button
                                            key={status}
                                            disabled={updatingStatus || selectedAlert.status === status}
                                            onClick={async () => {
                                                setUpdatingStatus(true);
                                                try {
                                                    const res = await fetch(`/api/alerts/${selectedAlert.id}/status?status=${status}`, { method: 'PATCH' });
                                                    if (res.ok) {
                                                        const data = await res.json();
                                                        setSelectedAlert(data.alert);
                                                        // Update the alert in the list too
                                                        setAlerts(prev => prev.map(a => a.id === selectedAlert.id ? data.alert : a));
                                                    }
                                                } catch (err) {
                                                    console.error('Failed to update status:', err);
                                                } finally {
                                                    setUpdatingStatus(false);
                                                }
                                            }}
                                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${selectedAlert.status === status
                                                ? 'bg-brand-600 text-white'
                                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                                } ${updatingStatus ? 'opacity-50 cursor-not-allowed' : ''}`}
                                        >
                                            {status === 'investigating' && <Eye className="w-4 h-4" />}
                                            {status === 'resolved' && <CheckCircle className="w-4 h-4" />}
                                            {status === 'dismissed' && <X className="w-4 h-4" />}
                                            {status.charAt(0).toUpperCase() + status.slice(1)}
                                        </button>
                                    ))}
                                </div>
                                <p className="text-xs text-slate-500 mt-2">Current status: <span className="text-slate-300">{selectedAlert.status || 'new'}</span></p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};