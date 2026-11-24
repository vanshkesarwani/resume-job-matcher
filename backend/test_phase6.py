"""
Automated Integration and Unit Tests for Phase 6 (Multi-Job Comparison & Permanent Deletion).
Tests:
- Step 16: Multi-Job Comparison endpoint (ranks jobs from highest to lowest match score,
  calculates percentage, matched & missing skills for each job)
- Step 17: Punctuation-containing skills accuracy (C++, C#, .NET, Node.js, Next.js)
- Step 18: Permanent deletion of resumes, analyses, comparisons, and account
"""
import os
from pathlib import Path
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

SAMPLE_RESUME = """
ALICE DEVELOPER
Senior Full-Stack Engineer | Python, React, AWS
Email: alice@example.com | San Francisco, CA

PROFESSIONAL SUMMARY:
Senior Full-Stack Engineer with 6+ years of hands-on experience designing, developing,
and scaling high-throughput web applications and cloud architectures. Proficient in Python,
FastAPI, Django, React, TypeScript, C++, PostgreSQL, and Docker.

TECHNICAL SKILLS:
- Languages: Python, JavaScript, TypeScript, C++, SQL, HTML, CSS
- Frontend: React, Next.js, Redux, Tailwind CSS
- Backend: FastAPI, Django, Node.js, REST APIs, Microservices
- Databases: PostgreSQL, MongoDB, Redis
- Cloud & DevOps: Docker, Kubernetes, AWS, CI/CD, Git, Linux

WORK EXPERIENCE:
Senior Software Engineer | TechScale Solutions (2020 - Present)
- Architected and built high-performance microservices using FastAPI, Python, and PostgreSQL.
- Implemented real-time dashboard interfaces using React, TypeScript, and Tailwind CSS.
- Deployed containerized applications with Docker and automated deployments using CI/CD pipelines on AWS.

Software Engineer | CloudForge (2018 - 2020)
- Developed backend endpoints with Django and REST APIs.
- Maintained legacy microservices built with C++ and Linux.
"""

JOB_PYTHON = """
Job Title: Senior Backend Engineer
Company: CloudScale
Requirements:
- 5+ years experience in Python and FastAPI.
- Strong knowledge of PostgreSQL, Redis, Docker, and REST APIs.
- Experience with AWS and CI/CD pipelines.
"""

JOB_DEVOPS = """
Job Title: Lead DevOps & Infrastructure Engineer
Company: InfraOps
Requirements:
- 7+ years of dedicated DevOps and Platform Engineering.
- Mastery of Terraform, Ansible, Kubernetes, Helm, ArgoCD, Prometheus, Grafana.
- Deep Linux kernel tuning and cloud networking on Azure and GCP.
"""

JOB_FRONTEND = """
Job Title: Senior Frontend Developer
Company: PixelCraft
Requirements:
- 4+ years of professional Frontend experience.
- Expert in React, TypeScript, Next.js, Tailwind CSS, and Redux.
- Good understanding of REST APIs and modern UI/UX design.
"""

def test_punctuation_skills_accuracy():
    """Step 17 Verification: Ensure C++, C#, .NET, Node.js accurately detected without regex bugs."""
    from app.services.parser_service import detect_skills_from_text
    skills = detect_skills_from_text("Candidate skilled in C++, C#, .NET, Node.js, and Python.")
    assert "C++" in skills, f"C++ missing from detected skills: {skills}"
    assert "C#" in skills, f"C# missing from detected skills: {skills}"
    assert ".NET" in skills, f".NET missing from detected skills: {skills}"
    assert "Node.js" in skills, f"Node.js missing from detected skills: {skills}"
    assert "Python" in skills, f"Python missing from detected skills: {skills}"
    print("✓ test_punctuation_skills_accuracy passed!")

def test_multi_job_comparison():
    """Step 16 Verification: Compare 1 resume against 3 distinct job descriptions."""
    # Register and log in a test user
    email = "phase6_tester@example.com"
    pwd = "Password123!"
    client.post("/api/v1/auth/signup", json={"name": "Phase 6 Tester", "email": email, "password": pwd})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "resume_text": SAMPLE_RESUME,
        "resume_filename": "Alice_Developer_Resume.pdf",
        "jobs": [
            {"job_id": "job_py", "job_title": "Senior Backend Engineer", "company": "CloudScale", "job_description": JOB_PYTHON},
            {"job_id": "job_infra", "job_title": "Lead DevOps & Infrastructure Engineer", "company": "InfraOps", "job_description": JOB_DEVOPS},
            {"job_id": "job_fe", "job_title": "Senior Frontend Developer", "company": "PixelCraft", "job_description": JOB_FRONTEND},
        ]
    }

    res = client.post("/api/v1/compare/multi-jobs", json=payload, headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["total_jobs_compared"] == 3
    assert len(data["ranked_jobs"]) == 3

    # Check ranking order: scores must be in descending order
    scores = [j["match_score"] for j in data["ranked_jobs"]]
    assert scores == sorted(scores, reverse=True), f"Jobs are not ranked descending: {scores}"

    # Check rank numbers
    for idx, job in enumerate(data["ranked_jobs"], start=1):
        assert job["rank"] == idx
        assert "matched_skills" in job
        assert "missing_skills" in job
        assert "ats_score" in job
        assert "summary" in job
        assert "key_recommendation" in job

    # Alice has strong Python + React background, so Python/Backend or Frontend should be top
    top_job = data["top_recommended_job"]
    assert top_job["job_title"] in ["Senior Backend Engineer", "Senior Frontend Developer"]
    assert top_job["match_score"] > data["ranked_jobs"][-1]["match_score"]

    # Verify history retrieval
    hist_res = client.get("/api/v1/compare/history", headers=headers)
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert len(hist) >= 1

    print("✓ test_multi_job_comparison passed!")

def test_permanent_deletion_and_security():
    """Step 18 Verification: Permanent deletion of files, history, and account."""
    # 1. Login user
    email = "phase6_tester@example.com"
    pwd = "Password123!"
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload a valid test resume file
    import pymupdf
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), SAMPLE_RESUME)
    valid_pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("test_delete.pdf", valid_pdf_bytes, "application/pdf")}
    up_res = client.post("/api/v1/resume/upload", files=files, headers=headers)
    assert up_res.status_code == 200, up_res.text

    # Verify resume appears in list
    resumes_list = client.get("/api/v1/user/resumes", headers=headers).json()
    assert len(resumes_list) >= 1
    resume_id = resumes_list[0]["id"]

    # Delete single resume permanently
    del_res = client.delete(f"/api/v1/user/resumes/{resume_id}", headers=headers)
    assert del_res.status_code == 200
    assert "permanently deleted" in del_res.json()["message"]

    # 3. Test bulk deletion of analyses
    clear_analyses = client.delete("/api/v1/user/analyses", headers=headers)
    assert clear_analyses.status_code == 200

    # 4. Test account permanent deletion
    del_account = client.delete("/api/v1/user/account", headers=headers)
    assert del_account.status_code == 200

    # Verify account is deleted (login fails)
    after_login = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert after_login.status_code == 401

    print("✓ test_permanent_deletion_and_security passed!")

if __name__ == "__main__":
    test_punctuation_skills_accuracy()
    test_multi_job_comparison()
    test_permanent_deletion_and_security()
    print("\n🎉 ALL PHASE 6 CORE BACKEND TESTS PASSED SUCCESSFULLY!")
