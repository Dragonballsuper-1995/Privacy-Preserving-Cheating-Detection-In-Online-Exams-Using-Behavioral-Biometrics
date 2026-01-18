/**
 * Exam Interface Page
 * Main page for taking exams with behavior logging
 */

'use client';

import { useEffect, useState, useCallback, use } from 'react';
import { useRouter } from 'next/navigation';
import { useBehaviorLogger } from '@/hooks/useBehaviorLogger';
import { QuestionRenderer } from '@/components/QuestionRenderer';
import { getExam, createSession, startSession, submitSession, submitAnswer, Exam } from '@/lib/api';

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
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [examStarted, setExamStarted] = useState(false);
    const [error, setError] = useState<string>('');

    const currentQuestion = exam?.questions?.[currentQuestionIndex];

    // Behavior logger
    const { flushEvents } = useBehaviorLogger({
        sessionId,
        questionId: currentQuestion?.id || '',
        enabled: examStarted && !!sessionId,
    });

    // Load exam data
    useEffect(() => {
        async function loadExam() {
            try {
                const examData = await getExam(examId);
                setExam(examData);
                setTimeRemaining(examData.duration_minutes * 60);

                // Initialize answers
                const initialAnswers: Record<string, string> = {};
                examData.questions?.forEach((q) => {
                    initialAnswers[q.id] = q.type === 'coding' ? (q.code_template || '') : '';
                });
                setAnswers(initialAnswers);
            } catch (err) {
                setError('Failed to load exam');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        }
        loadExam();
    }, [examId]);

    // Timer
    useEffect(() => {
        if (!examStarted || timeRemaining <= 0) return;

        const timer = setInterval(() => {
            setTimeRemaining((prev) => {
                if (prev <= 1) {
                    handleSubmit(); // Auto-submit when time runs out
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [examStarted, timeRemaining]);

    // Format time
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // Start exam
    const handleStart = async () => {
        try {
            // Create session with a simple student ID (in real app, this would come from auth)
            const session = await createSession(examId, `student_${Date.now()}`);
            setSessionId(session.id);
            await startSession(session.id);
            setExamStarted(true);
        } catch (err) {
            setError('Failed to start exam');
            console.error(err);
        }
    };

    // Update answer
    const handleAnswerChange = useCallback((answer: string) => {
        if (!currentQuestion) return;
        setAnswers((prev) => ({ ...prev, [currentQuestion.id]: answer }));
    }, [currentQuestion]);

    // Navigate questions
    const goToQuestion = (index: number) => {
        if (index >= 0 && index < (exam?.questions?.length || 0)) {
            setCurrentQuestionIndex(index);
        }
    };

    // Submit exam
    const handleSubmit = async () => {
        if (!sessionId) return;

        setIsSubmitting(true);
        try {
            // Flush any remaining events
            await flushEvents();

            // Submit all answers
            for (const [questionId, content] of Object.entries(answers)) {
                await submitAnswer(sessionId, questionId, content);
            }

            // Submit session
            await submitSession(sessionId);

            // Redirect to completion page
            router.push(`/exam/complete?session=${sessionId}`);
        } catch (err) {
            setError('Failed to submit exam');
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading exam...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="text-center">
                    <p className="text-red-500 text-lg">{error}</p>
                    <button
                        onClick={() => router.push('/')}
                        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Go Home
                    </button>
                </div>
            </div>
        );
    }

    // Pre-exam start screen
    if (!examStarted) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
                <div className="max-w-2xl w-full mx-4 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">{exam?.title}</h1>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">{exam?.description}</p>

                    <div className="grid grid-cols-2 gap-4 mb-8">
                        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                            <p className="text-sm text-blue-600 dark:text-blue-400">Duration</p>
                            <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                                {exam?.duration_minutes} minutes
                            </p>
                        </div>
                        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                            <p className="text-sm text-green-600 dark:text-green-400">Questions</p>
                            <p className="text-2xl font-bold text-green-700 dark:text-green-300">
                                {exam?.questions?.length}
                            </p>
                        </div>
                    </div>

                    <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 mb-6">
                        <h3 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">⚠️ Important Notes</h3>
                        <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                            <li>• Your behavior is being monitored for academic integrity</li>
                            <li>• Do not switch tabs or windows during the exam</li>
                            <li>• Copying and pasting from external sources will be detected</li>
                            <li>• The exam will auto-submit when time runs out</li>
                        </ul>
                    </div>

                    <button
                        onClick={handleStart}
                        className="w-full py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg"
                    >
                        Start Exam
                    </button>
                </div>
            </div>
        );
    }

    // Main exam interface
    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            {/* Header with timer */}
            <header className="fixed top-0 left-0 right-0 bg-white dark:bg-gray-800 shadow-md z-50">
                <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
                    <div>
                        <h1 className="text-lg font-semibold text-gray-900 dark:text-white">{exam?.title}</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            Question {currentQuestionIndex + 1} of {exam?.questions?.length}
                        </p>
                    </div>

                    <div className={`px-4 py-2 rounded-lg font-mono text-lg font-bold ${timeRemaining < 300
                        ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
                        : 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                        }`}>
                        ⏱️ {formatTime(timeRemaining)}
                    </div>
                </div>
            </header>

            {/* Main content */}
            <main className="pt-24 pb-32 px-4">
                <div className="max-w-4xl mx-auto">
                    {/* Question */}
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
                        <div className="flex items-center justify-between mb-4">
                            <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full text-sm font-medium">
                                {currentQuestion?.type?.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                                {currentQuestion?.points} points
                            </span>
                        </div>

                        {currentQuestion && (
                            <QuestionRenderer
                                question={currentQuestion}
                                answer={answers[currentQuestion.id] || ''}
                                onAnswerChange={handleAnswerChange}
                            />
                        )}
                    </div>

                    {/* Question navigation pills */}
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">Quick Navigation:</p>
                        <div className="flex flex-wrap gap-2">
                            {exam?.questions?.map((q, index) => (
                                <button
                                    key={q.id}
                                    onClick={() => goToQuestion(index)}
                                    className={`w-10 h-10 rounded-lg font-medium transition-all ${index === currentQuestionIndex
                                        ? 'bg-blue-500 text-white'
                                        : answers[q.id] && answers[q.id] !== (q.code_template || '')
                                            ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                            : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                                        }`}
                                >
                                    {index + 1}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </main>

            {/* Footer navigation */}
            <footer className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
                <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
                    <button
                        onClick={() => goToQuestion(currentQuestionIndex - 1)}
                        disabled={currentQuestionIndex === 0}
                        className="px-6 py-2 rounded-lg border-2 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                        ← Previous
                    </button>

                    {currentQuestionIndex === (exam?.questions?.length || 0) - 1 ? (
                        <button
                            onClick={handleSubmit}
                            disabled={isSubmitting}
                            className="px-6 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:opacity-50 transition-colors"
                        >
                            {isSubmitting ? 'Submitting...' : 'Submit Exam'}
                        </button>
                    ) : (
                        <button
                            onClick={() => goToQuestion(currentQuestionIndex + 1)}
                            className="px-6 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
                        >
                            Next →
                        </button>
                    )}
                </div>
            </footer>
        </div>
    );
}
