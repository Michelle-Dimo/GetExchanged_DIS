import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="ku_exchange",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('DROP TABLE IF EXISTS agreements;')
cur.execute('CREATE TABLE agreements (index INT UNIQUE,'
                                 'id INT PRIMARY KEY,'
                                 'institution VARCHAR (80) NOT NULL,'
                                 'text TEXT NOT NULL)'
                                 )

# Insert data into the table

with open("../data/Agreement_data.csv", "r") as f:
    cur.copy_expert("""
        COPY agreements(index, id, institution, text)
        FROM STDIN
        WITH (FORMAT csv, HEADER true)
    """, f)

cur.execute('DROP TABLE IF EXISTS reports;')
cur.execute('CREATE TABLE reports (academic_year INT NOT NULL,'
                                 'rating INT NOT NULL,'
                                 'report_id INT PRIMARY KEY,'
                                 'costs INTEGER NOT NULL,'
                                 'report_text TEXT NOT NULL,'
                                 'institution VARCHAR (80) NOT NULL,'
                                 'choices VARCHAR (80) NOT NULL)'
                                 )

with open("../data/Reports.csv", "r") as f:
    cur.copy_expert("""
        COPY reports(academic_year, rating, report_id, costs, report_text, institution, choices)
        FROM STDIN
        WITH (FORMAT csv, HEADER true)
    """, f)

cur.execute('DROP TABLE IF EXISTS study_fields;')
cur.execute('CREATE TABLE study_fields (index INT UNIQUE,'
                                 'field VARCHAR (80) NOT NULL,'
                                 'institution VARCHAR (80) NOT NULL,'
                                 'continent VARCHAR (20) NOT NULL,'
                                 'country VARCHAR (20) NOT NULL,'
                                 'city VARCHAR (20) NOT NULL,'
                                 'n_agreements INT NOT NULL,'
                                 'agreement_id INT NOT NULL)'
                                 )

with open("../data/Study_Fields.csv", "r") as f:
    cur.copy_expert("""
        COPY study_fields(field, institution, n_agreements, agreement_id, continent, country, city)
        FROM STDIN
        WITH (FORMAT csv, HEADER true)
    """, f)




conn.commit()

cur.close()
conn.close()