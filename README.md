# ANZ Insurance & Finance Company Data Enrichment Project

This project provides a robust, end-to-end solution for discovering, analyzing, and enriching data on the leading insurance and finance companies in Australia and New Zealand. The primary objective is to create a high-quality, actionable dataset that highlights companies actively hiring for key technology roles such as DevOps Engineers and Software Developers.

## Project Overview

By integrating data from authoritative industry rankings, business directories, job boards, company websites, and professional networks, the project systematically identifies top companies, verifies their hiring activity, and uncovers C-level technology decision makers. Through a multi-step enrichment process—including company profiling, hiring verification, executive research, and contact validation—the project delivers a comprehensive Excel workbook. This deliverable is designed to support business development, recruitment, and market research initiatives by providing detailed company profiles, executive contacts, and transparent data quality metrics.

## Installation and Setup

1. Clone this repository:
```bash
git clone https://github.com/DavidOgalo/ANZ_Insurance_Finance_Project.git
cd ANZ_Insurance_Finance_Project
```

2. Create a virtual environment:
```bash
python -m venv env
```

3. Activate the virtual environment:
```bash
# On Windows:
env\Scripts\activate

# On macOS/Linux:
source env/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create required directories:
```bash
mkdir -p data/raw data/processed data/final notebooks
```

## Running the Pipeline

Execute the scripts in the following order to generate the final deliverable:

1. Gather initial company data:
```bash
python scripts/company_research.py
```

2. Verify hiring status:
```bash
python scripts/hiring_verification.py
```

3. Enrich with contact information:
```bash
python scripts/contact_enrichment.py
```

4. Generate final Excel deliverable:
```bash
python scripts/data_consolidation.py
```

The final output will be available at `data/final/ANZ_Insurance_Finance_Companies.xlsx`.

## Script Details

### company_research.py
Collects information about top insurance and finance companies in Australia and New Zealand from multiple sources including stock exchanges, regulatory bodies, and industry associations.

### hiring_verification.py
Checks if companies are actively hiring for DevOps Engineers and Software Developers through company career pages, LinkedIn Jobs, and other job boards.

### contact_enrichment.py
Identifies C-level technology executives for each company and enriches their contact information, including direct business emails and phone numbers, using diligent online research.

### data_consolidation.py
Combines all data, creates the final dataset, and generates a comprehensive Excel file with multiple sheets including company data, summary dashboard, methodology, sources, and top opportunities.

## Methodology

The data collection methodology follows these key steps:

1. **Company Identification**: Gathering and verifying top ANZ insurance and finance companies from authoritative sources
2. **Hiring Verification**: Confirming active hiring status for DevOps and Software Developer roles
3. **Executive Research**: Finding C-level decision makers within each company
4. **Contact Enrichment**: Generating and verifying contact information through ethical methods
5. **Data Quality Assurance**: Standardizing, validating, and scoring data quality

For more details on the methodology, refer to the Methodology sheet in the final Excel deliverable.

## Data Sources

The following table summarizes the main sources used for data collection and enrichment:

| Source Type           | Source Name                  | URL                                   | Information Gathered                        |
|---------------------- |-----------------------------|----------------------------------------|---------------------------------------------|
| Industry Rankings     | ASX 200                      | https://www.asx.com.au                 | Company identification, market cap          |
| Industry Rankings     | NZX 50                       | https://www.nzx.com                    | Company identification, market cap          |
| Business Directory    | IBISWorld Australia          | https://www.ibisworld.com/au           | Industry classification, revenue            |
| Job Board             | Seek Australia               | https://www.seek.com.au                | Active hiring status, roles                 |
| Professional Network  | LinkedIn                     | https://www.linkedin.com               | C-level contacts, company size              |
| Email Verification    | Hunter.io                    | https://hunter.io                      | Email patterns, verification                |
| Company Websites      | Various                      | List of websites (see scripts)         | Contact information, open positions         |
| News Sources          | AFR                          | https://www.afr.com                    | Recent company developments                 |
| Industry Association  | Financial Services Council   | https://www.fsc.org.au                 | Member companies, leadership                |
| Data Enrichment       | Clay.com                     | https://clay.com                       | Contact enrichment                         |

A complete list of sources is available in the Sources sheet of the final deliverable.

## Templates

A template file, `ANZ_Insurance_Finannce_Template.xlsx`, is included in the `templates/` directory. This template provides a reference for the structure, formatting, and content expected in the final deliverable Excel workbook. It can be used as a guide for future projects, for customizing the output, or for ensuring consistency when extending the dataset. Review this template to understand the recommended layout and key components of a high-quality company data enrichment deliverable.

## Notes

- All contact information was ethically sourced from publicly available business sources
- Email addresses were carefully constructed using standard business email conventions and checked for validity through domain verification methods
- The data quality scoring system provides transparency about the confidence level of each data point
