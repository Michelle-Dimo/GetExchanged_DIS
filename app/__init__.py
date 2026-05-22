import os
from flask import Flask, app, render_template
import psycopg2

def create_app(test_config = None):
    # Create app
    app = Flask(__name__, instance_relative_config=True)


    def get_db_connection():
        conn = psycopg2.connect(host='localhost',
                                database='ku_exchange',
                                user=os.environ['DB_USERNAME'],
                                password=os.environ['DB_PASSWORD'])
        return conn

    # Configure app
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # Load the config if it exists.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    from . import init_db
    init_db.init_app(app)

    @app.route('/')
    def home():
        return render_template('homepage.html')

    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/index')
    def index():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM agreements;')
        agreements = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', agreements=agreements)
    
    @app.route('/reports')
    def reports():
        return render_template('reports.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
    
    from . import agreements
    app.register_blueprint(agreements.bp)
    

    @app.route('/profile')
    def profile():
        return render_template('profile.html')
    
    if __name__ == '__main__':
        app.run(debug=True)

    return app