import streamlit as st
import pandas as pd
import requests
import time
from database import get_db, Lead
from sqlalchemy.orm import Session
import plotly.express as px

st.set_page_config(page_title="LeadForge Dashboard", page_icon="🚀", layout="wide")

# API URL
API_URL = "http://localhost:8000"

# Initialize session state for authentication
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

def get_db_session():
    return next(get_db())

def login(email, password):
    """Authenticate user and get JWT token."""
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user_email = email
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

def logout():
    """Clear authentication."""
    st.session_state.token = None
    st.session_state.user_email = None

def get_headers():
    """Get headers with authentication token."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def fetch_stats():
    try:
        response = requests.get(f"{API_URL}/stats", headers=get_headers())
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            logout()
    except:
        return {}
    return {}

def trigger_scrape(niche):
    try:
        response = requests.post(f"{API_URL}/scrape/{niche}", headers=get_headers())
        if response.status_code == 200:
            st.success(f"Scraping started for {niche}!")
        elif response.status_code == 403:
            st.error("Scraping not available on your subscription tier. Please upgrade.")
        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            logout()
        else:
            st.error(f"Failed to start scraping: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")

# Login Page
if not st.session_state.token:
    st.title("🚀 LeadForge Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Sign In")
        email = st.text_input("Email", value="admin@leadforge.com")
        password = st.text_input("Password", type="password", value="admin")
        
        if st.button("Login", use_container_width=True):
            if login(email, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        st.markdown("---")
        st.info("**Demo Accounts:**\n\n"
                "**Admin (Enterprise):** admin@leadforge.com / admin\n\n"
                "**Free Tier:** free@test.com / test123")

else:
    # Sidebar
    st.sidebar.title("LeadForge 🚀")
    st.sidebar.write(f"👤 {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()
    
    page = st.sidebar.radio("Navigation", ["Dashboard", "Leads", "Scraper", "Logs"])
    
    if page == "Dashboard":
        st.title("System Overview")
        
        stats = fetch_stats()
        
        if stats:
            cols = st.columns(len(stats))
            for i, (niche, count) in enumerate(stats.items()):
                cols[i].metric(label=niche, value=count)
            
            # Chart
            df_stats = pd.DataFrame(list(stats.items()), columns=["Niche", "Count"])
            fig = px.bar(df_stats, x="Niche", y="Count", title="Leads per Niche", color="Niche")
            st.plotly_chart(fig)
        else:
            st.warning("Could not fetch stats. Please check your connection.")
    
    elif page == "Leads":
        st.title("Lead Database")
        
        db = get_db_session()
        
        # Filters
        niche_filter = st.selectbox("Filter by Niche", ["All"] + [r[0] for r in db.query(Lead.niche).distinct().all()])
        
        query = db.query(Lead)
        if niche_filter != "All":
            query = query.filter(Lead.niche == niche_filter)
        
        leads = query.order_by(Lead.date_added.desc()).limit(500).all()
        
        if leads:
            data = [lead.to_dict() for lead in leads]
            df = pd.DataFrame(data)
            st.dataframe(df)
            
            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download CSV",
                csv,
                "leads.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("No leads found.")
        
        db.close()
    
    elif page == "Scraper":
        st.title("Scraper Control")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Real Estate")
            if st.button("Scrape Real Estate"):
                trigger_scrape("Real Estate")
                
        with col2:
            st.subheader("Tutors")
            if st.button("Scrape Tutors"):
                trigger_scrape("Tutors")
                
        with col3:
            st.subheader("Service Providers")
            if st.button("Scrape Service Providers"):
                trigger_scrape("Service Providers")
    
    elif page == "Logs":
        st.title("System Logs")
        
        if st.button("Refresh Logs"):
            pass
            
        try:
            with open("app.log", "r") as f:
                lines = f.readlines()
                st.text_area("Log Output", "".join(lines[-50:]), height=600)
        except FileNotFoundError:
            st.error("Log file not found.")
