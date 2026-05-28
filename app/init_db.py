import os
from venv import create
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from flask import current_app, g
import click


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'],
        cursor_factory=DictCursor)
        
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



def init_db():
    conn = get_db()

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Get the absolute path to the directory containing init_db.py
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Execute a command: this creates a new table
    cur.execute('DROP TABLE IF EXISTS agreements CASCADE;')
    cur.execute('''CREATE TABLE agreements 
                        (index INT UNIQUE,
                        id INT PRIMARY KEY,
                        institution VARCHAR (80) NOT NULL,
                        text TEXT NOT NULL)'''
                                     )
    
    # Construct absolute path: goes up one level from 'app/' to project root, then into 'data/'
    agreements_path = os.path.normpath(os.path.join(base_dir, "../data/Agreement_data.csv"))

    # Insert data into the table
    with open(agreements_path, "r") as f:
        cur.copy_expert("""
            COPY agreements(index, id, institution, text)
            FROM STDIN
            WITH (FORMAT csv, HEADER true)
        """, f)

    ##Create users table
    
    cur.execute('DROP TABLE IF EXISTS users CASCADE;')
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'user_status'
            ) THEN
                CREATE TYPE user_status AS ENUM ('Alumni', 'Applicant');
            END IF;
        END
        $$;
    """)
    cur.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            ku_id VARCHAR(20) UNIQUE NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            study_field VARCHAR(100),
            password TEXT NOT NULL,
            status user_status NOT NULL
        );
    """)

    #cur.execute('DROP TABLE IF EXISTS reports;')
    #cur.execute('CREATE TABLE reports ('report_id INT PRIMARY KEY,'
    #                                 'user_id INT REFERENCES users(id)'
    #                                 'academic_year INT NOT NULL,'
    #                                 'rating INT NOT NULL,'
    #                                 'costs INTEGER NOT NULL,'
    #                                 'report_text TEXT NOT NULL,'
    #                                 'institution VARCHAR (80) NOT NULL,'
    #                                 'choices VARCHAR (80) NOT NULL)'
    #                                 )
#
    ## Construct the absolute path to the reports data like how we did with the agreements data.
    #reports_path = os.path.normpath(os.path.join(base_dir, "../data/Reports.csv"))
    #with open(reports_path, "r") as f:
    #    cur.copy_expert("""
    #        COPY reports(academic_year, rating, report_id, costs, report_text, institution, choices)
    #        FROM STDIN
    #        WITH (FORMAT csv, HEADER true)
    #    """, f)
#
    #cur.execute('DROP TABLE IF EXISTS study_fields;')
    #cur.execute('CREATE TABLE study_fields (index INT UNIQUE,'
    #                                 'field VARCHAR (80) NOT NULL,'
    #                                 'institution VARCHAR (80) NOT NULL,'
    #                                 'continent VARCHAR (20) NOT NULL,'
    #                                 'country VARCHAR (20) NOT NULL,'
    #                                 'city VARCHAR (20) NOT NULL,'
    #                                 'n_agreements INT NOT NULL,'
    #                                 'agreement_id INT NOT NULL)'
    #                                 )
#
    ## Construct the absolute path to the reports data like how we did with the agreements data.
    #study_fields_path = os.path.normpath(os.path.join(base_dir, "../data/Study_Fields.csv"))
    #with open(study_fields_path, "r") as f:
    #    cur.copy_expert("""
    #        COPY study_fields(field, institution, n_agreements, agreement_id, continent, country, city)
    #        FROM STDIN
    #        WITH (FORMAT csv, HEADER true)
    #    """, f)



    conn.commit()
    cur.close()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

