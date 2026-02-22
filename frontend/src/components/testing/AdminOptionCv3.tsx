'use client';
import React from 'react';

const AdminOptionCv3 = () => {
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
                    <p className="text-[10px] font-mono font-bold text-emerald-500 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded uppercase tracking-widest flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span> Network Active
                    </p>
                </div>
            </header>

            {/* Main Content Array & Drawer */}
            <div className="flex-1 overflow-hidden relative flex">

                <main className="flex-1 overflow-auto p-8 transition-all duration-300 pr-[680px]">

                    <div className="flex justify-between items-end mb-6">
                        <div>
                            <h1 className="text-2xl font-bold text-white tracking-tight mb-1">Live Target Matrix</h1>
                            <p className="text-gray-500 text-xs font-mono">1,204 STREAMS • 42 ANOMALIES</p>
                        </div>
                        <div className="flex bg-[#111] border border-[#222] rounded-xl p-1 shadow-sm h-10">
                            <button className="px-5 rounded-lg bg-[#222] text-white text-xs font-bold uppercase tracking-wider shadow-sm">All Scans</button>
                            <button className="px-5 rounded-lg text-gray-500 text-xs font-bold uppercase tracking-wider hover:bg-[#1a1a1a]">Flagged Only</button>
                        </div>
                    </div>

                    {/* Expanded Micro-Chart Stats Header */}
                    <div className="grid grid-cols-4 gap-4 mb-6">
                        {/* Stat Block 1 */}
                        <div className="bg-[#111] border border-[#222] rounded-2xl p-5 shadow-sm">
                            <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-1">Active Scans</p>
                            <p className="text-3xl font-bold text-white mb-3">1,204</p>
                            {/* Mini line chart simulation */}
                            <div className="flex items-end gap-1 h-6 w-full mt-auto opacity-50">
                                <div className="w-full bg-[#333] rounded-t h-[30%]"></div>
                                <div className="w-full bg-[#333] rounded-t h-[40%]"></div>
                                <div className="w-full bg-[#333] rounded-t h-[35%]"></div>
                                <div className="w-full bg-[#333] rounded-t h-[50%]"></div>
                                <div className="w-full bg-[#333] rounded-t h-[45%]"></div>
                                <div className="w-full bg-[#333] rounded-t h-[60%]"></div>
                                <div className="w-full bg-emerald-500 rounded-t h-[80%]"></div>
                            </div>
                        </div>

                        {/* Stat Block 2 */}
                        <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-5 shadow-sm relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-16 h-16 bg-red-500/10 rounded-bl-full pointer-events-none"></div>
                            <p className="text-[10px] text-red-500 font-bold uppercase tracking-widest mb-1">Security Flags</p>
                            <p className="text-3xl font-bold text-red-500 mb-3">42</p>
                            <div className="flex items-end gap-1 h-6 w-full mt-auto opacity-80">
                                <div className="w-full bg-red-500/40 rounded-t h-[10%]"></div>
                                <div className="w-full bg-red-500/40 rounded-t h-[15%]"></div>
                                <div className="w-full bg-red-500/40 rounded-t h-[10%]"></div>
                                <div className="w-full bg-red-500/40 rounded-t h-[20%]"></div>
                                <div className="w-full bg-red-500/70 rounded-t h-[40%]"></div>
                                <div className="w-full bg-red-500/90 rounded-t h-[70%]"></div>
                                <div className="w-full bg-red-500 rounded-t h-[90%]"></div>
                            </div>
                        </div>

                        {/* Stat Block 3 */}
                        <div className="bg-[#111] border border-[#222] rounded-2xl p-5 shadow-sm">
                            <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-1">Incident Rate</p>
                            <p className="text-3xl font-bold text-white mb-3">3.5%</p>
                            <div className="w-full h-1.5 bg-[#222] rounded-full mt-auto mb-1"><div className="w-[3.5%] h-full bg-red-500 rounded-full shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div></div>
                            <p className="text-[9px] text-gray-500 uppercase tracking-widest text-right">Crit Boundary 5%</p>
                        </div>

                        {/* Stat Block 4 */}
                        <div className="bg-[#111] border border-[#222] rounded-2xl p-5 shadow-sm flex flex-col justify-center items-center text-center">
                            <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-1">System Health</p>
                            <div className="w-16 h-16 rounded-full border-4 border-[#222] border-t-emerald-500 flex items-center justify-center shadow-[0_0_20px_rgba(16,185,129,0.1)] mt-2">
                                <span className="text-sm font-bold text-emerald-500">99%</span>
                            </div>
                        </div>
                    </div>

                    {/* Data Grid */}
                    <div className="bg-[#111] rounded-2xl border border-[#222] overflow-hidden shadow-sm">
                        <table className="w-full text-left border-collapse text-sm">
                            <thead>
                                <tr className="bg-[#0a0a0a] text-[10px] uppercase tracking-widest text-[#666] border-b border-[#222]">
                                    <th className="py-4 pl-6 pr-4 font-bold">Session Identity</th>
                                    <th className="p-4 font-bold">Current Quotient</th>
                                    <th className="p-4 font-bold">Risk Trajectory (10m)</th>
                                    <th className="py-4 pr-6 pl-4 font-bold text-right">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[#222]">
                                {/* Selected Row Example */}
                                <tr className="hover:bg-[#1a1a1a] cursor-pointer transition-colors bg-[#1a1a1a] border-l-4 border-red-500 shadow-[inset_4px_0_0_#ef4444]">
                                    <td className="py-5 pl-5 pr-4">
                                        <div className="font-mono text-white font-bold tracking-wide text-[13px] mb-1">acbfd3af-4ba9</div>
                                        <div className="text-[10px] text-[#666] font-bold uppercase tracking-widest">CS101 • 14:02 PM</div>
                                    </td>
                                    <td className="p-4">
                                        <div className="flex items-center gap-3 w-40">
                                            <span className="text-sm font-bold text-red-500 w-10">86%</span>
                                            <div className="flex-1 h-1.5 bg-[#222] rounded-full overflow-hidden">
                                                <div className="w-[86%] h-full bg-red-500"></div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="p-4 w-48">
                                        <div className="flex items-end gap-0.5 h-6 opacity-80">
                                            <div className="w-2 bg-emerald-500/30 rounded-t h-[20%]"></div>
                                            <div className="w-2 bg-emerald-500/40 rounded-t h-[40%]"></div>
                                            <div className="w-2 bg-yellow-500/60 rounded-t h-[60%]"></div>
                                            <div className="w-2 bg-red-500/80 rounded-t h-[90%]"></div>
                                            <div className="w-2 bg-red-500 rounded-t h-full"></div>
                                            <div className="w-2 bg-red-500/80 rounded-t h-[85%]"></div>
                                        </div>
                                    </td>
                                    <td className="py-4 pr-6 pl-4 text-right">
                                        <span className="text-[10px] bg-red-500/10 border border-red-500/20 px-2 py-1.5 rounded text-red-500 font-bold uppercase tracking-widest shadow-sm">Flagged</span>
                                    </td>
                                </tr>

                                {/* Normal Row Example */}
                                <tr className="hover:bg-[#1a1a1a] cursor-pointer transition-colors border-l-4 border-transparent">
                                    <td className="py-5 pl-5 pr-4">
                                        <div className="font-mono text-gray-300 font-bold tracking-wide text-[13px] mb-1">b72f10d2-8ca1</div>
                                        <div className="text-[10px] text-[#666] font-bold uppercase tracking-widest">CS101 • 14:01 PM</div>
                                    </td>
                                    <td className="p-4">
                                        <div className="flex items-center gap-3 w-40">
                                            <span className="text-sm font-bold text-emerald-500 w-10">14%</span>
                                            <div className="flex-1 h-1.5 bg-[#222] rounded-full overflow-hidden">
                                                <div className="w-[14%] h-full bg-emerald-500"></div>
                                            </div>
                                        </div>
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
                                    <td className="py-4 pr-6 pl-4 text-right">
                                        <span className="text-[10px] bg-[#222] border border-[#333] px-2 py-1.5 rounded text-gray-400 font-bold uppercase tracking-widest shadow-sm">Normal</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </main>

                {/* Slide-over Drawer (Simulated Open) */}
                <aside className="fixed right-0 top-0 bottom-0 mt-16 w-[650px] bg-[#111] border-l border-[#222] shadow-2xl flex flex-col z-40 transform translate-x-0 transition-transform duration-300">
                    <div className="p-8 border-b border-[#222] flex justify-between items-start bg-[#0a0a0a] shrink-0">
                        <div>
                            <p className="text-xs text-red-500 font-bold uppercase tracking-wider mb-2 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(239,68,68,1)]"></span> Target Locked
                            </p>
                            <h3 className="font-mono text-3xl font-bold text-white mb-2 tracking-tight">acbfd3af-4ba9</h3>
                            <p className="text-xs font-bold text-[#666] uppercase tracking-widest">CS101 Midterm  •  2,105 Events</p>
                        </div>
                        <button className="text-[#666] hover:text-white transition-colors bg-[#222] hover:bg-[#333] w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg border border-[#333]">&times;</button>
                    </div>

                    <div className="px-8 pt-6 pb-2 shrink-0 bg-[#0a0a0a]">
                        <div className="flex gap-2">
                            <button className="px-6 py-2.5 bg-[#222] text-white rounded-xl text-xs font-bold uppercase tracking-wider shadow-sm border border-[#333]">Overview</button>
                            <button className="px-6 py-2.5 text-[#666] hover:text-white hover:bg-[#1a1a1a] rounded-xl text-xs font-bold uppercase tracking-wider transition-colors">Timeline</button>
                            <button className="px-6 py-2.5 text-blue-400 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 rounded-xl text-xs font-bold uppercase tracking-wider transition-colors">Review</button>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto w-full p-8 bg-[#0a0a0a]">
                        <div className="w-full h-full border-2 border-dashed border-[#222] rounded-2xl flex flex-col items-center justify-center gap-4 text-center p-8">
                            <svg className="w-8 h-8 text-[#444]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            <p className="text-[#666] font-bold uppercase tracking-widest text-xs">Deep-Dive Analytics Panel content omitted for this mockup variation</p>
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    );
};

export default AdminOptionCv3;
