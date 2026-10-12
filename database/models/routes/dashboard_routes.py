
from flask import Blueprint, render_template, jsonify

from database.db import fetch_all, fetch_one

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    from database.models.brand_model import get_all_brands
    return render_template("dashboard.html", brands=get_all_brands())


@dashboard_bp.route("/api/dashboard/stats")
def dashboard_stats():
    total = fetch_one(
        "SELECT COUNT(*) AS count FROM detections"
    )["count"]

    high_risk = fetch_one(
        "SELECT COUNT(*) AS count FROM detections "
        "WHERE risk_level = 'High'"
    )["count"]

    needs_review = fetch_one(
        "SELECT COUNT(*) AS count FROM detections "
        "WHERE status = 'Needs Review'"
    )["count"]

    return jsonify({
        "total_detections": total,
        "high_risk": high_risk,
        "needs_review": needs_review
    })


@dashboard_bp.route("/api/dashboard/recent")
def recent_detections():
    rows = fetch_all("""
        SELECT id, target_name, platform, target_url,
               risk_score, risk_level, status, created_at
        FROM detections
        ORDER BY created_at DESC
        LIMIT 10
    """)

    return jsonify({"detections": rows})
