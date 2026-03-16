# API Documentation

## Overview

This document describes the REST API endpoints for the AI Resume Matching Platform.

**Base URL:** `http://localhost:8000/api/v1`

---

## Authentication

### POST /auth/login

Authenticate a user and create a session.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "student" | "recruiter"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "student",
      "createdAt": "2025-01-01T00:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "message": "Login successful",
  "timestamp": "2025-01-31T12:00:00Z"
}
```

### POST /auth/signup

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "role": "student" | "recruiter"
}
```

**Response:** Same structure as login (with `"message": "Account created successfully"`)

### POST /auth/logout

End the current session.

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-01-31T12:00:00Z"
}
```

---

## Resumes

### POST /resumes/upload

Upload and process a resume file.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (PDF or DOCX, max 5MB)

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "resume-uuid",
    "userId": "user-uuid",
    "fileName": "resume.pdf",
    "fileUrl": "https://storage/resumes/...",
    "fileSize": 1024000,
    "uploadedAt": "2025-01-31T12:00:00Z",
    "extractedText": "Resume content...",
    "extractedSkills": ["Python", "JavaScript", "React"],
    "status": "completed",
    "embeddingVector": [0.1, 0.2, ...]
  }
}
```

### GET /resumes/user/:userId

Get all resumes for a user.

**Response:**
```json
{
  "success": true,
  "data": [
    { /* Resume object */ }
  ]
}
```

### GET /resumes/:resumeId

Get a specific resume by ID.

### DELETE /resumes/:resumeId

Delete a resume.

---

## Jobs

### POST /jobs

Create a new job posting.

**Request:**
```json
{
  "title": "Software Engineering Intern",
  "company": "Google Inc.",
  "description": "Job description...",
  "requiredSkills": ["Python", "Java", "Algorithms"],
  "preferredSkills": ["Docker", "Kubernetes"],
  "experienceLevel": "internship" | "entry" | "mid" | "senior",
  "location": "Mountain View, CA",
  "locationType": "onsite" | "remote" | "hybrid",
  "salary": {
    "min": 7000,
    "max": 9000,
    "currency": "USD"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "job-uuid",
    "recruiterId": "recruiter-uuid",
    "title": "Software Engineering Intern",
    /* ... other fields */
    "embeddingVector": [0.1, 0.2, ...],
    "status": "active",
    "postedAt": "2025-01-31T12:00:00Z"
  }
}
```

### GET /jobs

Get all active jobs.

**Query Parameters:**
- `status` - Filter by status (active, closed, draft)
- `experienceLevel` - Filter by level
- `location` - Filter by location
- `page` - Page number (default: 1)
- `pageSize` - Items per page (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [/* Job objects */],
    "total": 100,
    "page": 1,
    "pageSize": 10,
    "totalPages": 10
  }
}
```

### GET /jobs/recruiter/:recruiterId

Get jobs posted by a recruiter.

### GET /jobs/:jobId

Get a specific job by ID.

### PUT /jobs/:jobId

Update a job posting.

### DELETE /jobs/:jobId

Delete a job posting.

---

## Matching

### POST /matches/resume/:resumeId

Find matching jobs for a resume.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "match-uuid",
      "resumeId": "resume-uuid",
      "jobId": "job-uuid",
      "studentId": "student-uuid",
      "recruiterId": "recruiter-uuid",
      "overallScore": 0.85,
      "skillScore": 0.90,
      "experienceScore": 0.80,
      "semanticScore": 0.85,
      "matchedSkills": ["Python", "React"],
      "missingSkills": ["Docker"],
      "explanation": {
        "summary": "Excellent match! Strong qualifications.",
        "strengths": ["Strong skill alignment", "..."],
        "gaps": ["Limited Docker experience"],
        "recommendations": ["Consider learning Docker"],
        "skillBreakdown": {
          "matched": ["Python", "React"],
          "missing": ["Docker"],
          "additional": ["TypeScript"]
        }
      },
      "status": "pending",
      "createdAt": "2025-01-31T12:00:00Z"
    }
  ]
}
```

### POST /matches/job/:jobId

Find matching candidates for a job.

**Response:** Similar to above

### GET /matches/student/:studentId

Get all matches for a student.

### GET /matches/recruiter/:recruiterId

Get all matches for a recruiter's jobs.

### GET /matches/job/:jobId

Get all matches for a specific job.

### PATCH /matches/:matchId/status

Update match status.

**Request:**
```json
{
  "status": "pending" | "viewed" | "shortlisted" | "rejected"
}
```

---

## Analytics

### GET /analytics/student/:studentId

Get student dashboard statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "resumesUploaded": 2,
    "matchesFound": 15,
    "averageScore": 0.78,
    "topMatchedRoles": ["Software Engineer", "Data Analyst"]
  }
}
```

### GET /analytics/recruiter/:recruiterId

Get recruiter dashboard statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "activeJobs": 5,
    "totalCandidates": 120,
    "shortlistedCandidates": 25,
    "averageMatchScore": 0.72
  }
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2025-01-31T12:00:00Z"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Rate Limiting

- **Public endpoints:** 60 requests/minute
- **Authenticated endpoints:** 300 requests/minute
- **Upload endpoints:** 10 requests/minute

Headers returned:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1612137600
```

---

## Pagination

Paginated responses include:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "pageSize": 10,
  "totalPages": 10
}
```

---

## WebSocket Events (Future)

Real-time updates for match processing:

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/matches');

// Events
{
  "event": "match_found",
  "data": { /* Match object */ }
}

{
  "event": "processing_complete",
  "data": { "resumeId": "...", "matchCount": 5 }
}
```
