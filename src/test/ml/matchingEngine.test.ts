/**
 * Tests for the client-side matching engine.
 *
 * These tests serve two purposes:
 * 1. Verify offline development behavior is correct
 * 2. Document the expected contract for backend matching responses
 *
 * The backend POST /api/v1/matches/resume/{id} must return a result
 * object conforming to the same shape tested here.
 */
import { describe, it, expect } from 'vitest';
import { matchResumeToJob } from '@/services/ml/matchingEngine';

import type { Resume, Job } from '@/types/models';

// ── Fixtures ──────────────────────────────────────────────────────────

const strongResume: Resume = {
  id: 'resume-1',
  userId: 'user-1',
  fileName: 'strong.pdf',
  fileUrl: 'http://test.com/strong.pdf',
  fileSize: 1000,
  uploadedAt: new Date(),
  extractedSkills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
  extractedText: 'Senior Python developer with 5 years experience in FastAPI',
  education: [],
  experience: [{ company: 'Test', position: 'Dev', description: 'desc', startDate: '2016-01-01', endDate: '2021-01-01' }], // 5 years
  embeddingVector: new Array(384).fill(1),
  status: 'completed',
};

const strongJob: Job = {
  id: 'job-1',
  recruiterId: 'rec-1',
  title: 'Senior Dev',
  company: 'Company A',
  location: 'Remote',
  locationType: 'remote',
  postedAt: new Date(),
  requiredSkills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
  preferredSkills: [],
  description: 'Senior Python developer with 5 years FastAPI experience',
  experienceLevel: 'senior',
  embeddingVector: new Array(384).fill(1),
  status: 'active',
};

const weakResume: Resume = {
  id: 'resume-2',
  userId: 'user-2',
  fileName: 'weak.pdf',
  fileUrl: 'http://test.com/weak.pdf',
  fileSize: 1000,
  uploadedAt: new Date(),
  extractedSkills: ['Watercolor', 'Pottery', 'Sculpture'],
  extractedText: 'Artist with 3 years of studio experience',
  education: [],
  experience: [{ company: 'Studio', position: 'Artist', description: 'art', startDate: '2018-01-01', endDate: '2021-01-01' }], // 3 years
  embeddingVector: new Array(384).fill(0),
  status: 'completed',
};

const weakJob: Job = {
  id: 'job-2',
  recruiterId: 'rec-2',
  title: 'DevOps',
  company: 'Company B',
  location: 'NY',
  locationType: 'onsite',
  postedAt: new Date(),
  requiredSkills: ['Kubernetes', 'Terraform', 'Rust', 'WASM', 'Go'],
  preferredSkills: [],
  description: 'Systems engineer with infrastructure automation expertise',
  experienceLevel: 'senior',
  embeddingVector: new Array(384).fill(-1),
  status: 'active',
};

const emptyResume: Resume = {
  id: 'resume-3',
  userId: 'user-3',
  fileName: 'empty.pdf',
  fileUrl: 'http://test.com/empty.pdf',
  fileSize: 100,
  uploadedAt: new Date(),
  extractedSkills: [],
  extractedText: '',
  education: [],
  experience: [],
  embeddingVector: new Array(384).fill(0),
  status: 'completed',
};

const emptyJob: Job = {
  id: 'job-3',
  recruiterId: 'rec-3',
  title: 'Intern',
  company: 'Company C',
  location: 'Remote',
  locationType: 'remote',
  postedAt: new Date(),
  requiredSkills: [],
  preferredSkills: [],
  description: '',
  experienceLevel: 'internship',
  embeddingVector: new Array(384).fill(0),
  status: 'active',
};

// ── Score range ────────────────────────────────────────────────────────

describe('Matching Engine — score range', () => {

  it('always returns overallScore >= 0', () => {
    const result = matchResumeToJob(weakResume, weakJob);
    expect(result.overallScore).toBeGreaterThanOrEqual(0);
  });

  it('always returns overallScore <= 1', () => {
    const result = matchResumeToJob(strongResume, strongJob);
    expect(result.overallScore).toBeLessThanOrEqual(1);
  });

  it('returns high score (>0.7) for identical skill sets', () => {
    const result = matchResumeToJob(strongResume, strongJob);
    expect(result.overallScore).toBeGreaterThan(0.7);
  });

  it('returns low score (<0.4) for completely mismatched profiles', () => {
    const result = matchResumeToJob(weakResume, weakJob);
    expect(result.overallScore).toBeLessThan(0.4);
  });

  it('returns valid score for empty input without throwing', () => {
    const result = matchResumeToJob(emptyResume, emptyJob);
    expect(result.overallScore).toBeGreaterThanOrEqual(0);
    expect(result.overallScore).toBeLessThanOrEqual(1);
  });

  it('score is higher for partial match than for zero match', () => {
    const partialResume = {
      ...weakResume,
      extractedSkills: ['Python'],
    };
    const partialJob = {
      ...weakJob,
      requiredSkills: ['Python', 'Kubernetes'],
    };
    const partialResult = matchResumeToJob(partialResume, partialJob);
    const zeroResult = matchResumeToJob(weakResume, weakJob);
    expect(partialResult.overallScore).toBeGreaterThan(
      zeroResult.overallScore
    );
  });

});

// ── Result shape ───────────────────────────────────────────────────────

describe('Matching Engine — result shape', () => {

  it('returns strengths as a non-null array', () => {
    const result = matchResumeToJob(strongResume, strongJob);
    expect(result.explanation).toHaveProperty('strengths');
    expect(Array.isArray(result.explanation.strengths)).toBe(true);
  });

  it('returns gaps as a non-null array', () => {
    const gapResume = {
      ...strongResume,
      extractedSkills: ['Python'],
    };
    const gapJob = {
      ...strongJob,
      requiredSkills: ['Python', 'FastAPI', 'Kubernetes', 'Terraform'],
    };
    const result = matchResumeToJob(gapResume, gapJob);
    expect(result.explanation).toHaveProperty('gaps');
    expect(Array.isArray(result.explanation.gaps)).toBe(true);
    expect(result.explanation.gaps.length).toBeGreaterThan(0);
  });

  it('returns recommendations as a non-null array', () => {
    const result = matchResumeToJob(strongResume, strongJob);
    expect(result.explanation).toHaveProperty('recommendations');
    expect(Array.isArray(result.explanation.recommendations)).toBe(true);
  });

  it('missingSkills contains skills present in job but not in resume', () => {
    const gapResume = {
      ...strongResume,
      extractedSkills: ['Python'],
    };
    const gapJob = {
      ...strongJob,
      requiredSkills: ['Python', 'Kubernetes'],
    };
    const result = matchResumeToJob(gapResume, gapJob);
    const missingLower = result.missingSkills.map((g: string) => g.toLowerCase());
    expect(missingLower.some((g: string) => g.includes('kubernetes'))).toBe(true);
  });

  it('matchedSkills contains skills present in both resume and job', () => {
    const matchResume = {
      ...strongResume,
      extractedSkills: ['Python', 'FastAPI'],
    };
    const matchJob = {
      ...strongJob,
      requiredSkills: ['Python', 'FastAPI', 'Kubernetes'],
    };
    const result = matchResumeToJob(matchResume, matchJob);
    const matchedLower = result.matchedSkills.map((s: string) => s.toLowerCase());
    expect(matchedLower.some((s: string) => s.includes('python'))).toBe(true);
  });

});

// ── Edge cases ─────────────────────────────────────────────────────────

describe('Matching Engine — edge cases', () => {

  it('handles empty resumeSkills without throwing', () => {
    expect(() =>
      matchResumeToJob({ ...strongResume, extractedSkills: [] }, strongJob)
    ).not.toThrow();
  });

  it('handles empty jobSkills without throwing', () => {
    expect(() =>
      matchResumeToJob(strongResume, { ...strongJob, requiredSkills: [] })
    ).not.toThrow();
  });

  it('handles empty text fields without throwing', () => {
    expect(() =>
      matchResumeToJob(
        { ...strongResume, extractedText: '' },
        { ...strongJob, description: '' }
      )
    ).not.toThrow();
  });

  it('handles zero experience values without throwing', () => {
    expect(() =>
      matchResumeToJob(
        { ...strongResume, experience: [] },
        { ...strongJob, experienceLevel: 'internship' }
      )
    ).not.toThrow();
  });

});
