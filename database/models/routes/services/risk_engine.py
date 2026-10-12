
import re


def calculate_risk(
    name_similarity=0,
    description="",
    is_official=False,
    logo_similarity=0
):
    """
    Calculate a heuristic risk score.
    This is not a calibrated probability of fraud.
    """

    if is_official:
        return {
            "risk_score": 0,
            "risk_level": "Low",
            "reasons": ["Entry matches an approved official asset"],
            "reputation_status": "not_checked"
        }

    score = 0
    reasons = []

    # Name similarity contributes up to 45 points.
    similarity = max(0, min(100, float(name_similarity or 0)))
    similarity_points = round(similarity * 0.45)
    score += similarity_points
    if similarity_points:
        reasons.append(f"Name similarity contributed {similarity_points} points")

    if similarity >= 80:
        reasons.append("High name similarity")
    elif similarity >= 55:
        reasons.append("Moderate name similarity")

    # Logo similarity contributes up to 25 points, if supplied.
    logo_similarity = max(0, min(100, float(logo_similarity or 0)))
    if logo_similarity:
        logo_points = round(logo_similarity * 0.25)
        score += logo_points
        if logo_similarity >= 80:
            reasons.append("High visual similarity to the reference logo")

    text = str(description or "").lower()
    keywords = {
        "free": 8,
        "giveaway": 10,
        "claim prize": 12,
        "limited offer": 8,
        "verify account": 10,
        "send password": 20,
        "enter otp": 20,
        "payment required": 10,
        "account suspended": 12,
        "urgent action": 8,
        "click the link": 8,
        "contact support": 8,
        "official support": 8
    }

    matches = [(keyword, points) for keyword, points in keywords.items() if keyword in text]
    for keyword, points in matches:
        score += points
    if matches:
        reasons.append("Potentially risky description phrases: " + ", ".join(keyword for keyword, _ in matches))

    # Keep the score in the range 0–100.
    score = min(100, max(0, score))

    if score >= 60:
        level = "High"
    elif score >= 35:
        level = "Medium"
    else:
        level = "Low"

    if not reasons:
        reasons.append("No strong risk indicators detected by the submitted information")

    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons
    }


def apply_reputation(risk, reputation):
    """Merge completed provider signals without treating unavailable as safe."""
    if not reputation or not reputation.get("checked"):
        risk["reputation_status"] = "not_checked"
        score = max(0, min(100, int(risk.get("risk_score", 0))))
        risk["risk_score"] = score
        risk["risk_level"] = "High" if score >= 60 else "Medium" if score >= 35 else "Low"
        return risk
    points = int(reputation.get("risk_points", 0))
    if points:
        risk["risk_score"] = max(int(risk.get("risk_score", 0)), points)
        for provider in reputation.get("providers", []):
            if provider.get("status") != "complete":
                continue
            if provider.get("malicious", 0) or provider.get("threats_found", 0):
                risk.setdefault("reasons", []).append(f"{provider['provider']} reported known URL threats")
            elif provider.get("suspicious", 0):
                risk.setdefault("reasons", []).append("VirusTotal reported suspicious URL activity")
    score = max(0, min(100, int(risk.get("risk_score", 0))))
    risk["risk_score"] = score
    risk["risk_level"] = "High" if score >= 60 else "Medium" if score >= 35 else "Low"
    risk["reputation_status"] = "checked"
    return risk
