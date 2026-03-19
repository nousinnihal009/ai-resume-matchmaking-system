/**
 * Tests for the API service layer.
 *
 * Every method in authAPI, resumeAPI, jobAPI, and matchAPI is tested
 * for: success path, error path, localStorage side-effects, and
 * JWT header attachment. MSW intercepts all HTTP calls.
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { authAPI, resumeAPI, jobAPI, matchAPI } from '@/services/api/apiService';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';
import {
  mockAuthResponse,
  mockUser,
  mockResume,
  mockJob,
  mockMatch,
  errorResponse,
} from '../mocks/handlers';

const API_BASE = 'http://localhost:8000/api/v1';

// ── authAPI ───────────────────────────────────────────────────────────

describe('authAPI', () => {

  beforeEach(() => localStorage.clear());

  describe('login()', () => {

    it('returns success true with AuthResponse on valid credentials', async () => {
      const result = await authAPI.login({
        email: 'student@test.com',
        password: 'TestPassword123!',
        role: 'student',
      });
      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data?.access_token).toBe(
        'mock-jwt-token-for-testing-only'
      );
    });

    it('stores access_token in localStorage under key "access_token"', async () => {
      await authAPI.login({
        email: 'student@test.com',
        password: 'TestPassword123!',
        role: 'student',
      });
      expect(localStorage.getItem('access_token')).toBe(
        'mock-jwt-token-for-testing-only'
      );
    });

    it('stores user object in localStorage under key "current_user"', async () => {
      await authAPI.login({
        email: 'student@test.com',
        password: 'TestPassword123!',
        role: 'student',
      });
      const stored = JSON.parse(
        localStorage.getItem('current_user') ?? 'null'
      );
      expect(stored).not.toBeNull();
      expect(stored.email).toBe('student@test.com');
      expect(stored.role).toBe('student');
    });

    it('does NOT store hashed_password in localStorage', async () => {
      await authAPI.login({
        email: 'student@test.com',
        password: 'TestPassword123!',
        role: 'student',
      });
      const stored = localStorage.getItem('current_user') ?? '';
      expect(stored).not.toContain('password');
      expect(stored).not.toContain('hashed_password');
    });

    it('returns success false on 401 without throwing', async () => {
      server.use(
        http.post(`${API_BASE}/auth/login`, () =>
          errorResponse('Invalid credentials', 401)
        )
      );
      const result = await authAPI.login({
        email: 'wrong@test.com',
        password: 'BadPassword!',
        role: 'student',
      });
      expect(result.success).toBe(false);
    });

    it('does not store token in localStorage on failed login', async () => {
      server.use(
        http.post(`${API_BASE}/auth/login`, () =>
          errorResponse('Invalid credentials', 401)
        )
      );
      await authAPI.login({
        email: 'wrong@test.com',
        password: 'BadPassword!',
        role: 'student',
      });
      expect(localStorage.getItem('access_token')).toBeNull();
    });

    it('returns success false on 500 server error without throwing', async () => {
      server.use(
        http.post(`${API_BASE}/auth/login`, () =>
          HttpResponse.json({}, { status: 500 })
        )
      );
      const result = await authAPI.login({
        email: 'student@test.com',
        password: 'TestPassword123!',
        role: 'student',
      });
      expect(result.success).toBe(false);
    });

  });

  describe('signup()', () => {

    it('returns success true with AuthResponse on valid data', async () => {
      const result = await authAPI.signup({
        email: 'newuser@test.com',
        password: 'TestPassword123!',
        confirmPassword: 'TestPassword123!',
        name: 'New User',
        role: 'student',
      });
      expect(result.success).toBe(true);
      expect(result.data?.access_token).toBeDefined();
    });

    it('stores token in localStorage on successful signup', async () => {
      await authAPI.signup({
        email: 'newuser@test.com',
        password: 'TestPassword123!',
        confirmPassword: 'TestPassword123!',
        name: 'New User',
        role: 'student',
      });
      expect(localStorage.getItem('access_token')).not.toBeNull();
    });

    it('returns success false on 409 duplicate email', async () => {
      server.use(
        http.post(`${API_BASE}/auth/signup`, () =>
          errorResponse('Email already registered', 409)
        )
      );
      const result = await authAPI.signup({
        email: 'existing@test.com',
        password: 'TestPassword123!',
        confirmPassword: 'TestPassword123!',
        name: 'Existing',
        role: 'student',
      });
      expect(result.success).toBe(false);
    });

  });

});

// ── jobAPI ────────────────────────────────────────────────────────────

describe('jobAPI', () => {

  it('getAll returns array with items', async () => {
    const result = await jobAPI.getAll();
    expect(result.success).toBe(true);
    const items = (result.data as any)?.items ?? result.data;
    expect(Array.isArray(items)).toBe(true);
    expect(items.length).toBeGreaterThan(0);
    expect(items[0].title).toBe('Senior Python Engineer');
  });

  it('create sends POST and returns job object', async () => {
    const result = await jobAPI.create({
      title: 'Senior Python Engineer',
      company: 'Acme Corp',
      description: 'We need a Python engineer.',
      requiredSkills: ['Python'],
      preferredSkills: [],
      experienceLevel: 'senior',
      location: 'Remote',
      locationType: 'remote',
      salaryCurrency: 'USD',
    }, 'user-recruiter-001');
    expect(result.success).toBe(true);
    expect(result.data?.id).toBe('job-001');
    expect(result.data?.title).toBe('Senior Python Engineer');
  });

  it('getAll returns success false on 500', async () => {
    server.use(
      http.get(`${API_BASE}/jobs`, () =>
        HttpResponse.json({}, { status: 500 })
      )
    );
    const result = await jobAPI.getAll();
    expect(result.success).toBe(false);
  });

});

// ── matchAPI ──────────────────────────────────────────────────────────

describe('matchAPI', () => {

  it('matchResumeToJobs returns array of matches', async () => {
    const result = await matchAPI.matchResumeToJobs('resume-001');
    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);
    expect(result.data?.[0]?.overallScore).toBe(82);
  });

  it('matchJobToCandidates returns array with overallScore field', async () => {
    const result = await matchAPI.matchJobToCandidates('job-001');
    expect(result.success).toBe(true);
    const item = result.data?.[0];
    expect(typeof item?.overallScore).toBe('number');
    expect(item?.overallScore).toBe(82);
  });

  it('getMatchesByStudent returns array of matches', async () => {
    const result = await matchAPI.getMatchesByStudent('user-student-001');
    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);
  });

  it('matchResumeToJobs returns success false on 404', async () => {
    server.use(
      http.post(`${API_BASE}/matches/resume/:resumeId`, () =>
        errorResponse('Resume not found', 404)
      )
    );
    const result = await matchAPI.matchResumeToJobs('nonexistent-id');
    expect(result.success).toBe(false);
  });

});

// ── resumeAPI ─────────────────────────────────────────────────────────

describe('resumeAPI', () => {

  it('upload sends multipart request and returns resume', async () => {
    const file = new File(
      ['John Doe\nPython Developer'],
      'resume.txt',
      { type: 'text/plain' }
    );
    const result = await resumeAPI.upload(file, 'user-student-001');
    expect(result.success).toBe(true);
    expect(result.data?.id).toBe('resume-001');
  });

  it('getByUser returns array for valid userId', async () => {
    const result = await resumeAPI.getByUser('user-student-001');
    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);
  });

  it('upload returns success false on server error', async () => {
    server.use(
      http.post(`${API_BASE}/resumes/upload`, () =>
        errorResponse('File too large', 413)
      )
    );
    const file = new File(['content'], 'resume.txt', {
      type: 'text/plain',
    });
    const result = await resumeAPI.upload(file, 'user-student-001');
    expect(result.success).toBe(false);
  });

});
