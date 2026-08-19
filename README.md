# AI Code Review & Debugging Assistant

A full-stack, production-ready AI Code Review and Debugging platform built with **Python**, **FastAPI**, **PostgreSQL**, **React**, **Python AST**, **Ruff**, **Bandit**, **Radon**, and **Ollama (`qwen2.5-coder:7b`)**.

---

## 🌟 Overview & Features

1. **User Authentication & Scoping**: Secure JWT token authentication with bcrypt password hashing and user-scoped data access.
2. **Deterministic Static Analysis Pipeline**:
   - **AST Analyzer**: Inspects abstract syntax trees for mutable default arguments, bare `except:` clauses, dangerous `eval()`/`exec()`, nested loops, unreachable code, and bad style patterns.
   - **Ruff Linting**: Automated multi-rule lint and style violation parsing into severity levels.
   - **Bandit Security Auditing**: Safe AST-level static security scan (detects hardcoded credentials, command injections, weak hashes, insecure random generators, unsafe imports).
   - **Radon Complexity & Maintainability**: Computes Cyclomatic Complexity (CC), Maintainability Index (MI), Raw LOC/SLOC/Comments metrics.
3. **Deterministic Scoring Engine**:
   - Baseline 100 points, deterministic deductions:
     - `CRITICAL`: -15 pts
     - `HIGH`: -8 pts
     - `MEDIUM`: -4 pts
     - `LOW`: -1 pt
   - Sub-score breakdown: **Overall**, **Security**, **Quality**, **Performance**, **Maintainability**.
4. **Local AI Engine via Ollama**:
   - Primary AI provider communicates with local `qwen2.5-coder:7b` through the Ollama HTTP API (`/api/generate`).
   - Validates JSON output strictly against Pydantic schemas with automated retry logic and fallback mechanisms.
   - Generates AI bug insights, security remediations, performance enhancements, and improved **Fixed Code**.
5. **Multi-Source Input Support**:
   - Interactive Monaco Code Editor with syntax highlighting.
   - Direct `.py` file upload via multipart endpoints.
   - Direct GitHub Repository URL scanning (scans multiple files, ignores binaries/virtualenvs, and generates repo-level health metrics).
6. **Dashboard & History**:
   - Interactive analytics charts (Recharts Radar & Bar graphs).
   - Review history management with instant inspection and deletion.

---

## 📐 System Architecture

```
                         USER
                          |
                          ↓
                   React Frontend (Vite + Tailwind + Monaco)
                          |
                       REST API (HTTP / Bearer JWT)
                          |
                          ↓
                    FastAPI Backend
                          |
        ┌─────────────────┼─────────────────┐
        |                 |                 |
        ↓                 ↓                 ↓
 Authentication     Review Engine      GitHub Service
        |                 |
        ↓                 ↓
   PostgreSQL       Analysis Pipeline
                          |
             ┌────────────┼────────────┐
             |            |            |
             ↓            ↓            ↓
           AST          Ruff        Bandit
         Analyzer      Analyzer     Analyzer
             |            |            |
             └────────────┼────────────┘
                          |
                          ↓
                   Radon Complexity
                          |
                          ↓
                   Scoring Engine
                          |
                          ↓
                    Ollama Service (HTTP API)
                          |
                          ↓
                  Qwen2.5-Coder 7B
                          |
                          ↓
                 AI Review & Fixed Code
                          |
                          ↓
                    PostgreSQL
                          |
                          ↓
                   React Dashboard
```

---

## 🛠 Technology Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.0, PostgreSQL, Alembic, Pydantic v2, PyJWT, Passlib/Bcrypt, Httpx, Pytest.
- **Static Analysis**: Python AST (`ast`), Ruff (`ruff`), Bandit (`bandit`), Radon (`radon`).
- **AI / LLM**: Ollama HTTP API with `qwen2.5-coder:7b` (and `MockAIProvider` for offline test isolation).
- **Frontend**: React 18, Vite, Tailwind CSS, Monaco Editor (`@monaco-editor/react`), Recharts, Lucide React, Axios, React Router v6.
- **DevOps**: Docker, Docker Compose, Makefile.

---

## 🚀 Step-by-Step Installation & Setup

### 1. Prerequisites
Ensure you have the following installed on your machine:
- Python 3.12+
- Node.js 18+ & npm
- PostgreSQL 14+
- Ollama (`https://ollama.com`)

---

### 2. Ollama Local Setup
Verify that Ollama is installed and running:

```bash
# Check version
ollama --version

# Start Ollama service (if not running as background app)
ollama serve &

# Pull the coding LLM model
ollama pull qwen2.5-coder:7b

# Verify model presence
ollama list
```

---

### 3. PostgreSQL Setup
Create the application database:

```bash
# Using createdb CLI
createdb code_reviewer

# Or using psql
psql -U postgres -c "CREATE DATABASE code_reviewer;"
```

---

### 4. Backend Setup & Run

```bash
# Navigate to backend directory
cd backend

# Create and activate Python 3.12 virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Run Alembic migrations
alembic upgrade head

# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be active at: `http://localhost:8000`
- Swagger Interactive Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

---

### 5. Frontend Setup & Run

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Frontend will be active at: `http://localhost:5173`

---

### 6. Running Automated Tests

Run the complete test suite (runs 100% offline using `MockAIProvider` and in-memory SQLite):

```bash
cd backend
source .venv/bin/activate
pytest -v
```

---

### 7. Docker Deployment (Optional)

Run the full stack with PostgreSQL and FastAPI in Docker:

```bash
docker compose up --build -d
```

> **Note for Docker & Ollama:** When backend runs inside Docker on macOS, it connects to Ollama on the host via `http://host.docker.internal:11434`.

---

## 🧪 Sample Code Files

Check the [`sample_code/`](./sample_code) folder for test inputs:
- `buggy.py`: Contains mutable default arguments, bare excepts, dead code, and unhandled variables.
- `insecure.py`: Contains hardcoded credentials, `exec`/`eval`, shell injection, weak MD5, and SQL injection patterns.
- `complex.py`: High cyclomatic complexity decision matrices and 3-level nested loops.
- `clean.py`: Clean PEP-8 compliant Python class with type annotations.
