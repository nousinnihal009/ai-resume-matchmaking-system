/**
 * Data Models and TypeScript Interfaces
 * Type definitions for the entire application
 */

// ==================== User Models ====================

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'recruiter' | 'admin';
  createdAt: Date;
  updatedAt: Date;
}

export interface StudentProfile extends User {
  role: 'student';
  university?: string;
  major?: string;
  graduationYear?: number;
  phoneNumber?: string;
  linkedinUrl?: string;
  githubUrl?: string;
}

export interface RecruiterProfile extends User {
  role: 'recruiter';
  company: string;
  position?: string;
  phoneNumber?: string;
  linkedinUrl?: string;
}

// ==================== Auth Response ====================

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

// ==================== Resume Models ====================

export interface Resume {
  id: string;
  userId: string;
  fileName: string;
  fileUrl: string;
  fileSize: number;
  uploadedAt: Date;
  extractedText: string;
  extractedSkills: string[];
  education: Education[];
  experience: Experience[];
  embeddingVector?: number[];
  status: 'processing' | 'completed' | 'failed';
  metadata?: Record<string, any>;
}

export interface Education {
  institution: string;
  degree: string;
  fieldOfStudy: string;
  startDate?: string;
  endDate?: string;
  grade?: string;
}

export interface Experience {
  company: string;
  position: string;
  description: string;
  startDate?: string;
  endDate?: string;
  skills?: string[];
}

// ==================== Job Models ====================

export interface Job {
  id: string;
  recruiterId: string;
  title: string;
  company: string;
  description: string;
  requiredSkills: string[];
  preferredSkills: string[];
  experienceLevel: 'internship' | 'entry' | 'mid' | 'senior';
  location: string;
  locationType: 'onsite' | 'remote' | 'hybrid';
  salary?: {
    min?: number;
    max?: number;
    currency: string;
  };
  postedAt: Date;
  expiresAt?: Date;
  status: 'active' | 'closed' | 'draft';
  embeddingVector?: number[];
  metadata?: Record<string, any>;
}

// ==================== Match Models ====================

export interface Match {
  id: string;
  resumeId: string;
  jobId: string;
  studentId: string;
  recruiterId: string;
  overallScore: number;
  skillScore: number;
  experienceScore: number;
  semanticScore: number;
  matchedSkills: string[];
  missingSkills: string[];
  explanation: MatchExplanation;
  createdAt: Date;
  status: 'pending' | 'viewed' | 'shortlisted' | 'rejected';
}

export interface MatchExplanation {
  summary: string;
  strengths: string[];
  gaps: string[];
  recommendations: string[];
  skillBreakdown: {
    matched: string[];
    missing: string[];
    additional: string[];
  };
}

// ==================== ML Pipeline Models ====================

export interface EmbeddingVector {
  id: string;
  entityId: string; // resumeId or jobId
  entityType: 'resume' | 'job';
  vector: number[];
  dimension: number;
  createdAt: Date;
}

export interface SkillExtraction {
  text: string;
  extractedSkills: string[];
  confidence: number;
  categories: {
    technical: string[];
    soft: string[];
    domain: string[];
  };
}

export interface SimilarityScore {
  resumeId: string;
  jobId: string;
  cosineSimilarity: number;
  euclideanDistance: number;
  dotProduct: number;
}

// ==================== API Response Models ====================

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ==================== Form Models ====================

export interface LoginForm {
  email: string;
  password: string;
  role: 'student' | 'recruiter';
}

export interface SignupForm extends LoginForm {
  name: string;
  confirmPassword: string;
}

export interface JobPostingForm {
  title: string;
  company: string;
  description: string;
  requiredSkills: string[];
  preferredSkills: string[];
  experienceLevel: Job['experienceLevel'];
  location: string;
  locationType: Job['locationType'];
  salaryMin?: number;
  salaryMax?: number;
  salaryCurrency: string;
}

// ==================== Analytics Models ====================

export interface MatchAnalytics {
  totalMatches: number;
  averageScore: number;
  scoreDistribution: {
    excellent: number;
    good: number;
    fair: number;
    poor: number;
  };
  topSkills: Array<{
    skill: string;
    frequency: number;
  }>;
}

export interface RecruiterDashboardStats {
  activeJobs: number;
  totalCandidates: number;
  shortlistedCandidates: number;
  averageMatchScore: number;
}

export interface StudentDashboardStats {
  resumesUploaded: number;
  matchesFound: number;
  averageScore: number;
  topMatchedRoles: string[];
}

// ==================== Filter and Sort Models ====================

export interface MatchFilters {
  minScore?: number;
  maxScore?: number;
  skills?: string[];
  experienceLevel?: string[];
  location?: string[];
  status?: Match['status'][];
}

export interface SortOptions {
  field: 'score' | 'date' | 'name' | 'company';
  order: 'asc' | 'desc';
}
