from flask import Blueprint, render_template, g, redirect, url_for, flash, request
from functools import wraps
from .init_db import get_db

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
def reports():

    return render_template('reports.html')

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
        academic_year = request.form.get('academic_year')

        db = get_db()

        try:
            cur = db.cursor()

            cur.execute(
                """
                UPDATE users
                SET full_name = %s,
                    email = %s,
                    study_field = %s,
                    academic_year = %s
                WHERE id = %s
                """,
                (
                    full_name,
                    email,
                    study_field,
                    academic_year,
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
