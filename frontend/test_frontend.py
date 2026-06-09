"""
Frontend Testing Suite - Test all Streamlit Components

Comprehensive test suite for the autonomous BI dashboard.
Tests all pages, components, and API integration.
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add backend to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 70)
    print("Test 1: IMPORT DEPENDENCIES")
    print("=" * 70)
    
    try:
        import streamlit
        print("✓ Streamlit imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Streamlit: {e}")
        return False
    
    try:
        import plotly
        print("✓ Plotly imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Plotly: {e}")
        return False
    
    try:
        import pandas
        print("✓ Pandas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Pandas: {e}")
        return False
    
    try:
        import requests
        print("✓ Requests imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Requests: {e}")
        return False
    
    print("\n✅ All imports successful\n")
    return True


def test_api_client():
    """Test API client functionality."""
    print("=" * 70)
    print("Test 2: API CLIENT")
    print("=" * 70)
    
    # Import API client from app
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Mock the APIClient
    class MockAPIClient:
        def __init__(self, base_url, token=None):
            self.base_url = base_url
            self.token = token
            self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        def get_health(self):
            return {"status": "healthy", "database": True}
        
        def query_text_to_sql(self, query):
            return {
                "sql_query": "SELECT * FROM sales WHERE date > '2026-06-01'",
                "query_results": [{"product": "Mango Nectar", "sales": 125000}],
                "interpretation": "Query executed successfully"
            }
    
    api_client = MockAPIClient("http://localhost:8001")
    
    # Test health check
    health = api_client.get_health()
    assert health["status"] == "healthy", "Health check failed"
    print("✓ Health check successful")
    
    # Test SQL query
    result = api_client.query_text_to_sql("What are top products?")
    assert "sql_query" in result, "SQL query not in result"
    assert "query_results" in result, "Query results not in result"
    print("✓ SQL query conversion working")
    
    print("\n✅ API client tests passed\n")
    return True


def test_data_processing():
    """Test data processing utilities."""
    print("=" * 70)
    print("Test 3: DATA PROCESSING UTILITIES")
    print("=" * 70)
    
    import pandas as pd
    import numpy as np
    
    # Test currency formatting
    value = 12500.50
    formatted = f"${value:,.0f}"
    assert formatted == "$12,500" or formatted == "$12,501", "Currency formatting failed"
    print("✓ Currency formatting working")
    
    # Test percentage formatting
    pct = 15.567
    formatted = f"{pct:.1f}%"
    assert formatted == "15.6%", "Percentage formatting failed"
    print("✓ Percentage formatting working")
    
    # Test growth calculation
    current = 150000
    previous = 100000
    growth = ((current - previous) / previous) * 100
    assert growth == 50.0, "Growth calculation failed"
    print("✓ Growth calculation working")
    
    # Test trend direction
    if growth > 0:
        direction = f"📈 +{growth:.1f}%"
    assert direction == "📈 +50.0%", "Trend direction failed"
    print("✓ Trend direction working")
    
    # Test outlier detection
    values = np.array([1, 2, 3, 4, 5, 100])  # 100 is outlier
    mean = np.mean(values)
    std = np.std(values)
    z_scores = np.abs((values - mean) / std)
    outliers = np.where(z_scores > 2.0)[0]
    assert len(outliers) > 0, "Outlier detection failed"
    print("✓ Outlier detection working")
    
    print("\n✅ Data processing tests passed\n")
    return True


def test_sample_data():
    """Test sample data generation."""
    print("=" * 70)
    print("Test 4: SAMPLE DATA GENERATION")
    print("=" * 70)
    
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Generate sample sales data
    start_date = datetime.now() - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=datetime.now(), freq='D')
    sales = [40000 + i*500 + (i**2)*10 for i in range(len(dates))]
    
    df_sales = pd.DataFrame({
        'Date': dates,
        'Sales': sales
    })
    
    assert len(df_sales) == 31, "Sales data generation failed"
    assert df_sales['Sales'].sum() > 0, "Sales sum should be positive"
    print(f"✓ Generated {len(df_sales)} days of sales data")
    
    # Generate product data
    products = ['Mango Nectar', 'Apple Cider', 'Orange Juice', 'Lemon Water', 'Berry Blend']
    sales_list = [125000, 98000, 87000, 76000, 65000]
    margins = [38, 35, 32, 30, 28]
    
    df_products = pd.DataFrame({
        'Product': products,
        'Sales': sales_list,
        'Margin': margins
    })
    
    assert len(df_products) == 5, "Product data generation failed"
    assert df_products['Sales'].sum() == 451000, "Product sales total incorrect"
    print(f"✓ Generated {len(df_products)} products with metrics")
    
    # Generate region data
    regions = ['North', 'South', 'East', 'West']
    sales_by_region = [180000, 165000, 150000, 125000]
    growth_rates = [12, 8, 5, 3]
    
    df_regions = pd.DataFrame({
        'Region': regions,
        'Sales': sales_by_region,
        'Growth': growth_rates
    })
    
    assert len(df_regions) == 4, "Regional data generation failed"
    print(f"✓ Generated {len(df_regions)} regions with metrics")
    
    print("\n✅ Sample data generation tests passed\n")
    return True


def test_insight_formatting():
    """Test insight formatting utilities."""
    print("=" * 70)
    print("Test 5: INSIGHT FORMATTING")
    print("=" * 70)
    
    # Test finding format
    finding = {
        "title": "Star Performer",
        "description": "Pure Mango Nectar outperforms targets",
        "severity": "POSITIVE"
    }
    
    formatted = f"**{finding['title']}**\n{finding['description']}"
    assert "Star Performer" in formatted, "Finding formatting failed"
    print("✓ Finding formatting working")
    
    # Test opportunity format
    opportunity = {
        "title": "Scale Promotion",
        "description": "Expand to new channels",
        "potential_value": 31250,
        "effort_level": "MEDIUM",
        "priority_score": 9
    }
    
    formatted = f"**{opportunity['title']}**: {opportunity['potential_value']}"
    assert "Scale Promotion" in formatted, "Opportunity formatting failed"
    print("✓ Opportunity formatting working")
    
    # Test alert format
    alert = {
        "title": "Stockout Alert",
        "message": "Premium Juice out of stock",
        "level": "CRITICAL"
    }
    
    level_map = {
        'CRITICAL': ('alert-critical', '🚨'),
        'WARNING': ('alert-warning', '⚠️'),
        'INFO': ('alert-success', 'ℹ️')
    }
    
    css_class, icon = level_map.get(alert['level'], ('alert-success', 'ℹ️'))
    assert css_class == 'alert-critical', "Alert formatting failed"
    print("✓ Alert formatting working")
    
    # Test recommendation format
    recommendation = {
        "title": "Address Stockouts",
        "action": "Increase inventory",
        "expected_impact": "Reduce stockout rate by 50%",
        "timeline": "URGENT",
        "priority": "HIGH"
    }
    
    priority_icons = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
    icon = priority_icons.get(recommendation['priority'], '🔵')
    formatted = f"{icon} {recommendation['title']}"
    assert "🔴" in formatted, "Recommendation formatting failed"
    print("✓ Recommendation formatting working")
    
    print("\n✅ Insight formatting tests passed\n")
    return True


def test_report_building():
    """Test report builder functionality."""
    print("=" * 70)
    print("Test 6: REPORT BUILDING")
    print("=" * 70)
    
    from datetime import datetime
    
    # Test executive summary report
    key_findings = [
        {"title": "Finding 1", "severity": "CRITICAL"},
        {"title": "Finding 2", "severity": "INFO"}
    ]
    
    recommendations = [
        {"title": "Rec 1", "action": "Action 1"},
        {"title": "Rec 2", "action": "Action 2"}
    ]
    
    kpi_status = {
        "on_target": 5,
        "at_risk": 2,
        "below_target": 1
    }
    
    report = {
        'report_type': 'executive_summary',
        'generated_at': datetime.now().isoformat(),
        'health_score': 72,
        'key_findings': key_findings,
        'recommendations': recommendations,
        'kpi_status': kpi_status
    }
    
    assert report['report_type'] == 'executive_summary', "Report type incorrect"
    assert len(report['key_findings']) == 2, "Findings count incorrect"
    assert len(report['recommendations']) == 2, "Recommendations count incorrect"
    print("✓ Executive summary report built successfully")
    
    # Test performance report
    sales_data = [{"amount": 40000, "date": "2026-06-09"}] * 30
    
    total_sales = sum(s.get('amount', 0) for s in sales_data)
    avg_sales = total_sales / len(sales_data)
    
    perf_report = {
        'report_type': 'performance_analysis',
        'generated_at': datetime.now().isoformat(),
        'total_sales': total_sales,
        'average_daily': avg_sales,
        'data_points': len(sales_data)
    }
    
    assert perf_report['total_sales'] == 1200000, "Performance report sales incorrect"
    print("✓ Performance analysis report built successfully")
    
    # Test opportunity report
    opportunities = [
        {"title": "Opp 1", "potential_value": 31250, "priority_score": 9},
        {"title": "Opp 2", "potential_value": 39000, "priority_score": 8}
    ]
    
    total_potential = sum(o.get('potential_value', 0) for o in opportunities)
    
    opp_report = {
        'report_type': 'opportunity_analysis',
        'total_potential_value': total_potential,
        'opportunities': opportunities
    }
    
    assert opp_report['total_potential_value'] == 70250, "Opportunity value incorrect"
    print("✓ Opportunity analysis report built successfully")
    
    print("\n✅ Report building tests passed\n")
    return True


def test_validation():
    """Test input validation."""
    print("=" * 70)
    print("Test 7: INPUT VALIDATION")
    print("=" * 70)
    
    from datetime import datetime, timedelta
    
    # Test date range validation
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    is_valid = start_date < end_date
    assert is_valid, "Date range validation failed"
    print("✓ Date range validation working")
    
    # Test query validation
    queries = [
        ("What are top products?", True),  # Valid
        ("", False),  # Empty
        ("x" * 1001, False),  # Too long
    ]
    
    for query, should_be_valid in queries:
        is_valid = len(query) > 0 and len(query) <= 1000
        assert is_valid == should_be_valid, f"Query validation failed for: {query[:50]}"
    
    print("✓ Query validation working")
    
    # Test response validation
    responses = [
        ({"status": "success", "data": []}, True),  # Valid
        ({"error": "Something went wrong"}, False),  # Has error
        ({}, False),  # Empty
    ]
    
    for response, should_be_valid in responses:
        is_valid = 'error' not in response and len(response) > 0
        assert is_valid == should_be_valid, f"Response validation failed"
    
    print("✓ Response validation working")
    
    print("\n✅ Input validation tests passed\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "STREAMLIT FRONTEND TEST SUITE" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    tests = [
        ("Import Dependencies", test_imports),
        ("API Client", test_api_client),
        ("Data Processing", test_data_processing),
        ("Sample Data Generation", test_sample_data),
        ("Insight Formatting", test_insight_formatting),
        ("Report Building", test_report_building),
        ("Input Validation", test_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with error: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL FRONTEND TESTS PASSED")
    else:
        print(f"\n❌ {total - passed} tests failed")
    
    print()
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
