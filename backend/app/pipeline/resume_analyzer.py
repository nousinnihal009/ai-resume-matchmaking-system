"""
Comprehensive Resume Analysis Engine.

Analyzes resumes across 6 dimensions matching industry standards:

1. CONTENT (40% of score)
   - ATS Parse Rate: can machines read this resume?
   - Quantifying Impact: are achievements measurable?
   - Repetition: overused words detected
   - Spelling & Grammar: errors found via Gemini

2. SECTIONS (20% of score)
   - Essential sections present/missing
   - Section quality scoring

3. ATS ESSENTIALS (15% of score)
   - File format compliance
   - Contact information completeness
   - Length appropriateness

4. DESIGN (10% of score)
   - Layout detection
   - Visual structure analysis
   - Template recommendations

5. SKILLS (10% of score)
   - Skill density
   - Categorization quality

6. TAILORING (5% of score — requires job description)
   - Keyword alignment
   - Role-specific optimization

All analysis falls back gracefully if Gemini is unavailable.
Results are cached via Redis to avoid duplicate Gemini calls.
"""
import re
import hashlib
from collections import Counter
from datetime import datetime, timezone
from typing import Any
from app.core.logging_config import get_logger

logger = get_logger(__name__)

ANALYZER_VERSION = "1.0.0"

# ── Essential resume sections ─────────────────────────────────────────
ESSENTIAL_SECTIONS = [
    "experience", "education", "skills", "summary", "contact"
]
OPTIONAL_SECTIONS = [
    "projects", "certifications", "awards", "publications",
    "languages", "volunteer", "interests", "references"
]

# ── Section detection patterns ────────────────────────────────────────
SECTION_PATTERNS = {
    "experience": [
        r"\bexperience\b", r"\bwork history\b", r"\bemployment\b",
        r"\bprofessional background\b", r"\binternship\b"
    ],
    "education": [
        r"\beducation\b", r"\bacademic\b", r"\bdegree\b",
        r"\buniversity\b", r"\bcollege\b", r"\bb\.tech\b", r"\bb\.e\b"
    ],
    "skills": [
        r"\bskills\b", r"\btechnical skills\b", r"\bcore competencies\b",
        r"\btechnologies\b", r"\bproficiencies\b"
    ],
    "summary": [
        r"\bsummary\b", r"\bprofile\b", r"\bobjective\b",
        r"\babout me\b", r"\bprofessional summary\b"
    ],
    "contact": [
        r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b",
        r"\b\+?[\d\s\-\(\)]{10,}\b",
        r"\blinkedin\.com\b", r"\bgithub\.com\b"
    ],
    "projects": [
        r"\bprojects\b", r"\bpersonal projects\b", r"\bside projects\b"
    ],
    "certifications": [
        r"\bcertif", r"\bcredential\b", r"\blicense\b"
    ],
}

# ── Contact extraction patterns ───────────────────────────────────────
CONTACT_PATTERNS = {
    "email": r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b",
    "phone": r"\b\+?[\d\s\-\(\)]{10,15}\b",
    "linkedin": r"linkedin\.com/in/[\w\-]+",
    "github": r"github\.com/[\w\-]+",
    "website": r"https?://[\w\-\.]+\.[a-z]{2,}[\w\-\._~:/?#\[\]@!$&\'()*+,;=%]*",
}

# ── Weak action verbs to flag ─────────────────────────────────────────
WEAK_VERBS = {
    "helped", "assisted", "worked on", "was responsible for",
    "did", "made", "handled", "dealt with", "was involved in",
}

# ── Strong action verbs ───────────────────────────────────────────────
STRONG_VERBS = {
    "architected", "engineered", "spearheaded", "orchestrated",
    "designed", "built", "deployed", "optimized", "reduced",
    "increased", "launched", "led", "mentored", "automated",
    "delivered", "streamlined", "transformed", "developed",
    "implemented", "created", "established", "managed",
}

# ── Template suggestions ──────────────────────────────────────────────
TEMPLATE_SUGGESTIONS = [
    {
        "name": "Double Column",
        "description": "Modern two-column layout. Skills on left, experience on right.",
        "best_for": "Tech roles, startups",
        "ats_friendly": True,
    },
    {
        "name": "Ivy League",
        "description": "Clean single-column academic style. Maximum ATS compatibility.",
        "best_for": "Academia, research, consulting",
        "ats_friendly": True,
    },
    {
        "name": "Elegant",
        "description": "Minimal design with strong typography hierarchy.",
        "best_for": "Product, design, marketing roles",
        "ats_friendly": True,
    },
    {
        "name": "Executive",
        "description": "Bold header with achievements-first structure.",
        "best_for": "Senior roles, leadership positions",
        "ats_friendly": True,
    },
]


# ══════════════════════════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ══════════════════════════════════════════════════════════════════════

async def analyze_resume_comprehensive(
    resume_text: str,
    file_name: str = "",
    file_size_bytes: int = 0,
) -> dict[str, Any]:
    """
    Run comprehensive 6-category analysis on resume text.

    Args:
        resume_text: Full extracted text content
        file_name: Original filename for format analysis
        file_size_bytes: File size for ATS compliance check

    Returns:
        Complete analysis report with scores and actionable feedback.
        Always returns a valid dict — never raises.
    """
    if not resume_text or not resume_text.strip():
        return _empty_report()

    logger.info(
        "comprehensive_analysis_started",
        text_length=len(resume_text),
        file_name=file_name,
    )

    # Run all rule-based analyses (fast, no API calls)
    sections = _analyze_sections(resume_text)
    contact = _analyze_contact(resume_text)
    repetition = _analyze_repetition(resume_text)
    file_info = _analyze_file(file_name, file_size_bytes)
    design = _analyze_design(resume_text)
    ats_parse = _calculate_ats_parse_rate(resume_text, sections)
    quantification = _analyze_quantification(resume_text)

    # Run Gemini-powered analyses (with caching + fallback)
    spelling_grammar = await _analyze_spelling_grammar_gemini(resume_text)
    content_quality = await _analyze_content_quality_gemini(resume_text)

    # Compute category scores
    content_score = _score_content(
        ats_parse, quantification, repetition, spelling_grammar
    )
    sections_score = _score_sections(sections)
    ats_score = _score_ats_essentials(file_info, contact)
    design_score = _score_design(design, resume_text)
    skills_score = _score_skills(resume_text)

    # Weighted overall score
    overall = (
        content_score * 0.40 +
        sections_score * 0.20 +
        ats_score * 0.15 +
        design_score * 0.10 +
        skills_score * 0.10 +
        75 * 0.05  # tailoring defaults to 75 until job is provided
    )
    overall_score = max(0, min(100, round(overall)))

    score_breakdown = {
        "content": {"score": content_score, "weight": 40},
        "sections": {"score": sections_score, "weight": 20},
        "ats_essentials": {"score": ats_score, "weight": 15},
        "design": {"score": design_score, "weight": 10},
        "skills": {"score": skills_score, "weight": 10},
        "tailoring": {"score": 75, "weight": 5,
                      "note": "Provide job description for tailored score"},
    }

    report = {
        "overall_score": overall_score,
        "score_breakdown": score_breakdown,
        "total_issues": (
            len(repetition.get("issues", [])) +
            len(spelling_grammar.get("spelling_errors", [])) +
            len(spelling_grammar.get("grammar_errors", [])) +
            len(sections.get("missing", []))
        ),

        # Category 1: Content
        "content": {
            "score": content_score,
            "ats_parse_rate": ats_parse,
            "ats_parse_status": "good" if ats_parse >= 85 else "warning",
            "quantification": quantification,
            "repetition": repetition,
            "spelling_grammar": spelling_grammar,
            "content_quality": content_quality,
        },

        # Category 2: Sections
        "sections": sections,

        # Category 3: ATS Essentials
        "ats_essentials": {
            "score": ats_score,
            "file_analysis": file_info,
            "contact_info": contact,
        },

        # Category 4: Design
        "design": {
            "score": design_score,
            "feedback": design.get("feedback", []),
            "template_suggestions": TEMPLATE_SUGGESTIONS,
            "layout_detected": design.get("layout", "unknown"),
        },

        # Category 5: Skills
        "skills_analysis": {
            "score": skills_score,
            "density": _calculate_skill_density(resume_text),
        },

        # Metadata
        "analyzer_version": ANALYZER_VERSION,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(
        "comprehensive_analysis_complete",
        overall_score=overall_score,
        total_issues=report["total_issues"],
    )

    return report


# ══════════════════════════════════════════════════════════════════════
# CATEGORY ANALYZERS
# ══════════════════════════════════════════════════════════════════════

def _analyze_sections(text: str) -> dict:
    """Detect which essential and optional sections are present."""
    text_lower = text.lower()
    present = []
    missing = []

    for section, patterns in SECTION_PATTERNS.items():
        found = any(
            re.search(p, text_lower) for p in patterns
        )
        if found:
            present.append(section)
        elif section in ESSENTIAL_SECTIONS:
            missing.append(section)

    return {
        "present": present,
        "missing": missing,
        "essential_present": [
            s for s in present if s in ESSENTIAL_SECTIONS
        ],
        "optional_present": [
            s for s in present if s in OPTIONAL_SECTIONS
        ],
    }


def _analyze_contact(text: str) -> dict:
    """Extract and validate contact information."""
    found = {}
    missing = []

    for field, pattern in CONTACT_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(0)
            # Mask sensitive data in storage
            if field == "email":
                parts = value.split("@")
                found[field] = {
                    "present": True,
                    "masked": f"{parts[0][:3]}***@{parts[1]}",
                }
            elif field == "phone":
                found[field] = {
                    "present": True,
                    "masked": value[:4] + "****" + value[-2:],
                }
            else:
                found[field] = {"present": True, "value": value}
        else:
            if field in ["email", "phone"]:
                missing.append(field)
            found[field] = {"present": False}

    return {
        "found": found,
        "missing": missing,
        "completeness_score": round(
            len([k for k, v in found.items() if v.get("present")])
            / len(CONTACT_PATTERNS) * 100
        ),
    }


def _analyze_repetition(text: str) -> dict:
    """Detect overused words and suggest alternatives."""
    SYNONYMS = {
        "completed": ["finished", "concluded", "fulfilled", "delivered"],
        "implemented": ["executed", "applied", "deployed", "established"],
        "developed": ["built", "created", "engineered", "designed"],
        "managed": ["led", "directed", "oversaw", "coordinated"],
        "worked": ["collaborated", "partnered", "contributed", "engaged"],
        "used": ["utilized", "leveraged", "applied", "employed"],
        "responsible": ["accountable", "owned", "spearheaded", "led"],
        "helped": ["supported", "assisted", "enabled", "facilitated"],
        "made": ["created", "produced", "generated", "built"],
        "improved": ["enhanced", "optimized", "elevated", "boosted"],
    }

    # Extract meaningful words (skip stopwords)
    STOPWORDS = {
        "the", "and", "for", "are", "but", "not", "you", "all",
        "can", "had", "her", "was", "one", "our", "out", "day",
        "get", "has", "him", "his", "how", "its", "may", "new",
        "now", "old", "see", "two", "who", "did", "did", "will",
        "with", "have", "this", "that", "from", "they", "been",
        "were", "said", "each", "which", "their", "time", "your",
    }

    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    counts = Counter(filtered)

    issues = []
    for word, count in counts.most_common(20):
        if count >= 3:
            suggestions = SYNONYMS.get(word, [])
            if count >= 4 or word in SYNONYMS:
                issues.append({
                    "word": word,
                    "count": count,
                    "severity": "high" if count >= 5 else "medium",
                    "suggestions": suggestions[:3] if suggestions else [],
                })

    return {
        "issues": issues[:10],
        "issue_count": len(issues),
        "has_issues": len(issues) > 0,
    }


def _analyze_file(file_name: str, file_size_bytes: int) -> dict:
    """Analyze file format and size for ATS compliance."""
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    size_kb = round(file_size_bytes / 1024, 1) if file_size_bytes else 0
    size_mb = round(file_size_bytes / (1024 * 1024), 2) if file_size_bytes else 0

    format_scores = {"pdf": 100, "docx": 80, "doc": 70, "txt": 50}
    format_score = format_scores.get(ext, 40)

    issues = []
    if ext not in ["pdf", "docx"]:
        issues.append(
            f"File format .{ext} has lower ATS compatibility. "
            f"PDF is recommended."
        )
    if size_mb > 2:
        issues.append(
            f"File size {size_mb}MB exceeds the 2MB limit for most "
            f"job portals. Compress images or reduce file size."
        )

    return {
        "file_name": file_name,
        "format": ext.upper() if ext else "Unknown",
        "size_kb": size_kb,
        "size_mb": size_mb,
        "format_score": format_score,
        "ats_compatible": ext in ["pdf", "docx"],
        "size_acceptable": size_mb <= 2,
        "issues": issues,
        "recommendation": (
            "PDF format under 2MB is ideal for ATS systems and "
            "most job portals."
        ),
    }


def _analyze_design(text: str) -> dict:
    """Analyze resume design and layout signals from text structure."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    total_lines = len(lines)

    # Estimate layout from structure signals
    all_caps_lines = sum(1 for l in lines if l.isupper() and len(l) > 3)
    short_lines = sum(1 for l in lines if len(l) < 30)
    bullet_lines = sum(
        1 for l in lines if l.startswith(("•", "-", "·", "*", "◦"))
    )

    layout = "single_column"
    if short_lines / max(total_lines, 1) > 0.4:
        layout = "two_column_likely"

    feedback = []
    if bullet_lines < 5:
        feedback.append(
            "Use bullet points to break up dense paragraphs and "
            "improve scannability."
        )
    if all_caps_lines < 3:
        feedback.append(
            "Add clear section headers in bold or caps to improve "
            "visual hierarchy."
        )
    if total_lines < 30:
        feedback.append(
            "Resume appears thin. Add more detail to projects and "
            "experience sections."
        )
    if total_lines > 150:
        feedback.append(
            "Resume may be too long. Aim for 1-2 pages for most roles."
        )

    feedback.append(
        "Consider a modern template — generic Word-default layouts "
        "blend into the pile. A distinctive but ATS-safe design "
        "increases callback rates."
    )

    return {
        "layout": layout,
        "feedback": feedback,
        "bullet_point_count": bullet_lines,
        "section_header_count": all_caps_lines,
        "estimated_pages": max(1, round(total_lines / 50)),
    }


def _calculate_ats_parse_rate(text: str, sections: dict) -> float:
    """Estimate what percentage of the resume an ATS can parse."""
    score = 100.0
    if len(sections.get("missing", [])) > 0:
        score -= len(sections["missing"]) * 5
    # Check for common ATS-blocking patterns
    if re.search(r'[^\x00-\x7F]', text):
        score -= 5  # Non-ASCII characters
    if text.count('\n') < 10:
        score -= 10  # Very flat structure
    return max(50.0, min(100.0, round(score, 1)))


def _analyze_quantification(text: str) -> dict:
    """Check if achievements are quantified with numbers."""
    impact_patterns = [
        r'\d+\s*%', r'\$\s*\d+', r'\d+\s*x\b',
        r'\d+\s*(million|billion|thousand|k)\b',
        r'(increased|decreased|reduced|improved|grew|saved|'
        r'boosted|cut|drove|generated)\s.*\d+',
    ]
    lines = text.split('\n')
    quantified = []
    unquantified_bullets = []

    for line in lines:
        line = line.strip()
        if not line or len(line) < 15:
            continue
        starts_with_action = any(
            line.lower().startswith(v) for v in STRONG_VERBS
        )
        has_number = any(
            re.search(p, line.lower()) for p in impact_patterns
        )
        if has_number:
            quantified.append(line[:100])
        elif starts_with_action and not has_number:
            unquantified_bullets.append(line[:100])

    return {
        "quantified_achievements": quantified[:5],
        "unquantified_bullets": unquantified_bullets[:5],
        "quantification_rate": round(
            len(quantified) / max(len(quantified) +
            len(unquantified_bullets), 1) * 100
        ),
        "has_impact_metrics": len(quantified) > 0,
        "suggestion": (
            "Add numbers to your bullet points: team size, "
            "percentage improvements, revenue impact, user counts."
            if not quantified else None
        ),
    }


async def _analyze_spelling_grammar_gemini(
    text: str
) -> dict:
    """Use Gemini to detect spelling and grammar issues."""
    text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
    cache_key = f"spell_grammar:{text_hash}"

    PROMPT = f"""
You are a professional resume editor. Analyze the following resume text
for spelling mistakes and grammar errors.

RESUME TEXT (first 3000 chars):
{text[:3000]}

Return ONLY valid JSON with this exact structure, no other text:
{{
    "spelling_errors": [
        {{"word": "misspeled", "suggestion": "misspelled", "context": "...surrounding text..."}}
    ],
    "grammar_errors": [
        {{"issue": "description of the grammar error", "original": "original text", "suggestion": "corrected text"}}
    ],
    "overall_language_quality": "excellent|good|fair|poor",
    "language_feedback": "one sentence overall assessment"
}}

Be conservative — only flag clear errors, not style preferences.
Maximum 5 spelling errors and 5 grammar errors.
"""

    try:
        from app.core.gemini_client import gemini_call
        result = await gemini_call(
            prompt=PROMPT,
            cache_key=cache_key,
            expect_json=True,
            cache_prefix="spell_grammar",
        )
        if result and isinstance(result, dict):
            return {
                "spelling_errors": result.get("spelling_errors", [])[:5],
                "grammar_errors": result.get("grammar_errors", [])[:5],
                "overall_quality": result.get(
                    "overall_language_quality", "unknown"
                ),
                "language_feedback": result.get("language_feedback", ""),
                "source": "gemini",
            }
    except Exception as exc:
        logger.error(
            "spelling_grammar_gemini_failed",
            error=str(exc),
        )

    # Fallback: basic rule-based spell check
    return {
        "spelling_errors": [],
        "grammar_errors": [],
        "overall_quality": "unknown",
        "language_feedback": (
            "Install GEMINI_API_KEY for AI-powered spell checking."
        ),
        "source": "rule_based",
    }


async def _analyze_content_quality_gemini(text: str) -> dict:
    """Use Gemini to assess overall content quality."""
    text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
    cache_key = f"content_quality:{text_hash}"

    PROMPT = f"""
You are an expert technical recruiter reviewing a resume.
Analyze the content quality of this resume.

RESUME TEXT:
{text[:4000]}

Return ONLY valid JSON with no other text:
{{
    "strengths": ["list of 2-3 genuine content strengths"],
    "weaknesses": ["list of 2-3 specific content weaknesses"],
    "action_verb_quality": "strong|moderate|weak",
    "specificity_score": <integer 0-100>,
    "professional_tone_score": <integer 0-100>,
    "suggestions": [
        "specific actionable suggestion 1",
        "specific actionable suggestion 2",
        "specific actionable suggestion 3"
    ]
}}
"""

    try:
        from app.core.gemini_client import gemini_call
        result = await gemini_call(
            prompt=PROMPT,
            cache_key=cache_key,
            expect_json=True,
            cache_prefix="content_quality",
        )
        if result and isinstance(result, dict):
            result["source"] = "gemini"
            return result
    except Exception as exc:
        logger.error(
            "content_quality_gemini_failed",
            error=str(exc),
        )

    return {
        "strengths": [],
        "weaknesses": [],
        "action_verb_quality": "unknown",
        "specificity_score": 0,
        "professional_tone_score": 0,
        "suggestions": [],
        "source": "rule_based",
    }


# ══════════════════════════════════════════════════════════════════════
# SCORING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def _score_content(
    ats_parse: float,
    quantification: dict,
    repetition: dict,
    spelling_grammar: dict,
) -> int:
    score = 100
    # ATS parse rate contributes 30% of content score
    score -= (100 - ats_parse) * 0.30
    # Repetition penalty
    score -= min(len(repetition.get("issues", [])) * 5, 20)
    # Spelling penalty
    score -= min(
        len(spelling_grammar.get("spelling_errors", [])) * 4, 16
    )
    # Grammar penalty
    score -= min(
        len(spelling_grammar.get("grammar_errors", [])) * 3, 12
    )
    # Quantification bonus
    q_rate = quantification.get("quantification_rate", 0)
    if q_rate < 30:
        score -= 10
    return max(0, min(100, round(score)))


def _score_sections(sections: dict) -> int:
    missing = len(sections.get("missing", []))
    present = len(sections.get("present", []))
    if missing == 0:
        return 100
    score = 100 - (missing * 15)
    return max(0, min(100, score))


def _score_ats_essentials(file_info: dict, contact: dict) -> int:
    score = 100
    if not file_info.get("ats_compatible"):
        score -= 20
    if not file_info.get("size_acceptable"):
        score -= 10
    contact_score = contact.get("completeness_score", 50)
    score = (score * 0.5) + (contact_score * 0.5)
    return max(0, min(100, round(score)))


def _score_design(design: dict, text: str) -> int:
    score = 70  # Base score
    if design.get("bullet_point_count", 0) >= 5:
        score += 10
    if design.get("section_header_count", 0) >= 3:
        score += 10
    pages = design.get("estimated_pages", 1)
    if 1 <= pages <= 2:
        score += 10
    return max(0, min(100, score))


def _score_skills(text: str) -> int:
    density = _calculate_skill_density(text)
    if density >= 15:
        return 90
    elif density >= 8:
        return 75
    elif density >= 4:
        return 55
    return 35


def _calculate_skill_density(text: str) -> int:
    """Count distinct technical skills mentioned."""
    TECH_SKILLS = {
        "python", "javascript", "typescript", "java", "c++", "c#",
        "react", "angular", "vue", "node", "fastapi", "django",
        "flask", "spring", "docker", "kubernetes", "aws", "azure",
        "gcp", "postgresql", "mysql", "mongodb", "redis", "git",
        "tensorflow", "pytorch", "scikit", "pandas", "numpy",
        "sql", "html", "css", "linux", "bash", "terraform",
        "graphql", "rest", "kafka", "spark", "hadoop", "airflow",
    }
    text_lower = text.lower()
    return sum(1 for skill in TECH_SKILLS if skill in text_lower)


def _empty_report() -> dict:
    return {
        "overall_score": 0,
        "score_breakdown": {},
        "total_issues": 0,
        "content": {},
        "sections": {"present": [], "missing": ESSENTIAL_SECTIONS},
        "ats_essentials": {},
        "design": {},
        "skills_analysis": {},
        "analyzer_version": ANALYZER_VERSION,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "error": "No resume text to analyze",
    }


# ══════════════════════════════════════════════════════════════════════
# RESUME TAILORING ENGINE
# ══════════════════════════════════════════════════════════════════════

async def tailor_resume_for_job(
    resume_text: str,
    job_description: str,
    resume_analysis: dict | None = None,
) -> dict[str, Any]:
    """
    Generate job-specific resume tailoring suggestions using Gemini.

    Compares resume content against job description and returns:
    - Missing keywords from the job description
    - Bullet points to add or rewrite
    - Skills to highlight more prominently
    - Tailoring score (how well resume fits this specific job)

    Args:
        resume_text: Full resume content
        job_description: Target job description text
        resume_analysis: Optional existing analysis to enrich suggestions

    Returns:
        Tailoring report with actionable changes. Never raises.
    """
    if not resume_text or not job_description:
        return {"error": "Both resume and job description required"}

    combined = resume_text[:2000] + job_description[:1000]
    cache_key = f"tailoring:{hashlib.sha256(combined.encode()).hexdigest()[:16]}"

    PROMPT = f"""
You are an expert resume coach and ATS optimization specialist.
A candidate wants to tailor their resume for a specific job.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

Analyze the fit and return ONLY valid JSON with this exact structure:

{{
    "tailoring_score": <integer 0-100, how well resume fits this job>,
    "missing_keywords": [
        "keyword1 from job description not in resume",
        "keyword2"
    ],
    "keywords_present": [
        "keyword already in resume that matches job"
    ],
    "bullet_rewrites": [
        {{
            "original": "existing bullet point from resume",
            "rewritten": "improved version that better matches job",
            "reason": "why this change improves fit"
        }}
    ],
    "sections_to_add": [
        "e.g. Add a Projects section highlighting X and Y"
    ],
    "skills_to_highlight": [
        "skill candidate has that should be more prominent for this role"
    ],
    "summary_rewrite": "rewritten professional summary optimized for this job",
    "overall_fit": "strong|moderate|weak",
    "fit_explanation": "2 sentence explanation of match quality",
    "top_3_gaps": [
        "most critical gap 1",
        "most critical gap 2",
        "most critical gap 3"
    ]
}}

Be specific and actionable. Reference actual content from both the
resume and job description.
"""

    try:
        from app.core.gemini_client import gemini_call
        result = await gemini_call(
            prompt=PROMPT,
            cache_key=cache_key,
            expect_json=True,
            cache_prefix="tailoring",
        )
        if result and isinstance(result, dict):
            result["source"] = "gemini"
            result["analyzed_at"] = datetime.now(timezone.utc).isoformat()
            return result
    except Exception as exc:
        logger.error(
            "resume_tailoring_gemini_failed",
            error=str(exc),
        )

    # Rule-based fallback
    return _rule_based_tailoring(resume_text, job_description)


def _rule_based_tailoring(
    resume_text: str, job_description: str
) -> dict:
    """Basic keyword matching fallback when Gemini unavailable."""
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text.lower()))
    job_words = set(re.findall(r'\b[a-z]{3,}\b', job_description.lower()))

    STOPWORDS = {
        "the", "and", "for", "are", "with", "this", "that",
        "have", "from", "they", "will", "been", "were", "your",
    }
    job_keywords = job_words - STOPWORDS - resume_words
    present_keywords = job_words & resume_words - STOPWORDS

    return {
        "tailoring_score": min(
            100, round(len(present_keywords) / max(len(job_words), 1) * 100)
        ),
        "missing_keywords": sorted(job_keywords)[:15],
        "keywords_present": sorted(present_keywords)[:10],
        "bullet_rewrites": [],
        "sections_to_add": [],
        "skills_to_highlight": [],
        "summary_rewrite": "",
        "overall_fit": "unknown",
        "fit_explanation": "Enable GEMINI_API_KEY for detailed analysis.",
        "top_3_gaps": [],
        "source": "rule_based",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
