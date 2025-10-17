from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

from auth_bp import auth_bp
from main_bp import main_bp
from models import db, User

app = Flask(__name__)
# Configs

# --  Hot reload of HTML
app.config.update(TEMPLATES_AUTO_RELOAD=True)

# -- Secret key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devkey')

# -- Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions

# -- Database and ORM from models.py
db.init_app(app)

# -- Bcrypt for password hashing
bcrypt = Bcrypt(app)

# -- Login manager for user sessions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.sneaky'

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)


