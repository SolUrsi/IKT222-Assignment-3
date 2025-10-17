from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import desc

from .models import db, Post, User
from .forms import MessageForm

main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.room'))
    return render_template("index.html")

@main_bp.route("/sneaky")
def sneaky():
    return render_template("sneaky.html")

@main_bp.route("/room", methods=["GET", "POST"])
@login_required
def room():
    form = MessageForm()

    if form.validate_on_submit():  
        newpost = Post(
            user_id=current_user.id,
            content=form.message.data,
        )
        db.session.add(newpost)
        db.session.commit()
    
        flash("Protocol Confirmed!", "success")
        return redirect(url_for('main.room'))
    
    posts = Post.query.options(db.joinedload(Post.author)).order_by(desc(Post.timestamp)).all()

    return render_template("room.html", posts=posts, form=form)

