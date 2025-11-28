# LeadForge 🚀

**A Production-Ready SaaS Platform for Automated Lead Generation**

LeadForge is a comprehensive lead generation system that automates the collection, enrichment, and management of business leads across multiple niches. Built with Flask and modern Python technologies, it features a RESTful API, real-time dashboard, and subscription-based access control.

---

## 🌟 Features

### Core Capabilities
- **Automated Lead Scraping**: Collect leads from multiple sources across different niches (Real Estate, Tutors, Service Providers)
- **Data Enrichment**: Enhance lead data with business ratings, reviews, and verification status
- **RESTful API**: Flask-powered backend with JWT authentication
- **Interactive Dashboard**: Streamlit-based UI for visualization and control
- **Subscription Tiers**: Free, Pro, and Enterprise plans with enforced limits
- **Async Architecture**: Non-blocking scraping operations for better performance
- **Database Persistence**: SQLAlchemy ORM with SQLite (production-ready for PostgreSQL)

### Security & Authentication
- JWT token-based authentication
- Bcrypt password hashing
- Protected API endpoints
- Session management

---

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Dashboard Guide](#dashboard-guide)
- [Subscription Tiers](#subscription-tiers)
- [Architecture](#architecture)
- [Development](#development)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Installation

### Prerequisites
- Python 3.13+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
```bash
cd /path/to/LeadForge
```

2. **Create and activate virtual environment**
```bash
python3 -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database**
The database will be automatically initialized on first run, creating:
- SQLite database (`leads.db`)
- Default admin user
- Required tables

---

## ⚡ Quick Start

### Running the Application

You need to run **two services** simultaneously:

#### Terminal 1: API Server
```bash
PYTHONPATH=src FLASK_APP=app.py flask run --host=0.0.0.0 --port=8000
```

#### Terminal 2: Dashboard
```bash
PYTHONPATH=src streamlit run src/dashboard.py
```

### Access Points
- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8501 (or 8502 if 8501 is busy)
- **API Docs**: http://localhost:8000/docs (Swagger UI)

### Default Credentials

| Account Type | Email | Password | Tier | Capabilities |
|-------------|-------|----------|------|--------------|
| Admin | `admin@leadforge.com` | `admin` | Enterprise | Full access, unlimited scraping |
| Free User | `free@test.com` | `test123` | Free | View 5 leads max, no scraping |

---

## 📖 Usage

### 1. Dashboard Access

1. Open http://localhost:8501 in your browser
2. Login with credentials (admin or free tier)
3. Navigate through the dashboard:
   - **Dashboard**: View statistics and charts
   - **Leads**: Browse, filter, and download leads
   - **Scraper**: Trigger scraping jobs (Enterprise/Pro only)
   - **Logs**: View system logs

### 2. API Access

#### Get Authentication Token
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@leadforge.com&password=admin"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Use Token for API Calls
```bash
# Set token variable
TOKEN="your_token_here"

# Get statistics
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/stats

# Get leads
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/leads?limit=10"

# Trigger scraping (Enterprise/Pro only)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/scrape/Real%20Estate"
```

---

## 🔌 API Documentation

### Endpoints

#### Authentication
- `POST /api/auth/login` - Login and get JWT token
  - **Body**: `username` (email), `password`
  - **Returns**: JWT access token

#### Leads Management
- `GET /api/leads` - Retrieve leads
  - **Auth**: Required
  - **Query Params**: `niche` (optional), `limit` (default: 100)
  - **Free Tier Limit**: Max 5 leads
  - **Returns**: Array of lead objects

- `GET /api/stats` - Get lead statistics
  - **Auth**: Required
  - **Returns**: Lead counts per niche

#### Scraping
- `POST /api/scrape/{niche}` - Trigger scraping job
  - **Auth**: Required (Pro/Enterprise only)
  - **Path Param**: `niche` (real_estate, tutors, service_providers)
  - **Returns**: Job status

#### Health
- `GET /` - API welcome message
- `GET /api/health` - Health check endpoint

### Interactive API Docs
Flask does not provide auto-generated API docs. For interactive testing, use tools like Postman or curl.

---

## 📊 Dashboard Guide

### Login Page
- Pre-filled with admin credentials for quick access
- Shows available demo accounts
- Session persists until logout

### Dashboard Tab
- **Metrics Cards**: Total leads per niche
- **Bar Chart**: Visual representation of lead distribution
- **Real-time Updates**: Refresh to see latest data

### Leads Tab
- **Filter**: By niche (All, Real Estate, Tutors, Service Providers)
- **Table View**: All lead details with sorting
- **Download**: Export filtered leads as CSV
- **Direct DB Access**: Bypasses API for faster queries

### Scraper Tab
- **Three Scraper Buttons**: One per niche
- **Instant Feedback**: Success/error messages
- **Tier Enforcement**: Free tier users see upgrade message

### Logs Tab
- **Last 50 Lines**: Recent system activity
- **Refresh Button**: Update log view
- **File Path**: `app.log` in project root

---

## 💎 Subscription Tiers

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| View Leads | ✅ (5 max) | ✅ Unlimited | ✅ Unlimited |
| Download CSV | ✅ | ✅ | ✅ |
| Trigger Scraping | ❌ | ✅ | ✅ |
| API Access | ✅ Limited | ✅ Full | ✅ Full |
| Dashboard Access | ✅ | ✅ | ✅ |
| Data Enrichment | ✅ | ✅ | ✅ |

### Tier Enforcement
- Enforced at API level
- Free tier: `GET /leads` returns max 5 results
- Free tier: `POST /scrape/*` returns 403 Forbidden
- Dashboard shows appropriate error messages

---

## 🏗️ Architecture

### Tech Stack
- **Backend**: Flask (Python web framework)
- **Frontend**: Streamlit (Python dashboard framework)
- **Database**: SQLAlchemy ORM + SQLite (PostgreSQL-ready)
- **Authentication**: Flask-JWT-Extended + Bcrypt hashing
- **Data Processing**: Pandas for data manipulation
- **Visualization**: Plotly for charts

### Project Structure
```
LeadForge/
├── src/
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration
│   ├── auth.py                # Authentication logic
│   ├── database.py            # Database models & setup
│   ├── logger.py              # Logging configuration
│   ├── dashboard.py           # Streamlit dashboard
│   ├── main.py                # CLI entry point
│   ├── routes/                # API routes
│   │   ├── auth_routes.py
│   │   ├── lead_routes.py
│   │   ├── scraper_routes.py
│   │   └── health_routes.py
│   ├── collectors/            # Scraping modules
│   │   ├── base_collector.py
│   │   ├── real_estate_collector.py
│   │   ├── tutor_collector.py
│   │   └── service_provider_collector.py
│   ├── processors/            # Data processing
│   │   └── data_processor.py
│   ├── generators/            # Report generation
│   │   └── report_generator.py
│   └── enrichment/            # Data enrichment
│       ├── base_enricher.py
│       └── google_places.py
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Container orchestration
├── leads.db                   # SQLite database (auto-created)
├── app.log                    # Application logs (auto-created)
└── README.md                  # This file
```

### Database Schema
- **users**: Authentication and subscription management
- **leads**: Collected lead data
- **sources**: Scraping source tracking
- **exports**: Report generation history
- **blacklist**: DNC (Do Not Contact) list

---

## 🛠️ Development

### Running Tests
```bash
# Test enrichment
PYTHONPATH=src python test_enrichment.py

# Test API endpoints
curl http://localhost:8000/api/health
```

### Adding a New Niche

1. **Create collector** in `src/collectors/`:
```python
from .base_collector import BaseCollector

class NewNicheCollector(BaseCollector):
    def __init__(self, db_session=None):
        super().__init__("New Niche", db_session)
    
    async def collect(self, num_samples=10):
        # Your scraping logic here
        pass
```

2. **Register in API** (`src/routes/scraper_routes.py`):
```python
from collectors.new_niche_collector import NewNicheCollector

niche_map = {
    # ...existing niches...
    "new_niche": (NewNicheCollector, "New Niche")
}
```

3. **Add to dashboard** (`src/dashboard.py`):
```python
if st.button("Scrape New Niche"):
    trigger_scrape("New Niche")
```

### Environment Variables
For production, set these environment variables:
- `SECRET_KEY`: JWT secret (change from default)
- `DATABASE_URL`: PostgreSQL connection string
- `API_HOST`: API server host
- `API_PORT`: API server port

---

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Configuration
- **Port 8000**: API server
- **Volumes**: Database and logs persisted
- **Auto-restart**: Unless stopped manually

---

## 🔧 Troubleshooting

### Common Issues

#### "Connection refused" on Dashboard
**Problem**: API server not running  
**Solution**: Start API server in separate terminal
```bash
PYTHONPATH=src FLASK_APP=app.py flask run --host=0.0.0.0 --port=8000
```

#### "Invalid credentials" on Login
**Problem**: Wrong email/password or API not running  
**Solution**: 
1. Verify API is running: `curl http://localhost:8000/health`
2. Use exact credentials: `admin@leadforge.com` / `admin`
3. Check for typos (case-sensitive)

#### "Module not found" Errors
**Problem**: PYTHONPATH not set  
**Solution**: Always prefix commands with `PYTHONPATH=src`

#### Database Locked
**Problem**: Multiple processes accessing SQLite  
**Solution**: Close all connections, restart services

#### Port Already in Use
**Problem**: Port 8000 or 8501 occupied  
**Solution**: 
```bash
# Find process
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Logs
Check `app.log` for detailed error messages:
```bash
tail -f app.log
```

---

## 📝 License

This project is for educational and demonstration purposes.

---

## 🤝 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check application logs in `app.log`

---

## 🎯 Roadmap

- [ ] PostgreSQL migration
- [ ] Real Google Places API integration
- [ ] Celery/Redis job queue
- [ ] Stripe payment integration
- [ ] Email notifications
- [ ] Advanced filtering and search
- [ ] Export to multiple formats
- [ ] Webhook support
- [ ] Rate limiting
- [ ] API key authentication

---

**Built with  using FastAPI, Streamlit, and Python**
