
import csv
import io

from flask import Blueprint, jsonify, render_template, Response, session

from database.db import fetch_all, fetch_one

report_bp = Blueprint("report", __name__)


@report_bp.route("/reports")
def reports_page():
    return render_template("reports.html")


@report_bp.route("/api/reports/summary")
def report_summary():
    total = fetch_one(
        "SELECT COUNT(*) AS count FROM detections WHERE user_id = ?",
        (session["user_id"],)
    )["count"]
    pending = fetch_one(
        "SELECT COUNT(*) AS count FROM detections "
        "WHERE user_id = ? AND status = 'Needs Review'",
        (session["user_id"],)
    )["count"]

    by_platform = fetch_all("""
        SELECT platform, COUNT(*) AS count
        FROM detections
        WHERE user_id = ?
        GROUP BY platform
        ORDER BY count DESC
    """, (session["user_id"],))

    by_risk = fetch_all("""
        SELECT risk_level, COUNT(*) AS count
        FROM detections
        WHERE user_id = ?
        GROUP BY risk_level
        ORDER BY count DESC
    """, (session["user_id"],))

    by_status = fetch_all("""
        SELECT status, COUNT(*) AS count
        FROM detections
        WHERE user_id = ?
        GROUP BY status
        ORDER BY count DESC
    """, (session["user_id"],))

    return jsonify({
        "total_detections": total,
        "needs_review": pending,
        "by_platform": by_platform,
        "by_risk": by_risk,
        "by_status": by_status
    })


@report_bp.route("/reports/export.csv")
def export_report_csv():
    rows = fetch_all("""
        SELECT id, target_name, platform, target_url,
               publisher, name_similarity, risk_score,
               risk_level, status, created_at
        FROM detections
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (session["user_id"],))

    output = io.StringIO()
    columns = [
        "id", "target_name", "platform", "target_url",
        "publisher", "name_similarity", "risk_score",
        "risk_level", "status", "created_at"
    ]

    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=digitalsentinel_report.csv"
        }
    )
