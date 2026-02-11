from flask import Blueprint, jsonify, session
from db import db_cursor

notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.route("/api/notifications")
def notifications():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 10",
            (session["user_id"],)
        )
        return jsonify(cursor.fetchall())