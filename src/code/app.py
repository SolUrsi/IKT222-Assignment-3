from flask import Flask
from flask.cli import with_appcontext
import click
import os
import sys
import pyotp

from .extensions import bcrypt, login_manager 
from .auth_bp import auth_bp
from .main_bp import main_bp
from .twofa_bp import twofa_bp
from .models import db, User, Post

def get_db_path(app_instance):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(project_root, 'data', 'app.db')

app = Flask(__name__)
# Configs

# --  Hot reload of HTML
app.config.update(TEMPLATES_AUTO_RELOAD=True)

# -- Secret key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devkey')

# -- Database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{get_db_path(app)}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions

# -- Database and ORM from models.py
db.init_app(app)

# -- Bcrypt for password hashing
bcrypt.init_app(app)

# -- Login manager for user sessions
login_manager.init_app(app)
login_manager.login_view = 'main.sneaky'

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom CLI command to initialize the database
# -- Creates 'data' directory if it doesn't exist and initializes database tables
@app.cli.command('init-db')
@with_appcontext
def init_db_command():
    db_path = get_db_path(app)
    data_dir = os.path.dirname(db_path)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    db.create_all()
    click.echo("Database tables created.")

    if User.query.count() == 0:
        seed_data()
    else:
        click.echo("Users already exist. Skipping data seed.")

def seed_data():
    hashed_password1 = bcrypt.generate_password_hash("password").decode('utf-8')
    hashed_password2 = bcrypt.generate_password_hash("secret").decode('utf-8')

    otp_secret1 = pyotp.random_base32()
    otp_secret2 = pyotp.random_base32()

    alice = User(username='Alice', email='alice@secret.com', password=hashed_password1, failed_login_attempts=0, lockout_until=None, otp_secret=otp_secret1, is_2fa_enabled=True)
    bob = User(username='Bob', email='bob@secret.com', password=hashed_password2, failed_login_attempts=0, lockout_until=None, otp_secret=otp_secret2, is_2fa_enabled=True)

    db.session.add_all([alice, bob])
    db.session.commit()

    posts = [
            Post(
                user_id=alice.id, 
                content='Hey Bob, did you hear about the cat intelligence project?'
            ),
            Post(
                user_id=bob.id, 
                content='Agent Alice! Keep it down! The topic is *highly* classified. But yes, the purr-fection levels are off the charts.'
            ),
            Post(
                user_id=alice.id, 
                content='Right, right. Code word "Whiskers". Anyway, Whiskers 7 is showing advanced object permanence related to tuna cans.'
            ),
            Post(
                user_id=bob.id,
                content='Incredible. Report back on the new feline overlord status. Over and out.'
            ),
        ]
    db.session.add_all(posts)
    db.session.commit()
    click.echo("Seed data added to the database.")

# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(twofa_bp)
