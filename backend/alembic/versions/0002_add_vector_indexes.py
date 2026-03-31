"""Add pgvector indexes for semantic similarity search

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgvector extension is enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Add Vector column to jobs table
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='jobs'
                AND column_name='job_embedding_vector'
            ) THEN
                ALTER TABLE jobs
                ADD COLUMN job_embedding_vector vector(384);
            END IF;
        END$$;
    """)

    # Convert embeddings.vector from float[] to vector(384) if needed
    # This is safe because both types store the same data
    op.execute("""
        DO $$
        BEGIN
            -- Only alter if column type is not already vector
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='embeddings'
                AND column_name='vector'
                AND data_type != 'USER-DEFINED'
            ) THEN
                ALTER TABLE embeddings
                ALTER COLUMN vector TYPE vector(384)
                USING vector::vector(384);
            END IF;
        END$$;
    """)

    # Create IVFFlat indexes for approximate nearest neighbor search
    # IVFFlat is faster than exact search for large datasets
    # lists=100 is optimal for datasets up to ~1M vectors

    # Index on embeddings table
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_embeddings_vector_ivfflat
        ON embeddings
        USING ivfflat (vector vector_cosine_ops)
        WITH (lists = 100);
    """)

    # Index on jobs table
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_jobs_embedding_vector_ivfflat
        ON jobs
        USING ivfflat (job_embedding_vector vector_cosine_ops)
        WITH (lists = 100);
    """)


def downgrade() -> None:
    op.execute(
        "DROP INDEX CONCURRENTLY IF EXISTS idx_embeddings_vector_ivfflat;"
    )
    op.execute(
        "DROP INDEX CONCURRENTLY IF EXISTS idx_jobs_embedding_vector_ivfflat;"
    )
    op.execute(
        "ALTER TABLE jobs DROP COLUMN IF EXISTS job_embedding_vector;"
    )
    # Revert embeddings.vector back to float[] type
    op.execute("""
        ALTER TABLE embeddings
        ALTER COLUMN vector TYPE float[]
        USING vector::float[];
    """)
