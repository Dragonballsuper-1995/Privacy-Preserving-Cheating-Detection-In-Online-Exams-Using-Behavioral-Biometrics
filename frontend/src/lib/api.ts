/**
 * API client for backend communication
 */

// Smart API URL detection based on how the frontend is accessed
export function getApiBase(): string {
    // If we're in the browser, detect the environment from the URL
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;

        // DEVELOPMENT: Localhost (use Next.js rewrites)
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return '';
        }

        // PRODUCTION: Render deployment
        if (hostname.includes('onrender.com')) {
            return 'https://cheating-detector-backend.onrender.com';
        }

        // DEVELOPMENT: VS Code tunnel (uses env var)
        if (hostname.includes('devtunnels.ms')) {
            return process.env.NEXT_PUBLIC_API_URL || '';
        }

        // DEVELOPMENT: Network IP access
        if (hostname.startsWith('192.168.')) {
            return `http://${hostname}:8000`;
        }
    }

    // Fallback (Server-side rendering or localhost dev)
    return process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
}

// Lazy: on the server this falls back to env/localhost; in the browser it detects the origin.
export const API_BASE = typeof window !== 'undefined'
    ? getApiBase()
    : (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000');

// ---- Auth Token Management ----

const TOKEN_KEY = 'cheating_detector_auth_token';

export function getStoredToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
    if (typeof window !== 'undefined') {
        localStorage.setItem(TOKEN_KEY, token);
    }
}

export function clearStoredToken(): void {
    if (typeof window !== 'undefined') {
        localStorage.removeItem(TOKEN_KEY);
    }
}

export function isAuthenticated(): boolean {
    return getStoredToken() !== null;
}

function getAuthHeaders(): Record<string, string> {
    const token = getStoredToken();
    if (token) {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        };
    }
    return { 'Content-Type': 'application/json' };
}

function getAuthHeadersGet(): Record<string, string> {
    const token = getStoredToken();
    if (token) {
        return { 'Authorization': `Bearer ${token}` };
    }
    return {};
}

// ---- Auth API ----

export interface AuthUser {
    id: string;
    email: string;
    full_name?: string;
    role: string;
    is_active: boolean;
}

export interface AuthToken {
    access_token: string;
    token_type: string;
    expires_in: number;
}

export async function loginUser(email: string, password: string): Promise<AuthToken> {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
        const detail = await res.json().catch(() => ({ detail: 'Login failed' }));
        throw new Error(detail.detail || 'Login failed');
    }
    const token: AuthToken = await res.json();
    setStoredToken(token.access_token);
    return token;
}

export async function registerUser(
    email: string,
    password: string,
    fullName?: string,
    role: string = 'student'
): Promise<AuthUser> {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName, role }),
    });
    if (!res.ok) {
        const detail = await res.json().catch(() => ({ detail: 'Registration failed' }));
        throw new Error(detail.detail || 'Registration failed');
    }
    return res.json();
}

export async function getCurrentUser(): Promise<AuthUser> {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: getAuthHeadersGet(),
    });
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
}

export function logoutUser(): void {
    clearStoredToken();
}

export interface Exam {
    id: string;
    title: string;
    description: string;
    duration_minutes: number;
    question_count?: number;
    questions?: Question[];
}

export interface Question {
    id: string;
    type: 'mcq' | 'subjective' | 'coding';
    content: string;
    points: number;

    // New metadata
    category?: 'mcq' | 'subjective' | 'coding';
    difficulty?: 'easy' | 'medium' | 'hard';
    subject?: string;
    topic?: string;
    tags?: string[];
    source?: string;
    explanation?: string;

    // MCQ specific
    options?: { id: string; text: string }[];

    // Coding specific
    code_template?: string;
    language?: string;
    test_cases?: { input: unknown; expected: unknown }[];

    // Subjective specific
    min_words?: number;
    max_words?: number;
    rubric?: { key_points?: string[]; scoring_guide?: string };
}

export interface CategorizedExam {
    id: string;
    title: string;
    description: string;
    duration_minutes: number;
    categories: {
        mcq: Question[];
        coding: Question[];
        subjective: Question[];
    };
    total_questions: number;
}

export interface Session {
    id: string;
    exam_id: string;
    student_id: string;
    status: 'not_started' | 'in_progress' | 'submitted' | 'analyzed';
    started_at?: string;
    submitted_at?: string;
    current_question: number;
}

export interface RiskScore {
    session_id: string;
    overall_score: number;
    typing_score: number;
    hesitation_score: number;
    paste_score: number;
    focus_score: number;
    similarity_score: number;
    is_flagged: boolean;
    flag_reasons: string[];
    features?: Record<string, unknown>;
    review_status?: 'pending' | 'confirmed_cheating' | 'false_positive';
    reviewed_by?: string;
    review_notes?: string;
}

// Exams API
export async function listExams(): Promise<{ exams: Exam[] }> {
    const res = await fetch(`${API_BASE}/api/exams/list`);
    if (!res.ok) throw new Error('Failed to fetch exams');
    return res.json();
}

export async function getExam(examId: string): Promise<Exam> {
    const res = await fetch(`${API_BASE}/api/exams/${examId}`);
    if (!res.ok) throw new Error('Failed to fetch exam');
    return res.json();
}

// Sessions API
export async function createSession(examId: string, studentId: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/api/sessions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exam_id: examId, student_id: studentId }),
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
}

export async function startSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/start`, {
        method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to start session');
}

export async function submitSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/submit`, {
        method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to submit session');
}

export async function submitAnswer(
    sessionId: string,
    questionId: string,
    content: string
): Promise<void> {
    const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: questionId, content }),
    });
    if (!res.ok) throw new Error('Failed to submit answer');
}

// Session result (student-facing, no risk scores)
export interface SessionResult {
    session_id: string;
    exam_id: string;
    status: string;
    started_at: string | null;
    submitted_at: string | null;
    answers: {
        question_id: string;
        answered: boolean;
        length: number;
        submitted_at: string | null;
    }[];
    total_answered: number;
    total_questions: number;
}

export async function getSessionResult(sessionId: string): Promise<SessionResult> {
    const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/result`);
    if (!res.ok) throw new Error('Failed to get session result');
    return res.json();
}

// Analysis API
export async function analyzeSession(sessionId: string): Promise<RiskScore> {
    const res = await fetch(`${API_BASE}/api/analysis/analyze`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ session_id: sessionId, include_features: true }),
    });
    if (!res.ok) throw new Error('Failed to analyze session');
    return res.json();
}

export async function getDashboardSummary(): Promise<{
    total_sessions: number;
    flagged_sessions: number;
    sessions: {
        session_id: string;
        risk_score: number;
        is_flagged: boolean;
        event_count: number;
        flag_reasons: string[];
        scores: {
            typing: number;
            hesitation: number;
            paste: number;
            focus: number;
            similarity: number;
        };
        created_at?: string;
        is_simulated?: boolean;
    }[];
}> {
    const res = await fetch(`${API_BASE}/api/analysis/dashboard/summary`, {
        headers: getAuthHeadersGet(),
    });
    if (!res.ok) throw new Error('Failed to fetch dashboard');
    return res.json();
}

// New Category APIs
export async function getCategories(): Promise<{ categories: { id: string; name: string; description: string }[] }> {
    const res = await fetch(`${API_BASE}/api/exams/categories`);
    if (!res.ok) throw new Error('Failed to fetch categories');
    return res.json();
}

export async function getSubjects(category?: string): Promise<{ subjects: string[] }> {
    const url = category ? `${API_BASE}/api/exams/subjects?category=${category}` : `${API_BASE}/api/exams/subjects`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch subjects');
    return res.json();
}

export async function getTopics(subject?: string): Promise<{ topics: string[] }> {
    const url = subject ? `${API_BASE}/api/exams/topics?subject=${subject}` : `${API_BASE}/api/exams/topics`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch topics');
    return res.json();
}

export async function searchQuestions(filters: {
    category?: string;
    difficulty?: string;
    subject?: string;
    topic?: string;
    tags?: string;
}): Promise<{ questions: Question[]; count: number }> {
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.difficulty) params.append('difficulty', filters.difficulty);
    if (filters.subject) params.append('subject', filters.subject);
    if (filters.topic) params.append('topic', filters.topic);
    if (filters.tags) params.append('tags', filters.tags);

    const res = await fetch(`${API_BASE}/api/exams/questions/search?${params}`);
    if (!res.ok) throw new Error('Failed to search questions');
    return res.json();
}

export async function getRandomQuestions(
    category: string,
    count: number = 5,
    difficulty?: string,
    subject?: string
): Promise<{ questions: Question[]; count: number }> {
    const params = new URLSearchParams({ category, count: count.toString() });
    if (difficulty) params.append('difficulty', difficulty);
    if (subject) params.append('subject', subject);

    const res = await fetch(`${API_BASE}/api/exams/questions/random?${params}`);
    if (!res.ok) throw new Error('Failed to get random questions');
    return res.json();
}

export async function getExamByCategory(examId: string): Promise<CategorizedExam> {
    const res = await fetch(`${API_BASE}/api/exams/${examId}/by-category`);
    if (!res.ok) throw new Error('Failed to fetch categorized exam');
    return res.json();
}

export async function getSessionTimeline(sessionId: string): Promise<{ timeline: unknown[] }> {
    const res = await fetch(`${API_BASE}/api/analysis/session/${sessionId}/timeline`, {
        headers: getAuthHeadersGet(),
    });
    if (!res.ok) throw new Error('Failed to fetch session timeline');
    return res.json();
}

export async function simulateSession(isCheater: boolean, count: number = 3, questionCount: number = 6): Promise<void> {
    const res = await fetch(`${API_BASE}/api/simulation/simulate`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
            is_cheater: isCheater,
            count,
            question_count: questionCount,
        }),
    });
    if (!res.ok) throw new Error('Simulation failed');
}

export interface CodeExecutionResult {
    success: boolean;
    stdout: string;
    stderr: string;
    execution_time: number;
    error: string | null;
}

export async function executeCode(
    code: string,
    language: string = 'python',
    timeout: number = 5,
    testInput?: string
): Promise<CodeExecutionResult> {
    const res = await fetch(`${API_BASE}/api/code/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            code,
            language,
            timeout,
            test_input: testInput,
        }),
    });
    if (!res.ok) {
        const error = await res.text();
        throw new Error(`Code execution failed: ${error}`);
    }
    return res.json();
}

export interface TestCase {
    input: unknown;
    expected: unknown;
}

export interface TestCaseResult {
    input: unknown;
    expected: unknown;
    actual: unknown;
    passed: boolean;
    error: string | null;
}

export interface RunTestsResult {
    success: boolean;
    passed: number;
    failed: number;
    total: number;
    results: TestCaseResult[];
    execution_time: number;
    error: string | null;
}

export async function runTests(
    code: string,
    functionName: string,
    testCases: TestCase[],
    language: string = 'python',
    timeout: number = 5
): Promise<RunTestsResult> {
    const res = await fetch(`${API_BASE}/api/code/run-tests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            code,
            function_name: functionName,
            test_cases: testCases,
            language,
            timeout,
        }),
    });
    if (!res.ok) {
        const error = await res.text();
        throw new Error(`Test execution failed: ${error}`);
    }
    return res.json();
}

// ── Instructor Exam Management ──

export async function createExam(
    title: string,
    description: string,
    durationMinutes: number,
): Promise<{ message: string; exam_id: string }> {
    const res = await fetch(`${API_BASE}/api/exams/create`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ title, description, duration_minutes: durationMinutes }),
    });
    if (!res.ok) throw new Error('Failed to create exam');
    return res.json();
}

export async function updateExam(
    examId: string,
    data: { title?: string; description?: string; duration_minutes?: number },
): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/api/exams/${examId}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update exam');
    return res.json();
}

export async function deleteExam(examId: string): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/api/exams/${examId}`, {
        method: 'DELETE',
        headers: getAuthHeadersGet(),
    });
    if (!res.ok) throw new Error('Failed to delete exam');
    return res.json();
}

export async function addQuestion(
    examId: string,
    question: Partial<Question> & { id: string; type: string; content: string },
): Promise<{ message: string; question_id: string }> {
    const res = await fetch(`${API_BASE}/api/exams/${examId}/questions`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(question),
    });
    if (!res.ok) throw new Error('Failed to add question');
    return res.json();
}

// ── MLOps & Model Drift Monitoring ──

export interface DriftMetric {
    drift_detected: boolean;
    p_value: number;
    statistic: number;
}

export interface ModelMetrics {
    status: 'healthy' | 'needs_retraining' | 'insufficient_data';
    message: string;
    metrics: Record<string, DriftMetric>;
    precision_estimate: number;
    total_sessions: number;
    reviewed_sessions_count: number;
}

export async function getModelMetrics(): Promise<ModelMetrics> {
    const res = await fetch(`${API_BASE}/api/models/metrics`, {
        headers: getAuthHeadersGet(),
    });
    if (!res.ok) throw new Error('Failed to fetch model metrics');
    return res.json();
}

export async function triggerRetraining(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/api/models/retrain`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to trigger retraining');
    return res.json();
}

