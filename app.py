from flask import Flask, session, send_from_directory
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')

# ... rest of your code ...

# Add this route to serve static files if needed
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)
app = Flask(__name__)

# Basic configuration
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv("MAX_FILE_SIZE_MB", 10)) * 1024 * 1024

# Import routes after app creation
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.files import files_bp
from routes.share import share_bp
from routes.notifications import notifications_bp
from routes.archive import archive_bp  # ADD THIS LINE

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(files_bp)
app.register_blueprint(share_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(archive_bp)  # ADD THIS LINE

@app.route('/')
def index():
    if 'user_id' in session:
        return '<script>window.location.href = "/dashboard";</script>'
    return '<script>window.location.href = "/login";</script>'

if __name__ == '__main__':
    app.run(debug=True)