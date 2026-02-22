/**
 * Exam Interface Page
 * Main page for taking exams with behavior logging
 *
 * Features:
 *  - ExamTimer with green → yellow → red color tiers & auto-submit
 *  - ProgressBar with answered count and clickable question bubbles
 *  - Confirmation dialog before final submission
 *  - Keyboard shortcuts: ← / → (navigation), Ctrl+Enter (submit)
 */

'use client';

import { useEffect, useState, useCallback, useRef, use, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useBehaviorLogger } from '@/hooks/useBehaviorLogger';
import { QuestionRenderer } from '@/components/QuestionRenderer';
import { ExamTimer } from '@/components/ExamTimer';
import { ProgressBar } from '@/components/ProgressBar';
import { getExam, createSession, startSession, submitSession, submitAnswer, Exam } from '@/lib/api';
import { Terminal, AlertTriangle, ChevronRight, ChevronLeft, Save, Loader2, Database, ShieldAlert, CheckCircle2, Key } from 'lucide-react';

interface PageProps {
    params: Promise<{ examId: string }>;
}

export default function ExamPage({ params }: PageProps) {
    const { examId } = use(params);
    const router = useRouter();

    // State
    const [exam, setExam] = useState<Exam | null>(null);
    const [sessionId, setSessionId] = useState<string>('');
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState<Record<string, string>>({});
    const [timeRemaining, setTimeRemaining] = useState<number>(0);
    const [totalTime, setTotalTime] = useState<number>(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [examStarted, setExamStarted] = useState(false);
    const [error, setError] = useState<string>('');
    const [showConfirm, setShowConfirm] = useState(false);

    const currentQuestion = exam?.questions?.[currentQuestionIndex];
    const questionIds = useMemo(() => exam?.questions?.map(q => q.id) || [], [exam]);

    // Default answers (e.g. code templates) — used to tell answered vs unanswered
    const defaultAnswers = useMemo(() => {
        const d: Record<string, string> = {};
        exam?.questions?.forEach(q => {
            if (q.type === 'coding' && q.code_template) d[q.id] = q.code_template;
        });
        return d;
    }, [exam]);

    // Behavior logger
    const { flushEvents } = useBehaviorLogger({
        sessionId,
        questionId: currentQuestion?.id || '',
        enabled: examStarted && !!sessionId,
    });

    // ── Load exam data ──
    useEffect(() => {
        async function loadExam() {
            try {
                const examData = await getExam(examId);
                setExam(examData);
                const total = examData.duration_minutes * 60;
                setTimeRemaining(total);
                setTotalTime(total);

                // Initialize answers
                const initialAnswers: Record<string, string> = {};
                examData.questions?.forEach((q) => {
                    initialAnswers[q.id] = q.type === 'coding' ? (q.code_template || '') : '';
                });
                setAnswers(initialAnswers);
            } catch (err) {
                setError('SYSTEM_ERROR: FAILED_TO_LOAD_EXAM_DATA');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        }
        loadExam();
    }, [examId]);

    // ── Timer ──
    useEffect(() => {
        if (!examStarted || timeRemaining <= 0) return;

        const timer = setInterval(() => {
            setTimeRemaining((prev) => Math.max(prev - 1, 0));
        }, 1000);

        return () => clearInterval(timer);
    }, [examStarted, timeRemaining]);

    // ── Update answer ──
    const handleAnswerChange = useCallback((answer: string) => {
        if (!currentQuestion) return;
        setAnswers((prev) => ({ ...prev, [currentQuestion.id]: answer }));
    }, [currentQuestion]);

    // ── Navigate questions ──
    const goToQuestion = useCallback((index: number) => {
        if (index >= 0 && index < (exam?.questions?.length || 0)) {
            setCurrentQuestionIndex(index);
        }
    }, [exam?.questions?.length]);

    // ── Keyboard shortcuts ──
    useEffect(() => {
        if (!examStarted) return;

        function handleKeyDown(e: KeyboardEvent) {
            // Ignore when typing in textarea / input / contentEditable
            const tag = (e.target as HTMLElement).tagName;
            const editable = (e.target as HTMLElement).isContentEditable;
            if (['TEXTAREA', 'INPUT'].includes(tag) || editable) {
                // Only allow Ctrl+Enter from inputs
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    setShowConfirm(true);
                }
                return;
            }

            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                goToQuestion(currentQuestionIndex - 1);
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                goToQuestion(currentQuestionIndex + 1);
            } else if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                setShowConfirm(true);
            }
        }

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [examStarted, currentQuestionIndex, goToQuestion]);

    // ── Start exam ──
    const handleStart = async () => {
        try {
            const session = await createSession(examId, `student_${Date.now()}`);
            setSessionId(session.id);
            await startSession(session.id);
            setExamStarted(true);
        } catch (err) {
            setError('CRITICAL_ERROR: SYSTEM_FAILED_TO_INITIALIZE_SESSION');
            console.error(err);
        }
    };

    // ── Submit exam (actual) ──
    const doSubmit = async () => {
        if (!sessionId) return;
        setIsSubmitting(true);
        setShowConfirm(false);
        try {
            await flushEvents();
            for (const [questionId, content] of Object.entries(answers)) {
                await submitAnswer(sessionId, questionId, content);
            }
            await submitSession(sessionId);
            router.push(`/exam/complete?session=${sessionId}`);
        } catch (err) {
            setError('CRITICAL_ERROR: FAILED_TO_TRANSMIT_DATA');
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    // ── Auto-submit ref (avoids stale closure) ──
    const doSubmitRef = useRef(doSubmit);
    doSubmitRef.current = doSubmit;

    // ── Auto-submit when time runs out ──
    useEffect(() => {
        if (examStarted && timeRemaining <= 0) {
            doSubmitRef.current();
        }
    }, [examStarted, timeRemaining]);

    // ── Computed helpers ──
    const answeredCount = questionIds.filter(
        id => answers[id] && answers[id] !== (defaultAnswers[id] || '')
    ).length;
    const unansweredCount = questionIds.length - answeredCount;

    // ── Loading state ──
    if (isLoading) {
        return (
            <div className="min-h-screen text-foreground flex items-center justify-center p-4 selection:bg-accent selection:text-background">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center gap-4"
                >
                    <div className="w-10 h-10 border-4 border-muted border-t-primary rounded-full animate-spin" />
                    <p className="font-sans text-sm font-semibold tracking-wider text-muted-foreground animate-pulse">Establishing Connection...</p>
                </motion.div>
            </div>
        );
    }

    // ── Error state ──
    if (error) {
        return (
            <div className="min-h-screen text-foreground flex items-center justify-center p-4 selection:bg-accent selection:text-background">
                <div className="max-w-md w-full p-8 rounded-xl bg-destructive/10 text-destructive border border-destructive/20 shadow-sm">
                    <div className="flex items-center gap-4 mb-6 pb-4 border-b border-destructive/20">
                        <ShieldAlert className="w-10 h-10" />
                        <h2 className="font-display text-2xl font-bold tracking-tight">System Error</h2>
                    </div>
                    <p className="font-mono text-base font-bold uppercase mb-8">{error}</p>
                    <button
                        onClick={() => router.push('/')}
                        className="w-full py-4 border-4 border-white bg-foreground text-white font-mono font-bold uppercase tracking-widest hover:bg-white hover:text-[#ff003c] transition-colors"
                    >
                        RETURN_TO_BASE
                    </button>
                </div>
            </div>
        );
    }

    // ── Pre-exam start screen ──
    if (!examStarted) {
        return (
            <div className="min-h-screen text-foreground font-sans flex items-center justify-center p-4 selection:bg-accent selection:text-background">
                <div className="max-w-2xl w-full bg-card rounded-xl border border-border shadow-lg overflow-hidden relative">
                    <div className="h-2 w-full bg-primary/20" />

                    <div className="p-8 md:p-10">
                        <div className="flex items-start gap-4 mb-6">
                            <div className="p-3 rounded-lg bg-primary/10 text-primary">
                                <Terminal className="w-8 h-8" />
                            </div>
                            <div>
                                <h1 className="font-display text-3xl md:text-5xl font-bold tracking-tight leading-none mb-2">
                                    {exam?.title}
                                </h1>
                                <p className="font-sans text-sm text-muted-foreground">
                                    {exam?.description || 'No description provided.'}
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-8">
                            <div className="p-4 rounded-xl border border-border bg-primary/5 text-primary flex flex-col justify-between">
                                <p className="font-sans text-xs font-semibold uppercase tracking-wider opacity-80 mb-2">Time Limit</p>
                                <p className="font-display text-3xl font-bold tracking-tight flex items-center gap-2">
                                    {exam?.duration_minutes} <span className="text-xl font-sans font-medium">min</span>
                                </p>
                            </div>
                            <div className="p-4 rounded-xl border border-border bg-card text-foreground flex flex-col justify-between shadow-sm bg-foreground/5">
                                <p className="font-sans text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Data Points</p>
                                <p className="font-display text-3xl font-bold tracking-tight flex items-center gap-2">
                                    {exam?.questions?.length} <span className="text-xl font-sans font-medium">nodes</span>
                                </p>
                            </div>
                        </div>

                        <div className="mb-6 p-4 rounded-xl border border-destructive/20 bg-destructive/10">
                            <h3 className="font-sans text-sm font-semibold text-destructive mb-3 flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5" />
                                Protocol Warnings
                            </h3>
                            <ul className="font-sans text-sm space-y-2 text-destructive/90 leading-relaxed font-medium">
                                <li>• Behavior telemetry recording will commence immediately.</li>
                                <li>• External navigation is monitored and logged.</li>
                                <li>• Copy/paste operations will flag session for review.</li>
                                <li>• Compulsory auto-submit on time expiration.</li>
                            </ul>
                        </div>

                        <div className="mb-8 p-4 rounded-xl border border-dashed border-border bg-secondary/50 relative overflow-hidden">
                            <h3 className="font-sans text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2">
                                <Key className="w-4 h-4" />
                                Operator Commands
                            </h3>
                            <ul className="font-sans text-xs font-medium space-y-2">
                                <li className="flex items-center gap-3">
                                    <div className="flex gap-1">
                                        <span className="px-2 py-1 bg-secondary text-secondary-foreground rounded border border-border">←</span>
                                        <span className="px-2 py-1 bg-secondary text-secondary-foreground rounded border border-border">→</span>
                                    </div>
                                    <span className="text-muted-foreground">Navigate Nodes</span>
                                </li>
                                <li className="flex items-center gap-3">
                                    <div className="flex gap-1">
                                        <span className="px-2 py-1 bg-secondary text-secondary-foreground rounded border border-border">CTRL</span>
                                        <span className="px-2 py-1 bg-secondary text-secondary-foreground rounded border border-border">ENTER</span>
                                    </div>
                                    <span className="text-muted-foreground">Transmit Data</span>
                                </li>
                            </ul>
                            <div className="absolute right-[-20px] bottom-[-20px] opacity-5 pointer-events-none text-primary">
                                <Terminal className="w-32 h-32" />
                            </div>
                        </div>

                        <button
                            onClick={handleStart}
                            className="w-full py-4 rounded-xl bg-primary text-primary-foreground font-sans text-lg font-semibold hover:bg-primary/90 transition-all shadow-sm active:scale-[0.98]"
                        >
                            Initiate Protocol
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // ═════════════════════════════════════════
    //  Main exam interface
    // ═════════════════════════════════════════
    return (
        <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background pb-32">

            {/* ── Confirmation dialog ── */}
            {showConfirm && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/80 backdrop-blur-sm p-4" onClick={() => setShowConfirm(false)}>
                    <div
                        className="w-full max-w-lg bg-card rounded-2xl border border-border shadow-xl overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="h-2 w-full bg-destructive" />
                        <div className="p-8">
                            <h2 className="font-display text-2xl font-bold tracking-tight mb-2 flex items-center gap-3 text-destructive">
                                <AlertTriangle className="w-7 h-7" />
                                Confirm Transmit
                            </h2>

                            <div className="my-6 p-4 rounded-xl border border-border bg-secondary/30 space-y-4 font-sans text-sm font-medium">
                                <div className="flex justify-between items-center border-b border-border/50 pb-2">
                                    <span className="text-muted-foreground">Data Points Secured:</span>
                                    <span className="text-lg text-primary">{answeredCount} / {questionIds.length}</span>
                                </div>
                                {unansweredCount > 0 && (
                                    <div className="flex justify-between items-center text-destructive">
                                        <span>Unsecured Points:</span>
                                        <span className="text-lg font-bold animate-pulse">{unansweredCount}</span>
                                    </div>
                                )}
                                <div className="flex justify-between items-center pt-2">
                                    <span className="text-muted-foreground">Time Remaining:</span>
                                    <span className="text-lg">{Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}</span>
                                </div>
                            </div>

                            <div className="flex flex-col sm:flex-row gap-4 mt-8">
                                <button
                                    onClick={() => setShowConfirm(false)}
                                    className="flex-1 py-2.5 rounded-lg border border-border bg-card text-foreground font-sans font-semibold hover:bg-secondary transition-colors"
                                >
                                    Abort
                                </button>
                                <button
                                    onClick={doSubmit}
                                    disabled={isSubmitting}
                                    className={`flex-1 flex justify-center items-center gap-2 py-2.5 rounded-lg font-sans font-semibold transition-all ${isSubmitting
                                        ? 'bg-secondary text-muted-foreground cursor-not-allowed'
                                        : 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm active:scale-[0.98]'
                                        }`}
                                >
                                    {isSubmitting ? (
                                        <><Loader2 className="w-4 h-4 animate-spin" /> Transmitting...</>
                                    ) : (
                                        <><CheckCircle2 className="w-4 h-4" /> Transmit</>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Header ── */}
            <header className="fixed top-0 left-0 right-0 bg-background/80 border-b border-border z-40 backdrop-blur-md">
                <motion.div
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.3 }}
                    className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4"
                >
                    <div className="min-w-0 flex-1 flex items-center gap-4">
                        <div className="hidden sm:flex p-2 rounded-lg bg-primary/10 text-primary">
                            <Terminal className="w-5 h-5" />
                        </div>
                        <div>
                            <h1 className="font-display text-lg md:text-xl font-bold tracking-tight truncate">
                                {exam?.title}
                            </h1>
                            <p className="font-sans text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                Node ID: {currentQuestionIndex + 1} / {exam?.questions?.length}
                            </p>
                        </div>
                    </div>
                    {/* Wrapping ExamTimer inside a clean container. */}
                    <div className="rounded-lg border border-border bg-card shadow-sm mx-2">
                        <ExamTimer remaining={timeRemaining} total={totalTime} />
                    </div>
                </motion.div>

                {/* Progress bar strip */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="px-4 pb-3 max-w-7xl mx-auto border-t border-border/50 pt-3"
                >
                    <ProgressBar
                        total={questionIds.length}
                        current={currentQuestionIndex}
                        questionIds={questionIds}
                        answers={answers}
                        defaults={defaultAnswers}
                        onNavigate={goToQuestion}
                    />
                </motion.div>
            </header>

            {/* ── Main content ── */}
            <main className="pt-40 md:pt-48 px-4 pb-12">
                <div className="max-w-4xl mx-auto">
                    {/* Question card */}
                    <div className="bg-card rounded-2xl border border-border shadow-sm overflow-hidden mb-6">

                        <div className="flex items-center justify-between p-4 border-b border-border bg-secondary/30">
                            <span className="px-3 py-1 rounded-full bg-primary/10 text-primary font-sans text-xs font-semibold uppercase tracking-wider">
                                Type: {currentQuestion?.type?.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className="font-sans text-sm font-bold flex items-center gap-2 text-muted-foreground">
                                <Database className="w-4 h-4" />
                                {currentQuestion?.points} pts
                            </span>
                        </div>

                        <div className="p-6 md:p-8">
                            {currentQuestion && (
                                <QuestionRenderer
                                    question={currentQuestion}
                                    answer={answers[currentQuestion.id] || ''}
                                    onAnswerChange={handleAnswerChange}
                                />
                            )}
                        </div>
                    </div>
                </div>
            </main>

            {/* ── Footer navigation ── */}
            < footer className="fixed bottom-0 left-0 right-0 bg-background/80 border-t border-border z-40 backdrop-blur-md" >
                <div className="max-w-4xl mx-auto px-4 py-4 flex flex-wrap items-center justify-between gap-4">
                    <button
                        onClick={() => goToQuestion(currentQuestionIndex - 1)}
                        disabled={currentQuestionIndex === 0}
                        className="px-4 md:px-6 py-2.5 rounded-lg flex items-center gap-2 border border-border bg-card font-sans font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-secondary transition-colors"
                    >
                        <ChevronLeft className="w-4 h-4" />
                        <span className="hidden sm:inline">Prev</span>
                    </button>

                    <span className="hidden md:flex items-center gap-3 font-sans font-medium text-xs text-muted-foreground uppercase tracking-wider">
                        <span>Nav: <kbd className="bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded border border-border/50 text-[10px]">←</kbd> <kbd className="bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded border border-border/50 text-[10px]">→</kbd></span>
                        <span className="opacity-50">|</span>
                        <span>Exec: <kbd className="bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded border border-border/50 text-[10px]">CTRL</kbd> + <kbd className="bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded border border-border/50 text-[10px]">ENTER</kbd></span>
                    </span>

                    {currentQuestionIndex === (exam?.questions?.length || 0) - 1 ? (
                        <button
                            onClick={() => setShowConfirm(true)}
                            disabled={isSubmitting}
                            className={`px-4 md:px-8 py-2.5 rounded-lg flex items-center gap-2 font-sans font-semibold text-sm transition-all ${isSubmitting
                                ? 'bg-secondary text-muted-foreground cursor-not-allowed'
                                : 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm active:scale-[0.98]'
                                }`}
                        >
                            {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                            <span className="hidden sm:inline">{isSubmitting ? 'Processing...' : 'Final Transmit'}</span>
                            <span className="sm:hidden">{isSubmitting ? 'Wait' : 'Done'}</span>
                        </button>
                    ) : (
                        <button
                            onClick={() => goToQuestion(currentQuestionIndex + 1)}
                            className="px-4 md:px-6 py-2.5 rounded-lg flex items-center gap-2 border border-border bg-card font-sans font-semibold text-sm hover:bg-secondary transition-colors active:scale-[0.98]"
                        >
                            <span className="hidden sm:inline">Next</span>
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    )}
                </div>
            </footer>
        </div>
    );
}
