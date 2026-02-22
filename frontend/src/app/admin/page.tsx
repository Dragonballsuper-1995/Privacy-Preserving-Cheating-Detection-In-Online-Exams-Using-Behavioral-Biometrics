/**
 * Enhanced Admin Dashboard
 * Full-featured dashboard with risk visualization, timeline, and export
 */

'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, AlertTriangle, Download, ArrowLeft, RefreshCw, Layers, ShieldAlert, Cpu, Database, Eye, Terminal, Clock, CheckCircle2 } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getDashboardSummary, analyzeSession, getSessionTimeline, simulateSession, getStoredToken, getApiBase } from '@/lib/api';
import { useAdminWebSocket } from '@/hooks/useAdminWebSocket';
import { ThemeToggle } from '@/components/theme-toggle';

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
    is_simulated?: boolean;
    review_status?: 'pending' | 'confirmed_cheating' | 'false_positive';
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
    similarity_score: number;
    is_flagged: boolean;
    flag_reasons: string[];
    features?: Record<string, unknown>;
    review_status?: 'pending' | 'confirmed_cheating' | 'false_positive';
    reviewed_by?: string;
    review_notes?: string;
}

export default function AdminDashboard() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [selectedSession, setSelectedSession] = useState<SessionDetails | null>(null);
    const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState<string>('overview'); const [simulating, setSimulating] = useState(false);
    const [sessionFilter, setSessionFilter] = useState<'all' | 'real' | 'simulated'>('all');
    const [submittingReview, setSubmittingReview] = useState(false);
    const [reviewNotes, setReviewNotes] = useState('');

    // Live WebSocket connection for real-time updates
    const { connected: wsConnected, alerts: wsAlerts, lastMessage, clearAlerts } = useAdminWebSocket();

    const hasLoadedRef = useRef(false);

    useEffect(() => {
        if (hasLoadedRef.current) return;
        hasLoadedRef.current = true;
        loadDashboard();
    }, []);

    useEffect(() => {
        if (lastMessage) {
            if (lastMessage.type === 'status_update' || lastMessage.type === 'risk_update') {
                loadDashboard();
            } else if (lastMessage.type === 'live_events') {
                // If this is the currently selected session, inject into timeline
                if (selectedSession && lastMessage.session_id === selectedSession.session_id) {
                    const newEvents = lastMessage.events.map((ev: any) => ({
                        timestamp: ev.timestamp,
                        type: ev.event_type,
                        data: ev.data,
                        question_id: ev.question_id,
                        annotation: 'LIVE_STREAM',
                    }));

                    setTimeline(prev => {
                        // Avoid duplicates by timestamp
                        const existingTimestamps = new Set(prev.map(e => e.timestamp));
                        const uniqueNew = newEvents.filter((e: any) => !existingTimestamps.has(e.timestamp));
                        // Prepend them to the top (or basically sort descending by timestamp later)
                        return [...uniqueNew, ...prev].sort((a, b) => b.timestamp - a.timestamp);
                    });
                }
            }
        }
    }, [lastMessage, selectedSession]);

    async function loadDashboard() {
        try {
            setLoading(true);
            const result = await getDashboardSummary();
            setData(result);
        } catch (err) {
            setError('FAILED_TO_LOAD_DATA. CHECK_BACKEND_CONNECTION.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    async function viewSession(sessionId: string) {
        try {
            const details = await analyzeSession(sessionId);
            setSelectedSession(details);
            setReviewNotes(details.review_notes || '');

            const timelineData = await getSessionTimeline(sessionId);
            // Default sort timeline descending (newest first)
            const sortedTimeline = ((timelineData.timeline || []) as TimelineEvent[]).sort((a, b) => b.timestamp - a.timestamp);
            setTimeline(sortedTimeline);
        } catch (err) {
            console.error('Failed to load session:', err);
        }
    }

    async function submitReview(status: 'confirmed_cheating' | 'false_positive') {
        if (!selectedSession) return;
        setSubmittingReview(true);
        try {
            const token = getStoredToken();
            const res = await fetch(`${getApiBase()}/api/reviews/${selectedSession.session_id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    review_status: status,
                    review_notes: reviewNotes
                })
            });

            if (!res.ok) throw new Error('Failed to submit review');

            // Reload dashboard and the selected session
            await loadDashboard();
            await viewSession(selectedSession.session_id);
        } catch (err) {
            console.error(err);
            alert('Failed to submit review');
        } finally {
            setSubmittingReview(false);
        }
    }

    const generateTestData = useCallback(async (type: 'honest' | 'cheater') => {
        setSimulating(true);
        try {
            await simulateSession(type === 'cheater', 3, 6);
            await loadDashboard();
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
        if (score >= 0.75) return 'text-destructive';
        if (score >= 0.5) return 'text-orange-500 dark:text-orange-400';
        if (score >= 0.3) return 'text-yellow-600 dark:text-yellow-400';
        return 'text-green-600 dark:text-green-400';
    };

    const getRiskBgColor = (score: number) => {
        if (score >= 0.75) return 'bg-destructive/10 text-destructive';
        if (score >= 0.5) return 'bg-orange-500/10 text-orange-600 dark:text-orange-400';
        if (score >= 0.3) return 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400';
        return 'bg-green-500/10 text-green-600 dark:text-green-400';
    };

    const formatTime = (ms: number) => {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`;
    };

    const formatDateTime = (timestamp?: string) => {
        if (!timestamp) return 'UNKNOWN_TIME';
        const date = new Date(timestamp);
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const year = date.getFullYear();
        let hours = date.getHours();
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12;
        return `${month}/${day}/${year} ${hours}:${minutes}${ampm}`;
    };

    return (
        <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background pb-20">
            {/* Header */}
            <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-border/50">
                <div className="w-full mx-auto px-4 md:px-8 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="p-2 rounded-lg border border-border/50 bg-card hover:bg-secondary transition-colors">
                            <ArrowLeft className="w-5 h-5 text-muted-foreground" />
                        </Link>
                        <div>
                            <h1 className="font-display text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-3">
                                <Activity className="w-7 h-7 text-primary" />
                                Admin Terminal
                            </h1>
                            <p className="font-sans text-xs font-medium text-muted-foreground tracking-wider uppercase">Global Monitoring & Analysis</p>
                        </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                        {/* WebSocket connection indicator */}
                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold tracking-wider uppercase transition-colors ${wsConnected ? 'border-primary/20 bg-primary/10 text-primary' : 'border-destructive/20 bg-destructive/10 text-destructive'}`}>
                            <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-primary shadow-[0_0_8px_rgba(var(--primary),0.6)] animate-pulse' : 'bg-destructive'}`} />
                            {wsConnected ? 'Live Link Active' : 'System Offline'}
                        </div>

                        <ThemeToggle />

                        <Link href="/admin/models" className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border/50 bg-card text-foreground font-sans font-semibold text-sm hover:bg-secondary transition-colors shadow-sm">
                            <Cpu className="w-4 h-4" />
                            ML Models
                        </Link>

                        <button onClick={exportData} disabled={!data?.sessions.length}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground font-sans font-semibold text-sm hover:bg-primary/90 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]">
                            <Download className="w-4 h-4" />
                            JSON
                        </button>

                        <button onClick={async () => {
                            const token = getStoredToken();
                            try {
                                const res = await fetch(`${getApiBase()}/api/analysis/export/csv`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
                                if (!res.ok) throw new Error('Export failed');
                                const blob = await res.blob();
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = 'sessions_export.csv';
                                a.click();
                                URL.revokeObjectURL(url);
                            } catch (err) { console.error('CSV export failed:', err); }
                        }}
                            disabled={!data?.sessions.length}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border/50 bg-card text-foreground font-sans font-semibold text-sm hover:bg-secondary transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]">
                            <Download className="w-4 h-4" />
                            CSV
                        </button>
                    </div>
                </div>
            </header>

            <main className="w-full mx-auto px-4 md:px-8 py-8">
                {/* WebSocket Alerts */}
                <AnimatePresence>
                    {wsAlerts.length > 0 && (
                        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mb-8 space-y-3">
                            <div className="flex items-center justify-between border-b border-border/50 pb-2">
                                <h3 className="font-display font-semibold tracking-wider text-destructive uppercase text-sm">System Alerts</h3>
                                <button onClick={clearAlerts} className="font-sans text-xs font-semibold uppercase text-muted-foreground hover:text-foreground transition-colors">Acknowledge All</button>
                            </div>
                            {wsAlerts.slice(-5).map((alert, i) => (
                                <motion.div key={i} initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
                                    className={`p-4 rounded-xl border flex items-start justify-between shadow-sm ${alert.severity === 'critical' ? 'bg-destructive/10 border-destructive/20' : 'bg-yellow-500/10 border-yellow-500/20'}`}>
                                    <div className="flex items-start gap-3">
                                        <ShieldAlert className={`w-5 h-5 shrink-0 ${alert.severity === 'critical' ? 'text-destructive' : 'text-yellow-600 dark:text-yellow-400'}`} />
                                        <div>
                                            <p className={`font-sans text-sm font-semibold tracking-wide ${alert.severity === 'critical' ? 'text-destructive' : 'text-yellow-700 dark:text-yellow-300'}`}>{alert.message}</p>
                                            <p className="font-mono text-xs text-muted-foreground mt-1">Session ID: {alert.session_id.substring(0, 12)}</p>
                                        </div>
                                    </div>
                                    <span className="font-sans font-medium text-xs text-muted-foreground bg-background/50 px-2 py-1 rounded-md">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Error */}
                {error && (
                    <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8 p-4 rounded-xl bg-destructive/10 text-destructive border border-destructive/20 flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5" />
                        <p className="font-sans text-sm font-semibold tracking-wide">{error}</p>
                    </motion.div>
                )}

                {/* Stats Cards */}
                {data && (
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-10">
                        {[
                            { label: 'Total Sessions', value: data!.total_sessions },
                            { label: 'Flagged Sessions', value: data!.flagged_sessions, alert: true },
                            { label: 'Global Flag Rate', value: data!.total_sessions > 0 ? ((data!.flagged_sessions / data!.total_sessions) * 100).toFixed(1) + '%' : '0%' },
                            {
                                label: 'Avg Risk Score',
                                value: (data!.sessions.length > 0 ? (data!.sessions.reduce((a, b) => a + b.risk_score, 0) / data!.sessions.length * 100).toFixed(0) : 0) + '%',
                                color: data!.sessions.length > 0 ? getRiskColor(data!.sessions.reduce((a, b) => a + b.risk_score, 0) / data!.sessions.length) : ''
                            }
                        ].map((stat, i) => (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1, type: "spring", stiffness: 100 }}
                                whileHover={{ scale: 1.02, y: -2 }}
                                key={i}
                                className={`rounded-2xl border border-border/50 bg-card p-5 md:p-6 shadow-sm hover:shadow-lg hover:border-primary/20 transition-all duration-300 ${stat.alert && stat.value > 0 ? 'relative overflow-hidden' : ''}`}
                            >
                                {stat.alert && stat.value > 0 && <div className="absolute top-0 right-0 w-16 h-16 bg-destructive/10 rounded-bl-full pointer-events-none" />}
                                <p className="font-sans text-xs md:text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-2 relative z-10">{stat.label}</p>
                                <p className={`font-display text-3xl md:text-5xl font-bold tracking-tight relative z-10 ${stat.alert && stat.value > 0 ? 'text-destructive' : ''} ${stat.color || 'text-foreground'}`}>
                                    {stat.value}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                )}

                {/* Controls */}
                <div className="mb-8 flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between p-4 rounded-xl border border-border/50 bg-card shadow-sm">
                    <div className="flex flex-wrap gap-3">
                        <Button onClick={() => generateTestData('honest')} disabled={simulating} variant="outline"
                            className="text-green-600 dark:text-green-400 border-green-500/50 bg-green-500/10 hover:bg-green-500/20 h-10 px-4 py-2.5">
                            {simulating ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Database className="w-4 h-4 mr-2" />}
                            Simulate Honest
                        </Button>
                        <Button onClick={() => generateTestData('cheater')} disabled={simulating} variant="outline"
                            className="text-destructive border-destructive/50 bg-destructive/10 hover:bg-destructive/20 h-10 px-4 py-2.5">
                            {simulating ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Database className="w-4 h-4 mr-2" />}
                            Simulate Cheating
                        </Button>
                    </div>

                    <div className="flex items-center gap-3">
                        <button onClick={loadDashboard}
                            className="p-2.5 rounded-lg border border-border/50 bg-secondary/50 hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground" title="Refresh Data">
                            <RefreshCw className="w-4 h-4" />
                        </button>
                        <div className="flex rounded-lg border border-border/50 p-1 bg-secondary/20">
                            {(['all', 'real', 'simulated'] as const).map((filter) => (
                                <button key={filter} onClick={() => setSessionFilter(filter)}
                                    className={`px-4 py-1.5 rounded-md font-sans text-xs font-semibold uppercase tracking-wider transition-colors ${sessionFilter === filter ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}>
                                    {filter}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">

                    {/* Sessions List (Sidebar) */}
                    <div className="lg:col-span-4 flex flex-col rounded-2xl border border-border/50 bg-card shadow-sm h-[600px] lg:h-[800px] overflow-hidden">
                        <div className="p-4 border-b border-border/50 bg-secondary/50 flex items-center justify-between">
                            <h2 className="font-display font-semibold tracking-wider text-sm uppercase flex items-center gap-2">
                                <Activity className="w-4 h-4 text-primary" />
                                Active Sessions
                            </h2>
                            <span className="font-sans text-xs bg-background/80 text-foreground px-2 py-1 rounded-md font-semibold shadow-sm border border-border/50">
                                {data?.sessions.length || 0} Total
                            </span>
                        </div>

                        <div className="flex-1 overflow-y-auto bg-background/50 custom-scrollbar">
                            {loading ? (
                                <div className="p-8 flex justify-center">
                                    <RefreshCw className="w-8 h-8 animate-spin text-primary" />
                                </div>
                            ) : !data?.sessions.length ? (
                                <div className="p-8 text-center font-sans text-sm font-medium text-muted-foreground uppercase tracking-wider">
                                    No Sessions Detected
                                </div>
                            ) : (
                                <div className="divide-y divide-border/50">
                                    {data?.sessions
                                        .filter(s => {
                                            if (sessionFilter === 'real') return !s.is_simulated;
                                            if (sessionFilter === 'simulated') return s.is_simulated;
                                            return true;
                                        })
                                        .sort((a, b) => {
                                            const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
                                            const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
                                            return dateB - dateA;
                                        })
                                        .map((session) => (
                                            <button key={session.session_id} onClick={() => viewSession(session.session_id)}
                                                className={`w-full text-left p-4 hover:bg-secondary/80 transition-all duration-300 hover:shadow-sm hover:pl-5 ${selectedSession?.session_id === session.session_id ? 'bg-secondary border-l-4 border-l-primary' : 'border-l-4 border-l-transparent'}`}>
                                                <div className="flex items-center justify-between mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-mono text-sm font-semibold tracking-wide">
                                                            {session.session_id.substring(0, 8)}
                                                        </span>
                                                        {session.review_status === 'confirmed_cheating' && (
                                                            <div title="Confirmed Cheating"><ShieldAlert className="w-4 h-4 text-destructive" /></div>
                                                        )}
                                                        {session.review_status === 'false_positive' && (
                                                            <div className="w-4 h-4 rounded-full border-2 border-green-500 text-green-500 flex items-center justify-center font-bold text-[10px]" title="False Positive">✓</div>
                                                        )}
                                                    </div>
                                                    {session.is_flagged && session.review_status === 'pending' && (
                                                        <span className="px-2 py-0.5 rounded-md bg-destructive/10 text-destructive border border-destructive/20 font-sans text-[10px] font-bold uppercase tracking-widest shadow-sm">Flagged</span>
                                                    )}
                                                </div>

                                                <div className="flex items-center gap-3 mb-3">
                                                    <div className="flex-1 h-2.5 rounded-full bg-secondary overflow-hidden">
                                                        <div className={`h-full rounded-full transition-all duration-500 ${getRiskBgColor(session.risk_score).split(' ')[0]}`} style={{ width: `${session.risk_score * 100}%` }} />
                                                    </div>
                                                    <span className={`font-display text-sm font-bold w-10 text-right ${getRiskColor(session.risk_score)}`}>
                                                        {(session.risk_score * 100).toFixed(0)}%
                                                    </span>
                                                </div>

                                                <div className="flex items-center justify-between text-muted-foreground">
                                                    <span className="font-sans text-xs font-medium uppercase tracking-wider">{formatDateTime(session.created_at)}</span>
                                                    <span className="font-sans text-xs font-semibold uppercase">{session.event_count} Events</span>
                                                </div>
                                            </button>
                                        ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Session Details (Main Area) */}
                    <div className="lg:col-span-8 flex flex-col rounded-2xl border border-border/50 bg-card shadow-sm h-[600px] lg:h-[800px] overflow-hidden">
                        {selectedSession ? (
                            <>
                                {/* Header Info */}
                                <div className="p-6 border-b border-border/50 bg-secondary/30">
                                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                                        <div>
                                            <p className="font-sans text-xs text-primary font-semibold uppercase tracking-wider mb-1">Target Analysis</p>
                                            <div className="flex items-center gap-3">
                                                <h2 className="font-mono text-2xl font-bold tracking-tight">{selectedSession!.session_id}</h2>
                                                {selectedSession!.review_status === 'confirmed_cheating' && (
                                                    <span className="px-2.5 py-1 rounded-md bg-destructive/10 text-destructive border border-destructive/20 font-sans text-xs font-bold uppercase tracking-wider shadow-sm">Confirmed</span>
                                                )}
                                                {selectedSession!.review_status === 'false_positive' && (
                                                    <span className="px-2.5 py-1 rounded-md bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20 font-sans text-xs font-bold uppercase tracking-wider shadow-sm">False Positive</span>
                                                )}
                                            </div>
                                        </div>
                                        <div className={`px-5 py-3 rounded-xl border border-border/50 font-display text-xl font-bold shadow-sm ${getRiskBgColor(selectedSession!.overall_score)}`}>
                                            Risk Quotient: {(selectedSession!.overall_score * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                </div>

                                {/* Tabs */}
                                <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col h-full overflow-hidden">
                                    <div className="border-b border-border/50 bg-secondary/20 p-2">
                                        <TabsList className="flex w-full bg-transparent p-0 gap-2 h-auto rounded-lg">
                                            {(['overview', 'timeline', 'features', 'review'] as const).map((tab) => {
                                                const icons = { overview: Eye, timeline: Clock, features: Cpu, review: CheckCircle2 };
                                                const Icon = icons[tab];
                                                return (
                                                    <TabsTrigger key={tab} value={tab} className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-sans font-semibold text-sm uppercase tracking-wider transition-all data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm text-muted-foreground hover:text-foreground">
                                                        <Icon className="w-4 h-4" />
                                                        <span className="hidden sm:inline">{tab}</span>
                                                    </TabsTrigger>
                                                );
                                            })}
                                        </TabsList>
                                    </div>

                                    <div className="flex-1 overflow-y-auto p-6 md:p-8 bg-background relative custom-scrollbar">

                                        {/* Overview Tab */}
                                        <TabsContent value="overview" className="mt-0 outline-none">
                                            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8 relative z-10">

                                                {/* Score Breakdown (Moved ABOVE Flag Reasons) */}
                                                <div>
                                                    <h3 className="font-sans text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Subsystem Analysis</h3>
                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                        {[
                                                            { label: 'Keystroke Dynamics', score: selectedSession!.typing_score },
                                                            { label: 'Hesitation Metric', score: selectedSession!.hesitation_score },
                                                            { label: 'Clipboard Activity', score: selectedSession!.paste_score },
                                                            { label: 'Window Focus Loss', score: selectedSession!.focus_score },
                                                            { label: 'Content Similarity', score: selectedSession!.similarity_score !== undefined ? selectedSession!.similarity_score : 0 },
                                                        ].map((item) => (
                                                            <div key={item.label} className="p-5 rounded-xl border border-border/50 bg-card flex flex-col justify-between h-28 shadow-sm hover:shadow-md transition-shadow">
                                                                <div className="flex justify-between items-center mb-3">
                                                                    <span className="font-sans text-xs font-bold uppercase tracking-wider text-muted-foreground">{item.label}</span>
                                                                    <span className={`font-display text-xl font-bold ${getRiskColor(item.score)}`}>
                                                                        {(item.score * 100).toFixed(0)}%
                                                                    </span>
                                                                </div>
                                                                <div className="w-full h-2 rounded-full border border-border/50 bg-secondary overflow-hidden">
                                                                    <div className={`h-full rounded-full transition-all duration-1000 ${getRiskBgColor(item.score).split(' ')[0]}`} style={{ width: `${item.score * 100}%` }} />
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>

                                                {/* Flag Reasons */}
                                                {selectedSession!.flag_reasons && selectedSession!.flag_reasons.length > 0 && (
                                                    <div className="p-6 rounded-2xl border border-destructive/20 bg-destructive/5 shadow-sm">
                                                        <h3 className="font-display font-semibold text-lg text-destructive tracking-widest uppercase flex items-center gap-2 mb-4">
                                                            <AlertTriangle className="w-5 h-5" />
                                                            Anomaly Triggers
                                                        </h3>
                                                        <ul className="space-y-3 font-sans text-sm font-medium text-foreground">
                                                            {selectedSession!.flag_reasons.map((reason, i) => (
                                                                <li key={i} className="flex items-start gap-3 bg-background/50 p-3 rounded-lg border border-destructive/10">
                                                                    <span className="text-destructive mt-0.5"><Activity className="w-4 h-4" /></span>
                                                                    <span className="uppercase tracking-wide">{reason}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </motion.div>
                                        </TabsContent>

                                        {/* Timeline Tab */}
                                        <TabsContent value="timeline" className="mt-0 outline-none">
                                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="relative z-10">
                                                {timeline.length === 0 ? (
                                                    <div className="text-center py-20 font-sans text-sm text-muted-foreground font-semibold uppercase tracking-widest">
                                                        No Telemetry Data Found
                                                    </div>
                                                ) : (
                                                    <div className="space-y-4">
                                                        {timeline.map((event, i) => (
                                                            <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} whileHover={{ scale: 1.01, x: 2 }} key={i} className="flex flex-col md:flex-row rounded-xl border border-border/50 bg-card shadow-sm overflow-hidden hover:border-primary/30 hover:shadow-md transition-all duration-300">
                                                                <div className="flex items-center md:justify-center md:w-28 p-3 border-b md:border-b-0 md:border-r border-border/50 bg-secondary/50 font-mono text-xs font-semibold text-muted-foreground">
                                                                    {formatTime(event.timestamp)}
                                                                </div>
                                                                <div className="flex-1 p-4 flex items-center justify-between gap-4">
                                                                    <div className="flex items-center gap-4">
                                                                        <span className={`px-2.5 py-1 rounded-md border font-sans text-[10px] font-bold uppercase tracking-wider ${event.type === 'paste' ? 'bg-destructive/10 border-destructive/20 text-destructive' : event.type === 'focus' ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-600 dark:text-yellow-400' : 'bg-primary/10 border-primary/20 text-primary'}`}>
                                                                            {event.type}
                                                                        </span>
                                                                        <span className="font-sans text-sm font-medium tracking-wide">
                                                                            {event.annotation || (event.data?.type as string) || 'Unknown Event'}
                                                                        </span>
                                                                    </div>
                                                                    <span className="font-mono text-xs font-medium text-muted-foreground bg-secondary/50 px-2 py-1 rounded-md border border-border/50">
                                                                        Q: {event.question_id?.replace('q', '') || '?'}
                                                                    </span>
                                                                </div>
                                                            </motion.div>
                                                        ))}
                                                    </div>
                                                )}
                                            </motion.div>
                                        </TabsContent>

                                        {/* Features Tab */}
                                        <TabsContent value="features" className="mt-0 outline-none">
                                            {selectedSession!.features && (
                                                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8 relative z-10">
                                                    <Accordion type="multiple" className="w-full space-y-4">
                                                        {Object.entries(selectedSession!.features).map(([category, features], idx) => (
                                                            <AccordionItem key={category} value={`item-${idx}`} className="rounded-xl border border-border/50 bg-card overflow-hidden shadow-sm">
                                                                <AccordionTrigger className="px-5 py-3 hover:no-underline hover:bg-secondary/50 font-sans text-sm font-semibold uppercase tracking-widest text-foreground data-[state=open]:border-b data-[state=open]:border-border/50 data-[state=open]:bg-secondary/50 transition-colors">
                                                                    {category} Vectors
                                                                </AccordionTrigger>
                                                                <AccordionContent className="p-0">
                                                                    <div className="grid grid-cols-1 sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-border/50 bg-background">
                                                                        {Object.entries((features || {}) as Record<string, unknown>).map(([key, value]) => (
                                                                            <div key={key} className="flex justify-between items-center p-4 border-b border-border/50 sm:border-b-0 hover:bg-secondary/20 transition-colors">
                                                                                <span className="font-sans text-xs font-medium uppercase tracking-wider text-muted-foreground pr-4">
                                                                                    {key.replace(/_/g, ' ')}
                                                                                </span>
                                                                                <span className="font-mono text-sm font-semibold text-right truncate text-foreground">
                                                                                    {typeof value === 'number' ? value.toFixed(3) : String(value)}
                                                                                </span>
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                </AccordionContent>
                                                            </AccordionItem>
                                                        ))}
                                                    </Accordion>
                                                </motion.div>
                                            )}
                                        </TabsContent>

                                        {/* Review Tab */}
                                        <TabsContent value="review" className="mt-0 outline-none">
                                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8 relative z-10">
                                                {/* Human Review Actions */}
                                                <div className="p-6 rounded-xl border border-border/50 bg-secondary/30 shadow-sm space-y-4">
                                                    <h3 className="font-display font-semibold text-lg text-foreground tracking-widest uppercase flex items-center gap-2">
                                                        <ShieldAlert className="w-5 h-5 text-primary" />
                                                        Human-in-the-Loop Review
                                                    </h3>
                                                    <textarea
                                                        value={reviewNotes}
                                                        onChange={(e) => setReviewNotes(e.target.value)}
                                                        placeholder="Enter reviewer notes here..."
                                                        className="w-full h-32 p-4 rounded-xl bg-background border border-border/50 font-sans text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow shadow-sm"
                                                    />
                                                    <div className="flex flex-col sm:flex-row gap-4">
                                                        <Button
                                                            disabled={submittingReview}
                                                            onClick={() => submitReview('confirmed_cheating')}
                                                            variant="destructive"
                                                            className="flex-1 h-12 font-sans text-sm font-bold uppercase tracking-wider shadow-sm transition-all active:scale-[0.98]"
                                                        >
                                                            Confirm Violation
                                                        </Button>
                                                        <Button
                                                            disabled={submittingReview}
                                                            onClick={() => submitReview('false_positive')}
                                                            className="flex-1 h-12 font-sans text-sm font-bold uppercase tracking-wider shadow-sm transition-all active:scale-[0.98] bg-green-600 hover:bg-green-700 text-white"
                                                        >
                                                            Dismiss Flag
                                                        </Button>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        </TabsContent>
                                    </div>
                                </Tabs>
                            </>
                        ) : (
                            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-muted-foreground bg-background/50">
                                <Terminal className="w-16 h-16 mb-4 opacity-20" />
                                <p className="font-sans text-lg font-semibold uppercase tracking-widest">Awaiting Selection</p>
                                <p className="font-sans text-xs font-medium mt-2 uppercase tracking-wide opacity-70">Select target from roster to initiate analysis</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
