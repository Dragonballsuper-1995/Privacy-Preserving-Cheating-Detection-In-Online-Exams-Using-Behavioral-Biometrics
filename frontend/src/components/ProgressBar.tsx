/**
 * ProgressBar — Visual progress indicator with clickable question bubbles.
 */

'use client';

interface ProgressBarProps {
    total: number;
    current: number;
    /** Question IDs in order */
    questionIds: string[];
    /** Map of questionId → answer value */
    answers: Record<string, string>;
    /** Default answer values (e.g. code template) per question to distinguish unanswered */
    defaults?: Record<string, string>;
    onNavigate: (index: number) => void;
}

export function ProgressBar({ total, current, questionIds, answers, defaults = {}, onNavigate }: ProgressBarProps) {
    const answered = questionIds.filter(
        (id) => answers[id] && answers[id] !== (defaults[id] || '')
    ).length;

    const pct = total > 0 ? Math.round((answered / total) * 100) : 0;

    return (
        <div className="space-y-3">
            {/* Overall progress bar */}
            <div className="flex items-center gap-3">
                <div className="flex-1 h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                        className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500"
                        style={{ width: `${pct}%` }}
                    />
                </div>
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                    {answered}/{total} answered
                </span>
            </div>

            {/* Question bubbles */}
            <div className="flex flex-wrap gap-2">
                {questionIds.map((id, idx) => {
                    const isAnswered = answers[id] && answers[id] !== (defaults[id] || '');
                    const isCurrent = idx === current;

                    let cls = 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600';
                    if (isCurrent) {
                        cls = 'bg-blue-500 text-white ring-2 ring-blue-300 dark:ring-blue-700 scale-110';
                    } else if (isAnswered) {
                        cls = 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
                    }

                    return (
                        <button
                            key={id}
                            onClick={() => onNavigate(idx)}
                            title={`Question ${idx + 1}${isAnswered ? ' ✓' : ''}`}
                            className={`w-9 h-9 rounded-lg text-sm font-medium transition-all duration-200 ${cls}`}
                        >
                            {idx + 1}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
