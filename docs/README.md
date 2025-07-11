# Resume-JD Matching System

A sophisticated system for matching resumes against job descriptions using NLP and vector similarity. The system processes both resumes and job descriptions, extracts relevant features, and provides intelligent matching based on skills, experience, and other criteria.

## 🏗️ Project Structure

```
jd_parsing/
├── db_utils.py           # Database operations for vector storage
├── education_utils.py    # Education information extraction
├── embedding_utils.py    # Text embedding generation   
├── experience_utils.py   # Experience information extraction
├── feature_extraction.py # Core feature extraction logic
├── jd_parser.py         # Job description parsing
├── matcher.py           # Resume-JD matching logic
├── search_resumes.py    # Resume search interface
└── weight_config.yml    # Matching weights configuration
```

## 📚 Core Components

### 1. Job Description Processing
- **`jd_parser.py`**: 
  - Parses job descriptions from various formats
  - Extracts key requirements, skills, experience levels
  - Generates structured JD representation
  - Input formats: JSON, plain text
  - Output: Standardized JD object with extracted features

### 2. Resume Processing
- **`feature_extraction.py`**:
  - Core logic for extracting features from resumes
  - Coordinates with specialized utils modules
  - Handles text preprocessing and normalization

- **`education_utils.py`**:
  - Extracts and standardizes education information
  - Handles degree recognition
  - Maps institutions and qualifications

- **`experience_utils.py`**:
  - Processes work experience sections
  - Extracts duration, roles, and responsibilities
  - Identifies relevant skills from experience

### 3. Vector Operations
- **`embedding_utils.py`**:
  - Generates embeddings for text using transformer models
  - Handles skill text vectorization
  - Manages embedding model loading and caching

- **`db_utils.py`**:
  - PostgreSQL + pgvector integration
  - Stores and retrieves resume vectors
  - Handles vector similarity search
  - Manages database connections and schema

### 4. Matching Engine
- **`matcher.py`**:
  - Implements core matching logic
  - Computes similarity scores
  - Applies weighted scoring across different features
  - Handles edge cases and special scenarios

- **`weight_config.yml`**:
  - Configurable weights for different matching criteria
  - Allows fine-tuning of matching importance
  - Supports different matching profiles

### 5. Search Interface
- **`search_resumes.py`**:
  - CLI interface for searching resumes
  - Handles query processing
  - Formats and displays results

## 🚀 Getting Started

### Prerequisites
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Setup
1. Install PostgreSQL with pgvector extension
2. Set up environment variables:
   ```env
   DB_HOST=your_host
   DB_PORT=5432
   DB_NAME=your_db
   DB_USER=your_user
   DB_PASSWORD=your_password
   ```

### Basic Usage
```bash
# Parse a job description
python jd_parser.py --input job_description.txt --output parsed_jd.json

# Search resumes against a JD
python search_resumes.py --jd parsed_jd.json --limit 10
```

## 🎯 Edge Cases Handled

The system is designed to handle various edge cases:

1. **Perfect Match**: Entry-level candidates with exact skill matches
2. **Overqualified**: Senior candidates applying for junior positions
3. **Fresh Graduates**: No experience but relevant projects/education
4. **Partial Matches**: Similar but not exact skill matches
5. **Career Changers**: Candidates transitioning between fields
6. **No Match**: Completely different skill sets

## 🔄 Vector Database Schema

### Resumes Table
```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    meta JSONB NOT NULL,
    skill_vec vector NOT NULL,
    exp_vec vector NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Resume Skill Vectors Table
```sql
CREATE TABLE resume_skill_vectors (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    skill_text TEXT NOT NULL,
    skill_vec vector NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Suggested Improvements

### 1. Code Structure
- Implement proper Python package structure
- Add `src` directory for source code
- Separate tests into `tests` directory
- Create `config` directory for configuration files
- Add proper logging configuration

```
resume_matcher/
├── src/
│   ├── parsers/
│   ├── extractors/
│   ├── matchers/
│   └── utils/
├── tests/
├── config/
└── docs/
```

### 2. Feature Enhancements
- Add support for more resume formats (PDF, DOCX)
- Implement caching for embeddings
- Add batch processing capabilities
- Support multiple languages
- Add resume validation and scoring
- Implement feedback loop for matching quality

### 3. Technical Improvements
- Add comprehensive test suite
- Implement proper logging
- Add input validation
- Improve error handling
- Add API documentation
- Implement rate limiting
- Add monitoring and metrics

### 4. Performance Optimizations
- Implement batch vector operations
- Add caching layer
- Optimize database queries
- Add connection pooling
- Implement async operations where applicable

### 5. DevOps Improvements
- Add CI/CD pipeline
- Implement containerization
- Add monitoring and alerting
- Implement backup strategy
- Add deployment documentation

### 6. Security Enhancements
- Add input sanitization
- Implement proper authentication
- Add role-based access control
- Implement secure credential management
- Add audit logging

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers. 