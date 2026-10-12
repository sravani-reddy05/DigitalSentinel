import json

from database.db import get_connection


def create_detection(
    brand_id,
    target_name,
    platform,
    target_url="",
    publisher="",
    description="",
    name_similarity=0,
    risk_score=0,
    risk_level="Low",
    reasons=None,
    status="Needs Review",
    is_official=False
):
    """Save a detection result."""

    if not target_name or not target_name.strip():
        raise ValueError("Target name is required.")

    if not 0 <= risk_score <= 100:
        raise ValueError("Risk score must be between 0 and 100.")

    reasons_json = json.dumps(reasons or [])

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO detections (
                brand_id,
                target_name,
                platform,
                target_url,
                publisher,
                description,
                name_similarity,
                risk_score,
                risk_level,
                reasons,
                status,
                is_official
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            brand_id,
            target_name.strip(),
            platform,
            target_url,
            publisher,
            description,
            name_similarity,
            risk_score,
            risk_level,
            reasons_json,
            status,
            int(is_official)
        ))

        detection_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO scan_history (
                brand_id,
                scan_type,
                target_name,
                risk_score,
                result_status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            brand_id,
            platform,
            target_name.strip(),
            risk_score,
            "Official" if is_official else risk_level
        ))

        connection.commit()

        return detection_id

    finally:
        connection.close()


def get_all_detections(
    brand_id=None,
    platform=None,
    status=None
):
    """Retrieve detections with optional filters."""

    query = """
        SELECT
            d.*,
            b.brand_name
        FROM detections AS d
        JOIN brand_profiles AS b
            ON d.brand_id = b.id
        WHERE 1 = 1
    """

    parameters = []

    if brand_id is not None:
        query += " AND d.brand_id = ?"
        parameters.append(brand_id)

    if platform:
        query += " AND d.platform = ?"
        parameters.append(platform)

    if status:
        query += " AND d.status = ?"
        parameters.append(status)

    query += " ORDER BY d.id DESC"

    connection = get_connection()

    try:
        cursor = connection.execute(
            query,
            parameters
        )

        results = []

        for row in cursor.fetchall():

            item = dict(row)
            item["risk_level"] = "High" if item.get("risk_level") == "Critical" else item.get("risk_level")

            try:
                item["reasons"] = json.loads(
                    item.get("reasons") or "[]"
                )
            except (ValueError, TypeError):
                item["reasons"] = []

            results.append(item)

        return results

    finally:
        connection.close()


def get_detection_by_id(detection_id):
    """Retrieve one detection by its ID."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                d.*,
                b.brand_name
            FROM detections AS d
            JOIN brand_profiles AS b
                ON d.brand_id = b.id
            WHERE d.id = ?
        """, (detection_id,))

        row = cursor.fetchone()

        if not row:
            return None

        item = dict(row)
        item["risk_level"] = "High" if item.get("risk_level") == "Critical" else item.get("risk_level")

        try:
            item["reasons"] = json.loads(
                item.get("reasons") or "[]"
            )
        except (ValueError, TypeError):
            item["reasons"] = []

        return item

    finally:
        connection.close()


def update_detection_status(
    detection_id,
    new_status
):
    """Update the investigation status."""

    allowed_statuses = {
        "Needs Review",
        "Under Investigation",
        "Confirmed Threat",
        "False Positive",
        "Resolved"
    }

    if new_status not in allowed_statuses:
        raise ValueError("Invalid detection status.")

    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE detections
            SET status = ?
            WHERE id = ?
        """, (
            new_status,
            detection_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def delete_detection(detection_id):
    """Delete a detection record."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
            DELETE FROM detections
            WHERE id = ?
        """, (detection_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()
