# Job Automation Tool - Data Analyst Roles

A Python-based job scraping and tracking tool for Data Analyst positions in the Indian job market.

## 🎯 Features

- **Automated Job Scraping**: Scrapes Data Analyst-related roles from Indeed India
- **Real-time Dashboard**: Streamlit-based dashboard to view and filter jobs
- **Smart Filtering**: Filter by status, company type, and search by keywords
- **Duplicate Prevention**: Automatically prevents duplicate job entries
- **Company Classification**: Infers company type (Startup/Mid-size/MNC)
- **CSV Storage**: Simple CSV-based storage (easily scalable to databases)

## 📋 Target Roles

- Data Analyst
- Business Analyst
- BI Analyst
- Reporting Analyst
- Analytics Executive
- Junior Data Analyst

## 🏢 Target Companies

- Startups
- Mid-size companies
- Large enterprises / MNCs

## 📁 Project Structure

```
job-automation/
├── scraper.py          # Job scraping logic
├── app.py              # Streamlit dashboard
├── tracker.csv         # Job data storage (auto-generated)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Scraper

```bash
python scraper.py
```

This will:
- Scrape jobs from Indeed India
- Save results to `tracker.csv`
- Avoid duplicates automatically

### 3. Launch the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📊 Dashboard Features

### Real-time View
- View all scraped jobs in a searchable table
- See job statistics (total, filtered, applied status)
- Company type distribution charts

### Filters
- **Status**: Filter by "Not Applied" or "Applied"
- **Company Type**: Filter by Startup, Mid-size, MNC, or Unknown
- **Search**: Search by job title, company name, or location

### Actions
- **Run Scraper**: Trigger scraping directly from the dashboard
- **Refresh Data**: Reload data from CSV
- **Export**: Download filtered results as CSV

## 📝 CSV Structure

The `tracker.csv` file contains the following columns:

| Column | Description |
|--------|-------------|
| Job Title | Job position title |
| Company Name | Company name |
| Location | Job location |
| Platform | Source platform (e.g., "Indeed") |
| Company Type | Startup / Mid-size / MNC / Unknown |
| Status | Not Applied / Applied |
| Date Added | Date when job was added (YYYY-MM-DD) |

## ⚙️ Configuration

### Adjust Scraping Parameters

Edit `scraper.py` to customize:

```python
# In main() function:
jobs = scraper.search_jobs(
    query="Data Analyst",
    location="India",
    max_pages=5  # Increase for more jobs
)
```

### Add More Search Queries

Edit the `search_queries` list in `scraper.py`:

```python
search_queries = [
    "Data Analyst",
    "Business Analyst",
    # Add more queries here
]
```

## 🔧 Troubleshooting

### Scraper Not Finding Jobs

1. **Check Internet Connection**: Ensure you're connected to the internet
2. **Indeed Structure Changed**: Indeed may have updated their HTML structure. Check the selectors in `_parse_job_cards()` method
3. **Rate Limiting**: If blocked, increase the delay in `time.sleep(2)` to a higher value

### Dashboard Not Loading

1. **Check if tracker.csv exists**: Run the scraper first
2. **Verify Streamlit Installation**: Run `pip install streamlit --upgrade`
3. **Check Port**: Ensure port 8501 is not in use

## 🛠️ Future Enhancements (Planned)

- Skill-based filtering (SQL, Excel, Power BI, Python)
- Fresher / 0–2 year role filtering
- Resume–JD keyword match scoring
- Multi-platform scraping (LinkedIn, Naukri, Wellfound)
- Editable application status inside dashboard
- Email notifications for new jobs
- Database integration (PostgreSQL/MySQL)

## 📄 License

This project is for personal use. Please respect Indeed's Terms of Service and robots.txt when scraping.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## ⚠️ Disclaimer

- Web scraping should be done responsibly
- Respect website terms of service
- Use rate limiting to avoid overloading servers
- This tool is for personal job search purposes only

## 📞 Support

For issues or questions, please check:
1. Error messages in the console
2. Scraper output in the dashboard
3. CSV file integrity

---

**Built with ❤️ for the Indian job market**


