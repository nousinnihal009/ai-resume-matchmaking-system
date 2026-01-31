/**
 * API Service Layer
 * Simulates backend API calls with mock data
 * In production, these would be actual HTTP requests to FastAPI backend
 */

import { logger } from '@/utils/logger';
import { sleep, generateId } from '@/utils/helpers';
import type {
  User,
  Resume,
  Job,
  Match,
  APIResponse,
  PaginatedResponse,
  LoginForm,
  SignupForm,
  JobPostingForm,
} from '@/types/models';
import {
  dataStore,
  getAllJobs,
  getAllResumes,
  getJobsByRecruiter,
  getResumesByUser,
  getMatchesByStudent,
  getMatchesByRecruiter,
  getMatchesByJob,
} from './mockData';
import { processResume, processJobDescription, executeResumeMatching, executeJobMatching } from '../ml/pipeline';

/**
 * Authentication API
 */
export const authAPI = {
  async login(credentials: LoginForm): Promise<APIResponse<User>> {
    logger.info('API: Login attempt', { email: credentials.email });
    await sleep(500); // Simulate network delay

    const user = Array.from(dataStore.users.values()).find(
      u => u.email === credentials.email && u.role === credentials.role
    );

    if (!user) {
      return {
        success: false,
        error: 'Invalid credentials',
        timestamp: new Date().toISOString(),
      };
    }

    // Store user in session
    sessionStorage.setItem('currentUser', JSON.stringify(user));

    return {
      success: true,
      data: user,
      timestamp: new Date().toISOString(),
    };
  },

  async signup(formData: SignupForm): Promise<APIResponse<User>> {
    logger.info('API: Signup attempt', { email: formData.email });
    await sleep(500);

    // Check if user already exists
    const existingUser = Array.from(dataStore.users.values()).find(
      u => u.email === formData.email
    );

    if (existingUser) {
      return {
        success: false,
        error: 'Email already registered',
        timestamp: new Date().toISOString(),
      };
    }

    // Create new user
    const userId = generateId();
    const newUser: User = {
      id: userId,
      email: formData.email,
      name: formData.name,
      role: formData.role,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    dataStore.users.set(userId, newUser);

    // Create profile based on role
    if (formData.role === 'student') {
      dataStore.studentProfiles.set(userId, {
        ...newUser,
        role: 'student',
      });
    } else if (formData.role === 'recruiter') {
      dataStore.recruiterProfiles.set(userId, {
        ...newUser,
        role: 'recruiter',
        company: 'Company Name', // Would be collected in signup form
      });
    }

    sessionStorage.setItem('currentUser', JSON.stringify(newUser));

    return {
      success: true,
      data: newUser,
      timestamp: new Date().toISOString(),
    };
  },

  async logout(): Promise<APIResponse<void>> {
    logger.info('API: Logout');
    sessionStorage.removeItem('currentUser');

    return {
      success: true,
      timestamp: new Date().toISOString(),
    };
  },

  getCurrentUser(): User | null {
    const userJson = sessionStorage.getItem('currentUser');
    return userJson ? JSON.parse(userJson) : null;
  },
};

/**
 * Resume API
 */
export const resumeAPI = {
  async upload(file: File, userId: string): Promise<APIResponse<Resume>> {
    logger.info('API: Uploading resume', { fileName: file.name, userId });

    try {
      // Process resume through ML pipeline
      const result = await processResume(file, userId);

      if (result.status === 'failed') {
        return {
          success: false,
          error: result.error || 'Failed to process resume',
          timestamp: new Date().toISOString(),
        };
      }

      // Create resume record
      const resume: Resume = {
        id: result.resumeId,
        userId,
        fileName: file.name,
        fileUrl: URL.createObjectURL(file),
        fileSize: file.size,
        uploadedAt: new Date(),
        extractedText: result.extractedText,
        extractedSkills: result.skills,
        education: result.education,
        experience: result.experience,
        embeddingVector: result.embedding,
        status: 'completed',
      };

      dataStore.resumes.set(resume.id, resume);

      logger.info('Resume uploaded successfully', { resumeId: resume.id });

      return {
        success: true,
        data: resume,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      logger.error('Resume upload failed', error as Error);
      return {
        success: false,
        error: 'Failed to upload resume',
        timestamp: new Date().toISOString(),
      };
    }
  },

  async getByUser(userId: string): Promise<APIResponse<Resume[]>> {
    logger.info('API: Getting resumes for user', { userId });
    await sleep(300);

    const resumes = getResumesByUser(userId);

    return {
      success: true,
      data: resumes,
      timestamp: new Date().toISOString(),
    };
  },

  async getById(resumeId: string): Promise<APIResponse<Resume>> {
    logger.info('API: Getting resume by ID', { resumeId });
    await sleep(200);

    const resume = dataStore.resumes.get(resumeId);

    if (!resume) {
      return {
        success: false,
        error: 'Resume not found',
        timestamp: new Date().toISOString(),
      };
    }

    return {
      success: true,
      data: resume,
      timestamp: new Date().toISOString(),
    };
  },

  async delete(resumeId: string): Promise<APIResponse<void>> {
    logger.info('API: Deleting resume', { resumeId });
    await sleep(200);

    dataStore.resumes.delete(resumeId);

    return {
      success: true,
      timestamp: new Date().toISOString(),
    };
  },
};

/**
 * Job API
 */
export const jobAPI = {
  async create(jobData: JobPostingForm, recruiterId: string): Promise<APIResponse<Job>> {
    logger.info('API: Creating job posting', { title: jobData.title });

    try {
      // Process job through ML pipeline
      const result = await processJobDescription({
        title: jobData.title,
        description: jobData.description,
        requiredSkills: jobData.requiredSkills,
      });

      if (result.status === 'failed') {
        return {
          success: false,
          error: result.error || 'Failed to process job',
          timestamp: new Date().toISOString(),
        };
      }

      // Create job record
      const job: Job = {
        id: result.jobId,
        recruiterId,
        title: jobData.title,
        company: jobData.company,
        description: jobData.description,
        requiredSkills: jobData.requiredSkills,
        preferredSkills: jobData.preferredSkills,
        experienceLevel: jobData.experienceLevel,
        location: jobData.location,
        locationType: jobData.locationType,
        salary: jobData.salaryMin && jobData.salaryMax ? {
          min: jobData.salaryMin,
          max: jobData.salaryMax,
          currency: jobData.salaryCurrency,
        } : undefined,
        postedAt: new Date(),
        status: 'active',
        embeddingVector: result.embedding,
      };

      dataStore.jobs.set(job.id, job);

      logger.info('Job created successfully', { jobId: job.id });

      return {
        success: true,
        data: job,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      logger.error('Job creation failed', error as Error);
      return {
        success: false,
        error: 'Failed to create job',
        timestamp: new Date().toISOString(),
      };
    }
  },

  async getByRecruiter(recruiterId: string): Promise<APIResponse<Job[]>> {
    logger.info('API: Getting jobs for recruiter', { recruiterId });
    await sleep(300);

    const jobs = getJobsByRecruiter(recruiterId);

    return {
      success: true,
      data: jobs,
      timestamp: new Date().toISOString(),
    };
  },

  async getAll(): Promise<APIResponse<Job[]>> {
    logger.info('API: Getting all jobs');
    await sleep(300);

    const jobs = getAllJobs();

    return {
      success: true,
      data: jobs,
      timestamp: new Date().toISOString(),
    };
  },

  async getById(jobId: string): Promise<APIResponse<Job>> {
    logger.info('API: Getting job by ID', { jobId });
    await sleep(200);

    const job = dataStore.jobs.get(jobId);

    if (!job) {
      return {
        success: false,
        error: 'Job not found',
        timestamp: new Date().toISOString(),
      };
    }

    return {
      success: true,
      data: job,
      timestamp: new Date().toISOString(),
    };
  },

  async update(jobId: string, updates: Partial<Job>): Promise<APIResponse<Job>> {
    logger.info('API: Updating job', { jobId });
    await sleep(300);

    const job = dataStore.jobs.get(jobId);

    if (!job) {
      return {
        success: false,
        error: 'Job not found',
        timestamp: new Date().toISOString(),
      };
    }

    const updatedJob = { ...job, ...updates, updatedAt: new Date() } as Job;
    dataStore.jobs.set(jobId, updatedJob);

    return {
      success: true,
      data: updatedJob,
      timestamp: new Date().toISOString(),
    };
  },

  async delete(jobId: string): Promise<APIResponse<void>> {
    logger.info('API: Deleting job', { jobId });
    await sleep(200);

    dataStore.jobs.delete(jobId);

    return {
      success: true,
      timestamp: new Date().toISOString(),
    };
  },
};

/**
 * Matching API
 */
export const matchAPI = {
  async matchResumeToJobs(resumeId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Matching resume to jobs', { resumeId });

    const resume = dataStore.resumes.get(resumeId);
    if (!resume) {
      return {
        success: false,
        error: 'Resume not found',
        timestamp: new Date().toISOString(),
      };
    }

    const allJobs = getAllJobs();
    const matchResults = await executeResumeMatching(resume, allJobs);

    // Convert match results to Match objects
    const matches: Match[] = matchResults.map(result => ({
      id: generateId(),
      resumeId: result.resumeId,
      jobId: result.jobId,
      studentId: result.studentId,
      recruiterId: result.recruiterId,
      overallScore: result.overallScore,
      skillScore: result.skillScore,
      experienceScore: result.experienceScore,
      semanticScore: result.semanticScore,
      matchedSkills: result.matchedSkills,
      missingSkills: result.missingSkills,
      explanation: result.explanation,
      createdAt: new Date(),
      status: 'pending',
    }));

    // Store matches
    matches.forEach(match => dataStore.matches.set(match.id, match));

    return {
      success: true,
      data: matches,
      timestamp: new Date().toISOString(),
    };
  },

  async matchJobToCandidates(jobId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Matching job to candidates', { jobId });

    const job = dataStore.jobs.get(jobId);
    if (!job) {
      return {
        success: false,
        error: 'Job not found',
        timestamp: new Date().toISOString(),
      };
    }

    const allResumes = getAllResumes();
    const matchResults = await executeJobMatching(job, allResumes);

    // Convert match results to Match objects
    const matches: Match[] = matchResults.map(result => ({
      id: generateId(),
      resumeId: result.resumeId,
      jobId: result.jobId,
      studentId: result.studentId,
      recruiterId: result.recruiterId,
      overallScore: result.overallScore,
      skillScore: result.skillScore,
      experienceScore: result.experienceScore,
      semanticScore: result.semanticScore,
      matchedSkills: result.matchedSkills,
      missingSkills: result.missingSkills,
      explanation: result.explanation,
      createdAt: new Date(),
      status: 'pending',
    }));

    // Store matches
    matches.forEach(match => dataStore.matches.set(match.id, match));

    return {
      success: true,
      data: matches,
      timestamp: new Date().toISOString(),
    };
  },

  async getMatchesByStudent(studentId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Getting matches for student', { studentId });
    await sleep(300);

    const matches = getMatchesByStudent(studentId);

    return {
      success: true,
      data: matches,
      timestamp: new Date().toISOString(),
    };
  },

  async getMatchesByRecruiter(recruiterId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Getting matches for recruiter', { recruiterId });
    await sleep(300);

    const matches = getMatchesByRecruiter(recruiterId);

    return {
      success: true,
      data: matches,
      timestamp: new Date().toISOString(),
    };
  },

  async getMatchesByJob(jobId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Getting matches for job', { jobId });
    await sleep(300);

    const matches = getMatchesByJob(jobId);

    return {
      success: true,
      data: matches,
      timestamp: new Date().toISOString(),
    };
  },

  async updateMatchStatus(matchId: string, status: Match['status']): Promise<APIResponse<Match>> {
    logger.info('API: Updating match status', { matchId, status });
    await sleep(200);

    const match = dataStore.matches.get(matchId);

    if (!match) {
      return {
        success: false,
        error: 'Match not found',
        timestamp: new Date().toISOString(),
      };
    }

    match.status = status;
    dataStore.matches.set(matchId, match);

    return {
      success: true,
      data: match,
      timestamp: new Date().toISOString(),
    };
  },
};
