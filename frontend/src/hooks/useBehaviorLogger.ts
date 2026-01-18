/**
 * Behavior Logger Hook
 * Captures keystrokes, paste events, and focus/blur for cheating detection.
 */

import { useCallback, useRef, useEffect, useMemo } from 'react';

export interface BehaviorEvent {
    session_id: string;
    question_id: string;
    event_type: 'key' | 'paste' | 'focus';
    data: Record<string, unknown>;
    timestamp: number;
}

interface UseBehaviorLoggerOptions {
    sessionId: string;
    questionId: string;
    enabled?: boolean;
    batchSize?: number;
    flushInterval?: number;
    apiEndpoint?: string;
}

export function useBehaviorLogger({
    sessionId,
    questionId,
    enabled = true,
    batchSize = 50,
    flushInterval = 5000,
    apiEndpoint = 'http://localhost:8000/api/events/log',
}: UseBehaviorLoggerOptions) {
    const eventsBuffer = useRef<BehaviorEvent[]>([]);
    const lastFlush = useRef<number>(0);

    // Lazy initialize lastFlush on first render
    if (lastFlush.current === 0) {
        lastFlush.current = Date.now();
    }

    // Flush events to backend
    const flushEvents = useCallback(async () => {
        if (eventsBuffer.current.length === 0) return;

        const eventsToSend = [...eventsBuffer.current];
        eventsBuffer.current = [];
        lastFlush.current = Date.now();

        try {
            await fetch(apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
    }, [sessionId, apiEndpoint]);

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

    // Keyboard event handler
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

    // Paste event handler
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

    // Focus/blur handlers
    const handleFocus = useCallback(() => {
        logEvent('focus', { type: 'focus' });
    }, [logEvent]);

    const handleBlur = useCallback(() => {
        logEvent('focus', { type: 'blur' });
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
            clearInterval(flushTimer);

            // Final flush on unmount
            flushEvents();
        };
    }, [enabled, handleKeyEvent, handlePaste, handleFocus, handleBlur, flushEvents, flushInterval]);

    return {
        logEvent,
        flushEvents,
        getEventCount: () => eventsBuffer.current.length,
    };
}
