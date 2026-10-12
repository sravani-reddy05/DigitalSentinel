
from flask import Blueprint, request, jsonify, render_template, send_from_directory
from pathlib import Path
from uuid import uuid4
from PIL import Image, UnidentifiedImageError

from database.models.brand_model import (
    create_brand,
    get_brand,
    get_all_brands,
    set_brand_logo,
)
from database.models.routes.services.brand_url_analyzer import analyze_brand_url

brand_bp = Blueprint("brand", __name__)


@brand_bp.route("/brands")
def brands_page():
    return render_template("brand_profile.html")


@brand_bp.route("/api/brands", methods=["GET"])
def list_brands():
    return jsonify({"brands": get_all_brands()})


@brand_bp.route("/api/brands/current", methods=["GET"])
def current_brand():
    brand = get_brand()

    if not brand:
        return jsonify({"error": "No brand profile found"}), 404

    return jsonify({"brand": brand})


@brand_bp.route("/api/brands", methods=["POST"])
def add_brand():
    data = request.get_json(silent=True) or {}

    brand_name = str(data.get("brand_name", "")).strip()
    official_website = str(
        data.get("official_website", "")
    ).strip()
    description = str(data.get("description", "")).strip()

    if not brand_name:
        return jsonify({"error": "Brand name is required"}), 400

    if len(brand_name) > 120:
        return jsonify({"error": "Brand name is too long"}), 400

    if official_website:
        from database.models.routes.services.integrations.utils.validators import validate_http_url
        valid_url, message = validate_http_url(official_website)
        if not valid_url:
            return jsonify({"error": message}), 400

    try:
        brand_id = create_brand(
            brand_name=brand_name,
            official_website=official_website,
            description=description
        )
        return jsonify({
            "message": "Brand profile created",
            "brand_id": brand_id
        }), 201
    except Exception:
        return jsonify({
            "error": "Unable to create brand profile"
        }), 500


@brand_bp.route("/api/brands/<int:brand_id>/logo", methods=["POST"])
def upload_brand_logo(brand_id):
    from config import Config
    brand = get_brand(brand_id)
    if not brand:
        return jsonify({"error": "Brand not found"}), 404
    image = request.files.get("logo")
    if not image or not image.filename:
        return jsonify({"error": "Choose a logo image first"}), 400
    if Path(image.filename).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        return jsonify({"error": "Logo must be PNG, JPG, JPEG, or WEBP"}), 400
    try:
        image.stream.seek(0)
        with Image.open(image.stream) as opened:
            opened.verify()
        image.stream.seek(0)
    except (UnidentifiedImageError, OSError, ValueError):
        return jsonify({"error": "The selected file is not a valid image"}), 400

    folder = Path(Config.UPLOAD_FOLDER) / "brand_logos"
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{brand_id}_{uuid4().hex}{Path(image.filename).suffix.lower()}"
    image.save(folder / filename)
    relative_path = f"brand_logos/{filename}"
    if not set_brand_logo(brand_id, relative_path):
        (folder / filename).unlink(missing_ok=True)
        return jsonify({"error": "Could not save logo for this brand"}), 500
    return jsonify({"message": "Brand logo saved", "logo_url": f"/brand-logos/{filename}"}), 201


@brand_bp.route("/api/brands/analyze", methods=["POST"])
def analyze_brand_candidate():
    from config import Config
    from database.models.routes.services.integrations.utils.validators import validate_http_url
    from database.models.routes.services.logo_analyzer import compare_image_upload

    data = request.form
    brand_id = data.get("brand_id", type=int)
    brand = get_brand(brand_id=brand_id) if brand_id else None
    if not brand:
        return jsonify({"error": "Choose a registered brand to analyze"}), 400

    target_url = str(data.get("target_url", "")).strip()
    candidate_image = request.files.get("candidate_logo")
    has_candidate_image = bool(candidate_image and candidate_image.filename)
    if not target_url and not has_candidate_image:
        return jsonify({"error": "Enter a URL or upload a logo to analyze"}), 400

    url_analysis = None
    if target_url:
        valid_url, message = validate_http_url(target_url, required=True)
        if not valid_url:
            return jsonify({"error": message}), 400
        url_analysis = analyze_brand_url(
            target_url,
            brand["brand_name"],
            brand.get("official_website", ""),
        )

    image_comparison = None
    if has_candidate_image:
        if Path(candidate_image.filename).suffix.lower() not in {
            ".png", ".jpg", ".jpeg", ".webp"
        }:
            return jsonify({"error": "Logo must be PNG, JPG, JPEG, or WEBP"}), 400
        try:
            candidate_image.stream.seek(0)
            with Image.open(candidate_image.stream) as opened:
                opened.verify()
            candidate_image.stream.seek(0)
        except (UnidentifiedImageError, OSError, ValueError):
            return jsonify({"error": "The selected file is not a valid image"}), 400

        reference_path = (
            Path(Config.UPLOAD_FOLDER) / brand["logo_path"]
            if brand.get("logo_path")
            else None
        )
        if reference_path and reference_path.is_file():
            comparison = compare_image_upload(reference_path, candidate_image)
            if comparison.get("error"):
                return jsonify({"error": comparison["error"]}), 422
            image_comparison = {
                "status": "compared",
                "similarity": comparison["similarity"],
                "method": comparison["method"],
                "notice": comparison["notice"],
            }
        else:
            image_comparison = {
                "status": "reference_logo_missing",
                "similarity": None,
                "notice": "Upload an approved brand logo before comparing candidate logos.",
            }

    logo_risk = bool(
        image_comparison
        and image_comparison.get("similarity") is not None
        and image_comparison["similarity"] >= 70
    )
    has_risk = bool(
        (url_analysis and url_analysis["has_risk"]) or logo_risk
    )
    analysis_complete = not (
        image_comparison
        and image_comparison["status"] == "reference_logo_missing"
    )

    return jsonify({
        "brand_name": brand["brand_name"],
        "has_risk": has_risk,
        "analysis_complete": analysis_complete,
        "url_analysis": url_analysis,
        "image_comparison": image_comparison,
        "logo_risk_threshold": 70,
        "notice": (
            "A visual match or URL pattern is a review signal, not proof of impersonation."
        ),
    })


@brand_bp.route("/brand-logos/<filename>")
def serve_brand_logo(filename):
    from config import Config
    if not filename or Path(filename).name != filename:
        return jsonify({"error": "Logo not found"}), 404
    return send_from_directory(Path(Config.UPLOAD_FOLDER) / "brand_logos", filename)
