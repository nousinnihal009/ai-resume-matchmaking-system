/**
 * MOCK DATA — FOR LOCAL DEVELOPMENT ONLY
 *
 * This file is only active when VITE_USE_MOCK=true in your .env file.
 * It is NOT used in production. All live data flows through apiService.ts
 * which calls the FastAPI backend at VITE_API_BASE_URL.
 *
 * To disable mock mode: set VITE_USE_MOCK=false (default)
 * To enable mock mode:  set VITE_USE_MOCK=true
 */
import type {
  User,
  StudentProfile,
  RecruiterProfile,
  Resume,
  Job,
  Match,
} from '@/types/models';
import { generateId } from '@/utils/helpers';

// In-memory stores
export const dataStore = {
  users: new Map<string, User>(),
  studentProfiles: new Map<string, StudentProfile>(),
  recruiterProfiles: new Map<string, RecruiterProfile>(),
  resumes: new Map<string, Resume>(),
  jobs: new Map<string, Job>(),
  matches: new Map<string, Match>(),
};

// Initialize with sample data
export function initializeSampleData(): void {
  // Sample Students
  const student1Id = generateId();
  const student1: StudentProfile = {
    id: student1Id,
    email: 'john.doe@university.edu',
    name: 'John Doe',
    role: 'student',
    university: 'Massachusetts Institute of Technology',
    major: 'Computer Science',
    graduationYear: 2025,
    phoneNumber: '+1-555-0123',
    linkedinUrl: 'https://linkedin.com/in/johndoe',
    githubUrl: 'https://github.com/johndoe',
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-01-15'),
  };

  const student2Id = generateId();
  const student2: StudentProfile = {
    id: student2Id,
    email: 'sarah.smith@stanford.edu',
    name: 'Sarah Smith',
    role: 'student',
    university: 'Stanford University',
    major: 'Data Science',
    graduationYear: 2024,
    phoneNumber: '+1-555-0124',
    linkedinUrl: 'https://linkedin.com/in/sarahsmith',
    createdAt: new Date('2024-02-01'),
    updatedAt: new Date('2024-02-01'),
  };

  dataStore.users.set(student1Id, student1);
  dataStore.users.set(student2Id, student2);
  dataStore.studentProfiles.set(student1Id, student1);
  dataStore.studentProfiles.set(student2Id, student2);

  // Sample Recruiters
  const recruiter1Id = generateId();
  const recruiter1: RecruiterProfile = {
    id: recruiter1Id,
    email: 'jane.recruiter@google.com',
    name: 'Jane Wilson',
    role: 'recruiter',
    company: 'Google Inc.',
    position: 'Senior Technical Recruiter',
    phoneNumber: '+1-555-0200',
    linkedinUrl: 'https://linkedin.com/in/janewilson',
    createdAt: new Date('2023-06-10'),
    updatedAt: new Date('2023-06-10'),
  };

  const recruiter2Id = generateId();
  const recruiter2: RecruiterProfile = {
    id: recruiter2Id,
    email: 'mike.hr@microsoft.com',
    name: 'Mike Johnson',
    role: 'recruiter',
    company: 'Microsoft Corporation',
    position: 'Campus Recruiter',
    phoneNumber: '+1-555-0201',
    linkedinUrl: 'https://linkedin.com/in/mikejohnson',
    createdAt: new Date('2023-08-15'),
    updatedAt: new Date('2023-08-15'),
  };

  dataStore.users.set(recruiter1Id, recruiter1);
  dataStore.users.set(recruiter2Id, recruiter2);
  dataStore.recruiterProfiles.set(recruiter1Id, recruiter1);
  dataStore.recruiterProfiles.set(recruiter2Id, recruiter2);

  // Sample Jobs
  const job1Id = generateId();
  const job1: Job = {
    id: job1Id,
    recruiterId: recruiter1Id,
    title: 'Software Engineering Intern',
    company: 'Google Inc.',
    description: `We're looking for talented software engineering interns to join our team. You'll work on real products used by billions of users worldwide.

Responsibilities:
- Design and implement features for Google Cloud Platform
- Collaborate with engineers on distributed systems
- Write clean, maintainable code
- Participate in code reviews and design discussions

What we're looking for:
- Currently pursuing a degree in Computer Science or related field
- Strong programming skills in Python, Java, or C++
- Experience with data structures and algorithms
- Knowledge of cloud technologies is a plus`,
    requiredSkills: ['Python', 'Java', 'Data Structures', 'Algorithms', 'Problem Solving'],
    preferredSkills: ['C++', 'Distributed Systems', 'Cloud Computing', 'Docker', 'Kubernetes'],
    experienceLevel: 'internship',
    location: 'Mountain View, CA',
    locationType: 'hybrid',
    salary: { min: 7000, max: 9000, currency: 'USD' },
    postedAt: new Date('2025-01-20'),
    expiresAt: new Date('2025-03-20'),
    status: 'active',
  };

  const job2Id = generateId();
  const job2: Job = {
    id: job2Id,
    recruiterId: recruiter2Id,
    title: 'ML Engineering Intern',
    company: 'Microsoft Corporation',
    description: `Join Microsoft's AI team as a Machine Learning Engineering Intern. Work on cutting-edge AI projects and learn from world-class researchers.

Responsibilities:
- Develop machine learning models for production systems
- Conduct experiments and analyze results
- Implement data pipelines for model training
- Collaborate with researchers and engineers

Requirements:
- Studying Computer Science, Machine Learning, or related field
- Strong programming skills in Python
- Experience with ML frameworks (TensorFlow, PyTorch)
- Understanding of machine learning fundamentals`,
    requiredSkills: ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Data Analysis'],
    preferredSkills: ['NLP', 'Computer Vision', 'Deep Learning', 'Azure', 'MLOps'],
    experienceLevel: 'internship',
    location: 'Redmond, WA',
    locationType: 'onsite',
    salary: { min: 6500, max: 8500, currency: 'USD' },
    postedAt: new Date('2025-01-25'),
    expiresAt: new Date('2025-04-01'),
    status: 'active',
  };

  const job3Id = generateId();
  const job3: Job = {
    id: job3Id,
    recruiterId: recruiter1Id,
    title: 'Full Stack Developer Intern',
    company: 'Google Inc.',
    description: `Build amazing web applications as a Full Stack Developer Intern at Google. Work with modern technologies and ship features to millions of users.

What you'll do:
- Develop frontend and backend features
- Work with React, TypeScript, and Node.js
- Design and implement RESTful APIs
- Write tests and maintain code quality

We're looking for:
- Experience with web development
- Knowledge of React and modern JavaScript
- Understanding of backend technologies
- Passion for building great user experiences`,
    requiredSkills: ['React', 'JavaScript', 'TypeScript', 'Node.js', 'HTML', 'CSS'],
    preferredSkills: ['Next.js', 'GraphQL', 'PostgreSQL', 'AWS', 'Docker'],
    experienceLevel: 'internship',
    location: 'San Francisco, CA',
    locationType: 'remote',
    salary: { min: 7500, max: 9500, currency: 'USD' },
    postedAt: new Date('2025-01-28'),
    status: 'active',
  };

  dataStore.jobs.set(job1Id, job1);
  dataStore.jobs.set(job2Id, job2);
  dataStore.jobs.set(job3Id, job3);

  console.log('Sample data initialized:', {
    users: dataStore.users.size,
    jobs: dataStore.jobs.size,
  });
}

// Initialize sample data on module load
initializeSampleData();

/**
 * Helper functions for data access
 */
export function getAllUsers(): User[] {
  return Array.from(dataStore.users.values());
}

export function getAllJobs(): Job[] {
  return Array.from(dataStore.jobs.values());
}

export function getAllResumes(): Resume[] {
  return Array.from(dataStore.resumes.values());
}

export function getAllMatches(): Match[] {
  return Array.from(dataStore.matches.values());
}

export function getJobsByRecruiter(recruiterId: string): Job[] {
  return Array.from(dataStore.jobs.values()).filter(job => job.recruiterId === recruiterId);
}

export function getResumesByUser(userId: string): Resume[] {
  return Array.from(dataStore.resumes.values()).filter(resume => resume.userId === userId);
}

export function getMatchesByStudent(studentId: string): Match[] {
  return Array.from(dataStore.matches.values()).filter(match => match.studentId === studentId);
}

export function getMatchesByRecruiter(recruiterId: string): Match[] {
  return Array.from(dataStore.matches.values()).filter(match => match.recruiterId === recruiterId);
}

export function getMatchesByJob(jobId: string): Match[] {
  return Array.from(dataStore.matches.values()).filter(match => match.jobId === jobId);
}
