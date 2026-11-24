# 🎯 AI Resume-to-Job Matcher

> **An intelligent AI-powered platform that analyzes your resume against target job descriptions, computes real-time ATS match scores, generates grounded improvement suggestions, and compares multiple job offers side-by-side.**

---

## 🌟 What is this Project? (In Simple Words)

When you apply for a job, companies use **Applicant Tracking Systems (ATS)** and recruiters to scan your resume. If your resume lacks the right keywords, technical skills, or clear bullet points, it gets rejected before a human even reads it.

**ResumeMatch** solves this problem:
1. **Upload your resume** (PDF or Word document).
2. **Paste one or more job descriptions**.
3. **Get an instant, honest match percentage (0–100%)** based on real skills, semantic meaning, experience, and education.
4. **See exactly what skills you have and what you are missing**.
5. **Get AI-powered suggestions** to rewrite weak bullet points using strong action verbs (without making up fake facts).
6. **Download a professional PDF report** or **compare multiple job offers** to see which one fits you best!

---

## 🚀 Key Features

### 📄 1. Smart Resume & Job Extraction
- Upload resumes in **PDF** or **DOCX (Word)** format.
- Automatically extracts text using **PyMuPDF** and **python-docx**.
- Intelligently organizes content into 5 core sections:
  - *Professional Summary*
  - *Technical Skills*
  - *Work Experience*
  - *Featured Projects*
  - *Education & Credentials*
- Automatically parses job descriptions to detect required vs. preferred qualifications, required years of experience, and degree requirements.

### 🔍 2. Advanced Skill Matching & Canonical Synonyms
- Identifies **200+ modern engineering and domain skills** across Frontend, Backend, Cloud/DevOps, AI/ML, Mobile, and Testing.
- Smart synonym mapping resolves real-world variations:
  - `JS` / `Vanilla JS` ➔ `JavaScript`
  - `TS` ➔ `TypeScript`
  - `K8s` ➔ `Kubernetes`
  - `Postgres` ➔ `PostgreSQL`
  - `React.js` ➔ `React`
  - `FastAPI` / `Django` / `Flask` ➔ Categorized frameworks
- Properly handles punctuation-containing skills like **`C++`**, **`C#`**, **`.NET`**, **`Node.js`**, **`Vue.js`**, and **`CI/CD`**.
- Categorizes skills into:
  - ✅ **Matched Skills** (with synonym detection details)
  - ⚠️ **Missing Required Skills** (critical mandatory gaps)
  - 💡 **Missing Preferred Skills** (bonus opportunities)

### 🧠 3. Semantic AI Embeddings & Meaning Fit
- Uses the pre-trained **`all-MiniLM-L6-v2`** Sentence-Transformer model.
- Converts resume text and job description into **384-dimensional numerical vectors (embeddings)**.
- Computes **Cosine Similarity** to measure the contextual alignment and overall role duties, even if the wording is different.

### 📊 4. Interactive Analysis Dashboard
- **Overall Match Percentage (0–100%)**: Weighted calculation combining skills (40%), semantic meaning (35%), and experience tenure (25%).
- **Composite ATS Readiness Score & Grade**: Evaluates Skills (35%), Semantic Fit (25%), Experience (20%), Education (10%), and ATS Layout Hygiene (10%) with letter grades (**A+**, **A**, **B**, **C**, **D**).
- **Experience Match**: Compares candidate years of experience against job seniority requirements (e.g. 5+ years vs required 3+ years).
- **Education Match**: Checks highest academic degree against role requirements.
- **AI Bullet Point Rewrites**: Rewrites passive phrases (e.g. *"worked on APIs"*) into high-impact executive statements (e.g. *"Architected and deployed high-throughput FastAPI microservices"*).
- **Strict Anti-Hallucination Guardrail**: Never invents fake skills, companies, dates, or metrics not present in the candidate's original resume.
- **📥 Download PDF Report**: Generates an executive, print-ready PDF report with charts, skill breakdown, and personalized recommendations via **ReportLab**.

### 🔐 5. Database & User Authentication
- **User Signup & Login**: Secure account registration with input validation.
- **Bcrypt Password Hashing**: Passwords are securely hashed; plain-text passwords are never stored.
- **JWT (JSON Web Tokens)**: Secure token-based session authentication with automatic header attachment.
- **Protected Routes**: Restricts private pages (like Dashboard and History) to logged-in users.
- **MongoDB Integration**: Stores user profiles, uploaded resumes, job descriptions, and match reports.
- **Zero-Crash Resilience**: Seamlessly falls back to an in-memory database engine (`mongomock`) when running in offline or local environments without a running MongoDB daemon.
- **History Drawer**: Review past reports, inspect previous resumes, reload past analyses in one click, and delete individual records.

### 🏆 6. Multi-Job Comparison & Ranking
- Upload **1 resume** and add **2 to 8 job postings** simultaneously.
- Compares your resume against all jobs in one go.
- **Automatic Ranking**: Ranks roles from **#1 (Best Match)** to **#N (Lowest Match)**.
- **Top Recommendation Hero Banner**: Highlights your best-fit offer, why it fits, and key candidate strengths.
- **Side-by-Side Comparison Matrix Table**: Compare Match %, ATS Grade, Skills Score, Semantic Similarity, and Experience Fit across all jobs at a glance.
- **Cross-Job Trend Insights**: Identifies which missing skills are shared across multiple roles (e.g., *"Docker and Kubernetes appear in 3 out of 4 roles"*).
- **One-Click In-Depth Inspection**: Click any compared job to instantly load its complete detailed report in the main dashboard!

### 🛡️ 7. Privacy & Permanent Data Erasure
- **Secure File Storage**: Uploaded files are renamed with unique UUIDs, protected against directory traversal, and given restricted file permissions (`0o600`).
- **Permanent File Deletion**: Deleting a resume record physically unlinks and removes the file from disk.
- **Bulk Clear**: One-click actions to clear all report history or delete all resumes.
- **Permanent Account Erasure**: "Delete Account & All Data" endpoint that completely wipes user credentials, resumes, files, jobs, and history.

---

## 🛠️ Tech Stack & Technologies

### Frontend
- **Framework**: [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Routing**: [React Router DOM v7](https://reactrouter.com/)
- **State Management**: React Context (`AuthContext`) + Session Storage

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **NLP & Embeddings**: [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`), [PyTorch](https://pytorch.org/)
- **Document Extractors**: [PyMuPDF](https://pymupdf.readthedocs.io/) (PDF), [python-docx](https://python-docx.readthedocs.io/) (Word)
- **PDF Generation**: [ReportLab](https://www.reportlab.com/)
- **Database**: [MongoDB](https://www.mongodb.com/) via [PyMongo](https://pymongo.readthedocs.io/) & [Motor](https://motor.readthedocs.io/) (with [mongomock](https://github.com/mongomock/mongomock) fallback)
- **Security & Auth**: [Bcrypt](https://pypi.org/project/bcrypt/), [Passlib](https://passlib.readthedocs.io/), [PyJWT](https://pyjwt.readthedocs.io/)

---

## 📂 Project Structure

```text
resume-job-matcher/
├── README.md                          # Main project documentation (this file)
├── .gitignore                         # Git exclusion rules
│
├── backend/                           # FastAPI Python Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py                # Auth dependencies & DB session injection
│   │   │   └── v1/
│   │   │       ├── api.py             # Main v1 API router
│   │   │       └── endpoints/         # Modular REST endpoints
│   │   │           ├── auth.py        # /signup, /login, /me
│   │   │           ├── resume.py      # /resume/upload, extract text & skills
│   │   │           ├── job.py         # /job/extract, parse requirements
│   │   │           ├── skills.py      # /skills/match, synonym resolution
│   │   │           ├── embeddings.py  # /embeddings/similarity, cosine similarity
│   │   │           ├── dashboard.py   # /dashboard/analyze, ATS scoring
│   │   │           ├── compare.py     # /compare/multi-jobs, ranking
│   │   │           ├── report.py      # /report/download-pdf, PDF generator
│   │   │           ├── user_data.py   # /user/resumes, /user/analyses, /user/account
│   │   │           └── llm.py         # /llm/suggestions, AI rewrites
│   │   ├── core/
│   │   │   ├── config.py              # Environment settings & CORS
│   │   │   └── security.py            # Bcrypt hashing & JWT token utils
│   │   ├── db/
│   │   │   └── mongodb.py             # MongoDB connection manager + mongomock
│   │   ├── schemas/                   # Pydantic request/response models
│   │   └── services/                  # Business logic & AI algorithms
│   │       ├── parser_service.py      # PDF/DOCX text & skill parsing
│   │       ├── skill_matcher_service.py # Skill matching & synonym dictionary
│   │       ├── embedding_service.py   # Sentence-Transformers embeddings
│   │       ├── dashboard_service.py   # ATS scoring & experience evaluation
│   │       ├── comparison_service.py  # Multi-job comparison & ranking
│   │       ├── pdf_report_service.py  # ReportLab PDF report generation
│   │       ├── storage_service.py     # Secure file upload & deletion
│   │       └── llm_service.py         # Grounded AI suggestion engine
│   ├── main.py                        # FastAPI entrypoint
│   ├── requirements.txt               # Backend dependencies
│   ├── test_phase5.py                 # Auth & database tests
│   ├── test_phase6.py                 # Multi-job comparison & deletion tests
│   ├── test_e2e_security.py           # User isolation security tests
│   └── test_accuracy_benchmark.py     # 36-case accuracy benchmark suite
│
└── frontend/                          # React + Vite Frontend
    ├── src/
    │   ├── context/
    │   │   └── AuthContext.jsx        # User authentication & token management
    │   ├── components/
    │   │   ├── Navbar.jsx             # Responsive navigation with user profile
    │   │   ├── Footer.jsx             # Clean footer
    │   │   ├── ProtectedRoute.jsx     # Route protection guard
    │   │   └── Hero.jsx               # Landing page hero
    │   ├── pages/
    │   │   ├── Home.jsx               # Homepage with feature overview
    │   │   ├── Login.jsx              # Sign In page
    │   │   ├── Signup.jsx             # Sign Up page
    │   │   ├── ResumeUpload.jsx       # Resume upload & parsing UI
    │   │   ├── JobDescription.jsx     # Job description extractor UI
    │   │   ├── AnalysisDasboard.jsx   # Match dashboard, charts & PDF download
    │   │   └── MultiJobComparison.jsx # Phase 6 Multi-Job Comparison matrix
    │   ├── App.jsx                    # Route configuration
    │   └── main.jsx                   # React root entry
    ├── package.json                   # Frontend dependencies
    └── vite.config.js                 # Vite bundler config
```

---

## ⚡ Step-by-Step Setup & How to Run

### Prerequisites
Make sure you have installed on your computer:
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Git**

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/vanshkesarwani/resume-job-matcher.git
cd resume-job-matcher
```

---

### Step 2: Set Up & Run the Backend

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # On macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows (Command Prompt):
   # python -m venv venv
   # venv\Scripts\activate
   ```

3. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - *(Optional)* Add your `GEMINI_API_KEY` or `OPENAI_API_KEY` in `backend/.env` if you wish to use live LLMs. If left blank, the system automatically uses its high-fidelity grounded NLP engine without needing external API keys.

5. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   - **Backend API**: `http://localhost:8000`
   - **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

### Step 3: Set Up & Run the Frontend

1. Open a **new terminal window** and navigate to the `frontend` directory:
   ```bash
   cd resume-job-matcher/frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - **Frontend Web App**: `http://localhost:5173`

---

## 🧪 Running the Automated Test Suite

The project includes automated integration tests and a comprehensive accuracy benchmark suite:

```bash
cd backend
source venv/bin/activate

# 1. Run Auth & Database Integration Tests
python test_phase5.py

# 2. Run Multi-Job Comparison & Permanent Deletion Tests
python test_phase6.py

# 3. Run End-to-End Security & User Isolation Tests
python test_e2e_security.py

# 4. Run the 36-Case Resume-to-Job Accuracy Benchmark
python test_accuracy_benchmark.py
```

All 36 benchmark cases validate that:
- Exact/strong role matches score between **70% and 98%**.
- Partial/adjacent skill matches score between **45% and 70%**.
- Extreme mismatches (e.g. Nurse vs Kubernetes SRE) score **below 40%**.
- Result: **36/36 Passed (100% Accuracy)**.

---

## 📖 How to Use the Application

1. **Sign Up / Log In**:
   - Create your personal account at `/signup` or log in at `/login`.
2. **Upload Your Resume**:
   - Go to `/upload` and upload your PDF or Word document.
   - The app extracts your skills, experience years, education, and bullet points.
3. **Analyze a Single Job Posting**:
   - Go to `/job-description` and paste any job posting.
   - Click **"Proceed to Resume Match"** to view your overall score, ATS readiness grade, matched skills, missing skills, and AI suggestions.
   - Click **"Download PDF Report"** to save a professional PDF summary.
4. **Compare Multiple Job Offers**:
   - Go to `/compare` (or click **"Compare Jobs"** in the top navigation bar).
   - Click **"Load 3 Sample Roles"** (or add your own job descriptions).
   - Click **"Compare All Job Postings"** to see your ranked leaderboard and side-by-side comparison matrix!
5. **Manage History & Privacy**:
   - Open the **"History & Saved Reports"** drawer from your dashboard to reload past reports or delete uploaded files permanently.

---

## 🛠️ How to Update and Push Changes to GitHub

Whenever you make improvements or changes to your project, use these 3 simple commands in your terminal:

```bash
# 1. Stage all changed files
git add .

# 2. Commit your changes with a message describing what you did
git commit -m "feat: your update message here"

# 3. Push to your GitHub repository
git push origin main
```

---

## 📜 License
This project is open-source and available under the **MIT License**.
