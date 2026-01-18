/**
 * Question Renderers
 * Components for rendering different types of exam questions
 */

'use client';

import { Question } from '@/lib/api';
import { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import CodeEditor to avoid SSR issues with Monaco
const CodeEditor = dynamic(
    () => import('@/components/CodeEditor').then((mod) => mod.CodeEditor),
    {
        ssr: false,
        loading: () => (
            <div className="h-[400px] bg-gray-900 rounded-lg flex items-center justify-center">
                <div className="text-gray-400">Loading code editor...</div>
            </div>
        )
    }
);

interface QuestionProps {
    question: Question;
    answer: string;
    onAnswerChange: (answer: string) => void;
}

// MCQ Question Component
export function MCQQuestion({ question, answer, onAnswerChange }: QuestionProps) {
    return (
        <div className="space-y-4">
            <p className="text-lg font-medium text-gray-900 dark:text-white">{question.content}</p>
            <div className="space-y-3">
                {question.options?.map((option) => (
                    <label
                        key={option.id}
                        className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${answer === option.id
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
                            }`}
                    >
                        <input
                            type="radio"
                            name={question.id}
                            value={option.id}
                            checked={answer === option.id}
                            onChange={(e) => onAnswerChange(e.target.value)}
                            className="w-4 h-4 text-blue-600"
                        />
                        <span className="ml-3 text-gray-700 dark:text-gray-300">{option.text}</span>
                    </label>
                ))}
            </div>
        </div>
    );
}

// Subjective Question Component (formerly Short Answer)
export function SubjectiveQuestion({ question, answer, onAnswerChange }: QuestionProps) {
    const wordCount = answer ? answer.trim().split(/\s+/).filter(word => word.length > 0).length : 0;

    const isUnderMin = question.min_words && wordCount < question.min_words;
    const isOverMax = question.max_words && wordCount > question.max_words;

    return (
        <div className="space-y-4">
            <p className="text-lg font-medium text-gray-900 dark:text-white">{question.content}</p>
            <textarea
                value={answer}
                onChange={(e) => onAnswerChange(e.target.value)}
                placeholder="Type your answer here..."
                className="w-full h-48 p-4 rounded-lg border-2 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:bg-gray-800 dark:border-gray-700 dark:text-white resize-none transition-all"
            />
            <div className="flex items-center justify-between text-sm">
                <span className={`${isUnderMin ? 'text-orange-500' : isOverMax ? 'text-red-500' : 'text-gray-500 dark:text-gray-400'
                    }`}>
                    {wordCount} words
                    {question.min_words && ` (min: ${question.min_words})`}
                    {question.max_words && ` (max: ${question.max_words})`}
                </span>
                {isUnderMin && <span className="text-orange-500">⚠️ Below minimum word count</span>}
                {isOverMax && <span className="text-red-500">❌ Exceeds maximum word count</span>}
            </div>
        </div>
    );
}

// Coding Question Component with Monaco Editor
export function CodingQuestion({ question, answer, onAnswerChange }: QuestionProps) {
    const [output, setOutput] = useState<string>('');
    const [isRunning, setIsRunning] = useState(false);
    const [activeTab, setActiveTab] = useState<'code' | 'output'>('code');

    const runCode = useCallback(async () => {
        setIsRunning(true);
        setActiveTab('output');

        // Simulate code execution (in production, this would call the backend)
        try {
            // For now, just show a message
            await new Promise(resolve => setTimeout(resolve, 500));
            setOutput(`✓ Code received. Execution will be performed on submission.\n\nYour code:\n${'-'.repeat(40)}\n${answer.substring(0, 500)}${answer.length > 500 ? '...' : ''}`);
        } catch {
            setOutput('Error running code. Please try again.');
        } finally {
            setIsRunning(false);
        }
    }, [answer]);

    const resetCode = useCallback(() => {
        if (question.code_template) {
            onAnswerChange(question.code_template);
        }
    }, [question.code_template, onAnswerChange]);

    return (
        <div className="space-y-4">
            <p className="text-lg font-medium text-gray-900 dark:text-white">{question.content}</p>

            {/* Toolbar */}
            <div className="flex items-center justify-between">
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('code')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'code'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                            }`}
                    >
                        Code
                    </button>
                    <button
                        onClick={() => setActiveTab('output')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'output'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                            }`}
                    >
                        Output
                    </button>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={resetCode}
                        className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                    >
                        Reset
                    </button>
                    <button
                        onClick={runCode}
                        disabled={isRunning}
                        className="px-4 py-2 bg-green-500 text-white text-sm font-medium rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors flex items-center gap-2"
                    >
                        {isRunning ? (
                            <>
                                <span className="animate-spin">⏳</span>
                                Running...
                            </>
                        ) : (
                            <>
                                ▶ Run Code
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Code Editor or Output */}
            {activeTab === 'code' ? (
                <CodeEditor
                    value={answer || question.code_template || ''}
                    onChange={onAnswerChange}
                    language={question.language || 'python'}
                    height="400px"
                />
            ) : (
                <div className="h-[400px] rounded-lg bg-gray-900 p-4 overflow-auto">
                    <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap">
                        {output || 'Click "Run Code" to see output here...'}
                    </pre>
                </div>
            )}

            {/* Test Cases */}
            {question.test_cases && question.test_cases.length > 0 && (
                <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 p-4">
                    <h4 className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-3">
                        📋 Test Cases
                    </h4>
                    <div className="space-y-2">
                        {question.test_cases.slice(0, 3).map((tc, i) => (
                            <div
                                key={i}
                                className="flex items-start gap-4 text-sm bg-white dark:bg-gray-800 rounded-lg p-3"
                            >
                                <div className="flex-1">
                                    <span className="text-gray-500 dark:text-gray-400">Input: </span>
                                    <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-gray-700 dark:text-gray-300">
                                        {JSON.stringify(tc.input)}
                                    </code>
                                </div>
                                <div className="flex-1">
                                    <span className="text-gray-500 dark:text-gray-400">Expected: </span>
                                    <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-gray-700 dark:text-gray-300">
                                        {JSON.stringify(tc.expected)}
                                    </code>
                                </div>
                            </div>
                        ))}
                        {question.test_cases.length > 3 && (
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                                + {question.test_cases.length - 3} more test cases
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

// Question Renderer (switches based on type)
export function QuestionRenderer({ question, answer, onAnswerChange }: QuestionProps) {
    switch (question.type) {
        case 'mcq':
            return <MCQQuestion question={question} answer={answer} onAnswerChange={onAnswerChange} />;
        case 'subjective':
            return <SubjectiveQuestion question={question} answer={answer} onAnswerChange={onAnswerChange} />;
        case 'coding':
            return <CodingQuestion question={question} answer={answer} onAnswerChange={onAnswerChange} />;
        default:
            return <p className="text-red-500">Unknown question type</p>;
    }
}

