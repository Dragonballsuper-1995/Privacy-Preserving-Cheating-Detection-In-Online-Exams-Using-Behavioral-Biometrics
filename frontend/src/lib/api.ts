/**
 * API client for backend communication
 */

// Smart API URL detection based on how the frontend is accessed
function getApiBase(): string {
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

        // DEVELOPMENT: VS Code tunnel
        if (hostname.includes('devtunnels.ms')) {
            return 'https://6vjfqk0n-8000.inc1.devtunnels.ms';
        }

        // DEVELOPMENT: Network IP access
        // DEVELOPMENT: Network IP access
        if (hostname.startsWith('192.168.')) {
            return `http://${hostname}:8000`;
        }
    }

    // Fallback (Server-side rendering or localhost dev)
    // Fallback (Server-side rendering or localhost dev)
    return process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
}

const API_BASE = getApiBase();

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
    similarity_score: number;
    editing_score: number;
    is_flagged: boolean;
    flag_reasons: string[];
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

// Analysis API
export async function analyzeSession(sessionId: string): Promise<RiskScore> {
    const res = await fetch(`${API_BASE}/api/analysis/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
        };
        created_at?: string;
        is_simulated?: boolean;
    }[];
}> {
    const res = await fetch(`${API_BASE}/api/analysis/dashboard/summary`);
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

export async function getSessionTimeline(sessionId: string): Promise<{ timeline: any[] }> {
    const res = await fetch(`${API_BASE}/api/analysis/session/${sessionId}/timeline`);
    if (!res.ok) throw new Error('Failed to fetch session timeline');
    return res.json();
}

export async function simulateSession(isCheater: boolean, count: number = 3, questionCount: number = 6): Promise<void> {
    const res = await fetch(`${API_BASE}/api/simulation/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
