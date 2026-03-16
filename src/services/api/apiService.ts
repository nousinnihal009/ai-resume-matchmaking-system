/**
 * API Service Layer
 * Real HTTP requests to FastAPI backend
 */

import { logger } from '@/utils/logger';
import type {
  User,
  AuthResponse,
  Resume,
  Job,
  Match,
  APIResponse,
  PaginatedResponse,
  LoginForm,
  SignupForm,
  JobPostingForm,
} from '@/types/models';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Generic API request helper
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<APIResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.error || `HTTP ${response.status}: ${response.statusText}`,
        timestamp: new Date().toISOString(),
      };
    }

    return {
      success: true,
      data: data.data,
      timestamp: data.timestamp || new Date().toISOString(),
    };
  } catch (error) {
    logger.error('API request failed', { endpoint, error });
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Get authorization header with JWT token
 */
function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Authentication API
 */
export const authAPI = {
  async login(credentials: LoginForm): Promise<APIResponse<AuthResponse>> {
    logger.info('API: Login attempt', { email: credentials.email });

    const response = await apiRequest<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    if (response.success && response.data) {
      // Store token from API response
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('current_user', JSON.stringify(response.data.user));
    }

    return response;
  },

  async signup(formData: SignupForm): Promise<APIResponse<AuthResponse>> {
    logger.info('API: Signup attempt', { email: formData.email });

    const response = await apiRequest<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(formData),
    });

    if (response.success && response.data) {
      // Store token from API response
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('current_user', JSON.stringify(response.data.user));
    }

    return response;
  },

  async logout(): Promise<APIResponse<void>> {
    logger.info('API: Logout');

    const response = await apiRequest<void>('/auth/logout', {
      method: 'POST',
      headers: getAuthHeaders(),
    });

    // Clear stored data
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');

    return response;
  },

  getCurrentUser(): User | null {
    const userJson = localStorage.getItem('current_user');
    return userJson ? JSON.parse(userJson) : null;
  },
};

/**
 * Resume API
 */
export const resumeAPI = {
  async upload(file: File, userId: string): Promise<APIResponse<Resume>> {
    logger.info('API: Uploading resume', { fileName: file.name, userId });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/resumes/upload`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || `HTTP ${response.status}: ${response.statusText}`,
          timestamp: new Date().toISOString(),
        };
      }

      return {
        success: true,
        data: data.data,
        timestamp: data.timestamp || new Date().toISOString(),
      };
    } catch (error) {
      logger.error('Resume upload failed', error as Error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed',
        timestamp: new Date().toISOString(),
      };
    }
  },

  async getByUser(userId: string): Promise<APIResponse<Resume[]>> {
    logger.info('API: Getting resumes for user', { userId });

    return apiRequest<Resume[]>(`/resumes/user/${userId}`, {
      headers: getAuthHeaders(),
    });
  },

  async getById(resumeId: string): Promise<APIResponse<Resume>> {
    logger.info('API: Getting resume by ID', { resumeId });

    return apiRequest<Resume>(`/resumes/${resumeId}`, {
      headers: getAuthHeaders(),
    });
  },

  async delete(resumeId: string): Promise<APIResponse<void>> {
    logger.info('API: Deleting resume', { resumeId });

    return apiRequest<void>(`/resumes/${resumeId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
  },
};

/**
 * Job API
 */
export const jobAPI = {
  async create(jobData: JobPostingForm, recruiterId: string): Promise<APIResponse<Job>> {
    logger.info('API: Creating job posting', { title: jobData.title });

    const payload = {
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
    };

    return apiRequest<Job>('/jobs', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
  },

  async getByRecruiter(recruiterId: string): Promise<APIResponse<Job[]>> {
    logger.info('API: Getting jobs for recruiter', { recruiterId });

    return apiRequest<Job[]>(`/jobs/recruiter/${recruiterId}`, {
      headers: getAuthHeaders(),
    });
  },

  async getAll(): Promise<APIResponse<Job[]>> {
    logger.info('API: Getting all jobs');

    return apiRequest<Job[]>('/jobs', {
      headers: getAuthHeaders(),
    });
  },

  async getById(jobId: string): Promise<APIResponse<Job>> {
    logger.info('API: Getting job by ID', { jobId });

    return apiRequest<Job>(`/jobs/${jobId}`, {
      headers: getAuthHeaders(),
    });
  },

  async update(jobId: string, updates: Partial<Job>): Promise<APIResponse<Job>> {
    logger.info('API: Updating job', { jobId });

    return apiRequest<Job>(`/jobs/${jobId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates),
    });
  },

  async delete(jobId: string): Promise<APIResponse<void>> {
    logger.info('API: Deleting job', { jobId });

    return apiRequest<void>(`/jobs/${jobId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
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
