/**
 * Behavior Logger Hook
 * Captures keystrokes, paste events, focus/blur, mouse movements,
 * clicks, and scroll events for cheating detection.
 */

import { useCallback, useRef, useEffect, useState } from 'react';
import { getStoredToken, getApiBase } from '@/lib/api';

export interface BehaviorEvent {
    session_id: string;
    question_id: string;
    event_type: 'key' | 'paste' | 'focus' | 'mouse' | 'click' | 'scroll';
    data: Record<string, unknown>;
    timestamp: number;
}

interface UseBehaviorLoggerOptions {
    sessionId: string;
    questionId: string;
    enabled?: boolean;
    batchSize?: number;
    flushInterval?: number;
    mouseThrottleMs?: number;
    apiEndpoint?: string;
}

export function useBehaviorLogger({
    sessionId,
    questionId,
    enabled = true,
    batchSize = 50,
    flushInterval = 5000,
    mouseThrottleMs = 60,
    apiEndpoint,
}: UseBehaviorLoggerOptions) {
    const eventsBuffer = useRef<BehaviorEvent[]>([]);
    const lastFlush = useRef<number>(0);
    const lastMouseLog = useRef<number>(0);
    const mouseDownTime = useRef<number>(0);
    const wsRef = useRef<WebSocket | null>(null);

    // Resolve endpoint once
    const resolvedEndpoint = apiEndpoint || `${getApiBase()}/api/events/log`;

    // Convert API base to WS base
    const getWsBase = useCallback(() => {
        const base = getApiBase();
        if (base.startsWith('https')) return base.replace('https', 'wss');
        if (base.startsWith('http')) return base.replace('http', 'ws');
        return `ws://${window.location.host}`; // fallback if relative
    }, []);

    // Establish WebSocket Connection
    useEffect(() => {
        if (!enabled) return;

        let reconnectTimer: ReturnType<typeof setTimeout>;

        const connectWs = () => {
            const wsUrl = `${getWsBase()}/ws/stream-events/${sessionId}`;
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                wsRef.current = ws;
                flushEvents(); // immediately flush buffered items
            };

            ws.onerror = (err) => {
                console.error("Behavior Logger WS Error:", err);
            };

            ws.onclose = () => {
                wsRef.current = null;
                reconnectTimer = setTimeout(connectWs, 3000);
            };
        };

        connectWs();

        return () => {
            clearTimeout(reconnectTimer);
            if (wsRef.current) {
                // Ensure no reconnect on clean unmount
                wsRef.current.onclose = null;
                wsRef.current.close();
                wsRef.current = null;
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [sessionId, enabled, getWsBase]); // excluding flushEvents to prevent reconnection loops

    // Initialize timestamp on mount
    useEffect(() => {
        lastFlush.current = Date.now();
    }, []);

    // Flush events to backend
    const flushEvents = useCallback(async () => {
        if (eventsBuffer.current.length === 0) return;

        const eventsToSend = [...eventsBuffer.current];
        eventsBuffer.current = [];
        lastFlush.current = Date.now();

        // Try WebSocket first
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            try {
                wsRef.current.send(JSON.stringify({ events: eventsToSend }));
                return; // successfully sent via WS
            } catch (error) {
                console.error('Failed to send behavior events via WS:', error);
                // Fall back to REST if WS payload failed
            }
        }

        // Fallback to REST request
        const headers: Record<string, string> = { 'Content-Type': 'application/json' };
        const token = getStoredToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        try {
            await fetch(resolvedEndpoint, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    session_id: sessionId,
                    events: eventsToSend,
                }),
            });
        } catch (error) {
            console.error('Failed to send behavior events:', error);
            // Re-add events to buffer on failure
            eventsBuffer.current = [...eventsToSend, ...eventsBuffer.current];
        }
    }, [sessionId, resolvedEndpoint]);

    // Add event to buffer
    const logEvent = useCallback(
        (eventType: BehaviorEvent['event_type'], data: Record<string, unknown>) => {
            if (!enabled) return;

            const event: BehaviorEvent = {
                session_id: sessionId,
                question_id: questionId,
                event_type: eventType,
                data,
                timestamp: Date.now(),
            };

            eventsBuffer.current.push(event);

            // Flush if batch size reached
            if (eventsBuffer.current.length >= batchSize) {
                flushEvents();
            }
        },
        [sessionId, questionId, enabled, batchSize, flushEvents]
    );

    // ---- Keyboard ----
    const handleKeyEvent = useCallback(
        (e: KeyboardEvent) => {
            logEvent('key', {
                type: e.type,
                key: e.key,
                code: e.code,
                shift: e.shiftKey,
                ctrl: e.ctrlKey,
                alt: e.altKey,
            });
        },
        [logEvent]
    );

    // ---- Paste ----
    const handlePaste = useCallback(
        (e: ClipboardEvent) => {
            const pastedText = e.clipboardData?.getData('text') || '';
            logEvent('paste', {
                type: 'paste',
                content_length: pastedText.length,
            });
        },
        [logEvent]
    );

    // ---- Focus / Blur ----
    const handleFocus = useCallback(() => {
        logEvent('focus', { type: 'focus' });
    }, [logEvent]);

    const handleBlur = useCallback(() => {
        logEvent('focus', { type: 'blur' });
    }, [logEvent]);

    // ---- Mouse Move (throttled) ----
    const handleMouseMove = useCallback(
        (e: MouseEvent) => {
            const now = Date.now();
            if (now - lastMouseLog.current < mouseThrottleMs) return;
            lastMouseLog.current = now;

            logEvent('mouse', {
                x: e.clientX,
                y: e.clientY,
                screenX: e.screenX,
                screenY: e.screenY,
            });
        },
        [logEvent, mouseThrottleMs]
    );

    // ---- Mouse Click (track duration via down/up) ----
    const handleMouseDown = useCallback(
        (e: MouseEvent) => {
            mouseDownTime.current = Date.now();
            void e.button; // button tracked via handleMouseUp
        },
        []
    );

    const handleMouseUp = useCallback(
        (e: MouseEvent) => {
            const duration = mouseDownTime.current > 0
                ? Date.now() - mouseDownTime.current
                : 0;
            const buttons = ['left', 'middle', 'right'];
            const button = buttons[e.button] || 'left';

            logEvent('click', {
                button,
                duration,
                x: e.clientX,
                y: e.clientY,
            });

            mouseDownTime.current = 0;
        },
        [logEvent]
    );

    // ---- Scroll ----
    const handleScroll = useCallback(() => {
        logEvent('scroll', {
            scrollX: window.scrollX,
            scrollY: window.scrollY,
        });
    }, [logEvent]);

    // Set up event listeners
    useEffect(() => {
        if (!enabled) return;

        // Keyboard events
        document.addEventListener('keydown', handleKeyEvent);
        document.addEventListener('keyup', handleKeyEvent);

        // Paste events
        document.addEventListener('paste', handlePaste);

        // Window focus/blur
        window.addEventListener('focus', handleFocus);
        window.addEventListener('blur', handleBlur);

        // Mouse events
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mousedown', handleMouseDown);
        document.addEventListener('mouseup', handleMouseUp);

        // Scroll events (throttled via passive listener)
        let scrollTimeout: ReturnType<typeof setTimeout> | null = null;
        const throttledScroll = () => {
            if (scrollTimeout) return;
            scrollTimeout = setTimeout(() => {
                handleScroll();
                scrollTimeout = null;
            }, 200);
        };
        window.addEventListener('scroll', throttledScroll, { passive: true });

        // Periodic flush
        const flushTimer = setInterval(() => {
            if (Date.now() - lastFlush.current >= flushInterval) {
                flushEvents();
            }
        }, flushInterval);

        // Cleanup
        return () => {
            document.removeEventListener('keydown', handleKeyEvent);
            document.removeEventListener('keyup', handleKeyEvent);
            document.removeEventListener('paste', handlePaste);
            window.removeEventListener('focus', handleFocus);
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mousedown', handleMouseDown);
            document.removeEventListener('mouseup', handleMouseUp);
            window.removeEventListener('scroll', throttledScroll);
            if (scrollTimeout) clearTimeout(scrollTimeout);
            clearInterval(flushTimer);

            // Final flush on unmount
            flushEvents();
        };
    }, [enabled, handleKeyEvent, handlePaste, handleFocus, handleBlur,
        handleMouseMove, handleMouseDown, handleMouseUp, handleScroll,
        flushEvents, flushInterval]);

    return {
        logEvent,
        flushEvents,
        getEventCount: () => eventsBuffer.current.length,
    };
}
