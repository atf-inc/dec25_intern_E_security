import { useState, useEffect } from 'react';
import {
    ShieldAlert,
    Activity,
    Clock,
    Search,
    Filter,
    CheckCircle,
    AlertTriangle
} from 'lucide-react';

export interface Alert {
    id: string;
    risk_score: number;
    user: string;
    department: string;
    domain: string;
    category: string;
    status: 'new' | 'investigating' | 'resolved';
    timestamp: string;
    ai_message?: string;
}

const StatusBadge = ({ status }: { status: Alert['status'] }) => {
    const styles = {
        new: "bg-red-100 text-red-800 border-red-200",
        investigating: "bg-yellow-100 text-yellow-800 border-yellow-200",
        resolved: "bg-green-100 text-green-800 border-green-200"
    };

    const icons = {
        new: AlertTriangle,
        investigating: Activity,
        resolved: CheckCircle
    };

    const Icon = icons[status];

    return (
        <span className={`flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status]}`}>
            <Icon size={12} />
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};

const API_URL = 'http://localhost:8000/api/alerts';

export const Dashboard = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await fetch(API_URL);
                if (!response.ok) throw new Error('Failed to fetch alerts');
                const data = await response.json();
                setAlerts(data.alerts || []);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error');
                setAlerts([]);
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
        const interval = setInterval(fetchAlerts, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading && alerts.length === 0) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="flex flex-col items-center gap-2">
                    <Activity className="animate-spin text-indigo-600" size={32} />
                    <p className="text-gray-500">Connecting to ShadowGuard Brain...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="mb-8">
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <ShieldAlert className="text-indigo-600" size={32} />
                            ShadowGuard Dashboard
                        </h1>
                        <p className="text-gray-500 mt-2">Real-time Shadow IT detection and risk analysis.</p>
                    </div>
                    {error && (
                        <div className="flex items-center gap-2 bg-yellow-50 text-yellow-800 px-4 py-2 rounded-lg border border-yellow-200 text-sm">
                            <AlertTriangle size={16} />
                            <span>Backend Offline</span>
                        </div>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {[
                    {
                        label: "Total Alerts",
                        value: alerts.length,
                        icon: ShieldAlert,
                        color: "text-blue-600"
                    },
                    {
                        label: "High Risk",
                        value: alerts.filter(a => a.risk_score > 75).length,
                        icon: AlertTriangle,
                        color: "text-red-600"
                    },
                    {
                        label: "Active Shadow IT",
                        value: new Set(alerts.map(a => a.domain)).size,
                        icon: Activity,
                        color: "text-purple-600"
                    },
                    {
                        label: "Avg Response",
                        value: "Real-time",
                        icon: Clock,
                        color: "text-green-600"
                    },
                ].map((stat, idx) => (
                    <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                                <p className="text-2xl font-semibold text-gray-900 mt-1">{stat.value}</p>
                            </div>
                            <stat.icon className={`${stat.color} opacity-80`} size={24} />
                        </div>
                    </div>
                ))}
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-200 flex flex-col sm:flex-row justify-between gap-4">
                    <h2 className="text-lg font-semibold text-gray-900">Recent Alerts</h2>
                    <div className="flex gap-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                            <input
                                type="text"
                                placeholder="Search alerts..."
                                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            />
                        </div>
                        <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                            <Filter size={18} />
                            Filter
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                            <tr>
                                <th className="px-6 py-3 font-medium">Risk Score</th>
                                <th className="px-6 py-3 font-medium">User / Dept</th>
                                <th className="px-6 py-3 font-medium">Domain / Category</th>
                                <th className="px-6 py-3 font-medium">Analysis</th>
                                <th className="px-6 py-3 font-medium">Status</th>
                                <th className="px-6 py-3 font-medium">Timestamp</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {alerts.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                                        No alerts found. Monitoring active...
                                    </td>
                                </tr>
                            ) : (
                                alerts.map((alert) => (
                                    <tr key={alert.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <span className={`font-bold ${alert.risk_score > 75 ? 'text-red-600' : alert.risk_score > 50 ? 'text-yellow-600' : 'text-green-600'}`}>
                                                    {alert.risk_score}
                                                </span>
                                                <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${alert.risk_score > 75 ? 'bg-red-500' : alert.risk_score > 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                                        style={{ width: `${alert.risk_score}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="text-sm font-medium text-gray-900">{alert.user}</span>
                                                <span className="text-xs text-gray-500">{alert.department}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="text-sm font-medium text-indigo-600">{alert.domain}</span>
                                                <span className="text-xs text-gray-500">{alert.category}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 min-w-[300px]">
                                            {alert.ai_message && (
                                                <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-3">
                                                    <div className="flex items-start gap-2">
                                                        <div className="min-w-[16px] mt-0.5">✨</div>
                                                        <p className="text-xs text-indigo-800 leading-relaxed">{alert.ai_message}</p>
                                                    </div>
                                                </div>
                                            )}
                                            {!alert.ai_message && <span className="text-xs text-gray-400 italic">No AI analysis available</span>}
                                        </td>
                                        <td className="px-6 py-4">
                                            <StatusBadge status={alert.status} />
                                        </td>
                                        <td className="px-6 py-4 text-xs text-gray-500">
                                            {new Date(alert.timestamp).toLocaleString()}
                                        </td>
                                    </tr>
                                )))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
