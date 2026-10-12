
from flask import Blueprint, request, jsonify, render_template
from pathlib import Path

from database.models.brand_model import get_brand
from database.models.detection_model import create_detection
from database.models.routes.services.username_analyzer import analyze_username
from database.models.routes.services.risk_engine import calculate_risk, apply_reputation
from database.models.routes.services.integrations.url_reputation import check_url_reputation
from database.models.routes.services.logo_analyzer import compare_image_upload
from config import Config
from PIL import Image, UnidentifiedImageError

social_bp = Blueprint("social", __name__)


@social_bp.route("/social-monitor")
def social_page():
    from database.models.brand_model import get_all_brands
    brand_id = request.args.get("brand_id", type=int)
    return render_template("social_monitor.html", brands=get_all_brands(), selected_brand_id=brand_id)


@social_bp.route("/api/social/scan", methods=["POST"])
def scan_social_profile():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    candidate_image = request.files.get("profile_image")

    target_name = str(data.get("username", "")).strip()
    target_url = str(data.get("profile_url", "")).strip()
    description = str(data.get("description", "")).strip()
    platform = str(data.get("platform", "Instagram")).strip()

    if not target_name:
        return jsonify({"error": "Username is required"}), 400

    if target_url:
        from database.models.routes.services.integrations.utils.validators import validate_http_url
        valid_url, message = validate_http_url(target_url)
        if not valid_url:
            return jsonify({"error": message}), 400

    if len(target_name) > 200 or len(description) > 2000:
        return jsonify({"error": "Input is too long"}), 400

    allowed_platforms = {
        "Instagram", "Facebook", "X", "TikTok", "Other"
    }
    if platform not in allowed_platforms:
        return jsonify({"error": "Unsupported platform"}), 400

    brand_id = data.get("brand_id")
    brand = get_brand(brand_id=int(brand_id)) if str(brand_id or "").isdigit() else get_brand()
    if not brand:
        return jsonify({
            "error": "Create a brand profile before scanning"
        }), 400

    analysis = analyze_username(
        target_name,
        brand["brand_name"]
    )

    visual_similarity = 0
    image_notice = None
    if candidate_image and candidate_image.filename and brand.get("logo_path"):
        if Path(candidate_image.filename).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            return jsonify({"error": "Profile image must be PNG, JPG, JPEG, or WEBP"}), 400
        try:
            candidate_image.stream.seek(0)
            with Image.open(candidate_image.stream) as image:
                image.verify()
            candidate_image.stream.seek(0)
            comparison = compare_image_upload(Path(Config.UPLOAD_FOLDER) / brand["logo_path"], candidate_image)
            visual_similarity = comparison.get("similarity", 0)
            image_notice = comparison.get("notice") or comparison.get("error")
        except (UnidentifiedImageError, OSError, ValueError):
            return jsonify({"error": "Profile image must be a valid PNG, JPG, JPEG, or WEBP image"}), 400

    risk = calculate_risk(
        name_similarity=analysis["similarity"],
        description=description, logo_similarity=visual_similarity,
        is_official=False
    )
    risk["reasons"] = list(dict.fromkeys(analysis.get("reasons", []) + risk["reasons"]))
    containment_points = 15 if analysis.get("contains_brand") else 0
    keyword_points = min(15, len(analysis.get("suspicious_keywords", [])) * 5)
    risk["risk_score"] = min(100, risk["risk_score"] + containment_points + keyword_points)
    if containment_points:
        risk["reasons"].append("Brand name match contributed 15 review points")
    if keyword_points:
        risk["reasons"].append(f"Promotional username terms contributed {keyword_points} review points")
    risk["risk_level"] = "High" if risk["risk_score"] >= 60 else "Medium" if risk["risk_score"] >= 35 else "Low"

    reputation = check_url_reputation(target_url) if target_url else None
    risk = apply_reputation(risk, reputation)
    if visual_similarity >= 70:
        risk["reasons"].append(f"Submitted profile image is visually similar to the saved brand logo ({visual_similarity:.0f}%)")

    detection_id = create_detection(
        brand_id=brand["id"],
        target_name=target_name,
        platform=platform,
        target_url=target_url,
        description=description,
        name_similarity=analysis["similarity"],
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        reasons=risk["reasons"],
        is_official=False
    )

    return jsonify({
        "message": "Profile indicators analyzed",
        "detection_id": detection_id,
        "analysis": analysis,
        "brand_name": brand["brand_name"],
        "visual_similarity": visual_similarity if candidate_image else None,
        "url_reputation": reputation,
        "risk": risk,
        "notice": (
            "Profile details are analyzed as submitted; the platform profile itself is not fetched. URL reputation checks use configured providers only."
        )
    }), 201
