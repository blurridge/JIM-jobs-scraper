import typer
from setup import *
from scraper import *

app = typer.Typer()


def main(
    skill_name: str = typer.Option(default=...),
    location: str = typer.Option(default=...),
    site: str = typer.Option(default="indeed"),
    num_pages: int = typer.Option(default=...),
):
    if site == "indeed":
        scrape_indeed(skill_name=skill_name, location=location, num_pages=num_pages)
    else:
        print("Not yet implemented.")


if __name__ == "__main__":
    create_db_dir()
    create_log_dir()
    typer.run(main)
