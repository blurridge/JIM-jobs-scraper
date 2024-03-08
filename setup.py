import os

def create_db_dir():
    """
    Creates database directory for scraped jobs.
    """
    job_db = "job_db"
    if not os.path.exists(job_db):
        os.mkdir(job_db)
        print('Base Directory Created Successfully.')
    
