from flask import Flask, render_template

app = Flask(__name__)
# --  Hot reload of HTML
app.config.update(TEMPLATES_AUTO_RELOAD=True)

# Public Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("")

@app.route("/login")
def login():
    return render_template("")

# Private Routes
# -- Requires authentication to view and interact with

@app.route("/room")
def room():
    return render_template("room.html")

# -- Authentication