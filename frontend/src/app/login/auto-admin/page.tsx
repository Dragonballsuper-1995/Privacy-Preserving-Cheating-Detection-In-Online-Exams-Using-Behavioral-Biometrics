/**
 * Auto-Login as Admin (Development Only)
 *
 * Navigate to /login/auto-admin to instantly authenticate
 * with the default admin credentials and redirect to /admin.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { loginUser, setStoredToken } from '@/lib/api';
import { Terminal, Loader2 } from 'lucide-react';

export default function AutoAdminLogin() {
    const router = useRouter();
    const [status, setStatus] = useState('AUTHENTICATING_AS_ADMIN...');
    const [isError, setIsError] = useState(false);

    useEffect(() => {
        async function autoLogin() {
            if (process.env.NODE_ENV !== 'development') {
                setStatus('ERROR: AUTO_LOGIN_AVAILABLE_IN_DEV_MODE_ONLY');
                setIsError(true);
                return;
            }
            try {
                const result = await loginUser('admin@cheatingdetector.com', 'admin123');
                setStoredToken(result.access_token);
                setStatus('ACCESS_GRANTED. REDIRECTING...');
                setTimeout(() => router.push('/admin'), 500);
            } catch {
                setStatus('AUTH_FAILED: CHECK_BACKEND_AND_DB_STATE');
                setIsError(true);
            }
        }
        autoLogin();
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4 text-foreground selection:bg-accent selection:text-background font-sans">
            <div className={`max-w-md w-full border-4 border-foreground bg-card p-8 text-center shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,0.1)] ${isError ? 'border-[#ff003c]' : ''}`}>
                <div className={`p-4 mx-auto mb-6 inline-flex border-4 border-foreground ${isError ? 'bg-[#ff003c] text-white' : 'bg-foreground text-background'}`}>
                    <Terminal className="w-8 h-8 stroke-[3]" />
                </div>
                {!isError && (
                    <div className="mb-6 flex justify-center">
                        <Loader2 className="w-8 h-8 animate-spin text-accent stroke-[3]" />
                    </div>
                )}
                <h2 className={`font-mono text-sm font-bold uppercase tracking-widest leading-relaxed ${isError ? 'text-[#ff003c]' : 'text-foreground/80 animate-pulse'}`}>
                    {status}
                </h2>
                <div className="mt-8 pt-4 border-t-4 border-foreground/10 font-mono text-xs text-foreground/50 uppercase font-bold break-all">
                    TARGET_ID: ADMIN@CHEATINGDETECTOR.COM
                </div>
            </div>
        </div>
    );
}
