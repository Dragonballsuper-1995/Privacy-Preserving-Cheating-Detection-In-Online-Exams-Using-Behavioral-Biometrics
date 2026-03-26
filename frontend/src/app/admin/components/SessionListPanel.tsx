'use client';

import { Activity, RefreshCw, ShieldAlert, Clock } from 'lucide-react';
import { useAdminDashboard } from '../context/AdminDashboardContext';
import type { SortOrder } from '../context/AdminDashboardContext';

function getRiskColor(score: number) {
    if (score >= 0.75) return 'text-destructive';
    if (score >= 0.5) return 'text-orange-500 dark:text-orange-400';
    if (score >= 0.3) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-green-600 dark:text-green-400';
}

function getRiskBgColor(score: number) {
    if (score >= 0.75) return 'bg-destructive/10 text-destructive';
    if (score >= 0.5) return 'bg-orange-500/10 text-orange-600 dark:text-orange-400';
    if (score >= 0.3) return 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400';
    return 'bg-green-500/10 text-green-600 dark:text-green-400';
}

function formatDateTime(timestamp?: string) {
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
}

export function SessionListPanel() {
    const {
        loading, filteredAndSortedSessions, selectedSession, sortOrder,
        setSortOrder, viewSession, getSessionAlias,
    } = useAdminDashboard();

    return (
        <div className="lg:col-span-4 flex flex-col glass-panel h-full overflow-hidden border border-white/5">
            {/* Header */}
            <div className="p-4 border-b border-border/50 bg-secondary/50 flex items-center justify-between">
                <h2 className="font-display font-semibold tracking-wider text-sm uppercase flex items-center gap-2">
                    <Activity className="w-4 h-4 text-primary" />
                    Active Sessions
                </h2>
                <span className="font-sans text-xs bg-background/80 text-foreground px-2 py-1 rounded-md font-semibold shadow-sm border border-border/50">
                    {filteredAndSortedSessions.length} sessions
                </span>
            </div>

            {/* Sorting Controls */}
            <div className="px-4 py-2 border-b border-border/50 bg-secondary/20 flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                    <Clock className="w-3 h-3" /> Sort by
                </div>
                <select
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value as SortOrder)}
                    className="bg-transparent border-none text-[10px] font-bold uppercase tracking-widest text-primary focus:ring-0 cursor-pointer outline-none"
                >
                    <option value="latest" className="bg-background">Latest session</option>
                    <option value="oldest" className="bg-background">Oldest session</option>
                    <option value="highest_risk" className="bg-background">Highest risk</option>
                    <option value="lowest_risk" className="bg-background">Lowest risk</option>
                </select>
            </div>

            {/* Session List */}
            <div className="flex-1 overflow-y-auto bg-background/50 custom-scrollbar">
                {loading ? (
                    <div className="p-8 flex justify-center">
                        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
                    </div>
                ) : !filteredAndSortedSessions.length ? (
                    <div className="p-8 text-center font-sans text-sm font-medium text-muted-foreground uppercase tracking-wider">
                        No Sessions Detected
                    </div>
                ) : (
                    <div className="divide-y divide-border/50">
                        {filteredAndSortedSessions.map((session) => (
                            <button
                                key={session.session_id}
                                onClick={() => viewSession(session.session_id)}
                                className={`w-full text-left p-4 hover:bg-secondary/80 hover:pl-5 ${
                                    selectedSession?.session_id === session.session_id
                                        ? 'bg-secondary border-l-4 border-l-primary'
                                        : 'border-l-4 border-l-transparent'
                                }`}
                                style={{ transition: 'background 150ms ease, padding-left 150ms ease' }}
                            >
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center gap-2">
                                        <span className="font-mono text-sm font-semibold tracking-wide">
                                            {getSessionAlias(session.session_id)}
                                        </span>
                                        {session.review_status === 'confirmed_cheating' && (
                                            <div title="Confirmed Cheating">
                                                <ShieldAlert className="w-4 h-4 text-destructive" />
                                            </div>
                                        )}
                                        {session.review_status === 'false_positive' && (
                                            <div className="w-4 h-4 rounded-full border-2 border-green-500 text-green-500 flex items-center justify-center font-bold text-[10px]" title="False Positive">✓</div>
                                        )}
                                    </div>
                                    {session.is_flagged && session.review_status === 'pending' && (
                                        <span className="px-2 py-0.5 rounded-md bg-destructive/10 text-destructive border border-destructive/20 font-sans text-[10px] font-bold uppercase tracking-widest shadow-sm">
                                            Flagged
                                        </span>
                                    )}
                                </div>

                                <div className="flex items-center gap-3 mb-3">
                                    <div className="flex-1 h-2.5 rounded-full bg-secondary overflow-hidden">
                                        <div
                                            className={`h-full rounded-full transition-all duration-500 ${getRiskBgColor(session.risk_score).split(' ')[0]}`}
                                            style={{ width: `${session.risk_score * 100}%` }}
                                        />
                                    </div>
                                    <span className={`font-display text-sm font-bold w-10 text-right ${getRiskColor(session.risk_score)}`}>
                                        {(session.risk_score * 100).toFixed(0)}%
                                    </span>
                                </div>

                                <div className="flex items-center justify-between text-muted-foreground">
                                    <span className="font-sans text-xs font-medium uppercase tracking-wider">
                                        {formatDateTime(session.created_at)}
                                    </span>
                                    <span className="font-sans text-xs font-semibold uppercase">
                                        {session.event_count} Events
                                    </span>
                                </div>
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
