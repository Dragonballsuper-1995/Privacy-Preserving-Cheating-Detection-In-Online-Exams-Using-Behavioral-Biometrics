'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getModelMetrics, triggerRetraining, ModelMetrics } from '@/lib/api';
import Link from 'next/link';
import { Activity, AlertTriangle, CheckCircle, Database, RefreshCw, Layers, ArrowLeft } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';

export default function ModelsDashboard() {
    const router = useRouter();
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
            } catch (err: any) {
                setError(err.message || 'Failed to load model metrics');
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
        } catch (err: any) {
            setRetrainMsg(`Error: ${err.message || 'Failed to trigger retraining'}`);
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
        <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background pb-20">
            <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-border/50 mb-8">
                <div className="max-w-7xl mx-auto px-4 md:px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link href="/admin" className="p-2 rounded-lg border border-border/50 bg-secondary/30 hover:bg-secondary hover:text-foreground transition-all shadow-sm">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div>
                            <h1 className="font-display text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-3">
                                <Activity className="w-8 h-8 text-primary" />
                                MLOps Terminal
                            </h1>
                            <p className="font-sans text-xs text-muted-foreground font-medium uppercase tracking-widest mt-1">Model Drift Monitoring</p>
                        </div>
                    </div>
                    <ThemeToggle />
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex flex-col md:flex-row md:items-start md:items-center md:justify-between mb-10 gap-6">
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
                            <div className="bg-card p-6 rounded-2xl shadow-sm border border-border/50 flex flex-col gap-4">
                                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <Database className="h-5 w-5 text-primary" />
                                </div>
                                <div>
                                    <p className="font-sans text-xs font-semibold text-muted-foreground uppercase tracking-widest">Total Sessions</p>
                                    <p className="font-mono text-3xl font-bold text-foreground mt-1">{metrics.total_sessions}</p>
                                </div>
                            </div>
                            <div className="bg-card p-6 rounded-2xl shadow-sm border border-border/50 flex flex-col gap-4">
                                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <Layers className="h-5 w-5 text-primary" />
                                </div>
                                <div>
                                    <p className="font-sans text-xs font-semibold text-muted-foreground uppercase tracking-widest">HITL Reviews</p>
                                    <p className="font-mono text-3xl font-bold text-foreground mt-1">{metrics.reviewed_sessions_count}</p>
                                </div>
                            </div>
                            <div className="bg-card p-6 rounded-2xl shadow-sm border border-border/50 flex flex-col gap-4">
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
                                {Object.entries(metrics.metrics).map(([featureName, driftData]) => (
                                    <div key={featureName} className={`bg-card rounded-2xl shadow-sm border overflow-hidden transition-all hover:shadow-md ${driftData.drift_detected ? 'border-destructive/30' : 'border-border/50'}`}>
                                        <div className={`px-5 py-4 border-b ${driftData.drift_detected ? 'bg-destructive/10 border-destructive/20' : 'bg-secondary/30 border-border/50'}`}>
                                            <h3 className={`font-sans tracking-wider uppercase text-sm font-bold border-b-0 ${driftData.drift_detected ? 'text-destructive' : 'text-foreground'}`}>
                                                {featureName.replace('_', ' ')}
                                            </h3>
                                        </div>
                                        <div className="p-6 space-y-4">
                                            <div className="flex justify-between items-center">
                                                <span className="font-sans text-xs font-medium text-muted-foreground uppercase tracking-widest">Drift Level</span>
                                                {driftData.drift_detected ? (
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest bg-destructive/10 text-destructive border border-destructive/20 shadow-sm">
                                                        Detected
                                                    </span>
                                                ) : (
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest bg-secondary text-foreground shadow-sm">
                                                        Nominal
                                                    </span>
                                                )}
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
                                        </div>
                                    </div>
                                ))}

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
    );
}
