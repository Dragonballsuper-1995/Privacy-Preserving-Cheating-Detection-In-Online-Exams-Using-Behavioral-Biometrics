'use client';

import { Database, RefreshCw, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAdminDashboard } from '../context/AdminDashboardContext';
import type { SessionFilter } from '../context/AdminDashboardContext';

export function ControlsBar() {
    const {
        simulating, sessionFilter, showFlaggedOnly,
        setSessionFilter, setShowFlaggedOnly, generateTestData, loadDashboard,
    } = useAdminDashboard();

    return (
        <div className="mb-8 flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between p-4 rounded-xl border border-border/50 bg-card shadow-sm">
            <div className="flex flex-wrap gap-3">
                <Button
                    onClick={() => generateTestData('honest')}
                    disabled={simulating}
                    variant="outline"
                    className="text-green-600 dark:text-green-400 border-green-500/50 bg-green-500/10 hover:bg-green-500/20 h-10 px-4 py-2.5"
                >
                    {simulating ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Database className="w-4 h-4 mr-2" />}
                    Simulate Honest
                </Button>
                <Button
                    onClick={() => generateTestData('cheater')}
                    disabled={simulating}
                    variant="outline"
                    className="text-destructive border-destructive/50 bg-destructive/10 hover:bg-destructive/20 h-10 px-4 py-2.5"
                >
                    {simulating ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Database className="w-4 h-4 mr-2" />}
                    Simulate Cheating
                </Button>
            </div>

            <div className="flex items-center gap-3">
                <button
                    onClick={loadDashboard}
                    className="p-2.5 rounded-lg border border-border/50 bg-secondary/50 hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
                    title="Refresh Data"
                >
                    <RefreshCw className="w-4 h-4" />
                </button>
                <div className="flex items-center gap-2">
                    <div className="flex rounded-lg border border-border/50 p-1 bg-secondary/20">
                        {(['all', 'real', 'simulated'] as SessionFilter[]).map((filter) => (
                            <button
                                key={filter}
                                onClick={() => setSessionFilter(filter)}
                                className={`px-4 py-1.5 rounded-md font-sans text-xs font-semibold uppercase tracking-wider transition-colors ${
                                    sessionFilter === filter
                                        ? 'bg-background text-primary shadow-sm'
                                        : 'text-muted-foreground hover:text-foreground'
                                }`}
                            >
                                {filter}
                            </button>
                        ))}
                    </div>
                    <button
                        onClick={() => setShowFlaggedOnly(!showFlaggedOnly)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border font-sans text-xs font-bold uppercase tracking-wider transition-all ${
                            showFlaggedOnly
                                ? 'bg-destructive/10 border-destructive/30 text-destructive shadow-[0_0_10px_rgba(255,107,107,0.1)]'
                                : 'bg-secondary/20 border-border/50 text-muted-foreground hover:text-foreground'
                        }`}
                    >
                        <ShieldAlert className={`w-3.5 h-3.5 ${showFlaggedOnly ? 'text-destructive' : ''}`} />
                        <span className="hidden sm:inline">Flagged Only</span>
                    </button>
                </div>
            </div>
        </div>
    );
}
