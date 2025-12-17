import { useState, useEffect } from 'react';
import {
    Shield,
    AlertTriangle,
    Activity,
    Users,
    Search,
    Bell,
    Menu,
    Globe,
    Clock,
    Filter
} from 'lucide-react';

interface Alert {
    id: string;
    risk_score: number;
    user: string;
    domain: string;
    category: string;
    timestamp: string;
}

export const Dashboard = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState('overview');
    const [stats, setStats] = useState([
        { label: 'Total Alerts', value: '0', trend: '+0%', icon: Bell, color: 'text-blue-400' },
        { label: 'High Risk', value: '0', trend: '+0%', icon: AlertTriangle, color: 'text-red-400' },
        { label: 'Active Users', value: '0', trend: '+0%', icon: Users, color: 'text-green-400' },
        { label: 'Avg Risk Score', value: '0.00', trend: '0%', icon: Activity, color: 'text-purple-400' },
    ]);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/alerts');
                if (!response.ok) throw new Error('Failed to fetch alerts');
                const data = await response.json();
                setAlerts(data.alerts || []);
                setError(null);

                // Update stats based on real data
                if (data.alerts && data.alerts.length > 0) {
                    const highRisk = data.alerts.filter((a: Alert) => a.risk_score > 75).length;
                    const uniqueUsers = new Set(data.alerts.map((a: Alert) => a.user)).size;
                    const avgRisk = (data.alerts.reduce((sum: number, a: Alert) => sum + a.risk_score, 0) / data.alerts.length / 100).toFixed(2);

                    setStats([
                        { label: 'Total Alerts', value: data.alerts.length.toString(), trend: '+0%', icon: Bell, color: 'text-blue-400' },
                        { label: 'High Risk', value: highRisk.toString(), trend: '+0%', icon: AlertTriangle, color: 'text-red-400' },
                        { label: 'Active Users', value: uniqueUsers.toString(), trend: '+0%', icon: Users, color: 'text-green-400' },
                        { label: 'Avg Risk Score', value: avgRisk, trend: '0%', icon: Activity, color: 'text-purple-400' },
                    ]);
                }
            } catch (err) {
                console.error('Error fetching alerts:', err);
                setError(err instanceof Error ? err.message : 'Failed to fetch alerts');
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
        const interval = setInterval(fetchAlerts, 5000); // Refresh every 5 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-brand-500/30">

            {/* Sidebar */}
            <aside className="fixed left-0 top-0 h-full w-20 lg:w-64 bg-slate-900/50 backdrop-blur-xl border-r border-slate-800/50 hidden md:flex flex-col z-50">
                <div className="p-6 flex items-center gap-3">
                    <div className="relative">
                        <div className="absolute inset-0 bg-brand-500 blur-lg opacity-40 rounded-full animate-pulse-glow"></div>
                        <Shield className="w-8 h-8 text-brand-400 relative z-10" />
                    </div>
                    <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 hidden lg:block">
                        ShadowGuard
                    </span>
                </div>

                <nav className="flex-1 px-4 py-8 space-y-2">
                    {['Overview', 'Events', 'Analytics', 'Settings'].map((item) => (
                        <button
                            key={item}
                            onClick={() => setActiveTab(item.toLowerCase())}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group
                ${activeTab === item.toLowerCase()
                                    ? 'bg-brand-500/10 text-brand-300 border border-brand-500/20 shadow-[0_0_15px_-5px_rgba(139,92,246,0.5)]'
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
                                placeholder="Search events, users, or domains..."
                                className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/50 transition-all placeholder:text-slate-600"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <button className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50 transition-colors">
                            <Bell className="w-5 h-5" />
                            {alerts.length > 0 && (
                                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                            )}
                        </button>
                    </div>
                </header>

                <div className="p-8 max-w-7xl mx-auto space-y-8">

                    {/* Welcome Section */}
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 animate-slide-up">
                        <div>
                            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 mb-2">
                                Security Overview
                            </h1>
                            <p className="text-slate-400">Real-time monitoring of shadow IT activities</p>
                        </div>
                        <div className="flex gap-2">
                            <button className="px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2">
                                <Filter className="w-4 h-4" /> Filter
                            </button>
                            <button className="px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-500 transition-all shadow-[0_0_20px_-5px_rgba(124,58,237,0.5)]">
                                Download Report
                            </button>
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>
                        {stats.map((stat, i) => (
                            <div key={i} className="glass-card p-5 rounded-2xl relative overflow-hidden group">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                    <stat.icon className={`w-16 h-16 ${stat.color}`} />
                                </div>
                                <div className="flex items-start justify-between mb-4">
                                    <div className={`p-2 rounded-lg bg-slate-900/50 border border-slate-800 ${stat.color}`}>
                                        <stat.icon className="w-5 h-5" />
                                    </div>
                                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${stat.trend.startsWith('+') ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
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
                    <div className="glass-panel rounded-2xl p-6 animate-slide-up" style={{ animationDelay: '0.2s' }}>
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                < Activity className="w-5 h-5 text-brand-400" />
                                Recent Alerts {loading && <span className="text-xs text-slate-500">(Loading...)</span>}
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
                                    {loading && alerts.length === 0 ? (
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
                                    ) : alerts.length === 0 ? (
                                        <tr>
                                            <td colSpan={6} className="py-12 text-center text-slate-400">
                                                No alerts yet. Monitoring active...
                                            </td>
                                        </tr>
                                    ) : (
                                        alerts.map((alert) => {
                                            const riskScore = alert.risk_score / 100;
                                            const status = riskScore > 0.8 ? 'High Risk' : riskScore > 0.4 ? 'Medium Risk' : 'Low Risk';
                                            const timeAgo = new Date(alert.timestamp).toLocaleString();

                                            return (
                                                <tr key={alert.id} className="group hover:bg-slate-800/20 transition-colors">
                                                    <td className="py-4 pl-4">
                                                        <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${riskScore > 0.8
                                                            ? 'bg-red-500/10 text-red-400 border-red-500/20'
                                                            : riskScore > 0.4
                                                                ? 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                                                                : 'bg-green-500/10 text-green-400 border-green-500/20'
                                                            }`}>
                                                            <div className={`w-1.5 h-1.5 rounded-full ${riskScore > 0.8 ? 'bg-red-400 animate-pulse' :
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
                                                        <button className="text-sm font-medium text-slate-400 hover:text-white transition-colors">
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
        </div>
    );
};
