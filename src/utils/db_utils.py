"""Database utilities for storing and retrieving resume vectors."""

import os
from typing import Dict, Any, List, Tuple, Optional
import json
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system env vars


def _vector_to_string(vec: np.ndarray) -> str:
    """Convert numpy array to PostgreSQL vector string format."""
    return '[' + ','.join(map(str, vec.tolist())) + ']'


class VectorDB:
    def __init__(self, dsn: str | None = None):
        """Connect to Postgres with pgvector."""
        if dsn:
            self.conn = psycopg2.connect(dsn)
        else:
            # Try individual parameters first (safer for special characters)
            host = os.getenv("DB_HOST")
            if host:
                print(f"🔗 Connecting to {host}...")
                self.conn = psycopg2.connect(
                    host=host,
                    port=os.getenv("DB_PORT", "5432"),
                    database=os.getenv("DB_NAME", "postgres"),
                    user=os.getenv("DB_USER", "postgres"),
                    password=os.getenv("DB_PASSWORD")
                )
            else:
                # Fall back to connection string
                database_url = os.getenv("DATABASE_URL")
                if not database_url:
                    raise ValueError(
                        "No database connection info found. Please set either:\n"
                        "1. Individual env vars: DB_HOST, DB_USER, DB_PASSWORD, etc.\n"
                        "2. DATABASE_URL connection string"
                    )
                print("🔗 Connecting via DATABASE_URL...")
                self.conn = psycopg2.connect(database_url)
        
        self._check_pgvector()
        self._ensure_tables()

    def _check_pgvector(self):
        """Verify pgvector extension is available."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector');"
            )
            if not cur.fetchone()[0]:
                raise RuntimeError(
                    "pgvector extension not found. Please run:\n"
                    "CREATE EXTENSION vector;"
                )

    def _ensure_tables(self):
        """Ensure required tables exist."""
        with self.conn.cursor() as cur:
            # Create resumes table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id SERIAL PRIMARY KEY,
                    filename TEXT UNIQUE NOT NULL,
                    meta JSONB NOT NULL,
                    skill_vec vector NOT NULL,
                    exp_vec vector NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create resume_skill_vectors table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS resume_skill_vectors (
                    id SERIAL PRIMARY KEY,
                    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
                    skill_text TEXT NOT NULL,
                    skill_vec vector NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_resume_skill_vectors_resume_id 
                ON resume_skill_vectors(resume_id);
            """)
            
            self.conn.commit()

    def get_resume_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Check if a resume with given filename exists and return its data if found."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, meta, skill_vec, exp_vec 
                FROM resumes 
                WHERE filename = %s;
                """,
                (filename,)
            )
            result = cur.fetchone()
            if result:
                return {
                    'id': result[0],
                    'meta': result[1],
                    'skill_vec': result[2],
                    'exp_vec': result[3]
                }
            return None

    def store_resume(
        self,
        filename: str,
        meta: Dict[str, Any],
        skill_vec: np.ndarray,
        exp_vec: np.ndarray,
        skill_texts: List[str],
        skill_vecs: np.ndarray,
        skip_if_exists: bool = True
    ) -> Optional[int]:
        """Store a resume and its vectors.
        
        Args:
            filename: Unique identifier for the resume
            meta: Resume metadata
            skill_vec: Mean skill vector for the resume
            exp_vec: Experience vector
            skill_texts: List of individual skill texts
            skill_vecs: Array of individual skill vectors
            skip_if_exists: If True, skip insertion if filename exists
            
        Returns:
            resume_id if stored successfully, None if skipped
        """
        # Check if resume already exists
        existing = self.get_resume_by_filename(filename)
        if existing:
            if skip_if_exists:
                print(f"⚠️ Skipping existing resume: {filename}")
                return None
            else:
                raise ValueError(f"Resume with filename '{filename}' already exists")

        try:
            with self.conn.cursor() as cur:
                # Insert main resume record
                cur.execute(
                    """
                    INSERT INTO resumes (filename, meta, skill_vec, exp_vec)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        filename,
                        json.dumps(meta),
                        _vector_to_string(skill_vec),
                        _vector_to_string(exp_vec),
                    )
                )
                resume_id = cur.fetchone()[0]

                # Batch insert individual skill vectors
                if len(skill_texts) > 0:
                    execute_values(
                        cur,
                        """
                        INSERT INTO resume_skill_vectors
                            (resume_id, skill_text, skill_vec)
                        VALUES %s;
                        """,
                        [
                            (resume_id, text, _vector_to_string(vec))
                            for text, vec in zip(skill_texts, skill_vecs)
                        ],
                    )

            self.conn.commit()
            print(f"✅ Successfully stored resume: {filename}")
            return resume_id

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to store resume {filename}: {str(e)}") from e

    def find_candidates(
        self,
        jd_skill_vec: np.ndarray,
        limit: int = 1000,
        min_similarity: float = 0.1
    ) -> List[Tuple[int, float, str, Dict[str, Any]]]:
        """Find resumes with similar mean skill vectors."""
        vec_str = _vector_to_string(jd_skill_vec)
        
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    id,
                    1 - (skill_vec <=> %s::vector) as similarity,
                    filename,
                    meta
                FROM resumes
                WHERE 1 - (skill_vec <=> %s::vector) > %s
                ORDER BY similarity DESC
                LIMIT %s;
                """,
                (vec_str, vec_str, min_similarity, limit)
            )
            results = [
                (id_, sim, filename, json.loads(meta) if isinstance(meta, str) else meta)
                for id_, sim, filename, meta in cur.fetchall()
            ]
        return results

    def get_skill_vectors(
        self, resume_id: int
    ) -> Tuple[List[str], np.ndarray]:
        """Get individual skill vectors for a resume."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT skill_text, skill_vec
                FROM resume_skill_vectors
                WHERE resume_id = %s
                ORDER BY skill_text;
                """,
                (resume_id,)
            )
            rows = cur.fetchall()
            if not rows:
                return [], np.empty((0, 384))  # Fixed dimension
            texts, vecs = zip(*rows)
            return list(texts), np.array([
                np.array(vec.strip('[]').split(','), dtype=float)
                for vec in vecs
            ])

    def close(self):
        """Close database connection."""
        self.conn.close()