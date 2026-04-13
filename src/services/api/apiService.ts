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
  ResumeAnalysisReport,
  TailoringReport,
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
        ...getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        window.dispatchEvent(new Event('auth:unauthorized'));
      }
      let errorMsg = data.error || data.detail;
      if (typeof errorMsg !== 'string' && errorMsg) {
        errorMsg = Array.isArray(errorMsg) ? errorMsg[0]?.msg : JSON.stringify(errorMsg);
      }
      
      return {
        success: false,
        error: errorMsg || `HTTP ${response.status}: ${response.statusText}`,
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
      // Store token in localStorage
      localStorage.setItem('access_token', response.data.accessToken);
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
      // Store token in localStorage
      localStorage.setItem('access_token', response.data.accessToken);
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
        if (response.status === 401) {
          window.dispatchEvent(new Event('auth:unauthorized'));
        }
        let errorMsg = data.error || data.detail;
        if (typeof errorMsg !== 'string' && errorMsg) {
          errorMsg = Array.isArray(errorMsg) ? errorMsg[0]?.msg : JSON.stringify(errorMsg);
        }

        return {
          success: false,
          error: errorMsg || `HTTP ${response.status}: ${response.statusText}`,
          timestamp: new Date().toISOString(),
        };
      }

      return {
        success: true,
        data: data.data?.resume || data.data,
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

import { AppConfig } from '@/config/app.config';

/**
 * Matching API
 */
export const matchAPI = {
  async matchResumeToJobs(resumeId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Matching resume to jobs', { resumeId });

    if (AppConfig.features.useMockApi) {
      logger.warn('Mock API active: skipping real resume match pipeline.', { resumeId });
      return {
        success: true,
        data: [],
        timestamp: new Date().toISOString(),
      };
    }

    return apiRequest<Match[]>(`/matches/resume/${resumeId}`, {
      method: 'POST',
    });
  },

  async matchJobToCandidates(jobId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Matching job to candidates', { jobId });

    if (AppConfig.features.useMockApi) {
      logger.warn('Mock API active: skipping real job match pipeline.', { jobId });
      return {
        success: true,
        data: [],
        timestamp: new Date().toISOString(),
      };
    }

    return apiRequest<Match[]>(`/matches/job/${jobId}`, {
      method: 'POST',
    });
  },

  async getMatchesByStudent(studentId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Getting matches for student', { studentId });
    return apiRequest<Match[]>(`/matches/student/${studentId}`);
  },

  async getMatchesByRecruiter(recruiterId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Getting matches for recruiter', { recruiterId });
    return apiRequest<Match[]>(`/matches/recruiter/${recruiterId}`);
  },

  async getMatchesByJob(jobId: string): Promise<APIResponse<Match[]>> {
    logger.info('API: Getting matches for job', { jobId });
    // Note: Depends on backend having a /matches/job/{job_id} GET endpoint or similar.
    // Testing suite showed GET /matches/job/{job_id} does exist.
    return apiRequest<Match[]>(`/matches/job/${jobId}`);
  },

  async updateMatchStatus(matchId: string, status: Match['status']): Promise<APIResponse<Match>> {
    logger.info('API: Updating match status', { matchId, status });
    return apiRequest<Match>(`/matches/${matchId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },
};

/**
 * Resume Analysis API
 */
export const resumeAnalysisAPI = {
  async runAnalysis(
    resumeId: string,
    forceRefresh = false,
  ): Promise<APIResponse<ResumeAnalysisReport>> {
    logger.info('API: Running resume analysis', { resumeId });
    return apiRequest<ResumeAnalysisReport>(
      `/resume-analysis/${resumeId}/analyze` +
      (forceRefresh ? '?force_refresh=true' : ''),
      { method: 'POST' }
    );
  },

  async getReport(
    resumeId: string,
  ): Promise<APIResponse<ResumeAnalysisReport>> {
    logger.info('API: Fetching analysis report', { resumeId });
    return apiRequest<ResumeAnalysisReport>(
      `/resume-analysis/${resumeId}/report`
    );
  },

  async tailorResume(
    resumeId: string,
    jobDescription: string,
  ): Promise<APIResponse<TailoringReport>> {
    logger.info('API: Tailoring resume', { resumeId });
    return apiRequest<TailoringReport>(
      `/resume-analysis/${resumeId}/tailor`,
      {
        method: 'POST',
        body: JSON.stringify({ job_description: jobDescription }),
      }
    );
  },
};
