"""
Streamlit Dashboard for Job Automation Tool
Real-time view of Data Analyst job listings
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import subprocess
import sys


def load_jobs():
    """
    Load jobs from tracker.csv
    
    Returns:
        DataFrame with jobs or empty DataFrame if file doesn't exist
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'tracker.csv')
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()


def run_scraper():
    """
    Run the scraper script in the background
    
    Returns:
        Success status
    """
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scraper_path = os.path.join(script_dir, 'scraper.py')
        
        # Run scraper.py from the correct directory
        result = subprocess.run(
            [sys.executable, scraper_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=script_dir  # Set working directory
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Scraper timed out after 5 minutes"
    except Exception as e:
        return False, "", str(e)


def main():
    """
    Main Streamlit app
    """
    # Page configuration
    st.set_page_config(
        page_title="Job Automation Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .stDataFrame {
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<p class="main-header">📊 Job Automation Dashboard</p>', unsafe_allow_html=True)
    st.markdown("**Data Analyst Roles Tracker - India Job Market**")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        st.divider()
        
        # Scraper section
        st.subheader("🔍 Scraper")
        if st.button("🚀 Run Scraper", use_container_width=True, type="primary"):
            with st.spinner("Scraping jobs from Indeed India... This may take a few minutes."):
                success, stdout, stderr = run_scraper()
                
                if success:
                    st.success("✓ Scraping completed!")
                    if stdout:
                        st.text_area("Scraper Output", stdout, height=100, disabled=True)
                    st.rerun()
                else:
                    st.error("✗ Scraping failed!")
                    if stderr:
                        st.text_area("Error Details", stderr, height=100, disabled=True)
        
        st.divider()
        
        # Filters
        st.subheader("🔽 Filters")
        
        # Status filter
        status_options = ["All", "Not Applied", "Applied"]
        selected_status = st.selectbox(
            "Filter by Status",
            status_options,
            index=0
        )
        
        # Company Type filter
        company_type_options = ["All", "Startup", "Mid-size", "MNC", "Unknown"]
        selected_company_type = st.selectbox(
            "Filter by Company Type",
            company_type_options,
            index=0
        )
        
        st.divider()
        
        # Info section
        st.subheader("ℹ️ Info")
        st.markdown("""
        **How to use:**
        1. Click "Run Scraper" to fetch new jobs
        2. Use filters to narrow down results
        3. View job details in the table below
        4. Export filtered data if needed
        """)
    
    # Load jobs
    df = load_jobs()
    
    if df.empty:
        st.warning("⚠️ No jobs found. Please run the scraper first!")
        st.info("💡 Click 'Run Scraper' in the sidebar to start collecting jobs.")
        return
    
    # Apply filters
    df_filtered = df.copy()
    
    # Check if required columns exist
    required_columns = ['Status', 'Company Type']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"⚠️ CSV is missing required columns: {', '.join(missing_columns)}")
        st.info("Please run the scraper to generate a proper CSV file.")
        return
    
    if selected_status != "All":
        df_filtered = df_filtered[df_filtered['Status'] == selected_status]
    
    if selected_company_type != "All":
        df_filtered = df_filtered[df_filtered['Company Type'] == selected_company_type]
    
    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    # Metrics
    with col1:
        st.metric("📋 Total Jobs", len(df))
    
    with col2:
        st.metric("👀 Filtered Jobs", len(df_filtered))
    
    with col3:
        if 'Status' in df.columns:
            not_applied = len(df[df['Status'] == 'Not Applied'])
            st.metric("⏳ Not Applied", not_applied)
        else:
            st.metric("⏳ Not Applied", 0)
    
    with col4:
        if 'Status' in df.columns:
            applied = len(df[df['Status'] == 'Applied'])
            st.metric("✅ Applied", applied)
        else:
            st.metric("✅ Applied", 0)
    
    st.divider()
    
    # Company Type breakdown
    st.subheader("📊 Company Type Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Company Type' in df.columns:
            company_counts = df['Company Type'].value_counts()
            st.bar_chart(company_counts)
    
    with col2:
        if 'Company Type' in df.columns:
            company_pct = df['Company Type'].value_counts(normalize=True) * 100
            st.dataframe(
                pd.DataFrame({
                    'Company Type': company_pct.index,
                    'Percentage': company_pct.values.round(2)
                }),
                use_container_width=True,
                hide_index=True
            )
    
    st.divider()
    
    # Jobs table
    st.subheader(f"📋 Job Listings ({len(df_filtered)} jobs)")
    
    # Search box
    search_term = st.text_input("🔍 Search jobs (by title, company, or location)", "")
    
    if search_term:
        # Check if search columns exist
        search_columns = []
        if 'Job Title' in df_filtered.columns:
            search_columns.append(df_filtered['Job Title'].str.contains(search_term, case=False, na=False))
        if 'Company Name' in df_filtered.columns:
            search_columns.append(df_filtered['Company Name'].str.contains(search_term, case=False, na=False))
        if 'Location' in df_filtered.columns:
            search_columns.append(df_filtered['Location'].str.contains(search_term, case=False, na=False))
        
        if search_columns:
            mask = search_columns[0]
            for col_mask in search_columns[1:]:
                mask = mask | col_mask
            df_filtered = df_filtered[mask]
            st.info(f"Found {len(df_filtered)} jobs matching '{search_term}'")
        else:
            st.warning("Search columns not found in data.")
    
    # Display table
    if not df_filtered.empty:
        # Format the dataframe for better display
        display_df = df_filtered.copy()
        
        # Show table with all columns
        st.dataframe(
            display_df,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
        # Export button
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"jobs_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No jobs match the current filters. Try adjusting your filters.")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <small>Job Automation Tool v1.0 | Last updated: {}</small>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)


if __name__ == "__main__":
    main()

