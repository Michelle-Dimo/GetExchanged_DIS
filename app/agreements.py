from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort
from app.init_db import get_db
import psycopg2

bp = Blueprint('agreements', __name__)

@bp.route('/agreements')
def table():
    db = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    db.execute('''
                SELECT DISTINCT a.id, a.institution, s.study_field, s.city, s.country
                FROM agreements AS a
                JOIN study_fields AS s ON s.agreement_id = a.id
                ORDER BY a.id
                            ''')
    agreements = db.fetchall()

    return render_template('agreements.html', agreements=agreements)
    
@bp.route('/agreements/<int:id>')
def agreement(id):
    db = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    db.execute('''
                SELECT *
                FROM parsed_agreement_text
                WHERE parsed_agreement_text."Agreement_ID" = %s
               ''', (id,))
    query_result = db.fetchone()
    agreement_data = dict(query_result)

    return render_template('agreements_text.html', agreement_data=agreement_data)
