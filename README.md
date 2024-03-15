# JIM Jobs Scraper

## Context
The JIM Jobs Scraper is a versatile tool designed to facilitate job searching by extracting job listings from three popular job search websites: JobStreet, Indeed, and Mynimo. This scraper offers users the ability to specify a skill or job title, location, and the number of pages to scrape, providing a comprehensive collection of relevant job opportunities.

Job seekers in various regions, particularly in Cebu, can utilize this tool to streamline their job search process by aggregating job listings from multiple sources into a single interface. Whether searching for entry-level positions or senior roles, the JIM Jobs Scraper simplifies the job hunting experience by consolidating job listings from diverse platforms.

## Run Locally 
Clone the project

```bash
  git clone https://github.com/blurridge/JIM-jobs-scraper
```

Go to the project directory

```bash
  cd JIM-jobs-scraper
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the script

```bash
  python main.py [-h] [-d DESTINATION] [-c] [-u] [-sd START_DATE] [-ed END_DATE]
```

## Arguments 
```bash
options:
 *  --skill-name        TEXT     Skill or job title to search for [default: None] [required]                           
 *  --location          TEXT     Location to search for jobs [default: None] [required]                               
 *  --site              TEXT     Website to scrape jobs from (options: Indeed, Mynimo, Jobstreet) [default: None]     
                                 [required]                                                                           
 *  --num-pages         INTEGER  Number of pages to scrape [default: None] [required]                                 
    --help                       Show this message and exit.
```

## Example usage
To scrape job listings for "Data Analyst" positions in "Cebu" from Indeed, you can use the following command:
```bash
python main.py --skill_name "Data Analyst" --location "Cebu" --site indeed --num_pages 3
```

## Stay in touch

If you have any questions, suggestions, or need further assistance, feel free to reach out to me. I'm always happy to help!

- Email: [zachriane01@gmail.com](mailto:zachriane01@gmail.com)
- GitHub: [@blurridge](https://github.com/blurridge)
- Twitter: [@zachahalol](https://twitter.com/zachahalol)
- Instagram: [@zachahalol](https://www.instagram.com/zachahalol)
- LinkedIn: [Zach Riane Machacon](https://www.linkedin.com/in/zachriane)