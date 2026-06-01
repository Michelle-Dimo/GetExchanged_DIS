import os
from flask import Flask, redirect, url_for, jsonify, request, render_template
import csv
import re
from app.init_db import get_db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DB_HOST=os.environ.get("DB_HOST"),
        DB_NAME=os.environ.get("DB_NAME"),
        DB_USER=os.environ.get("DB_USERNAME"),
        DB_PASSWORD=os.environ.get("DB_PASSWORD"),
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import init_db
    init_db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import main
    app.register_blueprint(main.bp)

    from . import agreements
    app.register_blueprint(agreements.bp)

    from . import reports
    app.register_blueprint(reports.bp)

    @app.route("/")
    def index():
        return redirect(url_for("main.home"))

    @app.route("/api/map-data")
    def map_data():
        db = get_db().cursor()
        db.execute("""
            SELECT
                institution,
                city,
                country,
                continent,
                latitude,
                longitude,
                COUNT(DISTINCT agreement_id) AS n_agreements,
                STRING_AGG(DISTINCT study_field, '||') AS study_fields
            FROM study_fields
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            GROUP BY institution, city, country, continent, latitude, longitude
        """)
        cols = [col[0] for col in db.description]
        rows = [dict(zip(cols, row)) for row in db.fetchall()]


        for row in rows:
            row["study_fields"] = row["study_fields"].split("||") if row["study_fields"] else []

        return jsonify({"universities": rows})

    @app.route("/search", methods=["POST"])
    def search():
        results = []
        query = request.form.get("search", "")

        try:
            pattern = re.compile(query, re.IGNORECASE)

            data_folder = "data"
            for filename in os.listdir(data_folder):
                if filename.endswith(".csv"):
                    filepath = os.path.join(data_folder, filename)

                    with open(filepath, newline="", encoding="utf-8") as f:
                        reader = csv.reader(f)

                        for row in reader:
                            row_text = " | ".join(row)
                            if pattern.search(row_text):
                                results.append({
                                    "file": filename,
                                    "match": row_text
                                })

        except re.error:
            results.append({
                "file": "Error",
                "match": "Invalid regex pattern"
            })

        return render_template("homepage.html", results=results)

    return app