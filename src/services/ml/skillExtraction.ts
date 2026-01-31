/**
 * Skill Extraction Service
 * Extracts technical and soft skills from text using pattern matching and NLP
 */

import { logger } from '@/utils/logger';

// Comprehensive skill taxonomy
const SKILL_TAXONOMY = {
  programming: [
    'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust',
    'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl',
  ],
  webFrontend: [
    'React', 'Angular', 'Vue.js', 'Next.js', 'Nuxt.js', 'Svelte', 'Redux',
    'HTML', 'CSS', 'SASS', 'LESS', 'Tailwind', 'Bootstrap', 'Material-UI',
    'Webpack', 'Vite', 'jQuery',
  ],
  webBackend: [
    'Node.js', 'Express', 'FastAPI', 'Django', 'Flask', 'Spring Boot',
    'ASP.NET', 'Ruby on Rails', 'Laravel', 'Nest.js', 'GraphQL', 'REST API',
  ],
  databases: [
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Cassandra', 'DynamoDB',
    'Oracle', 'SQL Server', 'SQLite', 'Elasticsearch', 'Neo4j', 'Firebase',
  ],
  cloudDevOps: [
    'AWS', 'Azure', 'Google Cloud', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
    'GitLab CI', 'GitHub Actions', 'Terraform', 'Ansible', 'CircleCI',
    'Travis CI', 'Heroku', 'Vercel', 'Netlify',
  ],
  dataScience: [
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
    'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Jupyter',
    'Data Analysis', 'Statistics', 'Neural Networks', 'NLP', 'Computer Vision',
  ],
  mobile: [
    'React Native', 'Flutter', 'iOS', 'Android', 'Swift', 'Kotlin',
    'Xamarin', 'Ionic', 'SwiftUI', 'Jetpack Compose',
  ],
  tools: [
    'Git', 'GitHub', 'GitLab', 'Bitbucket', 'JIRA', 'Confluence', 'Slack',
    'VS Code', 'IntelliJ', 'Eclipse', 'Postman', 'Figma', 'Adobe XD',
  ],
  softSkills: [
    'Leadership', 'Communication', 'Team Collaboration', 'Problem Solving',
    'Critical Thinking', 'Project Management', 'Agile', 'Scrum', 'Kanban',
    'Time Management', 'Public Speaking', 'Mentoring', 'Documentation',
  ],
  security: [
    'Cybersecurity', 'OAuth', 'JWT', 'Encryption', 'SSL/TLS', 'Penetration Testing',
    'OWASP', 'Security Auditing', 'Firewall', 'VPN',
  ],
  other: [
    'Blockchain', 'Solidity', 'Ethereum', 'Microservices', 'System Design',
    'API Design', 'Testing', 'Unit Testing', 'Integration Testing', 'CI/CD',
    'Version Control', 'Code Review', 'Design Patterns', 'OOP', 'Functional Programming',
  ],
};

// Flatten all skills into a single array
const ALL_SKILLS = Object.values(SKILL_TAXONOMY).flat();

// Create skill variations (e.g., "react.js" -> "React", "nodejs" -> "Node.js")
const SKILL_VARIATIONS: Record<string, string> = {
  'react.js': 'React',
  'reactjs': 'React',
  'vue': 'Vue.js',
  'vuejs': 'Vue.js',
  'angular.js': 'Angular',
  'angularjs': 'Angular',
  'node': 'Node.js',
  'nodejs': 'Node.js',
  'express.js': 'Express',
  'expressjs': 'Express',
  'next': 'Next.js',
  'nextjs': 'Next.js',
  'postgres': 'PostgreSQL',
  'postgresql': 'PostgreSQL',
  'mongo': 'MongoDB',
  'mongodb': 'MongoDB',
  'k8s': 'Kubernetes',
  'aws': 'AWS',
  'gcp': 'Google Cloud',
  'tf': 'TensorFlow',
  'tensorflow': 'TensorFlow',
  'ml': 'Machine Learning',
  'ai': 'Machine Learning',
  'dl': 'Deep Learning',
};

export interface SkillExtractionResult {
  skills: string[];
  categories: {
    technical: string[];
    soft: string[];
    tools: string[];
  };
  confidence: number;
  skillFrequency: Record<string, number>;
}

/**
 * Extract skills from text using pattern matching and normalization
 */
export function extractSkills(text: string): SkillExtractionResult {
  logger.debug('Extracting skills from text', { textLength: text.length });

  const normalizedText = text.toLowerCase();
  const foundSkills = new Set<string>();
  const skillFrequency: Record<string, number> = {};

  // Extract skills by pattern matching
  for (const skill of ALL_SKILLS) {
    const skillLower = skill.toLowerCase();
    const regex = new RegExp(`\\b${escapeRegex(skillLower)}\\b`, 'gi');
    const matches = normalizedText.match(regex);

    if (matches) {
      foundSkills.add(skill);
      skillFrequency[skill] = matches.length;
    }
  }

  // Check for skill variations
  for (const [variation, canonical] of Object.entries(SKILL_VARIATIONS)) {
    const regex = new RegExp(`\\b${escapeRegex(variation)}\\b`, 'i');
    if (regex.test(normalizedText)) {
      foundSkills.add(canonical);
      skillFrequency[canonical] = (skillFrequency[canonical] || 0) + 1;
    }
  }

  const skills = Array.from(foundSkills);

  // Categorize skills
  const technical = skills.filter(s =>
    SKILL_TAXONOMY.programming.includes(s) ||
    SKILL_TAXONOMY.webFrontend.includes(s) ||
    SKILL_TAXONOMY.webBackend.includes(s) ||
    SKILL_TAXONOMY.databases.includes(s) ||
    SKILL_TAXONOMY.dataScience.includes(s) ||
    SKILL_TAXONOMY.mobile.includes(s)
  );

  const soft = skills.filter(s => SKILL_TAXONOMY.softSkills.includes(s));
  const tools = skills.filter(s =>
    SKILL_TAXONOMY.tools.includes(s) ||
    SKILL_TAXONOMY.cloudDevOps.includes(s)
  );

  // Calculate confidence based on number of skills found
  const confidence = Math.min(skills.length / 10, 1.0);

  logger.info('Skill extraction completed', {
    totalSkills: skills.length,
    technical: technical.length,
    soft: soft.length,
    tools: tools.length,
    confidence,
  });

  return {
    skills,
    categories: {
      technical,
      soft,
      tools,
    },
    confidence,
    skillFrequency,
  };
}

/**
 * Extract skills with context (e.g., where in the resume they appear)
 */
export interface SkillContext {
  skill: string;
  contexts: string[];
  section?: 'experience' | 'education' | 'skills' | 'projects';
}

export function extractSkillsWithContext(text: string): SkillContext[] {
  const { skills } = extractSkills(text);
  const contexts: SkillContext[] = [];

  for (const skill of skills) {
    const skillRegex = new RegExp(`[^.!?]*\\b${escapeRegex(skill)}\\b[^.!?]*[.!?]`, 'gi');
    const matches = text.match(skillRegex) || [];
    
    contexts.push({
      skill,
      contexts: matches.slice(0, 3), // Top 3 contexts
      section: detectSection(text, skill),
    });
  }

  return contexts;
}

/**
 * Detect which section a skill appears in
 */
function detectSection(
  text: string,
  skill: string
): 'experience' | 'education' | 'skills' | 'projects' | undefined {
  const sections = [
    { name: 'experience' as const, keywords: ['EXPERIENCE', 'WORK HISTORY', 'EMPLOYMENT'] },
    { name: 'education' as const, keywords: ['EDUCATION', 'ACADEMIC', 'UNIVERSITY'] },
    { name: 'skills' as const, keywords: ['SKILLS', 'TECHNICAL SKILLS', 'COMPETENCIES'] },
    { name: 'projects' as const, keywords: ['PROJECTS', 'PORTFOLIO', 'WORK'] },
  ];

  const skillIndex = text.toLowerCase().indexOf(skill.toLowerCase());
  if (skillIndex === -1) return undefined;

  // Find the nearest section header before the skill
  let nearestSection: typeof sections[0]['name'] | undefined;
  let nearestDistance = Infinity;

  for (const section of sections) {
    for (const keyword of section.keywords) {
      const index = text.lastIndexOf(keyword, skillIndex);
      if (index !== -1 && skillIndex - index < nearestDistance) {
        nearestDistance = skillIndex - index;
        nearestSection = section.name;
      }
    }
  }

  return nearestSection;
}

/**
 * Calculate skill overlap between two skill sets
 */
export function calculateSkillOverlap(
  skills1: string[],
  skills2: string[]
): {
  matched: string[];
  onlyInFirst: string[];
  onlyInSecond: string[];
  overlapRatio: number;
} {
  const set1 = new Set(skills1.map(s => s.toLowerCase()));
  const set2 = new Set(skills2.map(s => s.toLowerCase()));

  const matched = skills1.filter(s => set2.has(s.toLowerCase()));
  const onlyInFirst = skills1.filter(s => !set2.has(s.toLowerCase()));
  const onlyInSecond = skills2.filter(s => !set1.has(s.toLowerCase()));

  const overlapRatio = matched.length / Math.max(skills1.length, skills2.length, 1);

  return {
    matched,
    onlyInFirst,
    onlyInSecond,
    overlapRatio,
  };
}

/**
 * Escape special regex characters
 */
function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Get skill category
 */
export function getSkillCategory(skill: string): string | null {
  for (const [category, skills] of Object.entries(SKILL_TAXONOMY)) {
    if (skills.includes(skill)) {
      return category;
    }
  }
  return null;
}

/**
 * Suggest related skills based on existing skills
 */
export function suggestRelatedSkills(skills: string[]): string[] {
  const suggestions = new Set<string>();

  // If someone knows React, they might know Redux, Next.js, etc.
  if (skills.some(s => s === 'React')) {
    suggestions.add('Redux');
    suggestions.add('Next.js');
    suggestions.add('TypeScript');
  }

  // If someone knows Python, suggest data science tools
  if (skills.some(s => s === 'Python')) {
    suggestions.add('Pandas');
    suggestions.add('NumPy');
    suggestions.add('Django');
  }

  // If someone knows Node.js, suggest related tools
  if (skills.some(s => s === 'Node.js')) {
    suggestions.add('Express');
    suggestions.add('MongoDB');
    suggestions.add('TypeScript');
  }

  // Remove skills that are already present
  const existingSkills = new Set(skills);
  return Array.from(suggestions).filter(s => !existingSkills.has(s));
}
