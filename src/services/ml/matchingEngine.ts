/**
 * Matching Engine
 * Core ML service for matching resumes to jobs
 */

import { logger } from '@/utils/logger';
import { AppConfig } from '@/config/app.config';
import { cosineSimilarity } from './embeddings';
import { calculateSkillOverlap } from './skillExtraction';
import type { Resume, Job, Match, MatchExplanation } from '@/types/models';
import { generateId } from '@/utils/helpers';

export interface MatchScore {
  overallScore: number;
  skillScore: number;
  experienceScore: number;
  semanticScore: number;
}

export interface MatchResult extends MatchScore {
  resumeId: string;
  jobId: string;
  studentId: string;
  recruiterId: string;
  matchedSkills: string[];
  missingSkills: string[];
  explanation: MatchExplanation;
}

/**
 * Match a single resume to a single job
 */
export function matchResumeToJob(resume: Resume, job: Job): MatchResult {
  logger.info('Matching resume to job', {
    resumeId: resume.id,
    jobId: job.id,
  });

  // Calculate individual scores
  const skillScore = calculateSkillScore(resume, job);
  const experienceScore = calculateExperienceScore(resume, job);
  const semanticScore = calculateSemanticScore(resume, job);

  // Calculate weighted overall score
  const overallScore =
    skillScore * AppConfig.ml.skillWeightage +
    experienceScore * AppConfig.ml.experienceWeightage +
    semanticScore * AppConfig.ml.semanticWeightage;

  // Identify matched and missing skills
  const { matched, onlyInSecond: missing } = calculateSkillOverlap(
    resume.extractedSkills,
    job.requiredSkills
  );

  // Generate explanation
  const explanation = generateMatchExplanation(
    resume,
    job,
    { overallScore, skillScore, experienceScore, semanticScore },
    matched,
    missing
  );

  logger.info('Match completed', {
    resumeId: resume.id,
    jobId: job.id,
    overallScore: overallScore.toFixed(3),
  });

  return {
    resumeId: resume.id,
    jobId: job.id,
    studentId: resume.userId,
    recruiterId: job.recruiterId,
    overallScore,
    skillScore,
    experienceScore,
    semanticScore,
    matchedSkills: matched,
    missingSkills: missing,
    explanation,
  };
}

/**
 * Match a resume to multiple jobs and return top K matches
 */
export function matchResumeToJobs(
  resume: Resume,
  jobs: Job[],
  topK: number = AppConfig.ml.topK
): MatchResult[] {
  logger.info('Matching resume to multiple jobs', {
    resumeId: resume.id,
    jobCount: jobs.length,
    topK,
  });

  const matches = jobs
    .filter(job => job.status === 'active')
    .map(job => matchResumeToJob(resume, job))
    .sort((a, b) => b.overallScore - a.overallScore)
    .slice(0, topK);

  logger.info('Multi-job matching completed', {
    matchCount: matches.length,
  });

  return matches;
}

/**
 * Match a job to multiple resumes and return top K candidates
 */
export function matchJobToResumes(
  job: Job,
  resumes: Resume[],
  topK: number = AppConfig.ml.topK
): MatchResult[] {
  logger.info('Matching job to multiple resumes', {
    jobId: job.id,
    resumeCount: resumes.length,
    topK,
  });

  const matches = resumes
    .filter(resume => resume.status === 'completed')
    .map(resume => matchResumeToJob(resume, job))
    .sort((a, b) => b.overallScore - a.overallScore)
    .slice(0, topK);

  logger.info('Multi-resume matching completed', {
    matchCount: matches.length,
  });

  return matches;
}

/**
 * Calculate skill match score
 */
function calculateSkillScore(resume: Resume, job: Job): number {
  const resumeSkills = new Set(resume.extractedSkills.map(s => s.toLowerCase()));
  const requiredSkills = job.requiredSkills;
  const preferredSkills = job.preferredSkills || [];

  let score = 0;
  let totalWeight = 0;

  // Required skills (higher weight)
  for (const skill of requiredSkills) {
    totalWeight += 1.0;
    if (resumeSkills.has(skill.toLowerCase())) {
      score += 1.0;
    }
  }

  // Preferred skills (lower weight)
  for (const skill of preferredSkills) {
    totalWeight += 0.5;
    if (resumeSkills.has(skill.toLowerCase())) {
      score += 0.5;
    }
  }

  return totalWeight > 0 ? score / totalWeight : 0;
}

/**
 * Calculate experience level match score
 */
function calculateExperienceScore(resume: Resume, job: Job): number {
  const experienceYears = estimateExperienceYears(resume);
  const requiredLevel = job.experienceLevel;

  const levelMap: Record<string, { min: number; max: number }> = {
    internship: { min: 0, max: 1 },
    entry: { min: 0, max: 2 },
    mid: { min: 2, max: 5 },
    senior: { min: 5, max: 100 },
  };

  const required = levelMap[requiredLevel];
  if (!required) return 0.5; // Default score if level unknown

  // Perfect match if within range
  if (experienceYears >= required.min && experienceYears <= required.max) {
    return 1.0;
  }

  // Partial match if close
  if (experienceYears < required.min) {
    const deficit = required.min - experienceYears;
    return Math.max(0, 1.0 - deficit * 0.2); // -20% per year deficit
  } else {
    const excess = experienceYears - required.max;
    return Math.max(0.5, 1.0 - excess * 0.1); // -10% per year excess, min 50%
  }
}

/**
 * Estimate years of experience from resume
 */
function estimateExperienceYears(resume: Resume): number {
  let totalYears = 0;

  for (const exp of resume.experience) {
    if (exp.startDate && exp.endDate) {
      const start = new Date(exp.startDate);
      const end = exp.endDate.toLowerCase() === 'present' 
        ? new Date() 
        : new Date(exp.endDate);
      
      const years = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 365);
      totalYears += years;
    } else {
      // Estimate 1 year if dates not provided
      totalYears += 1;
    }
  }

  return totalYears;
}

/**
 * Calculate semantic similarity score using embeddings
 */
function calculateSemanticScore(resume: Resume, job: Job): number {
  if (!resume.embeddingVector || !job.embeddingVector) {
    logger.warn('Missing embedding vectors, using fallback score');
    return 0.5;
  }

  const similarity = cosineSimilarity(resume.embeddingVector, job.embeddingVector);
  
  // Normalize to 0-1 range (cosine similarity is already -1 to 1)
  return (similarity + 1) / 2;
}

/**
 * Generate human-readable match explanation
 */
function generateMatchExplanation(
  resume: Resume,
  job: Job,
  scores: MatchScore,
  matchedSkills: string[],
  missingSkills: string[]
): MatchExplanation {
  const strengths: string[] = [];
  const gaps: string[] = [];
  const recommendations: string[] = [];

  // Analyze skill match
  const skillMatchRatio = matchedSkills.length / Math.max(job.requiredSkills.length, 1);
  
  if (skillMatchRatio >= 0.8) {
    strengths.push(`Strong skill alignment with ${matchedSkills.length}/${job.requiredSkills.length} required skills`);
  } else if (skillMatchRatio >= 0.5) {
    strengths.push(`Good skill match with ${matchedSkills.length} relevant skills`);
    gaps.push(`Missing ${missingSkills.length} required skills`);
  } else {
    gaps.push(`Limited skill overlap (${matchedSkills.length}/${job.requiredSkills.length} required skills)`);
  }

  // Analyze experience
  const experienceYears = estimateExperienceYears(resume);
  if (scores.experienceScore >= 0.8) {
    strengths.push(`Experience level (${experienceYears.toFixed(1)} years) aligns well with ${job.experienceLevel} role`);
  } else if (scores.experienceScore < 0.5) {
    gaps.push(`Experience level may not match ${job.experienceLevel} requirements`);
  }

  // Analyze semantic match
  if (scores.semanticScore >= 0.7) {
    strengths.push('Strong semantic alignment between resume and job description');
  }

  // Generate recommendations
  if (missingSkills.length > 0 && missingSkills.length <= 5) {
    recommendations.push(`Consider gaining experience in: ${missingSkills.slice(0, 3).join(', ')}`);
  }

  if (scores.experienceScore < 0.7) {
    recommendations.push('Highlight relevant projects and coursework to strengthen experience match');
  }

  // Generate summary
  let summary = '';
  if (scores.overallScore >= 0.85) {
    summary = 'Excellent match! This candidate has strong qualifications for this role.';
  } else if (scores.overallScore >= 0.70) {
    summary = 'Good match with relevant skills and experience. Worth considering.';
  } else if (scores.overallScore >= 0.55) {
    summary = 'Fair match. Some qualifications align, but there are gaps to address.';
  } else {
    summary = 'Limited match. Significant skill or experience gaps exist.';
  }

  return {
    summary,
    strengths,
    gaps,
    recommendations,
    skillBreakdown: {
      matched: matchedSkills,
      missing: missingSkills,
      additional: resume.extractedSkills.filter(
        s => !job.requiredSkills.some(r => r.toLowerCase() === s.toLowerCase())
      ),
    },
  };
}

/**
 * Batch match multiple resumes to multiple jobs
 */
export function batchMatch(
  resumes: Resume[],
  jobs: Job[]
): Map<string, Map<string, MatchResult>> {
  logger.info('Starting batch matching', {
    resumeCount: resumes.length,
    jobCount: jobs.length,
    totalMatches: resumes.length * jobs.length,
  });

  const results = new Map<string, Map<string, MatchResult>>();

  for (const resume of resumes) {
    if (resume.status !== 'completed') continue;

    const jobMatches = new Map<string, MatchResult>();
    for (const job of jobs) {
      if (job.status !== 'active') continue;

      const match = matchResumeToJob(resume, job);
      jobMatches.set(job.id, match);
    }

    results.set(resume.id, jobMatches);
  }

  logger.info('Batch matching completed', {
    resumesProcessed: results.size,
  });

  return results;
}
