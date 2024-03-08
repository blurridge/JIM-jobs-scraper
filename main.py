import typer
from setup import *
from scraper import *

app = typer.Typer()



if __name__ == "__main__":
    create_db_dir()
    create_log_dir()
    app()