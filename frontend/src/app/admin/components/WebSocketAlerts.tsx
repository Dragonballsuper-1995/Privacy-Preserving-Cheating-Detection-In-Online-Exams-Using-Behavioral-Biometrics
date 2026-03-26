'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert } from 'lucide-react';
import { useAdminDashboard } from '../context/AdminDashboardContext';

export function WebSocketAlerts() {
    const { wsAlerts, clearAlerts } = useAdminDashboard();

    return (
        <AnimatePresence>
            {wsAlerts.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mb-8 space-y-3"
                >
                    <div className="flex items-center justify-between border-b border-border/50 pb-2">
                        <h3 className="font-display font-semibold tracking-wider text-destructive uppercase text-sm">System Alerts</h3>
                        <button
                            onClick={clearAlerts}
                            className="font-sans text-xs font-semibold uppercase text-muted-foreground hover:text-foreground transition-colors"
                        >
                            Acknowledge All
                        </button>
                    </div>
                    {wsAlerts.slice(-5).map((alert, i) => (
                        <motion.div
                            key={i}
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            className={`p-4 rounded-xl border flex items-start justify-between shadow-sm ${
                                alert.severity === 'critical'
                                    ? 'bg-destructive/10 border-destructive/20'
                                    : 'bg-yellow-500/10 border-yellow-500/20'
                            }`}
                        >
                            <div className="flex items-start gap-3">
                                <ShieldAlert
                                    className={`w-5 h-5 shrink-0 ${
                                        alert.severity === 'critical'
                                            ? 'text-destructive'
                                            : 'text-yellow-600 dark:text-yellow-400'
                                    }`}
                                />
                                <div>
                                    <p className={`font-sans text-sm font-semibold tracking-wide ${
                                        alert.severity === 'critical'
                                            ? 'text-destructive'
                                            : 'text-yellow-700 dark:text-yellow-300'
                                    }`}>
                                        {alert.message}
                                    </p>
                                    <p className="font-mono text-xs text-muted-foreground mt-1">
                                        Session ID: {alert.session_id.substring(0, 12)}
                                    </p>
                                </div>
                            </div>
                            <span className="font-sans font-medium text-xs text-muted-foreground bg-background/50 px-2 py-1 rounded-md">
                                {new Date(alert.timestamp).toLocaleTimeString()}
                            </span>
                        </motion.div>
                    ))}
                </motion.div>
            )}
        </AnimatePresence>
    );
}
