/**
 * ExamTimer — Countdown timer with green → yellow → red color transitions.
 * Pulses when under 60 seconds.
 */

'use client';

import { useMemo } from 'react';

interface ExamTimerProps {
    /** Remaining seconds */
    remaining: number;
    /** Total exam time in seconds (for progress ring) */
    total: number;
}

export function ExamTimer({ remaining, total }: ExamTimerProps) {
    const mins = Math.floor(remaining / 60);
    const secs = remaining % 60;
    const display = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

    const pct = total > 0 ? remaining / total : 0;

    // Color tiers: green (>50%), yellow (20–50%), red (<20%)
    const tier = useMemo(() => {
        if (pct > 0.5) return 'green';
        if (pct > 0.2) return 'yellow';
        return 'red';
    }, [pct]);

    const pulse = remaining <= 60 && remaining > 0;

    // SVG ring
    const radius = 22;
    const circumference = 2 * Math.PI * radius;
    const dashOffset = circumference * (1 - pct);

    const colors: Record<string, { ring: string; bg: string; text: string }> = {
        green: { ring: '#22c55e', bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400' },
        yellow: { ring: '#eab308', bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-400' },
        red: { ring: '#ef4444', bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-600 dark:text-red-400' },
    };

    const c = colors[tier];

    return (
        <div
            className={`flex items-center gap-2.5 px-3 py-1.5 rounded-xl ${c.bg} ${pulse ? 'animate-timer-pulse' : ''}`}
        >
            {/* Progress ring */}
            <svg width="48" height="48" viewBox="0 0 48 48" className="shrink-0">
                {/* bg track */}
                <circle
                    cx="24" cy="24" r={radius}
                    fill="none" stroke="currentColor" strokeWidth="4"
                    className="text-gray-200 dark:text-gray-700"
                />
                {/* progress arc */}
                <circle
                    cx="24" cy="24" r={radius}
                    fill="none" stroke={c.ring} strokeWidth="4"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={dashOffset}
                    transform="rotate(-90 24 24)"
                    className="transition-all duration-700"
                />
                {/* center icon */}
                <text x="24" y="26" textAnchor="middle" fontSize="14" className="select-none" fill={c.ring}>
                    ⏱
                </text>
            </svg>

            <span className={`font-mono text-xl font-bold tracking-wide ${c.text}`}>
                {display}
            </span>
        </div>
    );
}
