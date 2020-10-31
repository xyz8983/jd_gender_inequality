
import os
import sys


# sys.path.append(os.path.join(os.path.abspath(os.getcwd()), 'src'))
# from src.db import create_connection

def test_create_connection():
    query = "create table person (id integer primary key, firstname varchar)"
    with create_connection() as conn:
        conn.execute(query)
    print("seems created?")    


if __name__ == '__main__':
    print(os.getcwd())
    print(__package__)
    print(sys.path)
    # test_create_connection()    