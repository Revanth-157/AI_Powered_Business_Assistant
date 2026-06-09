# Autonomous BI Dashboard - Streamlit Frontend

A comprehensive interactive dashboard for the Autonomous Business Intelligence system. Built with Streamlit for real-time insights, visualizations, and report generation.

## 🎯 Features

### Dashboard Pages

1. **🏠 Dashboard**
   - Key performance metrics at a glance
   - Health score gauges with delta indicators
   - Quick access to alerts and opportunities
   - KPI status distribution
   - Real-time business overview

2. **📊 Analytics**
   - Interactive sales trends with date range selection
   - Product performance analysis
   - Regional performance visualization
   - Year-over-year comparisons
   - Custom metric calculations

3. **💡 Autonomous Insights**
   - Key findings with confidence scores
   - Anomaly detection results with Z-score analysis
   - KPI health dashboard with multi-dimensional scoring
   - Business opportunity identification
   - Critical alerts and action items

4. **📈 Reports**
   - Executive Summary Reports
   - Detailed Analysis Reports
   - Opportunity Review Reports
   - KPI Scorecard Reports
   - Multi-format export (JSON, HTML, Markdown, Text, CSV, PDF)
   - Report scheduling and distribution
   - Report history and archive

5. **🔍 SQL Query Interface**
   - Natural language to SQL conversion
   - Real-time query execution
   - Results visualization
   - Query interpretation and insights
   - Sample query templates
   - Query history and save functionality

6. **⚙️ Settings**
   - API configuration and connection testing
   - Display theme selection
   - User preferences
   - System information

## 📦 Installation

### Prerequisites
- Python 3.8+
- FastAPI backend running on `http://localhost:8001`
- pip package manager

### Setup

1. **Install dependencies:**
```bash
cd frontend
pip install -r requirements.txt
```

2. **Verify backend is running:**
```bash
curl http://localhost:8001/api/v1/health
```

3. **Launch the dashboard:**
```bash
streamlit run streamlit_app.py
```

The dashboard will open at `http://localhost:8501`

## 🚀 Usage

### Basic Workflow

1. **Check Backend Status**
   - Look for the green status indicator in the sidebar
   - Shows health, database connection, and API availability

2. **Explore Dashboard**
   - View key metrics and KPI status
   - Check recent insights and alerts
   - Review available opportunities

3. **Run Analytics**
   - Select date range for analysis
   - View sales trends and product performance
   - Explore regional metrics

4. **Generate Insights**
   - Browse autonomous insights by type
   - Review anomaly detection results
   - View opportunities and recommended actions

5. **Create Reports**
   - Select report type (Executive, Detailed, etc.)
   - Generate and view formatted reports
   - Export to multiple formats
   - Schedule recurring reports

6. **Natural Language Queries**
   - Type business questions in plain English
   - System converts to SQL automatically
   - Execute and visualize results
   - Get AI-powered interpretation

## 🏗️ Architecture

### Components

```
frontend/
├── streamlit_app.py          # Main application with 6 pages
├── utils.py                  # Data processing and utilities
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Page Structure

Each page is self-contained with:
- **Data Loading:** Fetches from backend API
- **Processing:** Transforms data for visualization
- **Visualization:** Plotly charts and Streamlit components
- **Interactivity:** Date pickers, selectors, filters
- **Error Handling:** Graceful fallbacks for API failures

### API Integration

The `APIClient` class handles all backend communication:

```python
api_client = APIClient(base_url="http://localhost:8001", token=user_token)

# Generate insights
insights = api_client.generate_insights(query_results, metadata)

# Generate reports
report = api_client.generate_report("executive_summary", insights)

# Convert natural language to SQL
result = api_client.query_text_to_sql("What are top products?")
```

## 📊 Data Models

### Key Response Models

**Insight Response:**
```json
{
  "findings": [{"title": "...", "description": "...", "severity": "..."}],
  "anomalies": [...],
  "kpi_dashboard": {...},
  "opportunities": [...],
  "alerts": [...]
}
```

**Report Response:**
```json
{
  "report_id": "EXE-20260609-0001",
  "type": "executive_summary",
  "sections": [...],
  "metadata": {...},
  "recommendations": [...]
}
```

**SQL Query Response:**
```json
{
  "sql_query": "SELECT ...",
  "query_results": [...],
  "interpretation": "...",
  "execution_time": 0.234
}
```

## 🎨 Customization

### Styling

The dashboard uses custom CSS for consistent styling:
- Alert boxes for warnings/errors/success
- Insight boxes for findings
- Metric cards for KPIs
- Color-coded status indicators

Modify the CSS in `streamlit_app.py` under `st.markdown("""<style>...`)

### Configuration

Edit settings in `streamlit_app.py`:
- `page_icon`: Change dashboard icon
- `layout`: Switch to 'centered' for different layout
- `api_base_url`: Default backend URL
- Cache TTL: Modify data refresh intervals

### Custom Queries

Add sample queries in the SQL page by editing the `samples` list in `page_sql_query()`.

## 🔧 Development

### Add New Page

1. Create function `def page_new_page():`
2. Add to pages list in sidebar
3. Add routing in `main()` function

Example:
```python
def page_new_feature():
    st.title("🆕 New Feature")
    # Add content here

# In main():
elif "New Feature" in current_page:
    page_new_feature()
```

### Add New Visualization

Use Plotly for consistency:
```python
import plotly.express as px

fig = px.line(data, x='date', y='value', title='My Chart')
st.plotly_chart(fig, use_container_width=True)
```

### Add New API Integration

Extend `APIClient` class:
```python
def new_endpoint(self, param):
    response = requests.get(
        f"{self.base_url}/api/v1/new-endpoint",
        params={'param': param},
        headers=self.headers,
        timeout=10
    )
    return response.json()
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] Backend health check shows green
- [ ] Dashboard loads all metrics
- [ ] Date range filters work
- [ ] Reports generate without errors
- [ ] SQL queries execute and return results
- [ ] Settings page shows correct backend URL
- [ ] Navigation between pages is smooth
- [ ] Visualizations render correctly
- [ ] No console errors in browser

### Test Data

The dashboard uses sample data for demonstration:
- 30 days of sales data
- 5 products with performance metrics
- 4 regions with regional metrics
- Pre-generated insights and opportunities

## 📈 Performance

### Caching Strategy

- **Dashboard metrics:** 5 minute cache
- **Analytics data:** 10 minute cache
- **Report history:** 30 minute cache
- **Configuration:** Session-level cache

Cache helps reduce API load and improves response times.

### Optimization Tips

1. Limit date ranges in analytics queries
2. Use pagination for large datasets
3. Enable browser caching headers
4. Run backend on same network
5. Use connection pooling in backend

## 🔒 Security

### Features

- JWT token-based authentication
- Secure API communication over HTTP/HTTPS
- Configurable API endpoints
- User session management via Streamlit session state
- Input validation for all user queries

### Best Practices

- Never commit API tokens to version control
- Use HTTPS in production
- Implement rate limiting on backend
- Validate all user inputs
- Monitor API logs for suspicious activity

## 🐛 Troubleshooting

### Backend Not Responding

```
Error: Connection refused at http://localhost:8001
```

**Solution:** 
1. Check backend is running: `curl http://localhost:8001/api/v1/health`
2. Verify correct API URL in Settings
3. Check firewall rules
4. Review backend logs for errors

### Slow Performance

**Solutions:**
1. Close other browser tabs
2. Check network connection speed
3. Review backend logs for slow queries
4. Increase cache TTL in code
5. Optimize date range selection

### Missing Data in Visualizations

**Solutions:**
1. Verify data exists in database
2. Check date range filter
3. Review backend query results
4. Clear cache: `streamlit run streamlit_app.py --logger.level=debug`

### Page Reload Issues

**Solution:**
Clear browser cache and restart Streamlit:
```bash
# Kill existing process
Ctrl+C

# Restart
streamlit run streamlit_app.py
```

## 📚 Documentation

### API Endpoints Used

- `GET /api/v1/health` - Backend health check
- `POST /api/v1/insights/generate` - Generate insights
- `POST /api/v1/reports/generate/{type}` - Generate reports
- `POST /api/v1/reports/{id}/format` - Format reports
- `POST /api/v1/text-to-sql/query` - Convert NL to SQL
- `GET /api/v1/text-to-sql/samples` - Get sample queries

See backend documentation for full API reference.

## 🚀 Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]
```

Build and run:
```bash
docker build -t autonomous-bi-frontend .
docker run -p 8501:8501 autonomous-bi-frontend
```

### Production Settings

Create `.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = true
maxUploadSize = 200

[logger]
level = "info"

[client]
toolbarMode = "minimal"
```

## 📝 License

This project is part of the Autonomous BI System.

## 🤝 Support

For issues or questions:
1. Check troubleshooting guide above
2. Review backend logs
3. Check API connectivity
4. Contact support team

## 🔄 Version History

### v1.0 (2026-06-09)
- Initial release
- 6 main pages
- Full API integration
- Multi-format report support
- Natural language query interface
- Real-time insights display
