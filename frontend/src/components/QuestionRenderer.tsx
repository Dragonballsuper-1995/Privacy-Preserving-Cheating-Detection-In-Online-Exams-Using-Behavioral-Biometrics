/**
 * Question Renderers
 * Components for rendering different types of exam questions
 */

'use client';

import { Question } from '@/lib/api';
import { useState, useCallback, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import CodeEditor to avoid SSR issues with Monaco
const CodeEditor = dynamic(
    () => import('@/components/CodeEditor').then((mod) => mod.CodeEditor),
    {
        ssr: false,
        loading: () => (
            <div className="h-[400px] bg-muted rounded-lg flex items-center justify-center">
                <div className="text-muted-foreground text-sm font-medium">Loading code editor...</div>
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
            <p className="text-lg font-semibold text-foreground">{question.content}</p>
            <div className="space-y-3">
                {question.options?.map((option) => (
                    <label
                        key={option.id}
                        className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${answer === option.id
                            ? 'border-primary bg-primary/10 text-foreground'
                            : 'border-border hover:border-primary/40 bg-card text-foreground'
                            }`}
                    >
                        <input
                            type="radio"
                            name={question.id}
                            value={option.id}
                            checked={answer === option.id}
                            onChange={(e) => onAnswerChange(e.target.value)}
                            className="w-4 h-4 accent-primary"
                        />
                        <span className="ml-3 text-foreground font-medium">{option.text}</span>
                    </label>
                ))}
            </div>
        </div>
    );
}

// Subjective Question Component
export function SubjectiveQuestion({ question, answer, onAnswerChange }: QuestionProps) {
    const wordCount = answer ? answer.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
    const isOverMax = question.max_words && wordCount > question.max_words;

    return (
        <div className="space-y-4">
            <p className="text-lg font-semibold text-foreground">{question.content}</p>
            <textarea
                value={answer}
                onChange={(e) => onAnswerChange(e.target.value)}
                placeholder="Type your answer here..."
                className="w-full h-48 p-4 rounded-lg border-2 border-border focus:border-primary focus:ring-2 focus:ring-primary/20 bg-card text-foreground placeholder:text-muted-foreground resize-none transition-all outline-none"
            />
            <div className="flex items-center justify-between text-sm">
                <span className={`font-medium ${isOverMax ? 'text-destructive' : 'text-muted-foreground'}`}>
                    {wordCount} words
                    {question.max_words && ` (max: ${question.max_words})`}
                </span>
                {isOverMax && <span className="text-destructive font-semibold">❌ Exceeds maximum word count</span>}
            </div>
        </div>
    );
}

// Coding Question Component with Monaco Editor
export function CodingQuestion({ question, answer, onAnswerChange }: QuestionProps) {
    const [output, setOutput] = useState<string>('');
    const [isRunning, setIsRunning] = useState(false);
    const [activeTab, setActiveTab] = useState<'code' | 'output'>('code');

    useEffect(() => {
        setOutput('');
        setActiveTab('code');
    }, [question.id]);

    const runCode = useCallback(async () => {
        setIsRunning(true);
        setActiveTab('output');
        setOutput('⏳ Running tests...');

        try {
            const testCases = question.test_cases || [];

            if (testCases.length === 0) {
                const { executeCode } = await import('@/lib/api');
                const result = await executeCode(answer, question.language || 'python', 5);

                if (result.success) {
                    let out = '';
                    if (result.stdout) out += `📤 Output:\n${result.stdout}`;
                    if (!out) out = '✅ Code executed successfully (no output)';
                    out += `\n\n⏱️ Execution time: ${result.execution_time}s`;
                    setOutput(out);
                } else {
                    let errorOutput = '❌ Execution failed\n\n';
                    if (result.error) errorOutput += `Error: ${result.error}\n`;
                    if (result.stderr) errorOutput += `\n${result.stderr}`;
                    setOutput(errorOutput);
                }
            } else {
                const { runTests } = await import('@/lib/api');
                const funcMatch = (question.code_template || answer).match(/def\s+(\w+)\s*\(/);
                const functionName = funcMatch ? funcMatch[1] : 'solution';

                const result = await runTests(
                    answer,
                    functionName,
                    testCases.map(tc => ({ input: tc.input, expected: tc.expected })),
                    question.language || 'python',
                    5
                );

                const outputLines: string[] = [];
                if (result.error) outputLines.push(`❌ Error: ${result.error}\n`);
                outputLines.push(`📊 Test Results: ${result.passed}/${result.total} passed\n`);
                outputLines.push('─'.repeat(50) + '\n');

                result.results.forEach((tr, idx) => {
                    const icon = tr.passed ? '✅' : '❌';
                    outputLines.push(`${icon} Test ${idx + 1}:`);
                    outputLines.push(`   Input:    ${JSON.stringify(tr.input)}`);
                    outputLines.push(`   Expected: ${JSON.stringify(tr.expected)}`);
                    outputLines.push(`   Actual:   ${JSON.stringify(tr.actual)}`);
                    if (tr.error) outputLines.push(`   Error:    ${tr.error}`);
                    outputLines.push('');
                });

                outputLines.push(`⏱️ Execution time: ${result.execution_time}s`);
                setOutput(outputLines.join('\n'));
            }
        } catch (error) {
            setOutput(`❌ Error running code: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsRunning(false);
        }
    }, [answer, question.language, question.test_cases, question.code_template]);

    const resetCode = useCallback(() => {
        if (question.code_template) onAnswerChange(question.code_template);
    }, [question.code_template, onAnswerChange]);

    return (
        <div className="space-y-4">
            <p className="text-lg font-semibold text-foreground">{question.content}</p>

            {/* Toolbar */}
            <div className="flex items-center justify-between">
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('code')}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${activeTab === 'code'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                            }`}
                    >
                        Code
                    </button>
                    <button
                        onClick={() => setActiveTab('output')}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${activeTab === 'output'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                            }`}
                    >
                        Output
                    </button>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={resetCode}
                        className="px-3 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors font-medium"
                    >
                        Reset
                    </button>
                    <button
                        onClick={runCode}
                        disabled={isRunning}
                        className="px-4 py-2 bg-accent text-accent-foreground text-sm font-semibold rounded-lg hover:bg-accent/80 disabled:opacity-50 transition-colors flex items-center gap-2"
                    >
                        {isRunning ? (
                            <>
                                <span className="animate-spin">⏳</span>
                                Running...
                            </>
                        ) : (
                            <>▶ Run Code</>
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
                <div className="h-[400px] rounded-lg bg-muted p-4 overflow-auto border border-border">
                    <pre className="text-sm text-foreground font-mono whitespace-pre-wrap">
                        {output || 'Click "Run Code" to see output here...'}
                    </pre>
                </div>
            )}

            {/* Test Cases */}
            {question.test_cases && question.test_cases.length > 0 && (
                <div className="rounded-lg bg-primary/5 border border-primary/20 p-4">
                    <h4 className="text-sm font-semibold text-primary mb-3">
                        📋 Test Cases
                    </h4>
                    <div className="space-y-2">
                        {question.test_cases.slice(0, 3).map((tc, i) => (
                            <div
                                key={i}
                                className="flex items-start gap-4 text-sm bg-card border border-border rounded-lg p-3"
                            >
                                <div className="flex-1">
                                    <span className="text-muted-foreground font-medium">Input: </span>
                                    <code className="bg-muted px-2 py-0.5 rounded text-foreground font-mono text-xs">
                                        {JSON.stringify(tc.input)}
                                    </code>
                                </div>
                                <div className="flex-1">
                                    <span className="text-muted-foreground font-medium">Expected: </span>
                                    <code className="bg-muted px-2 py-0.5 rounded text-foreground font-mono text-xs">
                                        {JSON.stringify(tc.expected)}
                                    </code>
                                </div>
                            </div>
                        ))}
                        {question.test_cases.length > 3 && (
                            <p className="text-sm text-muted-foreground font-medium">
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
            return <p className="text-destructive font-medium">Unknown question type</p>;
    }
}
