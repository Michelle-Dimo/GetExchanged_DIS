import os
import re
from flask import Flask, app, redirect, render_template, request, g, url_for
import psycopg2

def create_app(test_config = None):
    # Create app
    app = Flask(__name__, instance_relative_config=True)

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

    #To be able to authenticate users
    from . import auth
    app.register_blueprint(auth.bp)

    from . import main
    app.register_blueprint(main.bp)

    from . import agreements
    app.register_blueprint(agreements.bp)

    # Map (plz virk)
    from flask import jsonify
    import csv

    @app.route('/')
    def index():

        if g.user:
            return redirect(url_for('main.home'))

        return redirect(url_for('auth.login'))
    
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