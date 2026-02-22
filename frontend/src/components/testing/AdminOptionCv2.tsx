'use client';
import React from 'react';

const AdminOptionCv2 = () => {
    return (
        <div className="bg-[#050505] text-gray-200 font-sans h-screen flex flex-col overflow-hidden relative">
            {/* Navbar */}
            <header className="h-16 bg-[#111] border-b border-[#222] flex items-center justify-between px-8 shrink-0 relative z-50 shadow-md">
                <div className="flex items-center gap-6">
                    <span className="font-bold text-lg tracking-tight text-white flex items-center gap-2">
                        <div className="w-4 h-4 bg-emerald-500 rounded-sm"></div>
                        Admin Terminal
                    </span>
                    <div className="h-6 w-px bg-gray-800"></div>
                    <nav className="flex space-x-6">
                        <span className="text-sm font-bold text-emerald-400 border-b-2 border-emerald-500 py-5">Global Roster</span>
                        <span className="text-sm font-medium text-gray-400 hover:text-white transition-colors py-5 cursor-pointer">ML Models</span>
                    </nav>
                </div>
                <div className="flex gap-4">
                    <p className="text-xs font-mono text-gray-500 flex flex-col items-end">
                        <span>Latency</span>
                        <span className="text-emerald-500">24ms <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full inline-block mb-0.5 animate-pulse"></span></span>
                    </p>
                </div>
            </header>

            {/* Main Content Array & Drawer */}
            <div className="flex-1 overflow-hidden relative flex">

                {/* Main Grid Area */}
                <main className="flex-1 overflow-auto p-8 transition-all duration-300 pr-[680px]">

                    {/* Refined Header & Condensed Stats inside a single bar */}
                    <div className="flex justify-between items-center mb-6 bg-[#111] border border-[#222] rounded-2xl p-4 shadow-sm">
                        <div className="flex items-center gap-8 pl-4">
                            <div>
                                <h1 className="text-xl font-bold text-white mb-0.5">Live Target Matrix</h1>
                                <p className="text-gray-500 text-xs font-mono">1,204 ACTIVE STREAMS</p>
                            </div>
                            <div className="flex items-center gap-6 ml-4 border-l border-[#333] pl-6">
                                <div>
                                    <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-1">Global Incident Rate</p>
                                    <p className="text-lg font-bold text-white leading-none">3.5%</p>
                                </div>
                                <div>
                                    <p className="text-[10px] text-red-500 font-bold uppercase tracking-widest mb-1">Security Flags</p>
                                    <p className="text-lg font-bold text-red-500 leading-none">42</p>
                                </div>
                            </div>
                        </div>
                        <div className="flex bg-[#0a0a0a] rounded-xl p-1 border border-[#333]">
                            <button className="px-4 py-2 rounded-lg bg-[#222] text-white text-xs font-bold uppercase tracking-wider shadow-sm">All</button>
                            <button className="px-4 py-2 rounded-lg text-gray-500 text-xs font-bold uppercase tracking-wider hover:bg-[#1a1a1a]">Flagged</button>
                        </div>
                    </div>

                    {/* Refined Compact Data Grid */}
                    <div className="bg-[#111] rounded-2xl border border-[#222] overflow-hidden shadow-sm">
                        <table className="w-full text-left border-collapse text-sm">
                            <thead>
                                <tr className="bg-[#0a0a0a] text-[10px] uppercase tracking-widest text-[#666] border-b border-[#222]">
                                    <th className="py-4 pl-6 pr-4 font-bold">Session Identity</th>
                                    <th className="p-4 font-bold">Risk Trajectory (10m)</th>
                                    <th className="p-4 font-bold">Current Quotient</th>
                                    <th className="p-4 font-bold">Status</th>
                                    <th className="py-4 pr-6 pl-4 font-bold text-right">Event Density</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[#222]">
                                {/* Selected Row */}
                                <tr className="hover:bg-[#1a1a1a] cursor-pointer transition-colors bg-[#1a1a1a] border-l-4 border-emerald-500 shadow-[inset_4px_0_0_#10b981]">
                                    <td className="py-5 pl-5 pr-4">
                                        <div className="font-mono text-white font-bold tracking-wide">acbfd3af-4ba9</div>
                                        <div className="text-[10px] text-[#666] mt-1">CS101 • 14:02 PM</div>
                                    </td>
                                    <td className="p-4 w-48">
                                        <div className="flex items-end gap-0.5 h-6 opacity-80">
                                            <div className="w-2 bg-emerald-500/30 rounded-t h-[20%]"></div>
                                            <div className="w-2 bg-emerald-500/40 rounded-t h-[40%]"></div>
                                            <div className="w-2 bg-yellow-500/60 rounded-t h-[60%]"></div>
                                            <div className="w-2 bg-red-500/80 rounded-t h-[90%]"></div>
                                            <div className="w-2 bg-red-500 rounded-t h-[100%]"></div>
                                            <div className="w-2 bg-red-500/80 rounded-t h-[85%]"></div>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <span className="text-lg font-bold text-red-500">86%</span>
                                    </td>
                                    <td className="p-4"><span className="text-[10px] bg-red-500/10 border border-red-500/20 px-2 py-1.5 rounded text-red-500 font-bold uppercase tracking-widest shadow-sm">Flagged</span></td>
                                    <td className="py-4 pr-6 pl-4 text-right font-mono text-[#888]">2,105</td>
                                </tr>
                                {/* Normal Row */}
                                <tr className="hover:bg-[#1a1a1a] cursor-pointer transition-colors border-l-4 border-transparent">
                                    <td className="py-5 pl-5 pr-4">
                                        <div className="font-mono text-gray-300 font-bold tracking-wide">b72f10d2-8ca1</div>
                                        <div className="text-[10px] text-[#666] mt-1">CS101 • 14:01 PM</div>
                                    </td>
                                    <td className="p-4 w-48">
                                        <div className="flex items-end gap-0.5 h-6 opacity-40 grayscale hover:grayscale-0 transition-all">
                                            <div className="w-2 bg-emerald-500 rounded-t h-[15%]"></div>
                                            <div className="w-2 bg-emerald-500 rounded-t h-[12%]"></div>
                                            <div className="w-2 bg-emerald-500 rounded-t h-[18%]"></div>
                                            <div className="w-2 bg-emerald-500 rounded-t h-[10%]"></div>
                                            <div className="w-2 bg-emerald-500 rounded-t h-[14%]"></div>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <span className="text-lg font-bold text-emerald-500 opacity-60">14%</span>
                                    </td>
                                    <td className="p-4"><span className="text-[10px] bg-[#222] border border-[#333] px-2 py-1.5 rounded text-gray-500 font-bold uppercase tracking-widest shadow-sm">Normal</span></td>
                                    <td className="py-4 pr-6 pl-4 text-right font-mono text-[#666]">923</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </main>

                {/* Slide-over Drawer (Simulated Open) */}
                <aside className="fixed right-0 top-0 bottom-0 mt-16 w-[650px] bg-[#111] border-l border-[#222] shadow-2xl flex flex-col z-40 transform translate-x-0 transition-transform duration-300">
                    <div className="p-8 border-b border-[#222] flex justify-between items-start bg-[#111] shrink-0">
                        <div>
                            <p className="text-xs text-red-500 font-bold uppercase tracking-wider mb-2 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(239,68,68,1)]"></span> Target Locked
                            </p>
                            <h3 className="font-mono text-3xl font-bold text-white mb-2 tracking-tight">acbfd3af-4ba9</h3>
                            <p className="text-xs font-bold text-[#666] uppercase tracking-widest">CS101 Midterm  •  2,105 Events  •  Active</p>
                        </div>
                        <button className="text-[#666] hover:text-white transition-colors bg-[#222] hover:bg-[#333] w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg shadow-sm border border-[#333]">&times;</button>
                    </div>

                    <div className="px-8 pt-6 pb-2 shrink-0 bg-[#0a0a0a]">
                        <div className="flex gap-2">
                            <button className="px-6 py-2.5 bg-[#222] text-white rounded-xl text-xs font-bold uppercase tracking-wider shadow-sm border border-[#333]">Overview</button>
                            <button className="px-6 py-2.5 text-[#666] hover:text-white hover:bg-[#1a1a1a] rounded-xl text-xs font-bold uppercase tracking-wider transition-colors">Timeline</button>
                            <button className="px-6 py-2.5 text-[#666] hover:text-white hover:bg-[#1a1a1a] rounded-xl text-xs font-bold uppercase tracking-wider transition-colors">Features</button>
                            <button className="px-6 py-2.5 text-blue-400 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 rounded-xl text-xs font-bold uppercase tracking-wider transition-colors flex items-center gap-2">Review</button>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-[#0a0a0a]">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-[#111] p-5 rounded-2xl border border-[#222]">
                                <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-1">Target Quotient</p>
                                <p className="text-3xl font-bold text-red-500">86%</p>
                            </div>
                            <div className="bg-[#111] p-5 rounded-2xl border border-[#222]">
                                <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-1">Primary Vector</p>
                                <p className="text-lg mt-1 font-bold text-red-500">Focus Loss (65%)</p>
                            </div>
                        </div>

                        <div>
                            <h4 className="text-[10px] font-bold uppercase tracking-widest text-[#555] mb-4 border-b border-[#222] pb-2">Subsystem Breakdown</h4>
                            <div className="space-y-4">
                                <div className="bg-[#111] p-5 rounded-xl border border-[#222] hover:border-[#333] transition-colors relative overflow-hidden">
                                    <div className="absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-red-500/10 to-transparent pointer-events-none"></div>
                                    <div className="flex justify-between items-center mb-4">
                                        <div>
                                            <h5 className="text-sm font-bold text-white mb-1">Tab Switching</h5>
                                            <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest">Focus Subsystem</p>
                                        </div>
                                        <span className="text-2xl font-bold text-red-500">65%</span>
                                    </div>
                                    <div className="h-1.5 bg-[#222] rounded-full overflow-hidden"><div className="w-[65%] h-full bg-red-500 rounded-r-full shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div></div>
                                </div>

                                <div className="bg-[#111] p-5 rounded-xl border border-[#222] hover:border-[#333] transition-colors">
                                    <div className="flex justify-between items-center mb-4">
                                        <div>
                                            <h5 className="text-sm font-bold text-white mb-1">Clipboard Insertion</h5>
                                            <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest">Macro Subsystem</p>
                                        </div>
                                        <span className="text-2xl font-bold text-red-500">92%</span>
                                    </div>
                                    <div className="h-1.5 bg-[#222] rounded-full overflow-hidden"><div className="w-[92%] h-full bg-red-500 rounded-r-full"></div></div>
                                </div>
                            </div>
                        </div>

                        <button className="w-full py-4 mt-4 rounded-xl border border-[#333] bg-[#111] text-white font-bold uppercase tracking-widest text-xs hover:bg-[#1a1a1a] transition-all shadow-sm">
                            Open Full Analysis Timeline &rarr;
                        </button>
                    </div>
                </aside>
            </div>

        </div>
    );
};

export default AdminOptionCv2;
