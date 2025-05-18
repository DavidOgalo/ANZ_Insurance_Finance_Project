"""
company_research.py - Script to gather information about top ANZ insurance and finance companies
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import os
import re
from datetime import datetime
from urllib.parse import urlparse
import json
import csv

# Create directories if they don't exist
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/final', exist_ok=True)

# Initialize the DataFrame with the required columns
def create_companies_dataframe():
    columns = [
        'company_id', 'company_name', 'industry', 'country', 'company_size', 
        'annual_revenue', 'company_website', 'linkedin_url', 'actively_hiring',
        'hiring_devops', 'hiring_developers', 'data_source', 'last_verified'
    ]
    
    return pd.DataFrame(columns=columns)

def extract_domain(url):
    """Extract domain from URL"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None

# Hard-coded sample data for Australian finance companies since web scraping might be blocked
def get_sample_australia_finance_companies():
    """Get a sample list of Australian finance companies"""
    companies = [
        {"company_name": "Commonwealth Bank of Australia", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "commbank.com.au"},
        {"company_name": "Westpac Banking Corporation", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "westpac.com.au"},
        {"company_name": "National Australia Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "nab.com.au"},
        {"company_name": "Australia and New Zealand Banking Group", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "anz.com.au"},
        {"company_name": "Macquarie Group", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "macquarie.com"},
        {"company_name": "Suncorp Group", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "suncorp.com.au"},
        {"company_name": "Bank of Queensland", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "boq.com.au"},
        {"company_name": "Bendigo and Adelaide Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "bendigobank.com.au"},
        {"company_name": "AMP Limited", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "amp.com.au"},
        {"company_name": "Judo Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "judo.bank"},
        {"company_name": "Tyro Payments", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "tyro.com"},
        {"company_name": "MyState Limited", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "mystate.com.au"},
        {"company_name": "Xinja Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "xinja.com.au"},
        {"company_name": "86 400", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "86400.com.au"},
        {"company_name": "Volt Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "voltbank.com.au"},
        {"company_name": "Heritage Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "heritage.com.au"},
        {"company_name": "Teachers Mutual Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "tmbank.com.au"},
        {"company_name": "Greater Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "greater.com.au"},
        {"company_name": "IMB Bank", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "imb.com.au"},
        {"company_name": "Beyond Bank Australia", "industry": "Finance", "country": "Australia", "data_source": "Sample Data", "company_website": "beyondbank.com.au"},
    ]
    return companies

# Hard-coded sample data for Australian insurance companies
def get_sample_australia_insurance_companies():
    """Get a sample list of Australian insurance companies"""
    companies = [
        {"company_name": "QBE Insurance Group", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "qbe.com"},
        {"company_name": "Insurance Australia Group", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "iag.com.au"},
        {"company_name": "Suncorp Insurance", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "suncorp.com.au"},
        {"company_name": "Allianz Australia", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "allianz.com.au"},
        {"company_name": "Youi Insurance", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "youi.com.au"},
        {"company_name": "Budget Direct", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "budgetdirect.com.au"},
        {"company_name": "AAMI Insurance", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "aami.com.au"},
        {"company_name": "NRMA Insurance", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "nrma.com.au"},
        {"company_name": "Medibank Private", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "medibank.com.au"},
        {"company_name": "Bupa Australia", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "bupa.com.au"},
        {"company_name": "HCF", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "hcf.com.au"},
        {"company_name": "NIB Health Funds", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "nib.com.au"},
        {"company_name": "AIA Australia", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "aia.com.au"},
        {"company_name": "TAL Life Limited", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "tal.com.au"},
        {"company_name": "Zurich Australia", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "zurich.com.au"},
        {"company_name": "MetLife Insurance Limited", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "metlife.com.au"},
        {"company_name": "Chubb Insurance Australia", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "chubb.com/au"},
        {"company_name": "RACQ Insurance", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "racq.com.au/insurance"},
        {"company_name": "RACV Insurance", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "racv.com.au/insurance"},
        {"company_name": "Hollard Insurance", "industry": "Insurance", "country": "Australia", "data_source": "Sample Data", "company_website": "hollard.com.au"},
    ]
    return companies

# Hard-coded sample data for New Zealand finance companies
def get_sample_nz_finance_companies():
    """Get a sample list of New Zealand finance companies"""
    companies = [
        {"company_name": "ANZ Bank New Zealand", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "anz.co.nz"},
        {"company_name": "Westpac New Zealand", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "westpac.co.nz"},
        {"company_name": "Bank of New Zealand", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "bnz.co.nz"},
        {"company_name": "ASB Bank", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "asb.co.nz"},
        {"company_name": "Kiwibank", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "kiwibank.co.nz"},
        {"company_name": "TSB Bank", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "tsb.co.nz"},
        {"company_name": "Heartland Bank", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "heartland.co.nz"},
        {"company_name": "The Co-operative Bank", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "co-operativebank.co.nz"},
        {"company_name": "SBS Bank", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "sbsbank.co.nz"},
        {"company_name": "Rabobank New Zealand", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "rabobank.co.nz"},
        {"company_name": "HSBC New Zealand", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "hsbc.co.nz"},
        {"company_name": "China Construction Bank NZ", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "nz.ccb.com"},
        {"company_name": "Industrial and Commercial Bank of China NZ", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "icbcnz.com"},
        {"company_name": "Bank of China New Zealand", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "bankofchina.com/nz"},
        {"company_name": "Credit Union Baywide", "industry": "Finance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "nzcubaywide.co.nz"},
    ]
    return companies

# Hard-coded sample data for New Zealand insurance companies
def get_sample_nz_insurance_companies():
    """Get a sample list of New Zealand insurance companies"""
    companies = [
        {"company_name": "AA Insurance", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "aainsurance.co.nz"},
        {"company_name": "Tower Insurance", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "tower.co.nz"},
        {"company_name": "IAG New Zealand", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "iag.co.nz"},
        {"company_name": "FMG Insurance", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "fmg.co.nz"},
        {"company_name": "AMI Insurance", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "ami.co.nz"},
        {"company_name": "State Insurance", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "state.co.nz"},
        {"company_name": "Medical Assurance Society", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "mas.co.nz"},
        {"company_name": "Vero Insurance", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "vero.co.nz"},
        {"company_name": "Southern Cross Health Society", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "southerncross.co.nz"},
        {"company_name": "AIA New Zealand", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "aia.co.nz"},
        {"company_name": "Partners Life", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "partnerslife.co.nz"},
        {"company_name": "Fidelity Life", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "fidelitylife.co.nz"},
        {"company_name": "Cigna Life Insurance", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "cigna.co.nz"},
        {"company_name": "Asteron Life", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "asteronlife.co.nz"},
        {"company_name": "Accuro Health Insurance", "industry": "Insurance", "country": "New Zealand", "data_source": "Sample Data", "company_website": "accuro.co.nz"},
    ]
    return companies

def search_asx_companies():
    """
    Get sample ASX-listed financial and insurance companies since scraping might be blocked
    """
    print("Getting ASX listed companies...")
    companies = [
        {"company_name": "Commonwealth Bank", "industry": "Finance", "country": "Australia", "data_source": "ASX", "company_website": "commbank.com.au"},
        {"company_name": "Westpac Banking Corporation", "industry": "Finance", "country": "Australia", "data_source": "ASX", "company_website": "westpac.com.au"},
        {"company_name": "National Australia Bank", "industry": "Finance", "country": "Australia", "data_source": "ASX", "company_website": "nab.com.au"},
        {"company_name": "ANZ Banking Group", "industry": "Finance", "country": "Australia", "data_source": "ASX", "company_website": "anz.com.au"},
        {"company_name": "Macquarie Group", "industry": "Finance", "country": "Australia", "data_source": "ASX", "company_website": "macquarie.com"},
        {"company_name": "QBE Insurance Group", "industry": "Insurance", "country": "Australia", "data_source": "ASX", "company_website": "qbe.com"},
        {"company_name": "Insurance Australia Group", "industry": "Insurance", "country": "Australia", "data_source": "ASX", "company_website": "iag.com.au"},
        {"company_name": "Suncorp Group", "industry": "Both", "country": "Australia", "data_source": "ASX", "company_website": "suncorp.com.au"},
        {"company_name": "AMP Limited", "industry": "Both", "country": "Australia", "data_source": "ASX", "company_website": "amp.com.au"},
        {"company_name": "Medibank Private", "industry": "Insurance", "country": "Australia", "data_source": "ASX", "company_website": "medibank.com.au"},
    ]
    return companies

def search_nzx_companies():
    """
    Get sample NZX-listed financial and insurance companies since scraping might be blocked
    """
    print("Getting NZX listed companies...")
    companies = [
        {"company_name": "Heartland Group Holdings", "industry": "Finance", "country": "New Zealand", "data_source": "NZX", "company_website": "heartland.co.nz"},
        {"company_name": "Tower Limited", "industry": "Insurance", "country": "New Zealand", "data_source": "NZX", "company_website": "tower.co.nz"},
        {"company_name": "Westpac Banking Corporation", "industry": "Finance", "country": "New Zealand", "data_source": "NZX", "company_website": "westpac.co.nz"},
        {"company_name": "ANZ Bank New Zealand", "industry": "Finance", "country": "New Zealand", "data_source": "NZX", "company_website": "anz.co.nz"},
        {"company_name": "Kiwibank", "industry": "Finance", "country": "New Zealand", "data_source": "NZX", "company_website": "kiwibank.co.nz"},
    ]
    return companies

def enrich_with_company_websites(companies_df):
    """
    Try to find company websites for each company in the dataframe
    """
    print("Enriching with company websites...")
    
    for index, row in companies_df.iterrows():
        if pd.isna(row['company_website']):
            company_name = row['company_name']
            try:
                # Simplified approach for demo purposes
                company_url = f"https://www.{company_name.lower().replace(' ', '')}.com"
                companies_df.at[index, 'company_website'] = company_url
            except Exception as e:
                print(f"Error finding website for {company_name}: {e}")
    
    return companies_df

def enrich_with_linkedin(companies_df):
    """
    Try to find LinkedIn URLs for each company
    """
    print("Enriching with LinkedIn URLs...")
    
    for index, row in companies_df.iterrows():
        if pd.isna(row['linkedin_url']):
            company_name = row['company_name']
            try:
                # Generate a likely LinkedIn company URL
                formatted_name = company_name.lower().replace(' ', '-').replace('&', 'and')
                linkedin_url = f"https://www.linkedin.com/company/{formatted_name}"
                companies_df.at[index, 'linkedin_url'] = linkedin_url
            except Exception as e:
                print(f"Error finding LinkedIn for {company_name}: {e}")
    
    return companies_df

def write_to_csv(data, filename):
    """Write data to CSV file directly"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                print(f"Successfully wrote data to {filename}")
                return True
            else:
                print(f"No data to write to {filename}")
                return False
    except Exception as e:
        print(f"Error writing to CSV {filename}: {e}")
        return False

def main():
    print("Starting data collection process...")
    
    # Collect companies from various sources
    all_companies = []
    
    # Get companies from sample data (since web scraping might be blocked)
    all_companies.extend(search_asx_companies())
    all_companies.extend(search_nzx_companies())
    all_companies.extend(get_sample_australia_finance_companies())
    all_companies.extend(get_sample_australia_insurance_companies())
    all_companies.extend(get_sample_nz_finance_companies())
    all_companies.extend(get_sample_nz_insurance_companies())
    
    # Write raw data to CSV directly
    raw_csv_path = 'data/raw/companies_raw.csv'
    write_to_csv(all_companies, raw_csv_path)
    
    # Convert to DataFrame and add company_id
    try:
        collected_df = pd.DataFrame(all_companies)
        collected_df['company_id'] = range(1, len(collected_df) + 1)
        
        # Set default values
        collected_df['actively_hiring'] = 'Unknown'
        collected_df['hiring_devops'] = 'Unknown'
        collected_df['hiring_developers'] = 'Unknown'
        collected_df['last_verified'] = datetime.now().strftime('%Y-%m-%d')
        
        # Remove duplicates based on company name
        collected_df = collected_df.drop_duplicates(subset=['company_name'])
        
        # Ensure all required columns exist
        required_columns = [
            'company_id', 'company_name', 'industry', 'country', 'company_size', 
            'annual_revenue', 'company_website', 'linkedin_url', 'actively_hiring',
            'hiring_devops', 'hiring_developers', 'data_source', 'last_verified'
        ]
        
        for col in required_columns:
            if col not in collected_df.columns:
                collected_df[col] = None
        
        # Enrich data with websites and LinkedIn URLs if missing
        if 'company_website' in collected_df.columns:
            collected_df = enrich_with_company_websites(collected_df)
        
        if 'linkedin_url' in collected_df.columns:
            collected_df = enrich_with_linkedin(collected_df)
        
        # Save the raw data to Excel
        excel_path = 'data/raw/companies_raw.xlsx'
        collected_df.to_excel(excel_path, index=False)
        print(f"Successfully saved data to {excel_path}")
        
        # Also save to CSV as backup
        csv_path = 'data/raw/companies_processed.csv'
        collected_df.to_csv(csv_path, index=False)
        print(f"Successfully saved data to {csv_path}")
        
        print(f"Collected {len(collected_df)} companies and saved to data/raw/")
    except Exception as e:
        print(f"Error processing dataframe: {e}")
        # Write error to a log file
        with open('data/raw/error_log.txt', 'w') as f:
            f.write(f"Error occurred at {datetime.now()}: {str(e)}")

if __name__ == "__main__":
    main()