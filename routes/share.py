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
    
    # Get list of user's files for dropdown (latest 5)
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT id, original_filename, uploaded_at 
               FROM files 
               WHERE owner_id=%s AND is_archived=FALSE 
               ORDER BY uploaded_at DESC 
               LIMIT 5""",
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
    expiry_days = data.get("expiry_days")  # Optional expiry

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

        # Check if already shared
        cursor.execute(
            "SELECT 1 FROM file_shares WHERE file_id=%s AND shared_with_user_id=%s",
            (file_id, target["id"])
        )
        if cursor.fetchone():
            return jsonify({"error": "File already shared with this user"}), 400

        # Create share
        cursor.execute(
            "INSERT INTO file_shares (file_id, shared_with_user_id) VALUES (%s, %s)",
            (file_id, target["id"])
        )
        
        # Create notification for the user
        cursor.execute(
            """INSERT INTO notifications (user_id, message) 
               VALUES (%s, %s)""",
            (target["id"], f"{session['username']} shared a file with you: {file_id}")
        )

    return jsonify({"message": "File shared successfully"})

@share_bp.route("/api/users/suggest")
@login_required_json
def suggest_users():
    """Get users that the current user has shared with before (for autocomplete)"""
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])
    
    with db_cursor() as cursor:
        # Get users that have been shared with before (distinct)
        cursor.execute("""
            SELECT DISTINCT u.username 
            FROM users u
            JOIN file_shares fs ON u.id = fs.shared_with_user_id
            WHERE fs.file_id IN (
                SELECT id FROM files WHERE owner_id = %s
            )
            AND u.username LIKE %s
            LIMIT 5
        """, (session["user_id"], f"%{query}%"))
        
        return jsonify([user["username"] for user in cursor.fetchall()])

@share_bp.route("/api/shares/recent")
@login_required_json
def recent_shares():
    """Get recent shares made BY the current user"""
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                f.original_filename,
                u.username as shared_with,
                fs.shared_at,
                f.id as file_id
            FROM file_shares fs
            JOIN files f ON fs.file_id = f.id
            JOIN users u ON fs.shared_with_user_id = u.id
            WHERE f.owner_id = %s
            ORDER BY fs.shared_at DESC
            LIMIT 10
        """, (session["user_id"],))
        
        return jsonify(cursor.fetchall())

@share_bp.route("/api/shares/with-me")
@login_required_json
def shares_with_me():
    """Get files shared WITH the current user"""
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                f.original_filename,
                u.username as shared_by,
                fs.shared_at,
                f.id as file_id
            FROM file_shares fs
            JOIN files f ON fs.file_id = f.id
            JOIN users u ON f.owner_id = u.id
            WHERE fs.shared_with_user_id = %s
            ORDER BY fs.shared_at DESC
            LIMIT 10
        """, (session["user_id"],))
        
        return jsonify(cursor.fetchall())