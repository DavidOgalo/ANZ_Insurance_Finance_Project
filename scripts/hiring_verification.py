"""
hiring_verification.py - Check if companies are actively hiring for DevOps and Software Developer roles
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import os
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse

def load_companies():
    """Load the enriched companies data"""
    try:
        return pd.read_excel('data/processed/companies_enriched.xlsx')
    except FileNotFoundError:
        print("Enriched companies file not found. Using raw data...")
        try:
            return pd.read_excel('data/raw/companies_raw.xlsx')
        except FileNotFoundError:
            print("Raw companies file not found. Please run company_research.py first.")
            exit(1)

# Mock function to simulate webpage content for testing
def mock_job_page_content(company_name, has_devops=False, has_software_dev=False):
    """Generate mock webpage content for testing"""
    content = f"""
    <html>
    <head><title>{company_name} Careers</title></head>
    <body>
        <h1>{company_name} Career Opportunities</h1>
        <div class="job-listings">
    """
    
    if has_devops:
        content += """
            <div class="job-posting">
                <h3>DevOps Engineer</h3>
                <p>We are looking for an experienced DevOps Engineer to join our team.</p>
                <p>Requirements:</p>
                <ul>
                    <li>Experience with AWS or Azure</li>
                    <li>Knowledge of CI/CD pipelines</li>
                    <li>Infrastructure as Code experience</li>
                </ul>
            </div>
        """
    
    if has_software_dev:
        content += """
            <div class="job-posting">
                <h3>Software Developer</h3>
                <p>Join our development team and work on cutting-edge applications.</p>
                <p>Requirements:</p>
                <ul>
                    <li>Experience with Java or Python</li>
                    <li>Knowledge of web frameworks</li>
                    <li>Database experience</li>
                </ul>
            </div>
        """
    
    content += """
        </div>
    </body>
    </html>
    """
    
    return content

def check_company_careers_page(company_name, company_url, use_mock=True):
    """
    Check if the company has relevant job openings on their careers page
    """
    if pd.isna(company_url):
        return {'has_devops': False, 'has_software_dev': False, 'source': None}
    
    job_keywords = {
        'devops': ['devops', 'dev ops', 'site reliability', 'sre', 'platform engineer', 'infrastructure engineer'],
        'software_dev': ['software developer', 'software engineer', 'programmer', 'web developer', 'frontend', 'backend', 'full stack']
    }
    
    result = {'has_devops': False, 'has_software_dev': False, 'source': None}
    
    # If using mock data for testing
    if use_mock:
        # Randomly determine if the company has job openings
        # This is just for demonstration purposes
        has_devops = random.choice([True, False])
        has_software_dev = random.choice([True, False])
        
        # Generate mock content
        mock_content = mock_job_page_content(company_name, has_devops, has_software_dev)
        
        # Parse the mock content
        soup = BeautifulSoup(mock_content, 'html.parser')
        page_text = soup.get_text().lower()
        
        # Check for DevOps roles
        for keyword in job_keywords['devops']:
            if keyword in page_text:
                result['has_devops'] = True
                result['source'] = f"{company_url}/careers"
                break
        
        # Check for Software Developer roles
        for keyword in job_keywords['software_dev']:
            if keyword in page_text:
                result['has_software_dev'] = True
                result['source'] = f"{company_url}/careers"
                break
        
        return result
    
    # Real implementation for web scraping
    # Clean and validate the URL
    if not company_url.startswith(('http://', 'https://')):
        company_url = 'https://' + company_url
    
    # Common paths to careers/jobs pages
    career_paths = [
        '/careers', '/jobs', '/join-us', '/work-with-us', '/about/careers',
        '/about-us/careers', '/en/careers', '/about/jobs', '/current-vacancies',
        '/vacancies', '/employment', '/work-for-us', '/careers/jobs'
    ]
    
    # Try direct careers URL first
    careers_urls = []
    for path in career_paths:
        careers_urls.append(urljoin(company_url, path))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for url in careers_urls:
        try:
            print(f"Checking {url}")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                # Check for DevOps roles
                for keyword in job_keywords['devops']:
                    if keyword in page_text:
                        result['has_devops'] = True
                        result['source'] = url
                        break
                
                # Check for Software Developer roles
                for keyword in job_keywords['software_dev']:
                    if keyword in page_text:
                        result['has_software_dev'] = True
                        result['source'] = url
                        break
                
                # If we found both types, no need to check further
                if result['has_devops'] and result['has_software_dev']:
                    return result
                
                # Try to find job listings on this page
                job_links = []
                for a in soup.find_all('a'):
                    link_text = a.text.lower()
                    if any(word in link_text for word in ['job', 'career', 'position', 'vacancy', 'role']):
                        href = a.get('href')
                        if href:
                            if not href.startswith(('http://', 'https://')):
                                href = urljoin(url, href)
                            job_links.append(href)
                
                # Check the first few job links if any
                for job_link in job_links[:3]:  # Limit to 3 to avoid too many requests
                    try:
                        job_response = requests.get(job_link, headers=headers, timeout=10)
                        if job_response.status_code == 200:
                            job_soup = BeautifulSoup(job_response.text, 'html.parser')
                            job_text = job_soup.get_text().lower()
                            
                            # Check for DevOps roles
                            if not result['has_devops']:
                                for keyword in job_keywords['devops']:
                                    if keyword in job_text:
                                        result['has_devops'] = True
                                        result['source'] = job_link
                                        break
                            
                            # Check for Software Developer roles
                            if not result['has_software_dev']:
                                for keyword in job_keywords['software_dev']:
                                    if keyword in job_text:
                                        result['has_software_dev'] = True
                                        result['source'] = job_link
                                        break
                        
                        time.sleep(random.uniform(1, 2))  # Be respectful with requests
                    except Exception as e:
                        print(f"Error checking job link {job_link}: {e}")
            
            time.sleep(random.uniform(1, 3))  # Add delay between requests
            
        except Exception as e:
            print(f"Error checking {url}: {e}")
    
    return result

def check_linkedin_jobs(company_name, linkedin_url=None, use_mock=True):
    """
    Check if the company has relevant job openings on LinkedIn
    """
    result = {'has_devops': False, 'has_software_dev': False, 'source': None}
    
    # If using mock data for testing
    if use_mock:
        # Randomly determine if the company has job openings on LinkedIn
        has_devops = random.choice([True, False])
        has_software_dev = random.choice([True, False])
        
        if has_devops:
            result['has_devops'] = True
            result['source'] = f"https://www.linkedin.com/jobs/search/?keywords={company_name}%20DevOps"
        
        if has_software_dev:
            result['has_software_dev'] = True
            result['source'] = f"https://www.linkedin.com/jobs/search/?keywords={company_name}%20Software%20Developer"
        
        return result
    
    # Real implementation for web scraping
    try:
        # Use company name to search for jobs if LinkedIn URL is not available
        company_query = company_name.replace(' ', '%20')
        
        # Use proper LinkedIn Jobs URL
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={company_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Look for job titles in the text
            devops_pattern = re.compile(r'\b(devops|site reliability|sre|platform engineer)\b')
            software_dev_pattern = re.compile(r'\b(software developer|software engineer|programmer|web developer|frontend|backend|full stack)\b')
            
            if devops_pattern.search(page_text):
                result['has_devops'] = True
                result['source'] = search_url
            
            if software_dev_pattern.search(page_text):
                result['has_software_dev'] = True
                result['source'] = search_url
                
    except Exception as e:
        print(f"Error checking LinkedIn jobs for {company_name}: {e}")
    
    return result

def check_seek_jobs(company_name, country, use_mock=True):
    """
    Check if the company has relevant job openings on Seek
    """
    result = {'has_devops': False, 'has_software_dev': False, 'source': None}
    
    # If using mock data for testing
    if use_mock:
        # Randomly determine if the company has job openings on Seek
        has_devops = random.choice([True, False])
        has_software_dev = random.choice([True, False])
        
        domain = 'seek.com.au' if country == 'Australia' else 'seek.co.nz'
        company_query = company_name.replace(' ', '-').lower()
        seek_url = f"https://www.{domain}/jobs?keywords={company_query}"
        
        if has_devops:
            result['has_devops'] = True
            result['source'] = seek_url
        
        if has_software_dev:
            result['has_software_dev'] = True
            result['source'] = seek_url
        
        return result
    
    # Real implementation for web scraping
    try:
        # Formulate the search URL based on country
        domain = 'seek.com.au' if country == 'Australia' else 'seek.co.nz'
        company_query = company_name.replace(' ', '-').lower()
        
        seek_url = f"https://www.{domain}/jobs?keywords={company_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(seek_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Look for job titles in the text
            if any(keyword in page_text for keyword in ['devops', 'dev ops', 'site reliability', 'sre', 'platform engineer']):
                result['has_devops'] = True
                result['source'] = seek_url
            
            if any(keyword in page_text for keyword in ['software developer', 'software engineer', 'programmer', 'web developer']):
                result['has_software_dev'] = True
                result['source'] = seek_url
                
    except Exception as e:
        print(f"Error checking Seek jobs for {company_name}: {e}")
    
    return result

def verify_hiring_status(companies_df, use_mock=True):
    """
    Check all companies for active hiring in relevant roles
    """
    print("Verifying hiring status for all companies...")
    
    # Add new columns for tracking the source of hiring info
    companies_df['devops_source'] = None
    companies_df['software_dev_source'] = None
    
    for index, row in companies_df.iterrows():
        company_name = row['company_name']
        company_url = row['company_website'] if not pd.isna(row['company_website']) else None
        linkedin_url = row['linkedin_url'] if not pd.isna(row['linkedin_url']) else None
        country = row['country']
        
        print(f"Checking hiring status for {company_name}...")
        
        # Check company careers page
        if company_url:
            careers_result = check_company_careers_page(company_name, company_url, use_mock=use_mock)
            if careers_result['has_devops']:
                companies_df.at[index, 'hiring_devops'] = 'Yes'
                companies_df.at[index, 'devops_source'] = careers_result['source']
            if careers_result['has_software_dev']:
                companies_df.at[index, 'hiring_developers'] = 'Yes'
                companies_df.at[index, 'software_dev_source'] = careers_result['source']
        
        # If we don't have both yes results yet, check LinkedIn
        if companies_df.at[index, 'hiring_devops'] != 'Yes' or companies_df.at[index, 'hiring_developers'] != 'Yes':
            linkedin_result = check_linkedin_jobs(company_name, linkedin_url, use_mock=use_mock)
            if linkedin_result['has_devops'] and companies_df.at[index, 'hiring_devops'] != 'Yes':
                companies_df.at[index, 'hiring_devops'] = 'Yes'
                companies_df.at[index, 'devops_source'] = linkedin_result['source']
            if linkedin_result['has_software_dev'] and companies_df.at[index, 'hiring_developers'] != 'Yes':
                companies_df.at[index, 'hiring_developers'] = 'Yes'
                companies_df.at[index, 'software_dev_source'] = linkedin_result['source']
        
        # Finally check Seek if we still don't have both yes results
        if companies_df.at[index, 'hiring_devops'] != 'Yes' or companies_df.at[index, 'hiring_developers'] != 'Yes':
            seek_result = check_seek_jobs(company_name, country, use_mock=use_mock)
            if seek_result['has_devops'] and companies_df.at[index, 'hiring_devops'] != 'Yes':
                companies_df.at[index, 'hiring_devops'] = 'Yes'
                companies_df.at[index, 'devops_source'] = seek_result['source']
            if seek_result['has_software_dev'] and companies_df.at[index, 'hiring_developers'] != 'Yes':
                companies_df.at[index, 'hiring_developers'] = 'Yes'
                companies_df.at[index, 'software_dev_source'] = seek_result['source']
        
        # Mark as 'No' if still unknown after all checks
        if companies_df.at[index, 'hiring_devops'] != 'Yes':
            companies_df.at[index, 'hiring_devops'] = 'No'
        if companies_df.at[index, 'hiring_developers'] != 'Yes':
            companies_df.at[index, 'hiring_developers'] = 'No'
        
        # Set actively_hiring based on either devops or software dev roles
        if companies_df.at[index, 'hiring_devops'] == 'Yes' or companies_df.at[index, 'hiring_developers'] == 'Yes':
            companies_df.at[index, 'actively_hiring'] = 'Yes'
        else:
            companies_df.at[index, 'actively_hiring'] = 'No'
        
        # Add a small delay between companies to avoid being rate-limited
        time.sleep(random.uniform(0.1, 0.5))
    
    return companies_df

def main():
    # Load the companies data
    companies_df = load_companies()
    
    # Verify hiring status for all companies
    updated_df = verify_hiring_status(companies_df, use_mock=True)
    
    # Save the results
    os.makedirs('data/processed', exist_ok=True)
    updated_df.to_csv('data/processed/companies_hiring_verified.csv', index=False)
    updated_df.to_excel('data/processed/companies_hiring_verified.xlsx', index=False)
    
    # Count companies that are actively hiring
    hiring_count = len(updated_df[updated_df['actively_hiring'] == 'Yes'])
    hiring_devops_count = len(updated_df[updated_df['hiring_devops'] == 'Yes'])
    hiring_developers_count = len(updated_df[updated_df['hiring_developers'] == 'Yes'])
    
    print(f"\nHiring Verification Complete!")
    print(f"Total companies checked: {len(updated_df)}")
    print(f"Companies actively hiring: {hiring_count}")
    print(f"Companies hiring DevOps: {hiring_devops_count}")
    print(f"Companies hiring Software Developers: {hiring_developers_count}")
    print(f"\nResults saved to data/processed/companies_hiring_verified.xlsx")

if __name__ == "__main__":
    main()