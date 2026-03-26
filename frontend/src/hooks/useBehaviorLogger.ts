/**
 * Behavior Logger Hook
 * Captures keystrokes, paste events, focus/blur, mouse movements,
 * clicks, and scroll events for cheating detection.
 *
 * Performance: Event listeners are attached once. sessionId and questionId
 * are accessed via refs so no re-attachment occurs on question changes.
 */

import { useCallback, useRef, useEffect } from 'react';
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
    mouseThrottleMs = 100,
    apiEndpoint,
}: UseBehaviorLoggerOptions) {
    const eventsBuffer = useRef<BehaviorEvent[]>([]);
    const lastFlush = useRef<number>(0);
    const lastMouseLog = useRef<number>(0);
    const mouseDownTime = useRef<number>(0);
    const wsRef = useRef<WebSocket | null>(null);

    // Stable refs — updated every render, read inside stable callbacks
    const sessionIdRef = useRef(sessionId);
    const questionIdRef = useRef(questionId);
    const enabledRef = useRef(enabled);
    const batchSizeRef = useRef(batchSize);
    const flushIntervalRef = useRef(flushInterval);
    const mouseThrottleMsRef = useRef(mouseThrottleMs);
    const apiEndpointRef = useRef(apiEndpoint);

    sessionIdRef.current = sessionId;
    questionIdRef.current = questionId;
    enabledRef.current = enabled;
    batchSizeRef.current = batchSize;
    flushIntervalRef.current = flushInterval;
    mouseThrottleMsRef.current = mouseThrottleMs;
    apiEndpointRef.current = apiEndpoint;

    const resolvedEndpointRef = useRef('');
    resolvedEndpointRef.current = apiEndpoint || `${getApiBase()}/api/events/log`;

    // Convert API base to WS base — stable function, no deps
    const getWsBase = useCallback(() => {
        const base = getApiBase();
        if (base.startsWith('https')) return base.replace('https', 'wss');
        if (base.startsWith('http')) return base.replace('http', 'ws');
        return `ws://${window.location.host}`;
    }, []);

    // Flush events — stable reference, reads from refs
    const flushEvents = useCallback(async () => {
        if (eventsBuffer.current.length === 0) return;

        const eventsToSend = [...eventsBuffer.current];
        eventsBuffer.current = [];
        lastFlush.current = Date.now();

        // Try WebSocket first
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            try {
                wsRef.current.send(JSON.stringify({ events: eventsToSend }));
                return;
            } catch (error) {
                console.error('Failed to send behavior events via WS:', error);
            }
        }

        // Fallback to REST
        const headers: Record<string, string> = { 'Content-Type': 'application/json' };
        const token = getStoredToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        try {
            await fetch(resolvedEndpointRef.current, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    session_id: sessionIdRef.current,
                    events: eventsToSend,
                }),
            });
        } catch (error) {
            console.error('Failed to send behavior events:', error);
            eventsBuffer.current = [...eventsToSend, ...eventsBuffer.current];
        }
    }, []); // truly stable — all data accessed via refs

    // Log event — stable reference
    const logEvent = useCallback(
        (eventType: BehaviorEvent['event_type'], data: Record<string, unknown>) => {
            if (!enabledRef.current) return;

            eventsBuffer.current.push({
                session_id: sessionIdRef.current,
                question_id: questionIdRef.current,
                event_type: eventType,
                data,
                timestamp: Date.now(),
            });

            if (eventsBuffer.current.length >= batchSizeRef.current) {
                flushEvents();
            }
        },
        [flushEvents]
    );

    // Stable handler refs — so addEventListener / removeEventListener always
    // receive the exact same function reference.
    const handleKeyEventRef = useRef((e: KeyboardEvent) => {
        logEvent('key', {
            type: e.type,
            key: e.key,
            code: e.code,
            shift: e.shiftKey,
            ctrl: e.ctrlKey,
            alt: e.altKey,
        });
    });

    const handlePasteRef = useRef((e: ClipboardEvent) => {
        const pastedText = e.clipboardData?.getData('text') || '';
        logEvent('paste', { type: 'paste', content_length: pastedText.length });
    });

    const handleFocusRef = useRef(() => logEvent('focus', { type: 'focus' }));
    const handleBlurRef = useRef(() => logEvent('focus', { type: 'blur' }));

    const handleMouseMoveRef = useRef((e: MouseEvent) => {
        const now = Date.now();
        if (now - lastMouseLog.current < mouseThrottleMsRef.current) return;
        lastMouseLog.current = now;
        logEvent('mouse', { x: e.clientX, y: e.clientY, screenX: e.screenX, screenY: e.screenY });
    });

    const handleMouseDownRef = useRef((e: MouseEvent) => {
        mouseDownTime.current = Date.now();
        void e.button;
    });

    const handleMouseUpRef = useRef((e: MouseEvent) => {
        const duration = mouseDownTime.current > 0 ? Date.now() - mouseDownTime.current : 0;
        const buttons = ['left', 'middle', 'right'];
        logEvent('click', {
            button: buttons[e.button] || 'left',
            duration,
            x: e.clientX,
            y: e.clientY,
        });
        mouseDownTime.current = 0;
    });

    const handleScrollRef = useRef(() => {
        logEvent('scroll', { scrollX: window.scrollX, scrollY: window.scrollY });
    });

    // Keep handler refs up to date with latest logEvent
    useEffect(() => {
        handleKeyEventRef.current = (e: KeyboardEvent) => {
            logEvent('key', { type: e.type, key: e.key, code: e.code, shift: e.shiftKey, ctrl: e.ctrlKey, alt: e.altKey });
        };
        handlePasteRef.current = (e: ClipboardEvent) => {
            logEvent('paste', { type: 'paste', content_length: e.clipboardData?.getData('text').length ?? 0 });
        };
        handleFocusRef.current = () => logEvent('focus', { type: 'focus' });
        handleBlurRef.current = () => logEvent('focus', { type: 'blur' });
        handleMouseMoveRef.current = (e: MouseEvent) => {
            const now = Date.now();
            if (now - lastMouseLog.current < mouseThrottleMsRef.current) return;
            lastMouseLog.current = now;
            logEvent('mouse', { x: e.clientX, y: e.clientY, screenX: e.screenX, screenY: e.screenY });
        };
        handleMouseDownRef.current = (e: MouseEvent) => { mouseDownTime.current = Date.now(); void e.button; };
        handleMouseUpRef.current = (e: MouseEvent) => {
            const duration = mouseDownTime.current > 0 ? Date.now() - mouseDownTime.current : 0;
            logEvent('click', { button: ['left', 'middle', 'right'][e.button] || 'left', duration, x: e.clientX, y: e.clientY });
            mouseDownTime.current = 0;
        };
        handleScrollRef.current = () => logEvent('scroll', { scrollX: window.scrollX, scrollY: window.scrollY });
    }, [logEvent]);

    // WebSocket — re-connects only when sessionId or enabled changes
    useEffect(() => {
        if (!enabled || !sessionId) return;

        let reconnectTimer: ReturnType<typeof setTimeout>;

        const connectWs = () => {
            const wsUrl = `${getWsBase()}/ws/stream-events/${sessionIdRef.current}`;
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                wsRef.current = ws;
                flushEvents();
            };
            ws.onerror = (err) => console.error('Behavior Logger WS Error:', err);
            ws.onclose = () => {
                wsRef.current = null;
                reconnectTimer = setTimeout(connectWs, 3000);
            };
        };

        connectWs();

        return () => {
            clearTimeout(reconnectTimer);
            if (wsRef.current) {
                wsRef.current.onclose = null;
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, [sessionId, enabled, getWsBase, flushEvents]);

    // Event listeners — attached ONCE when enabled changes
    useEffect(() => {
        if (!enabled) return;

        // Thin wrappers that always delegate to the latest ref
        const onKeyDown = (e: KeyboardEvent) => handleKeyEventRef.current(e);
        const onKeyUp = (e: KeyboardEvent) => handleKeyEventRef.current(e);
        const onPaste = (e: ClipboardEvent) => handlePasteRef.current(e);
        const onFocus = () => handleFocusRef.current();
        const onBlur = () => handleBlurRef.current();
        const onMouseMove = (e: MouseEvent) => handleMouseMoveRef.current(e);
        const onMouseDown = (e: MouseEvent) => handleMouseDownRef.current(e);
        const onMouseUp = (e: MouseEvent) => handleMouseUpRef.current(e);

        let scrollTimeout: ReturnType<typeof setTimeout> | null = null;
        const onScroll = () => {
            if (scrollTimeout) return;
            scrollTimeout = setTimeout(() => {
                handleScrollRef.current();
                scrollTimeout = null;
            }, 200);
        };

        document.addEventListener('keydown', onKeyDown);
        document.addEventListener('keyup', onKeyUp);
        document.addEventListener('paste', onPaste);
        window.addEventListener('focus', onFocus);
        window.addEventListener('blur', onBlur);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mousedown', onMouseDown);
        document.addEventListener('mouseup', onMouseUp);
        window.addEventListener('scroll', onScroll, { passive: true });

        const flushTimer = setInterval(() => {
            if (Date.now() - lastFlush.current >= flushIntervalRef.current) {
                flushEvents();
            }
        }, flushIntervalRef.current);

        return () => {
            document.removeEventListener('keydown', onKeyDown);
            document.removeEventListener('keyup', onKeyUp);
            document.removeEventListener('paste', onPaste);
            window.removeEventListener('focus', onFocus);
            window.removeEventListener('blur', onBlur);
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mousedown', onMouseDown);
            document.removeEventListener('mouseup', onMouseUp);
            window.removeEventListener('scroll', onScroll);
            if (scrollTimeout) clearTimeout(scrollTimeout);
            clearInterval(flushTimer);
            flushEvents();
        };
    }, [enabled, flushEvents]); // only re-runs when enabled toggles

    return {
        logEvent,
        flushEvents,
        getEventCount: () => eventsBuffer.current.length,
    };
}
