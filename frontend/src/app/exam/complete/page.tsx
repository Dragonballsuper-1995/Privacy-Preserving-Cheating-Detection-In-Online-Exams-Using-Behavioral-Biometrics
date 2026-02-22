/**
 * Student Results Page
 * Shows after exam submission with detailed result summary
 */

'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { getSessionResult, SessionResult, analyzeSession } from '@/lib/api';
import { Terminal, Activity, Clock, Database, CheckCircle2, AlertTriangle, ArrowLeft, Loader2 } from 'lucide-react';

/* ------------------------------------------------------------------ */
/*  Status badge component                                             */
/* ------------------------------------------------------------------ */
function StatusBadge({ status }: { status: string }) {
    const map: Record<string, { label: string; cls: string }> = {
        submitted: {
            label: 'Under Review',
            cls: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20 dark:text-yellow-400',
        },
        analyzed: {
            label: 'Review Complete',
            cls: 'bg-green-500/10 text-green-600 border-green-500/20 dark:text-green-400',
        },
        in_progress: {
            label: 'In Progress',
            cls: 'bg-primary/10 text-primary border-primary/20',
        },
    };
    const info = map[status] ?? {
        label: status,
        cls: 'bg-muted text-muted-foreground border-border',
    };
    return (
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-sans text-xs font-semibold uppercase tracking-wider border ${info.cls}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-current" />
            {info.label}
        </span>
    );
}

/* ------------------------------------------------------------------ */
/*  Circular progress ring (Brutalist equivalent)                      */
/* ------------------------------------------------------------------ */
function ProgressRing({ answered, total }: { answered: number; total: number }) {
    const pct = total > 0 ? (answered / total) * 100 : 0;

    return (
        <div className="w-full flex items-center gap-4">
            <div className="flex-1 rounded-full bg-secondary h-3 relative overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    className="absolute top-0 left-0 bottom-0 bg-primary"
                />
            </div>
            <div className="font-display text-2xl font-bold min-w-[3ch] text-right">
                {answered}/{total}
            </div>
        </div>
    );
}

/* ------------------------------------------------------------------ */
/*  Main content                                                       */
/* ------------------------------------------------------------------ */
function ResultsContent() {
    const searchParams = useSearchParams();
    const sessionId = searchParams.get('session');

    const [result, setResult] = useState<SessionResult | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!sessionId) { setLoading(false); return; }

        async function load() {
            try {
                // Trigger analysis in the background (best-effort)
                analyzeSession(sessionId!).catch(() => { /* ignore */ });

                const data = await getSessionResult(sessionId!);
                setResult(data);
            } catch {
                setError('CRITICAL_ERROR: COULD_NOT_LOAD_SESSION_RESULTS');
            } finally {
                setLoading(false);
            }
        }
        load();
    }, [sessionId]);

    /* ── no session param ── */
    if (!sessionId) {
        return (
            <div className="min-h-screen text-foreground flex items-center justify-center p-4 selection:bg-accent selection:text-background">
                <div className="text-center space-y-4 border border-border/50 rounded-2xl p-8 bg-card shadow-sm max-w-sm w-full">
                    <p className="font-sans font-semibold tracking-wider text-destructive">No Session Identifier Detected</p>
                    <Link href="/" className="inline-block px-6 py-2.5 rounded-lg border border-border bg-card text-foreground font-sans font-semibold text-sm hover:bg-secondary transition-colors">Return to Dashboard</Link>
                </div>
            </div>
        );
    }

    /* ── loading ── */
    if (loading) {
        return (
            <div className="min-h-screen text-foreground flex items-center justify-center p-4 selection:bg-accent selection:text-background">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center gap-4"
                >
                    <div className="w-10 h-10 border-4 border-muted border-t-primary rounded-full animate-spin" />
                    <p className="font-sans text-sm font-semibold tracking-wider text-muted-foreground animate-pulse">Retrieving Telemetry Data...</p>
                </motion.div>
            </div>
        );
    }

    /* ── error ── */
    if (error || !result) {
        return (
            <div className="min-h-screen text-foreground flex items-center justify-center p-4 selection:bg-accent selection:text-background">
                <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="max-w-md w-full mx-4 border border-border/50 rounded-2xl bg-card p-8 text-center space-y-6 shadow-sm"
                >
                    <div className="w-16 h-16 mx-auto rounded-full bg-primary/10 text-primary flex items-center justify-center mb-4">
                        <CheckCircle2 className="w-8 h-8" />
                    </div>
                    <h1 className="font-display text-2xl font-bold tracking-tight">
                        Transmission Complete
                    </h1>
                    <p className="font-sans text-sm text-muted-foreground">
                        {error || 'Assessment data secured. Results pending review.'}
                    </p>
                    <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 font-mono text-xs text-muted-foreground break-all">
                        Session ID: {sessionId}
                    </div>
                    <Link href="/" className="inline-block w-full px-6 py-3 rounded-xl bg-primary text-primary-foreground font-sans font-semibold hover:bg-primary/90 transition-all shadow-sm active:scale-[0.98]">
                        Return to Dashboard
                    </Link>
                </motion.div>
            </div>
        );
    }

    /* ── Format timestamps ── */
    const fmtTime = (iso: string | null) => {
        if (!iso) return '—';
        try {
            const d = new Date(iso);
            return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`;
        } catch { return iso; }
    };

    /* ── Compute duration ── */
    const duration = (() => {
        if (!result.started_at || !result.submitted_at) return null;
        const ms = new Date(result.submitted_at).getTime() - new Date(result.started_at).getTime();
        if (isNaN(ms) || ms <= 0) return null;
        const mins = Math.floor(ms / 60000);
        const secs = Math.floor((ms % 60000) / 1000);
        return `${mins}M ${secs}S`;
    })();

    /* ── Full results UI ── */
    return (
        <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background py-10 px-4 md:py-20">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="max-w-3xl mx-auto space-y-8"
            >

                {/* ── Header card ── */}
                <div className="border border-border/50 rounded-3xl bg-card p-8 md:p-12 text-center space-y-6 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-2 bg-primary/20" />

                    <div className="w-20 h-20 mx-auto rounded-full bg-primary/10 text-primary flex items-center justify-center mb-4 mt-4">
                        <CheckCircle2 className="w-10 h-10" />
                    </div>

                    <h1 className="font-display text-4xl md:text-5xl font-bold tracking-tight leading-none">
                        Transmission
                        <br />
                        <span className="text-primary">Successful</span>
                    </h1>

                    <div className="py-2">
                        <StatusBadge status={result.status} />
                    </div>

                    <p className="font-sans text-sm text-muted-foreground max-w-lg mx-auto px-4 py-2 border-l-2 border-r-2 border-primary/20">
                        All data points secured. Telemetry logs awaiting instructor decryption.
                    </p>
                </div>

                {/* ── Stats row ── */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Progress ring area */}
                    <div className="md:col-span-1 rounded-2xl border border-border/50 bg-card p-6 shadow-sm flex flex-col justify-center gap-4">
                        <p className="font-sans text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                            <Database className="w-4 h-4" /> Completed Nodes
                        </p>
                        <ProgressRing answered={result.total_answered} total={result.total_questions} />
                    </div>

                    {/* Time info */}
                    <div className="md:col-span-2 rounded-2xl border border-border/50 bg-card p-6 shadow-sm bg-secondary/20">
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                            <div className="sm:col-span-2">
                                <p className="font-sans text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-2">
                                    <Terminal className="w-3 h-3" /> Session ID
                                </p>
                                <p className="font-mono text-sm font-medium text-foreground truncate">{result.session_id}</p>
                            </div>
                            <div className="sm:col-span-2">
                                <p className="font-sans text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-2">
                                    <Clock className="w-3 h-3" /> Duration
                                </p>
                                <p className="font-display text-lg font-bold text-foreground">{duration || 'N/A'}</p>
                            </div>
                            <div className="sm:col-span-2 border-t border-border/50 pt-4">
                                <p className="font-sans text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">Initiated</p>
                                <p className="font-sans text-sm text-foreground/80 font-medium">{fmtTime(result.started_at)}</p>
                            </div>
                            <div className="sm:col-span-2 border-t border-border/50 pt-4">
                                <p className="font-sans text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">Terminated</p>
                                <p className="font-sans text-sm text-foreground/80 font-medium">{fmtTime(result.submitted_at)}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* ── Answer breakdown ── */}
                {result.answers.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="rounded-2xl border border-border/50 bg-card shadow-sm overflow-hidden"
                    >
                        <div className="px-6 py-4 border-b border-border/50 bg-secondary/30">
                            <h2 className="font-sans text-sm font-semibold uppercase tracking-wider flex items-center gap-2 text-foreground">
                                <Activity className="w-4 h-4 text-primary" />
                                Data Point Summary
                            </h2>
                        </div>
                        <ul className="divide-y divide-border/50 bg-card">
                            {result.answers.map((ans, i) => (
                                <li key={ans.question_id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center gap-4 hover:bg-secondary/20 transition-colors">
                                    <span className="w-8 h-8 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center font-sans text-sm font-semibold">
                                        {i + 1}
                                    </span>
                                    <div className="flex-1 min-w-0">
                                        <p className="font-sans text-sm font-semibold text-foreground truncate">
                                            {ans.question_id}
                                        </p>
                                        <p className="font-sans text-xs text-muted-foreground uppercase tracking-wider mt-1 font-medium">
                                            {ans.answered ? `Payload: ${ans.length} bytes` : 'No payload detected'}
                                        </p>
                                    </div>
                                    <div className="sm:ml-auto flex items-center">
                                        {ans.answered ? (
                                            <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-600 dark:text-green-400 font-sans text-[10px] font-bold uppercase tracking-widest border border-green-500/20">
                                                Secured
                                            </span>
                                        ) : (
                                            <span className="px-3 py-1 rounded-full bg-destructive/10 text-destructive font-sans text-[10px] font-bold uppercase tracking-widest border border-destructive/20">
                                                Null
                                            </span>
                                        )}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </motion.div>
                )}

                {/* ── Actions ── */}
                <div className="flex flex-col sm:flex-row gap-4 pt-4">
                    <Link href="/"
                        className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl border border-border bg-card text-foreground font-sans font-semibold hover:bg-secondary transition-colors shadow-sm active:scale-[0.98]">
                        <ArrowLeft className="w-5 h-5" />
                        Return to Dashboard
                    </Link>
                    <Link href="/admin"
                        className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-primary text-primary-foreground font-sans font-semibold hover:bg-primary/90 transition-colors shadow-sm active:scale-[0.98]">
                        <Terminal className="w-5 h-5" />
                        System Dashboard
                    </Link>
                </div>
            </motion.div>
        </div>
    );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */
export default function ExamCompletePage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen text-foreground flex items-center justify-center p-4 selection:bg-accent selection:text-background">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 border-8 border-foreground border-t-accent rounded-full animate-spin" />
                    <p className="font-mono text-sm font-bold uppercase tracking-widest animate-pulse">INITIALIZING...</p>
                </div>
            </div>
        }>
            <ResultsContent />
        </Suspense>
    );
}
