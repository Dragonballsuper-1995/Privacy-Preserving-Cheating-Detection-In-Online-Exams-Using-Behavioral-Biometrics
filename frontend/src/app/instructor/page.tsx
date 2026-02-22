/**
 * Instructor Dashboard
 * Shows exams created by the instructor and session stats
 */

'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FileText, Plus, Trash2, ArrowRight, LayoutDashboard, Database, Activity } from 'lucide-react';
import { listExams, deleteExam, Exam, isAuthenticated } from '@/lib/api';

/* ───── page ───── */
export default function InstructorDashboard() {
    const [exams, setExams] = useState<Exam[]>([]);
    const [loading, setLoading] = useState(true);
    const [deleting, setDeleting] = useState<string | null>(null);

    const load = useCallback(async () => {
        try {
            const data = await listExams();
            setExams(data.exams);
        } catch (err) {
            console.error('Failed to load exams', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { load(); }, [load]);

    const handleDelete = async (examId: string) => {
        if (!confirm('DESTROY THIS EXAM? THIS ACTION IS PERMANENT.')) return;
        setDeleting(examId);
        try {
            await deleteExam(examId);
            setExams(prev => prev.filter(e => e.id !== examId));
        } catch {
            alert('SYSTEM ERROR: ONLY CUSTOM EXAMS CAN BE DESTROYED.');
        } finally {
            setDeleting(null);
        }
    };

    /* ───── guard ───── */
    if (!isAuthenticated()) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background p-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="max-w-md w-full border-4 border-foreground bg-card p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,0.1)] space-y-6 text-center"
                >
                    <h2 className="font-display text-3xl font-black uppercase tracking-tighter">ACCESS DENIED</h2>
                    <p className="text-foreground/70 font-mono text-sm uppercase">INSTRUCTOR CREDENTIALS REQUIRED.</p>
                    <Link href="/login" className="block w-full py-4 border-2 border-foreground bg-accent text-background font-display font-bold uppercase tracking-widest hover:bg-foreground hover:text-background transition-colors">
                        AUTHENTICATE
                    </Link>
                </motion.div>
            </div>
        );
    }

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
    };

    return (
        <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background pb-20">

            {/* ── Top bar ── */}
            <header className="sticky top-0 z-30 bg-background border-b-4 border-foreground">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between p-6 gap-4">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-accent text-background border-2 border-foreground">
                            <LayoutDashboard className="w-6 h-6 stroke-[3]" />
                        </div>
                        <div>
                            <h1 className="font-display text-2xl md:text-3xl font-extrabold uppercase tracking-tight">COMMAND CENTER</h1>
                            <p className="font-mono text-xs uppercase text-foreground/60 tracking-widest">SYSTEM_STATUS: NOMINAL</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 w-full md:w-auto">
                        <Link href="/" className="font-mono text-sm uppercase font-bold hover:text-accent transition-colors hidden sm:block">
                            [ RETURN_HOME ]
                        </Link>
                        <Link href="/instructor/create-exam"
                            className="flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-3 border-2 border-foreground bg-foreground text-background font-display font-bold uppercase tracking-wider hover:bg-accent hover:border-foreground transition-all duration-200">
                            <Plus className="w-5 h-5 stroke-[3]" />
                            INITIALIZE_EXAM
                        </Link>
                    </div>
                </div>
            </header>

            {/* ── Body ── */}
            <main className="max-w-7xl mx-auto px-6 py-12">

                {/* Stats row */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16"
                >
                    {[
                        { label: 'TOTAL_DEPLOYMENTS', value: exams.length, icon: Database },
                        { label: 'QUERIES_INDEXED', value: exams.reduce((s, e) => s + (e.question_count || e.questions?.length || 0), 0), icon: FileText },
                        { label: 'CUSTOM_VECTORS', value: exams.filter(e => !e.id.startsWith('demo-') && !e.id.startsWith('categorized-')).length, icon: Activity },
                    ].map((stat, i) => (
                        <motion.div key={stat.label} variants={itemVariants} className="relative group">
                            {/* Harsh shadow layer */}
                            <div className="absolute inset-0 bg-foreground translate-x-1 translate-y-1 transition-transform group-hover:translate-x-2 group-hover:translate-y-2" />
                            <div className="relative bg-card border-2 border-foreground p-6 flex items-start justify-between">
                                <div>
                                    <h2 className="font-mono text-xs uppercase tracking-widest text-foreground/60 mb-2">{stat.label}</h2>
                                    <p className="font-display text-5xl font-black">{loading ? '—' : stat.value}</p>
                                </div>
                                <stat.icon className="w-8 h-8 text-accent opacity-50" />
                            </div>
                        </motion.div>
                    ))}
                </motion.div>

                {/* Section Header */}
                <div className="flex items-end justify-between mb-8 border-b-2 border-foreground pb-4">
                    <h2 className="font-display text-2xl font-bold uppercase tracking-tight">ACTIVE_DEPLOYMENTS</h2>
                    <span className="font-mono text-xs text-foreground/50">[{exams.length} RECORDS_FOUND]</span>
                </div>

                {/* Exams grid */}
                {loading ? (
                    <div className="flex items-center justify-center py-32">
                        <div className="w-16 h-16 border-4 border-foreground border-t-accent rounded-none animate-spin" />
                    </div>
                ) : exams.length === 0 ? (
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        className="bg-accent/10 border-2 border-dashed border-foreground p-16 text-center space-y-6"
                    >
                        <FileText className="w-16 h-16 mx-auto text-foreground/30 mb-4" />
                        <h3 className="font-display text-2xl font-black uppercase">NO_RECORDS_FOUND</h3>
                        <p className="font-mono text-sm text-foreground/60">DATABASE QUERY RETURNED 0 RESULTS.</p>
                        <Link href="/instructor/create-exam"
                            className="inline-block mt-4 px-8 py-4 border-2 border-foreground bg-accent text-background font-display font-bold uppercase tracking-widest hover:bg-foreground transition-colors">
                            EXECUTE_CREATION_PROTOCOL
                        </Link>
                    </motion.div>
                ) : (
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="show"
                        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                    >
                        {exams.map(exam => {
                            const isDemo = exam.id.startsWith('demo-') || exam.id.startsWith('categorized-');
                            return (
                                <motion.div key={exam.id} variants={itemVariants} className="relative group flex flex-col h-full">
                                    {/* Harsh offset shadow */}
                                    <div className="absolute inset-0 bg-accent translate-x-2 translate-y-2 transition-transform group-hover:translate-x-3 group-hover:translate-y-3" />

                                    <div className="relative flex flex-col h-full bg-card border-4 border-foreground p-0">
                                        {/* Header area */}
                                        <div className="p-6 border-b-4 border-foreground bg-foreground text-background flex justify-between items-start">
                                            <div className="flex-1 pr-4">
                                                <h3 className="font-display text-xl font-black uppercase leading-tight truncate" title={exam.title}>{exam.title}</h3>
                                                <div className="font-mono text-xs text-background/60 mt-2 truncate">ID: {exam.id.split('-')[0]}***</div>
                                            </div>
                                            {isDemo && (
                                                <span className="px-2 py-1 bg-accent text-background font-mono text-[10px] font-bold uppercase tracking-wider border-2 border-background">
                                                    DEMO
                                                </span>
                                            )}
                                        </div>

                                        {/* Content area */}
                                        <div className="p-6 flex-1 flex flex-col">
                                            <p className="font-sans text-sm text-foreground/80 line-clamp-3 mb-6 flex-1">
                                                {exam.description || "NO_DESCRIPTION_PROVIDED."}
                                            </p>

                                            <div className="grid grid-cols-2 gap-4 font-mono text-xs uppercase tracking-tight py-4 border-y-2 border-dashed border-border/50">
                                                <div>
                                                    <span className="text-foreground/50 block mb-1">DURATION</span>
                                                    <span className="font-bold text-sm text-accent">{exam.duration_minutes}m</span>
                                                </div>
                                                <div>
                                                    <span className="text-foreground/50 block mb-1">CAPACITY</span>
                                                    <span className="font-bold text-sm">{exam.question_count ?? exam.questions?.length ?? 0} Qs</span>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="flex border-t-4 border-foreground">
                                            <Link href={`/exam/${exam.id}`}
                                                className="flex-1 flex items-center justify-center gap-2 py-4 font-display font-bold uppercase tracking-widest text-sm hover:bg-accent hover:text-background transition-colors group/btn">
                                                PREVIEW
                                                <ArrowRight className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                                            </Link>
                                            {!isDemo && (
                                                <button onClick={() => handleDelete(exam.id)}
                                                    disabled={deleting === exam.id}
                                                    className="px-6 border-l-4 border-foreground font-display font-bold text-background bg-red-600 hover:bg-red-700 transition-colors disabled:opacity-50 disabled:bg-gray-600 flex items-center justify-center">
                                                    {deleting === exam.id ? <div className="w-5 h-5 border-2 border-background border-t-red-600 rounded-full animate-spin" /> : <Trash2 className="w-5 h-5" />}
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })}
                    </motion.div>
                )}
            </main>
        </div>
    );
}
