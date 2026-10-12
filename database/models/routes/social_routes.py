
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

SUSPICIOUS_DESCRIPTION_PHRASES = (
    "free", "giveaway", "claim prize", "limited offer", "verify account",
    "send password", "enter otp", "verify account", "claim prize",
    "payment required", "free giveaway", "official support", "contact support",
    "click the link", "urgent action", "account suspended",
)


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
    description_signals = list(dict.fromkeys(phrase for phrase in SUSPICIOUS_DESCRIPTION_PHRASES if phrase in description.lower()))

    visual_similarity = None
    image_comparison = {"status": "not_uploaded", "similarity": None}
    if candidate_image and candidate_image.filename:
        if Path(candidate_image.filename).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            return jsonify({"error": "Profile image must be PNG, JPG, JPEG, or WEBP"}), 400
        try:
            candidate_image.stream.seek(0)
            with Image.open(candidate_image.stream) as image:
                image.verify()
            candidate_image.stream.seek(0)
            if brand.get("logo_path"):
                comparison = compare_image_upload(Path(Config.UPLOAD_FOLDER) / brand["logo_path"], candidate_image)
                visual_similarity = comparison.get("similarity", 0) if not comparison.get("error") else None
                image_comparison = {"status": "compared" if visual_similarity is not None else "comparison_failed", "similarity": visual_similarity,
                                    "method": comparison.get("method"),
                                    "notice": comparison.get("notice") or comparison.get("error")}
            else:
                image_comparison = {"status": "reference_logo_missing", "similarity": None,
                                    "notice": "Upload an approved brand logo to compare profile images."}
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
    if visual_similarity is not None and visual_similarity >= 70:
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
        "visual_similarity": visual_similarity,
        "image_comparison": image_comparison,
        "assessment": {
            "username": analysis,
            "description_phrases": description_signals,
            "ownership": {"status": "unverified", "message": "Account ownership cannot be confirmed from manually submitted profile details."},
        },
        "url_reputation": reputation,
        "risk": risk,
        "notice": (
            "Profile details are analyzed as submitted; the platform profile itself is not fetched. URL reputation checks use configured providers only."
        )
    }), 201
