from dotenv import load_dotenv
load_dotenv(override=False)

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os

from config import Config
from database.db import initialize_database
from database.seed_data import seed_database
from database.models.user_model import create_user, get_user_by_email, verify_user_password

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
app.secret_key = Config.SECRET_KEY


@app.context_processor
def template_settings():
    user_email = session.get("user_email")
    user = get_user_by_email(user_email) if user_email else None
    return {
        "current_language": session.get("language", "en"),
        "current_user": user,
    }


@app.before_request
def require_login():
    public_paths = {"/login", "/signup", "/logout", "/health", "/architecture"}
    if request.path.startswith("/static/"):
        return None
    if request.path.startswith("/api/") and request.path != "/api/assistant/chat":
        return None
    if request.path.startswith("/language/"):
        return None
    if request.path in public_paths or request.path.startswith("/login") or request.path.startswith("/signup"):
        return None
    if request.path == "/" and not session.get("user_id"):
        return redirect(url_for("login_page"))


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


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = verify_user_password(email, password)
        if user is None:
            return render_template("login.html", auth_error="Invalid email or password. Please try again.", form_type="signin")

        session.clear()
        session["user_id"] = user["id"]
        session["user_email"] = user["email"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["language"] = session.get("language", "en")
        return redirect(url_for("home"))

    return render_template("login.html", auth_error=None, form_type="signin")


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""
        provider = (request.form.get("provider") or "email").strip().lower()

        if provider == "google" and not email:
            return render_template("login.html", auth_error="Please enter your Google email address.", form_type="signup")

        if not username and provider == "email":
            return render_template("login.html", auth_error="Please enter your full name.", form_type="signup")
        if not email:
            return render_template("login.html", auth_error="Please enter your email address.", form_type="signup")
        if not password:
            return render_template("login.html", auth_error="Please set a password.", form_type="signup")
        if password != confirm_password and provider == "email":
            return render_template("login.html", auth_error="Passwords do not match.", form_type="signup")
        if len(password) < 8:
            return render_template("login.html", auth_error="Password must be at least 8 characters long.", form_type="signup")

        if not username:
            username = email.split("@", 1)[0]

        try:
            create_user(username, email, password, role="analyst")
        except ValueError as exc:
            return render_template("login.html", auth_error=str(exc), form_type="signup")

        user = verify_user_password(email, password)
        if user is None:
            return render_template("login.html", auth_error="Account created, but sign in was not successful. Please log in manually.", form_type="signin")

        session.clear()
        session["user_id"] = user["id"]
        session["user_email"] = user["email"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["language"] = session.get("language", "en")
        return redirect(url_for("home"))

    return render_template("login.html", auth_error=None, form_type="signup")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# Home page
@app.route("/")
def home():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
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
    if language not in {"en", "hi", "te"}:
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
