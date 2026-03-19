/**
 * Tests for the MatchScoreCard component.
 *
 * Verifies that match scores, mapped skill lengths are
 * correctly displayed to the user.
 */
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { render } from '../utils';
import { MatchScoreCard } from '@/app/components/MatchScoreCard';

const mockMatchProp: any = {
  id: 'match-001',
  resumeId: 'resume-001',
  jobId: 'job-001',
  studentId: 'student-001',
  recruiterId: 'recruiter-001',
  overallScore: 0.82,
  skillScore: 0.75,
  experienceScore: 0.85,
  semanticScore: 0.86,
  matchedSkills: ['Python expertise', 'FastAPI experience'],
  missingSkills: ['Kubernetes knowledge'],
  explanation: {
    summary: 'Good match',
    strengths: ['Python expertise'],
    gaps: ['Kubernetes knowledge'],
    recommendations: ['Learn Kubernetes'],
    skillBreakdown: {
      matched: ['Python expertise', 'FastAPI experience'],
      missing: ['Kubernetes knowledge'],
      additional: [],
    }
  },
  status: 'pending',
  createdAt: new Date(),
};

describe('MatchScoreCard', () => {

  // ── Score display ───────────────────────────────────────────────────

  describe('score display', () => {

    it('renders the overall score value (82)', () => {
      render(<MatchScoreCard match={mockMatchProp} />);
      expect(screen.getByText(/82/)).toBeInTheDocument();
    });

    it('does not crash when overallScore is 0', () => {
      expect(() =>
        render(
          <MatchScoreCard match={{ ...mockMatchProp, overallScore: 0 }} />
        )
      ).not.toThrow();
    });

    it('does not crash when overallScore is 1', () => {
      expect(() =>
        render(
          <MatchScoreCard match={{ ...mockMatchProp, overallScore: 1 }} />
        )
      ).not.toThrow();
    });

  });

  // ── Skills Display ───────────────────────────────────────────────────────

  describe('skills display', () => {

    it('renders matched skill length', () => {
      render(<MatchScoreCard match={mockMatchProp} />);
      // Should show '2 matched'
      expect(screen.getByText(/2 matched/i)).toBeInTheDocument();
    });

    it('renders missing skill length', () => {
      render(<MatchScoreCard match={mockMatchProp} />);
      // Should show '1 missing'
      expect(screen.getByText(/1 missing/i)).toBeInTheDocument();
    });

    it('does not crash when matchedSkills is empty array', () => {
      expect(() =>
        render(
          <MatchScoreCard match={{ ...mockMatchProp, matchedSkills: [] }} />
        )
      ).not.toThrow();
    });

    it('does not crash when missingSkills is empty array', () => {
      expect(() =>
        render(
          <MatchScoreCard match={{ ...mockMatchProp, missingSkills: [] }} />
        )
      ).not.toThrow();
    });

  });

});
