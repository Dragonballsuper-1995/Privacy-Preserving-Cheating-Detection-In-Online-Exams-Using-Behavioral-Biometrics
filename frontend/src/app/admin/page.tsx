/**
 * Admin Dashboard — Refactored for Performance
 *
 * This page is a thin server-compatible shell.
 * All state + logic lives in AdminDashboardContext (client).
 * Interactive UI is split into focused client island components.
 *
 * Performance gains:
 *  - Static sidebar nav, header structure rendered without forcing full-tree hydration
 *  - 'use client' boundary pushed to leaf-level islands via context
 *  - Framer-motion, Radix Tabs/Accordion only loaded when the detail panel mounts
 */

'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Activity, AlertTriangle, Download, ArrowLeft, Cpu, Database, Eye } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';
import { AdminDashboardProvider, useAdminDashboard } from './context/AdminDashboardContext';
import { WebSocketAlerts } from './components/WebSocketAlerts';
import { ControlsBar } from './components/ControlsBar';
import { SessionListPanel } from './components/SessionListPanel';
import { SessionDetailPanel } from './components/SessionDetailPanel';

// ─── Inner shell (consumes context) ──────────────────────────────────────────

function DashboardShell() {
    const {
        data, initializing, error, wsConnected,
        showFlaggedOnly, setShowFlaggedOnly, setSessionFilter,
        exportData, exportCsv,
    } = useAdminDashboard();

    // System Initializing screen
    if (initializing) {
        return (
            <div className="h-screen flex items-center justify-center bg-[#0d0a1b] text-foreground">
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center space-y-6 p-8">
                    <div className="w-16 h-16 rounded-2xl bg-primary/20 border border-primary/30 flex items-center justify-center mx-auto shadow-[0_0_30px_rgba(195,180,253,0.3)]">
                        <Activity className="w-8 h-8 text-primary animate-pulse" />
                    </div>
                    <div>
                        <h2 className="font-display text-2xl font-bold tracking-tight text-foreground">System Initializing</h2>
                        <p className="font-mono text-xs text-primary/70 tracking-widest uppercase mt-2">Loading ML models & backend services...</p>
                    </div>
                    <div className="flex gap-2 justify-center">
                        {[0, 1, 2].map(i => (
                            <div
                                key={i}
                                className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"
                                style={{ animationDelay: `${i * 0.2}s` }}
                            />
                        ))}
                    </div>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="h-screen overflow-hidden flex bg-[#0d0a1b] text-foreground font-sans selection:bg-accent selection:text-background relative">
            <div className="absolute inset-0 bg-cyber-grid pointer-events-none opacity-10" />

            {/* Sidebar */}
            <aside className="hidden lg:flex flex-col w-72 glass-panel rounded-none border-r border-white/5 z-40 sticky top-0 h-screen bg-[#0f0f13]/90">
                <div className="p-6 border-b border-white/5">
                    <h1 className="font-display text-2xl font-bold tracking-tight flex items-center gap-3">
                        <Activity className="w-7 h-7 text-primary" />
                        Overseer
                    </h1>
                    <p className="font-mono text-[10px] text-primary/70 tracking-widest uppercase mt-2">v2.0 Integrity Matrix</p>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                    <div className="font-sans text-xs font-bold text-muted-foreground uppercase tracking-widest px-4 pb-2 pt-4">Modules</div>
                    <Link href="/admin" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-primary/20 text-primary border border-primary/20 shadow-[0_0_15px_rgba(195,180,253,0.15)] font-semibold transition-all">
                        <Cpu className="w-5 h-5" />
                        Live Feed
                    </Link>
                    <Link href="/admin/models" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-muted-foreground hover:text-foreground font-medium transition-all group">
                        <Database className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                        ML Models
                    </Link>

                    {/* Stats — rendered in sidebar when data is available */}
                    {data && (
                        <div className="mt-8 pt-8 border-t border-white/5 space-y-4">
                            <div className="font-sans text-[10px] font-bold text-primary/50 uppercase tracking-[0.2em] px-4">System Insights</div>
                            <div className="grid grid-cols-1 gap-3 px-2">
                                {[
                                    {
                                        label: 'Total Sessions',
                                        value: data.total_sessions,
                                        onClick: () => { setSessionFilter('all'); setShowFlaggedOnly(false); },
                                    },
                                    {
                                        label: 'Flagged',
                                        value: data.flagged_sessions,
                                        alert: true,
                                        onClick: () => setShowFlaggedOnly(prev => !prev),
                                        active: showFlaggedOnly,
                                    },
                                    {
                                        label: 'Flag Rate',
                                        value: data.total_sessions > 0
                                            ? ((data.flagged_sessions / data.total_sessions) * 100).toFixed(1) + '%'
                                            : '0%',
                                    },
                                    {
                                        label: 'Avg Risk',
                                        value: (data.sessions.reduce((acc, s) => acc + s.risk_score, 0) /
                                            (data.sessions.length || 1) * 100).toFixed(0) + '%',
                                    },
                                ].map((stat, i) => (
                                    <button
                                        key={i}
                                        onClick={stat.onClick}
                                        disabled={!stat.onClick}
                                        className={`p-4 rounded-xl border transition-all text-left flex flex-col justify-between h-20 group ${
                                            stat.onClick ? 'cursor-pointer' : 'cursor-default'
                                        } ${
                                            stat.active
                                                ? 'bg-destructive/10 border-destructive/30'
                                                : 'bg-white/[0.02] border-white/5 hover:bg-white/5'
                                        }`}
                                    >
                                        <span className="font-sans text-[9px] font-bold uppercase tracking-wider text-muted-foreground group-hover:text-white/70 transition-colors">
                                            {stat.label}
                                        </span>
                                        <span className={`font-display text-xl font-bold tracking-tight ${stat.alert ? 'text-destructive' : 'text-foreground'}`}>
                                            {stat.value}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </nav>
                <div className="p-6 border-t border-white/5">
                    <Link href="/" className="flex items-center gap-3 text-sm text-muted-foreground hover:text-foreground transition-colors group">
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> Exit Portal
                    </Link>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0 z-10">
                {/* Header */}
                <header className="sticky top-0 z-30 glass-panel rounded-none border-b border-white/5 bg-[#130f23]/80">
                    <div className="w-full mx-auto px-4 md:px-8 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex items-center gap-4 lg:hidden">
                            <Link href="/" className="p-2 rounded-lg border border-border/50 bg-white/5 hover:bg-white/10 transition-colors">
                                <ArrowLeft className="w-5 h-5 text-muted-foreground" />
                            </Link>
                            <h1 className="font-display text-xl font-bold tracking-tight text-primary">Overseer Admin</h1>
                        </div>
                        <div className="hidden lg:block">
                            <h2 className="font-display text-2xl font-bold tracking-tight">Threat Analytics</h2>
                        </div>
                        <div className="flex flex-wrap items-center gap-3 ml-auto">
                            {/* WS status indicator */}
                            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold tracking-wider uppercase transition-colors ${
                                wsConnected
                                    ? 'border-primary/20 bg-primary/10 text-primary shadow-[0_0_10px_rgba(195,180,253,0.2)]'
                                    : 'border-destructive/20 bg-destructive/10 text-destructive'
                            }`}>
                                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-primary animate-pulse' : 'bg-destructive'}`} />
                                {wsConnected ? 'Live Link' : 'Offline'}
                            </div>
                            <ThemeToggle />
                            <div className="flex gap-2">
                                <button
                                    onClick={exportData}
                                    disabled={!data?.sessions.length}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/20 text-primary border border-primary/30 font-sans font-semibold text-sm hover:bg-primary/30 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
                                >
                                    <Download className="w-4 h-4" /> JSON
                                </button>
                                <button
                                    onClick={exportCsv}
                                    disabled={!data?.sessions.length}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-foreground font-sans font-semibold text-sm hover:bg-white/10 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
                                >
                                    <Download className="w-4 h-4" /> CSV
                                </button>
                            </div>
                        </div>
                    </div>
                </header>

                <main className="flex-1 min-h-0 w-full mx-auto px-4 lg:px-6 py-6 flex flex-col overflow-hidden">
                    {/* WS Alerts island */}
                    <WebSocketAlerts />

                    {/* Error banner */}
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-8 p-4 rounded-xl bg-destructive/10 text-destructive border border-destructive/20 flex items-center gap-3"
                        >
                            <AlertTriangle className="w-5 h-5" />
                            <p className="font-sans text-sm font-semibold tracking-wide">{error}</p>
                        </motion.div>
                    )}

                    {/* Controls island */}
                    <ControlsBar />

                    {/* Sessions grid */}
                    <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 overflow-hidden">
                        <SessionListPanel />
                        <SessionDetailPanel />
                    </div>
                </main>
            </div>
        </div>
    );
}

// ─── Page export (wraps shell in provider) ────────────────────────────────────

export default function AdminDashboard() {
    return (
        <AdminDashboardProvider>
            <DashboardShell />
        </AdminDashboardProvider>
    );
}
