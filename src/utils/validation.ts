/**
 * Validation Utilities
 * Input validation and sanitization functions
 */

import { AppConfig } from '@/config/app.config';

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Email validation
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Password validation - at least 8 chars, 1 uppercase, 1 lowercase, 1 number
 */
export function validatePassword(password: string): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * File validation for resume uploads
 */
export function validateResumeFile(file: File): {
  isValid: boolean;
  error?: string;
} {
  // Check file size
  if (file.size > AppConfig.upload.maxFileSize) {
    return {
      isValid: false,
      error: `File size exceeds ${AppConfig.upload.maxFileSize / (1024 * 1024)}MB limit`,
    };
  }

  // Check file type
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!AppConfig.upload.allowedFormats.includes(fileExtension)) {
    return {
      isValid: false,
      error: `Invalid file format. Allowed formats: ${AppConfig.upload.allowedFormats.join(', ')}`,
    };
  }

  // Check MIME type
  if (!AppConfig.upload.allowedMimeTypes.includes(file.type)) {
    return {
      isValid: false,
      error: 'Invalid file type',
    };
  }

  return { isValid: true };
}

/**
 * Sanitize user input to prevent XSS
 */
export function sanitizeInput(input: string): string {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

/**
 * Validate skill tags
 */
export function validateSkills(skills: string[]): {
  isValid: boolean;
  error?: string;
} {
  if (skills.length === 0) {
    return {
      isValid: false,
      error: 'At least one skill is required',
    };
  }

  if (skills.length > 50) {
    return {
      isValid: false,
      error: 'Maximum 50 skills allowed',
    };
  }

  for (const skill of skills) {
    if (skill.length > 50) {
      return {
        isValid: false,
        error: 'Skill name cannot exceed 50 characters',
      };
    }
  }

  return { isValid: true };
}

/**
 * Validate URL
 */
export function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate phone number (basic validation)
 */
export function validatePhoneNumber(phone: string): boolean {
  const phoneRegex = /^\+?[\d\s\-()]+$/;
  return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
}
