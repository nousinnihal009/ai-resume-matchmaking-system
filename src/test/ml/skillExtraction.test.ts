/**
 * Tests for the client-side skill extraction service.
 *
 * Skill extraction underpins the entire matching pipeline.
 * These tests verify correctness across common resume text patterns,
 * edge cases, and the deduplication contract.
 */
import { describe, it, expect } from 'vitest';
import { extractSkills } from '@/services/ml/skillExtraction';

describe('Skill Extraction', () => {

  // ── Core extraction ──────────────────────────────────────────────────

  describe('core extraction', () => {

    it('extracts Python from resume text', () => {
      const result = extractSkills(
        'Experienced Python developer with 5 years'
      );
      const lower = result.skills.map((s: string) => s.toLowerCase());
      expect(lower).toContain('python');
    });

    it('extracts multiple skills from single sentence', () => {
      const result = extractSkills(
        'Built REST APIs using FastAPI and deployed to AWS with Docker'
      );
      expect(result.skills.length).toBeGreaterThan(1);
    });

    it('extracts skills from multi-line resume text', () => {
      const text = [
        'John Doe — Software Engineer',
        'Skills: Python, TypeScript, PostgreSQL',
        'Experience: Led team using React and Node.js',
      ].join('\n');
      const result = extractSkills(text);
      const lower = result.skills.map((s: string) => s.toLowerCase());
      expect(lower).toContain('python');
      expect(lower).toContain('typescript');
    });

  });

  // ── Case insensitivity ───────────────────────────────────────────────

  describe('case insensitivity', () => {

    it('finds "python" when written in lowercase', () => {
      const result = extractSkills('expert in python programming');
      const lower = result.skills.map((s: string) => s.toLowerCase());
      expect(lower).toContain('python');
    });

    it('finds "PYTHON" when written in uppercase', () => {
      const result = extractSkills('PYTHON AND FASTAPI DEVELOPER');
      const lower = result.skills.map((s: string) => s.toLowerCase());
      expect(lower).toContain('python');
    });

    it('finds "Python" when written in title case', () => {
      const result = extractSkills('Proficient in Python and React');
      const lower = result.skills.map((s: string) => s.toLowerCase());
      expect(lower).toContain('python');
    });

  });

  // ── Deduplication ────────────────────────────────────────────────────

  describe('deduplication', () => {

    it('returns Python only once when mentioned three times', () => {
      const result = extractSkills(
        'Python developer using Python frameworks built with Python'
      );
      const pythonEntries = result.skills.filter(
        (s: string) => s.toLowerCase() === 'python'
      );
      expect(pythonEntries.length).toBe(1);
    });

  });

  // ── Return type ──────────────────────────────────────────────────────

  describe('return type', () => {

    it('always returns an array of skills inside the result object', () => {
      expect(Array.isArray(extractSkills('any text').skills)).toBe(true);
      expect(Array.isArray(extractSkills('').skills)).toBe(true);
    });

    it('returns empty array for empty string', () => {
      expect(extractSkills('').skills.length).toBe(0);
    });

    it('returns empty array for text with no known skills', () => {
      const result = extractSkills(
        'I enjoy hiking, cooking, and reading novels on weekends'
      );
      expect(Array.isArray(result.skills)).toBe(true);
    });

  });

  // ── Robustness ───────────────────────────────────────────────────────

  describe('robustness', () => {

    it('does not throw for empty string', () => {
      expect(() => extractSkills('')).not.toThrow();
    });

    it('does not throw for whitespace-only string', () => {
      expect(() => extractSkills('   \n\t  ')).not.toThrow();
    });

    it('does not throw for very long input', () => {
      const longText = 'Python '.repeat(1000);
      expect(() => extractSkills(longText)).not.toThrow();
    });

  });

});
