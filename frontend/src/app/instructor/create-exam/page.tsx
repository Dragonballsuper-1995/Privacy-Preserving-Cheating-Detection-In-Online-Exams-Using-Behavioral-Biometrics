/**
 * Create Exam Page
 * Lets instructors build an exam with questions
 */

'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, ChevronLeft, Save, Code, AlignLeft, CheckSquare, AlertTriangle } from 'lucide-react';
import { createExam, addQuestion, isAuthenticated } from '@/lib/api';

/* ───── question draft type ───── */
interface QuestionDraft {
    localId: string;
    type: 'mcq' | 'subjective' | 'coding';
    content: string;
    points: number;
    options: { id: string; text: string }[];
    correctOption: string;
    codeTemplate: string;
    language: string;
    minWords: number;
    maxWords: number;
}

function emptyQuestion(): QuestionDraft {
    return {
        localId: crypto.randomUUID(),
        type: 'mcq',
        content: '',
        points: 10,
        options: [
            { id: 'a', text: '' },
            { id: 'b', text: '' },
            { id: 'c', text: '' },
            { id: 'd', text: '' },
        ],
        correctOption: 'a',
        codeTemplate: '',
        language: 'python',
        minWords: 0,
        maxWords: 200,
    };
}

/* ───── page ───── */
export default function CreateExamPage() {
    const router = useRouter();
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [duration, setDuration] = useState(30);
    const [questions, setQuestions] = useState<QuestionDraft[]>([emptyQuestion()]);
    const [activeIdx, setActiveIdx] = useState(0);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    /* ── update question helper ── */
    const update = useCallback((idx: number, patch: Partial<QuestionDraft>) => {
        setQuestions(prev => prev.map((q, i) => (i === idx ? { ...q, ...patch } : q)));
    }, []);

    /* ── add / remove question ── */
    const addQ = () => {
        setQuestions(prev => [...prev, emptyQuestion()]);
        setActiveIdx(questions.length);
    };
    const removeQ = (idx: number) => {
        if (questions.length <= 1) return;
        setQuestions(prev => prev.filter((_, i) => i !== idx));
        if (activeIdx >= questions.length - 1) setActiveIdx(Math.max(0, questions.length - 2));
    };

    /* ── option helpers ── */
    const updateOption = (qIdx: number, optIdx: number, text: string) => {
        setQuestions(prev =>
            prev.map((q, i) =>
                i === qIdx
                    ? { ...q, options: q.options.map((o, j) => (j === optIdx ? { ...o, text } : o)) }
                    : q,
            ),
        );
    };

    /* ── submit ── */
    const handleSubmit = async () => {
        setError('');
        if (!title.trim()) { setError('EXAM_TITLE_REQUIRED'); return; }
        if (questions.some(q => !q.content.trim())) { setError('ALL_QUESTIONS_REQUIRE_CONTENT'); return; }

        setSaving(true);
        try {
            const { exam_id } = await createExam(title, description, duration);

            // Add each question
            for (const q of questions) {
                const payload: Record<string, unknown> = {
                    id: q.localId,
                    type: q.type,
                    content: q.content,
                    points: q.points,
                    category: q.type,
                };

                if (q.type === 'mcq') {
                    payload.options = q.options.filter(o => o.text.trim());
                    payload.correct_option = q.correctOption;
                }
                if (q.type === 'coding') {
                    payload.code_template = q.codeTemplate;
                    payload.language = q.language;
                }
                if (q.type === 'subjective') {
                    payload.min_words = q.minWords;
                    payload.max_words = q.maxWords;
                }

                await addQuestion(exam_id, payload as Parameters<typeof addQuestion>[1]);
            }

            router.push('/instructor');
        } catch (err) {
            setError((err as Error).message || 'FAILED_TO_DEPLOY_EXAM');
        } finally {
            setSaving(false);
        }
    };

    /* guard */
    if (!isAuthenticated()) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background p-4">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="max-w-md w-full border-4 border-foreground bg-card p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,0.1)] text-center space-y-6"
                >
                    <AlertTriangle className="w-16 h-16 mx-auto text-accent" />
                    <h2 className="font-display text-3xl font-black uppercase tracking-tighter">RESTRICTED_ACCESS</h2>
                    <p className="font-mono text-sm text-foreground/70 uppercase">AUTHORIZATION_REQUIRED_FOR_EXAM_CREATION</p>
                    <Link href="/login" className="block w-full py-4 border-2 border-foreground bg-accent text-background font-display font-bold uppercase tracking-widest hover:bg-foreground hover:text-background transition-colors">
                        AUTHENTICATE
                    </Link>
                </motion.div>
            </div>
        );
    }

    const q = questions[activeIdx];

    return (
        <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background pb-32">
            {/* ── Header ── */}
            <header className="sticky top-0 z-30 bg-background border-b-4 border-foreground">
                <div className="max-w-6xl mx-auto flex items-center justify-between p-4 md:p-6 gap-4">
                    <div className="flex items-center gap-4">
                        <Link href="/instructor" className="p-2 border-2 border-foreground hover:bg-accent hover:text-background transition-colors">
                            <ChevronLeft className="w-6 h-6 stroke-[3]" />
                        </Link>
                        <div>
                            <h1 className="font-display text-xl md:text-2xl font-black uppercase tracking-tight">INITIALIZE_EXAM</h1>
                            <p className="font-mono text-xs text-foreground/60 tracking-widest uppercase hidden sm:block">DEPLOY_NEW_ASSESSMENT_VECTOR</p>
                        </div>
                    </div>
                    <button onClick={handleSubmit} disabled={saving}
                        className="flex items-center gap-2 px-6 py-3 bg-accent text-background border-2 border-foreground font-display font-bold uppercase tracking-widest transition-all hover:bg-foreground disabled:opacity-50 disabled:cursor-not-allowed group">
                        {saving ? (
                            <div className="w-5 h-5 border-2 border-background border-t-transparent rounded-full animate-spin" />
                        ) : (
                            <Save className="w-5 h-5 stroke-[3] group-hover:scale-110 transition-transform" />
                        )}
                        <span className="hidden sm:inline">{saving ? 'DEPLOYING...' : 'PUBLISH_EXAM'}</span>
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 md:px-6 py-8 space-y-12">
                <AnimatePresence>
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="bg-red-500 text-background font-mono p-4 border-4 border-foreground font-bold uppercase shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.1)] flex items-center gap-3"
                        >
                            <AlertTriangle className="w-6 h-6 stroke-[3]" />
                            <span>ERROR: {error}</span>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* ── Exam metadata ── */}
                <section className="bg-card border-4 border-foreground p-6 md:p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,0.1)] relative">
                    <div className="absolute top-0 right-0 bg-foreground text-background font-mono text-xs px-3 py-1 font-bold uppercase tracking-widest">
                        METADATA
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4">
                        <div className="md:col-span-2 space-y-2">
                            <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">EXAM_TITLE</label>
                            <input value={title} onChange={e => setTitle(e.target.value)}
                                placeholder="E.G. DATA STRUCTURES MIDTERM"
                                className="w-full px-4 py-3 border-4 border-foreground bg-background font-display font-bold text-lg focus:outline-none focus:border-accent transition-colors placeholder:text-foreground/20" />
                        </div>
                        <div className="md:col-span-2 space-y-2">
                            <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">DESCRIPTION_LOG</label>
                            <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3}
                                placeholder="ENTER SUMMARY OF THIS ASSESSMENT..."
                                className="w-full px-4 py-3 border-4 border-foreground bg-background font-sans text-sm focus:outline-none focus:border-accent resize-y transition-colors placeholder:text-foreground/20" />
                        </div>
                        <div className="space-y-2">
                            <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">TIME_LIMIT (MINUTES)</label>
                            <input type="number" value={duration} onChange={e => setDuration(+e.target.value)} min={5} max={300}
                                className="w-full px-4 py-3 border-4 border-foreground bg-background font-mono font-bold text-xl focus:outline-none focus:border-accent transition-colors" />
                        </div>
                    </div>
                </section>

                {/* ── Question tabs + editor ── */}
                <section className="bg-card border-4 border-foreground shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,0.1)] flex flex-col md:flex-row">

                    {/* Sidebar Tabs */}
                    <div className="md:w-48 xl:w-64 border-b-4 md:border-b-0 md:border-r-4 border-foreground bg-foreground/5 flex flex-row md:flex-col overflow-x-auto md:overflow-y-auto">
                        <div className="p-4 border-b-4 border-foreground bg-foreground text-background hidden md:block">
                            <h3 className="font-display font-bold uppercase tracking-widest">QUESTIONS</h3>
                        </div>
                        {questions.map((_, i) => (
                            <button key={i} onClick={() => setActiveIdx(i)}
                                className={`flex-shrink-0 md:w-full px-6 py-4 border-r-4 md:border-r-0 md:border-b-4 border-foreground font-mono font-bold text-lg uppercase transition-colors text-left ${i === activeIdx
                                    ? 'bg-accent text-background border-b-accent' // active
                                    : 'bg-transparent text-foreground hover:bg-foreground/10'
                                    }`}>
                                Q_0{i + 1}
                            </button>
                        ))}
                        <button onClick={addQ}
                            className="flex-shrink-0 md:w-full px-6 py-4 flex items-center justify-center gap-2 font-mono font-bold text-sm uppercase text-foreground hover:bg-accent hover:text-background transition-colors group">
                            <Plus className="w-5 h-5 stroke-[3] group-hover:scale-125 transition-transform" />
                            <span className="hidden md:inline">ADD_NODE</span>
                        </button>
                    </div>

                    {/* Editor Panel */}
                    <div className="flex-1 p-6 md:p-8 bg-background relative min-w-0">
                        {q && (
                            <div className="space-y-8 animate-in fade-in duration-300">

                                {/* Header / Type Selector */}
                                <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6 border-b-4 border-foreground pb-6">
                                    <div className="flex flex-wrap items-center gap-3">
                                        {(['mcq', 'subjective', 'coding'] as const).map(t => {
                                            const icons = { mcq: CheckSquare, subjective: AlignLeft, coding: Code };
                                            const Icon = icons[t];
                                            return (
                                                <button key={t} onClick={() => update(activeIdx, { type: t })}
                                                    className={`px-4 py-2 border-2 border-foreground font-mono text-xs uppercase font-bold tracking-widest flex items-center gap-2 transition-colors ${q.type === t
                                                        ? 'bg-foreground text-background'
                                                        : 'bg-transparent hover:bg-foreground/10'
                                                        }`}>
                                                    <Icon className="w-4 h-4" />
                                                    {t === 'mcq' ? 'MULTIPLE_CHOICE' : t}
                                                </button>
                                            );
                                        })}
                                    </div>

                                    <div className="flex items-center gap-4">
                                        <div className="flex items-center gap-2 bg-foreground/5 px-4 py-2 border-2 border-foreground">
                                            <label className="font-mono text-xs uppercase font-bold">PTS:</label>
                                            <input type="number" value={q.points} onChange={e => update(activeIdx, { points: +e.target.value })} min={1} max={100}
                                                className="w-16 bg-transparent font-mono font-black text-lg text-right outline-none text-accent" />
                                        </div>
                                        {questions.length > 1 && (
                                            <button onClick={() => removeQ(activeIdx)}
                                                className="p-3 border-2 border-foreground text-foreground hover:bg-red-500 hover:text-background hover:border-red-500 transition-colors"
                                                title="DELETE QUESTION">
                                                <Trash2 className="w-5 h-5 stroke-[3]" />
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {/* Content text area */}
                                <div className="space-y-3">
                                    <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">PROMPT_DATA</label>
                                    <textarea value={q.content} onChange={e => update(activeIdx, { content: e.target.value })} rows={4}
                                        placeholder="ENTER QUESTION PROMPT HERE..."
                                        className="w-full px-4 py-4 border-4 border-foreground bg-card font-sans text-base focus:outline-none focus:border-accent resize-y transition-colors placeholder:text-foreground/30 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.1)]" />
                                </div>

                                {/* Dynamic Fields based on Type */}
                                <div className="pt-4">
                                    {/* MCQ options */}
                                    {q.type === 'mcq' && (
                                        <div className="space-y-4">
                                            <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">EVALUATION_MATRIX [SELECT CORRECT]</label>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {q.options.map((opt, oi) => (
                                                    <div key={opt.id}
                                                        className={`flex items-center border-4 transition-colors ${q.correctOption === opt.id ? 'border-accent bg-accent/5' : 'border-foreground bg-card focus-within:border-accent/50'}`}>
                                                        <label className="flex items-center justify-center p-4 cursor-pointer">
                                                            <div className="relative flex items-center justify-center w-6 h-6 border-2 border-foreground bg-background">
                                                                <input type="radio" name={`correct-${q.localId}`}
                                                                    checked={q.correctOption === opt.id}
                                                                    onChange={() => update(activeIdx, { correctOption: opt.id })}
                                                                    className="appearance-none peer absolute inset-0 cursor-pointer" />
                                                                <div className="w-3 h-3 bg-accent opacity-0 peer-checked:opacity-100 transition-opacity" />
                                                            </div>
                                                        </label>
                                                        <div className="font-mono text-xl font-black uppercase px-2 text-foreground/30">{opt.id}</div>
                                                        <input value={opt.text}
                                                            onChange={e => updateOption(activeIdx, oi, e.target.value)}
                                                            placeholder={`ENTER OPTION ${opt.id.toUpperCase()}`}
                                                            className="flex-1 bg-transparent py-4 pr-4 font-sans focus:outline-none placeholder:text-foreground/20 font-medium" />
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Coding template */}
                                    {q.type === 'coding' && (
                                        <div className="space-y-6">
                                            <div className="max-w-xs space-y-2">
                                                <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">RUNTIME_ENVIRONMENT</label>
                                                <div className="relative">
                                                    <select value={q.language} onChange={e => update(activeIdx, { language: e.target.value })}
                                                        className="w-full appearance-none px-4 py-3 border-4 border-foreground bg-card font-mono font-bold uppercase text-sm outline-none focus:border-accent cursor-pointer">
                                                        <option value="python">PYTHON_3</option>
                                                        <option value="javascript">NODE_JS</option>
                                                        <option value="java">JAVA_17</option>
                                                        <option value="cpp">C++_20</option>
                                                    </select>
                                                    <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                                                        <div className="w-0 h-0 border-l-[6px] border-r-[6px] border-t-[8px] border-l-transparent border-r-transparent border-t-foreground" />
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="space-y-2">
                                                <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">STARTER_TEMPLATE</label>
                                                <textarea value={q.codeTemplate} onChange={e => update(activeIdx, { codeTemplate: e.target.value })} rows={8}
                                                    placeholder="// Inject starter code here..."
                                                    spellCheck={false}
                                                    className="w-full p-4 border-4 border-foreground bg-[#1e1e1e] text-[#d4d4d4] font-mono text-sm focus:outline-none focus:ring-2 focus:ring-accent resize-y transition-shadow" />
                                            </div>
                                        </div>
                                    )}

                                    {/* Subjective constraints */}
                                    {q.type === 'subjective' && (
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-foreground/5 p-6 border-4 border-foreground border-dashed">
                                            <div className="space-y-2">
                                                <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">MINIMUM_WORDS</label>
                                                <input type="number" value={q.minWords} onChange={e => update(activeIdx, { minWords: +e.target.value })} min={0}
                                                    className="w-full px-4 py-3 border-4 border-foreground bg-card font-mono text-xl font-bold outline-none focus:border-accent" />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="block font-mono text-sm font-bold uppercase tracking-widest text-foreground/80">MAXIMUM_WORDS</label>
                                                <input type="number" value={q.maxWords} onChange={e => update(activeIdx, { maxWords: +e.target.value })} min={0}
                                                    className="w-full px-4 py-3 border-4 border-foreground bg-card font-mono text-xl font-bold outline-none focus:border-accent" />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </section>

                {/* ── Preview summary ── */}
                <section className="bg-foreground text-background p-6 md:p-8 relative">
                    {/* Harsh offset shadow via pseudo element or wrapper */}
                    <div className="absolute -inset-2 bg-accent -z-10 translate-x-4 translate-y-4 hidden md:block" />
                    <h2 className="font-display text-xl font-bold uppercase tracking-widest mb-6 text-accent">DEPLOYMENT_SUMMARY</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        {[
                            { label: 'TOTAL_NODES', value: questions.length },
                            { label: 'MCQ_TYPE', value: questions.filter(q => q.type === 'mcq').length },
                            { label: 'CODING_TYPE', value: questions.filter(q => q.type === 'coding').length },
                            { label: 'SUBJECTIVE_TYPE', value: questions.filter(q => q.type === 'subjective').length },
                        ].map(s => (
                            <div key={s.label} className="border-l-4 border-accent pl-4">
                                <p className="font-display text-4xl font-black">{s.value}</p>
                                <p className="font-mono text-[10px] font-bold uppercase tracking-widest text-background/60 mt-1">{s.label}</p>
                            </div>
                        ))}
                    </div>
                    <div className="mt-8 pt-6 border-t-[3px] border-dashed border-background/20 font-mono text-sm flex flex-wrap gap-4 justify-between">
                        <span>EST. MAX_SCORE: <strong className="text-accent">{questions.reduce((s, q) => s + q.points, 0)}</strong></span>
                        <span>ALLOCATED_TIME: <strong className="text-accent">{duration}m</strong></span>
                    </div>
                </section>

                {/* Bottom spacer for scroll room */}
                <div className="h-12" />
            </main>
        </div>
    );
}
