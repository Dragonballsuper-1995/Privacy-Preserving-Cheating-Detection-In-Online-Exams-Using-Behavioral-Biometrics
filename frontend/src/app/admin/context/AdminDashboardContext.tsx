'use client';

import { createContext, useContext, useState, useCallback, useRef, useEffect, useMemo, ReactNode } from 'react';
import {
    getDashboardSummary,
    analyzeSession,
    getSessionTimeline,
    simulateSession,
    getStoredToken,
    clearStoredToken,
    getApiBase,
    checkHealth,
} from '@/lib/api';
import { useAdminWebSocket } from '@/hooks/useAdminWebSocket';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface SessionScore {
    typing: number;
    hesitation: number;
    paste: number;
    focus: number;
}

export interface SessionSummary {
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

export interface DashboardData {
    total_sessions: number;
    flagged_sessions: number;
    sessions: SessionSummary[];
}

export interface TimelineEvent {
    timestamp: number;
    type: string;
    data: Record<string, unknown>;
    question_id: string;
    annotation?: string;
    severity?: string;
}

export interface SessionDetails {
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

export type SessionFilter = 'all' | 'real' | 'simulated';
export type SortOrder = 'latest' | 'oldest' | 'highest_risk' | 'lowest_risk';

// ─── Context Shape ─────────────────────────────────────────────────────────────

interface AdminDashboardContextValue {
    // Data
    data: DashboardData | null;
    selectedSession: SessionDetails | null;
    timeline: TimelineEvent[];
    // UI State
    loading: boolean;
    initializing: boolean;
    error: string | null;
    activeTab: string;
    simulating: boolean;
    sessionFilter: SessionFilter;
    showFlaggedOnly: boolean;
    sortOrder: SortOrder;
    submittingReview: boolean;
    reviewNotes: string;
    // WebSocket
    wsConnected: boolean;
    wsAlerts: { message: string; session_id: string; severity: string; timestamp: string }[];
    // Derived
    filteredAndSortedSessions: SessionSummary[];
    getSessionAlias: (sessionId: string) => string;
    // Actions
    setActiveTab: (tab: string) => void;
    setSessionFilter: (f: SessionFilter) => void;
    setShowFlaggedOnly: (v: boolean | ((prev: boolean) => boolean)) => void;
    setSortOrder: (o: SortOrder) => void;
    setReviewNotes: (v: string) => void;
    loadDashboard: () => Promise<void>;
    viewSession: (sessionId: string) => Promise<void>;
    submitReview: (status: 'confirmed_cheating' | 'false_positive') => Promise<void>;
    generateTestData: (type: 'honest' | 'cheater') => Promise<void>;
    exportData: () => Promise<void>;
    exportCsv: () => Promise<void>;
    clearAlerts: () => void;
}

const AdminDashboardContext = createContext<AdminDashboardContextValue | null>(null);

export function useAdminDashboard() {
    const ctx = useContext(AdminDashboardContext);
    if (!ctx) throw new Error('useAdminDashboard must be used within AdminDashboardProvider');
    return ctx;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AdminDashboardProvider({ children }: { children: ReactNode }) {
    const [data, setData] = useState<DashboardData | null>(null);
    const [selectedSession, setSelectedSession] = useState<SessionDetails | null>(null);
    const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [initializing, setInitializing] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<string>('overview');
    const [simulating, setSimulating] = useState(false);
    const [sessionFilter, setSessionFilter] = useState<SessionFilter>('all');
    const [showFlaggedOnly, setShowFlaggedOnly] = useState(false);
    const [sortOrder, setSortOrder] = useState<SortOrder>('latest');
    const [submittingReview, setSubmittingReview] = useState(false);
    const [reviewNotes, setReviewNotes] = useState('');

    const { connected: wsConnected, alerts: wsAlerts, lastMessage, clearAlerts } = useAdminWebSocket();
    const hasLoadedRef = useRef(false);

    // ── Derived ──────────────────────────────────────────────────────────────

    const chronologicallySortedSessions = useMemo(() => {
        if (!data?.sessions) return [];
        return [...data.sessions].sort((a, b) => {
            const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
            const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
            return dateA - dateB;
        });
    }, [data?.sessions]);

    const getSessionAlias = useCallback((sessionId: string) => {
        const idx = chronologicallySortedSessions.findIndex(s => s.session_id === sessionId);
        return idx !== -1 ? `Session-${idx + 1}` : 'Unknown Session';
    }, [chronologicallySortedSessions]);

    const filteredAndSortedSessions = useMemo(() => {
        if (!data?.sessions) return [];
        return data.sessions
            .filter((s: SessionSummary) => {
                if (sessionFilter === 'real' && s.is_simulated) return false;
                if (sessionFilter === 'simulated' && !s.is_simulated) return false;
                if (showFlaggedOnly && !s.is_flagged) return false;
                return true;
            })
            .sort((a, b) => {
                const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
                const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
                if (sortOrder === 'latest') return dateB - dateA;
                if (sortOrder === 'oldest') return dateA - dateB;
                if (sortOrder === 'highest_risk') return b.risk_score - a.risk_score;
                if (sortOrder === 'lowest_risk') return a.risk_score - b.risk_score;
                return 0;
            });
    }, [data?.sessions, sessionFilter, sortOrder, showFlaggedOnly]);

    // ── Actions ──────────────────────────────────────────────────────────────

    const loadDashboard = useCallback(async () => {
        try {
            setLoading(true);
            const result = await getDashboardSummary();
            setData(result);
            setError(null);
        } catch (err: unknown) {
            if (err instanceof Error && err.message === 'UNAUTHORIZED') {
                setError('SESSION_EXPIRED. RE-AUTHENTICATING...');
                clearStoredToken();
                window.location.href = '/login/auto-admin';
            } else {
                setError('FAILED_TO_LOAD_DATA. CHECK_BACKEND_CONNECTION.');
                console.error(err);
            }
        } finally {
            setLoading(false);
            setInitializing(false);
        }
    }, []);

    const checkSystemHealth = useCallback(async () => {
        try {
            const health = await checkHealth();
            if (health.initialization_complete) {
                setInitializing(false);
                loadDashboard();
            } else {
                setInitializing(true);
                setTimeout(checkSystemHealth, 2000);
            }
        } catch {
            setError('FAILED_TO_CONNECT_TO_BACKEND. PLEASE_START_SERVER.');
            setInitializing(false);
            setLoading(false);
        }
    }, [loadDashboard]);

    const viewSession = useCallback(async (sessionId: string) => {
        try {
            const [details, timelineData] = await Promise.all([
                analyzeSession(sessionId),
                getSessionTimeline(sessionId),
            ]);
            setSelectedSession(details);
            setReviewNotes(details.review_notes || '');
            const sortedTimeline = ((timelineData.timeline || []) as TimelineEvent[]).sort(
                (a, b) => b.timestamp - a.timestamp
            );
            setTimeline(sortedTimeline);
        } catch (err) {
            console.error('Failed to load session:', err);
        }
    }, []);

    const submitReview = useCallback(async (status: 'confirmed_cheating' | 'false_positive') => {
        if (!selectedSession) return;
        setSubmittingReview(true);
        try {
            const token = getStoredToken();
            const res = await fetch(`${getApiBase()}/api/reviews/${selectedSession.session_id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
                body: JSON.stringify({ review_status: status, review_notes: reviewNotes }),
            });
            if (!res.ok) throw new Error('Failed to submit review');
            await loadDashboard();
            await viewSession(selectedSession.session_id);
        } catch (err) {
            console.error(err);
            alert('Failed to submit review');
        } finally {
            setSubmittingReview(false);
        }
    }, [selectedSession, reviewNotes, loadDashboard, viewSession]);

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
    }, [loadDashboard]);

    const exportData = useCallback(async () => {
        if (!data) return;
        const exportContent = {
            exported_at: new Date().toISOString(),
            summary: {
                total_sessions: data.total_sessions,
                flagged_sessions: data.flagged_sessions,
                flag_rate:
                    data.total_sessions > 0
                        ? ((data.flagged_sessions / data.total_sessions) * 100).toFixed(2) + '%'
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

    const exportCsv = useCallback(async () => {
        const token = getStoredToken();
        try {
            const res = await fetch(`${getApiBase()}/api/analysis/export/csv`, {
                headers: token ? { Authorization: `Bearer ${token}` } : {},
            });
            if (!res.ok) throw new Error('Export failed');
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'sessions_export.csv';
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error('CSV export failed:', err);
        }
    }, []);

    // ── Effects ───────────────────────────────────────────────────────────────

    useEffect(() => {
        if (!getStoredToken()) {
            window.location.href = '/login/auto-admin';
            return;
        }
        if (hasLoadedRef.current) return;
        hasLoadedRef.current = true;
        checkSystemHealth();
    }, [checkSystemHealth]);

    useEffect(() => {
        if (lastMessage) {
            if (lastMessage.type === 'status_update' || lastMessage.type === 'risk_update') {
                loadDashboard();
            } else if (lastMessage.type === 'live_events') {
                if (selectedSession && lastMessage.session_id === selectedSession.session_id) {
                    const newEvents = lastMessage.events.map((ev: { timestamp: number; event_type: string; data: Record<string, unknown>; question_id: string }) => ({
                        timestamp: ev.timestamp,
                        type: ev.event_type,
                        data: ev.data,
                        question_id: ev.question_id,
                        annotation: 'LIVE_STREAM',
                    }));
                    setTimeline(prev => {
                        const existingTimestamps = new Set(prev.map(e => e.timestamp));
                        const uniqueNew = newEvents.filter((e: TimelineEvent) => !existingTimestamps.has(e.timestamp));
                        return [...uniqueNew, ...prev].sort((a, b) => b.timestamp - a.timestamp);
                    });
                }
            }
        }
    }, [lastMessage, selectedSession, loadDashboard]);

    return (
        <AdminDashboardContext.Provider
            value={{
                data, selectedSession, timeline,
                loading, initializing, error,
                activeTab, simulating, sessionFilter, showFlaggedOnly, sortOrder,
                submittingReview, reviewNotes,
                wsConnected, wsAlerts,
                filteredAndSortedSessions, getSessionAlias,
                setActiveTab, setSessionFilter, setShowFlaggedOnly, setSortOrder, setReviewNotes,
                loadDashboard, viewSession, submitReview, generateTestData, exportData, exportCsv,
                clearAlerts,
            }}
        >
            {children}
        </AdminDashboardContext.Provider>
    );
}
