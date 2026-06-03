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


    @app.route("/search", methods=["GET"])
    def search():
        query = request.args.get("q", "").strip()
        if not query:
            return render_template("search_results.html", results={"agreements": [], "reports": []}, query="")

        db = get_db()
        cur = db.cursor()

        # 1. Search Agreements: Match on institution, study field, or country with a similarity threshold > 0.2
        cur.execute("""
            SELECT DISTINCT a.id, a.institution,
                   GREATEST(similarity(a.institution, %s), COALESCE(similarity(s.study_field, %s), 0), COALESCE(similarity(s.country, %s), 0)) as score
            FROM agreements a
            LEFT JOIN study_fields s ON a.id = s.agreement_id
            WHERE similarity(a.institution, %s) > 0.20
               OR similarity(s.study_field, %s) > 0.20
               OR similarity(s.country, %s) > 0.20
            ORDER BY score DESC
            LIMIT 10;
        """, (query, query, query, query, query, query))
        agreement_rows = cur.fetchall()

        # 2. Search Reports: Match on institution or study field
        cur.execute("""
            SELECT DISTINCT institution, 
                   GREATEST(similarity(institution, %s), COALESCE(similarity(study_field, %s), 0)) as score
            FROM reports
            WHERE similarity(institution, %s) > 0.20
               OR similarity(study_field, %s) > 0.20
            ORDER BY score DESC
            LIMIT 10;
        """, (query, query, query, query))
        report_rows = cur.fetchall()

        results = {
            "agreements": [{"id": r[0], "institution": r[1], "score": round(r[2], 2)} for r in agreement_rows],
            "reports": [{"institution": r[0], "score": round(r[1], 2)} for r in report_rows]
        }

        return render_template("search_results.html", results=results, query=query)


    return app