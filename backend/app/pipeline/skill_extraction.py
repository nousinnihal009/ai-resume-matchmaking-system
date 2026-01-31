"""
Skill extraction pipeline using NLP and pattern matching.
"""
import re
from typing import List, Set
import structlog

logger = structlog.get_logger(__name__)

# Predefined skill keywords (can be expanded)
TECHNICAL_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby",
    "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "powershell",

    # Web Technologies
    "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask",
    "spring", "asp.net", "jquery", "bootstrap", "sass", "less",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle",
    "sqlite", "cassandra", "dynamodb",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github actions",
    "terraform", "ansible", "puppet", "chef",

    # Data Science & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "jupyter", "tableau", "power bi",

    # Tools & Frameworks
    "git", "linux", "windows", "macos", "agile", "scrum", "kanban",
}

SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "problem solving", "critical thinking",
    "time management", "adaptability", "creativity", "empathy", "collaboration",
}


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from text using pattern matching.

    Args:
        text: Input text to analyze

    Returns:
        List of extracted skills
    """
    logger.info("Extracting skills from text", text_length=len(text))

    text_lower = text.lower()
    found_skills = set()

    # Extract technical skills
    for skill in TECHNICAL_SKILLS:
        if skill in text_lower:
            found_skills.add(skill.title())

    # Extract soft skills
    for skill in SOFT_SKILLS:
        if skill in text_lower:
            found_skills.add(skill.title())

    # Extract additional patterns
    found_skills.update(_extract_programming_languages(text_lower))
    found_skills.update(_extract_frameworks(text_lower))
    found_skills.update(_extract_tools(text_lower))

    skills_list = sorted(list(found_skills))
    logger.info("Skills extracted", count=len(skills_list), skills=skills_list)

    return skills_list


def _extract_programming_languages(text: str) -> Set[str]:
    """Extract programming languages using regex patterns."""
    languages = set()

    # Common programming language patterns
    patterns = [
        r'\bpython\b',
        r'\bjava\b',
        r'\bjavascript\b',
        r'\btypescript\b',
        r'\bc\+\+|\bcpp\b',
        r'\bc#\b',
        r'\bgo\b',
        r'\brust\b',
        r'\bphp\b',
        r'\bruby\b',
        r'\bswift\b',
        r'\bkotlin\b',
        r'\bscala\b',
        r'\br\b',
        r'\bmatlab\b',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        languages.update(match.title() for match in matches)

    return languages


def _extract_frameworks(text: str) -> Set[str]:
    """Extract frameworks and libraries."""
    frameworks = set()

    framework_patterns = [
        r'\breact\b',
        r'\bangular\b',
        r'\bvue\b',
        r'\bdjango\b',
        r'\bflask\b',
        r'\bspring\b',
        r'\bexpress\b',
        r'\bnode\.js\b',
        r'\btensorflow\b',
        r'\bpytorch\b',
        r'\bscikit-learn\b',
    ]

    for pattern in framework_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        frameworks.update(match.title() for match in matches)

    return frameworks


def _extract_tools(text: str) -> Set[str]:
    """Extract tools and technologies."""
    tools = set()

    tool_patterns = [
        r'\bdocker\b',
        r'\bkubernetes\b',
        r'\baws\b',
        r'\bazure\b',
        r'\bgcp\b',
        r'\bgit\b',
        r'\bjenkins\b',
        r'\bterraform\b',
    ]

    for pattern in tool_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        tools.update(match.title() for match in matches)

    return tools


async def extract_skills_from_resume(text: str) -> List[str]:
    """
    Extract skills specifically from resume text.
    """
    return extract_skills_from_text(text)


async def extract_skills_from_job(text: str) -> List[str]:
    """
    Extract skills specifically from job description text.
    """
    return extract_skills_from_text(text)


def calculate_skill_match(resume_skills: List[str], job_skills: List[str]) -> dict:
    """
    Calculate skill matching between resume and job.

    Args:
        resume_skills: Skills from resume
        job_skills: Required skills from job

    Returns:
        Dictionary with match statistics
    """
    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)

    matched = resume_set.intersection(job_set)
    missing = job_set - resume_set
    additional = resume_set - job_set

    match_score = len(matched) / len(job_set) if job_set else 0

    return {
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing)),
        "additional": sorted(list(additional)),
        "match_score": match_score,
        "matched_count": len(matched),
        "required_count": len(job_set),
    }
