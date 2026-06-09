#!/usr/bin/env python3
"""Test script for Text-to-SQL API endpoints"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001/api/v1"

# Test credentials
TEST_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test@Password123",
    "full_name": "Test User"
}

def test_authentication():
    """Test user registration and login"""
    print("\n" + "=" * 60)
    print("Test 1: Authentication")
    print("=" * 60)
    
    # Register
    print("Testing registration...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=TEST_USER
    )
    
    if response.status_code == 200:
        print("✓ Registration successful")
        user = response.json()
    else:
        print(f"⚠ Registration failed or user already exists: {response.status_code}")
        # Try to login with existing user
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        if response.status_code == 200:
            print("✓ Using existing user account")
            user = response.json()
        else:
            print(f"✗ Login failed: {response.status_code}")
            return None
    
    # Extract token
    if "access_token" in response.json():
        token = response.json()["access_token"]
        print(f"✓ Access token obtained")
        return {"Authorization": f"Bearer {token}"}
    else:
        print(f"✗ No access token in response")
        return None


def test_schema_info(headers):
    """Test getting schema information"""
    print("\n" + "=" * 60)
    print("Test 2: Get Schema Info")
    print("=" * 60)
    
    response = requests.get(
        f"{BASE_URL}/text-to-sql/schema",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Schema retrieved successfully")
        print(f"  Tables: {', '.join(data.get('tables', [])[:5])}")
        return True
    else:
        print(f"✗ Failed to retrieve schema: {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def test_sample_queries(headers):
    """Test getting sample queries"""
    print("\n" + "=" * 60)
    print("Test 3: Get Sample Queries")
    print("=" * 60)
    
    response = requests.get(
        f"{BASE_URL}/text-to-sql/samples",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        samples = data.get("samples", [])
        print(f"✓ Sample queries retrieved successfully ({len(samples)} queries)")
        for i, sample in enumerate(samples[:3], 1):
            print(f"  {i}. {sample['question']}")
        return True
    else:
        print(f"✗ Failed to retrieve samples: {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def test_validate_query(headers, sql):
    """Test SQL validation"""
    print("\n" + "=" * 60)
    print("Test 4: Validate SQL Query")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/text-to-sql/validate?sql_query={sql}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        is_valid = data.get("is_valid", False)
        validation = data.get("validation_result", {})
        print(f"✓ Validation completed")
        print(f"  Valid: {is_valid}")
        print(f"  Risk: {validation.get('estimated_risk', 'unknown')}")
        if not is_valid:
            errors = validation.get("errors", [])
            print(f"  Errors: {errors}")
        return is_valid
    else:
        print(f"✗ Validation failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def test_text_to_sql_query(headers):
    """Test complete text-to-SQL pipeline"""
    print("\n" + "=" * 60)
    print("Test 5: Text-to-SQL Query Processing")
    print("=" * 60)
    
    query = "Which promotion performed best last month?"
    print(f"Question: {query}")
    
    response = requests.post(
        f"{BASE_URL}/text-to-sql/query",
        json={"query": query, "use_llm": False},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Query processed successfully")
        print(f"  Generated SQL: {data.get('generated_sql', '').split('FROM')[0]}...")
        print(f"  Valid: {data.get('is_valid', False)}")
        print(f"  Results: {len(data.get('results', []))} rows")
        
        # Check interpretation
        interpretation = data.get("interpretation", {})
        if interpretation:
            print(f"  Summary: {interpretation.get('summary', '')[:100]}...")
            findings = interpretation.get("key_findings", [])
            if findings:
                print(f"  Key findings: {len(findings)} identified")
        
        print(f"  Execution time: {data.get('execution_time_ms', 0)}ms")
        return True
    else:
        print(f"✗ Query processing failed: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        return False


def test_explain_query(headers, sql):
    """Test query explanation"""
    print("\n" + "=" * 60)
    print("Test 6: Explain SQL Query")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/text-to-sql/explain?sql_query={sql}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        explanation = data.get("explanation", "")
        print(f"✓ Explanation generated")
        print(f"  {explanation.split('Retrieving')[1][:200] if 'Retrieving' in explanation else explanation[:200]}")
        return True
    else:
        print(f"✗ Explanation failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("TEXT-TO-SQL API ENDPOINT TESTS")
    print(f"Backend: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Step 1: Authenticate
    headers = test_authentication()
    if not headers:
        print("\n✗ Authentication failed - cannot proceed with tests")
        return
    
    # Step 2-3: Schema and samples
    test_schema_info(headers)
    test_sample_queries(headers)
    
    # Step 4-6: Query processing
    test_text_to_sql_query(headers)
    
    print("\n" + "=" * 60)
    print("✓ API ENDPOINT TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
