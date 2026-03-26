'use client';

import { useState, useEffect } from 'react';
import { getModelMetrics, triggerRetraining, ModelMetrics } from '@/lib/api';
import Link from 'next/link';
import { Activity, AlertTriangle, CheckCircle, Database, RefreshCw, Layers, ArrowLeft, Cpu } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';

export default function ModelsDashboard() {
    const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isRetraining, setIsRetraining] = useState(false);
    const [retrainMsg, setRetrainMsg] = useState<string | null>(null);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const data = await getModelMetrics();
                setMetrics(data);
            } catch (err: unknown) {
                setError(err instanceof Error ? err.message : 'Failed to load model metrics');
            } finally {
                setLoading(false);
            }
        };

        fetchMetrics();
    }, []);

    const handleRetrain = async () => {
        setIsRetraining(true);
        setRetrainMsg(null);
        try {
            const res = await triggerRetraining();
            setRetrainMsg(res.message);
        } catch (err: unknown) {
            setRetrainMsg(`Error: ${err instanceof Error ? err.message : 'Failed to trigger retraining'}`);
        } finally {
            setIsRetraining(false);
            // Optionally refresh metrics after some time
            setTimeout(() => {
                window.location.reload();
            }, 5000);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background pb-20">
                <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-border/50">
                    <div className="max-w-7xl mx-auto px-4 md:px-6 py-4 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link href="/admin" className="p-2 rounded-lg border border-border/50 bg-secondary/30 hover:bg-secondary hover:text-foreground transition-all shadow-sm">
                                <ArrowLeft className="w-5 h-5" />
                            </Link>
                            <h1 className="font-display text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-3">
                                <Activity className="w-8 h-8 text-primary" />
                                MLOps Terminal
                            </h1>
                        </div>
                        <ThemeToggle />
                    </div>
                </header>
                <div className="flex-1 flex flex-col items-center justify-center p-32">
                    <RefreshCw className="w-12 h-12 text-primary animate-spin mb-4" />
                    <p className="font-sans font-medium text-muted-foreground uppercase tracking-widest text-sm">Initializing Telemetry</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background pb-20">
                <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-border/50">
                    <div className="max-w-7xl mx-auto px-4 md:px-6 py-4 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link href="/admin" className="p-2 rounded-lg border border-border/50 bg-secondary/30 hover:bg-secondary hover:text-foreground transition-all shadow-sm">
                                <ArrowLeft className="w-5 h-5" />
                            </Link>
                            <h1 className="font-display text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-3">
                                <Activity className="w-8 h-8 text-primary" />
                                MLOps Terminal
                            </h1>
                        </div>
                        <ThemeToggle />
                    </div>
                </header>
                <div className="flex-1 flex items-center justify-center p-8 mt-10">
                    <div className="bg-destructive/5 border border-destructive/20 p-8 rounded-2xl shadow-sm text-center max-w-md w-full">
                        <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
                        <h2 className="text-xl font-bold font-display uppercase tracking-widest text-destructive mb-2">Metrics Unavailable</h2>
                        <p className="font-sans text-sm text-muted-foreground mb-6">{error}</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="w-full bg-destructive text-destructive-foreground font-sans font-bold uppercase tracking-wider py-3 rounded-xl shadow-sm hover:opacity-90 transition-opacity"
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex text-foreground font-sans selection:bg-accent selection:text-background relative">
            <div className="absolute inset-0 bg-cyber-grid pointer-events-none opacity-10"></div>
            
            {/* Dark Side Nav */}
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
                    <Link href="/admin" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-muted-foreground hover:text-foreground font-medium transition-all group">
                        <Cpu className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                        Live Feed
                    </Link>
                    <Link href="/admin/models" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-primary/20 text-primary border border-primary/20 shadow-[0_0_15px_rgba(195,180,253,0.15)] font-semibold transition-all">
                        <Database className="w-5 h-5" />
                        ML Models
                    </Link>
                </nav>
                <div className="p-6 border-t border-white/5">
                    <Link href="/" className="flex items-center gap-3 text-sm text-muted-foreground hover:text-foreground transition-colors group">
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> Exit Portal
                    </Link>
                </div>
            </aside>

            <div className="flex-1 flex flex-col min-w-0 z-10 w-full">
                <header className="sticky top-0 z-30 glass-panel rounded-none border-b border-white/5 bg-[#130f23]/80 mb-8">
                    <div className="w-full mx-auto px-4 md:px-8 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex items-center gap-4 lg:hidden">
                            <Link href="/admin" className="p-2 rounded-lg border border-border/50 bg-white/5 hover:bg-white/10 transition-colors">
                                <ArrowLeft className="w-5 h-5 text-muted-foreground" />
                            </Link>
                            <h1 className="font-display text-xl font-bold tracking-tight text-primary">MLOps Terminal</h1>
                        </div>
                        <div className="hidden lg:block">
                            <h2 className="font-display text-2xl font-bold tracking-tight">Model Monitor</h2>
                        </div>
                        <div className="ml-auto">
                            <ThemeToggle />
                        </div>
                    </div>
                </header>

                <main className="w-full max-w-7xl mx-auto px-4 md:px-8 pb-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-10 gap-6">
                    <div>
                        <h1 className="text-3xl font-display font-semibold text-foreground tracking-tight flex items-center gap-2">
                            <Layers className="w-8 h-8 text-primary" />
                            Risk Fusion Model
                        </h1>
                        <p className="mt-2 text-muted-foreground font-sans text-sm">
                            Real-time data drift monitoring & periodic retraining trigger sequences.
                        </p>
                    </div>

                    <div className="flex flex-col items-start md:items-end">
                        <button
                            onClick={handleRetrain}
                            disabled={isRetraining || metrics?.status === 'insufficient_data'}
                            className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-xl hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm font-sans font-bold uppercase tracking-wider text-sm active:scale-[0.98]"
                        >
                            <RefreshCw className={`h-4 w-4 ${isRetraining ? 'animate-spin' : ''}`} />
                            {isRetraining ? 'Initiating Pipeline...' : 'Trigger Retraining Pipeline'}
                        </button>
                        {retrainMsg && (
                            <p className="text-xs mt-3 text-primary font-semibold uppercase tracking-wider bg-primary/10 px-3 py-1.5 rounded-md border border-primary/20">
                                {retrainMsg}
                            </p>
                        )}
                    </div>
                </div>

                {metrics && (
                    <div className="space-y-10">
                        {/* Status Header */}
                        <div className={`p-6 md:p-8 rounded-2xl border shadow-sm flex flex-col md:flex-row items-center gap-6 ${metrics.status === 'healthy' ? 'bg-green-500/10 border-green-500/20 text-green-700 dark:text-green-400' :
                            metrics.status === 'needs_retraining' ? 'bg-destructive/10 border-destructive/20 text-destructive' :
                                'bg-yellow-500/10 border-yellow-500/20 text-yellow-700 dark:text-yellow-400'
                            }`}>
                            {metrics.status === 'healthy' ? (
                                <CheckCircle className="h-10 w-10 flex-shrink-0" />
                            ) : (
                                <AlertTriangle className="h-10 w-10 flex-shrink-0" />
                            )}
                            <div>
                                <h3 className="font-display text-2xl font-bold tracking-tight uppercase border-b-0">
                                    System Status: {metrics.status.replace('_', ' ')}
                                </h3>
                                <p className="mt-1 font-sans text-sm font-medium opacity-80 uppercase tracking-widest">
                                    {metrics.message}
                                </p>
                            </div>
                        </div>

                        {/* Top level stats */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                            <div className="glass-panel p-6 shadow-sm border border-white/5 flex flex-col gap-4">
                                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <Database className="h-5 w-5 text-primary" />
                                </div>
                                <div>
                                    <p className="font-sans text-xs font-semibold text-muted-foreground uppercase tracking-widest">Total Sessions</p>
                                    <p className="font-mono text-3xl font-bold text-foreground mt-1">{metrics.total_sessions}</p>
                                </div>
                            </div>
                            <div className="glass-panel p-6 shadow-sm border border-white/5 flex flex-col gap-4">
                                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <Layers className="h-5 w-5 text-primary" />
                                </div>
                                <div>
                                    <p className="font-sans text-xs font-semibold text-muted-foreground uppercase tracking-widest">HITL Reviews</p>
                                    <p className="font-mono text-3xl font-bold text-foreground mt-1">{metrics.reviewed_sessions_count}</p>
                                </div>
                            </div>
                            <div className="glass-panel p-6 shadow-sm border border-white/5 flex flex-col gap-4">
                                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <Activity className="h-5 w-5 text-primary" />
                                </div>
                                <div>
                                    <p className="font-sans text-xs font-semibold text-muted-foreground uppercase tracking-widest">Flag Precision</p>
                                    <p className="font-mono text-3xl font-bold text-foreground mt-1">
                                        {metrics.reviewed_sessions_count > 0
                                            ? `${(metrics.precision_estimate * 100).toFixed(1)}%`
                                            : 'N/A'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Drift Metrics Grid */}
                        <div className="pt-6">
                            <h2 className="font-display text-xl font-bold text-foreground mb-6 uppercase tracking-wider flex items-center gap-2 border-b-0">
                                <Activity className="w-5 h-5 text-primary" />
                                Subsystem Distribution Drift (K-S)
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {Object.entries(metrics.metrics).map(([featureName, driftData]) => {
                                    const state = isRetraining ? 'training' : (driftData.drift_detected ? 'deprecated' : 'online');
                                    return (
                                        <div key={featureName} className={`glass-panel overflow-hidden transition-all hover:shadow-[0_0_20px_rgba(195,180,253,0.15)] ${state === 'deprecated' ? 'grayscale opacity-80 border-white/5' : 'border-white/10'}`}>
                                            <div className="px-5 py-4 border-b border-white/5 bg-white/5 flex justify-between items-center">
                                                <h3 className="font-sans tracking-wider uppercase text-sm font-bold text-foreground">
                                                    {featureName.replace('_', ' ')}
                                                </h3>
                                                <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest shadow-sm border ${state === 'online' ? 'bg-primary/20 text-primary border-primary/30' : state === 'training' ? 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30' : 'bg-muted/20 border-border/50 text-muted-foreground'}`}>
                                                    {state === 'online' && <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />}
                                                    {state === 'training' && <RefreshCw className="w-3 h-3 animate-spin" />}
                                                    {state}
                                                </span>
                                            </div>
                                            <div className="p-6 space-y-4">
                                                {state === 'training' ? (
                                                    <div className="py-4 space-y-2">
                                                        <div className="flex justify-between text-xs font-mono text-muted-foreground">
                                                            <span>Epoch 34/100</span>
                                                            <span>68%</span>
                                                        </div>
                                                        <div className="w-full h-1.5 rounded-full bg-secondary overflow-hidden">
                                                            <div className="h-full bg-yellow-500 w-[68%] rounded-full opacity-80 animate-pulse" />
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <>
                                                        <div className="flex justify-between items-center">
                                                            <span className="font-sans text-xs font-medium text-muted-foreground uppercase tracking-widest">Drift Status</span>
                                                            <span className="font-mono text-sm font-semibold pr-1 text-foreground">
                                                                {driftData.drift_detected ? 'Detected' : 'Nominal'}
                                                            </span>
                                                        </div>
                                                        <div className="flex justify-between items-center">
                                                            <span className="font-sans text-xs font-medium text-muted-foreground uppercase tracking-widest">p-value</span>
                                                            <span className={`font-mono text-sm font-semibold pr-1 ${driftData.p_value < 0.05 ? 'text-destructive' : 'text-foreground'}`}>
                                                                {driftData.p_value.toExponential(2)}
                                                            </span>
                                                        </div>
                                                        <div className="flex justify-between items-center">
                                                            <span className="font-sans text-xs font-medium text-muted-foreground uppercase tracking-widest">KS Stat</span>
                                                            <span className="font-mono text-sm font-semibold pr-1 text-foreground">
                                                                {driftData.statistic.toFixed(4)}
                                                            </span>
                                                        </div>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}

                                {Object.keys(metrics.metrics).length === 0 && (
                                    <div className="col-span-full py-16 text-center text-muted-foreground bg-secondary/20 rounded-2xl border border-border/50 border-dashed">
                                        <p className="font-sans text-sm font-semibold uppercase tracking-widest">Insufficient Telemetry Data</p>
                                    </div>
                                )}
                            </div>
                        </div>

                    </div>
                )}
                </main>
            </div>
        </div>
    );
}
