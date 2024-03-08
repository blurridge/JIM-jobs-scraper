from bs4 import BeautifulSoup
import logging
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}
URLS = {
    "indeed": "https://ph.indeed.com/jobs"
}
DB = {
    "indeed": "job_db/scraped_indeed_jobs.csv"
}
FIELD_NAMES = ['job_id', 'job_name', 'company_name', 'job_location', 'job_link']
log = logging.getLogger(__name__)

def csv_file_exists():
    """
    Checks if dataset file exists.
    """
    return Path(DB['indeed']).is_file()

def extract_site(site: str, skill_name: str, location="Cebu", indeed_no_page=0):
    """
    Extracts the html from the requested site.
    """
    options = Options()
    driver = webdriver.Chrome(options=options)
    url = ""
    if site == "indeed":
        url = URLS[site] + f"?q={skill_name.replace(' ', '+')}&l={location}&start={indeed_no_page * 10}"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

def scrape_indeed(skill_name="Data Analyst", location="Cebu", no_pages=0):
    soup = extract_site(site="indeed", skill_name=skill_name, location=location, indeed_no_page=no_pages)
    job_cards_div = soup.find('div', attrs={'id': 'mosaic-provider-jobcards'})
    if job_cards_div:
        if not csv_file_exists():
            logging.info(f"Dataset file not found. Creating new .csv file...")
            with open(DB['indeed'], 'w', newline='') as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
                csv_writer.writeheader()
        with open(DB["indeed"], 'a')  as indeed_file:
            jobs = job_cards_div.find_all('li', attrs={'class': 'css-5lfssm eu4oa1w0'})
            for job in jobs:
                job_div = job.find('div', attrs={'class': 'cardOutline'})
                if job_div:
                    job_id = job_div.find('a', class_='jcs-JobTitle')['data-jk']
                    job_name = job_div.find('span', attrs={'id': f"jobTitle-{job_id}"}).text.strip()
                    company_name = job_div.find('span', attrs={'data-testid': "company-name"}).text.strip()
                    job_location = job_div.find('div', attrs={'data-testid': "text-location"}).text.strip()
                    job_link = f"https://ph.indeed.com/viewjob?jk={job_id}"
                    job_payload = {
                        'job_id': job_id,
                        'job_name': job_name,
                        'company_name': company_name,
                        'job_location': job_location,
                        'job_link': job_link
                    }
                    csv_writer = csv.DictWriter(indeed_file, fieldnames=FIELD_NAMES)
                    csv_writer.writerow(job_payload)
        
if __name__ == "__main__":
    scrape_indeed()