import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
    Calendar,
    Tag,
    Search,
    BarChart3,
    Table as TableIcon,
    TrendingUp,
    X,
    Plus,
    Loader2,
    AlertCircle
} from 'lucide-react';

const MIXPANEL_API_URL = 'https://ues.api.zupay.in/data/fetch_mixpanel_events';

const COLORS = ['#8B5CF6', '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#6366F1', '#EC4899'];

function MixpanelAnalytics() {
    const [fromDate, setFromDate] = useState(() => {
        const d = new Date();
        d.setDate(d.getDate() - 14);
        return d.toISOString().split('T')[0];
    });
    const [toDate, setToDate] = useState(() => new Date().toISOString().split('T')[0]);
    const [events, setEvents] = useState(['rc_trial_started_event', 'Signup Completed', 'rc_cancellation_event']);
    const [newEvent, setNewEvent] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchData = async () => {
        if (events.length === 0) {
            setError('Please add at least one event');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await axios.post(MIXPANEL_API_URL, {
                from_date: fromDate,
                to_date: toDate,
                events: events
            });

            if (response.data.status === 'success') {
                setData(response.data);
            } else {
                setError('Failed to fetch data from API');
            }
        } catch (err) {
            console.error('Error fetching Mixpanel data:', err);
            setError('Error connecting to the analytics server');
        } finally {
            setLoading(false);
        }
    };

    const addEvent = () => {
        if (newEvent && !events.includes(newEvent)) {
            setEvents([...events, newEvent]);
            setNewEvent('');
        }
    };

    const removeEvent = (eventToRemove) => {
        setEvents(events.filter(e => e !== eventToRemove));
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            addEvent();
        }
    };

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const prepareChartData = () => {
        if (!data || !data.data || !data.data.series) return [];

        return data.data.series.map(date => {
            const entry = { date };
            Object.keys(data.data.values).forEach(eventName => {
                entry[eventName] = data.data.values[eventName][date] || 0;
            });
            return entry;
        });
    };

    const chartData = prepareChartData();

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
                    <BarChart3 className="w-8 h-8 mr-3 text-purple-600" />
                    Mixpanel Analytics
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    Track and visualize user events across custom date ranges.
                </p>
            </div>

            {/* Control Panel */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Date Pickers */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center">
                            <Calendar className="w-4 h-4 mr-2" />
                            Date Range
                        </h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1 caps tracking-wider">FROM</label>
                                <input
                                    type="date"
                                    value={fromDate}
                                    onChange={(e) => setFromDate(e.target.value)}
                                    className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-purple-500 outline-none transition-all dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1 caps tracking-wider">TO</label>
                                <input
                                    type="date"
                                    value={toDate}
                                    onChange={(e) => setToDate(e.target.value)}
                                    className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-purple-500 outline-none transition-all dark:text-white"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Event Tags */}
                    <div className="lg:col-span-2 space-y-4">
                        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center">
                            <Tag className="w-4 h-4 mr-2" />
                            Event Names
                        </h3>
                        <div className="flex flex-wrap gap-2 mb-3">
                            {events.map((event, index) => (
                                <span
                                    key={event}
                                    className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border border-purple-100 dark:border-purple-800"
                                >
                                    {event}
                                    <button
                                        onClick={() => removeEvent(event)}
                                        className="ml-2 hover:text-purple-900 dark:hover:text-purple-100 transition-colors"
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                </span>
                            ))}
                        </div>
                        <div className="flex gap-2">
                            <div className="relative flex-1">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Enter event name (e.g. Signup Completed)"
                                    value={newEvent}
                                    onChange={(e) => setNewEvent(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-purple-500 outline-none transition-all dark:text-white"
                                />
                            </div>
                            <button
                                onClick={addEvent}
                                className="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 p-2 rounded-xl transition-colors"
                                title="Add Event"
                            >
                                <Plus className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                            </button>
                        </div>
                    </div>
                </div>

                <div className="mt-8 flex justify-end">
                    <button
                        onClick={fetchData}
                        disabled={loading}
                        className="flex items-center px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-purple-200 dark:shadow-none disabled:opacity-50 disabled:cursor-not-allowed group"
                    >
                        {loading ? (
                            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        ) : (
                            <TrendingUp className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                        )}
                        {loading ? 'Fetching...' : 'Show Data'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-xl flex items-center mb-8">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    {error}
                </div>
            )}

            {/* KPI Section */}
            {data && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {Object.entries(data.count).map(([eventName, total], index) => (
                        <div key={eventName} className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
                            <div className="flex items-center justify-between mb-2">
                                <div
                                    className="w-2 h-8 rounded-full"
                                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                                />
                                <span className="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest">Total Counts</span>
                            </div>
                            <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 truncate" title={eventName}>
                                {eventName}
                            </h4>
                            <p className="text-3xl font-extrabold text-gray-900 dark:text-white mt-1">
                                {total.toLocaleString()}
                            </p>
                        </div>
                    ))}
                </div>
            )}

            {/* Charts Section */}
            {data && (
                <div className="grid grid-cols-1 gap-8 mb-8">
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6 flex items-center">
                            <TrendingUp className="w-5 h-5 mr-2 text-blue-500" />
                            Event Trends over Time
                        </h3>
                        <div className="h-[400px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                    <XAxis
                                        dataKey="date"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#9ca3af', fontSize: 12 }}
                                        dy={10}
                                        tickFormatter={(str) => {
                                            const date = new Date(str);
                                            return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
                                        }}
                                    />
                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#9ca3af', fontSize: 12 }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            borderRadius: '12px',
                                            border: 'none',
                                            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                                            backgroundColor: 'rgba(255, 255, 255, 0.95)'
                                        }}
                                    />
                                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                    {events.map((eventName, index) => (
                                        <Line
                                            key={eventName}
                                            type="monotone"
                                            dataKey={eventName}
                                            stroke={COLORS[index % COLORS.length]}
                                            strokeWidth={3}
                                            dot={{ r: 4, strokeWidth: 2, fill: '#fff' }}
                                            activeDot={{ r: 6, strokeWidth: 0 }}
                                        />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            )}

            {/* Data Table */}
            {data && (
                <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center">
                            <TableIcon className="w-5 h-5 mr-2 text-green-500" />
                            Raw Data Breakdown
                        </h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-900/50">
                                    <th className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">Date</th>
                                    {events.map((event) => (
                                        <th key={event} className="px-6 py-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">{event}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {chartData.map((row, i) => (
                                    <tr key={row.date} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                                        <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                                            {new Date(row.date).toLocaleDateString(undefined, { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })}
                                        </td>
                                        {events.map((event) => (
                                            <td key={event} className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${row[event] > 0 ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : 'text-gray-400'}`}>
                                                    {row[event] || 0}
                                                </span>
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!data && !loading && !error && (
                <div className="flex flex-col items-center justify-center py-20 bg-gray-50 dark:bg-gray-900/30 rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-800">
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-full shadow-lg mb-6">
                        <TrendingUp className="w-12 h-12 text-purple-600" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No Data Fetched</h3>
                    <p className="text-gray-600 dark:text-gray-400 max-w-xs text-center">
                        Select your events and date range above, then click "Show Data" to see analytics.
                    </p>
                </div>
            )}
        </div>
    );
}

export default MixpanelAnalytics;
