import os
from flask import Flask, render_template
import psycopg2

def create_app(test_config = None):
    # Create app
    app = Flask(__name__, instance_relative_config=True)


    def get_db_connection():
        conn = psycopg2.connect(host='localhost',
                                database='ku_exchange',
                                user=os.environ['DB_USERNAME'],
                                password=os.environ['DB_PASSWORD'])
        return conn

    # Configure app
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # Load the config if it exists.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    


    @app.route('/')
    def index():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM agreements;')
        agreements = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', agreements=agreements)

    return app

