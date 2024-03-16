from bs4 import BeautifulSoup
import logging
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
}
URLS = {
    "indeed": "https://ph.indeed.com/jobs",
    "mynimo": "https://www.mynimo.com/cebu-jobs",
    "jobstreet": "https://www.jobstreet.com.ph/",
}
DB = {
    "indeed": "job_db/scraped_indeed_jobs.csv",
    "mynimo": "job_db/scraped_mynimo_jobs.csv",
    "jobstreet": "job_db/scraped_jobstreet_jobs.csv",
}
FIELD_NAMES = ["job_id", "job_name", "company_name", "job_location", "job_link", "query"]
MAX_RETRIES = 3
log = logging.getLogger(__name__)


def csv_file_exists(site: str) -> bool:
    """
    Checks if the CSV dataset file exists.

    Parameters:
    - site (str): The site for which the dataset file existence is checked.

    Returns:
    - bool: True if the dataset file exists, False otherwise.
    """
    return Path(DB[site]).is_file()


def write_headers(site: str) -> None:
    """
    Writes headers to the CSV dataset file.

    Parameters:
    - site (str): The site for which headers are written to the dataset file.

    Returns:
    - None
    """
    with open(DB[site], "w", newline="") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
        csv_writer.writeheader()


def extract_existing_job_ids(site: str) -> set:
    """
    Extracts existing job IDs from the CSV dataset file.

    Parameters:
    - site (str): The site from which existing job IDs are extracted.

    Returns:
    - set: A set containing existing job IDs extracted from the dataset file.
    """
    existing_job_ids = set()
    if not csv_file_exists(site):
        logging.info(
            f"{site.title()} dataset file not found. Creating new .csv file..."
        )
        write_headers(site)
    else:
        with open(DB[site], newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_job_ids.add(row["job_id"])
    return existing_job_ids


def extract_site(
    site: str, skill_name: str, location="Cebu", num_page=0
) -> BeautifulSoup:
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
    elif site == "jobstreet":
        url = (
            URLS[site]
            + f"{skill_name.replace(' ', '-')}-jobs/in-{location.replace(' ', '-')}"
        )
    log.info(
        f"Scraping {site.title()} for {skill_name.title()} in {location.title()} [Page #{num_page + 1}]"
    )
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def scrape_indeed(skill_name: str, location="Cebu", num_pages=1) -> None:
    """
    Scrapes job listings from Indeed website based on provided parameters.

    Parameters:
    - skill_name (str): The skill or job title to search for.
    - location (str, optional): The location to search for jobs. Defaults to "Cebu".
    - num_pages (int, optional): The number of pages to scrape. Defaults to 1.

    Returns:
    - None

    The function scrapes job listings from Indeed website based on the provided skill name,
    location, and number of pages to scrape. It extracts job attributes such as job ID,
    job name, company name, job location, and job link. The function also checks if the
    dataset file exists, creates a new one if not found, and extracts existing job IDs.
    It logs information about each job being added to the dataset or if the job is already
    present and skips it.
    """
    global MAX_RETRIES
    num_retries = 0
    existing_job_ids = extract_existing_job_ids("indeed")
    prev_set_len = len(existing_job_ids)
    for page in range(0, num_pages):
        soup = extract_site(
            site="indeed", skill_name=skill_name, location=location, num_page=page
        )
        job_cards_div = soup.find("div", attrs={"id": "mosaic-provider-jobcards"})
        if job_cards_div:
            log.info("Jobs found. Scraping attributes...")
            prev_set_len = len(existing_job_ids)
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
                            "query": skill_name,
                        }
                        if job_id not in existing_job_ids:
                            existing_job_ids.add(job_id)
                            log.info(f"Adding {job_id} by {company_name} to dataset...")
                            csv_writer = csv.DictWriter(
                                indeed_file, fieldnames=FIELD_NAMES
                            )
                            csv_writer.writerow(job_payload)
            if prev_set_len == len(existing_job_ids) and existing_job_ids:
                log.error(
                    f"No new jobs found. {MAX_RETRIES - num_retries} retries left. Going to next page..."
                )
                num_retries += 1
            else:
                num_retries = 0
            if num_retries > MAX_RETRIES:
                log.error("Max number of retries reached. Ending scrape...")
                break
        else:
            log.error("No jobs found.")


def scrape_mynimo(skill_name: str, location="Cebu", num_pages=1) -> None:
    """
    Scrapes job listings from Mynimo website based on provided parameters.

    Parameters:
    - skill_name (str): The skill or job title to search for.
    - location (str, optional): The location to search for jobs. Defaults to "Cebu".
    - num_pages (int, optional): The number of pages to scrape. Defaults to 1.

    Returns:
    - None

    The function scrapes job listings from Mynimo website based on the provided skill name,
    location, and number of pages to scrape. It extracts job attributes such as job ID,
    job name, company name, job location, and job link. The function also checks if the
    dataset file exists, creates a new one if not found, and extracts existing job IDs.
    It logs information about each job being added to the dataset or if the job is already
    present and skips it.
    """
    global MAX_RETRIES
    num_retries = 0
    existing_job_ids = extract_existing_job_ids("mynimo")
    prev_set_len = len(existing_job_ids)
    for page in range(0, num_pages):
        soup = extract_site(
            site="mynimo", skill_name=skill_name, location=location, num_page=page
        )
        job_cards_div = soup.find(
            "div",
            attrs={"data-chakra-component": "CStack", "class": "css-j7qwjs css-0"},
        )
        if job_cards_div:
            log.info("Jobs found. Scraping attributes...")
            prev_set_len = len(existing_job_ids)
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
                    job_link = f"https://www.mynimo.com/jobs/view/{job_id}"
                    job_payload = {
                        "job_id": job_id,
                        "job_name": job_name,
                        "company_name": company_name,
                        "job_location": job_location,
                        "job_link": job_link,
                        "query": skill_name,
                    }
                    if job_id not in existing_job_ids:
                        existing_job_ids.add(job_id)
                        log.info(f"Adding {job_id} by {company_name} to dataset...")
                        csv_writer = csv.DictWriter(mynimo_file, fieldnames=FIELD_NAMES)
                        csv_writer.writerow(job_payload)
            if prev_set_len == len(existing_job_ids) and existing_job_ids:
                log.error(
                    f"No new jobs found. {MAX_RETRIES - num_retries} retries left. Going to next page..."
                )
                num_retries += 1
            else:
                num_retries = 0
            if num_retries > MAX_RETRIES:
                log.error("Max number of retries reached. Ending scrape...")
                break
        else:
            log.error("No jobs found.")


def scrape_jobstreet(skill_name: str, location="Cebu", num_pages=1) -> None:
    """
    Scrapes job listings from Mynimo website based on provided parameters.

    Parameters:
    - skill_name (str): The skill or job title to search for.
    - location (str, optional): The location to search for jobs. Defaults to "Cebu".
    - num_pages (int, optional): The number of pages to scrape. Defaults to 1.

    Returns:
    - None

    The function scrapes job listings from Jobstreet website based on the provided skill name,
    location, and number of pages to scrape. It extracts job attributes such as job ID,
    job name, company name, job location, and job link. The function also checks if the
    dataset file exists, creates a new one if not found, and extracts existing job IDs.
    It logs information about each job being added to the dataset or if the job is already
    present and skips it.
    """
    global MAX_RETRIES
    num_retries = 0
    existing_job_ids = extract_existing_job_ids("jobstreet")
    prev_set_len = len(existing_job_ids)
    for page in range(0, num_pages):
        soup = extract_site(
            site="jobstreet", skill_name=skill_name, location=location, num_page=page
        )
        jobs = soup.find_all("div", attrs={"data-search-sol-meta": True})
        if jobs:
            log.info("Jobs found. Scraping attributes...")
            prev_set_len = len(existing_job_ids)
            with open(DB["jobstreet"], "a") as jobstreet_file:
                for job in jobs:
                    job_id = (
                        job.find("a", attrs={"data-automation": "jobTitle"})["id"]
                        .split("-")[-1]
                        .strip()
                    )
                    job_name = job.find(
                        "a", attrs={"data-automation": "jobTitle"}
                    ).text.strip()
                    company_name = job.find(
                        "a", attrs={"data-automation": "jobCompany"}
                    ).text.strip()
                    job_location = job.find(
                        "a", attrs={"data-automation": "jobLocation"}
                    ).text.strip()
                    job_link = f"https://www.jobstreet.com.ph/job/{job_id}"
                    job_payload = {
                        "job_id": job_id,
                        "job_name": job_name,
                        "company_name": company_name,
                        "job_location": job_location,
                        "job_link": job_link,
                        "query": skill_name,
                    }
                    if job_id not in existing_job_ids:
                        existing_job_ids.add(job_id)
                        log.info(f"Adding {job_id} by {company_name} to dataset...")
                        csv_writer = csv.DictWriter(
                            jobstreet_file, fieldnames=FIELD_NAMES
                        )
                        csv_writer.writerow(job_payload)
            if prev_set_len == len(existing_job_ids) and existing_job_ids:
                log.error(
                    f"No new jobs found. {MAX_RETRIES - num_retries} retries left. Going to next page..."
                )
                num_retries += 1
            else:
                num_retries = 0
            if num_retries > MAX_RETRIES:
                log.error("Max number of retries reached. Ending scrape...")
                break
        else:
            log.error("No jobs found.")
