/**
 * Custom Hooks for Data Management
 * React hooks for interacting with the API layer
 */

import { useState, useEffect, useCallback } from 'react';
import { resumeAPI, jobAPI, matchAPI } from '@/services/api/apiService';
import type { Resume, Job, Match, JobPostingForm } from '@/types/models';
import { logger } from '@/utils/logger';
import { toast } from 'sonner';

/**
 * Hook for resume management
 */
export function useResumes(userId?: string) {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResumes = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await resumeAPI.getByUser(userId);
      if (response.success && response.data) {
        setResumes(response.data);
      } else {
        setError(response.error || 'Failed to fetch resumes');
      }
    } catch (err) {
      logger.error('Error fetching resumes', err as Error);
      setError('An error occurred while fetching resumes');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const uploadResume = async (file: File) => {
    if (!userId) {
      toast.error('User not logged in');
      return { success: false };
    }

    setIsLoading(true);
    try {
      const response = await resumeAPI.upload(file, userId);
      
      if (response.success && response.data) {
        setResumes(prev => [response.data!, ...prev]);
        toast.success('Resume uploaded successfully!');
        return { success: true, data: response.data };
      } else {
        toast.error(response.error || 'Failed to upload resume');
        return { success: false };
      }
    } catch (err) {
      logger.error('Error uploading resume', err as Error);
      toast.error('An error occurred while uploading');
      return { success: false };
    } finally {
      setIsLoading(false);
    }
  };

  const deleteResume = async (resumeId: string) => {
    try {
      const response = await resumeAPI.delete(resumeId);
      
      if (response.success) {
        setResumes(prev => prev.filter(r => r.id !== resumeId));
        toast.success('Resume deleted');
        return { success: true };
      } else {
        toast.error(response.error || 'Failed to delete resume');
        return { success: false };
      }
    } catch (err) {
      logger.error('Error deleting resume', err as Error);
      toast.error('An error occurred');
      return { success: false };
    }
  };

  useEffect(() => {
    fetchResumes();
  }, [fetchResumes]);

  return {
    resumes,
    isLoading,
    error,
    uploadResume,
    deleteResume,
    refetch: fetchResumes,
  };
}

/**
 * Hook for job management
 */
export function useJobs(recruiterId?: string) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = recruiterId 
        ? await jobAPI.getByRecruiter(recruiterId)
        : await jobAPI.getAll();
        
      if (response.success && response.data) {
        setJobs(response.data);
      } else {
        setError(response.error || 'Failed to fetch jobs');
      }
    } catch (err) {
      logger.error('Error fetching jobs', err as Error);
      setError('An error occurred while fetching jobs');
    } finally {
      setIsLoading(false);
    }
  }, [recruiterId]);

  const createJob = async (jobData: JobPostingForm) => {
    if (!recruiterId) {
      toast.error('Recruiter not logged in');
      return { success: false };
    }

    setIsLoading(true);
    try {
      const response = await jobAPI.create(jobData, recruiterId);
      
      if (response.success && response.data) {
        setJobs(prev => [response.data!, ...prev]);
        toast.success('Job posted successfully!');
        return { success: true, data: response.data };
      } else {
        toast.error(response.error || 'Failed to create job');
        return { success: false };
      }
    } catch (err) {
      logger.error('Error creating job', err as Error);
      toast.error('An error occurred');
      return { success: false };
    } finally {
      setIsLoading(false);
    }
  };

  const updateJob = async (jobId: string, updates: Partial<Job>) => {
    try {
      const response = await jobAPI.update(jobId, updates);
      
      if (response.success && response.data) {
        setJobs(prev => prev.map(j => j.id === jobId ? response.data! : j));
        toast.success('Job updated');
        return { success: true };
      } else {
        toast.error(response.error || 'Failed to update job');
        return { success: false };
      }
    } catch (err) {
      logger.error('Error updating job', err as Error);
      toast.error('An error occurred');
      return { success: false };
    }
  };

  const deleteJob = async (jobId: string) => {
    try {
      const response = await jobAPI.delete(jobId);
      
      if (response.success) {
        setJobs(prev => prev.filter(j => j.id !== jobId));
        toast.success('Job deleted');
        return { success: true };
      } else {
        toast.error(response.error || 'Failed to delete job');
        return { success: false };
      }
    } catch (err) {
      logger.error('Error deleting job', err as Error);
      toast.error('An error occurred');
      return { success: false };
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return {
    jobs,
    isLoading,
    error,
    createJob,
    updateJob,
    deleteJob,
    refetch: fetchJobs,
  };
}

/**
 * Hook for match management
 */
export function useMatches(userId?: string, userRole?: 'student' | 'recruiter') {
  const [matches, setMatches] = useState<Match[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMatches = useCallback(async () => {
    if (!userId || !userRole) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = userRole === 'student'
        ? await matchAPI.getMatchesByStudent(userId)
        : await matchAPI.getMatchesByRecruiter(userId);
        
      if (response.success && response.data) {
        setMatches(response.data);
      } else {
        setError(response.error || 'Failed to fetch matches');
      }
    } catch (err) {
      logger.error('Error fetching matches', err as Error);
      setError('An error occurred while fetching matches');
    } finally {
      setIsLoading(false);
    }
  }, [userId, userRole]);

  const matchResume = async (resumeId: string) => {
    setIsLoading(true);
    try {
      const response = await matchAPI.matchResumeToJobs(resumeId);
      
      if (response.success && response.data) {
        setMatches(response.data);
        toast.success(`Found ${response.data.length} matching opportunities!`);
        return { success: true, data: response.data };
      } else {
        toast.error(response.error || 'Failed to find matches');
        return { success: false };
      }
    } catch (err) {
      logger.error('Error matching resume', err as Error);
      toast.error('An error occurred');
      return { success: false };
    } finally {
      setIsLoading(false);
    }
  };

  const matchJob = async (jobId: string) => {
    setIsLoading(true);
    try {
      const response = await matchAPI.matchJobToCandidates(jobId);
      
      if (response.success && response.data) {
        setMatches(response.data);
        toast.success(`Found ${response.data.length} matching candidates!`);
        return { success: true, data: response.data };
      } else {
        toast.error(response.error || 'Failed to find matches');
        return { success: false };
      }
    } catch (err) {
      logger.error('Error matching job', err as Error);
      toast.error('An error occurred');
      return { success: false };
    } finally {
      setIsLoading(false);
    }
  };

  const updateMatchStatus = async (matchId: string, status: Match['status']) => {
    try {
      const response = await matchAPI.updateMatchStatus(matchId, status);
      
      if (response.success && response.data) {
        setMatches(prev => prev.map(m => m.id === matchId ? response.data! : m));
        return { success: true };
      } else {
        toast.error(response.error || 'Failed to update status');
        return { success: false };
      }
    } catch (err) {
      logger.error('Error updating match status', err as Error);
      return { success: false };
    }
  };

  useEffect(() => {
    fetchMatches();
  }, [fetchMatches]);

  return {
    matches,
    isLoading,
    error,
    matchResume,
    matchJob,
    updateMatchStatus,
    refetch: fetchMatches,
  };
}
