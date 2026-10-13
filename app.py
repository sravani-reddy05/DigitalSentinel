from dotenv import load_dotenv
load_dotenv(override=False)

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import secrets
import smtplib
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from config import Config
from database.db import initialize_database
from database.seed_data import seed_database
from database.models.user_model import (
    create_user,
    get_user_by_email,
    verify_user_password,
    set_password_reset_nonce,
    get_user_for_password_reset,
    update_user_password,
)

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
    public_paths = {
        "/login", "/signup", "/logout", "/health",
        "/forgot-password", "/reset-password",
    }
    if request.path.startswith("/static/"):
        return None
    if request.path.startswith("/language/"):
        return None
    if (
        request.path in public_paths
        or request.path.startswith("/reset-password/")
    ):
        return None
    if not session.get("user_id"):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Please sign in to access this resource."}), 401
        return redirect(url_for("login_page", next=request.full_path))


def _password_reset_serializer():
    return URLSafeTimedSerializer(app.secret_key, salt="digitalsentinel-password-reset")


def _send_password_reset_email(email, reset_url):
    if not all((Config.SMTP_HOST, Config.SMTP_FROM_EMAIL)):
        raise RuntimeError("SMTP_HOST and SMTP_FROM_EMAIL must be configured to send password reset emails.")

    message = EmailMessage()
    message["Subject"] = "Reset your DigitalSentinel password"
    message["From"] = Config.SMTP_FROM_EMAIL
    message["To"] = email
    message.set_content(
        "A password reset was requested for your DigitalSentinel account.\n\n"
        f"Use this link within one hour to choose a new password:\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=15) as smtp:
        if Config.SMTP_USE_TLS:
            smtp.starttls()
        if Config.SMTP_USERNAME:
            smtp.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        smtp.send_message(message)


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


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    status_message = None
    error_message = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        user = get_user_by_email(email)
        status_message = (
            "If an account uses that email address, reset instructions will be sent. "
            "If you do not receive an email, contact the administrator."
        )
        if user:
            nonce = secrets.token_urlsafe(24)
            set_password_reset_nonce(user["id"], nonce)
            token = _password_reset_serializer().dumps(
                {"user_id": user["id"], "nonce": nonce}
            )
            reset_url = url_for("reset_password", token=token, _external=True)
            try:
                _send_password_reset_email(user["email"], reset_url)
            except (OSError, smtplib.SMTPException, RuntimeError):
                app.logger.exception("Could not send password reset email")
        return render_template(
            "password_reset.html",
            reset_mode=False,
            status_message=status_message,
        )

    return render_template(
        "password_reset.html",
        reset_mode=False,
        status_message=status_message,
        error_message=error_message,
    )


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        token_data = _password_reset_serializer().loads(token, max_age=3600)
    except SignatureExpired:
        return render_template(
            "password_reset.html",
            reset_mode=True,
            token=token,
            error_message="This reset link has expired. Request a new one.",
        ), 400
    except BadSignature:
        return render_template(
            "password_reset.html",
            reset_mode=True,
            token=token,
            error_message="This reset link is invalid. Request a new one.",
        ), 400

    user = get_user_for_password_reset(
        token_data.get("user_id"), token_data.get("nonce")
    )
    if not user:
        return render_template(
            "password_reset.html",
            reset_mode=True,
            token=token,
            error_message="This reset link has already been used or is no longer valid.",
        ), 400

    if request.method == "POST":
        password = request.form.get("password") or ""
        confirmation = request.form.get("confirm_password") or ""
        if len(password) < 8:
            error_message = "Password must be at least 8 characters long."
        elif password != confirmation:
            error_message = "Passwords do not match."
        else:
            update_user_password(user["id"], password)
            return render_template(
                "login.html",
                auth_error=None,
                form_type="signin",
                auth_status="Password updated. Sign in with your new password.",
            )
    else:
        error_message = None

    return render_template(
        "password_reset.html",
        reset_mode=True,
        token=token,
        error_message=error_message,
    )


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
