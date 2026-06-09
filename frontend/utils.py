"""
Frontend Utilities - Data Processing and Visualization Helpers
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json


class DataProcessor:
    """Process and transform data for visualization."""
    
    @staticmethod
    def format_currency(value: float) -> str:
        """Format value as currency."""
        return f"${value:,.0f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format value as percentage."""
        return f"{value:.1f}%"
    
    @staticmethod
    def calculate_growth(current: float, previous: float) -> float:
        """Calculate growth percentage."""
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    
    @staticmethod
    def get_trend_direction(growth: float) -> str:
        """Get trend direction indicator."""
        if growth > 0:
            return f"📈 +{growth:.1f}%"
        elif growth < 0:
            return f"📉 {growth:.1f}%"
        else:
            return "➡️ 0%"
    
    @staticmethod
    def aggregate_sales_data(data: List[Dict], period: str = "daily") -> pd.DataFrame:
        """Aggregate sales data by period."""
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df.get('timestamp', []))
        
        if period == "daily":
            grouped = df.groupby(df['timestamp'].dt.date)['amount'].sum()
        elif period == "weekly":
            grouped = df.groupby(df['timestamp'].dt.isocalendar().week)['amount'].sum()
        elif period == "monthly":
            grouped = df.groupby(df['timestamp'].dt.month)['amount'].sum()
        else:
            grouped = df.groupby(df['timestamp'].dt.date)['amount'].sum()
        
        return pd.DataFrame({'period': grouped.index, 'sales': grouped.values})
    
    @staticmethod
    def calculate_kpi_metrics(data: List[Dict]) -> Dict[str, Any]:
        """Calculate KPI metrics from data."""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        
        return {
            'total_sales': df['amount'].sum() if 'amount' in df else 0,
            'average_transaction': df['amount'].mean() if 'amount' in df else 0,
            'transaction_count': len(df),
            'unique_products': df['product_id'].nunique() if 'product_id' in df else 0,
            'unique_stores': df['store_id'].nunique() if 'store_id' in df else 0,
        }
    
    @staticmethod
    def identify_outliers(values: List[float], threshold: float = 2.0) -> List[int]:
        """Identify outliers using z-score."""
        if len(values) < 2:
            return []
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return []
        
        z_scores = np.abs((values - mean) / std)
        return np.where(z_scores > threshold)[0].tolist()


class InsightFormatter:
    """Format insights for display."""
    
    @staticmethod
    def format_finding(finding: Dict) -> str:
        """Format a finding for display."""
        return f"**{finding.get('title', 'Finding')}**\n{finding.get('description', '')}"
    
    @staticmethod
    def format_opportunity(opportunity: Dict) -> str:
        """Format an opportunity for display."""
        return f"""
**{opportunity.get('title', 'Opportunity')}**
- Description: {opportunity.get('description', '')}
- Potential Value: {opportunity.get('potential_value', '$0')}
- Effort: {opportunity.get('effort_level', 'MEDIUM')}
- Priority: {opportunity.get('priority_score', 5)}/10
"""
    
    @staticmethod
    def format_alert(alert: Dict) -> Tuple[str, str]:
        """Format alert and return HTML and CSS class."""
        level = alert.get('level', 'INFO').upper()
        
        level_map = {
            'CRITICAL': ('alert-critical', '🚨'),
            'WARNING': ('alert-warning', '⚠️'),
            'INFO': ('alert-success', 'ℹ️')
        }
        
        css_class, icon = level_map.get(level, ('alert-success', 'ℹ️'))
        
        html = f"""
<div class='{css_class}'>
    <strong>{icon} {alert.get('title', 'Alert')}</strong><br>
    {alert.get('message', '')}
</div>
"""
        return html, css_class
    
    @staticmethod
    def format_recommendation(recommendation: Dict) -> str:
        """Format a recommendation for display."""
        priority = recommendation.get('priority', 'MEDIUM')
        priority_icons = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
        
        return f"""
{priority_icons.get(priority, '🔵')} **{recommendation.get('title', 'Recommendation')}**
- Action: {recommendation.get('action', '')}
- Impact: {recommendation.get('expected_impact', 'Unknown')}
- Timeline: {recommendation.get('timeline', 'ASAP')}
"""


class ReportBuilder:
    """Build structured reports from components."""
    
    @staticmethod
    def build_executive_summary(
        health_score: float,
        key_findings: List[Dict],
        recommendations: List[Dict],
        kpi_status: Dict
    ) -> Dict[str, Any]:
        """Build executive summary report."""
        return {
            'report_type': 'executive_summary',
            'generated_at': datetime.now().isoformat(),
            'health_score': health_score,
            'executive_overview': {
                'total_findings': len(key_findings),
                'critical_findings': sum(1 for f in key_findings if f.get('severity') == 'CRITICAL'),
                'recommendations': len(recommendations)
            },
            'key_findings': key_findings,
            'recommendations': recommendations,
            'kpi_status': kpi_status,
            'next_steps': [
                "Monitor critical alerts",
                "Execute recommended actions",
                "Review KPI trends"
            ]
        }
    
    @staticmethod
    def build_performance_report(
        sales_data: List[Dict],
        product_performance: List[Dict],
        regional_data: List[Dict]
    ) -> Dict[str, Any]:
        """Build performance analysis report."""
        return {
            'report_type': 'performance_analysis',
            'generated_at': datetime.now().isoformat(),
            'sales_summary': {
                'total_sales': sum(s.get('amount', 0) for s in sales_data),
                'average_daily': np.mean([s.get('amount', 0) for s in sales_data]),
                'data_points': len(sales_data)
            },
            'top_products': sorted(
                product_performance,
                key=lambda x: x.get('sales', 0),
                reverse=True
            )[:10],
            'regional_performance': regional_data,
            'trends': {
                'sales_trend': 'increasing',
                'margin_trend': 'stable',
                'growth_rate': 8.5
            }
        }
    
    @staticmethod
    def build_opportunity_report(opportunities: List[Dict]) -> Dict[str, Any]:
        """Build opportunity analysis report."""
        total_potential = sum(o.get('potential_value', 0) for o in opportunities)
        
        return {
            'report_type': 'opportunity_analysis',
            'generated_at': datetime.now().isoformat(),
            'total_opportunities': len(opportunities),
            'total_potential_value': total_potential,
            'opportunities_by_priority': {
                'high': len([o for o in opportunities if o.get('priority_score', 0) >= 8]),
                'medium': len([o for o in opportunities if 5 <= o.get('priority_score', 0) < 8]),
                'low': len([o for o in opportunities if o.get('priority_score', 0) < 5])
            },
            'opportunities': sorted(
                opportunities,
                key=lambda x: x.get('potential_value', 0),
                reverse=True
            ),
            'quick_wins': [o for o in opportunities if o.get('effort_level') == 'LOW'],
            'strategic_initiatives': [o for o in opportunities if o.get('effort_level') == 'HIGH']
        }


class CacheManager:
    """Manage Streamlit cache for API responses."""
    
    @staticmethod
    @st.cache_data(ttl=300)  # 5 minute cache
    def cache_api_response(url: str, params: Dict = None) -> Dict[str, Any]:
        """Cache API response."""
        import requests
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    @st.cache_data(ttl=600)  # 10 minute cache
    def cache_large_dataset(key: str, data: pd.DataFrame) -> pd.DataFrame:
        """Cache large datasets."""
        return data
    
    @staticmethod
    def clear_cache():
        """Clear Streamlit cache."""
        st.cache_data.clear()


class ValidationHelper:
    """Validate user inputs and API responses."""
    
    @staticmethod
    def validate_date_range(start_date, end_date) -> Tuple[bool, str]:
        """Validate date range."""
        if start_date > end_date:
            return False, "Start date must be before end date"
        
        if (end_date - start_date).days > 365:
            return False, "Date range cannot exceed 365 days"
        
        return True, ""
    
    @staticmethod
    def validate_query(query: str) -> Tuple[bool, str]:
        """Validate SQL or natural language query."""
        if not query or len(query.strip()) == 0:
            return False, "Query cannot be empty"
        
        if len(query) > 1000:
            return False, "Query is too long (max 1000 characters)"
        
        return True, ""
    
    @staticmethod
    def validate_api_response(response: Dict) -> Tuple[bool, str]:
        """Validate API response."""
        if 'error' in response:
            return False, response['error']
        
        if not response:
            return False, "Empty response from server"
        
        return True, ""
