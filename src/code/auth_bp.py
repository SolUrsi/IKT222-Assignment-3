from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required

from code.models import db, User
from code.app import bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/')

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        # https://flask-bcrypt.readthedocs.io/en/1.0.1/, to hash passwords in python3 we need .decode("utf-8")
        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8")
        email = request.form.get("email")
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.room"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
