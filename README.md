# AI-Driven Resume & Internship Matching Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

> **Production-ready ML platform for intelligent resume-to-job matching using semantic embeddings, skill extraction, and multi-factor ranking algorithms.**

Built for technical interviews, placements, and demonstrating full-stack ML engineering expertise.

---

## 🎯 Project Overview

This platform demonstrates a **complete AI/ML system** that:

- **Extracts** structured data from resume PDFs/DOCX files
- **Analyzes** skills using NLP and pattern matching
- **Generates** semantic embeddings for resumes and job descriptions
- **Matches** candidates to roles using cosine similarity and weighted scoring
- **Ranks** results by skill overlap, experience fit, and semantic relevance
- **Explains** match scores with human-readable insights

### Key Features

- 🧠 **AI-Powered Matching Engine** - Multi-factor scoring algorithm
- 📄 **Resume Processing Pipeline** - Text extraction, skill extraction, embedding generation
- 🎯 **Semantic Similarity** - Vector-based matching beyond keyword search
- 📊 **Match Analytics** - Score breakdowns and explanations
- 👥 **Dual User Roles** - Separate experiences for students and recruiters
- 🔒 **Role-Based Access** - Secure authentication and authorization
- ⚡ **Real-Time Processing** - Instant match results
- 📱 **Responsive Design** - Works on desktop and mobile

---

## 🏗️ Architecture

### System Design

```
┌─────────────────┐
│   Frontend      │  React + TypeScript + Tailwind CSS
│   (User Layer)  │  Student & Recruiter Dashboards
└────────┬────────┘
         │
┌────────▼────────┐
│   API Layer     │  RESTful service interfaces
│   (Service)     │  Authentication, CRUD operations
└────────┬────────┘
         │
┌────────▼────────┐
│   ML Pipeline   │  Processing & Matching Engine
│   (ML Layer)    │  ├─ Text Extraction
│                 │  ├─ Skill Extraction
│                 │  ├─ Embedding Generation
│                 │  └─ Matching Algorithm
└────────┬────────┘
         │
┌────────▼────────┐
│   Data Layer    │  PostgreSQL + Vector Store
│   (Storage)     │  Users, Jobs, Resumes, Matches
└─────────────────┘
```

### ML Pipeline Flow

```
Resume Upload → Text Extraction → Skill Extraction → Embedding → Match Scoring → Ranked Results
                                                           ↓
Job Posting   → Skill Parsing   → Embedding Generation ────┘
```

### Matching Algorithm

The system uses a **weighted multi-factor scoring model**:

```
Overall Score = (0.4 × Skill Score) + (0.3 × Experience Score) + (0.3 × Semantic Score)
```

- **Skill Score**: Jaccard similarity of required vs. candidate skills
- **Experience Score**: Alignment between years of experience and job level
- **Semantic Score**: Cosine similarity of embedding vectors

---

## 📁 Project Structure

```
ai-resume-matcher/
├── src/
│   ├── app/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── MatchScoreCard.tsx
│   │   │   └── SkillBadgeList.tsx
│   │   ├── layouts/           # Layout components
│   │   │   └── RootLayout.tsx
│   │   ├── pages/             # Page components
│   │   │   ├── auth/          # Login, Signup
│   │   │   ├── student/       # Student Dashboard
│   │   │   ├── recruiter/     # Recruiter Dashboard
│   │   │   ├── LandingPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── routes.ts          # React Router configuration
│   │   └── App.tsx            # Root component
│   ├── services/
│   │   ├── api/               # API service layer
│   │   │   ├── apiService.ts  # API calls
│   │   │   └── mockData.ts    # In-memory data store
│   │   └── ml/                # ML pipeline
│   │       ├── textExtraction.ts      # Resume text parsing
│   │       ├── skillExtraction.ts     # NLP skill extraction
│   │       ├── embeddings.ts          # Vector embeddings
│   │       ├── matchingEngine.ts      # Matching algorithm
│   │       └── pipeline.ts            # Pipeline orchestrator
│   ├── contexts/              # React Context providers
│   │   └── AuthContext.tsx
│   ├── hooks/                 # Custom React hooks
│   │   └── useData.ts
│   ├── types/                 # TypeScript definitions
│   │   └── models.ts
│   ├── config/                # Configuration
│   │   └── app.config.ts
│   ├── database/              # Database schemas
│   │   └── schema.ts          # PostgreSQL DDL
│   ├── utils/                 # Utility functions
│   │   ├── helpers.ts
│   │   ├── logger.ts
│   │   └── validation.ts
│   └── styles/                # Global styles
├── docs/                      # Documentation
│   ├── API.md                # API documentation
│   ├── ML_PIPELINE.md        # ML system details
│   └── DEPLOYMENT.md         # Deployment guide
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Multi-container setup
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/pnpm
- (Optional) Docker for containerized deployment

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-resume-matcher
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   ```
   http://localhost:5173
   ```

### Demo Login Credentials

**Student Account:**
- Email: `john.doe@university.edu`
- Password: `demo123`

**Recruiter Account:**
- Email: `jane.recruiter@google.com`
- Password: `demo123`

---

## 🧪 Usage Guide

### For Students

1. **Sign up** with student role
2. **Upload your resume** (PDF or DOCX)
3. **View matches** - AI instantly finds relevant internships
4. **Review match scores** - See skill alignment and recommendations

### For Recruiters

1. **Sign up** with recruiter role
2. **Post a job** with requirements and description
3. **Find candidates** - AI matches qualified candidates
4. **Review profiles** - See ranked candidates with match explanations

---

## 🧠 ML Pipeline Details

### 1. Text Extraction

```typescript
// Simulates PDF/DOCX parsing
const { text } = await extractTextFromFile(file);
```

**Production Implementation:**
- Use `pdf-parse` for PDF files
- Use `mammoth.js` for DOCX files

### 2. Skill Extraction

```typescript
const { skills, categories } = extractSkills(text);
```

**Features:**
- Pattern matching against 200+ technical skills
- Categorization: technical, soft skills, tools
- Skill normalization (e.g., "react.js" → "React")

### 3. Embedding Generation

```typescript
const embedding = await generateEmbedding(text);
```

**Current:** Simulated sentence embeddings (384-dim vectors)

**Production:** Replace with:
- Sentence-Transformers (`all-MiniLM-L6-v2`)
- OpenAI Embeddings API
- Custom BERT fine-tuned model

### 4. Matching Algorithm

```typescript
const matches = matchResumeToJobs(resume, jobs, topK);
```

**Scoring Formula:**
```
overallScore = 0.4 × skillScore + 0.3 × experienceScore + 0.3 × semanticScore
```

### 5. Ranking & Explanation

Generates human-readable explanations:
- Strengths (matched qualifications)
- Gaps (missing skills/experience)
- Recommendations (improvement suggestions)

---

## 📊 Database Schema

### Core Tables

```sql
users               -- User accounts (students & recruiters)
student_profiles    -- Extended student data
recruiter_profiles  -- Extended recruiter data
resumes            -- Uploaded resumes + extracted data
jobs               -- Job postings
embeddings         -- Vector embeddings (384-dim)
matches            -- Match results with scores
match_history      -- Status change tracking
```

See [/src/database/schema.ts](./src/database/schema.ts) for full schema.

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# ML Configuration
ML_EMBEDDING_DIM=384
ML_SIMILARITY_THRESHOLD=0.6
ML_TOP_K_MATCHES=10

# Feature Flags
ENABLE_REALTIME_MATCHING=true
ENABLE_SKILL_EXTRACTION=true
```

### Adjustable Parameters

Edit `/src/config/app.config.ts`:

```typescript
ml: {
  skillWeightage: 0.4,        // Weight for skill matching
  experienceWeightage: 0.3,   // Weight for experience
  semanticWeightage: 0.3,     // Weight for semantic similarity
  topK: 10,                   // Number of matches to return
}
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t ai-resume-matcher .

# Run container
docker run -p 3000:80 ai-resume-matcher
```

### Docker Compose (Full Stack)

```bash
docker-compose up
```

This starts:
- Frontend (React)
- Backend API (FastAPI) - *to be implemented*
- PostgreSQL database
- pgvector for similarity search

---

## 🧪 Testing & Evaluation

### Match Quality Metrics

Evaluate matching performance:

```bash
npm run evaluate
```

Metrics:
- **Precision@K**: % of relevant matches in top K
- **NDCG**: Ranking quality score
- **Mean Reciprocal Rank**: Position of first relevant match

### Manual Testing

Test with sample data:

```bash
npm run test:matching
```

---

## 🚀 Production Deployment

### Backend Implementation

To make this production-ready, implement:

1. **FastAPI Backend**
   ```python
   # app/main.py
   from fastapi import FastAPI
   from sentence_transformers import SentenceTransformer
   
   app = FastAPI()
   model = SentenceTransformer('all-MiniLM-L6-v2')
   
   @app.post("/api/resumes/upload")
   async def upload_resume(file: UploadFile):
       # Process resume
       pass
   ```

2. **PostgreSQL with pgvector**
   ```sql
   CREATE EXTENSION vector;
   ALTER TABLE embeddings 
   ALTER COLUMN vector TYPE vector(384);
   CREATE INDEX ON embeddings 
   USING ivfflat (vector vector_cosine_ops);
   ```

3. **Async Processing**
   - Use Celery for background jobs
   - Redis for job queue
   - Webhook notifications

### Scaling Considerations

- **Horizontal Scaling**: Stateless API servers behind load balancer
- **Caching**: Redis for frequently accessed matches
- **Vector Search**: Use FAISS or Pinecone for large-scale similarity search
- **CDN**: CloudFront for static assets

---

## 📚 Additional Documentation

- [API Documentation](./docs/API.md) - Endpoint specifications
- [ML Pipeline](./docs/ML_PIPELINE.md) - Deep dive into algorithms
- [Deployment Guide](./docs/DEPLOYMENT.md) - Production setup
- [Contributing](./CONTRIBUTING.md) - Development guidelines

---

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **React Router** - Navigation
- **Tailwind CSS v4** - Styling
- **shadcn/ui** - Component library
- **Recharts** - Data visualization

### Backend (Mock)
- Mock API layer with in-memory data
- Production: **FastAPI**, **PostgreSQL**, **Redis**

### ML/NLP
- Simulated embeddings (replace with real models)
- Pattern-based skill extraction
- Cosine similarity matching

### DevOps
- **Vite** - Build tool
- **Docker** - Containerization
- **Git** - Version control

---

## 🎓 Learning Objectives

This project demonstrates:

✅ **Full-Stack Development** - React frontend + API design  
✅ **ML System Design** - Pipeline architecture, model integration  
✅ **NLP Techniques** - Text extraction, embeddings, similarity  
✅ **Database Design** - Relational schema, indexing, RLS  
✅ **Software Engineering** - Clean code, modularity, testing  
✅ **System Architecture** - Scalable, maintainable design

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) file

---

## 👥 Author

Built for technical interviews and placement demonstrations.

**Contact:**
- Portfolio: [Your Portfolio URL]
- LinkedIn: [Your LinkedIn]
- Email: [Your Email]

---

## 🙏 Acknowledgments

- shadcn/ui for component library
- Sentence Transformers for NLP inspiration
- React and Vite communities

---

## 📈 Future Enhancements

- [ ] Real ML model integration (BERT, GPT embeddings)
- [ ] Resume parsing with pdfplumber/pytesseract
- [ ] Multi-language support
- [ ] Video interview scheduling
- [ ] Applicant tracking system (ATS)
- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] A/B testing framework

---

**⭐ If this project helped you, please star the repository!**
