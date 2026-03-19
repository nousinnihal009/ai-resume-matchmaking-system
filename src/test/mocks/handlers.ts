import { http, HttpResponse } from 'msw';

const API_BASE = 'http://localhost:8000/api/v1';

// ── Canonical mock objects ─────────────────────────────────────────────

export const mockUser = {
  id: 'user-student-001',
  email: 'student@test.com',
  name: 'Test Student',
  role: 'student' as const,
  createdAt: new Date('2026-01-01T00:00:00Z'),
  updatedAt: new Date('2026-01-01T00:00:00Z'),
};

export const mockRecruiter = {
  id: 'user-recruiter-001',
  email: 'recruiter@test.com',
  name: 'Test Recruiter',
  role: 'recruiter' as const,
  createdAt: new Date('2026-01-01T00:00:00Z'),
  updatedAt: new Date('2026-01-01T00:00:00Z'),
};

export const mockAuthResponse = {
  user: mockUser,
  access_token: 'mock-jwt-token-for-testing-only',
  token_type: 'bearer',
};

export const mockResume = {
  id: 'resume-001',
  userId: 'user-student-001',
  fileName: 'test-resume.txt',
  fileUrl: 'https://example.com/resume.txt',
  fileSize: 1024,
  uploadedAt: new Date('2026-01-01T00:00:00Z'),
  extractedText: 'Senior Python developer with 5 years experience in FastAPI',
  extractedSkills: ['Python', 'FastAPI', 'PostgreSQL'],
  education: [],
  experience: [],
  status: 'completed' as const,
};

export const mockJob = {
  id: 'job-001',
  recruiterId: 'user-recruiter-001',
  title: 'Senior Python Engineer',
  company: 'Acme Corp',
  description: 'We need a Python engineer.',
  requiredSkills: ['Python', 'FastAPI', 'PostgreSQL'],
  preferredSkills: [],
  experienceLevel: 'senior' as const,
  location: 'Remote',
  locationType: 'remote' as const,
  postedAt: new Date('2026-01-01T00:00:00Z'),
  status: 'active' as const,
};

export const mockMatch = {
  id: 'match-001',
  resumeId: 'resume-001',
  jobId: 'job-001',
  studentId: 'user-student-001',
  recruiterId: 'user-recruiter-001',
  overallScore: 82,
  skillScore: 75,
  experienceScore: 85,
  semanticScore: 86,
  matchedSkills: ['Python expertise', 'FastAPI experience'],
  missingSkills: ['Kubernetes knowledge'],
  explanation: {
    summary: 'Good match',
    strengths: ['Python expertise', 'FastAPI experience'],
    gaps: ['Kubernetes knowledge'],
    recommendations: ['Learn Kubernetes basics', 'Get AWS certification'],
    skillBreakdown: {
      matched: ['Python expertise', 'FastAPI experience'],
      missing: ['Kubernetes knowledge'],
      additional: [],
    }
  },
  createdAt: new Date('2026-01-01T00:00:00Z'),
  status: 'pending' as const,
};

// ── Error response factory ─────────────────────────────────────────────

export const errorResponse = (message: string, status = 400) =>
  HttpResponse.json(
    { success: false, error: message, data: null },
    { status }
  );

// ── MSW request handlers ───────────────────────────────────────────────

export const handlers = [
  // Auth
  http.post(`${API_BASE}/auth/login`, () =>
    HttpResponse.json({
      success: true,
      data: mockAuthResponse,
      message: 'Login successful',
    })
  ),

  http.post(`${API_BASE}/auth/signup`, () =>
    HttpResponse.json({
      success: true,
      data: mockAuthResponse,
      message: 'Account created successfully',
    })
  ),

  http.post(`${API_BASE}/auth/logout`, () =>
    HttpResponse.json({
      success: true,
      data: null,
      message: 'Logged out',
    })
  ),

  // Resumes
  http.post(`${API_BASE}/resumes/upload`, () =>
    HttpResponse.json({
      success: true,
      data: mockResume,
    })
  ),

  http.get(`${API_BASE}/resumes/user/:userId`, () =>
    HttpResponse.json({
      success: true,
      data: [mockResume],
    })
  ),

  http.get(`${API_BASE}/resumes/:resumeId`, () =>
    HttpResponse.json({
      success: true,
      data: mockResume,
    })
  ),

  http.delete(`${API_BASE}/resumes/:resumeId`, () =>
    HttpResponse.json({
      success: true,
      data: null,
    })
  ),

  // Jobs
  http.post(`${API_BASE}/jobs`, () =>
    HttpResponse.json({
      success: true,
      data: mockJob,
    })
  ),

  http.get(`${API_BASE}/jobs/recruiter/:recruiterId`, () =>
    HttpResponse.json({
      success: true,
      data: [mockJob],
    })
  ),

  http.get(`${API_BASE}/jobs`, () =>
    HttpResponse.json({
      success: true,
      data: [mockJob],
    })
  ),

  http.get(`${API_BASE}/jobs/:jobId`, () =>
    HttpResponse.json({
      success: true,
      data: mockJob,
    })
  ),

  http.put(`${API_BASE}/jobs/:jobId`, () =>
    HttpResponse.json({
      success: true,
      data: mockJob,
    })
  ),

  http.delete(`${API_BASE}/jobs/:jobId`, () =>
    HttpResponse.json({
      success: true,
      data: null,
    })
  ),

  // Matches
  http.post(`${API_BASE}/matches/resume/:resumeId`, () =>
    HttpResponse.json({
      success: true,
      data: [mockMatch],
    })
  ),

  http.post(`${API_BASE}/matches/job/:jobId`, () =>
    HttpResponse.json({
      success: true,
      data: [mockMatch],
    })
  ),

  http.get(`${API_BASE}/matches/student/:studentId`, () =>
    HttpResponse.json({
      success: true,
      data: [mockMatch],
    })
  ),

  http.get(`${API_BASE}/matches/recruiter/:recruiterId`, () =>
    HttpResponse.json({
      success: true,
      data: [mockMatch],
    })
  ),

  http.get(`${API_BASE}/matches/job/:jobId`, () =>
    HttpResponse.json({
      success: true,
      data: [mockMatch],
    })
  ),

  http.patch(`${API_BASE}/matches/:matchId/status`, () =>
    HttpResponse.json({
      success: true,
      data: { ...mockMatch, status: 'viewed' },
    })
  ),
];
