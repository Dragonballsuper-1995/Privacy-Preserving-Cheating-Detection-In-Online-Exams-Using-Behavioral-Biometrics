/**
 * Category Tabs Component
 * Displays tabs for navigating between MCQ, Coding, and Subjective sections
 */

'use client';

import { Question } from '@/lib/api';

export type CategoryType = 'mcq' | 'coding' | 'subjective';

interface CategoryTabsProps {
    categories: {
        mcq: Question[];
        coding: Question[];
        subjective: Question[];
    };
    activeCategory: CategoryType;
    onCategoryChange: (category: CategoryType) => void;
    answeredCounts?: {
        mcq: number;
        coding: number;
        subjective: number;
    };
}

export function CategoryTabs({ categories, activeCategory, onCategoryChange, answeredCounts }: CategoryTabsProps) {
    const tabs = [
        { id: 'mcq' as CategoryType, name: 'Multiple Choice', icon: '📝', count: categories.mcq.length },
        { id: 'coding' as CategoryType, name: 'Coding', icon: '💻', count: categories.coding.length },
        { id: 'subjective' as CategoryType, name: 'Subjective', icon: '✍️', count: categories.subjective.length }
    ];

    return (
        <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex space-x-4" aria-label="Category tabs">
                {tabs.map((tab) => {
                    const isActive = activeCategory === tab.id;
                    const answeredCount = answeredCounts?.[tab.id] || 0;
                    const hasQuestions = tab.count > 0;

                    if (!hasQuestions) return null;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => onCategoryChange(tab.id)}
                            disabled={!hasQuestions}
                            className={`
                                group inline-flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm
                                transition-colors duration-200
                                ${isActive
                                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                    : hasQuestions
                                        ? 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                                        : 'border-transparent text-gray-300 dark:text-gray-600 cursor-not-allowed'
                                }
                            `}
                        >
                            <span className="text-lg">{tab.icon}</span>
                            <span>{tab.name}</span>
                            <span className={`
                                ml-2 py-0.5 px-2 rounded-full text-xs font-medium
                                ${isActive
                                    ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                                    : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                                }
                            `}>
                                {answeredCount}/{tab.count}
                            </span>
                        </button>
                    );
                })}
            </nav>
        </div>
    );
}
