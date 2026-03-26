'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldAlert, Key, Terminal, User, Loader2, Mail, Lock } from 'lucide-react';
import { loginUser, registerUser, getCurrentUser, isAuthenticated, type AuthUser } from '@/lib/api';

export default function LoginPage() {
    const router = useRouter();
    const [mode, setMode] = useState<'login' | 'register'>('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [checkingAuth, setCheckingAuth] = useState(true);

    // Check if already authenticated
    useEffect(() => {
        async function checkAuth() {
            if (isAuthenticated()) {
                try {
                    const user: AuthUser = await getCurrentUser();
                    const redirectTo = (user.role === 'admin' || user.role === 'instructor') ? '/admin' : '/';
                    router.push(redirectTo);
                    return;
                } catch {
                    // Token invalid, continue to login
                }
            }
            setCheckingAuth(false);
        }
        checkAuth();
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (mode === 'register') {
                await registerUser(email, password, fullName || undefined);
                // After registration, auto-login
                await loginUser(email, password);
            } else {
                await loginUser(email, password);
            }

            // Check user role and redirect
            const user = await getCurrentUser();
            const redirectTo = (user.role === 'admin' || user.role === 'instructor') ? '/admin' : '/';
            router.push(redirectTo);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'ACCESS_DENIED:_UNAUTHORIZED');
        } finally {
            setLoading(false);
        }
    };

    if (checkingAuth) {
        return (
            <div className="min-h-screen text-foreground flex items-center justify-center p-4 selection:bg-accent selection:text-background">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 border-8 border-foreground border-t-accent rounded-full animate-spin" />
                    <p className="font-mono text-sm font-bold uppercase tracking-widest animate-pulse">VERIFYING_CREDENTIALS...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center p-4 selection:bg-accent selection:text-background relative">
            <div className="absolute inset-0 bg-cyber-grid pointer-events-none opacity-10"></div>
            <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 rounded-2xl glass-panel relative overflow-hidden z-10 shadow-[0_0_40px_rgba(0,0,0,0.5)] border border-primary/20">

                {/* Left side info */}
                <div className="hidden md:flex flex-col justify-between p-12 relative overflow-hidden bg-primary/5">
                    <div className="absolute inset-0 bg-cyber-grid pointer-events-none opacity-30"></div>
                    <div className="relative z-10">
                        <div className="p-3 rounded-xl bg-primary/20 text-primary mb-6 ring-1 ring-primary/30 inline-flex">
                            <ShieldAlert className="w-8 h-8" />
                        </div>
                        <h2 className="font-display text-4xl font-bold tracking-tight text-foreground mb-4">
                            System Access
                        </h2>
                        <p className="font-sans text-lg text-muted-foreground">
                            Authenticate to access the Overseer Protocol. All sessions are monitored for security compliance.
                        </p>
                    </div>
                    <div className="relative z-10 mt-12">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/50 border border-primary/20 text-primary text-xs font-mono shadow-[0_0_10px_rgba(195,180,253,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
                            ENVIRONMENT: SECURE
                        </div>
                    </div>
                </div>

                <div className="p-8 md:p-12 relative bg-card/30 backdrop-blur-md border-l border-white/5">
                    {/* Header */}
                    <div className="mb-8 text-center flex flex-col items-center">
                        <div className="p-3 rounded-xl bg-primary/10 text-primary mb-4 ring-1 ring-primary/20">
                            <Lock className="w-6 h-6" />
                        </div>
                        <h1 className="font-display text-2xl md:text-3xl font-bold tracking-tight text-foreground mb-2">
                            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
                        </h1>
                        <p className="font-sans text-sm text-muted-foreground">
                            {mode === 'login' ? 'Enter your credentials to continue' : 'Register for a new admin portal account'}
                        </p>
                    </div>

                    {/* Error */}
                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-destructive/10 text-destructive border border-destructive/20 shadow-sm flex items-center gap-3">
                            <ShieldAlert className="w-5 h-5 shrink-0" />
                            <p className="font-sans text-sm font-medium">{error}</p>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {mode === 'register' && (
                            <div className="space-y-1.5">
                                <label className="font-sans text-sm font-medium text-foreground">
                                    Full Name
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                                        <User className="w-4 h-4" />
                                    </div>
                                    <input
                                        type="text"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                        className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-border/50 bg-background font-sans text-sm outline-none shadow-sm input-glow"
                                        placeholder="Jane Doe"
                                    />
                                </div>
                            </div>
                        )}

                        <div className="space-y-1.5">
                            <label className="font-sans text-sm font-medium text-foreground">
                                Email Address
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                                    <Mail className="w-4 h-4" />
                                </div>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-border/50 bg-background font-sans text-sm outline-none shadow-sm input-glow"
                                    placeholder="admin@example.com"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="font-sans text-sm font-medium text-foreground">
                                Password
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                                    <Key className="w-4 h-4" />
                                </div>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-border/50 bg-background font-sans text-sm outline-none shadow-sm input-glow"
                                    placeholder="••••••••"
                                    required
                                    minLength={4}
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full flex justify-center items-center py-2.5 mt-2 rounded-lg font-sans text-sm font-semibold shadow-sm transition-all active:scale-[0.98] ${loading
                                    ? 'bg-primary/70 text-primary-foreground cursor-not-allowed'
                                    : 'bg-primary text-primary-foreground hover:bg-primary/90'
                                }`}
                        >
                            {loading ? (
                                <span className="flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Processing...
                                </span>
                            ) : (
                                mode === 'login' ? 'Sign In' : 'Create Account'
                            )}
                        </button>
                    </form>

                    {/* Toggle mode */}
                    <div className="mt-8 pt-6 border-t border-border/50 text-center">
                        <p className="font-sans text-sm text-muted-foreground mb-2">
                            {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
                        </p>
                        <button
                            type="button"
                            onClick={() => {
                                setMode(mode === 'login' ? 'register' : 'login');
                                setError('');
                            }}
                            className="font-sans text-sm font-semibold text-primary hover:text-primary/80 transition-colors"
                        >
                            {mode === 'login' ? 'Register here' : 'Sign in instead'}
                        </button>
                    </div>

                    {/* Default credentials hint */}
                    {mode === 'login' && process.env.NODE_ENV === 'development' && (
                        <div className="mt-8 p-4 rounded-xl border border-destructive/20 bg-destructive/5 relative shadow-sm">
                            <div className="absolute top-0 right-0 -mt-2 -mr-2 p-1.5 rounded-full bg-background border border-destructive/20 text-destructive shadow-sm">
                                <Terminal className="w-3 h-3" />
                            </div>
                            <p className="font-sans text-xs font-semibold uppercase tracking-wider text-destructive mb-3 flex items-center gap-1.5">
                                Development Mode
                            </p>
                            <div className="space-y-2 font-mono text-sm">
                                <div className="flex items-center justify-between pb-2 border-b border-border/50">
                                    <span className="text-muted-foreground font-sans text-xs font-medium">Email</span>
                                    <span className="font-medium text-foreground">admin@cheatingdetector.com</span>
                                </div>
                                <div className="flex items-center justify-between pt-1">
                                    <span className="text-muted-foreground font-sans text-xs font-medium">Password</span>
                                    <span className="font-medium text-foreground">admin123</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
