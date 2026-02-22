'use client';

import React, { useState } from 'react';
import AdminOptionCv2 from '../../components/testing/AdminOptionCv2';
import AdminOptionCv3 from '../../components/testing/AdminOptionCv3';

export default function TestingAdminPage() {
    const [activeLayout, setActiveLayout] = useState<'Cv2' | 'Cv3'>('Cv3');

    return (
        <>
            {/* Floating Toolbar to Switch Layouts */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] bg-gray-900/90 backdrop-blur border border-gray-700 p-2 rounded-full shadow-2xl flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-widest text-gray-400 px-3">Test Layout:</span>
                <button
                    onClick={() => setActiveLayout('Cv2')}
                    className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-colors ${activeLayout === 'Cv2' ? 'bg-emerald-500 text-black' : 'text-white hover:bg-gray-800'}`}>
                    Option C_v2 (Compact Drawer)
                </button>
                <button
                    onClick={() => setActiveLayout('Cv3')}
                    className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-colors ${activeLayout === 'Cv3' ? 'bg-emerald-500 text-black' : 'text-white hover:bg-gray-800'}`}>
                    Option C_v3 (Expanded Stats)
                </button>
            </div>

            {/* Render Active Layout */}
            {activeLayout === 'Cv2' && <AdminOptionCv2 />}
            {activeLayout === 'Cv3' && <AdminOptionCv3 />}
        </>
    );
}
