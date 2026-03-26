/**
 * Admin Dashboard — Loading Skeleton
 *
 * Shown by Next.js automatically (via React Suspense) while the admin page
 * fetches its initial data. Zero client-side JavaScript — pure server HTML.
 */

export default function AdminLoading() {
    return (
        <div className="h-screen overflow-hidden flex bg-[#0d0a1b] text-foreground font-sans animate-pulse">
            {/* Sidebar Skeleton */}
            <aside className="hidden lg:flex flex-col w-72 border-r border-white/5 bg-[#0f0f13]/90">
                {/* Logo area */}
                <div className="p-6 border-b border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="w-7 h-7 rounded-lg bg-white/10" />
                        <div className="h-6 w-28 rounded-md bg-white/10" />
                    </div>
                    <div className="h-3 w-36 rounded bg-white/5 mt-3" />
                </div>
                {/* Nav items */}
                <nav className="flex-1 p-4 space-y-2 pt-8">
                    <div className="h-3 w-16 rounded bg-white/5 px-4 mb-4" />
                    <div className="h-11 rounded-xl bg-primary/10 border border-primary/10" />
                    <div className="h-11 rounded-xl bg-white/[0.02] border border-white/5" />
                </nav>
            </aside>

            {/* Main Area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header Skeleton */}
                <header className="border-b border-white/5 bg-[#130f23]/80 px-8 py-4 flex items-center justify-between">
                    <div className="h-7 w-48 rounded-md bg-white/10" />
                    <div className="flex gap-3">
                        <div className="h-8 w-24 rounded-full bg-primary/10 border border-primary/10" />
                        <div className="h-8 w-8 rounded-lg bg-white/5" />
                        <div className="h-8 w-20 rounded-lg bg-white/5" />
                        <div className="h-8 w-20 rounded-lg bg-white/5" />
                    </div>
                </header>

                {/* Content Skeleton */}
                <div className="flex-1 px-6 py-6 flex flex-col gap-6 overflow-hidden">
                    {/* Controls bar */}
                    <div className="h-16 rounded-xl border border-border/30 bg-white/[0.02]" />

                    {/* Two-column grid */}
                    <div className="flex-1 min-h-0 grid grid-cols-12 gap-8">
                        {/* Session list */}
                        <div className="col-span-4 rounded-xl border border-white/5 bg-white/[0.02] flex flex-col overflow-hidden">
                            <div className="p-4 border-b border-white/5 flex justify-between items-center">
                                <div className="h-4 w-32 rounded bg-white/10" />
                                <div className="h-6 w-16 rounded-md bg-white/5" />
                            </div>
                            <div className="p-4 border-b border-white/5">
                                <div className="h-3 w-20 rounded bg-white/5" />
                            </div>
                            <div className="flex-1 divide-y divide-white/5 overflow-hidden">
                                {Array.from({ length: 6 }).map((_, i) => (
                                    <div key={i} className="p-4 space-y-3">
                                        <div className="flex justify-between">
                                            <div className="h-4 w-24 rounded bg-white/10" />
                                            <div className="h-5 w-14 rounded-md bg-destructive/10" />
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="flex-1 h-2.5 rounded-full bg-white/5" />
                                            <div className="h-4 w-10 rounded bg-white/10" />
                                        </div>
                                        <div className="flex justify-between">
                                            <div className="h-3 w-28 rounded bg-white/5" />
                                            <div className="h-3 w-16 rounded bg-white/5" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Detail panel empty state */}
                        <div className="col-span-8 rounded-xl border border-white/5 bg-white/[0.02] flex items-center justify-center">
                            <div className="text-center space-y-4">
                                <div className="w-16 h-16 rounded-2xl bg-white/5 mx-auto" />
                                <div className="h-4 w-40 rounded bg-white/10 mx-auto" />
                                <div className="h-3 w-56 rounded bg-white/5 mx-auto" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
