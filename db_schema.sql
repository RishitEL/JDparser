-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS pgvector;

-- Resume table with vectors and metadata
CREATE TABLE resumes (
    id              SERIAL PRIMARY KEY,
    filename        TEXT NOT NULL,
    meta            JSONB NOT NULL,              -- full parsed resume
    skill_vec       vector(768) NOT NULL,        -- mean skill vector for ANN
    exp_vec         vector(768) NOT NULL,        -- experience vector
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Individual skill vectors (many-to-one with resumes)
CREATE TABLE resume_skill_vectors (
    resume_id       INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    skill_text      TEXT NOT NULL,               -- the actual skill string
    skill_vec       vector(768) NOT NULL,        -- individual embedding
    PRIMARY KEY (resume_id, skill_text)
);

-- IVF index for fast ANN on mean skill vector
CREATE INDEX ON resumes 
    USING ivfflat (skill_vec vector_cosine_ops)
    WITH (lists = 100);

-- Basic btree indices
CREATE INDEX ON resume_skill_vectors(resume_id);
CREATE INDEX ON resumes(created_at);

-- Example view for debugging/monitoring
CREATE VIEW resume_stats AS
SELECT 
    r.id,
    r.filename,
    (r.meta->>'name')::text as name,
    COUNT(DISTINCT sv.skill_text) as skill_count,
    r.created_at
FROM resumes r
LEFT JOIN resume_skill_vectors sv ON sv.resume_id = r.id
GROUP BY r.id, r.filename, r.meta, r.created_at; 