
from flask import Blueprint, request, jsonify, render_template
from pathlib import Path
from PIL import Image, UnidentifiedImageError

from database.models.brand_model import get_brand
from database.models.detection_model import create_detection
from database.models.routes.services.username_analyzer import analyze_username
from database.models.routes.services.risk_engine import calculate_risk, apply_reputation
from database.models.routes.services.integrations.url_reputation import check_url_reputation
from database.models.routes.services.logo_analyzer import compare_image_upload
from config import Config

app_store_bp = Blueprint("app_store", __name__)


@app_store_bp.route("/app-monitor")
def app_monitor_page():
    from database.models.brand_model import get_all_brands
    brand_id = request.args.get("brand_id", type=int)
    return render_template("app_monitor.html", brands=get_all_brands(), selected_brand_id=brand_id)


@app_store_bp.route("/api/apps/scan", methods=["POST"])
def scan_app_listing():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    candidate_image = request.files.get("app_icon")

    app_name = str(data.get("app_name", "")).strip()
    publisher = str(data.get("publisher", "")).strip()
    app_url = str(data.get("app_url", "")).strip()
    description = str(data.get("description", "")).strip()
    platform = str(data.get("platform", "Google Play")).strip()

    if not app_name:
        return jsonify({"error": "App name is required"}), 400

    if app_url:
        from database.models.routes.services.integrations.utils.validators import validate_http_url
        valid_url, message = validate_http_url(app_url)
        if not valid_url:
            return jsonify({"error": message}), 400

    if len(app_name) > 200 or len(publisher) > 200:
        return jsonify({"error": "Input is too long"}), 400

    if len(description) > 2000:
        return jsonify({"error": "Description is too long"}), 400

    if platform not in {"Google Play", "Apple App Store", "Other"}:
        return jsonify({"error": "Unsupported app store"}), 400

    brand_id = data.get("brand_id")
    brand = get_brand(brand_id=int(brand_id)) if str(brand_id or "").isdigit() else get_brand()
    if not brand:
        return jsonify({
            "error": "Create a brand profile before scanning"
        }), 400

    analysis = analyze_username(app_name, brand["brand_name"])

    visual_similarity = 0
    if candidate_image and candidate_image.filename and brand.get("logo_path"):
        if Path(candidate_image.filename).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            return jsonify({"error": "App icon must be PNG, JPG, JPEG, or WEBP"}), 400
        try:
            candidate_image.stream.seek(0)
            with Image.open(candidate_image.stream) as image:
                image.verify()
            candidate_image.stream.seek(0)
            visual_similarity = compare_image_upload(Path(Config.UPLOAD_FOLDER) / brand["logo_path"], candidate_image).get("similarity", 0)
        except (UnidentifiedImageError, OSError, ValueError):
            return jsonify({"error": "App icon must be a valid PNG, JPG, JPEG, or WEBP image"}), 400

    risk = calculate_risk(
        name_similarity=analysis["similarity"],
        description=description, logo_similarity=visual_similarity,
        is_official=False
    )
    risk["reasons"] = list(dict.fromkeys(analysis.get("reasons", []) + risk["reasons"]))

    reputation = check_url_reputation(app_url) if app_url else None
    risk = apply_reputation(risk, reputation)
    if visual_similarity >= 70:
        risk["reasons"].append(f"Submitted app icon is visually similar to the saved brand logo ({visual_similarity:.0f}%)")

    detection_id = create_detection(
        brand_id=brand["id"],
        target_name=app_name,
        platform=platform,
        target_url=app_url,
        publisher=publisher,
        description=description,
        name_similarity=analysis["similarity"],
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        reasons=risk["reasons"],
        is_official=False
    )

    return jsonify({
        "message": "App listing indicators analyzed",
        "detection_id": detection_id,
        "analysis": analysis,
        "brand_name": brand["brand_name"],
        "visual_similarity": visual_similarity if candidate_image else None,
        "url_reputation": reputation,
        "risk": risk,
        "notice": (
            "App name and publisher information were analyzed as entered; the listing itself was not fetched. URL reputation checks use configured providers only."
        )
    }), 201
