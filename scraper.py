from bs4 import BeautifulSoup
import logging
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

# TODO: Check if pages repeat. If it repeats, stop scraping.

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
}
URLS = {
    "indeed": "https://ph.indeed.com/jobs",
    "mynimo": "https://www.mynimo.com/cebu-jobs",
}
DB = {
    "indeed": "job_db/scraped_indeed_jobs.csv",
    "mynimo": "job_db/scraped_mynimo_jobs.csv",
}
FIELD_NAMES = ["job_id", "job_name", "company_name", "job_location", "job_link"]
log = logging.getLogger(__name__)


def csv_file_exists(site: str):
    """
    Checks if dataset file exists.
    """
    return Path(DB[site]).is_file()


def extract_site(site: str, skill_name: str, location="Cebu", num_page=0):
    """
    Extracts the HTML from the requested site.

    Parameters:
    - site (str): The website to extract data from.
    - skill_name (str): The skill or job title to search for.
    - location (str): The location where the job search should be conducted. Defaults to "Cebu".
    - num_page (int): The number of pages to scrape. If set to 0, scrapes only first page. Defaults to 0.

    Returns:
    - soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
    """
    options = Options()
    driver = webdriver.Chrome(options=options)
    url = ""
    if site == "indeed":
        url = (
            URLS[site]
            + f"?q={skill_name.replace(' ', '+')}&l={location}&start={num_page * 10}"
        )
    elif site == "mynimo":
        url = (
            URLS[site]
            + f"search?page={num_page}&search_by=content&keyword={skill_name.replace(' ', '%20')}&region_name=cebu&category_name_pretty=&searchType="
        )
    log.info(
        f"Scraping {site.title()} for {skill_name.title()} in {location.title()} [Page #{num_page + 1}]"
    )
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def scrape_indeed(skill_name: str, location="Cebu", num_pages=1):
    """
    Scrapes job postings from Indeed for a specific skill and location, and writes the data to a CSV file.

    Parameters:
    - skill_name (str): The skill or job title to search for.
    - location (str): The location where the job search should be conducted. Defaults to "Cebu".
    - num_pages (int): The number of pages to scrape. If set to 0, scrapes only first page. Defaults to 0.

    Returns:
    - None

    This function scrapes job postings from Indeed based on the provided skill_name and location.
    It writes the extracted data to a CSV file named 'indeed_jobs.csv' in the job_db directory.
    Each job posting is represented as a dictionary containing 'job_id', 'job_name',
    'company_name', 'job_location', and 'job_link' keys.
    """
    for page in range(0, num_pages):
        soup = extract_site(
            site="indeed", skill_name=skill_name, location=location, num_page=page
        )
        job_cards_div = soup.find("div", attrs={"id": "mosaic-provider-jobcards"})
        if job_cards_div:
            log.info("Job found. Scraping attributes...")
            if not csv_file_exists("indeed"):
                logging.info(f"Dataset file not found. Creating new .csv file...")
                with open(DB["indeed"], "w", newline="") as csvfile:
                    csv_writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
                    csv_writer.writeheader()
            with open(DB["indeed"], "a") as indeed_file:
                jobs = job_cards_div.find_all(
                    "li", attrs={"class": "css-5lfssm eu4oa1w0"}
                )
                for job in jobs:
                    job_div = job.find("div", attrs={"class": "cardOutline"})
                    if job_div:
                        job_id = job_div.find("a", class_="jcs-JobTitle")["data-jk"]
                        job_name = job_div.find(
                            "span", attrs={"id": f"jobTitle-{job_id}"}
                        ).text.strip()
                        company_name = job_div.find(
                            "span", attrs={"data-testid": "company-name"}
                        ).text.strip()
                        job_location = job_div.find(
                            "div", attrs={"data-testid": "text-location"}
                        ).text.strip()
                        job_link = f"https://ph.indeed.com/viewjob?jk={job_id}"
                        job_payload = {
                            "job_id": job_id,
                            "job_name": job_name,
                            "company_name": company_name,
                            "job_location": job_location,
                            "job_link": job_link,
                        }
                        log.info(f"Adding {job_id} by {company_name} to dataset...")
                        csv_writer = csv.DictWriter(indeed_file, fieldnames=FIELD_NAMES)
                        csv_writer.writerow(job_payload)
        else:
            log.error("No jobs found.")


def scrape_mynimo(skill_name: str, location="Cebu", num_pages=1):
    for page in range(0, num_pages):
        soup = extract_site(
            site="mynimo", skill_name=skill_name, location=location, num_page=page
        )
        job_cards_div = soup.find(
            "div",
            attrs={"data-chakra-component": "CStack", "class": "css-j7qwjs css-0"},
        )
        if job_cards_div:
            log.info("Job found. Scraping attributes...")
            if not csv_file_exists("mynimo"):
                logging.info(f"Dataset file not found. Creating new .csv file...")
                with open(DB["mynimo"], "w", newline="") as csvfile:
                    csv_writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
                    csv_writer.writeheader()
            with open(DB["mynimo"], "a") as mynimo_file:
                jobs = job_cards_div.find_all(
                    "a",
                    attrs={
                        "data-chakra-component": "CPseudoBox",
                        "class": "href-button css-h9szfi",
                    },
                )
                for job in jobs:
                    job_id = job["href"].split("/")[3]
                    job_name = job.find(
                        "p",
                        attrs={
                            "data-chakra-component": "CText",
                            "class": "href-button css-qkcbob",
                        },
                    ).text.strip()
                    company_name = (
                        job.find("h5", attrs={"class": "company-name-text"})
                        .contents[-1]
                        .strip()
                    )
                    job_location = job.find(
                        "p",
                        attrs={"data-chakra-component": "CText", "class": "css-6of238"},
                    ).text.strip()
                    job_link = f"https://www.mynimo.com/jobs/view/" + job_id
                    job_payload = {
                        "job_id": job_id,
                        "job_name": job_name,
                        "company_name": company_name,
                        "job_location": job_location,
                        "job_link": job_link,
                    }
                    log.info(f"Adding {job_id} by {company_name} to dataset...")
                    csv_writer = csv.DictWriter(mynimo_file, fieldnames=FIELD_NAMES)
                    csv_writer.writerow(job_payload)
