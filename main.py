import typer
from setup import *
from scraper import *

app = typer.Typer()

def validate_site_option(option_value: str):
    valid_sites = ["indeed", "mynimo", "jobstreet"]
    if option_value.lower() not in valid_sites:
        raise typer.BadParameter(f"Invalid site '{option_value}'. Please choose from: {', '.join(valid_sites)}")
    return option_value

def validate_num_pages_option(option_value: int):
    if option_value <= 0:
        raise typer.BadParameter("Number of pages must be a positive integer.")
    return option_value

def main(
    skill_name: str = typer.Option(default=..., help="Skill or job title to search for"),
    location: str = typer.Option(default=..., help="Location to search for jobs"),
    site: str = typer.Option(default=..., callback=validate_site_option, help="Website to scrape jobs from (options: Indeed, Mynimo, Jobstreet)"),
    num_pages: int = typer.Option(default=..., callback=validate_num_pages_option, help="Number of pages to scrape"),
):
    if site.lower().strip() == "indeed":
        scrape_indeed(skill_name=skill_name, location=location, num_pages=num_pages)
    elif site.lower().strip() == "mynimo":
        scrape_mynimo(skill_name=skill_name, location=location, num_pages=num_pages)
    elif site.lower().strip() == "jobstreet":
        scrape_jobstreet(skill_name=skill_name, location=location, num_pages=num_pages)


if __name__ == "__main__":
    create_db_dir()
    create_log_dir()
    typer.run(main)
