/**
 * Home Page - Exam Selection
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { listExams, Exam } from '@/lib/api';

export default function HomePage() {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadExams() {
      try {
        const data = await listExams();
        setExams(data.exams);
      } catch (err) {
        setError('Failed to load exams. Make sure the backend is running.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadExams();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">🎓</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Cheating Detection System
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Privacy-Preserving Online Exam Proctoring
              </p>
            </div>
          </div>
          <Link
            href="/admin"
            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            Admin Dashboard
          </Link>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Available Exams
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Select an exam to begin. Your behavior will be monitored using AI-based analysis
            to ensure academic integrity — no camera or microphone required.
          </p>
        </div>

        {/* Error state */}
        {error && (
          <div className="max-w-xl mx-auto mb-8 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <p className="text-sm text-red-500 dark:text-red-500 mt-2">
              Run <code className="bg-red-100 dark:bg-red-900/30 px-1 rounded">uvicorn app.main:app --reload</code> in the backend directory.
            </p>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        )}

        {/* Exams grid */}
        {!loading && !error && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {exams.map((exam) => (
              <div
                key={exam.id}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                <div className="h-2 bg-gradient-to-r from-blue-500 to-indigo-600"></div>
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {exam.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                    {exam.description}
                  </p>

                  <div className="flex items-center gap-4 mb-6 text-sm">
                    <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
                      <span>⏱️</span>
                      <span>{exam.duration_minutes} min</span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
                      <span>📝</span>
                      <span>{exam.question_count} questions</span>
                    </div>
                  </div>

                  <Link
                    href={`/exam/${exam.id}`}
                    className="block w-full py-3 text-center bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-medium rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all"
                  >
                    Start Exam
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Feature highlights */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="w-16 h-16 mx-auto mb-4 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
              <span className="text-3xl">🔒</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Privacy-First
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              No camera or microphone required. Detection is based on typing behavior and answer analysis.
            </p>
          </div>
          <div className="text-center p-6">
            <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
              <span className="text-3xl">🤖</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              AI-Powered
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Advanced machine learning analyzes keystroke dynamics, hesitation patterns, and answer similarity.
            </p>
          </div>
          <div className="text-center p-6">
            <div className="w-16 h-16 mx-auto mb-4 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center">
              <span className="text-3xl">📊</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Explainable Results
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Every flag comes with clear reasons, enabling fair review and human oversight.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
