
from flask import Blueprint, request, jsonify, render_template

from database.models.detection_model import (
    get_all_detections,
    get_detection_by_id,
    delete_detection,
    update_detection_status
)

detection_bp = Blueprint("detection", __name__)

ALLOWED_STATUSES = {
    "Needs Review",
    "Under Investigation",
    "Confirmed Threat",
    "False Positive",
    "Resolved"
}


@detection_bp.route("/detections")
def detections_page():
    return render_template("detections.html")


@detection_bp.route("/detection/<int:detection_id>")
def detection_details_page(detection_id):
    detection = get_detection_by_id(detection_id)

    if not detection:
        return render_template("404.html"), 404

    return render_template(
        "detection_details.html",
        detection=detection
    )


@detection_bp.route("/api/detections", methods=["GET"])
def list_detections():
    platform = request.args.get("platform")
    status = request.args.get("status")

    detections = get_all_detections(
        platform=platform or None,
        status=status or None
    )

    return jsonify({"detections": detections})


@detection_bp.route(
    "/api/detections/<int:detection_id>",
    methods=["GET"]
)
def detection_details(detection_id):
    detection = get_detection_by_id(detection_id)

    if not detection:
        return jsonify({"error": "Detection not found"}), 404

    return jsonify({"detection": detection})


@detection_bp.route(
    "/api/detections/<int:detection_id>",
    methods=["DELETE"]
)
def remove_detection(detection_id):
    if not get_detection_by_id(detection_id):
        return jsonify({"error": "Detection not found"}), 404

    if not delete_detection(detection_id):
        return jsonify({"error": "Could not delete detection"}), 500

    return jsonify({
        "message": "Detection deleted",
        "detection_id": detection_id
    })


@detection_bp.route(
    "/api/detections/<int:detection_id>/status",
    methods=["PATCH"]
)
def change_detection_status(detection_id):
    data = request.get_json(silent=True) or {}
    new_status = str(data.get("status", "")).strip()

    if new_status not in ALLOWED_STATUSES:
        return jsonify({
            "error": "Invalid status",
            "allowed_statuses": sorted(ALLOWED_STATUSES)
        }), 400

    detection = get_detection_by_id(detection_id)
    if not detection:
        return jsonify({"error": "Detection not found"}), 404

    updated = update_detection_status(detection_id, new_status)

    if not updated:
        return jsonify({
            "error": "Could not update detection status"
        }), 500

    return jsonify({
        "message": "Detection status updated",
        "detection_id": detection_id,
        "status": new_status
    })
