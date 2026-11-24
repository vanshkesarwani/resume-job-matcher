# Resume Job Matcher — Backend API

FastAPI backend providing resume parsing, ATS scoring analysis, and job description matching.

## Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── analysis.py      # POST /api/v1/analysis/match
│   │       │   ├── health.py        # GET /api/v1/health
│   │       │   └── resume.py        # POST /api/v1/resume/upload
│   │       └── api.py               # Combined API v1 router
│   ├── core/
│   │   └── config.py                # App settings, CORS, and environment
│   ├── schemas/
│   │   ├── analysis.py              # Pydantic models for ATS analysis
│   │   └── resume.py                # Pydantic models for resume upload
│   └── services/
│       ├── matcher_service.py       # Scoring engine & suggestions generator
│       └── parser_service.py        # PDF/Text parsing and skill detection
├── venv/                            # Python virtual environment (ignored in git)
├── .env.example                     # Environment variables template
├── .gitignore                       # Python & environment git exclusions
├── main.py                          # FastAPI application entrypoint
└── requirements.txt                 # Project dependencies
```

## Setup & Running

### 1. Activate Virtual Environment
```bash
cd backend
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Development Server
```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Basic verification (`{"message": "Hello World"}`) |
| `GET` | `/docs` | Interactive Swagger UI API documentation |
| `GET` | `/redoc` | Alternative ReDoc documentation |
| `GET` | `/api/v1/health` | Service health status check |
| `POST` | `/api/v1/resume/upload` | Upload PDF or TXT resume to parse text & skills |
| `POST` | `/api/v1/analysis/match` | Compare resume against job description & get ATS score |

