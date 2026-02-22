'use client';
import React from 'react';

const HomeOptionB = () => {
    return (
        <div className="bg-gray-950 text-white font-sans min-h-screen flex overflow-hidden">
            {/* Left Hero Column */}
            <div className="relative w-1/2 flex flex-col justify-center px-16 lg:px-24">
                {/* Background elements */}
                <div className="absolute -top-32 -left-32 w-[600px] h-[600px] bg-emerald-500/20 blur-[100px] rounded-full pointer-events-none"></div>
                <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-gray-950 to-transparent pointer-events-none"></div>

                <div className="relative z-10">
                    <div className="font-bold text-lg tracking-tight flex items-center gap-2 mb-24 opacity-80">
                        <div className="w-5 h-5 bg-emerald-500 rounded-sm"></div>
                        CheatingDetector
                    </div>

                    <h1 className="text-6xl font-bold tracking-tight mb-8 leading-tight">
                        Privacy-Preserving <br />
                        <span className="text-emerald-400">AI Integrity Node</span>
                    </h1>
                    <p className="text-xl text-gray-400 max-w-lg mb-12 leading-relaxed">
                        Advanced behavioral biometrics and multi-modal neural analysis to ensure assessment integrity without
                        compromising student privacy.
                    </p>

                    <div className="flex flex-col gap-6 font-semibold uppercase tracking-wider text-sm">
                        <div className="flex items-center gap-4 text-gray-300">
                            <div className="w-10 h-10 rounded-full bg-gray-900 border border-gray-800 flex justify-center items-center text-emerald-500">&#10003;</div>
                            Biometric Validation
                        </div>
                        <div className="flex items-center gap-4 text-gray-300">
                            <div className="w-10 h-10 rounded-full bg-gray-900 border border-gray-800 flex justify-center items-center text-emerald-500">&#10003;</div>
                            Real-time Threat Modeling
                        </div>
                        <div className="flex items-center gap-4 text-gray-300">
                            <div className="w-10 h-10 rounded-full bg-gray-900 border border-gray-800 flex justify-center items-center text-emerald-500">&#10003;</div>
                            Zero-Knowledge Architecture
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Actions Column (Exams & Login Split) */}
            <div className="w-1/2 bg-gray-900/50 border-l border-gray-800 relative z-20 flex flex-col h-[100vh] overflow-y-auto">
                {/* Auth Header */}
                <div className="flex justify-end p-8 space-x-4">
                    <button className="px-5 py-2.5 hover:bg-gray-800 rounded-lg text-sm font-bold uppercase tracking-widest transition-colors shadow-sm">Sign In</button>
                    <button className="px-5 py-2.5 bg-white text-gray-950 rounded-lg text-sm font-bold uppercase tracking-widest hover:bg-gray-200 transition-colors shadow-sm">Access Portal</button>
                </div>

                {/* Active Roster */}
                <div className="flex-1 px-12 pb-12">
                    <h2 className="text-2xl font-bold tracking-tight mb-8 flex items-center justify-between">
                        Live Assessment Matrix
                        <span className="text-xs font-bold uppercase tracking-widest text-gray-500 px-3 py-1 bg-gray-900 rounded-lg border border-gray-800">3 Online</span>
                    </h2>

                    <div className="space-y-4">
                        {/* Exam Row */}
                        <div className="bg-gray-950 p-6 rounded-2xl border border-gray-800 hover:border-emerald-500/50 transition-colors cursor-pointer group flex items-center gap-6">
                            <div className="w-16 h-16 bg-gray-900 rounded-xl flex items-center justify-center border border-gray-800 shrink-0">
                                <div className="w-5 h-5 bg-gray-400 rounded-sm group-hover:bg-emerald-400 transition-colors"></div>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold mb-1 group-hover:text-emerald-400 transition-colors">CS101 Midterm Examination</h3>
                                <div className="flex items-center gap-4 text-xs font-bold uppercase tracking-wider text-gray-500">
                                    <span>Prof. Alan Turing</span>
                                    <span className="w-1 h-1 bg-gray-800 rounded-full"></span>
                                    <span>60 Minutes</span>
                                </div>
                            </div>
                            <button className="px-4 py-2 bg-gray-900 border border-gray-800 text-white rounded-lg text-xs font-bold uppercase tracking-widest group-hover:bg-emerald-500 group-hover:text-gray-950 group-hover:border-emerald-500 transition-all">Begin</button>
                        </div>

                        {/* Row 2 */}
                        <div className="bg-gray-950 p-6 rounded-2xl border border-gray-800 hover:border-emerald-500/50 transition-colors cursor-pointer group flex items-center gap-6">
                            <div className="w-16 h-16 bg-gray-900 rounded-xl flex items-center justify-center border border-gray-800 shrink-0">
                                <div className="w-5 h-5 bg-gray-400 rounded-sm group-hover:bg-emerald-400 transition-colors"></div>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold mb-1 group-hover:text-emerald-400 transition-colors">Advanced Algorithms</h3>
                                <div className="flex items-center gap-4 text-xs font-bold uppercase tracking-wider text-gray-500">
                                    <span>Prof. Grace Hopper</span>
                                    <span className="w-1 h-1 bg-gray-800 rounded-full"></span>
                                    <span>120 Minutes</span>
                                </div>
                            </div>
                            <button className="px-4 py-2 bg-gray-900 border border-gray-800 text-white rounded-lg text-xs font-bold uppercase tracking-widest group-hover:bg-emerald-500 group-hover:text-gray-950 group-hover:border-emerald-500 transition-all">Begin</button>
                        </div>
                    </div>

                    {/* Quick Auth */}
                    <div className="mt-12 p-8 border border-gray-800 border-dashed rounded-2xl text-center bg-gray-900/30">
                        <p className="text-sm text-gray-500 mb-4 font-bold uppercase tracking-widest">Administrator Access</p>
                        <div className="flex border border-gray-800 rounded-lg overflow-hidden bg-gray-950 max-w-sm mx-auto">
                            <input type="text" placeholder="Passkey" className="bg-transparent border-none px-4 py-2 text-sm text-white w-full outline-none" />
                            <button className="bg-emerald-500 hover:bg-emerald-400 px-6 py-2 text-gray-950 text-xs font-bold uppercase tracking-widest transition-colors">Auth</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HomeOptionB;
