# routes/archive.py
from flask import Blueprint, render_template, session, redirect
from functools import wraps

archive_bp = Blueprint("archive", __name__)

def login_required_html(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@archive_bp.route("/archive")
@login_required_html
def archive_page():
    return render_template("archive.html", username=session["username"])