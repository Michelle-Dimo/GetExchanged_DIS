#link to tutorial: https://flask.palletsprojects.com/en/stable/tutorial/database/


from flask import (
    Blueprint, flash, g, redirect,
    render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from app.init_db import get_db

bp = Blueprint('auth', __name__)

#register
@bp.route('/register', methods=('GET', 'POST'))
def register():

    if request.method == 'POST':

        ku_id = request.form['ku_id']
        full_name = request.form['full_name']
        email = request.form['email']
        study_field = request.form['study_field']
        academic_year = request.form['academic_year']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()

        error = None

        if not ku_id:
            error = 'KU ID is required.'

        elif not password:
            error = 'Password is required.'

        if error is None:

            hashed_password = generate_password_hash(password)

            cur.execute(
                '''
                INSERT INTO users
                (ku_id, full_name, email, study_field, academic_year, password)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''',
                (
                    ku_id,
                    full_name,
                    email,
                    study_field,
                    academic_year,
                    hashed_password
                )
            )

            db.commit()

            flash('Account created successfully.')
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('register.html')

#login
@bp.route('/login', methods=('GET', 'POST'))
def login():

    if request.method == 'POST':

        ku_id = request.form['ku_id']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()

        cur.execute(
            'SELECT * FROM users WHERE ku_id = %s',
            (ku_id,)
        )

        user = cur.fetchone()

        error = None

        if user is None:
            error = 'Incorrect KU ID.'

        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:

            session.clear()
            session['user_id'] = user['id']

            flash('Logged in successfully.')

            return redirect(url_for('home'))

        flash(error)

    return render_template('login.html')

#logout
@bp.route('/logout')
def logout():

    session.clear()

    flash('You have been logged out.')

    return redirect(url_for('home'))

#automatic login of users
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