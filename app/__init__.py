import os
import re
from flask import Flask, app, render_template, request
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
    
    from . import init_db
    init_db.init_app(app)

    # Creating routes
    @app.route('/')
    def home():
        return render_template('homepage.html')

    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/index')
    def index():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM agreements;')
        agreements = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', agreements=agreements)
    
    @app.route('/reports')
    def reports():
        return render_template('reports.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
    
    @app.route('/profile')
    def profile():
        return render_template('profile.html')
    
    from . import agreements
    app.register_blueprint(agreements.bp)

    # Map (plz virk)
    from flask import jsonify
    import csv

    @app.route("/api/map-data")
    def map_data():
        rows = []
        with open("data/Study_fields_with_latlon.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
        return jsonify({"universities": rows})

    # Regex matching for homepage (maybe?? idk, har givet det et skud)
    DATA_FOLDER = "data"
    @app.route("/search", methods=["POST"])
    def search():
        results = []
        if request.method == "POST":
            search = request.form.get("search")
            try:
                pattern = re.compile(search, re.IGNORECASE)
                for filename in os.listdir(DATA_FOLDER):
                    if filename.endswith(".csv"):
                        filepath = os.path.join(DATA_FOLDER, filename)
                        with open(filepath, newline="", encoding="utf-8") as file:
                            reader = csv.reader(file)
                            for row in reader:
                                row_text = " | ".join(row)
                                if pattern.search(row_text):
                                    results.append({"file": filename, "match": row_text})
            except re.error:
                results.append({"file": "Error", "match": "Invalid regex pattern"})
        return render_template("homepage.html", results=results)
    return app