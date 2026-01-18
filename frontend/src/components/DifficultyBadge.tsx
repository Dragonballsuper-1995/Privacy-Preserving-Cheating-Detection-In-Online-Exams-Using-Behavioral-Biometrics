/**
 * Difficulty Badge Component
 * Displays difficulty levels with color-coded badges
 */

'use client';

interface DifficultyBadgeProps {
    difficulty?: 'easy' | 'medium' | 'hard';
    showPoints?: boolean;
    points?: number;
}

export function DifficultyBadge({ difficulty, showPoints = false, points }: DifficultyBadgeProps) {
    if (!difficulty) return null;

    const colors = {
        easy: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
        medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
        hard: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
    };

    const icons = {
        easy: '🟢',
        medium: '🟡',
        hard: '🔴'
    };

    return (
        <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[difficulty]}`}>
                <span>{icons[difficulty]}</span>
                {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
            </span>
            {showPoints && points && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                    {points} pts
                </span>
            )}
        </div>
    );
}
