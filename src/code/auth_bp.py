from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
import datetime
from datetime import timedelta

from .models import db, User
from .app import bcrypt
from .forms import LoginForm, SignupForm

auth_bp = Blueprint('auth', __name__, url_prefix='/')

MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 5

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        # https://flask-bcrypt.readthedocs.io/en/1.0.1/, to hash passwords in python3 we need .decode("utf-8") 
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("[SYSTEM] Similar agent already exists. Choose another.", "error")
            return redirect(url_for("auth.signup"))
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("[SYSTEM] Agent created! Log in.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("signup.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and user.lockout_until and user.lockout_until > datetime.datetime.now(datetime.UTC):
            remaining = user.lockout_until - datetime.datetime.now(datetime.UTC)
            flash(f"[SYSTEM] WHISKER PROTOCOL VIOLATION.Agent locked. Try again in {remaining.seconds // 60} minutes and {remaining.seconds % 60} seconds.", "error")
            return render_template("login.html", form=form)
        
        # --- Check Credentials ---
        if user and bcrypt.check_password_hash(user.password, password):
            # --- Successful Login: Reset attempts and lockout ---
            user.failed_login_attempts = 0
            user.lockout_until = None
            db.session.commit()

            login_user(user)
            flash("[SYSTEM] Operation successful. Agent now active.", "success")
            return redirect(url_for("main.room"))
        else:
            # --- Failed Login Attempt ---
            if user:
                user.failed_login_attempts += 1

                # --- 2. Check for Lockout condition ---
                if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                    lockout_time = datetime.datetime.now(datetime.UTC) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                    user.lockout_until = lockout_time
                    user.failed_login_attempts = 0 # Reset count after lockout
                    flash(f"[SYSTEM] WHISKER PROTOCOL VIOLATION. Agent is locked for {LOCKOUT_DURATION_MINUTES} minutes.", "error")
                else:
                    flash(f"[SYSTEM] WHISKER PROTOCOL VIOLATION.Invalid agent credentials. You have {MAX_LOGIN_ATTEMPTS - user.failed_login_attempts} attempts left.", "error")
            else:
                # Security Best Practice: Don't give away whether the *username* exists.
                flash("[SYSTEM] WHISKER PROTOCOL VIOLATION.Invalid agent credentials.", "error")
            
            db.session.commit()

    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("[SYSTEM] Agent has closed comms.", "info")
    return redirect(url_for("main.home"))
