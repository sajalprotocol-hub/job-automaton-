"""
Job Scraper for Indeed India
Scrapes Data Analyst and related roles from Indeed India
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import csv
import os


class IndeedScraper:
    """
    Scraper class for Indeed India job listings
    """
    
    def __init__(self):
        """Initialize the scraper with headers to mimic a browser"""
        self.base_url = "https://in.indeed.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def search_jobs(self, query="Data Analyst", location="India", max_pages=5):
        """
        Search for jobs on Indeed India
        
        Args:
            query: Job search query (default: "Data Analyst")
            location: Location filter (default: "India")
            max_pages: Maximum number of pages to scrape (default: 5)
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Search terms for Data Analyst-related roles
        search_queries = [
            "Data Analyst",
            "Business Analyst",
            "BI Analyst",
            "Reporting Analyst",
            "Analytics Executive",
            "Junior Data Analyst"
        ]
        
        print(f"Starting job scrape for {len(search_queries)} search queries...")
        
        for search_query in search_queries:
            print(f"\nSearching for: {search_query}")
            
            for page in range(max_pages):
                try:
                    # Indeed URL structure
                    start = page * 10  # Indeed shows 10 jobs per page
                    url = f"{self.base_url}/jobs"
                    params = {
                        'q': search_query,
                        'l': location,
                        'start': start
                    }
                    
                    print(f"  Page {page + 1}/{max_pages}...", end=" ")
                    
                    # Make request with error handling
                    response = self.session.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find job cards (Indeed uses different selectors - we'll try common ones)
                    job_cards = soup.find_all('div', class_='job_seen_beacon') or \
                               soup.find_all('div', {'data-jk': True}) or \
                               soup.find_all('a', {'data-jk': True})
                    
                    if not job_cards:
                        # Try alternative selector
                        job_cards = soup.find_all('div', class_='jobCard')
                    
                    if not job_cards:
                        print("No jobs found on this page.")
                        break
                    
                    page_jobs = self._parse_job_cards(job_cards, search_query)
                    jobs.extend(page_jobs)
                    
                    print(f"Found {len(page_jobs)} jobs")
                    
                    # Rate limiting - be respectful to Indeed's servers
                    time.sleep(2)
                    
                    # If we got fewer than 10 jobs, we've reached the last page
                    if len(page_jobs) < 10:
                        break
                        
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching page {page + 1}: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error on page {page + 1}: {e}")
                    continue
        
        print(f"\nTotal jobs scraped: {len(jobs)}")
        return jobs
    
    def _parse_job_cards(self, job_cards, search_query):
        """
        Parse job card HTML elements into job dictionaries
        
        Args:
            job_cards: List of BeautifulSoup elements containing job info
            search_query: The search query used (for tracking)
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        for card in job_cards:
            try:
                # Extract job title
                title_elem = card.find('h2', class_='jobTitle') or \
                           card.find('a', class_='jcs-JobTitle') or \
                           card.find('span', title=True)
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    # Clean up title (remove "new" badges, etc.)
                    title = title.replace('new', '').strip()
                else:
                    title = "N/A"
                
                # Extract company name
                company_elem = card.find('span', class_='companyName') or \
                             card.find('a', {'data-testid': 'company-name'}) or \
                             card.find('span', {'data-testid': 'company-name'})
                
                if company_elem:
                    company = company_elem.get_text(strip=True)
                else:
                    company = "N/A"
                
                # Extract location
                location_elem = card.find('div', class_='companyLocation') or \
                              card.find('div', {'data-testid': 'text-location'})
                
                if location_elem:
                    location = location_elem.get_text(strip=True)
                else:
                    location = "N/A"
                
                # Only add jobs that have valid data
                if title != "N/A" and company != "N/A":
                    job = {
                        'Job Title': title,
                        'Company Name': company,
                        'Location': location,
                        'Platform': 'Indeed',
                        'Company Type': self._infer_company_type(company),
                        'Status': 'Not Applied',
                        'Date Added': datetime.now().strftime('%Y-%m-%d')
                    }
                    jobs.append(job)
                    
            except Exception as e:
                # Skip jobs that can't be parsed
                continue
        
        return jobs
    
    def _infer_company_type(self, company_name):
        """
        Infer company type based on company name
        This is a simple heuristic - can be improved later
        
        Args:
            company_name: Name of the company
            
        Returns:
            Company type: "Startup", "Mid-size", "MNC", or "Unknown"
        """
        company_lower = company_name.lower()
        
        # Known MNCs (add more as needed)
        mnc_keywords = ['microsoft', 'google', 'amazon', 'accenture', 'tcs', 'infosys', 
                       'wipro', 'cognizant', 'ibm', 'oracle', 'sap', 'deloitte', 
                       'pwc', 'ey', 'kpmg', 'capgemini', 'tech mahindra', 'hcl']
        
        # Check for MNC
        for keyword in mnc_keywords:
            if keyword in company_lower:
                return "MNC"
        
        # Very small companies might be startups
        # This is a simple heuristic - in production, you'd use company size APIs
        if len(company_name) < 15:
            return "Startup"
        
        # Default to Mid-size for others
        return "Mid-size"
    
    def save_to_csv(self, jobs, filename='tracker.csv'):
        """
        Save jobs to CSV file, avoiding duplicates
        
        Args:
            jobs: List of job dictionaries
            filename: Output CSV filename
        """
        if not jobs:
            print("No jobs to save.")
            return
        
        # Convert to DataFrame
        df_new = pd.DataFrame(jobs)
        
        # Load existing jobs if file exists
        if os.path.exists(filename):
            df_existing = pd.read_csv(filename)
            
            # Remove duplicates based on Job Title + Company Name
            # Keep existing entries (preserve status, etc.)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined = df_combined.drop_duplicates(
                subset=['Job Title', 'Company Name'],
                keep='first'  # Keep the first occurrence (existing entries)
            )
            
            # Count new jobs
            new_jobs_count = len(df_combined) - len(df_existing)
            print(f"\nAdded {new_jobs_count} new jobs to {filename}")
            print(f"Total jobs in tracker: {len(df_combined)}")
            
            df_final = df_combined
        else:
            df_final = df_new
            print(f"\nCreated new file: {filename}")
            print(f"Total jobs: {len(df_final)}")
        
        # Ensure columns are in the correct order
        columns = ['Job Title', 'Company Name', 'Location', 'Platform', 
                  'Company Type', 'Status', 'Date Added']
        
        # Reorder columns
        df_final = df_final.reindex(columns=columns)
        
        # Save to CSV
        df_final.to_csv(filename, index=False)
        print(f"Jobs saved to {filename}")


def main():
    """
    Main function to run the scraper
    """
    print("=" * 60)
    print("Indeed India Job Scraper - Data Analyst Roles")
    print("=" * 60)
    
    # Initialize scraper
    scraper = IndeedScraper()
    
    # Scrape jobs
    jobs = scraper.search_jobs(
        query="Data Analyst",
        location="India",
        max_pages=5  # Adjust based on how many jobs you want
    )
    
    # Save to CSV
    if jobs:
        scraper.save_to_csv(jobs, 'tracker.csv')
        print("\n✓ Scraping completed successfully!")
    else:
        print("\n⚠ No jobs were scraped. Please check:")
        print("  - Internet connection")
        print("  - Indeed website accessibility")
        print("  - Selectors may need updating if Indeed changed their HTML structure")


if __name__ == "__main__":
    main()


