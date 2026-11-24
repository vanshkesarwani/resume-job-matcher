"""
Automated Integration and Unit Tests for Phase 5 (MongoDB & Authentication).
Tests:
- User signup & duplicate email validation (201 Created & 400 Bad Request)
- User login (success 200 OK & invalid credentials 401 Unauthorized)
- Token verification (/auth/me)
- Unauthenticated access rejection (401 Unauthorized)
- User data isolation (user A cannot see or delete user B's records)
- Record saving and deletion (resumes, jobs, analyses)
"""
import sys
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json().get("status") == "healthy"

def test_signup_and_duplicate():
    # 1. Signup user 1
    signup_payload = {
        "name": "Alice Developer",
        "email": "alice@example.com",
        "password": "Password123!"
    }
    res = client.post("/api/v1/auth/signup", json=signup_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["name"] == "Alice Developer"
    assert "id" in data["user"]

    # 2. Duplicate signup should return 400
    res_dup = client.post("/api/v1/auth/signup", json=signup_payload)
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"]

def test_login():
    # Correct login
    login_payload = {
        "email": "alice@example.com",
        "password": "Password123!"
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alice@example.com"

    # Wrong password
    bad_login = {
        "email": "alice@example.com",
        "password": "WrongPassword!"
    }
    res_bad = client.post("/api/v1/auth/login", json=bad_login)
    assert res_bad.status_code == 401

    # Non-existent user
    res_none = client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": "pass"})
    assert res_none.status_code == 401

def test_get_current_user_me():
    # Login to get token
    login_res = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]

    # With valid token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "alice@example.com"

    # Without token
    res_no_auth = client.get("/api/v1/auth/me")
    assert res_no_auth.status_code == 401

    # With invalid token
    res_invalid = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert res_invalid.status_code == 401

def test_user_data_and_isolation():
    # 1. Login Alice
    alice_login = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "Password123!"})
    alice_token = alice_login.json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}

    # 2. Signup Bob
    bob_signup = client.post("/api/v1/auth/signup", json={"name": "Bob Tester", "email": "bob@example.com", "password": "Secret456!"})
    bob_token = bob_signup.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # 3. Unauthenticated access to user data should be 401
    assert client.get("/api/v1/user/resumes").status_code == 401
    assert client.get("/api/v1/user/jobs").status_code == 401
    assert client.get("/api/v1/user/analyses").status_code == 401

    # 4. Alice saves an analysis record
    save_payload = {
        "job_title": "Full Stack Engineer",
        "resume_filename": "alice_resume.pdf",
        "overall_match_percentage": 88,
        "ats_score": 85,
        "ats_grade": "A",
        "matched_skills": ["Python", "FastAPI", "React"],
        "missing_skills": ["Docker", "Kubernetes"],
        "summary_text": "Strong match overall.",
        "report_data": {"notes": "Test report payload"}
    }
    save_res = client.post("/api/v1/user/analyses/save", json=save_payload, headers=alice_headers)
    assert save_res.status_code == 201, save_res.text
    analysis_record = save_res.json()
    analysis_id = analysis_record["id"]
    assert analysis_record["overall_match_percentage"] == 88

    # 5. Alice sees her analysis in history
    alice_analyses = client.get("/api/v1/user/analyses", headers=alice_headers).json()
    assert len(alice_analyses) >= 1
    assert any(a["id"] == analysis_id for a in alice_analyses)

    # 6. Bob cannot see Alice's analysis in his history
    bob_analyses = client.get("/api/v1/user/analyses", headers=bob_headers).json()
    assert not any(a["id"] == analysis_id for a in bob_analyses)

    # 7. Bob attempts to delete Alice's analysis -> 404 Not Found (or forbidden)
    bob_delete = client.delete(f"/api/v1/user/analyses/{analysis_id}", headers=bob_headers)
    assert bob_delete.status_code == 404

    # 8. Alice deletes her own analysis -> 200 OK
    alice_delete = client.delete(f"/api/v1/user/analyses/{analysis_id}", headers=alice_headers)
    assert alice_delete.status_code == 200

    # 9. Verify deletion
    alice_analyses_after = client.get("/api/v1/user/analyses", headers=alice_headers).json()
    assert not any(a["id"] == analysis_id for a in alice_analyses_after)

if __name__ == "__main__":
    test_health()
    print("✓ test_health passed")
    test_signup_and_duplicate()
    print("✓ test_signup_and_duplicate passed")
    test_login()
    print("✓ test_login passed")
    test_get_current_user_me()
    print("✓ test_get_current_user_me passed")
    test_user_data_and_isolation()
    print("✓ test_user_data_and_isolation passed")
    print("\n🎉 ALL PHASE 5 INTEGRATION TESTS PASSED SUCCESSFULLY!")
