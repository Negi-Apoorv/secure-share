# routes/share.py
from flask import Blueprint, request, jsonify, session, render_template, redirect
from functools import wraps
from db import db_cursor

share_bp = Blueprint("share", __name__)

def login_required_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@share_bp.route("/share")
def share_page():
    if "user_id" not in session:
        return redirect("/login")
    
    # Get file ID from query parameter
    file_id = request.args.get("file", type=int)
    
    # If file_id is provided, get file info
    file_info = None
    if file_id:
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT id, original_filename FROM files WHERE id=%s AND owner_id=%s AND is_archived=FALSE",
                (file_id, session["user_id"])
            )
            file_info = cursor.fetchone()
    
    # Get list of user's files for dropdown (for general share)
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT id, original_filename FROM files WHERE owner_id=%s AND is_archived=FALSE ORDER BY uploaded_at DESC",
            (session["user_id"],)
        )
        user_files = cursor.fetchall()
    
    return render_template(
        "share.html", 
        username=session["username"],
        file_info=file_info,
        user_files=user_files
    )
@share_bp.route("/api/share", methods=["POST"])
@login_required_json
def share():
    data = request.json
    file_id = data.get("file_id")
    username = data.get("username")

    if not file_id or not username:
        return jsonify({"error": "Missing fields"}), 400

    with db_cursor() as cursor:
        # Find target user
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        target = cursor.fetchone()
        if not target:
            return jsonify({"error": "User not found"}), 404

        # Verify ownership
        cursor.execute(
            "SELECT 1 FROM files WHERE id=%s AND owner_id=%s",
            (file_id, session["user_id"])
        )
        if not cursor.fetchone():
            return jsonify({"error": "You can only share your own files"}), 403

        # Create share
        cursor.execute(
            "INSERT INTO file_shares (file_id, shared_with_user_id) VALUES (%s, %s)",
            (file_id, target["id"])
        )

    return jsonify({"message": "File shared"})