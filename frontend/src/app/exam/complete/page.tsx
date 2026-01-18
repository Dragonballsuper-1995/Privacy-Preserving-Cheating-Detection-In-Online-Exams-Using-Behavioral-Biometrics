/**
 * Exam Completion Page
 * Shows after exam submission
 */

'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { analyzeSession, RiskScore } from '@/lib/api';

function CompletionContent() {
    const searchParams = useSearchParams();
    const sessionId = searchParams.get('session');
    const [analysis, setAnalysis] = useState<RiskScore | null>(null);
    const [loading, setLoading] = useState(true);
    const [analysisError, setAnalysisError] = useState(false);

    useEffect(() => {
        async function analyze() {
            if (!sessionId) {
                setLoading(false);
                return;
            }
            try {
                const result = await analyzeSession(sessionId);
                setAnalysis(result);
                setAnalysisError(false);
            } catch (err) {
                console.error('Analysis failed:', err);
                setAnalysisError(true);
                // Analysis failed but that's okay - exam was still submitted
            } finally {
                setLoading(false);
            }
        }
        analyze();
    }, [sessionId]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800">
            <div className="max-w-2xl w-full mx-4 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 text-center">
                <div className="w-20 h-20 mx-auto mb-6 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                    <svg className="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                </div>

                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                    Exam Submitted Successfully!
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mb-8">
                    Your exam has been submitted and is being analyzed.
                </p>


                {loading ? (
                    <div className="animate-pulse bg-gray-100 dark:bg-gray-700 rounded-lg p-6">
                        <p className="text-gray-500 dark:text-gray-400">Analyzing your session...</p>
                    </div>
                ) : analysisError ? (
                    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-8">
                        <div className="flex items-start gap-3">
                            <svg className="w-6 h-6 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <div className="flex-1">
                                <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                                    Analysis Not Available
                                </h3>
                                <p className="text-sm text-blue-700 dark:text-blue-300">
                                    Your exam was submitted successfully, but behavioral analysis is not available for this session.
                                    This may happen if event tracking was not enabled during the exam.
                                </p>
                                {sessionId && (
                                    <p className="text-xs text-blue-600 dark:text-blue-400 mt-2 font-mono">
                                        Session ID: {sessionId}
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                ) : analysis && (
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6 mb-8">
                        <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4">
                            Session Analysis
                        </h2>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
                                <p className="text-gray-500 dark:text-gray-400">Session ID</p>
                                <p className="font-mono text-xs text-gray-700 dark:text-gray-300 truncate">
                                    {sessionId}
                                </p>
                            </div>
                            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
                                <p className="text-gray-500 dark:text-gray-400">Status</p>
                                <p className={`font-semibold ${analysis.is_flagged
                                    ? 'text-red-500'
                                    : 'text-green-500'
                                    }`}>
                                    {analysis.is_flagged ? 'Under Review' : 'Complete'}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                        href="/"
                        className="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
                    >
                        Back to Home
                    </Link>
                    <Link
                        href="/admin"
                        className="px-6 py-3 border-2 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                        View Dashboard
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default function ExamCompletePage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        }>
            <CompletionContent />
        </Suspense>
    );
}
