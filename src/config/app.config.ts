/**
 * Application Configuration
 * Centralized configuration management for the AI Resume Matching Platform
 */

export const AppConfig = {
  // Application Metadata
  app: {
    name: 'AI Resume Matcher',
    version: '1.0.0',
    environment: import.meta.env.MODE || 'development',
  },

  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 30000, // 30 seconds
    retryAttempts: 3,
  },

  // ML Pipeline Configuration
  ml: {
    embeddingDimension: 384, // Typical for sentence transformers
    similarityThreshold: 0.6,
    topK: 10, // Top K matches to return
    skillWeightage: 0.4,
    experienceWeightage: 0.3,
    semanticWeightage: 0.3,
  },

  // File Upload Configuration
  upload: {
    maxFileSize: 5 * 1024 * 1024, // 5MB
    allowedFormats: ['.pdf', '.docx', '.doc'],
    allowedMimeTypes: [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ],
  },

  // Pagination Configuration
  pagination: {
    defaultPageSize: 10,
    maxPageSize: 100,
  },

  // Feature Flags
  features: {
    enableRealtimeMatching: true,
    enableSkillExtraction: true,
    enableMatchExplanation: true,
    enableAnalytics: true,
  },

  // User Roles
  roles: {
    STUDENT: 'student',
    RECRUITER: 'recruiter',
    ADMIN: 'admin',
  },

  // Match Score Thresholds
  matchThresholds: {
    excellent: 0.85,
    good: 0.70,
    fair: 0.55,
    poor: 0.40,
  },
} as const;

// Type exports for TypeScript support
export type UserRole = (typeof AppConfig.roles)[keyof typeof AppConfig.roles];
export type Environment = 'development' | 'staging' | 'production';
