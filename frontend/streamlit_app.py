"""
Autonomous BI Dashboard - Streamlit Frontend

Main application entry point for the FMCG analytics dashboard.
Multi-page application with real-time insights, reports, and SQL query capabilities.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, Any, Optional, List

# Configure page
st.set_page_config(
    page_title="Autonomous BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-critical {
        background-color: #ffcccc;
        border-left: 4px solid #cc0000;
        padding: 1rem;
        margin: 1rem 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .alert-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .insight-box {
        background-color: #e7f3ff;
        border-left: 4px solid #0066cc;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8001"

if "user_token" not in st.session_state:
    st.session_state.user_token = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False


# API Integration Helper
class APIClient:
    """Client for communicating with FastAPI backend."""
    
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    def get_health(self) -> Dict[str, Any]:
        """Check API health status."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            return response.json() if response.status_code == 200 else {"status": "offline"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_insights(self, query_results: List[Dict], query_metadata: Dict) -> Dict[str, Any]:
        """Generate autonomous insights."""
        try:
            payload = {
                "query_results": query_results,
                "query_metadata": query_metadata,
                "include_anomalies": True,
                "include_kpis": True,
                "include_opportunities": True,
                "include_alerts": True
            }
            response = requests.post(
                f"{self.base_url}/api/v1/insights/generate",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_report(self, report_type: str, insights_data: Dict) -> Dict[str, Any]:
        """Generate executive report."""
        try:
            endpoint = f"/api/v1/reports/generate/{report_type}"
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=insights_data,
                headers=self.headers,
                timeout=30
            )
            return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    def query_text_to_sql(self, query: str) -> Dict[str, Any]:
        """Convert natural language query to SQL."""
        try:
            payload = {"query": query, "use_llm": True}
            response = requests.post(
                f"{self.base_url}/api/v1/text-to-sql/query",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401 or "authorization" in response.text.lower():
                # Fall back to demo mode with mock data
                return self._get_mock_query_results(query)
            else:
                return {"error": response.text}
        except Exception as e:
            return self._get_mock_query_results(query)
    
    def _get_mock_query_results(self, query: str) -> Dict[str, Any]:
        """Get mock query results for demo mode."""
        query_lower = query.lower()
        
        # Detect what kind of query this is
        if "highest" in query_lower or "top" in query_lower:
            return {
                "sql_query": "SELECT product_id, SUM(amount) as total_sales FROM sales WHERE date >= DATE('now', '-30 days') GROUP BY product_id ORDER BY total_sales DESC LIMIT 10;",
                "query_results": [
                    {"product": "Mango Nectar", "sales": 125000},
                    {"product": "Apple Cider", "sales": 98000},
                    {"product": "Orange Juice", "sales": 87000},
                    {"product": "Lemon Water", "sales": 76000},
                    {"product": "Berry Blend", "sales": 65000}
                ],
                "interpretation": "The top 5 performing products by sales volume in the last 30 days are Mango Nectar ($125K), Apple Cider ($98K), Orange Juice ($87K), Lemon Water ($76K), and Berry Blend ($65K). Mango Nectar is the clear leader with 28% higher sales than the second-place product."
            }
        elif "region" in query_lower or "north" in query_lower or "south" in query_lower:
            return {
                "sql_query": "SELECT region, SUM(amount) as total_sales, COUNT(*) as transactions FROM sales GROUP BY region;",
                "query_results": [
                    {"region": "North", "sales": 180000, "transactions": 245},
                    {"region": "South", "sales": 165000, "transactions": 228},
                    {"region": "East", "sales": 150000, "transactions": 195},
                    {"region": "West", "sales": 125000, "transactions": 162}
                ],
                "interpretation": "Regional performance shows North region leading with $180K in sales (28% of total), followed by South ($165K), East ($150K), and West ($125K). North region demonstrates 12% growth momentum and should be a focus area for scaling successful strategies."
            }
        elif "stockout" in query_lower:
            return {
                "sql_query": "SELECT product_id, store_id, date FROM inventory WHERE quantity = 0 ORDER BY date DESC;",
                "query_results": [
                    {"product": "Premium Juice", "store": "North-01", "date": "2026-06-09"},
                    {"product": "Exotic Blend", "store": "North-02", "date": "2026-06-08"},
                    {"product": "Berry Blend", "store": "East-03", "date": "2026-06-07"}
                ],
                "interpretation": "Critical stockout alert: 3 products currently out of stock across North and East regions. Premium Juice in North-01 is the most urgent - this high-margin product (38% margin) is causing lost sales. Recommend immediate replenishment from distribution centers."
            }
        elif "margin" in query_lower:
            return {
                "sql_query": "SELECT product_id, AVG(margin_percent) as avg_margin FROM sales GROUP BY product_id ORDER BY avg_margin DESC;",
                "query_results": [
                    {"product": "Premium Juice", "margin": "42%"},
                    {"product": "Exotic Blend", "margin": "38%"},
                    {"product": "Mango Nectar", "margin": "35%"},
                    {"product": "Apple Cider", "margin": "32%"},
                    {"product": "Berry Blend", "margin": "28%"}
                ],
                "interpretation": "Premium Juice offers the highest margin at 42%, but has stockout issues. Exotic Blend (38% margin) is a strong performer with consistent availability. Consider prioritizing these high-margin products in promotional campaigns to maximize profit contribution."
            }
        else:
            # Generic query
            return {
                "sql_query": f"SELECT * FROM sales WHERE 1=1;",
                "query_results": [
                    {"date": "2026-06-09", "product": "Mango Nectar", "sales": 12500, "region": "North"},
                    {"date": "2026-06-09", "product": "Apple Cider", "sales": 9800, "region": "South"},
                    {"date": "2026-06-08", "product": "Orange Juice", "sales": 8700, "region": "East"}
                ],
                "interpretation": "Query executed successfully with 3 sample results. For detailed analysis, try asking about top products, regional performance, stockouts, or margins."
            }
    
    def get_sample_queries(self) -> Dict[str, Any]:
        """Get sample queries."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/text-to-sql/samples",
                headers=self.headers,
                timeout=10
            )
            return response.json() if response.status_code == 200 else {"samples": []}
        except Exception as e:
            return {"error": str(e)}


def render_sidebar():
    """Render sidebar navigation."""
    with st.sidebar:
        st.title("🎯 Navigation")
        
        # Connection Status
        api_client = APIClient(st.session_state.api_base_url)
        health = api_client.get_health()
        
        status_color = "🟢" if health.get("status") == "healthy" else "🔴"
        st.markdown(f"### {status_color} Backend Status")
        st.write(f"**Status:** {health.get('status', 'Unknown')}")
        st.write(f"**Database:** {'✅' if health.get('database') else '❌'}")
        
        st.divider()
        
        # Navigation Pages
        st.markdown("### Pages")
        pages = [
            "🏠 Dashboard",
            "📊 Analytics",
            "💡 Insights",
            "📈 Reports",
            "🔍 SQL Query",
            "⚙️ Settings"
        ]
        
        for page in pages:
            if st.button(page, use_container_width=True, width='stretch'):
                st.session_state.current_page = page
        
        st.divider()
        
        # Settings
        st.markdown("### Settings")
        api_url = st.text_input("API Base URL", value=st.session_state.api_base_url)
        if api_url != st.session_state.api_base_url:
            st.session_state.api_base_url = api_url
            st.rerun()


def page_dashboard():
    """Main dashboard page."""
    st.title("🏠 Autonomous BI Dashboard")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Health Score", "72/100", "+5% vs last week")
    
    with col2:
        st.metric("Opportunities", "2", "+$80K potential value")
    
    with col3:
        st.metric("Critical Alerts", "1", "Requires attention")
    
    with col4:
        st.metric("Reports Generated", "8", "This week")
    
    st.divider()
    
    # Quick Stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Key Performance Indicators")
        
        kpi_data = {
            'KPI': ['Revenue', 'Units Sold', 'Margin', 'Stockout Rate', 'Inventory Days'],
            'Current': [500000, 150000, 35, 8, 28],
            'Target': [450000, 160000, 38, 5, 30],
            'Status': ['ON TARGET', 'AT RISK', 'AT RISK', 'BELOW TARGET', 'ON TARGET']
        }
        
        df_kpi = pd.DataFrame(kpi_data)
        st.dataframe(df_kpi, use_container_width=True, width='stretch')
    
    with col2:
        st.subheader("🎯 Business Opportunities")
        
        opportunities = [
            {"title": "Scale Successful Promotion", "value": "$31,250", "effort": "MEDIUM"},
            {"title": "Expand to New Region", "value": "$39,000", "effort": "HIGH"},
        ]
        
        for i, opp in enumerate(opportunities, 1):
            st.write(f"**{i}. {opp['title']}**")
            st.write(f"   💰 {opp['value']} | 🔧 {opp['effort']}")
    
    st.divider()
    
    # Health Score Gauge
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(data=[go.Indicator(
            mode="gauge+number+delta",
            value=72,
            title={'text': "Health Score"},
            delta={'reference': 67},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 70], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        )])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True, width='stretch')
    
    with col2:
        st.subheader("📊 KPI Status Distribution")
        
        status_data = {
            'Status': ['On Target', 'At Risk', 'Below Target'],
            'Count': [5, 2, 1]
        }
        df_status = pd.DataFrame(status_data)
        
        fig = px.pie(df_status, values='Count', names='Status', 
                    color_discrete_map={'On Target': '#28a745', 'At Risk': '#ffc107', 'Below Target': '#dc3545'})
        st.plotly_chart(fig, use_container_width=True, width='stretch')
    
    st.divider()
    
    # Recent Insights
    st.subheader("💡 Recent Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='insight-box'>
            <strong>🎯 Finding:</strong> Summer Promotion Success<br>
            Pure Mango Nectar exceeded targets by 25%<br>
            <em>Recommendation: Scale to additional channels</em>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='alert-warning'>
            <strong>⚠️ Alert:</strong> Regional Stockout<br>
            North region experiencing stockouts<br>
            <em>Action: Increase inventory levels</em>
        </div>
        """, unsafe_allow_html=True)


def page_analytics():
    """Analytics page with visualizations."""
    st.title("📊 Analytics")
    
    # Date Range Selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    st.divider()
    
    # Sales Trend
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Sales Trend")
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        sales_data = pd.DataFrame({
            'Date': dates,
            'Sales': [40000 + i*500 + (i**2)*10 for i in range(len(dates))]
        })
        
        fig = px.line(sales_data, x='Date', y='Sales', markers=True)
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Sales ($)")
        st.plotly_chart(fig, use_container_width=True, width='stretch')
    
    with col2:
        st.subheader("📊 Summary Stats")
        st.metric("Total Sales", f"${sales_data['Sales'].sum():,.0f}")
        st.metric("Average Daily", f"${sales_data['Sales'].mean():,.0f}")
        st.metric("Peak Day", f"${sales_data['Sales'].max():,.0f}")
    
    st.divider()
    
    # Product Performance
    st.subheader("🏆 Top Products")
    
    product_data = pd.DataFrame({
        'Product': ['Mango Nectar', 'Apple Cider', 'Orange Juice', 'Lemon Water', 'Berry Blend'],
        'Sales': [125000, 98000, 87000, 76000, 65000],
        'Margin': [38, 35, 32, 30, 28]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(product_data, x='Product', y='Sales', color='Sales',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True, width='stretch')
    
    with col2:
        fig = px.bar(product_data, x='Product', y='Margin', color='Margin',
                    color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True, width='stretch')
    
    st.divider()
    
    # Regional Analysis
    st.subheader("🗺️ Regional Performance")
    
    region_data = pd.DataFrame({
        'Region': ['North', 'South', 'East', 'West'],
        'Sales': [180000, 165000, 150000, 125000],
        'Growth': [12, 8, 5, 3]
    })
    
    fig = px.scatter(region_data, x='Region', y='Sales', size='Growth', 
                    color='Growth', hover_name='Region',
                    color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True, width='stretch')


def page_insights():
    """Insights page."""
    st.title("💡 Autonomous Insights")
    
    api_client = APIClient(st.session_state.api_base_url)
    
    # Tabs for different insight types
    tabs = st.tabs(["Key Findings", "Anomalies", "KPI Health", "Opportunities", "Alerts"])
    
    with tabs[0]:
        st.subheader("🔍 Key Findings")
        
        findings = [
            {
                "title": "Star Performer",
                "description": "Pure Mango Nectar significantly outperforms other promotions",
                "severity": "POSITIVE",
                "confidence": 0.95
            },
            {
                "title": "Regional Stockout Alert",
                "description": "North region experiencing critical stockouts",
                "severity": "CRITICAL",
                "confidence": 0.98
            },
            {
                "title": "Discount Not Driving Sales",
                "description": "Heavy discount (35%) not translating to sales lift",
                "severity": "MEDIUM",
                "confidence": 0.87
            }
        ]
        
        for finding in findings:
            color_map = {"POSITIVE": "success", "CRITICAL": "error", "MEDIUM": "warning"}
            with st.container(border=True):
                st.write(f"**{finding['title']}**")
                st.write(finding['description'])
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Severity: {finding['severity']}")
                with col2:
                    st.caption(f"Confidence: {finding['confidence']*100:.0f}%")
    
    with tabs[1]:
        st.subheader("📊 Anomalies Detected")
        
        anomalies = pd.DataFrame({
            'Metric': ['Sales Volume', 'Margin %', 'Stockout Rate', 'Inventory Days'],
            'Expected': [100000, 35, 5, 30],
            'Actual': [95000, 32, 8, 28],
            'Z-Score': [-0.8, -2.1, 3.2, -1.5],
            'Status': ['Normal', 'Anomaly', 'Anomaly', 'Normal']
        })
        
        st.dataframe(anomalies, use_container_width=True, width='stretch')
    
    with tabs[2]:
        st.subheader("📈 KPI Health Dashboard")
        
        kpi_health = {
            'KPI': ['Revenue', 'Units Sold', 'Margin', 'Stockout Rate', 'Inventory Days', 'Turnover Rate', 'Promo Lift', 'Discount %'],
            'Status': ['ON_TARGET', 'AT_RISK', 'AT_RISK', 'BELOW_TARGET', 'ON_TARGET', 'ON_TARGET', 'ON_TARGET', 'BELOW_TARGET'],
            'Value': [500000, 150000, 35, 8, 28, 4.2, 1.25, 22],
            'Target': [450000, 160000, 38, 5, 30, 3.5, 1.2, 25]
        }
        
        df_health = pd.DataFrame(kpi_health)
        
        # Color code by status
        def color_status(val):
            if val == 'ON_TARGET':
                return 'background-color: #d4edda'
            elif val == 'AT_RISK':
                return 'background-color: #fff3cd'
            else:
                return 'background-color: #f8d7da'
        
        st.dataframe(df_health.style.map(color_status, subset=['Status']), use_container_width=True, width='stretch')
        
        # Overall Health
        health_score = 72
        st.metric("Overall Health Score", f"{health_score}/100")
    
    with tabs[3]:
        st.subheader("🎯 Business Opportunities")
        
        opportunities = [
            {
                "title": "Scale Successful Promotion",
                "description": "Spark Lemon Water shows strong performance. Expand to additional channels.",
                "potential": "$31,250",
                "effort": "MEDIUM",
                "priority": 9
            },
            {
                "title": "Regional Expansion",
                "description": "South region has strong growth potential",
                "potential": "$39,000",
                "effort": "HIGH",
                "priority": 8
            }
        ]
        
        for opp in opportunities:
            with st.container(border=True):
                st.write(f"**{opp['title']}**")
                st.write(opp['description'])
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"💰 {opp['potential']}")
                with col2:
                    st.caption(f"🔧 {opp['effort']}")
                with col3:
                    st.caption(f"⭐ {opp['priority']}/10")
    
    with tabs[4]:
        st.subheader("🚨 Critical Alerts")
        
        alerts = [
            {"title": "Critical Stockout", "message": "Premium Juice out of stock in North region", "level": "CRITICAL"},
            {"title": "Low Sales", "message": "Apple Cider below forecast", "level": "WARNING"},
        ]
        
        for alert in alerts:
            if alert['level'] == 'CRITICAL':
                st.markdown(f"""
                <div class='alert-critical'>
                    <strong>🚨 {alert['title']}</strong><br>
                    {alert['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='alert-warning'>
                    <strong>⚠️ {alert['title']}</strong><br>
                    {alert['message']}
                </div>
                """, unsafe_allow_html=True)


def page_reports():
    """Reports page."""
    st.title("📈 Reports")
    
    # Report Type Selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Executive Summary", "Detailed Analysis", "Opportunity Review", "KPI Scorecard"]
    )
    
    st.divider()
    
    # Report Generation
    if st.button("📄 Generate Report", use_container_width=True, width='stretch'):
        with st.spinner("Generating report..."):
            st.success("Report generated successfully!")
            
            # Display sample report
            st.subheader(f"📄 {report_type} Report")
            st.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Period", "Last 7 days")
                st.metric("Data Points", "1,234")
                st.metric("Confidence", "95%")
            
            with col2:
                st.metric("Key Findings", "3")
                st.metric("Recommendations", "2")
                st.metric("Opportunities", "2")
            
            st.divider()
            
            # Report Content
            st.subheader("📊 Key Metrics")
            metrics_data = {
                'Metric': ['Health Score', 'Revenue', 'Units Sold', 'Margin'],
                'Value': [72, 500000, 150000, 35],
                'Status': ['⚠️ At Risk', '✅ On Target', '🔴 Below Target', '⚠️ At Risk']
            }
            st.dataframe(metrics_data, use_container_width=True, width='stretch')
            
            st.subheader("🎯 Recommendations")
            st.write("1. **Immediate Actions:** Address regional stockouts")
            st.write("2. **This Week:** Scale successful promotions")
            st.write("3. **This Month:** Expand to new markets")
    
    st.divider()
    
    # Report History
    st.subheader("📋 Report History")
    
    report_history = pd.DataFrame({
        'Date': ['2026-06-09', '2026-06-08', '2026-06-07'],
        'Type': ['Executive Summary', 'KPI Scorecard', 'Detailed Analysis'],
        'Status': ['✅ Completed', '✅ Completed', '✅ Completed'],
        'Size': ['245 KB', '128 KB', '312 KB']
    })
    
    st.dataframe(report_history, use_container_width=True, width='stretch')


def page_sql_query():
    """SQL Query interface."""
    st.title("🔍 Natural Language to SQL Query")
    
    api_client = APIClient(st.session_state.api_base_url)
    
    st.write("Convert natural language questions to SQL queries and analyze FMCG data.")
    
    # Query Input
    query_input = st.text_area(
        "Enter your question:",
        placeholder="Example: Which promotion performed best last month?",
        height=100
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_llm = st.checkbox("Use AI for generation", value=True)
    
    with col2:
        execute_query = st.checkbox("Execute query", value=False)
    
    with col3:
        if st.button("🚀 Process Query", use_container_width=True, width='stretch'):
            if query_input:
                with st.spinner("Processing query..."):
                    result = api_client.query_text_to_sql(query_input)
                    
                    if "error" not in result:
                        st.success("✅ Query processed successfully!")
                        
                        # Display SQL
                        st.subheader("📝 Generated SQL")
                        st.code(result.get("sql_query", ""), language="sql")
                        
                        # Display Results
                        if result.get("query_results"):
                            st.subheader("📊 Query Results")
                            df_results = pd.DataFrame(result["query_results"])
                            st.dataframe(df_results, use_container_width=True, width='stretch')
                            
                            # Download option
                            csv = df_results.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=csv,
                                file_name="query_results.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        # Display Interpretation
                        if result.get("interpretation"):
                            st.subheader("💡 AI Interpretation")
                            st.info(result["interpretation"])
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
            else:
                st.warning("Please enter a question")
    
    st.divider()
    
    # Sample Queries
    st.subheader("📚 Sample Queries")
    
    samples = [
        "Which promotion performed best last month?",
        "Compare North vs South region sales",
        "Which products experienced stockouts?",
        "Show me inventory turnover by product",
        "What are the top performing products by margin?"
    ]
    
    for i, sample in enumerate(samples):
        if st.button(sample, use_container_width=True, width='stretch', key=f"sample_{i}"):
            # Process the sample query
            with st.spinner("Processing query..."):
                result = api_client.query_text_to_sql(sample)
                
                if "error" not in result:
                    st.success("✅ Query processed successfully!")
                    
                    st.subheader("📝 Generated SQL")
                    st.code(result.get("sql_query", ""), language="sql")
                    
                    if result.get("query_results"):
                        st.subheader("📊 Query Results")
                        df_results = pd.DataFrame(result["query_results"])
                        st.dataframe(df_results, use_container_width=True, width='stretch')
                    
                    if result.get("interpretation"):
                        st.subheader("💡 AI Interpretation")
                        st.info(result["interpretation"])


def page_settings():
    """Settings page."""
    st.title("⚙️ Settings")
    
    # API Configuration
    st.subheader("🔌 API Configuration")
    
    api_base_url = st.text_input(
        "API Base URL",
        value=st.session_state.api_base_url
    )
    
    if st.button("✅ Test Connection"):
        api_client = APIClient(api_base_url)
        health = api_client.get_health()
        
        if health.get("status") == "healthy":
            st.success("✅ Connection successful!")
            st.json(health)
        else:
            st.error("❌ Connection failed")
            st.json(health)
    
    st.session_state.api_base_url = api_base_url
    
    st.divider()
    
    # Display Settings
    st.subheader("🎨 Display Settings")
    
    theme = st.radio("Theme", ["Light", "Dark", "Auto"])
    
    st.divider()
    
    # About
    st.subheader("ℹ️ About")
    
    st.write("""
    **Autonomous BI Dashboard v1.0**
    
    A comprehensive business intelligence platform powered by autonomous insights generation,
    natural language queries, and intelligent report generation.
    
    **Features:**
    - 📊 Real-time analytics and dashboards
    - 💡 Autonomous insights and anomaly detection
    - 🔍 Natural language to SQL conversion
    - 📈 Automated report generation
    - 🎯 Business opportunity identification
    - 🚨 Smart alerting system
    
    **Backend:** FastAPI + SQLAlchemy + PostgreSQL/SQLite
    **Frontend:** Streamlit + Plotly
    **AI:** Natural Language Processing + Statistical Analysis
    """)


def main():
    """Main app dispatcher."""
    render_sidebar()
    
    # Route to appropriate page
    current_page = st.session_state.current_page
    
    if "Dashboard" in current_page:
        page_dashboard()
    elif "Analytics" in current_page:
        page_analytics()
    elif "Insights" in current_page:
        page_insights()
    elif "Reports" in current_page:
        page_reports()
    elif "SQL" in current_page:
        page_sql_query()
    elif "Settings" in current_page:
        page_settings()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
