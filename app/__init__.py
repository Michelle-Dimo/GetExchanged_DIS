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
    def home():
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
    
    @app.route("/search", methods=["GET", "POST"])
    def search():
        results = []
        
        if request.method == "POST":
            query = request.form.get("search", "")
        else:
            query = request.args.get("search", "")

        if query:
            query = query.strip()
            db = get_db()
            cursor = db.cursor()

            search_sql = """
                SELECT DISTINCT
                    institution, city, country, study_field
                FROM study_fields
                WHERE 
                    institution %% %s 
                    OR city %% %s 
                    OR country %% %s 
                    OR study_field %% %s
                    OR institution ILIKE %s
                LIMIT 50;
            """
            
            contains_pattern = f"%%{query}%%"

            try:
                cursor.execute(search_sql, (query, query, query, query, contains_pattern))
                raw_rows = cursor.fetchall()
                
                for row in raw_rows:
                    row_text = " | ".join(str(item) for item in row if item is not None)
                    
                    results.append({
                        "file": "Database Record",
                        "match": row_text
                    })
            except Exception as e:
                results.append({
                    "file": "System Error",
                    "match": f"Search failed: {str(e)}"
                })

        return render_template("homepage.html", results=results, query=query)

    return app