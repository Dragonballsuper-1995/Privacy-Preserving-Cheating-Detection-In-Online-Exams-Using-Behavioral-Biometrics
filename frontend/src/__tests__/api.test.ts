/**
 * Tests for the API client module (api.ts)
 *
 * Covers:
 * - Token management (get/set/clear/isAuthenticated)
 * - Auth API functions (login, register, logout)
 * - Auth header injection
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import {
    getStoredToken,
    setStoredToken,
    clearStoredToken,
    isAuthenticated,
    loginUser,
    registerUser,
    logoutUser,
    getCurrentUser,
} from '@/lib/api';

// --- Token management ---

describe('Token Management', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('returns null when no token is stored', () => {
        expect(getStoredToken()).toBeNull();
    });

    it('stores and retrieves a token', () => {
        setStoredToken('my-jwt-token');
        expect(getStoredToken()).toBe('my-jwt-token');
    });

    it('clears a stored token', () => {
        setStoredToken('my-jwt-token');
        clearStoredToken();
        expect(getStoredToken()).toBeNull();
    });

    it('isAuthenticated returns false with no token', () => {
        expect(isAuthenticated()).toBe(false);
    });

    it('isAuthenticated returns true with a token', () => {
        setStoredToken('abc');
        expect(isAuthenticated()).toBe(true);
    });
});

// --- Auth API ---

describe('Auth API', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.restoreAllMocks();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('loginUser stores token on success', async () => {
        const mockResponse = {
            access_token: 'new-token-123',
            token_type: 'bearer',
            expires_in: 3600,
        };

        vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
            new Response(JSON.stringify(mockResponse), {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
            })
        );

        const result = await loginUser('test@test.com', 'password');

        expect(result.access_token).toBe('new-token-123');
        expect(getStoredToken()).toBe('new-token-123');
    });

    it('loginUser throws on failure', async () => {
        vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
            new Response(JSON.stringify({ detail: 'Invalid credentials' }), {
                status: 401,
                headers: { 'Content-Type': 'application/json' },
            })
        );

        await expect(loginUser('bad@test.com', 'wrong')).rejects.toThrow(
            'Invalid credentials'
        );
        expect(getStoredToken()).toBeNull();
    });

    it('registerUser calls the register endpoint', async () => {
        const mockUser = {
            id: 'user-1',
            email: 'new@test.com',
            full_name: 'New User',
            role: 'student',
            is_active: true,
        };

        const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
            new Response(JSON.stringify(mockUser), {
                status: 201,
                headers: { 'Content-Type': 'application/json' },
            })
        );

        const result = await registerUser('new@test.com', 'pass123', 'New User');

        expect(result.email).toBe('new@test.com');
        expect(fetchSpy).toHaveBeenCalledTimes(1);

        const [url, options] = fetchSpy.mock.calls[0];
        expect((url as string).includes('/api/auth/register')).toBe(true);
        expect(options?.method).toBe('POST');
    });

    it('getCurrentUser sends auth header', async () => {
        setStoredToken('test-token-456');

        const mockUser = {
            id: 'user-1',
            email: 'me@test.com',
            role: 'admin',
            is_active: true,
        };

        const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
            new Response(JSON.stringify(mockUser), { status: 200 })
        );

        await getCurrentUser();

        const [, options] = fetchSpy.mock.calls[0];
        const headers = options?.headers as Record<string, string>;
        expect(headers['Authorization']).toBe('Bearer test-token-456');
    });

    it('logoutUser clears the stored token', () => {
        setStoredToken('my-token');
        expect(isAuthenticated()).toBe(true);

        logoutUser();

        expect(isAuthenticated()).toBe(false);
        expect(getStoredToken()).toBeNull();
    });
});
