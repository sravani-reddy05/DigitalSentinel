
from flask import Blueprint, render_template, jsonify, session

from database.db import fetch_all, fetch_one

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    from database.models.brand_model import get_all_brands
    return render_template("dashboard.html", brands=get_all_brands())


@dashboard_bp.route("/api/dashboard/stats")
def dashboard_stats():
    total = fetch_one(
        "SELECT COUNT(*) AS count FROM detections WHERE user_id = ?",
        (session["user_id"],)
    )["count"]

    high_risk = fetch_one(
        "SELECT COUNT(*) AS count FROM detections "
        "WHERE user_id = ? AND risk_level IN ('High', 'Critical')",
        (session["user_id"],)
    )["count"]

    needs_review = fetch_one(
        "SELECT COUNT(*) AS count FROM detections "
        "WHERE user_id = ? AND status = 'Needs Review'",
        (session["user_id"],)
    )["count"]

    by_risk = fetch_all("""
        SELECT CASE WHEN risk_level = 'Critical' THEN 'High' ELSE risk_level END AS risk_level,
               COUNT(*) AS count
        FROM detections
        WHERE user_id = ?
        GROUP BY CASE WHEN risk_level = 'Critical' THEN 'High' ELSE risk_level END
    """, (session["user_id"],))
    risk_counts = {row["risk_level"]: row["count"] for row in by_risk}
    trend_rows = fetch_all("""
        SELECT date(created_at) AS day, COUNT(*) AS total,
               SUM(CASE WHEN risk_level IN ('High', 'Critical') THEN 1 ELSE 0 END) AS high,
               SUM(CASE WHEN risk_level = 'Medium' THEN 1 ELSE 0 END) AS medium,
               SUM(CASE WHEN risk_level = 'Low' THEN 1 ELSE 0 END) AS low
        FROM detections
        WHERE user_id = ? AND date(created_at) >= date('now', '-6 day')
        GROUP BY date(created_at)
        ORDER BY day
    """, (session["user_id"],))

    return jsonify({
        "total_detections": total,
        "high_risk": high_risk,
        "medium_risk": risk_counts.get("Medium", 0),
        "low_risk": risk_counts.get("Low", 0),
        "needs_review": needs_review,
        "risk_counts": risk_counts,
        "trend": trend_rows
    })


@dashboard_bp.route("/api/dashboard/recent")
def recent_detections():
    rows = fetch_all("""
        SELECT id, target_name, platform, target_url,
               risk_score, risk_level, status, created_at
        FROM detections
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    """, (session["user_id"],))

    return jsonify({"detections": rows})
