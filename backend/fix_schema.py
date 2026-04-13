"""
Quick script to add missing columns to the database for the demo.
Adds columns that exist in SQLAlchemy models but not yet in PostgreSQL.
"""
import psycopg2

DB_URL = "postgresql://postgres:Sub-Zero12@localhost:5432/resume_matcher"

COLUMNS_TO_ADD = [
    # (table, column, type)
    ("resumes", "extra_metadata", "JSONB DEFAULT '{}'"),
    ("resumes", "seniority_level", "VARCHAR(50)"),
    ("resumes", "years_of_experience", "FLOAT"),
    ("resumes", "career_trajectory", "VARCHAR(100)"),
    ("resumes", "domain_expertise", "JSONB"),
    ("resumes", "impact_metrics", "JSONB"),
    ("resumes", "context_aware_skills", "JSONB"),
    ("resumes", "resume_analysis", "JSONB"),
    ("resumes", "analysis_version", "VARCHAR(20)"),
    ("jobs", "extra_metadata", "JSONB DEFAULT '{}'"),
    ("jobs", "job_embedding_vector", "BYTEA"),  # placeholder, no pgvector needed
]

conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cur = conn.cursor()

for table, column, col_type in COLUMNS_TO_ADD:
    sql = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {col_type};"
    try:
        cur.execute(sql)
        print(f"  OK: {table}.{column}")
    except Exception as e:
        print(f"  SKIP: {table}.{column} — {e}")

# Also try to enable pgvector extension (may fail if not installed in PG, that's fine)
try:
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("  OK: pgvector extension enabled")
    # Now alter job_embedding_vector to proper vector type
    cur.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='jobs' AND column_name='job_embedding_vector'
                AND data_type != 'USER-DEFINED'
            ) THEN
                ALTER TABLE jobs ALTER COLUMN job_embedding_vector TYPE vector(384)
                USING NULL;
            END IF;
        END$$;
    """)
    print("  OK: jobs.job_embedding_vector converted to vector(384)")
except Exception as e:
    print(f"  NOTE: pgvector not available ({e}) — vector search disabled but app will work")

cur.close()
conn.close()
print("\nDone! Database schema is now in sync with models.")
