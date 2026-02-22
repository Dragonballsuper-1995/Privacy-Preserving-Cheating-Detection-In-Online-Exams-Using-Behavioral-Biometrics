/**
 * Admin WebSocket Hook
 *
 * Connects to ws://<host>/ws/admin to receive real-time updates:
 *   - risk_update   {session_id, risk_score, risk_level}
 *   - status_update  {session_id, status, details}
 *   - alert          {session_id, alert_type, message, severity}
 *   - heartbeat      {}
 */

'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { getStoredToken, getApiBase } from '@/lib/api';

export interface WsRiskUpdate {
    type: 'risk_update';
    session_id: string;
    risk_score: number;
    risk_level: string;
    timestamp: string;
}

export interface WsStatusUpdate {
    type: 'status_update';
    session_id: string;
    status: string;
    details?: Record<string, unknown>;
    timestamp: string;
}

export interface WsAlert {
    type: 'alert';
    session_id: string;
    alert_type: string;
    message: string;
    severity: string;
    timestamp: string;
}

export interface WsLiveEvents {
    type: 'live_events';
    session_id: string;
    events: Array<{
        session_id: string;
        question_id: string;
        event_type: string;
        data: Record<string, unknown>;
        timestamp: number;
        logged_at?: string;
    }>;
    timestamp: string;
}

export type WsMessage = WsRiskUpdate | WsStatusUpdate | WsAlert | WsLiveEvents | { type: 'pong' | 'heartbeat' | 'subscribed';[key: string]: unknown };

interface UseAdminWebSocketOptions {
    enabled?: boolean;
    reconnectInterval?: number;
    maxReconnectAttempts?: number;
}

interface UseAdminWebSocketReturn {
    connected: boolean;
    lastMessage: WsMessage | null;
    alerts: WsAlert[];
    riskUpdates: Map<string, WsRiskUpdate>;
    clearAlerts: () => void;
}

export function useAdminWebSocket({
    enabled = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
}: UseAdminWebSocketOptions = {}): UseAdminWebSocketReturn {
    const [connected, setConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState<WsMessage | null>(null);
    const [alerts, setAlerts] = useState<WsAlert[]>([]);
    const [riskUpdates, setRiskUpdates] = useState<Map<string, WsRiskUpdate>>(new Map());

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectCount = useRef(0);
    const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

    const clearAlerts = useCallback(() => {
        setAlerts([]);
    }, []);

    useEffect(() => {
        if (!enabled) return;

        function connect() {
            // Derive WS URL from API base
            let apiBase = getApiBase();

            // If API base is empty (localhost with Next.js rewrites), connect directly to backend
            if (!apiBase) {
                apiBase = 'http://localhost:8000';
            }

            const wsProtocol = apiBase.startsWith('https') ? 'wss' : 'ws';
            const wsHost = apiBase.replace(/^https?:\/\//, '');
            const wsUrl = `${wsProtocol}://${wsHost}/ws/admin`;

            const token = getStoredToken();
            const fullUrl = token ? `${wsUrl}?token=${encodeURIComponent(token)}` : wsUrl;

            const ws = new WebSocket(fullUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                setConnected(true);
                reconnectCount.current = 0;

                // Subscribe to all sessions
                ws.send(JSON.stringify({ action: 'subscribe_all' }));
            };

            ws.onmessage = (event) => {
                try {
                    const msg: WsMessage = JSON.parse(event.data);
                    setLastMessage(msg);

                    if (msg.type === 'risk_update') {
                        setRiskUpdates(prev => {
                            const next = new Map(prev);
                            next.set((msg as WsRiskUpdate).session_id, msg as WsRiskUpdate);
                            return next;
                        });
                    } else if (msg.type === 'alert') {
                        setAlerts(prev => [...prev, msg as WsAlert]);
                    }
                } catch {
                    // Ignore non-JSON messages
                }
            };

            ws.onclose = () => {
                setConnected(false);
                wsRef.current = null;

                // Auto-reconnect
                if (reconnectCount.current < maxReconnectAttempts) {
                    reconnectCount.current += 1;
                    reconnectTimer.current = setTimeout(connect, reconnectInterval);
                }
            };

            ws.onerror = () => {
                ws.close();
            };
        }

        connect();

        // Ping keepalive every 25s
        const pingTimer = setInterval(() => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({ action: 'ping' }));
            }
        }, 25_000);

        return () => {
            clearInterval(pingTimer);
            if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
            if (wsRef.current) {
                wsRef.current.onclose = null; // Prevent reconnect on intentional close
                wsRef.current.close();
            }
        };
    }, [enabled, reconnectInterval, maxReconnectAttempts]);

    return { connected, lastMessage, alerts, riskUpdates, clearAlerts };
}
