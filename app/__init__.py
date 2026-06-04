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
    

    @app.route("/search", methods=["GET"])
    def search_page():
        query = request.args.get("q", "").strip()
        db = get_db()
        cursor = db.cursor()
    
        agreements_results = []
        reports_results = []
    
        if query:
            like_pattern = f"%{query}%"
    
            # 1. DEEP TEXT SEARCH FOR AGREEMENTS
            agreements_sql = """
                SELECT DISTINCT 
                    a."Agreement_ID" AS id, 
                    a."Institution" AS institution,
                    (
                        (CASE WHEN a."Institution" ILIKE %s THEN 20 ELSE 0 END) +
                        (CASE WHEN s.study_field ILIKE %s THEN 15 ELSE 0 END) +
                        (CASE WHEN s.city ILIKE %s OR s.country ILIKE %s THEN 10 ELSE 0 END) +
                        (CASE WHEN a."Agreement_text" ILIKE %s OR a."description" ILIKE %s THEN 5 ELSE 0 END)
                    ) AS score
                FROM agreements AS a
                JOIN study_fields AS s ON s.agreement_id = a."Agreement_ID"
                WHERE a."Institution" ILIKE %s 
                   OR s.study_field ILIKE %s
                   OR s.city ILIKE %s
                   OR s.country ILIKE %s
                   OR a."Agreement_text" ILIKE %s
                   OR a."description" ILIKE %s
                ORDER BY score DESC, institution ASC;
            """
            cursor.execute(agreements_sql, [like_pattern] * 12)
            for row in cursor.fetchall():
                agreements_results.append({"id": row[0], "institution": row[1], "score": row[2]})
    
            # 2. DEEP TEXT SEARCH FOR REPORTS (Now selecting individual report_id)
            reports_sql = """
                SELECT report_id, institution,
                    (
                        (CASE WHEN institution ILIKE %s THEN 20 ELSE 0 END) +
                        (CASE WHEN study_field ILIKE %s THEN 15 ELSE 0 END) +
                        (CASE WHEN overall_comments ILIKE %s 
                               OR crucial_aspects ILIKE %s 
                               OR unexpected_costs ILIKE %s 
                               OR cost_comparison ILIKE %s
                               OR most_rewarding ILIKE %s 
                               OR greatest_challenge ILIKE %s THEN 5 ELSE 0 END)
                    ) AS score
                FROM reports
                WHERE institution ILIKE %s 
                   OR study_field ILIKE %s
                   OR overall_comments ILIKE %s
                   OR crucial_aspects ILIKE %s
                   OR unexpected_costs ILIKE %s
                   OR cost_comparison ILIKE %s
                   OR most_rewarding ILIKE %s
                   OR greatest_challenge ILIKE %s
                ORDER BY score DESC, institution ASC;
            """
            cursor.execute(reports_sql, [like_pattern] * 16)
            for row in cursor.fetchall():
                reports_results.append({"id": row[0], "institution": row[1], "score": row[2]})
    
        return render_template(
            "search.html", 
            query=query, 
            agreements=agreements_results, 
            reports=reports_results
        )
    
    
    @app.route("/api/live-search", methods=["GET"])
    def live_search():
        query = request.args.get("q", "").strip()
        db = get_db()
        cursor = db.cursor()
    
        agreements_results = []
        reports_results = []
        like_pattern = f"%{query}%"
    
        if query:
            agreements_sql = """
                SELECT DISTINCT a."Agreement_ID", a."Institution"
                FROM agreements AS a
                JOIN study_fields AS s ON s.agreement_id = a."Agreement_ID"
                WHERE a."Institution" ILIKE %s 
                   OR s.study_field ILIKE %s 
                   OR a."Agreement_text" ILIKE %s 
                   OR a."description" ILIKE %s
                LIMIT 3;
            """
            cursor.execute(agreements_sql, (like_pattern, like_pattern, like_pattern, like_pattern))
        else:
            cursor.execute('SELECT DISTINCT "Agreement_ID", "Institution" FROM agreements ORDER BY "Institution" ASC LIMIT 3;')
        agreements_results = [{"id": r[0], "institution": r[1]} for r in cursor.fetchall()]
    
        if query:
            # Modified to select report_id along with the institution name
            reports_sql = """
                SELECT report_id, institution FROM reports 
                WHERE institution ILIKE %s 
                   OR study_field ILIKE %s 
                   OR overall_comments ILIKE %s 
                   OR crucial_aspects ILIKE %s
                   OR unexpected_costs ILIKE %s
                LIMIT 3;
            """
            cursor.execute(reports_sql, (like_pattern, like_pattern, like_pattern, like_pattern, like_pattern))
        else:
            cursor.execute('SELECT report_id, institution FROM reports ORDER BY institution ASC LIMIT 3;')
        reports_results = [{"id": r[0], "institution": r[1]} for r in cursor.fetchall()]
    
        return jsonify({"agreements": agreements_results, "reports": reports_results})

    return app