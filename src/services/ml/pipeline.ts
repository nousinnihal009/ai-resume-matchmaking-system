/**
 * ML Pipeline Orchestrator
 * Coordinates the entire ML workflow for resume processing and matching
 */

import { logger } from '@/utils/logger';
import { extractTextFromFile, parseStructuredData } from './textExtraction';
import { extractSkills } from './skillExtraction';
import { generateEmbedding } from './embeddings';
import { matchResumeToJobs, matchJobToResumes, type MatchResult } from './matchingEngine';
import type { Resume, Job } from '@/types/models';
import { generateId } from '@/utils/helpers';

export interface ResumeProcessingResult {
  resumeId: string;
  extractedText: string;
  skills: string[];
  education: any[];
  experience: any[];
  embedding: number[];
  status: 'completed' | 'failed';
  error?: string;
}

export interface JobProcessingResult {
  jobId: string;
  skills: string[];
  embedding: number[];
  status: 'completed' | 'failed';
  error?: string;
}

/**
 * Process uploaded resume through the entire ML pipeline
 */
export async function processResume(file: File, userId: string): Promise<ResumeProcessingResult> {
  const resumeId = generateId();
  
  logger.info('Starting resume processing pipeline', {
    resumeId,
    userId,
    fileName: file.name,
  });

  try {
    // Step 1: Extract text from file
    logger.time(`resume-extraction-${resumeId}`);
    const { text: extractedText } = await extractTextFromFile(file);
    logger.timeEnd(`resume-extraction-${resumeId}`);

    // Step 2: Parse structured data
    logger.time(`resume-parsing-${resumeId}`);
    const structured = parseStructuredData(extractedText);
    logger.timeEnd(`resume-parsing-${resumeId}`);

    // Step 3: Extract skills
    logger.time(`skill-extraction-${resumeId}`);
    const { skills } = extractSkills(extractedText);
    logger.timeEnd(`skill-extraction-${resumeId}`);

    // Step 4: Generate embedding
    logger.time(`embedding-generation-${resumeId}`);
    const embedding = await generateEmbedding(extractedText);
    logger.timeEnd(`embedding-generation-${resumeId}`);

    logger.info('Resume processing completed', {
      resumeId,
      skillCount: skills.length,
      textLength: extractedText.length,
    });

    return {
      resumeId,
      extractedText,
      skills,
      education: structured.education,
      experience: structured.experience,
      embedding,
      status: 'completed',
    };
  } catch (error) {
    logger.error('Resume processing failed', error as Error, { resumeId });
    
    return {
      resumeId,
      extractedText: '',
      skills: [],
      education: [],
      experience: [],
      embedding: [],
      status: 'failed',
      error: (error as Error).message,
    };
  }
}

/**
 * Process job description through the ML pipeline
 */
export async function processJobDescription(jobData: {
  title: string;
  description: string;
  requiredSkills: string[];
}): Promise<JobProcessingResult> {
  const jobId = generateId();
  
  logger.info('Starting job processing pipeline', {
    jobId,
    title: jobData.title,
  });

  try {
    // Combine job data for embedding
    const combinedText = `${jobData.title}\n${jobData.description}\nRequired Skills: ${jobData.requiredSkills.join(', ')}`;

    // Extract additional skills from description
    const { skills: extractedSkills } = extractSkills(combinedText);
    
    // Combine with provided skills
    const allSkills = Array.from(new Set([...jobData.requiredSkills, ...extractedSkills]));

    // Generate embedding
    const embedding = await generateEmbedding(combinedText);

    logger.info('Job processing completed', {
      jobId,
      skillCount: allSkills.length,
    });

    return {
      jobId,
      skills: allSkills,
      embedding,
      status: 'completed',
    };
  } catch (error) {
    logger.error('Job processing failed', error as Error, { jobId });
    
    return {
      jobId,
      skills: [],
      embedding: [],
      status: 'failed',
      error: (error as Error).message,
    };
  }
}

/**
 * Execute matching workflow for a resume against all jobs
 */
export async function executeResumeMatching(
  resume: Resume,
  allJobs: Job[],
  topK: number = 10
): Promise<MatchResult[]> {
  logger.info('Executing resume matching workflow', {
    resumeId: resume.id,
    jobCount: allJobs.length,
    topK,
  });

  try {
    // Filter active jobs only
    const activeJobs = allJobs.filter(job => job.status === 'active');

    if (activeJobs.length === 0) {
      logger.warn('No active jobs available for matching');
      return [];
    }

    // Execute matching
    const matches = matchResumeToJobs(resume, activeJobs, topK);

    logger.info('Resume matching completed', {
      resumeId: resume.id,
      matchCount: matches.length,
    });

    return matches;
  } catch (error) {
    logger.error('Resume matching failed', error as Error, {
      resumeId: resume.id,
    });
    throw error;
  }
}

/**
 * Execute matching workflow for a job against all resumes
 */
export async function executeJobMatching(
  job: Job,
  allResumes: Resume[],
  topK: number = 50
): Promise<MatchResult[]> {
  logger.info('Executing job matching workflow', {
    jobId: job.id,
    resumeCount: allResumes.length,
    topK,
  });

  try {
    // Filter completed resumes only
    const completedResumes = allResumes.filter(resume => resume.status === 'completed');

    if (completedResumes.length === 0) {
      logger.warn('No completed resumes available for matching');
      return [];
    }

    // Execute matching
    const matches = matchJobToResumes(job, completedResumes, topK);

    logger.info('Job matching completed', {
      jobId: job.id,
      matchCount: matches.length,
    });

    return matches;
  } catch (error) {
    logger.error('Job matching failed', error as Error, {
      jobId: job.id,
    });
    throw error;
  }
}

/**
 * Health check for ML pipeline
 */
export async function mlPipelineHealthCheck(): Promise<{
  status: 'healthy' | 'degraded' | 'unhealthy';
  components: {
    textExtraction: boolean;
    skillExtraction: boolean;
    embedding: boolean;
    matching: boolean;
  };
}> {
  logger.info('Running ML pipeline health check');

  const components = {
    textExtraction: true,
    skillExtraction: true,
    embedding: true,
    matching: true,
  };

  try {
    // Test skill extraction
    const testText = 'Python JavaScript React Node.js';
    const { skills } = extractSkills(testText);
    components.skillExtraction = skills.length > 0;

    // Test embedding generation
    const testEmbedding = await generateEmbedding(testText);
    components.embedding = testEmbedding.length > 0;

    const healthyCount = Object.values(components).filter(Boolean).length;
    const status = healthyCount === 4 ? 'healthy' : healthyCount >= 2 ? 'degraded' : 'unhealthy';

    logger.info('ML pipeline health check completed', { status, components });

    return { status, components };
  } catch (error) {
    logger.error('ML pipeline health check failed', error as Error);
    return { status: 'unhealthy', components };
  }
}
