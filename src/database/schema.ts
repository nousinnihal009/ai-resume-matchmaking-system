/**
 * Database Schema Definition
 * PostgreSQL schema for the AI Resume Matching Platform
 * 
 * This file serves as documentation for the database structure.
 * In a production environment, these would be implemented as migrations.
 */

export const DATABASE_SCHEMA = `

-- ==================== USERS TABLE ====================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'recruiter', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ==================== STUDENT PROFILES TABLE ====================
CREATE TABLE student_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    university VARCHAR(255),
    major VARCHAR(255),
    graduation_year INTEGER,
    phone_number VARCHAR(20),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_student_profiles_user_id ON student_profiles(user_id);

-- ==================== RECRUITER PROFILES TABLE ====================
CREATE TABLE recruiter_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company VARCHAR(255) NOT NULL,
    position VARCHAR(255),
    phone_number VARCHAR(20),
    linkedin_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recruiter_profiles_user_id ON recruiter_profiles(user_id);

-- ==================== RESUMES TABLE ====================
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    extracted_text TEXT,
    extracted_skills JSONB DEFAULT '[]',
    education JSONB DEFAULT '[]',
    experience JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_status ON resumes(status);
CREATE INDEX idx_resumes_extracted_skills ON resumes USING GIN (extracted_skills);

-- ==================== JOBS TABLE ====================
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recruiter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    required_skills JSONB DEFAULT '[]',
    preferred_skills JSONB DEFAULT '[]',
    experience_level VARCHAR(20) NOT NULL CHECK (experience_level IN ('internship', 'entry', 'mid', 'senior')),
    location VARCHAR(255) NOT NULL,
    location_type VARCHAR(20) NOT NULL CHECK (location_type IN ('onsite', 'remote', 'hybrid')),
    salary_min DECIMAL(10, 2),
    salary_max DECIMAL(10, 2),
    salary_currency VARCHAR(3) DEFAULT 'USD',
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'closed', 'draft')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jobs_recruiter_id ON jobs(recruiter_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_required_skills ON jobs USING GIN (required_skills);
CREATE INDEX idx_jobs_experience_level ON jobs(experience_level);

-- ==================== EMBEDDINGS TABLE ====================
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('resume', 'job')),
    vector FLOAT[] NOT NULL,
    dimension INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_id, entity_type)
);

CREATE INDEX idx_embeddings_entity ON embeddings(entity_id, entity_type);

-- For vector similarity search (requires pgvector extension)
-- CREATE EXTENSION IF NOT EXISTS vector;
-- ALTER TABLE embeddings ALTER COLUMN vector TYPE vector(384);
-- CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (vector vector_cosine_ops);

-- ==================== MATCHES TABLE ====================
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recruiter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    overall_score DECIMAL(5, 4) NOT NULL CHECK (overall_score >= 0 AND overall_score <= 1),
    skill_score DECIMAL(5, 4) NOT NULL,
    experience_score DECIMAL(5, 4) NOT NULL,
    semantic_score DECIMAL(5, 4) NOT NULL,
    matched_skills JSONB DEFAULT '[]',
    missing_skills JSONB DEFAULT '[]',
    explanation JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'viewed', 'shortlisted', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resume_id, job_id)
);

CREATE INDEX idx_matches_resume_id ON matches(resume_id);
CREATE INDEX idx_matches_job_id ON matches(job_id);
CREATE INDEX idx_matches_student_id ON matches(student_id);
CREATE INDEX idx_matches_recruiter_id ON matches(recruiter_id);
CREATE INDEX idx_matches_overall_score ON matches(overall_score DESC);
CREATE INDEX idx_matches_status ON matches(status);

-- ==================== MATCH HISTORY TABLE ====================
CREATE TABLE match_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_match_history_match_id ON match_history(match_id);

-- ==================== ANALYTICS EVENTS TABLE ====================
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at);

-- ==================== TRIGGERS FOR UPDATED_AT ====================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matches_updated_at BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== ROW LEVEL SECURITY POLICIES ====================
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE recruiter_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;

-- Students can only see their own data
CREATE POLICY students_own_data ON resumes
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- Recruiters can only see their own jobs
CREATE POLICY recruiters_own_jobs ON jobs
    FOR ALL
    USING (recruiter_id = current_setting('app.current_user_id')::UUID);

-- Students can see matches for their resumes
CREATE POLICY students_see_own_matches ON matches
    FOR SELECT
    USING (student_id = current_setting('app.current_user_id')::UUID);

-- Recruiters can see matches for their jobs
CREATE POLICY recruiters_see_job_matches ON matches
    FOR SELECT
    USING (recruiter_id = current_setting('app.current_user_id')::UUID);

`;

/**
 * Sample Data Generation Functions
 */
export const SAMPLE_DATA_SEEDS = `

-- Insert sample users
INSERT INTO users (id, email, password_hash, name, role) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'john.student@university.edu', '$2b$10$hashedpassword', 'John Doe', 'student'),
    ('550e8400-e29b-41d4-a716-446655440002', 'jane.recruiter@techcorp.com', '$2b$10$hashedpassword', 'Jane Smith', 'recruiter');

-- Insert sample student profile
INSERT INTO student_profiles (user_id, university, major, graduation_year) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'MIT', 'Computer Science', 2025);

-- Insert sample recruiter profile
INSERT INTO recruiter_profiles (user_id, company, position) VALUES
    ('550e8400-e29b-41d4-a716-446655440002', 'TechCorp Inc.', 'Senior Recruiter');

`;

export default DATABASE_SCHEMA;
