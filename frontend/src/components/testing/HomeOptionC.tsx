'use client';
import React from 'react';

const HomeOptionC = () => {
    return (
        <div className="bg-[#050505] text-white font-sans min-h-screen">
            {/* Navbar */}
            <nav className="absolute top-0 w-full p-6 flex justify-between items-center z-50">
                <div className="font-bold text-xl tracking-tight flex items-center gap-2">
                    <div className="w-6 h-6 bg-emerald-500 rounded-sm"></div>
                    CheatingDetector
                </div>
                <div className="space-x-4 flex items-center">
                    <button className="text-sm font-bold uppercase tracking-widest text-[#888] hover:text-white transition-colors">Docs</button>
                    <div className="w-px h-4 bg-[#333]"></div>
                    <button className="text-sm font-bold uppercase tracking-widest text-emerald-400 hover:text-emerald-300 transition-colors">Sign In</button>
                    <button className="px-5 py-2 bg-white text-black text-xs font-bold uppercase tracking-widest rounded hover:bg-gray-200 transition-colors">Access Portal</button>
                </div>
            </nav>

            {/* Hero Section */}
            <div className="relative pt-40 pb-20 flex flex-col items-center justify-center text-center px-6">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[500px] bg-emerald-500/10 blur-[150px] rounded-full pointer-events-none"></div>

                <div className="relative z-10 max-w-4xl mx-auto">
                    <h1 className="text-6xl md:text-7xl font-bold tracking-tight mb-8">
                        Privacy-Preserving <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">AI Integrity Node</span>
                    </h1>
                    <p className="text-xl text-[#888] max-w-2xl mx-auto leading-relaxed mb-12">
                        Advanced behavioral biometrics and multi-modal neural analysis. Ensuring assessment integrity without compromising student privacy.
                    </p>
                </div>
            </div>

            {/* Floating Active Roster */}
            <div className="relative z-20 max-w-5xl mx-auto px-6 -mt-8 pb-32">
                <div className="bg-[#111]/80 backdrop-blur-xl border border-[#222] rounded-3xl p-8 shadow-2xl">
                    <div className="flex items-center justify-between mb-8 pb-6 border-b border-[#222]">
                        <h2 className="text-xl font-bold tracking-tight">Active Assessment Matrix</h2>
                        <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded font-mono text-xs uppercase font-bold tracking-widest flex items-center">
                            <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full animate-pulse mr-2"></span> 3 Online Nodes
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Exam Card 1 */}
                        <div className="bg-[#1a1a1a] p-6 rounded-2xl border border-[#333] hover:border-emerald-500/50 hover:bg-[#222] transition-colors cursor-pointer group">
                            <h3 className="text-lg font-bold mb-1 group-hover:text-emerald-400 transition-colors">CS101 Midterm</h3>
                            <p className="text-[#666] text-xs font-bold uppercase tracking-wider mb-8">Prof. Alan Turing</p>
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[10px] text-[#555] font-bold uppercase tracking-widest mb-1">Duration</p>
                                    <p className="font-mono text-sm">60 Min</p>
                                </div>
                                <button className="w-10 h-10 rounded-full bg-[#111] border border-[#333] flex items-center justify-center group-hover:bg-emerald-500 group-hover:border-emerald-500 text-white group-hover:text-black transition-all">
                                    &rarr;
                                </button>
                            </div>
                        </div>
                        {/* Exam Card 2 */}
                        <div className="bg-[#1a1a1a] p-6 rounded-2xl border border-[#333] hover:border-emerald-500/50 hover:bg-[#222] transition-colors cursor-pointer group">
                            <h3 className="text-lg font-bold mb-1 group-hover:text-emerald-400 transition-colors">Advanced Algorithms</h3>
                            <p className="text-[#666] text-xs font-bold uppercase tracking-wider mb-8">Prof. Grace Hopper</p>
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[10px] text-[#555] font-bold uppercase tracking-widest mb-1">Duration</p>
                                    <p className="font-mono text-sm">120 Min</p>
                                </div>
                                <button className="w-10 h-10 rounded-full bg-[#111] border border-[#333] flex items-center justify-center group-hover:bg-emerald-500 group-hover:border-emerald-500 text-white group-hover:text-black transition-all">
                                    &rarr;
                                </button>
                            </div>
                        </div>
                        {/* Exam Card 3 */}
                        <div className="bg-[#1a1a1a] p-6 rounded-2xl border border-[#333] hover:border-emerald-500/50 hover:bg-[#222] transition-colors cursor-pointer group">
                            <h3 className="text-lg font-bold mb-1 group-hover:text-emerald-400 transition-colors">System Architecture</h3>
                            <p className="text-[#666] text-xs font-bold uppercase tracking-wider mb-8">Prof. Ada Lovelace</p>
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[10px] text-[#555] font-bold uppercase tracking-widest mb-1">Duration</p>
                                    <p className="font-mono text-sm">90 Min</p>
                                </div>
                                <button className="w-10 h-10 rounded-full bg-[#111] border border-[#333] flex items-center justify-center group-hover:bg-emerald-500 group-hover:border-emerald-500 text-white group-hover:text-black transition-all">
                                    &rarr;
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HomeOptionC;
