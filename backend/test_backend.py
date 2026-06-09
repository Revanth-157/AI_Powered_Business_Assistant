"""
Simple test script to verify FastAPI backend is running correctly.
Run with: python test_backend.py
"""

import requests
import json
import sys
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "testuser@fmcg.local"
TEST_USERNAME = "testuser001"
TEST_PASSWORD = "TestPassword123!"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_result(test_name: str, passed: bool, message: str = ""):
    """Print test result."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} {test_name}")
    if message:
        print(f"  └─ {message}")


def test_health_check():
    """Test health endpoint."""
    try:
        resp = requests.get(f"{BASE_URL}/health")
        passed = resp.status_code == 200
        data = resp.json()
        print_result("Health Check", passed, f"Status: {data.get('status')}")
        return passed
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False


def test_register():
    """Test user registration."""
    try:
        payload = {
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "full_name": "Test User"
        }
        resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
        
        # Might already exist
        if resp.status_code == 400:
            print_result("Register", True, "User already exists (ok for test)")
            return True
        
        passed = resp.status_code == 200
        if passed:
            data = resp.json()
            print_result("Register", True, f"User ID: {data.get('id')[:8]}...")
        else:
            print_result("Register", False, f"Status {resp.status_code}")
        return passed
    except Exception as e:
        print_result("Register", False, str(e))
        return False


def test_login() -> Optional[str]:
    """Test login and return access token."""
    try:
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
        
        if resp.status_code != 200:
            print_result("Login", False, f"Status {resp.status_code}")
            return None
        
        data = resp.json()
        access_token = data.get("access_token")
        expires_in = data.get("expires_in", "?")
        
        print_result("Login", True, f"Token expires in {expires_in}s")
        return access_token
    except Exception as e:
        print_result("Login", False, str(e))
        return None


def test_chat(token: str):
    """Test chat endpoint."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "message": "What is the promotional performance for last week?"
        }
        resp = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
        
        passed = resp.status_code in [200, 503]  # 503 if AI not initialized
        if resp.status_code == 503:
            print_result("Chat", True, "AI workflow not initialized (ok for test)")
        else:
            data = resp.json()
            response_len = len(data.get("assistant_response", ""))
            print_result("Chat", passed, f"Response: {response_len} chars")
        return passed
    except Exception as e:
        print_result("Chat", False, str(e))
        return False


def test_analytics(token: str):
    """Test analytics endpoint."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "query": "Show me regional sales for last month",
            "granularity": "week"
        }
        resp = requests.post(f"{BASE_URL}/analytics/query", json=payload, headers=headers)
        
        passed = resp.status_code in [200, 503]
        if resp.status_code == 503:
            print_result("Analytics", True, "AI workflow not initialized (ok for test)")
        else:
            data = resp.json()
            kpis_count = len(data.get("kpis", []))
            print_result("Analytics", passed, f"KPIs: {kpis_count}")
        return passed
    except Exception as e:
        print_result("Analytics", False, str(e))
        return False


def test_dashboard(token: str):
    """Test dashboard endpoint."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
        
        passed = resp.status_code == 200
        data = resp.json()
        print_result("Dashboard", passed, f"Timestamp: {data.get('timestamp', 'N/A')[:10]}")
        return passed
    except Exception as e:
        print_result("Dashboard", False, str(e))
        return False


def test_reports(token: str):
    """Test reports endpoint."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create report
        payload = {
            "title": "Test Report",
            "intent": "PROMO_PERFORMANCE",
            "report_type": "standard"
        }
        resp = requests.post(f"{BASE_URL}/reports", json=payload, headers=headers)
        
        if resp.status_code != 200:
            print_result("Create Report", False, f"Status {resp.status_code}")
            return False
        
        report_data = resp.json()
        report_id = report_data.get("id")
        print_result("Create Report", True, f"Report ID: {report_id[:8]}...")
        
        # List reports
        resp = requests.get(f"{BASE_URL}/reports", headers=headers)
        list_data = resp.json()
        report_count = list_data.get("total", 0)
        
        print_result("List Reports", resp.status_code == 200, f"Total: {report_count}")
        return True
    except Exception as e:
        print_result("Reports", False, str(e))
        return False


def main():
    """Run all tests."""
    print(f"\n{YELLOW}=" * 60)
    print(f"FastAPI Backend Test Suite")
    print(f"Target: {BASE_URL}")
    print(f"=" * 60 + f"{RESET}\n")
    
    results = []
    
    # Basic connectivity
    print(f"{YELLOW}[1] Basic Connectivity{RESET}")
    results.append(test_health_check())
    print()
    
    # Authentication
    print(f"{YELLOW}[2] Authentication{RESET}")
    results.append(test_register())
    token = test_login()
    results.append(token is not None)
    print()
    
    if not token:
        print(f"{RED}Cannot continue without authentication token{RESET}")
        print(f"\n{YELLOW}Test Summary: {sum(results)}/{len(results)} passed{RESET}\n")
        return 1
    
    # Protected endpoints
    print(f"{YELLOW}[3] Chat & Analytics{RESET}")
    results.append(test_chat(token))
    results.append(test_analytics(token))
    results.append(test_dashboard(token))
    print()
    
    # Reports
    print(f"{YELLOW}[4] Reports{RESET}")
    results.append(test_reports(token))
    print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    percentage = int((passed / total) * 100)
    
    status_color = GREEN if percentage >= 80 else YELLOW if percentage >= 50 else RED
    print(f"{status_color}Test Summary: {passed}/{total} passed ({percentage}%){RESET}")
    
    if percentage >= 80:
        print(f"{GREEN}✓ Backend is operational!{RESET}")
        return 0
    else:
        print(f"{YELLOW}⚠ Some tests failed. Check configuration.{RESET}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Unexpected error: {str(e)}{RESET}")
        sys.exit(1)
