"""
Resume Deep Understanding Engine powered by Google Gemini.

Extracts structured intelligence from resume text that goes far
beyond keyword matching:

1. Seniority estimation — junior/mid/senior/staff/principal
2. Years of experience — computed from timeline, not stated
3. Career trajectory — IC growth, management track, pivots
4. Impact metrics — quantified achievements extracted verbatim
5. Context-aware skills — skill + context pairs showing how used
6. Hidden skill inference — skills implied by projects/achievements
7. Domain expertise — primary domains (web, ML, data, infra, etc.)

All extraction falls back to rule-based logic if Gemini is
unavailable, ensuring the system always returns something useful.

Analysis results are versioned so stale analyses can be detected
and re-run when the prompt or model changes.
"""
import re
from typing import Any
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Version this prompt — increment when logic changes
# so existing analyses can be detected as stale
ANALYSIS_VERSION = "1.0.0"

RESUME_ANALYSIS_PROMPT = """
You are an expert technical recruiter and AI talent analyst.
Analyze the following resume text and extract structured intelligence.

RESUME TEXT:
{resume_text}

Extract and return ONLY a valid JSON object with this exact structure.
Do not include any text before or after the JSON:

{{
    "seniority_level": "junior|mid|senior|staff|principal",
    "years_of_experience": <float, computed from timeline not stated value>,
    "career_trajectory": "IC growth|management track|career pivot|early career|consultant",
    "domain_expertise": ["list", "of", "primary", "domains"],
    "impact_metrics": [
        "exact verbatim achievement statements with numbers",
        "e.g. Reduced API latency by 40 percent",
        "e.g. Led team of 8 engineers"
    ],
    "context_aware_skills": {{
        "Python": "used for ML pipeline development and data processing",
        "FastAPI": "built production REST APIs serving 1M+ requests/day",
        "skill_name": "context of how the skill was used"
    }},
    "inferred_skills": [
        "skills not explicitly mentioned but strongly implied by context",
        "e.g. if they mention BERT fine-tuning, infer: PyTorch, Hugging Face"
    ],
    "skill_depth": {{
        "expert": ["skills used in production, at scale, with impact"],
        "proficient": ["skills used regularly in real projects"],
        "familiar": ["mentioned but limited evidence of depth"]
    }},
    "career_summary": "2-3 sentence professional summary of this candidate",
    "red_flags": [
        "any concerns: gaps, inconsistencies, vague claims"
    ],
    "strengths": [
        "standout qualities that make this candidate distinctive"
    ]
}}

Rules:
- years_of_experience: compute from earliest role to present, not stated value
- seniority_level: base on scope of impact, team size, system complexity
- context_aware_skills: only include skills where you can infer context
- inferred_skills: only include if strongly implied, not guessed
- impact_metrics: extract verbatim or near-verbatim, must contain numbers
- Be conservative — only include what the resume actually supports
"""


async def analyze_resume(resume_text: str) -> dict[str, Any]:
    """
    Perform deep understanding analysis on resume text using Gemini.

    Falls back to rule-based extraction if Gemini is unavailable.

    Args:
        resume_text: Full extracted text content of the resume

    Returns:
        Structured analysis dict with all intelligence fields.
        Always returns a valid dict — never raises.
    """
    if not resume_text or not resume_text.strip():
        return _empty_analysis()

    logger.info(
        "resume_analysis_started",
        text_length=len(resume_text),
        version=ANALYSIS_VERSION,
    )

    # Build cache key from resume text hash
    import hashlib
    text_hash = hashlib.sha256(resume_text.encode()).hexdigest()[:16]
    cache_key = f"resume_analysis:{text_hash}:{ANALYSIS_VERSION}"

    # Try Gemini first
    try:
        from app.core.gemini_client import gemini_call
        prompt = RESUME_ANALYSIS_PROMPT.format(
            resume_text=resume_text[:8000]  # Limit to avoid token overflow
        )
        result = await gemini_call(
            prompt=prompt,
            cache_key=cache_key,
            expect_json=True,
            cache_prefix="resume_analysis",
        )

        if result and isinstance(result, dict):
            result["analysis_version"] = ANALYSIS_VERSION
            result["analysis_source"] = "gemini"
            logger.info(
                "resume_analysis_complete",
                source="gemini",
                seniority=result.get("seniority_level"),
                years_exp=result.get("years_of_experience"),
            )
            return result

    except Exception as exc:
        logger.error(
            "resume_analysis_gemini_failed",
            error=str(exc),
            fallback="rule_based",
        )

    # Fallback to rule-based extraction
    logger.info("resume_analysis_fallback", source="rule_based")
    return _rule_based_analysis(resume_text)


def analyze_resume_sync(resume_text: str) -> dict[str, Any]:
    """
    Synchronous wrapper for Celery task context.
    Uses only rule-based extraction — no Gemini in sync context.
    Call analyze_resume() from async endpoints for Gemini support.
    """
    return _rule_based_analysis(resume_text)


def _rule_based_analysis(resume_text: str) -> dict[str, Any]:
    """
    Rule-based resume analysis fallback.
    Provides reasonable estimates without Gemini.
    """
    text_lower = resume_text.lower()

    # Seniority estimation from keyword signals
    seniority = "mid"
    if any(k in text_lower for k in [
        "principal", "distinguished", "fellow", "vp ", "vice president"
    ]):
        seniority = "principal"
    elif any(k in text_lower for k in [
        "staff engineer", "staff software", "tech lead", "technical lead"
    ]):
        seniority = "staff"
    elif any(k in text_lower for k in [
        "senior", "sr.", "lead ", "architect", "manager"
    ]):
        seniority = "senior"
    elif any(k in text_lower for k in [
        "junior", "jr.", "intern", "graduate", "entry level"
    ]):
        seniority = "junior"

    # Extract impact metrics (lines with numbers + % or x)
    impact_patterns = [
        r'\d+%',
        r'\d+x\b',
        r'\$\d+',
        r'\d+\s*(million|billion|thousand|k\b)',
        r'(increased|decreased|reduced|improved|grew|saved).*\d+',
    ]
    impact_metrics = []
    for line in resume_text.split('\n'):
        line = line.strip()
        if any(re.search(p, line.lower()) for p in impact_patterns):
            if 10 < len(line) < 200:
                impact_metrics.append(line)

    # Estimate years of experience from year mentions
    years = re.findall(r'\b(19|20)\d{2}\b', resume_text)
    years_exp = 0.0
    if years:
        year_ints = [int(y) for y in years]
        span = max(year_ints) - min(year_ints)
        years_exp = float(min(span, 30))

    return {
        "seniority_level": seniority,
        "years_of_experience": years_exp,
        "career_trajectory": "IC growth",
        "domain_expertise": [],
        "impact_metrics": impact_metrics[:10],
        "context_aware_skills": {},
        "inferred_skills": [],
        "skill_depth": {"expert": [], "proficient": [], "familiar": []},
        "career_summary": "",
        "red_flags": [],
        "strengths": [],
        "analysis_version": ANALYSIS_VERSION,
        "analysis_source": "rule_based",
    }


def _empty_analysis() -> dict[str, Any]:
    """Return empty analysis for empty/None resume text."""
    return {
        "seniority_level": "unknown",
        "years_of_experience": 0.0,
        "career_trajectory": "unknown",
        "domain_expertise": [],
        "impact_metrics": [],
        "context_aware_skills": {},
        "inferred_skills": [],
        "skill_depth": {"expert": [], "proficient": [], "familiar": []},
        "career_summary": "",
        "red_flags": [],
        "strengths": [],
        "analysis_version": ANALYSIS_VERSION,
        "analysis_source": "empty",
    }
