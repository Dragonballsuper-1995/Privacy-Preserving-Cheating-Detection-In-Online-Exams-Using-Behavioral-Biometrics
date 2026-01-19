/**
 * Enhanced Admin Dashboard
 * Full-featured dashboard with risk visualization, timeline, and export
 */

'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';

// Smart API URL detection - same logic as lib/api.ts
function getApiBase(): string {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        if (hostname.includes('onrender.com')) {
            return 'https://cheating-detector-backend.onrender.com';
        }
        if (hostname.includes('devtunnels.ms')) {
            return 'https://6vjfqk0n-8000.inc1.devtunnels.ms';
        }
        if (hostname === '192.168.89.1' || hostname.startsWith('192.168.')) {
            return 'http://192.168.89.1:8000';
        }
    }
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

const API_BASE = getApiBase();

interface SessionScore {
    typing: number;
    hesitation: number;
    paste: number;
    focus: number;
}

interface SessionSummary {
    session_id: string;
    risk_score: number;
    is_flagged: boolean;
    event_count: number;
    flag_reasons: string[];
    scores: SessionScore;
    created_at?: string;
    is_simulated?: boolean;  // Added simulation flag
}

interface DashboardData {
    total_sessions: number;
    flagged_sessions: number;
    sessions: SessionSummary[];
}

interface TimelineEvent {
    timestamp: number;
    type: string;
    data: Record<string, unknown>;
    question_id: string;
    annotation?: string;
    severity?: string;
}

interface SessionDetails {
    session_id: string;
    overall_score: number;
    typing_score: number;
    hesitation_score: number;
    paste_score: number;
    focus_score: number;
    is_flagged: boolean;
    flag_reasons: string[];
    features?: {
        keystroke: Record<string, unknown>;
        hesitation: Record<string, unknown>;
        paste: Record<string, unknown>;
        focus: Record<string, unknown>;
    };
}

export default function AdminDashboard() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [selectedSession, setSelectedSession] = useState<SessionDetails | null>(null);
    const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState<'overview' | 'timeline' | 'features'>('overview');
    const [simulating, setSimulating] = useState(false);
    const [sessionFilter, setSessionFilter] = useState<'all' | 'real' | 'simulated'>('all');

    useEffect(() => {
        loadDashboard();
    }, []);

    async function loadDashboard() {
        try {
            setLoading(true);
            const res = await fetch(`${API_BASE}/api/analysis/dashboard/summary`);
            if (!res.ok) throw new Error('Failed to load dashboard');
            const result = await res.json();
            setData(result);
        } catch (err) {
            setError('Failed to load dashboard. Make sure the backend is running.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    async function viewSession(sessionId: string) {
        try {
            // Get detailed analysis
            const res = await fetch(`${API_BASE}/api/analysis/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, include_features: true }),
            });
            if (res.ok) {
                const details = await res.json();
                setSelectedSession(details);
            }

            // Get timeline
            const timelineRes = await fetch(`${API_BASE}/api/analysis/session/${sessionId}/timeline`);
            if (timelineRes.ok) {
                const timelineData = await timelineRes.json();
                setTimeline(timelineData.timeline || []);
            }
        } catch (err) {
            console.error('Failed to load session:', err);
        }
    }

    const generateTestData = useCallback(async (type: 'honest' | 'cheater') => {
        setSimulating(true);
        try {
            const res = await fetch(`${API_BASE}/api/simulation/simulate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    is_cheater: type === 'cheater',
                    count: 3,
                    question_count: 6,
                }),
            });
            if (res.ok) {
                await loadDashboard();
            }
        } catch (err) {
            console.error('Simulation failed:', err);
        } finally {
            setSimulating(false);
        }
    }, []);

    const exportData = useCallback(async () => {
        if (!data) return;

        const exportContent = {
            exported_at: new Date().toISOString(),
            summary: {
                total_sessions: data.total_sessions,
                flagged_sessions: data.flagged_sessions,
                flag_rate: data.total_sessions > 0
                    ? (data.flagged_sessions / data.total_sessions * 100).toFixed(2) + '%'
                    : '0%',
            },
            sessions: data.sessions.map(s => ({
                session_id: s.session_id,
                risk_score: s.risk_score,
                is_flagged: s.is_flagged,
                event_count: s.event_count,
                scores: s.scores,
                flag_reasons: s.flag_reasons,
            })),
        };

        const blob = new Blob([JSON.stringify(exportContent, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cheating_detection_export_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }, [data]);

    const getRiskColor = (score: number) => {
        if (score >= 0.75) return 'text-red-500';
        if (score >= 0.5) return 'text-orange-500';
        if (score >= 0.3) return 'text-yellow-500';
        return 'text-green-500';
    };

    const getRiskBgColor = (score: number) => {
        if (score >= 0.75) return 'bg-red-500';
        if (score >= 0.5) return 'bg-orange-500';
        if (score >= 0.3) return 'bg-yellow-500';
        return 'bg-green-500';
    };

    const formatTime = (ms: number) => {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`;
    };

    const formatDateTime = (timestamp?: string) => {
        if (!timestamp) return 'No date';
        const date = new Date(timestamp);

        // Format as: MM/DD/YYYY HH:MM AM/PM
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const year = date.getFullYear();

        let hours = date.getHours();
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12; // Convert to 12-hour format

        return `${month}/${day}/${year} ${hours}:${minutes} ${ampm}`;
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                            Admin Dashboard
                        </h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            Monitor sessions and review flagged submissions
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={exportData}
                            disabled={!data?.sessions.length}
                            className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
                        >
                            📥 Export Data
                        </button>
                        <Link
                            href="/"
                            className="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                        >
                            ← Back
                        </Link>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-6">
                {/* Error */}
                {error && (
                    <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <p className="text-red-600 dark:text-red-400">{error}</p>
                    </div>
                )}

                {/* Stats Cards */}
                {data && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-100 dark:border-gray-700">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Total Sessions</p>
                            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                                {data.total_sessions}
                            </p>
                        </div>
                        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-100 dark:border-gray-700">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Flagged</p>
                            <p className="text-3xl font-bold text-red-500 mt-1">
                                {data.flagged_sessions}
                            </p>
                        </div>
                        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-100 dark:border-gray-700">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Flag Rate</p>
                            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                                {data.total_sessions > 0
                                    ? ((data.flagged_sessions / data.total_sessions) * 100).toFixed(1)
                                    : 0}%
                            </p>
                        </div>
                        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-100 dark:border-gray-700">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Avg Risk Score</p>
                            <p className={`text-3xl font-bold mt-1 ${data.sessions.length > 0
                                ? getRiskColor(data.sessions.reduce((a, b) => a + b.risk_score, 0) / data.sessions.length)
                                : 'text-gray-900 dark:text-white'
                                }`}>
                                {data.sessions.length > 0
                                    ? (data.sessions.reduce((a, b) => a + b.risk_score, 0) / data.sessions.length * 100).toFixed(0)
                                    : 0}%
                            </p>
                        </div>
                    </div>
                )}

                {/* Simulate Buttons */}
                <div className="mb-6 flex gap-3 items-center">
                    <button
                        onClick={() => generateTestData('honest')}
                        disabled={simulating}
                        className="px-4 py-2 text-sm bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/50 disabled:opacity-50 transition-colors"
                    >
                        {simulating ? '⏳' : '➕'} Simulate Honest Sessions
                    </button>
                    <button
                        onClick={() => generateTestData('cheater')}
                        disabled={simulating}
                        className="px-4 py-2 text-sm bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 disabled:opacity-50 transition-colors"
                    >
                        {simulating ? '⏳' : '➕'} Simulate Cheating Sessions
                    </button>
                    <button
                        onClick={loadDashboard}
                        className="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                    >
                        🔄 Refresh
                    </button>

                    {/* Session Filter */}
                    <div className="ml-auto flex gap-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400 self-center">Show:</span>
                        {(['all', 'real', 'simulated'] as const).map((filter) => (
                            <button
                                key={filter}
                                onClick={() => setSessionFilter(filter)}
                                className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${sessionFilter === filter
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                    }`}
                            >
                                {filter.charAt(0).toUpperCase() + filter.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Main Content */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Sessions List */}
                    <div className="lg:col-span-1 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                        <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                            <div className="flex items-center justify-between">
                                <h2 className="font-semibold text-gray-900 dark:text-white">Sessions</h2>
                                <span
                                    title="Risk Formula: (Behavioral×0.35) + (Anomaly×0.35) + (Similarity×0.30)\nBehavioral = avg(Typing, Hesitation, Paste, Focus)"
                                    className="text-xs text-gray-500 dark:text-gray-400 cursor-help border-b border-dashed border-gray-400"
                                >
                                    ℹ️ Formula
                                </span>
                            </div>
                        </div>

                        {loading ? (
                            <div className="p-8 text-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                            </div>
                        ) : !data?.sessions.length ? (
                            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                                <p>No sessions yet.</p>
                                <p className="text-sm mt-2">Take an exam or simulate sessions.</p>
                            </div>
                        ) : (
                            <div className="max-h-[600px] overflow-y-auto divide-y divide-gray-100 dark:divide-gray-700">
                                {data.sessions
                                    .filter(s => {
                                        if (sessionFilter === 'real') return !s.is_simulated;
                                        if (sessionFilter === 'simulated') return s.is_simulated;
                                        return true;  // 'all' - show everything
                                    })
                                    .sort((a, b) => {
                                        // Sort by created_at (most recent first)
                                        const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
                                        const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
                                        return dateB - dateA;
                                    })
                                    .map((session) => (
                                        <div
                                            key={session.session_id}
                                            onClick={() => viewSession(session.session_id)}
                                            className={`px-4 py-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors ${selectedSession?.session_id === session.session_id
                                                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500'
                                                : ''
                                                }`}
                                        >
                                            <div className="flex items-center justify-between mb-1">
                                                <div className="flex flex-col">
                                                    <span className="font-mono text-xs text-gray-600 dark:text-gray-400">
                                                        {session.session_id.substring(0, 8)}...
                                                    </span>
                                                    <span className="text-xs text-gray-500 dark:text-gray-500 mt-0.5">
                                                        📅 {formatDateTime(session.created_at)}
                                                    </span>
                                                </div>
                                                {session.is_flagged && (
                                                    <span className="px-2 py-0.5 bg-red-500 text-white text-xs rounded font-medium">
                                                        FLAGGED
                                                    </span>
                                                )}
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full ${getRiskBgColor(session.risk_score)}`}
                                                        style={{ width: `${session.risk_score * 100}%` }}
                                                    />
                                                </div>
                                                <span className={`text-sm font-semibold ${getRiskColor(session.risk_score)}`}>
                                                    {(session.risk_score * 100).toFixed(0)}%
                                                </span>
                                            </div>
                                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                                {session.event_count} events
                                            </p>
                                        </div>
                                    ))}
                            </div>
                        )}
                    </div>

                    {/* Session Details */}
                    <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                        {selectedSession ? (
                            <>
                                {/* Tabs */}
                                <div className="flex border-b border-gray-100 dark:border-gray-700">
                                    {(['overview', 'timeline', 'features'] as const).map((tab) => (
                                        <button
                                            key={tab}
                                            onClick={() => setActiveTab(tab)}
                                            className={`px-4 py-3 text-sm font-medium transition-colors ${activeTab === tab
                                                ? 'text-blue-600 border-b-2 border-blue-600'
                                                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                                                }`}
                                        >
                                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                                        </button>
                                    ))}
                                </div>

                                <div className="p-6">
                                    {/* Overview Tab */}
                                    {activeTab === 'overview' && (
                                        <div className="space-y-6">
                                            {/* Overall Score */}
                                            <div>
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="text-sm text-gray-600 dark:text-gray-400">Overall Risk</span>
                                                    <span className={`text-2xl font-bold ${getRiskColor(selectedSession.overall_score)}`}>
                                                        {(selectedSession.overall_score * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full ${getRiskBgColor(selectedSession.overall_score)} transition-all`}
                                                        style={{ width: `${selectedSession.overall_score * 100}%` }}
                                                    />
                                                </div>
                                            </div>

                                            {/* Score Breakdown */}
                                            <div className="grid grid-cols-2 gap-4">
                                                {[
                                                    { label: 'Typing', score: selectedSession.typing_score, icon: '⌨️' },
                                                    { label: 'Hesitation', score: selectedSession.hesitation_score, icon: '⏸️' },
                                                    { label: 'Paste', score: selectedSession.paste_score, icon: '📋' },
                                                    { label: 'Focus', score: selectedSession.focus_score, icon: '👁️' },
                                                ].map((item) => (
                                                    <div key={item.label} className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <span>{item.icon}</span>
                                                            <span className="text-sm text-gray-600 dark:text-gray-400">{item.label}</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                                                                <div
                                                                    className={`h-full ${getRiskBgColor(item.score)}`}
                                                                    style={{ width: `${item.score * 100}%` }}
                                                                />
                                                            </div>
                                                            <span className={`text-sm font-semibold ${getRiskColor(item.score)}`}>
                                                                {(item.score * 100).toFixed(0)}%
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>

                                            {/* Flag Reasons */}
                                            {selectedSession.flag_reasons.length > 0 && (
                                                <div>
                                                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                                                        ⚠️ Flag Reasons
                                                    </h3>
                                                    <div className="space-y-2">
                                                        {selectedSession.flag_reasons.map((reason, i) => (
                                                            <div
                                                                key={i}
                                                                className="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg"
                                                            >
                                                                <span className="text-red-500">•</span>
                                                                <span className="text-sm text-red-700 dark:text-red-400">{reason}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Timeline Tab */}
                                    {activeTab === 'timeline' && (
                                        <div className="space-y-2 max-h-[500px] overflow-y-auto">
                                            {timeline.length === 0 ? (
                                                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                                                    No timeline events available
                                                </p>
                                            ) : (
                                                timeline.map((event, i) => (
                                                    <div
                                                        key={i}
                                                        className={`flex items-center gap-3 p-2 rounded-lg ${event.severity === 'high'
                                                            ? 'bg-red-50 dark:bg-red-900/20'
                                                            : event.severity === 'medium'
                                                                ? 'bg-yellow-50 dark:bg-yellow-900/20'
                                                                : 'bg-gray-50 dark:bg-gray-700/30'
                                                            }`}
                                                    >
                                                        <span className="text-xs text-gray-500 dark:text-gray-400 w-16">
                                                            {formatTime(event.timestamp)}
                                                        </span>
                                                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${event.type === 'paste' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                                                            event.type === 'focus' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                                                                'bg-gray-100 text-gray-700 dark:bg-gray-600 dark:text-gray-300'
                                                            }`}>
                                                            {event.type}
                                                        </span>
                                                        <span className="text-xs text-gray-600 dark:text-gray-400 flex-1">
                                                            {event.annotation || (event.data?.type as string) || '-'}
                                                        </span>
                                                        <span className="text-xs text-gray-400">
                                                            Q{event.question_id?.replace('q', '') || '?'}
                                                        </span>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    )}

                                    {/* Features Tab */}
                                    {activeTab === 'features' && selectedSession.features && (
                                        <div className="space-y-4">
                                            {Object.entries(selectedSession.features).map(([category, features]) => (
                                                <div key={category} className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4">
                                                    <h3 className="font-medium text-gray-800 dark:text-gray-200 mb-3 capitalize">
                                                        {category} Features
                                                    </h3>
                                                    <div className="grid grid-cols-2 gap-2 text-sm">
                                                        {Object.entries(features as Record<string, unknown>).map(([key, value]) => (
                                                            <div key={key} className="flex justify-between">
                                                                <span className="text-gray-600 dark:text-gray-400">
                                                                    {key.replace(/_/g, ' ')}
                                                                </span>
                                                                <span className="font-mono text-gray-800 dark:text-gray-200">
                                                                    {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                                                </span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <div className="flex items-center justify-center h-96 text-gray-500 dark:text-gray-400">
                                Select a session to view details
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
