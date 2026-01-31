# Project Architecture & Folder Structure

## Overview

This document describes the complete folder structure and organization of the AI Resume Matching Platform.

---

## Directory Tree

```
ai-resume-matcher/
├── src/                           # Source code
│   ├── app/                       # React application
│   │   ├── components/            # Reusable UI components
│   │   │   ├── ui/               # shadcn/ui component library
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   └── ... (30+ components)
│   │   │   ├── MatchScoreCard.tsx     # Match visualization
│   │   │   ├── SkillBadgeList.tsx     # Skill display
│   │   │   └── figma/                 # Figma integration components
│   │   │       └── ImageWithFallback.tsx
│   │   ├── layouts/               # Layout components
│   │   │   └── RootLayout.tsx
│   │   ├── pages/                 # Page components
│   │   │   ├── auth/             # Authentication pages
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   └── SignupPage.tsx
│   │   │   ├── student/          # Student dashboard
│   │   │   │   └── StudentDashboard.tsx
│   │   │   ├── recruiter/        # Recruiter dashboard
│   │   │   │   └── RecruiterDashboard.tsx
│   │   │   ├── LandingPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── routes.ts             # React Router configuration
│   │   └── App.tsx               # Root application component
│   │
│   ├── services/                  # Business logic & APIs
│   │   ├── api/                  # API service layer
│   │   │   ├── apiService.ts     # API client functions
│   │   │   └── mockData.ts       # In-memory data store
│   │   └── ml/                   # ML pipeline
│   │       ├── textExtraction.ts      # Resume parsing
│   │       ├── skillExtraction.ts     # Skill identification
│   │       ├── embeddings.ts          # Vector generation
│   │       ├── matchingEngine.ts      # Matching algorithm
│   │       └── pipeline.ts            # Pipeline orchestrator
│   │
│   ├── contexts/                  # React Context providers
│   │   └── AuthContext.tsx       # Authentication state
│   │
│   ├── hooks/                     # Custom React hooks
│   │   └── useData.ts            # Data fetching hooks
│   │
│   ├── types/                     # TypeScript definitions
│   │   └── models.ts             # Data models & interfaces
│   │
│   ├── config/                    # Configuration
│   │   └── app.config.ts         # Application config
│   │
│   ├── database/                  # Database schemas
│   │   └── schema.ts             # PostgreSQL schema definition
│   │
│   ├── utils/                     # Utility functions
│   │   ├── helpers.ts            # General helpers
│   │   ├── logger.ts             # Logging utility
│   │   └── validation.ts         # Input validation
│   │
│   └── styles/                    # Global styles
│       ├── fonts.css             # Font imports
│       ├── index.css             # Main stylesheet
│       ├── tailwind.css          # Tailwind directives
│       └── theme.css             # Theme variables
│
├── docs/                          # Documentation
│   ├── API.md                    # API documentation
│   ├── ML_PIPELINE.md            # ML system details
│   ├── DEPLOYMENT.md             # Deployment guide
│   └── ARCHITECTURE.md           # This file
│
├── public/                        # Static assets
│   └── favicon.ico
│
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Multi-container setup
├── nginx.conf                     # Nginx configuration
├── package.json                   # NPM dependencies
├── tsconfig.json                  # TypeScript configuration
├── vite.config.ts                 # Vite build config
├── postcss.config.mjs             # PostCSS config
└── README.md                      # Project README
```

---

## Module Descriptions

### `/src/app/` - Frontend Application

Main React application with pages, components, and routing.

**Key Files:**
- `App.tsx` - Root component with RouterProvider
- `routes.ts` - Route definitions
- `pages/` - Top-level page components
- `components/` - Reusable UI components

### `/src/services/` - Business Logic

All non-UI logic including API calls and ML processing.

#### `/src/services/api/`
Mock API layer simulating backend:
- `apiService.ts` - API functions (auth, resumes, jobs, matches)
- `mockData.ts` - In-memory data store

#### `/src/services/ml/`
Machine learning pipeline:
- `textExtraction.ts` - Extract text from files
- `skillExtraction.ts` - Identify skills using NLP
- `embeddings.ts` - Generate semantic vectors
- `matchingEngine.ts` - Calculate match scores
- `pipeline.ts` - Orchestrate entire workflow

### `/src/contexts/` - Global State

React Context providers for shared state:
- `AuthContext.tsx` - User authentication state

### `/src/hooks/` - Custom Hooks

Reusable React hooks:
- `useData.ts` - Data fetching (resumes, jobs, matches)

### `/src/types/` - Type Definitions

TypeScript interfaces and types:
- `models.ts` - Complete data model definitions

### `/src/config/` - Configuration

Centralized app configuration:
- `app.config.ts` - Environment-based settings

### `/src/database/` - Database Schema

PostgreSQL schema definitions:
- `schema.ts` - Complete SQL schema

### `/src/utils/` - Utilities

Helper functions:
- `helpers.ts` - General purpose utilities
- `logger.ts` - Structured logging
- `validation.ts` - Input validation

---

## Data Flow

### User Upload Flow
```
User uploads resume
    ↓
StudentDashboard calls uploadResume()
    ↓
useData hook → apiService.uploadResume()
    ↓
processResume() in ml/pipeline.ts
    ↓
1. extractTextFromFile()
2. extractSkills()
3. generateEmbedding()
    ↓
Resume stored in dataStore
    ↓
matchResume() triggered
    ↓
matchResumeToJobs() in matchingEngine.ts
    ↓
Matches displayed in UI
```

### Matching Flow
```
Resume Embedding (384-dim) ──┐
                              │
                              ├─→ cosineSimilarity() ──→ Semantic Score
                              │
Job Embedding (384-dim) ──────┘

Resume Skills ────┐
                  ├─→ calculateSkillScore() ──→ Skill Score
Job Skills ───────┘

Resume Experience ──┐
                    ├─→ calculateExperienceScore() ──→ Experience Score
Job Level ──────────┘

                    ↓
          Weighted Combination
                    ↓
            Overall Match Score
                    ↓
           Ranking & Explanation
```

---

## Component Hierarchy

```
App
├── AuthProvider
└── RouterProvider
    └── RootLayout
        ├── LandingPage
        ├── LoginPage
        ├── SignupPage
        ├── StudentDashboard
        │   ├── Stats Cards
        │   ├── Tabs (Upload, Matches, Resumes)
        │   ├── ResumeCard
        │   ├── MatchScoreCard
        │   └── MatchDetailDialog
        └── RecruiterDashboard
            ├── Stats Cards
            ├── Tabs (Jobs, Candidates)
            ├── JobCard
            ├── CreateJobDialog
            └── CandidateDetailDialog
```

---

## State Management

### Global State (Context)
- **AuthContext**: User session, login/logout

### Component State (Hooks)
- **useResumes**: Resume data fetching and mutations
- **useJobs**: Job data fetching and mutations
- **useMatches**: Match data fetching and mutations

### Local State (useState)
- Component-specific UI state
- Form inputs
- Dialog visibility

---

## Routing Structure

```
/ (Root)
├── / (Landing Page)
├── /login (Login)
├── /signup (Signup)
├── /student (Student Dashboard) - Protected
├── /recruiter (Recruiter Dashboard) - Protected
└── * (404 Not Found)
```

---

## API Endpoints (Mock)

### Authentication
- `POST /auth/login`
- `POST /auth/signup`
- `POST /auth/logout`

### Resumes
- `POST /resumes/upload`
- `GET /resumes/user/:userId`
- `GET /resumes/:resumeId`
- `DELETE /resumes/:resumeId`

### Jobs
- `POST /jobs`
- `GET /jobs`
- `GET /jobs/recruiter/:recruiterId`
- `GET /jobs/:jobId`
- `PUT /jobs/:jobId`
- `DELETE /jobs/:jobId`

### Matching
- `POST /matches/resume/:resumeId`
- `POST /matches/job/:jobId`
- `GET /matches/student/:studentId`
- `GET /matches/recruiter/:recruiterId`
- `PATCH /matches/:matchId/status`

---

## Database Schema

### Tables
- `users` - User accounts
- `student_profiles` - Student metadata
- `recruiter_profiles` - Recruiter metadata
- `resumes` - Resume files and extracted data
- `jobs` - Job postings
- `embeddings` - Vector representations
- `matches` - Match results
- `match_history` - Status change log

---

## Technology Stack

### Frontend
- React 18 + TypeScript
- React Router 7
- Tailwind CSS v4
- shadcn/ui components
- Vite build tool

### Backend (Mock)
- In-memory data store
- Simulated async operations
- Production: FastAPI + PostgreSQL

### ML Pipeline
- Simulated embeddings
- Pattern-based skill extraction
- Production: Sentence Transformers

---

## Development Workflow

1. **Make changes** in `/src`
2. **Test locally** with `npm run dev`
3. **Build** with `npm run build`
4. **Deploy** with Docker

---

## Scalability Considerations

### Frontend
- Code splitting by route
- Lazy loading for heavy components
- Asset optimization (images, fonts)

### Backend
- Horizontal scaling with load balancer
- Caching layer (Redis)
- CDN for static assets

### ML Pipeline
- Batch processing for embeddings
- Vector index (FAISS) for fast search
- GPU acceleration for models

### Database
- Read replicas for queries
- Connection pooling
- Partitioning for large tables

---

## Security

### Frontend
- XSS prevention (input sanitization)
- CSRF protection
- Secure cookie handling

### Backend
- JWT authentication
- Rate limiting
- Input validation
- SQL injection prevention

### Database
- Row-level security (RLS)
- Encrypted connections
- Regular backups

---

## Monitoring

### Metrics to Track
- API response times
- Match generation latency
- Error rates
- User activity (signups, uploads, matches)

### Logging
- Structured JSON logs
- Error tracking (Sentry)
- Performance monitoring (New Relic)

---

## Future Architecture

### Microservices Split
```
API Gateway
├── Auth Service
├── Resume Service
├── Job Service
├── ML Service (GPU)
└── Analytics Service
```

### Message Queue
- Celery + RabbitMQ for async jobs
- Webhooks for notifications
- Event-driven architecture

---

For more details, see:
- [API Documentation](./API.md)
- [ML Pipeline](./ML_PIPELINE.md)
- [Deployment Guide](./DEPLOYMENT.md)
