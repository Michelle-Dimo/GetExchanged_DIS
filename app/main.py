from flask import Blueprint, render_template, g, redirect, url_for, flash, request
from functools import wraps
from .init_db import get_db
import psycopg2.extras
import psycopg2
from psycopg2.extras import RealDictCursor

bp = Blueprint('main', __name__)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


@bp.route('/home')
def home():
    return render_template('homepage.html')


@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@bp.route('/reports')
def table():
    db = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    db.execute('''
        SELECT
            report_id,
            institution,
            study_field,
            academic_year
        FROM reports
        ORDER BY institution
    ''')

    reports = db.fetchall()

    return render_template('reports.html', reports=reports)

@bp.route('/my_reports')
@login_required
def my_reports():
    db = get_db().cursor()
    db.execute(
        'SELECT * FROM reports WHERE user_id = %s',
        (g.user['id'],)
    )
    reports = db.fetchall()
    return render_template('my_reports.html', reports=reports)

@bp.route('/about')
def about():

    return render_template('about.html')

@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    if request.method == 'POST':

        full_name = request.form.get('full_name')
        email = request.form.get('email')
        study_field = request.form.get('study_field')
        status = request.form.get('status')
        db = get_db()

        try:
            cur = db.cursor()

            cur.execute(
                """
                UPDATE users
                SET full_name = %s,
                    email = %s,
                    study_field = %s,
                    status = %s
                WHERE id = %s
                """,
                (
                    full_name,
                    email,
                    study_field,
                    status,
                    g.user['id']
                )
            )

            db.commit()
            cur.close()

            flash("Profile updated successfully!", "success")

        except Exception as e:
            db.rollback()
            flash(f"Something went wrong: {e}", "error")
        
        if not full_name or not email:
            flash("Name and email are required", "error")
            return redirect(url_for('main.edit_profile'))

        return redirect(url_for('main.profile'))

    return render_template('edit_profile.html')


from app.init_db import get_db

@bp.route('/my_applications')
@login_required
def my_applications():
    db = get_db().cursor()
    db.execute(
        '''
        SELECT a.id, a.status, a.created_at, ag.institution, ag.text
        FROM applications a
        JOIN agreements ag ON a.agreement_id = ag.id
        WHERE a.user_id = %s
        ORDER BY a.created_at DESC
        ''',
        (g.user['id'],)
    )
    applications = db.fetchall()
    return render_template('my_applications.html', applications=applications)

@bp.route('/apply/<int:agreement_id>', methods=['POST'])
@login_required
def apply(agreement_id):
    db = get_db()
    cur = db.cursor()

    # Check if already applied
    cur.execute(
        'SELECT id FROM applications WHERE user_id = %s AND agreement_id = %s',
        (g.user['id'], agreement_id)
    )
    existing = cur.fetchone()

    if existing:
        flash('You have already applied to this agreement.')
    else:
        cur.execute(
            'INSERT INTO applications (user_id, agreement_id) VALUES (%s, %s)',
            (g.user['id'], agreement_id)
        )
        db.commit()
        flash('Application submitted successfully.')

    return redirect(url_for('main.my_applications'))