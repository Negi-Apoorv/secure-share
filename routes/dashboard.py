from flask import Blueprint, render_template, session, redirect
from functools import wraps

dashboard_bp = Blueprint("dashboard", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])