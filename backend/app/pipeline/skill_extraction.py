"""
Skill extraction pipeline for resume and job processing.
"""
import re
import logging
from typing import List, Dict, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Service for extracting skills from text."""

    def __init__(self):
        """Initialize the skill extractor with predefined skill sets."""
        self.technical_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell',

            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'asp.net', 'jquery', 'bootstrap', 'sass', 'less',

            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite', 'cassandra', 'dynamodb',

            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'terraform', 'ansible', 'puppet',

            # Data Science & ML
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'jupyter', 'spark', 'hadoop', 'kafka',

            # Tools & Frameworks
            'git', 'linux', 'windows', 'macos', 'android', 'ios', 'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'kanban'
        }

        self.soft_skills = {
            'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking', 'time management',
            'adaptability', 'creativity', 'emotional intelligence', 'conflict resolution', 'negotiation',
            'project management', 'decision making', 'analytical thinking', 'attention to detail'
        }

        self.domain_skills = {
            'finance', 'healthcare', 'e-commerce', 'education', 'gaming', 'blockchain', 'cybersecurity',
            'iot', 'ai', 'nlp', 'computer vision', 'robotics', 'biotech', 'automotive', 'retail'
        }

        # Compile regex patterns for efficiency
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for skill matching."""
        all_skills = self.technical_skills | self.soft_skills | self.domain_skills
        # Sort by length (longest first) to match multi-word skills before single words
        skill_patterns = sorted(all_skills, key=len, reverse=True)
        # Escape special regex characters and create case-insensitive pattern
        escaped_skills = [re.escape(skill) for skill in skill_patterns]
        self.skill_pattern = re.compile(r'\b(?:' + '|'.join(escaped_skills) + r')\b', re.IGNORECASE)

    async def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extract skills from text.

        Args:
            text: The text to analyze

        Returns:
            Dictionary containing extracted skills and metadata
        """
        try:
            if not text or not text.strip():
                return {
                    'extracted_skills': [],
                    'confidence': 0.0,
                    'categories': {
                        'technical': [],
                        'soft': [],
                        'domain': []
                    }
                }

            # Normalize text
            normalized_text = self._normalize_text(text)

            # Find all skill matches
            matches = self.skill_pattern.findall(normalized_text)

            # Remove duplicates and normalize case
            found_skills = list(set(match.lower() for match in matches))

            # Categorize skills
            categories = {
                'technical': [skill for skill in found_skills if skill in self.technical_skills],
                'soft': [skill for skill in found_skills if skill in self.soft_skills],
                'domain': [skill for skill in found_skills if skill in self.domain_skills]
            }

            # Calculate confidence based on text length and skill matches
            confidence = min(len(found_skills) * 0.1, 1.0) if found_skills else 0.0

            return {
                'extracted_skills': found_skills,
                'confidence': confidence,
                'categories': categories
            }

        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            return {
                'extracted_skills': [],
                'confidence': 0.0,
                'categories': {
                    'technical': [],
                    'soft': [],
                    'domain': []
                }
            }

    def _normalize_text(self, text: str) -> str:
        """Normalize text for better skill extraction."""
        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Handle common abbreviations and variations
        replacements = {
            'js': 'javascript',
            'ts': 'typescript',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'nlp': 'natural language processing',
            'cv': 'computer vision',
            'ci/cd': 'continuous integration',
            'ci': 'continuous integration',
            'cd': 'continuous deployment'
        }

        for abbr, full in replacements.items():
            text = re.sub(r'\b' + re.escape(abbr) + r'\b', full, text)

        return text

    def get_skill_suggestions(self, partial_skill: str, limit: int = 10) -> List[str]:
        """Get skill suggestions based on partial input."""
        if not partial_skill:
            return []

        partial_lower = partial_skill.lower()
        all_skills = list(self.technical_skills | self.soft_skills | self.domain_skills)

        # Filter skills that start with the partial input
        matches = [skill for skill in all_skills if skill.startswith(partial_lower)]

        # Sort by relevance (exact prefix match first, then alphabetical)
        matches.sort(key=lambda x: (not x.startswith(partial_lower + ' '), x))

        return matches[:limit]


# Global skill extractor instance
skill_extractor = SkillExtractor()
