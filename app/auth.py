#link to tutorial: https://flask.palletsprojects.com/en/stable/tutorial/database/

from flask import (
    Blueprint, flash, g, redirect,
    render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from .init_db import get_db

#regex patterns to verify KU-ID and email:
import re
KU_ID_PATTERN = re.compile(r'^[a-zA-Z]{3}\d{3}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=('GET', 'POST'))
def register():

    if g.user:
        return redirect(url_for('main.home'))

    if request.method == 'POST':

        ku_id = request.form.get('ku_id')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        study_field = request.form.get('study_field')
        password = request.form.get('password')
        status = request.form.get('status')

        error = None

        # Basic validation
        if not ku_id:
            error = 'KU ID is required.'
        elif not password:
            error = 'Password is required.'

        if not ku_id:
            error = 'KU ID is required.'
        elif not KU_ID_PATTERN.match(ku_id):
            error = 'KU ID must be 3 letters followed by 3 digits (e.g. abc123).'
        elif not password:
            error = 'Password is required.'
        elif not EMAIL_PATTERN.match(email):
            error = 'Invalid email format.'

        db = get_db()
        cur = db.cursor()

        # Check if user exists
        if error is None:
            cur.execute(
                'SELECT id FROM users WHERE ku_id = %s',
                (ku_id,)
            )
            existing_user = cur.fetchone()

            if existing_user is not None:
                error = 'User already exists.'

        # Insert user
        if error is None:

            hashed_password = generate_password_hash(password)

            cur.execute(
                """
                INSERT INTO users
                (ku_id, full_name, email, study_field, password, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    ku_id,
                    full_name,
                    email,
                    study_field,
                    hashed_password,
                    status
                )
            )

            db.commit()
            cur.close()

            flash('Account created successfully.', 'success')
            return redirect(url_for('auth.login'))

        cur.close()
        flash(error, 'error')

    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():

    if g.user:
        return redirect(url_for('main.home'))

    if request.method == 'POST':

        ku_id = request.form.get('ku_id')
        password = request.form.get('password')

        db = get_db()
        cur = db.cursor()

        cur.execute(
            'SELECT * FROM users WHERE ku_id = %s',
            (ku_id,)
        )

        user = cur.fetchone()
        cur.close()

        error = None

        if user is None:
            error = 'Incorrect KU ID.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if not ku_id:
            error = 'KU ID is required.'
        elif not KU_ID_PATTERN.match(ku_id):
            error = 'KU ID must be 3 letters followed by 3 digits (e.g. abc123).'
        elif not password:
            error = 'Password is required.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']

            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.home'))

        flash(error, 'error')

    return render_template('login.html')

@bp.route('/logout')
def logout():

    session.clear()
    flash('You have been logged out.', 'info')

    return redirect(url_for('auth.login'))

@bp.before_app_request
def load_logged_in_user():

    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cur = db.cursor()

        cur.execute(
            'SELECT * FROM users WHERE id = %s',
            (user_id,)
        )

        g.user = cur.fetchone()
        cur.close()