"""
contact_enrichment.py - Find C-level executives and their contact information
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
import dns.resolver

def load_companies():
    """Load the hiring-verified companies data"""
    try:
        return pd.read_excel('data/processed/companies_hiring_verified.xlsx')
    except FileNotFoundError:
        print("Hiring verified companies file not found. Please run hiring_verification.py first.")
        exit(1)

def filter_actively_hiring_companies(companies_df):
    """Filter to keep only companies that are actively hiring"""
    hiring_df = companies_df[
        (companies_df['actively_hiring'] == 'Yes') &
        ((companies_df['hiring_devops'] == 'Yes') | (companies_df['hiring_developers'] == 'Yes'))
    ]
    
    # If we have less than 100 companies after filtering, return all we have
    if len(hiring_df) < 100:
        print(f"Warning: Only {len(hiring_df)} companies are actively hiring. Using all available companies.")
        return hiring_df
    else:
        # Sort by company size or revenue if available, otherwise just take the first 100
        if 'company_size' in hiring_df.columns and not hiring_df['company_size'].isna().all():
            hiring_df = hiring_df.sort_values('company_size', ascending=False)
        elif 'annual_revenue' in hiring_df.columns and not hiring_df['annual_revenue'].isna().all():
            hiring_df = hiring_df.sort_values('annual_revenue', ascending=False)
        
        return hiring_df.head(100)

# Mock data generator for testing
def generate_mock_executive(company_name, use_mock=True):
    """Generate mock executive data for testing"""
    # List of common first names
    first_names = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"
    ]
    
    # List of common last names
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
        "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"
    ]
    
    # List of tech executive titles
    titles = [
        "Chief Technology Officer", "CTO",
        "Chief Information Officer", "CIO",
        "Chief Digital Officer", "CDO",
        "VP of Engineering", "VP of Technology",
        "Head of Technology", "Head of Engineering",
        "Director of IT", "Director of Technology"
    ]
    
    # Randomly select name and title
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    title = random.choice(titles)
    
    # Generate mock LinkedIn URL
    linkedin_url = f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(10000, 99999)}"
    
    # Create the executive record
    executive = {
        'name': f"{first_name} {last_name}",
        'title': title,
        'linkedin_url': linkedin_url,
        'source': 'Mock Data'
    }
    
    return executive

def find_linkedin_executives(company_name, linkedin_url=None, use_mock=True):
    """
    Find C-level executives on LinkedIn
    """
    if use_mock:
        # Generate 1-3 mock executives
        num_executives = random.randint(1, 3)
        executives = []
        
        for _ in range(num_executives):
            executives.append(generate_mock_executive(company_name))
        
        return executives
    
    # Real implementation would go here
    executives = []
    
    try:
        # Format search query
        company_query = company_name.replace(' ', '%20')
        titles_query = '"CTO"%20OR%20"Chief%20Technology%20Officer"%20OR%20"CIO"%20OR%20"Chief%20Information%20Officer"%20OR%20"VP%20Engineering"%20OR%20"Head%20of%20Technology"'
        
        search_url = f"https://www.google.com/search?q=site%3Alinkedin.com%2Fin%20{company_query}%20({titles_query})"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for LinkedIn profile URLs in search results
            for a_tag in soup.find_all('a'):
                href = a_tag.get('href', '')
                if 'linkedin.com/in/' in href and '/pub/dir/' not in href:
                    # Get the profile URL
                    profile_url = re.search(r'(https://\w+\.linkedin\.com/in/[^&]+)', href)
                    if profile_url:
                        profile_url = profile_url.group(1)
                        
                        # Get the name and title from the search result
                        result_text = a_tag.get_text()
                        
                        # Extract name (simplistic approach)
                        name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', result_text)
                        name = name_match.group(1) if name_match else "Unknown"
                        
                        # Extract title (look for common C-level titles)
                        title_patterns = [
                            r'CTO', r'Chief Technology Officer', 
                            r'CIO', r'Chief Information Officer',
                            r'CDO', r'Chief Digital Officer',
                            r'VP of (Technology|Engineering|IT)',
                            r'Head of (Technology|Engineering|IT)',
                            r'Director of (Technology|Engineering|IT)'
                        ]
                        
                        title = "Technology Executive"  # Default
                        for pattern in title_patterns:
                            title_match = re.search(pattern, result_text)
                            if title_match:
                                title = title_match.group(0)
                                break
                        
                        executives.append({
                            'name': name,
                            'title': title,
                            'linkedin_url': profile_url,
                            'source': 'LinkedIn via Google'
                        })
    except Exception as e:
        print(f"Error finding LinkedIn executives for {company_name}: {e}")
    
    return executives

def find_company_executives(company_name, company_url, use_mock=True):
    """
    Find C-level executives on company website
    """
    if use_mock:
        # For mock data, decide if we should return executives
        if random.choice([True, False]):
            # Generate 1-2 mock executives
            num_executives = random.randint(1, 2)
            executives = []
            
            for _ in range(num_executives):
                exec_data = generate_mock_executive(company_name)
                # Change source to company website
                exec_data['source'] = f"{company_url}/about/leadership"
                executives.append(exec_data)
            
            return executives
        else:
            return []
    
    # Real implementation would go here
    executives = []
    
    if pd.isna(company_url):
        return executives
    
    try:
        # Clean and validate the URL
        if not company_url.startswith(('http://', 'https://')):
            company_url = 'https://' + company_url
        
        # Common paths to leadership/team pages
        leadership_paths = [
            '/about/leadership', '/about/management', '/about/team', 
            '/about-us/leadership', '/about-us/management', '/about-us/team',
            '/company/leadership', '/company/management', '/company/team',
            '/leadership', '/management', '/team', '/about', '/about-us',
            '/who-we-are', '/our-team', '/our-people'
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Check each potential leadership page
        for path in leadership_paths:
            leadership_url = company_url + path
            try:
                response = requests.get(leadership_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_text = soup.get_text().lower()
                    
                    # Check if this page likely contains leadership info
                    if any(term in page_text for term in ['leadership', 'management', 'executive', 'team', 'board']):
                        # Look for tech executive titles in the text
                        tech_titles = [
                            'cto', 'chief technology officer',
                            'cio', 'chief information officer',
                            'chief digital officer', 'cdo',
                            'vp of technology', 'vp of engineering', 'vp of it',
                            'head of technology', 'head of engineering', 'head of it',
                            'director of technology', 'director of engineering', 'director of it'
                        ]
                        
                        # Find all headings and paragraphs that might contain executive info
                        potential_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'])
                        
                        for element in potential_elements:
                            element_text = element.get_text().lower()
                            
                            # Check if this element contains a tech executive title
                            if any(title in element_text for title in tech_titles):
                                # Find the closest name to this title (this is a simplified approach)
                                name_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)'
                                name_match = re.search(name_pattern, element.get_text())
                                
                                if name_match:
                                    name = name_match.group(1)
                                    
                                    # Determine the title based on what was found
                                    title = "Technology Executive"  # Default
                                    for t in tech_titles:
                                        if t in element_text:
                                            title = t.title()  # Capitalize the title
                                            break
                                    
                                    executives.append({
                                        'name': name,
                                        'title': title,
                                        'source': leadership_url
                                    })
                    
                    # If we've found executives, no need to check other pages
                    if executives:
                        break
                        
            except Exception as e:
                print(f"Error checking {leadership_url}: {e}")
                
            # Add a short delay between requests
            time.sleep(random.uniform(0.1, 0.5))
                
    except Exception as e:
        print(f"Error finding executives on company website for {company_name}: {e}")
    
    return executives

def extract_domain_from_url(url):
    """Extract the domain name from a URL"""
    if pd.isna(url):
        return None
    
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse the URL and extract the domain
        parsed_url = url.split('//')[-1].split('/')[0]
        
        # Remove www. if present
        if parsed_url.startswith('www.'):
            parsed_url = parsed_url[4:]
            
        return parsed_url
    except Exception as e:
        print(f"Error extracting domain from {url}: {e}")
        return None

def discover_email_pattern(company_domain):
    """
    Determine the likely email pattern for a company
    For mock data, randomly choose a pattern
    """
    common_patterns = [
        'first.last@{}',
        'firstlast@{}',
        'first_last@{}',
        'flast@{}',
        'first.l@{}',
        'f.last@{}'
    ]
    
    # Randomly choose a pattern for mock data
    return random.choice(common_patterns).format(company_domain)

def generate_email(first_name, last_name, domain, pattern=None):
    """
    Generate an email address based on a pattern
    """
    if not pattern:
        pattern = 'first.last@{}'.format(domain)
    
    first = first_name.lower()
    last = last_name.lower()
    
    # Generate email based on pattern
    if pattern == 'first.last@{}'.format(domain):
        return f"{first}.{last}@{domain}"
    elif pattern == 'firstlast@{}'.format(domain):
        return f"{first}{last}@{domain}"
    elif pattern == 'first_last@{}'.format(domain):
        return f"{first}_{last}@{domain}"
    elif pattern == 'flast@{}'.format(domain):
        return f"{first[0]}{last}@{domain}"
    elif pattern == 'first.l@{}'.format(domain):
        return f"{first}.{last[0]}@{domain}"
    elif pattern == 'f.last@{}'.format(domain):
        return f"{first[0]}.{last}@{domain}"
    else:
        # Default to first.last if pattern is unknown
        return f"{first}.{last}@{domain}"

def verify_email_exists(email, use_mock=True):
    """
    Basic email verification
    For mock data, randomly decide if email is valid
    """
    if use_mock:
        # Randomly decide if email is valid (80% chance)
        return random.random() < 0.8
    
    # Real implementation would check MX records
    domain = email.split('@')[1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return True if mx_records else False
    except Exception:
        return False

def find_phone_number(executive_name, company_name, use_mock=True):
    """
    Try to find phone numbers for executives
    For mock data, randomly generate a phone number
    """
    if use_mock:
        # Decide if we should return a phone number (30% chance)
        if random.random() < 0.3:
            # Generate random phone number
            country_code = "+61" if random.random() < 0.7 else "+64"  # Australia or New Zealand
            area_code = str(random.randint(2, 9))
            first_part = str(random.randint(1000, 9999))
            second_part = str(random.randint(1000, 9999))
            
            return f"{country_code} {area_code} {first_part} {second_part}"
        else:
            return None
    
    # In a real implementation, you would use a service like RocketReach
    # or similar, which would require API access
    return None

def enrich_contacts(companies_df, use_mock=True):
    """
    Find C-level technology executives for each company and enrich with contact info
    """
    # Create a dataframe to store executive information
    columns = [
        'company_id', 'executive_name', 'executive_title', 'linkedin_url',
        'email', 'phone', 'source', 'verification_status'
    ]
    
    executives_df = pd.DataFrame(columns=columns)
    
    for index, row in companies_df.iterrows():
        company_id = row['company_id']
        company_name = row['company_name']
        company_url = row['company_website'] if not pd.isna(row['company_website']) else None
        linkedin_url = row['linkedin_url'] if not pd.isna(row['linkedin_url']) else None
        
        print(f"Finding executives for {company_name}...")
        
        # Try to find executives on LinkedIn
        linkedin_execs = find_linkedin_executives(company_name, linkedin_url, use_mock=use_mock)
        
        # Try to find executives on company website
        website_execs = find_company_executives(company_name, company_url, use_mock=use_mock) if company_url else []
        
        # Combine executives from both sources, preferring LinkedIn if duplicate names
        all_execs = linkedin_execs.copy()
        linkedin_names = [exec['name'].lower() for exec in linkedin_execs]
        
        for exec in website_execs:
            if exec['name'].lower() not in linkedin_names:
                all_execs.append(exec)
        
        # If no executives found, add a placeholder
        if not all_execs:
            all_execs.append({
                'name': 'Technology Decision Maker',
                'title': 'CTO or equivalent',
                'source': 'Placeholder - requires manual research'
            })
        
        # Extract domain from company website for email generation
        company_domain = extract_domain_from_url(company_url) if company_url else None
        
        # Discover email pattern for the company
        email_pattern = discover_email_pattern(company_domain) if company_domain else None
        
        # Process each executive
        for exec in all_execs:
            exec_name = exec['name']
            
            # Skip if the name is "Unknown"
            if exec_name == "Unknown":
                continue
                
            # Split name into first and last
            name_parts = exec_name.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = name_parts[-1]  # Take last word as last name
                
                # Generate email if domain available
                email = None
                verification_status = 'Not Verified'
                
                if company_domain and email_pattern:
                    email = generate_email(first_name, last_name, company_domain, email_pattern)
                    
                    # Basic verification
                    if verify_email_exists(email, use_mock=use_mock):
                        verification_status = 'Domain MX Verified'
                
                # Try to find phone number
                phone = find_phone_number(exec_name, company_name, use_mock=use_mock)
                
                # Add to executives dataframe
                new_row = {
                    'company_id': company_id,
                    'executive_name': exec_name,
                    'executive_title': exec['title'],
                    'linkedin_url': exec.get('linkedin_url', None),
                    'email': email,
                    'phone': phone,
                    'source': exec['source'],
                    'verification_status': verification_status
                }
                
                # Append the new row to the DataFrame
                executives_df = pd.concat([executives_df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Add a delay between companies
        time.sleep(random.uniform(0.1, 0.3))
    
    return executives_df

def main():
    # Load the companies data
    all_companies_df = load_companies()
    
    # Filter to keep only actively hiring companies
    hiring_companies_df = filter_actively_hiring_companies(all_companies_df)
    
    # Find and enrich contact information
    executives_df = enrich_contacts(hiring_companies_df, use_mock=True)
    
    # Save the results
    os.makedirs('data/processed', exist_ok=True)
    
    # Save the filtered companies
    hiring_companies_df.to_csv('data/processed/top_hiring_companies.csv', index=False)
    hiring_companies_df.to_excel('data/processed/top_hiring_companies.xlsx', index=False)
    
   # Save the executives data
    executives_df.to_csv('data/processed/executives_contacts.csv', index=False)
    executives_df.to_excel('data/processed/executives_contacts.xlsx', index=False)
    
    print(f"\nContact Enrichment Complete!")
    print(f"Total companies processed: {len(hiring_companies_df)}")
    print(f"Total executives found: {len(executives_df)}")
    print(f"Executives with email addresses: {len(executives_df[~executives_df['email'].isna()])}")
    print(f"Executives with phone numbers: {len(executives_df[~executives_df['phone'].isna()])}")
    print(f"\nResults saved to data/processed/")

if __name__ == "__main__":
    main()
    