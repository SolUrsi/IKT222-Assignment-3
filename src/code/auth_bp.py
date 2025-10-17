from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required

from .models import db, User
from .app import bcrypt
from .forms import LoginForm, SignupForm

auth_bp = Blueprint('auth', __name__, url_prefix='/')

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
            flash("Username or email already exists. Please choose another.", "error")
            return redirect(url_for("auth.signup"))
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("signup.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.room"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
