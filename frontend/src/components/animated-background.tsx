export function AnimatedBackground() {
    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
            {/* Grid Pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#8a2be233_1px,transparent_1px),linear-gradient(to_bottom,#8a2be233_1px,transparent_1px)] bg-[size:32px_32px] opacity-[0.15] dark:opacity-[0.08] mask-image:radial-gradient(ellipse_100%_100%_at_50%_50%,black_10%,transparent_100%)"></div>

            {/* Animated Glowing Orbs */}
            <div className="absolute top-[-20%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-primary/10 dark:bg-primary/10 blur-[120px] animate-blob"></div>
            <div className="absolute top-[10%] right-[-20%] w-[40vw] h-[40vw] rounded-full bg-accent/10 dark:bg-accent/10 blur-[130px] animate-blob animation-delay-2000"></div>
            <div className="absolute bottom-[-20%] left-[10%] w-[60vw] h-[60vw] rounded-full bg-secondary/15 dark:bg-secondary/10 blur-[140px] animate-blob animation-delay-4000"></div>
        </div>
    );
}
