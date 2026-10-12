from dotenv import load_dotenv
load_dotenv(override=False)

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os

from config import Config
from database.db import initialize_database
from database.seed_data import seed_database

from database.models.routes.dashboard_routes import dashboard_bp
from database.models.routes.brand_routes import brand_bp
from database.models.routes.social_routes import social_bp
from database.models.routes.app_store_routes import app_store_bp
from database.models.routes.detection_routes import detection_bp
from database.models.routes.report_routes import report_bp
from database.models.routes.assistant_routes import assistant_bp


# Create Flask application
app = Flask(__name__, template_folder="uploads/templates", static_folder="uploads/templates")
app.add_url_rule("/static/<path:filename>", endpoint="project_static", view_func=app.send_static_file)

# Load application configuration
app.config.from_object(Config)


@app.context_processor
def template_settings():
    return {
        "current_language": session.get("language", "en"),
    }


# Initialize database
with app.app_context():
    initialize_database()
    if Config.SEED_DEMO_DATA:
        seed_database()


# Register application routes
app.register_blueprint(dashboard_bp)
app.register_blueprint(brand_bp)
app.register_blueprint(social_bp)
app.register_blueprint(app_store_bp)
app.register_blueprint(detection_bp)
app.register_blueprint(report_bp)
app.register_blueprint(assistant_bp)


# Home page
@app.route("/")
def home():
    from database.models.brand_model import get_all_brands
    return render_template("dashboard.html", brands=get_all_brands())


@app.route("/architecture")
def architecture_page():
    return render_template("architecture.html")


@app.route("/settings")
def settings_page():
    return render_template("settings.html")


@app.route("/language/<language>")
def set_language(language):
    if language not in {"en", "hi", "es", "fr", "de", "te"}:
        language = "en"
    session["language"] = language
    next_path = request.referrer or url_for("home")
    if not next_path.startswith(request.host_url):
        next_path = url_for("home")
    return redirect(next_path)


# Health check
@app.route("/health")
def health():
    return jsonify({
        "status": "success",
        "application": "DigitalSentinel",
        "message": "Application is running"
    })


# Handle missing pages
@app.errorhandler(404)
def page_not_found(error):

    if request.path.startswith("/api/"):
        return jsonify({
            "error": "API endpoint not found"
        }), 404

    return render_template("404.html"), 404


# Handle unexpected errors
@app.errorhandler(500)
def internal_server_error(error):

    app.logger.exception("An unexpected server error occurred")

    if request.path.startswith("/api/"):
        return jsonify({
            "error": "An internal server error occurred"
        }), 500

    return (
        "An internal server error occurred. Please try again later.",
        500
    )


# Run application locally
if __name__ == "__main__":

    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        host="127.0.0.1",
        port=int(os.getenv("PORT", 5000))
    )
