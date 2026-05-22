from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort
from app.init_db import get_db

bp = Blueprint('agreements', __name__)

@bp.route('/agreements')
def table():
    db = get_db().cursor()
    db.execute('''
                SELECT *
                FROM agreements 
                            ''')
    agreements = db.fetchall()

    return render_template('agreements.html', agreements=agreements)
    
    