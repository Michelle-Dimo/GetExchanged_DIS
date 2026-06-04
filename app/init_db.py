import os
import psycopg2
from psycopg2.extras import DictCursor
import click
import pandas as pd
from sqlalchemy import create_engine, text, SmallInteger, Float
from flask import g


DB_USER = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=DictCursor
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    conn.commit()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # ---------------- AGREEMENTS ----------------
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    engine = create_engine(connection_string)

    with engine.begin() as sa_con:
        sa_con.execute(text("DROP TABLE IF EXISTS agreements CASCADE"))

    agreement_parsed = pd.read_csv(
        os.path.join(base_dir, "../data/New_Parsed_Agreement_Data.csv")
    )

    agreement_parsed.to_sql(
        "agreements",
        engine,
        index=False,
        if_exists="fail"
    )

    print("Agreements imported successfully!")

    cur.execute("DROP TABLE IF EXISTS users CASCADE;")

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
        )
    """)

    reports_path = os.path.normpath(
        os.path.join(base_dir, "../data/Reports_clean.csv")
    )

    df = pd.read_csv(reports_path)

    rating_cols = [
        'overall_rating',
        'arrival_satisfaction',
        'housing_satisfaction',
        'registration_ease',
        'academics_satisfaction',
        'nonacademic_satisfaction'
    ]

    df[rating_cols] = df[rating_cols].apply(
        pd.to_numeric, errors='coerce'
    ).astype('Int64')

    cost_cols = [
        'cost_insurance',
        'cost_housing_pm',
        'cost_books',
        'cost_transport',
        'cost_food',
        'cost_personal',
        'cost_communication',
        'cost_other'
    ]

    for col in cost_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in cost_cols:
        max_val = df[col].max()
        print(f"{col} max value: {max_val}")

        bad = df[df[col] > 1e10]
        if not bad.empty:
            print(f"Overflow candidates in {col}:")
            print(bad[[col]].head())

    for col in cost_cols:
        df.loc[df[col] > 1e10, col] = None


    with engine.begin() as con:
        con.execute(text("DROP TABLE IF EXISTS reports CASCADE"))

    df.to_sql(
        "reports",
        engine,
        if_exists="fail",
        index=False,
        dtype={
            'overall_rating': SmallInteger(),
            'arrival_satisfaction': SmallInteger(),
            'housing_satisfaction': SmallInteger(),
            'registration_ease': SmallInteger(),
            'academics_satisfaction': SmallInteger(),
            'nonacademic_satisfaction': SmallInteger(),

            'cost_insurance': Float(),
            'cost_housing_pm': Float(),
            'cost_books': Float(),
            'cost_transport': Float(),
            'cost_food': Float(),
            'cost_personal': Float(),
            'cost_communication': Float(),
            'cost_other': Float(),
        }
    )

    with engine.begin() as con:
        con.execute(text("CREATE INDEX IF NOT EXISTS idx_reports_inst_trgm ON reports USING gin (institution gin_trgm_ops);"))
        con.execute(text("CREATE INDEX IF NOT EXISTS idx_reports_field_trgm ON reports USING gin (study_field gin_trgm_ops);"))

    print("Reports imported successfully!")

    cur.execute("DROP TABLE IF EXISTS study_fields;")

    cur.execute("""
        CREATE TABLE study_fields (
            index INT UNIQUE,
            study_field VARCHAR(80) NOT NULL,
            institution VARCHAR(80) NOT NULL,
            continent VARCHAR(20) NOT NULL,
            country VARCHAR(40) NOT NULL,
            city VARCHAR(80) NOT NULL,
            n_agreements INT NOT NULL,
            agreement_id INT NOT NULL,
            latitude FLOAT,
            longitude FLOAT
        )
    """)

    study_fields_path = os.path.normpath(
        os.path.join(base_dir, "../data/Study_fields_with_latlon.csv")
    )

    with open(study_fields_path, "r") as f:
        cur.copy_expert("""
            COPY study_fields (
                index,
                study_field,
                institution,
                continent,
                country,
                city,
                n_agreements,
                agreement_id,
                latitude,
                longitude        
            )
            FROM STDIN WITH (FORMAT csv, HEADER true)
        """, f)

    conn.commit()
    cur.close()


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)