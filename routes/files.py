from flask import Blueprint, request, jsonify, session, send_file
from werkzeug.utils import secure_filename
from functools import wraps
import os, uuid, io
from db import db_cursor
from crypto_utils import encrypt_bytes, decrypt_bytes

files_bp = Blueprint("files", __name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/encrypted")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def login_required_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@files_bp.route("/upload", methods=["POST"])
@login_required_json
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Invalid file"}), 400

    try:
        # Debug: Check if file is received
        print(f"Uploading file: {file.filename}, size: {len(file.read())}")
        file.seek(0)  # Reset file pointer
        
        # Encrypt and save file
        encrypted = encrypt_bytes(file.read())
        stored_filename = f"{uuid.uuid4().hex}.bin"
        file_path = os.path.join(UPLOAD_DIR, stored_filename)
        
        # Debug: Check UPLOAD_DIR
        print(f"Upload directory: {UPLOAD_DIR}")
        print(f"Full path: {file_path}")
        
        with open(file_path, "wb") as f:
            f.write(encrypted)

        # Save to database
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO files (owner_id, original_filename, stored_filename) VALUES (%s, %s, %s)",
                (session["user_id"], secure_filename(file.filename), stored_filename)
            )

        return jsonify({"message": "Uploaded"})
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@files_bp.route("/api/files/my")
@login_required_json
def my_files():
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT id, original_filename, uploaded_at FROM files WHERE owner_id=%s AND is_archived=FALSE",
            (session["user_id"],)
        )
        return jsonify(cursor.fetchall())

@files_bp.route("/file/download/<int:file_id>")
@login_required_json
def download(file_id):
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT stored_filename, original_filename FROM files WHERE id=%s AND owner_id=%s",
            (file_id, session["user_id"])
        )
        file = cursor.fetchone()

    if not file:
        return "Access denied", 403

    # Decrypt and send file
    encrypted_path = os.path.join(UPLOAD_DIR, file["stored_filename"])
    with open(encrypted_path, "rb") as f:
        decrypted = decrypt_bytes(f.read())

    return send_file(
        io.BytesIO(decrypted),
        as_attachment=True,
        download_name=file["original_filename"]
    )

@files_bp.route("/api/files/shared")
@login_required_json
def shared_files():
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT f.id, f.original_filename, f.uploaded_at, u.username as owner
               FROM files f
               JOIN file_shares s ON f.id = s.file_id
               JOIN users u ON f.owner_id = u.id
               WHERE s.shared_with_user_id = %s""",
            (session["user_id"],)
        )
        return jsonify(cursor.fetchall())
    
@files_bp.route("/file/archive", methods=["POST"])
@login_required_json
def archive_file():
    data = request.json
    file_id = data.get("file_id")
    
    if not file_id:
        return jsonify({"error": "File ID required"}), 400
    
    try:
        with db_cursor() as cursor:
            # Verify ownership and archive
            cursor.execute(
                "UPDATE files SET is_archived=TRUE WHERE id=%s AND owner_id=%s",
                (file_id, session["user_id"])
            )
            
            if cursor.rowcount == 0:
                return jsonify({"error": "File not found or access denied"}), 404
            
        return jsonify({"message": "File archived"})
    
    except Exception as e:
        print(f"Archive error: {str(e)}")
        return jsonify({"error": f"Archive failed: {str(e)}"}), 500