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
  accessToken: string;
  tokenType: string;
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

// ==================== Resume Analysis Types ====================

export interface RepetitionIssue {
  word: string;
  count: number;
  severity: 'high' | 'medium';
  suggestions: string[];
}

export interface SpellingError {
  word: string;
  suggestion: string;
  context: string;
}

export interface GrammarError {
  issue: string;
  original: string;
  suggestion: string;
}

export interface ContactField {
  present: boolean;
  masked?: string;
  value?: string;
}

export interface ScoreCategory {
  score: number;
  weight: number;
  note?: string;
}

export interface BulletRewrite {
  original: string;
  rewritten: string;
  reason: string;
}

export interface TemplateSuggestion {
  name: string;
  description: string;
  best_for: string;
  ats_friendly: boolean;
}

export interface ResumeAnalysisReport {
  overall_score: number;
  total_issues: number;
  score_breakdown: Record<string, ScoreCategory>;
  content: {
    score: number;
    ats_parse_rate: number;
    ats_parse_status: string;
    quantification: {
      quantified_achievements: string[];
      unquantified_bullets: string[];
      quantification_rate: number;
      has_impact_metrics: boolean;
      suggestion: string | null;
    };
    repetition: {
      issues: RepetitionIssue[];
      issue_count: number;
      has_issues: boolean;
    };
    spelling_grammar: {
      spelling_errors: SpellingError[];
      grammar_errors: GrammarError[];
      overall_quality: string;
      language_feedback: string;
      source: string;
    };
    content_quality: {
      strengths: string[];
      weaknesses: string[];
      action_verb_quality: string;
      specificity_score: number;
      professional_tone_score: number;
      suggestions: string[];
      source: string;
    };
  };
  sections: {
    present: string[];
    missing: string[];
    essential_present: string[];
    optional_present: string[];
  };
  ats_essentials: {
    score: number;
    file_analysis: {
      format: string;
      size_kb: number;
      size_mb: number;
      format_score: number;
      ats_compatible: boolean;
      size_acceptable: boolean;
      issues: string[];
      recommendation: string;
    };
    contact_info: {
      found: Record<string, ContactField>;
      missing: string[];
      completeness_score: number;
    };
  };
  design: {
    score: number;
    feedback: string[];
    template_suggestions: TemplateSuggestion[];
    layout_detected: string;
  };
  skills_analysis: {
    score: number;
    density: number;
  };
  analyzer_version: string;
  analyzed_at: string;
}

export interface TailoringReport {
  tailoring_score: number;
  missing_keywords: string[];
  keywords_present: string[];
  bullet_rewrites: BulletRewrite[];
  sections_to_add: string[];
  skills_to_highlight: string[];
  summary_rewrite: string;
  overall_fit: string;
  fit_explanation: string;
  top_3_gaps: string[];
  source: string;
  analyzed_at: string;
}
