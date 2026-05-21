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


conn.commit()

cur.close()
conn.close()