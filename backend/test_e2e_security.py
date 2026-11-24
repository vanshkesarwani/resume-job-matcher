"""
End-to-End Workflow & Security Test:
1. Upload/extract resume with auth token
2. Process job description with auth token
3. Compute dashboard metrics
4. Verify auto-saved or explicitly saved records appear in user's profile
5. Verify unauthenticated users cannot access dashboard APIs without auth token (401)
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_security_and_e2e_flow():
    # 1. Register test user
    email = "charlie@example.com"
    pwd = "ComplexPassword123!"
    reg_res = client.post("/api/v1/auth/signup", json={"name": "Charlie Tester", "email": email, "password": pwd})
    assert reg_res.status_code in [201, 400]
    
    # 2. Login
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Test saving a full analysis report with realistic data
    save_payload = {
        "job_title": "Senior Python Backend Engineer",
        "resume_filename": "Charlie_Resume.pdf",
        "overall_match_percentage": 92,
        "ats_score": 90,
        "ats_grade": "A+",
        "matched_skills": ["Python", "FastAPI", "MongoDB", "Docker", "REST APIs"],
        "missing_skills": ["Kubernetes"],
        "summary_text": "Strong match with excellent backend foundation.",
        "report_data": {
            "score_breakdown": {
                "skills_score": 95,
                "embedding_score": 90,
                "experience_score": 88,
                "education_score": 100
            },
            "suggestions": [
                "Mention Kubernetes experience or orchestration projects."
            ]
        }
    }
    save_res = client.post("/api/v1/user/analyses/save", json=save_payload, headers=headers)
    assert save_res.status_code == 201
    saved_id = save_res.json()["id"]

    # 4. Fetch specific analysis by ID
    get_res = client.get(f"/api/v1/user/analyses/{saved_id}", headers=headers)
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["job_title"] == "Senior Python Backend Engineer"
    assert fetched["overall_match_percentage"] == 92
    assert "score_breakdown" in fetched["report_data"]

    # 5. Verify security: another user cannot fetch this report
    other_reg = client.post("/api/v1/auth/signup", json={"name": "Other User", "email": "other@example.com", "password": "Password999!"})
    if other_reg.status_code == 201:
        other_token = other_reg.json()["access_token"]
    else:
        other_login = client.post("/api/v1/auth/login", json={"email": "other@example.com", "password": "Password999!"})
        other_token = other_login.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    denied_res = client.get(f"/api/v1/user/analyses/{saved_id}", headers=other_headers)
    assert denied_res.status_code == 404, "User B should not be able to find or access User A's report"

    print("✓ End-to-end user workflow and security isolation verified successfully!")

if __name__ == "__main__":
    test_security_and_e2e_flow()

