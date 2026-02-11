from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import db_cursor
import re

auth_bp = Blueprint("auth", __name__)

def normalize_username(username):
    """Normalize username for case-insensitive login"""
    return username.lower() if len(username) <= 4 else username[:4].lower() + username[4:]

def is_valid_password(password):
    """Basic password validation"""
    return (
        len(password) >= 6 and
        re.search(r"[A-Za-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[^A-Za-z0-9]", password)
    )

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        with db_cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username_normalized=%s",
                (normalize_username(username),)
            )
            user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")

        flash("Invalid login credentials")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm = request.form["confirm"]

        if not is_valid_password(password) or password != confirm:
            flash("Invalid credentials or passwords don't match")
            return redirect("/register")

        try:
            with db_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, username_normalized, password_hash) VALUES (%s, %s, %s)",
                    (username, normalize_username(username), generate_password_hash(password))
                )
                session["user_id"] = cursor.lastrowid
                session["username"] = username
            return redirect("/dashboard")
        except:
            flash("Username already exists")

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")