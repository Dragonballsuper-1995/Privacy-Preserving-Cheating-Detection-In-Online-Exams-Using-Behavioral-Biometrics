'use client';

import { motion } from 'framer-motion';
import { AlertTriangle, Activity, Eye, Clock, Cpu, CheckCircle2, ShieldAlert, Terminal } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import { useAdminDashboard } from '../context/AdminDashboardContext';

// ─── Shared Helpers ────────────────────────────────────────────────────────────

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

function formatTime(ms: number) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`;
}

// ─── Component ────────────────────────────────────────────────────────────────

export function SessionDetailPanel() {
    const {
        selectedSession, timeline, activeTab, setActiveTab,
        submittingReview, reviewNotes, setReviewNotes,
        submitReview, getSessionAlias,
    } = useAdminDashboard();

    if (!selectedSession) {
        return (
            <div className="lg:col-span-8 flex flex-col h-full glass-panel overflow-hidden border border-white/5 relative">
                <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-muted-foreground bg-background/50">
                    <Terminal className="w-16 h-16 mb-4 opacity-20" />
                    <p className="font-sans text-lg font-semibold uppercase tracking-widest">Awaiting Selection</p>
                    <p className="font-sans text-xs font-medium mt-2 uppercase tracking-wide opacity-70">Select target from roster to initiate analysis</p>
                </div>
            </div>
        );
    }

    return (
        <div className="lg:col-span-8 flex flex-col h-full glass-panel overflow-hidden border border-white/5 relative">
            {/* Header Info */}
            <div className="p-6 border-b border-border/50 bg-secondary/30">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <p className="font-sans text-xs text-primary font-semibold uppercase tracking-wider mb-1">Target Analysis</p>
                        <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-3">
                                <h2 className="font-display text-2xl font-bold tracking-tight">
                                    {getSessionAlias(selectedSession.session_id)}
                                </h2>
                                {selectedSession.review_status === 'confirmed_cheating' && (
                                    <span className="px-2.5 py-1 rounded-md bg-destructive/10 text-destructive border border-destructive/20 font-sans text-xs font-bold uppercase tracking-wider shadow-sm">Confirmed</span>
                                )}
                                {selectedSession.review_status === 'false_positive' && (
                                    <span className="px-2.5 py-1 rounded-md bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20 font-sans text-xs font-bold uppercase tracking-wider shadow-sm">False Positive</span>
                                )}
                            </div>
                            <p className="font-mono text-[10px] text-muted-foreground truncate opacity-70" title={selectedSession.session_id}>
                                UUID: {selectedSession.session_id}
                            </p>
                        </div>
                    </div>
                    <div className={`px-5 py-3 rounded-xl border border-border/50 font-display text-xl font-bold shadow-sm ${getRiskBgColor(selectedSession.overall_score)}`}>
                        Risk Quotient: {(selectedSession.overall_score * 100).toFixed(0)}%
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
                                <TabsTrigger
                                    key={tab}
                                    value={tab}
                                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-sans font-semibold text-sm uppercase tracking-wider transition-all data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm text-muted-foreground hover:text-foreground"
                                >
                                    <Icon className="w-4 h-4" />
                                    <span className="hidden sm:inline">{tab}</span>
                                </TabsTrigger>
                            );
                        })}
                    </TabsList>
                </div>

                <div className="flex-1 overflow-y-auto p-6 md:p-8 bg-background/30 backdrop-blur-md relative custom-scrollbar">

                    {/* Overview Tab */}
                    <TabsContent value="overview" className="mt-0 outline-none">
                        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8 relative z-10">
                            <div>
                                <h3 className="font-sans text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Subsystem Analysis</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {[
                                        { label: 'Keystroke Dynamics', score: selectedSession.typing_score },
                                        { label: 'Hesitation Metric', score: selectedSession.hesitation_score },
                                        { label: 'Clipboard Activity', score: selectedSession.paste_score },
                                        { label: 'Window Focus Loss', score: selectedSession.focus_score },
                                        { label: 'Content Similarity', score: selectedSession.similarity_score ?? 0 },
                                    ].map((item) => (
                                        <div key={item.label} className="p-5 rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm flex flex-col justify-between h-28 hover:bg-white/10 transition-all shadow-sm hover:shadow-md">
                                            <div className="flex justify-between items-center mb-3">
                                                <span className="font-sans text-xs font-bold uppercase tracking-wider text-muted-foreground">{item.label}</span>
                                                <span className={`font-display text-xl font-bold ${getRiskColor(item.score)}`}>
                                                    {(item.score * 100).toFixed(0)}%
                                                </span>
                                            </div>
                                            <div className="w-full h-2 rounded-full border border-border/50 bg-secondary overflow-hidden">
                                                <div
                                                    className={`h-full rounded-full transition-all duration-1000 ${getRiskBgColor(item.score).split(' ')[0]}`}
                                                    style={{ width: `${item.score * 100}%` }}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {selectedSession.flag_reasons?.length > 0 && (
                                <div className="p-6 rounded-2xl border border-destructive/20 bg-destructive/5 shadow-sm">
                                    <h3 className="font-display font-semibold text-lg text-destructive tracking-widest uppercase flex items-center gap-2 mb-4">
                                        <AlertTriangle className="w-5 h-5" /> Anomaly Triggers
                                    </h3>
                                    <ul className="space-y-3 font-sans text-sm font-medium text-foreground">
                                        {selectedSession.flag_reasons.map((reason, i) => (
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
                                        <motion.div
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: i * 0.03, type: 'spring', stiffness: 260, damping: 20 }}
                                            whileHover={{ scale: 1.005, x: 2 }}
                                            key={i}
                                            className="flex flex-col md:flex-row rounded-xl border border-border/50 bg-card shadow-sm overflow-hidden hover:border-primary/30 hover:shadow-md"
                                        >
                                            <div className="flex items-center md:justify-center md:w-28 p-3 border-b md:border-b-0 md:border-r border-border/50 bg-secondary/50 font-mono text-xs font-semibold text-muted-foreground">
                                                {formatTime(event.timestamp)}
                                            </div>
                                            <div className="flex-1 p-4 flex items-center justify-between gap-4">
                                                <div className="flex items-center gap-4">
                                                    <span className={`px-2.5 py-1 rounded-md border font-sans text-[10px] font-bold uppercase tracking-wider ${
                                                        event.type === 'paste'
                                                            ? 'bg-destructive/10 border-destructive/20 text-destructive'
                                                            : event.type === 'focus'
                                                            ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-600 dark:text-yellow-400'
                                                            : 'bg-primary/10 border-primary/20 text-primary'
                                                    }`}>
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
                        {selectedSession.features && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8 relative z-10">
                                <Accordion type="multiple" className="w-full space-y-4">
                                    {Object.entries(selectedSession.features).map(([category, features], idx) => (
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
                            <div className="p-6 rounded-xl border border-border/50 bg-secondary/30 shadow-sm space-y-4">
                                <h3 className="font-display font-semibold text-lg text-foreground tracking-widest uppercase flex items-center gap-2">
                                    <ShieldAlert className="w-5 h-5 text-primary" /> Human-in-the-Loop Review
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
        </div>
    );
}
