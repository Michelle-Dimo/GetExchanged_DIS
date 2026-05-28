from flask import Blueprint, render_template, g, redirect, url_for
from functools import wraps

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


@bp.route('/about')
def about():

    return render_template('about.html')