from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route("/")
def home():
    return render_template("index.html")

@main_bp.route("/sneaky")
def sneaky():
    return render_template("sneaky.html")

@main_bp.route("/room")
@login_required
def room():
    return render_template("room.html")

