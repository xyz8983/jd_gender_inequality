import sqlite3
from sqlite3 import Error
from contextlib import contextmanager

DB_SCHEMA = 'job_description.db'

def create_db(db_file=DB_SCHEMA):
    """create a new db if the db file does not exist"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("success")
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

@contextmanager
def create_connection(db_file=DB_SCHEMA):
    try:
        conn = sqlite3.connect(db_file)
        yield conn.cursor()
        conn.commit()
    except Error as e:
        print(e)    
    finally:
        if conn:
            conn.close()


def create_table():
    query_wuyi_job_male = """
        CREATE TABLE IF NOT EXISTS wuyi_job_male 
        (
            url varchar primary key,
            job_title varchar,
            job_description = Field() #[str]
            descrimination_content varchar
            keywords = Field() #[str]  #todo: the first 2-3 is enough
            job_type = Field() #[str] 
            city varchar,
            district varchar,
            company_name varchar,
            company_type varchar,
            company_size varchar,
            salary_range varchar
        )       
    """
    with create_connection() as conn:
        conn.execute(query_wuyi_job_male)
    print("seems created?")


# if __name__ == '__main__':
#     pass