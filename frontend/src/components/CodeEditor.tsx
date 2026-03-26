/**
 * Monaco Code Editor Component
 * VS Code-like editor for coding questions
 */

'use client';

import { useRef, useCallback } from 'react';
import Editor, { OnMount, OnChange } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';

interface CodeEditorProps {
    value: string;
    onChange: (value: string) => void;
    language?: string;
    height?: string;
    readOnly?: boolean;
}

export function CodeEditor({
    value,
    onChange,
    language = 'python',
    height = '400px',
    readOnly = false,
}: CodeEditorProps) {
    const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

    const handleEditorMount: OnMount = useCallback((editor) => {
        editorRef.current = editor;
        editor.focus();
    }, []);

    const handleChange: OnChange = useCallback((newValue) => {
        onChange(newValue || '');
    }, [onChange]);

    return (
        <div className="rounded-lg overflow-hidden border-2 border-gray-700">
            {/* Editor Header */}
            <div className="bg-gray-800 px-4 py-2 flex items-center justify-between border-b border-gray-700">
                <div className="flex items-center gap-3">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                        <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                        <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    </div>
                    <span className="text-sm font-medium text-gray-400 uppercase">
                        {language}
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">
                        Changes saved automatically
                    </span>
                </div>
            </div>

            {/* Monaco Editor */}
            <Editor
                height={height}
                language={language}
                value={value}
                onChange={handleChange}
                onMount={handleEditorMount}
                theme="vs-dark"
                options={{
                    readOnly,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    fontSize: 14,
                    lineNumbers: 'on',
                    automaticLayout: false,
                    tabSize: 4,
                    insertSpaces: true,
                    wordWrap: 'on',
                    folding: true,
                    bracketPairColorization: { enabled: true },
                    padding: { top: 16 },
                }}
                loading={
                    <div className="flex items-center justify-center h-full bg-gray-900">
                        <div className="text-gray-400">Loading editor...</div>
                    </div>
                }
            />
        </div>
    );
}

