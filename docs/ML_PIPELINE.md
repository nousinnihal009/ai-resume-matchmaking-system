# ML Pipeline Documentation

## Overview

The AI Resume Matcher uses a sophisticated machine learning pipeline to match candidates with job opportunities. This document provides detailed technical specifications of the ML system.

---

## Architecture

```
┌─────────────────┐
│  Input Layer    │  Resume PDF/DOCX or Job Description
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Extraction │  Convert documents to plain text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Skill Extraction │  NLP-based skill identification
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embeddings    │  Generate semantic vector representations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Matching Engine  │  Calculate similarity scores
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ranking &     │  Sort and generate explanations
│  Explanation    │
└─────────────────┘
```

---

## 1. Text Extraction

### Purpose
Convert resume PDFs and DOCX files into structured text.

### Current Implementation
Simulated text extraction for demonstration. Returns sample resume text.

### Production Implementation

**For PDF Files:**
```python
import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text
```

**For DOCX Files:**
```python
from docx import Document

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
```

### Structured Parsing

After text extraction, parse into sections:

```python
def parse_resume_structure(text: str) -> dict:
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "skills": extract_skills_section(text),
    }
```

---

## 2. Skill Extraction

### Approach
Hybrid pattern matching + NLP technique.

### Skill Taxonomy

**200+ Skills across categories:**
- Programming Languages (20+)
- Web Technologies (30+)
- Databases (12+)
- Cloud & DevOps (20+)
- Data Science & ML (25+)
- Mobile Development (10+)
- Soft Skills (15+)

### Algorithm

```typescript
function extractSkills(text: string): string[] {
  const skills = [];
  const normalizedText = text.toLowerCase();
  
  // 1. Exact matching
  for (const skill of SKILL_DATABASE) {
    if (normalizedText.includes(skill.toLowerCase())) {
      skills.push(skill);
    }
  }
  
  // 2. Variation matching
  for (const [variation, canonical] of SKILL_VARIATIONS) {
    if (normalizedText.includes(variation)) {
      skills.push(canonical);
    }
  }
  
  // 3. Contextual extraction (future)
  // Use NER models to extract skills from context
  
  return [...new Set(skills)];
}
```

### Production Enhancement

Use Named Entity Recognition (NER):

```python
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_skills_ner(text: str) -> List[str]:
    doc = nlp(text)
    skills = []
    
    for ent in doc.ents:
        if ent.label_ in ["SKILL", "TECHNOLOGY"]:
            skills.append(ent.text)
    
    return skills
```

Or fine-tune BERT for skill extraction:

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification

model = AutoModelForTokenClassification.from_pretrained(
    "jjzha/jobbert-base-cased"
)
tokenizer = AutoTokenizer.from_pretrained("jjzha/jobbert-base-cased")
```

---

## 3. Embedding Generation

### Purpose
Generate semantic vector representations capturing meaning beyond keywords.

### Vector Dimensions
**384-dimensional** vectors (standard for sentence transformers).

### Current Implementation
Simulated deterministic embeddings based on text features.

### Production Implementation

**Using Sentence Transformers:**

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> List[float]:
    """Generate 384-dim semantic embedding."""
    embedding = model.encode(text)
    return embedding.tolist()
```

**Alternative: OpenAI Embeddings:**

```python
import openai

def generate_embedding_openai(text: str) -> List[float]:
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']
```

### Embedding Strategy

**For Resumes:**
```
embedding = encode(
    name + "\n" + 
    summary + "\n" +
    experience_descriptions + "\n" +
    skills
)
```

**For Jobs:**
```
embedding = encode(
    title + "\n" +
    description + "\n" +
    "Required Skills: " + skills
)
```

---

## 4. Similarity Calculation

### Cosine Similarity

Primary metric for comparing embeddings:

```typescript
function cosineSimilarity(vec1: number[], vec2: number[]): number {
  let dotProduct = 0;
  let norm1 = 0;
  let norm2 = 0;
  
  for (let i = 0; i < vec1.length; i++) {
    dotProduct += vec1[i] * vec2[i];
    norm1 += vec1[i] * vec1[i];
    norm2 += vec2[i] * vec2[i];
  }
  
  return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
}
```

**Range:** -1 to 1 (higher = more similar)

### Other Metrics

**Euclidean Distance:**
```typescript
function euclideanDistance(vec1: number[], vec2: number[]): number {
  let sum = 0;
  for (let i = 0; i < vec1.length; i++) {
    sum += Math.pow(vec1[i] - vec2[i], 2);
  }
  return Math.sqrt(sum);
}
```

**Dot Product:**
```typescript
function dotProduct(vec1: number[], vec2: number[]): number {
  return vec1.reduce((sum, val, i) => sum + val * vec2[i], 0);
}
```

---

## 5. Matching Algorithm

### Multi-Factor Scoring

```typescript
interface MatchScore {
  skillScore: number;      // 0-1
  experienceScore: number; // 0-1
  semanticScore: number;   // 0-1
  overallScore: number;    // 0-1
}
```

### Weighted Formula

```
Overall = (w1 × Skill) + (w2 × Experience) + (w3 × Semantic)
```

**Default Weights:**
- w1 (Skill): 0.4
- w2 (Experience): 0.3
- w3 (Semantic): 0.3

### Component Calculations

#### Skill Score

Jaccard similarity with weighted required vs. preferred:

```typescript
function calculateSkillScore(
  candidateSkills: string[],
  requiredSkills: string[],
  preferredSkills: string[]
): number {
  let score = 0;
  let totalWeight = 0;
  
  // Required skills (weight 1.0)
  for (const skill of requiredSkills) {
    totalWeight += 1.0;
    if (candidateSkills.includes(skill)) {
      score += 1.0;
    }
  }
  
  // Preferred skills (weight 0.5)
  for (const skill of preferredSkills) {
    totalWeight += 0.5;
    if (candidateSkills.includes(skill)) {
      score += 0.5;
    }
  }
  
  return totalWeight > 0 ? score / totalWeight : 0;
}
```

#### Experience Score

Alignment with job level requirements:

```typescript
const levelMap = {
  internship: { min: 0, max: 1 },
  entry: { min: 0, max: 2 },
  mid: { min: 2, max: 5 },
  senior: { min: 5, max: 100 },
};

function calculateExperienceScore(
  candidateYears: number,
  jobLevel: string
): number {
  const required = levelMap[jobLevel];
  
  if (candidateYears >= required.min && 
      candidateYears <= required.max) {
    return 1.0; // Perfect match
  }
  
  if (candidateYears < required.min) {
    const deficit = required.min - candidateYears;
    return Math.max(0, 1.0 - deficit * 0.2);
  }
  
  const excess = candidateYears - required.max;
  return Math.max(0.5, 1.0 - excess * 0.1);
}
```

#### Semantic Score

Normalized cosine similarity:

```typescript
function calculateSemanticScore(
  resumeEmbedding: number[],
  jobEmbedding: number[]
): number {
  const similarity = cosineSimilarity(resumeEmbedding, jobEmbedding);
  
  // Normalize from [-1, 1] to [0, 1]
  return (similarity + 1) / 2;
}
```

---

## 6. Ranking

### Top-K Selection

Return top K matches sorted by overall score:

```typescript
function rankMatches(
  matches: Match[],
  k: number = 10
): Match[] {
  return matches
    .sort((a, b) => b.overallScore - a.overallScore)
    .slice(0, k);
}
```

### Diversity Filtering (Optional)

Ensure diversity in top results:

```typescript
function diversifyResults(
  matches: Match[],
  diversityFactor: number = 0.3
): Match[] {
  // Balance between relevance and diversity
  // Avoid showing only similar jobs
}
```

---

## 7. Explanation Generation

### Purpose
Provide human-readable insights into match scores.

### Components

```typescript
interface MatchExplanation {
  summary: string;
  strengths: string[];
  gaps: string[];
  recommendations: string[];
  skillBreakdown: {
    matched: string[];
    missing: string[];
    additional: string[];
  };
}
```

### Generation Logic

```typescript
function generateExplanation(
  match: MatchScore,
  candidateSkills: string[],
  requiredSkills: string[]
): MatchExplanation {
  const summary = generateSummary(match.overallScore);
  const strengths = analyzeStrengths(match);
  const gaps = analyzeGaps(candidateSkills, requiredSkills);
  const recommendations = generateRecommendations(gaps);
  
  return { summary, strengths, gaps, recommendations, ... };
}
```

---

## 8. Performance Optimization

### Batch Processing

Process multiple embeddings in parallel:

```python
def batch_generate_embeddings(texts: List[str]) -> List[List[float]]:
    embeddings = model.encode(texts, batch_size=32)
    return embeddings.tolist()
```

### Caching

Cache embeddings to avoid recomputation:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text_hash: str) -> List[float]:
    # Return cached or compute
    pass
```

### Vector Indexing

For large-scale search, use approximate nearest neighbor:

```python
import faiss

# Create FAISS index
index = faiss.IndexFlatIP(384)  # Inner product for cosine
index.add(np.array(embeddings))

# Search
distances, indices = index.search(query_embedding, k=10)
```

---

## 9. Evaluation Metrics

### Precision@K

Percentage of relevant items in top K:

```python
def precision_at_k(relevant: set, predicted: list, k: int) -> float:
    top_k = set(predicted[:k])
    return len(top_k & relevant) / k
```

### NDCG (Normalized Discounted Cumulative Gain)

Ranking quality metric:

```python
def ndcg_at_k(relevance_scores: list, k: int) -> float:
    dcg = sum(
        (2**rel - 1) / np.log2(i + 2)
        for i, rel in enumerate(relevance_scores[:k])
    )
    ideal = sorted(relevance_scores, reverse=True)
    idcg = sum(
        (2**rel - 1) / np.log2(i + 2)
        for i, rel in enumerate(ideal[:k])
    )
    return dcg / idcg if idcg > 0 else 0
```

### Mean Reciprocal Rank

Average position of first relevant result:

```python
def mrr(relevant: set, predicted: list) -> float:
    for i, item in enumerate(predicted):
        if item in relevant:
            return 1 / (i + 1)
    return 0
```

---

## 10. Model Replacement Guide

The system is designed for easy model swapping:

### Step 1: Create Model Wrapper

```python
# models/embedding_model.py

class EmbeddingModel:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
    
    def batch_encode(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()
```

### Step 2: Update Configuration

```python
# config.py

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# or
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
# or
EMBEDDING_MODEL = "openai:text-embedding-ada-002"
```

### Step 3: Retrain/Re-embed

```bash
python scripts/regenerate_embeddings.py
```

---

## Future Enhancements

- [ ] Fine-tune BERT on resume-job pairs
- [ ] Add attention weights for explainability
- [ ] Multi-modal matching (include work samples, portfolios)
- [ ] Temporal decay for experience recency
- [ ] Active learning from recruiter feedback
- [ ] Transfer learning from similar domains

---

## References

- [Sentence-BERT Paper](https://arxiv.org/abs/1908.10084)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Hugging Face Transformers](https://huggingface.co/transformers/)
