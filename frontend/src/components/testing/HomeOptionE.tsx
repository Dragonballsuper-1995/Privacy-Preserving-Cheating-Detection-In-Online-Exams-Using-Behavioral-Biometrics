'use client';
import React from 'react';

const HomeOptionE = () => {
    return (
        <div className="bg-gray-950 text-white font-sans min-h-screen flex overflow-hidden relative">

            {/* Abstract glowing background */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[70%] bg-emerald-900/30 blur-[150px] rounded-full mix-blend-screen"></div>
                <div className="absolute bottom-[20%] right-[5%] w-[30%] h-[50%] bg-blue-900/20 blur-[120px] rounded-full mix-blend-screen"></div>
            </div>

            {/* Left Hero Column */}
            <div className="relative w-1/2 flex flex-col justify-center px-16 lg:px-24 z-10 border-r border-white/5 bg-gray-950/50 backdrop-blur-sm">
                <div className="absolute top-8 left-16">
                    <div className="font-bold text-xl tracking-tight flex items-center gap-2 text-white">
                        <div className="w-2 h-6 bg-emerald-500 rounded-sm"></div>
                        CheatingDetector
                    </div>
                </div>

                <div className="inline-flex px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 w-max mb-6 font-mono text-xs uppercase tracking-widest text-emerald-400 font-bold items-center gap-2">
                    <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full animate-ping"></span> Global Intelligence Node
                </div>

                <h1 className="text-6xl font-bold tracking-tight mb-8 leading-tight">
                    Privacy-First <br />
                    Neural <span className="text-emerald-400">Integrity.</span>
                </h1>
                <p className="text-xl text-gray-400 max-w-lg mb-12 leading-relaxed">
                    Advanced behavioral biometrics and multi-modal neural analysis to ensure assessment integrity without compromising student privacy.
                </p>

                <div className="flex items-center gap-8 text-sm font-bold uppercase tracking-wider text-gray-300 mb-12">
                    <div className="flex flex-col gap-1">
                        <span className="text-3xl text-emerald-400">400+</span>
                        <span className="text-[10px] text-gray-500">Global Nodes</span>
                    </div>
                    <div className="w-px h-12 bg-white/10"></div>
                    <div className="flex flex-col gap-1">
                        <span className="text-3xl text-emerald-400">&lt;50ms</span>
                        <span className="text-[10px] text-gray-500">Detection Latency</span>
                    </div>
                </div>

                <div className="flex gap-4">
                    <button className="px-8 py-4 bg-white hover:bg-gray-200 text-black font-bold uppercase tracking-widest text-sm rounded-xl transition-all shadow-[0_0_20px_rgba(255,255,255,0.1)]">Access Portal</button>
                    <button className="px-8 py-4 bg-gray-900 border border-gray-800 hover:bg-gray-800 text-white font-bold uppercase tracking-widest text-sm rounded-xl transition-all">Documentation</button>
                </div>
            </div>

            {/* Right Structured Matrix Column */}
            <div className="w-1/2 relative z-20 flex flex-col justify-center px-12 lg:px-20">
                <div className="bg-gray-900/60 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl relative">
                    <div className="absolute -top-px -left-px w-32 h-px bg-gradient-to-r from-emerald-500 to-transparent"></div>
                    <div className="absolute -left-px -top-px w-px h-32 bg-gradient-to-b from-emerald-500 to-transparent"></div>

                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-2xl font-bold tracking-tight">Active Matrix</h2>
                        <div className="flex items-center gap-4">
                            <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded font-mono text-[10px] uppercase font-bold tracking-widest hover:opacity-100 cursor-default">
                                3 Online
                            </span>
                            <button className="text-xs font-bold text-gray-500 hover:text-white transition-colors uppercase tracking-widest">Login &rarr;</button>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {/* Row 1 */}
                        <div className="bg-black/40 p-5 rounded-2xl border border-white/5 hover:border-emerald-500/30 hover:bg-gray-900 transition-colors cursor-pointer group flex items-center gap-6">
                            <div className="w-14 h-14 bg-gray-900 rounded-xl flex items-center justify-center border border-gray-800">
                                <div className="w-4 h-4 bg-gray-500 rounded-sm group-hover:bg-emerald-400 transition-colors"></div>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold mb-1 group-hover:text-emerald-400 transition-colors">Information Security</h3>
                                <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Prof. Rivest • 60 Minutes</p>
                            </div>
                        </div>

                        {/* Row 2 */}
                        <div className="bg-black/40 p-5 rounded-2xl border border-white/5 hover:border-emerald-500/30 hover:bg-gray-900 transition-colors cursor-pointer group flex items-center gap-6">
                            <div className="w-14 h-14 bg-gray-900 rounded-xl flex items-center justify-center border border-gray-800">
                                <div className="w-4 h-4 bg-gray-500 rounded-sm group-hover:bg-emerald-400 transition-colors"></div>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold mb-1 group-hover:text-emerald-400 transition-colors">CS101 Midterm</h3>
                                <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Prof. Turing • 90 Minutes</p>
                            </div>
                        </div>

                        {/* Row 3 */}
                        <div className="bg-black/40 p-5 rounded-2xl border border-white/5 hover:border-emerald-500/30 hover:bg-gray-900 transition-colors cursor-pointer group flex items-center gap-6">
                            <div className="w-14 h-14 bg-emerald-500/10 rounded-xl flex items-center justify-center border border-emerald-500/30">
                                <div className="w-4 h-4 bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] rounded-sm animate-pulse"></div>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold mb-1 group-hover:text-emerald-400 transition-colors">Advanced Algorithms</h3>
                                <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Prof. Hopper • 120 Minutes</p>
                            </div>
                        </div>
                    </div>

                    {/* Login footer */}
                    <div className="mt-8 pt-8 border-t border-white/5 flex gap-4">
                        <input type="text" placeholder="Access Token" className="flex-1 bg-black/50 border border-gray-800 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50" />
                        <button className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-black rounded-lg text-sm font-bold uppercase tracking-widest transition-colors shadow-lg shadow-emerald-500/20">Verify</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HomeOptionE;
