# Phase 0 Findings

A. `matchAPI` methods:
  - `matchResumeToJobs(resumeId: string): Promise<APIResponse<Match[]>>`
    - MOCK: Retrieves resume and jobs from dataStore, executes ML pipeline in browser, stores in `dataStore.matches`.
  - `matchJobToCandidates(jobId: string): Promise<APIResponse<Match[]>>`
    - MOCK: Same as above, but for job -> resumes.
  - `getMatchesByStudent(studentId: string): Promise<APIResponse<Match[]>>`
    - MOCK: Returns from `dataStore.matches`.
  - `getMatchesByRecruiter(recruiterId: string): Promise<APIResponse<Match[]>>`
    - MOCK: Returns from `dataStore.matches`.
  - `getMatchesByJob(jobId: string): Promise<APIResponse<Match[]>>`
    - MOCK: Returns from `dataStore.matches`.
  - `updateMatchStatus(matchId: string, status: Match['status']): Promise<APIResponse<Match>>`
    - MOCK: Updates status in `dataStore.matches`.

B. `resumeAPI`, `jobAPI`, `authAPI` methods:
  - `authAPI`:
    - `login(credentials: LoginForm): Promise<APIResponse<AuthResponse>>`
      - REAL: hits `POST /auth/login`, saves `access_token` and `current_user` in `localStorage`.
    - `signup(formData: SignupForm): Promise<APIResponse<AuthResponse>>`
      - REAL: hits `POST /auth/signup`, saves `access_token` and `current_user` in `localStorage`.
    - `logout(): Promise<APIResponse<void>>`
      - REAL: hits `POST /auth/logout`, clears `localStorage`.
    - `getCurrentUser(): User | null`
      - REAL: reads `current_user` from `localStorage`.
  - `resumeAPI`:
    - `upload(file: File, userId: string): Promise<APIResponse<Resume>>`
      - REAL: hits `POST /resumes/upload`, uses fetch with `getAuthHeaders` and `FormData`.
    - `getByUser(userId: string): Promise<APIResponse<Resume[]>>`
      - REAL: hits `GET /resumes/user/{userId}`, uses `apiRequest`.
    - `getById(resumeId: string): Promise<APIResponse<Resume>>`
      - REAL: hits `GET /resumes/{resumeId}`, uses `apiRequest`.
    - `delete(resumeId: string): Promise<APIResponse<void>>`
      - REAL: hits `DELETE /resumes/{resumeId}`, uses `apiRequest`.
  - `jobAPI`:
    - `create(jobData: JobPostingForm, recruiterId: string): Promise<APIResponse<Job>>`
      - REAL: hits `POST /jobs`, passes payload.
    - `getByRecruiter(recruiterId: string): Promise<APIResponse<Job[]>>`
      - REAL: hits `GET /jobs/recruiter/{recruiterId}`.
    - `getAll(): Promise<APIResponse<Job[]>>`
      - REAL: hits `GET /jobs`.
    - `getById(jobId: string): Promise<APIResponse<Job>>`
      - REAL: hits `GET /jobs/{jobId}`.
    - `update(jobId: string, updates: Partial<Job>): Promise<APIResponse<Job>>`
      - REAL: hits `PUT /jobs/{jobId}`.
    - `delete(jobId: string): Promise<APIResponse<void>>`
      - REAL: hits `DELETE /jobs/{jobId}`.

C. `APIResponse<T>` shape:
  ```typescript
  export interface APIResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
    timestamp: string;
  }
  ```

D. Exact field names:
  - `Match`: id, resumeId, jobId, studentId, recruiterId, overallScore, skillScore, experienceScore, semanticScore, matchedSkills, missingSkills, explanation (MatchExplanation), createdAt, status.
  - `Resume`: id, userId, fileName, fileUrl, fileSize, uploadedAt, extractedText, extractedSkills, education, experience, embeddingVector, status, metadata.
  - `Job`: id, recruiterId, title, company, description, requiredSkills, preferredSkills, experienceLevel, location, locationType, salary, postedAt, expiresAt, status, embeddingVector, metadata.
  - `User`: id, email, name, role, createdAt, updatedAt.

E. Auth token attachment:
  - Handled directly in `apiService.tsx`. `apiRequest` function accepts `options.headers` which are spread out. The caller passes `headers: getAuthHeaders()` in every `apiService` method. `apiRequest` itself does NOT attach from `localStorage`.

F. Does `apiRequest` read from `localStorage`?
  - NO. `getAuthHeaders()` reads from `localStorage` and is called by the individual API methods (`authAPI`, `resumeAPI`, `jobAPI`). However, `apiRequest` itself only defaults `Content-Type`. I need to apply Phase 4b to inject it automatically so I don't need to specify `headers: getAuthHeaders()` everywhere. Wait, the prompt implies adding it if it doesn't exist inside `apiRequest()`.

G. `localStorage` keys:
  - `access_token`
  - `current_user`

H. `StudentDashboard` calls:
  - `useResumes(user?.id) -> uploadResume`
  - `useMatches(user?.id, 'student') -> matchResume`
  - Uses `dataStore.jobs.get(jobId)` directly inside `.map` logic to get job! (Mock Data Leak 1)
  - Also uses `dataStore.jobs.get(selectedMatch.jobId)` for `MatchDetailDialog`. (Mock Data Leak 2)

I. `RecruiterDashboard` calls:
  - `useJobs(user?.id) -> createJob`
  - `useMatches(user?.id, 'recruiter') -> matchJob`
  - Uses `dataStore.matches` directly in `JobCard`. (Mock Data Leak 1)
  - Uses `dataStore.resumes.get(match.resumeId)`, `dataStore.users.get(match.studentId)`, `dataStore.jobs.get(match.jobId)` heavily inside the candidate mapping and `.getResumeById`, `.getUserById`. (Mock Data Leaks 2, 3, 4)

J. `app.config.ts` content:
  - `AppConfig` exported as const object (default config shape). No `export const USE_MOCK_API = ...`. Instead, the file ends with `export type Environment = ...`. The last key-value pair of `AppConfig` object is `matchThresholds`.

K. `VITE_USE_MOCK` flag?
  - Doesn't exist currently.

L. Path confirmed: Yes.
