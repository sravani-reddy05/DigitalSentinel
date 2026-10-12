
from database.models.routes.services.username_analyzer import analyze_username
from database.models.routes.services.risk_engine import calculate_risk


def analyze_app_listing(
    app_name,
    brand_name,
    publisher="",
    description="",
    platform="Google Play"
):
    name_result = analyze_username(app_name, brand_name)

    risk_result = calculate_risk(
        name_similarity=name_result["similarity"],
        description=description,
        is_official=False
    )

    warnings = []

    if not publisher.strip():
        warnings.append("Publisher information was not provided")

    return {
        "platform": platform,
        "app_name": app_name,
        "publisher": publisher,
        "name_analysis": name_result,
        "risk": risk_result,
        "warnings": warnings,
        "limitations": [
            "The listing was not fetched from a live app store",
            "Publisher ownership was not independently verified"
        ]
    }
