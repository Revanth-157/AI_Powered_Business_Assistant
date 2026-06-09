#!/usr/bin/env python3
"""Authenticate and test Text-to-SQL API"""

import requests
import json

# Register
print("Registering new user...")
response = requests.post(
    'http://localhost:8001/api/v1/auth/register',
    json={
        'email': 'demo@fmcg.com',
        'username': 'demoadmin',
        'password': 'Demo@Password123',
        'full_name': 'Demo Admin'
    }
)

print(f'Register Status: {response.status_code}')

# Login
print("\nLogging in...")
response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={
        'email': 'demo@fmcg.com',
        'password': 'Demo@Password123'
    }
)

print(f'Login Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    token = data.get('access_token', '')
    print(f'Token: {token[:50]}...')
    
    # Test schema endpoint
    print("\n--- Testing Schema Endpoint ---")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        'http://localhost:8001/api/v1/text-to-sql/schema',
        headers=headers
    )
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        tables = data.get('tables', [])
        print(f'Tables: {len(tables)}')
        print(f'Sample: {tables[:3]}')
    else:
        print(f'Error: {response.text}')
    
    # Test samples endpoint
    print("\n--- Testing Samples Endpoint ---")
    response = requests.get(
        'http://localhost:8001/api/v1/text-to-sql/samples',
        headers=headers
    )
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        samples = data.get('samples', [])
        print(f'Samples: {len(samples)}')
        if samples:
            print(f'First: {samples[0]["question"]}')
    else:
        print(f'Error: {response.text}')
    
    # Test query endpoint
    print("\n--- Testing Query Endpoint ---")
    response = requests.post(
        'http://localhost:8001/api/v1/text-to-sql/query',
        json={'query': 'Which promotion performed best last month?', 'use_llm': False},
        headers=headers
    )
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Valid: {data.get("is_valid", False)}')
        print(f'Results: {len(data.get("results", []))}')
        print(f'Execution time: {data.get("execution_time_ms", 0)}ms')
    else:
        print(f'Error: {response.text[:500]}')

else:
    print(f'Login failed: {response.text}')
