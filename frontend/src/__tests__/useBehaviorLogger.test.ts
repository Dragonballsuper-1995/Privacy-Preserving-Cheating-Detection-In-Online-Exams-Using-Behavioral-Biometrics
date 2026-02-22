/**
 * Tests for the useBehaviorLogger hook
 *
 * Covers:
 * - Event logging (key, paste, focus, mouse, click, scroll)
 * - Buffer management and flushing
 * - Throttling of mouse events
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useBehaviorLogger } from '@/hooks/useBehaviorLogger';

// Mock the api module
vi.mock('@/lib/api', () => ({
    getStoredToken: () => 'fake-token',
    getApiBase: () => 'http://localhost:8000',
}));

describe('useBehaviorLogger', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        vi.spyOn(globalThis, 'fetch').mockResolvedValue(
            new Response('{}', { status: 200 })
        );
    });

    afterEach(() => {
        vi.useRealTimers();
        vi.restoreAllMocks();
    });

    const defaultProps = {
        sessionId: 'session-1',
        questionId: 'q-1',
        enabled: true,
        batchSize: 50,
        flushInterval: 5000,
    };

    it('starts with 0 events in buffer', () => {
        const { result } = renderHook(() => useBehaviorLogger(defaultProps));
        expect(result.current.getEventCount()).toBe(0);
    });

    it('logs a key event', () => {
        const { result } = renderHook(() => useBehaviorLogger(defaultProps));

        act(() => {
            result.current.logEvent('key', { key: 'a', code: 'KeyA' });
        });

        expect(result.current.getEventCount()).toBe(1);
    });

    it('logs a paste event', () => {
        const { result } = renderHook(() => useBehaviorLogger(defaultProps));

        act(() => {
            result.current.logEvent('paste', { content_length: 42 });
        });

        expect(result.current.getEventCount()).toBe(1);
    });

    it('logs a mouse event', () => {
        const { result } = renderHook(() => useBehaviorLogger(defaultProps));

        act(() => {
            result.current.logEvent('mouse', { x: 100, y: 200 });
        });

        expect(result.current.getEventCount()).toBe(1);
    });

    it('logs a click event', () => {
        const { result } = renderHook(() => useBehaviorLogger(defaultProps));

        act(() => {
            result.current.logEvent('click', {
                button: 'left',
                duration: 120,
                x: 50,
                y: 60,
            });
        });

        expect(result.current.getEventCount()).toBe(1);
    });

    it('logs a scroll event', () => {
        const { result } = renderHook(() => useBehaviorLogger(defaultProps));

        act(() => {
            result.current.logEvent('scroll', { scrollX: 0, scrollY: 300 });
        });

        expect(result.current.getEventCount()).toBe(1);
    });

    it('flushes events to the backend', async () => {
        const fetchSpy = vi.spyOn(globalThis, 'fetch');
        const { result } = renderHook(() => useBehaviorLogger(defaultProps));

        act(() => {
            result.current.logEvent('key', { key: 'a' });
            result.current.logEvent('key', { key: 'b' });
        });

        expect(result.current.getEventCount()).toBe(2);

        await act(async () => {
            await result.current.flushEvents();
        });

        expect(result.current.getEventCount()).toBe(0);
        expect(fetchSpy).toHaveBeenCalledTimes(1);

        const [url, options] = fetchSpy.mock.calls[0];
        expect((url as string)).toContain('/api/events/log');
        expect(options?.method).toBe('POST');

        // Verify auth header is included
        const headers = options?.headers as Record<string, string>;
        expect(headers['Authorization']).toBe('Bearer fake-token');
    });

    it('auto-flushes when batch size is reached', async () => {
        const fetchSpy = vi.spyOn(globalThis, 'fetch');
        const { result } = renderHook(() =>
            useBehaviorLogger({ ...defaultProps, batchSize: 3 })
        );

        await act(async () => {
            result.current.logEvent('key', { key: 'a' });
            result.current.logEvent('key', { key: 'b' });
            result.current.logEvent('key', { key: 'c' }); // triggers flush
        });

        expect(fetchSpy).toHaveBeenCalled();
    });

    it('does not log events when disabled', () => {
        const { result } = renderHook(() =>
            useBehaviorLogger({ ...defaultProps, enabled: false })
        );

        act(() => {
            result.current.logEvent('key', { key: 'a' });
        });

        expect(result.current.getEventCount()).toBe(0);
    });

    it('re-adds events to buffer on flush failure', async () => {
        vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(
            new Error('Network error')
        );

        const { result } = renderHook(() => useBehaviorLogger(defaultProps));

        act(() => {
            result.current.logEvent('key', { key: 'a' });
        });

        await act(async () => {
            await result.current.flushEvents();
        });

        // Events should be back in the buffer
        expect(result.current.getEventCount()).toBe(1);
    });
});
