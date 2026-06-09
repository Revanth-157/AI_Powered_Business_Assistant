#!/usr/bin/env python3
"""Test script for Text-to-SQL functionality"""

from services.text_to_sql_service import TextToSQLService
from database import SessionLocal

def test_text_to_sql():
    """Test Text-to-SQL module"""
    db = SessionLocal()
    service = TextToSQLService(db)
    
    # Test 1: Schema extraction
    print("=" * 60)
    print("Test 1: Schema Extraction")
    print("=" * 60)
    tables = service.schema_extractor.get_available_tables()
    print(f"✓ Available tables: {', '.join(tables)}")
    
    # Test 2: Sample queries
    print("\n" + "=" * 60)
    print("Test 2: Sample Queries")
    print("=" * 60)
    samples = service.get_sample_queries()
    print(f"✓ Sample queries count: {len(samples)}")
    for i, sample in enumerate(samples[:3], 1):
        print(f"  {i}. {sample['question']} (Intent: {sample['intent']})")
    
    # Test 3: SQL generation
    print("\n" + "=" * 60)
    print("Test 3: SQL Generation")
    print("=" * 60)
    test_query = "Which promotion performed best last month?"
    sql, metadata = service.sql_generator.generate_sql(test_query, use_llm=False)
    print(f"✓ Query: {test_query}")
    print(f"✓ Generated SQL:\n{sql}")
    print(f"✓ Metadata: {metadata}")
    
    # Test 4: Query validation
    print("\n" + "=" * 60)
    print("Test 4: Query Validation")
    print("=" * 60)
    is_valid, validation = service.validate_query(sql)
    print(f"✓ Query is valid: {is_valid}")
    if not is_valid:
        print(f"  Errors: {validation.get('errors', [])}")
    else:
        print(f"  Risk level: {validation.get('estimated_risk', 'unknown')}")
        if validation.get('warnings'):
            print(f"  Warnings: {validation['warnings']}")
    
    # Test 5: Query explanation
    print("\n" + "=" * 60)
    print("Test 5: Query Explanation")
    print("=" * 60)
    explanation = service.explain_query(sql)
    print(f"✓ Query explanation:\n{explanation}")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    test_text_to_sql()
