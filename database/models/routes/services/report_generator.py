
import csv
import io

from database.db import fetch_all


def generate_detection_csv(brand_id=None):
    query = """
        SELECT id, target_name, platform, target_url,
               publisher, name_similarity, risk_score,
               risk_level, status, created_at
        FROM detections
    """

    parameters = ()

    if brand_id is not None:
        query += " WHERE brand_id = ?"
        parameters = (brand_id,)

    query += " ORDER BY created_at DESC"

    rows = fetch_all(query, parameters)

    output = io.StringIO()
    columns = [
        "id",
        "target_name",
        "platform",
        "target_url",
        "publisher",
        "name_similarity",
        "risk_score",
        "risk_level",
        "status",
        "created_at"
    ]

    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

    return output.getvalue()


def generate_report_summary(brand_id=None):
    query = """
        SELECT risk_level, COUNT(*) AS count
        FROM detections
    """

    parameters = ()

    if brand_id is not None:
        query += " WHERE brand_id = ?"
        parameters = (brand_id,)

    query += " GROUP BY risk_level ORDER BY count DESC"

    risk_summary = fetch_all(query, parameters)

    return {
        "risk_summary": risk_summary,
        "total_detections": sum(
            row["count"] for row in risk_summary
        )
    }
