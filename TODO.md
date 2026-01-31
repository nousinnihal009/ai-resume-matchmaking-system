# Backend Generation TODO

## Phase 1: Project Structure Setup
- [ ] Create backend/ directory with layered structure
- [ ] Set up Python project files (requirements.txt, Dockerfile, etc.)
- [ ] Update docker-compose.yml with backend and postgres services

## Phase 2: Database Layer
- [ ] Implement SQLAlchemy models from schema.ts
- [ ] Set up async database connection and session management
- [ ] Create database configuration and environment handling

## Phase 3: Core Components
- [ ] Implement JWT authentication utilities
- [ ] Set up password hashing and validation
- [ ] Create response models and error handling

## Phase 4: Schemas Layer
- [ ] Define Pydantic schemas for all API requests/responses
- [ ] Implement validation for auth, resumes, jobs, matches

## Phase 5: Services Layer
- [ ] Implement authentication service
- [ ] Create resume service with file handling
- [ ] Create job service
- [ ] Implement matching service

## Phase 6: ML Pipeline Layer
- [ ] Implement text extraction from PDFs/DOCX
- [ ] Create skill extraction using NLP
- [ ] Set up sentence transformers for embeddings
- [ ] Implement matching engine with scoring

## Phase 7: API Layer
- [ ] Create auth endpoints (login, signup, logout)
- [ ] Implement resume endpoints (upload, get, delete)
- [ ] Create job endpoints (create, get, update, delete)
- [ ] Implement matching endpoints
- [ ] Add analytics endpoints

## Phase 8: Integration & Testing
- [ ] Update frontend to use real API
- [ ] Test all endpoints
- [ ] Verify ML pipeline integration
