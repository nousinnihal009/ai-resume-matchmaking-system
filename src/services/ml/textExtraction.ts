/**
 * Resume Text Extraction Service
 * Simulates text extraction from PDF/DOCX files
 * In production, this would use libraries like pdf-parse or mammoth.js
 */

import { logger } from '@/utils/logger';

export interface ExtractedContent {
  text: string;
  metadata: {
    pageCount?: number;
    wordCount: number;
    characterCount: number;
  };
}

/**
 * Extract text from uploaded resume file
 * This is a simulation - in production, use proper PDF/DOCX parsers
 */
export async function extractTextFromFile(file: File): Promise<ExtractedContent> {
  logger.info('Extracting text from file', { fileName: file.name, fileSize: file.size });

  try {
    // Simulate async processing
    await new Promise(resolve => setTimeout(resolve, 1000));

    // In production, you would use:
    // - pdf-parse for PDFs
    // - mammoth.js for DOCX files
    // For demo purposes, we return a simulated extraction

    const simulatedText = await readFileAsText(file);
    const wordCount = simulatedText.split(/\s+/).length;
    const characterCount = simulatedText.length;

    logger.info('Text extraction completed', {
      wordCount,
      characterCount,
    });

    return {
      text: simulatedText,
      metadata: {
        wordCount,
        characterCount,
      },
    };
  } catch (error) {
    logger.error('Text extraction failed', error as Error, { fileName: file.name });
    throw new Error('Failed to extract text from file');
  }
}

/**
 * Read file as text (for demo purposes)
 */
function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      resolve(text || generateSampleResumeText(file.name));
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    
    // For binary files, we'll just generate sample text
    // In production, use proper parsers
    reader.readAsText(file);
  });
}

/**
 * Generate sample resume text for demonstration
 */
function generateSampleResumeText(fileName: string): string {
  return `
JOHN DOE
Software Engineer
john.doe@email.com | +1-555-0123 | linkedin.com/in/johndoe

SUMMARY
Passionate software engineer with 3 years of experience in full-stack development.
Strong background in React, Node.js, Python, and cloud technologies.
Proven track record of delivering scalable web applications.

EDUCATION
Bachelor of Science in Computer Science
Massachusetts Institute of Technology (MIT)
Graduated: May 2022 | GPA: 3.8/4.0

EXPERIENCE
Software Engineer Intern | Google Inc.
June 2021 - August 2021
- Developed features for Google Cloud Platform using Python and Go
- Implemented microservices architecture with Kubernetes
- Collaborated with team of 5 engineers on distributed systems
- Technologies: Python, Go, Kubernetes, Docker, gRPC

Full Stack Developer Intern | Microsoft
June 2020 - August 2020
- Built web applications using React and TypeScript
- Developed RESTful APIs with Node.js and Express
- Implemented authentication with Azure Active Directory
- Technologies: React, TypeScript, Node.js, Azure, MongoDB

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, C++, Go
Web Technologies: React, Node.js, Express, Next.js, HTML, CSS
Databases: PostgreSQL, MongoDB, Redis, MySQL
Cloud & DevOps: AWS, Azure, Docker, Kubernetes, CI/CD, Git
Machine Learning: TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy

PROJECTS
AI Resume Matcher | Personal Project
- Built full-stack application with React and FastAPI
- Implemented ML pipeline for semantic matching using embeddings
- Used PostgreSQL with vector extensions for similarity search

E-Commerce Platform | Team Project
- Developed scalable e-commerce platform with microservices
- Integrated payment processing with Stripe
- Implemented real-time inventory management

CERTIFICATIONS
- AWS Certified Solutions Architect - Associate
- Google Cloud Professional Developer
- MongoDB Certified Developer

ACHIEVEMENTS
- Dean's List (2019-2022)
- Hackathon Winner - MIT TechX 2021
- Published research paper on distributed systems
  `.trim();
}

/**
 * Extract structured data from resume text
 */
export interface StructuredResume {
  name?: string;
  email?: string;
  phone?: string;
  summary?: string;
  education: Array<{
    institution: string;
    degree: string;
    field: string;
    year?: string;
  }>;
  experience: Array<{
    company: string;
    position: string;
    duration?: string;
    description: string;
  }>;
}

export function parseStructuredData(text: string): StructuredResume {
  logger.debug('Parsing structured data from text');

  // Simple regex-based extraction (in production, use proper NER models)
  const emailMatch = text.match(/[\w.-]+@[\w.-]+\.\w+/);
  const phoneMatch = text.match(/\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
  
  // Extract name (first line typically)
  const lines = text.split('\n').filter(l => l.trim());
  const name = lines[0]?.trim();

  // Extract sections (simplified)
  const summaryMatch = text.match(/SUMMARY\s+([\s\S]+?)(?=\n\n[A-Z]|$)/i);
  
  return {
    name,
    email: emailMatch?.[0],
    phone: phoneMatch?.[0],
    summary: summaryMatch?.[1]?.trim(),
    education: [],
    experience: [],
  };
}
