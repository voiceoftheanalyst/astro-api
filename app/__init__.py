from flask import Flask
from flask_cors import CORS

# Create the Flask application instance
app = Flask(__name__)
CORS(app)

# Import routes after app is created to avoid circular imports
from app import api

# Register the routes
app.register_blueprint(api.bp)

# This makes the app variable available when importing from app
__all__ = ["app"]
