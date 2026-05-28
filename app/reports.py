from flask import (
    Blueprint, render_template
)

from app.init_db import get_db
import psycopg2
from psycopg2.extras import RealDictCursor

bp = Blueprint('reports', __name__)

@bp.route('/reports')
def table():
    db = get_db().cursor(cursor_factory=RealDictCursor)

    db.execute('''
    SELECT
        report_id,
        institution,
        study_field,
        academic_year
    FROM reports
    ORDER BY report_id
    ''')

    reports = db.fetchall()

    return render_template('reports.html', reports=reports)


# Single report page
@bp.route('/reports/<int:id>')
def report(id):
    db = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    db.execute('''
        SELECT
            report_id,
            institution,
            study_field,
            academic_year,
            report_text,
            costs,
            choices
        FROM reports
        WHERE report_id = %s
    ''', (id,))

    report = db.fetchone()

    return render_template('report_text.html', report=report)