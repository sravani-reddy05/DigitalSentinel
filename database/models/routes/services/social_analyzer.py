
from database.models.routes.services.username_analyzer import analyze_username
from database.models.routes.services.risk_engine import calculate_risk


def analyze_social_profile(
    username,
    brand_name,
    description="",
    platform="Instagram"
):
    username_result = analyze_username(username, brand_name)

    risk_result = calculate_risk(
        name_similarity=username_result["similarity"],
        description=description,
        is_official=False
    )

    return {
        "platform": platform,
        "username_analysis": username_result,
        "risk": risk_result,
        "limitations": [
            "No live social platform lookup was performed",
            "The risk score is heuristic, not proof of impersonation"
        ]
    }
