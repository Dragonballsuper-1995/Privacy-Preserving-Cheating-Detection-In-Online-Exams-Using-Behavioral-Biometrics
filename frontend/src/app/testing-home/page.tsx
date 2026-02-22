'use client';

import React, { useState } from 'react';
import HomeOptionB from '../../components/testing/HomeOptionB';
import HomeOptionC from '../../components/testing/HomeOptionC';
import HomeOptionE from '../../components/testing/HomeOptionE';

export default function TestingHomePage() {
    const [activeLayout, setActiveLayout] = useState<'B' | 'C' | 'E'>('E');

    return (
        <>
            {/* Floating Toolbar to Switch Layouts */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] bg-gray-900/90 backdrop-blur border border-gray-700 p-2 rounded-full shadow-2xl flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-widest text-gray-400 px-3">Test Layout:</span>
                <button
                    onClick={() => setActiveLayout('B')}
                    className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-colors ${activeLayout === 'B' ? 'bg-emerald-500 text-black' : 'text-white hover:bg-gray-800'}`}>
                    Option B
                </button>
                <button
                    onClick={() => setActiveLayout('C')}
                    className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-colors ${activeLayout === 'C' ? 'bg-emerald-500 text-black' : 'text-white hover:bg-gray-800'}`}>
                    Option C
                </button>
                <button
                    onClick={() => setActiveLayout('E')}
                    className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-colors ${activeLayout === 'E' ? 'bg-emerald-500 text-black' : 'text-white hover:bg-gray-800'}`}>
                    Option E
                </button>
            </div>

            {/* Render Active Layout */}
            {activeLayout === 'B' && <HomeOptionB />}
            {activeLayout === 'C' && <HomeOptionC />}
            {activeLayout === 'E' && <HomeOptionE />}
        </>
    );
}
